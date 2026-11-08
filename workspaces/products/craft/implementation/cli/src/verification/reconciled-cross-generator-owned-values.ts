import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertReconciledProjectPlan,type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {assertCrossGeneratorBoundary,type CrossGeneratorBoundary} from './reconciled-cross-generator-boundary.js';
import {decodeTypedRecordContract,decodeTypedSumContract,type TypedType} from '../typed-operation/contracts.js';
import {createOwnedValueContext,isWitnessUnavailable,WitnessUnavailable,type SumRecipe} from './reconciled-value-context.js';
import {evaluateRecordWitness} from './reconciled-record-witness.js';
import {assertPolicyData} from '../typed-backend/policy-rules.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';

export const CROSS_GENERATOR_OWNED_VALUES_DEFINITION_SHA256 = 'e404d6f1ffe4985687aea11b298c64f396b0e442a0931e8d005ce60af1484faf';
const fail=(s:string):never=>{throw new TypeError('CROSS_GENERATOR_OWNED_VALUES:'+s);};
const same=(a:unknown,b:unknown,s:string)=>{if(canonicalJson(a)!==canonicalJson(b))fail(s);};
const pascal=(s:string)=>s.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
const part=(s:string)=>s.length+':'+s;
const registered=new WeakSet<object>();
function freeze<T>(v:T):T {if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
type Location=readonly (string|number)[];
type Leaf={type:Extract<TypedType,{kind:'named'}>;recipe:SumRecipe;location:Location;occurrence:string};
type Call={provider:string;method:'isOwned'|'key';arity:number;input_paths:Location[];result:boolean|string};
const ordered=<T extends {name:string}>(xs:readonly T[])=>[...xs].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0);

