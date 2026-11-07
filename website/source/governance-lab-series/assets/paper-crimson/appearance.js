(() => {
  const base = new URL('.', document.currentScript.src);
  const root = document.documentElement;
  const header = document.querySelector('.topbar-inner');
  if (!header) return;
  const brand = header.querySelector('.brand,.research-brand');
  header.querySelectorAll('nav a').forEach(link => {
    if (link.textContent.trim() === 'Guide') {
      link.href = new URL('../../start-here.html', base).href;
    }
  });
  if (brand && !brand.querySelector('img')) {
    const logo = document.createElement('img');
    logo.alt = 'CyberAlchemy Lab';
    logo.width = 176;
    logo.height = 41;
    brand.replaceChildren(logo);
  }
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'site-theme-toggle';
  button.innerHTML = '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M20 14A8 8 0 0 1 10 4a8 8 0 1 0 10 10Z"/></svg>';
  function setTheme(dark) {
    root.dataset.theme = dark ? 'dark' : 'light';
    button.setAttribute('aria-pressed', String(dark));
    button.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} theme`);
    header.querySelectorAll('.brand img,.research-brand img').forEach(img => {
      img.src = new URL(`logo${dark ? '-dark' : ''}.svg`, base).href;
    });
  }
  setTheme(root.dataset.theme === 'dark');
  button.addEventListener('click', () => {
    const dark = root.dataset.theme !== 'dark';
    setTheme(dark);
    try { localStorage.setItem('cyberalchemy-paper-theme', dark ? 'dark' : 'light'); } catch (_) {}
  });
  header.append(button);
  // Keep overflowing code reachable by keyboard, including after a chapter
  // switch or viewport resize. Fitted blocks do not add extra tab stops.
  const codeBlocks = [...document.querySelectorAll('pre[data-code-scroll]')];
  function syncCodeFocus(block) {
    const overflow = block.clientWidth > 0 &&
      (block.scrollWidth > block.clientWidth + 1 || block.scrollHeight > block.clientHeight + 1);
    if (overflow) {
      block.tabIndex = 0;
      if (!block.hasAttribute('role')) {
        block.setAttribute('role', 'region'); block.dataset.codeScrollRole = 'true';
      }
      if (!block.hasAttribute('aria-label') && !block.hasAttribute('aria-labelledby')) {
        block.setAttribute('aria-label', 'Scrollable code example'); block.dataset.codeScrollLabel = 'true';
      }
    } else {
      block.removeAttribute('tabindex');
      if (block.dataset.codeScrollRole) { block.removeAttribute('role'); delete block.dataset.codeScrollRole; }
      if (block.dataset.codeScrollLabel) { block.removeAttribute('aria-label'); delete block.dataset.codeScrollLabel; }
    }
  }
  if ('ResizeObserver' in window) {
    const codeObserver = new ResizeObserver(entries => entries.forEach(entry => syncCodeFocus(entry.target)));
    codeBlocks.forEach(block => codeObserver.observe(block));
  } else {
    window.addEventListener('resize', () => codeBlocks.forEach(syncCodeFocus));
  }
  codeBlocks.forEach(syncCodeFocus);
  document.fonts.ready.then(() => codeBlocks.forEach(syncCodeFocus));
  // Keep theme preference synchronized across other open website tabs.
  window.addEventListener('storage', event => {
    if (event.key === 'cyberalchemy-paper-theme') setTheme(event.newValue === 'dark');
  });
})();
