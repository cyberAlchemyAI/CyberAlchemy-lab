// Regression against frozen independent judgments and synchronous/async parity.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../../..');
const lab=path.join(root,'website/dist/governance-lab-series');
const ctx={window:{},URL,setTimeout};vm.createContext(ctx);
const raw=fs.readFileSync(path.join(lab,'assets/site-search-index-fallback.js'),'utf8');
vm.runInContext(raw.substring(0,raw.indexOf('window.LabSiteSearchIndex.base=')),ctx);
vm.runInContext(fs.readFileSync(path.join(lab,'assets/search-engine.js'),'utf8'),ctx);
(async()=>{
  const payload=ctx.window.LabSiteSearchIndex,entries=payload.entries,engine=ctx.LabSearchEngine;
  assert.ok(entries.every(entry=>entry.prepared?.version==='lab-lexical/v1'),'Every entry must have versioned build features');
  assert.equal(payload.preparedStats.version,'lab-lexical/v1');
  const sync=engine.prepare(entries,payload.preparedStats),asyncIndex=await engine.prepareAsync(entries,payload.preparedStats);
  const rawIndex=engine.prepare(entries.map(({prepared,...entry})=>entry));
  for(let i=0;i<entries.length;i++){
    const value=item=>JSON.stringify({title:[...item.titleTerms],aliases:[...item.aliasTerms],body:[...item.bodyTerms],length:item.length,topics:item.aliasesTopics});
    assert.equal(value(sync[i]),value(rawIndex[i]),'Build/browser lexical parity: '+entries[i].id);
  }
  assert.equal(JSON.stringify([...sync.stats.df]),JSON.stringify([...rawIndex.stats.df]));
  assert.equal(JSON.stringify([...sync.stats.lexicon]),JSON.stringify([...rawIndex.stats.lexicon]));
  const judgments=JSON.parse(fs.readFileSync(path.join(lab,'research/search-judgments.json'),'utf8')).judgments;
  const rows=[];
  for(const q of judgments){
    const hits=engine.search(asyncIndex,q.query),other=engine.search(sync,q.query);
    assert.equal(JSON.stringify(hits.map(h=>[h.id,h.score])),JSON.stringify(other.map(h=>[h.id,h.score])),q.query);
    assert.equal(JSON.stringify(hits.map(h=>[h.id,h.score])),JSON.stringify(engine.search(rawIndex,q.query).map(h=>[h.id,h.score])),'Original algorithm: '+q.query);
    const rank=hits.findIndex(h=>q.acceptable.includes(h.href))+1;
    assert.ok(q.kind==='exact-title'?rank===1:rank>0&&rank<=3,q.query);
    rows.push({query:q.query,rank});
  }
  for(const query of ['purple aardvark telescope','qzxv qzpq','pizza delivery coupon'])assert.equal(engine.search(asyncIndex,query).length,0);
  const constructor=engine.prepare([{id:'constructor-fixture',title:'Constructor',text:'A constructor accepts a field.',aliases:['constructor'],href:'constructor.html',group:'Fixture'}]);
  assert.ok(constructor[0].bodyTerms.has('constructor'),'Inherited Object.prototype keys must remain literal words');
  assert.equal(engine.search(constructor,'constructor')[0].id,'constructor-fixture');
  const result={curated:rows.length,passing:rows.length,identical_sync_async_ranks:true,build_browser_entry_parity:entries.length,original_algorithm_rank_parity:true,negative_queries:3,rows};
  let quickRaw=fs.readFileSync(path.join(lab,'assets/site-search-quick-fallback.js'),'utf8');
  vm.runInContext(quickRaw.substring(0,quickRaw.indexOf('window.LabSiteSearchQuick.base=')),ctx);
  const quick=ctx.window.LabSiteSearchQuick;
  const quickIndex=engine.prepare(quick.entries,quick.preparedStats);
  const quickReference=engine.prepare(quick.entries.map(({prepared,...entry})=>entry));
  assert.equal(JSON.stringify([...quickIndex.stats.df]),JSON.stringify([...quickReference.stats.df]));
  assert.equal(JSON.stringify([...quickIndex.stats.lexicon]),JSON.stringify([...quickReference.stats.lexicon]));
  for(const q of judgments)assert.equal(JSON.stringify(engine.search(quickIndex,q.query).map(x=>[x.id,x.score])),JSON.stringify(engine.search(quickReference,q.query).map(x=>[x.id,x.score])));
  result.quick_entry_parity=quick.entries.length;result.constructor_literal_regression=true;
  fs.writeFileSync(path.join(root,'output/playwright/live-review-github-20261015/search-regression.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({...result,rows:undefined}));
})().catch(e=>{console.error(e);process.exitCode=1;});
