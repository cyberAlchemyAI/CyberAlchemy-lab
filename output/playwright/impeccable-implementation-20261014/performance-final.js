async(page)=>{
 const config={"base":"http://127.0.0.1:8766/candidate-site/"},rows=[];
 for(let sample=1;sample<=5;sample++){
  const tab=await page.context().newPage();await tab.setViewportSize({width:390,height:844});
  const cdp=await tab.context().newCDPSession(tab);await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});
  await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:100,downloadThroughput:200000,uploadThroughput:93750});await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});
  await tab.addInitScript(()=>{window.metrics={cls:[],lcp:[],longTasks:[]};for(const[type,key]of[['layout-shift','cls'],['largest-contentful-paint','lcp'],['longtask','longTasks']])try{new PerformanceObserver(list=>{for(const e of list.getEntries())window.metrics[key].push({time:e.startTime,value:e.value||null,duration:e.duration,recentInput:e.hadRecentInput||false});}).observe({type,buffered:true});}catch{}});
  try{
   await tab.goto(config.base+'governance-lab-series/lab-reference-library.html#catalog-definitions',{waitUntil:'load',timeout:60000});await tab.evaluate(()=>document.fonts.ready);await tab.waitForTimeout(600);
   const startup=await tab.evaluate(()=>({metrics:window.metrics,domNodes:document.querySelectorAll('*').length,bodyVisible:getComputedStyle(document.querySelector('main')).visibility,searchInitiallyLoaded:!!window.LabSiteSearchIndex,referenceTextInitiallyLoaded:!!window.LabReferenceSearchText}));
   const catalogMs=null;
   await tab.evaluate(()=>{
    const input=document.getElementById('docs-search-input'),result=document.querySelector('.site-search-results');
    window.searchPaints=[];let current=null;
    input.addEventListener('input',()=>{current={query:input.value,start:performance.now()};window.searchPaints.push(current);},true);
    new MutationObserver(()=>{if(current&&!current.first&&result.querySelector('a')&&!result.hidden){const event=current;requestAnimationFrame(()=>{event.first=performance.now()-event.start;});}}).observe(result,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden']});
   });
   const globalStart=Date.now();await tab.evaluate(()=>{const p=LabSearchEngine.prepare;LabSearchEngine.prepare=(...args)=>{const t=performance.now();const result=p(...args);window.prepareMs=performance.now()-t;return result;};});await tab.locator('#docs-search-input').fill('Calculation versus Operation');await tab.locator('.site-search-results a').first().waitFor({timeout:60000});const globalMs=Date.now()-globalStart;await tab.waitForFunction(()=>window.LabSiteSearch?.count>0,undefined,{timeout:60000});const completeMs=Date.now()-globalStart;await tab.locator('#docs-search-input').fill('Work');await tab.waitForFunction(()=>window.searchPaints.some(x=>x.query==='Work'&&x.first));const paints=await tab.evaluate(()=>window.searchPaints);const ranks=await tab.evaluate(()=>['Work','Definition','Calculation versus Operation'].map(query=>{const t=performance.now();const hits=LabSiteSearch.rank(query);return {query,ms:performance.now()-t,count:hits.length};}));
   const results=await tab.locator('.site-search-results a').evaluateAll(nodes=>nodes.slice(0,3).map(n=>({text:n.textContent.trim(),href:n.href})));
   rows.push({sample,startup,catalogMs,globalMs,completeMs,paints,ranks,prepareMs:await tab.evaluate(()=>window.prepareMs),resources:await tab.evaluate(()=>performance.getEntriesByType("resource").filter(r=>r.name.includes("site-search-")).map(r=>({name:r.name,duration:r.duration,bytes:r.encodedBodySize}))),results});
  }catch(error){rows.push({sample,error:String(error)});}finally{await cdp.detach();await tab.close();}
 }
 return JSON.stringify({profile:'Chromium localhost, 390x844 CSS viewport, 4x emulated CPU slowdown, 100ms network latency, 200000 B/s download (1.6 Mbit/s), 93750 B/s upload. Fresh tab per sample, network cache disabled, OS cache retained. Local static server sends uncompressed files. Simulation, not a physical device or field percentile.',rows});
}
