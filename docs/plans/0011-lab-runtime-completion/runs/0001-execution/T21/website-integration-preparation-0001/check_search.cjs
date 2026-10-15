const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'../../../../../../..'),base=path.join(__dirname,'prototype/website/dist/governance-lab-series');
const ctx={window:{},URL};vm.createContext(ctx);
let raw=fs.readFileSync(path.join(base,'assets/site-search-index-fallback.js'),'utf8');raw=raw.substring(0,raw.indexOf('window.LabSiteSearchIndex.base='));
vm.runInContext(raw,ctx);vm.runInContext(fs.readFileSync(path.join(base,'assets/search-engine.js'),'utf8'),ctx);
const index=ctx.LabSearchEngine.prepare(ctx.window.LabSiteSearchIndex.entries);
const map=JSON.parse(fs.readFileSync(path.join(base,'research/reference-pages.json'),'utf8')).legacy_routes;
const canonical=href=>{const [file,id]=href.split('#');return file==='lab-reference-library.html'&&map[id]?map[id]+'#'+id:href;};
const sets={curated:JSON.parse(fs.readFileSync(path.join(base,'research/search-judgments.json'),'utf8')).judgments,
 originalWholeSite:JSON.parse(fs.readFileSync(path.join(root,'website/review/2026-10-12-site-review/search-questions.json'),'utf8')).questions,
 fresh:JSON.parse(fs.readFileSync(path.join(root,'website/review/2026-10-12-site-review/fresh-search-questions.json'),'utf8')).questions};
const evaluated={};for(const [name,questions]of Object.entries(sets))evaluated[name]=questions.map(q=>{
 const begin=performance.now(),hits=ctx.LabSearchEngine.search(index,q.query),ms=performance.now()-begin;
 const accepted=hit=>q.acceptable.map(canonical).some(h=>hit.href===h||name!=='curated'&&hit.href.startsWith(h+'#'));
 const rank=hits.findIndex(accepted)+1;
 return {...q,acceptableRank:rank||null,pass:q.kind==='exact-title'?rank===1:rank>0&&rank<=3,results:hits.length,ms,topFive:hits.slice(0,5).map(h=>({title:h.title,href:h.href,score:h.score}))};
});
const negatives=['qzxv qzpq','purple aardvark telescope','zzzzunknownzzzz','pizza delivery coupon'];
const negativeResults=negatives.map(query=>({query,results:ctx.LabSearchEngine.search(index,query).length}));
const result={indexEntries:index.length,method:'Literal exact curated destinations, or explicitly chosen page/chapter boundaries for the original and fresh expert sets. No participant claims.',evaluated,negativeResults};
const output=path.join(__dirname,'search-ranking.json');
fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(Object.fromEntries(Object.entries(evaluated).map(([name,rows])=>[name,{pass:rows.filter(r=>r.pass).length,total:rows.length,zero:rows.filter(r=>!r.results).map(r=>r.query),misses:rows.filter(r=>!r.pass).map(r=>({query:r.query,rank:r.acceptableRank,top:r.topFive.slice(0,3)}))}]))));
