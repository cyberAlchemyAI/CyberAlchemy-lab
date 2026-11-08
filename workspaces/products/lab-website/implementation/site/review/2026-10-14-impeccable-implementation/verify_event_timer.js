async page=>{
 const tab=await page.context().newPage();
 try {
  await tab.clock.install({time:new Date('2026-10-23T23:59:00-03:00')});
  await tab.goto('http://127.0.0.1:8766/candidate-site/governance-lab-series/hackathon.html');
  const before=await tab.locator('[data-event-status]').innerText();
  await tab.clock.fastForward(61000);
  const after=await tab.locator('[data-event-status]').innerText();
  if(!before.includes('pending')||!after.includes('have closed'))throw new Error(JSON.stringify({before,after}));
  const actions=await tab.locator('[data-event-action]').allTextContents();
  if(actions.some(x=>x==='Register'||x==='Submit project'))throw new Error('An action survived its deadline');
  return {summary:{checks:1,failures:0},before,after,actions,method:'Playwright virtual browser clock, live page timer across the UTC-3 submission boundary.'};
 }finally{await tab.close();}
}
