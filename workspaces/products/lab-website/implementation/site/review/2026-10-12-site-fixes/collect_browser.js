async (page) => {
  const config = /*CONFIG*/ {};
  const states = [];
  const events = [];
  const errorListener = error => events.push({kind:'pageerror',url:page.url(),message:String(error)});
  const consoleListener = message => {
    if (['warning','error'].includes(message.type())) events.push({kind:'console',url:page.url(),level:message.type(),message:message.text()});
  };
  const failedListener = request => events.push({kind:'requestfailed',page:page.url(),url:request.url(),error:request.failure()});
  const responseListener = response => {
    if (response.status()>=400) events.push({kind:'http',page:page.url(),url:response.url(),status:response.status()});
  };
  page.on('pageerror',errorListener);page.on('console',consoleListener);
  page.on('requestfailed',failedListener);page.on('response',responseListener);
  page.setDefaultTimeout(15000);
  for (const item of config.states) {
    const row={...item};
    try {
      // Avoid retaining an injected axe instance while navigating only a hash.
      // Interactive same-document navigation has its own journey collector.
      await page.goto('about:blank');
      await page.setViewportSize({width:item.width,height:1000});
      const response=await page.goto(config.base+item.path,{waitUntil:'load'});
      await page.evaluate(()=>document.fonts.ready);
      await page.waitForTimeout(120);
      if (item.expand) await page.locator(item.expand).evaluateAll(nodes=>nodes.forEach(node=>node.open=true));
      if (item.map) {
        await page.getByRole('button',{name:item.map,exact:true}).click();
        if (item.perspective) await page.getByRole('button',{name:item.perspective,exact:true}).click();
      }
      if(item.scroll)await page.locator(item.scroll).first().scrollIntoViewIfNeeded();
      row.status=response?.status();row.url=page.url();
      row.measurements=await page.evaluate(()=>{
        const visible=el=>{const r=el.getBoundingClientRect();const s=getComputedStyle(el);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none';};
        const identify=el=>el.id?`#${el.id}`:el.tagName.toLowerCase()+'.'+[...el.classList].slice(0,3).join('.');
        const box=el=>{const r=el.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};
        const main=document.querySelector('main')||document.body;
        const header=document.querySelector('.topbar');
        const headings=[...main.querySelectorAll('h1,h2,h3,h4')].filter(visible).map(el=>({tag:el.tagName,id:el.id,text:el.textContent.trim(),...box(el),fontSize:getComputedStyle(el).fontSize}));
        const paragraphs=[...main.querySelectorAll('p')].filter(visible).map(el=>({selector:identify(el),text:el.textContent.trim().slice(0,200),chars:el.textContent.trim().length,fontSize:getComputedStyle(el).fontSize,lineHeight:getComputedStyle(el).lineHeight,...box(el)}));
        const controls=[...document.querySelectorAll('a,button,input,select,summary,[tabindex]')].filter(visible).map(el=>({selector:identify(el),role:el.getAttribute('role'),label:el.getAttribute('aria-label')||el.textContent.trim().slice(0,90),href:el.getAttribute('href'),tabIndex:el.tabIndex,...box(el)}));
        const svgs=[...main.querySelectorAll('svg')].filter(visible).filter(el=>el.querySelector('text'));
        const diagrams=svgs.map(svg=>{
          const scale=svg.viewBox.baseVal.width?svg.getBoundingClientRect().width/svg.viewBox.baseVal.width:1;
          const text=[...svg.querySelectorAll('text')].filter(visible).map(t=>({text:t.textContent.trim(),cssFont:parseFloat(getComputedStyle(t).fontSize),approxDisplayedFont:parseFloat(getComputedStyle(t).fontSize)*scale}));
          return {selector:identify(svg),...box(svg),viewBox:svg.getAttribute('viewBox'),text};
        });
        return {
          title:document.title,route:document.body.dataset.docsRoute||null,width:innerWidth,height:innerHeight,
          pageScrollWidth:document.documentElement.scrollWidth,pageHorizontalOverflow:document.documentElement.scrollWidth>innerWidth+1,
          documentHeight:document.documentElement.scrollHeight,domNodes:document.querySelectorAll('*').length,
          header:header?box(header):null,headings,paragraphs,controls,diagrams,
          images:[...main.querySelectorAll('img')].filter(visible).map(el=>({src:el.getAttribute('src'),alt:el.getAttribute('alt'),complete:el.complete,naturalWidth:el.naturalWidth,...box(el)})),
          scrollRegions:[...main.querySelectorAll('[role="region"],.diagram-shell,.diagram-scroll,.table-scroll,.smap-panel')].filter(visible).filter(el=>el.scrollWidth>el.clientWidth+1).map(el=>({selector:identify(el),tabIndex:el.tabIndex,label:el.getAttribute('aria-label'),clientWidth:el.clientWidth,scrollWidth:el.scrollWidth})),
          currentLinks:[...document.querySelectorAll('[aria-current="page"]')].map(el=>({text:el.textContent.trim(),href:el.getAttribute('href')})),
          searchPresent:Boolean(document.querySelector('#docs-search-input')),
          canonical:document.querySelector('link[rel="canonical"]')?.href||null,
          description:document.querySelector('meta[name="description"]')?.content||null,
          resourceTimings:performance.getEntriesByType('resource').map(r=>({name:r.name,duration:r.duration,bytes:r.decodedBodySize,type:r.initiatorType})),
          navigation:performance.getEntriesByType('navigation').map(n=>({load:n.loadEventEnd,domContentLoaded:n.domContentLoadedEventEnd,transfer:n.transferSize})),
          browserLanguages:navigator.languages
        };
      });
      if(item.axe){
        await page.addScriptTag({path:config.axe});
        row.accessibility=await page.evaluate(async()=>{
          const result=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});
          const compact=rules=>rules.map(r=>({id:r.id,impact:r.impact,description:r.description,help:r.help,helpUrl:r.helpUrl,tags:r.tags,nodes:r.nodes.map(n=>({target:n.target,html:n.html,failureSummary:n.failureSummary,any:n.any,all:n.all,none:n.none}))}));
          return {version:result.testEngine.version,url:result.url,violations:compact(result.violations),incomplete:compact(result.incomplete),passes:result.passes.map(r=>r.id)};
        });
      }
      if(item.aria)row.aria=await page.locator('body').ariaSnapshot();
      if(item.screenshot){
        row.screenshot=config.output+'/screenshots/'+config.engine+'-'+item.key+'.png';
        await page.screenshot({path:row.screenshot,fullPage:row.measurements.documentHeight<12000,animations:'allow',timeout:45000});
      }
    } catch(error){row.error=String(error);}
    states.push(row);
  }
  page.off('pageerror',errorListener);page.off('console',consoleListener);
  page.off('requestfailed',failedListener);page.off('response',responseListener);
  return JSON.stringify({engine:config.engine,browserVersion:page.context().browser().version(),states,events});
}
