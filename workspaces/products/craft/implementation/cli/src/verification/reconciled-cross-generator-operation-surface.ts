import path from 'node:path';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertReconciledProjectPlan, type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import type {TypedType} from '../typed-operation/contracts.js';
import {assertCrossGeneratorBoundary, type CrossGeneratorBoundary} from './reconciled-cross-generator-boundary.js';
import {createOperationBinding} from './reconciled-operation-binding.js';
import {deriveCrossGeneratorOperationDependencies} from './reconciled-cross-generator-factory-surface.js';

export const CROSS_GENERATOR_OPERATION_DEFINITION_SHA256 = '0c0dd71a1f05571f972aa21312d2eecf5aaa244d2c459186fe71ec4e4ac2c0b5';
const fail = (message: string): never => {throw new TypeError('CROSS_GENERATOR_OPERATION_SURFACE:' + message);};
const same = (a: unknown, b: unknown, reason: string) => {if (canonicalJson(a) !== canonicalJson(b)) fail(reason);};
const sorted = (values: readonly string[]) => [...new Set(values)].sort();
const name = (selector: string) => selector.split(':')[1]!.split('-').map(w => w[0]!.toUpperCase() + w.slice(1)).join('');
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze);Object.freeze(value);}return value;}
export interface OperationSurfaceImport {
 readonly specifier: string; readonly names: readonly string[]; readonly target_path: string; readonly type_only: boolean; readonly reexport: boolean;
}
export interface OperationSurfaceModule {
 readonly selector: string | null; readonly role: string; readonly relative_path: string; readonly callable: string;
 readonly value_exports: readonly string[]; readonly type_exports: readonly string[]; readonly imports: readonly OperationSurfaceImport[]; readonly sha256: string;
}
const operationTypes = ['OperationInput','OperationValue','OperationOutcome','OperationDependencies','OperationBatch','Transaction','CommitReceipt','ReadRequest','WriteIntent','EventIntent'];
const eventTypes = ['EventInput','EventValue'];
const registered = new WeakSet<object>();

