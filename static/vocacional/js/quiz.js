// =============================================================
// Quiz Vocacional – Stepper Likert 1–5 com debug
// -------------------------------------------------------------
// Espera no template:
//
//   window.quizData = {{ perguntas|safe }}
//   window.quizInterleaveKey = 'dimensao'  // opcional
//
// Estrutura mínima no HTML (já está pronta no avaliacao_form.html):
//   <form id="quiz-form"> ... </form>
//   #quiz-container, #prev-button, #next-button, #counter,
//   #progress-bar, #progress-text
// =============================================================


function log(...args) {
  console.log('[quiz]', ...args);
}
log('quiz.js carregado');

(function () {
  // ... resto do arquivo como já está ...
})();
(function () {
  // ----------------------------------------------------------
  // Referências ao DOM
  // ----------------------------------------------------------
  const form    = document.getElementById('quiz-form');
  const box     = document.getElementById('quiz-container');
  const btnPrev = document.getElementById('prev-button');
  const btnNext = document.getElementById('next-button');
  const bar     = document.getElementById('progress-bar');
  const ptext   = document.getElementById('progress-text');

  if (!form || !box) {
    console.warn('[quiz] abortando: #quiz-form ou #quiz-container não encontrados.');
    return;
  }

  // ----------------------------------------------------------
  // Utilitários
  // ----------------------------------------------------------
  const byId  = (id) => document.getElementById(id);
  const clamp = (n, a, b) => Math.max(a, Math.min(b, n));
  const esc   = (s) =>
    String(s).replace(/[&<>"']/g, (c) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])
    );

  const csrf = () => {
    const inp = form.querySelector('input[name="csrfmiddlewaretoken"]');
    return inp ? inp.value : '';
  };

  function ensureHidden(qid) {
    // garante um <input type="hidden" name="p{ID}-valor">
    let i = byId(`p${qid}-valor`);
    if (!i) {
      i = document.createElement('input');
      i.type = 'hidden';
      i.name = `p${qid}-valor`;
      i.id   = `p${qid}-valor`;
      form.appendChild(i);
    }
    return i;
  }

  // ----------------------------------------------------------
  // Interleaving – mistura perguntas por chave (dimensão, etc.)
  // ----------------------------------------------------------
  function vkey(obj, path) {
    const parts = String(path).split('.');
    let cur = obj;
    for (const p of parts) cur = cur && cur[p];
    return cur ?? '__none__';
  }

  function interleave(items, key) {
    if (!key) return items;
    try {
      const groups = new Map();
      for (const it of items) {
        const k = vkey(it, key);
        if (!groups.has(k)) groups.set(k, []);
        groups.get(k).push(it);
      }
      const buckets = [...groups.values()].sort((a, b) => b.length - a.length);
      const out = [];
      while (buckets.some((b) => b.length)) {
        for (const b of buckets) {
          if (b.length) out.push(b.shift());
        }
      }
      return out;
    } catch (err) {
      console.warn('[quiz] interleave falhou, usando ordem original', err);
      return items;
    }
  }

  // ----------------------------------------------------------
  // Estado básico do quiz
  // ----------------------------------------------------------
  let list = Array.isArray(window.quizData) ? window.quizData.slice() : [];
  const rawTotal = list.length;
  const interleaveKey = window.quizInterleaveKey || null;

  const counter = document.getElementById("counter");
  const progressText = document.getElementById("progress-text");

  if (!Array.isArray(data) || !data.length) {
    if (counter) counter.textContent = "0/0";
    if (progressText) progressText.textContent = "0/0 (0%)";
    console.warn("quizData vazio ou inválido", data);
    return;
  }
  
  console.log('[quiz] dados recebidos do backend:', {
    rawTotal,
    interleaveKey,
    sample: list[0]
  });

  if (interleaveKey) {
    list = interleave(list, interleaveKey);
    console.log('[quiz] lista após interleaving:', {
      total: list.length,
      first: list[0]
    });
  }

  const total = list.length;
  let idx = 0;                    // índice atual
  const answers = new Map();      // q.id -> valor (1..5)

  if (!total) {
    console.warn('[quiz] nenhuma pergunta disponível (total = 0).');
    box.innerHTML = '<em>Nenhuma pergunta disponível.</em>';
    if (counter) counter.textContent = '0/0';
    if (btnPrev) btnPrev.disabled = true;
    if (btnNext) btnNext.disabled = true;
    if (ptext)   ptext.textContent = '0/0 (0%)';
    return;
  }

  // ----------------------------------------------------------
  // Pré-carrega respostas existentes (rascunho)
  // ----------------------------------------------------------
  list.forEach((q, i) => {
    const hidden = byId(`p${q.id}-valor`);
    const valRaw = hidden ? parseInt(hidden.value, 10) : (q.resposta || null);
    if (valRaw && !Number.isNaN(valRaw)) {
      const v = clamp(valRaw, 1, 5);
      answers.set(q.id, v);
    }
  });

  // Começa na primeira questão ainda não respondida
  const firstMissing = list.findIndex((q) => !answers.has(q.id));
  if (firstMissing >= 0) idx = firstMissing;
  console.log('[quiz] estado inicial:', {
    total,
    respondidas: answers.size,
    idxInicial: idx
  });

  // ----------------------------------------------------------
  // Progresso
  // ----------------------------------------------------------
  function updateProgress() {
    const done = answers.size;
    const pct  = total ? Math.round((done / total) * 100) : 0;
    if (bar)   bar.style.width = pct + '%';
    if (ptext) ptext.textContent = `${done}/${total} (${pct}%)`;
  }

  function canNext() {
    const q = list[idx];
    return answers.has(q.id);
  }

  function showWarn(show) {
    const w = document.getElementById('warn');
    if (w) w.style.display = show ? 'block' : 'none';
  }

  // ----------------------------------------------------------
  // Autosave de 1 resposta
  // ----------------------------------------------------------
  async function autosaveOne(qid, val) {
    try {
      const fd = new URLSearchParams();
      fd.append('csrfmiddlewaretoken', csrf());
      fd.append(`p${qid}-valor`, String(val));

      console.log('[quiz] autosaveOne()', { qid, val });

      const res = await fetch(window.location.href, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: fd.toString(),
        credentials: 'same-origin'
      });

      if (!res.ok) {
        console.warn('[quiz] autosave falhou (HTTP)', res.status);
      }
    } catch (err) {
      console.warn('[quiz] autosaveOne lançou exceção', err);
    }
  }

  // ----------------------------------------------------------
  // Navegação
  // ----------------------------------------------------------
  function go(delta) {
    if (delta > 0 && !canNext()) {
      showWarn(true);
      return;
    }
    showWarn(false);
    idx = clamp(idx + delta, 0, total - 1);
    console.log('[quiz] go()', { delta, idx });
    render();
  }

  // ----------------------------------------------------------
  // Renderização de 1 questão
  // ----------------------------------------------------------
  function render() {
    if (!total) {
      box.innerHTML = '<em>Nenhuma pergunta disponível.</em>';
      if (counter) counter.textContent = '0/0';
      btnPrev && (btnPrev.disabled = true);
      btnNext && (btnNext.disabled = true);
      updateProgress();
      return;
    }

    idx = clamp(idx, 0, total - 1);
    const q   = list[idx];
    const cur = answers.get(q.id) || 0;

    // Tentamos vários campos possíveis para o texto
    const questionText =
      q.texto ??
      q.pergunta ??
      q.enunciado ??
      q.descricao ??
      q.descricao_curta ??
      q.titulo ??
      '';

    console.log('[quiz] render()', {
      idx,
      qid: q.id,
      questionText,
      cur
    });

    box.innerHTML = `
      <div style="text-align:left">
        <div style="font-weight:600; margin-bottom:.5rem">
          ${idx + 1}. ${esc(questionText)}
        </div>

        <div class="likert" role="radiogroup" aria-label="Escala de 1 a 5">
          ${[1, 2, 3, 4, 5]
            .map(
              (v) => `
            <label class="pill ${cur === v ? 'active' : ''}" for="q_${q.id}_${v}">
              <input id="q_${q.id}_${v}" type="radio" name="q_${q.id}" value="${v}" ${
                cur === v ? 'checked' : ''
              } />
              <span class="pill-num">${v}</span>
              <span class="pill-text">${
                {
                  1: 'não tem nada a ver comigo',
                  2: 'discordo',
                  3: 'indiferente',
                  4: 'concordo',
                  5: 'tem tudo a ver comigo'
                }[v]
              }</span>
            </label>`
            )
            .join('')}
        </div>

        <div id="warn" class="warn-msg" style="display:none">
          Escolha uma opção para avançar.
        </div>
      </div>
    `;

    if (counter) counter.textContent = `${idx + 1}/${total}`;

    // listeners dos rádios
    box.querySelectorAll('input[type="radio"]').forEach((r) => {
      r.addEventListener('change', () => {
        const val = parseInt(r.value, 10);
        answers.set(q.id, val);
        ensureHidden(q.id).value = String(val);

        // visual: deixa só a pílula atual ativa
        box.querySelectorAll('.pill').forEach((p) => p.classList.remove('active'));
        r.closest('.pill')?.classList.add('active');

        showWarn(false);
        updateProgress();
        autosaveOne(q.id, val);

        // auto-avanço suave
        if (idx < total - 1) {
          setTimeout(() => go(1), 140);
        }
      });
    });

    const firstRadio = box.querySelector('input[type="radio"]');
    if (firstRadio) firstRadio.focus();

    updateProgress();
  }

  // ----------------------------------------------------------
  // Eventos de botões e teclado
  // ----------------------------------------------------------
  if (btnPrev) btnPrev.addEventListener('click', () => go(-1));
  if (btnNext) btnNext.addEventListener('click', () => go(1));

  // Teclado: ← → e 1..5
  window.addEventListener('keydown', (e) => {
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;

    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      go(-1);
    }
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      go(1);
    }
    if (/^[1-5]$/.test(e.key)) {
      const v = parseInt(e.key, 10);
      const q = list[idx];
      answers.set(q.id, v);
      ensureHidden(q.id).value = String(v);

      const radio = box.querySelector(`input[type="radio"][value="${v}"]`);
      if (radio) radio.checked = true;

      box.querySelectorAll('.pill').forEach((p) => p.classList.remove('active'));
      radio?.closest('.pill')?.classList.add('active');

      showWarn(false);
      updateProgress();
      autosaveOne(q.id, v);

      if (idx < total - 1) {
        setTimeout(() => go(1), 140);
      }
    }
  });

  // Impede finalizar com perguntas em branco
  form.addEventListener('submit', (e) => {
    const submitter = e.submitter;
    const isFinalizar = submitter && submitter.name === 'finalizar';
    if (isFinalizar && answers.size < total) {
      e.preventDefault();
      showWarn(true);
      console.warn('[quiz] tentativa de finalizar com perguntas em branco');
      return;
    }
  });

  // Expor um pequeno hook para inspeção manual
  window.quizDebug = {
    list,
    answers,
    go,
    render
  };

  // Primeira renderização
  render();
})();
