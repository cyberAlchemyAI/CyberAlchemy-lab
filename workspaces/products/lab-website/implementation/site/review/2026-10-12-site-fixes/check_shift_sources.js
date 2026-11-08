async(page)=>{
 const config=/*CONFIG*/ {};
 const tab=await page.context().newPage();await tab.setViewportSize({width:1440,height:1000});
 await tab.addInitScript(()=>{window.shifts=[];new PerformanceObserver(list=>{for(const s of list.getEntries())if(!s.hadRecentInput)window.shifts.push({time:s.startTime,value:s.value,sources:s.sources.map(x=>({tag:x.node?.tagName,className:x.node?.className,id:x.node?.id,previous:x.previousRect.toJSON(),current:x.currentRect.toJSON()}))});}).observe({type:'layout-shift',buffered:true});});
 await tab.goto(config.base+'governance-lab-series/index.html');await tab.evaluate(()=>document.fonts.ready);await tab.waitForTimeout(600);const result=await tab.evaluate(()=>window.shifts);await tab.close();return JSON.stringify(result);
}
