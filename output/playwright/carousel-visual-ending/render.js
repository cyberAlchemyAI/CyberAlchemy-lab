async(page) => {
  const out = '/home/vlad_/projects/CyberAlchemy-lab/website/promotion/governance-teaser/investigation-v3/';
  const evidence = '/home/vlad_/projects/CyberAlchemy-lab/output/playwright/carousel-visual-ending/';
  await page.route('**/*', route => route.continue());
  await page.goto('http://127.0.0.1:34717/investigation-v3/index.html?visual-ending=' + Date.now());
  await page.setViewportSize({width:1200,height:1500});
  await page.evaluate(() => document.body.classList.add('export'));
  await page.evaluate(() => document.fonts.ready);
  await page.locator('.slide img').evaluateAll(nodes => Promise.all(nodes.map(n => n.decode())));
  const slides = page.locator('.slide');
  for (let i=9; i<await slides.count(); i++) await slides.nth(i).screenshot({path:out+'slide-'+(i+1)+'.png'});
  await page.pdf({path:out+'cyberalchemy-governance-investigation.pdf',preferCSSPageSize:true,printBackground:true,tagged:true,outline:true});
  const geometry = await slides.evaluateAll(nodes => nodes.map((n,i) => {
    const f=n.querySelector('footer').getBoundingClientRect(), b=n.getBoundingClientRect();
    const content=[...n.children].filter(x => !['HEADER','FOOTER','IMG'].includes(x.tagName));
    return {slide:i+1,title:n.querySelector('h1,h2').innerText,contentBottom:Math.round(Math.max(...content.map(x=>x.getBoundingClientRect().bottom))-b.top),footerTop:Math.round(f.top-b.top)};
  }));
  const comparison=[];
  await page.goto('http://127.0.0.1:34717/compare-v3.html?visual-ending='+Date.now());
  for(const width of [1440,390]) {
    await page.setViewportSize({width,height:width===1440?1100:844});
    for(let section=0; section<10; section++) {
      await page.locator('#section').selectOption(String(section));
      await page.locator('.images img').evaluateAll(nodes=>Promise.all(nodes.map(n=>n.decode())));
      comparison.push(await page.evaluate(()=>({width:innerWidth,section:document.querySelector('#section').selectedOptions[0].textContent,count:document.querySelector('#count').textContent,brokenImages:[...document.images].filter(n=>!n.naturalWidth).length,overflow:document.documentElement.scrollWidth>innerWidth})));
    }
    await page.screenshot({path:evidence+'comparison-'+width+'.png',fullPage:true});
  }
  return {geometry,comparison};
}
