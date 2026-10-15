async page=>{
 const base='http://127.0.0.1:8768/';const rows=[],errors=[];
 const listener=e=>errors.push(String(e));page.on('pageerror',listener);
 for(const width of [390,1440]){
  await page.setViewportSize({width,height:1000});
  for(const path of ['governance-lab-series/research.html','governance-lab-series/hackathon.html','governance-lab-series/start-here.html','governance-lab-series/lab-reference-library.html#catalog-definitions','governance-lab-series/reference/def-cal-definition-definition.html','craft-documentation-proposal/craft-model.html','robot-learning-series/robot-learning-series.html']){
   try{
    await page.goto(base+path);await page.evaluate(()=>document.fonts.ready);
    await page.waitForFunction(()=>getComputedStyle(document.querySelector('main')).visibility!=='hidden',undefined,{timeout:7000});
    const row=await page.evaluate(()=>{const menu=document.querySelector('.site-navigation');const summary=menu?.querySelector('summary');return {width:innerWidth,scroll:document.documentElement.scrollWidth,menu:!!menu,summaryVisible:!!summary&&summary.getBoundingClientRect().height>0,title:document.querySelector('h1')?.textContent,main:getComputedStyle(document.querySelector('main')).visibility};});
    row.pass=row.scroll<=width+1&&row.main!=='hidden'&&!!row.title&&(width>900||row.summaryVisible);
    if(width===1440&&path.endsWith('/start-here.html')){await page.locator('#docs-search-input').fill('Work');await page.waitForFunction(()=>LabSiteSearch.count>0);row.search={entries:await page.evaluate(()=>LabSiteSearch.count),links:await page.locator('.site-search-results a').count()};row.pass=row.pass&&row.search.links>0;}
    rows.push({path,...row});
   }catch(error){rows.push({path,width,pass:false,error:String(error)});}
  }
 }
 page.off('pageerror',listener);return {summary:{states:rows.length,failures:rows.filter(x=>!x.pass).length,runtimeErrors:errors.length},rows,errors};
}
