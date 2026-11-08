/** Generated control/dataflow component tests. Native observations below are
 * labelled fixtures, never original invocation/row/commit proof or app acceptance.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC18/CONTEXT.md. */
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,cpSync,readFileSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {stripTypeScriptTypes} from 'node:module';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createCoreCommerceSourceOwner} from '../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../src/commerce/commerce-computation-domain.js';
import {createCommerceLocalPlanOwnerV1} from '../src/commerce/commerce-local-plan-owner-v1.js';
import {createCommerceOperationGenerationOwnerV1} from '../src/commerce/commerce-operation-generation-owner-v1.js';
import {generateCommerceValueCodecBundle} from '../src/commerce/commerce-value-codec-generation.js';
import {deriveCommerceSourceRecoveryPlansV1} from '../src/generation/commerce-recovery-plan-v1.js';
const cli=fileURLToPath(new URL('../',import.meta.url)),repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url)),base=path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/EC18');
let root:string,plans:any,owner:any,codecs:any,values:any,operations:any[];
const generated=new Map<string,any>();
const ok=(r:any)=>{assert.equal(r.ok,true,JSON.stringify(r,(_k,v)=>typeof v==='bigint'?String(v):v));return r.value;};
const plain=(v:any):any=>Array.isArray(v)?v.map(plain):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).map(([k,x])=>[k,plain(x)])):v;
before(async()=>{
 root=mkdtempSync(path.join(base,'operation-control-'));const sourceRoot=path.join(root,'source');cpSync(path.join(repo,'examples/ecommerce-target-candidate'),sourceRoot,{recursive:true,errorOnExist:true,force:false});
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(sourceRoot),actual=sources.inspect(capture),paths=new Set(actual.reconstruction.modules.map((m:any)=>m.path)),texts=actual.files.filter((f:any)=>paths.has(f.path)),limits=JSON.parse(readFileSync(path.join(sourceRoot,'contracts/compute-bounds.json'),'utf8')).computation.limits,semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(sourceRoot,'application.alch'),domain=createCommerceComputationDomainOwner(stage,source),baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 values=domain.inspect(baseline).contract.values;operations=semantics.inspect(semantic).effects.filter((p:any)=>p.protocol===null);plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);owner=createCommerceOperationGenerationOwnerV1(plans);
 const codecBundle=generateCommerceValueCodecBundle(stage,source,domain,baseline);for(const f of codecBundle.files)writeFileSync(path.join(root,f.path.replace(/\.ts$/,'.js')),stripTypeScriptTypes(f.text));codecs=(await import(pathToFileURL(path.join(root,'values-and-codecs.js')).href)).createCommerceValueCodecs();
});
after(()=>plans?.dispose());
async function build(id:string){let row=generated.get(id);if(row)return row;const operation=plans.bindOperation(id),source=owner.generateControl(operation),bundle=owner.files(source),directory=path.join(root,id.replaceAll('.','-')),physical=owner.materialize(source,directory);await owner.importControlComponent(physical);const module=await import(pathToFileURL(path.join(directory,'operation-control.js')).href);row={operation,bundle,directory,physical,module};generated.set(id,row);return row;}

/** A test-only technical observation seam. Pure callees and codecs are original
 * source-derived components. Context/read/native facts remain fixture data. */
