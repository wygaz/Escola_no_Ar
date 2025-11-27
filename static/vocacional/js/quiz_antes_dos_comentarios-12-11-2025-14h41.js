// Quiz stepper Likert 1–5 com barra de progresso, autosave e navegação
// Caminho sugerido: static/vocacional/js/quiz.js
// Depende do template injetar:  const quizData = {{ perguntas|safe }};
// Opcional: antes deste script, configurar window.quizInterleaveKey = 'dimensao' | 'especialidade' | 'grupo' | etc.

console.log('quiz.js carregado');

  // ===== toasts (micro feedback de salvamento) =====
  function ensureToastHost() {
    let host = document.getElementById('toast-host');
    if (!host) {
      host = document.createElement('div');
      host.id = 'toast-host';
      host.className = 'toast-host';
      document.body.appendChild(host);
    }
    return host;
  }
  const toastState = { last: 0, minInterval: 2000 };
  function showToast(msg, kind = 'ok') {
    const now = Date.now();
    if (now - toastState.last < toastState.minInterval) return; // evita spam
    toastState.last = now;
    const host = ensureToastHost();
    const el = document.createElement('div');
    el.className = `toast ${kind}`;
    el.textContent = msg;
    host.appendChild(el);
    requestAnimationFrame(() => el.classList.add('show'));
    setTimeout(() => {
      el.classList.remove('show');
      el.classList.add('hide');
      setTimeout(() => el.remove(), 400);
    }, 1400);
  }
window.quizDebug = { ping: true };

