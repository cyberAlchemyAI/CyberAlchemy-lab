(() => {
  const base = new URL('.', document.currentScript.src);
  const root = document.documentElement;
  const header = document.querySelector('.topbar-inner');
  if (!header) return;
  const brand = header.querySelector('.brand,.research-brand');
  if (brand && !brand.querySelector('img')) {
    const logo = document.createElement('img');
    logo.alt = 'CyberAlchemy Lab';
    logo.width = 176;
    logo.height = 41;
    brand.replaceChildren(logo);
  }
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'preview-theme-toggle';
  button.innerHTML = '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M20 14A8 8 0 0 1 10 4a8 8 0 1 0 10 10Z"/></svg>';
  function setTheme(dark) {
    root.dataset.theme = dark ? 'dark' : 'light';
    button.setAttribute('aria-pressed', String(dark));
    button.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} theme`);
    header.querySelectorAll('.brand img,.research-brand img').forEach(img => {
      img.src = new URL(`assets/logo${dark ? '-dark' : ''}.svg`, base).href;
    });
  }
  setTheme(root.dataset.theme === 'dark');
  button.addEventListener('click', () => {
    const dark = root.dataset.theme !== 'dark';
    setTheme(dark);
    try { localStorage.setItem('cyberalchemy-paper-preview-theme', dark ? 'dark' : 'light'); } catch (_) {}
  });
  header.append(button);
  // Keep theme preference synchronized if the comparison is open in another tab.
  window.addEventListener('storage', event => {
    if (event.key === 'cyberalchemy-paper-preview-theme') setTheme(event.newValue === 'dark');
  });
})();
