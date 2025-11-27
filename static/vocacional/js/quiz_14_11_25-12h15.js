// =============================================================
// Quiz Vocacional – Stepper Likert 1–5
// -------------------------------------------------------------
// Recursos:
// - Navegação por passos (Anterior/Próximo)
// - Escala Likert (1..5) via clique e atalhos do teclado (1..5)
// - Auto‑avanço para a próxima questão após marcar
// - Autosave de cada resposta (AJAX) para o servidor
// - Barra de progresso + contador
// - Retoma de onde parou (abre na 1ª não respondida)
// - Interleaving opcional de itens por chave (evitar irmãos consecutivos)
// -------------------------------------------------------------
// Dependências do template:
//   window.quizData = {{ perguntas|safe }}          // array [{id, texto, resposta?, dimensao?}]
//   (opcional) window.quizInterleaveKey = 'dimensao'|'especialidade'|'grupo'|... (string)
// Estrutura mínima no HTML:
//   <form id="quiz-form">  (com input CSRF)
//     <div id="quiz-container"></div>
//     <button id="prev-button" type="button">Anterior</button>
//     <button id="next-button" type="button">Próxima</button>
//     <div id="counter"></div>
//     <div class="progress"><div id="progress-bar" class="bar"></div></div>
//     <div id="progress-text"></div>
//     <button type="submit" name="finalizar" value="1">Finalizar</button>
//   </form>
// -------------------------------------------------------------
// Dica: incremente a querystring ao incluir o arquivo para forçar reload
//   <script src=".../quiz.js?v=20251112"></script>
// =============================================================

console.log('quiz.js carregado');

// =============================================================
// Toasts – micro feedback de salvamento
// =============================================================
function ensureToastHost(){
  /** Cria (uma única vez) o container dos toasts. */
  let host = document.getElementById('toast-host');
  if(!host){
    host = document.createElement('div');
    host.id = 'toast-host';
    host.className = 'toast-host';
    document.body.appendChild(host);
  }
  return host;
}

const toastState = { last: 0, minInterval: 2000 };

function showToast(message, kind='ok'){
  /** Exibe um toast curto. Há um intervalo mínimo para evitar spam visual. */
  const now = Date.now();
  if (now - toastState.last < toastState.minInterval) return;
  toastState.last = now;

  const host = ensureToastHost();
  const el = document.createElement('div');
  el.className = `toast ${kind}`;
  el.textContent = message;
  host.appendChild(el);

  requestAnimationFrame(()=> el.classList.add('show'));
  setTimeout(()=>{
    el.classList.remove('show');
    el.classList.add('hide');
    setTimeout(()=> el.remove(), 400);
  }, 1400);
}

