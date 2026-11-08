/** Finite data/schema/statement derivation. Data alone is not a store owner.
 * Open Questions: docs/COMMERCE-SQLITE-FAMILY-V1.md#open-questions. */
import {dataDigest,canonicalJson,type Json} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {compilePersistenceCompositionV2} from '../system-integration/persistence-v2.js';
import {SYSTEM_INTEGRATION_DEFINITION_PACK_SHA256} from '../system-integration/kernel-v2.js';
import type {PersistenceMappingV1,PersistenceFieldMappingV1} from '../system-integration/persistence-v2-types.js';
import type {RecordDefinitionV1,ValueSchemaV1,ValueTypeV1,ReadPlanV1,FlowExprV1,ComputationLimitsV1,SourceIdentityV1} from './commerce-data-v1.js';
const where={path:'service-sqlite-family',start:0,end:0};
const hex=(value:string)=>Buffer.from(value).toString('hex');
export const sqliteIdentifierV1=(value:string)=>{if(typeof value!=='string'||!value.length||Buffer.byteLength(value)>2048||/[\u0000-\u001f]/.test(value))fail('InvalidContract',where,'bounded generated SQL identifier required');return '"'+value.replaceAll('"','""')+'"';};
export interface CommerceSqliteColumnV1 {readonly name:string;readonly sql_name:string;readonly type:ValueTypeV1;readonly nullable:boolean;readonly conversion:'canonical-source-value-json/v1-candidate'}
export interface CommerceSqliteTableV1 {readonly entity:string;readonly owner:string;readonly source:SourceIdentityV1;readonly physical_name:string;readonly columns:readonly CommerceSqliteColumnV1[];readonly keys:readonly (readonly string[])[];readonly record:RecordDefinitionV1;readonly create_sql:string;readonly indexes:readonly string[];readonly insert_sql:string;readonly select_key_sql:readonly string[]}
export interface CommerceSqliteQuerySlotV1 {readonly id:string;readonly expression:FlowExprV1;readonly type:ValueTypeV1;readonly origin:'parameter'|'private-context-scalar'|'literal'}
export interface CommerceSqliteQueryV1 {readonly id:string;readonly service:string;readonly plan:Extract<ReadPlanV1,{kind:'local'}>;readonly sql:string;readonly slots:readonly CommerceSqliteQuerySlotV1[];readonly residual:readonly FlowExprV1[];readonly source_aliases:readonly {readonly alias:string;readonly entity:string;readonly columns:readonly {readonly column:string;readonly result_name:string}[]}[];readonly qualification:'source-scoped-statement-data-only;original-native-query-and-context-owner-required'}
export interface CommerceSqliteServiceDataV1 {readonly schema_version:'craft.commerce-sqlite-service-schema/v1-candidate';readonly service:string;readonly prefix:string;readonly values:ValueSchemaV1;readonly limits:ComputationLimitsV1;readonly tables:readonly CommerceSqliteTableV1[];readonly queries:readonly CommerceSqliteQueryV1[];readonly migration_sql:string;readonly persistence:ReturnType<typeof compilePersistenceCompositionV2>;readonly schema_sha256:string;readonly native_runtime_qualified:false;readonly authority_effect:'none'}
function shape(t:ValueTypeV1,values:ValueSchemaV1):Pick<PersistenceFieldMappingV1,'logical_shape'|'storage_shape'|'collection_semantics'>{
 if(t.kind==='scalar'||t.kind==='string'||t.kind==='literal')return {logical_shape:'scalar',storage_shape:'scalar',collection_semantics:'not-applicable'};
 if(t.kind==='refinement'){if(!values.refinements.some(r=>r.name===t.name))fail('UnknownReference',where,'storage refinement absent');return {logical_shape:'value-object',storage_shape:'scalar',collection_semantics:'not-applicable'};}
 if(t.kind==='record'){if(!values.records.some(r=>r.name===t.name))fail('UnknownReference',where,'storage record absent');return {logical_shape:values.records.find(r=>r.name===t.name)!.role==='Entity'?'entity-reference':'value-object',storage_shape:'embedded',collection_semantics:'not-applicable'};}
 if(t.kind==='enum'||t.kind==='variant'){const e=values.enums.find(e=>e.name===(t.kind==='variant'?t.enum_name:t.name));if(!e)fail('UnknownReference',where,'storage enum absent');const simple=e.variants.every(v=>Object.keys(v.fields).length===0);return {logical_shape:simple?'enum':'sum',storage_shape:simple?'scalar':'embedded',collection_semantics:'not-applicable'};}
 if(t.kind==='optional'){if(t.element.kind==='optional')fail('UnsupportedCapability',where,'nested optional has no lossless selected canonical wire');shape(t.element,values);return {logical_shape:'optional',storage_shape:'nullable',collection_semantics:'not-applicable'};}
 if(t.kind==='list'){shape(t.element,values);return {logical_shape:'list',storage_shape:'array',collection_semantics:'ordered'};}
 return fail('UnsupportedCapability',where,'unimplemented storage shape');
}
function storageTree(type:ValueTypeV1,values:ValueSchemaV1,active=new Set<string>(),depth=0):void {
 if(depth>32)fail('ResourceLimit',where,'bounded storage type tree required');shape(type,values);
 if(type.kind==='list'||type.kind==='optional'){storageTree(type.element,values,active,depth+1);return;}
 if(type.kind==='record'||type.kind==='enum'||type.kind==='variant'){
  const name=type.kind==='variant'?type.enum_name:type.name;if(active.has(name))fail('UnsupportedCapability',where,'recursive selected storage representation unsupported');const next=new Set(active);next.add(name);
  if(type.kind==='record'){for(const t of Object.values(values.records.find(r=>r.name===name)!.fields))storageTree(t,values,next,depth+1);}
  else for(const v of values.enums.find(e=>e.name===name)!.variants){if(Object.hasOwn(v.fields,'kind'))fail('UnsupportedCapability',where,'algebraic payload cannot collide with canonical kind discriminator');for(const t of Object.values(v.fields))storageTree(t,values,next,depth+1);}
 }
}
export function deriveCommerceSqliteTableV1(record:RecordDefinitionV1,service:string,prefix:string,source:SourceIdentityV1,values:ValueSchemaV1,suffix?:string):CommerceSqliteTableV1 {
 if(record.role!=='Entity'||!record.entity||!record.entity.identity.length)fail('InvalidContract',where,'source-owned Entity with explicit identity required');
 const physical=prefix+service+'_'+(suffix??hex(record.name)),columns=Object.entries(record.fields).map(([name,type])=>{storageTree(type,values);return {name,sql_name:'f_'+hex(name),type,nullable:type.kind==='optional',conversion:'canonical-source-value-json/v1-candidate' as const};}),keys=[record.entity.identity,...record.entity.unique];
 for(const key of keys){
  if(!key.length||new Set(key).size!==key.length)fail('InvalidContract',where,'nonempty exact key required');
  for(const name of key){const f=columns.find(c=>c.name===name);if(!f||!['scalar','string','literal','refinement','enum'].includes(f.type.kind))fail('UnsupportedCapability',where,'selected key must be a closed scalar value, not optional/collection/record');const type=f.type;if(type.kind==='enum'){const enumName=type.name;if(values.enums.find(e=>e.name===enumName)!.variants.some(v=>Object.keys(v.fields).length))fail('UnsupportedCapability',where,'algebraic sum cannot become a scalar key');}}
 }

 const q=sqliteIdentifierV1,field=(name:string)=>q(columns.find(c=>c.name===name)!.sql_name),select=columns.map(c=>q(c.sql_name)+' AS '+q(c.name)).join(', '),indexes=record.entity.unique.map((key,i)=>'CREATE UNIQUE INDEX '+q(physical+'_unique_'+i)+' ON '+q(physical)+' ('+key.map(field).join(', ')+');');
 const definitions=columns.map(c=>q(c.sql_name)+' TEXT'+(c.nullable?'':' NOT NULL')+' CHECK ('+(c.nullable?q(c.sql_name)+' IS NULL OR ':'')+'json_valid('+q(c.sql_name)+'))');
 const create='CREATE TABLE '+q(physical)+' ('+definitions.join(', ')+', PRIMARY KEY ('+record.entity.identity.map(field).join(', ')+')) STRICT;';
 return coreFreeze({entity:record.name,owner:service,source,physical_name:physical,columns,keys,record,create_sql:create,indexes,insert_sql:'INSERT INTO '+q(physical)+' ('+columns.map(c=>q(c.sql_name)).join(', ')+') VALUES ('+columns.map(()=>'?').join(', ')+')',select_key_sql:keys.map(key=>'SELECT '+select+' FROM '+q(physical)+' WHERE '+key.map(name=>field(name)+' = ?').join(' AND ')+' LIMIT 2')});
}
export function deriveCommerceSqliteQueryV1(plan:Extract<ReadPlanV1,{kind:'local'}>,tables:readonly CommerceSqliteTableV1[],service:string):CommerceSqliteQueryV1 {
 if(plan.service!==service||plan.cross_service_tables!==false)fail('InvalidContract',where,'Query service must match original repository owner');
 const aliases=plan.sources.map((r,i)=>{const t=tables.find(t=>t.entity===r.entity);if(!t||t.owner!==service)fail('InvalidContract',where,'Query cannot read a foreign or absent table');return {source:r,table:t,sql:'r'+i};}),slots:CommerceSqliteQuerySlotV1[]=[],residual:FlowExprV1[]=[],q=sqliteIdentifierV1;
 const rowField=(e:FlowExprV1)=>{if(e.op!=='field'||e.value.op!=='var')return null;const root=e.value;const a=aliases.find(a=>a.source.binding===root.name),f=a?.table.columns.find(c=>c.name===e.field);return a&&f?{a,f}:null;};
 const dataOrigin=(e:FlowExprV1):CommerceSqliteQuerySlotV1['origin']|null=>{if(e.op==='literal')return 'literal';if(e.op==='var'&&plan.parameters.some(p=>p.name===e.name))return 'parameter';if(e.op==='field'&&e.value.op==='private_context'){const root=e.value;if(plan.contexts.some(c=>c.binding===root.binding&&c.source_type===root.source_type))return 'private-context-scalar';}return null;};
 const edges:{left:{alias:string;field:string};right:{alias:string;field:string}|null}[]=[];
 const equality=(e:FlowExprV1):string|null=>{
  if(e.op!=='binary'||e.operator!=='eq')return null;
  const a=rowField(e.left),b=rowField(e.right);if(a&&b){edges.push({left:{alias:a.a.sql,field:a.f.name},right:{alias:b.a.sql,field:b.f.name}},{left:{alias:b.a.sql,field:b.f.name},right:{alias:a.a.sql,field:a.f.name}});return q(a.a.sql)+'.'+q(a.f.sql_name)+' = '+q(b.a.sql)+'.'+q(b.f.sql_name);}
  const f=a??b,v=a?e.right:e.left,origin=dataOrigin(v);if(!f||!origin)return null;const id='s'+slots.length;edges.push({left:{alias:f.a.sql,field:f.f.name},right:null});slots.push({id,expression:v,type:f.f.type,origin});return q(f.a.sql)+'.'+q(f.f.sql_name)+' = ?';
 };
 const predicates:string[]=[];const retain=(e:FlowExprV1)=>{if(e.op==='binary'&&e.operator==='and'){retain(e.left);retain(e.right);}else{const sql=equality(e);if(sql)predicates.push(sql);else residual.push(e);}};
 for(const a of aliases)if(a.source.join)retain(a.source.join.expression);retain(plan.predicate.expression);
 // A source key is independently checked by Core. SQL conversion must also
 // preserve its explicit predicate; no broad scan silently replaces a key.
 const bounded=new Set<string>(),columns=new Map(aliases.map(a=>[a.sql,new Set<string>()]));let changed=true;while(changed){changed=false;for(const edge of edges)if(edge.right===null||bounded.has(edge.right.alias)){const set=columns.get(edge.left.alias)!;if(!set.has(edge.left.field)){set.add(edge.left.field);changed=true;}}for(const a of aliases)if(!bounded.has(a.sql)&&a.source.lookup_key.every(k=>columns.get(a.sql)!.has(k))){bounded.add(a.sql);changed=true;}}
 if(bounded.size!==aliases.length)fail('UnsupportedCapability',where,'every source lookup key needs an actual translated parameter/context/constant or already-keyed row predicate');
 const source_aliases=aliases.map(a=>({alias:a.source.binding,entity:a.table.entity,columns:a.table.columns.map(c=>({column:c.name,result_name:aliases.length===1?c.name:a.source.binding+'.'+c.name}))}));
 const select=aliases.flatMap((a,i)=>a.table.columns.map((c,j)=>q(a.sql)+'.'+q(c.sql_name)+' AS '+q(source_aliases[i]!.columns[j]!.result_name))).join(', '),from=aliases.map(a=>q(a.table.physical_name)+' AS '+q(a.sql)).join(' CROSS JOIN ');
 return coreFreeze({id:plan.query.module+'.'+plan.query.name,service,plan,sql:'SELECT '+select+' FROM '+from+' WHERE '+predicates.join(' AND ')+' LIMIT 4097',slots,residual,source_aliases,qualification:'source-scoped-statement-data-only;original-native-query-and-context-owner-required'});
}
export function deriveCommerceSqliteServiceV1(service:string,prefix:string,tables:readonly CommerceSqliteTableV1[],queries:readonly CommerceSqliteQueryV1[],values:ValueSchemaV1,limits:ComputationLimitsV1):CommerceSqliteServiceDataV1 {
 const id='commerce.'+service,ref=(kind:string)=>kind+':'+id,conversion=ref('conversion'),mappings:PersistenceMappingV1[]=tables.map(t=>{
  const model='physical-model:'+id+'.'+hex(t.entity),physical='physical:'+id+'.'+hex(t.entity)+'/',fields=t.columns.map(c=>({logical_property_ref:t.entity+'#'+c.name,physical_field_ref:physical+hex(c.name),...shape(c.type,values),conversion_ref:conversion}));
  return {mapping_id:'mapping:'+id+'.'+hex(t.entity),logical_subject_refs:[t.entity],physical_models:[{model_id:model,model_kind:'relational-table',physical_name:t.physical_name,version:'version:initial'}],identity_mappings:t.record.entity!.identity.map(name=>({logical_property_ref:t.entity+'#'+name,physical_field_ref:physical+hex(name),conversion_ref:conversion})),field_mappings:fields,relation_mappings:[],index_mappings:t.keys.map((key,i)=>({index_id:'index:'+id+'.'+hex(t.entity)+'.k'+i,model_ref:model,physical_name:i?t.physical_name+'_unique_'+(i-1):'sqlite_autoindex_'+t.physical_name+'_1',field_refs:key.map(n=>physical+hex(n)),unique:true,order:'unordered' as const})),conversion_rules:[{conversion_id:conversion,source_shape:'source-value-domain',target_shape:'canonical-json-text-or-outer-optional-sql-null',direction:'bidirectional',lossless:true,implementation_ref:'codec:commerce.canonical.source.values.v1'}],version:'version:initial',authority_effect:'none'};
 });
 const binding=(m:PersistenceMappingV1)=>({binding_id:'persistence:'+id+'.'+hex(m.logical_subject_refs[0]!),integration_binding_ref:ref('integration'),logical_subject_refs:m.logical_subject_refs,dependency_contract_ref:ref('contract'),adapter_ref:'adapter:commerce.sqlite.v1',resource_ref:ref('resource'),implementation_profile_ref:'profile:commerce.sqlite.v1',logical_physical_mapping_ref:m.mapping_id,evidence_boundary:'source-derived-repository-schema-only;actual-native-store-owner-required',authority_effect:'none'}),bindings=mappings.map(binding);
 const kernel={schema_version:'domainspec.integration-kernel/v2-candidate',kernel_id:ref('kernel'),definition_pack_sha256:SYSTEM_INTEGRATION_DEFINITION_PACK_SHA256,integration_bindings:[{binding_id:ref('integration'),concern:'persistence',direction:'bidirectional',logical_boundary_ref:ref('boundary'),contract_ref:ref('contract'),provider_realization_ref:ref('realization'),policy_refs:[],serialization_profile_ref:null,failure_mapping_ref:ref('failure'),evidence_boundary:'generated-data-only;not-native-runtime-observed',authority_effect:'none'}],provider_profiles:[{profile_id:'profile:commerce.sqlite.v1',concern:'persistence',provider_kind:'sqlite',capability_set:['service-owned-schema','exact-value-codec'],configuration_schema_ref:'schema:commerce.sqlite.family.v1',secret_slot_refs:[],compatibility_constraints:['source-owner-required'],authority_effect:'none'}],provider_realizations:[{realization_id:ref('realization'),provider_profile_ref:'profile:commerce.sqlite.v1',adapter_ref:'adapter:commerce.sqlite.v1',resource_ref:ref('resource'),configuration_ref:ref('configuration'),credential_binding_ref:null,deployment_ref:null,evidence_boundary:'generation-only;no-runtime-claim',runtime_observed:false,authority_effect:'none'}],serialization_profiles:[],failure_mappings:[{mapping_id:ref('failure'),boundary_ref:ref('boundary'),cases:[{provider_failure_matcher:'provider:unavailable',failure_outcome_ref:'outcome:unavailable',outcome_class:'unknown'}],unknown_failure_outcome_ref:'outcome:unavailable',continuation_owner_ref:ref('owner'),evidence_boundary:'source-query-actions-and-future-original-store-dispositions',authority_effect:'none'}],runtime_receipts:[],runtime_guarantees_observed:false,authority_effect:'none'};
 const persistence=compilePersistenceCompositionV2({schema_version:'domainspec.persistence-composition/v2-candidate',composition_id:ref('composition'),integration_kernel:kernel,persistence_bindings:bindings,persistence_mappings:mappings,transaction_guarantees:[],migrations:bindings.map(b=>({migration_id:'migration:'+id+'.'+hex(b.logical_subject_refs[0]!),persistence_binding_ref:b.binding_id,from_version:'version:empty',to_version:'version:initial',forward_steps:[{step_id:ref('step')+'.'+hex(b.logical_subject_refs[0]!),step_kind:'schema',operation_ref:ref('create')+'.'+hex(b.logical_subject_refs[0]!),reversible:false}],data_transform_refs:[],compatibility_window:'none',rollback_posture:'forward-only',rollback_step_refs:[],verification_refs:[ref('verification')+'.'+hex(b.logical_subject_refs[0]!)],authority_effect:'none'})),runtime_guarantees_observed:false,authority_effect:'none'});
 const migration_sql='BEGIN IMMEDIATE;\n'+tables.flatMap(t=>[t.create_sql,...t.indexes]).join('\n')+'\nCOMMIT;\n';
 const subject={schema_version:'craft.commerce-sqlite-service-schema/v1-candidate' as const,service,prefix,values,limits,tables,queries,migration_sql,persistence,native_runtime_qualified:false as const,authority_effect:'none' as const};return coreFreeze({...subject,schema_sha256:dataDigest(subject)});
}

