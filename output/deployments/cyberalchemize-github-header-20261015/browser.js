async page=>{
 const base='https://cyberalchemize.com/',out='/home/vlad_/projects/CyberAlchemy-lab/output/deployments/cyberalchemize-github-header-20261015';
 const routes=['governance-lab-series/index.html','governance-lab-series/governance-lab-reference.html','governance-lab-series/reference/def-cal-definition-actor.html','governance-lab-series/hackathon.html'];
 const rows=[],checks=[],errors=[],audits=[];const check=(name,pass,data={})=>checks.push({name,pass,...data});
 page.on('pageerror',e=>errors.push(String(e)));const cdp=await page.context().newCDPSession(page);await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});await page.emulateMedia({reducedMotion:'reduce'});
 try{
 for(const route of routes)for(const width of [320,390,1440])for(const mode of ['light','dark']){
  await page.setViewportSize({width,height:900});const res=await page.goto(base+route+'?mode='+mode+'&review=github-header');check('HTTP '+route,res.status()===200);await page.evaluate(async()=>{await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))});
  const state=await page.evaluate(()=>{
   const header=document.querySelector('header.header,.topbar'),link=header?.querySelector('.github-cta'),r=link?.getBoundingClientRect(),cs=link&&getComputedStyle(link),box=e=>e.getBoundingClientRect().toJSON();
   const controls=header?[...header.querySelectorAll('a,button,input,summary')].filter(e=>e!==link&&!link?.contains(e)&&e.getBoundingClientRect().width&&getComputedStyle(e).visibility!=='hidden'):[];
   const overlap=link?controls.filter(e=>{const b=e.getBoundingClientRect();return b.right>r.left+1&&b.left<r.right-1&&b.bottom>r.top+1&&b.top<r.bottom-1}).map(e=>e.textContent.trim()||e.getAttribute('aria-label')):[];
   return{href:link?.href,label:link?.getAttribute('aria-label'),icon:!!link?.querySelector('svg[aria-hidden="true"]'),rect:r?.toJSON(),theme:document.documentElement.dataset.theme,color:cs?.color,background:cs?.backgroundColor,overflow:document.documentElement.scrollWidth>innerWidth+1,overlap,controls:controls.map(e=>({label:e.textContent.trim()||e.getAttribute('aria-label'),rect:box(e)}))};
  });rows.push({route,width,mode,...state});check('visible usable header CTA '+route+' '+width+' '+mode,!!state.rect&&state.rect.height>=44&&state.rect.width>=44&&state.rect.left>=0&&state.rect.right<=width&&state.rect.top<240&&state.icon&&!state.overflow&&!state.overlap.length&&state.href==='https://github.com/cyberAlchemyAI/CyberAlchemy-lab'&&state.color!==state.background,{state});
  await page.locator('.github-cta').first().focus();await page.keyboard.press('Tab');await page.keyboard.press('Shift+Tab');check('keyboard reaches CTA '+route+' '+width+' '+mode,await page.locator('.github-cta').first().evaluate(e=>e===document.activeElement));
  if(['governance-lab-series/index.html','governance-lab-series/governance-lab-reference.html'].includes(route)&&[390,1440].includes(width)){
   await page.screenshot({path:out+'/'+(route.endsWith('index.html')?'home':'docs')+'-'+width+'-'+mode+'.png'});
   await page.addScriptTag({path:'/home/vlad_/.npm/_npx/0f94ee7615faf582/node_modules/axe-core/axe.min.js'});const audit=await page.evaluate(async()=>{const r=await axe.run(document.querySelector('header.header,.topbar'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)}))});audits.push({route,width,mode,violations:audit});
  }
  if(width===320&&mode==='light'){
   const summary=page.locator('.site-navigation>summary,.more>summary').first();if(await summary.count()){await summary.click();check('mobile menu opens '+route,await summary.evaluate(e=>e.parentElement.open));check('CTA survives menu opening '+route,await page.locator('.github-cta').isVisible());await summary.click()}
   const theme=page.locator('.site-theme-toggle,.theme').first();if(await theme.count()){await theme.click();check('theme toggle works '+route,await page.evaluate(()=>document.documentElement.dataset.theme==='dark'))}
  }
 }
 }catch(e){errors.push(String(e))}
 return{summary:{layouts:rows.length,checks:checks.length,failures:checks.filter(c=>!c.pass).length,runtimeErrors:errors.length,a11yStates:audits.length,a11yViolations:audits.reduce((n,a)=>n+a.violations.length,0)},rows,checks,errors,audits};
}
