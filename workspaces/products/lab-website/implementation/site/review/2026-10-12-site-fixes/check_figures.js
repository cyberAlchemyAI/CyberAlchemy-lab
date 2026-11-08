async(page)=>{
 const config=/*CONFIG*/ {},rows=[];const events=[];
 const onerror=e=>events.push(String(e));page.on('pageerror',onerror);
 await page.setViewportSize({width:1440,height:1000});
 // Figure links are supplied by the generated article, not a guessed list.
 await page.goto(config.base+'craft-documentation-proposal/craft-model.html#definition');
 const craft=await page.locator('img[src*="assets/figures/"]').evaluateAll(nodes=>[...new Set(nodes.map(n=>n.src))]);
 await page.goto(config.base+'governance-lab-series/governance-lab-reference.html#start');
 const guide=await page.locator('.diagram-shell>svg').evaluateAll(nodes=>nodes.map(svg=>({id:svg.querySelector('title')?.id,source:svg.outerHTML})));
 const assets=[];
 for(const figure of guide){const id=figure.id?.replace(/-title$/,'');if(id)assets.push(config.base+'governance-lab-series/assets/'+id+'.svg');}
 for(const url of [...craft,...assets]){
  try{
   const response=await page.goto(url);await page.evaluate(()=>document.fonts?.ready);const result=await page.evaluate(()=>{
    const svg=document.querySelector('svg'),view=svg.viewBox.baseVal;
    const box=b=>({x:b.x,y:b.y,width:b.width,height:b.height});
    const contains=(r,b)=>b.x>=r.x-1&&b.y>=r.y-1&&b.x+b.width<=r.x+r.width+1&&b.y+b.height<=r.y+r.height+1;
    const groups=[...svg.querySelectorAll('g')].filter(g=>g.querySelector(':scope>text')&&g.querySelector(':scope>rect,:scope>polygon,:scope>ellipse'));
    const nodes=groups.map(g=>{
     const shapes=[...g.querySelectorAll(':scope>rect,:scope>polygon,:scope>ellipse')].map(s=>box(s.getBBox()));
     const x=Math.min(...shapes.map(b=>b.x)),y=Math.min(...shapes.map(b=>b.y));const shape={x,y,width:Math.max(...shapes.map(b=>b.x+b.width))-x,height:Math.max(...shapes.map(b=>b.y+b.height))-y};
     return {shape,text:[...g.querySelectorAll(':scope>text')].map(t=>({text:t.textContent.trim(),bounds:box(t.getBBox())})).filter(t=>!contains(shape,t.bounds))};
    });
    const clipped=[...svg.querySelectorAll('text')].map(t=>({text:t.textContent.trim(),bounds:box(t.getBBox())})).filter(t=>!contains({x:view.x,y:view.y,width:view.width,height:view.height},t.bounds));
    return {title:svg.querySelector('title')?.textContent,nodes:groups.length,nodeOverflow:nodes.filter(n=>n.text.length),clipped};
   });rows.push({url,status:response?.status(),...result});
  }catch(error){rows.push({url,error:String(error)});}
 }
 page.off('pageerror',onerror);return JSON.stringify({rows,events});
}
