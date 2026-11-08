import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from './project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {normalizeCompositionOntology} from './composition-ontology.js';
import {canonicalJson,sha256} from './source-manifest.js';

// DSR-011 candidate projection. Never executes a binding or infers a domain edge.
// Scope and evidence: PCR/COMPOSITION-BOUNDARY.md.
export const COMPOSITION_BOUNDARY_VERSION='domainspec.composition-boundary-selection/v1-candidate';
export const COMPOSITION_BOUNDARY_CONTRACT_SHA256='2f11a5a0a33befaf6e074c389f1231d1de3d85abb2690302ac163cbfffb88fde';
export interface CompositionBoundarySelection {
  readonly schema_version:typeof COMPOSITION_BOUNDARY_VERSION;
  readonly graph_sha256:string;
  readonly contract_sha256:typeof COMPOSITION_BOUNDARY_CONTRACT_SHA256;
}
const fail=(message:string):never=>{throw new Error('DS_COMPOSITION_BOUNDARY:'+message);};
const compare=(a:unknown,b:unknown)=>{const x=canonicalJson(a),y=canonicalJson(b);return x<y?-1:x>y?1:0;};
const freeze=<T>(value:T):T=>{
  if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.values(value).forEach(freeze);Object.freeze(value);}return value;
};
const copy=<T>(value:T):T=>structuredClone(value);
const checkedBoundaries=new WeakSet<object>();
export type CompiledCompositionBoundary=ReturnType<typeof compileCompositionBoundary>;
export function assertCompiledCompositionBoundary(value:unknown):asserts value is CompiledCompositionBoundary{
  if(!value||typeof value!=='object'||!checkedBoundaries.has(value))fail('unvalidated boundary');
}

/** Consume only a registered checked snapshot and exact candidate selection.
 * This is a lossless representation boundary, not a new dataflow type checker.
 */
export function compileCompositionBoundary(graph:CompiledProjectGraph,selection:CompositionBoundarySelection,contract:string){
  assertCompiledProjectSnapshot(graph);
  if(!selection||typeof selection!=='object'||Array.isArray(selection)||![Object.prototype,null].includes(Object.getPrototypeOf(selection)))fail('selection object required');
  const descriptors=Object.getOwnPropertyDescriptors(selection),keys=['schema_version','graph_sha256','contract_sha256'];
  if(Reflect.ownKeys(descriptors).length!==keys.length||Reflect.ownKeys(descriptors).some(k=>typeof k!=='string'||!keys.includes(k))||
    Object.values(descriptors).some(d=>!Object.hasOwn(d,'value')||!d.enumerable))fail('closed data selection required');
  if(selection.schema_version!==COMPOSITION_BOUNDARY_VERSION||selection.contract_sha256!==COMPOSITION_BOUNDARY_CONTRACT_SHA256||
    typeof contract!=='string'||sha256(contract)!==COMPOSITION_BOUNDARY_CONTRACT_SHA256)fail('selection or contract drift');
  const certificate=createCompiledProjectCertificate(graph);
  if(selection.graph_sha256!==certificate.graph_sha256)fail('stale graph selection');
  const source=(relative_path:string)=>{
    const row=graph.source_manifest.sources.find(s=>s.relative_path===relative_path)??fail('missing source evidence:'+relative_path);
    return {relative_path:row.relative_path,sha256:row.sha256,source_type:row.source_type,source_id:row.source_id};
  };
  const domainNodes=graph.nodes.map(n=>({selector:n.selector,kind:n.kind,meta_type_id:n.meta_type_id,
    source:source('specs/'+n.feature_id+'/nodes/'+n.node_id+'.json')})).sort(compare);
  const domainEdges=graph.relationships.map(edge=>({
    ...copy(edge),source_evidence:source(edge.scope==='project'?'edges/'+edge.edge_id+'.json':'specs/'+edge.source.feature_id+'/edges/'+edge.edge_id+'.json'),
  })).sort(compare);
  const coreContracts=graph.nodes.filter(n=>n.body.typed_contract!==undefined).map(n=>({
    owner:{space:'domain' as const,selector:n.selector},kind:n.kind,
    source:{...source('specs/'+n.feature_id+'/nodes/'+n.node_id+'.json'),pointer:'/body/typed_contract'},
    form:'typed-core-contract' as const,contract:copy(n.body.typed_contract),
  })).sort(compare);
  const untyped=graph.nodes.filter(n=>n.body.typed_contract===undefined).map(n=>n.selector).sort();
  const compositionGraphs=(graph.compositions??[]).map(c=>{
    const ontology=normalizeCompositionOntology(c.source.ontology),evidence=source('compositions/'+c.id+'.json');
    return {composition_id:c.id,source:evidence,source_format:ontology.source_format,authored_schema:c.source.ontology.schema_version,
      nodes:ontology.nodes.map((n:{id:string;name:string;source:unknown;meaning:unknown})=>({
        identity:{space:'composition' as const,composition_id:c.id,local_id:n.id},
        name:n.name,meaning:copy(n.meaning),source:{...evidence,pointer:'/ontology/nodes',authored:copy(n.source)},
      })).sort(compare),
      references:ontology.references.map((r:{source:string;target:string;role:string;evidence:unknown})=>({
        source:{space:'composition' as const,composition_id:c.id,local_id:r.source},
        target:{space:'composition' as const,composition_id:c.id,local_id:r.target},
        role:r.role,evidence:{...evidence,pointer:'/ontology/references',authored:copy(r.evidence)},
      })).sort(compare)};
  }).sort(compare);
  const compositionContracts=(graph.compositions??[]).map(c=>({
    owner:{space:'composition' as const,composition_id:c.id},
    source:{...source('compositions/'+c.id+'.json'),pointer:'/contract'},
    form:'declarative-function-contract' as const,contract:copy(c.source.contract),
  })).sort(compare);
  const bridges=(graph.compositions??[]).flatMap(c=>Object.entries(c.source.core_bindings as Record<string,{selector:string;fields:Record<string,string>}>).map(([name,b])=>({
    source:{space:'composition' as const,composition_id:c.id,name},
    target:{space:'domain' as const,selector:b.selector},fields:copy(b.fields),
    evidence:{...source('compositions/'+c.id+'.json'),pointer:'/core_bindings/'+name},
  }))).sort(compare);
  const body={schema_version:'domainspec.compiled-composition-boundary/v1-candidate' as const,selection:copy(selection),certificate,
    domain_graph:{nodes:domainNodes,relationships:domainEdges},
    composition_graphs:compositionGraphs,
    value_bindings:{core_contracts:coreContracts,composition_contracts:compositionContracts,untyped_domain_nodes:untyped},
    bridges,
    coverage:{domain_nodes:domainNodes.length,domain_relationships:domainEdges.length,compositions:compositionGraphs.length,
      composition_nodes:compositionGraphs.reduce((n,c)=>n+c.nodes.length,0),composition_references:compositionGraphs.reduce((n,c)=>n+c.references.length,0),
      core_typed_contracts:coreContracts.length,composition_contracts:compositionContracts.length,untyped_domain_nodes:untyped.length,bridges:bridges.length},
    validation_ceiling:'checked-source-projection-not-execution-or-new-type-proof' as const,authority_effect:'none' as const};
  const result=freeze({...body,boundary_sha256:sha256(canonicalJson(body))});
  checkedBoundaries.add(result);
  return result;
}
