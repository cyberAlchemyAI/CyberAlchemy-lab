/* An expanded SVG camera. The original stage and inspector are moved, never cloned. */
(() => {
  const root = document.getElementById('system-map');
  const dialog = document.getElementById('map-canvas-dialog');
  if (!root || !dialog || typeof dialog.showModal !== 'function') return;
  const get = id => document.getElementById(id);
  const stage = root.querySelector('.smap-stage');
  const inspector = get('map-inspector');
  const expand = get('map-expand');
  const model = JSON.parse(get('system-map-data').textContent);
  const view = get('map-canvas-view'), lens = get('map-canvas-lens');
  const details = get('map-canvas-details');
  const originals = new Map([...stage.querySelectorAll('.smap-diagram')].map(svg => [svg, svg.getAttribute('viewBox')]));
  const camera = { x: 580, y: 325, zoom: 1 };
  const pointers = new Map();
  const compact = matchMedia('(max-width: 1000px)');
  let svg, stageHome, inspectorHome, opener, savedPresentation, savedScroll;
  let active = false, dragged = false, suppressClick = false, pinch = null;

  function graph() {
    const id = root.querySelector('[data-map-view][aria-pressed="true"]').dataset.mapView;
    const current = model.views.find(v => v.id === id);
    const key = root.querySelector('[data-governance-focus][aria-pressed="true"]')?.dataset.governanceFocus;
    return { current, layout: current.focus_views?.find(v => v.focus_key === key) || current };
  }
  function activeSVG() { return [...originals.keys()].find(el => el.getBoundingClientRect().width > 0); }
  function bounds() {
    const [x, y, width, height] = originals.get(svg).split(/[,\s]+/).map(Number);
    return { x, y, width, height };
  }
  function scale() {
    if (!svg) return 1;
    const b = bounds();
    return Math.max(.01, Math.min(Math.max(1, stage.clientWidth - 32) / b.width, Math.max(1, stage.clientHeight - 32) / b.height)) * camera.zoom;
  }
  function render() {
    if (!active || !svg || !stage.clientWidth || !stage.clientHeight) return;
    const s = scale(), w = stage.clientWidth / s, h = stage.clientHeight / s;
    svg.setAttribute('viewBox', `${camera.x - w / 2} ${camera.y - h / 2} ${w} ${h}`);
    get('map-canvas-zoom').textContent = Math.round(camera.zoom * 100) + '%';
    get('map-canvas-minus').disabled = camera.zoom <= .4;
    get('map-canvas-plus').disabled = camera.zoom >= 4;
    get('map-canvas-focus').disabled = !graph().layout.placements.some(p => p.node === get('map-node-picker').value);
  }
  function fit() {
    if (!active) return;
    svg = activeSVG();
    if (!svg) return;
    const b = bounds();
    camera.x = b.x + b.width / 2; camera.y = b.y + b.height / 2; camera.zoom = 1;
    render();
  }
  function zoomTo(value, clientX, clientY) {
    if (!svg) return;
    const r = stage.getBoundingClientRect(), x = (clientX ?? r.left + r.width / 2) - r.left - r.width / 2;
    const y = (clientY ?? r.top + r.height / 2) - r.top - r.height / 2;
    const old = scale(), worldX = camera.x + x / old, worldY = camera.y + y / old;
    camera.zoom = Math.max(.4, Math.min(4, value));
    camera.x = worldX - x / scale(); camera.y = worldY - y / scale(); render();
  }
  function focusSelection() {
    const node = graph().layout.placements.find(p => p.node === get('map-node-picker').value);
    if (!node || !svg) return;
    camera.zoom = 1;
    const targetScale = Math.min(440, stage.clientWidth * .64) / node.width;
    camera.zoom = Math.max(1.25, Math.min(4, targetScale / scale()));
    camera.x = node.x + node.width / 2; camera.y = node.y + node.height / 2;
    render();
  }
  function sync() {
    if (!active) return;
    const { current, layout } = graph();
    view.value = current.id;
    get('map-canvas-lens-field').hidden = !current.focus_views;
    lens.replaceChildren(...(current.focus_views || []).map(f => new Option(f.title, f.focus_key)));
    if (current.focus_views) lens.value = layout.focus_key;
    const selected = model.nodes[get('map-node-picker').value];
    get('map-canvas-selection').textContent = selected ? ' · ' + selected.title : '';
    const next = activeSVG();
    if (next !== svg) fit(); else render();
  }
  function setDetails(open) {
    details.dataset.open = String(open);
    dialog.dataset.detailsOpen = String(open);
    get('map-canvas-details-toggle').setAttribute('aria-expanded', String(open));
    get('map-canvas-details-label').textContent = open ? 'Hide details' : 'Show details';
    get('map-canvas-inspector').hidden = !open;
    requestAnimationFrame(render);
  }
  function openCanvas(event) {
    if (active) { sync(); return; }
    opener = event?.detail?.opener || document.activeElement;
    savedScroll = { x: scrollX, y: scrollY };
    savedPresentation = get('map-list-mode').getAttribute('aria-pressed') === 'true' ? 'list' : get('map-guide-mode').getAttribute('aria-pressed') === 'true' ? 'guide' : 'diagram';
    stageHome = document.createComment('Inline system map'); inspectorHome = document.createComment('Inline concept details');
    stage.before(stageHome); inspector.before(inspectorHome);
    active = true; root.dataset.mapExpanded = 'true'; expand.setAttribute('aria-expanded', 'true');
    root.dispatchEvent(new CustomEvent('lab:mapcanvasopen'));
    get('map-canvas-stage').append(stage); get('map-canvas-inspector').append(inspector);
    setDetails(!compact.matches);
    document.documentElement.classList.add('map-canvas-open'); document.body.classList.add('map-canvas-open');
    dialog.showModal(); sync();
    requestAnimationFrame(() => { fit(); if (event?.detail?.focusSelection) focusSelection(); stage.focus({ preventScroll: true }); });
  }
  function cleanup(navigation = false) {
    if (!active) return;
    active = false;
    for (const [element, original] of originals) element.setAttribute('viewBox', original);
    stageHome.replaceWith(stage); inspectorHome.replaceWith(inspector);
    delete root.dataset.mapExpanded; expand.setAttribute('aria-expanded', 'false');
    pointers.clear(); pinch = null; dragged = false; stage.classList.remove('is-dragging');
    document.documentElement.classList.remove('map-canvas-open'); document.body.classList.remove('map-canvas-open');
    root.dispatchEvent(new CustomEvent('lab:mapcanvasclose', { detail: { presentation: savedPresentation } }));
    if (!navigation) {
      (opener?.isConnected && opener.getClientRects().length ? opener : expand).focus({ preventScroll: true });
      window.scrollTo({ left: savedScroll.x, top: savedScroll.y, behavior: 'instant' });
    }
  }
  function close(navigation = false) { dialog.close(); cleanup(navigation); }
  for (const v of model.views) view.add(new Option(v.title, v.id));
  view.addEventListener('change', () => root.dispatchEvent(new CustomEvent('lab:mapcanvasview', { detail: { id: view.value } })));
  lens.addEventListener('change', () => root.dispatchEvent(new CustomEvent('lab:mapcanvaslens', { detail: { key: lens.value } })));
  expand.hidden = false;
  expand.addEventListener('click', () => openCanvas());
  root.addEventListener('lab:mapexpand', openCanvas);
  document.addEventListener('lab:mapnavigate', sync);
  get('map-canvas-close').addEventListener('click', () => close());
  dialog.addEventListener('close', () => cleanup());
  dialog.addEventListener('click', event => {
    const r = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom)) close();
  });
  document.addEventListener('click', event => { if (active && dialog.contains(event.target) && event.target.closest('a[href]')) close(true); }, true);
  get('map-canvas-minus').addEventListener('click', () => zoomTo(camera.zoom / 1.25));
  get('map-canvas-plus').addEventListener('click', () => zoomTo(camera.zoom * 1.25));
  get('map-canvas-fit').addEventListener('click', fit);
  get('map-canvas-focus').addEventListener('click', focusSelection);
  stage.addEventListener('click', event => {
    if (suppressClick) { event.preventDefault(); event.stopImmediatePropagation(); suppressClick = false; return; }
    if (!active && !event.target.closest('[data-map-node]')) openCanvas();
  }, true);
  stage.addEventListener('keydown', event => {
    if (!active) { if (event.target === stage && ['Enter', ' '].includes(event.key)) { event.preventDefault(); openCanvas(); } return; }
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    const deltas = { ArrowLeft: [-48, 0], ArrowRight: [48, 0], ArrowUp: [0, -48], ArrowDown: [0, 48] };
    if (deltas[event.key]) { event.preventDefault(); const [x, y] = deltas[event.key]; camera.x += x / scale(); camera.y += y / scale(); render(); }
    else if (['+', '='].includes(event.key)) { event.preventDefault(); zoomTo(camera.zoom * 1.25); }
    else if (event.key === '-') { event.preventDefault(); zoomTo(camera.zoom / 1.25); }
    else if (event.key === '0') { event.preventDefault(); fit(); }
  });
  stage.addEventListener('focusin', event => {
    const node = event.target.closest('[data-map-node]');
    if (!active || !node?.matches(':focus-visible')) return;
    const r = node.getBoundingClientRect(), frame = stage.getBoundingClientRect();
    if (r.left >= frame.left + 8 && r.right <= frame.right - 8 && r.top >= frame.top + 8 && r.bottom <= frame.bottom - 8) return;
    const placement = graph().layout.placements.find(p => p.node === node.dataset.mapNode);
    if (placement) {
      camera.x = placement.x + placement.width / 2;
      camera.y = placement.y + placement.height / 2;
      render();
    }
  });
  stage.addEventListener('wheel', event => { if (active) { event.preventDefault(); zoomTo(camera.zoom * Math.exp(-event.deltaY * .002), event.clientX, event.clientY); } }, { passive: false });
  function pinchState() {
    const [a, b] = [...pointers.values()];
    return a && b ? { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, distance: Math.hypot(a.x - b.x, a.y - b.y) } : null;
  }
  stage.addEventListener('pointerdown', event => {
    if (!active || event.button !== 0) return;
    if (!pointers.size) { dragged = false; suppressClick = false; }
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY, startX: event.clientX, startY: event.clientY });
    if (!event.target.closest('[data-map-node]')) stage.setPointerCapture(event.pointerId);
    pinch = pinchState();
  });
  stage.addEventListener('pointermove', event => {
    if (!active || !pointers.has(event.pointerId)) return;
    const previous = pointers.get(event.pointerId);
    pointers.set(event.pointerId, { ...previous, x: event.clientX, y: event.clientY });
    if (pointers.size > 1) {
      const next = pinchState();
      if (pinch && next && pinch.distance > 0) {
        zoomTo(camera.zoom * next.distance / pinch.distance, pinch.x, pinch.y);
        camera.x -= (next.x - pinch.x) / scale(); camera.y -= (next.y - pinch.y) / scale(); render(); dragged = true;
      }
      pinch = next;
    } else if (dragged || Math.hypot(event.clientX - previous.startX, event.clientY - previous.startY) > 5) {
      dragged = true; camera.x -= (event.clientX - previous.x) / scale(); camera.y -= (event.clientY - previous.y) / scale(); render();
    }
    if (dragged) { event.preventDefault(); stage.setPointerCapture(event.pointerId); stage.classList.add('is-dragging'); }
  });
  function release(event) {
    if (!pointers.has(event.pointerId)) return;
    pointers.delete(event.pointerId); pinch = pinchState();
    if (dragged) suppressClick = true;
    if (!pointers.size) { stage.classList.remove('is-dragging'); setTimeout(() => { suppressClick = false; }, 0); }
  }
  stage.addEventListener('pointerup', release); stage.addEventListener('pointercancel', release); stage.addEventListener('lostpointercapture', release);
  new ResizeObserver(() => { if (active) render(); }).observe(stage);
  get('map-canvas-details-toggle').addEventListener('click', () => setDetails(details.dataset.open !== 'true'));
  compact.addEventListener('change', () => { if (active) { setDetails(!compact.matches); requestAnimationFrame(render); } });
})();
