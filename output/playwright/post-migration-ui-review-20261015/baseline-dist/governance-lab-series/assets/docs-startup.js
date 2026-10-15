/* Prepare chapter pages before exposing their first reading layout.
   No JS leaves the complete article visible. Missing scripts release the
   fallback at load or after a bounded delay. The skip action changes focus,
   never the reader's chapter or browser history. */
(() => {
  const root = document.documentElement;
  root.setAttribute('data-docs-startup', 'pending');
  let released = false;
  const release = () => {
    if (released) return;
    released = true;
    root.removeAttribute('data-docs-startup');
  };
  setTimeout(release, 2500);
  addEventListener('load', () => requestAnimationFrame(() => requestAnimationFrame(release)), {once: true});
  // A script failure must not leave the fallback article hidden.
  addEventListener('error', event => {
    if (event.target?.tagName === 'SCRIPT') release();
  }, true);
  document.addEventListener('click', event => {
    const link = event.target.closest?.('a.skip-link, a.skip');
    if (!link || event.button !== 0 || event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) return;
    const main = document.querySelector('main');
    if (!main) return;
    const header = main.querySelector('.docs-topic-header:not([hidden]) h1');
    const chapter = main.querySelector('[data-docs-chapter]:not([hidden])');
    const target = header || chapter?.querySelector('h1, h2') || main;
    event.preventDefault();
    event.stopImmediatePropagation();
    target.setAttribute('tabindex', '-1');
    target.focus({preventScroll: true});
    target.scrollIntoView({block: 'start', behavior: 'instant'});
  }, true);
})();
