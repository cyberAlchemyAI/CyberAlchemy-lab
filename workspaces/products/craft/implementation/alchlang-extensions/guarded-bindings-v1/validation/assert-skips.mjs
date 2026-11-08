import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
const root=path.resolve(process.argv[2]??''),output=process.argv[3];if(process.argv.length!==4)throw Error('usage: node validation/assert-skips.mjs <conformance directory> <new receipt.json>');
const evidence=[];
for(const name of ['checkout-quote','checkout-quote-http']){
 const r=JSON.parse(readFileSync(path.join(root,name,'report.json'),'utf8'));assert.equal(r.status,'pass');
 for(const c of r.cases){
  const status=c.node.outcome.result?.status;if(!['no_price','ambiguous_price','quoted','shipping_unavailable'].includes(status))continue;
  for(const target of ['node','rust']){
   const run=c[target],skip=['no_price','ambiguous_price'].includes(status),decisions=run.decisions;
   const guard=decisions.filter(e=>e.kind==='binding-guard'&&e.binding==='shipping');assert.equal(guard.length,1,c.name);assert.equal(guard[0].passed,!skip,c.name);
   assert.equal(decisions.filter(e=>e.kind==='module-skipped'&&e.module==='Shipping').length,skip?1:0,c.name);
   assert.equal(decisions.filter(e=>e.kind==='module-start'&&e.module==='Shipping').length,skip?0:1,c.name);
   if(skip){assert.equal(run.requests.length,name==='checkout-quote-http'?1:0,c.name);assert.ok(!decisions.some(e=>e.module?.startsWith('Shipping')&&e.kind!=='module-skipped'),c.name);}
   evidence.push({module:name,case:c.name,target,status,shipping:skip?'skipped':'invoked',requests:run.requests.length});
  }
 }
}
assert.ok(evidence.some(e=>e.status==='no_price'));assert.ok(evidence.some(e=>e.status==='ambiguous_price'));
const receipt={schema_version:'alchlang.guarded-binding-evidence/v1',status:'pass',checks:evidence.length,evidence,authority_effect:'none'};
writeFileSync(output,JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({status:'pass',checks:evidence.length}));
