async(page)=>{const config=/*CONFIG*/ {};const rows=[];page.setDefaultTimeout(20000);async function scenario(name,fn){try{rows.push({name,result:await fn()});}catch(error){rows.push({name,error:String(error)});}}
const screenshot=async name=>{const file=config.output+'/screenshots/'+name+'.png';await page.screenshot({path:file});return file;};
  await scenario('actual browser zoom at 200 and 400 percent',async()=>{
    const settings=await page.context().newPage();await settings.goto('chrome://settings/appearance');
    const available=await settings.evaluate(()=>Boolean(chrome.settingsPrivate?.setDefaultZoom));if(!available)throw new Error('Browser zoom API unavailable');
    const results=[];
    try{
      await page.setViewportSize({width:1280,height:1000});
      for(const zoom of [2,4]){
        await settings.evaluate(zoom=>new Promise(resolve=>chrome.settingsPrivate.setDefaultZoom(zoom,resolve)),zoom);
        for(const path of ['governance-lab-series/index.html','governance-lab-series/start-here.html','craft-documentation-proposal/craft-model.html#definition','governance-lab-series/lab-reference-library.html#essay-6','robot-learning-series/robot-learning-series.html']){
          await page.goto(config.base+path);await page.evaluate(()=>document.fonts.ready);
          const measurements=await page.evaluate(()=>({innerWidth,devicePixelRatio,scrollWidth:document.documentElement.scrollWidth,header:document.querySelector('.topbar')?.getBoundingClientRect().height,search:Boolean(document.querySelector('#docs-search-input'))}));
          if(measurements.search){await page.keyboard.press('/');await page.getByRole('combobox',{name:'Search all documentation'}).fill('Work');await page.locator('.site-search-results a').first().waitFor();await page.keyboard.press('ArrowDown');}
          const active=await page.evaluate(()=>{const r=document.activeElement.getBoundingClientRect();return {tag:document.activeElement.tagName,x:r.x,y:r.y,width:r.width,height:r.height};});
          results.push({path,zoom,measurements,active});
          if(path.includes('start-here'))await screenshot('zoom-'+zoom);
        }
      }
    }finally{await settings.evaluate(()=>new Promise(resolve=>chrome.settingsPrivate.setDefaultZoom(1,resolve)));await settings.close();}
    return results;
  });

return JSON.stringify({rows});}
