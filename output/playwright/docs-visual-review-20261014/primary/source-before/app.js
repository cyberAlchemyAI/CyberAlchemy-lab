(() => {
  const root = document.documentElement;
  const toggle = document.querySelector('.theme');
  const params = new URLSearchParams(location.search);
  const palette = 'paper';
  root.dataset.palette = palette;
  function setTheme(dark) {
    const mode = dark ? 'dark' : 'light';
    root.dataset.theme = mode;
    toggle.setAttribute('aria-pressed', String(dark));
    toggle.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} theme`);
    document.querySelector('.brand img').src = `assets/logo${dark ? '-dark' : ''}.svg`;
    document.querySelector('.hero-art img').src = `assets/knot-${palette}-${mode}.svg`;
  }
  let mode = 'light';
  try { mode = localStorage.getItem('cyberalchemy-paper-preview-theme') || mode; } catch (_) {}
  if (['light','dark'].includes(params.get('mode'))) mode = params.get('mode');
  setTheme(mode === 'dark');
  toggle.addEventListener('click', () => {
    const dark = root.dataset.theme !== 'dark';
    setTheme(dark);
    try { localStorage.setItem('cyberalchemy-paper-preview-theme', dark ? 'dark' : 'light'); } catch (_) {}
  });

  const stages = {
    meaning: {type: 'DEFINITION', title: 'Start with what<br>the work means.', text: 'Make the requirement and its terms explicit. The team and its agents need the same reference before they examine what happened.'},
    work: {type: 'WORK', title: 'Make the attempt<br>inspectable.', text: 'Connect the attempted export to its requirement and the work around it. Keep the intended result separate from what actually happened.'},
    evidence: {type: 'EVIDENCE', title: 'Keep the finding<br>with its context.', text: 'Examine the export and record the reported omission. Evidence connects the observation to the requirement it was checked against.'},
    decision: {type: 'DECISION', title: 'Give the next step<br>a reason.', text: 'Use the recorded requirement, attempt and evidence to explain what should happen next. Keep the decision connected to its basis.'}
  };
  const tabs = [...document.querySelectorAll('[role=tab]')];
  function select(tab, focus = false) {
    const index = tabs.indexOf(tab), key = tab.dataset.stage, stage = stages[key];
    tabs.forEach(item => { const chosen = item === tab; item.setAttribute('aria-selected', String(chosen)); item.tabIndex = chosen ? 0 : -1; });
    document.querySelector('#demo-panel').setAttribute('aria-labelledby', tab.id);
    document.querySelector('#stage-type').textContent = stage.type;
    document.querySelector('#stage-number').textContent = `0${index + 1} / 04`;
    document.querySelector('#stage-title').innerHTML = stage.title;
    document.querySelector('#stage-copy').textContent = stage.text;
    document.querySelectorAll('[data-record]').forEach(row => {
      const selected = row.dataset.record === key;
      row.classList.toggle('active', selected);
      row.querySelector('.record-state').textContent = selected ? 'SELECTED' : 'LINKED';
    });
    if (focus) tab.focus();
  }
  tabs.forEach(tab => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', event => {
      const index = tabs.indexOf(tab);
      const next = {ArrowRight: (index + 1) % tabs.length, ArrowLeft: (index + tabs.length - 1) % tabs.length, Home: 0, End: tabs.length - 1}[event.key];
      if (next !== undefined) { event.preventDefault(); select(tabs[next], true); }
    });
  });
  const more = document.querySelector('.more');
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && more.open) { more.open = false; more.querySelector('summary').focus(); } });
  document.addEventListener('click', event => { if (!more.contains(event.target)) more.open = false; });
  more.querySelectorAll('a').forEach(link => link.addEventListener('click', () => { more.open = false; }));
})();
