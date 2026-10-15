async page=>{
 const base='http://127.0.0.1:8768/';const rows=[];
 const check=async(name,fn)=>{try{rows.push({name,pass:true,result:await fn()});}catch(error){rows.push({name,pass:false,error:String(error)});}};
 const assert=(condition,message)=>{if(!condition)throw new Error(message);};
 page.setDefaultTimeout(20000);
 await check('phone menu destinations and focus',async()=>{
  await page.setViewportSize({width:390,height:844});await page.goto(base+'governance-lab-series/start-here.html');
  const menu=page.locator('.site-navigation');await menu.locator('summary').focus();await page.keyboard.press('Enter');assert(await menu.getAttribute('open')!==null,'Menu did not open with keyboard');
  const links=await menu.locator('a').allTextContents();assert(links.includes('Craft')&&links.includes('Reference'),'Destinations missing');
  await menu.getByRole('link',{name:'Craft',exact:true}).click();await page.waitForURL('**/craft-model.html#craft-overview');
  assert(await page.locator('h1:visible').count()>0,'Craft title missing');return links;
 });
 await check('early incident, exact lookup and Craft example routes',async()=>{
  await page.goto(base);await page.locator('.actions a').filter({hasText:'Follow an incident'}).click();await page.waitForURL('**/incident-walkthrough.html');
  await page.goto(base+'governance-lab-series/start-here.html');await page.locator('.start-quick-path a').filter({hasText:'Find an exact definition'}).click();await page.waitForURL('**#catalog-definitions');
  await page.goto(base+'craft-documentation-proposal/craft-model.html');await page.locator('.craft-example-entry a').click();assert(new URL(page.url()).hash==='#definition','Craft example did not open');return {incident:true,lookup:true,craft:true};
 });
 await check('search quick and complete results, keyboard, scope and Escape',async()=>{
  await page.goto(base+'governance-lab-series/start-here.html');await page.keyboard.press('/');
  const input=page.locator('#docs-search-input');assert(await input.evaluate(e=>e===document.activeElement),'Shortcut did not focus search');
  await input.fill('Calculation versus Operation');await page.locator('.site-search-results a').first().waitFor();
  await page.keyboard.press('ArrowDown');const selected=await page.evaluate(()=>document.activeElement.dataset.searchId);
  await page.waitForFunction(()=>LabSiteSearch.count>0);assert(await page.evaluate(()=>document.activeElement.dataset.searchId)===selected,'Complete results stole focus');
  await page.keyboard.press('Escape');assert(await input.evaluate(e=>e===document.activeElement),'Escape did not return focus');assert(await page.locator('.site-search-results').isHidden(),'Escape did not dismiss results');
  await input.fill('qzxvqzpqnonexistent');await page.locator('.site-search-empty').filter({hasText:'No matches'}).waitFor();
  await input.fill('Work');await page.locator('#site-search-scope').selectOption('Reference records');assert((await page.locator('.site-search-results a').all()).length>0,'Scoped records missing');
  const timings=await page.evaluate(()=>['Work','Definition','Calculation versus Operation'].map(query=>{const t=performance.now();const results=LabSiteSearch.rank(query);return {query,ms:performance.now()-t,count:results.length};}));
  return {preservedFocus:selected,entries:await page.evaluate(()=>LabSiteSearch.count),timings};
 });
 await check('search failure and retry, and late close stays closed',async()=>{
  const tab=await page.context().newPage();let fail=true;
  await tab.route('**/site-search-index.js',route=>fail?route.abort():route.continue());
  await tab.goto(base+'governance-lab-series/start-here.html');await tab.locator('#docs-search-input').fill('Work');
  await tab.getByRole('button',{name:'Retry search',exact:true}).waitFor();assert(await tab.locator('.site-search-progress').count()===0,'Failed search still says loading');
  fail=false;await tab.getByRole('button',{name:'Retry search',exact:true}).click();await tab.waitForFunction(()=>LabSiteSearch.count>0);
  await tab.locator('#docs-search-input').press('Escape');assert(await tab.locator('.site-search-results').isHidden(),'Results reopened');await tab.close();return {recovered:true};
 });
 await check('closing a pending search prevents late reopening',async()=>{
  const tab=await page.context().newPage();let release;
  const gate=new Promise(resolve=>release=resolve);
  await tab.route('**/site-search-index.js',async route=>{await gate;await route.continue();});
  await tab.goto(base+'governance-lab-series/start-here.html');await tab.locator('#docs-search-input').fill('Work');
  await tab.locator('.site-search-results a').first().waitFor();await tab.locator('#docs-search-input').press('Escape');release();
  await tab.waitForFunction(()=>LabSiteSearch.count>0);assert(await tab.locator('.site-search-results').isHidden(),'Late completion reopened a dismissed search');
  await tab.close();return true;
 });
 await check('complete catalog search, unknown input and browse recovery',async()=>{
  await page.goto(base+'governance-lab-series/lab-reference-library.html#catalog-definitions');await page.locator('#catalog-search').fill('governed participant identity');
  await page.waitForFunction(()=>!!window.LabReferenceSearchText);await page.locator('#catalog-definitions .catalog-item:visible').first().waitFor();const count=await page.locator('#catalog-definitions .catalog-item:visible').count();
  await page.locator('#catalog-search').fill('qzxvqzpqnonexistent');await page.getByRole('button',{name:'Browse all records',exact:true}).click();
  const restored=await page.locator('#catalog-definitions .catalog-item:visible').count();assert(restored>count,'Browse did not restore complete catalog');return {count,restored};
 });
 await check('catalog missing payload retry',async()=>{
  const tab=await page.context().newPage();let fail=true;await tab.route('**/reference-search-data.js',route=>fail?route.abort():route.continue());
  await tab.goto(base+'governance-lab-series/lab-reference-library.html#catalog-definitions');await tab.locator('#catalog-search').fill('governed participant identity');
  await tab.getByRole('button',{name:'Retry complete-record search',exact:true}).waitFor();fail=false;await tab.getByRole('button',{name:'Retry complete-record search',exact:true}).click();
  await tab.waitForFunction(()=>!!window.LabReferenceSearchText);assert(await tab.locator('.catalog-retry').isHidden(),'Retry was not cleared');await tab.close();return true;
 });
 await check('phase changes retain honest action states',async()=>{
  await page.goto(base+'governance-lab-series/hackathon.html');
  const phases=await page.evaluate(()=>['2026-10-13T17:59:59-03:00','2026-10-13T18:00:00-03:00','2026-10-24T00:00:00-03:00','2026-10-24T12:00:00-03:00','2026-10-25T18:00:00-03:00','2026-10-26T00:00:00-03:00'].map(at=>LabEventStatus.state(Date.parse(at))));
  assert(phases.map(s=>s.phase).join(',')==='before,building,submitted,voting,review,ended','Browser phases differ');assert(phases.every(s=>Object.values(s.actions).every(a=>!a.enabled)),'An unconfigured form became available');
  const text=await page.locator('[data-event-status]').innerText();assert(text.includes('pending'),'Current registration state is misleading');return {phases:phases.map(s=>s.phase),text};
 });
 await check('native disclosure, fragment reload, parent category and history',async()=>{
  await page.goto(base+'governance-lab-series/reference/def-cal-definition-definition.html');
  const disclosure=page.locator('.record-body details').first();
  if(await disclosure.count()){
    const wasOpen=await disclosure.getAttribute('open')!==null;
    await disclosure.locator('summary').focus();await page.keyboard.press('Enter');
    assert((await disclosure.getAttribute('open')!==null)!==wasOpen,'Keyboard disclosure did not toggle');
    if(wasOpen)await page.keyboard.press('Enter');
    assert(await disclosure.getAttribute('open')!==null,'Keyboard disclosure did not reopen');
  }
  await page.locator('.docs-local-nav details').evaluateAll(nodes=>nodes.forEach(e=>e.open=true));
  const fragments=await page.locator('.docs-record-outline a[href*="#"],.docs-toc a[href*="#"]').all();if(fragments.length){await fragments[fragments.length-1].click();await page.reload();assert(new URL(page.url()).hash,'Direct fragment lost on reload');}
  return {h1:await page.locator('h1:visible').innerText(),selected:await page.locator('.article-tree [aria-current]').count()};
 });
 await check('preview homepage walkthrough and shared theme',async()=>{
  await page.goto(base);assert(await page.locator('.palette-study').count()===0,'Palette selector remains');
  await page.locator('[data-stage=meaning]').click();await page.locator('[data-stage=meaning]').press('End');
  assert(await page.locator('#stage-type').innerText()==='DECISION','Homepage keyboard walkthrough failed');
  await page.locator('.theme').click();assert(await page.evaluate(()=>document.documentElement.dataset.theme)==='dark','Homepage dark theme failed');
  await page.locator('.nav-docs').click();await page.waitForURL('**/start-here.html');
  assert(await page.evaluate(()=>document.documentElement.dataset.theme)==='dark','Shared theme was lost');
  await page.locator('.preview-theme-toggle').click();assert(await page.evaluate(()=>document.documentElement.dataset.theme)==='light','Document theme toggle failed');
  await page.locator('.brand').click();await page.waitForURL('**/index.html');assert(new URL(page.url()).port==='8768','Home escaped preview');return true;
 });
 await check('carousel keyboard, reduced motion and synthesized touch cancellation',async()=>{
  await page.emulateMedia({reducedMotion:'reduce'});await page.goto(base+'governance-lab-series/hackathon.html');
  assert(await page.locator('[data-rotation]').innerText()==='Play','Autoplay active with reduced motion');await page.locator('[data-next]').focus();await page.keyboard.press('Enter');
  const count=await page.locator('[data-count]').innerText();assert(count.includes('02'),'Next idea did not advance');
  const cdp=await page.context().newCDPSession(page);await cdp.send('Emulation.setTouchEmulationEnabled',{enabled:true,maxTouchPoints:1});await page.locator('.hack-carousel').scrollIntoViewIfNeeded();
  const rect=await page.locator('.hack-carousel-slides').boundingBox();const x=rect.x+rect.width*.75,y=Math.max(0,Math.min(800,rect.y+100));
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});
  await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x-150,y}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  assert((await page.locator('[data-count]').innerText()).includes('03'),'Synthesized swipe did not advance');
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchCancel',touchPoints:[]});
  await page.locator('[data-next]').click();assert((await page.locator('[data-count]').innerText()).includes('04'),'Cancelled touch broke the next action');await cdp.detach();await page.emulateMedia({reducedMotion:'no-preference'});return {keyboard:true,synthesizedSwipe:true,synthesizedTouchCancel:true,physicalTouch:false};
 });
 await check('long and multilingual search input has a bounded recovery',async()=>{
  await page.goto(base+'governance-lab-series/start-here.html');await page.locator('#docs-search-input').fill('Évidence العربية 中文 '+('x'.repeat(480)));await page.waitForFunction(()=>LabSiteSearch.count>0);assert(await page.locator('.site-search-empty').isVisible(),'Unknown long query has no empty state');
  await page.locator('#docs-search-input').fill('Definition');await page.locator('.site-search-results a').first().waitFor();return {overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),recovered:true};
 });
 return {summary:{checks:rows.length,failures:rows.filter(r=>!r.pass).length},rows};
}