function fixture(row:any,overrides:Record<string,any>={}){
 const trace:string[]=[],sites=row.bundle.manifest.source_sites,pure=new Map();let charges=0;
 const value=(type:any,v:any,locals:any[]=[]):any=>{
  // Optional/read-set wrappers are compiler-local typed data, not extra roots
  // registered into the immutable codec universe. Real leaves keep its codecs.
  if(type.kind==='optional'){assert.ok(v&&typeof v==='object');assert.ok(v.kind==='some'||v.kind==='none');assert.deepEqual(Object.keys(v).sort(),v.kind==='some'?['kind','value']:['kind']);return v.kind==='none'?Object.freeze({kind:'none'}):Object.freeze({kind:'some',value:value(type.element,v.value,locals)});}
  if(type.kind==='list'){assert.ok(Array.isArray(v));assert.ok(v.length>=type.min_items&&v.length<=type.max_items);return Object.freeze(v.map(x=>value(type.element,x,locals)));}
  const local=type.kind==='record'?locals.find(r=>r.name===type.name):null;
  if(local){assert.deepEqual(Object.keys(v).sort(),Object.keys(local.fields).sort());return Object.freeze(Object.fromEntries(Object.entries(local.fields).map(([k,t])=>[k,value(t,v[k],locals)])));}
  return ok(codecs.copyCommerceValue(ok(codecs.checkCommerceSchema({...values,root:type})),v));
 };
 const runtime:any={
  assertCurrent(_source:string,_operation:string,p:string){trace.push('current:'+p);},parameters(v:any){return v;},charge(){assert.ok(++charges<100000);},
  validateRole(p:string,v:any){const r=sites[p];return value(r.result,v,r.local_records);},
  validateReturn(v:any){return ok(codecs.copyCommerceValue(ok(codecs.checkCommerceSchema({...values,root:plans.inspectOperation(row.operation).plan.result})),v));},
  context(p:string){trace.push('fixture-context:'+p);throw Error('UnexpectedContext');},
  enumValue(_p:string,type:string,variant:string,fields:any){const def=values.enums.find((e:any)=>e.name===type),value=def.variants.every((v:any)=>!Object.keys(v.fields).length)?variant:{kind:variant,...fields};return ok(codecs.copyCommerceValue(codecs.schemaForType(type),value));},
  async pure(p:string,args:any[]){trace.push('original-pure:'+p);let c=pure.get(p);if(!c){c=plans.bindPureCall(row.operation,p);pure.set(p,c);}const view=c.owner.inspect(c.handle),input=Object.fromEntries(view.callee.parameters.map((b:any,i:number)=>[b.name,args[i]])),encoded=ok(codecs.encodeComputationParameters(codecs.schemaForCallableArguments(view.callee.declaration),input)),result=c.owner.evaluateBoundParameters(c.handle,encoded).observation.result;if(!result.ok)return {ok:false,code:result.error.code};return {ok:true,value:ok(codecs.decodeComputationValue(ok(codecs.checkCommerceSchema({...values,root:view.callee.result})),result.wire))};},
  async native(p:string,_args:any[]){trace.push('fixture-native:'+p);throw Error('UnexpectedNative');},async preflight(p:string){trace.push('preflight:'+p);},
  async count(p:string){trace.push('fixture-count:'+p);return 1n;},async read(p:string,_key:any,_args:any){trace.push('fixture-read:'+p);throw Error('UnexpectedRead');},
  async call(p:string,_args:any){trace.push('fixture-call:'+p);throw Error('UnexpectedCall');},assertObservation(){},
  async openReadSet(p:string){trace.push('read-set-open:'+p);return {fixture_lease:p};},async closeReadSet(lease:any){trace.push('read-set-close:'+lease.fixture_lease);},
  async transaction(p:string,_scope:any){trace.push('fixture-transaction:'+p);throw Error('UnexpectedTransaction');},assertTransaction(){throw Error('NoOriginalNativeDisposition');},assertSourceReturn(){throw Error('NoOriginalRollbackProof');},assertRecovery(){throw Error('NoOriginalRecoveryDisposition');},
  async acknowledge(p:string){trace.push('fixture-ack:'+p);throw Error('NoOriginalConsumerCommit');},...overrides,
 };return {runtime,trace};
}
const receipt={orderId:'order-one',status:'AwaitingStock',payableMinor:400n,currency:'USD'},fingerprint='a'.repeat(64),customer={logicalEntryId:'checkout',customerId:'customer-one',commandId:'command-one',principalPresent:true,currentActionAllowed:true};

