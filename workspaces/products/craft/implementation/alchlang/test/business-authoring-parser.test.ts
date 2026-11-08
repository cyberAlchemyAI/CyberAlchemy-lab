import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {parseBusinessSource,assertParsedBusinessSourceCurrent,BusinessSourceRejected} from '../src/business-authoring-parser.js';
import type {ParsedBusinessSource} from '../src/business-authoring-protocol.js';
const contracts=new URL('../../../../../../../research/craft-alchlang-user-readiness-2026-10-12/business-authoring-design-2026-10-14/implementation-plan/contracts/',import.meta.url);
const reference=readFileSync(new URL('reference-business.alch',contracts),'utf8');
const reject=(source:string,code:string,line?:number)=>assert.throws(()=>parseBusinessSource(source),error=>{
  assert.ok(error instanceof BusinessSourceRejected);assert.ok(error.code.startsWith(code),error.message);assert.equal(error.source,'business.alch');if(line!==undefined)assert.equal(error.line,line);assert.ok(error.column>=1);return true;
});
test('reference grammar captures all authored facts and original line obligations',()=>{
  const parsed=parseBusinessSource(reference);assertParsedBusinessSourceCurrent(parsed);
  assert.deepEqual(parsed.data.identity,{namespace:'dispatching',stable_id:'dispatching',version:'1',title:'Delivery acknowledgements',owner:'dispatch-team'});
  assert.equal(parsed.data.requirements[0]!.examples[0]!.given,'Delivery 31, verified true, label north-hub.');
  assert.equal(parsed.data.definitions[0]!.boolean_field.path[0],'verified');
  const lines=reference.split('\n').map((raw,i)=>({raw,line:i+1})).filter(({raw})=>raw.trim()&&!raw.trimStart().startsWith('#'));
  assert.equal(parsed.data.source_spans.length,lines.length);assert.equal(parsed.data.obligations.length,lines.length);
  assert.equal(new Set(parsed.data.obligations.map(o=>o.selector)).size,lines.length);
  for(const [i,row] of lines.entries()){const span=parsed.data.source_spans[i]!;assert.equal(span.line,row.line);assert.equal(span.column,row.raw.length-row.raw.trimStart().length+1);assert.equal(span.text,row.raw);assert.equal(parsed.data.obligations[i]!.span_selector,span.selector);}
  assert.equal(parsed.source.sha256,createHash('sha256').update(reference).digest('hex'));assert.equal(parsed.source.bytes,Buffer.byteLength(reference));
});
test('CRLF/comments preserve exact source capture while every fact retains a physical line',()=>{
  const source='# owner commentary\r\n'+reference.replaceAll('\n','\r\n');const parsed=parseBusinessSource(source,'business/model.alch');
  assert.equal(parsed.source.text,source);assert.equal(parsed.source.bytes,Buffer.byteLength(source));assert.equal(parsed.data.source_spans[0]!.line,2);assert.equal(parsed.data.source_spans[0]!.source,'business/model.alch');
  assert.equal(parsed.data.source_spans[0]!.source_sha256,parsed.source.sha256);
});
test('registered parsed data is deeply immutable; JSON and object clones are not custody',()=>{
  const parsed=parseBusinessSource(reference);
  assert.throws(()=>{(parsed.data.entities[0]!.fields as unknown[]).push({});},TypeError);
  assert.throws(()=>{(parsed.source as {text:string}).text='drift';},TypeError);
  for(const forged of [JSON.parse(JSON.stringify(parsed)),{...parsed},Object.create(parsed),new Proxy(parsed,{})])assert.throws(()=>assertParsedBusinessSourceCurrent(forged as ParsedBusinessSource),error=>error instanceof BusinessSourceRejected&&error.code==='BUSINESS_HANDLE');
});
test('syntax is closed: no tabs, inline comments, unknown clauses, extra depth or code',()=>{
  for(const [before,after] of [['  context ','\tcontext '],['owner dispatch-team','owner dispatch-team # inline'],['  effects none','  effects fetch'],['  effects none','  native "execute"'],['  meaning "One received delivery acknowledgement."','      meaning "One received delivery acknowledgement."']])reject(reference.replace(before!,after!),'BUSINESS_');
  reject(reference+'\nimport "external"\n','BUSINESS_SYNTAX');
  reject(reference.replace('  ceiling "One supplied value; no external verification or proof."','  ceiling "One supplied value; no external verification or proof." # inline'),'BUSINESS_SYNTAX');
  reject(reference.replace('  context ', '   context '),'BUSINESS_SYNTAX');
  reject(reference.replace('  context ', '  context \ud800'),'BUSINESS_SYNTAX');
});
test('required case bodies, prose, owner, scenarios and explicit applicability are never invented',()=>{
  for(const clause of ['owner dispatch-team\n','  context "A caller submits one delivery acknowledgement."\n','    why "The declared eligibility predicate holds."\n','  meaning "One received delivery acknowledgement."\n','  applies-when "ConfirmDelivery is requested."\n','  actor "Delivery API caller"\n','  audience public\n'])reject(reference.replace(clause,''),'BUSINESS_REQUIRED');
  reject(reference.replace(/  counterexample ineligible:[\s\S]*?\n\nentity/,'entity'),'BUSINESS_REQUIRED');
  const none=reference.replace('  applies-when "ConfirmDelivery is requested."','  applies-when none').replace('  actor "Delivery API caller"','  actors none');
  assert.deepEqual(parseBusinessSource(none).data.requirements[0]!.actors,[]);
  reject(none.replace('  actors none','  actors none\n  actor "Someone"'),'BUSINESS_AMBIGUOUS');
});
test('single clauses, declarations, fields and scenario identities cannot collide',()=>{
  for(const [before,after] of [['owner dispatch-team','owner dispatch-team\nowner other'],['  identity id','  identity id\n  identity id'],['  label String meaning "Label retained in the acknowledgement."','  id String meaning "Duplicate."'],['  counterexample ineligible:','  counterexample eligible:']])reject(reference.replace(before!,after!),'BUSINESS_AMBIGUOUS');
  reject(reference+'\nentity delivery:\n','BUSINESS_AMBIGUOUS');
  reject(reference+'\nentity DeliveryReady:\n','BUSINESS_AMBIGUOUS');
  reject(reference.replace('entity Delivery:','entity CraftRequest_Delivery:'),'BUSINESS_RESERVED');
  reject(reference.replace('entity Delivery:','entity craft_request_delivery:'),'BUSINESS_RESERVED');
  reject(reference.replace('  label String','  bad__field String'),'BUSINESS_SYNTAX');
});
test('all portable source keys and finite byte/line/depth/field budgets are enforced',()=>{
  for(const key of ['../model.alch','/model.alch','a/../model.alch','a\\model.alch','C:model.alch','a//model.alch','a/./model.alch','x\0.alch'])assert.throws(()=>parseBusinessSource(reference,key),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_SOURCE_PATH');
  reject('#'.repeat(1048577),'BUSINESS_SOURCE_BUDGET');reject('\n'.repeat(10000),'BUSINESS_SOURCE_BUDGET');
  reject(reference.replace('  effects none',' '.repeat(34)+'effects none'),'BUSINESS_SOURCE_BUDGET');
  const fields=Array.from({length:257},(_,i)=>`  flag_${i} Bool meaning "Flag."`).join('\n');reject(reference.replace('  identity id','  identity id\n'+fields),'BUSINESS_SOURCE_BUDGET');
});
test('diagnostics identify the exact malformed line and column',()=>{
  const broken=reference.replace('  boolean-field delivery.verified','  boolean-field delivery');const line=broken.split('\n').findIndex(s=>s==='  boolean-field delivery')+1;
  assert.throws(()=>parseBusinessSource(broken,'inputs/model.alch'),e=>{assert.ok(e instanceof BusinessSourceRejected);assert.equal(e.code,'BUSINESS_SYNTAX');assert.equal(e.source,'inputs/model.alch');assert.equal(e.line,line);assert.equal(e.column,3);return true;});
});
test('frozen schema field and repeated signature/scenario/clause budgets bound every parsed DTO',()=>{
  reject(reference.replace('owner dispatch-team','owner '+'x'.repeat(4097)),'BUSINESS_SOURCE_BUDGET');
  reject(reference.replace('version 1 "Delivery','version '+'v'.repeat(4097)+' "Delivery'),'BUSINESS_SOURCE_BUDGET');
  reject(reference.replace('"One received delivery acknowledgement."',JSON.stringify('x'.repeat(4097))),'BUSINESS_SOURCE_BUDGET');
  const sorts=Array.from({length:257},(_,i)=>`  sort Sort${i} interpreted-as Delivery`).join('\n');reject(reference.replace('  sort DeliveryValue interpreted-as Delivery',sorts),'BUSINESS_SOURCE_BUDGET');
  const applies=Array.from({length:257},(_,i)=>`  applies-when "Condition ${i}."`).join('\n');reject(reference.replace('  applies-when "ConfirmDelivery is requested."',applies),'BUSINESS_SOURCE_BUDGET');
  const cases=Array.from({length:257},(_,i)=>`  example case${i}:\n    given "Value."\n    when "Request."\n    then "Return."\n    why "Eligible."`).join('\n');reject(reference.replace('  example eligible:',cases+'\n  example eligible:'),'BUSINESS_SOURCE_BUDGET');
});
test('field names may coincide with grammar clause keywords and remain explicit fields',()=>{
  const source=reference.replace('  label String meaning "Label retained in the acknowledgement."','  label String meaning "Label retained in the acknowledgement."\n  meaning String meaning "Business meaning value."\n  identity Bool meaning "Identity flag value."');
  const entity=parseBusinessSource(source).data.entities[0]!;assert.equal(entity.fields.find(f=>f.name==='meaning')!.type,'String');assert.equal(entity.fields.find(f=>f.name==='identity')!.type,'Bool');assert.equal(entity.identity,'id');
  assert.equal(parseBusinessSource(reference.replace('capability DeliveryAcknowledgement:','capability CraftRequester:')).data.capabilities[0]!.id,'CraftRequester');
  reject(reference+'\r','BUSINESS_SYNTAX');
});
