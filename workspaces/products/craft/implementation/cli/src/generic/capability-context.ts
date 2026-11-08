/** Bounded single-scope contexts and read-only tools on original runtime/Auth owners.
 * Tenant is the checked Entry access.scope; no general tenant mapping is implied.
 * Source access is limited to checked Query Entity sources and their fresh Entry grants.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions. */
import path from 'node:path';import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {captureJson,dataDigest} from '../profile-engine/contracts.js';
import {requireGenericCapabilityProjection,type GenericCompositionHandle} from './public-sdk.js';
import {requireGenericCapabilityRuntimeBinding} from './execution-session.js';
import type {GenericApplicationRuntime} from './invocation-owner.js';
import type {GenericFixtureActor} from './entry-authorization.js';
import type {ValueTypeV1} from '../commerce/commerce-data-v1.js';
import type {GenericContextDependencyV1,GenericSourceContextManifestV1} from './capability-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['capability-owner'+ext,'public-sdk'+ext,'entry-authorization'+ext,'execution-session'+ext,'sqlite-repository'+ext]);
const at={path:'generic-capability-context',start:0,end:0};
export interface GenericCapabilityContext {readonly kind:'original-capability-context/v1'}
export interface GenericBoundedSearchHandle {readonly kind:'original-bounded-search/v1'}
export function createGenericCapabilityContextOwner(composition:unknown,handle:GenericCompositionHandle,runtime:GenericApplicationRuntime){
 const binding=requireGenericCapabilityRuntimeBinding(runtime,composition,handle),projection=requireGenericCapabilityProjection(handle),{plans,application,authorization}=binding;
 const current=()=>{pin.assertCurrent();binding.assertCurrent();requireGenericCapabilityProjection(handle);};current();
 type Row={actor:GenericFixtureActor;root:ReturnType<typeof runtime.entry>;selected:typeof projection.bindings[number];tools:readonly string[];tenant:string;subject:string;grantsRevision:string;deadline:number;fence:number;cancelled:boolean;calls:number;maximum:number;dependencies:Map<string,GenericContextDependencyV1>;snapshots:object[];usedTools:Set<string>};
 const contexts=new WeakMap<object,Row>(),searches=new WeakMap<object,{context:GenericCapabilityContext;value:unknown;snapshot:object}>();let fence=0;
 const row=(h:GenericCapabilityContext)=>{const r=h&&typeof h==='object'?contexts.get(h):undefined;if(!r)fail('ForeignOwner',at,'original same-owner capability context required');current();if(r.cancelled||r.fence!==fence||Date.now()>=r.deadline)fail('StaleOwner',at,'cancelled, superseded or expired capability context');for(const snapshot of r.snapshots)binding.assertSnapshot(snapshot);return r;};
 async function fresh(h:GenericCapabilityContext,entry?:ReturnType<typeof runtime.entry>){const r=row(h),target=entry??r.root,canonical=dataDigest({binding:r.selected.id,fence:r.fence});const access=await authorization.authorize(r.actor,target,canonical,'child-auth');row(h);if(!access.ok)fail('ForeignOwner',at,'current capability root grant denied or unavailable');const ready=await authorization.consume(access.value);row(h);if(!ready.ok)fail('ForeignOwner',at,'current capability root READY required');try{const principal=authorization.capabilityPrincipal(ready.value,target);if(principal.tenant!==r.tenant||principal.actor!==r.subject)fail('ForeignOwner',at,'capability context cannot change tenant or principal');r.grantsRevision=principal.grants_revision;return principal;}finally{authorization.retire(ready.value);}}
 const owner=Object.freeze({
  async open(actor:GenericFixtureActor,entryId:string,bindingId:string,options:{deadline_ms:number;tool_names:readonly string[];max_tool_calls:number}):Promise<GenericCapabilityContext>{
   current();const opts=captureJson(options) as unknown as typeof options;if(!opts||Object.keys(opts).sort().join(',')!=='deadline_ms,max_tool_calls,tool_names'||!Number.isSafeInteger(opts.deadline_ms)||opts.deadline_ms<=Date.now()||!Number.isSafeInteger(opts.max_tool_calls)||!Array.isArray(opts.tool_names))fail('InvalidContract',at,'finite deadline and original run delegation required');
   const selected=projection.bindings.find(b=>b.id===bindingId);if(!selected||!['agent-run/v1','search/v1'].includes(selected.contract.kind))fail('UnsupportedCapability',at,'selected agent or search binding required');
   if(opts.deadline_ms-Date.now()>selected.bounds.deadline_ms||opts.max_tool_calls<0||opts.max_tool_calls>selected.bounds.max_tool_calls||new Set(opts.tool_names).size!==opts.tool_names.length||opts.tool_names.some(name=>!selected.tools.some(tool=>tool.name===name)))fail('InvalidContract',at,'delegation must narrow checked binding bounds/tools');
   const root=runtime.entry(entryId),target=plans.inspectEntry(root);plans.assertChild(root,application);if(selected.contract.kind==='search/v1'){if(target.target_role!=='Query'||plans.inspectQuery(plans.bindQuery(application,target.target)).source.entity!==selected.contract.search.collection)fail('ForeignOwner',at,'search source requires its exact collection Query Entry grant');}
   const canonical=dataDigest({binding:bindingId,fence:fence+1}),access=await authorization.authorize(actor,root,canonical,'child-auth');current();if(!access.ok)fail('ForeignOwner',at,'actual current root grant required');const ready=await authorization.consume(access.value);current();if(!ready.ok)fail('ForeignOwner',at,'actual final root READY required');
   try{const principal=authorization.capabilityPrincipal(ready.value,root);if(target.access.scope!==principal.tenant)fail('ForeignOwner',at,'checked single tenant scope required');const out=Object.freeze({kind:'original-capability-context/v1' as const});contexts.set(out,{actor,root,selected,tools:opts.tool_names,tenant:principal.tenant,subject:principal.actor,grantsRevision:principal.grants_revision,deadline:opts.deadline_ms,fence:++fence,cancelled:false,calls:0,maximum:opts.max_tool_calls,dependencies:new Map(),snapshots:[],usedTools:new Set()});row(out);return out;}finally{authorization.retire(ready.value);}
  },
  inspect(h:GenericCapabilityContext){const r=row(h),app=plans.inspectSourceApplication(application);return coreFreeze({schema_version:'craft.trusted-search-context/v1',tenant:r.tenant,actor:r.subject,source_scope:[...new Set(r.selected.tools.filter(t=>r.tools.includes(t.name)).map(t=>plans.inspectQuery(plans.bindQuery(application,t.query)).source.entity).concat(r.selected.contract.kind==='search/v1'?[r.selected.contract.search.collection]:[]))],grants_revision:r.grantsRevision,source_policy_revision:app.contract_sha256,fence:r.fence,deadline_ms:r.deadline,origin:'original-server-owner',authority_effect:'none'});},
  async invokeTool(h:GenericCapabilityContext,name:string,wire:Uint8Array){const r=row(h),tool=r.selected.tools.find(t=>t.name===name);if(!tool||!r.tools.includes(name)||++r.calls>r.maximum)fail('UnsupportedCapability',at,'tool outside original bounded run delegation');
   const entry=runtime.entry(tool.entry),target=plans.inspectEntry(entry),query=plans.inspectQuery(plans.bindQuery(application,tool.query));if(target.access.scope!==r.tenant||target.target!==query.query||target.target_role!=='Query')fail('ForeignOwner',at,'tool must preserve tenant and exact read-only source');
   await fresh(h);row(h);const prepared=runtime.prepareInput(entry,wire);try{
    const granted=await runtime.authorize(r.actor,prepared);row(h);if(!granted.ok)return granted;
    const transfer=await runtime.consume(granted.value,prepared);row(h);if(!transfer.ok)return transfer;
    const snapshot=binding.captureSnapshot(),result=await runtime.execute(transfer.value);row(h);binding.assertSnapshot(snapshot);await fresh(h);row(h);binding.assertSnapshot(snapshot);await fresh(h,entry);row(h);const snapshotRevision=binding.assertSnapshot(snapshot);
    r.usedTools.add(name);r.snapshots.push(snapshot);r.dependencies.set(query.source.entity,{source:query.source.entity,revision:'query-snapshot:'+snapshotRevision+':'+dataDigest(result),content_sha256:dataDigest({prior:r.dependencies.get(query.source.entity)?.content_sha256??null,result}),acl_revision:r.grantsRevision,policy_revision:plans.inspectSourceApplication(application).contract_sha256,role:'tool-result'});return result;
   }finally{runtime.disposePrepared(prepared);}
  },
  async prepareSearch(h:GenericCapabilityContext,request:unknown):Promise<GenericBoundedSearchHandle>{const r=row(h);if(r.selected.contract.kind!=='search/v1')fail('UnsupportedCapability',at,'selected bounded-search contract required');const spec=r.selected.contract.search,value=captureJson(request) as {text:string;top_k:number;filters:{field:string;operator:'eq'|'in';value:unknown}[]};
   if(!value||Object.keys(value).sort().join(',')!=='filters,text,top_k'||typeof value.text!=='string'||Buffer.byteLength(value.text)>r.selected.bounds.max_input_bytes||!Number.isSafeInteger(value.top_k)||value.top_k<1||value.top_k>spec.top_k||!Array.isArray(value.filters)||value.filters.length>spec.filter_fields.length)fail('InvalidContract',at,'closed bounded search request required');
   for(const filter of value.filters){if(!filter||Object.keys(filter).sort().join(',')!=='field,operator,value'||!spec.filter_fields.includes(filter.field)||!spec.filter_operators.includes(filter.operator))fail('UnsupportedCapability',at,'unsupported search filter shape');const values=filter.operator==='in'?filter.value:[filter.value];if(!Array.isArray(values)||values.length<1||values.length>100||values.some(v=>!isGenericCapabilityScalarOperand(r.selected.search_filter_codecs[filter.field]!,v)))fail('UnsupportedCapability',at,'bounded scalar eq/in operands required');}
   if(Buffer.byteLength(JSON.stringify(value))>r.selected.bounds.max_input_bytes||new Set(value.filters.map(v=>v.field)).size!==value.filters.length)fail('InvalidContract',at,'bounded unique scalar filters required');
   await fresh(h);row(h);const out=Object.freeze({kind:'original-bounded-search/v1' as const});searches.set(out,{context:h,snapshot:binding.captureSnapshot(),value:coreFreeze({request:value,search:spec,context:owner.inspect(h),authority_effect:'none'})});return out;
  },
  inspectSearch(h:GenericBoundedSearchHandle){const r=h&&typeof h==='object'?searches.get(h):undefined;if(!r)fail('ForeignOwner',at,'original same-owner search handle required');row(r.context);binding.assertSnapshot(r.snapshot);return r.value;},
  async assertRelease(h:GenericCapabilityContext){const r=row(h);await fresh(h);row(h);for(const name of r.usedTools){const tool=r.selected.tools.find(t=>t.name===name)!;await fresh(h,runtime.entry(tool.entry));row(h);}},
  manifest(h:GenericCapabilityContext):GenericSourceContextManifestV1{const r=row(h),dependencies=[...r.dependencies.values()];return coreFreeze({schema_version:'craft.source-context-manifest/v1',tenant:r.tenant,dependencies,context_sha256:dataDigest(dependencies),authority_effect:'none'});},
  assertCurrent(h:GenericCapabilityContext){row(h);},assertBinding(h:GenericCapabilityContext,id:string){if(row(h).selected.id!==id)fail('ForeignOwner',at,'context belongs to another checked capability binding');},cancel(h:GenericCapabilityContext){const r=row(h);r.cancelled=true;},
 });return owner;
}

/** Scalar wire validation shared with the selected, source-derived filter codecs. */
export function isGenericCapabilityScalarOperand(codec:ValueTypeV1,value:unknown):boolean {
 if(codec.kind==='scalar')return codec.name==='Bool'?typeof value==='boolean':typeof value==='string'&&/^(0|[1-9][0-9]{0,19})$/.test(value)&&BigInt(value)<=18446744073709551615n;
 if(codec.kind==='literal')return value===codec.value;
 if(codec.kind==='string')return typeof value==='string'&&value.isWellFormed()&&Buffer.byteLength(value)<=codec.max_bytes&&[...value].length<=codec.max_scalars;
 return false;
}
