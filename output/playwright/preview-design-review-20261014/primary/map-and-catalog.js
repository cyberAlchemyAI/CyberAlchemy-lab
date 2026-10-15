async(page)=>{
 const config={"base": "http://127.0.0.1:8768/", "output": "/home/vlad_/projects/CyberAlchemy-lab/output/playwright/preview-design-review-20261014/primary", "run": "paper-map-and-catalog"}, rows=[],events=[];page.setDefaultTimeout(15000);
 page.on('pageerror',e=>events.push({type:'pageerror',message:String(e)}));page.on('requestfailed',r=>events.push({type:'requestfailed',url:r.url(),error:r.failure()}));
 await page.context().tracing.start({screenshots:true,snapshots:true});
 async function check(name,fn){try{rows.push({name,result:await fn()});}catch(e){rows.push({name,error:String(e)});}}
 for(const [name,path]of [['guide','governance-lab-series/governance-lab-reference.html#system-map'],['essay','governance-lab-series/lab-reference-library.html#essay-6'],['craft','craft-documentation-proposal/craft-model.html#taxonomy'],['robot','robot-learning-series/robot-learning-series.html#essay-3'],['record','governance-lab-series/reference/def-cal-definition-work.html#def-cal-definition-work']])await check('skip-'+name,async()=>{
  await page.goto(config.base+path);await page.waitForFunction(()=>!document.documentElement.hasAttribute('data-docs-startup'));
  const before=page.url();await page.locator('.skip-link,.skip').focus();await page.keyboard.press('Enter');
  const focused=await page.evaluate(()=>({text:document.activeElement.textContent.trim(),inMain:!!document.activeElement.closest('main'),route:document.body.dataset.docsRoute}));
  await page.keyboard.press('Tab');const next=await page.evaluate(()=>({tag:document.activeElement.tagName,text:document.activeElement.textContent.trim().slice(0,120),inMain:!!document.activeElement.closest('main')}));
  return {before,after:page.url(),focused,next,pass:before===page.url()&&focused.inMain&&next.inMain};
 });
 await check('map-all-layouts',async()=>{
  await page.setViewportSize({width:1440,height:1000});await page.goto(config.base+'governance-lab-series/governance-lab-reference.html#system-map');
  const model=await page.evaluate(()=>JSON.parse(document.getElementById('system-map-data').textContent)),results=[];
  for(const view of model.views){
   await page.getByRole('button',{name:view.title,exact:true}).click();
   for(const graph of view.focus_views||[view]){
    if(view.focus_views)await page.locator('[data-governance-focus="'+graph.focus_key+'"]').click();
    await page.locator('#map-diagram-mode').click();await page.locator('#map-fit').click();
    const fit=await page.locator('.smap-diagram:visible').evaluate(svg=>({svg:svg.getBoundingClientRect().width,panel:document.querySelector('.smap-stage').clientWidth}));
    await page.locator('#map-zoom-in').click();const zoom=await page.locator('.smap-diagram:visible').evaluate(svg=>svg.getBoundingClientRect().width);await page.locator('#map-zoom-out').click();
    const clipping=await page.locator('.smap-diagram:visible').evaluate(svg=>[...svg.querySelectorAll('.smap-node')].flatMap(node=>{
     const box=node.querySelector(':scope>rect').getBBox();return [...node.querySelectorAll(':scope>text')].map(text=>({node:node.dataset.mapNode,text:text.textContent.trim(),bounds:text.getBBox(),box})).filter(({bounds:b,box:r})=>b.x<r.x-1||b.x+b.width>r.x+r.width+1||b.y<r.y-1||b.y+b.height>r.y+r.height+1);
    }));
    await page.locator('#map-list-mode').click();const list=await page.locator('#map-relationship-list').innerText();
    const missing=graph.edges.filter(e=>!list.includes(model.nodes[e.source].title+' — '+e.label+' → '+model.nodes[e.target].title));
    results.push({view:view.id,focus:graph.focus_key||null,fit,fitPass:Math.abs(fit.svg-fit.panel)<1,zoom,zoomPass:zoom>fit.svg,clipping,missing});await page.locator('#map-diagram-mode').click();
   }
  }return results;
 });
 await check('legacy-reference-link',async()=>{
  await page.goto(config.base+'governance-lab-series/lab-reference-library.html#def-cal-definition-work');await page.waitForURL('**/reference/def-cal-definition-work.html#def-cal-definition-work');
  return {url:page.url(),bodies:await page.locator('.record-body').count(),title:await page.locator('h1').innerText()};
 });
 await check('catalog-complete-text-and-recovery',async()=>{
  await page.goto(config.base+'governance-lab-series/lab-reference-library.html#catalog-definitions');await page.locator('#catalog-search').fill('governed participant identity');
  await page.waitForFunction(()=>!!window.LabReferenceSearchText);await page.waitForTimeout(100);
  const count=await page.locator('#catalog-definitions .catalog-item:visible').count();await page.locator('#catalog-search').fill('qzxvqzpqnonexistent');await page.waitForTimeout(100);
  const empty=await page.locator('#catalog-definitions .catalog-empty:visible').count();await page.getByRole('button',{name:'Browse all records',exact:true}).click();
  return {count,empty,restored:await page.locator('#catalog-definitions .catalog-item:visible').count()};
 });
 await check('robot-shared-search',async()=>{
  await page.goto(config.base+'robot-learning-series/robot-learning-series.html');await page.locator('#docs-search-input').fill('Calculation versus Operation');await page.waitForFunction(()=>window.LabSiteSearch?.count>0);await page.waitForTimeout(100);
  return {search:await page.locator('.site-search-results:visible').count(),links:await page.locator('.site-search-results a').count(),home:await page.locator('.brand').getAttribute('href'),favicon:await page.locator('link[rel=icon]').getAttribute('href')};
 });
 await page.context().tracing.stop({path:config.output+'/traces/'+config.run+'.zip'});
 return JSON.stringify({rows,events});
}
