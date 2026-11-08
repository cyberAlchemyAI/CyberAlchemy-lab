/* Exact library navigation, title-first search and an offline static fallback. */
(() => {
  const scriptBase=new URL('./',document.currentScript.src);
  const library = document.querySelector('.resource-shelf');
  if (!library) return;
  const panels = [...library.querySelectorAll('[data-panel]')];
  const buttons = [...library.querySelectorAll('[data-select]')];
  const search = library.querySelector('#catalog-search');
  const scope = library.querySelector('#catalog-search-scope');
  const searchHelp=library.querySelector('.search-help');searchHelp.setAttribute('role','status');
  const retry=document.createElement('button');retry.type='button';retry.textContent='Retry complete-record search';retry.hidden=true;
  retry.className='catalog-retry';retry.addEventListener('click',filter);searchHelp.after(retry);
  const entries = new Map(panels.map(p => [p, [...p.querySelectorAll('.catalog-item')].map(row => ({row, title:row.dataset.title, reference:(row.querySelector('.record-id,.catalog-identity')?.textContent||'').trim().toLowerCase()}))]));
  let fullTextLoading=null;
  function loadFullText(){
    if(window.LabReferenceSearchText)return Promise.resolve();
    if(fullTextLoading)return fullTextLoading;
    fullTextLoading=new Promise((resolve,reject)=>{
      const script=document.createElement('script');script.src=new URL('reference-search-data.js',scriptBase);
      const fail=()=>{clearTimeout(timer);script.remove();fullTextLoading=null;reject(new Error('The complete-record search data did not load.'));};
      const timer=setTimeout(fail,20000);
      script.onload=async()=>{try{await(window.LabReferenceSearchTextReady||Promise.resolve(window.LabReferenceSearchText));clearTimeout(timer);resolve();}catch(error){fail();}};
      script.onerror=fail;
      document.head.append(script);
    });return fullTextLoading;
  }
  function browseAll(){search.value='';filter();search.focus();}
  panels.forEach(panel=>{
    const empty=document.createElement('div');empty.className='catalog-empty';empty.hidden=true;
    const p=document.createElement('p');p.textContent='No records match. Try a shorter term, search complete records, or browse this catalog.';
    const reset=document.createElement('button');reset.type='button';reset.textContent='Browse all records';reset.addEventListener('click',browseAll);
    empty.append(p,reset);panel.querySelector('.result-count').after(empty);
  });
  function select(name) {
    panels.forEach(p => p.hidden = p.dataset.panel !== name);
    buttons.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.select === name)));
  }
  function filter() {
    const q = search.value.trim().toLocaleLowerCase();
    retry.hidden=true;
    search.setAttribute('aria-busy','false');
    if(q&&scope.value==='all'&&!window.LabReferenceSearchText){
      search.setAttribute('aria-busy','true');searchHelp.textContent='Loading complete-record search…';
      loadFullText().then(()=>{searchHelp.textContent='Exact titles appear first, followed by title matches and references in other records.';filter();}).catch(()=>{
        search.setAttribute('aria-busy','false');
        if(!search.value.trim()||scope.value!=='all')return;
        searchHelp.textContent='Complete-record search is unavailable. Search titles, clear the query or retry.';retry.hidden=false;
      });
      return;
    }
    panels.forEach(panel => {
      let count = 0;
      const rows=entries.get(panel).map(e=>({...e,rank:!q?0:e.title===q||e.reference===q?0:e.title.startsWith(q)?1:e.title.includes(q)?2:3,match:!q||e.title.includes(q)||(scope.value==='all'&&(window.LabReferenceSearchText?.[e.row.id]||e.row.dataset.search).includes(q))})).sort((a,b)=>a.rank-b.rank||a.title.localeCompare(b.title));
      rows.forEach(({row,rank,match})=>{
        row.hidden=!match;if(match)count++;
        let note=row.querySelector('.search-match');
        if(q&&match){if(!note){note=document.createElement('small');note.className='search-match';row.querySelector('.catalog-title').append(note);}note.textContent=rank===0?'Exact title or identity':rank<3?'Title match':'Mentioned in this record';}else if(note)note.remove();
        panel.append(row);
      });
      panel.querySelector('.result-count').textContent = `${count} of ${rows.length} records${q ? ' match this search' : ''}`;
      panel.querySelector('.catalog-empty').hidden=count!==0;
    });
  }
  buttons.forEach(b => b.addEventListener('click', () => {
    select(b.dataset.select);
    if (document.body.dataset.docsEnhanced === 'library') {
      document.dispatchEvent(new CustomEvent('lab:catalognavigate', {detail:{id:'catalog-'+b.dataset.select}}));
    } else {
      const url=new URL(location.href);url.hash='catalog-'+b.dataset.select;history.replaceState(null,'',url);
    }
  }));
  search.addEventListener('input', filter);
  scope.addEventListener('change',filter);
  library.querySelector('#clear-search').addEventListener('click',browseAll);
  function revealHash(scroll = true) {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (!target || !library.contains(target)) return;
    const panel = target.closest('.catalog-panel');
    if (panel) { search.value = ''; filter(); select(panel.dataset.panel); }
    let node = target;
    while (node) { if (node.tagName === 'DETAILS') node.open = true; node = node.parentElement; }
    if (scroll) requestAnimationFrame(() => target.scrollIntoView({ block: 'start', behavior:'instant' }));
  }
  // The documentation adapter owns routing; catalog semantics stay here.
  window.LabReferenceCatalog = {select, filter, revealHash};
  select('definitions'); filter();
  document.getElementById('catalog-library').open=true;
  addEventListener('hashchange', () => {if (document.body.dataset.docsEnhanced !== 'library') revealHash();});
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (link && link.hash === location.hash && document.body.dataset.docsEnhanced !== 'library') revealHash();
  });
  revealHash();
  const controls=library.querySelector('.catalog-controls');
  const offset=()=>library.style.setProperty('--catalog-anchor-offset',(controls.getBoundingClientRect().height+32)+'px');
  offset();new ResizeObserver(offset).observe(controls);
})();
