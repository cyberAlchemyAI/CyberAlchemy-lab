async page => {
 const out='/home/vlad_/projects/CyberAlchemy-lab/output/playwright/docs-cards-20261014';
 await page.setViewportSize({width:1440,height:1000});
 await page.screenshot({path:out+'/reference-guide.png'});
 const reference=await page.evaluate(()=>({cards:[...document.querySelectorAll('a[href^="/guide/"]')].map(a=>({text:a.innerText,css: Object.fromEntries(['backgroundColor','border','borderRadius','padding','fontFamily','fontSize','display'].map(k=>[k,getComputedStyle(a)[k]]))})),main:document.querySelector('main')?.outerHTML.slice(0,1500)}));
 await page.goto('https://guide.telegraphprotocol.com/guide/miner');await page.screenshot({path:out+'/reference-path.png'});
 const path=await page.evaluate(()=>({headings:[...document.querySelectorAll('h1,h2,h3')].map(h=>h.innerText),steps:[...document.querySelectorAll('button')].map(b=>({text:b.innerText,expanded:b.getAttribute('aria-expanded')}))}));
 const pages=[];
 for(const slug of ['governance-lab-series/start-here.html','governance-lab-series/governance-lab-reference.html#start','governance-lab-series/lab-reference-library.html#articles-library','craft-documentation-proposal/craft-model.html#craft-overview','governance-lab-series/read-record.html']) {
 await page.goto('http://127.0.0.1:8768/'+slug);await page.waitForFunction(()=>!document.documentElement.hasAttribute('data-docs-startup'));await page.emulateMedia({reducedMotion:'reduce'});await page.screenshot({path:out+'/before-'+slug.split('/').pop().split('.')[0]+'.png'});
 pages.push(await page.evaluate(()=>({url:location.href,main:document.querySelector('main')?.className,headings:[...document.querySelectorAll('main h1,main h2,main h3')].filter(h=>h.getBoundingClientRect().width).slice(0,22).map(h=>h.textContent),navs:[...document.querySelectorAll('main nav')].map(n=>({class:n.className,label:n.getAttribute('aria-label'),html:n.outerHTML.slice(0,3500)}))})));
 }
 return {reference,path,pages};
}
