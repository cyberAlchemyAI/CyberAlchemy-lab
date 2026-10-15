/* Shared, offline search. The generated index is loaded as a script so that
   local file pages need no fetch permissions, server or external service. */
(() => {
  let data = window.LabSiteSearchIndex;
  const base = new URL("../", document.currentScript.src).href;
  const header = document.querySelector('.topbar-inner');
  if (!header) return;
  const siteHeader=header.closest('.topbar');
  if(siteHeader&&'ResizeObserver' in window){
    const measureHeader=()=>document.documentElement.style.setProperty('--site-header-height',Math.ceil(siteHeader.getBoundingClientRect().height)+'px');
    new ResizeObserver(measureHeader).observe(siteHeader);measureHeader();
  }
  const create = (tag, className, text) => {
    const el=document.createElement(tag);
    if(className)el.className=className;
    if(text)el.textContent=text;
    return el;
  };
  const nav=header.querySelector('nav');
  if(document.body.dataset.siteFamily!=='research'&&!nav.querySelector('[data-site-craft]')){
    const a=create('a','','Craft');a.href=new URL('../craft-documentation-proposal/craft-model.html#craft-overview',base);a.dataset.siteCraft='';
    if(document.body.dataset.edition==='craft')a.setAttribute('aria-current','page');nav.append(a);
  }
  const sidebar=document.querySelector('.article-tree .article-contents');
  if(sidebar){
    // Preserve the navigation node used by chapter controllers, and move its
    // existing links so active routes and history handling keep their bindings.
    const main=sidebar.querySelector(':scope > nav') || create('nav');
    main.setAttribute('aria-label','Documentation navigation');
    const existing=[...sidebar.querySelectorAll('a[href]')];
    const canonical=url=>{
      const value=new URL(url,location.href);
      value.pathname=value.pathname.replace(/\/governance-lab-series\.html$/, '/governance-lab-reference.html');
      return value.href;
    };
    const used=new Set();
    const core=[
      ['Getting started',[
        ['start-here.html','Start here','start'],
        ['governance-lab-reference.html#start','Lab overview'],
        ['governance-lab-reference.html#foundations','Definitions first'],
        ['incident-walkthrough.html','Follow an incident','learning'],
        ['concept-comparisons.html','Compare the concepts','learning'],
        ['governance-lab-reference.html#system-map','Interactive system map']
      ]],
      ['Governance',[
        ['governance-lab-reference.html#governance','Authority and meaning'],
        ['governance-lab-reference.html#evidence','Provenance and evidence'],
        ['governance-lab-reference.html#change','Lifecycle and admission']
      ]],
      ['The Lab model',[
        ['governance-lab-reference.html#purpose','Intent, product and project'],
        ['governance-lab-reference.html#records','Definitions and connections'],
        ['governance-lab-reference.html#agent','Agent work and memory'],
        ['governance-lab-reference.html#learning','Operational learning'],
        ['governance-lab-reference.html#today','Current operational scope']
      ]],
      ['Practical guides',[
        ['read-record.html','Read a record','practical'],
        ['prepare-definition.html','Prepare a definition','practical'],
        ['prepare-incident-assessment.html','Prepare an assessment','practical'],
        ['resume-agent-work.html','Resume agent work','practical']
      ]],
      ['Software design',[
        ['../craft-documentation-proposal/craft-model.html#craft-overview','Craft documentation','craft']
      ]],
      ['Expanded essays',[
        ['lab-reference-library.html#articles-library','Series overview']
      ]],
      ['Reference',[
        ['lab-reference-library.html#reference','Reference library'],
        ['record-examples.html','Complete examples','practical'],
        ['lab-reference-library.html#research','Sources and open questions']
      ]],
      ['About CyberAlchemy',[
        ['index.html','The company brain','research'],
        ['hackathon.html','Craft × Lab hackathon','research'],
        ['company-brain.html','Why a company brain?','research'],
        ['research.html','Research & culture','research'],
        ['../robot-learning-series/robot-learning-series.html','Robot learning','research'],
        ['source-and-status.html','Source & status','research']
      ]]
    ];
    const take=(href,label,marker)=>{
      const absolute=new URL(href,base);
      const a=existing.find(node=>!used.has(node)&&canonical(node.href)===canonical(absolute.href)) || create('a');
      if(!a.hasAttribute('href')){
        const sameGuide=document.body.dataset.docsEnhanced==='guide'&&absolute.pathname.endsWith('/governance-lab-reference.html');
        a.href=sameGuide?absolute.hash:absolute.href;
        if(sameGuide)a.dataset.section=absolute.hash.slice(1);
      }
      a.textContent=label;
      if(marker==='start')a.dataset.siteStart='';
      if(marker==='learning')a.dataset.siteLearning=href.replace('.html','');
      if(marker==='practical')a.dataset.sitePractical=href.replace('.html','');
      if(marker==='craft')a.dataset.siteCraft='';
      if(marker==='research')a.dataset.siteResearch='';
      if(!a.hasAttribute('data-section')&&!a.hasAttribute('data-library-route')&&!a.hasAttribute('data-craft-route')){
        const target=new URL(a.href,location.href);
        if(target.pathname===location.pathname&&!target.hash)a.setAttribute('aria-current','page');
        else a.removeAttribute('aria-current');
      }
      used.add(a);return a;
    };
    const groups=[];
    for(const[label,links]of core){
      const group=create('div','docs-navigation-group');group.dataset.navigationGroup=label;
      group.append(create('p','tree-label',label));
      for(const[href,title,marker]of links){
        const a=take(href,title,marker);group.append(a);
        // Library details stay with Reference, before examples and sources.
        if(label==='Reference'&&href.endsWith('#reference')){
          for(const id of ['library-reading-guide','catalog-definitions','catalog-types','catalog-relations','catalog-endpoints','catalog-history']){
            const local=existing.find(node=>node.dataset.libraryRoute===id);
            if(local&&!used.has(local)){group.append(local);used.add(local);}
          }
        }
      }
      if(label==='Software design'){
        for(const local of existing.filter(node=>node.hasAttribute('data-craft-route'))){
          if(!used.has(local)){group.append(local);used.add(local);}
        }
      }
      if(label==='Expanded essays'){
        for(const local of existing.filter(node=>/^essay-\d+$/.test(node.dataset.libraryRoute||''))){
          if(!used.has(local)){group.append(local);used.add(local);}
        }
      }
      if(label==='Reference'){
        const local=existing.find(node=>node.dataset.section==='reading-next');
        if(local&&!used.has(local)){group.append(local);used.add(local);}
      }
      groups.push(group);
    }
    main.replaceChildren(...groups);
    for(const node of [...sidebar.children]){
      if(node!==main&&node.tagName!=='SUMMARY'&&!node.classList.contains('tree-progress')&&!node.classList.contains('tree-title'))node.remove();
    }
    if(!main.parentElement)sidebar.append(main);
    // A direct link into a lower group should leave its selected topic visible
    // in the desktop tree, without opening the compact mobile disclosure.
    const tree=sidebar.closest('.article-tree');
    const revealCurrent=()=>requestAnimationFrame(()=>{
      if(!tree||matchMedia('(max-width:900px)').matches)return;
      const active=main.querySelector('a[aria-current]');
      if(!active||tree.scrollHeight<=tree.clientHeight)return;
      const item=active.getBoundingClientRect();const viewport=tree.getBoundingClientRect();
      if(item.top<viewport.top||item.bottom>viewport.bottom)tree.scrollTop+=item.top-viewport.top-40;
    });
    new MutationObserver(revealCurrent).observe(main,{subtree:true,attributes:true,attributeFilter:['aria-current']});
    revealCurrent();
  }
  let search=header.querySelector('.docs-search');
  if(!search){search=create('div','docs-search');header.append(search);}
  search.replaceChildren();search.hidden=false;
  const label=create('label','site-search-sr-only','Search all documentation');label.htmlFor='docs-search-input';
  const input=create('input');input.type='text';input.inputMode='search';input.id='docs-search-input';input.placeholder=document.body.dataset.siteFamily==='research'?'Search docs':'Search all docs';input.autocomplete='off';input.setAttribute('aria-controls','docs-search-results');input.setAttribute('aria-expanded','false');
  input.setAttribute('role','combobox');input.setAttribute('aria-haspopup','dialog');input.setAttribute('aria-autocomplete','list');
  const results=create('div','docs-search-results site-search-results');results.id='docs-search-results';results.hidden=true;
  results.setAttribute('role','dialog');results.setAttribute('aria-label','Documentation search results');
  const announcement=create('p','site-search-sr-only');announcement.setAttribute('role','status');announcement.setAttribute('aria-live','polite');
  search.append(label,input,create('kbd','','/'),results,announcement);
  const groupOrder=['The Lab','Start here','Learning paths','Practical guides','Reference examples','Guide','Expanded essays','Reference records','Craft','Applications','Hackathon','Research lab','Sources'];
  const availableGroups=()=>{
    const declared=Object.keys(data?.groups||{});
    return declared.length?[...groupOrder.filter(group=>declared.includes(group)),...declared.filter(group=>!groupOrder.includes(group)).sort()]:groupOrder;
  };
  // Every reading family gets a true focus bypass. Chapter adapters register
  // their capture handler first; the shared fallback covers standalone pages.
  document.addEventListener('click',event=>{
    const a=event.target.closest?.('a.skip-link,a.skip');
    if(!a||event.defaultPrevented||event.button!==0||event.ctrlKey||event.metaKey||event.altKey||event.shiftKey)return;
    const main=document.querySelector('main');if(!main)return;
    let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{id='';}
    const current=document.getElementById(id);
    const scope=current&&main.contains(current)?current.closest('article[id^="essay-"],.record-page'):null;
    const target=scope?.querySelector('h1,h2')||main.querySelector('h1,h2')||main;
    event.preventDefault();event.stopImmediatePropagation();target.tabIndex=-1;
    target.focus({preventScroll:true});target.scrollIntoView({block:'start',behavior:'instant'});
  },true);
  const normalize=window.LabSearchEngine.normalize;
  let index=data?window.LabSearchEngine.prepare(data.entries):null;
  let loading=null;
  function load(){
    if(index)return Promise.resolve(index);
    if(loading)return loading;
    loading=new Promise((resolve,reject)=>{
      const script=document.createElement('script');script.src=new URL('assets/site-search-index.js',base);
      script.onload=async()=>{
        try{
          data=await(window.LabSiteSearchIndexReady||Promise.resolve(window.LabSiteSearchIndex));
          index=window.LabSearchEngine.prepare(data.entries);window.LabSiteSearch.count=index.length;resolve(index);
        }catch(error){script.remove();loading=null;reject(error);}
      };
      script.onerror=()=>{script.remove();loading=null;reject(new Error('The local search index could not be loaded.'));};document.head.append(script);
    });return loading;
  }
  let selected='All documentation';let expanded=false;let matches=[];
  let searchSequence=0;
  function close(){searchSequence++;results.hidden=true;input.setAttribute('aria-expanded','false');}
  function highlight(el,value,terms){
    const normalized=normalize(value);let offset=0;
    while(offset<value.length){
      let start=-1;let length=0;
      for(const term of terms){const found=normalized.indexOf(term,offset);if(found>=0&&(start<0||found<start)){start=found;length=term.length;}}
      if(start<0){el.append(document.createTextNode(value.slice(offset)));break;}
      el.append(document.createTextNode(value.slice(offset,start)));el.append(create('mark','',value.slice(start,start+length)));offset=start+length;
    }
  }
  function snippet(entry,terms){
    const text=entry.text;const key=entry.textKey;
    let at=terms.map(term=>key.indexOf(term)).filter(at=>at>=0).sort((a,b)=>a-b)[0]||0;
    let start=Math.max(0,at-65);if(start)start=text.indexOf(' ',start)+1;
    let end=Math.min(text.length,start+210);if(end<text.length){const space=text.lastIndexOf(' ',end);if(space>start)end=space;}
    return(start?'… ':'')+text.slice(start,end)+(end<text.length?' …':'');
  }
  function render(){
    results.replaceChildren();const terms=normalize(input.value.trim()).split(/\s+/).filter(Boolean);
    if(!terms.length){close();return;}
    const visible=matches.filter(item=>selected==='All documentation'||item.group===selected);
    const toolbar=create('div','site-search-toolbar');const count=create('p','docs-search-count',`${visible.length} ${visible.length===1?'result':'results'} across ${selected==='All documentation'?'the documentation':selected.toLowerCase()}`);toolbar.append(count);announcement.textContent=count.textContent;
    const scopeLabel=create('label','site-search-scope','Search in');scopeLabel.htmlFor='site-search-scope';
    const scope=create('select');scope.id='site-search-scope';scope.setAttribute('aria-label','Search in');
    for(const group of ['All documentation',...availableGroups()]){const option=create('option','',group);option.value=group;scope.append(option);}scope.value=selected;
    scope.addEventListener('change',()=>{selected=scope.value;expanded=false;render();results.querySelector('select').focus();});scopeLabel.append(scope);toolbar.append(scopeLabel);results.append(toolbar);
    if(!visible.length)results.append(create('p','site-search-empty','No matches. Try a shorter term or choose All documentation.'));
    let displayed=0;
    const best=visible.slice(0,3);
    if(best.length){
      const section=create('section','site-search-group');section.append(create('h2','site-search-group-label','Best matches'));const list=create('ul');
      for(const item of best){const li=create('li');const a=create('a');a.href=new URL(item.href,base);a.dataset.searchGroup=item.group;a.dataset.searchId=item.id;
        const title=create('strong');highlight(title,item.title,terms);const where=create('span','site-search-location',item.section||item.group);const excerpt=create('span','site-search-snippet');highlight(excerpt,snippet(item,terms),terms);a.append(title,where,excerpt);li.append(a);list.append(li);}
      section.append(list);results.append(section);displayed+=best.length;
    }
    for(const group of availableGroups()){
      const all=visible.filter(item=>item.group===group&&!best.includes(item));if(!all.length)continue;
      const items=expanded?all:all.slice(0,selected==='All documentation'?4:15);displayed+=items.length;
      const section=create('section','site-search-group');const heading=create('h2','site-search-group-label',`${group} · ${all.length}`);section.append(heading);
      const list=create('ul');
      for(const item of items){
        const li=create('li');const a=create('a');a.href=new URL(item.href,base);a.dataset.searchGroup=group;a.dataset.searchId=item.id;
        const title=create('strong');highlight(title,item.title,terms);const location=create('span','site-search-location',item.section||group);const excerpt=create('span','site-search-snippet');highlight(excerpt,snippet(item,terms),terms);
        a.append(title,location,excerpt);li.append(a);list.append(li);
      }
      section.append(list);results.append(section);
    }
    if(displayed<visible.length){const more=create('button','site-search-more',`Show all ${visible.length} results`);more.type='button';more.addEventListener('click',()=>{expanded=true;render();});results.append(more);}
    results.hidden=false;input.setAttribute('aria-expanded','true');
  }
  async function runSearch(){
    const sequence=++searchSequence;
    expanded=false;
    if(!input.value.trim()){close();return;}
    if(!index){results.replaceChildren(create('p','site-search-empty','Loading the local documentation index…'));results.hidden=false;input.setAttribute('aria-expanded','true');announcement.textContent='Loading documentation search.';}
    try{await load();if(sequence!==searchSequence)return;matches=window.LabSearchEngine.search(index,input.value);render();}
    catch(error){results.replaceChildren(create('p','site-search-empty',error.message+' Check the assets folder, then type again to retry.'));announcement.textContent=error.message;}
  }
  input.addEventListener('input',runSearch);
  input.addEventListener('focus',()=>{load().catch(()=>{});if(input.value.trim())runSearch();});
  input.addEventListener('keydown',event=>{
    if(event.key==='Escape'){event.preventDefault();close();input.blur();}
    if((event.key==='Enter'||event.key==='ArrowDown')&&!results.hidden){const first=results.querySelector('a');if(first){event.preventDefault();event.key==='Enter'?first.click():first.focus();}}
  });
  results.addEventListener('keydown',event=>{
    if(event.key==='Escape'){event.preventDefault();input.focus();close();}
    if(event.key==='ArrowDown'||event.key==='ArrowUp'){
      const links=[...results.querySelectorAll('a')];const at=links.indexOf(document.activeElement);
      if(at>=0){event.preventDefault();if(event.key==='ArrowUp'&&at===0)input.focus();else links[Math.max(0,Math.min(links.length-1,at+(event.key==='ArrowDown'?1:-1)))].focus();}
    }
  });
  document.addEventListener('click',event=>{if(!search.contains(event.target)||event.target.closest('.site-search-results a'))close();});
  document.addEventListener('keydown',event=>{
    const typing=/INPUT|TEXTAREA|SELECT/.test(event.target.tagName)||event.target.isContentEditable;
    if((event.key==='/'&&!event.ctrlKey&&!event.metaKey&&!event.altKey&&!typing)||((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k')){event.preventDefault();input.focus();input.scrollIntoView({behavior:'instant',block:'center',inline:'nearest'});}
  });
  window.LabSiteSearch={count:index?index.length:0,get groups(){return availableGroups();},close,ready:load,rank:value=>index?window.LabSearchEngine.search(index,value):[]};
  const topbar=header.closest('.topbar');
  const measureHeader=()=>document.documentElement.style.setProperty('--docs-header-height',topbar.getBoundingClientRect().height+'px');
  measureHeader();if('ResizeObserver'in window)new ResizeObserver(measureHeader).observe(topbar);
})();
