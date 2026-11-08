import path from 'node:path';
import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';
import type {FactRecipe} from './reconciled-rule-facts.js';
import {createMappingFacts} from './reconciled-mapping-facts.js';
import {MappingCapacity,type MappingType} from './reconciled-mapping-reference.js';
import {decodeTypedMappingContract} from '../typed-backend/contracts.js';
import {decodeTypedInputMappingContract} from '../typed-backend/mapping-inputs.js';
import {decodePublicMapping} from '../typed-backend/mapping-public.js';
import {compilePublicMapping} from '../input/compiled-public-mapping.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../input/composition-boundary.js';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../input/compiled-field-model.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
export const SEMANTIC_MAPPING_DEFINITION_SHA256='beedf8c37f43f80cdb5d1f3d90f06ee82bb015734f11ef4641e0617fac1019d0';
export interface MappingControls {
 readonly selector:string;readonly kind:'Mapping';readonly state:'ready';readonly adapter:'mapping';
 readonly contract_sha256:string;readonly relative_path:string;readonly callable:string;readonly names:readonly string[];
 readonly module_paths:readonly string[];readonly cases:readonly SemanticCase[];readonly recipes:readonly FactRecipe[];
 readonly native_imports:readonly {relative_path:string;imports:readonly {specifier:string;target_path:string}[]}[];
}
export function mappingModule(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,plan:ReconciledProjectPlan){
 const callable='mapping'+node.node_id.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
 const modules=plan.resolved.modules.filter(m=>m.qualified_selectors.includes(node.selector)&&m.exports.some(e=>e.name===callable&&e.kind==='value'));
 if(modules.length!==1)throw new TypeError('MAPPING_CONTROLS:unique constructor required');
 const paths=new Set<string>(),visit=(p:string)=>{
  if(paths.has(p))return;paths.add(p);const m=plan.resolved.modules.find(m=>m.relative_path===p);
  if(!m||m.qualified_selectors.some(s=>s!==node.selector&&graph.nodes.find(n=>n.selector===s)!.kind!=='Interface'))throw new TypeError('MAPPING_CONTROLS:foreign native dependency');
  for(const i of m.imports){if(!i.target_path)throw new TypeError('MAPPING_CONTROLS:external dependency');visit(i.target_path);}
 };visit(modules[0]!.relative_path);
 return {callable,relative_path:modules[0]!.relative_path,module_paths:[...paths].sort(),native_imports:[...paths].sort().map(relative_path=>({relative_path,imports:plan.resolved.modules.find(m=>m.relative_path===relative_path)!.imports.map(i=>({specifier:i.specifier,target_path:i.target_path!}))}))};
}
export function createMappingEffectAudit(graph:CompiledProjectGraph,plan:ReconciledProjectPlan){
 const nodes=graph.nodes.filter(n=>n.kind==='Mapping');return {definition_sha256:SEMANTIC_MAPPING_DEFINITION_SHA256,roots:nodes.map(n=>n.selector).sort(),module_paths:[...new Set(nodes.flatMap(n=>mappingModule(n,graph,plan).module_paths))].sort()};
}
const view=(v:any):unknown=>v===null?['null']:typeof v!=='object'?[typeof v,String(v)]:Array.isArray(v)?['array',v.map(view)]:['record',Object.keys(v).sort().map(k=>[k,view(v[k])])];
/** Target-independent source witnesses; native bindings are added by each adapter. */
export function createMappingSemanticCases(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph){
 const version=(node.body.typed_contract as any).schema_version,legacy=version==='domainspec.typed-mapping/v1',pub=version==='domainspec.typed-mapping/v3';
  const contract=legacy?decodeTypedMappingContract(node.body.typed_contract):pub?decodePublicMapping(node.body.typed_contract):decodeTypedInputMappingContract(node.body.typed_contract);
  const parameters:readonly {name:string;type:MappingType}[]=contract.schema_version==='domainspec.typed-mapping/v1'?[{name:'source',type:{kind:'named',selector:contract.source}}]:contract.inputs;
  const fields=contract.fields as any[],extra=legacy?fields.flatMap(f=>f.default?[{op:'literal',...f.default}]:[]):fields.flatMap(f=>[f.value,...(f.default?[f.default]:[])]);
  const facts=createMappingFacts(graph,extra),ref=facts.reference,errors=pub?'RULE_INPUT':'MAPPING_INPUT';
  const targetType:MappingType=typeof contract.target==='string'?{kind:'named',selector:contract.target}:contract.target,target=ref.get(targetType);
  const rows=fields.map(f=>({binding:f,field:target.properties.find(p=>p.name===f.target)!}));
  const outcome=(recipe:FactRecipe):SemanticCase['expected']=>{
   try{
    const raw=ref.members(recipe,errors);if(Object.keys(raw).some(k=>!parameters.some(p=>p.name===k)))throw new TypeError(errors);
    if(Object.keys(raw).length!==parameters.length)throw new TypeError('MAPPING_INPUT');
    const args=new Map(parameters.map(p=>[p.name,{type:p.type,value:ref.normalize(p.type,raw[p.name]!,errors)}]));
    const output:[string,unknown][]=[];
    for(const {binding:b,field}of rows){
     let value:any;
     if(legacy){
      const source=ref.members(raw.source!,errors),present=b.source!==null&&Object.hasOwn(source,b.source);
      if(b.source!==null&&b.default===null&&contract.total&&!present)throw new TypeError('MAPPING_REQUIRED_VALUE');
      if(b.source!==null&&b.default===null&&!contract.total&&!present&&ref.get(parameters[0]!.type).properties.find(p=>p.name===b.source)!.type.kind==='optional')continue;
      value=present?args.get('source')!.value[b.source]:b.default?ref.value({op:'literal',...b.default},args).value:args.get('source')!.value[b.source];
     }else{value=ref.value(b.value,args).value;if(value===null&&b.default!==null)value=ref.value(b.default,args).value;}
     output.push([field.name,view(value)]);
    }
    return {kind:'value',value:canonicalJson(output)};
   }catch(e){if(e instanceof TypeError&&['MAPPING_INPUT','MAPPING_REQUIRED_VALUE','RULE_INPUT','INTERFACE_VALUE'].includes(e.message))return {kind:'error',name:'TypeError',message:e.message};throw e;}
  };
  const cases:SemanticCase[]=[],recipes:FactRecipe[]=[],seen=new Set<string>(),ids=new Map<string,number>();let bytes=256;
  const intern=(r:FactRecipe):number=>{
   const link=(x:FactRecipe):FactRecipe=>({tag:'ref',value:String(intern(x))});
   const value={...r,...(r.base?{base:link(r.base)}:{}),...(r.input?{input:link(r.input)}:{}),...(r.payload?{payload:link(r.payload)}:{}),...(r.items?{items:r.items.map(link)}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,x])=>[k,link(x)]))}:{})};
   const encoded=canonicalJson(value),id=ids.get(encoded);if(id!==undefined)return id;bytes+=Buffer.byteLength(encoded)+1;if(bytes>8388608)throw new MappingCapacity('bounded Mapping serialized case capacity exceeded');
   const n=recipes.length;recipes.push(value);ids.set(encoded,n);return n;
  };
  const add=(recipe:FactRecipe)=>{
   const id=String(intern(recipe));if(seen.has(id))return;seen.add(id);if(cases.length>=4096)throw new MappingCapacity('bounded Mapping case capacity exceeded');
   const c:SemanticCase={id:'case-'+cases.length,mode:'mapping',format:'string',values:[id],expected:outcome(recipe)};
   bytes+=Buffer.byteLength(canonicalJson(c))+1;if(bytes>8388608)throw new MappingCapacity('bounded Mapping serialized case capacity exceeded');cases.push(c);
  };
  const columns=parameters.map(p=>facts.samples(p.type)),base=columns.map(c=>c[0]!),input=(v:readonly FactRecipe[]):FactRecipe=>({tag:'fields',fields:Object.fromEntries(parameters.map((p,i)=>[p.name,v[i]!]))}),baseline=input(base);
  for(const values of facts.vectors(columns))add(input(values));
  for(const mode of ['frozen','null-prototype','null','array','number','string','undefined','coercion','inherited','extra','symbol'])add(facts.bad(baseline,mode));
  const shape=(r:FactRecipe):unknown=>r.tag==='scalar'?{tag:r.tag}:{tag:r.tag,variant:r.variant,...(r.input?{input:shape(r.input)}:{}),...(r.payload?{payload:shape(r.payload)}:{}),...(r.items?{items:r.items.map(shape)}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,v])=>[k,shape(v)]))}:{})};
  for(const [i,p]of parameters.entries()){
   for(const mode of ['getter','non-enumerable','missing-field'])add(facts.bad(baseline,mode,p.name));
   for(const r of [...new Map(columns[i]!.map(r=>[canonicalJson(shape(r)),r])).values()]){
    for(const invalid of facts.negative(p.type,r)){const values=[...base];values[i]=invalid;add(input(values));}
    for(const omission of facts.omissions(p.type,r)){const values=[...base];values[i]=omission.recipe;add(input(values));}
   }
  }
  return {contract,parameters,rows,ref,legacy,pub,cases,recipes,bytes,target};
}
export function createMappingControls(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,plan:ReconciledProjectPlan):MappingControls|Readonly<{selector:string;kind:'Mapping';state:'not_evaluable';reason:string}>{
 try{
  let {contract,parameters,rows,ref,legacy,pub,cases,recipes,bytes,target}=createMappingSemanticCases(node,graph);
  const module=mappingModule(node,graph,plan);
  // Reconstruct the selected descriptor from checked source contracts, never emitted code.
  const certificate=createCompiledProjectCertificate(graph),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},getReconciledSource('composition'));
  const roots=graph.nodes.filter(n=>['Entity','Value Object','Enum'].includes(n.kind)).map(n=>n.selector).sort();
  const compiled=roots.length?compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots,bindings:plan.selection.field_bindings},getReconciledSource('field')):null;
  const providerPath=module.relative_path.replace(/\.ts$/,'.provider.ts'),provider=plan.resolved.artifacts.find(a=>a.relative_path===providerPath)!;
  let descriptor:any;
  if(pub){
   const checked=compilePublicMapping(graph,boundary,compiled,node.selector,getReconciledSource('public_mapping_value_object'));
   const imports=checked.bindings.interface_selectors.map(selector=>{
    const m=plan.resolved.modules.find(m=>m.qualified_selectors.includes(selector)&&m.exports.some(e=>e.name==='publicContracts'))!;
    let relative=path.posix.relative(path.posix.dirname(providerPath),m.relative_path).replace(/\.ts$/,'.js');if(!relative.startsWith('.'))relative='./'+relative;
    return {selector,path:relative,artifact_sha256:plan.resolved.artifacts.find(a=>a.relative_path===m.relative_path)!.sha256,contract_sha256:sha256(canonicalJson(checked.interfaces.find(i=>i.source.selector===selector)!.contract))};
   });
   descriptor={schema_version:'domainspec.generated-public-mapping-descriptor/v1-candidate',selector:node.selector,protocol_id:'typescript.bound-mapping/v1',mapping_sha256:checked.mapping_sha256,definition_sha256:sha256(getReconciledSource('public_boundary')),contract:checked.contract,bindings:checked.bindings,imports,provider_sha256:provider.sha256,field_compilation_sha256:compiled?.compilation_sha256??null,graph_sha256:certificate.graph_sha256,effect_contract:'pure-explicit-field-projection',invariant_execution:'not-performed',authority_effect:'none'};
  }else{
   const result_fields=rows.map(({binding:b,field:f})=>({name:f.name,type:f.type,optional:legacy&&b.source!==null&&b.default===null&&!contract.total&&ref.get(parameters[0]!.type).properties.find(p=>p.name===b.source)!.type.kind==='optional',ontology_property:f.ontology_property}));
   descriptor={schema_version:'domainspec.generated-mapping-descriptor/v1-candidate',protocol_id:'typescript.bound-mapping/v1',selector:node.selector,ontology_mapping:contract.ontology_mapping,source_schema:contract.schema_version,contract_sha256:sha256(canonicalJson(contract)),source:boundary.value_bindings.core_contracts.find(c=>c.owner.selector===node.selector)!.source,inputs:parameters,target:{selector:contract.target,kind:target.kind,fields:result_fields},total:contract.total,field_model_sha256:compiled!.model.model_sha256,value_profile:plan.selection.value_profile,fields:contract.fields,default_semantics:legacy?'absent-source-property-only':'explicit-nullish-fallback',return_semantics:'field-projection-not-construction',effect_contract:'pure-explicit-values',dependency_contract:'declared-inputs-only',result_consumption:'complete',primary_callable_count:1,failures:['MAPPING_INPUT','MAPPING_REQUIRED_VALUE'],provider:{id:node.selector+'/typescript-exact/v1',sha256:provider.sha256},authority_effect:'none'};
  }
  const binding:SemanticCase={id:'binding',mode:'mapping-descriptor',format:'string',values:[],expected:{kind:'value',value:canonicalJson({...descriptor,descriptor_sha256:sha256(canonicalJson(descriptor))})}};
  bytes+=Buffer.byteLength(canonicalJson(binding));if(bytes>8388608||cases.length>=4096)throw new MappingCapacity('bounded Mapping binding case capacity exceeded');cases.unshift(binding);
  return {selector:node.selector,kind:'Mapping',state:'ready',adapter:'mapping',contract_sha256:sha256(canonicalJson(contract)),...module,names:parameters.map(p=>p.name),cases,recipes};
 }catch(e){if(e instanceof MappingCapacity)return {selector:node.selector,kind:'Mapping',state:'not_evaluable',reason:e.message};throw e;}
}
