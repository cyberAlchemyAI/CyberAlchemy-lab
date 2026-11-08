import {selectCompiledProjectNode,type CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {TypedType} from '../typed-operation/contracts.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {createOwnedValueContext,isWitnessUnavailable,WitnessUnavailable,type SumRecipe,type Dependency} from './reconciled-value-context.js';
import {recordWitnesses,evaluateRecordWitness,type RecordWitnessProbe} from './reconciled-record-witness.js';
export const SEMANTIC_FACTORY_DEFINITION_SHA256='d00e4d73c782b1aab880f6c0b14d9cd33828ece9a64cdbf846ace69faa76f8f8';
export interface FactoryControls {
 readonly selector:string;readonly kind:'Entity'|'Value Object';readonly state:'ready';readonly adapter:'factory';
 readonly contract_sha256:string;readonly relative_path:string;readonly callable:string;readonly names:readonly string[];
 readonly module_paths:readonly string[];readonly cases:readonly SemanticCase[];readonly value_contract_sha256:string;
 readonly shape:TypedType;readonly dependencies:Readonly<Record<string,Dependency>>;readonly baseline:SumRecipe;
}
type Recipe=SumRecipe & Readonly<{field?:string}>;
type Request=Readonly<{route:'create'|'reconstruct'|'transition'|'extend';chain:readonly string[];input:Recipe;previous?:Recipe}>;
/** Source lifecycle requests and outcomes; the backend binds validator receipts. */
export function createFactorySemanticCases(ctx:ReturnType<typeof createOwnedValueContext>,boundTrace:(probe:RecordWitnessProbe['expected'])=>unknown){
  const {root,rootShape,dependencies,reference,ref,valueContract}=ctx;
  if(root.kind==='Enum')throw new TypeError('DS_FACTORY_CONTROLS:record required');
  const values=ctx.samples(rootShape),baseline=values[0]!,fields=[...root.record.properties].sort((a,b)=>a.name<b.name?-1:1),cases:SemanticCase[]=[],seen=new Set<string>();
  const childSamples=new Map(fields.map(f=>[canonicalJson(f.type),ctx.samples(f.type)]));
  const tag=(type:TypedType):string=>type.kind==='scalar'?type.name:type.kind==='sum'?'Sum':type.kind==='named'?(dependencies[type.selector]!.kind==='Entity'?'Entity':dependencies[type.selector]!.kind==='Value Object'?'ValueObject':dependencies[type.selector]!.plain?'Enum':'Sum'):type.kind[0]!.toUpperCase()+type.kind.slice(1);
  const metadata={protocol_id:root.kind==='Entity'?'typescript.owned-entity-component/v1-candidate':'typescript.owned-value-component/v1',concept:root.selector,contract_sha256:valueContract,frozen:true};
  const push=(request:Request,value:unknown,error=false)=>{
   const encoded=canonicalJson(request);if(seen.has(encoded))return;seen.add(encoded);
   if(cases.length>=4096)throw new WitnessUnavailable('bounded factory case capacity exceeded');
   cases.push({id:'case-'+cases.length,mode:'factory',format:'string',values:[encoded],expected:error?{kind:'error',name:'TypeError',message:'INVALID_EXTENSION'}:{kind:'value',value:canonicalJson(value)}});
  };
  const chains:string[][]=[];
  const visit=(chain:string[])=>{if(chains.length>=4096)throw new WitnessUnavailable('bounded factory extension chain capacity exceeded');chains.push(chain);for(const e of root.binding.extensions)if(!chain.includes(e.id))visit([...chain,e.id]);};visit([]);
  for(const chain of chains){
   const validators=[...root.binding.base_validators,...chain.flatMap(id=>root.binding.extensions.find(e=>e.id===id)!.validators)];
   const search={...root,binding:{...root.binding,base_validators:validators},probes:[] as readonly RecordWitnessProbe[]};
   const accepted=chain.length?recordWitnesses(search,reference,t=>childSamples.get(canonicalJson(t))!):values;
   const probes=chain.length?search.probes:root.probes;
   const evaluate=(r:SumRecipe)=>evaluateRecordWitness(root,reference,r,validators);
   const observe=(request:Request,recipe:SumRecipe,invalid?:'INVALID_FIELDS'|'INVALID_PREVIOUS')=>{
    const probe=invalid?{ok:false,failure_codes:[invalid],trace:{route:'create' as const,phases:invalid==='INVALID_PREVIOUS'?[]:['normalize'],validators:[]}}:evaluate(recipe);
    let ok=probe.ok,codes=[...probe.failure_codes],phases=[...probe.trace.phases];
    if(ok&&request.route==='transition'&&ref(rootShape,recipe).key!==ref(rootShape,request.previous!).key){ok=false;codes=['IDENTITY_CHANGED'];phases=['normalize','resolve-identity'];}
    let snapshot:unknown=null;
    if(ok){
     const value=ref(rootShape,recipe);
     snapshot={view:value.view,key:value.owned_key,hash:value.owned_key,owned:true,fresh:true,fresh_previous:true,equal_copy:true,equals_baseline:value.key===ref(rootShape,baseline).key,
      clone_rejected:true,foreign_rejected:true,snapshot_copy_equal:true,snapshot_clone_equal:false,snapshot_foreign_equal:false,metadata,
      components_frozen:true,components:fields.map(f=>({field:f.name,tag:tag(f.type),protocol_id:'typescript.owned-value-component/v1',protocol_sha256:valueContract,frozen:true,field_value_identical:true})),
      identity:root.kind==='Entity'?{frozen:true,component_index:fields.findIndex(f=>f.identity)}:null};
    }
    push(request,{ok,failure_codes:codes,trace:{route:request.route,phases,validators:boundTrace(probe)},frozen:{result:true,failure_codes:true,trace:true,phases:true,validators:true,validator_rows:true},
     factory:{frozen:true,extensions:[...chain],extensions_frozen:true,base_extensions:[],base_frozen:true,base_extensions_frozen:true,transition_present:root.kind==='Entity'},snapshot});
   };
   // Apply every observed base failure to extended chains too, ensuring extensions cannot bypass base validation.
   const selected=[...new Map([...root.probes,...probes].map(p=>[canonicalJson(p.recipe),p.recipe])).values()];
   for(const recipe of selected){
    const input:Recipe={tag:'fields',fields:recipe.fields!};
    for(const route of ['create','reconstruct'] as const)observe({route,chain,input},recipe);
    if(root.kind==='Entity'){
     observe({route:'transition',chain,input,previous:baseline},recipe);
     if(evaluate(recipe).ok)observe({route:'transition',chain,input,previous:recipe},recipe);
    }
   }
   const good=accepted[0]!,baseInput:Recipe={tag:'fields',fields:good.fields!};
   const invalid=(input:Recipe)=>{for(const route of ['create','reconstruct',...(root.kind==='Entity'?['transition'] as const:[])] as const)observe({route,chain,input,...(route==='transition'?{previous:baseline}:{})},good,'INVALID_FIELDS');};
   for(const mode of ['null','array','number','string','undefined','coercion','inherited','extra','symbol'])invalid({tag:'bad',mode,base:baseInput});
   for(const f of fields){
    for(const mode of ['getter','non-enumerable'])invalid({tag:'bad',mode,field:f.name,base:baseInput});
    if(f.type.kind==='optional'){
     const recipe={...good,fields:{...good.fields,[f.name]:{tag:'null'}}};
     for(const route of ['create','reconstruct'] as const)observe({route,chain,input:{tag:'bad',mode:'missing-field',field:f.name,base:baseInput}},recipe);
    }else invalid({tag:'bad',mode:'missing-field',field:f.name,base:baseInput});
    // A nominal nested witness remains valid until the owning field normalizer checks the mutated value.
    const containsBad=(r:SumRecipe):boolean=>r.tag==='bad'||Object.values(r.fields??{}).some(containsBad)||(r.items??[]).some(containsBad)||!!(r.input&&containsBad(r.input))||!!(r.payload&&containsBad(r.payload));
    const failsBeforeField=(r:SumRecipe):boolean=>r.tag==='named'&&containsBad(r.input!)||(r.items??[]).some(failsBeforeField)||!!(r.payload&&failsBeforeField(r.payload));
    // Invalid named-sum construction is tested by its sum adapter, not misreported as factory normalization.
    for(const n of ctx.negative(f.type,good.fields![f.name]!))if(!failsBeforeField(n.recipe))invalid({tag:'fields',fields:{...good.fields,[f.name]:n.recipe}});
   }
   for(const mode of ['frozen','null-prototype'])for(const route of ['create','reconstruct'] as const)observe({route,chain,input:{tag:'bad',base:baseInput,mode}},good);
   if(root.kind==='Entity')for(const mode of ['null','raw-named','clone-named','foreign-named','getter'])for(const input of [baseInput,{tag:'bad',mode:'null',base:baseInput}])observe({route:'transition',chain,input,previous:{tag:'bad',mode,field:'fields',base:baseline}},good,'INVALID_PREVIOUS');
   let unknown='__semantic_unknown__';while(root.binding.extensions.some(e=>e.id===unknown))unknown+='_';
   for(const input of [{tag:'scalar',value:unknown},{tag:'null'},{tag:'bad',mode:'coercion',base:{tag:'scalar',value:''}},...chain.map(value=>({tag:'scalar',value}))] as Recipe[])push({route:'extend',chain,input},null,true);
  }
  return {baseline,cases};
}
export function createFactoryControls(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,plan:ReconciledProjectPlan):FactoryControls|Readonly<{selector:string;kind:string;state:'not_evaluable';reason:string}>{
 try{
  const ctx=createOwnedValueContext(node,graph,plan,true),{root,rootShape,dependencies,valueContract}=ctx;
  if(root.kind==='Enum')throw new TypeError('DS_FACTORY_CONTROLS:record required');
  const {baseline,cases}=createFactorySemanticCases(ctx,probe=>probe.trace.validators.map(v=>{
   const callable='rule'+v.rule.split(':')[1]!.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
   const modules=plan.resolved.modules.filter(m=>m.qualified_selectors.includes(v.rule)&&m.exports.some(e=>e.name===callable&&e.kind==='value'));
   if(modules.length!==1)throw new TypeError('DS_FACTORY_CONTROLS:unique Rule module required');
   return {...v,closure_sha256:selectCompiledProjectNode(graph,v.rule).typed_closure!.closure_sha256,artifact_sha256:modules[0]!.sha256};
  }));
  return {selector:node.selector,kind:root.kind,state:'ready',adapter:'factory',contract_sha256:sha256(canonicalJson({record:root.record,binding:root.binding})),relative_path:root.relative_path,callable:root.callable,names:[...root.record.properties].sort((a,b)=>a.name<b.name?-1:1).map(f=>f.name),module_paths:ctx.module_paths,cases,value_contract_sha256:valueContract,shape:rootShape,dependencies,baseline};
 }catch(error){if(isWitnessUnavailable(error))return {selector:node.selector,kind:node.kind,state:'not_evaluable',reason:error.message};throw error;}
}
