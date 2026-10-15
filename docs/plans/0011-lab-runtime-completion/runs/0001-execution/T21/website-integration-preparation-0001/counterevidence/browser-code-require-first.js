async (page) => {
 const fs=require('node:fs'),path=require('node:path');
 const owner=JSON.parse(fs.readFileSync('prototype/website/source/governance-lab-series/runtime/narrative.json','utf8'));
 const errors=[],badResponses=[],rows=[];
 page.on('pageerror',error=>errors.push(String(error)));
 page.on('response',response=>{if(response.status()>=400)badResponses.push({url:response.url(),status:response.status()});});
 for(const width of [1280,390]) {
  await page.setViewportSize({width,height:900});
  for(const item of owner.pages) {
   const response=await page.goto('http://127.0.0.1:18767/governance-lab-series/'+item.site_file);
   await page.waitForFunction(()=>document.querySelector('[data-site-runtime]'));
   const metrics=await page.evaluate(({id,sections})=>{
    const article=document.getElementById(id),box=article.getBoundingClientRect();
    return {title:document.title,h1:article.querySelector('h1').textContent,viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,article:{x:box.x,width:box.width},runtimeNavigation:document.querySelectorAll('aside [data-site-runtime]').length,toc:document.querySelectorAll('.docs-toc a[href^="#'+id+'-"]').length,expectedSections:sections,codeBlocks:article.querySelectorAll('pre code').length};
   },{id:item.article_id,sections:item.sections.length});
   rows.push({page:item.site_file,width,status:response.status(),...metrics,pass:response.status()===200&&metrics.h1===item.title&&metrics.runtimeNavigation===14&&metrics.toc>=item.sections.length&&metrics.documentWidth<=width+1});
   if(item.key==='overview')await page.screenshot({path:'output/playwright/runtime-overview-'+width+'.png',fullPage:true});
  }
 }
 await page.setViewportSize({width:1280,height:900});
 await page.goto('http://127.0.0.1:18767/governance-lab-series/runtime-overview.html');
 const search=page.getByRole('combobox',{name:'Search all documentation'});
 await search.fill('How do I recover and retry safely?');
 await page.waitForFunction(()=>document.querySelectorAll('[role="option"]').length>0);
 const options=await page.locator('[role="option"]').evaluateAll(nodes=>nodes.slice(0,5).map(n=>({text:n.textContent,href:n.getAttribute('href')})));
 await page.screenshot({path:'output/playwright/search-recovery-desktop.png',fullPage:false});
 const result={schema_version:'lab-T21-owned-browser-checks/v1',authority_effect:'none',method:'Cached offline Playwright CLI, explicit installed Chromium executable and process-local cached libraries. Expert browser checks only, no participant or runtime claims.',rows,errors,badResponses,search:{query:'How do I recover and retry safely?',options},pass:rows.every(r=>r.pass)&&errors.length===0&&badResponses.length===0&&options.slice(0,3).some(r=>(r.href||'').includes('runtime-recovery.html')),full_T21_complete:false};
 fs.writeFileSync('output/playwright/browser-checks.json',JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({pass:result.pass,pages:rows.length,errors,badResponses,failed:rows.filter(r=>!r.pass),search:result.search}));
}
