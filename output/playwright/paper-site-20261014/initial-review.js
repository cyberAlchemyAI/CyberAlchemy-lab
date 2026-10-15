async page=>{
 const rows=[],errors=[];page.on('pageerror',e=>errors.push(String(e)));
 const pages=[['home',''],['start','governance-lab-series/start-here.html'],['guide','governance-lab-series/governance-lab-reference.html'],['catalog','governance-lab-series/lab-reference-library.html#catalog-definitions'],['record','governance-lab-series/reference/def-cal-definition-definition.html'],['craft','craft-documentation-proposal/craft-model.html'],['research','governance-lab-series/research.html'],['event','governance-lab-series/hackathon.html'],['robot','robot-learning-series/robot-learning-series.html'],['reader','governance-lab-series/research/reader-study.html']];
 for(const[name,path]of pages){
  for(const width of [390,1440]){
   try{
    await page.setViewportSize({width,height:1000});await page.goto('http://127.0.0.1:8768/'+path);await page.locator('h1:visible').first().waitFor();
    await page.screenshot({path:`output/playwright/paper-site-20261014/${name}-${width}.png`});
    rows.push(await page.evaluate(({name,path})=>({name,path,width:innerWidth,scroll:document.documentElement.scrollWidth,palette:document.documentElement.dataset.palette,bodyFont:getComputedStyle(document.body).fontFamily,h1Font:getComputedStyle(document.querySelector('h1')).fontFamily,background:getComputedStyle(document.body).backgroundColor,header:document.querySelector('.topbar,.header')?.getBoundingClientRect().height,themeButton:!!document.querySelector('.preview-theme-toggle,.theme')}),{name,path}));
   }catch(error){rows.push({name,path,width,error:String(error)});}
  }
 }
 return {rows,errors};
}
