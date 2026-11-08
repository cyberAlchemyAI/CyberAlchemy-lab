import {captureJson,dataDigest,sha256,reject,type Json,type ProfileProject,type Origin} from './contracts.js';
import {assertProfileSnapshotCurrent,type ProfileSnapshot,type ProfileSnapshotV2} from './loader.js';
import type {ProfileProjectV2} from './contracts-v2.js';

/** Closed business/wire input preparation, never generation or remote access.
 * Open questions: docs/PROFILE-AUTHORING.md. */
export interface BusinessSelector {readonly source:string;readonly selector:string;readonly line:number;readonly text:string;readonly sha256:string}
export interface WireField {readonly type:'identifier'|'string'|'integer'|'boolean';readonly min?:number;readonly max?:number;readonly const?:Json;readonly pattern?:string}
export interface WireBinding {readonly intent_id:string;readonly source:string;readonly operation:Readonly<{kind:'read';method:'GET';location_ref:string}>;readonly wire_schema:Readonly<{id:string;version:string;fields:Readonly<Record<string,WireField>>}>;readonly wire_schema_sha256:string;readonly correspondence:Readonly<Record<string,string>>;readonly missing_fields:'reject';readonly extra_fields:'reject'}
export interface BusinessInput {readonly project:ProfileProject|ProfileProjectV2;readonly sources:Readonly<Record<string,string>>;readonly selectors:readonly BusinessSelector[];readonly wire:readonly WireBinding[];readonly source_sha256:string}
const inputs=new WeakMap<object,ProfileSnapshot|ProfileSnapshotV2>();
const ident=/^[A-Za-z][A-Za-z0-9_-]{0,127}$/;
function record(v:unknown,fields:readonly string[],required=fields):Record<string,any>{if(!v||typeof v!=='object'||Array.isArray(v))reject('PROFILE_WIRE_SHAPE','/','record required');const r=v as Record<string,any>;if(Object.keys(r).some(k=>!fields.includes(k))||required.some(k=>!Object.hasOwn(r,k)))reject('PROFILE_WIRE_SHAPE','/','closed wire fields required');return r;}
export function prepareProfileBusinessInput(snapshot:ProfileSnapshot|ProfileSnapshotV2):BusinessInput {
 assertProfileSnapshotCurrent(snapshot);const selectors:BusinessSelector[]=[],sources:Record<string,string>=Object.create(null);
 for(const name of snapshot.project.domain_sources){const text=snapshot.sources[name]!.text!;sources[name]=text;let current:string|undefined;
  for(const [index,line] of text.split('\n').entries()){
   const stripped=line.trim();if(!stripped||stripped.startsWith('#'))continue;
   if(!line.startsWith(' ')){
    if(/^(profile|endpoint|service|integration|import|native|execution|interpretation)\b/.test(line))reject('PROFILE_TECHNICAL_SOURCE_FORBIDDEN',`${name}:${index+1}`,'business sources cannot author technical carriers');
    const declaration=/^(entity|calculation|schema|rule|mapping|result|policy)\s+([A-Za-z][A-Za-z0-9_]*)\s*:/.exec(line);
    if(declaration){current=declaration[1]+':'+declaration[2];if(selectors.some(s=>s.source===name&&s.selector===current))reject('PROFILE_BUSINESS_SELECTOR_DUPLICATE',current,'one business declaration required');selectors.push(Object.freeze({source:name,selector:current,line:index+1,text:line,sha256:sha256(text)}));}
    else if(!/^(domain|owner|logic)\s/.test(line))reject('PROFILE_BUSINESS_DECLARATION_UNSUPPORTED',`${name}:${index+1}`,'unsupported required source declaration');
   }else{
    if(/^\s*(transport|url-env|secret-env|auth-env|runtime|method|path|timeout-ms|max-bytes|error-status)\b/.test(line))reject('PROFILE_TECHNICAL_SOURCE_FORBIDDEN',`${name}:${index+1}`,'technical clause forbidden');
    if(current)selectors.push(Object.freeze({source:name,selector:current+'#clause:'+(index+1),line:index+1,text:line,sha256:sha256(text)}));
   }
  }
 }
 const has=(source:string,selector:string)=>selectors.some(s=>s.source===source&&s.selector===selector);
 const meanings=new Set<string>();for(const intent of snapshot.project.public_intents){const key=intent.source+'#'+intent.result_ref;if(meanings.has(key))reject('PROFILE_PUBLIC_INTENT_ALIAS',intent.id,'two aliases do not establish independent public intents');meanings.add(key);for(const [kind,ref] of [['result',intent.result_ref],['schema',intent.input_ref],['schema',intent.output_ref]])if(!has(intent.source,kind+':'+ref))reject('PROFILE_PUBLIC_INTENT_UNKNOWN_REF',intent.id,'intent must reach an authored schema/result');if(intent.access.kind==='policy'&&!has(intent.source,'policy:'+intent.access.policy_ref))reject('PROFILE_AUTH_POLICY_UNSUPPORTED',intent.id,'required business policy is unresolved');}
 for(const claim of snapshot.project.formal_claims)if(!has(claim.source,claim.selector))reject('PROFILE_CLAIM_UNKNOWN_REF',claim.id,'claim selector must be authored');
 const configuration=snapshot.project.integration_configuration;const data=record(captureJson(configuration===undefined?{schema_version:'craft.integration-configuration/v1',bindings:[]}:JSON.parse(snapshot.sources[configuration]!.text!)),['schema_version','bindings']);if(data.schema_version!=='craft.integration-configuration/v1'||!Array.isArray(data.bindings)||data.bindings.length>32)reject('PROFILE_WIRE_SHAPE','/','supported finite integration contract required');
 const bindings:WireBinding[]=[];const seen=new Set<string>();
 for(const raw of data.bindings){const row=record(raw,['intent_id','source','operation','wire_schema','wire_schema_sha256','correspondence','missing_fields','extra_fields']);if(typeof row.intent_id!=='string'||seen.has(row.source+'#'+row.intent_id))reject('PROFILE_WIRE_DUPLICATE','/bindings','one binding per read intent required');seen.add(row.source+'#'+row.intent_id);
  const intent=snapshot.project.external_reads.find(i=>i.id===row.intent_id&&i.source===row.source);if(!intent)reject('PROFILE_WIRE_INTENT_UNKNOWN',row.intent_id,'configuration cannot invent a dependency');
  const operation=record(row.operation,['kind','method','location_ref']);if(operation.kind!=='read'||operation.method!=='GET'||typeof operation.location_ref!=='string'||!ident.test(operation.location_ref))reject('PROFILE_WIRE_OPERATION_UNSUPPORTED',row.intent_id,'read-only GET and declarative location ref required');
  const schema=record(row.wire_schema,['id','version','fields']);if(typeof schema.id!=='string'||!ident.test(schema.id)||typeof schema.version!=='string'||!/^\d+\.\d+\.\d+$/.test(schema.version))reject('PROFILE_WIRE_SCHEMA_ID',row.intent_id,'schema identity/version required');
  const fields=record(schema.fields,Object.keys(schema.fields??{}));if(!Object.keys(fields).length||Object.keys(fields).length>64)reject('PROFILE_WIRE_SCHEMA_LIMIT',row.intent_id,'bounded nonempty wire fields required');
  for(const [name,rawField] of Object.entries(fields)){if(!ident.test(name))reject('PROFILE_WIRE_FIELD',name,'wire field identifier required');const field=record(rawField,['type','min','max','const','pattern'],['type']);if(!['identifier','string','integer','boolean'].includes(field.type))reject('PROFILE_WIRE_FIELD_TYPE',name,'supported scalar wire type required');for(const bound of ['min','max'])if(field[bound]!==undefined&&(!Number.isSafeInteger(field[bound])||field[bound]<0))reject('PROFILE_WIRE_FIELD_BOUND',name,'nonnegative integer bounds required');if(field.min!==undefined&&field.max!==undefined&&field.min>field.max)reject('PROFILE_WIRE_FIELD_BOUND',name,'ordered bounds required');if(field.pattern!==undefined&&(typeof field.pattern!=='string'||field.pattern.length>512))reject('PROFILE_WIRE_FIELD_PATTERN',name,'bounded declared pattern required');}
  if(dataDigest(schema)!==row.wire_schema_sha256)reject('PROFILE_WIRE_SCHEMA_DIGEST',row.intent_id,'wire schema bytes/meaning differ from pin');
  const correspondence=record(row.correspondence,Object.keys(row.correspondence??{}));if(Object.values(correspondence).some(v=>typeof v!=='string'||!Object.hasOwn(fields,v))||new Set(Object.values(correspondence)).size!==Object.keys(correspondence).length)reject('PROFILE_WIRE_CORRESPONDENCE',row.intent_id,'typed field projection/rename only; no code or transformations');
  if(row.missing_fields!=='reject'||row.extra_fields!=='reject')reject('PROFILE_WIRE_FIELD_POLICY',row.intent_id,'missing and extra wire fields must reject');
  if(!has(intent.source,'schema:'+intent.output_ref))reject('PROFILE_WIRE_OUTPUT_UNKNOWN',row.intent_id,'dependency output schema must be authored');bindings.push(raw as WireBinding);
 }
 for(const intent of snapshot.project.external_reads)if(!seen.has(intent.source+'#'+intent.id))reject('PROFILE_WIRE_CONTRACT_REQUIRED',intent.id,'missing exact wire configuration');
 const input=Object.freeze({project:snapshot.project,sources:Object.freeze(sources),selectors:Object.freeze(selectors),wire:Object.freeze(bindings),source_sha256:snapshot.lock.source_sha256});inputs.set(input,snapshot);return input;
}
export function assertProfileBusinessInputCurrent(input:BusinessInput):void {const snapshot=inputs.get(input);if(!snapshot)reject('PROFILE_BUSINESS_INPUT_UNREGISTERED','/','prepare exact source input in this process');assertProfileSnapshotCurrent(snapshot);}
