import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
const root=path.resolve(process.argv[2]??''),output=process.argv[3];if(process.argv.length!==4)throw Error('usage: node validation/assert-inputs.mjs <conformance directory> <new receipt.json>');
const evidence=[];
for(const name of ['checkout-quote','checkout-quote-http']){
 const report=JSON.parse(readFileSync(path.join(root,name,'report.json'),'utf8'));assert.equal(report.status,'pass');
 const fixtures=JSON.parse(readFileSync(path.resolve(import.meta.dirname,'..',name+'.fixtures.json'),'utf8'));
 for(const c of report.cases){const fixture=fixtures.find(f=>f.name===c.name);
  for(const target of ['node','rust']){
   const run=c[target],d=run.decisions,status=run.outcome.result?.status,skip=['no_price','ambiguous_price'].includes(status),ready=d.filter(e=>e.kind==='binding-input'&&e.binding==='shipping');
   if(skip){assert.equal(ready.length,0,c.name);assert.ok(!d.some(e=>e.kind==='node-start'&&['ShippingInput','ShippingRequest'].includes(e.declaration)),c.name);assert.ok(!d.some(e=>e.kind==='module-start'&&e.module==='Shipping'),c.name);assert.equal(run.requests.length,name==='checkout-quote-http'?1:0,c.name);evidence.push({module:name,case:c.name,target,check:'guard skips mapping and shipping'});}
   if(ready.length){assert.equal(ready.length,1,c.name);const mapped=d.findIndex(e=>e.kind==='binding-input');assert.ok(mapped<d.findIndex(e=>e.kind==='module-start'&&e.module==='Shipping'),c.name);assert.equal(d.filter(e=>e.kind==='node-start'&&e.declaration==='ShippingInput').length,1,c.name);}
   if(name==='checkout-quote-http'&&run.requests.length===2){
    const expected={request:{...fixture.input.shipping,request_id:fixture.responses[0].body.request_id},...(fixture.input.shipping_snapshot?{snapshot:fixture.input.shipping_snapshot}:{})};
    assert.deepEqual(run.requests[1].body,expected,c.name);evidence.push({module:name,case:c.name,target,check:'exact mapped HTTP input',request_id:expected.request.request_id});
   }
   if(c.name==='mapped_input_schema_rejected_before_shipping'){assert.equal(run.outcome.code,'FUNCTION_MODULE_INPUT_SCHEMA');assert.equal(run.requests.length,1);assert.equal(ready.length,0);assert.equal(d.at(-1).kind,'binding-input-error');assert.ok(!d.some(e=>e.kind==='module-start'&&e.module==='Shipping'));evidence.push({module:name,case:c.name,target,check:'invalid mapped input prevents shipping request'});}
  }
 }
}
assert.ok(evidence.some(e=>e.request_id==='wrong'),'upstream identity differs from original request');
assert.ok(evidence.some(e=>e.case==='mapped_optional_null_note'));assert.ok(evidence.some(e=>e.case==='mapped_input_schema_rejected_before_shipping'));
const receipt={schema_version:'alchlang.module-input-evidence/v1',status:'pass',checks:evidence.length,evidence,authority_effect:'none'};
writeFileSync(output,JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({status:'pass',checks:evidence.length}));
