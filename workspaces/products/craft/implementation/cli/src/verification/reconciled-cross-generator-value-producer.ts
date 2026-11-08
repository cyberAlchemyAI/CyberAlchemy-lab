import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertReconciledProjectPlan,type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {assertCrossGeneratorBoundary,type CrossGeneratorBoundary} from './reconciled-cross-generator-boundary.js';
import {decodeTypedSumContract,type TypedType} from '../typed-operation/contracts.js';
import {createOwnedValueContext,isWitnessUnavailable,WitnessUnavailable,type SumRecipe} from './reconciled-value-context.js';
import {assertPolicyData} from '../typed-backend/policy-rules.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';

export const CROSS_GENERATOR_VALUE_PRODUCER_DEFINITION_SHA256 = '2e88a37aa1efd21ebcc4aabde5d22ca692a8840c2403cff1c9c3215533221ecc';
const fail=(s:string):never=>{throw new TypeError('CROSS_GENERATOR_VALUE_PRODUCER:'+s);};
const same=(a:unknown,b:unknown,s:string)=>{if(canonicalJson(a)!==canonicalJson(b))fail(s);};
const pascal=(s:string)=>s.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
const part=(s:string)=>s.length+':'+s;
const registered=new WeakSet<object>();
function freeze<T>(v:T):T {if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
type Location=readonly (string|number)[];
type Leaf={type:Extract<TypedType,{kind:'named'}>;recipe:SumRecipe;location:Location;occurrence:string};
type Call={provider:string;method:'isOwned'|'key';arity:number;input_paths:Location[];result:boolean|string};
const ordered=<T extends {name:string}>(xs:readonly T[])=>[...xs].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0);

