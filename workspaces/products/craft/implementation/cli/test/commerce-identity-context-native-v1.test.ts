/** Original source-call and private invocation join; no application assembly. */
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,mkdirSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../src/commerce/commerce-core-pure-contract.js';
import {createCoreCommerceEffectContracts} from '../src/commerce/commerce-core-role-contracts.js';
import {createCommerceComputationDomainOwner} from '../src/commerce/commerce-computation-domain.js';
import {createCommerceLocalPlanOwnerV1} from '../src/commerce/commerce-local-plan-owner-v1.js';
import {createCommerceIdentityCallOwner} from '../src/commerce/commerce-identity-call-owner.js';
import {createCommerceIdentityContextNativeV1} from '../src/commerce/commerce-identity-context-native-v1.js';
import {produceCommerceAuthNativeOwnerV1} from '../src/commerce/commerce-auth-ready-bridge-v1.js';
import {createCommerceEntryContextOwnerV1,registerCommerceEntryFixtureActorV1} from '../src/commerce/commerce-entry-context-v1.js';
import {createCommerceSourceInvocationOwnerV1} from '../src/commerce/commerce-source-invocation-owner-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from './support/commerce-auth-fixture-provider-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
let root:string,sources:any,capture:any,stage:any,source:any,domain:any,baseline:any,plans:any,calls:any,authNative:any,auth:any,invocations:any,identity:any;
let checkout:any,clock:any,other:any;
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;

before(async()=>{
 root=mkdtempSync(path.join(tmpdir(),'commerce-identity-context-'));
 sources=createCoreCommerceSourceOwner();capture=sources.prepare(candidate);
 const captured=sources.inspect(capture),paths=new Set(captured.reconstruction.modules.map((m:any)=>m.path)),texts=captured.files.filter((f:any)=>paths.has(f.path)),assets=captured.files.filter((f:any)=>f.path.endsWith('.json'));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 stage=createCoreCommerceStageSourceOwner(sources,semantics);source=await stage.prepare(candidate,'application.alch');
 domain=createCommerceComputationDomainOwner(stage,source);
 const limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
 calls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline);
 const effects=createCoreCommerceEffectContracts(texts,assets),place=effects.find((p:any)=>p.operation?.module==='Orders'&&p.operation?.name==='PlaceOrder'),payment=effects.find((p:any)=>p.operation?.module==='Payments'&&p.operation?.name==='CapturePayment');
 assert.ok(place);assert.ok(payment);
 const select=(plan:any,method:string)=>{const path=calls.paths(plan).find((p:string)=>calls.inspect(calls.bind(plan,p)).observation.method===method);assert.ok(path,method);return calls.bind(plan,path);};
 checkout=select(place,'checkoutFingerprint');clock=select(place,'clockEpochMs');other=select(payment,'captureFingerprint');
 authNative=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
 auth=await createCommerceEntryContextOwnerV1(sources,capture,stage,source,domain,baseline,authNative,path.join(root,'auth'));
 invocations=await createCommerceSourceInvocationOwnerV1(stage,source,domain,baseline,plans,auth,path.join(root,'invocations'));
 const identityDirectory=path.join(root,'identity');mkdirSync(identityDirectory);
 identity=await createCommerceIdentityContextNativeV1(calls,stage,source,domain,baseline,invocations,[checkout,clock,other],identityDirectory);
});
after(async()=>{identity?.dispose();invocations?.dispose();auth?.dispose();await authNative?.dispose();plans?.dispose();if(root)rmSync(root,{recursive:true,force:true});});

async function rootInvocation(entryId:string,input:Record<string,unknown>){
 const entry=auth.bindEntry(entryId),definition=auth.inspectEntry(entry),subject='customer-one',evidence='identity-context-evidence',fixture=seedCommerceAuthFixtureDatabaseV1(authNative,{subject,evidence,session:'identity-context-session',routes:[{entry:entryId,permission:definition.access.auth_permission}]}),actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{subject,evidence,principal_kind:'customer',service_id:null,scope:definition.access.auth_permission.scope}),prepared=auth.prepareInput(entry,Buffer.from(JSON.stringify(input))),allowed=await auth.authorizeCommerceEntry(actor,entry,prepared);
 assert.equal(allowed.ok,true);const authorized=await auth.consumeCommerceEntryContext(allowed.value,entry,prepared);return invocations.begin(authorized,input);
}

test('V5 identity context invokes only the original source method for its live operation',async()=>{
 const invocation=await rootInvocation('Orders.PlaceOrderEntry',{quoteId:'quote-one',checkoutKey:'checkout-one'}),site=identity.bindOriginalCallsite(checkout),native=identity.createCommerceIdentityProducers(invocation,site);
 identity.assertCommerceIdentityContextCurrent(native,invocation);
 const expected=JSON.parse(readFileSync(path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/EC03/identity-vectors.json'),'utf8')).tuple_vectors.find((v:any)=>v.id==='checkout-ascii');
 assert.equal(native.checkoutFingerprint(...expected.fields),expected.sha256);
 assert.throws(()=>native.clockEpochMs(),code('UnboundMethod'));
 assert.throws(()=>({...native}).checkoutFingerprint(...expected.fields),code('ForeignOwner'));
 assert.throws(()=>identity.assertCommerceIdentityContextCurrent({...native},invocation),code('ForeignOwner'));
 assert.throws(()=>identity.createCommerceIdentityProducers({...invocation},site),code('ForeignInvocation'));
 assert.throws(()=>identity.createCommerceIdentityProducers(invocation,{...site}),code('ForeignCallsite'));
 assert.throws(()=>identity.createCommerceIdentityProducers(invocation,identity.bindOriginalCallsite(other)),code('ForeignInvocation'));
 const clockNative=identity.createCommerceIdentityProducers(invocation,identity.bindOriginalCallsite(clock));
 const timestamp=clockNative.clockEpochMs();assert.equal(typeof timestamp,'bigint');assert.ok(timestamp>=0n);
 assert.throws(()=>Reflect.apply(clockNative.clockEpochMs,clockNative,[1]),code('ProducerValueRejected'));
 assert.throws(()=>clockNative.checkoutFingerprint('entry','customer','quote'),code('UnboundMethod'));
 invocations.retire(invocation);assert.throws(()=>native.checkoutFingerprint(...expected.fields),code('RetiredInvocation'));
});
