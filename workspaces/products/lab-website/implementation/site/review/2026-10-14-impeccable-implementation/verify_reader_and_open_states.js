async page=>{
 const base='http://127.0.0.1:8766/candidate-site/';const rows=[];
 const check=async(name,fn)=>{try{rows.push({name,pass:true,result:await fn()});}catch(error){rows.push({name,pass:false,error:String(error)});}};
 await check('open menu and search accessibility',async()=>{
  await page.setViewportSize({width:390,height:844});await page.goto(base+'governance-lab-series/start-here.html');await page.locator('.site-navigation > summary').click();
  await page.addScriptTag({path:'/home/vlad_/.npm/_npx/0f94ee7615faf582/node_modules/axe-core/axe.min.js'});
  const menu=await page.evaluate(async()=>{const r=await axe.run({runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa','best-practice']}});return {violations:r.violations,incomplete:r.incomplete};});
  await page.locator('.site-navigation > summary').click();await page.locator('#docs-search-input').fill('Work');await page.waitForFunction(()=>LabSiteSearch.count>0);
  const search=await page.evaluate(async()=>{const r=await axe.run({runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa','best-practice']}});return {violations:r.violations,incomplete:r.incomplete};});
  if(menu.violations.length||search.violations.length)throw new Error(JSON.stringify({menu:menu.violations,search:search.violations}));return {menu,search};
 });
 await check('reader local response download is synthetic mechanics only',async()=>{
  await page.goto(base+'governance-lab-series/research/reader-study.html');await page.getByLabel('Anonymous participant code',{exact:true}).fill('NOT-A-PARTICIPANT');
  await page.getByLabel('I agree to share these answers for this documentation review.').check();
  const waiting=page.waitForEvent('download');await page.getByRole('button',{name:'Download my response file',exact:true}).click();const file=await waiting;
  await file.saveAs('/home/vlad_/projects/CyberAlchemy-lab/output/playwright/impeccable-implementation-20261014/synthetic-NOT-PARTICIPANT.json');
  const failure=await file.failure();if(failure)throw new Error(failure);
  return {filename:file.suggestedFilename(),actualParticipant:false,status:await page.locator('#download-status').innerText()};
 });
 return {summary:{checks:rows.length,failures:rows.filter(x=>!x.pass).length},rows};
}
