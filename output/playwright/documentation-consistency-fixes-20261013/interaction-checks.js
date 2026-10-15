async (page) => {
  const checks=[],errors=[];
  page.on('pageerror',error=>errors.push(String(error)));
  const check=async(name,run)=>{
    try { const result=await run();checks.push({name,passed:result===true,result}); }
    catch(error){checks.push({name,passed:false,error:String(error)});}
  };
  const url='http://127.0.0.1:33733/governance-lab-series/reference/def-cal-definition-definition.html';
  await page.setViewportSize({width:390,height:844});await page.goto(url);
  const browse=page.locator('.article-contents');
  await check('mobile navigation starts collapsed',()=>browse.evaluate(el=>!el.open));
  await check('keyboard opens navigation',async()=>{await browse.locator('summary').press('Enter');return browse.evaluate(el=>el.open);});
  await check('keyboard closes navigation',async()=>{await browse.locator('summary').press('Space');return browse.evaluate(el=>!el.open);});
  await check('parent catalog link opens the correct library topic',async()=>{
    await browse.locator('summary').click();
    await page.locator('.article-tree a[data-library-route="catalog-definitions"]').click();
    await page.waitForURL('**/lab-reference-library.html#catalog-definitions');
    await page.waitForFunction(()=>document.body.dataset.docsEnhanced==='library');
    return await page.locator('.docs-topic-header h1').textContent()==='Definitions';
  });
  await page.setViewportSize({width:1440,height:1000});await page.goto(url);
  const identityLink=page.locator('.docs-toc a').filter({hasText:'Exact identity, version and content fingerprint'});
  const identityHash=await identityLink.getAttribute('href');
  await check('outline reveals closed identity details',async()=>{
    await identityLink.click();
    await page.waitForFunction(()=>document.getElementById(location.hash.slice(1)).closest('details').open);
    return page.evaluate(()=>{const target=document.getElementById(location.hash.slice(1)),r=target.getBoundingClientRect();return target.closest('details').open&&r.y>=document.querySelector('.topbar').getBoundingClientRect().bottom-2&&r.y<innerHeight;});
  });
  await check('direct fragment reload reveals the same formal details',async()=>{
    await page.goto(url+identityHash);
    await page.waitForFunction(()=>document.getElementById(location.hash.slice(1)).closest('details').open);
    return page.evaluate(()=>document.getElementById(location.hash.slice(1)).closest('details').open);
  });
  await check('outline and navigation respond to viewport changes',async()=>{
    await page.setViewportSize({width:390,height:844});
    await page.waitForFunction(()=>!document.querySelector('.article-contents').open&&!document.querySelector('.docs-toc').open);
    await page.setViewportSize({width:1440,height:1000});
    await page.waitForFunction(()=>document.querySelector('.article-contents').open&&document.querySelector('.docs-toc').open);
    return true;
  });
  const scopes=[['record',url],['guide','http://127.0.0.1:33733/governance-lab-series/governance-lab-reference.html#records'],['craft','http://127.0.0.1:33733/craft-documentation-proposal/craft-model.html#craft-overview']];
  for(const[label,start]of scopes)await check('site search reaches member-of from '+label,async()=>{
    await page.goto(start);await page.waitForFunction(()=>document.documentElement.dataset.docsStartup!=='pending');
    const input=page.getByLabel('Search all documentation',{exact:true});
    await input.fill('member-of');
    const result=page.locator('#docs-search-results a[href*="rel-relation-member-of.html"]').first();
    await result.waitFor({state:'visible',timeout:10000});
    await result.click();await page.waitForURL('**/reference/rel-relation-member-of.html*');
    return await page.locator('.record-page h1').textContent()==='member-of';
  });
  await check('escape dismisses search',async()=>{
    const input=page.getByLabel('Search all documentation',{exact:true});await input.fill('Definition');
    await page.locator('#docs-search-results').waitFor({state:'visible'});await input.press('Escape');
    return await input.getAttribute('aria-expanded')==='false'&&await page.locator('#docs-search-results').isHidden();
  });
  await page.goto('http://127.0.0.1:33733/governance-lab-series/reference/type-cal-artifact-type-typed-relation-v3.html');
  await check('formal code block supports keyboard focus',async()=>{
    const block=page.locator('.record-body pre').first();
    const summaries=await block.evaluate(el=>{const ids=[];for(let detail=el.closest('details');detail;detail=detail.parentElement.closest('details'))if(!detail.open)ids.push(detail.querySelector('summary').id);return ids.reverse();});
    for(const id of summaries){const summary=page.locator('[id="'+id+'"]');await summary.scrollIntoViewIfNeeded();await summary.press('Enter');}
    await block.focus();return block.evaluate(el=>document.activeElement===el&&el.getAttribute('role')==='region'&&!!el.getAttribute('aria-label'));
  });
  return JSON.stringify({checks,errors});
}
