async page => {
  const errors=[],rows=[],shots=[];
  page.on('pageerror',e=>errors.push(String(e)));
  for(const palette of ['paper','mist','ink']){
    for(const mode of ['light','dark']){
      await page.goto(`http://127.0.0.1:8768/?palette=${palette}&mode=${mode}`);
      await page.emulateMedia({reducedMotion:'reduce'});
      for(const width of [320,390,768,1024,1440]){
        await page.setViewportSize({width,height:1000});
        await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
        const row=await page.evaluate(()=>{
          const s=getComputedStyle(document.documentElement);
          const hex=name=>s.getPropertyValue(name).trim();
          function lum(h){const rgb=h.replace('#','');const v=(rgb.length===3?[...rgb].map(v=>v+v).join(''):rgb).match(/../g).map(x=>parseInt(x,16)/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return v[0]*.2126+v[1]*.7152+v[2]*.0722;}
          const pairs=[['--ink','--paper'],['--muted','--paper'],['--muted','--soft'],['--muted','--panel'],['--on-accent','--accent'],['--accent','--paper'],['--green','--paper']].map(([a,b])=>{const A=lum(hex(a)),B=lum(hex(b));return {foreground:a,background:b,ratio:+((Math.max(A,B)+.05)/(Math.min(A,B)+.05)).toFixed(2)};});
          return {palette:document.documentElement.dataset.palette,mode:document.documentElement.dataset.theme,width:innerWidth,scroll:document.documentElement.scrollWidth,contrast:pairs,selectedPalette:document.querySelector('[data-palette-choice][aria-current]')?.dataset.paletteChoice};
        });
        row.pass=row.scroll<=width+1&&row.palette===palette&&row.mode===mode&&row.selectedPalette===palette&&row.contrast.every(p=>p.ratio>=4.5);rows.push(row);
      }
      await page.evaluate(()=>scrollTo(0,0));
      const hero=`output/playwright/telegraph-colors-20261014/${palette}-${mode}-desktop.png`;
      await page.screenshot({path:hero});shots.push(hero);
      if(mode===(palette==='ink'?'dark':'light')){
        await page.locator('#model').scrollIntoViewIfNeeded();await page.screenshot({path:`output/playwright/telegraph-colors-20261014/${palette}-demo.png`});
        await page.setViewportSize({width:390,height:844});await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:`output/playwright/telegraph-colors-20261014/${palette}-mobile.png`});
      }
    }
  }
  await page.goto('http://127.0.0.1:8768/?palette=paper&mode=light');
  await page.locator('[data-palette-choice=mist]').click();
  const chooser=await page.evaluate(()=>document.documentElement.dataset.palette==='mist'&&new URL(location.href).searchParams.get('palette')==='mist');
  await page.locator('.theme').click();const theme=await page.evaluate(()=>document.documentElement.dataset.theme==='dark');
  await page.reload();const persistence=await page.evaluate(()=>document.documentElement.dataset.theme==='dark');
  await page.locator('[data-stage=meaning]').click();await page.locator('[data-stage=meaning]').press('ArrowRight');
  const keyboard=await page.evaluate(()=>document.activeElement.id==='tab-work'&&document.querySelector('#stage-type').textContent==='WORK');
  return {summary:{states:rows.length,failures:rows.filter(r=>!r.pass).length,runtimeErrors:errors.length},rows,shots,chooser,theme,persistence,keyboard,errors};
}
