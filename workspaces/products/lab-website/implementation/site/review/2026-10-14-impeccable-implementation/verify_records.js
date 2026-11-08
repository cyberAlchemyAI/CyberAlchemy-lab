async page=>{
 const base='http://127.0.0.1:8766/candidate-site/governance-lab-series/';
 await page.goto(base+'index.html');
 const records=await page.evaluate(async base=>(await(await fetch(base+'research/reference-pages.json')).json()).records,base);
 const states=[],errors=[];const listener=e=>errors.push(String(e));page.on('pageerror',listener);
 for(const width of [390,1440]){
  await page.setViewportSize({width,height:1000});
  for(const record of records){
   try{
    const path=record.path||record.href||record.file;
    if(!path)throw new Error('No record page path: '+JSON.stringify(record));
    await page.goto(new URL(path,base).href);await page.evaluate(()=>document.fonts.ready);
    await page.waitForFunction(()=>getComputedStyle(document.querySelector('main')).visibility!=='hidden',undefined,{timeout:7000});
    const data=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,h1:document.querySelector('h1')?.textContent,body:!!document.querySelector('.record-body'),menu:!!document.querySelector('.site-navigation'),selected:!!document.querySelector('.article-tree [aria-current]'),visible:getComputedStyle(document.querySelector('main')).visibility}));
    states.push({id:record.id,width,...data,pass:data.scroll<=width+1&&!!data.h1&&data.body&&data.menu&&data.selected&&data.visible!=='hidden'});
   }catch(error){states.push({id:record.id,width,pass:false,error:String(error)});}
  }
 }
 page.off('pageerror',listener);
 return {summary:{records:records.length,states:states.length,failures:states.filter(x=>!x.pass).length,runtimeErrors:errors.length},states,errors};
}
