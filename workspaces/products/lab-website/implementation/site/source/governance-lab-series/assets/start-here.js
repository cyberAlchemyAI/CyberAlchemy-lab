/* Optional navigation enhancement; the complete introduction is static HTML. */
(() => {
  for (const [id, query] of [['start-browse', '(max-width:900px)'], ['start-toc', '(max-width:1200px)']]) {
    const details = document.getElementById(id);
    if (!details) continue;
    const media = matchMedia(query);
    details.open = !media.matches;
    media.addEventListener('change', event => { details.open = !event.matches; });
  }
  if (!('IntersectionObserver' in window)) return;
  const links = [...document.querySelectorAll('#start-toc a')];
  const observer = new IntersectionObserver(entries => {
    const current = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
    if (!current) return;
    for (const link of links) {
      if (link.hash === '#' + current.target.id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  }, { rootMargin: '-110px 0px -60% 0px' });
  document.querySelectorAll('.start-content section[id]').forEach(section => observer.observe(section));
})();
