/** Original generated read -> retained Auth/source observation. Direct apps can
 * consume another application's Query without pretending to be an agent tool.
 * No copied ACL, SQL interpreter or new storage owner. Open Questions:
 * docs/GENERIC-CAPABILITIES.md#open-questions. */
import {types} from 'node:util';
import {pinCoreImplementation,withCorePhysicalIdentityPhase} from '../commerce/commerce-core-physical.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {dataDigest} from '../profile-engine/contracts.js';
import {requireGenericCapabilityRuntimeBinding} from './execution-session.js';
import type {GenericCompositionHandle} from './public-sdk.js';
import type {GenericApplicationRuntime} from './invocation-owner.js';
import type {GenericFixtureActor,GenericReadyFrame} from './entry-authorization.js';
const ext=import.meta.url.endsWith('.ts')?'.ts':'.js',pin=pinCoreImplementation(import.meta.url,['execution-session'+ext,'entry-authorization'+ext,'sqlite-repository'+ext]);
const at={path:'generic-query-observation',start:0,end:0};
export interface GenericQueryObservation {readonly kind:'original-generated-query-observation/v1'}
export function createGenericQueryObservationOwner(composition:unknown,handle:GenericCompositionHandle,runtime:GenericApplicationRuntime){
 const original=requireGenericCapabilityRuntimeBinding(runtime,composition,handle),{plans,application,authorization}=original;
 let closed=false;const current=()=>{pin.assertCurrent();if(closed)fail('DisposedOwner',at,'query observation owner closed');original.assertCurrent();};
 type Principal=ReturnType<typeof authorization.capabilityPrincipal>;
 type Row={actor:GenericFixtureActor;entry:ReturnType<typeof runtime.entry>;input:Uint8Array;canonical:string;snapshot:object;frame:GenericReadyFrame;authSource:object;principal:Principal;result:any;deadline:number;retired:boolean};
 const rows=new WeakMap<object,Row>(),live=new Set<Row>();
 const row=(h:GenericQueryObservation)=>{current();const r=h&&typeof h==='object'?rows.get(h):undefined;if(!r||r.retired)fail('ForeignOwner',at,'original live same-owner Query observation required');if(Date.now()>=r.deadline)fail('StaleOwner',at,'Query observation expired');authorization.assertFrame(r.frame,r.entry,r.canonical);authorization.assertFrameSource(r.authSource,r.frame,r.entry);original.assertSnapshot(r.snapshot);return r;};
 const fresh=async(actor:GenericFixtureActor,entry:ReturnType<typeof runtime.entry>,canonical:string,deadline:number)=>{current();if(Date.now()>=deadline)fail('StaleOwner',at,'Query observation deadline');const granted=await authorization.authorize(actor,entry,canonical,'child-auth');current();if(!granted.ok)fail('ForeignOwner',at,'current original Query grant required');const ready=await authorization.consume(granted.value);current();if(!ready.ok)fail('ForeignOwner',at,'current original Query READY required');try{if(Date.now()>=deadline)fail('StaleOwner',at,'Query observation deadline');return {frame:ready.value,principal:authorization.capabilityPrincipal(ready.value,entry),authSource:authorization.captureFrameSource(ready.value,entry)};}catch(error){authorization.retire(ready.value);throw error;}};
 const copy=(wire:Uint8Array)=>{if(types.isProxy(wire)||!types.isUint8Array(wire))fail('InvalidContract',at,'original unshared Query input bytes');const p=Object.getPrototypeOf(Uint8Array.prototype),get=(name:string)=>Object.getOwnPropertyDescriptor(p,name)!.get!.call(wire),length=get('byteLength'),buffer=get('buffer');if(types.isSharedArrayBuffer(buffer)||length>1048576)fail('ResourceLimit',at,'bounded unshared Query input');return new Uint8Array(new Uint8Array(buffer,get('byteOffset'),length));};
 const retire=(r:Row)=>{if(r.retired)return;r.retired=true;authorization.retire(r.frame);live.delete(r);};
 const owner=Object.freeze({
  async read(actor:GenericFixtureActor,entryId:string,wire:Uint8Array,settings:{deadline_ms:number}):Promise<GenericQueryObservation>{
   current();if(live.size>=256)fail('ResourceLimit',at,'at most256 live Query observations per owner');if(!settings||Object.keys(settings).join(',')!=='deadline_ms'||!Number.isSafeInteger(settings.deadline_ms)||settings.deadline_ms<=Date.now()||settings.deadline_ms-Date.now()>3600000)fail('InvalidContract',at,'explicit Query observation deadline within one hour');
   const entry=runtime.entry(entryId),target=plans.inspectEntry(entry);plans.assertChild(entry,application);if(target.target_role!=='Query')fail('UnsupportedCapability',at,'only an actual checked read-only Query Entry');
   const input=copy(wire),prepared=runtime.prepareInput(entry,input),canonical=runtime.inspectPrepared(prepared).canonical_input_sha256;let frame:GenericReadyFrame|undefined;
   try{const ready=await fresh(actor,entry,canonical,settings.deadline_ms);frame=ready.frame;const grant=await runtime.authorize(actor,prepared);current();if(!grant.ok)fail('ForeignOwner',at,'actual original Query invocation grant');const transfer=await runtime.consume(grant.value,prepared);current();if(!transfer.ok)fail('ForeignOwner',at,'actual original Query invocation READY');const result=await runtime.execute(transfer.value);current();if(!result.ok||result.outcome.kind!=='Returned')fail('InvalidContract',at,'Query must return its checked observation');const snapshot=original.captureQuerySnapshot(prepared);original.assertSnapshot(snapshot);authorization.assertFrame(frame,entry,canonical);if(!result.ok||result.outcome.kind!=='Returned')fail('InvalidContract',at,'Query must return its checked observation');if(Date.now()>=settings.deadline_ms)fail('StaleOwner',at,'Query observation deadline');
    const lease=Object.freeze({kind:'original-generated-query-observation/v1' as const}),r:Row={actor,entry,input,canonical,snapshot,frame,authSource:ready.authSource,principal:ready.principal,result,deadline:settings.deadline_ms,retired:false};rows.set(lease,r);live.add(r);frame=undefined;try{row(lease);return lease;}catch(error){retire(r);throw error;}
   }finally{if(frame)authorization.retire(frame);runtime.disposePrepared(prepared);}
  },
  // Only immutable implementation-file pins share this synchronous phase.
  // SQL snapshots, Auth source epochs and lease deadlines are still checked on
  // every call; all sampled physical identities are checked again at its exit.
  inspect(h:GenericQueryObservation){return withCorePhysicalIdentityPhase(()=>{const r=row(h),selected=plans.inspectEntry(r.entry);return coreFreeze({entry:selected.entry,query:selected.target,principal:r.principal,input_sha256:r.canonical,source_revision:original.assertSnapshot(r.snapshot),result:r.result,value:r.result.outcome.value,content_sha256:dataDigest(r.result.outcome.value),deadline_ms:r.deadline,authority_effect:'none' as const});});},
  assertCurrent(h:GenericQueryObservation){withCorePhysicalIdentityPhase(()=>{row(h);});},
  async refresh(h:GenericQueryObservation){const r=row(h);try{const freshGrant=await fresh(r.actor,r.entry,r.canonical,r.deadline);try{row(h);if(freshGrant.principal.actor!==r.principal.actor||freshGrant.principal.tenant!==r.principal.tenant)fail('ForeignOwner',at,'Query observation principal cannot change');authorization.retire(r.frame);r.frame=freshGrant.frame;r.authSource=freshGrant.authSource;r.principal=freshGrant.principal;return owner.inspect(h);}catch(error){authorization.retire(freshGrant.frame);throw error;}}catch(error){retire(r);throw error;}},
  retire(h:GenericQueryObservation){const r=h&&typeof h==='object'?rows.get(h):undefined;if(!r)fail('ForeignOwner',at,'original Query observation');retire(r);},
  close(){if(closed)return;for(const r of live)retire(r);closed=true;},
 });current();return owner;
}
