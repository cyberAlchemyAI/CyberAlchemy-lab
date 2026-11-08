/** Genuine Rust/Auth/source/family/SQLite composition in fresh private fixtures.
 * Typed child arguments and transaction frames are component input fixtures;
 * no full generated operation, causal resource, worker or public SDK claim.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC17/CONTEXT.md. */
import test,{before,after} from 'node:test';
import {createHash} from 'node:crypto';
import {generateCommerceValueCodecBundle} from '../src/commerce/commerce-value-codec-generation.js';
import assert from 'node:assert/strict';
import {mkdtempSync,cpSync,readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../src/commerce/commerce-computation-domain.js';
import {createCommerceLocalPlanOwnerV1} from '../src/commerce/commerce-local-plan-owner-v1.js';
import {createCommerceTechnicalModelOwnerV5} from '../src/profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../src/profile-engine/family-v5.js';
import {createCommerceSqliteFamilyOwnerV1} from '../src/commerce/commerce-sqlite-family-v1.js';
import {createCommerceSqliteTransactionOwnerV1} from '../src/commerce/commerce-sqlite-transaction-owner-v1.js';
import {produceCommerceAuthNativeOwnerV1} from '../src/commerce/commerce-auth-ready-bridge-v1.js';
import {createCommerceEntryContextOwnerV1,registerCommerceEntryFixtureActorV1} from '../src/commerce/commerce-entry-context-v1.js';
import {createCommerceSourceInvocationOwnerV1,assertCommerceSourceInvocationOwnerV1} from '../src/commerce/commerce-source-invocation-owner-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from './support/commerce-auth-fixture-provider-v1.js';
import {openCommerceSqliteUnitOfWorkV1} from '../profiles/commerce-local-v1-candidate/runtime/sqlite-unit-of-work.js';
import {createCommerceSqliteSourceReadOwnerV1} from '../profiles/commerce-local-v1-candidate/runtime/source-read-owner.js';
const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url)),base=process.env.CRAFT_SOURCE_INVOCATION_FIXTURE_ROOT??path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/EC17');
let root:string,makeInvocationOwner:(directory:string)=>Promise<any>,native:any,auth:any,invocations:any,plans:any,family:any,programs:any;const resources=new Map<string,any>();
const code=(c:string)=>(e:any)=>e?.code===c||e?.diagnostics?.[0]?.code===c;
const plain=(v:any):any=>Array.isArray(v)?v.map(plain):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).map(([k,x])=>[k,plain(x)])):v;
let serial=0;
const paymentInput={orderId:'order-one',attemptKey:'attempt-one',amountMinor:25n,currency:'USD'};
const measurements:any[]=[];let workload:any;
function measure<T>(phase:string,run:()=>T):T{const cpu=process.cpuUsage(),memory=process.memoryUsage(),start=performance.now();const value=run();measurements.push({phase,wall_ms:performance.now()-start,cpu_microseconds:process.cpuUsage(cpu),rss_before_bytes:memory.rss,rss_after_bytes:process.memoryUsage().rss,process_cumulative_max_rss_kib:process.resourceUsage().maxRSS});return value;}

