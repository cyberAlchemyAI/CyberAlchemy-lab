import {assertCompiledCompositionBoundary,type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,type CompiledProjectFields} from '../input/compiled-field-model.js';
import {decodeTypedMappingContract} from '../typed-backend/contracts.js';
import {decodeTypedInputMappingContract,TYPED_MAPPING_INPUTS_VERSION} from '../typed-backend/mapping-inputs.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {PROFILED_SOURCE_DIGESTS} from './profiled-project.js';
import {EXACT_UINT64_PROFILE} from './exact-uint64.js';
import {renderConfiguredMapping} from './configured-mapping-source.js';
import type {PlannedArtifact} from './contracts.js';

export const CONFIGURED_MAPPING_VERSION='domainspec.configured-mappings-selection/v1-candidate';
export const MAPPING_CONTRACT_SHA256='626f05cb4fe01ec0552e1c2c939abf712235ed84fee319ac38a81148e6449c73';
const CONFIGURATION_SHA256='9ac018e42080483f373219049b466d8a515cb3e7748181ea8e635b1162af8317';
export interface ConfiguredMappingSelection {
  readonly schema_version:typeof CONFIGURED_MAPPING_VERSION;
  readonly language:'typescript';
  readonly value_profile:typeof EXACT_UINT64_PROFILE;
  readonly boundary_sha256:string;
  readonly field_compilation_sha256:string;
  readonly module_root:string;
  readonly roots:readonly string[];
}
export interface MappingConfigurationSources {readonly configuration:string;readonly base:string;readonly typescript:string;readonly mapping_contract:string;}
const fail=(message:string):never=>{throw new Error('DS_CONFIGURED_MAPPING:'+message);};
const freeze=<T>(value:T):T=>{if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.values(value).forEach(freeze);Object.freeze(value);}return value;};
const reserved=new Set(('as async await break case catch class const continue crate debugger def default del do else enum except export extends false finally fn for from function global if impl import in interface is lambda let loop match mod move mut new nonlocal null package pass private protected pub public raise ref return self static struct super switch this throw trait true try type typeof unsafe use var void while with yield con prn aux nul '+Array.from({length:9},(_,i)=>`com${i+1} lpt${i+1}`).join(' ')).split(' '));
const portable=(s:string)=>/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(s)&&!reserved.has(s);
function keys(value:unknown,expected:readonly string[]):void{
  if(!value||typeof value!=='object'||Array.isArray(value)||![Object.prototype,null].includes(Object.getPrototypeOf(value)))fail('plain data object required');
  const d=Object.getOwnPropertyDescriptors(value);
  if(Reflect.ownKeys(d).length!==expected.length||Reflect.ownKeys(d).some(k=>typeof k!=='string'||!expected.includes(k))||Object.values(d).some(v=>!Object.hasOwn(v,'value')||!v.enumerable))fail('closed data object required');
}
function frozenLiteral(v:unknown):string{
  if(Array.isArray(v))return `Object.freeze([${v.map(frozenLiteral).join(',')}])`;
  if(v&&typeof v==='object')return `Object.freeze({${Object.entries(v).map(([k,x])=>`[${JSON.stringify(k)}]:${frozenLiteral(x)}`).join(',')}})`;
  return JSON.stringify(v);
}
/** Caller selects the checked field closure and the same graph's boundary.
 * Produces no writes, runtime adapter or new source admission.
 */
