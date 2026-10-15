async page => {
 const base='http://127.0.0.1:8768/';const routes=new Set(['','governance-lab-series/start-here.html','governance-lab-series/incident-walkthrough.html','governance-lab-series/concept-comparisons.html','governance-lab-series/research.html','governance-lab-series/company-brain.html','governance-lab-series/hackathon.html','governance-lab-series/source-and-status.html','robot-learning-series/robot-learning-series.html','robot-learning-series/robot-learning-series.html#essay-1','robot-learning-series/robot-learning-series.html#essay-2','robot-learning-series/robot-learning-series.html#essay-3']);
 for(const path of ['governance-lab-series/governance-lab-reference.html','governance-lab-series/lab-reference-library.html','craft-documentation-proposal/craft-model.html']){
  await page.goto(base+path);await page.waitForFunction(()=>!document.documentElement.hasAttribute('data-docs-startup'));
  const links=await page.evaluate(()=>[...document.querySelectorAll('.article-tree a[href],.contents a[href]')].map(a=>new URL(a.href)).filter(u=>u.pathname===location.pathname&&u.hash).map(u=>u.pathname.slice(1)+u.hash));links.forEach(link=>routes.add(link));
 }
 const rows=[];await page.setViewportSize({width:1440,height:1000});
 for(const path of routes){
  try{
   const url=new URL(path,base);url.searchParams.set('mode','dark');await page.goto(url.href);await page.waitForFunction(()=>!document.documentElement.hasAttribute('data-docs-startup'));
   const result=await page.evaluate(()=>{
    const lum=rgb=>{const c=rgb.match(/[\d.]+/g)?.map(Number);if(!c||c.length>3&&c[3]<.98)return null;const v=c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;});return v[0]*.2126+v[1]*.7152+v[2]*.0722;};
    const candidates=[],surfaces=[],seen=new Set();
    for(const el of document.querySelectorAll('main *,article *,section *')){
     if(el.closest('svg,[aria-hidden="true"]')||!el.getClientRects().length)continue;
     const style=getComputedStyle(el);if(style.visibility==='hidden'||style.display==='none')continue;
     const selector=el.id?'#'+el.id:el.tagName.toLowerCase()+(typeof el.className==='string'&&el.className?'.'+el.className.trim().split(/\s+/).join('.'):'' );
     const rect=el.getBoundingClientRect();const background=lum(style.backgroundColor);
     if(background!==null&&background>.7&&rect.width*rect.height>1600&&!seen.has('surface'+selector)){surfaces.push({selector,background:style.backgroundColor,color:style.color,text:el.textContent.trim().slice(0,80)});seen.add('surface'+selector);}
     const direct=[...el.childNodes].filter(n=>n.nodeType===Node.TEXT_NODE).map(n=>n.textContent).join(' ').trim();
     if(direct.length<3)continue;const foreground=lum(style.color);if(foreground===null)continue;
     let parent=el,bg=null,bgColor;
     while(parent&&bg===null){bgColor=getComputedStyle(parent).backgroundColor;bg=lum(bgColor);parent=parent.parentElement;}
     if(bg===null)continue;const ratio=(Math.max(foreground,bg)+.05)/(Math.min(foreground,bg)+.05);
     if(ratio<3&&!seen.has(selector+style.color+bgColor)){candidates.push({selector,text:direct.slice(0,100),ratio:+ratio.toFixed(2),color:style.color,background:bgColor,size:style.fontSize});seen.add(selector+style.color+bgColor);}
    }
    return {route:document.body.dataset.docsRoute,lowContrastCandidates:candidates.slice(0,40),legacyLightSurfaces:surfaces.slice(0,25)};
   });rows.push({path,...result});
  }catch(error){rows.push({path,error:String(error)});}
 }
 return {routes:routes.size,rows};
}