before(async()=>{
 root=mkdtempSync(path.join(base,'source-invocation-controls-'));const sourceRoot=path.join(root,'source');cpSync(path.join(repo,'examples/ecommerce-target-candidate'),sourceRoot,{recursive:true,errorOnExist:true,force:false});
 // Actual source mutation fixture exercises an algebraic pure return inside a
 // transaction. Canonical source and frozen expected contracts remain unchanged.
 const file=path.join(sourceRoot,'services/payments.alch'),old=readFileSync(file,'utf8'),needle='      version <- 1\n    on-unique-conflict return InspectPaymentCommand';assert.equal(old.split(needle).length,2);writeFileSync(file,old.replace(needle,'      version <- 1\n    let derivedOutcome = ToPaymentOutcome(intent)\n    on-unique-conflict return InspectPaymentCommand'));
 const identityPath=path.join(sourceRoot,'contracts/contract-identities.json'),identities=JSON.parse(readFileSync(identityPath,'utf8')),moduleIdentity=identities.modules.find((m:any)=>m.artifact.path==='services/payments.alch'),changed=readFileSync(file);assert.ok(moduleIdentity);moduleIdentity.artifact.sha256=createHash('sha256').update(changed).digest('hex');moduleIdentity.artifact.bytes=changed.length;writeFileSync(identityPath,JSON.stringify(identities,null,2)+'\n');
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(sourceRoot),actual=sources.inspect(capture),paths=new Set(actual.reconstruction.modules.map((m:any)=>m.path)),texts=actual.files.filter((f:any)=>paths.has(f.path)),limits=JSON.parse(readFileSync(path.join(sourceRoot,'contracts/compute-bounds.json'),'utf8')).computation.limits,semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(sourceRoot,'application.alch'),domain=createCommerceComputationDomainOwner(stage,source),baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 workload={fixture:'copied ecommerce-target-candidate plus declared algebraic-mapping exercise',captured_source_sha256:actual.capture_sha256,captured_files:actual.files.length,captured_bytes:actual.files.reduce((n:any,f:any)=>n+f.bytes,0),modules:actual.reconstruction.modules.length};
 const first=measure('prepared-process-first-codec-generation',()=>generateCommerceValueCodecBundle(stage,source,domain,baseline)),second=measure('prepared-process-repeated-codec-generation',()=>generateCommerceValueCodecBundle(stage,source,domain,baseline));assert.deepEqual(first.manifest.members,second.manifest.members);workload.generated_members=first.manifest.members;workload.repeated_generated_members=second.manifest.members;workload.generated_bytes=first.manifest.members.reduce((n,f)=>n+f.bytes,0);workload.generation_definition='two real codec emitter calls on identical captured owners in one process; prepared-process first explicit call versus repeated call; neither is cold CLI startup; OS/module/compiler caches are not flushed; this is component generation, not full-application generation';
 plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));auth=await createCommerceEntryContextOwnerV1(sources,capture,stage,source,domain,baseline,native,path.join(root,'auth-context'));invocations=await createCommerceSourceInvocationOwnerV1(stage,source,domain,baseline,plans,auth,path.join(root,'invocations'));
 makeInvocationOwner=(directory:string)=>createCommerceSourceInvocationOwnerV1(stage,source,domain,baseline,plans,auth,directory);
 const models=createCommerceTechnicalModelOwnerV5(),families=createCommerceFamilyOwnerV5(models),model=await models.checkTechnicalSource(sourceRoot,'profiles/implementation.alch'),selected=families.derive(model,stage.inspect(source).application.parameters,{kind:'local-effects',omitted_capabilities:'unsupported-not-silently-executed',targets:[{module:'Orders',name:'PlaceOrder',role:'Operation'}]});
 family=createCommerceSqliteFamilyOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,selected);
 for(const service of ['orders','payments']){const schema=family.bindService(service),bundle=family.materialize(schema,path.join(root,'repository-'+service)),unit=await openCommerceSqliteUnitOfWorkV1(family,bundle,path.join(root,service+'.sqlite'),'create'),reader=await createCommerceSqliteSourceReadOwnerV1(plans,family,bundle,unit);resources.set(service,{bundle,unit,reader});}
 programs=await createCommerceSqliteTransactionOwnerV1(sources,capture,stage,source,domain,baseline,plans,family,resources.get('payments').bundle,path.join(root,'payment-identities'));
});
after(async()=>{if(root)writeFileSync(path.join(root,'generation-resource-measurements.json'),JSON.stringify({schema_version:'GEN00.2-generation-measurements/v1',workload,measurements,resource_scope:'phase CPU/RSS observes Node process only; cumulative maxRSS is whole process; native child build is excluded from emitter timings',open_questions_ref:'../../evidence/GEN00.2/README.md#open-questions'},null,2)+'\n');for(const r of resources.values()){r.reader.dispose();r.unit.close();}invocations?.dispose();auth?.dispose();await native?.dispose();family?.dispose();plans?.dispose();});
async function authorization(entryId:string,input:any){
 const entry=auth.bindEntry(entryId),definition=auth.inspectEntry(entry),n=++serial,kind=definition.access.principal_kind,subject=kind==='customer'?'customer-one':'service-'+definition.access.caller,fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence:'evidence-'+n,session:'session-'+n,routes:[{entry:entryId,permission:definition.access.auth_permission}]}),actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{subject,evidence:'evidence-'+n,principal_kind:kind,service_id:kind==='service'?definition.access.caller:null,scope:definition.access.auth_permission.scope}),wire=Buffer.from(JSON.stringify(input,(_k,v)=>typeof v==='bigint'?String(v):v)),prepared=auth.prepareInput(entry,wire),allowed=await auth.authorizeCommerceEntry(actor,entry,prepared);assert.equal(allowed.ok,true);const original=await auth.consumeCommerceEntryContext(allowed.value,entry,prepared);return {original,actor,entry};
}
async function rootInvocation(id:string,input:any){const a=await authorization(id,input);return {...a,invocation:invocations.begin(a.original,input)};}
function find(plan:any,predicate:(v:any)=>boolean){const found:{path:string;value:any}[]=[];const walk=(v:any,p:string)=>{if(!v||typeof v!=='object')return;if(predicate(v))found.push({path:p,value:v});if(Array.isArray(v))v.forEach((x,i)=>walk(x,p+'['+i+']'));else Object.entries(v).forEach(([k,x])=>walk(x,p+'.'+k));};walk(plan,'$');assert.ok(found.length);return found[0]!;}

