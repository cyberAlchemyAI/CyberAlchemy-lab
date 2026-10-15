async page=>{
 const lab='http://127.0.0.1:8767/governance-lab-series/';const out='/home/vlad_/projects/CyberAlchemy-lab/output/playwright/paper-crimson-current-20261014';const rows=[],a11y=[],errors=[];page.on('pageerror',e=>errors.push(e.message));await page.emulateMedia({reducedMotion:'reduce'});
 for(const mode of ['light','dark'])for(const width of [390,1440]){
 await page.setViewportSize({width,height:1000});await page.goto(lab+'index.html?mode='+mode+'&verify=focused#lab');await page.locator('.brain-map-node[data-brain-part=agents]').click();
 rows.push(await page.evaluate(()=>({width:innerWidth,theme:document.documentElement.dataset.theme,overflow:document.documentElement.scrollWidth>innerWidth+1,open:document.querySelector('.home-background').open,agentColor:getComputedStyle(document.querySelector('.brain-agents strong')).color,buttonColor:getComputedStyle(document.querySelector('.legacy-home-content .ds-button')).color,buttonBg:getComputedStyle(document.querySelector('.legacy-home-content .ds-button')).backgroundColor})));
 await page.addScriptTag({path:'/home/vlad_/.npm/_npx/0f94ee7615faf582/node_modules/axe-core/axe.min.js'});const a=await page.evaluate(async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});return {violations:r.violations,incomplete:r.incomplete};});a11y.push({mode,width,...a});await page.screenshot({path:out+'/focused-home-background-'+width+'-'+mode+'.png'});
 }
 await page.goto(lab+'index.html?mode=dark&verify=focused-banner');await page.screenshot({path:out+'/final-home-dark.png'});
 await page.goto(lab+'governance-lab-reference.html?verify=focused-map#system-map');await page.waitForFunction(()=>!document.documentElement.hasAttribute('data-docs-startup'));await page.screenshot({path:out+'/final-system-map.png'});
 const title=await page.locator('#smap-overview-records-title').textContent();
 return {summary:{states:rows.length,overflows:rows.filter(r=>r.overflow).length,closedLegacySections:rows.filter(r=>!r.open).length,a11yStates:a11y.length,violations:a11y.reduce((n,a)=>n+a.violations.length,0),runtimeErrors:errors.length},rows,a11y,mapAccessibleName:title,errors};
}
