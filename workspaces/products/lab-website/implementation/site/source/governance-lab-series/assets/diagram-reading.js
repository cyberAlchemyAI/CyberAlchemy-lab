/* Progressive enhancement: the full source diagrams remain the no-script view. */
(() => {
  for (const root of document.querySelectorAll('[data-diagram-reading]')) {
    const steps = JSON.parse(root.querySelector('.diagram-reading-data').textContent);
    const modes = [...root.querySelectorAll('[data-diagram-mode]')];
    const reader = root.querySelector('.diagram-reader');
    const full = root.querySelector('.diagram-reading-full');
    const previous = root.querySelector('[data-diagram-prev]');
    const next = root.querySelector('[data-diagram-next]');
    let index = 0, chosen = false;
    function render() {
      root.querySelector('[data-diagram-step-title]').textContent = steps[index][0];
      root.querySelector('[data-diagram-step-copy]').textContent = steps[index][1];
      root.querySelector('[data-diagram-position]').textContent = `${index + 1} / ${steps.length}`;
      previous.disabled = index === 0;
      next.disabled = index === steps.length - 1;
    }
    function mode(value) {
      root.dataset.readingMode = value;
      reader.hidden = value !== 'guide';
      full.hidden = value !== 'whole';
      for (const button of modes) button.setAttribute('aria-pressed', String(button.dataset.diagramMode === value));
    }
    function adapt() {
      if (!chosen && root.clientWidth) mode(root.clientWidth < Number(root.dataset.minReadableWidth) ? 'guide' : 'whole');
    }
    for (const button of modes) button.addEventListener('click', () => { chosen = true; mode(button.dataset.diagramMode); });
    previous.addEventListener('click', () => { index = Math.max(0, index - 1); render(); });
    next.addEventListener('click', () => { index = Math.min(steps.length - 1, index + 1); render(); });
    root.querySelector('.diagram-reading-controls').hidden = false;
    render(); adapt();
    new ResizeObserver(adapt).observe(root);
  }
})();
