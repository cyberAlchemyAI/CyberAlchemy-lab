async page => {
 const base='http://127.0.0.1:8766/candidate-site/';
 const output='/home/vlad_/projects/CyberAlchemy-lab/output/playwright/impeccable-implementation-20261014';
 const routes=[
  ['home','governance-lab-series/index.html'],['hackathon','governance-lab-series/hackathon.html'],
  ['company','governance-lab-series/company-brain.html'],['research','governance-lab-series/research.html'],
  ['source','governance-lab-series/source-and-status.html'],['start','governance-lab-series/start-here.html'],
  ['incident','governance-lab-series/incident-walkthrough.html'],['compare','governance-lab-series/concept-comparisons.html'],
  ['read','governance-lab-series/read-record.html'],['prepare','governance-lab-series/prepare-definition.html'],
  ['assessment','governance-lab-series/prepare-incident-assessment.html'],['resume','governance-lab-series/resume-agent-work.html'],
  ['examples','governance-lab-series/record-examples.html'],['guide','governance-lab-series/governance-lab-reference.html'],
  ['map','governance-lab-series/governance-lab-reference.html#system-map'],['catalog','governance-lab-series/lab-reference-library.html'],
  ['definitions','governance-lab-series/lab-reference-library.html#catalog-definitions'],
  ['types','governance-lab-series/lab-reference-library.html#catalog-types'],
  ['relations','governance-lab-series/lab-reference-library.html#catalog-relations'],
  ['record','governance-lab-series/reference/def-cal-definition-definition.html'],
  ['relation','governance-lab-series/reference/rel-relation-member-of.html'],
  ['craft','craft-documentation-proposal/craft-model.html'],['craft-example','craft-documentation-proposal/craft-model.html#definition'],
  ['robot','robot-learning-series/robot-learning-series.html'],['reader','governance-lab-series/research/reader-study.html'],
  ...Array.from({length:8},(_,i)=>['essay-'+(i+1),'governance-lab-series/lab-reference-library.html#essay-'+(i+1)])
 ];
 const errors=[],states=[],a11y=[];
 const onError=e=>errors.push({url:page.url(),message:String(e)});
 const onFailed=r=>errors.push({url:r.url(),failure:r.failure()});
 page.on('pageerror',onError);page.on('requestfailed',onFailed);
 const visible=e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'};
 for(const width of [320,390,768,1024,1440]){
  await page.setViewportSize({width,height:1000});
  for(const [name,path]of routes){
   try{
    await page.goto(base+path);await page.evaluate(()=>document.fonts.ready);
    await page.waitForFunction(()=>getComputedStyle(document.querySelector('main')).visibility!=='hidden',undefined,{timeout:7000});
    const row=await page.evaluate(()=>{
     const main=document.querySelector('main');const menu=document.querySelector('.site-navigation');const h=[...document.querySelectorAll('h1')].find(e=>e.getBoundingClientRect().height&&getComputedStyle(e).visibility!=='hidden');
     return {url:location.href,width:innerWidth,scrollWidth:document.documentElement.scrollWidth,mainVisible:!!main&&getComputedStyle(main).visibility!=='hidden',h1:h?.textContent.trim(),menu:menu?{open:menu.open,summary:getComputedStyle(menu.querySelector('summary')).display}:null,bodyText:main?.innerText.length};
    });
    if(row.scrollWidth>width+1||!row.mainVisible||!row.h1)row.failure='overflow, hidden main or missing visible title';
    if(width<=900&&row.menu){
     if(row.menu.open)row.failure='compact navigation starts open';
     await page.locator('.site-navigation > summary').click();
     const nav=await page.locator('.site-navigation nav').evaluate(e=>({width:e.clientWidth,scroll:e.scrollWidth,links:[...e.querySelectorAll('a')].map(a=>{const r=a.getBoundingClientRect();return {text:a.textContent,x:r.x,right:r.right,y:r.y,height:r.height}})}));
     row.expandedNavigation=nav;
     if(nav.scroll>nav.width+1||nav.links.some(a=>a.x<0||a.right>width+1||a.height<40))row.failure='expanded navigation clips or undersizes a destination';
     await page.locator('.site-navigation > summary').click();
    }
    if([390,1440].includes(width)&&['home','hackathon','start','catalog','record','craft'].includes(name)){
     row.screenshot=output+'/'+name+'-'+width+'.png';await page.screenshot({path:row.screenshot});
    }
    if(width===1440&&['home','hackathon','start','guide','catalog','record','craft'].includes(name)){
     await page.addScriptTag({path:'/home/vlad_/.npm/_npx/0f94ee7615faf582/node_modules/axe-core/axe.min.js'});
     const result=await page.evaluate(async()=>{
      const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});
      const pack=items=>items.map(x=>({id:x.id,impact:x.impact,help:x.help,nodes:x.nodes.map(n=>({target:n.target,html:n.html,failureSummary:n.failureSummary}))}));
      return {violations:pack(r.violations),incomplete:pack(r.incomplete)};
     });a11y.push({name,width,...result});
    }
    states.push({name,...row});
   }catch(error){states.push({name,width,failure:String(error)});}
  }
 }
 page.off('pageerror',onError);page.off('requestfailed',onFailed);
 return {summary:{states:states.length,failures:states.filter(s=>s.failure).length,runtimeErrors:errors.length,axeStates:a11y.length,axeViolations:a11y.reduce((n,x)=>n+x.violations.length,0)},states,errors,a11y};
}
