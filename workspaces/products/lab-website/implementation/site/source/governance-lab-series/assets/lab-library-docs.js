/* The library uses the same documentation shell as the visual guide.
   Exact records and essay paragraphs are moved, never rewritten. */
(() => {
  const library = document.querySelector('.resource-shelf');
  const catalog = window.LabReferenceCatalog;
  if (!library || !catalog) return;
  const create = (tag, className, text) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text) el.textContent = text;
    return el;
  };
  const link = (href, label) => {const el = create('a', '', label); el.href = href; return el;};
  const labels = new Map([
    ['reference', ['Reference', 'Reference library']],
    ['library-reading-guide', ['Reference', 'How to use the library']],
    ['catalog-definitions', ['Reference', 'Definitions']],
    ['catalog-types', ['Reference', 'Record formats']],
    ['catalog-relations', ['Reference', 'Connection rules']],
    ['catalog-endpoints', ['Reference', 'Endpoint kinds']],
    ['catalog-history', ['Reference', 'Versions and record facets']],
    ['articles-library', ['Expanded essays', 'Explore the model in depth']],
    ['research', ['Research', 'Sources and open questions']]
  ]);
  const chapters = new Map();
  const essays = [...library.querySelectorAll('article[id^="essay-"]')];
  const essayIndex = create('section', 'docs-essay-index'); essayIndex.id = 'articles-library';
  const essayBody = library.querySelector('#articles-library > .library-body');
  while (essayBody.firstChild && !essayBody.firstChild.matches?.('.reading-layout')) essayIndex.append(essayBody.firstChild);
  const essayNote = essayBody.querySelector('.contents-note');
  if (essayNote) {essayNote.className = 'small docs-session-note'; essayIndex.append(essayNote);}
  const reference = library.querySelector('#reference');
  const controls = library.querySelector('.catalog-controls'); controls.id = 'catalog-search-tools';
  controls.removeAttribute('data-theme');
  const intro = create('div', 'docs-catalog-intro');
  while (reference.firstChild && reference.firstChild !== controls) intro.append(reference.firstChild);
  reference.prepend(intro);
  const historyChapter = create('section', 'docs-catalog-history'); historyChapter.id = 'catalog-history';
  historyChapter.append(library.querySelector('.catalog-extras'));
  const research = library.querySelector('#research');
  // The documentation shell supplies H1; visible research subsections are H2.
  for(const heading of research.querySelectorAll('h3')){
    const replacement=create('h2','docs-reference-subheading');
    for(const attribute of heading.attributes)replacement.setAttribute(attribute.name,attribute.value);
    replacement.append(...heading.childNodes);heading.replaceWith(replacement);
  }
  const readingGuide = library.querySelector('#library-reading-guide');
  for (const node of [reference, readingGuide, historyChapter, essayIndex, ...essays, research]) {
    node.dataset.docsChapter = node.id; chapters.set(node.id, node);
  }
  const subtitles = {
    'essay-1': [[2,'Meaning as a foundation'],[5,'Permission to act'],[7,'Three distinct governance questions'],[9,'How accepted meaning affects future work']],
    'essay-2': [[2,'Trace origins and production'],[4,'From a source to a supported claim'],[7,'What a fingerprint establishes'],[10,'A view for investigation']],
    'essay-3': [[2,'States and kinds of change'],[4,'Proposal, decision and admission'],[7,'Two histories of the result'],[10,'Challenges and the next session']],
    'essay-4': [[2,'Product and capability'],[4,'Project, goal and work'],[6,'Methods and implementation'],[8,'Preparing the right context'],[11,'Continuity through Project State']],
    'essay-5': [[2,'Meaning, structure and representation'],[5,'Resolve the accepted contract'],[6,'Declare the connection'],[8,'Extend the model explicitly'],[11,'Build ontology views']],
    'essay-6': [[2,'Participants and reusable roles'],[4,'Assignment and permission'],[6,'A bounded session'],[7,'Saved knowledge and session memory'],[9,'The current runtime boundary'],[11,'Actions and tools']],
    'essay-7': [[2,'From experience to a proposed lesson'],[4,'Record use and assess benefit'],[5,'Investigate and experiment'],[7,'Failures, incidents and controls'],[9,'Classification and feedback'],[11,'Continuity for the next agent']],
    'essay-8': [[2,'Understand catalog counts'],[4,'The local operational foundation'],[6,'Know the selected source state'],[8,'Ontology implementation and views'],[10,'What still needs to be demonstrated']]
  };
  for (const essay of essays) {
    labels.set(essay.id, [Number(essay.id.split('-')[1]) <= 3 ? 'Governance essays' : 'Lab model essays', essay.querySelector('.article-heading h2').textContent.trim()]);
    const paragraphs = [...essay.querySelector('.prose').children];
    for (const [number, text] of subtitles[essay.id]) {
      const heading = create('h2', 'docs-essay-subheading', text);
      heading.id = `${essay.id}-section-${number}`; paragraphs[number - 1].before(heading);
    }
  }
  const main = document.querySelector('main');
  const layout = create('div', 'docs-library-layout');
  const sidebar = create('aside', 'article-tree docs-library-sidebar');
  sidebar.setAttribute('aria-label', 'Documentation navigation');
  const browse = create('details', 'article-contents');
  const mobile = matchMedia('(max-width:900px)'); browse.open = !mobile.matches;
  mobile.addEventListener('change', event => {browse.open = !event.matches;});
  browse.append(create('summary', '', 'Browse documentation'));
  const nav = create('nav');
  const navLink = (id, text) => {const a = link('#'+id, text || labels.get(id)[1]); a.dataset.libraryRoute = id; return a;};
  nav.append(create('p','tree-label','Getting started'),link('governance-lab-reference.html#start','Lab overview'),link('governance-lab-reference.html#governance','Visual guide'),link('governance-lab-reference.html#system-map','Interactive system map'));
  nav.append(create('p','tree-label','Reference'));
  for (const id of ['reference','library-reading-guide','catalog-definitions','catalog-types','catalog-relations','catalog-endpoints','catalog-history']) nav.append(navLink(id));
  nav.append(create('p','tree-label','Expanded essays'),navLink('articles-library','Series overview'));
  nav.append(create('p','tree-label','Governance'));
  essays.slice(0,3).forEach(essay => nav.append(navLink(essay.id)));
  nav.append(create('p','tree-label','The Lab model'));
  essays.slice(3).forEach(essay => nav.append(navLink(essay.id)));
  nav.append(create('p','tree-label','Research'),navLink('research'));
  browse.append(nav);sidebar.append(browse);
  const tocAside = create('aside','docs-local-nav'); tocAside.setAttribute('aria-label','On this page');
  const toc = create('details','docs-toc'); const compact = matchMedia('(max-width:1200px)'); toc.open = !compact.matches;
  compact.addEventListener('change',event => {toc.open = !event.matches;});
  const tocNav = create('nav');tocNav.setAttribute('aria-label','Headings on this page');
  toc.append(create('summary','','On this page'),tocNav);tocAside.append(toc);
  const header = create('header','docs-topic-header');const breadcrumb = create('p','docs-breadcrumb');const title=create('h1');title.tabIndex=-1;
  header.append(breadcrumb,title);
  const pager = create('nav','docs-pager');pager.setAttribute('aria-label','Previous and next topics');
  library.replaceChildren(header,...chapters.values(),pager);
  library.classList.add('docs-library-content'); library.removeAttribute('aria-labelledby');title.id='docs-library-page-title';
  main.querySelector('.reference-masthead').remove();
  layout.append(sidebar,library,tocAside);main.prepend(layout);
  // A compact index replaces the long record list on the library entrance.
  const catalogIndex = create('nav','docs-reference-index');catalogIndex.setAttribute('aria-label','Browse reference catalogs');
  for (const [id, description] of [['catalog-definitions','What a term means and where it applies.'],['catalog-types','What a record must contain.'],['catalog-relations','Which connections are permitted.'],['catalog-endpoints','Which kinds can appear at either end of a connection.']]) {
    const a=link('#'+id,'');a.append(create('strong','',labels.get(id)[1]),create('span','',description));catalogIndex.append(a);
  }
  // Lookup first; the captured scope, prose and totals remain intact below.
  intro.prepend(catalogIndex);
  document.body.dataset.docsEnhanced='library';
  const aliases = {library:'reference','library-title':'reference','top':'reference','catalog-library':'reference','research-library':'research'};
  const order = ['articles-library',...essays.map(e=>e.id),'reference','library-reading-guide','catalog-definitions','catalog-types','catalog-relations','catalog-endpoints','catalog-history','research'];
  let current = '';
  let observer;
  function routeFor(id) {
    if (labels.has(id)) return id;
    if (aliases[id]) return aliases[id];
    if (id === 'catalog-search-tools') return current.startsWith('catalog-') && current !== 'catalog-history' ? current : 'catalog-definitions';
    const target=(id ? document.getElementById(id) : null);
    if (target?.closest('.catalog-panel')) return target.closest('.catalog-panel').id;
    return target?.closest('[data-docs-chapter]')?.dataset.docsChapter || 'reference';
  }
  function contents(chapter, route) {
    observer?.disconnect();tocNav.replaceChildren();
    let headings;
    if (route.startsWith('catalog-') && route!=='catalog-history') headings=[controls,document.getElementById(route).querySelector('.result-count')];
    else if (route==='catalog-history') headings=[...historyChapter.querySelectorAll('.catalog-extras > details')];
    else headings=[...chapter.querySelectorAll('h2, h3')].filter(h=>!h.closest('details')&&!h.closest('.article-heading')&&!h.hidden&&getComputedStyle(h).display!=='none');
    headings.forEach((heading,index)=>{
      if (!heading.id) heading.id=`docs-${route}-heading-${index+1}`;
      const text=heading===controls?'Search the catalog':heading.matches('.result-count')?'Records':heading.matches('details')?heading.querySelector('summary').textContent.trim():heading.textContent.trim();
      tocNav.append(link('#'+heading.id,text));
    });
    if(!headings.length)tocNav.append(link('#'+route,'Overview'));
    if('IntersectionObserver'in window){
      observer=new IntersectionObserver(entries=>{
        const visible=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top)[0];
        if(!visible)return;
        for(const a of tocNav.querySelectorAll('a')){if(a.hash==='#'+visible.target.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');}
      },{rootMargin:'-100px 0px -65% 0px'});
      headings.forEach(h=>observer.observe(h));
    }
  }
  function show(scroll=true,focus=false) {
    let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{id='';}
    const route=routeFor(id);const changed=current!==route;current=route;
    document.body.dataset.docsRoute=route;
    const isCatalog=route.startsWith('catalog-')&&route!=='catalog-history';
    const chapter=chapters.get(isCatalog?'reference':route);
    for(const node of chapters.values())node.hidden=node!==chapter;
    intro.hidden=isCatalog;controls.hidden=!isCatalog;
    for(const panel of library.querySelectorAll('.catalog-panel'))panel.hidden=!isCatalog||panel.id!==route;
    if(isCatalog)catalog.select(route.replace('catalog-',''));
    if((id ? document.getElementById(id) : null)?.closest('.catalog-item'))catalog.revealHash(false);
    breadcrumb.replaceChildren(link('governance-lab-reference.html#start','CyberAlchemy Lab'),create('span','',' / '+labels.get(route)[0]));
    title.textContent=labels.get(route)[1];document.title=title.textContent+' · CyberAlchemy Lab';
    for(const a of nav.querySelectorAll('[data-library-route]')){if(a.dataset.libraryRoute===route)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');}
    document.querySelector('[data-library-top]').setAttribute('aria-current','page');
    if(changed){
      contents(chapter,route);pager.replaceChildren();const index=order.indexOf(route);
      for(const[direction,next]of[['Previous',order[index-1]],['Next',order[index+1]]]){
        if(!next){pager.append(create('span'));continue;}
        const a=link('#'+next,'');a.append(create('span','',direction),create('strong','',labels.get(next)[1]+(direction==='Next'?' →':'')));pager.append(a);
      }
    }
    if(focus)title.focus({preventScroll:true});
    if(scroll)requestAnimationFrame(()=>{
      const target=(id ? document.getElementById(id) : null);
      if(target&&chapter.contains(target)&&!labels.has(id)&&!aliases[id]){
        let ancestor=target;while(ancestor&&ancestor!==chapter){if(ancestor.tagName==='DETAILS')ancestor.open=true;ancestor=ancestor.parentElement;}
        target.scrollIntoView({block:'start',behavior:'instant'});
      }else window.scrollTo({top:0,behavior:'instant'});
    });
  }
  function navigate(id){
    const url=new URL(location.href);url.hash=id;
    if(url.href!==location.href)history.pushState(null,'',url);
    if(mobile.matches)browse.open=false;
    const changed=routeFor(id)!==current;show(true,changed);
  }
  document.addEventListener('click',event=>{
    const a=event.target.closest('a[href]');
    if(!a||event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey||a.target||a.hasAttribute('download'))return;
    const url=new URL(a.href,location.href);if(url.pathname!==location.pathname||url.search!==location.search||!url.hash)return;
    let id;try{id=decodeURIComponent(url.hash.slice(1));}catch{return;}
    if(!(id ? document.getElementById(id) : null)&&!labels.has(id)&&!aliases[id])return;
    event.preventDefault();navigate(id);
  });
  document.addEventListener('lab:catalognavigate',event=>navigate(event.detail.id));
  addEventListener('hashchange',()=>show());addEventListener('popstate',()=>show());
  show();if(document.readyState!=='complete')addEventListener('load',()=>show(),{once:true});
})();
