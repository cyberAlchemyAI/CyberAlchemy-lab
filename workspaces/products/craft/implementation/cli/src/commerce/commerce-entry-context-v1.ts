/** Original source-entry/input and current native Auth decision custody.
 * Auth facets do not certify business rows, worker claims or applied effects.
 * Open Questions: docs/COMMERCE-AUTH-READY-BRIDGE-V1.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {mkdirSync} from 'node:fs';
import {randomUUID,createHash} from 'node:crypto';
import {stripTypeScriptTypes} from 'node:module';
import {captureJson,dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation,pinCorePhysicalCaptures,writeCoreExclusiveFile,type CorePhysicalFile} from './commerce-core-physical.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCoreCommerceStageSourceOwner,type CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {createCoreValueTypes} from './commerce-core-types.js';
import {createCoreContextCatalog} from './commerce-core-context.js';
import {coreValueAstType} from './commerce-core-pure.js';
import {generateCommerceValueCodecBundle} from './commerce-value-codec-generation.js';
import {assertCommerceAuthNativeOwnerV1,inspectCommerceAuthFixtureDatabaseV1,type CommerceAuthNativeOwnerV1,type CommerceAuthFixtureDatabaseV1,type AuthBridgeRequestV1,type AuthReadyProjectionV1,COMMERCE_AUTH_READY_ABI_V1} from './commerce-auth-ready-bridge-v1.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
import type {EntryContractV1} from './commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url));
const code=pinCoreImplementation(import.meta.url,['commerce-auth-ready-bridge-v1'+ext,'commerce-core-source-owner'+ext,'commerce-core-stage-owner'+ext,'commerce-computation-domain'+ext,'commerce-value-codec-generation'+ext,'commerce-core-types'+ext,'commerce-core-context'+ext,'commerce-core-pure'+ext,'commerce-core-physical'+ext,'commerce-core-syntax'+ext,'../profile-engine/contracts'+ext]);
export class CommerceEntryContextErrorV1 extends Error {constructor(readonly code:'ForeignOwner'|'DisposedOwner'|'StaleOwner'|'InputRejected'|'Forbidden'|'AlreadyConsumed'|'InvalidContract'){super(code);this.name='CommerceEntryContextErrorV1';}}
function fail(code:CommerceEntryContextErrorV1['code']):never {throw new CommerceEntryContextErrorV1(code);}
export interface CommerceAuthEntryV1 {readonly kind:'original-commerce-auth-entry/v1-candidate'}
export interface CommerceAuthInputV1 {readonly kind:'original-commerce-auth-input/v1-candidate'}
export interface CommerceAuthActorV1 {readonly kind:'original-commerce-auth-fixture-actor/v1-candidate'}
export interface CommerceEntryAuthorizationV1 {readonly kind:'original-commerce-entry-authorization/v1-candidate'}
export interface CommerceInvocationAuthorizationV1 {readonly kind:'original-commerce-invocation-authorization/v1-candidate'}
export interface CommerceCustomerAuthorizationV1 {readonly kind:'original-commerce-customer-authorization/v1-candidate'}
export interface CommerceServiceAuthorizationV1 {readonly kind:'original-commerce-service-authorization/v1-candidate'}
export interface CommerceResourceAuthorizationV1 {readonly kind:'original-commerce-resource-authorization/v1-candidate'}
export type CommerceAuthorizationResultV1={readonly ok:true;readonly value:CommerceEntryAuthorizationV1}|{readonly ok:false;readonly code:'unauthorized'|'forbidden';readonly status:401|403};
export interface CommerceFixtureActorAssignmentV1 {readonly subject:string;readonly evidence:string;readonly principal_kind:'customer'|'service';readonly service_id:string|null;readonly scope:string}
export interface CommerceEntryContextOwnerV1 {
 bindEntry(id:string):CommerceAuthEntryV1;
 inspectEntry(entry:CommerceAuthEntryV1):EntryContractV1;
 prepareInput(entry:CommerceAuthEntryV1,wire:Uint8Array):CommerceAuthInputV1;
 inspectInput(input:CommerceAuthInputV1):Readonly<{entry:string;canonical_sha256:string;bytes:number;authority_effect:'none'}>;
 matchesPreparedInput(input:CommerceAuthInputV1,sourceArguments:unknown):boolean;
 encodeEntryArguments(entry:CommerceAuthEntryV1,sourceArguments:unknown):Uint8Array;
 assertActor(actor:CommerceAuthActorV1):void;
 inspectActor(actor:CommerceAuthActorV1):Readonly<CommerceFixtureActorAssignmentV1>;
 authorizeCommerceEntry(actor:CommerceAuthActorV1|null,entry:CommerceAuthEntryV1,input:CommerceAuthInputV1,signal?:AbortSignal):Promise<CommerceAuthorizationResultV1>;
 consumeCommerceEntryContext(context:CommerceEntryAuthorizationV1,entry:CommerceAuthEntryV1,input:CommerceAuthInputV1,signal?:AbortSignal):Promise<CommerceInvocationAuthorizationV1>;
 disposeCommerceEntryContext(context:CommerceEntryAuthorizationV1):void;
 inspectInvocation(invocation:CommerceInvocationAuthorizationV1):Readonly<Record<string,unknown>>;
 principalScope(invocation:CommerceInvocationAuthorizationV1):CommerceCustomerAuthorizationV1|CommerceServiceAuthorizationV1;
 resourceScope(invocation:CommerceInvocationAuthorizationV1):CommerceResourceAuthorizationV1;
 inspectScope(scope:CommerceCustomerAuthorizationV1|CommerceServiceAuthorizationV1|CommerceResourceAuthorizationV1):Readonly<Record<string,unknown>>;
 disposeActor(actor:CommerceAuthActorV1):void;disposeInput(input:CommerceAuthInputV1):void;disposeEntry(entry:CommerceAuthEntryV1):void;
 inspect():Readonly<Record<string,unknown>>;assertCurrent():void;dispose():void;
}
type Entry={data:EntryContractV1;schema:any;principalSchema:any|null;disposed:boolean};
type Input={entry:Entry;canonical:Buffer;digest:string;disposed:boolean};
type Actor={database:CommerceAuthFixtureDatabaseV1;assignment:CommerceFixtureActorAssignmentV1;identity:string;disposed:boolean};
type Context={entry:Entry;input:Input;actor:Actor;binding:AuthBridgeRequestV1['binding'];ready:AuthReadyProjectionV1;state:'fresh'|'consuming'|'consumed'|'retired';disposed:boolean};
type Invocation={context:Context;ready:AuthReadyProjectionV1;principal:CommerceCustomerAuthorizationV1|CommerceServiceAuthorizationV1;resource:CommerceResourceAuthorizationV1};
type Registry={current:()=>void;actors:WeakMap<object,Actor>;native:CommerceAuthNativeOwnerV1;codecs:any};
const registered=new WeakMap<object,Registry>();
export function assertCommerceEntryContextOwnerV1(owner:CommerceEntryContextOwnerV1):void {const s=owner&&typeof owner==='object'?registered.get(owner):undefined;if(!s)fail('ForeignOwner');s.current();}
/** Fixture-only issuer, deliberately not exported by the public SDK. It needs
 * an actual native-created scratch namespace and the source-bound owner. */
