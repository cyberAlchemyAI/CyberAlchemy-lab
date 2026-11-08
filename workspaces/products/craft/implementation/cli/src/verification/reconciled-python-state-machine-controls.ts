import type {CompiledProjectGraph} from '../input/project-model.js';
import {getPythonStateMachineVerificationContext, getPythonDataVerificationContext, type ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {createStateMachineSemanticCases} from './reconciled-state-machine-controls.js';

export function createPythonStateMachineControls(node: CompiledProjectGraph['nodes'][number], graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan) {
  const module = getPythonStateMachineVerificationContext(plan).find(m => m.selector === node.selector);
  const shared = createStateMachineSemanticCases(node, graph);
  if (shared.state !== 'ready') return shared;
  if (!module || module.descriptor.contract_sha256 !== shared.contract_sha256 ||
      canonicalJson(module.descriptor.contract) !== canonicalJson(shared.contract) ||
      module.descriptor.source.body_sha256 !== sha256(canonicalJson(node.body)) ||
      module.descriptor.field_model_sha256 !== (getPythonDataVerificationContext(plan).model?.model_sha256 ?? null))
    throw new TypeError('DS_PYTHON_STATE_MACHINE_CONTROLS:source/model binding');
  const events = Object.fromEntries(module.descriptor.event_dependencies.map(ref => {
    const target = graph.nodes.find(n => n.selector === ref.selector);
    if (!target || target.kind !== 'Event' || sha256(canonicalJson(target.body)) !== ref.body_sha256)
      throw new TypeError('DS_PYTHON_STATE_MACHINE_CONTROLS:Event reference binding');
    return [ref.selector, {kind: target.kind, body: target.body}];
  }));
  return {...shared, adapter: 'python-state-machine' as const, module, events};
}
