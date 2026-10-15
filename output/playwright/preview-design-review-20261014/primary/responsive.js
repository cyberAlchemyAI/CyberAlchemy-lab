async page=>{
 const base='http://127.0.0.1:8768/';const rows=[],errors=[];
 page.on('pageerror',e=>errors.push(String(e)));page.setDefaultTimeout(15000);
 const routes=['','governance-lab-series/start-here.html','governance-lab-series/incident-walkthrough.html','governance-lab-series/governance-lab-reference.html#system-map','governance-lab-series/lab-reference-library.html#catalog-definitions','governance-lab-series/lab-reference-library.html#essay-6','governance-lab-series/reference/def-cal-definition-definition.html','craft-documentation-proposal/craft-model.html#definition','governance-lab-series/research.html','governance-lab-series/company-brain.html','governance-lab-series/hackathon.html','governance-lab-series/source-and-status.html','robot-learning-series/robot-learning-series.html','robot-learning-series/robot-learning-series.html#essay-3','governance-lab-series/research/reader-study.html'];
 for(const mode of ['light','dark']){
  for(const width of (mode==='light'?[320,390,768,1024,1440]:[390,1440])){
   await page.setViewportSize({width,height:1000});
   for(const path of routes){
    try{
     const url=new URL(path,base);url.searchParams.set('mode',mode);await page.goto(url.href);
     await page.waitForFunction(()=>!document.documentElement.hasAttribute('data-docs-startup'));
     await page.waitForTimeout(50);
     const row=await page.evaluate(()=>{const main=document.querySelector('main')||document.body;const head=document.querySelector('h1');return {url:location.href,width:innerWidth,scroll:document.documentElement.scrollWidth,main:getComputedStyle(main).visibility,title:head?.textContent,palette:document.documentElement.dataset.palette,theme:document.documentElement.dataset.theme,background:getComputedStyle(document.body).backgroundColor,menu:!!document.querySelector('.site-navigation'),themeButton:!!document.querySelector('.preview-theme-toggle,.theme')};});
     row.pass=row.scroll<=width+1&&row.main!=='hidden'&&!!row.title&&row.palette==='paper'&&row.theme===mode&&row.themeButton;rows.push(row);
     if(width===1440&&['governance-lab-series/start-here.html','governance-lab-series/reference/def-cal-definition-definition.html','craft-documentation-proposal/craft-model.html#definition','governance-lab-series/research/reader-study.html','governance-lab-series/lab-reference-library.html#catalog-definitions'].includes(path)){
      const name=path.split('/').pop().replace(/[.#]/g,'-');await page.screenshot({path:`output/playwright/preview-design-review-20261014/primary/final-${mode}-${name}.png`});
     }
    }catch(error){rows.push({path,width,mode,pass:false,error:String(error)});}
   }
  }
 }
 return {summary:{states:rows.length,failures:rows.filter(r=>!r.pass).length,runtimeErrors:errors.length},rows,errors};
}
