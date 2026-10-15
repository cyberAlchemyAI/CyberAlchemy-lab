const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'../../..');
const out=path.join(root,'website/output/playwright/ux-validator/20261012-whole-site/measurements');
const base=path.join(root,'website/dist/governance-lab-series');
const ctx={window:{},URL,console};vm.createContext(ctx);
let raw=fs.readFileSync(path.join(base,'assets/site-search-index.js'),'utf8');
raw=raw.substring(0,raw.indexOf('window.LabSiteSearchIndex.base='));
vm.runInContext(raw,ctx);
vm.runInContext(fs.readFileSync(path.join(base,'assets/search-engine.js'),'utf8'),ctx);
const index=ctx.LabSearchEngine.prepare(ctx.window.LabSiteSearchIndex.entries);
const earlier=JSON.parse(fs.readFileSync(path.join(root,'website/source/governance-lab-series/research/search-judgments.json'),'utf8')).judgments;
const next=JSON.parse(fs.readFileSync(path.join(__dirname,'search-questions.json'),'utf8')).questions;
function evaluate(questions,prefix=false){
 return questions.map(q=>{
  const hits=ctx.LabSearchEngine.search(index,q.query);
  const acceptable=hit=>q.acceptable.some(h=>prefix?hit.href===h||hit.href.startsWith(h+'#')||hit.href.startsWith(h+'-'):hit.href===h);
  const rank=hits.findIndex(acceptable)+1;
  return {...q,results:hits.length,acceptableRank:rank||null,topThreeAcceptable:rank>0&&rank<=3,topFive:hits.slice(0,5).map(h=>({title:h.title,href:h.href,group:h.group,score:h.score}))};
 });
}
const data={entries:index.length,indexedPages:[...new Set(index.map(e=>e.href.split('#')[0]))],earlier:evaluate(earlier),wholeSite:evaluate(next,true)};
fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'search-ranking.json'),JSON.stringify(data,null,2)+'\n');
console.log(JSON.stringify({entries:index.length,earlierPasses:data.earlier.filter(r=>r.topThreeAcceptable).length,earlierTotal:data.earlier.length,newTopThree:data.wholeSite.filter(r=>r.topThreeAcceptable).length,newTotal:data.wholeSite.length,zeroResults:data.wholeSite.filter(r=>!r.results).map(r=>r.query),robotIndexed:data.indexedPages.some(p=>p.includes('robot-learning'))},null,2));
