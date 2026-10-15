// Shared, preview-only appearance preference; runs before the page is painted.
(() => {
  let mode = 'light';
  try { mode = localStorage.getItem('cyberalchemy-paper-preview-theme') || mode; } catch (_) {}
  const requested = new URLSearchParams(location.search).get('mode');
  if (requested === 'light' || requested === 'dark') mode = requested;
  document.documentElement.dataset.theme = mode === 'dark' ? 'dark' : 'light';
  document.documentElement.dataset.palette = 'paper';
})();