/** Source-derived owned field protocols, not generated-descriptor expectations. */
export function createCrossGeneratorOwnedValueControls(graph:CompiledProjectGraph,plan:ReconciledProjectPlan,boundary:CrossGeneratorBoundary,definition:string){
 if(typeof definition!=='string'||sha256(definition)!==CROSS_GENERATOR_OWNED_VALUES_DEFINITION_SHA256)fail('definition drift');
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
 const rows=graph.nodes.filter(n=>n.kind==='Entity'||n.kind==='Value Object').map(node=>{
  const fields=ordered(decodeTypedRecordContract(node.body.typed_contract).properties),relative_path=nativePath(node.selector),callable='create'+pascal(node.node_id)+'Factory';
  const occurrences:{id:string;type:Extract<TypedType,{kind:'named'}>;target_path:string;symbol:string}[]=[];
  const declare=(t:TypedType,p:string[]):void=>{
   if(t.kind==='named'){occurrences.push({id:canonicalJson(p),type:t,target_path:nativePath(t.selector),symbol:pascal(t.selector.split(':')[1]!)+'ValueComponent'});return;}
   if(t.kind==='sum'){for(const v of ordered(t.variants))if(v.payload)declare(v.payload,[...p,'variant:'+v.name]);}
   else if('element'in t)declare(t.element,[...p,t.kind]);
  };
  fields.forEach(f=>declare(f.type,[f.name]));
  const edges=boundary.edges.filter(e=>e.importer_path===relative_path&&e.category==='generated-runtime'&&e.names.some(n=>n.endsWith('ValueComponent')));
  same(edges.map(e=>({target_path:e.target_path,names:e.names})),occurrences.map(o=>({target_path:o.target_path,names:[o.symbol]})),'source-owned import occurrences');
  for(const e of edges)if(e.namespace||e.reexport)fail('owned import form');
  const protocol=occurrences.map((o,i)=>({...o,edge_sha256:edges[i]!.edge_sha256}));
  const common={selector:node.selector,kind:node.kind,relative_path,callable,protocol,fields};
  if(!protocol.length)return {...common,state:'inapplicable' as const,reason:'no owned field runtime imports'};
  const unmet=(reason:string)=>({...common,state:'not_evaluable' as const,reason});
  try{
   const ctx=createOwnedValueContext(node,graph,plan),root=ctx.root;if(root.kind==='Enum')fail('factory root');
   const records=ctx.samples(ctx.rootShape);
   const closure=boundary.roots.find(r=>r.selector===node.selector)??fail('missing root closure');
   same(ctx.module_paths,closure.module_paths,'owned closure');
   for(const d of Object.values(ctx.dependencies))same(d.relative_path,nativePath(d.selector),'source-derived provider path');
   const leaves=(record:SumRecipe):Leaf[]=>{
    const result:Leaf[]=[];
    const walk=(t:TypedType,r:SumRecipe,p:Location,schema:string[]):void=>{
     if(t.kind==='named'){result.push({type:t,recipe:r,location:p,occurrence:canonicalJson(schema)});return;}
     if(t.kind==='optional'){if(r.tag!=='null')walk(t.element,r,p,[...schema,t.kind]);}
     else if(t.kind==='list'||t.kind==='set')r.items!.forEach((x,i)=>walk(t.element,x,[...p,i],[...schema,t.kind]));
     else if(t.kind==='sum'){const v=t.variants.find(v=>v.name===r.variant)!;if(v.payload)walk(v.payload,r.payload!,[...p,'payload'],[...schema,'variant:'+v.name]);}
    };
    fields.forEach(f=>walk(f.type,record.fields![f.name]!,[f.name],[f.name]));return result;
   };
   const replace=(record:SumRecipe,target:Location):SumRecipe=>{
    const walk=(t:TypedType,r:SumRecipe,p:Location):SumRecipe=>{
     if(canonicalJson(p)===canonicalJson(target))return {tag:'bad',mode:negativeMode,base:r};
     if(t.kind==='optional')return r.tag==='null'?r:walk(t.element,r,p);
     if(t.kind==='list'||t.kind==='set')return {...r,items:r.items!.map((x,i)=>walk(t.element,x,[...p,i]))};
     if(t.kind==='sum'){const v=t.variants.find(v=>v.name===r.variant)!;return v.payload?{...r,payload:walk(v.payload,r.payload!,[...p,'payload'])}:r;}
     return r;
    };
    return {...record,fields:Object.fromEntries(fields.map(f=>[f.name,walk(f.type,record.fields![f.name]!,[f.name])]))};
   };
   const cases:{id:string;route:string;recipe:SumRecipe;previous?:SumRecipe;expected:unknown}[]=[],seen=new Set<string>(),visits=new Map<string,Set<string>>();
   let totalCalls=0,negativeMode='';
   const add=(recipe:SumRecipe,route:string)=>{
    const id=canonicalJson({recipe,route});if(seen.has(id))return;seen.add(id);
    if(cases.length>=4096)throw new WitnessUnavailable('owned-value case capacity');
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
    let valid=true;for(const f of fields)if(!normalize(f.type,recipe.fields![f.name]!,[f.name])){valid=false;break;}
    let outcome:unknown;
    if(!valid)outcome={ok:false,failure_codes:['INVALID_FIELDS'],trace:{route,phases:['normalize'],validators:[]},value_key:null,value_view:null};
    else{
     const expected=evaluateRecordWitness(root as Exclude<typeof root,{kind:'Enum'}>,ctx.reference,recipe);
     if(!expected.ok)fail('source-valid owned witness rejected');
     for(const f of fields)if(node.kind==='Value Object'||f.identity)key(f.type,recipe.fields![f.name]!,[f.name]);
     const value=ctx.ref(ctx.rootShape,recipe);
     outcome={...expected,trace:{...expected.trace,route},value_key:value.owned_key,value_view:value.view};
    }
    totalCalls+=calls.length;if(totalCalls>65536)throw new WitnessUnavailable('owned-value call capacity');
    const caseId='owned-'+cases.length;cases.push({id:caseId,route,recipe,...(route==='transition'?{previous:valid?recipe:records[0]!}:{}),expected:{id:caseId,outcome,calls,getter_reads:0,input_changed:false}});
   };
   for(const record of records){
    for(const route of ['create','reconstruct',...(node.kind==='Entity'?['transition']:[])])add(record,route);
    for(const leaf of leaves(record))for(const mode of ['raw-named','clone-named','foreign-named']){
     negativeMode=mode;const invalid=replace(record,leaf.location);for(const route of ['create','reconstruct',...(node.kind==='Entity'?['transition']:[])])add(invalid,route);
    }
   }
   for(const o of protocol)if(['owned','raw-named','clone-named','foreign-named'].some(mode=>!visits.get(o.id)?.has(mode)))return unmet('owned field occurrence lacks complete ownership witnesses:'+o.id);
   const row={...common,state:'ready' as const,shape:ctx.rootShape,dependencies:ctx.dependencies,baseline:records[0]!,module_paths:ctx.module_paths,
    modules:ctx.module_paths.map(p=>boundary.modules.find(m=>m.relative_path===p)!),cases,
    ownership_coverage:protocol.map(o=>({occurrence:o.id,edge_sha256:o.edge_sha256,modes:[...visits.get(o.id)!].sort()}))};
   if(Buffer.byteLength(canonicalJson(row))>8388608)return unmet('owned-value serialized family capacity');return row;
  }catch(e){if(isWitnessUnavailable(e))return unmet(e.message);throw e;}
 });
 const coverage=boundary.edges.map(e=>({edge_sha256:e.edge_sha256,category:e.category,
  status:e.category!=='generated-runtime'?'non-runtime' as const:rows.some(r=>r.state==='ready'&&r.protocol.some(p=>p.edge_sha256===e.edge_sha256))?'protocol-selected' as const:'not_evaluable' as const}));
 const body={schema_version:'domainspec.cross-generator-owned-value-controls/v1-candidate' as const,definition_sha256:CROSS_GENERATOR_OWNED_VALUES_DEFINITION_SHA256,
  boundary_sha256:boundary.boundary_sha256,project_plan_sha256:plan.plan_sha256,source_manifest_sha256:graph.source_manifest.manifest_sha256,rows,coverage,authority_effect:'none' as const};
 const result=freeze({...body,controls_sha256:sha256(canonicalJson(body))});registered.add(result);return result;
}
export type CrossGeneratorOwnedValueControls=ReturnType<typeof createCrossGeneratorOwnedValueControls>;
export function assertCrossGeneratorOwnedValueControls(v:unknown):asserts v is CrossGeneratorOwnedValueControls{if(!v||typeof v!=='object'||!registered.has(v))fail('registered controls required');}
export function crossGeneratorOwnedValueProbe(c:CrossGeneratorOwnedValueControls){
 assertCrossGeneratorOwnedValueControls(c);
 return freeze({controls_sha256:c.controls_sha256,rows:c.rows.flatMap(r=>r.state!=='ready'?[]:[{
  selector:r.selector,kind:r.kind,relative_path:r.relative_path,callable:r.callable,shape:r.shape,fields:r.fields,baseline:r.baseline,
  modules:r.modules.map(m=>({relative_path:m.relative_path,sha256:m.sha256})),
  dependencies:Object.fromEntries(Object.entries(r.dependencies).map(([s,d])=>{if(d.kind==='Enum')return[s,d];const {binding,probes,...native}=d;return[s,{...native,probes:[]}];})),
  cases:r.cases.map(({expected,...input})=>input)
 }])});
}
export function checkCrossGeneratorOwnedValueObservations(c:CrossGeneratorOwnedValueControls,v:unknown){
 assertCrossGeneratorOwnedValueControls(c);assertPolicyData(v);
 const rows=c.rows.flatMap(r=>r.state!=='ready'?[]:[{selector:r.selector,cases:r.cases.map(c=>c.expected)}]);if(!rows.length)fail('no executable owned-value family');
 same(v,{controls_sha256:c.controls_sha256,rows},'native observation mismatch');
 return freeze({controls_sha256:c.controls_sha256,tested_factory_count:rows.length,tested_case_count:rows.reduce((n,r)=>n+r.cases.length,0),
  remaining:c.rows.filter(r=>r.state==='not_evaluable').map(r=>({selector:r.selector,reason:r.reason})),
  uncovered_runtime_edge_count:c.coverage.filter(e=>e.status==='not_evaluable').length,public_cross_generator_behavior:'not_evaluable' as const,authority_effect:'none' as const});
}
