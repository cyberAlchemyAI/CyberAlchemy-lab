/* Former homepage bookmarks now belong to the research page. */
(() => {
  if (document.body.dataset.landing !== 'product') return;
  const routeLegacyBookmark = () => {
    if (!['#why', '#culture', '#research', '#alignment'].includes(location.hash)) return;
    const destination = new URL('research.html', location.href);
    destination.search = location.search;
    destination.hash = location.hash;
    location.replace(destination.href);
  };
  window.addEventListener('hashchange', routeLegacyBookmark);
  routeLegacyBookmark();
})();
