import {assertCrossGeneratorValueProducerControls, CROSS_GENERATOR_VALUE_PRODUCER_DEFINITION_SHA256, type CrossGeneratorValueProducerControls} from './reconciled-cross-generator-value-producer.js';
import path from 'node:path';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {compileSelectedProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256} from '../input/compiled-field-model.js';
import {assertReconciledProjectPlan, type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {decodeTypedRecordContract, decodeTypedSumContract, decodeTypedRuleContract, type TypedType, type RuleExpression} from '../typed-operation/contracts.js';
import {assertCrossGeneratorBoundary, type CrossGeneratorBoundary} from './reconciled-cross-generator-boundary.js';
import {assertCrossGeneratorFactoryControls, type CrossGeneratorFactoryControls} from './reconciled-cross-generator-factory.js';
import {assertCrossGeneratorOwnedValueControls, type CrossGeneratorOwnedValueControls} from './reconciled-cross-generator-owned-values.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';

export const CROSS_GENERATOR_FACTORY_EXECUTION_DEFINITION_SHA256 = 'caaa51768bc0c922a987396f6c36de5f66eb056401d8e81c1399bd3b6811eeb2';
export const CROSS_GENERATOR_OWNED_VALUES_EXECUTION_DEFINITION_SHA256 = '2d42301c7b07de11bb43da66b4b4d3386288c2b4bdea04118443acc4e4e1ac11';
const fail = (reason: string): never => {throw new TypeError('CROSS_GENERATOR_FACTORY_SURFACE:' + reason);};
const same = (a: unknown, b: unknown, reason: string) => {if (canonicalJson(a) !== canonicalJson(b)) fail(reason);};
const sorted = (xs: readonly string[]) => [...new Set(xs)].sort();
const pascal = (s: string) => s.split('-').map(w => w[0]!.toUpperCase() + w.slice(1)).join('');
const dependencies = (e: RuleExpression): string[] => e.op === 'rule_ref' ? [e.selector] : e.op === 'all' || e.op === 'any' ? e.terms.flatMap(dependencies) : e.op === 'not' ? dependencies(e.term) : e.op === 'exists' || e.op === 'exactly_one' || e.op === 'unique' ? dependencies(e.where) : [];
function freeze<T>(v: T): T {if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freeze); Object.freeze(v);} return v;}
type Import = {specifier: string; names: string[]; target_path: string; type_only: boolean; reexport: false};
type Surface = {selector: string | null; role: string; relative_path: string; callable: string; value_exports: string[]; type_exports: string[]; imports: Import[]};
const registered = new WeakSet<object>();

/** Expected surfaces come from typed source and explicit bindings, never generated text. */
export function createCrossGeneratorFactorySurface(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, boundary: CrossGeneratorBoundary, behavior: CrossGeneratorFactoryControls, definition: string) {
  if (typeof definition !== 'string' || sha256(definition) !== CROSS_GENERATOR_FACTORY_EXECUTION_DEFINITION_SHA256) fail('definition drift');
  assertCompiledProjectSnapshot(graph); assertReconciledProjectPlan(plan); assertCrossGeneratorBoundary(boundary); assertCrossGeneratorFactoryControls(behavior);
  same(createCompiledProjectCertificate(graph), plan.resolved.certificate, 'foreign graph');
  same(behavior.project_plan_sha256, plan.plan_sha256, 'foreign plan'); same(behavior.boundary_sha256, boundary.boundary_sha256, 'foreign boundary');
  same(behavior.source_manifest_sha256, graph.source_manifest.manifest_sha256, 'foreign source');
  const bound = deriveFactoryModules(graph, plan, boundary, behavior.rows.filter(r => r.state === 'ready').map(r => r.selector));
  const rows = behavior.rows.map(row => row.state !== 'ready' ? row : {...row, modules: bindClosure(row, bound)});
  const body={schema_version:'domainspec.cross-generator-factory-surface/v1-candidate' as const,definition_sha256:CROSS_GENERATOR_FACTORY_EXECUTION_DEFINITION_SHA256,project_plan_sha256:plan.plan_sha256,source_manifest_sha256:graph.source_manifest.manifest_sha256,boundary_sha256:boundary.boundary_sha256,controls_sha256:behavior.controls_sha256,rows,authority_effect:'none' as const};
  const result=freeze({...body,behavior,surface_sha256:sha256(canonicalJson(body))});registered.add(result);return result;
}
export type CrossGeneratorFactorySurface = ReturnType<typeof createCrossGeneratorFactorySurface>;
export function assertCrossGeneratorFactorySurface(v: unknown): asserts v is CrossGeneratorFactorySurface {if(!v||typeof v!=='object'||!registered.has(v))fail('registered surface required');}

