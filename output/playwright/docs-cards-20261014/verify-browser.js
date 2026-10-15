async page => {
 const base='http://127.0.0.1:8768/';const out='/home/vlad_/projects/CyberAlchemy-lab/output/playwright/docs-cards-20261014';
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const cdp=await page.context().newCDPSession(page);await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});
 await page.emulateMedia({reducedMotion:'reduce'});
 const paths=['understand-lab','investigate-incident','read-record','prepare-definition','resume-agent-work','explore-craft'];
 const routes=['governance-lab-series/start-here.html','governance-lab-series/governance-lab-reference.html#start','governance-lab-series/governance-lab-reference.html#reading-next','governance-lab-series/lab-reference-library.html#articles-library','governance-lab-series/lab-reference-library.html#reference','governance-lab-series/incident-walkthrough.html','governance-lab-series/concept-comparisons.html',...paths.map(p=>'governance-lab-series/path-'+p+'.html'),'craft-documentation-proposal/craft-model.html#definition','governance-lab-series/reference/def-cal-definition-definition.html'];
 const rows=[],a11y=[],screenshots=[];
 async function go(route,mode='light') {const u=new URL(route,base);u.searchParams.set('mode',mode);u.searchParams.set('review','doc-cards');await page.goto(u.href);await page.waitForFunction(()=>!document.documentElement.hasAttribute('data-docs-startup'));await page.evaluate(()=>document.fonts.ready);await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));}
 for(const mode of ['light','dark'])for(const width of [320,390,768,1024,1440])for(const route of routes){
  await page.setViewportSize({width,height:1000});await go(route,mode);
  const result=await page.evaluate(()=>{
   const visible=e=>!!(e.getBoundingClientRect().width&&e.getBoundingClientRect().height);
   const selector='.docs-path-card,.start-reading-paths>a,.entry-paths>a,.resource-shelf .chapter-card,.docs-reference-index>a,.reference-grid>a';
   const cards=[...document.querySelectorAll(selector)].filter(visible).map(e=>{const r=e.getBoundingClientRect();const s=getComputedStyle(e);return {title:e.innerText.slice(0,70),x:r.x,y:r.y,width:r.width,height:r.height,display:s.display,padding:s.padding,bg:s.backgroundColor,border:s.borderWidth,overflow:e.scrollWidth>e.clientWidth+1,nested:!!e.querySelector('a,button')};});
   return {overflow:document.documentElement.scrollWidth>innerWidth+1,scrollWidth:document.documentElement.scrollWidth,width:innerWidth,cards,path:document.querySelector('[data-reading-path]')?.dataset.readingPath,steps:document.querySelectorAll('.docs-reading-step').length,progress:document.querySelector('[data-reading-status]')?.textContent,theme:document.documentElement.dataset.theme,guideLink:[...document.querySelectorAll('.topbar nav a')].find(a=>a.textContent.trim()==='Guide')?.getAttribute('href')};
  });
  rows.push({route,mode,width,...result});
  const key=(route.includes('start-here')?'home':route.includes('path-understand')?'path':route.includes('articles-library')?'essays':route.endsWith('#start')?'overview':null);
  if(key&&((width===1440&&mode==='light')||(width===390&&mode==='dark'))){const name=`after-${key}-${width}-${mode}.png`;await page.screenshot({path:out+'/'+name});screenshots.push(name);}
  if(width===1440&&['governance-lab-series/start-here.html','governance-lab-series/path-understand-lab.html','governance-lab-series/lab-reference-library.html#articles-library','governance-lab-series/governance-lab-reference.html#start'].includes(route)){
   await page.addScriptTag({path:'/home/vlad_/.npm/_npx/0f94ee7615faf582/node_modules/axe-core/axe.min.js'});
   const r=await page.evaluate(async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});return {violations:r.violations,incomplete:r.incomplete};});a11y.push({route,mode,...r});
  }
 }
 await page.setViewportSize({width:1280,height:1000});await go('governance-lab-series/start-here.html');
 const destinations=await page.locator('.docs-path-card').evaluateAll(as=>as.map(a=>({href:a.href,title:a.querySelector('strong').textContent})));
 const checks=[];
 for(const d of destinations){await page.goto(d.href);await page.waitForFunction(()=>!!document.querySelector('[data-reading-path]'));checks.push({name:'path '+d.title,pass:await page.locator('h1').textContent()===d.title && await page.locator('[data-mark-read]').count()===3});}
 await go('governance-lab-series/path-understand-lab.html');await page.locator('[data-reset-reading]').evaluate(b=>{if(!b.disabled)b.click()});
 await page.locator('[data-mark-read]').first().click();checks.push({name:'mark read',pass:await page.locator('[data-mark-read]').first().getAttribute('aria-pressed')==='true'&&await page.locator('[data-reading-status]').textContent()==='1 of 3 steps read'});
 await page.reload();checks.push({name:'progress survives reload',pass:await page.locator('[data-mark-read]').first().getAttribute('aria-pressed')==='true'});
 await go('governance-lab-series/path-read-record.html');checks.push({name:'paths retain independent progress',pass:await page.locator('[data-reading-status]').textContent()==='0 of 3 steps read'});
 await go('governance-lab-series/path-understand-lab.html');await page.locator('[data-mark-read]').nth(1).click();await page.locator('[data-mark-read]').nth(2).click();checks.push({name:'completion',pass:(await page.locator('[data-reading-status]').textContent()).includes('3 of 3 steps read · Reading path complete')});
 await page.locator('[data-reset-reading]').click();checks.push({name:'reset',pass:await page.locator('[data-reading-status]').textContent()==='0 of 3 steps read'});
 const summary=page.locator('#step-2>summary');await summary.focus();await page.keyboard.press('Enter');checks.push({name:'native step keyboard collapse',pass:await page.locator('#step-2').getAttribute('open')===null});
 await page.evaluate(()=>location.hash='step-2');checks.push({name:'step hash reveals content',pass:await page.locator('#step-2').getAttribute('open')!==null});
 const sources=[];for(const d of destinations){await page.goto(d.href);sources.push(...await page.locator('.docs-step-actions>a').evaluateAll(as=>as.map(a=>a.href)));}
 const links=[];for(const href of sources){await page.goto(href);await page.waitForFunction(()=>!document.documentElement.hasAttribute('data-docs-startup'));await page.waitForTimeout(50);links.push(await page.evaluate(()=>({url:location.href,title:document.title,hash:location.hash,target:!location.hash||!!document.getElementById(decodeURIComponent(location.hash.slice(1))),visible:!location.hash||!!document.getElementById(decodeURIComponent(location.hash.slice(1)))?.getBoundingClientRect().width})));}
 await go('governance-lab-series/path-understand-lab.html');const search=page.locator('#docs-search-input');await search.fill('Work');await page.waitForSelector('.site-search-results a');checks.push({name:'shared search works on new paths',pass:await page.locator('.site-search-results a').count()>0});
 return {summary:{states:rows.length,overflowFailures:rows.filter(r=>r.overflow).length,cardFailures:rows.filter(r=>r.cards.some(c=>c.overflow||c.nested||c.display!=='flex')).length,checks:checks.length,checkFailures:checks.filter(c=>!c.pass).length,sourceLinks:links.length,sourceLinkFailures:links.filter(l=>!l.target||!l.visible).length,a11yStates:a11y.length,violations:a11y.reduce((n,r)=>n+r.violations.length,0),runtimeErrors:errors.length},rows,checks,links,a11y,errors,screenshots};
}