test('all original invocable Operations emit/import explicit control code and compile as one corpus',async()=>{
 const kinds=new Set(),expressions=new Set(),recoveryKinds=new Set(),files:string[]=[];let transactions=0,recoveries=0;
 for(const p of operations){const id=p.operation.module+'.'+p.operation.name,row=await build(id);row.bundle.manifest.generated_control_kinds.forEach((k:string)=>kinds.add(k));row.bundle.manifest.generated_expression_kinds.forEach((k:string)=>expressions.add(k));row.bundle.manifest.recovery_plans.forEach((r:any)=>{recoveries++;recoveryKinds.add(r.kind);});transactions+=row.bundle.manifest.transactions.length;assert.equal(row.bundle.manifest.outer_control_generation,true);assert.equal(row.bundle.manifest.recovery_generation,true);assert.equal(row.bundle.manifest.whole_operation_generation,false);assert.equal(row.bundle.manifest.original_runtime_assembly,false);assert.match(row.module.runOperation.toString(),/runtime\./);for(const name of ['native-effect-contract.ts','effectful-transactions.ts','operation-execution-contract.ts','operation-control.ts'])files.push(path.join(row.directory,name));}
 assert.equal(transactions,17);assert.deepEqual([...kinds].sort(),['acknowledge','action','call','case','conditional','count','guard','let','preflight','present','read','read-set','transaction']);assert.equal(expressions.has('sort'),true);assert.equal(expressions.has('map'),true);
 assert.equal(recoveries,3);assert.deepEqual([...recoveryKinds].sort(),['proven-rollback-reread-original-inbox-or-shipment','reread-original-inbox','resolve-original-replay']);
 writeFileSync(path.join(root,'control-corpus.json'),JSON.stringify({operations:operations.length,transactions,control_kinds:[...kinds].sort(),expression_kinds:[...expressions].sort(),source_recoveries:recoveries,recovery_kinds:[...recoveryKinds].sort(),original_native_assembly:false},null,2)+'\n');
 const probe=path.join(root,'closed-native-value-types.ts');writeFileSync(probe,`import type {Data,Observation,OperationResult} from './Orders-PlaceOrder/operation-execution-contract.js';
const value:Data={amount:1n,items:[true,'x'],optional:{kind:'none'}};
// @ts-expect-error Native UInt64 uses bigint, never JS number.
const numeric:Data=1;
// @ts-expect-error Functions are not native values or business callbacks.
const callback:Data=()=>true;
// @ts-expect-error A valued uncertain observation must include its value.
const observation:Observation={kind:'indeterminate',ticket:undefined,channel:null,has_value:true};
// @ts-expect-error A valued uncertain result must include its value.
const result:OperationResult={kind:'indeterminate',tickets:[],has_value:true,source_code:null,commits:[],do_not_ack:true};
const uncertainty:OperationResult={kind:'indeterminate',tickets:[],has_value:true,value,source_code:null,commits:[],do_not_ack:true};
void [value,numeric,callback,observation,result,uncertainty];
`);files.push(probe);
 execFileSync(process.execPath,[path.join(cli,'node_modules/typescript/bin/tsc'),'--ignoreConfig','--noEmit','--strict','--target','ES2022','--module','NodeNext','--moduleResolution','NodeNext','--skipLibCheck',...files],{cwd:root,stdio:'pipe'});
});
test('PlaceOrder replay uses actual source pure gate and returns saved receipt before quote, clock or new effects',async()=>{
 const row=await build('Orders.PlaceOrder'),f=fixture(row,{context(){return customer;},async native(_p:string){return fingerprint;},async read(){return {kind:'found',value:{logicalEntryId:'checkout',customerId:'customer-one',checkoutKey:'key-one',quoteId:'quote-one',fingerprint,state:'Accepted',orderId:{kind:'some',value:'order-one'},receipt:{kind:'some',value:receipt},version:1n}};}}),result=await row.module.runOperation({quoteId:'quote-one',checkoutKey:'key-one'},f.runtime);
 assert.equal(result.kind,'returned');assert.deepEqual({...result.value},receipt);assert.equal(result.commits.length,0);assert.equal(f.trace.some(x=>x.startsWith('fixture-call:')||x.startsWith('fixture-transaction:')||x.startsWith('fixture-ack:')),false);
});
test('current access guard rejects before replay read or identity acquisition',async()=>{
 const row=await build('Orders.PlaceOrder'),f=fixture(row,{context(){return {...customer,currentActionAllowed:false};}}),result=await row.module.runOperation({quoteId:'quote-one',checkoutKey:'key-one'},f.runtime);assert.equal(result.kind,'rejected');assert.equal(result.code,'forbidden');assert.equal(f.trace.some(x=>/fixture-(read|native|call|count)/.test(x)),false);
});
test('read-set sorts actual source keys and closes its lease before an invoke-return handler',async()=>{
 const row=await build('Inventory.ReserveStock'),seen:string[]=[],command={commandId:'cmd',orderId:'order',kind:'Reserve',requestFingerprint:fingerprint,outcome:{kind:'Pending',commandId:'cmd'},version:1n};let leaseClosed=false;
 const f=fixture(row,{context(){throw Error('UnexpectedDataContext');},async native(p:string){const site=row.bundle.manifest.source_sites[p];if(site.method==='ownsOrProvesQuiescentLocalCommand')return true;return fingerprint;},async call(p:string){const site=row.bundle.manifest.source_sites[p];if(site.target==='Inventory.StartStockCommand')return {kind:'value',value:{kind:'Ready',command},commits:[],unresolved:[]};assert.equal(site.target,'Inventory.RejectStockCommand');assert.equal(leaseClosed,true);seen.push('handler');return {kind:'value',value:{kind:'Unknown',commandId:'cmd'},commits:[],unresolved:[]};},async read(_p:string,key:any){seen.push(key.sku);return {kind:'missing'};},async closeReadSet(){leaseClosed=true;seen.push('close');}});
 const result=await row.module.runOperation({orderId:'order',commandId:'cmd',lines:[{sku:'z',quantity:1n},{sku:'a',quantity:1n}]},f.runtime);assert.deepEqual(seen,['a','close','handler']);assert.equal(result.kind,'returned');assert.equal(result.value.kind,'Unknown');assert.equal(result.commits.length,0);
});
test('callee uncertainty is retained across a source data return and cannot become committed success',async()=>{
 const row=await build('Inventory.ReserveStock'),ticket={test_seam:'uncertain-original-owner-not-claimed'},f=fixture(row,{async native(){return fingerprint;},async call(){return {kind:'indeterminate',ticket,has_value:true,value:{kind:'Unknown',commandId:'cmd'},channel:null};}}),result=await row.module.runOperation({orderId:'order',commandId:'cmd',lines:[]},f.runtime);assert.equal(result.kind,'indeterminate');assert.equal(result.do_not_ack,true);assert.equal(result.has_value,true);assert.deepEqual(result.tickets,[ticket]);assert.equal(result.commits.length,0);
});
test('custody failure after awaited native observation propagates before later source work',async()=>{
 const row=await build('Orders.PlaceOrder');let revoked=false;const f=fixture(row,{assertCurrent(){if(revoked)throw Error('RetiredOriginalInvocation');},context(){return customer;},async read(){return {kind:'missing'};},async native(){revoked=true;return fingerprint;}});await assert.rejects(()=>row.module.runOperation({quoteId:'quote-one',checkoutKey:'key-one'},f.runtime),/RetiredOriginalInvocation/);assert.equal(f.trace.some(x=>x.startsWith('fixture-count:')||x.startsWith('original-pure:')),false);
});
test('transaction uncertainty fixture executes the declared Unknown return while retaining its unresolved ticket',async()=>{
 const row=await build('Inventory.StartStockCommand'),tx=plans.inspectOperation(row.operation).transactions[0],action=tx.plan.handlers.find((h:any)=>h.channel==='on-unknown-commit').action,ticket={test_seam:'unresolved-transaction-observation-not-original-proof'};let selected=false;
 const f=fixture(row,{async read(){return {kind:'missing'};},async transaction(p:string){assert.equal(p,tx.path);return {kind:'indeterminate',ticket,source_action:action,retain_original:true,do_not_ack:true};},assertTransaction(_p:string,s:any){assert.equal(s.kind,'indeterminate');},assertSourceReturn(_p:string,_s:any,a:any){assert.deepEqual(a,action);selected=true;}}),result=await row.module.runOperation({commandId:'cmd',orderId:'order',kind:'Reserve',requestFingerprint:fingerprint},f.runtime);
 assert.equal(selected,true);assert.equal(result.kind,'indeterminate');assert.equal(result.has_value,true);assert.deepEqual({...result.value},{kind:'Unknown',commandId:'cmd'});assert.deepEqual(result.tickets,[ticket]);assert.equal(result.do_not_ack,true);assert.equal(result.commits.length,0);
});

