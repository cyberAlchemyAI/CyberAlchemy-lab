import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';
import type {MappingControls} from './reconciled-mapping-controls.js';
import {createMappingFacts} from './reconciled-mapping-facts.js';
import {MappingCapacity,type MappingType} from './reconciled-mapping-reference.js';
import {interfaceVersionCases,interfaceSignature} from './reconciled-interface-reference.js';
import type {FactRecipe} from './reconciled-rule-facts.js';
import {decodeNamedInterface,NAMED_INTERFACE_DEFINITION_SHA256} from '../typed-backend/interface.js';
import {INTERFACE_VERSION_POLICY_DEFINITION_SHA256} from '../typed-backend/interface-version-policy.js';
import {qualifyPublicType} from '../typed-backend/mapping-public.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../input/compiled-field-model.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
export const SEMANTIC_INTERFACE_DEFINITION_SHA256='e602326219c22b9d6195dd3ef7b3ccf24405e315c9e2a34cbade04bb14895f47';
export interface InterfaceControls extends Omit<MappingControls,'kind'|'adapter'>{
 readonly kind:'Interface';readonly adapter:'interface';readonly signature_source:string;
}
export function interfaceModule(node:CompiledProjectGraph['nodes'][number],plan:ReconciledProjectPlan){
 const modules=plan.resolved.modules.filter(m=>m.qualified_selectors.includes(node.selector)&&m.exports.some(e=>e.name==='publicContracts'&&e.kind==='value'));
 if(modules.length!==1)throw new TypeError('INTERFACE_CONTROLS:unique boundary required');
 const m=modules[0]!;if(m.qualified_selectors.length!==1||m.imports.length)throw new TypeError('INTERFACE_CONTROLS:standalone boundary required');
 return {callable:'publicContracts',relative_path:m.relative_path,module_paths:[m.relative_path],native_imports:[{relative_path:m.relative_path,imports:[]}]};
}
export function createInterfaceEffectAudit(graph:CompiledProjectGraph,plan:ReconciledProjectPlan){
 const nodes=graph.nodes.filter(n=>n.kind==='Interface');return {definition_sha256:SEMANTIC_INTERFACE_DEFINITION_SHA256,roots:nodes.map(n=>n.selector).sort(),module_paths:nodes.map(n=>interfaceModule(n,plan).relative_path).sort()};
}
const view=(v:any):unknown=>v===null?['null']:typeof v!=='object'?[typeof v,String(v)]:Array.isArray(v)?['array',v.map(view)]:['record',Object.keys(v).sort().map(k=>[k,view(v[k])])];
export function createInterfaceControls(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,plan:ReconciledProjectPlan):InterfaceControls|Readonly<{selector:string;kind:'Interface';state:'not_evaluable';reason:string}>{
 try{
  const module=interfaceModule(node,plan);
  const certificate=createCompiledProjectCertificate(graph),roots=graph.nodes.filter(n=>['Entity','Value Object','Enum'].includes(n.kind)).map(n=>n.selector).sort();
  const fields=roots.length?compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots,bindings:plan.selection.field_bindings},getReconciledSource('field')):null;
  const shared=createInterfaceSemanticCases(node,graph,fields?.compilation_sha256??null);
  if(shared.state!=='ready')return shared;
  const signature_source=interfaceSignature(graph,node.selector,module.relative_path);
  if(shared.serialized_bytes+Buffer.byteLength(signature_source)>8388608)throw new MappingCapacity('bounded Interface signature capacity exceeded');
  const {contract:_,serialized_bytes:__,...controls}=shared;
  return {...controls,adapter:'interface',...module,signature_source};
 }catch(e){if(e instanceof MappingCapacity)return {selector:node.selector,kind:'Interface',state:'not_evaluable',reason:e.message.replace('bounded Mapping','bounded Interface')};throw e;}
}

/** Shared source cases only. Native adapters bind their checked field compilation
 * and actual module separately; this does not construct a TypeScript plan. */
