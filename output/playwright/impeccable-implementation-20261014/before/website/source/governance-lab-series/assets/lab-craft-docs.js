/* Craft's existing article joins the Lab site without changing its contents. */
(() => {
  if(document.body.dataset.edition!=='craft')return;
  const create=(tag,className,text)=>{const el=document.createElement(tag);if(className)el.className=className;if(text)el.textContent=text;return el;};
  const link=(href,text)=>{const el=create('a','',text);el.href=href;return el;};
  const article=document.getElementById('article');const layout=document.querySelector('.article-layout');const hero=document.querySelector('.hero');
  const chapters=new Map();const labels=new Map();
  const overview=create('section','docs-craft-overview');overview.id='craft-overview';overview.dataset.docsChapter=overview.id;overview.append(hero);article.prepend(overview);chapters.set(overview.id,overview);labels.set(overview.id,'Craft overview');
  for(const section of article.querySelectorAll('.article-section')){section.dataset.docsChapter=section.id;chapters.set(section.id,section);labels.set(section.id,section.querySelector('h2').textContent.trim());}
  const sidebar=document.querySelector('.contents');sidebar.className='contents article-tree';
  const browse=document.getElementById('article-navigation');browse.className='article-contents';
  const mobile=matchMedia('(max-width:900px)');browse.open=!mobile.matches;mobile.addEventListener('change',event=>{browse.open=!event.matches;});
  const nav=create('nav');nav.setAttribute('aria-label','Documentation navigation');
  nav.append(create('p','tree-label','Getting started'),link('../governance-lab-series/governance-lab-reference.html#start','Lab overview'),link('../governance-lab-series/governance-lab-reference.html#governance','Visual guide'),link('../governance-lab-series/lab-reference-library.html#reference','Reference library'),link('../governance-lab-series/lab-reference-library.html#articles-library','Expanded essays'));
  nav.append(create('p','tree-label','Craft · Software design'));
  for(const[id,title]of labels){const a=link('#'+id,title);a.dataset.craftRoute=id;nav.append(a);}
  browse.replaceChildren(create('summary','','Browse documentation'),nav);
  const header=create('header','docs-topic-header');const breadcrumb=create('p','docs-breadcrumb');const title=create('h1');title.tabIndex=-1;header.append(breadcrumb,title);article.prepend(header);
  const pager=create('nav','docs-pager');pager.setAttribute('aria-label','Previous and next topics');article.append(pager);
  const tocAside=create('aside','docs-local-nav');tocAside.setAttribute('aria-label','On this page');
  const toc=create('details','docs-toc');const compact=matchMedia('(max-width:1200px)');toc.open=!compact.matches;compact.addEventListener('change',event=>{toc.open=!event.matches;});
  const tocNav=create('nav');tocNav.setAttribute('aria-label','Headings on this page');toc.append(create('summary','','On this page'),tocNav);tocAside.append(toc);layout.append(tocAside);
  const paths=create('nav','docs-craft-paths');paths.setAttribute('aria-label','Start exploring Craft');
  for(const[id,description]of[['taxonomy','Explore the roles and connections in a model.'],['definition','Follow the capacity decision example.'],['process','See how a model carries the design into code.']]){const a=link('#'+id,'');a.append(create('strong','',labels.get(id)),create('span','',description));paths.append(a);}
  overview.append(create('h2','docs-path-heading','Start exploring Craft'),paths);
  document.body.dataset.docsEnhanced='craft';
  // The current chapter title is H1. Its visible subsections therefore use
  // H2; the hidden original section title stays in the no-JS source.
  for(const heading of article.querySelectorAll('.article-section > h3')){
    const replacement=create('h2','docs-craft-subheading');
    for(const attribute of heading.attributes)replacement.setAttribute(attribute.name,attribute.value);
    replacement.classList.add('docs-craft-subheading');
    replacement.append(...heading.childNodes);heading.replaceWith(replacement);
  }
  let current='';let observer;
  function routeFor(id){if(chapters.has(id))return id;return document.getElementById(id)?.closest('[data-docs-chapter]')?.dataset.docsChapter||'craft-overview';}
  function show(scroll=true,focus=false){
    let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{id='';}const route=routeFor(id);const changed=current!==route;current=route;document.body.dataset.docsRoute=route;
    for(const[key,chapter]of chapters)chapter.hidden=key!==route;
    header.hidden=route==='craft-overview';title.textContent=labels.get(route);breadcrumb.replaceChildren(link('../governance-lab-series/governance-lab-reference.html#start','CyberAlchemy Lab'),create('span','',' / Craft'));
    document.title=labels.get(route)+' · Craft · CyberAlchemy Lab';
    for(const a of nav.querySelectorAll('[data-craft-route]')){if(a.dataset.craftRoute===route)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');}
    if(changed){
      observer?.disconnect();tocNav.replaceChildren();const chapter=chapters.get(route);const headings=[...chapter.querySelectorAll('.docs-craft-subheading, .docs-path-heading')];
      headings.forEach((h,i)=>{if(!h.id)h.id=`craft-${route}-heading-${i+1}`;tocNav.append(link('#'+h.id,h.textContent.trim()));});if(!headings.length)tocNav.append(link('#'+route,'Overview'));
      if('IntersectionObserver'in window){observer=new IntersectionObserver(entries=>{const e=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top)[0];if(!e)return;for(const a of tocNav.querySelectorAll('a')){if(a.hash==='#'+e.target.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');}},{rootMargin:'-100px 0px -65% 0px'});headings.forEach(h=>observer.observe(h));}
      pager.replaceChildren();const order=[...chapters.keys()];const i=order.indexOf(route);
      for(const[direction,next]of[['Previous',order[i-1]],['Next',order[i+1]]]){if(!next){pager.append(create('span'));continue;}const a=link('#'+next,'');a.append(create('span','',direction),create('strong','',labels.get(next)+(direction==='Next'?' →':'')));pager.append(a);}
    }
    if(focus&&route!=='craft-overview')title.focus({preventScroll:true});
    if(scroll)requestAnimationFrame(()=>{const target=document.getElementById(id);if(target&&chapters.get(route).contains(target)&&id!==route)target.scrollIntoView({block:'start',behavior:'instant'});else window.scrollTo({top:0,behavior:'instant'});});
    requestAnimationFrame(()=>dispatchEvent(new Event('resize')));
  }
  document.addEventListener('click',event=>{
    const a=event.target.closest('a[href]');if(!a||event.defaultPrevented||event.button!==0||event.ctrlKey||event.metaKey||event.altKey||event.shiftKey||a.target||a.hasAttribute('download'))return;
    const url=new URL(a.href,location.href);if(url.pathname!==location.pathname||url.search!==location.search||!url.hash)return;
    let id;try{id=decodeURIComponent(url.hash.slice(1));}catch{return;}if(!document.getElementById(id)&&!chapters.has(id))return;
    event.preventDefault();if(url.href!==location.href)history.pushState(null,'',url);if(mobile.matches)browse.open=false;show(true,routeFor(id)!==current);
  });
  addEventListener('hashchange',()=>show());addEventListener('popstate',()=>show());show();if(document.readyState!=='complete')addEventListener('load',()=>show(),{once:true});
})();