function sample(type:any,seed=1):any {
 switch(type.kind){
  case'scalar':return type.name==='Bool'?false:1n;case'literal':return type.value;case'string':return 'data-'+seed;
  case'refinement':{const r=values.refinements.find((r:any)=>r.name===type.name);return r.pattern==='^[a-f0-9]{64}$'?'a'.repeat(64):r.pattern==='^evt_[a-f0-9]{64}$'?'evt_'+'a'.repeat(64):'id-'+seed;}
  case'optional':return {kind:'none'};case'list':return Array.from({length:Math.max(type.min_items,Math.min(2,type.max_items))},(_,i)=>sample(type.element,seed*10+i));
  case'record':{const r=values.records.find((r:any)=>r.name===type.name);assert.ok(r);return Object.fromEntries(Object.entries(r.fields).map(([k,t])=>[k,sample(t,seed)]));}
  case'enum':case'variant':{const e=values.enums.find((e:any)=>e.name===(type.kind==='variant'?type.enum_name:type.name)),v=type.kind==='variant'?e.variants.find((v:any)=>v.name===type.variant):e.variants[0];return e.variants.every((v:any)=>!Object.keys(v.fields).length)?v.name:{kind:v.name,...Object.fromEntries(Object.entries(v.fields).map(([k,t])=>[k,sample(t,seed)]))};}
  default:throw Error('UnsupportedFixtureType');
 }
}
function replayRecoveryFixture(row:any,mode:'accepted'|'missing'|'conflict'|'revoked'|'deny-proof'){
 const recovery=row.bundle.manifest.recovery_plans[0],readKeys:any[]=[],events:string[]=[],nativeMethods:string[]=[];let readCount=0,currentAccess=true;
 const quote={id:'quote-one',customerId:'customer-one',currency:'USD',lines:[{sku:'sku-one',quantity:2n,unitPriceMinor:100n}],discountMinor:0n,taxMinor:0n,shippingMinor:0n,expiresAtEpochMs:1000n,version:1n};
 const f=fixture(row,{context(){return {...customer,currentActionAllowed:currentAccess};},async native(p:string){const site=row.bundle.manifest.source_sites[p];nativeMethods.push(site.method);events.push('native:'+site.method);if(site.method==='checkoutFingerprint')return fingerprint;if(site.method==='clockEpochMs')return 10n;if(site.method==='newOrderId')return 'order-new';if(site.method==='eventMetadata')return sample(site.result);throw Error('UnexpectedFixtureIdentity');},
  async read(p:string,key:any){const site=row.bundle.manifest.source_sites[p];if(site.entity===null){events.push('quote');return {kind:'found',value:quote};}readKeys.push(key);events.push('replay');if(++readCount===1||mode==='missing')return {kind:'missing'};return {kind:'found',value:{logicalEntryId:'checkout',customerId:'customer-one',checkoutKey:'key-one',quoteId:'quote-one',fingerprint:mode==='conflict'?'b'.repeat(64):fingerprint,state:'Accepted',orderId:{kind:'some',value:receipt.orderId},receipt:{kind:'some',value:receipt},version:1n}};},
  async transaction(p:string){events.push('transaction');assert.equal(p,recovery.transaction_path);if(mode==='revoked')currentAccess=false;return {kind:'generated-recovery-required',recovery:recovery.kind,rollback:Symbol('fixture-rollback-observation-not-original-proof'),source_path:p};},
  assertTransaction(){},assertRecovery(p:string,_s:any,plan:any){events.push('recovery-proof-seam');assert.equal(p,recovery.transaction_path);assert.deepEqual(plan,recovery);if(mode==='deny-proof')throw Error('UnownedRecoveryDisposition');},
 });return {...f,events,readKeys,nativeMethods};
}