/** Source-derived incidence only. No call, behavioral, native or custody pass is implied. */
export function createCrossGeneratorOperationSurface(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, boundary: CrossGeneratorBoundary, definition: string) {
 if (typeof definition !== 'string' || sha256(definition) !== CROSS_GENERATOR_OPERATION_DEFINITION_SHA256) fail('definition drift');
 assertCompiledProjectSnapshot(graph);assertReconciledProjectPlan(plan);assertCrossGeneratorBoundary(boundary);
 same(createCompiledProjectCertificate(graph), plan.resolved.certificate, 'foreign graph');
 same(boundary.project_plan_sha256, plan.plan_sha256, 'foreign boundary');
 same(boundary.source_manifest_sha256, graph.source_manifest.manifest_sha256, 'foreign source');
 const config = JSON.parse(getReconciledSource('configuration'));
 for (const [kind, role] of [['Operation','application/operations'],['Event','domain/events']])
  if (config.types.find((t: any) => t.kind === kind)?.role !== role) fail('configured native role');
 const nativePath = (selector: string, role: string, suffix = '') => {
  const [feature,id] = selector.split(':');return plan.selection.module_root+'/features/'+feature+'/src/'+(role==='operations'?'application/':'domain/')+role+'/'+id+suffix+'.ts';
 };
 const imp = (from: string, to: string, names: readonly string[], type_only = false, reexport = false): OperationSurfaceImport => {
  const relative = path.posix.relative(path.posix.dirname(from),to).replace(/\.ts$/,'.js');
  return {specifier:relative.startsWith('.')?relative:'./'+relative,names:[...names].sort(),target_path:to,type_only,reexport};
 };
 const rows = graph.nodes.filter(n => n.kind === 'Operation').map(node => {
  const binding = createOperationBinding(node,graph,plan), action = binding.action, b = action.bindings;
  const relative_path = nativePath(node.selector,'operations'), provider = nativePath(node.selector,'operations','.provider');
  same(binding.relative_path,relative_path,'source wrapper path');
  const declarations = new Map(binding.fields?.model.declarations.map(d => [d.selector,d]));
  const dataRoots: string[] = [], imports: OperationSurfaceImport[] = [];
  const initializations: {selector:string;method:'factory';path:string}[] = [], visited = new Set<string>();
  const owned = (type: TypedType, depth = 0): void => {
   if (depth > 64 || visited.size > 65536) fail('owned adapter capacity');
   const key = canonicalJson(type);if (visited.has(key)) return;visited.add(key);
   if (type.kind === 'scalar') return;
   if (type.kind === 'optional' || type.kind === 'list' || type.kind === 'set') {owned(type.element,depth+1);return;}
   if (type.kind === 'sum') {type.variants.forEach(v => {if(v.payload)owned(v.payload,depth+1);});return;}
   const d = declarations.get(type.selector) ?? fail('owned declaration');
   dataRoots.push(type.selector);
   const role = d.kind === 'Enum' ? 'enums' : d.kind === 'Entity' ? 'entities' : 'value-objects';
   const sum = d.kind === 'Enum' && d.contract.variants.some(v => v.payload !== null);
   const target = nativePath(type.selector,role,d.kind === 'Enum' ? sum ? '.sum' : '.component' : '');
   imports.push(imp(provider,target,[d.kind === 'Enum' ? name(type.selector)+'ValueComponent' : 'create'+name(type.selector)+'Factory']));
   if (d.kind === 'Enum') {if(sum)owned({kind:'sum',variants:d.contract.variants},depth+1);}
   else {
    d.contract.properties.forEach(p => owned(p.type,depth+1));
    initializations.push({selector:type.selector,method:'factory',path:target});
   }
  };
  // Provider declarations create the result adapter before the write adapters.
  owned(b.result.type);action.writes.forEach(w => owned({kind:'named',selector:w.target}));
  const modules = new Map<string,OperationSurfaceModule>(deriveCrossGeneratorOperationDependencies(graph,plan,boundary,sorted(dataRoots),action.guards.map(g => g.selector)));
  const ownModule = (selector: string, role: string, p: string, callable: string, value_exports: string[], type_exports: string[], expected: OperationSurfaceImport[]) => {
   if (modules.size >= 8192 || modules.has(p)) fail('module capacity or duplicate');
   const captured = boundary.modules.find(m => m.relative_path === p) ?? fail('missing source module:'+p);
   const artifact = plan.resolved.artifacts.find(a => a.relative_path === p) ?? fail('missing artifact');
   same(captured.qualified_selectors,[selector],'source module owner:'+p);
   same(captured.exports,[...value_exports.map(name => ({name,kind:'value'})),...type_exports.map(name => ({name,kind:'type'}))].sort((a,b) => a.name<b.name?-1:a.name>b.name?1:a.kind<b.kind?-1:1),'source exports:'+p);
   const edges = boundary.edges.filter(e => e.importer_path === p);
   if(edges.some(e => e.namespace || e.category === 'native-standard-library'))fail('unsupported import:'+p);
   same(edges.map(({specifier,names,target_path,type_only,reexport}) => ({specifier,names,target_path,type_only,reexport})),expected,'source imports:'+p);
   if(sha256(artifact.content)!==captured.sha256)fail('artifact drift:'+p);
   modules.set(p,{selector,role,relative_path:p,callable,value_exports:[...value_exports].sort(),type_exports:[...type_exports].sort(),imports:expected,sha256:captured.sha256});
  };
  const eventImports: OperationSurfaceImport[] = [];
  for (const selector of sorted(action.events.map(e => e.target))) {
   const p = nativePath(selector,'events'), implementation = nativePath(selector,'events','.provider'), callable = 'event'+name(selector);
   ownModule(selector,'event-provider',implementation,'make',['make'],eventTypes,[]);
   ownModule(selector,'event-wrapper',p,callable,[callable],eventTypes,[imp(p,implementation,['make']),imp(p,implementation,eventTypes,true,true)]);
   eventImports.push(imp(provider,p,[callable]),imp(provider,p,eventTypes,true));
  }
  const guardImports = action.guards.map(g => imp(provider,nativePath(g.selector,'rules'),['rule'+name(g.selector)]));
  ownModule(node.selector,'operation-provider',provider,'execute',['execute'],[...operationTypes,'OperationFailure'],[...guardImports,...eventImports,...imports]);
  ownModule(node.selector,'operation-wrapper',relative_path,binding.callable,[binding.callable],operationTypes,[imp(relative_path,provider,['execute']),imp(relative_path,provider,operationTypes,true,true)]);
  const pending = [relative_path], seen = new Set<string>();
  while (pending.length) {const p=pending.pop()!;if(seen.has(p))continue;seen.add(p);const m=modules.get(p)??fail('missing derived closure:'+p);m.imports.forEach(i=>pending.push(i.target_path));}
  same([...seen].sort(),[...modules.keys()].sort(),'unused derived dependency');
  same([...seen].sort(),binding.module_paths,'complete source closure');
  return {selector:node.selector,kind:'Operation' as const,state:'surface-ready' as const,relative_path,provider_path:provider,callable:binding.callable,
   action_sha256:action.action_sha256,descriptor:binding.descriptor,modules:[...modules.values()].sort((a,b)=>a.relative_path<b.relative_path?-1:1),
   initialization:initializations,guards:action.guards.map((g,index)=>({index,selector:g.selector,arguments:g.arguments})),
   events:action.events.map((e,index)=>({index,slot:e.slot,target:e.target,parameter:e.parameter,clock:e.contract.occurred_at_policy==='generated'?e.slot:null})),
   writes:action.writes,result:b.result,behavior_status:'not_evaluable' as const,native_status:'not_evaluable' as const};
 });
 const selectedPaths = new Set(rows.flatMap(r=>r.modules.map(m=>m.relative_path)));
 const body = {schema_version:'domainspec.cross-generator-operation-surface/v1-candidate' as const,definition_sha256:CROSS_GENERATOR_OPERATION_DEFINITION_SHA256,
  project_plan_sha256:plan.plan_sha256,source_manifest_sha256:graph.source_manifest.manifest_sha256,boundary_sha256:boundary.boundary_sha256,
  rows,coverage:boundary.edges.map(e=>({edge_sha256:e.edge_sha256,state:selectedPaths.has(e.importer_path)?'surface-bound' as const:'uncovered' as const,behavior_status:'not_evaluable' as const})),
  behavior_status:'not_evaluable' as const,authority_effect:'none' as const};
 const result=freeze({...body,surface_sha256:sha256(canonicalJson(body))});registered.add(result);return result;
}
export type CrossGeneratorOperationSurface = ReturnType<typeof createCrossGeneratorOperationSurface>;
export function assertCrossGeneratorOperationSurface(value: unknown): asserts value is CrossGeneratorOperationSurface {
 if(!value||typeof value!=='object'||!registered.has(value))fail('registered Operation surface required');
}
