async page => {
  const rows = [], errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  await page.goto('http://127.0.0.1:8768/');
  for (const width of [320,390,768,1024,1440]) {
    await page.setViewportSize({width,height:1000});
    for (const dark of [false,true]) {
      if (await page.locator('.theme').getAttribute('aria-pressed') !== String(dark)) await page.locator('.theme').click();
      rows.push(await page.evaluate(() => ({width:innerWidth,theme:document.documentElement.dataset.theme,scrollWidth:document.documentElement.scrollWidth,pass:document.documentElement.scrollWidth<=innerWidth+1,images:[...document.images].every(image=>image.complete&&image.naturalWidth>0)})));
    }
  }
  await page.locator('.theme').click();
  const states = [];
  for (const stage of ['meaning','work','evidence','decision']) {
    await page.locator(`[data-stage=${stage}]`).click();
    states.push({stage,selected:await page.locator(`[data-stage=${stage}]`).getAttribute('aria-selected'),title:await page.locator('#stage-title').innerText(),records:await page.locator('.connection-list li.active').count()});
  }
  await page.locator('[data-stage=meaning]').click();
  await page.locator('[data-stage=meaning]').press('ArrowRight');
  const keyboard = await page.evaluate(()=>document.activeElement.id==='tab-work'&&document.activeElement.getAttribute('aria-selected')==='true');
  await page.locator('[data-stage=work]').press('End');
  const keyboardEnd = await page.evaluate(()=>document.activeElement.id==='tab-decision');
  await page.locator('.more summary').click();
  const menuOpen = await page.locator('.more').getAttribute('open')!==null;
  await page.locator('.more summary').press('Escape');
  const escape = await page.evaluate(()=>!document.querySelector('.more').open&&document.activeElement.matches('.more summary'));
  await page.locator('.theme').click();
  await page.reload();
  const persistence = await page.locator('.theme').getAttribute('aria-pressed')==='true';
  await page.locator('.theme').click();
  await page.locator('[data-stage=meaning]').click();
  const links = await page.evaluate(()=>[...document.querySelectorAll('a[href^="#"]')].map(a=>({href:a.getAttribute('href'),valid:a.getAttribute('href')==='#'||!!document.getElementById(a.getAttribute('href').slice(1))})));
  await page.emulateMedia({reducedMotion:'reduce'});
  const reducedMotion=await page.evaluate(()=>getComputedStyle(document.documentElement).scrollBehavior==='auto');
  await page.setViewportSize({width:1440,height:1000});await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:'output/playwright/telegraph-direction-20261014/final-desktop.png',fullPage:true});
  await page.locator('.theme').click();await page.screenshot({path:'output/playwright/telegraph-direction-20261014/final-dark.png'});await page.locator('.theme').click();
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:'output/playwright/telegraph-direction-20261014/final-mobile.png',fullPage:true});
  return {summary:{responsiveStates:rows.length,failures:rows.filter(r=>!r.pass||!r.images).length,runtimeErrors:errors.length},rows,states,keyboard,keyboardEnd,menuOpen,escape,persistence,reducedMotion,links,errors};
}