const ownedSurfaces = new WeakSet<object>();
/** Owned-value readiness is independent of factory-to-Rule witness readiness. */
export function createCrossGeneratorOwnedValueSurface(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, boundary: CrossGeneratorBoundary, behavior: CrossGeneratorOwnedValueControls, definition: string) {
  if (typeof definition !== 'string' || sha256(definition) !== CROSS_GENERATOR_OWNED_VALUES_EXECUTION_DEFINITION_SHA256) fail('owned definition drift');
  assertCompiledProjectSnapshot(graph); assertReconciledProjectPlan(plan); assertCrossGeneratorBoundary(boundary); assertCrossGeneratorOwnedValueControls(behavior);
  same(createCompiledProjectCertificate(graph), plan.resolved.certificate, 'foreign graph');
  same(behavior.project_plan_sha256, plan.plan_sha256, 'foreign plan'); same(behavior.boundary_sha256, boundary.boundary_sha256, 'foreign boundary');
  same(behavior.source_manifest_sha256, graph.source_manifest.manifest_sha256, 'foreign source');
  const bound = deriveFactoryModules(graph, plan, boundary, behavior.rows.filter(r => r.state === 'ready').map(r => r.selector));
  const rows = behavior.rows.map(row => row.state !== 'ready' ? row : {...row, modules: bindClosure(row, bound)});
  const body={schema_version:'domainspec.cross-generator-owned-value-surface/v1-candidate' as const,definition_sha256:CROSS_GENERATOR_OWNED_VALUES_EXECUTION_DEFINITION_SHA256,project_plan_sha256:plan.plan_sha256,source_manifest_sha256:graph.source_manifest.manifest_sha256,boundary_sha256:boundary.boundary_sha256,controls_sha256:behavior.controls_sha256,rows,authority_effect:'none' as const};
  const result=freeze({...body,behavior,surface_sha256:sha256(canonicalJson(body))});ownedSurfaces.add(result);return result;
}
export type CrossGeneratorOwnedValueSurface = ReturnType<typeof createCrossGeneratorOwnedValueSurface>;
export function assertCrossGeneratorOwnedValueSurface(v: unknown): asserts v is CrossGeneratorOwnedValueSurface {if(!v||typeof v!=='object'||!ownedSurfaces.has(v))fail('registered owned surface required');}

const producerSurfaces = new WeakSet<object>();
/** Actual Enum roots use the same checked recursive data-module derivation. */
export function createCrossGeneratorValueProducerSurface(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, boundary: CrossGeneratorBoundary, behavior: CrossGeneratorValueProducerControls, definition: string) {
  if (typeof definition !== 'string' || sha256(definition) !== CROSS_GENERATOR_VALUE_PRODUCER_DEFINITION_SHA256) fail('producer definition drift');
  assertCompiledProjectSnapshot(graph); assertReconciledProjectPlan(plan); assertCrossGeneratorBoundary(boundary); assertCrossGeneratorValueProducerControls(behavior);
  same(createCompiledProjectCertificate(graph), plan.resolved.certificate, 'foreign graph');
  same(behavior.project_plan_sha256, plan.plan_sha256, 'foreign plan'); same(behavior.boundary_sha256, boundary.boundary_sha256, 'foreign boundary');
  same(behavior.source_manifest_sha256, graph.source_manifest.manifest_sha256, 'foreign source');
  const bound = deriveFactoryModules(graph, plan, boundary, behavior.rows.filter(r => r.state === 'ready').map(r => r.selector));
  const rows = behavior.rows.map(row => row.state !== 'ready' ? row : {...row, modules: bindClosure(row, bound)});
  const body={schema_version:'domainspec.cross-generator-value-producer-surface/v1-candidate' as const,definition_sha256:CROSS_GENERATOR_VALUE_PRODUCER_DEFINITION_SHA256,project_plan_sha256:plan.plan_sha256,source_manifest_sha256:graph.source_manifest.manifest_sha256,boundary_sha256:boundary.boundary_sha256,controls_sha256:behavior.controls_sha256,rows,authority_effect:'none' as const};
  const result=freeze({...body,behavior,surface_sha256:sha256(canonicalJson(body))});producerSurfaces.add(result);return result;
}
export type CrossGeneratorValueProducerSurface = ReturnType<typeof createCrossGeneratorValueProducerSurface>;
export function assertCrossGeneratorValueProducerSurface(v: unknown): asserts v is CrossGeneratorValueProducerSurface {if(!v||typeof v!=='object'||!producerSurfaces.has(v))fail('registered producer surface required');}

