async (page) => {
  const config=/*CONFIG*/ {};
  const rows=[];const events=[];
  page.setDefaultTimeout(12000);
  const event=error=>events.push({url:page.url(),error:String(error)});
  page.on('pageerror',event);
  await page.context().tracing.start({screenshots:true,snapshots:true,sources:false});
  async function scenario(name,fn){
    const row={name};try{row.result=await fn();row.outcome='observed';}catch(error){row.error=String(error);row.outcome='failed';}rows.push(row);
  }
  async function go(path,width=1440){await page.setViewportSize({width,height:1000});await page.goto(config.base+path,{waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);}
  const screenshot=async name=>{const p=config.output+'/screenshots/journey-'+name+'.png';await page.screenshot({path:p,animations:'allow',timeout:60000});return p;};
  const focus=()=>page.evaluate(()=>{const e=document.activeElement,r=e.getBoundingClientRect();return {tag:e.tagName,id:e.id,text:e.textContent.trim().slice(0,100),rect:{x:r.x,y:r.y,width:r.width,height:r.height},viewport:{width:innerWidth,height:innerHeight}};});
  await scenario('homepage role selection and reset',async()=>{
    await go('governance-lab-series/index.html');const results=[];
    for(const label of ['People Intentions & review','Agents Scoped sessions','Knowledge Meaning & evidence','Work Plans & attempts','Decisions Review & change']){
      const button=page.getByRole('button',{name:label,exact:true});await button.click();results.push({label,pressed:await button.getAttribute('aria-pressed'),detail:await page.locator('.brain-map-detail').innerText()});await button.click();results.at(-1).reset=await button.getAttribute('aria-pressed');
    }
    return {results,screenshot:await screenshot('home-roles')};
  });
  await scenario('homepage to introduction to incident to governance',async()=>{
    await page.getByRole('link',{name:'Explore the Lab',exact:true}).click();const intro=page.url();
    await page.getByRole('link',{name:'Follow an incident',exact:true}).first().click();const incident=page.url();
    await page.getByRole('link',{name:'Authority and meaning',exact:true}).first().click();const authority=page.url();
    await page.getByText('Read the full definition',{exact:true}).filter({visible:true}).click();
    const formal=await page.locator('#governance .definition-card').first().innerText().catch(()=>page.locator('#governance details[open]').first().innerText());
    return {intro,incident,authority,formal:formal.slice(0,9000),screenshot:await screenshot('definition-expanded')};
  });
  await scenario('guide topic navigation and browser history',async()=>{
    await go('governance-lab-series/governance-lab-reference.html#governance');
    await page.getByRole('link',{name:'Provenance and evidence',exact:true}).first().click();const evidence=page.url();
    await page.getByRole('link',{name:'Lifecycle and admission',exact:true}).first().click();const change=page.url();
    await page.goBack();const back=page.url();await page.goForward();const forward=page.url();
    return {evidence,change,back,forward,current:await page.locator('.article-tree [aria-current="page"]').innerText(),focus:await focus()};
  });
  await scenario('search exact record from product homepage',async()=>{
    await go('governance-lab-series/index.html');await page.keyboard.press('/');
    const input=page.getByRole('combobox',{name:'Search all documentation'});await input.fill('Work');
    await page.locator('.site-search-results a').first().waitFor();const first=await page.locator('.site-search-results a').first().getAttribute('href');
    await input.press('Enter');await page.waitForURL(/reference\/def-cal-definition-work/);
    return {first,url:page.url(),recordBody:await page.locator('.record-body').count(),screenshot:await screenshot('exact-record')};
  });
  await scenario('search from research into Craft and Escape focus',async()=>{
    await go('governance-lab-series/research.html');const input=page.getByRole('combobox',{name:'Search all documentation'});
    await input.fill('does Accept reserve capacity?');await page.locator('.site-search-results a').first().waitFor();
    const first=await page.locator('.site-search-results a').first().getAttribute('href');await input.press('ArrowDown');const resultFocus=await focus();await page.keyboard.press('Escape');
    const escape={focus:await focus(),expanded:await input.getAttribute('aria-expanded'),hidden:await page.locator('#docs-search-results').isHidden()};
    await input.fill('does Accept reserve capacity?');await page.locator('.site-search-results a').first().waitFor();await input.press('Enter');await page.waitForURL(/craft-model/);
    return {first,resultFocus,escape,destination:page.url(),topic:await page.locator('.docs-topic-header h1').innerText()};
  });
  await scenario('catalog empty search and recovery',async()=>{
    await go('governance-lab-series/lab-reference-library.html#catalog-definitions');await page.locator('#catalog-search').fill('no-such-record-xyz');
    const empty=await page.locator('#catalog-definitions .catalog-empty').innerText();await page.getByRole('button',{name:'Browse all records',exact:true}).filter({visible:true}).click();
    return {empty,restored:await page.locator('#catalog-definitions .result-count').innerText(),query:await page.locator('#catalog-search').inputValue()};
  });
  await scenario('compact navigation selects a topic and closes',async()=>{
    await go('governance-lab-series/start-here.html',390);const browse=page.locator('.article-contents');const closed=await browse.getAttribute('open');
    await page.getByText('Browse documentation',{exact:true}).click();await page.getByRole('link',{name:'Prepare a definition',exact:true}).first().click();
    return {initialOpen:closed,groups:await page.locator('.docs-navigation-group').count(),destination:page.url(),finalOpen:await page.locator('.article-contents').getAttribute('open'),screenshot:await screenshot('phone-practical')};
  });
  await scenario('session demonstration preserves saved records',async()=>{
    await go('governance-lab-series/governance-lab-reference.html#agent');const before=await page.locator('#agent').innerText();
    await page.getByRole('button',{name:'Close this session',exact:true}).click();const after=await page.locator('#agent').innerText();
    const fresh=page.getByRole('button',{name:'Start a fresh session',exact:true});const freshAvailable=await fresh.isEnabled();
    await fresh.click();const freshNote=await page.locator('#session-note').innerText();
    return {before:before.slice(-4200),after:after.slice(-4200),freshAvailable,freshNote,oldNoteRestored:freshNote.includes('Compare E12')};
  });
  await scenario('Craft figure dialog and keyboard return',async()=>{
    await go('craft-documentation-proposal/craft-model.html#definition');const opener=page.locator('.article-section:not([hidden]) .diagram-open').first();
    await opener.click();const dialog=page.locator('#diagram-dialog');await dialog.waitFor({state:'visible'});const title=await page.locator('#dialog-title').innerText();
    const image=await page.locator('#dialog-image').getAttribute('alt');const shot=await screenshot('craft-dialog');await page.keyboard.press('Escape');
    return {title,image,closed:await dialog.isHidden(),focus:await focus(),screenshot:shot};
  });
  await scenario('search dialog accessibility in an open state',async()=>{
    await go('governance-lab-series/index.html');await page.getByRole('combobox',{name:'Search all documentation'}).fill('Work');await page.locator('.site-search-results a').first().waitFor();
    await page.addScriptTag({path:config.axe});const result=await page.evaluate(async()=>{const r=await axe.run({runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return {violations:r.violations,incomplete:r.incomplete};});
    return {accessibility:result,aria:await page.locator('#docs-search-results').ariaSnapshot(),screenshot:await screenshot('search-open')};
  });
  await scenario('reader form local download, synthetic mechanics only',async()=>{
    await go('governance-lab-series/research/reader-study.html');await page.getByLabel('Anonymous participant code',{exact:true}).fill('REVIEW-MECHANICS-ONLY');
    await page.getByLabel('I agree to share these answers for this documentation review.').check();
    const download=page.waitForEvent('download');await page.getByRole('button',{name:'Download my response file',exact:true}).click();const file=await download;
    await file.saveAs(config.output+'/measurements/synthetic-response-NOT-PARTICIPANT.json');
    return {filename:file.suggestedFilename(),failure:await file.failure(),status:await page.locator('#download-status').innerText(),actualParticipant:false};
  });
  await page.context().tracing.stop({path:config.output+'/traces/fixed-site-journeys.zip'});
  page.off('pageerror',event);
  return JSON.stringify({browserVersion:page.context().browser().version(),rows,events});
}
