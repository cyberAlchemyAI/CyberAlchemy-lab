/* View and neighborhood navigation for the local conceptual map. */
(() => {
  const root = document.getElementById('system-map');
  if (!root) return;
  const model = JSON.parse(document.getElementById('system-map-data').textContent);
  const get = id => document.getElementById(id);
  const picker = get('map-node-picker');
  let current = model.views[0];
  let selected = null;
  let journeyIndex = null;
  let governanceFocus = 'overview';
  let restoring = true;
  let presentation = matchMedia('(max-width:760px)').matches ? 'list' : 'diagram';
  let zoom = 1;
  let fitted = false;

  function openExplorer() { const e=get('map-explorer'); if(e)e.open=true; }
  function ensureFeedback() {
    if(!selected)return;
    requestAnimationFrame(()=>{
      const e=get('map-selection-feedback'),r=e.getBoundingClientRect();
      if(r.top<16 || r.bottom>innerHeight-16)e.scrollIntoView({block:'nearest',behavior:'instant'});
    });
  }
  function writeState() {
    if(restoring)return;
    const url=new URL(location.href);
    url.searchParams.set('map-view',current.id);
    for(const key of ['map-lens','map-node','map-step'])url.searchParams.delete(key);
    if(current.focus_views)url.searchParams.set('map-lens',governanceFocus);
    if(selected)url.searchParams.set('map-node',selected);
    if(journeyIndex!==null)url.searchParams.set('map-step',String(journeyIndex+1));
    url.hash='system-map';
    if(url.href!==location.href)history.pushState(null,'',url);
    document.dispatchEvent(new CustomEvent('lab:mapnavigate'));
  }
  function navigate(action) { openExplorer();action();writeState(); }
  function setPresentation(mode) {
    presentation=mode;
    root.querySelector('.smap-stage').hidden=mode==='list';
    root.querySelector('.smap-pan-hint').hidden=mode==='list';
    get('map-relationship-list').hidden=mode!=='list';
    get('map-diagram-mode').setAttribute('aria-pressed',String(mode==='diagram'));
    get('map-list-mode').setAttribute('aria-pressed',String(mode==='list'));
    for(const id of ['map-zoom-out','map-zoom-in','map-fit','map-zoom-status'])get(id).hidden=mode==='list';
    updateZoom();
  }
  function updateZoom() {
    const width=fitted?root.querySelector('.smap-stage').clientWidth:Math.round(1160*zoom);
    root.style.setProperty('--map-diagram-width',width+'px');
    get('map-zoom-status').textContent=fitted?'Fit to panel':Math.round(zoom*100)+'%';
  }
  function updateListSelection() {
    get('map-relationship-list').querySelectorAll('[data-map-select]').forEach(b=>{
      const active=b.dataset.mapSelect===selected;b.setAttribute('aria-pressed',String(active));b.closest('li').classList.toggle('is-selected',active);
    });
  }
  function renderRelationshipList() {
    const list=get('map-relationship-list');list.replaceChildren();
    for(const p of activeGraph().placements) {
      const node=model.nodes[p.node],li=element('li'),button=element('button','smap-family-'+node.family);
      if(node.visual_role)button.dataset.modelConcept=node.visual_role;
      button.append(iconFor(node.id),element('span','',node.title));
      button.type='button';button.dataset.mapSelect=node.id;button.setAttribute('aria-pressed','false');
      button.addEventListener('click',()=>navigate(()=>selectNode(node.id)));
      li.append(button,element('p','',node.subtitle),element('small','',node.kind==='ephemeral'?'Temporary session state':visualLabel(node)));
      const connections=element('ul');
      for(const edge of activeGraph().edges.filter(e=>e.source===node.id||e.target===node.id))connections.append(element('li','',model.nodes[edge.source].title+' — '+edge.label+' → '+model.nodes[edge.target].title));
      if(connections.childElementCount)li.append(connections);
      list.append(li);
    }
    updateListSelection();
  }

  function activeGraph() {
    return current.focus_views ? current.focus_views.find(v => v.focus_key === governanceFocus) : current;
  }

  function activePanel() {
    const panel = get('map-panel-' + current.id);
    return current.focus_views ? panel.querySelector('[data-map-focus="' + governanceFocus + '"]') : panel;
  }

  function updateLegend() {
    const nodes = activeGraph().placements.map(p => model.nodes[p.node]);
    const concepts = new Set(nodes.map(node => node.visual_role).filter(Boolean));
    const families = new Set(nodes.filter(node => !node.visual_role).map(node => node.family));
    root.querySelectorAll('.smap-legend-item').forEach(el => {
      el.hidden = el.dataset.mapConcept ? !concepts.has(el.dataset.mapConcept) : !families.has(el.dataset.mapFamily);
    });
    root.querySelector('.smap-ephemeral-key').hidden = !!current.focus_views;
  }

  function setGovernanceFocus(key) {
    if (!current.focus_views) return;
    governanceFocus = key;
    const graph = activeGraph();
    get('map-panel-governance').querySelectorAll('[data-map-focus]').forEach(p => { p.hidden = p.dataset.mapFocus !== key; });
    root.querySelectorAll('[data-governance-focus]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.governanceFocus === key)));
    get('map-question').textContent = graph.question;
    get('map-summary').textContent = graph.summary;
    updateLegend();
    selectNode(null);
    renderRelationshipList();
  }

  function element(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = text;
    return el;
  }

  function visualLabel(node) {
    return node.visual_role ? model.visual_language.model_roles[node.visual_role].label : model.visual_language.families[node.family].label;
  }

  function endJourney() {
    journeyIndex = null;
    get('map-journey').hidden = true;
  }

  function resetInspector() {
    get('map-node-icon-badge').hidden = true;
    get('map-node-family').textContent = '';
    get('map-node-title').textContent = 'Choose where to begin';
    get('map-node-role').textContent = 'Select a concept to read its role and follow its connections.';
    get('map-node-example').textContent = 'Every concept has a role, an illustrative export example and links to its definitions.';
    get('map-node-boundary').textContent = '';
    get('map-read-section').href = '#' + current.chapter;
    get('map-source-details').hidden = true;
    get('map-node-definitions').replaceChildren();
    get('map-connections').replaceChildren(element('li', '', 'Choose a node to inspect incoming and outgoing connections.'));
  }

  function iconFor(id) {
    const source = get('map-panel-' + current.id).querySelector('[data-map-node="' + id + '"] .smap-node-glyph');
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('class', 'smap-glyph');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    const glyph = source.cloneNode(true);
    glyph.removeAttribute('transform');
    glyph.setAttribute('class', 'smap-glyph');
    svg.append(glyph);
    return svg;
  }

  function highlight() {
    const panel = activePanel();
    const edges = activeGraph().edges.filter(e => e.source === selected || e.target === selected);
    const neighbors = new Set(edges.flatMap(e => [e.source, e.target]));
    panel.querySelectorAll('[data-map-node]').forEach(g => {
      const id = g.dataset.mapNode;
      g.classList.toggle('is-selected', id === selected);
      g.classList.toggle('is-neighbor', selected !== null && id !== selected && neighbors.has(id));
      g.classList.toggle('is-dim', selected !== null && !neighbors.has(id));
      g.setAttribute('aria-pressed', String(id === selected));
    });
    panel.querySelectorAll('[data-edge-index]').forEach(g => {
      const active = g.dataset.source === selected || g.dataset.target === selected;
      g.classList.toggle('is-active', selected !== null && active);
      g.classList.toggle('is-dim', selected !== null && !active);
    });
    updateListSelection();
  }

  function selectNode(id, keepJourney = false) {
    if (id && current.focus_views) {
      const home = current.node_focus[id];
      const isLens = ['authority','provenance','lifecycle','challenge'].includes(id);
      if (!activeGraph().placements.some(p => p.node === id) || (isLens && home !== governanceFocus)) {
        const active=document.activeElement;
        const moveFocus = active && (active.hasAttribute('data-map-node')||active.hasAttribute('data-map-select'));
        const listFocus=active&&active.hasAttribute('data-map-select');
        setGovernanceFocus(home);
        if (moveFocus) (listFocus?get('map-relationship-list').querySelector('[data-map-select="'+id+'"]'):activePanel().querySelector('[data-map-node="' + id + '"]')).focus({ preventScroll: true });
      }
    }
    if (!keepJourney) endJourney();
    selected = id || null;
    picker.value = id || '';
    highlight();
    if (!id) { resetInspector(); return; }
    const node = model.nodes[id];
    const badge = get('map-node-icon-badge');
    badge.className = 'smap-inspector-icon smap-family-' + node.family;
    if(node.visual_role)badge.dataset.modelConcept=node.visual_role;
    else delete badge.dataset.modelConcept;
    badge.hidden = false;
    get('map-node-icon').replaceChildren(...iconFor(id).childNodes);
    get('map-node-family').textContent = visualLabel(node);
    get('map-node-title').textContent = node.title;
    get('map-node-role').textContent = node.role;
    get('map-node-example').textContent = 'Export example · ' + node.example;
    get('map-node-boundary').textContent = node.boundary;
    get('map-read-section').href = '#' + node.chapter;
    const list = get('map-connections');
    list.replaceChildren();
    current.edges.filter(e => e.source === id || e.target === id).forEach(e => {
      const outgoing = e.source === id;
      const other = outgoing ? e.target : e.source;
      const li = element('li');
      const button = element('button', 'smap-connection-button smap-family-' + model.nodes[other].family);
      if(model.nodes[other].visual_role)button.dataset.modelConcept=model.nodes[other].visual_role;
      button.type = 'button';
      button.append(element('span', 'smap-connection-direction', outgoing ? 'OUT →' : 'IN ←'),
                    iconFor(other),
                    element('span', '', model.nodes[other].title));
      button.addEventListener('click', () => navigate(()=>selectNode(other)));
      li.append(button, element('span', 'smap-connection-copy', e.explanation));
      list.append(li);
    });
    const definitions = get('map-node-definitions');
    definitions.replaceChildren();
    node.definitions.forEach(d => {
      const li = element('li');
      const link = element('a', '', d.display_term || d.term);
      link.href = d.href;
      const source = element('a', '', 'Exact source');
      source.href = d.source;
      li.append(link, document.createTextNode(' · ' + d.effective_status + ' · '), source,
                element('span', 'smap-source-binding', d.ref));
      definitions.append(li);
    });
    get('map-source-details').hidden = false;
    if(!restoring)ensureFeedback();
  }

  function setView(id) {
    current = model.views.find(v => v.id === id) || model.views[0];
    endJourney();
    root.querySelectorAll('[data-map-panel]').forEach(p => { p.hidden = p.dataset.mapPanel !== current.id; });
    root.querySelectorAll('[data-map-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.mapView === current.id)));
    get('map-question').textContent = current.question;
    get('map-summary').textContent = current.summary;
    picker.replaceChildren(new Option('Choose a node…', ''));
    current.placements.forEach(p => picker.add(new Option(model.nodes[p.node].title, p.node)));
    get('governance-focus-controls').hidden = !current.focus_views;
    get('map-reset').textContent = current.focus_views ? 'Reset overview' : 'Show all connections';
    if (current.focus_views) setGovernanceFocus('overview');
    else { selectNode(null); updateLegend(); }
    renderRelationshipList();
    get('map-start-example').textContent = 'Follow an incident investigation →';
  }

  function showStep(index) {
    journeyIndex = Math.max(0, Math.min(model.journey.length - 1, index));
    const step = model.journey[journeyIndex];
    get('map-journey').hidden = false;
    get('map-step-title').textContent = step.title;
    get('map-step-copy').textContent = step.text;
    get('map-step-count').textContent = (journeyIndex + 1) + ' / ' + model.journey.length;
    get('map-step-prev').disabled = journeyIndex === 0;
    get('map-step-next').disabled = journeyIndex === model.journey.length - 1;
    selectNode(step.node, true);
  }

  root.querySelectorAll('[data-map-view]').forEach(b => b.addEventListener('click', () => navigate(()=>setView(b.dataset.mapView))));
  root.querySelectorAll('[data-governance-focus]').forEach(b => b.addEventListener('click', () => navigate(()=>setGovernanceFocus(b.dataset.governanceFocus))));
  root.querySelectorAll('[data-map-node]').forEach(g => {
    g.addEventListener('click', () => navigate(()=>selectNode(g.dataset.mapNode)));
    g.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); navigate(()=>selectNode(g.dataset.mapNode)); }
    });
  });
  picker.addEventListener('change', () => navigate(()=>selectNode(picker.value)));
  get('map-reset').addEventListener('click', () => navigate(()=>current.focus_views ? setGovernanceFocus('overview') : selectNode(null)));
  get('map-start-example').addEventListener('click', () => navigate(()=>{setView('overview');showStep(0);}));
  get('map-step-prev').addEventListener('click', () => navigate(()=>showStep(journeyIndex - 1)));
  get('map-step-next').addEventListener('click', () => navigate(()=>showStep(journeyIndex + 1)));
  get('map-step-stop').addEventListener('click', () => navigate(()=>selectNode(null)));
  document.querySelectorAll('[data-map-jump]').forEach(a => a.addEventListener('click', event => {event.preventDefault();navigate(()=>setView(a.dataset.mapJump));root.scrollIntoView({block:'start',behavior:'instant'});}));
  get('map-diagram-mode').addEventListener('click',()=>setPresentation('diagram'));
  get('map-list-mode').addEventListener('click',()=>setPresentation('list'));
  get('map-zoom-out').addEventListener('click',()=>{fitted=false;zoom=Math.max(.5,zoom-.25);updateZoom();});
  get('map-zoom-in').addEventListener('click',()=>{fitted=false;zoom=Math.min(2,zoom+.25);updateZoom();});
  get('map-fit').addEventListener('click',()=>{fitted=true;updateZoom();});
  function restoreURL() {
    restoring=true;
    const params=new URL(location.href).searchParams;
    const view=params.get('map-view');setView(model.views.some(v=>v.id===view)?view:'overview');
    const lens=params.get('map-lens');
    if(current.focus_views&&current.focus_views.some(f=>f.focus_key===lens))setGovernanceFocus(lens);
    const step=Number(params.get('map-step')),node=params.get('map-node');
    if(step>=1&&step<=model.journey.length&&Number.isInteger(step)){setView('overview');showStep(step-1);}
    else if(current.placements.some(p=>p.node===node))selectNode(node);
    if(view||location.hash==='#system-map')openExplorer();
    restoring=false;
    if(selected&&location.hash==='#system-map')ensureFeedback();
  }
  if(matchMedia('(max-width:760px)').matches)get('map-connected-roles').open=false;
  setPresentation(presentation);restoreURL();
  addEventListener('popstate',restoreURL);
  addEventListener('resize',()=>{if(fitted)updateZoom();});
})();
