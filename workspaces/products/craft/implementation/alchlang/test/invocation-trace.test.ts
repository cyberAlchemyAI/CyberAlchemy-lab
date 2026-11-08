import assert from 'node:assert/strict';
import test from 'node:test';
import {mkdtempSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {buildFunction} from '../src/function-builder.js';
import {digest} from '../src/domainspec-profile.js';
const implementation=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const extension=path.resolve(implementation,'../extensions/invocation-trace-v1');
const sourcePath=path.join(extension,'quantity-price.alch');
const fixtures=JSON.parse(readFileSync(path.resolve(extension,'../medusa-quantity-price-v1/fixtures.json'),'utf8'));
const input=(f:any)=>({request:structuredClone(f.request),snapshot:structuredClone(f.snapshot)});
async function bundle(t:any){const p=mkdtempSync(path.join(os.tmpdir(),'alch-trace-test-'));t.after(()=>rmSync(p,{recursive:true,force:true}));const out=path.join(p,'bundle');await buildFunction(sourcePath,out);return {p,out,api:await import(pathToFileURL(path.join(out,'app/function/index.mjs')).href)};}

test('traced and ordinary invocation agree across every pricing fixture with source-bound evidence',async t=>{
 const {api,out}=await bundle(t);
 for(const f of fixtures){const body=input(f),before=structuredClone(body),normal=JSON.parse(JSON.stringify(await api.invoke(body))),trace=await api.invokeWithTrace(body);
  assert.equal(trace.outcome.status,'succeeded',f.name);assert.deepEqual(JSON.parse(JSON.stringify(trace.outcome.result)),normal);assert.deepEqual(body,before);assert.equal(trace.capture.complete,true);
  assert.equal(trace.binding.source_sha256,digest(readFileSync(sourcePath)));assert.equal(trace.binding.build_manifest_sha256,digest(readFileSync(path.join(out,'manifest.json'))));assert.equal(trace.binding.behavior_sha256,digest(readFileSync(path.join(out,'app/function/behavior.mjs'))));assert.equal(trace.binding.ontology_sha256,digest(readFileSync(path.join(out,'provenance/function/ontology.json'))));
  assert.equal(trace.events.filter((e:any)=>e.kind==='selected-case').length,1);
  assert.ok(trace.events.every((e:any)=>e.definition?.source.sha256===trace.binding.source_sha256));
  if(f.expected.status!=='quoted')assert.equal(trace.declarations.find((n:any)=>n.name==='LineSubtotal').state,'not_evaluated');
  else assert.ok(trace.events.some((e:any)=>e.node_kind==='Calculation'&&e.kind==='node-result'&&e.value.$uint64));
 }
 const trace=await api.invokeWithTrace(input(fixtures[0]));
 assert.ok(trace.answer.includes('quoted'));assert.ok(trace.selection_reason.rule_results.some((r:any)=>r.name==='UniquePrice'&&r.value===true));
 const cheapest=trace.queries.find((q:any)=>q.name==='Cheapest');assert.equal(cheapest.accepted,1);assert.equal(cheapest.complete,true);
 const rejected=trace.events.find((e:any)=>e.kind==='query-row'&&e.declaration==='Cheapest'&&!e.accepted);assert.ok(rejected);assert.ok(rejected.row.amountMinor.$uint64);assert.ok(rejected.clause.text.startsWith('where not (exists'));
 const response=await api.handler(new Request('http://localhost/quote',{method:'POST',headers:{authorization:'Bearer test','content-type':'application/json'},body:JSON.stringify(input(fixtures[0]))}),{QUOTE_API_TOKEN:'test'});
 assert.ok(!Object.hasOwn(await response.json(),'events'));
});

test('failed assertions, overflow and absent provided bindings produce causal incomplete execution receipts',async t=>{
 const {api}=await bundle(t);
 const invalid=input(fixtures[0]);invalid.snapshot.prices.push(structuredClone(invalid.snapshot.prices[0]));
 const duplicate=await api.invokeWithTrace(invalid);assert.equal(duplicate.outcome.code,'QUOTE_DUPLICATE_PRICE');assert.equal(duplicate.selected_case,null);assert.equal(duplicate.capture.complete,true);
 assert.ok(duplicate.events.some((e:any)=>e.kind==='assertion'&&e.code==='QUOTE_DUPLICATE_PRICE'&&!e.passed));
 assert.equal(duplicate.declarations.find((n:any)=>n.name==='Cheapest').state,'not_evaluated');
 const max=input(fixtures.find((f:any)=>f.name==='uint64_max'));max.request.quantity=2;
 const overflow=await api.invokeWithTrace(max);assert.equal(overflow.outcome.status,'failed');assert.equal(overflow.outcome.code,'CALCULATION_OVERFLOW');assert.ok(overflow.events.some((e:any)=>e.declaration==='LineSubtotal'&&e.kind==='node-error'));
 const missing=await api.invokeWithTrace({request:fixtures[0].request});assert.equal(missing.outcome.code,'FUNCTION_INTEGRATION_REQUIRED');assert.ok(!JSON.stringify(missing).includes('authorization'));
 let getterCalls=0;const hostile={get request(){getterCalls++;return fixtures[0].request;}};const failed=await api.invokeWithTrace(hostile);assert.equal(failed.outcome.code,'FUNCTION_RECORD');assert.equal(failed.binding.input_sha256,null);assert.equal(getterCalls,0);
});

test('capture limits do not alter results and concurrent invocations do not share events',async t=>{
 const {api}=await bundle(t),body=input(fixtures[0]);
 const limited=await api.invokeWithTrace(body,{maxEvents:1});assert.equal(limited.outcome.status,'succeeded');assert.equal(limited.capture.truncated,true);assert.equal(limited.events.length,1);assert.equal(limited.selection_reason,null);assert.ok(limited.declarations.every((d:any)=>d.state==='not_fully_observed'));
 const bytes=await api.invokeWithTrace(body,{maxBytes:256});assert.equal(bytes.outcome.status,'succeeded');assert.equal(bytes.capture.complete,false);assert.ok(bytes.capture.recorded_bytes<=256);
 await assert.rejects(api.invokeWithTrace(body,{maxEvents:0}),/TRACE_LIMIT_OPTIONS/);
 const a=input(fixtures[0]),b=input(fixtures[0]);a.request.request_id='trace-a';b.request.request_id='trace-b';
 const [left,right]=await Promise.all([api.invokeWithTrace(a),api.invokeWithTrace(b)]);assert.notEqual(left.binding.input_sha256,right.binding.input_sha256);assert.ok(!JSON.stringify(left).includes('trace-b'));assert.ok(!JSON.stringify(right).includes('trace-a'));
 const deterministic=await api.invokeWithTrace(a);assert.deepEqual(left,deterministic);
});

test('CLI trace executes only provided input and reports failed execution with nonzero exit',async t=>{
 const {p}=await bundle(t),file=path.join(p,'input.json'),cli=path.join(implementation,'dist/cli.js');writeFileSync(file,JSON.stringify(input(fixtures[0])));
 const receipt=JSON.parse(execFileSync(process.execPath,[cli,'trace',sourcePath,'--input',file],{encoding:'utf8'}));assert.equal(receipt.outcome.status,'succeeded');assert.equal(receipt.execution_mode,'local-provided-inputs');
 writeFileSync(file,JSON.stringify({request:fixtures[0].request}));
 try{execFileSync(process.execPath,[cli,'trace',sourcePath,'--input',file],{encoding:'utf8',stdio:'pipe',env:{...process.env,PRICE_SNAPSHOT_URL:'https://example.invalid/never-call',PRICE_SNAPSHOT_TOKEN:'DO_NOT_CAPTURE'}});assert.fail('failure exit required');}
 catch(error){const failure=error as any;assert.equal(failure.status,1);const trace=JSON.parse(failure.stdout);assert.equal(trace.outcome.code,'FUNCTION_INTEGRATION_REQUIRED');assert.ok(!failure.stdout.includes('DO_NOT_CAPTURE'));}
});
