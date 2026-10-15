async(page)=>{
 const config=/*CONFIG*/ {};await page.setViewportSize({width:390,height:1000});await page.goto(config.base+'robot-learning-series/robot-learning-series.html');
 return JSON.stringify(await page.evaluate(()=>[...document.querySelectorAll('body *')].filter(el=>{const r=el.getBoundingClientRect();return r.width&&r.right>innerWidth+1;}).map(el=>({tag:el.tagName,class:el.className,text:el.textContent.trim().slice(0,70),rect:el.getBoundingClientRect().toJSON(),width:getComputedStyle(el).width,minWidth:getComputedStyle(el).minWidth,overflow:getComputedStyle(el).overflow,display:getComputedStyle(el).display}))));
}