(function () {
  const form   = document.getElementById('quiz-form');
  const box    = document.getElementById('quiz-container');
  const btnPrev= document.getElementById('prev-button');
  const btnNext= document.getElementById('next-button');
  const counter= document.getElementById('counter');
  const bar    = document.getElementById('progress-bar');
  const ptext  = document.getElementById('progress-text');

  if (!form || !box) {
    console.warn('[quiz] Elementos base não encontrados (#quiz-form, #quiz-container).');
    return;
  }

  const scaleText = {
    1: 'não tem nada a ver comigo',
    2: 'discordo',
    3: 'indiferente',
    4: 'concordo',
    5: 'tem tudo a ver comigo'
  };

  // ------------ helpers ------------
  const byId = (id) => document.getElementById(id);
  const clamp = (n, a, b) => Math.max(a, Math.min(b, n));
  const escapeHtml = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
  const getCsrf = () => {
    const inp = form.querySelector('input[name="csrfmiddlewaretoken"]');
    return inp ? inp.value : '';
  };
  function ensureHiddenInput(qid) {
    let inp = byId(`p${qid}-valor`);
    if (!inp) {
      inp = document.createElement('input');
      inp.type = 'hidden';
      inp.name = `p${qid}-valor`;
      inp.id   = `p${qid}-valor`;
      form.appendChild(inp);
    }
    return inp;
  }

  // --------- intercalar pares (evitar itens irmãos consecutivos) ---------
  // Estratégia simples: dada uma chave, reordena para que a mesma chave não se repita seguidamente, quando possível.
  function interleaveByKey(items, key) {
    if (!key) return items;
    try {
      const groups = new Map();
      for (const it of items) {
        const k = valueKey(it, key);
        if (!groups.has(k)) groups.set(k, []);
        groups.get(k).push(it);
      }
      // ordena grupos do maior para o menor para melhor mistura
      const buckets = Array.from(groups.values()).sort((a,b) => b.length - a.length);
      const out = [];
      // round-robin simples
      while (buckets.some(b => b.length)) {
        for (const b of buckets) {
          if (b.length) out.push(b.shift());
        }
      }
      return out;
    } catch (e) {
      console.warn('[quiz] interleave falhou, mantendo ordem original', e);
      return items;
    }
  }
  function valueKey(obj, path) {
    // aceita dot-path: 'dimensao.slug' ou chaves diretas: 'dimensao', 'especialidade'
    const parts = String(path).split('.');
    let cur = obj;
    for (const p of parts) cur = cur && cur[p];
    return cur ?? '__none__';
  }

  // ---------- Estado ----------
  let list = Array.isArray(window.quizData) ? window.quizData.slice() : [];
  const interleaveKey = window.quizInterleaveKey || null; // ex.: 'dimensao' | 'especialidade' | 'grupo'
  if (list.length && interleaveKey) {
    list = interleaveByKey(list, interleaveKey);
    window.quizDebug.interleaved = true;
  }

  const total = list.length;
  let idx = 0;
  const answers = new Map(); // qid => valor 1..5

  // Pré-carrega respostas (vêm do servidor ou de inputs hidden)
  if (total > 0) {
    for (const q of list) {
      const hidden = byId(`p${q.id}-valor`);
      const val = hidden ? parseInt(hidden.value, 10) : (q.resposta || null);
      if (val) answers.set(q.id, clamp(val, 1, 5));
    }
  }
  
  // escolher início: primeira não respondida
  function computeStartIndex() {
    for (let i = 0; i < total; i++) {
      const q = list[i];
      if (!answers.has(q.id)) return i;
    }
    return 0; // todas respondidas
  }
  idx = computeStartIndex();

  function updateProgress() {
    const done = answers.size;
    const pct = total ? Math.round((done / total) * 100) : 0;
    if (bar) bar.style.width = pct + '%';
    if (ptext) ptext.textContent = `${done}/${total} (${pct}%)`;
  }

  function showWarn(show) {
    const w = byId('warn');
    if (w) w.style.display = show ? 'block' : 'none';
  }

  function canGoNext() {
    const q = list[idx];
    return q && answers.has(q.id);
  }

  let hasRendered = false;

  function go(delta) {
    if (delta > 0 && !canGoNext()) {
      showWarn(true);
      return;
    }
    showWarn(false);
    idx = clamp(idx + delta, 0, total - 1);
    render();
    hasRendered = true;
  }

  async function autosaveOne(qid, val) {
    try {
      const fd = new URLSearchParams();
      fd.append('csrfmiddlewaretoken', getCsrf());
      fd.append(`p${qid}-valor`, String(val));
      const res = await fetch(window.location.href, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: fd.toString(),
        credentials: 'same-origin',
      });
      if (res && res.ok) showToast('Progresso salvo!', 'ok');
    } catch (_) { /* silencia erros de rede */ }
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
    const q = list[idx];
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
        <div id="warn" class="warn-msg" style="display:none">Escolha uma opção para avançar.</div>
      </div>
    `;

    if (counter) counter.textContent = `${idx + 1}/${total}`;

    // listeners dos radios
    box.querySelectorAll('input[type="radio"]').forEach(r => {
      r.addEventListener('change', () => {
        const val = parseInt(r.value, 10);
        answers.set(q.id, val);
        ensureHiddenInput(q.id).value = String(val);
        box.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
        r.closest('.pill')?.classList.add('active');
        showWarn(false);
        updateProgress();
        autosaveOne(q.id, val);

        // >>> AUTO-AVANÇAR <<<
        if (idx < total - 1) {
          setTimeout(() => go(1), 140); // pequeno delay só p/ feedback visual
        } else {
          // última questão: foca o 'Finalizar'
          const fin = form.querySelector('button[name="finalizar"]');
          fin?.focus();
        }
      });
    });


    // focus acessível
    const first = box.querySelector('input[type="radio"]');
    if (first) first.focus();

    updateProgress();
  }

  // Botões prev/next
  if (btnPrev) btnPrev.addEventListener('click', () => go(-1));
  if (btnNext) btnNext.addEventListener('click', () => go(1));

  // Teclado: ← → e 1..5
  window.addEventListener('keydown', (e) => {
    if (['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)) return;
    if (e.key === 'ArrowLeft')  { e.preventDefault(); go(-1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); go(1); }
    if (/^[1-5]$/.test(e.key)) {
      const v = parseInt(e.key, 10);
      const q = list[idx];
      if (!q) return;
      answers.set(q.id, v);
      ensureHiddenInput(q.id).value = String(v);
      const radio = box.querySelector(`input[type="radio"][value="${v}"]`);
      if (radio) {
        radio.checked = true;
        box.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
        radio.closest('.pill')?.classList.add('active');
      }
      showWarn(false);
      updateProgress();
      autosaveOne(q.id, v);
    }
  });

  // Intercepta submit para diferenciar Salvar vs Finalizar
  form.addEventListener('submit', (e) => {
    const submitter = e.submitter; // navegadores modernos
    const isFinalizar = submitter && submitter.name === 'finalizar';
    if (isFinalizar && answers.size < total) {
      e.preventDefault();
      showWarn(true);
      return;
    }
    // caso contrário deixa o servidor tratar
  });

  // Primeira renderização
  render();
})();