test('only original consumed Auth plus exact canonical typed entry input issues one root invocation',async()=>{
 measure('uncached-target-preparation',()=>invocations.prepareTarget({module:'Orders',name:'PlaceOrder',role:'Operation'}));
 measure('cached-target-preparation',()=>invocations.prepareTarget({module:'Orders',name:'PlaceOrder',role:'Operation'}));
 const input={quoteId:'quote-one',checkoutKey:'checkout-one'},a=await authorization('Orders.PlaceOrderEntry',input);assert.throws(()=>invocations.begin({...a.original},input),code('ForeignOwner'));assert.throws(()=>invocations.begin(a.original,{...input,quoteId:'other-quote'}),code('ForeignAuthorizedInput'));assert.throws(()=>invocations.begin(a.original,{...input,authorized:true}),code('InputType'));
 const h=invocations.begin(a.original,{checkoutKey:input.checkoutKey,quoteId:input.quoteId}),v=invocations.inspect(h);assert.equal(v.operation,'Orders.PlaceOrder');assert.equal(v.entry,'Orders.PlaceOrderEntry');assert.equal(v.depth,0);assert.equal(v.actual_business_resource_owners_qualified,false);assert.deepEqual(plain(invocations.parameters(h)),input);assert.throws(()=>invocations.begin(a.original,input),code('AlreadyAcquired'));assert.throws(()=>invocations.inspect({...h}),code('ForeignInvocation'));assert.throws(()=>assertCommerceSourceInvocationOwnerV1({...invocations}),code('ForeignOwner'));
 const other=await rootInvocation('Orders.PlaceOrderEntry',{quoteId:'quote-two',checkoutKey:'checkout-two'});assert.equal(invocations.operation(other.invocation),invocations.operation(h),'reuse original checked definition, never compile a new target per request');assert.notDeepEqual(plain(invocations.parameters(other.invocation)),plain(invocations.parameters(h)));
});
test('private original customer read keys work with real invocation custody and reject another principal or cloned invocation',async()=>{
 const a=await rootInvocation('Orders.PlaceOrderEntry',{quoteId:'quote-one',checkoutKey:'checkout-one'}),r=resources.get('orders'),op=invocations.operation(a.invocation),site=r.reader.bind(op,'$.body[3]'),key={logicalEntryId:'Orders.PlaceOrderEntry',customerId:'customer-one',checkoutKey:'checkout-one'},authorization={owner:invocations,invocation:a.invocation};
 assert.deepEqual(r.reader.inspectObservation(r.reader.read(site,key,authorization)),{kind:'missing'});assert.throws(()=>r.reader.read(site,{...key,customerId:'customer-two'},authorization),code('ForeignPrivateKey'));assert.throws(()=>r.reader.read(site,key,{owner:invocations,invocation:{...a.invocation}}),code('ForeignInvocation'));
});
test('local helper invocation requires the actual source call path and typed forwarding, while entry calls require fresh authorization',async()=>{
 const a=await rootInvocation('Payments.CapturePaymentEntry',paymentInput),op=invocations.operation(a.invocation),view=plans.inspectOperation(op),call=find(view.plan,v=>v.target==='Payments.DispatchOriginalCapture'&&v.authorization==='original-local-context-forwarding-required'),args={orderId:paymentInput.orderId,attemptKey:paymentInput.attemptKey,requestFingerprint:'a'.repeat(64)},child=invocations.deriveLocalCall(a.invocation,call.path,args);
 assert.equal(invocations.inspect(child).operation,'Payments.DispatchOriginalCapture');assert.equal(invocations.inspect(child).parent_call_path,call.path);assert.equal(invocations.inspect(child).depth,1);assert.deepEqual(plain(invocations.parameters(child)),args);assert.throws(()=>invocations.deriveLocalCall(a.invocation,'$.body[0]',args),code('NotSourceCall'));assert.throws(()=>invocations.deriveLocalCall(a.invocation,call.path,{...args,requestFingerprint:'bad'}),code('InputType'));
 const customer=await rootInvocation('Orders.PlaceOrderEntry',{quoteId:'quote-one',checkoutKey:'checkout-one'}),remote=find(plans.inspectOperation(invocations.operation(customer.invocation)).plan,v=>v.entry==='Catalog.ReadQuoteEntry');assert.throws(()=>invocations.deriveLocalCall(customer.invocation,remote.path,{quoteId:'quote-one',customerId:'customer-one'}),code('FreshEntryAuthorizationRequired'));
 invocations.retire(a.invocation);assert.throws(()=>invocations.inspect(child),code('RetiredInvocation'));
});
test('source/native transaction evaluates actual algebraic Mapping result through private computation wire',async()=>{
 const a=await rootInvocation('Payments.CapturePaymentEntry',paymentInput),op=invocations.operation(a.invocation),view=plans.inspectOperation(op),tx=view.transactions.find((t:any)=>t.plan.name==='PrepareCapture');assert.ok(tx);const program=await programs.bind(op,plans.bindTransaction(op,tx.path)),u=resources.get('payments').unit,k={logicalEntryId:'component-source-call',principalId:'service-orders',commandId:'algebraic-result',fingerprint:'a'.repeat(64),transactionNamespace:'1'.repeat(64)},lease=u.claimCommand(k);assert.equal(lease.kind,'claimed');
 const result=u.applySourceTransaction(programs,program,lease.command,{...paymentInput,requestFingerprint:'a'.repeat(64)},{owner:invocations,invocation:a.invocation});assert.equal(result.kind,'committed',result.kind==='rolled-back'?JSON.stringify(u.inspectDisposition(result.rollback)):undefined);assert.deepEqual(plain(result.result.derivedOutcome),{kind:'Pending',attemptKey:'attempt-one'});assert.equal(u.countRows('Payments.PaymentAttempt'),1);const row=u.readRow('Payments.PaymentAttempt',0,{attemptKey:'attempt-one'});assert.equal(u.inspectRow(row).value.amountMinor,25n);
 const observed=u.observeCommand(k);assert.equal(observed.kind,'recorded');assert.equal(u.inspectDisposition(observed.receipt).kind,'committed');assert.deepEqual(plain(observed.result.derivedOutcome),{kind:'Pending',attemptKey:'attempt-one'});assert.throws(()=>u.inspectDisposition({...observed.receipt}),code('ForeignDisposition'));
 writeFileSync(path.join(root,'actual-algebraic-result.json'),JSON.stringify({source_fixture:'source-mutated transaction adds actual ToPaymentOutcome(intent) let; canonical source unchanged',operation:invocations.inspect(a.invocation),program:programs.inspect(program),result:plain(result.result)},(_k,v)=>typeof v==='bigint'?String(v):v,2)+'\n');
});
test('an Auth service decision cannot stand in for the deferred original worker lifecycle producer',async()=>{
 const input={orderId:'order-one',expectedProgressVersion:1n},a=await authorization('Orders.ClaimCheckoutWorkEntry',input);assert.throws(()=>invocations.begin(a.original,input),code('WorkerProducerRequired'));
});
test('cached target preparation rejects changed generated codecs instead of trusting its cached plan',async()=>{
 const isolated=await makeInvocationOwner(path.join(root,'cache-tamper-owner'));isolated.prepareTarget({module:'Orders',name:'PlaceOrder',role:'Operation'});const file=path.join(root,'cache-tamper-owner','values-and-codecs.js'),before=readFileSync(file);
 try{writeFileSync(file,Buffer.concat([before,Buffer.from('\n// copied-fixture corruption\n')]));assert.throws(()=>isolated.prepareTarget({module:'Orders',name:'PlaceOrder',role:'Operation'}),code('StaleOwner'));}finally{writeFileSync(file,before);isolated.dispose();}assert.deepEqual(readFileSync(file),before);
});
test('Query targets reuse genuine checked reads with independent arguments and reject forged or disposed handles',async()=>{
 const selector={module:'Orders',name:'GetOrder',role:'Query'};invocations.prepareTarget(selector);
 const a=await rootInvocation('Orders.GetOrderEntry',{orderId:'order-one'}),b=await rootInvocation('Orders.GetOrderEntry',{orderId:'order-two'}),read=invocations.read(a.invocation);
 assert.equal(invocations.inspect(a.invocation).role,'Query');assert.equal(invocations.read(b.invocation),read,'repeated Query uses the same original checked read');assert.notDeepEqual(plain(invocations.parameters(a.invocation)),plain(invocations.parameters(b.invocation)));assert.throws(()=>invocations.read({...a.invocation}),code('ForeignInvocation'));assert.throws(()=>plans.inspectRead({...read}),code('ForeignOwner'));
 invocations.retire(a.invocation);assert.throws(()=>invocations.inspect(a.invocation),code('RetiredInvocation'));assert.equal(invocations.read(b.invocation),read,'retiring one Query invocation preserves another original invocation');plans.disposeRead(read);assert.throws(()=>invocations.inspect(b.invocation),code('DisposedOwner'));assert.throws(()=>invocations.prepareTarget(selector),code('DisposedOwner'));
});
test('cached Query target rejects changed generated codecs with original physical custody',async()=>{
 const isolated=await makeInvocationOwner(path.join(root,'query-cache-tamper-owner')),selector={module:'Catalog',name:'ReadQuote',role:'Query'};isolated.prepareTarget(selector);isolated.prepareTarget(selector);const file=path.join(root,'query-cache-tamper-owner','values-and-codecs.js'),before=readFileSync(file);
 try{writeFileSync(file,Buffer.concat([before,Buffer.from('\n// copied-query-fixture corruption\n')]));assert.throws(()=>isolated.prepareTarget(selector),code('StaleOwner'));}finally{writeFileSync(file,before);isolated.dispose();}assert.deepEqual(readFileSync(file),before);
});
test('retired source targets and disposed Auth actors revoke derived invocation custody',async()=>{
 const a=await rootInvocation('Orders.PlaceOrderEntry',{quoteId:'quote-one',checkoutKey:'checkout-one'});plans.disposeOperation(invocations.operation(a.invocation));assert.throws(()=>invocations.inspect(a.invocation),code('DisposedOwner'));assert.throws(()=>invocations.prepareTarget({module:'Orders',name:'PlaceOrder',role:'Operation'}),code('DisposedOwner'));
 const b=await rootInvocation('Payments.CapturePaymentEntry',{...paymentInput,attemptKey:'other-attempt'});auth.disposeActor(b.actor);assert.throws(()=>invocations.inspect(b.invocation),code('DisposedOwner'));
 assert.throws(()=>invocations.parameters(b.invocation),code('DisposedOwner'));
 assert.throws(()=>invocations.operation(b.invocation),code('DisposedOwner'));
 assert.throws(()=>invocations.parameters(a.invocation),code('DisposedOwner'));
 assert.throws(()=>invocations.operation(a.invocation),code('DisposedOwner'));
});

test('cached target preparation rejects a changed captured source even when the target was already prepared',()=>{
 invocations.prepareTarget({module:'Payments',name:'CapturePayment',role:'Operation'});invocations.prepareTarget({module:'Catalog',name:'ReadQuote',role:'Query'});const file=path.join(root,'source','services/payments.alch'),before=readFileSync(file);
 try{writeFileSync(file,Buffer.concat([before,Buffer.from('\n// copied-fixture corruption\n')]));assert.throws(()=>invocations.prepareTarget({module:'Payments',name:'CapturePayment',role:'Operation'}),code('StaleOwner'));assert.throws(()=>invocations.prepareTarget({module:'Catalog',name:'ReadQuote',role:'Query'}),code('StaleOwner'));}finally{writeFileSync(file,before);}assert.deepEqual(readFileSync(file),before);
});
