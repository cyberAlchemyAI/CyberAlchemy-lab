async page=>{
 const rows=[];
 await page.setViewportSize({width:1440,height:1000});
 for(const mode of ['light','dark'])for(const path of ['','governance-lab-series/start-here.html','governance-lab-series/lab-reference-library.html#catalog-definitions','governance-lab-series/reference/def-cal-definition-definition.html','craft-documentation-proposal/craft-model.html#definition','governance-lab-series/hackathon.html','robot-learning-series/robot-learning-series.html']){
  const url=new URL(path,'http://127.0.0.1:8768/');url.searchParams.set('mode',mode);await page.goto(url.href);await page.waitForFunction(()=>!document.documentElement.hasAttribute('data-docs-startup'));
  await page.addScriptTag({path:'/home/vlad_/.npm/_npx/0f94ee7615faf582/node_modules/axe-core/axe.min.js'});
  const result=await page.evaluate(async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});return {violations:r.violations,incomplete:r.incomplete,passes:r.passes.length};});
  rows.push({path,mode,...result});
 }
 return {summary:{states:rows.length,violations:rows.reduce((n,r)=>n+r.violations.length,0)},rows};
}
