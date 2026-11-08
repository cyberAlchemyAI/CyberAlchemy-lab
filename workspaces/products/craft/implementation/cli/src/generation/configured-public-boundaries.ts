import path from 'node:path';
import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCompiledCompositionBoundary,type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,type CompiledProjectFields} from '../input/compiled-field-model.js';
import {compilePublicMapping} from '../input/compiled-public-mapping.js';
import {assertInterfaceData,NAMED_INTERFACE_DEFINITION_SHA256} from '../typed-backend/interface.js';
import {isPublicMappingDefinitionSha256,PUBLIC_MAPPING_VERSION} from '../typed-backend/mapping-public.js';
import {renderNamedInterfaceSource} from './named-interface-source.js';
import {renderPublicMappingSource} from './public-mapping-source.js';
import {PROFILED_SOURCE_DIGESTS} from './profiled-project.js';
import {EXACT_UINT64_PROFILE} from './exact-uint64.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import type {PlannedArtifact} from './contracts.js';
import {MINIMAL_VALUE_CONTEXT_SHA256} from './reconciled-sources.js';
export const CONFIGURED_PUBLIC_BOUNDARIES_VERSION='domainspec.configured-public-boundaries-selection/v1-candidate';
export const PUBLIC_BOUNDARY_GENERATION_SHA256='686852a3615345f8ae2f66957d0b6c0ce825007b0e7c5d41492644b880aac0b9';
const CONFIGURATION_SHA256='9ac018e42080483f373219049b466d8a515cb3e7748181ea8e635b1162af8317';
export interface PublicBoundarySelection {readonly schema_version:typeof CONFIGURED_PUBLIC_BOUNDARIES_VERSION;readonly language:'typescript';readonly value_profile:typeof EXACT_UINT64_PROFILE;readonly module_root:string;readonly roots:readonly string[];}
export interface PublicBoundarySources {readonly configuration:string;readonly base:string;readonly typescript:string;readonly generation_contract:string;readonly public_mapping_contract:string;readonly interface_contract:string;}
const fail=(message:string):never=>{throw new TypeError('DS_PUBLIC_BOUNDARIES:'+message);};
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};
const keys=(v:unknown,names:readonly string[])=>{if(!v||typeof v!=='object'||Array.isArray(v)||canonicalJson(Object.keys(v).sort())!==canonicalJson([...names].sort()))fail('closed selection/source keys');};
const reserved=new Set(('as async await break case catch class const continue crate debugger def default del do else enum except export extends false finally fn for from function global if impl import in interface is lambda let loop match mod move mut new nonlocal null package pass private protected pub public raise ref return self static struct super switch this throw trait true try type typeof unsafe use var void while with yield con prn aux nul '+Array.from({length:9},(_,i)=>`com${i+1} lpt${i+1}`).join(' ')).split(' '));
const portable=(x:string)=>typeof x==='string'&&x.length<=128&&/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(x)?.[0]===x&&!reserved.has(x);
const pascal=(x:string)=>x.split('-').map(s=>s[0]!.toUpperCase()+s.slice(1)).join('');
const literal=(v:unknown):string=>Array.isArray(v)?'Object.freeze(['+v.map(literal).join(',')+'])':v&&typeof v==='object'?'Object.freeze({'+Object.entries(v).map(([k,x])=>'['+JSON.stringify(k)+']:'+literal(x)).join(',')+'})':JSON.stringify(v);
const leaf=(from:string,to:string)=>{const p=path.posix.relative(path.posix.dirname(from),to).replace(/\.ts$/,'.js');return p.startsWith('.')?p:'./'+p;};
/** Pure checked-snapshot planner. Artifact writing and CLI integration are later tasks. */
export function planConfiguredPublicBoundaries(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,fields:CompiledProjectFields|null,selection:PublicBoundarySelection,sources:PublicBoundarySources){
 assertCompiledProjectSnapshot(graph);assertCompiledCompositionBoundary(boundary);if(fields!==null)assertCompiledProjectFields(fields);
 assertInterfaceData(selection);assertInterfaceData(sources);keys(selection,['schema_version','language','value_profile','module_root','roots']);keys(sources,['configuration','base','typescript','generation_contract','public_mapping_contract','interface_contract']);
 if(selection.schema_version!==CONFIGURED_PUBLIC_BOUNDARIES_VERSION||selection.language!=='typescript'||selection.value_profile!==EXACT_UINT64_PROFILE)fail('unsupported selection');
 const certificate=createCompiledProjectCertificate(graph);
 if((fields!==null&&(fields.selection.schema_version!==EXACT_PROJECT_FIELD_SELECTION_VERSION||fields.certificate.graph_sha256!==certificate.graph_sha256))||boundary.certificate.graph_sha256!==certificate.graph_sha256)fail('same-graph exact fields required');
 if(typeof selection.module_root!=='string'||!selection.module_root.split('/').every(portable))fail('unsafe module root');
 if(!Array.isArray(selection.roots)||selection.roots.length<1||selection.roots.length>256||selection.roots.some(s=>typeof s!=='string'||s.split(':').length!==2||!s.split(':').every(portable))||new Set(selection.roots).size!==selection.roots.length)fail('unique portable roots required');
 const roots=[...selection.roots].sort();
 if(typeof sources.public_mapping_contract!=='string'||!isPublicMappingDefinitionSha256(sha256(sources.public_mapping_contract)))fail('source drift:public_mapping_contract');
 const expected={configuration:CONFIGURATION_SHA256,...PROFILED_SOURCE_DIGESTS,generation_contract:PUBLIC_BOUNDARY_GENERATION_SHA256,public_mapping_contract:sha256(sources.public_mapping_contract),interface_contract:NAMED_INTERFACE_DEFINITION_SHA256};
 for(const key of Object.keys(expected) as (keyof PublicBoundarySources)[])if(typeof sources[key]!=='string'||sha256(sources[key])!==expected[key])fail('source drift:'+key);
 const config=JSON.parse(sources.configuration),profile=JSON.parse(sources.typescript);
 for(const [kind,role,blockers,form,protocol] of [
  ['Interface','application/interfaces',['DSR-009','DSR-011'],'typescript.bound-interface-structural','typescript.bound-interface/v1'],
  ['Mapping','application/mappings',['DSR-009','DSR-011','DSR-014'],'typescript.bound-mapping-function','typescript.bound-mapping/v1'],
 ] as const){
  const cell=config.types.find((c:{kind:string})=>c.kind===kind),overlay=profile.representation_overlays.find((o:{contract_id:string})=>o.contract_id===kind.toLowerCase()+'.profile-representation');
  if(cell?.role!==role||canonicalJson(cell.blocked_by)!==canonicalJson(blockers)||overlay?.candidate_protocols.length!==1||overlay.candidate_protocols[0].form_id!==form||overlay.candidate_protocols[0].protocol_id!==protocol)fail('selected profile/configuration mismatch');
 }
 const interfaceSelectors=new Set<string>(),mappings:ReturnType<typeof compilePublicMapping>[]=[];
 for(const selector of roots){
  const node=graph.nodes.find(n=>n.selector===selector);if(!node)fail('unknown root');
  if(node!.kind==='Interface'&&node!.body.typed_contract!==undefined)interfaceSelectors.add(selector);
  else if(node!.kind==='Mapping'&&(node!.body.typed_contract as {schema_version?:string}|undefined)?.schema_version===PUBLIC_MAPPING_VERSION){const mapping=compilePublicMapping(graph,boundary,fields,selector,sources.public_mapping_contract);mappings.push(mapping);mapping.bindings.interface_selectors.forEach(s=>interfaceSelectors.add(s));}
  else fail('roots require named Interface or public Mapping v3');
 }
 const location=(selector:string,role:string)=>{const parts=selector.split(':');if(parts.length!==2||!parts.every(portable))return fail('unsafe dependency selector');return selection.module_root+'/features/'+parts[0]+'/src/application/'+role+'/'+parts[1]+'.ts';};
 const artifacts:PlannedArtifact[]=[],paths=new Set<string>();
 const artifact=(relative_path:string,content:string)=>{if(paths.has(relative_path.toLowerCase()))fail('artifact collision');paths.add(relative_path.toLowerCase());const a={relative_path,content,size_bytes:Buffer.byteLength(content),sha256:sha256(content)};artifacts.push(a);return a;};
 const interfaces=[...interfaceSelectors].sort().map(selector=>{const rendered=renderNamedInterfaceSource(graph,selector,fields),relative_path=location(selector,'interfaces'),a=artifact(relative_path,rendered.content);return {selector,kind:'Interface' as const,relative_path,artifact_sha256:a.sha256,descriptor:rendered.descriptor};});
 const modules=mappings.map(mapping=>{
  const relative_path=location(mapping.selector,'mappings'),provider_path=relative_path.replace(/\.ts$/,'.provider.ts'),callable='mapping'+pascal(mapping.selector.split(':')[1]!);
  const imports=mapping.bindings.interface_selectors.map((selector,i)=>{const api=interfaces.find(a=>a.selector===selector)??fail('missing Interface dependency');return {selector,alias:'Public'+i,path:leaf(provider_path,api.relative_path),descriptor:api.descriptor,artifact_sha256:api.artifact_sha256};});
  const rendered=renderPublicMappingSource(mapping,fields,imports),provider=artifact(provider_path,rendered.content);
  const body={schema_version:'domainspec.generated-public-mapping-descriptor/v1-candidate',selector:mapping.selector,protocol_id:'typescript.bound-mapping/v1',mapping_sha256:mapping.mapping_sha256,definition_sha256:PUBLIC_BOUNDARY_GENERATION_SHA256,contract:mapping.contract,bindings:mapping.bindings,imports:imports.map(i=>({selector:i.selector,path:i.path,artifact_sha256:i.artifact_sha256,contract_sha256:i.descriptor.contract_sha256})),provider_sha256:provider.sha256,field_compilation_sha256:fields?.compilation_sha256??null,graph_sha256:certificate.graph_sha256,effect_contract:'pure-explicit-field-projection',invariant_execution:'not-performed',authority_effect:'none'};
  const descriptor={...body,descriptor_sha256:sha256(canonicalJson(body))};
  artifact(relative_path,'import {map} from '+JSON.stringify(leaf(relative_path,provider_path))+';\nexport type {Parameters,Result} from '+JSON.stringify(leaf(relative_path,provider_path))+';\nexport const '+callable+'=Object.freeze(Object.assign(map,{descriptor:'+literal(descriptor)+'}));\n');
  return {selector:mapping.selector,kind:'Mapping' as const,relative_path,provider_path,callable,descriptor};
 });
 artifacts.sort((a,b)=>a.relative_path<b.relative_path?-1:1);
 const body={schema_version:'domainspec.configured-public-boundaries-plan/v1-candidate' as const,selection:{...selection,roots},certificate,boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields?.compilation_sha256??null,source_digests:expected,interfaces,modules,artifacts,discharged_configuration_prerequisites:['DSR-009','DSR-011'],bounded_prerequisite_evidence:{'DSR-014':'explicit-projection-bindings-not-parent-completion'},authority_effect:'none' as const};
 const selectedBody={...body,...(fields===null?{minimal_context_sha256:MINIMAL_VALUE_CONTEXT_SHA256}:{})};
 return freeze({...selectedBody,plan_sha256:sha256(canonicalJson(selectedBody))});
}
