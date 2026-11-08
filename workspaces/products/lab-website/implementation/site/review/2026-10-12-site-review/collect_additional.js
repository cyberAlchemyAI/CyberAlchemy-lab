async (page) => {
  const config=/*CONFIG*/ {};
  const rows=[];
  page.setDefaultTimeout(20000);
  async function scenario(name,fn){const row={name};try{row.result=await fn();row.outcome='observed';}catch(error){row.error=String(error);row.outcome='failed';}rows.push(row);}
  const screenshot=async name=>{const file=config.output+'/screenshots/additional-'+name+'.png';await page.screenshot({path:file,timeout:60000});return file;};
  await scenario('all system-map layouts, nodes and relationship equivalents',async()=>{
    await page.setViewportSize({width:1440,height:1000});await page.goto(config.base+'governance-lab-series/governance-lab-reference.html#system-map');
    const explorer=page.locator('#map-explorer');if(!(await explorer.evaluate(el=>el.open)))await explorer.locator(':scope>summary').click();
    const model=await page.evaluate(()=>JSON.parse(document.getElementById('system-map-data').textContent));const layouts=[];
    for(const view of model.views){
      await page.getByRole('button',{name:view.title,exact:true}).click();
      for(const graph of view.focus_views||[view]){
        if(view.focus_views)await page.locator('[data-governance-focus="'+graph.focus_key+'"]').click();
        const nodes=[];
        for(const placement of graph.placements){
          // Selecting an axis in the overview intentionally opens its lens.
          // Restore the starting lens before examining the next concept.
          if(view.focus_views)await page.locator('[data-governance-focus="'+graph.focus_key+'"]').click();
          await page.locator('#map-diagram-mode').click();
          const node=page.locator('[data-map-node="'+placement.node+'"]:visible');await node.click();
          nodes.push({id:placement.node,expected:model.nodes[placement.node].title,observed:await page.locator('#map-node-title').innerText(),selectedButtons:await page.locator('[data-map-node][aria-pressed="true"]').count(),url:page.url()});
        }
        if(view.focus_views)await page.locator('[data-governance-focus="'+graph.focus_key+'"]').click();
        await page.locator('#map-list-mode').click();const text=await page.locator('#map-relationship-list').innerText();
        const pairs=graph.edges.map(edge=>({source:edge.source,target:edge.target,label:edge.label,text:model.nodes[edge.source].title+' — '+edge.label+' → '+model.nodes[edge.target].title}));
        const missing=pairs.filter(p=>!text.includes(p.text));await page.locator('#map-diagram-mode').click();
        const dimensions=await page.locator('.smap-diagram:visible').evaluate(svg=>({width:svg.getBoundingClientRect().width,height:svg.getBoundingClientRect().height,viewBox:svg.getAttribute('viewBox'),text:[...svg.querySelectorAll('text')].map(el=>({text:el.textContent.trim(),font:parseFloat(getComputedStyle(el).fontSize)*svg.getBoundingClientRect().width/svg.viewBox.baseVal.width}))}));
        layouts.push({view:view.id,focus:graph.focus_key||null,nodes,edges:pairs.length,missingTextEdges:missing,dimensions});
      }
    }
    await page.getByRole('button',{name:'Governance',exact:true}).click();await page.locator('[data-governance-focus="authority"]').click();
    const node=page.locator('[data-map-node]:visible').first();await node.focus();await page.keyboard.press('Enter');
    const keyboard={pressed:await node.getAttribute('aria-pressed'),feedback:await page.locator('#map-node-title').innerText()};
    await page.locator('#map-zoom-in').click();const zoom=await page.locator('#map-zoom-status').innerText();
    return {layouts,keyboard,zoom,screenshot:await screenshot('governance-map')};
  });
  await scenario('session demonstration after closing',async()=>{
    await page.goto(config.base+'governance-lab-series/governance-lab-reference.html#agent');const button=page.getByRole('button',{name:'Close this session',exact:true});await button.click();
    return {text:await page.locator('#agent').innerText(),buttons:await page.getByRole('button').allTextContents(),screenshot:await screenshot('session-closed')};
  });
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
  await scenario('root, Craft and legacy redirects',async()=>{
    const paths=['index.html?review=1#how','craft-documentation-proposal/index.html?review=1#definition',
      'governance-lab-series/governance-authority.html?review=1#authority-incident',
      'governance-lab-series/governance-provenance.html?review=1#provenance-incident',
      'governance-lab-series/governance-lifecycle.html?review=1#lifecycle-example'];
    const results=[];
    for(const path of paths){await page.goto(config.base+path);await page.waitForTimeout(150);results.push({source:path,destination:page.url(),title:await page.title()});}
    return results;
  });
  await scenario('offline file delivery, robot navigation and company links',async()=>{
    const results=[];
    for(const path of ['governance-lab-series/index.html','governance-lab-series/research.html','governance-lab-series/lab-reference-library.html#essay-6','craft-documentation-proposal/craft-model.html#definition','robot-learning-series/robot-learning-series.html']){
      await page.goto(config.fileBase+path);const search=page.locator('#docs-search-input');let count=null;
      if(await search.count()){await search.fill('Work');await page.locator('.site-search-results a').first().waitFor();count=await page.locator('.site-search-results a').count();}
      results.push({path,url:page.url(),searchResults:count,brandHref:await page.locator('.brand').getAttribute('href').catch(()=>null),links:await page.locator('a[href]').evaluateAll(nodes=>nodes.map(n=>({text:n.textContent.trim().slice(0,100),href:n.getAttribute('href')})))});
    }
    return results;
  });
  await scenario('no-JavaScript reading and redirect fallback',async()=>{
    const context=await page.context().browser().newContext({javaScriptEnabled:false,viewport:{width:390,height:1000}});const tab=await context.newPage();const results=[];
    try{
      for(const path of ['governance-lab-series/index.html','governance-lab-series/start-here.html','governance-lab-series/governance-lab-reference.html#governance','governance-lab-series/lab-reference-library.html#reference','craft-documentation-proposal/craft-model.html#definition','governance-lab-series/governance-authority.html']){
        await tab.goto(config.base+path);await tab.waitForTimeout(150);results.push({path,destination:tab.url(),headings:await tab.getByRole('heading',{level:1}).allTextContents(),overflow:await tab.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)});
      }
    }finally{await context.close();}return results;
  });
  return JSON.stringify({rows});
}
