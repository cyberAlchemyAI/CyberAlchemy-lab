import type {CompiledProjectGraph} from '../input/project-model.js';
import {selectCompiledProjectNode} from '../input/project-model.js';
import {getPythonDecisionVerificationContext, type ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {createPythonOwnedValueContext} from './reconciled-python-value-context.js';
import {createFactorySemanticCases} from './reconciled-factory-controls.js';
import {isWitnessUnavailable, type Dependency, type SumRecipe} from './reconciled-value-context.js';
import {evaluateRecordWitness} from './reconciled-record-witness.js';

export function createPythonFactoryControls(node: CompiledProjectGraph['nodes'][number], graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan) {
  try {
    const context = createPythonOwnedValueContext(node.selector, graph, plan, true), {root, rootShape, dependencies, module_paths} = context;
    if (root.kind === 'Enum') throw new TypeError('DS_PYTHON_FACTORY_CONTROLS:record required');
    const rules = getPythonDecisionVerificationContext(plan).rules;
    const shared = createFactorySemanticCases(context, probe => probe.trace.validators.map(v => {
      const module = rules.find(m => m.selector === v.rule);
      const artifact = plan.artifacts.find(a => a.relative_path === module?.relative_path);
      if (!module || !artifact || module.closure_sha256 !== selectCompiledProjectNode(graph, v.rule).typed_closure!.closure_sha256) throw new TypeError('DS_PYTHON_FACTORY_CONTROLS:Rule binding');
      return {...v, closure_sha256: module.closure_sha256, artifact_sha256: artifact.sha256};
    }));
    const cases = shared.cases.map(c => {
      if (c.expected.kind === 'error') return c;
      const value = JSON.parse(c.expected.value), snapshot = value.snapshot;
      return {...c, expected: {kind: 'value' as const, value: canonicalJson({ok: value.ok, failure_codes: value.failure_codes, trace: value.trace,
        extensions: value.factory.extensions, snapshot: snapshot ? {view: snapshot.view, key: snapshot.key, equals_baseline: snapshot.equals_baseline} : null})}};
    });
    // Extension search can select a previous snapshot absent from the base
    // sample list. Bind every constructed record to its source-predicted base
    // creation outcome before the native helper is allowed to use it.
    const ownedDependencies: Record<string, Dependency> = {...dependencies};
    const bindRecipe = (value: unknown): void => {
      if (!value || typeof value !== 'object') return;
      const recipe = value as SumRecipe;
      if (recipe.tag === 'record') {
        const dep = ownedDependencies[recipe.selector!]!;
        if (dep.kind === 'Enum') throw new TypeError('DS_PYTHON_FACTORY_CONTROLS:record dependency required');
        if (!dep.probes.some(p => canonicalJson(p.recipe) === canonicalJson(recipe))) ownedDependencies[dep.selector] = {...dep,
          probes: [...dep.probes, {recipe, expected: evaluateRecordWitness(dep, context.reference, recipe)}]};
      }
      Object.values(value).forEach(bindRecipe);
    };
    bindRecipe(shared.baseline); for (const c of shared.cases) bindRecipe(JSON.parse(c.values[0]!));
    return {selector: node.selector, kind: node.kind, state: 'ready' as const, adapter: 'python-factory' as const,
      module: {selector: node.selector, relative_path: root.relative_path, symbol: root.symbol, callable: root.callable},
      contract_sha256: sha256(canonicalJson({record: root.record, binding: root.binding})), shape: rootShape, dependencies: ownedDependencies, module_paths, baseline: shared.baseline, cases};
  } catch (error) {
    if (isWitnessUnavailable(error)) return {selector: node.selector, kind: node.kind, state: 'not_evaluable' as const, reason: error.message};
    throw error;
  }
}
