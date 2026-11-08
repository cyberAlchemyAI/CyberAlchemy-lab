/** Source-stage projection only. Data cannot mint registered owner handles.
 * Open Questions: docs/COMMERCE-STAGE-API.md#open-questions. */
import path from 'node:path';
import {captureJson} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceChildren as children,coreSourceDescendants as descendants,coreSourceTokens as tokens,coreSourceText as text,coreSourceFail as fail,coreRelativePath,type CoreSourceNode} from './commerce-core-syntax.js';
import {createCoreValueTypes} from './commerce-core-types.js';
import {createCoreContextCatalog} from './commerce-core-context.js';
import {coreValueAstType,type CorePureSemantics} from './commerce-core-pure.js';
import type {CoreCommerceSourceInspection} from './commerce-core-source-owner.js';
import type {CoreCommerceSemanticInspection} from './commerce-core-semantic-owner.js';
import type {CoreCommerceDeclaration} from './commerce-core-reconstruction.js';
import type {ApplicationContractV1,ModuleContractV1,SourceIdentityV1,RoleSelectorV1,ValueSchemaV1,ValueTypeV1,ProfilePackageV1,ComputationLimitsV1} from './commerce-data-v1.js';
const words=(n:CoreSourceNode)=>tokens(n).filter(t=>!t.layout).map(t=>t.token);
export function coreCommerceValueSchema(pure:CorePureSemantics,root:ValueTypeV1):ValueSchemaV1 {
 const records=pure.value_declarations.filter(d=>d.role!=='Enum'),enums=pure.value_declarations.filter(d=>d.role==='Enum');
 if(records.length>64||enums.length>64||pure.source_refinements.length>64)fail('ResourceLimit',{path:'application.alch',start:0,end:0},'closed source value schema limits');
 return coreFreeze({schema_version:'craft.commerce-values/v1-candidate',records:records.map(d=>({name:d.name,role:d.role as 'Entity'|'ValueObject'|'Event',fields:Object.fromEntries(d.fields.map(f=>[f.name,coreValueAstType(f.type)])),invariants:pure.record_invariants.find(r=>r.record===d.name)!.invariants,event_version:d.event_version,entity:d.role==='Entity'?{identity:d.identity,unique:d.unique,immutable:d.immutable==='all'?d.fields.map(f=>f.name):d.immutable,version:d.fields.some(f=>f.name==='version'&&f.type.kind==='UInt64')?'version':null}:null})),enums:enums.map(d=>({name:d.name,variants:d.variants.map(v=>({name:v.name,wire:v.wire,fields:Object.fromEntries(v.fields.map(f=>[f.name,coreValueAstType(f.type)]))}))})),refinements:pure.source_refinements.map(r=>({name:r.name,carrier:{kind:'string',max_bytes:r.max_bytes,max_scalars:r.max_scalars},min_utf8_bytes:r.min_bytes,max_utf8_bytes:r.max_bytes,min_unicode_scalars:r.min_scalars,max_unicode_scalars:r.max_scalars,pattern:r.pattern,normalization:'none',equality:'exact-scalar-sequence'})),collection_predicates:pure.collection_predicates.map(p=>({type:coreValueAstType(p.type),rule:p.rule})),root});
}
export function projectCoreCommerceStageData(capture:CoreCommerceSourceInspection,semantic:CoreCommerceSemanticInspection):Readonly<{application:ApplicationContractV1;modules:readonly ModuleContractV1[];limits:ComputationLimitsV1|null}> {
 const model=capture.reconstruction,types=createCoreValueTypes(model),catalog=createCoreContextCatalog(types,capture.files.filter(f=>f.path.endsWith('.json'))),app=[...types.declarations.values()].find(d=>d.interface_kind==='application-composition')!;
 const selector=(d:CoreCommerceDeclaration):RoleSelectorV1=>{if(!d.meta_type)fail('UnsupportedCapability',d.syntax,'claim target requires an existing meta-type declaration');return {module:d.module,role:d.meta_type,name:d.name};};
 const identity=(module:string):SourceIdentityV1=>{const m=types.modules.get(module);if(!m)fail('UnknownReference',app.syntax,'captured module required');return {module:m.module,version:1,artifact:{path:m.path,sha256:m.sha256,bytes:m.bytes}};};
 const modules:ModuleContractV1[]=model.modules.map(m=>{
  const grouped=new Map<string,string[]>();for(const i of m.imports){const end=i.target.lastIndexOf('.'),module=i.target.slice(0,end),name=i.target.slice(end+1);const prior=grouped.get(module)??[];prior.push(name);grouped.set(module,prior);}
  const claims=m.declarations.filter(d=>d.surface==='FormalClaim').map(d=>{
   const ts=words(d.syntax),raw=text(children(d.syntax,'reference')[0]!),relative=raw.includes('/')?raw:path.posix.join(path.posix.dirname(m.path),raw),file=capture.files.find(f=>f.path===relative);
   if(!coreRelativePath(relative)||!file)fail('UnknownReference',d.syntax,'claim source must be an original captured file');
   return {id:d.id,language:ts[ts.indexOf('language')+1] as 'lean4'|'smtlib2'|'alloy'|'tla-plus'|'souffle',source:{path:file.path,sha256:file.sha256,bytes:file.bytes},targets:children(children(d.syntax,'name-list')[0]!,'qualified-name').map(n=>selector(types.resolve(m.module,text(n),n)))};
  });
  return {schema_version:'alchlang.commerce-module/v1-candidate',source:identity(m.module),imports:[...grouped].map(([module,names])=>({module,names})),declarations:m.declarations.filter(d=>d.meta_type!==null).map(d=>({selector:selector(d),span:{path:d.syntax.path,start:d.syntax.start,end:d.syntax.end}})),entries:semantic.entries.filter(e=>m.declarations.some(d=>d.surface==='Entry'&&d.id===e.id)),formal_claims:claims,formal_claims_required:false,authority_effect:'none'};
 });
 const clauses=descendants(app.syntax,'application-clause');
 const single=(head:string,required=true)=>{const rows=clauses.filter(n=>words(n)[0]===head);if(rows.length>1||required&&!rows.length)fail('MissingMapping',app.syntax,'one source application '+head+' required');return rows[0]??null;};
 const implementation=single('implementation')!,mapping=types.resolve(app.module,text(children(implementation,'qualified-name')[0]!),implementation);
 if(mapping.surface!=='Mapping'||!types.modules.get(mapping.module)!.declarations.some(d=>d.interface_kind==='technical-profile-family'))fail('TypeMismatch',implementation,'implementation Mapping must belong to its captured technical profile module');
 single('parameters');const parameters=catalog.asset(app,['parameters']);if(!parameters)fail('MissingMapping',app.syntax,'captured application parameters required');
 const inert=captureJson(parameters.value) as unknown as ProfilePackageV1['parameters'];
 if(!inert||typeof inert!=='object'||Array.isArray(inert)||Object.keys(inert).length!==4||typeof inert.tablePrefix!=='string'||!/^[a-z][a-z0-9_]{0,15}$/.test(inert.tablePrefix)||inert.requestBytes!==4096||inert.responseBytes!==131072||inert.bodyTimeoutMs!==2000)fail('InvalidContract',app.syntax,'parameters must satisfy the existing closed ProfilePackage v5 contract');
 const entryCatalog=single('entry-catalog',false);let entries=semantic.entries.map(e=>e.id);if(entryCatalog){const module=text(children(entryCatalog,'qualified-name')[0]!);entries=model.modules.find(m=>m.module===module)!.declarations.filter(d=>d.surface==='Entry').map(d=>d.id);}
 const required_outputs=clauses.filter(n=>words(n)[0]==='required-output').map(n=>words(n)[1] as ApplicationContractV1['required_outputs'][number]);
 if(required_outputs.length!==5||new Set(required_outputs).size!==5)fail('MissingMapping',app.syntax,'shared application contract requires all five explicit output selections');
 if(model.services.length<1||model.services.length>16||entries.length<1||entries.length>64)fail('ResourceLimit',app.syntax,'shared application contract requires1..16services and1..64entries');
 const application:ApplicationContractV1={schema_version:'craft.commerce-application/v1-candidate',id:app.id,modules:model.modules.map(m=>identity(m.module)),services:model.services.map(s=>({id:s.service,module:s.module})),profile_source:identity(mapping.module),profile_mapping:mapping.id,parameters:inert,entries,required_outputs,formal_claims_required:false,authority_effect:'none'};
 const bounds=catalog.asset(app,['computation-bounds']);let limits:ComputationLimitsV1|null=null;
 if(bounds){const value=captureJson(bounds.value) as any;if(value.schema_version!=='craft.commerce-compute-bounds/v1-candidate'||value.computation?.required_schema_version!=='domainspec.iteration-expression/v2-candidate'||value.computation?.required_semantics_revision!=='ordered-metered-commerce-v2-candidate')fail('UnsupportedCapability',app.syntax,'captured computation ABI/version required');limits=value.computation.limits;const keys=['max_input_bytes','max_output_bytes','max_value_bytes','max_items','max_iterations','max_ast_nodes','max_ast_depth','max_call_depth','fuel'];if(!limits||typeof limits!=='object'||Array.isArray(limits)||Object.keys(limits).length!==keys.length||keys.some(k=>!Object.hasOwn(limits!,k)||!Number.isSafeInteger((limits as any)[k])||(limits as any)[k]<1||(limits as any)[k]>2147483647))fail('InvalidContract',app.syntax,'captured closed positive computation limits required');}
 return coreFreeze({application,modules,limits});
}