function bindClosure(row: {selector: string; relative_path: string; modules: readonly {relative_path: string}[]}, bound: Map<string, Surface & {sha256: string}>) {
  const pending=[row.relative_path],seen=new Set<string>();
  while(pending.length){const p=pending.pop()!;if(seen.has(p))continue;seen.add(p);const m=bound.get(p)??fail('missing derived closure');m.imports.forEach(i=>pending.push(i.target_path));}
  const paths=[...seen].sort();same(paths,row.modules.map(m=>m.relative_path),'complete source-derived closure:'+row.selector);
  return paths.map(p=>bound.get(p)!);
}

/** Private composition bridge. It adds source Rule roots without inventing a factory. */
export function deriveCrossGeneratorOperationDependencies(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, boundary: CrossGeneratorBoundary, roots: readonly string[], ruleRoots: readonly string[]) {
  assertCompiledProjectSnapshot(graph); assertReconciledProjectPlan(plan); assertCrossGeneratorBoundary(boundary);
  same(createCompiledProjectCertificate(graph), plan.resolved.certificate, 'foreign graph');
  same(boundary.project_plan_sha256, plan.plan_sha256, 'foreign boundary');
  return deriveFactoryModules(graph, plan, boundary, roots, ruleRoots);
}

function deriveFactoryModules(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, boundary: CrossGeneratorBoundary, roots: readonly string[], ruleRoots: readonly string[] = []) {
  const config = JSON.parse(getReconciledSource('configuration'));
  for (const [kind, role] of [['Entity','domain/entities'],['Value Object','domain/value-objects'],['Enum','domain/enums'],['Rule','domain/rules']])
    if (config.types.find((t: any) => t.kind === kind)?.role !== role) fail('configured native role');
  const nodes = new Map(graph.nodes.map(n => [n.selector, n]));
  const dataRoots = graph.nodes.filter(n => ['Entity','Value Object','Enum'].includes(n.kind)).map(n => n.selector).sort();
  const fields = dataRoots.length ? compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: plan.resolved.certificate.graph_sha256, roots: dataRoots, bindings: plan.selection.field_bindings}, getReconciledSource('field')) : null;
  const declarations = new Map(fields?.model.declarations.map(d => [d.selector, d]));
  const nativePath = (selector: string, role: string, suffix = '') => {const [feature,id] = selector.split(':'); return plan.selection.module_root + '/features/' + feature + '/src/domain/' + role + '/' + id + suffix + '.ts';};
  const nameOf = (selector: string) => pascal(selector.split(':')[1]!);
  const runtime = plan.selection.module_root + '/runtime/enum.ts';
  const surfaces = new Map<string, Surface>();
  const imp = (from: string, to: string, name: string, type_only = false): Import => {const rel = path.posix.relative(path.posix.dirname(from), to).replace(/\.ts$/, '.js'); return {specifier: rel.startsWith('.') ? rel : './' + rel, names: [name], target_path: to, type_only, reexport: false};};
  const install = (s: Surface) => {if (surfaces.size >= 8192) fail('module capacity'); surfaces.set(s.relative_path, s);};
  const valueTarget = (selector: string) => {
    const d = declarations.get(selector) ?? fail('missing source declaration'), name = nameOf(selector);
    return {path: nativePath(selector, d.kind === 'Enum' ? 'enums' : d.kind === 'Entity' ? 'entities' : 'value-objects', d.kind === 'Enum' ? d.contract.variants.some(v => v.payload !== null) ? '.sum' : '.component' : ''), name, type: name + (d.kind === 'Enum' ? 'Case' : 'Snapshot')};
  };
  const valueImports = (type: TypedType, owner: string): Import[] => {
    if (type.kind === 'scalar') return [];
    if (type.kind === 'reference') return [];
    if (type.kind === 'named') {const t = valueTarget(type.selector); visitData(type.selector); return [imp(owner,t.path,t.name+'ValueComponent'),imp(owner,t.path,t.type,true)];}
    if (type.kind === 'sum') return [...type.variants].sort((a,b)=>a.name<b.name?-1:1).flatMap(v=>v.payload?valueImports(v.payload,owner):[]);
    return valueImports(type.element, owner);
  };
  function visitRule(selector: string) {
    const p = nativePath(selector,'rules'); if (surfaces.has(p)) return;
    const n = nodes.get(selector); if (n?.kind !== 'Rule') fail('missing source Rule');
    const contract = decodeTypedRuleContract(n!.body.typed_contract), refs = sorted(dependencies(contract.expression)), callable = 'rule'+nameOf(selector);
    const s: Surface = {selector,role:'rule',relative_path:p,callable,value_exports:[callable],type_exports:[],imports:refs.map(r=>imp(p,nativePath(r,'rules'),'rule'+nameOf(r)))};
    install(s); refs.forEach(visitRule);
  }
  function visitData(selector: string) {
    const d = declarations.get(selector) ?? fail('missing data declaration'), t = valueTarget(selector), p = t.path, name = t.name;
    if (surfaces.has(p)) return;
    if (d.kind === 'Enum') {
      const sum = decodeTypedSumContract(nodes.get(selector)!.body.typed_contract);
      const s: Surface = {selector,role:sum.variants.some(v=>v.payload!==null)?'sum':'enum-component',relative_path:p,callable:name+'ValueComponent',value_exports:[name+'ValueComponent'],type_exports:sum.variants.some(v=>v.payload!==null)?[name+'Case',name+'Input']:[name+'Case'],imports:[]};
      install(s);
      if (s.role === 'sum') s.imports = valueImports({kind:'sum',variants:sum.variants},p);
      else {
        const definitionPath = nativePath(selector,'enums');
        s.imports = [imp(p,definitionPath,name)];
        install({selector,role:'enum-definition',relative_path:definitionPath,callable:name,value_exports:[name],type_exports:[name],imports:[imp(definitionPath,runtime,'defineEnum'),imp(definitionPath,runtime,'EnumValue',true)]});
        if (!surfaces.has(runtime)) install({selector:null,role:'enum-runtime',relative_path:runtime,callable:'defineEnum',value_exports:['composeEnum','defineEnum'],type_exports:['EnumValue'],imports:[]});
      }
      return;
    }
    const contract = decodeTypedRecordContract(nodes.get(selector)!.body.typed_contract);
    const binding = plan.selection.factories.find(b=>b.selector===selector) ?? fail('missing source factory binding');
    const rules = sorted([...binding.base_validators,...binding.extensions.flatMap(e=>e.validators)].map(v=>v.rule));
    const s: Surface = {selector,role:'factory',relative_path:p,callable:'create'+name+'Factory',value_exports:[name+'FieldBindings',name+'ValueComponent','create'+name+'Factory'].sort(),type_exports:[name+'Fields',name+'Snapshot'],imports:rules.map(r=>imp(p,nativePath(r,'rules'),'rule'+nameOf(r)))};
    install(s); rules.forEach(visitRule);
    s.imports.push(...[...contract.properties].sort((a,b)=>a.name<b.name?-1:1).flatMap(f=>valueImports(f.type,p)));
    for (const ref of fields!.model.bindings.filter(b=>b.owner===selector)) {
      visitData(ref.target);
      if (ref.target !== selector) s.imports.push(imp(p,valueTarget(ref.target).path,nameOf(ref.target)+'Fields',true));
    }
  }
  roots.forEach(visitData); ruleRoots.forEach(visitRule);
  const bound = new Map([...surfaces].map(([p,s]) => {
    const native = boundary.modules.find(m=>m.relative_path===p) ?? fail('missing expected module:'+p), artifact = plan.resolved.artifacts.find(a=>a.relative_path===p) ?? fail('missing captured artifact');
    same(native.exports, [...s.value_exports.map(name=>({name,kind:'value'})),...s.type_exports.map(name=>({name,kind:'type'}))].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:a.kind<b.kind?-1:1), 'source-derived exports:'+p);
    same(native.qualified_selectors, s.selector === null ? [] : [s.selector], 'source module owner:'+p);
    same(boundary.edges.filter(e=>e.importer_path===p).map(e=>({specifier:e.specifier,names:e.names,target_path:e.target_path,type_only:e.type_only,reexport:e.reexport})),s.imports,'source-derived imports:'+p);
    if (boundary.edges.some(e=>e.importer_path===p&&(e.namespace||e.category==='native-standard-library'))) fail('unsupported module import');
    if (sha256(artifact.content)!==native.sha256) fail('captured artifact drift');
    if (s.role==='enum-runtime' && artifact.content!==getReconciledSource('enum_provider')) fail('Enum provider drift');
    return [p,{...s,sha256:native.sha256}] as const;
  }));
  return bound;
}
