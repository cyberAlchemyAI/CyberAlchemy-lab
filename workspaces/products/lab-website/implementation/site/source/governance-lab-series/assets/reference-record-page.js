/* Lightweight behavior for static record pages. Exact records need no chapter controller. */
(() => {
  if (document.body.dataset.docsEnhanced !== 'record') return;
  const record = document.querySelector('.record-page');
  const browse = document.querySelector('.article-tree .article-contents');
  const outline = document.querySelector('.docs-toc');
  const bindDisclosure = (element, query) => {
    if (!element) return;
    const media = matchMedia(query);
    element.open = !media.matches;
    media.addEventListener('change', event => { element.open = !event.matches; });
  };
  bindDisclosure(browse, '(max-width:900px)');
  bindDisclosure(outline, '(max-width:1200px)');
  const links = [...document.querySelectorAll('.docs-toc nav a')];
  const targetFor = link => document.getElementById(decodeURIComponent(link.hash.slice(1)));
  const targets = links.map(link => ({ link, target: targetFor(link) })).filter(item => item.target);
  let pending = false;
  const updateOutline = () => {
    pending = false;
    const top = (document.querySelector('.topbar')?.getBoundingClientRect().height || 0) + 60;
    let active = targets[0];
    for (const item of targets) {
      const element = item.target === record ? record.querySelector('h1') : item.target;
      if (element.getClientRects().length && element.getBoundingClientRect().top <= top) active = item;
    }
    for (const item of targets) {
      if (item === active) item.link.setAttribute('aria-current', 'location');
      else item.link.removeAttribute('aria-current');
    }
  };
  const schedule = () => {
    if (!pending) { pending = true; requestAnimationFrame(updateOutline); }
  };
  const revealFragment = () => {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = (id ? document.getElementById(id) : null);
    if (!target || !record.contains(target)) return;
    for (let detail = target.closest('details'); detail; detail = detail.parentElement?.closest('details')) detail.open = true;
    requestAnimationFrame(() => { target.scrollIntoView({ block: 'start' }); schedule(); });
  };
  window.addEventListener('hashchange', revealFragment);
  window.addEventListener('scroll', schedule, { passive: true });
  record.addEventListener('toggle', schedule, true);
  revealFragment();
  schedule();
})();