/** Source-derived Enum and sum producer protocols; expected answers never enter native probes. */
export function createCrossGeneratorValueProducerControls(graph:CompiledProjectGraph,plan:ReconciledProjectPlan,boundary:CrossGeneratorBoundary,definition:string){
 if(typeof definition!=='string'||sha256(definition)!==CROSS_GENERATOR_VALUE_PRODUCER_DEFINITION_SHA256)fail('definition drift');
 assertCompiledProjectSnapshot(graph);assertReconciledProjectPlan(plan);assertCrossGeneratorBoundary(boundary);
 same(createCompiledProjectCertificate(graph),plan.resolved.certificate,'foreign graph');
 same(boundary.project_plan_sha256,plan.plan_sha256,'foreign plan');same(boundary.source_manifest_sha256,graph.source_manifest.manifest_sha256,'foreign source');
 const nodes=new Map(graph.nodes.map(n=>[n.selector,n]));
 const nativePath=(selector:string)=>{
  const n=nodes.get(selector)??fail('missing source provider');
  const role=n.kind==='Entity'?'entities':n.kind==='Value Object'?'value-objects':n.kind==='Enum'?'enums':fail('owned provider kind');
  const suffix=n.kind==='Enum'?(decodeTypedSumContract(n.body.typed_contract).variants.some(v=>v.payload!==null)?'.sum':'.component'):'';
  return plan.selection.module_root+'/features/'+n.feature_id+'/src/domain/'+role+'/'+n.node_id+suffix+'.ts';
 };
 const rows=graph.nodes.filter(n=>n.kind==='Enum').map(node=>{
  const contract=decodeTypedSumContract(node.body.typed_contract),shape:TypedType={kind:'sum',variants:contract.variants},relative_path=nativePath(node.selector),callable=pascal(node.node_id)+'ValueComponent';
  if(contract.variants.every(v=>v.payload===null)){
   const definition_path=relative_path.replace(/\.component\.ts$/,'.ts'),runtime_path=plan.selection.module_root+'/runtime/enum.ts',definition_symbol=pascal(node.node_id),members=ordered(contract.variants).map(v=>[v.name,v.name]);
   const requirements=[{importer_path:definition_path,target_path:runtime_path,names:['defineEnum']},{importer_path:relative_path,target_path:definition_path,names:[definition_symbol]}];
   const protocol=requirements.map((requirement,i)=>{
    const edges=boundary.edges.filter(e=>e.category==='generated-runtime'&&e.importer_path===requirement.importer_path);
    same(edges.map(e=>({importer_path:e.importer_path,target_path:e.target_path,names:e.names})),[requirement],'plain Enum boundary');
    if(edges[0]!.namespace||edges[0]!.reexport)fail('plain import form');
    return {id:'plain-'+i,...requirement,edge_sha256:edges[0]!.edge_sha256};
   });
   const closure=boundary.roots.find(r=>r.selector===node.selector)??fail('missing Enum closure');
   same(closure.module_paths,[definition_path,relative_path,runtime_path].sort(),'plain Enum closure');
   const valueContract=sha256(getReconciledSource('factory'));
   const expected={id:'initialize',calls:[{provider:runtime_path,method:'defineEnum',arity:1,input:members,result:{members,frozen:true},input_changed:false}],
    reads:members.map(([name,value])=>({provider:node.selector,member:name,value})),
    outcome:{definition_owned:true,definition_frozen:true,values_frozen:true,members:members.map(([name,value])=>({name,variant:value,key:part(node.selector)+part(valueContract)+part(value!),owned:true,frozen:true,singleton:true}))},getter_reads:0,input_changed:false};
   const common={selector:node.selector,kind:node.kind,adapter:'plain-enum' as const,relative_path,callable,definition_path,definition_symbol,runtime_path,protocol};
   const row={...common,state:'ready' as const,
    module_paths:closure.module_paths,modules:closure.module_paths.map(p=>boundary.modules.find(m=>m.relative_path===p)!),cases:[{id:'initialize',expected}]};
   if(members.length>65536||Buffer.byteLength(canonicalJson(row))>8388608)return {...common,state:'not_evaluable' as const,reason:'plain Enum producer family capacity'};
   return row;
  }
  const occurrences:{id:string;type:Extract<TypedType,{kind:'named'}>;target_path:string;symbol:string}[]=[];
  const declare=(t:TypedType,p:string[]):void=>{
   if(t.kind==='named'){occurrences.push({id:canonicalJson(p),type:t,target_path:nativePath(t.selector),symbol:pascal(t.selector.split(':')[1]!)+'ValueComponent'});return;}
   if(t.kind==='sum'){for(const v of ordered(t.variants))if(v.payload)declare(v.payload,[...p,'variant:'+v.name]);}
   else if('element'in t)declare(t.element,[...p,t.kind]);
  };
  declare(shape,[]);
  const edges=boundary.edges.filter(e=>e.importer_path===relative_path&&e.category==='generated-runtime'&&e.names.some(n=>n.endsWith('ValueComponent')));
  same(edges.map(e=>({target_path:e.target_path,names:e.names})),occurrences.map(o=>({target_path:o.target_path,names:[o.symbol]})),'source-owned import occurrences');
  for(const e of edges)if(e.namespace||e.reexport)fail('owned import form');
  const protocol=occurrences.map((o,i)=>({...o,edge_sha256:edges[i]!.edge_sha256}));
  const common={selector:node.selector,kind:node.kind,adapter:'sum' as const,relative_path,callable,protocol,shape};
  if(!protocol.length)return {...common,state:'inapplicable' as const,reason:'no named payload runtime imports'};
  const unmet=(reason:string)=>({...common,state:'not_evaluable' as const,reason});
  try{
   const ctx=createOwnedValueContext(node,graph,plan),root=ctx.root;if(root.kind!=='Enum'||root.plain)fail('payload sum root');
   const records=ctx.samples(ctx.rootShape);
   const closure=boundary.roots.find(r=>r.selector===node.selector)??fail('missing root closure');
   same(ctx.module_paths,closure.module_paths,'sum closure');
   for(const d of Object.values(ctx.dependencies))same(d.relative_path,nativePath(d.selector),'source-derived provider path');
   const leaves=(record:SumRecipe):Leaf[]=>{
    const result:Leaf[]=[];
    const walk=(t:TypedType,r:SumRecipe,p:Location,schema:string[]):void=>{
     if(t.kind==='named'){result.push({type:t,recipe:r,location:p,occurrence:canonicalJson(schema)});return;}
     if(t.kind==='optional'){if(r.tag!=='null')walk(t.element,r,p,[...schema,t.kind]);}
     else if(t.kind==='list'||t.kind==='set')r.items!.forEach((x,i)=>walk(t.element,x,[...p,i],[...schema,t.kind]));
     else if(t.kind==='sum'){const v=t.variants.find(v=>v.name===r.variant)!;if(v.payload)walk(v.payload,r.payload!,[...p,'payload'],[...schema,'variant:'+v.name]);}
    };
    walk(shape,record,[],[]);return result;
   };
   const replace=(record:SumRecipe,target:Location):SumRecipe=>{
    const walk=(t:TypedType,r:SumRecipe,p:Location):SumRecipe=>{
     if(canonicalJson(p)===canonicalJson(target))return {tag:'bad',mode:negativeMode,base:r};
     if(t.kind==='optional')return r.tag==='null'?r:walk(t.element,r,p);
     if(t.kind==='list'||t.kind==='set')return {...r,items:r.items!.map((x,i)=>walk(t.element,x,[...p,i]))};
     if(t.kind==='sum'){const v=t.variants.find(v=>v.name===r.variant)!;return v.payload?{...r,payload:walk(v.payload,r.payload!,[...p,'payload'])}:r;}
     return r;
    };
    return walk(shape,record,[]);
   };
   const cases:{id:string;recipe:SumRecipe;expected:unknown}[]=[],seen=new Set<string>(),visits=new Map<string,Set<string>>();
   let totalCalls=0,negativeMode='';
   const add=(recipe:SumRecipe)=>{
    const id=canonicalJson(recipe);if(seen.has(id))return;seen.add(id);
    if(cases.length>=4096)throw new WitnessUnavailable('value-producer case capacity');
    const all=leaves(recipe),calls:Call[]=[];
    const alias=(leaf:Leaf)=>{
     const r=leaf.recipe,d=ctx.dependencies[leaf.type.selector]!;
     return r.tag!=='bad'&&d.kind==='Enum'&&d.plain?'enum:'+leaf.type.selector+':'+r.variant:canonicalJson(leaf.location);
    };
    const inputPaths=(p:Location)=>{
     const leaf=all.find(l=>canonicalJson(l.location)===canonicalJson(p))??fail('source argument location');
     return all.filter(l=>alias(l)===alias(leaf)).map(l=>l.location).sort((a,b)=>canonicalJson(a)<canonicalJson(b)?-1:1);
    };
    const emit=(t:Extract<TypedType,{kind:'named'}>,r:SumRecipe,p:Location,method:Call['method'],result:Call['result'])=>{
     calls.push({provider:t.selector,method,arity:1,input_paths:inputPaths(p),result});
     if(method==='isOwned'){const leaf=all.find(l=>canonicalJson(l.location)===canonicalJson(p))!;if(!visits.has(leaf.occurrence))visits.set(leaf.occurrence,new Set());visits.get(leaf.occurrence)!.add(r.tag==='bad'?r.mode!:'owned');}
    };
    const providerKey=(t:Extract<TypedType,{kind:'named'}>,r:SumRecipe)=>{
     const d=ctx.dependencies[t.selector]!;
     return d.kind!=='Enum'?ctx.ref(t,r).owned_key!:part(t.selector)+part(ctx.valueContract)+part(d.plain?r.variant!:ctx.ref({kind:'sum',variants:d.contract.variants},r.input!).key);
    };
    const key=(t:TypedType,r:SumRecipe,p:Location):string=>{
     if(t.kind==='named'){const value=providerKey(t,r);emit(t,r,p,'key',value);return ctx.ref(t,r).key;}
     if(t.kind==='optional')return r.tag==='null'?ctx.ref(t,r).key:part('Optional')+part('present')+part(key(t.element,r,p));
     // Collection and inline-sum protocols retain the key formed during normalization.
     return ctx.ref(t,r).key;
    };
    const normalize=(t:TypedType,r:SumRecipe,p:Location):boolean=>{
     if(t.kind==='named'){const owned=r.tag!=='bad';emit(t,r,p,'isOwned',owned);return owned;}
     if(t.kind==='optional')return r.tag==='null'||normalize(t.element,r,p);
     if(t.kind==='list'||t.kind==='set'){for(const [i,x]of r.items!.entries()){if(!normalize(t.element,x,[...p,i]))return false;key(t.element,x,[...p,i]);}return true;}
     if(t.kind==='sum'){const v=t.variants.find(v=>v.name===r.variant)!;if(v.payload){if(!normalize(v.payload,r.payload!,[...p,'payload']))return false;key(v.payload,r.payload!,[...p,'payload']);}return true;}
     return true;
    };
    const valid=normalize(shape,recipe,[]);
    let outcome:unknown;
    if(!valid){
     const rejected=all.find(l=>l.recipe.tag==='bad')??fail('missing rejected leaf'),d=ctx.dependencies[rejected.type.selector]!;
     outcome={error:{name:'TypeError',message:d.kind==='Entity'?'UNOWNED_ENTITY':d.kind==='Value Object'?'UNOWNED_COMPONENT':d.plain?'UNOWNED_ENUM_CASE':'UNOWNED_SUM_CASE'}};
    }else{
     const value=ctx.ref(shape,recipe);
     outcome={value_key:part(node.selector)+part(ctx.valueContract)+part(value.key),value_view:value.view,owned:true,frozen:true};
    }
    totalCalls+=calls.length;if(totalCalls>65536)throw new WitnessUnavailable('value-producer call capacity');
    const caseId='sum-'+cases.length;cases.push({id:caseId,recipe,expected:{id:caseId,outcome,calls,getter_reads:0,input_changed:false}});
   };
   for(const record of records){
    add(record);
    for(const leaf of leaves(record))for(const mode of ['raw-named','clone-named','foreign-named']){
     negativeMode=mode;add(replace(record,leaf.location));
    }
   }
   for(const o of protocol)if(['owned','raw-named','clone-named','foreign-named'].some(mode=>!visits.get(o.id)?.has(mode)))return unmet('named payload occurrence lacks complete ownership witnesses:'+o.id);
   const row={...common,state:'ready' as const,dependencies:ctx.dependencies,baseline:records[0]!,module_paths:ctx.module_paths,
    modules:ctx.module_paths.map(p=>boundary.modules.find(m=>m.relative_path===p)!),cases,
    ownership_coverage:protocol.map(o=>({occurrence:o.id,edge_sha256:o.edge_sha256,modes:[...visits.get(o.id)!].sort()}))};
   if(Buffer.byteLength(canonicalJson(row))>8388608)return unmet('value-producer serialized family capacity');return row;
  }catch(e){if(isWitnessUnavailable(e))return unmet(e.message);throw e;}
 });
 const coverage=boundary.edges.map(e=>({edge_sha256:e.edge_sha256,category:e.category,
  status:e.category!=='generated-runtime'?'non-runtime' as const:rows.some(r=>r.state==='ready'&&r.protocol.some(p=>p.edge_sha256===e.edge_sha256))?'protocol-selected' as const:'not_evaluable' as const}));
 const body={schema_version:'domainspec.cross-generator-value-producer-controls/v1-candidate' as const,definition_sha256:CROSS_GENERATOR_VALUE_PRODUCER_DEFINITION_SHA256,
  boundary_sha256:boundary.boundary_sha256,project_plan_sha256:plan.plan_sha256,source_manifest_sha256:graph.source_manifest.manifest_sha256,rows,coverage,authority_effect:'none' as const};
 const result=freeze({...body,controls_sha256:sha256(canonicalJson(body))});registered.add(result);return result;
}
export type CrossGeneratorValueProducerControls=ReturnType<typeof createCrossGeneratorValueProducerControls>;
export function assertCrossGeneratorValueProducerControls(v:unknown):asserts v is CrossGeneratorValueProducerControls{if(!v||typeof v!=='object'||!registered.has(v))fail('registered controls required');}
export function crossGeneratorValueProducerProbe(c:CrossGeneratorValueProducerControls){
 assertCrossGeneratorValueProducerControls(c);
 return freeze({controls_sha256:c.controls_sha256,rows:c.rows.flatMap(r=>r.state!=='ready'?[]:[r.adapter==='plain-enum'?{
  selector:r.selector,kind:r.kind,adapter:r.adapter,relative_path:r.relative_path,callable:r.callable,definition_path:r.definition_path,definition_symbol:r.definition_symbol,runtime_path:r.runtime_path,
  modules:r.modules.map(m=>({relative_path:m.relative_path,sha256:m.sha256})),cases:r.cases.map(({expected,...input})=>input)
 }:{
  selector:r.selector,kind:r.kind,adapter:r.adapter,relative_path:r.relative_path,callable:r.callable,shape:r.shape,baseline:r.baseline,
  modules:r.modules.map(m=>({relative_path:m.relative_path,sha256:m.sha256})),
  dependencies:Object.fromEntries(Object.entries(r.dependencies).map(([s,d])=>{if(d.kind==='Enum')return[s,d];const {binding,probes,...native}=d;return[s,{...native,probes:[]}];})),
  cases:r.cases.map(({expected,...input})=>input)
 }])});
}
export function checkCrossGeneratorValueProducerObservations(c:CrossGeneratorValueProducerControls,v:unknown){
 assertCrossGeneratorValueProducerControls(c);assertPolicyData(v);
 const rows=c.rows.flatMap(r=>r.state!=='ready'?[]:[{selector:r.selector,cases:r.cases.map(c=>c.expected)}]);if(!rows.length)fail('no executable value-producer family');
 same(v,{controls_sha256:c.controls_sha256,rows},'native observation mismatch');
 return freeze({controls_sha256:c.controls_sha256,tested_producer_count:rows.length,tested_case_count:rows.reduce((n,r)=>n+r.cases.length,0),
  remaining:c.rows.filter(r=>r.state==='not_evaluable').map(r=>({selector:r.selector,reason:r.reason})),
  uncovered_runtime_edge_count:c.coverage.filter(e=>e.status==='not_evaluable').length,public_cross_generator_behavior:'not_evaluable' as const,authority_effect:'none' as const});
}