export function registerCommerceEntryFixtureActorV1(owner:CommerceEntryContextOwnerV1,database:CommerceAuthFixtureDatabaseV1,proposal:CommerceFixtureActorAssignmentV1):CommerceAuthActorV1 {
 const s=registered.get(owner);if(!s)fail('ForeignOwner');s.current();inspectCommerceAuthFixtureDatabaseV1(s.native,database);
 const a=captureJson(proposal)as unknown as CommerceFixtureActorAssignmentV1;
 if(Object.keys(a).sort().join(',')!=='evidence,principal_kind,scope,service_id,subject'||!['customer','service'].includes(a.principal_kind)||a.principal_kind==='service'&&(typeof a.service_id!=='string'||!a.service_id.length)||a.principal_kind==='customer'&&a.service_id!==null)fail('InvalidContract');
 for(const value of [a.subject,a.evidence,a.scope,...(a.service_id===null?[]:[a.service_id])])if(typeof value!=='string'||value.length===0||Buffer.byteLength(value)>256||/\p{Cc}/u.test(value)||Buffer.from(value).toString('utf8')!==value)fail('InvalidContract');
 const h=Object.freeze({kind:'original-commerce-auth-fixture-actor/v1-candidate' as const});s.actors.set(h,{database,assignment:a,identity:randomUUID(),disposed:false});return h;
}
export async function createCommerceEntryContextOwnerV1(sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,native:CommerceAuthNativeOwnerV1,directory:string):Promise<CommerceEntryContextOwnerV1> {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceStageSourceOwner(stage);assertCommerceComputationDomainOwner(domain);assertCommerceAuthNativeOwnerV1(native);code.assertCurrent();
 const actual=sources.inspect(capture),parent=stage.inspect(source),checked=domain.inspect(baseline);
 if(actual.capture_sha256!==parent.source_sha256||checked.source_capture_sha256!==parent.source_sha256)fail('ForeignOwner');
 const declarations=stage.moduleContracts(source).flatMap(m=>m.entries),profilePaths=[...new Set(declarations.map(e=>e.access.decision.binding_path))];
 if(profilePaths.length!==1)fail('InvalidContract');const profile=actual.files.find(f=>f.path===profilePaths[0]);if(!profile)fail('InvalidContract');const config=JSON.parse(profile.text);
 if(config.abi!==COMMERCE_AUTH_READY_ABI_V1||config.process_protocol?.requests_per_child!==1||config.process_protocol.input_bytes!==4096||config.process_protocol.output_bytes!==8192||config.process_protocol.parallel_children!==4||config.process_protocol.queued_requests!==64||config.process_protocol.startup_and_evaluation_wait_ms!==2000||config.process_protocol.public_child_command_or_callback_override!==false)fail('InvalidContract');
 if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory)fail('InvalidContract');mkdirSync(directory,{mode:0o700});
 const bundle=generateCommerceValueCodecBundle(stage,source,domain,baseline),files:CorePhysicalFile[]=[],texts=new Map<string,string>();
 for(const f of bundle.files){for(const [name,text]of [[f.path,f.text],[f.path.replace(/\.ts$/,'.js'),stripTypeScriptTypes(f.text)]]as const){const row=writeCoreExclusiveFile(path.join(directory,name),text);files.push(row);texts.set(name,text);}}
 const physical=pinCorePhysicalCaptures(files);
 const url=(s:string)=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64'),needle="'./commerce-domain-values.js'",codec=texts.get('values-and-codecs.js')!;
 if(!codec.includes(needle))fail('InvalidContract');const runtime=await import(url(codec.replace(needle,JSON.stringify(url(texts.get('commerce-domain-values.js')!))))),codecs=runtime.createCommerceValueCodecs();
 const sourceTypes=createCoreValueTypes(actual.reconstruction),contextCatalog=createCoreContextCatalog(sourceTypes,actual.files.filter(f=>f.path.endsWith('.json')));
 const nativeIdentity=dataDigest(native.inspect()),profileIdentity=createHash('sha256').update(profile.text).digest('hex');
 let disposed=false;const entries=new WeakMap<object,Entry>(),inputs=new WeakMap<object,Input>(),actors=new WeakMap<object,Actor>(),contexts=new WeakMap<object,Context>(),invocations=new WeakMap<object,Invocation>(),scopes=new WeakMap<object,{invocation:Invocation;kind:'customer'|'service'|'resource'}>();
 const current=()=>{if(disposed)fail('DisposedOwner');try{code.assertCurrent();sources.assertCurrent(capture);stage.assertCurrent(source);domain.assertCurrent(baseline);native.assertCurrent();physical.assertCurrent();}catch{return fail('StaleOwner');}};
 const lookup=<T extends{disposed:boolean}>(map:WeakMap<object,T>,h:object):T=>{const r=h&&typeof h==='object'?map.get(h):undefined;if(!r)fail('ForeignOwner');if(r.disposed)fail('DisposedOwner');return r;};
 const entry=(h:CommerceAuthEntryV1)=>lookup(entries,h),input=(h:CommerceAuthInputV1)=>{const r=lookup(inputs,h);if(r.entry.disposed)fail('DisposedOwner');return r;};
 const actor=(h:CommerceAuthActorV1)=>lookup(actors,h);
 const contextCurrent=(c:Context)=>{current();if(c.disposed||c.actor.disposed||c.input.disposed||c.entry.disposed)fail('DisposedOwner');};
 const request=(c:Pick<Context,'binding'|'actor'|'entry'>):AuthBridgeRequestV1=>({abi:COMMERCE_AUTH_READY_ABI_V1,request:{request_id:randomUUID(),authentication_evidence_ref:c.actor.assignment.evidence,route_id:c.entry.data.access.auth_route_id},binding:c.binding,expected_permission:c.entry.data.access.auth_permission});
 const deny=()=>Object.freeze({ok:false as const,code:'forbidden' as const,status:403 as const});
 const currentReady=(p:AuthReadyProjectionV1)=>({subject:p.authenticated_subject_id,session:p.session_id,permission:p.required_permission,scope:p.scope_evidence_ref,evidence_revision:p.authentication_evidence_revision,route_revision:p.route_binding_revision,authorization_revision:p.current_authorization_revision,policy_snapshot_sha256:p.policy_snapshot_sha256});
 const owner:CommerceEntryContextOwnerV1=Object.freeze({
  bindEntry(id:string){current();const d=declarations.find(e=>e.id===id);if(!d)fail('InvalidContract');const h=Object.freeze({kind:'original-commerce-auth-entry/v1-candidate' as const});const declaration=sourceTypes.declarations.get(d.access.context.source_type);if(!declaration)fail('InvalidContract');const ctx=contextCatalog.require(declaration),field=ctx.properties.find(p=>p.name===(d.access.principal_kind==='customer'?'customerId':'serviceId'));let principalSchema:any|null=null;if(field){const result=codecs.checkCommerceSchema({...checked.contract.values,root:coreValueAstType(field.type)});if(!result.ok)fail('InvalidContract');principalSchema=result.value;}else if(d.access.principal_kind==='customer')fail('InvalidContract');entries.set(h,{data:d,schema:codecs.schemaForEntryArguments(id),principalSchema,disposed:false});return h;},
  inspectEntry(h:CommerceAuthEntryV1){current();return entry(h).data;},
  prepareInput(h:CommerceAuthEntryV1,wire:Uint8Array){current();const e=entry(h);if(!(wire instanceof Uint8Array)||wire.byteLength>4096)fail('InputRejected');const decoded=codecs.decodeCommerceValue(e.schema,new Uint8Array(wire));if(!decoded.ok)fail('InputRejected');const encoded=codecs.encodeCommerceValue(e.schema,decoded.value);if(!encoded.ok)fail('InputRejected');const canonical=Buffer.from(encoded.value),i=Object.freeze({kind:'original-commerce-auth-input/v1-candidate' as const});inputs.set(i,{entry:e,canonical,digest:createHash('sha256').update(canonical).digest('hex'),disposed:false});return i;},
  inspectInput(h:CommerceAuthInputV1){current();const i=input(h);return Object.freeze({entry:i.entry.data.id,canonical_sha256:i.digest,bytes:i.canonical.byteLength,authority_effect:'none' as const});},
  matchesPreparedInput(h:CommerceAuthInputV1,sourceArguments:unknown){current();const i=input(h);const result=codecs.encodeCommerceValue(i.entry.schema,sourceArguments);return result.ok&&Buffer.from(result.value).equals(i.canonical);},
  encodeEntryArguments(h:CommerceAuthEntryV1,sourceArguments:unknown){current();const e=entry(h),result=codecs.encodeCommerceValue(e.schema,sourceArguments);if(!result.ok)fail('InputRejected');return new Uint8Array(result.value);},
  assertActor(h:CommerceAuthActorV1){current();const a=actor(h);if(a.disposed)fail('DisposedOwner');},
  inspectActor(h:CommerceAuthActorV1){current();const a=actor(h);if(a.disposed)fail('DisposedOwner');return coreFreeze(a.assignment);},
  async authorizeCommerceEntry(principal:CommerceAuthActorV1|null,eh:CommerceAuthEntryV1,ih:CommerceAuthInputV1,signal?:AbortSignal){
   current();const e=entry(eh),i=input(ih);if(i.entry!==e)fail('ForeignOwner');const a=principal&&typeof principal==='object'?actors.get(principal):undefined;if(!a)return Object.freeze({ok:false as const,code:'unauthorized' as const,status:401 as const});if(a.disposed)return deny();
   if(e.principalSchema!==null&&!codecs.copyCommerceValue(e.principalSchema,a.assignment.principal_kind==='customer'?a.assignment.subject:a.assignment.service_id).ok)return deny();
   if(a.assignment.principal_kind!==e.data.access.principal_kind||a.assignment.scope!==e.data.access.auth_permission.scope||a.assignment.principal_kind==='service'&&a.assignment.service_id!==e.data.access.caller)return deny();
   const binding={invocation_id:randomUUID(),logical_entry_id:e.data.id,bound_operation_id:e.data.invokes.module+'.'+e.data.invokes.name,canonical_input_sha256:i.digest,checked_source_sha256:parent.source_sha256,profile_config_sha256:profileIdentity,native_basis_sha256:nativeIdentity,actor_owner_identity:a.identity,causal_owner_identity:null,target_service_id:e.data.service,store_or_event_epoch:dataDigest(inspectCommerceAuthFixtureDatabaseV1(native,a.database))};
   try{const completion=await native.execute(a.database,request({binding,actor:a,entry:e}),signal);current();if(a.disposed||i.disposed||e.disposed)return deny();native.assertCompletionDatabase(completion,a.database);const response=native.inspectCompletion(completion).response;if(response.outcome!=='allow'||!response.ready||response.ready.authenticated_subject_id!==a.assignment.subject){
    if(process.env.CRAFT_COMMERCE_AUTH_DIAGNOSTIC==='1')process.stderr.write('commerce-auth diagnostic=readiness-denied outcome='+response.outcome+'\n');
    return deny();
   }const h=Object.freeze({kind:'original-commerce-entry-authorization/v1-candidate' as const});contexts.set(h,{entry:e,input:i,actor:a,binding,ready:response.ready,state:'fresh',disposed:false});return Object.freeze({ok:true as const,value:h});}catch(error){
    if(process.env.CRAFT_COMMERCE_AUTH_DIAGNOSTIC==='1')process.stderr.write('commerce-auth diagnostic=bridge-error code='+String((error as {code?:unknown})?.code??'unclassified')+'\n');
    return deny();
   }
  },
  async consumeCommerceEntryContext(h:CommerceEntryAuthorizationV1,eh:CommerceAuthEntryV1,ih:CommerceAuthInputV1,signal?:AbortSignal){
   const c=lookup(contexts,h);if(c.state!=='fresh')fail('AlreadyConsumed');c.state='consuming';
   try{contextCurrent(c);if(entry(eh)!==c.entry||input(ih)!==c.input)fail('Forbidden');const completion=await native.execute(c.actor.database,request(c),signal);contextCurrent(c);native.assertCompletionDatabase(completion,c.actor.database);const response=native.inspectCompletion(completion).response;if(response.outcome!=='allow'||!response.ready||dataDigest(currentReady(response.ready))!==dataDigest(currentReady(c.ready)))fail('Forbidden');
    c.state='consumed';const principal=Object.freeze({kind:c.actor.assignment.principal_kind==='customer'?'original-commerce-customer-authorization/v1-candidate' as const:'original-commerce-service-authorization/v1-candidate' as const}),resource=Object.freeze({kind:'original-commerce-resource-authorization/v1-candidate' as const}),v:Invocation={context:c,ready:response.ready,principal,resource},out=Object.freeze({kind:'original-commerce-invocation-authorization/v1-candidate' as const});invocations.set(out,v);scopes.set(principal,{invocation:v,kind:c.actor.assignment.principal_kind});scopes.set(resource,{invocation:v,kind:'resource'});return out;
   }catch(error){c.state='retired';if(error instanceof CommerceEntryContextErrorV1)throw error;return fail('Forbidden');}
  },
  disposeCommerceEntryContext(h:CommerceEntryAuthorizationV1){lookup(contexts,h).disposed=true;},
  inspectInvocation(h:CommerceInvocationAuthorizationV1){const v=h&&typeof h==='object'?invocations.get(h):undefined;if(!v)fail('ForeignOwner');contextCurrent(v.context);return coreFreeze({entry:v.context.entry.data.id,operation:v.context.binding.bound_operation_id,input_sha256:v.context.input.digest,source_sha256:parent.source_sha256,profile_sha256:profileIdentity,native_component_sha256:nativeIdentity,invocation_id:v.context.binding.invocation_id,principal_kind:v.context.actor.assignment.principal_kind,permission:v.ready.required_permission,policy_snapshot_sha256:v.ready.policy_snapshot_sha256,business_resource_requirements:v.context.entry.data.access.resource_bindings,resource_condition:v.context.entry.data.access.resource_condition,actual_business_resource_owners_qualified:false,qualification:'entry-bound-native-authorization-custody-only;not-operation-store-worker-event-or-delivery-authority',authority_effect:'none'});},
  principalScope(h:CommerceInvocationAuthorizationV1){const v=invocations.get(h);if(!v)fail('ForeignOwner');contextCurrent(v.context);return v.principal;},resourceScope(h:CommerceInvocationAuthorizationV1){const v=invocations.get(h);if(!v)fail('ForeignOwner');contextCurrent(v.context);return v.resource;},
  inspectScope(h:CommerceCustomerAuthorizationV1|CommerceServiceAuthorizationV1|CommerceResourceAuthorizationV1){const row=scopes.get(h);if(!row)fail('ForeignOwner');const v=row.invocation,c=v.context;contextCurrent(c);return coreFreeze({kind:row.kind,...row.kind==='customer'?{customerId:v.ready.authenticated_subject_id,logicalEntryId:c.entry.data.id,commandId:c.binding.invocation_id,principalPresent:true,currentActionAllowed:true}:row.kind==='service'?{serviceId:c.actor.assignment.service_id,targetServiceId:c.entry.data.service,currentEntryId:c.entry.data.id,currentActionAllowed:true}:{...v.ready.required_permission,subject:v.ready.authenticated_subject_id,logicalEntryId:c.entry.data.id},policy_snapshot_sha256:v.ready.policy_snapshot_sha256,qualification:'private-auth-scope-projection-only;not-business-resource-worker-or-command-custody',authority_effect:'none'});},
  disposeActor(h:CommerceAuthActorV1){actor(h).disposed=true;},disposeInput(h:CommerceAuthInputV1){input(h).disposed=true;},disposeEntry(h:CommerceAuthEntryV1){entry(h).disposed=true;},
  inspect(){current();return coreFreeze({kind:'original-commerce-entry-context-owner/v1-candidate',source_sha256:parent.source_sha256,profile_sha256:profileIdentity,native_component_sha256:nativeIdentity,source_entries:declarations.map(e=>e.id),physical_codec_members:files.map(f=>f.file),fixture_provider_only:true,qualification:'actual-source/input/native-auth-context-component-only;not-registered-protected-application-join',authority_effect:'none'});},assertCurrent:current,dispose(){disposed=true;},
 });registered.set(owner,{current,actors,native,codecs});current();return owner;
}
