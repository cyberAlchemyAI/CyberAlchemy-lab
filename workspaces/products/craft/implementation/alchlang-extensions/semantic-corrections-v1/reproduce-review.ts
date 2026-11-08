import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {compileOntologyHost} from '../../implementation/src/ontology-host.js';
import {compileLocalHost} from '../../implementation/src/local-host.js';
import {compileEventExecution,buildEventExecution} from '../../implementation/src/event-execution.js';
import assert from 'node:assert/strict';
const source=readFileSync(new URL('../ontology-schema-v1/orders-v2.alch',import.meta.url),'utf8');
const variant=source.replace('pending -> committed','pending -> cancelled').replace('input operationId, orderId, status, outboxMessageId, occurredAt, payload','input orderId').replace('max-receives 5','max-receives 1').replace('retention-seconds 345600','retention-seconds 60');
const old=await compileOntologyHost(variant),normalized=(await compileLocalHost(old.normalized)).normalized;
const work=mkdtempSync(path.join(tmpdir(),'alch-review-repro-'));
try{
 const input=path.join(work,'source.alch'),bundle=path.join(work,'bundle');writeFileSync(input,normalized);await buildEventExecution(input,bundle);
 const config=(await compileEventExecution(normalized)).config;
 const request={command:'invoke',operation:'place-order',expected_version:0,now:1788696000000,at:'2026-09-06T12:00:00.000Z',facts:{schemaVersion:'provided-by-caller',operationId:'op1',orderId:'o1',status:'pending',outboxMessageId:'m1',occurredAt:'2026-09-06T12:00:00.000Z',payload:{quantity:2}}};
 const context={actor:'OrderService',grants:['order-transaction-authority'],transport_grants:['order-transport']};
 const results=[];
 for(const target of ['node','rust']){
  const database=path.join(work,target+'.sqlite');const run=(r:any)=>{const p=spawnSync(target==='node'?process.execPath:path.join(bundle,'alch-event'),target==='node'?[path.join(bundle,'handler.mjs')]:[],{input:JSON.stringify({request:r,context}),encoding:'utf8',env:{...process.env,ALCH_EVENT_DATABASE:database}});return JSON.parse(p.stdout);};
  const narrowed=run({...request,facts:{orderId:'o1'}});assert.equal(narrowed.error,'FACTS');
  const first=run(request);assert.equal(first.status,'committed');
  const snapshot=run({command:'inspect'});assert.equal(snapshot.states[0].state.status,'committed');assert.equal(snapshot.states[0].state.schemaVersion,'v2');
  const second=run({...request,expected_version:1,facts:{...request.facts,outboxMessageId:'m2'}});assert.equal(second.status,'committed');
  results.push({target,classification:'known-failures-reproduced',narrowed_input:narrowed,declared_transition:'cancelled',actual_state:snapshot.states[0].state.status,supplied_default:'provided-by-caller',actual_default:snapshot.states[0].state.schemaVersion,committed_state_reentered:second.status});
 }
 assert.equal(config.max_attempts,5);assert(!Object.hasOwn(config,'retention_ms'));
 await assert.rejects(()=>compileOntologyHost(source.replace('entity OutboxMessage:\n','')));
 writeFileSync(new URL('./counterexamples.json',import.meta.url),JSON.stringify({status:'known-failures-reproduced',product_pass:false,source_sha256:createHash('sha256').update(source).digest('hex'),variant_sha256:createHash('sha256').update(variant).digest('hex'),results,declared_max_receives:1,runtime_max_attempts:config.max_attempts,declared_retention_seconds:60,runtime_retention:'omitted',empty_outbox_required:true,authority_effect:'none'},null,2)+'\n');
}finally{rmSync(work,{recursive:true,force:true});}
