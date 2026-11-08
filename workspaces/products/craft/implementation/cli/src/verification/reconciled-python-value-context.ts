import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson} from '../input/source-manifest.js';
import {assertReconciledPythonProjectPlan, getPythonFactoryVerificationContext, getPythonDataVerificationContext, type ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import {pythonSymbol} from '../generation/configured-python-owned-values.js';
import {pythonEnumSymbol} from '../generation/configured-python-enums.js';
import {createBoundOwnedValueContext} from './reconciled-value-context.js';

const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_VALUE_CONTEXT:' + reason);};

/** Source witness preparation only, bound to real registered Python modules.
 * Does not execute factories or certify ownership/native behavior. */
export function createPythonOwnedValueContext(selector: string, graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan, includeExtensions = false) {
  assertCompiledProjectSnapshot(graph); assertReconciledPythonProjectPlan(plan);
  if (canonicalJson(createCompiledProjectCertificate(graph)) !== canonicalJson(plan.certificate) || canonicalJson(graph.source_manifest) !== canonicalJson(plan.semantic_sources)) fail('graph/plan identity');
  const node = graph.nodes.find(n => n.selector === selector) ?? fail('unknown source selector');
  const model = getPythonDataVerificationContext(plan).model;
  const factories = getPythonFactoryVerificationContext(plan);
  const module = (selector: string, symbol: string) => {
    const found = plan.modules.filter(m => m.qualified_selectors.includes(selector) && m.bindings.includes(symbol));
    if (found.length !== 1) return fail('unique native value module required:' + selector + ':' + symbol);
    return found[0]!;
  };
  return createBoundOwnedValueContext(node, graph, {
    record: (selector, reference) => {
      const declaration = reference.get(selector);
      if (declaration.kind === 'Enum') return fail('record required');
      const factory = factories.find(m => m.selector === selector) ?? fail('private factory binding required');
      const binding = plan.selection.factories.find(f => f.selector === selector) ?? fail('authored factory binding required');
      const symbol = pythonSymbol(selector.split(':')[1]!) + 'ValueComponent';
      const native = module(selector, symbol);
      if (factory.relative_path !== native.relative_path || !native.bindings.includes(factory.callable)) fail('factory module identity');
      if (canonicalJson(model?.declarations.find(d => d.selector === selector)?.contract) !== canonicalJson(declaration.contract)) fail('record/model identity');
      return {selector, kind: declaration.kind, plain: false, relative_path: native.relative_path, symbol, callable: factory.callable,
        record: declaration.contract, binding, probes: []};
    },
    enumeration: (selector, contract) => {
      const plain = contract.variants.every(v => v.payload === null);
      const id = selector.split(':')[1]!, symbol = plain ? pythonEnumSymbol(id) : pythonSymbol(id) + 'ValueComponent';
      return {kind: 'Enum', selector, contract, plain, symbol, relative_path: module(selector, symbol).relative_path};
    },
    closure: root => {
      const paths = new Set<string>();
      const visit = (relative: string) => {
        if (paths.has(relative)) return;
        paths.add(relative);
        const native = plan.modules.find(m => m.relative_path === relative) ?? fail('missing native closure');
        for (const dependency of native.imports) {
          if (dependency.target_path !== null) visit(dependency.target_path);
          else if (dependency.dependency !== 'python-standard-library') fail('unbound native import');
        }
      };
      visit(root.relative_path); return [...paths].sort();
    },
  }, includeExtensions);
}
