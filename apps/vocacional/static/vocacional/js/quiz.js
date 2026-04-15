/* static/vocacional/js/quiz.js
 * Renderizador do Vocacional (Bônus 75)
 * - lê window.quizData (injetado pelo template)
 * - mostra 1 pergunta por vez
 * - guarda respostas em inputs hidden (p{id}-valor) para submit normal
 * - faz autosave leve (AJAX) ao escolher a opção
 */

(function () {
  const data = Array.isArray(window.quizData) ? window.quizData : [];

  const form = document.getElementById('quiz-form');
  const container = document.getElementById('quiz-container');
  const btnPrev = document.getElementById('prev-button');
  const btnNext = document.getElementById('next-button');
  const counter = document.getElementById('counter');
  const progressText = document.getElementById('progress-text');
  const progressBar = document.getElementById('progress-bar');

  if (!form || !container) return;

  // Se não veio nada do backend, explica claramente.
  if (!data.length) {
    container.innerHTML = `
      <div class="alert alert-warning" style="margin:0">
        Nenhuma pergunta foi encontrada no banco de dados.<br>
        <small>Se é a primeira execução local, aplique as migrações e/ou rode o seed do Vocacional.</small>
      </div>
    `;
    if (counter) counter.textContent = '0/0';
    if (progressText) progressText.textContent = '0/0 (0%)';
    if (progressBar) progressBar.style.width = '0%';
    if (btnPrev) btnPrev.disabled = true;
    if (btnNext) btnNext.disabled = true;
    return;
  }

  const csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
  const csrf = csrfInput ? csrfInput.value : '';

  // Inputs hidden para submit final (um por pergunta)
  const hiddenById = new Map();
  data.forEach((q) => {
    const hid = document.createElement('input');
    hid.type = 'hidden';
    hid.name = `p${q.id}-valor`;
    hid.id = `hid-p${q.id}`;
    hid.value = q.resposta ? String(q.resposta) : '';
    form.appendChild(hid);
    hiddenById.set(q.id, hid);
  });

  let idx = 0;
  let autosaveTimer = null;

  function answeredCount() {
    let n = 0;
    for (const q of data) {
      const v = hiddenById.get(q.id)?.value;
      if (v) n += 1;
    }
    return n;
  }

  function updateProgress() {
    const total = data.length;
    const done = answeredCount();
    const pct = total ? Math.round((done / total) * 100) : 0;

    if (counter) counter.textContent = `${idx + 1}/${total}`;
    if (progressText) progressText.textContent = `${done}/${total} (${pct}%)`;
    if (progressBar) progressBar.style.width = `${pct}%`;
  }

  function currentValue(qid) {
    return hiddenById.get(qid)?.value || '';
  }

  function setCurrentValue(qid, value) {
    const hid = hiddenById.get(qid);
    if (!hid) return;
    hid.value = String(value);
  }

  function autosaveOne(qid) {
    if (!csrf) return;
    const value = currentValue(qid);
    if (!value) return;

    // debounce
    if (autosaveTimer) clearTimeout(autosaveTimer);
    autosaveTimer = setTimeout(() => {
      const fd = new FormData();
      fd.append('csrfmiddlewaretoken', csrf);
      fd.append('action', 'save');
      fd.append(`p${qid}-valor`, value);

      fetch(window.location.href, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: fd,
      }).catch(() => {});
    }, 350);
  }

  function render() {
    const q = data[idx];

    const val = currentValue(q.id);

    // layout simples (aproveita o CSS do projeto)
    const title = q.codigo ? `<div class="text-muted" style="font-size:.9rem">${q.codigo}</div>` : '';

    container.innerHTML = `
      <div class="mb-3">
        ${title}
        <div class="h5" style="margin:.25rem 0 0">${q.texto}</div>
      </div>

      <div class="d-flex flex-wrap gap-2" aria-label="Escala 1 a 5">
        ${[1,2,3,4,5].map((n) => {
          const checked = String(n) === String(val) ? 'checked' : '';
          return `
            <label class="btn btn-outline-light" style="min-width:56px">
              <input type="radio" name="current_choice" value="${n}" ${checked} style="display:none">
              ${n}
            </label>
          `;
        }).join('')}
      </div>

      <div class="text-muted mt-2" style="font-size:.9rem">
        1 = discordo totalmente · 5 = concordo totalmente
      </div>
    `;

    // listeners nos radios
    const radios = container.querySelectorAll('input[type="radio"][name="current_choice"]');
    radios.forEach((r) => {
      r.addEventListener('change', () => {
        setCurrentValue(q.id, r.value);
        updateProgress();
        if (btnNext) btnNext.disabled = false;
        autosaveOne(q.id);
      });
    });

    // botões
    if (btnPrev) btnPrev.disabled = idx <= 0;
    if (btnNext) btnNext.disabled = !currentValue(q.id);

    updateProgress();
  }

  function go(delta) {
    const q = data[idx];
    if (delta > 0 && !currentValue(q.id)) {
      // não avança sem resposta
      const warn = document.createElement('div');
      warn.className = 'alert alert-warning mt-3';
      warn.textContent = 'Responda a pergunta para avançar.';
      // evita duplicar
      if (!container.querySelector('.alert')) container.appendChild(warn);
      return;
    }

    idx = Math.max(0, Math.min(data.length - 1, idx + delta));
    render();
  }

  // Botões
  if (btnPrev) btnPrev.addEventListener('click', () => go(-1));
  if (btnNext) btnNext.addEventListener('click', () => go(1));

  // Teclas (1–5 e setas)
  document.addEventListener('keydown', (e) => {
    // ignora quando digitando em input/textarea
    const tag = (e.target && e.target.tagName) ? e.target.tagName.toLowerCase() : '';
    if (tag === 'input' || tag === 'textarea' || tag === 'select') return;

    if (e.key >= '1' && e.key <= '5') {
      const q = data[idx];
      setCurrentValue(q.id, e.key);
      render();
      autosaveOne(q.id);
      return;
    }

    if (e.key === 'ArrowLeft') go(-1);
    if (e.key === 'ArrowRight') go(1);
  });

  // inicial
  render();
})();
