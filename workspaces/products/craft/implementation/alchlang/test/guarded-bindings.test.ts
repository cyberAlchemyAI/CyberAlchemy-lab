import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,rmSync,writeFileSync,copyFileSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
import {checkFunction,buildFunction,inspectFunctionOntology} from '../src/function-builder.js';
import {createBoundary} from '../src/boundary-runtime.js';
import {loadModuleTree} from '../src/module-source.js';
const extension=path.resolve(import.meta.dirname,'../../extensions/guarded-bindings-v1'),source=path.join(extension,'checkout-quote.alch');
const fixtures=JSON.parse(readFileSync(path.join(extension,'checkout-quote.fixtures.json'),'utf8'));
test('guarded checkout skips local shipping without provider configuration and derives guard scaffolds',async t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'alch-guard-node-'));t.after(()=>rmSync(root,{recursive:true,force:true}));await buildFunction(source,path.join(root,'bundle'));
 const api=await import(pathToFileURL(path.join(root,'bundle/app/function/index.mjs')).href);
 for(const name of ['no_price_skips_missing_shipping_provider','ambiguous_price_skips_missing_shipping_provider','quoted']){
  const f=fixtures.find((f:any)=>f.name===name),trace=await api.invokeWithTrace(f.input);assert.deepEqual(JSON.parse(JSON.stringify(trace.outcome)),f.expected);assert.equal(trace.capture.complete,true);
  const skip=name!=='quoted';assert.equal(trace.events.some((e:any)=>e.kind==='module-skipped'&&e.module==='Shipping'),skip);assert.equal(trace.events.some((e:any)=>e.kind==='module-start'&&e.module==='Shipping'),!skip);
 }
 const o=await inspectFunctionOntology(source);assert.ok("nodes" in o);assert.ok(o.references.some((r:any)=>r.role==='conditionally-binds'));const result:any=o.nodes.find((n:any)=>n.kind==='result');assert.equal(result.bindings[1].condition.path[0],'HasPrice');
});
test('both targets reject unsafe reads and circular binding dependencies',async t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'alch-guard-check-'));t.after(()=>rmSync(root,{recursive:true,force:true}));for(const n of ['quantity-price.alch','shipping-quote.alch'])copyFileSync(path.join(extension,n),path.join(root,n));
 const file=path.join(root,'checkout.alch'),original=readFileSync(source,'utf8');
 for(const [from,to]of [['condition HasPrice and shipping.status','condition shipping.status'],['bind pricing from ItemPrice','bind pricing from ItemPrice when Quoted']]as const){writeFileSync(file,original.replace(from,to));for(const target of ['node-http','rust-http'])await assert.rejects(()=>checkFunction(file,target),/unguarded binding output|forward\/cyclic/);}
});
test('guard errors and skipped calls have distinct trace events; observers cannot trigger calls',async()=>{
 const {model,boundaryBindings}=loadModuleTree(source).parsed;let calls=0;const events:any[]=[];
 // Test the transport boundary directly with input-only guards to isolate zero-effect behavior.
 const binding={...boundaryBindings[1],condition:{op:'literal',value:false}};
 const boundary=createBoundary(model,[binding],()=>({request_id:'checkout-1',status:'no_price',currency_code:'usd'}),()=>{},{Shipping:async()=>{calls++;throw Error('unexpected call');}},e=>{events.push(e);throw Error('observer');},()=>false);
 await boundary.invoke(fixtures[0].input);assert.equal(calls,0);assert.deepEqual(events.map(e=>e.kind),['binding-guard','module-skipped']);
 const failed=createBoundary(model,[binding],()=>null,()=>{},{},e=>events.push(e),()=>{throw Object.assign(Error('bad guard'),{code:'FUNCTION_UINT64'});});
 await assert.rejects(()=>failed.invoke(fixtures[0].input),/FUNCTION_UINT64/);assert.equal(events.at(-1).kind,'binding-error');assert.equal(events.at(-1).code,'FUNCTION_UINT64');
});
