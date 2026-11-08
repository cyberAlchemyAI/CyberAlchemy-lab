import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {CrossGeneratorBoundary} from './reconciled-cross-generator-boundary.js';
import {createCrossGeneratorOperationSurface} from './reconciled-cross-generator-operation-surface.js';
import {createOperationProtocolReference} from './reconciled-cross-generator-operation-reference.js';
import {createOperationCases,operationVectorCaseIds,isOperationCapacity,OperationCasesUnavailable} from './reconciled-operation-cases.js';
import {createOperationProtocolSelection} from './reconciled-operation-protocol-selection.js';
import type {FactRecipe} from './reconciled-rule-facts.js';
import {assertPolicyData} from '../typed-backend/policy-rules.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';

export const CROSS_GENERATOR_OPERATION_PROTOCOL_SHA256='d40ea336a6af8673e69a4a958ee7f9885fdef26f890a50dd863e0d294fbaa56d';
const registered=new WeakSet<object>();
const fail=(s:string):never=>{throw new TypeError('CROSS_GENERATOR_OPERATION:'+s);};
function freeze<T>(v:T):T{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
export function expandOperationProtocolRecipe(recipes:readonly FactRecipe[],id:number):FactRecipe{
 let visits=0;const active=new Set<number>();
 const read=(r:FactRecipe,depth=0):FactRecipe=>{
  if(++visits>65536||depth>64)throw new OperationCasesUnavailable('Operation protocol recipe capacity');
  if(r.tag==='ref'){
   const i=Number(r.value);if(!Number.isSafeInteger(i)||i<0||i>=recipes.length||active.has(i))fail('recipe reference');
   active.add(i);const value=read(recipes[i]!,depth);active.delete(i);return value;
  }
  return {...r,...(r.base?{base:read(r.base,depth+1)}:{}),...(r.input?{input:read(r.input,depth+1)}:{}),...(r.payload?{payload:read(r.payload,depth+1)}:{}),
   ...(r.items?{items:r.items.map(v=>read(v,depth+1))}:{}),...(r.fields?{fields:Object.fromEntries(Object.entries(r.fields).map(([k,v])=>[k,read(v,depth+1)]))}:{})};
 };return read({tag:'ref',value:String(id)});
}
export function createCrossGeneratorOperationControls(graph:CompiledProjectGraph,plan:ReconciledProjectPlan,boundary:CrossGeneratorBoundary,definition:string,protocolDefinition:string){
 if(typeof protocolDefinition!=='string'||sha256(protocolDefinition)!==CROSS_GENERATOR_OPERATION_PROTOCOL_SHA256)fail('protocol definition drift');
 const surface=createCrossGeneratorOperationSurface(graph,plan,boundary,definition);
 const rows=surface.rows.map(row=>{
  const direct=boundary.edges.filter(e=>e.importer_path===row.provider_path&&e.category==='generated-runtime').map(e=>e.edge_sha256);
  try{
   const reference=createOperationProtocolReference(graph,plan,surface,row.selector),source=createOperationCases(graph,plan,reference.binding);
   const vectorIds=new Set(operationVectorCaseIds(source)),selector=createOperationProtocolSelection(graph,plan,reference.binding);
   let calls=reference.initialization.length,bytes=Buffer.byteLength(canonicalJson(source.recipes));
   const cases=source.cases.map(c=>{
    const data=JSON.parse(c.values[0]!),input=expandOperationProtocolRecipe(source.recipes,data.input);
    const fixture={reads:data.reads.map((r:any)=>({...r,value:expandOperationProtocolRecipe(source.recipes,r.value)})),clocks:data.clocks};
    const observed=reference.expected(c.id,input,fixture,data.mode);
    if(c.expected.kind!=='value'||canonicalJson(observed.semantic)!==c.expected.value)fail('source outcome mismatch');
    calls+=observed.calls.length;const result={id:c.id,data,expected:observed};bytes+=Buffer.byteLength(canonicalJson(result));
    if(calls>65536||bytes>8388608)throw new OperationCasesUnavailable('Operation protocol family capacity');
    selector.consider(c.id,input,observed,vectorIds.has(c.id));
    return result;
   });
   if(!cases.length||cases.length>4096)throw new OperationCasesUnavailable('Operation protocol case capacity');
   const identity={operation:true,events:row.modules.filter(m=>m.role==='event-wrapper').map(m=>({selector:m.selector,original:true}))};
   const selected=selector.select(cases);
   return {...row,state:'ready' as const,adapter:'operation-protocol' as const,direct_edges:direct,initialization:reference.initialization,identity,cases:selected.cases,selection:selected.selection,recipes:source.recipes};
  }catch(e){if(isOperationCapacity(e))return {...row,state:'not_evaluable' as const,reason:e.message,direct_edges:direct};throw e;}
 });
 const covered=new Set(rows.flatMap(r=>r.state==='ready'?r.direct_edges:[]));
 const body={schema_version:'domainspec.cross-generator-operation-controls/v2-candidate' as const,definition_sha256:surface.definition_sha256,protocol_sha256:CROSS_GENERATOR_OPERATION_PROTOCOL_SHA256,
  project_plan_sha256:plan.plan_sha256,source_manifest_sha256:surface.source_manifest_sha256,boundary_sha256:boundary.boundary_sha256,surface_sha256:surface.surface_sha256,rows,
  coverage:boundary.edges.map(e=>({edge_sha256:e.edge_sha256,category:e.category,state:covered.has(e.edge_sha256)?'direct-protocol-selected':'not_evaluable'})),authority_effect:'none' as const};
 const result=freeze({...body,controls_sha256:sha256(canonicalJson(body))});registered.add(result);return result;
}
export type CrossGeneratorOperationControls=ReturnType<typeof createCrossGeneratorOperationControls>;
export function assertCrossGeneratorOperationControls(v:unknown):asserts v is CrossGeneratorOperationControls{
 if(!v||typeof v!=='object'||!registered.has(v))fail('registered controls required');
}
export function crossGeneratorOperationProbe(controls:CrossGeneratorOperationControls){
 assertCrossGeneratorOperationControls(controls);
 return {controls_sha256:controls.controls_sha256,protocol_sha256:controls.protocol_sha256,rows:controls.rows.flatMap(r=>r.state!=='ready'?[]:[{
  selector:r.selector,adapter:r.adapter,relative_path:r.relative_path,provider_path:r.provider_path,callable:r.callable,modules:r.modules,
  recipes:r.recipes,cases:r.cases.map(c=>({id:c.id,data:c.data}))
 }])};
}
export function checkCrossGeneratorOperationObservations(controls:CrossGeneratorOperationControls,observations:unknown){
 assertCrossGeneratorOperationControls(controls);assertPolicyData(observations);
 const rows=controls.rows.filter(r=>r.state==='ready');
 if(!rows.length)fail('no ready Operation families');
 const expected={controls_sha256:controls.controls_sha256,rows:rows.map(r=>({selector:r.selector,initialization:r.initialization,identity:r.identity,descriptor:r.descriptor,cases:r.cases.map(c=>({id:c.id,...c.expected}))}))};
 if(canonicalJson(observations)!==canonicalJson(expected))fail('observation mismatch');
 return {tested_operation_count:rows.length,tested_case_count:rows.reduce((n,r)=>n+r.cases.length,0),tested_call_count:rows.reduce((n,r)=>n+r.initialization.length+r.cases.reduce((m,c)=>m+c.expected.calls.length,0),0),
  remaining:controls.rows.filter(r=>r.state!=='ready').map(r=>({selector:r.selector,reason:r.reason})),uncovered_runtime_edge_count:controls.coverage.filter(e=>e.category==='generated-runtime'&&e.state==='not_evaluable').length,
  public_cross_generator_behavior:'not_evaluable' as const,retained_execution:'not_evaluable' as const,authority_effect:'none' as const};
}