export function planConfiguredMappings(boundary:CompiledCompositionBoundary,fields:CompiledProjectFields,selection:ConfiguredMappingSelection,sources:MappingConfigurationSources){
  assertCompiledCompositionBoundary(boundary);assertCompiledProjectFields(fields);
  keys(selection,['schema_version','language','value_profile','boundary_sha256','field_compilation_sha256','module_root','roots']);
  keys(sources,['configuration','base','typescript','mapping_contract']);
  if(selection.schema_version!==CONFIGURED_MAPPING_VERSION||selection.language!=='typescript'||selection.value_profile!==EXACT_UINT64_PROFILE)fail('unsupported selection');
  if(selection.boundary_sha256!==boundary.boundary_sha256||selection.field_compilation_sha256!==fields.compilation_sha256||fields.certificate.graph_sha256!==boundary.certificate.graph_sha256)fail('stale or cross-graph selection');
  if(fields.selection.schema_version!==EXACT_PROJECT_FIELD_SELECTION_VERSION)fail('exact checked fields required');
  if(typeof selection.module_root!=='string'||!selection.module_root.split('/').every(portable))fail('unsafe module root');
  if(!Array.isArray(selection.roots)||Object.getPrototypeOf(selection.roots)!==Array.prototype)fail('plain roots required');
  const d:Record<string,PropertyDescriptor>=Object.getOwnPropertyDescriptors(selection.roots),length=d.length!.value;
  if(!Number.isSafeInteger(length)||length<1||Reflect.ownKeys(d).length!==length+1)fail('nonempty dense roots required');
  const roots:string[]=[];for(let i=0;i<length;i++){const v=d[String(i)];if(!v||!Object.hasOwn(v,'value')||!v.enumerable||typeof v.value!=='string')return fail('inert roots required');roots.push(v.value);}
  if(new Set(roots).size!==roots.length)fail('duplicate roots');roots.sort();
  const expected={configuration:CONFIGURATION_SHA256,...PROFILED_SOURCE_DIGESTS,mapping_contract:MAPPING_CONTRACT_SHA256};
  for(const key of Object.keys(expected) as (keyof typeof expected)[])if(typeof sources[key]!=='string'||sha256(sources[key])!==expected[key])fail('source drift:'+key);
  const config=JSON.parse(sources.configuration),cell=config.types.find((t:{kind:string})=>t.kind==='Mapping');
  if(cell?.role!=='application/mappings'||canonicalJson(cell.blocked_by)!=='["DSR-009","DSR-011","DSR-014"]')fail('unexpected Mapping configuration');
  const overlay=JSON.parse(sources.typescript).representation_overlays.find((o:{contract_id:string})=>o.contract_id==='mapping.profile-representation');
  const protocol=overlay?.candidate_protocols.find((p:{protocol_id:string})=>p.protocol_id==='typescript.bound-mapping/v1');
  if(protocol?.form_id!=='typescript.bound-mapping-function')fail('missing Mapping protocol');
  const artifacts:PlannedArtifact[]=[];
  const artifact=(relative_path:string,content:string)=>{const a={relative_path,content,size_bytes:Buffer.byteLength(content),sha256:sha256(content)};artifacts.push(a);return a;};
  const modules=roots.map(selector=>{
    const parts=selector.split(':');if(parts.length!==2||!parts.every(portable))fail('unsafe selector');
    const row=boundary.value_bindings.core_contracts.find(c=>c.owner.selector===selector);if(!row||row.kind!=='Mapping')return fail('typed Mapping required:'+selector);
    const contract=(row.contract as {schema_version?:string}).schema_version===TYPED_MAPPING_INPUTS_VERSION?decodeTypedInputMappingContract(row.contract):decodeTypedMappingContract(row.contract),rendered=renderConfiguredMapping(contract,fields.model);
    const [feature,node]=parts as [string,string],callable='mapping'+node.split('-').map(s=>s[0]!.toUpperCase()+s.slice(1)).join('');
    const relative_path=`${selection.module_root}/features/${feature}/src/${cell.role}/${node}.ts`,provider_path=relative_path.replace(/\.ts$/,'.provider.ts');
    const implementation=artifact(provider_path,rendered.content),provider_import=`./${node}.provider.js`;
    const descriptorBody={schema_version:'domainspec.generated-mapping-descriptor/v1-candidate',protocol_id:'typescript.bound-mapping/v1',selector,
      ontology_mapping:contract.ontology_mapping,source_schema:contract.schema_version,contract_sha256:sha256(canonicalJson(contract)),source:row.source,inputs:rendered.inputs,
      target:{selector:contract.target,kind:rendered.target_kind,fields:rendered.result_fields},total:contract.total,field_model_sha256:fields.model.model_sha256,
      value_profile:selection.value_profile,fields:contract.fields,default_semantics:contract.schema_version===TYPED_MAPPING_INPUTS_VERSION?'explicit-nullish-fallback':'absent-source-property-only',
      return_semantics:'field-projection-not-construction',effect_contract:'pure-explicit-values',dependency_contract:'declared-inputs-only',result_consumption:'complete',primary_callable_count:1,
      failures:['MAPPING_INPUT','MAPPING_REQUIRED_VALUE'],provider:{id:selector+'/typescript-exact/v1',sha256:implementation.sha256},authority_effect:'none'};
    const descriptor={...descriptorBody,descriptor_sha256:sha256(canonicalJson(descriptorBody))};
    artifact(relative_path,`import {map} from ${JSON.stringify(provider_import)};\nexport const ${callable}=Object.freeze(Object.assign(map,{descriptor:${frozenLiteral(descriptor)}}));\n`);
    return {selector,relative_path,provider_path,provider_import,callable,descriptor};
  });
  artifacts.sort((a,b)=>a.relative_path<b.relative_path?-1:1);
  const body={schema_version:'domainspec.configured-mappings-plan/v1-candidate' as const,selection:{...selection,roots},source_digests:expected,
    boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields.compilation_sha256,certificate:boundary.certificate,modules,artifacts,
    discharged_configuration_prerequisites:['DSR-009','DSR-011'],bounded_prerequisite_evidence:{'DSR-014':'explicit-typed-inputs-and-target-bindings-not-parent-completion'},authority_effect:'none' as const};
  return freeze({...body,plan_sha256:sha256(canonicalJson(body))});
}
