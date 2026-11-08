import {MINIMAL_VALUE_CONTEXT_SHA256} from '../generation/reconciled-sources.js';
import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from './project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCompiledCompositionBoundary,type CompiledCompositionBoundary} from './composition-boundary.js';
import {assertCompiledProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,type CompiledProjectFields} from './compiled-field-model.js';
import {decodePublicMapping,checkPublicMapping,isPublicMappingDefinitionSha256,PUBLIC_MAPPING_VALUE_OBJECT_CONTRACT_SHA256,PUBLIC_MAPPING_VERSION} from '../typed-backend/mapping-public.js';
import {decodeNamedInterface} from '../typed-backend/interface.js';
import {canonicalJson,sha256} from './source-manifest.js';
const fail=(m:string):never=>{throw new TypeError('DS_PUBLIC_MAPPING:'+m);};
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};
const checked=new WeakSet<object>();
export type CheckedPublicMapping=ReturnType<typeof compilePublicMapping>;
export function assertCheckedPublicMapping(value:unknown):asserts value is CheckedPublicMapping{
 if(!value||typeof value!=='object'||!checked.has(value))fail('unregistered Mapping');
}
export function compilePublicMapping(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,fields:CompiledProjectFields|null,selector:string,definition:string){
 assertCompiledProjectSnapshot(graph);assertCompiledCompositionBoundary(boundary);if(fields!==null)assertCompiledProjectFields(fields);
 if(typeof definition!=='string'||!isPublicMappingDefinitionSha256(sha256(definition)))return fail('definition drift');
 const definition_sha256=sha256(definition);
 const certificate=createCompiledProjectCertificate(graph);
 if((fields!==null&&(fields.selection.schema_version!==EXACT_PROJECT_FIELD_SELECTION_VERSION||fields.certificate.graph_sha256!==certificate.graph_sha256))||boundary.certificate.graph_sha256!==certificate.graph_sha256)return fail('cross-graph or non-exact fields');
 const node=graph.nodes.find(n=>n.selector===selector);
 if(!node||node.kind!=='Mapping'||(node.body.typed_contract as {schema_version?:string}|undefined)?.schema_version!==PUBLIC_MAPPING_VERSION)return fail('versioned public Mapping required');
 const contract=decodePublicMapping(node.body.typed_contract);
 const interfaces=graph.nodes.filter(n=>n.kind==='Interface'&&n.body.typed_contract!==undefined).map(n=>({selector:n.selector,contract:decodeNamedInterface(n.body.typed_contract)}));
 const bindings=checkPublicMapping(contract,fields?.model.declarations??[],interfaces,definition_sha256===PUBLIC_MAPPING_VALUE_OBJECT_CONTRACT_SHA256);
 const source=(selector:string)=>{
  const [feature,id]=selector.split(':'),relative_path='specs/'+feature+'/nodes/'+id+'.json';
  const entry=graph.source_manifest.sources.find(s=>s.relative_path===relative_path)??fail('source evidence');
  return {selector,relative_path,sha256:entry.sha256,pointer:'/body/typed_contract'};
 };
 const body={schema_version:'domainspec.checked-public-mapping/v1-candidate' as const,selector,contract,bindings,certificate,
  boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields?.compilation_sha256??null,...(fields===null?{minimal_context_sha256:MINIMAL_VALUE_CONTEXT_SHA256}:{}),definition_sha256,
  source:source(selector),interfaces:bindings.interface_selectors.map(selector=>({source:source(selector),contract:interfaces.find(i=>i.selector===selector)!.contract})),
  target_owner:node.body.target,graph_relationship:'maps',member_relationship:'exposes',runtime_execution:'not-performed',authority_effect:'none' as const};
 const value=freeze({...body,mapping_sha256:sha256(canonicalJson(body))});checked.add(value);return value;
}
