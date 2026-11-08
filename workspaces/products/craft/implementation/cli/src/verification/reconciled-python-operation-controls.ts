import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertReconciledPythonProjectPlan, getPythonOperationVerificationContext, getPythonEventVerificationContext, type ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {createBoundEffectfulOperationReference} from './reconciled-operation-effect-reference.js';
import {createOperationSemanticCases, isOperationCapacity} from './reconciled-operation-cases.js';
import {createPythonOwnedValueContext} from './reconciled-python-value-context.js';

export function createPythonOperationControls(node: CompiledProjectGraph['nodes'][number], graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan) {
  assertCompiledProjectSnapshot(graph); assertReconciledPythonProjectPlan(plan);
  if (node.kind !== 'Operation' || !graph.nodes.includes(node) || canonicalJson(createCompiledProjectCertificate(graph)) !== canonicalJson(plan.certificate))
    throw new TypeError('DS_PYTHON_OPERATION_CONTROLS:graph/plan identity');
  const context = getPythonOperationVerificationContext(plan), module = context.modules.find(m => m.selector === node.selector);
  const action = context.actions.find(a => a.bindings.selector === node.selector);
  if (!action || !module || module.descriptor.action_sha256 !== action.action_sha256 ||
      canonicalJson(plan.selection.operations.find(a => a.selector === node.selector)) !== canonicalJson(action.bindings) ||
      canonicalJson(module.descriptor.bindings) !== canonicalJson(action.bindings))
    throw new TypeError('DS_PYTHON_OPERATION_CONTROLS:checked action binding');
  try {
    const oracle = createBoundEffectfulOperationReference(graph, action, plan.selection.factories);
    const shared = createOperationSemanticCases(action, oracle, selector => createPythonOwnedValueContext(selector, graph, plan));
    const cases = shared.cases.map(c => {
      // The native Python API validates receipt shape explicitly. Preserve that
      // existing failure code; do not import TypeScript exception mechanics.
      const fixture = JSON.parse(c.values[0]!), expected = JSON.parse((c.expected as {value: string}).value);
      const fields = expected.outcome[1], code = fields.find((f: any) => f[0] === 'code'), stage = fields.find((f: any) => f[0] === 'stage');
      if (fixture.mode.startsWith('receipt-') && stage?.[1][1] === 'commit' && code?.[1][1] === 'COMMIT_UNCERTAIN') {
        code[1][1] = 'INVALID_COMMIT_RECEIPT';
        return {...c, expected: {kind: 'value' as const, value: canonicalJson(expected)}};
      }
      return c;
    });
    for (const phase of ['begin', 'read', 'commit', 'rollback']) {
      const source = cases.find(c => JSON.parse((c.expected as {value: string}).value).trace.some((s: string) => phase === 'read' ? s.startsWith('read:') && s.endsWith('-rejected') : s === phase + '-rejected'));
      if (source) cases.push({...source, id: 'native-cancel-' + phase, mode: 'operation-native-cancel',
        values: [canonicalJson({...JSON.parse(source.values[0]!), cancel: phase})]});
    }
    if (cases.length + 1 > 4096 || Buffer.byteLength(canonicalJson({cases, recipes: shared.recipes})) > 8388608)
      return {selector: node.selector, kind: 'Operation' as const, state: 'not_evaluable' as const, reason: 'bounded native Operation case capacity exceeded'};
    const event_modules = getPythonEventVerificationContext(plan).filter(m => action.events.some(e => e.target === m.selector));
    const selectors = new Set([node.selector, ...action.guards.map(g => g.selector), ...action.events.map(e => e.target),
      ...event_modules.flatMap(m => m.descriptor.references.map(r => r.selector))]);
    return {selector: node.selector, kind: 'Operation' as const, state: 'ready' as const, adapter: 'python-operation' as const,
      module, action, contract_sha256: sha256(canonicalJson(action.bindings)), recipes: shared.recipes,
      cases: [{id: 'binding', mode: 'operation-descriptor', format: 'string' as const, values: [], expected: {kind: 'value' as const, value: canonicalJson(module.descriptor)}}, ...cases],
      nodes: Object.fromEntries(graph.nodes.filter(n => selectors.has(n.selector)).map(n => [n.selector, {kind: n.kind, body: n.body}])),
      event_modules};
  } catch (error) {
    if (isOperationCapacity(error)) return {selector: node.selector, kind: 'Operation' as const, state: 'not_evaluable' as const, reason: error.message};
    throw error;
  }
}
