(() => {
  const scrollRegions = document.querySelectorAll('.table-scroll, .diagram-scroll');
  const focusScrollableRegions = () => {
    for (const region of scrollRegions) {
      if (region.scrollWidth > region.clientWidth + 1) region.tabIndex = 0;
      else region.removeAttribute('tabindex');
    }
  };
  window.addEventListener('resize', focusScrollableRegions);
  window.addEventListener('load', focusScrollableRegions);
  for (const image of document.querySelectorAll('.diagram-scroll img')) image.addEventListener('load', focusScrollableRegions);
  focusScrollableRegions();

  const dialog = document.querySelector('#diagram-dialog');
  const image = document.querySelector('#dialog-image');
  let opener;
  document.querySelectorAll('.diagram-open').forEach(link => {
    link.addEventListener('click', event => {
      if (typeof dialog.showModal !== 'function') return;
      event.preventDefault();
      opener = link;
      document.querySelector('#dialog-title').textContent = link.dataset.title;
      const source = link.closest('figure').querySelector('img');
      image.src = link.href;
      image.alt = source.alt;
      document.querySelector('#diagram-download').href = link.href;
      dialog.showModal();
    });
  });
  dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => opener?.focus());
})();
