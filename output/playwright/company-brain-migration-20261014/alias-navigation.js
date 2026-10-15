async page=>{
 const rows=[],errors=[];page.on('pageerror',e=>errors.push(e.message));await page.emulateMedia({reducedMotion:'reduce'});
 const base='http://127.0.0.1:8767/governance-lab-series/index.html';
 const targets={craft:'paper-craft','hero-title':'paper-hero-title',explore:'paper-explore','home-example-title':'model'};
 for(const width of [390,1440])for(const mode of ['light','dark']){
  await page.setViewportSize({width,height:1000});
  for(const id of ['craft','hero-title','explore','home-example-title','hero-title']){
   const q='?mode='+mode+'&verify=scroll-final';await page.goto(base+q+'#'+id);await page.waitForURL(base+q+'#'+targets[id]);await page.waitForTimeout(150);const r=await page.locator('#'+targets[id]).evaluate(e=>e.getBoundingClientRect().toJSON());rows.push({width,mode,id,pass:r.top>=-2&&r.top<250,rect:r});
  }
 }
 const local='file:///home/vlad_/projects/CyberAlchemy-lab/website/dist/governance-lab-series/index.html?mode=dark&verify=scroll-final';
 for(const id of ['craft','hero-title']){await page.goto(local+'#'+id);await page.waitForURL(local+'#'+targets[id]);await page.waitForTimeout(150);const r=await page.locator('#'+targets[id]).evaluate(e=>e.getBoundingClientRect().toJSON());rows.push({id,fileOrigin:true,pass:r.top>=-2&&r.top<250,rect:r});}
 return{summary:{checks:rows.length,failures:rows.filter(r=>!r.pass).length,runtimeErrors:errors.length},rows,errors};
}