/** Shared canonical tuple data codec; no repository or invocation custody. */
export function encodeSourceSqliteTypedTupleV1(entity:string,fields:readonly {readonly name:string;readonly type:ValueTypeV1;readonly cell:string}[],limit:number):Buffer {
 const bad=(code:string):never=>{throw Object.assign(new Error(code),{code});};
 if(!Number.isSafeInteger(limit)||limit<1||limit>524288||fields.length>4096)bad('StorageBound');
 const KEY_MAGIC=Buffer.from([0x43,0x4b,0x31,0]);
 const parts:Buffer[]=[KEY_MAGIC];let bytes=KEY_MAGIC.length;
 const number=(n:number)=>{if(!Number.isSafeInteger(n)||n<0||n>0xffffffff)bad('StorageBound');const b=Buffer.alloc(4);b.writeUInt32BE(n);parts.push(b);bytes+=4;};
 const text=(s:string)=>{if(typeof s!=='string')bad('StorageType');const b=Buffer.from(s,'utf8');if(b.toString('utf8')!==s)bad('StorageType');number(b.length);parts.push(b);bytes+=b.length;if(bytes>limit)bad('StorageBound');};
 text(entity);number(fields.length);
 for(const f of fields){text(f.name);text(canonicalJson(f.type as Json));text(f.cell);}
 if(bytes>limit)bad('StorageBound');return Buffer.concat(parts,bytes);
}
