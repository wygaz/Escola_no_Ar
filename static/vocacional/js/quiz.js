// Quiz stepper Likert 1–5 com barra de progresso, autosave e navegação
// Caminho: static/vocacional/js/quiz.js
// Depende de o template injetar:  const quizData = {{ perguntas|safe }};

console.log('quiz.js carregado');
window.quizDebug = { ping: true };


(function () {
  const form = document.getElementById('quiz-form');
  const box = document.getElementById('quiz-container');
  const btnPrev = document.getElementById('prev-button');
  const btnNext = document.getElementById('next-button');
  const counter = document.getElementById('counter');
  const bar = document.getElementById('progress-bar');
  const ptext = document.getElementById('progress-text');

  const scaleText = {
    1: "não tem nada a ver comigo",
    2: "discordo",
    3: "indiferente",
    4: "concordo",
    5: "tem tudo a ver comigo"
  };


  if (!form || !box) return;

  // ------------ helpers ------------
  function byId(id) { return document.getElementById(id); }

  function getCsrf() {
    const inp = form.querySelector('input[name="csrfmiddlewaretoken"]');
    return inp ? inp.value : '';
  }

  function clamp(n, a, b) { return Math.max(a, Math.min(b, n)); }

  function ensureHiddenInput(qid) {
    let inp = byId(`p${qid}-valor`);
    if (!inp) {
      inp = document.createElement('input');
      inp.type = 'hidden';
      inp.name = `p${qid}-valor`;
      inp.id = `p${qid}-valor`;
      form.appendChild(inp);
    }
    return inp;
  }

  // Estado
  const total = Array.isArray(quizData) ? quizData.length : 0;
  let idx = 0;
  const answers = new Map(); // qid => valor 1..5

  // Pré-carrega respostas
  if (total > 0) {
    for (const q of quizData) {
      const hidden = byId(`p${q.id}-valor`);
      const val = hidden ? parseInt(hidden.value, 10) : (q.resposta || null);
      if (val) answers.set(q.id, clamp(val, 1, 5));
    }
  }

  function updateProgress() {
    const done = answers.size;
    const pct = total ? Math.round((done / total) * 100) : 0;
    if (bar) bar.style.width = pct + '%';
    if (ptext) ptext.textContent = `${done}/${total} (${pct}%)`;
  }

function render() {
  if (!total) {
    box.innerHTML = '<em>Nenhuma pergunta disponível.</em>';
    if (counter) counter.textContent = '0/0';
    if (btnPrev) btnPrev.disabled = true;
    if (btnNext) btnNext.disabled = true;
    updateProgress();
    return;
  }

  idx = clamp(idx, 0, total - 1);
  const q = quizData[idx];
  const currentVal = answers.get(q.id) || 0;

  box.innerHTML = `
    <div style="text-align:left">
      <div style="font-weight:600; margin-bottom:.5rem">${idx + 1}. ${escapeHtml(q.texto || q.pergunta || '')}</div>
      <div class="likert" role="radiogroup" aria-label="Escala de 1 a 5">
        ${[1,2,3,4,5].map(v => `
          <label class="pill ${currentVal===v? 'active':''}" for="q_${q.id}_${v}">
            <input id="q_${q.id}_${v}" type="radio" name="q_${q.id}" value="${v}" ${currentVal===v? 'checked':''} />
            <span class="pill-num">${v}</span>
            <span class="pill-text">${scaleText[v]}</span>
          </label>
        `).join('')}
      </div>
      <div id="warn" class="warn-msg">Escolha uma opção para avançar.</div>
    </div>
  `;

  if (counter) counter.textContent = `${idx + 1}/${total}`;

  // wire dos radios
  box.querySelectorAll('input[type="radio"]').forEach(r => {
    r.addEventListener('change', () => {
      const val = parseInt(r.value, 10);
      answers.set(q.id, val);
      ensureHiddenInput(q.id).value = String(val);
      // atualiza destaque das pílulas
      box.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
      r.closest('.pill')?.classList.add('active');
      updateProgress();
      autosaveOne(q.id, val);
    });
  });

  // foco
  const first = box.querySelector('input[type="radio"]');
  if (first) first.focus();

  updateProgress();
}

    // Wire dos radios
    box.querySelectorAll('input[type="radio"]').forEach(r => {
      r.addEventListener('change', () => {
        const val = parseInt(r.value, 10);
        answers.set(q.id, val);
        ensureHiddenInput(q.id).value = String(val);
        updateProgress();
        autosaveOne(q.id, val);
      });
    });

    // Focus primeiro radio
    const first = box.querySelector('input[type="radio"]');
    if (first) first.focus();

    updateProgress();
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[c]);
  }

  function canGoNext() {
    const q = quizData[idx];
    return answers.has(q.id);
  }

  function showWarn(show) {
    const w = byId('warn');
    if (w) w.style.display = show ? 'block' : 'none';
  }

  function go(delta) {
    if (delta > 0 && !canGoNext()) {
      showWarn(true);
      return;
    }
    showWarn(false);
    idx = clamp(idx + delta, 0, total - 1);
    render();
  }

  async function autosaveOne(qid, val) {
    try {
      const fd = new URLSearchParams();
      fd.append('csrfmiddlewaretoken', getCsrf());
      fd.append(`p${qid}-valor`, String(val));
      await fetch(window.location.href, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/x-www-form-urlencoded' },
        body: fd.toString(),
        credentials: 'same-origin',
      });
    } catch (_) { /* silencia */ }
  }

  // Botões prev/next
  if (btnPrev) btnPrev.addEventListener('click', () => go(-1));
  if (btnNext) btnNext.addEventListener('click', () => go(1));

  // Teclado: ← → e 1..5
  window.addEventListener('keydown', (e) => {
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;
    if (e.key === 'ArrowLeft') { e.preventDefault(); go(-1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); go(1); }
    if (/^[1-5]$/.test(e.key)) {
      const v = parseInt(e.key, 10);
      const q = quizData[idx];
      answers.set(q.id, v);
      ensureHiddenInput(q.id).value = String(v);
      const radio = box.querySelector(`input[type="radio"][value="${v}"]`);
      if (radio) radio.checked = true;
      updateProgress();
      autosaveOne(q.id, v);
    }
  });

  // Intercepta submit para diferenciar Salvar vs Finalizar
  form.addEventListener('submit', (e) => {
    const submitter = e.submitter; // suporte moderno
    const isFinalizar = submitter && submitter.name === 'finalizar';
    if (isFinalizar && answers.size < total) {
      e.preventDefault();
      showWarn(true);
      return;
    }
  });

  // Primeira renderização
  render();
})();
