/** Exact original-source/native identity components. No selected invocation.
 * Open Questions: docs/COMMERCE-NATIVE-IDENTITY.md#open-questions. */
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,mkdirSync,rmSync,renameSync,statSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createCoreCommerceEffectContracts,createCoreCommerceWorkflowContracts} from '../../src/commerce/commerce-core-role-contracts.js';
import {createCommerceComputationDomainOwner} from '../../src/commerce/commerce-computation-domain.js';
import {createCommerceIdentityCallOwner,assertCommerceIdentityCallOwner} from '../../src/commerce/commerce-identity-call-owner.js';
import {generateCommerceIdentityBundle,checkCommerceTaggedIdentitySlotGroupsV1} from '../../src/commerce/commerce-identity-generation.js';
import {createCommerceIdentityComponentOwner} from '../../src/commerce/commerce-identity-component.js';
const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,''),limits=JSON.parse(readFileSync(new URL('../../../../../../../implementation/craft-alchlang-commerce-2026-10-16/evidence/EC07/pure-producer-model-09.json',import.meta.url),'utf8')).limits,vectors=JSON.parse(readFileSync(new URL('../../../../../../../implementation/craft-alchlang-commerce-2026-10-16/evidence/EC03/identity-vectors.json',import.meta.url),'utf8'));
let sources:any,capture:any,stage:any,source:any,domain:any,baseline:any,calls:any,native:any,component:any,plans:any[],handles:any[],bindings:any[],directory:string;
before(async()=>{
 sources=createCoreCommerceSourceOwner();capture=sources.prepare(candidate);const data=sources.inspect(capture),paths=new Set(data.reconstruction.modules.map((m:any)=>m.path)),texts=data.files.filter((f:any)=>paths.has(f.path)),assets=data.files.filter((f:any)=>f.path.endsWith('.json'));plans=[...createCoreCommerceEffectContracts(texts,assets),...createCoreCommerceWorkflowContracts(texts,assets)];
 stage=createCoreCommerceStageSourceOwner(sources,createCoreCommerceSemanticOwner(sources));source=await stage.prepare(candidate,'application.alch');domain=createCommerceComputationDomainOwner(stage,source);baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));calls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline);handles=[];
 for(const p of plans)for(const path of calls.paths(p))handles.push(calls.bind(p,path));bindings=calls.inspectMany(handles);directory=mkdtempSync(path.join(tmpdir(),'commerce-native-identities-'));native=createCommerceIdentityComponentOwner(calls,stage,source,domain,baseline);component=await native.materialize(handles,directory);
});
after(()=>{if(directory)rmSync(directory,{recursive:true,force:true});});
const chosen=(method:string,predicate:(b:any)=>boolean=()=>true)=>{const index=bindings.findIndex(b=>b.observation.method===method&&predicate(b));assert.ok(index>=0,method+' has a genuine source call');return handles[index];},invoke=(method:string,args:any[],predicate?:(b:any)=>boolean)=>native.evaluateBoundParameters(component,chosen(method,predicate),args),ok=(r:any)=>{assert.equal(r.ok,true,JSON.stringify(r,(_k,x)=>typeof x==='bigint'?String(x):x));return r.value;},bad=(r:any)=>{assert.equal(r.ok,false);assert.equal(r.error.code,'ProducerValueRejected');};
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;
const order='ord_'+'a'.repeat(64),attempt='cmd_'+'b'.repeat(64),stock=[{sku:'A',quantity:1n},{sku:'é',quantity:18446744073709551615n}],vector=(id:string)=>vectors.tuple_vectors.find((r:any)=>r.id===id),literal=(name:string)=>(b:any)=>b.parameters[0].literal?.value===name;
const canon=(v:any):string=>v===null?'null':typeof v==='bigint'?JSON.stringify(String(v)):typeof v==='string'?JSON.stringify(v):Array.isArray(v)?'['+v.map(canon).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canon(v[k])).join(',')+'}',expected=(d:string,fields:string[])=>{const all=[d,...fields].map(s=>Buffer.from(s)),chunks:Buffer[]=[];for(const b of all){const n=Buffer.alloc(4);n.writeUInt32BE(b.length);chunks.push(n,b);}return createHash('sha256').update(Buffer.concat(chunks)).digest('hex');};
test('genuine source calls cover all12native methods across original Operations and Workflow',()=>{
 assertCommerceIdentityCallOwner(calls);assert.equal(new Set(bindings.map(b=>b.observation.method)).size,12);assert.ok(bindings.some(b=>b.caller==='Orders.Checkout.Checkout'));
 for(const b of bindings){assert.equal(b.observation.placement,'original-source-expression-callsite');assert.equal(b.observation.custody,'required-from-original-native-owner');assert.equal(b.authority_effect,'none');assert.ok(Object.isFrozen(b.parameters));}
});
for(const id of ['checkout-ascii','checkout-exact-unicode','checkout-decomposed-unicode'])test('unchanged EC03 literal '+id+' matches actual producer',()=>{const v=vector(id);assert.equal(ok(invoke('checkoutFingerprint',v.fields)),v.sha256);});
test('order,command and occurrence IDs match independent frozen tuples',()=>{
 assert.equal(ok(invoke('newOrderId',vector('order-id').fields)),'ord_'+vector('order-id').sha256);
 assert.equal(ok(invoke('commandId',vector('capture-command').fields,literal('payments.capture'))),'cmd_'+vector('capture-command').sha256);
 const metadata=ok(invoke('eventMetadata',['orders',order,1n,0n,order,attempt],b=>b.caller==='Orders.PlaceOrder'));assert.equal(metadata.eventId,'evt_'+vector('occurrence-v1').sha256);assert.equal(metadata.aggregateVersion,1n);assert.equal(metadata.ordinal,0n);
});
test('stock,provider capture and cancellation match unchanged EC03 hashes',()=>{
 assert.equal(ok(invoke('stockLinesFingerprint',[stock])),vector('stock-lines').sha256);
 assert.equal(ok(invoke('captureFingerprint',[attempt,order,18446744073709551615n,'USD'])),vector('capture-request').sha256);
 assert.equal(ok(invoke('orderActionFingerprint',['cancel',order,{kind:'some',value:'PaymentDeclined'}],literal('cancel'))),vector('cancel-action').sha256);
});
test('checked tagged enum slots preserve replay, definitive conflict and Unknown continuation',()=>{
 const h=chosen('taggedCommandIdentity',b=>b.caller==='Orders.RecordCheckoutObservation');
 const payment=(status:'Captured'|'Declined',reference:string)=>({attemptKey:attempt,orderId:order,amountMinor:25n,currency:'USD',requestFingerprint:'a'.repeat(64),status,providerReference:{kind:'some',value:reference},version:2n});
 const applied={kind:'CaptureApplied',payment:payment('Captured','provider-1')},rejected={kind:'CaptureRejected',payment:payment('Declined','provider-2')},unknown={kind:'CaptureUnknown',attemptKey:attempt};
 const first=ok(native.evaluateBoundParameters(component,h,[order,applied])),same=ok(native.evaluateBoundParameters(component,h,[order,applied]));
 const conflict=ok(native.evaluateBoundParameters(component,h,[order,rejected])),later=ok(native.evaluateBoundParameters(component,h,[order,unknown]));
 assert.equal(first.commandId,'cmd_'+expected('craft.tagged-observation/v1-candidate/slot',[order,'Orders.CheckoutObservation','capture-outcome']));
 assert.deepEqual({...first},{...same});assert.equal(first.commandId,conflict.commandId);assert.notEqual(first.requestFingerprint,conflict.requestFingerprint);
 assert.notEqual(first.commandId,later.commandId);assert.notEqual(first.requestFingerprint,later.requestFingerprint);
 bad(native.evaluateBoundParameters(component,h,[order,{kind:'InventedObservation',payment:payment('Captured','provider-1')}]));
});
test('tagged slot table must cover each original variant once with inert data',()=>{
 assert.deepEqual({...checkCommerceTaggedIdentitySlotGroupsV1({'capture-outcome':['CaptureApplied','CaptureRejected'],'capture-unknown':['CaptureUnknown']},['CaptureApplied','CaptureRejected','CaptureUnknown'])},{CaptureApplied:'capture-outcome',CaptureRejected:'capture-outcome',CaptureUnknown:'capture-unknown'});
 for(const slots of [null,{}, {'capture-outcome':['CaptureApplied']},{'capture-outcome':['CaptureApplied','CaptureApplied']},{'capture-outcome':['CaptureApplied','Foreign']},new Proxy({'capture-outcome':['CaptureApplied']},{})])
  assert.throws(()=>checkCommerceTaggedIdentitySlotGroupsV1(slots,['CaptureApplied','CaptureRejected']),code('InvalidContract'));
});
test('stock command optional version is part of identity with exact method preconditions',()=>{
 const h=chosen('stockCommandFingerprint',literal('reserve')),r=native.evaluateBoundParameters(component,h,['reserve',order,stock,{kind:'none'}]);assert.equal(ok(r),expected('craft.stock-command/v1-candidate',['reserve',order,canon(stock),'none']));
 bad(native.evaluateBoundParameters(component,h,['reserve',order,stock,{kind:'some',value:1n}]));
 const allocate=chosen('stockCommandFingerprint',literal('allocate'));assert.equal(ok(native.evaluateBoundParameters(component,allocate,['allocate',order,stock,{kind:'some',value:18446744073709551615n}])),expected('craft.stock-command/v1-candidate',['allocate',order,canon(stock),'some:18446744073709551615']));bad(native.evaluateBoundParameters(component,allocate,['allocate',order,stock,{kind:'none'}]));
});
test('source literal namespace and action bindings cannot be substituted with another allowed value',()=>{
 bad(invoke('commandId',['inventory.reserve',order],literal('payments.capture')));bad(invoke('orderActionFingerprint',['confirm',order,{kind:'none'}],literal('cancel')));bad(invoke('orderActionFingerprint',['cancel',order,{kind:'none'}],literal('cancel')));
});
test('event metadata target service and exact source literals are enforced',()=>{
 const h=chosen('eventMetadata',b=>b.caller==='Orders.PlaceOrder');for(const args of [['fulfillment',order,1n,0n,order,attempt],['orders',order,2n,0n,order,attempt],['orders',order,1n,1n,order,attempt]])bad(native.evaluateBoundParameters(component,h,args));
 const b=calls.inspect(h);assert.equal(b.service,'orders');assert.deepEqual(b.event_targets,[{name:'Shop.Events.OrderPlaced',version:1}]);
});
const event=()=>({metadata:{eventId:'evt_'+'a'.repeat(64),producer:'orders',aggregateId:order,aggregateVersion:1n,ordinal:0n,correlationId:order,commandId:attempt},orderId:order,customerId:'alice',lines:[{sku:'A',quantity:1n}],payableMinor:1200n,currency:'USD',reservationId:'r1',reservationVersion:1n,paymentAttemptKey:attempt,providerReference:'p1'});
test('event fingerprint binds actual source Event name/version and full occurrence content',()=>{
 const h=chosen('eventFingerprint',b=>b.event_schema?.name==='Shop.Events.OrderConfirmed'),e=event(),first=ok(native.evaluateBoundParameters(component,h,[e]));assert.equal(first,expected('craft.event-content/v1-candidate',['Shop.Events.OrderConfirmed','1',canon(e)]));
 const other=event();other.metadata.eventId='evt_'+'b'.repeat(64);assert.notEqual(ok(native.evaluateBoundParameters(component,h,[other])),first);bad(native.evaluateBoundParameters(component,h,[{...e,qualifiedEventType:'Invented.Event'}]));
});
test('confirmed content fingerprint excludes metadata while retaining all nine immutable fields',()=>{
 const e=event(),{metadata,...content}=e,args=[e.orderId,e.customerId,e.lines,e.payableMinor,e.currency,e.reservationId,e.reservationVersion,e.paymentAttemptKey,e.providerReference],first=ok(invoke('confirmedOrderFingerprint',args));assert.equal(first,expected('craft.confirmed-order/v1-candidate',[canon(content)]));
 assert.notEqual(ok(invoke('confirmedOrderFingerprint',[...args.slice(0,8),'p2'])),first);assert.equal(metadata.producer,'orders');
});
test('original line order and exact scalar sequence are preserved without normalization',()=>{
 assert.notEqual(ok(invoke('stockLinesFingerprint',[stock])),ok(invoke('stockLinesFingerprint',[[...stock].reverse()])));assert.notEqual(ok(invoke('checkoutFingerprint',vector('checkout-exact-unicode').fields)),ok(invoke('checkoutFingerprint',vector('checkout-decomposed-unicode').fields)));
});
test('producer boundaries reject numeric coercion,invalid Unicode and invalid record/collection data',()=>{
 for(const amount of [1,'1',-1n,18446744073709551616n])bad(invoke('captureFingerprint',[attempt,order,amount,'USD']));bad(invoke('checkoutFingerprint',['entry','\ud800','quote']));bad(invoke('stockLinesFingerprint',[[]]));bad(invoke('stockLinesFingerprint',[[stock[0],stock[0]]]));bad(invoke('stockLinesFingerprint',[[{sku:'A',quantity:0n}]]));bad(invoke('stockLinesFingerprint',[[{sku:'A',quantity:1n,extra:true}]]));
});
test('full100line/control-character domain is accepted without mutating or sorting inputs',()=>{
 const rows=Array.from({length:100},(_,i)=>({sku:String(i).padStart(128,'\u0001'),quantity:18446744073709551615n})),copy=structuredClone(rows),r=invoke('stockLinesFingerprint',[rows]);assert.equal(typeof ok(r),'string');assert.ok(r.tuple_bytes<=524288);assert.deepEqual(rows,copy);bad(invoke('stockLinesFingerprint',[[...rows,rows[0]]]));
});
test('active argument arrays and nested getters are rejected without invocation',()=>{
 let touched=0;const h=chosen('checkoutFingerprint'),proxy=new Proxy(['entry','customer','quote'],{get(){touched++;throw Error('hook');}}),getter=Object.defineProperty(['entry','customer','quote'],'0',{get(){touched++;return 'entry';},enumerable:true});for(const args of [proxy,getter,Object.assign(['entry','customer','quote'],{extra:true})])bad(native.evaluateBoundParameters(component,h,args));
 const line=Object.defineProperty({sku:'A',quantity:1n},'quantity',{get(){touched++;return 1n;},enumerable:true});bad(invoke('stockLinesFingerprint',[[line]]));assert.equal(touched,0);
});
test('foreign,cloned or uncaptured private source-call/component tokens cannot invoke primitives',()=>{
 const h=chosen('checkoutFingerprint');for(const fake of [{...h},new Proxy(h,{}),{}])assert.throws(()=>native.evaluateBoundParameters(component,fake,['e','c','q']));assert.throws(()=>native.inspect({...component}));assert.throws(()=>createCommerceIdentityCallOwner({...sources},capture,stage,source,domain,baseline));assert.throws(()=>assertCommerceIdentityCallOwner({...calls}));
 const p=plans.find(p=>p.operation?.name==='PlaceOrder'),uncaptured=calls.bind(p,calls.paths(p).find((p:string)=>p.includes('body[4]'))??calls.paths(p)[0]);assert.throws(()=>native.evaluateBoundParameters(component,uncaptured,['e','c','q']));
});
test('wrong source-plan DTO and an invented call path cannot establish source ownership',()=>{
 const p=plans.find(p=>p.operation?.name==='PlaceOrder');assert.throws(()=>calls.paths({...p,service:'fulfillment'}));assert.throws(()=>calls.bind(p,'$.invented.expression'));
 let touched=0;const evil=Object.defineProperty([chosen('checkoutFingerprint')],'0',{get(){touched++;return chosen('checkoutFingerprint');},enumerable:true});assert.throws(()=>generateCommerceIdentityBundle(calls,evil,stage,source,domain,baseline));assert.equal(touched,0);
});
test('physical component owns exact TS/JS closure and selected basis remains unclaimed',()=>{
 const info=native.inspect(component);assert.equal(info.physical_members.length,10);assert.match(info.qualification,/no-original-invocation-or-private-context/);for(const f of info.physical_members){const b=readFileSync(f.path);assert.equal(b.length,f.bytes);assert.equal(createHash('sha256').update(b).digest('hex'),f.sha256);assert.equal(statSync(f.path).mode&0o777,0o600);}
});
test('real native wall clock returns an exact nonnegative UInt64 with no public time argument',()=>{
 const h=chosen('clockEpochMs'),v=ok(native.evaluateBoundParameters(component,h,[]));assert.equal(typeof v,'bigint');assert.ok(v>=0n&&v<=18446744073709551615n);bad(native.evaluateBoundParameters(component,h,[1n]));
});
test('adversarial isolated host clock numbers are rejected before bigint conversion',()=>{
 const h=chosen('clockEpochMs'),key=calls.inspect(h).key,url=pathToFileURL(path.join(directory,'context.js')).href,script=`const [url,key,kind]=process.argv.slice(1);Date.now=()=>({negative:-1,fraction:1.5,unsafe:9007199254740992,nan:NaN,infinity:Infinity}[kind]);const {createCommerceIdentityPrimitives}=await import(url);const r=createCommerceIdentityPrimitives().evaluateNativeIdentityData(key,[]);console.log(JSON.stringify(r));`;
 for(const kind of ['negative','fraction','unsafe','nan','infinity'])bad(JSON.parse(execFileSync(process.execPath,['--input-type=module','-e',script,url,key,kind],{encoding:'utf8'})));
});
test('exclusive materialization preserves an occupied destination',async()=>{
 const occupied=path.join(directory,'occupied');mkdirSync(occupied);writeFileSync(path.join(occupied,'package.json'),'retain');await assert.rejects(native.materialize([chosen('checkoutFingerprint')],occupied));assert.equal(readFileSync(path.join(occupied,'package.json'),'utf8'),'retain');
});
test('one revoked token is still rejected in a batch while other tokens remain current',()=>{
 const p=plans.find(p=>p.operation?.name==='PlaceOrder'),extra=calls.bind(p,calls.paths(p)[0]),batch=[handles[0],extra,handles.at(-1)];assert.equal(calls.inspectMany(batch).length,3);calls.dispose(extra);assert.throws(()=>calls.assertCurrentSet(batch),(e:any)=>e.diagnostics?.[0]?.code==='DisposedOwner');assert.equal(calls.inspectMany(handles).length,57);
 let touched=0;const active=Object.defineProperty([handles[0]],'0',{get(){touched++;return handles[0];},enumerable:true});assert.throws(()=>calls.assertCurrentSet(active));assert.equal(touched,0);
});
test('changed native bytes invalidate a separately captured component',async()=>{
 const nested=path.join(directory,'changed-bytes');mkdirSync(nested);const h=await native.materialize([chosen('checkoutFingerprint')],nested),file=path.join(nested,'context.js');writeFileSync(file,readFileSync(file,'utf8')+'\n');assert.throws(()=>native.assertCurrent(h),(e:any)=>e.diagnostics?.[0]?.code==='StaleOwner');
});
test('same-byte native member replacement invalidates its original component',()=>{
 const file=path.join(directory,'context.js');writeFileSync(file+'.replacement',readFileSync(file));renameSync(file+'.replacement',file);assert.throws(()=>native.assertCurrent(component),(e:any)=>e.diagnostics?.[0]?.code==='StaleOwner');assert.throws(()=>native.evaluateBoundParameters(component,chosen('checkoutFingerprint'),['e','c','q']));
});
test('disposing a genuine original source parent revokes source-call bindings',()=>{
 stage.dispose(source);assert.throws(()=>calls.inspect(chosen('checkoutFingerprint')),(e:any)=>e.diagnostics?.[0]?.code==='DisposedOwner');
});
