(() => {
  // Lê o JSON injetado pela view
  const elData = document.getElementById('perguntas-data');
  if (!elData) { console.warn('Sem #perguntas-data'); return; }
  const perguntas = JSON.parse(elData.textContent || '[]');

  // Elementos esperados na página (coloque esses IDs/atributos no template)
  const elTexto = document.querySelector('#pergunta');          // onde aparece o texto
  const elPos   = document.querySelector('#pos');                // número atual
  const elTot   = document.querySelector('#total');              // total
  const btnPrev = document.querySelector('[data-prev]');         // botão "Anterior"
  const btnNext = document.querySelector('[data-next]');         // botão "Próxima"

  if (elTot)  elTot.textContent = perguntas.length;
  let i = 0;

  function render() {
    const p = perguntas[i] || {};
    if (elTexto) elTexto.textContent = p.texto || '—';
    if (elPos)   elPos.textContent   = perguntas.length ? (i + 1) : 0;
  }

  btnNext?.addEventListener('click', () => {
    if (i < perguntas.length - 1) { i++; render(); }
  });

  btnPrev?.addEventListener('click', () => {
    if (i > 0) { i--; render(); }
  });

  // Atalhos de teclado (← → 1..5) — opcional
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') btnNext?.click();
    if (e.key === 'ArrowLeft')  btnPrev?.click();
    // aqui você pode mapear 1..5 para marcar resposta e fazer autosave
  });

  // Primeiro paint
  render();
})();