export function createInterfaceSemanticCases(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,fieldCompilationSha256:string|null){
 assertCompiledProjectSnapshot(graph);
 if(!graph.nodes.includes(node)||node.kind!=='Interface')throw new TypeError('INTERFACE_CONTROLS:registered Interface source required');
 if(fieldCompilationSha256!==null&&(typeof fieldCompilationSha256!=='string'||!/^[a-f0-9]{64}$/.test(fieldCompilationSha256)))throw new TypeError('INTERFACE_CONTROLS:field compilation identity');
 try{
  const contract=decodeNamedInterface(node.body.typed_contract),facts=createMappingFacts(graph),ref=facts.reference;
  const cases:SemanticCase[]=[],recipes:FactRecipe[]=[],ids=new Map<string,number>(),seen=new Set<string>();let bytes=256;
  const capacity=(reason:string):never=>{throw new MappingCapacity('bounded Interface '+reason+' capacity exceeded');};
  const intern=(r:FactRecipe):number=>{
   const link=(x:FactRecipe):FactRecipe=>({tag:'ref',value:String(intern(x))});
   const v={...r,...(r.base?{base:link(r.base)}:{}),...(r.input?{input:link(r.input)}:{}),...(r.payload?{payload:link(r.payload)}:{}),...(r.items?{items:r.items.map(link)}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,x])=>[k,link(x)]))}:{})};
   const encoded=canonicalJson(v),old=ids.get(encoded);if(old!==undefined)return old;bytes+=Buffer.byteLength(encoded)+1;if(bytes>8388608)capacity('serialized recipe');
   const id=recipes.length;recipes.push(v);ids.set(encoded,id);return id;
  };
  const add=(mode:string,values:string[],expected:SemanticCase['expected'])=>{
   const identity=canonicalJson({mode,values});if(seen.has(identity))return;seen.add(identity);if(cases.length>=4096)capacity('case');
   const c:SemanticCase={id:'case-'+cases.length,mode,format:'string',values,expected};bytes+=Buffer.byteLength(canonicalJson(c))+1;if(bytes>8388608)capacity('serialized case');cases.push(c);
  };
  const value=(v:unknown):SemanticCase['expected']=>({kind:'value',value:canonicalJson(v)});
  const certificate=createCompiledProjectCertificate(graph);
  const relative_path='specs/'+node.feature_id+'/nodes/'+node.node_id+'.json',source=graph.source_manifest.sources.find(s=>s.relative_path===relative_path)!;
  add('interface-descriptor',[],value({schema_version:'domainspec.named-interface-descriptor/v1-candidate',selector:node.selector,definition_sha256:NAMED_INTERFACE_DEFINITION_SHA256,graph_sha256:certificate.graph_sha256,source:{relative_path,sha256:source.sha256},field_compilation_sha256:fieldCompilationSha256,contract_sha256:sha256(canonicalJson(contract)),contract,effect_contract:'structural-interface-and-pure-shape-normalizers',invariant_execution:'not-performed',transport_execution:'not-performed',authority_effect:'none'}));
  add('interface-version-descriptor',[],value({...contract.version_policy,definition_sha256:INTERFACE_VERSION_POLICY_DEFINITION_SHA256,authority_effect:'none'}));
  add('interface-surface',[],value({public:contract.contracts.map(c=>c.contract_id).sort(),endpoints:contract.operations.map(o=>o.operation_id).sort()}));
  const shape=(r:FactRecipe):unknown=>r.tag==='scalar'?{tag:r.tag}:{tag:r.tag,variant:r.variant,...(r.input?{input:shape(r.input)}:{}),...(r.payload?{payload:shape(r.payload)}:{}),...(r.items?{items:r.items.map(shape)}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,x])=>[k,shape(x)]))}:{})};
  const protocol=(t:MappingType,route:string[])=>{
   const put=(r:FactRecipe)=>{
    let expected:SemanticCase['expected'];try{const v=ref.normalize(t,r,'INTERFACE_VALUE');expected=value({normalized:view(v),key:ref.key(t,v)});}catch(e){if(e instanceof TypeError&&e.message==='INTERFACE_VALUE')expected={kind:'error',name:'TypeError',message:e.message};else throw e;}
    add('interface-value',[String(intern(r)),...route],expected);
   };
   const samples=facts.samples(t);for(const r of samples)put(r);
   for(const r of [...new Map(samples.map(r=>[canonicalJson(shape(r)),r])).values()]){
    for(const bad of facts.negative(t,r))put(bad);
    for(const o of facts.omissions(t,r))put(o.recipe);
   }
   if(t.kind==='contract'||t.kind==='named'&&ref.get(t).kind!=='Enum')for(const mode of ['frozen','null-prototype'])put(facts.bad(samples[0]!,mode));
  };
  for(const c of [...contract.contracts].sort((a,b)=>a.contract_id<b.contract_id?-1:1))protocol({kind:'contract',interface_selector:node.selector,contract_id:c.contract_id},['public',c.contract_id]);
  for(const o of [...contract.operations].sort((a,b)=>a.operation_id<b.operation_id?-1:1))for(const side of ['request','result'] as const)protocol(qualifyPublicType(o[side],node.selector),['endpoint',o.operation_id,side]);
  for(const {recipe,result}of interfaceVersionCases(contract))add('interface-version',[String(intern(recipe))],value(result));
  return {selector:node.selector,kind:'Interface' as const,state:'ready' as const,contract,contract_sha256:sha256(canonicalJson(contract)),names:contract.contracts.map(c=>c.contract_id).sort(),cases,recipes,serialized_bytes:bytes};
 }catch(e){if(e instanceof MappingCapacity)return {selector:node.selector,kind:'Interface' as const,state:'not_evaluable' as const,reason:e.message.replace('bounded Mapping','bounded Interface')};throw e;}
}
