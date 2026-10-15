async(page)=>{
 const config=/*CONFIG*/ {},rows=[],events=[];
 const error=e=>events.push(String(e));page.on('pageerror',error);page.setDefaultTimeout(15000);
 const root=config.fileRoot||'file:///home/vlad_/projects/CyberAlchemy-lab/website/dist/';
 const bases=[config.base,'http://127.0.0.1:34117/CyberAlchemy-lab/',root];
 for(const base of bases){
  for(const path of ['index.html?delivery=1#how','craft-documentation-proposal/index.html?delivery=1#typed-model','governance-lab-series/governance-lab-series.html?delivery=1#evidence','governance-lab-series/governance-authority.html?delivery=1#authority-incident','governance-lab-series/governance-provenance.html?delivery=1#provenance-incident','governance-lab-series/governance-lifecycle.html?delivery=1#lifecycle-example','governance-lab-series/lab-reference-library.html?delivery=1#def-cal-definition-work']){
   try{await page.goto(base+path);await page.waitForTimeout(150);rows.push({kind:'redirect',base,path,destination:page.url(),title:await page.title()});}catch(e){rows.push({kind:'redirect',base,path,error:String(e)});}
  }
  for(const path of ['governance-lab-series/start-here.html','governance-lab-series/lab-reference-library.html#essay-6','craft-documentation-proposal/craft-model.html#taxonomy','robot-learning-series/robot-learning-series.html','governance-lab-series/hackathon.html']){
   try{await page.goto(base+path);const input=page.locator('#docs-search-input');await input.fill('Work');await page.locator('.site-search-results a').first().waitFor();const first=await page.locator('.site-search-results a').first().getAttribute('href');await input.press('Enter');await page.waitForURL('**/reference/def-cal-definition-work.html#def-cal-definition-work');
    rows.push({kind:'search',base,path,first,destination:page.url(),body:await page.locator('.record-body').count(),title:await page.locator('h1').innerText()});
   }catch(e){rows.push({kind:'search',base,path,error:String(e)});}
  }
 }
 // Complete fallback delivery without browser compression support, including
 // file origin. The fallback still contains every indexed entry.
 for(const base of [config.base,root]){
  const context=await page.context().browser().newContext();await context.addInitScript(()=>Object.defineProperty(window,'DecompressionStream',{value:undefined,configurable:true}));const tab=await context.newPage();
  try{await tab.goto(base+'governance-lab-series/lab-reference-library.html#catalog-definitions');await tab.locator('#catalog-search').fill('governed participant identity');await tab.waitForFunction(()=>!!window.LabReferenceSearchText);const catalog=await tab.locator('#catalog-definitions .catalog-item:visible').count();await tab.locator('#docs-search-input').fill('Work');await tab.locator('.site-search-results a').first().waitFor();rows.push({kind:'plaintext-fallback',base,catalog,indexEntries:await tab.evaluate(()=>window.LabSiteSearch.count),fallbacks:await tab.locator('script[src*="fallback"]').count()});}catch(e){rows.push({kind:'plaintext-fallback',base,error:String(e)});}finally{await context.close();}
 }
 const context=await page.context().browser().newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const tab=await context.newPage();
 try{
  for(const path of ['governance-lab-series/index.html','governance-lab-series/governance-lab-reference.html#governance','governance-lab-series/lab-reference-library.html#catalog-definitions','governance-lab-series/reference/def-cal-definition-work.html#def-cal-definition-work','craft-documentation-proposal/craft-model.html#definition','robot-learning-series/robot-learning-series.html','governance-lab-series/research/reader-study.html','governance-lab-series/governance-lab-series.html','governance-lab-series/governance-authority.html']){
   await tab.goto(config.base+path);if(path.includes('governance-lab-series.html'))await tab.waitForURL('**/governance-lab-reference.html');if(path.endsWith('governance-authority.html'))await tab.waitForURL('**/governance-lab-reference.html#governance');
   rows.push({kind:'no-js',path,destination:tab.url(),headings:await tab.getByRole('heading',{level:1}).allTextContents(),bodyVisible:await tab.locator('main').evaluate(el=>getComputedStyle(el).visibility),overflow:await tab.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),recordBody:await tab.locator('.record-body').count(),formDisabled:path.includes('reader-study')?await tab.locator('button[type=submit]').isDisabled():null});
  }
 }finally{await context.close();}
 page.off('pageerror',error);return JSON.stringify({rows,events});
}
