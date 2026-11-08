import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';
import type {MappingControls} from './reconciled-mapping-controls.js';
import type {TypedType,ValueExpression} from '../typed-operation/contracts.js';
import {decodeTypedQueryContract} from '../typed-backend/contracts.js';
import {createStructuralFacts,RuleFactsCapacity,type FactRecipe} from './reconciled-rule-facts.js';
import {createQueryReference} from './reconciled-query-reference.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../input/composition-boundary.js';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../input/compiled-field-model.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {queryCardinalityExtension} from '../generation/query-cardinality-extension.js';
export const SEMANTIC_QUERY_DEFINITION_SHA256='f21529bc1e75b0c2e0721298c3b3d6edcf30dbd9060ca6ec6ac36fec0deb6105';
export interface QueryControls extends Omit<MappingControls,'kind'|'adapter'>{readonly kind:'Query';readonly adapter:'query';readonly result_cardinality?:'list'|'optional';}
export function queryModule(node:CompiledProjectGraph['nodes'][number],plan:ReconciledProjectPlan){
 const callable='query'+node.node_id.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
 const modules=plan.resolved.modules.filter(m=>m.qualified_selectors.includes(node.selector)&&m.exports.some(e=>e.name===callable&&e.kind==='value'));
 if(modules.length!==1)throw new TypeError('QUERY_CONTROLS:unique callable required');
 const paths=new Set<string>(),visit=(p:string)=>{
  if(paths.has(p))return;paths.add(p);const m=plan.resolved.modules.find(m=>m.relative_path===p);
  if(!m||m.qualified_selectors.some(s=>s!==node.selector))throw new TypeError('QUERY_CONTROLS:foreign native dependency');
  for(const i of m.imports){if(!i.target_path)throw new TypeError('QUERY_CONTROLS:external dependency');visit(i.target_path);}
 };visit(modules[0]!.relative_path);
 return {callable,relative_path:modules[0]!.relative_path,module_paths:[...paths].sort(),native_imports:[...paths].sort().map(relative_path=>({relative_path,imports:plan.resolved.modules.find(m=>m.relative_path===relative_path)!.imports.map(i=>({specifier:i.specifier,target_path:i.target_path!}))}))};
}
export function createQueryEffectAudit(graph:CompiledProjectGraph,plan:ReconciledProjectPlan){
 const nodes=graph.nodes.filter(n=>n.kind==='Query');return {definition_sha256:SEMANTIC_QUERY_DEFINITION_SHA256,roots:nodes.map(n=>n.selector).sort(),module_paths:[...new Set(nodes.flatMap(n=>queryModule(n,plan).module_paths))].sort()};
}
/** Target-independent source witnesses; native bindings are added by each adapter. */
export function createQuerySemanticCases(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph){
 const contract=decodeTypedQueryContract(node.body.typed_contract),extra:ValueExpression[]=[];
  const walk=(v:any)=>{if(!v||typeof v!=='object')return;if(v.kind==='literal')extra.push({op:'literal',type:v.type,value:v.value});for(const x of Object.values(v))if(Array.isArray(x))x.forEach(walk);else if(x&&typeof x==='object')walk(x);};walk(contract.filter);
  const capacity=(why:string):never=>{throw new RuleFactsCapacity('bounded Query '+why+' capacity exceeded');};
  if(contract.limit!==null&&contract.limit>=4096)capacity('limit witness');
  const facts=createStructuralFacts(graph,[],extra),reference=createQueryReference(contract,facts.reference),rowType:TypedType={kind:'named',selector:contract.source},rows=facts.samples(rowType),columns=contract.inputs.map(p=>facts.samples(p.type));
  const params=(v:readonly FactRecipe[]):FactRecipe=>({tag:'fields',fields:Object.fromEntries(contract.inputs.map((p,i)=>[p.name,v[i]!]))}),base=params(columns.map(c=>c[0]!)),list=(r:readonly FactRecipe[]):FactRecipe=>({tag:'list',items:r}),first=rows[0]!;
  const recipes:FactRecipe[]=[],ids=new Map<string,number>(),cases:SemanticCase[]=[],seen=new Set<string>();let bytes=256;
  const intern=(r:FactRecipe):number=>{
   const link=(x:FactRecipe):FactRecipe=>({tag:'ref',value:String(intern(x))});
   const value={...r,...(r.base?{base:link(r.base)}:{}),...(r.input?{input:link(r.input)}:{}),...(r.payload?{payload:link(r.payload)}:{}),...(r.items?{items:r.items.map(link)}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,x])=>[k,link(x)]))}:{})};
   const encoded=canonicalJson(value),old=ids.get(encoded);if(old!==undefined)return old;bytes+=Buffer.byteLength(encoded)+1;if(bytes>8388608)capacity('serialized case');
   const id=recipes.length;recipes.push(value);ids.set(encoded,id);return id;
  };
  const add=(r:FactRecipe,p:FactRecipe)=>{
   if((r.items?.length??0)>4096)capacity('row occurrence');
   const input:FactRecipe={tag:'fields',fields:{rows:r,parameters:p}},id=String(intern(input));if(seen.has(id))return;seen.add(id);if(cases.length>=4095)capacity('case');
   let expected:SemanticCase['expected'];try{expected={kind:'value',value:canonicalJson(reference.evaluate(r,p))};}catch(e){if(e instanceof TypeError&&['QUERY_INPUT','QUERY_CARDINALITY'].includes(e.message))expected={kind:'error',name:'TypeError',message:e.message};else throw e;}
   const c:SemanticCase={id:'case-'+cases.length,mode:'query',format:'string',values:[id],expected};bytes+=Buffer.byteLength(canonicalJson(c))+1;if(bytes>8388608)capacity('serialized case');cases.push(c);
  };
  add(list([]),base);
  for(const vector of facts.vectors([rows,...columns])){
   const r=vector[0]!,p=params(vector.slice(1));add(list([r]),p);add(list([r,first,r]),p);
  }
  const parameterVectors=facts.vectors(columns);
  for(const vector of parameterVectors){
   const p=params(vector);add(list([]),p);add(list(rows.slice(0,64)),p);add(list([...rows.slice(0,64)].reverse()),p);
  }
  // Exercise each admitted finite limit at either side without exponential products.
  if(contract.limit!==null)for(const n of [Math.max(0,contract.limit-1),contract.limit,contract.limit+1])add(list(Array.from({length:n},(_,i)=>rows[i%rows.length]!)),base);
  const rowShape=(r:FactRecipe):unknown=>r.tag==='scalar'?{tag:r.tag}:{tag:r.tag,variant:r.variant,...(r.input?{input:rowShape(r.input)}:{}),...(r.payload?{payload:rowShape(r.payload)}:{}),...(r.items?{items:r.items.map(rowShape)}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,x])=>[k,rowShape(x)]))}:{})};
  const representatives=[...new Map(rows.map(r=>[canonicalJson(rowShape(r)),r])).values()];
  for(const r of representatives){
   for(const bad of facts.negative(rowType,r)){add(list([bad]),base);add(list([first,bad]),base);}
   for(const o of facts.omissions(rowType,r))add(list([o.recipe]),base);
  }
  for(const mode of ['null','object','collection-extra','collection-symbol','collection-inherited','sparse','collection-getter','collection-hidden'])add(facts.bad(list([first]),mode),base);
  for(const mode of ['frozen','null-prototype','null','array','number','string','undefined','coercion','inherited','extra','symbol'])add(list([first]),facts.bad(base,mode));
  for(const [i,p]of contract.inputs.entries()){
   for(const mode of ['getter','non-enumerable','missing-field']){add(list([]),facts.bad(base,mode,p.name));add(list([first]),facts.bad(base,mode,p.name));}
   for(const invalid of facts.negative(p.type,columns[i]![0]!)){const vector=columns.map(c=>c[0]!);vector[i]=invalid;add(list([]),params(vector));add(list([first]),params(vector));}
  }
  return {contract,reference,cases,recipes,bytes,capacity};
}
export function createQueryControls(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,plan:ReconciledProjectPlan):QueryControls|Readonly<{selector:string;kind:'Query';state:'not_evaluable';reason:string}>{
 try{
  let {contract,reference,cases,recipes,bytes,capacity}=createQuerySemanticCases(node,graph);
  const module=queryModule(node,plan);
  const certificate=createCompiledProjectCertificate(graph),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},getReconciledSource('composition'));
  const compiled=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots:graph.nodes.filter(n=>['Entity','Value Object','Enum'].includes(n.kind)).map(n=>n.selector).sort(),bindings:plan.selection.field_bindings},getReconciledSource('field'));
  const provider=plan.resolved.artifacts.find(a=>a.relative_path===module.relative_path.replace(/\.ts$/,'.provider.ts'))!;
  const descriptor={schema_version:'domainspec.generated-query-descriptor/v1-candidate',protocol_id:'typescript.bound-query/v1',selector:node.selector,ontology_query:contract.ontology_query,contract_sha256:sha256(canonicalJson(contract)),source:boundary.value_bindings.core_contracts.find(c=>c.owner.selector===node.selector)!.source,inputs:contract.inputs,read_targets:[{selector:contract.source,fields:reference.fields.map(f=>f.name).sort()}],result_fields:contract.projection.map(name=>({name,type:reference.fields.find(f=>f.name===name)!.type})),field_model_sha256:compiled.model.model_sha256,value_profile:plan.selection.value_profile,filter:contract.filter,order_by:contract.order_by,limit:contract.limit,...queryCardinalityExtension(contract,'typescript'),return_semantics:'read-model',effect_contract:'declared-read-only',dependency_contract:'declared-read-targets-only',failure_contract:'declared',result_consumption:'complete',primary_callable_count:1,supporting_exports:'explicit-only',failures:['QUERY_INPUT',...(contract.schema_version==='domainspec.typed-query/v2'&&contract.result_cardinality==='optional'?['QUERY_CARDINALITY']:[])],provider:{id:node.selector+'/typescript-exact/v1',sha256:provider.sha256},authority_effect:'none'};
  const binding:SemanticCase={id:'binding',mode:'query-descriptor',format:'string',values:[],expected:{kind:'value',value:canonicalJson({...descriptor,descriptor_sha256:sha256(canonicalJson(descriptor))})}};
  bytes+=Buffer.byteLength(canonicalJson(binding));if(bytes>8388608)capacity('serialized binding');cases.unshift(binding);
  return {selector:node.selector,kind:'Query',state:'ready',adapter:'query',contract_sha256:sha256(canonicalJson(contract)),...module,names:contract.inputs.map(p=>p.name),cases,recipes,...(contract.schema_version==='domainspec.typed-query/v2'?{result_cardinality:contract.result_cardinality}:{})};
 }catch(e){if(e instanceof RuleFactsCapacity)return {selector:node.selector,kind:'Query',state:'not_evaluable',reason:e.message.replace('bounded Rule','bounded Query')};throw e;}
}
