async page=>{
 const rows=[];
 for(const width of [320,390,768]){
  await page.setViewportSize({width,height:900});
  for(const mode of ['light','dark'])for(const [edition,base]of [['live','https://cyberalchemize.com/'],['preview','http://127.0.0.1:8780/']]){
   await page.goto(base+'governance-lab-series/index.html');const toggle=page.getByRole('button',{name:new RegExp(`Switch to ${mode}`)});if(await toggle.count())await toggle.click();
   await page.screenshot({path:`output/playwright/open-brain-style-correction/mobile-${edition}-${width}-${mode}-home.png`});
   rows.push(await page.evaluate(({edition,width,mode})=>{const props=el=>el?{cls:el.className,font:getComputedStyle(el).fontSize,line:getComputedStyle(el).lineHeight,color:getComputedStyle(el).color,pad:getComputedStyle(el).padding,border:getComputedStyle(el).border,width:el.getBoundingClientRect().width,left:el.getBoundingClientRect().left}:null;return{edition,width,mode,pageWidth:document.documentElement.scrollWidth,body:props(document.body),frame:props(document.querySelector('.page-frame,.site-frame,.frame')),header:props(document.querySelector('header')),h1:props(document.querySelector('h1')),hero:props(document.querySelector('.hero')),heroImage:props(document.querySelector('.hero img')),links:[...document.querySelectorAll('header a')].filter(e=>e.checkVisibility()).map(e=>e.textContent.trim())}}, {edition,width,mode}));
  }
  for(const [edition,base]of [['live','https://cyberalchemize.com/'],['preview','http://127.0.0.1:8780/']]){
   await page.goto(base+'governance-lab-series/start-here.html');const toggle=page.getByRole('button',{name:/Switch to light/});if(await toggle.count())await toggle.click();
   await page.screenshot({path:`output/playwright/open-brain-style-correction/mobile-${edition}-${width}-light-start.png`});
   rows.push(await page.evaluate(({edition,width})=>({edition,width,route:'start',pageWidth:document.documentElement.scrollWidth,bodyClass:document.body.className,header:document.querySelector('header')?.className,font:getComputedStyle(document.querySelector('main p')).fontSize,padding:getComputedStyle(document.querySelector('main')).padding}),{edition,width}));
  }
 }
 return rows;
}
