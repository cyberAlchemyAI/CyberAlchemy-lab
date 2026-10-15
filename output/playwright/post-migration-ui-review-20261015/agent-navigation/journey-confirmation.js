async page=>{
 const base='http://127.0.0.1:8767/governance-lab-series/';const checks=[];
 await page.setViewportSize({width:390,height:1000});await page.emulateMedia({reducedMotion:'reduce'});
 for(const slug of ['understand-lab','investigate-incident','read-record','prepare-definition','resume-agent-work','explore-craft']){
  const url=base+'path-'+slug+'.html?verify=independent-nav-final';await page.goto(url);const destinations=await page.locator('.docs-step-actions>a').evaluateAll(as=>as.map(a=>a.href));
  const reset=page.locator('[data-reset-reading]');if(!await reset.isDisabled())await reset.click();await page.locator('[data-mark-read]').first().click();await page.reload();checks.push({name:slug+' saved progress',pass:await page.locator('[data-mark-read]').first().getAttribute('aria-pressed')==='true'});
  for(let i=0;i<destinations.length;i++){
   await page.goto(url);const link=page.locator('.docs-step-actions>a').nth(i);await link.click();await page.waitForFunction(()=>!document.documentElement.hasAttribute('data-docs-startup'));const expected=new URL(destinations[i]);const actual=new URL(page.url());const title=await page.locator('main h1').first().textContent();checks.push({name:slug+' step '+(i+1),pass:actual.pathname===expected.pathname&&actual.hash===expected.hash&&!!title?.trim(),destination:actual.pathname+actual.hash,title:title?.trim()});
  }
  await page.goto(url);await page.locator('.docs-all-paths').click();checks.push({name:slug+' back to chooser',pass:new URL(page.url()).pathname.endsWith('/start-here.html')&&new URL(page.url()).hash==='#reading-paths'&&await page.locator('.docs-path-card').count()===6});await page.goto(url);if(!await page.locator('[data-reset-reading]').isDisabled())await page.locator('[data-reset-reading]').click();
 }
 const context=await page.context().browser().newContext({javaScriptEnabled:false,viewport:{width:390,height:1000}});const nojs=await context.newPage();
 for(const route of ['start-here.html','company-brain.html','governance-lab-reference.html#system-map','lab-reference-library.html#catalog-definitions','reference/def-cal-definition-actor.html#def-cal-definition-actor','read-record.html','runtime-overview.html','path-understand-lab.html']){
  await nojs.goto(base+route);const observed=await nojs.evaluate(()=>{const sidebar=document.querySelector('.article-tree');const links=[...(sidebar?.querySelectorAll('a')||[])];const hasStart=links.some(a=>new URL(a.href).pathname.endsWith('/start-here.html'));const intro=links.filter(a=>new URL(a.href).pathname.endsWith('/company-brain.html'));const home=links.filter(a=>new URL(a.href).pathname.endsWith('/index.html'));const stale=home.some(a=>a.textContent.trim()==='The company brain');const globalHome=[...document.querySelectorAll('.topbar a')].some(a=>new URL(a.href).pathname.endsWith('/index.html'));return {hasStart,intro:intro.length,home:home.length,stale,globalHome};});checks.push({name:'noJS '+route,pass:!observed.stale&&observed.globalHome&&(!observed.hasStart||observed.intro===1),observed});
 }
 await context.close();return {checks,failures:checks.filter(c=>!c.pass)};
}
