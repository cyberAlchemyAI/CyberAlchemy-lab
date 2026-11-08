import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,rmSync,writeFileSync,copyFileSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
import {checkFunction,buildFunction,inspectFunctionOntology} from '../src/function-builder.js';
const extension=path.resolve(import.meta.dirname,'../../extensions/module-input-mappings-v1'),source=path.join(extension,'checkout-quote.alch');
const fixtures=JSON.parse(readFileSync(path.join(extension,'checkout-quote.fixtures.json'),'utf8'));
test('local input mapping uses pricing output, preserves quotes and is skipped with shipping',async t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'alch-input-node-'));t.after(()=>rmSync(root,{recursive:true,force:true}));await buildFunction(source,path.join(root,'bundle'));const api=await import(pathToFileURL(path.join(root,'bundle/app/function/index.mjs')).href);
 for(const name of ['quoted','no_price_skips_missing_shipping_provider','ambiguous_price_skips_missing_shipping_provider']){
  const f=fixtures.find((f:any)=>f.name===name),trace=await api.invokeWithTrace(f.input);assert.deepEqual(JSON.parse(JSON.stringify(trace.outcome)),f.expected);assert.equal(trace.capture.complete,true);
  assert.equal(trace.events.filter((e:any)=>e.kind==='node-start'&&e.declaration==='ShippingInput').length,name==='quoted'?1:0);
  if(name==='quoted'){const mapped=trace.events.find((e:any)=>e.kind==='node-result'&&e.declaration==='ShippingRequest');assert.equal(mapped.value.request_id,f.input.pricing.request.request_id);assert.ok(trace.events.findIndex((e:any)=>e.kind==='binding-input')<trace.events.findIndex((e:any)=>e.kind==='module-start'&&e.module==='Shipping'));}
 }
 const ontology=await inspectFunctionOntology(source);assert.ok('nodes' in ontology);assert.ok(ontology.references.some((r:any)=>r.role==='input-mapping'));
});
test('both targets reject wrong input mapping types, forward roots and missing mapping declarations',async t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'alch-input-check-'));t.after(()=>rmSync(root,{recursive:true,force:true}));for(const n of ['quantity-price.alch','shipping-quote.alch'])copyFileSync(path.join(extension,n),path.join(root,n));const file=path.join(root,'checkout.alch'),original=readFileSync(source,'utf8');
 for(const [from,to]of [['input ShippingInput','input MissingMapping'],['input ShippingInput','input ShippingRequest'],['field request_id = pricing.request_id','field request_id = shipping.request_id']]as const){writeFileSync(file,original.replace(from,to));for(const target of ['node-http','rust-http'])await assert.rejects(()=>checkFunction(file,target),/Mapping|mapping|forward\/cyclic/);}
});
test('HTTP module body is mapped and invalid mapped schema fails before a shipping request',async t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'alch-input-http-'));t.after(()=>rmSync(root,{recursive:true,force:true}));await buildFunction(path.join(extension,'checkout-quote-http.alch'),path.join(root,'bundle'));const api=await import(pathToFileURL(path.join(root,'bundle/app/function/index.mjs')).href),fs=JSON.parse(readFileSync(path.join(extension,'checkout-quote-http.fixtures.json'),'utf8'));
 for(const name of ['quoted','mapped_optional_null_note','mapped_input_schema_rejected_before_shipping']){
  const f=fs.find((f:any)=>f.name===name),events:any[]=[],requests:any[]=[];let used=0;const invoker=api.createInvoker((e:any)=>events.push(e));
  const call=invoker.invoke(f.input,f.env,{observeRequest:(r:any)=>requests.push(r),fetch:async()=>{const r=f.responses[used++];assert.ok(r);return new Response(JSON.stringify(r.body),{status:r.status});}});
  if(name==='mapped_input_schema_rejected_before_shipping'){await assert.rejects(()=>call,/FUNCTION_MODULE_INPUT_SCHEMA/);assert.equal(requests.length,1);assert.equal(events.at(-1).kind,'binding-input-error');}
  else {assert.deepEqual(JSON.parse(JSON.stringify(await call)),f.expected.result);assert.equal(requests.length,2);const body=JSON.parse(requests[1].body);assert.equal(body.request.request_id,f.responses[0].body.request_id);assert.deepEqual(body.request,{...f.input.shipping,request_id:f.responses[0].body.request_id});assert.deepEqual(body.snapshot,f.input.shipping_snapshot);}
 }
});
