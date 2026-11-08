/* Exact legacy fragment destinations, with ordinary visible HTML fallbacks. */
(() => {
  function followMovedFragment() {
    let identity;
    try { identity = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    const destination = document.getElementById(identity)?.dataset.migratedTo;
    if (!destination) return;
    const target = new URL(destination, location.href);
    // Keep appearance and other caller query parameters, including file delivery.
    target.search = location.search;
    if (target.origin === location.origin && target.pathname === location.pathname) {
      // A native smooth scroll towards the alias can outlive a second hash
      // navigation. Resolve its URL without starting a competing animation.
      try { history.replaceState(null, '', target.href); }
      catch (_) { location.replace(target.href); }
      const reveal = () => document.getElementById(decodeURIComponent(target.hash.slice(1)))
        ?.scrollIntoView({block: 'start', behavior: 'instant'});
      reveal();
      requestAnimationFrame(reveal);
      return;
    }
    location.replace(target.href);
  }
  followMovedFragment();
  window.addEventListener('hashchange', followMovedFragment);
})();
