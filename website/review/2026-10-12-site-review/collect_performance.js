async(page)=>{
  const config=/*CONFIG*/ {};
  const paths=['governance-lab-series/index.html','governance-lab-series/company-brain.html','governance-lab-series/research.html','governance-lab-series/start-here.html','governance-lab-series/governance-lab-reference.html#governance','governance-lab-series/lab-reference-library.html#reference','craft-documentation-proposal/craft-model.html#craft-overview','robot-learning-series/robot-learning-series.html'];
  const rows=[];
  for(const path of paths){
    for(let sample=1;sample<=5;sample++){
      const tab=await page.context().newPage();await tab.setViewportSize({width:1440,height:1000});
      const cdp=await tab.context().newCDPSession(tab);await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});
      await tab.addInitScript(()=>{
        window.reviewMetrics={lcp:[],cls:[],longTasks:[]};
        for(const[type,key]of[['largest-contentful-paint','lcp'],['layout-shift','cls'],['longtask','longTasks']]){
          try{new PerformanceObserver(list=>{for(const e of list.getEntries())window.reviewMetrics[key].push({time:e.startTime,value:e.value||null,duration:e.duration,recentInput:e.hadRecentInput||false});}).observe({type,buffered:true});}catch{}
        }
      });
      try{
        await tab.goto(config.base+path,{waitUntil:'load',timeout:60000});await tab.evaluate(()=>document.fonts.ready);await tab.waitForTimeout(600);
        rows.push(await tab.evaluate(({path,sample})=>({path,sample,url:location.href,domNodes:document.querySelectorAll('*').length,metrics:window.reviewMetrics,nav:performance.getEntriesByType('navigation').map(x=>({domContentLoaded:x.domContentLoadedEventEnd,load:x.loadEventEnd,decodedBytes:x.decodedBodySize})),resources:performance.getEntriesByType('resource').map(x=>({name:x.name,decodedBytes:x.decodedBodySize,duration:x.duration})),searchInitiallyLoaded:Boolean(window.LabSiteSearchIndex)}),{path,sample}));
      }catch(error){rows.push({path,sample,error:String(error)});}
      await cdp.detach();await tab.close();
    }
  }
  return JSON.stringify({environment:'WSL localhost, one owned persistent Chromium profile, fresh tab per sample, network cache disabled per tab, OS cache retained, no CPU/network throttling. Observers stopped 600 ms after fonts ready. These are local diagnostics, not field percentiles or INP.',rows});
}