test('generated checkout recovery uses the captured original key and fingerprint, then the actual source replay gate',async()=>{
 const row=await build('Orders.PlaceOrder'),f=replayRecoveryFixture(row,'accepted'),result=await row.module.runOperation({quoteId:'quote-one',checkoutKey:'key-one'},f.runtime);
 assert.equal(result.kind,'returned');assert.deepEqual({...result.value},receipt);assert.equal(result.commits.length,0);assert.equal(f.readKeys.length,2);assert.equal(f.readKeys[0],f.readKeys[1]);assert.equal(Object.isFrozen(f.readKeys[0]),true);assert.deepEqual(f.events.slice(f.events.indexOf('recovery-proof-seam')),['recovery-proof-seam','replay']);assert.deepEqual(f.nativeMethods,['checkoutFingerprint','clockEpochMs','newOrderId','eventMetadata']);
});
test('missing or conflicting authoritative replay cannot retry fresh work after the original rollback',async()=>{
 const row=await build('Orders.PlaceOrder');for(const mode of ['missing','conflict'] as const){const f=replayRecoveryFixture(row,mode),result=await row.module.runOperation({quoteId:'quote-one',checkoutKey:'key-one'},f.runtime);assert.equal(result.kind,mode==='missing'?'failed':'rejected');assert.equal(result.code,mode==='missing'?'outcome-unknown':'replay-key-conflict');assert.equal(f.events.filter(x=>x==='quote').length,1);assert.equal(f.events.filter(x=>x==='transaction').length,1);}
});
test('recovery rechecks current access and requires its original disposition before another authoritative read',async()=>{
 const row=await build('Orders.PlaceOrder'),revoked=replayRecoveryFixture(row,'revoked'),result=await row.module.runOperation({quoteId:'quote-one',checkoutKey:'key-one'},revoked.runtime);assert.equal(result.kind,'rejected');assert.equal(result.code,'forbidden');assert.equal(revoked.readKeys.length,1);
 const denied=replayRecoveryFixture(row,'deny-proof');await assert.rejects(()=>row.module.runOperation({quoteId:'quote-one',checkoutKey:'key-one'},denied.runtime),/UnownedRecoveryDisposition/);assert.equal(denied.readKeys.length,1);
});
function fulfillmentRecoveryFixture(row:any,mode:'inbox'|'conflicting-inbox'|'missing-inbox'|'shipment'){
 const plan=plans.inspectOperation(row.operation).plan,confirmed=sample(plan.parameters[0].type),events:string[]=[],keys=new Map<string,any[]>();confirmed.metadata.producer='orders';confirmed.metadata.aggregateId=confirmed.orderId;confirmed.metadata.correlationId=confirmed.orderId;
 const recovery=row.bundle.manifest.recovery_plans.find((r:any)=>r.kind===(mode==='shipment'?'proven-rollback-reread-original-inbox-or-shipment':'reread-original-inbox')),anchorPath=recovery.original_read_paths[0],secondary=plan.body.find((s:any,i:number)=>s.kind==='read'&&'$.body['+i+']'!==anchorPath),shipment=sample({kind:'record',name:secondary.entity}),stored=sample(plan.result);shipment.orderId=confirmed.orderId;shipment.orderFingerprint=fingerprint;
 let inboxReads=0,shipmentReads=0;
 const f=fixture(row,{context(){return {currentEntryId:'Fulfillment.OnOrderConfirmed',currentActionAllowed:true,serviceId:'orders',targetServiceId:'fulfillment'};},async native(p:string){const site=row.bundle.manifest.source_sites[p];events.push('native:'+site.method);if(site.method==='commandId')return 'shipment-new';if(site.method==='eventMetadata')return sample(site.result);return fingerprint;},async read(p:string,key:any){const seen=keys.get(p)??[];seen.push(key);keys.set(p,seen);if(p===anchorPath){events.push('inbox-read');if(++inboxReads===1||mode==='missing-inbox'||mode==='shipment')return {kind:'missing'};return {kind:'found',value:{consumerEntryId:'Fulfillment.OnOrderConfirmed',occurrenceId:confirmed.metadata.eventId,eventFingerprint:mode==='conflicting-inbox'?'b'.repeat(64):fingerprint,orderId:confirmed.orderId,receipt:stored,version:1n}};}events.push('shipment-read');if(++shipmentReads===1&&mode==='shipment')return {kind:'missing'};return {kind:'found',value:shipment};},
  async transaction(p:string){events.push('transaction:'+p);if(mode==='shipment'&&p!==recovery.transaction_path)throw Error('StopAtOriginalInboxCommitRequired');assert.equal(p,recovery.transaction_path);return {kind:'generated-recovery-required',recovery:recovery.kind,rollback:Symbol('fixture-rollback-not-original-proof'),source_path:p};},assertTransaction(){},assertRecovery(p:string,_s:any,r:any){events.push('recovery-proof-seam');assert.equal(p,recovery.transaction_path);assert.deepEqual(r,recovery);},
 });return {...f,confirmed,events,keys,stored,recovery};
}
test('generated inbox recovery reruns original identity guards and returns its stored receipt without fresh shipment work',async()=>{
 const row=await build('Fulfillment.CreateShipment'),f=fulfillmentRecoveryFixture(row,'inbox'),result=await row.module.runOperation({confirmed:f.confirmed},f.runtime);assert.equal(result.kind,'returned');assert.deepEqual(plain(result.value),f.stored);assert.equal(result.commits.length,0);const key=f.keys.get(f.recovery.original_read_paths[0])!;assert.equal(key.length,2);assert.equal(key[0],key[1]);assert.deepEqual(f.events.slice(f.events.indexOf('recovery-proof-seam')),['recovery-proof-seam','inbox-read']);
});
test('missing/conflicting recovered inbox cannot be acknowledged or replaced by another shipment',async()=>{
 const row=await build('Fulfillment.CreateShipment');for(const mode of ['missing-inbox','conflicting-inbox'] as const){const f=fulfillmentRecoveryFixture(row,mode),result=await row.module.runOperation({confirmed:f.confirmed},f.runtime);assert.equal(result.kind,mode==='missing-inbox'?'failed':'rejected');assert.equal(result.code,mode==='missing-inbox'?'outcome-unknown':'event-identity-conflict');assert.equal(f.events.some(x=>x==='native:commandId'||x==='native:eventMetadata'),false);assert.equal(f.trace.some(x=>x.startsWith('fixture-ack:')),false);}
});
test('inbox-or-shipment recovery reaches the original inbox transaction instead of retrying a shipment write',async()=>{
 const row=await build('Fulfillment.CreateShipment'),f=fulfillmentRecoveryFixture(row,'shipment');await assert.rejects(()=>row.module.runOperation({confirmed:f.confirmed},f.runtime),/StopAtOriginalInboxCommitRequired/);const after=f.events.slice(f.events.indexOf('recovery-proof-seam'));assert.deepEqual(after,['recovery-proof-seam','inbox-read','shipment-read','transaction:'+f.recovery.nested_transaction_paths[0]]);assert.equal(f.events.filter(x=>x==='transaction:'+f.recovery.transaction_path).length,1);
});
test('ambiguous receipt anchors and unresolved-as-rollback recovery reject during source construction',async()=>{
 const row=await build('Orders.PlaceOrder'),view=plans.inspectOperation(row.operation),input={operation:view.operation,source_capture_sha256:view.source_capture_sha256,effect_plan:view.plan,transactions:view.transactions};
 const uncertain=structuredClone(input);uncertain.transactions[0].plan.handlers[0].requires='original-unresolved-commit';uncertain.effect_plan.body[25].transaction=uncertain.transactions[0].plan;assert.throws(()=>deriveCommerceSourceRecoveryPlansV1(uncertain as any),/UnresolvedRecoveryRequiresDistinctNativeProtocol/);
 const ambiguous=structuredClone(input);ambiguous.effect_plan.body.splice(4,0,{...structuredClone(ambiguous.effect_plan.body[3]),name:'another-receipt'});ambiguous.transactions[0].path='$.body[26].transaction';assert.throws(()=>deriveCommerceSourceRecoveryPlansV1(ambiguous as any),/AmbiguousRecoveryReceiptRead/);
});

