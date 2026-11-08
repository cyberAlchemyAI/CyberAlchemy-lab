import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {getPythonInterfaceVerificationContext, type ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import {canonicalJson} from '../input/source-manifest.js';
import {createInterfaceSemanticCases} from './reconciled-interface-controls.js';

export function createPythonInterfaceControls(node: CompiledProjectGraph['nodes'][number], graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan) {
  assertCompiledProjectSnapshot(graph);
  const module = getPythonInterfaceVerificationContext(plan).find(m => m.selector === node.selector);
  if (canonicalJson(createCompiledProjectCertificate(graph)) !== canonicalJson(plan.certificate) || canonicalJson(graph.source_manifest) !== canonicalJson(plan.semantic_sources))
    throw new TypeError('DS_PYTHON_INTERFACE_CONTROLS:graph/plan identity');
  const shared = createInterfaceSemanticCases(node, graph, plan.field_compilation_sha256);
  if (shared.state !== 'ready') return shared;
  if (!module || module.descriptor.contract_sha256 !== shared.contract_sha256 || canonicalJson(module.descriptor.contract) !== canonicalJson(shared.contract) ||
      module.descriptor.graph_sha256 !== plan.certificate.graph_sha256 || module.descriptor.field_compilation_sha256 !== plan.field_compilation_sha256)
    throw new TypeError('DS_PYTHON_INTERFACE_CONTROLS:source/field binding');
  const descriptorCase = shared.cases.find(c => c.mode === 'interface-descriptor')!;
  if (descriptorCase.expected.kind !== 'value' || canonicalJson(JSON.parse(descriptorCase.expected.value).source) !== canonicalJson(module.descriptor.source))
    throw new TypeError('DS_PYTHON_INTERFACE_CONTROLS:source bytes');
  const {serialized_bytes: _, ...semantic} = shared;
  // Keep source expectations intact. The runner checks Python's additional
  // descriptor fields independently, then projects the shared descriptor view.
  const controls = {...semantic, adapter: 'python-interface' as const, module};
  if (Buffer.byteLength(canonicalJson(controls)) > 8388608)
    return {selector: node.selector, kind: 'Interface' as const, state: 'not_evaluable' as const, reason: 'bounded Interface native controls capacity exceeded'};
  return controls;
}
