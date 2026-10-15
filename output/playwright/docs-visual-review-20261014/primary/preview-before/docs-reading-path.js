/* Reading notes are local to this browser; documentation remains static HTML. */
(() => {
  const path = document.querySelector('[data-reading-path]');
  if (!path) return;
  const steps = [...path.querySelectorAll('[data-step]')];
  const storageKey = `cyberalchemy-preview-reading-v1:${path.dataset.readingPath}`;
  const status = path.querySelector('[data-reading-status]');
  const reset = path.querySelector('[data-reset-reading]');
  let read = new Set();
  let storageAvailable = true;

  function parse(value) {
    try {
      const ids = JSON.parse(value);
      return new Set(Array.isArray(ids) ? ids.filter(id => steps.some(step => step.dataset.step === id)) : []);
    } catch (_) { return new Set(); }
  }
  try { read = parse(localStorage.getItem(storageKey)); }
  catch (_) { storageAvailable = false; }

  function render() {
    steps.forEach(step => {
      const done = read.has(step.dataset.step);
      const button = step.querySelector('[data-mark-read]');
      step.dataset.read = String(done);
      button.setAttribute('aria-pressed', String(done));
      button.firstChild.textContent = done ? 'Mark as unread' : 'Mark as read';
      step.querySelector('[data-step-state]').textContent = done ? 'Read' : '';
    });
    status.textContent = `${read.size} of ${steps.length} steps read${read.size === steps.length ? ' · Reading path complete' : ''}`;
    reset.disabled = read.size === 0;
    path.querySelector('[data-reading-storage]').textContent = storageAvailable
      ? 'Reading progress is saved in this browser.'
      : 'Reading progress is available for this visit; browser storage is unavailable.';
  }
  function save() {
    try { localStorage.setItem(storageKey, JSON.stringify([...read])); }
    catch (_) { storageAvailable = false; }
    render();
  }
  steps.forEach(step => {
    const button = step.querySelector('[data-mark-read]');
    button.hidden = false;
    button.addEventListener('click', () => {
      const id = step.dataset.step;
      if (read.has(id)) read.delete(id); else read.add(id);
      save();
    });
  });
  reset.hidden = false;
  reset.addEventListener('click', () => { read.clear(); save(); });
  path.querySelector('.docs-reading-progress').hidden = false;
  render();
  function revealStep() {
    const step = steps.find(item => `#${item.id}` === location.hash);
    if (step) step.open = true;
  }
  revealStep();
  window.addEventListener('hashchange', revealStep);
  window.addEventListener('storage', event => {
    if (event.key === storageKey || event.key === null) {
      read = parse(event.newValue);
      render();
    }
  });
})();
