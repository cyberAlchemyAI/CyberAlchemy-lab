async(page)=>{const config={"base": "http://127.0.0.1:8766/candidate-site/", "output": "/home/vlad_/projects/CyberAlchemy-lab/output/playwright/impeccable-implementation-20261014", "run": "impeccable-map-nodes"};const rows=[];page.setDefaultTimeout(20000);async function scenario(name,fn){try{rows.push({name,result:await fn()});}catch(error){rows.push({name,error:String(error)});}}
const screenshot=async name=>{const file=config.output+'/screenshots/'+config.run+'-'+name+'.png';await page.screenshot({path:file});return file;};
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
          const node=page.locator('[data-map-node="'+placement.node+'"]:visible');await page.locator('#map-node-picker').selectOption(placement.node);
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

return JSON.stringify({rows});}