test('single-payload enum match passes the payload to the original typed observation Rule',async()=>{
 const row=await build('Orders.RecordCheckoutObservation');
 const order=sample({kind:'record',name:'Orders.Order'});
 order.id='order-one';order.status='AwaitingStock';order.version=1n;
 order.lines=[{sku:'sku-one',quantity:1n}];
 const progress=sample({kind:'record',name:'Orders.CheckoutProgress'});
 progress.orderId=order.id;progress.state=order.status;progress.version=2n;
 progress.reserveCommandId='reserve-one';progress.reserveResult={kind:'none'};
 const reservation=sample({kind:'record',name:'Inventory.ReservationView'});
 Object.assign(reservation,{reservationId:'reservation-one',orderId:order.id,lines:order.lines,
  linesFingerprint:fingerprint,reserveCommandId:progress.reserveCommandId,
  lastCommandId:progress.reserveCommandId,status:'Reserved',version:1n});
 const f=fixture(row,{
  async read(p:string){const entity=row.bundle.manifest.source_sites[p].entity;
   if(entity==='Orders.Order')return {kind:'found',value:order};
   assert.equal(entity,'Orders.CheckoutProgress');return {kind:'found',value:progress};
  },
  async native(p:string){const method=row.bundle.manifest.source_sites[p].method;
   if(method==='owns')return true;
   if(method==='stockLinesFingerprint')return fingerprint;
   if(method==='commandId')return reservation.reservationId;
   assert.equal(method,'taggedCommandIdentity');throw Error('StopAfterSourcePayloadChecks');
  },
 });
 let payloadChecks=0;const originalPure=f.runtime.pure;
 f.runtime.pure=async(p:string,args:any[])=>{
  if(row.bundle.manifest.source_sites[p].declaration==='Orders.MatchingReservation'){
   assert.deepEqual(plain(args[1]),reservation,'single-field match binding is the declared payload, not its enum wrapper');
   payloadChecks++;
  }
  return originalPure(p,args);
 };
 await assert.rejects(()=>row.module.runOperation({orderId:order.id,expectedOrderVersion:1n,
  expectedProgressVersion:2n,observation:{kind:'ReserveApplied',reservation}},f.runtime),
  /StopAfterSourcePayloadChecks/);
 assert.equal(payloadChecks,1);
 assert.equal(f.trace.some(row=>row.startsWith('fixture-transaction:')),false);
});
