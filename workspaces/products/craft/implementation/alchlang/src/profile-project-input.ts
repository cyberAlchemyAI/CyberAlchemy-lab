import {parseDeclarativeSource} from './declarative-profile.js';
import {deriveOntology} from './derived-ontology.js';
import {parseServiceSource} from './service-profile.js';
import {digest} from './domainspec-profile.js';
import type {DomainSpecCompiler} from './domainspec-cli.js';

/** Trusted adapter; backend is the registered Craft constructor, never package code.
 * Open questions: docs/PROFILE-GENERATION.md (PE20), PE05 prepared graph ownership. */
export interface ProfileBusinessBackend {assertProfileBusinessInputCurrent(input:unknown):void}
export interface ProfileTechnicalSelection {
 readonly intent_id:string;readonly route:string;readonly method:'POST';readonly request_bytes:number;readonly timeout_ms:number;
 readonly read_timeout_ms:number;readonly read_max_bytes:number;readonly read_credentials:'none'|'bearer';
 readonly success_status:number;readonly rejection_status:number;
 readonly origin:Readonly<{source:string;selector:string;sha256:string}>;
}
export interface LoweredProfileSources {
 readonly service:string;readonly files:Readonly<Record<string,string>>;
 readonly entries:readonly Readonly<{id:string;intent_id:string;source:string;route:string;access:'public';environment:readonly string[]}>[];
 readonly origins:readonly Readonly<{artifact:string;business_source:string;business_selector:string;profile_source:string;profile_rule:string;profile_sha256:string;configuration_selector?:string}>[];
 readonly functions:readonly Readonly<{source:string;parsed:ReturnType<typeof parseDeclarativeSource>;compiled:ReturnType<DomainSpecCompiler['compileDeclarativeFunction']>;ontology:ReturnType<typeof deriveOntology>}>[];
 readonly source_sha256:string;
}
const loweredStates=new WeakMap<object,{input:unknown;backend:ProfileBusinessBackend;fingerprint:string}>();
export function assertLoweredProfileSourcesCurrent(value:LoweredProfileSources):void {const state=loweredStates.get(value);if(!state||digest(JSON.stringify(value))!==state.fingerprint)throw Error('PROFILE_LOWERED_SOURCES_UNREGISTERED_OR_CHANGED');state.backend.assertProfileBusinessInputCurrent(state.input);}
const failure=(code:string,detail:string):never=>{throw Error(code+': '+detail);};
const slots=(id:string)=>'DEPENDENCY_'+id.toUpperCase().replace(/[^A-Z0-9_]/g,'_');
export function deriveProfileSources(input:unknown,backend:ProfileBusinessBackend,compiler:DomainSpecCompiler,selections:readonly ProfileTechnicalSelection[]):LoweredProfileSources {
 backend.assertProfileBusinessInputCurrent(input);const prepared=input as any,project=prepared.project;
 if(selections.length!==project.public_intents.length||new Set(selections.map(s=>s.intent_id)).size!==selections.length)failure('PROFILE_ENTRY_SELECTION','exactly one selection per authored public intent required');
 const files:Record<string,string>=Object.create(null),entries:any[]=[],origins:any[]=[],functions:any[]=[];const routes=new Set<string>(),usedSlots=new Map<string,string>();
 for(const [index,intent] of project.public_intents.entries()){
  const technical=selections.find(s=>s.intent_id===intent.id);if(!technical)failure('PROFILE_ENTRY_SELECTION',intent.id);
  if(intent.access.kind!=='public')failure('PROFILE_AUTH_POLICY_UNSUPPORTED','no registered authorization adapter for required policy '+intent.id);
  if(technical!.method!=='POST'||!/^\/[A-Za-z0-9_/-]+$/.test(technical!.route)||technical!.route.includes('..')||routes.has(technical!.route))failure('PROFILE_ROUTE_CONFLICT',intent.id);routes.add(technical!.route);
  for(const key of ['request_bytes','timeout_ms','read_timeout_ms','read_max_bytes'] as const)if(!Number.isSafeInteger(technical![key])||technical![key]<1||technical![key]>16777216)failure('PROFILE_TECHNICAL_LIMIT',key);
  for(const status of [technical!.success_status,technical!.rejection_status])if(!Number.isInteger(status)||status<200||status>599)failure('PROFILE_TECHNICAL_STATUS',intent.id);
  if(!['none','bearer'].includes(technical!.read_credentials)||!technical!.origin||!/^\w[\w.-]*$/.test(technical!.origin.selector)||!/^[a-f0-9]{64}$/.test(technical!.origin.sha256))failure('PROFILE_TECHNICAL_ORIGIN',intent.id);
  const business=prepared.sources[intent.source] as string;if(typeof business!=='string')failure('PROFILE_BUSINESS_SOURCE_REQUIRED',intent.id);
  if(/^(profile|endpoint|service|integration|import|native|execution|interpretation)\b/m.test(business))failure('PROFILE_TECHNICAL_SOURCE_FORBIDDEN',intent.source);
  let source=business.replace(/^(domain .*\n)/m,'$1profile declarative-function-v1\n');
  const environment:string[]=[];const integrations:string[]=[];
  for(const read of project.external_reads.filter((r:any)=>r.source===intent.source)){
   const wire=prepared.wire.find((w:any)=>w.intent_id===read.id&&w.source===read.source);if(!wire)failure('PROFILE_WIRE_CONTRACT_REQUIRED',read.id);
   const slot=slots(read.id);if(usedSlots.has(slot)&&usedSlots.get(slot)!==read.id)failure('PROFILE_ENVIRONMENT_SLOT_CONFLICT',read.id);usedSlots.set(slot,read.id);environment.push(slot+'_URL');if(technical!.read_credentials==='bearer')environment.push(slot+'_TOKEN');
   // The runtime read adapter validates/project-renames the exact wire contract;
   // this compiler carrier receives only the authored dependency schema.
   const query=Object.entries(read.request_fields).map(([key,value])=>{if(!/^[A-Za-z][A-Za-z0-9_]*$/.test(key)||typeof value!=='string'||!/^input\.[A-Za-z][A-Za-z0-9_]*$/.test(value))failure('PROFILE_READ_REQUEST_FIELD',read.id);return `  query ${key} ${value}\n`;}).join('');
   integrations.push(`integration ${read.id}:\n  transport http-get\n  url-env ${slot}_URL\n${technical!.read_credentials==='bearer'?`  secret-env ${slot}_TOKEN\n`:''}${query}  output ${read.output_ref}\n  timeout-ms ${technical!.read_timeout_ms}\n  max-bytes ${technical!.read_max_bytes}\n`);
   origins.push({artifact:`functions/entry${index}.alch`,business_source:intent.source,business_selector:'external-read:'+read.id,profile_source:technical!.origin.source,profile_rule:technical!.origin.selector,profile_sha256:technical!.origin.sha256,configuration_selector:'binding:'+wire.intent_id});
  }
  // Append after business declarations; parser resolves all bindings as one checked contract.
  source+='\n'+integrations.join('\n');
  source+=`\nendpoint Entry${index}:\n  target node-http\n  runtime node>=26.8.1\n  method POST\n  path ${JSON.stringify(technical!.route)}\n  input ${intent.input_ref}\n  output ${intent.output_ref}\n  result ${intent.result_ref}\n  auth-env INTERNAL_COMPATIBILITY_AUTH\n  max-bytes ${technical!.request_bytes}\n  timeout-ms ${technical!.timeout_ms}\n  error-status 422\n${intent.outcomes.map((o:any)=>`  status ${o.code} ${o.kind==='success'?technical!.success_status:technical!.rejection_status}\n`).join('')}  error FUNCTION_ENV_REQUIRED 503\n  error FUNCTION_INTEGRATION_TIMEOUT 504\n  error FUNCTION_INTEGRATION_STATUS 502\n  error FUNCTION_INTEGRATION_SCHEMA 502\n  error FUNCTION_INTEGRATION_FAILED 502\n  error FUNCTION_INTEGRATION_LIMIT 502\n  error FUNCTION_OUTPUT_SCHEMA 500\n`;
  const parsed=parseDeclarativeSource(source),compiled=compiler.compileDeclarativeFunction(parsed.contract),name=`functions/entry${index}.alch`;
  // Wire projection must cover exactly the authored fields with compatible types/bounds.
  for(const read of project.external_reads.filter((r:any)=>r.source===intent.source)){
   const wire=prepared.wire.find((w:any)=>w.intent_id===read.id&&w.source===read.source),expected=parsed.model.schemas[read.output_ref];
   if(Object.keys(expected).sort().join(',')!==Object.keys(wire.correspondence).sort().join(','))failure('PROFILE_WIRE_CORRESPONDENCE',read.id);
   for(const [target,remote] of Object.entries(wire.correspondence)){const domainField=expected[target],wireField=wire.wire_schema.fields[remote as string];if(!wireField||domainField.type!==wireField.type)failure('PROFILE_WIRE_VALUE_TYPE',read.id+'.'+target);for(const key of ['min','max','const','pattern'])if(domainField[key]!==undefined&&domainField[key]!==wireField[key])failure('PROFILE_BUSINESS_CONSTRAINT_CONFLICT',read.id+'.'+target+'.'+key);}
  }
  const status=parsed.model.schemas[intent.output_ref]?.status;
  for(const outcome of intent.outcomes){if(!status||status.const!==undefined&&status.const!==outcome.code||status.pattern&&!new RegExp(status.pattern).test(outcome.code))failure('PROFILE_OUTCOME_UNKNOWN',intent.id);}
  files[name]=source;entries.push(Object.freeze({id:`Entry${index}`,intent_id:intent.id,source:name,route:technical!.route,access:'public',environment:Object.freeze(environment)}));
  functions.push(Object.freeze({source:name,parsed,compiled,ontology:deriveOntology(parsed,compiled.trace,name)}));origins.push({artifact:name,business_source:intent.source,business_selector:'public-intent:'+intent.id,profile_source:technical!.origin.source,profile_rule:technical!.origin.selector,profile_sha256:technical!.origin.sha256});
 }
 const service=`domain ${project.id}\nprofile service-v1\nowner profile-engine\n${entries.map((e,i)=>`import Function${i} from ${JSON.stringify('./'+e.source)}`).join('\n')}\n\nservice GeneratedService:\n  meaning "Derived entry assembly from explicit business intents."\n\n${entries.map((e,i)=>`entry ${e.id}:\n  function Function${i}\n  meaning ${JSON.stringify('Expose authored intent '+e.intent_id)}\n`).join('\n')}`;
 parseServiceSource(service);files['service.alch']=service;backend.assertProfileBusinessInputCurrent(input);
 const result=Object.freeze({service,files:Object.freeze(files),entries:Object.freeze(entries),origins:Object.freeze(origins.map(o=>Object.freeze(o))),functions:Object.freeze(functions),source_sha256:prepared.source_sha256});loweredStates.set(result,{input,backend,fingerprint:digest(JSON.stringify(result))});return result;
}
