import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import type {TypedType} from '../typed-operation/contracts.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {createPythonOwnedValueContext} from './reconciled-python-value-context.js';
import {createSumSemanticCases} from './reconciled-sum-controls.js';
import {isWitnessUnavailable, type Dependency, type SumRecipe} from './reconciled-value-context.js';

/** Identify the same malformed leaf using Python's existing exact error API. */
function nativeError(type: TypedType, recipe: SumRecipe, dependencies: Readonly<Record<string, Dependency>>): string | null {
  if (type.kind === 'optional') return recipe.tag === 'null' ? null : nativeError(type.element, recipe, dependencies);
  if (recipe.tag === 'bad') {
    if (type.kind === 'scalar') return {String: 'INVALID_STRING', Bool: 'INVALID_BOOL', UInt64: 'INVALID_UINT64'}[type.name];
    if (type.kind === 'list' || type.kind === 'set') return recipe.mode === 'duplicate' ? 'DUPLICATE_SET_VALUE' : 'INVALID_COLLECTION';
    if (type.kind === 'sum') return ['missing-variant', 'unknown-variant'].includes(recipe.mode!) ? 'INVALID_SUM_VARIANT'
      : ['extra', 'missing-payload', 'surplus-payload'].includes(recipe.mode!) ? 'INVALID_SUM_PAYLOAD' : 'INVALID_SUM';
    const d = dependencies[type.selector]!;
    return d.kind === 'Enum' && d.plain ? 'UNOWNED_ENUM_CASE' : 'UNOWNED_COMPONENT';
  }
  if (type.kind === 'scalar') return null;
  if (type.kind === 'list' || type.kind === 'set') return recipe.items!.map(r => nativeError(type.element, r, dependencies)).find(Boolean) ?? null;
  if (type.kind === 'sum') {
    const v = type.variants.find(v => v.name === recipe.variant)!;
    return v.payload ? nativeError(v.payload, recipe.payload!, dependencies) : null;
  }
  const d = dependencies[type.selector]!;
  return d.kind === 'Enum' && !d.plain ? nativeError({kind: 'sum', variants: d.contract.variants}, recipe.input!, dependencies) : null;
}

export function createPythonSumControls(node: CompiledProjectGraph['nodes'][number], graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan) {
  try {
    const context = createPythonOwnedValueContext(node.selector, graph, plan), {root, rootShape, dependencies, module_paths} = context;
    if (root.kind !== 'Enum' || root.plain) throw new TypeError('DS_PYTHON_SUM_CONTROLS:payload-bearing sum required');
    const shared = createSumSemanticCases(context);
    const cases = shared.cases.map(c => {
      if (c.expected.kind === 'value') return {...c, native_error: null};
      const native_error = nativeError(rootShape, JSON.parse(c.values[0]!), dependencies);
      if (!native_error) throw new TypeError('DS_PYTHON_SUM_CONTROLS:unmapped negative recipe');
      return {...c, native_error};
    });
    for (const d of Object.values(dependencies)) if (d.kind !== 'Enum') for (const probe of d.probes)
      cases.push({id: 'case-' + cases.length, mode: 'record-probe', format: 'string', values: [canonicalJson(probe.recipe)], expected: {kind: 'value', value: canonicalJson(probe.expected)}, native_error: null});
    return {selector: node.selector, kind: node.kind, state: 'ready' as const, adapter: 'python-sum' as const,
      module: {selector: node.selector, relative_path: root.relative_path, symbol: root.symbol, callable: 'create_' + node.selector.split(':')[1]!.replaceAll('-', '_')},
      contract: root.contract, contract_sha256: sha256(canonicalJson(root.contract)), shape: rootShape, dependencies, module_paths, baseline: shared.baseline, cases};
  } catch (error) {
    if (isWitnessUnavailable(error)) return {selector: node.selector, kind: node.kind, state: 'not_evaluable' as const, reason: error.message};
    throw error;
  }
}