(function(){
  // ===========================================================
  // Referências aos elementos do DOM
  // ===========================================================
  const form    = document.getElementById('quiz-form');
  const box     = document.getElementById('quiz-container');
  const btnPrev = document.getElementById('prev-button');
  const btnNext = document.getElementById('next-button');
  const counter = document.getElementById('counter');
  const bar     = document.getElementById('progress-bar');
  const ptext   = document.getElementById('progress-text');

  if(!form || !box){
    console.warn('[quiz] Elementos base ausentes (#quiz-form, #quiz-container).');
    return; // aborta para não gerar erros em páginas sem o quiz
  }

  // ===========================================================
  // Utilitários
  // ===========================================================
  const byId   = (id)=> document.getElementById(id);
  const clamp  = (n,a,b)=> Math.max(a, Math.min(b, n));
  const esc    = (s)=> String(s).replace(/[&<>"']/g, c=> ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
  const csrf   = ()=> (form.querySelector('input[name="csrfmiddlewaretoken"]').value || '');

  function ensureHidden(qid){
    /** Garante um <input type="hidden" name="p{ID}-valor"> para o POST. */
    let i = byId(`p${qid}-valor`);
    if(!i){
      i = document.createElement('input');
      i.type = 'hidden';
      i.name = `p${qid}-valor`;
      i.id   = `p${qid}-valor`;
      form.appendChild(i);
    }
    return i;
  }

  // ===========================================================
  // Interleaving – mistura perguntas por chave para evitar irmãs consecutivas
  // ===========================================================
  function vkey(obj, path){
    /** Lê uma chave simples ou dot‑path (ex.: 'dimensao.slug'). */
    const parts = String(path).split('.');
    let cur = obj;
    for(const p of parts) cur = cur && cur[p];
    return cur ?? '__none__';
  }

  function interleave(items, key){
    /**
     * Estratégia round‑robin: agrupa por chave, ordena buckets do maior p/ menor
     * e intercala um item de cada bucket até acabar.
     */
    if(!key) return items;
    try{
      const groups = new Map();
      for(const it of items){
        const k = vkey(it, key);
        if(!groups.has(k)) groups.set(k, []);
        groups.get(k).push(it);
      }
      const buckets = [...groups.values()].sort((a,b)=> b.length - a.length);
      const out = [];
      while (buckets.some(b=> b.length)){
        for(const b of buckets){ if(b.length) out.push(b.shift()); }
      }
      return out;
    }catch(err){
      console.warn('[quiz] interleave falhou, usando ordem original', err);
      return items;
    }
  }

  // ===========================================================
  // Estado do Quiz
  // ===========================================================
  /** Lista de perguntas vindas do servidor. */
  let list  = Array.isArray(window.quizData) ? window.quizData.slice() : [];
  const key = window.quizInterleaveKey || null; // 'dimensao'|'especialidade'|...
  if (list.length && key) list = interleave(list, key);

  const total   = list.length;
  let idx       = 0;                 // índice atual no array de perguntas
  const answers = new Map();         // Map<qid, 1..5>

  /** Rótulos da escala Likert */
  const scaleText = {
    1:'não tem nada a ver comigo',
    2:'discordo',
    3:'indiferente',
    4:'concordo',
    5:'tem tudo a ver comigo'
  };

  // Pré‑carrega respostas já salvas (server -> JSON) ou em hiddens
  for (const q of list){
    const hid = byId(`p${q.id}-valor`);
    const v   = hid ? parseInt(hid.value, 10) : (q.resposta || null);
    if (v) answers.set(q.id, clamp(v,1,5));
  }

  // Começa na 1ª pergunta não respondida (retomada de sessão)
  function computeStartIndex(){
    for (let i=0;i<total;i++) if(!answers.has(list[i].id)) return i;
    return 0; // caso todas já estejam respondidas
  }
  idx = clamp(computeStartIndex(), 0, Math.max(total-1, 0));

  // ===========================================================
  // UI helpers
  // ===========================================================
  function progress(){
    /** Atualiza barra e texto de progresso. */
    const done = answers.size;
    const pct  = total ? Math.round((done/total)*100) : 0;
    if (bar)  bar.style.width = pct + '%';
    if (ptext) ptext.textContent = `${done}/${total} (${pct}%)`;
  }

  function warn(show){
    /** Mostra/oculta aviso para marcar opção antes de avançar. */
    const w = byId('warn');
    if (w) w.style.display = show ? 'block' : 'none';
  }

  function canNext(){
    /** Só permite avançar se a atual estiver respondida. */
    const q = list[idx];
    return q && answers.has(q.id);
  }

  // ===========================================================
  // Persistência de 1 resposta (autosave AJAX)
  // ===========================================================
  async function autosaveOne(qid, val){
    try{
      const fd = new URLSearchParams();
      fd.append('csrfmiddlewaretoken', csrf());
      fd.append(`p${qid}-valor`, String(val));
      const res = await fetch(window.location.href, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type'    : 'application/x-www-form-urlencoded',
        },
        body: fd.toString(),
        credentials: 'same-origin',
      });
      if (res && res.ok) showToast('Progresso salvo!', 'ok');
    }catch(_){ /* falha silenciosa para não travar a UX */ }
  }

  // ===========================================================
  // Navegação
  // ===========================================================
  function go(delta){
    /** Avança/retrocede um passo, respeitando a regra de resposta obrigatória. */
    if (delta > 0 && !canNext()) { warn(true); return; }
    warn(false);
    idx = clamp(idx + delta, 0, total-1);
    render();
  }

  // ===========================================================
  // Renderização de 1 questão
  // ===========================================================
function render() {
  if (!total) {
    box.innerHTML = '<p>Nenhuma pergunta disponível.</p>';
    return;
  }

  idx = clamp(idx, 0, total - 1);
  const q = list[idx];
  const currentVal = answers.get(q.id) || 0;

  // tenta vários nomes de campo possíveis para o enunciado
  const questionText =
    q.texto ??
    q.pergunta ??
    q.enunciado ??
    q.descricao ??
    q.descricao_curta ??
    q.titulo ??
    '';

    box.innerHTML = `
      <div style="text-align:left">
        <div style="font-weight:600; margin-bottom:.5rem">
          ${idx + 1}. ${esc(questionText)}
        </div>

        <div class="likert" role="radiogroup" aria-label="Escala de 1 a 5">
          ${[1, 2, 3, 4, 5].map(v => `
            <label class="pill ${currentVal === v ? 'active' : ''}" for="q_${q.id}_${v}">
              <input id="q_${q.id}_${v}" type="radio" name="q_${q.id}" value="${v}" ${currentVal === v ? 'checked' : ''} />
              <span class="pill-num">${v}</span>
              <span class="pill-text">${scaleText[v]}</span>
            </label>
          `).join('')}
        </div>

        <div id="warn" class="warn-msg">Escolha uma opção para avançar.</div>
      </div>
    `;

    if (counter) counter.textContent = `${idx+1}/${total}`;

    // Listener dos rádios (clique/toque)
    box.querySelectorAll('input[type="radio"]').forEach(r=>{
      r.addEventListener('change', ()=>{
        const val = parseInt(r.value, 10);
        answers.set(q.id, val);
        ensureHidden(q.id).value = String(val);

        // feedback visual da pílula ativa
        box.querySelectorAll('.pill').forEach(p=> p.classList.remove('active'));
        r.closest('.pill')?.classList.add('active');

        warn(false);
        progress();
        autosaveOne(q.id, val);

        // Auto‑avanço com pequeno delay para o usuário perceber a seleção
        if (idx < total-1){
          setTimeout(()=> go(1), 140);
        } else {
          // Última questão: foca o botão Finalizar para acelerar o fluxo
          form.querySelector('button[name="finalizar"]')?.focus();
        }
      });
    });

    // Acessibilidade: foca o primeiro rádio
    box.querySelector('input[type="radio"]')?.focus();

    progress();
  }

  // Botões Anterior/Próxima
  btnPrev?.addEventListener('click', ()=> go(-1));
  btnNext?.addEventListener('click', ()=> go(1));

  // Teclado: setas e escolha direta 1..5
  window.addEventListener('keydown', (e)=>{
    // Evita capturar quando o foco está em inputs do formulário
    if (['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)) return;

    if (e.key === 'ArrowLeft'){  e.preventDefault(); go(-1); }
    if (e.key === 'ArrowRight'){ e.preventDefault(); go(1);  }

    // Marca por atalho numérico
    if (/^[1-5]$/.test(e.key)){
      const v = parseInt(e.key, 10);
      const q = list[idx];
      if (!q) return;

      answers.set(q.id, v);
      ensureHidden(q.id).value = String(v);

      // reflete visualmente
      const radio = box.querySelector(`input[type="radio"][value="${v}"]`);
      if (radio){
        radio.checked = true;
        box.querySelectorAll('.pill').forEach(p=> p.classList.remove('active'));
        radio.closest('.pill')?.classList.add('active');
      }

      warn(false);
      progress();
      autosaveOne(q.id, v);

      // Auto‑avanço pelo teclado também
      if (idx < total-1){
        setTimeout(()=> go(1), 120);
      } else {
        form.querySelector('button[name="finalizar"]')?.focus();
      }
    }
  });

  // Submit do form: impede finalizar se ainda houver itens em branco
  form.addEventListener('submit', (e)=>{
    const submitter   = e.submitter;            // Requer browsers modernos
    const isFinalizar = submitter && submitter.name === 'finalizar';
    if (isFinalizar && answers.size < total){
      e.preventDefault();
      warn(true);
      return;
    }
    // Deixa o servidor persistir tudo quando não for AJAX (Salvar/Finalizar)
  });

  // Primeira renderização
  render();
})();
