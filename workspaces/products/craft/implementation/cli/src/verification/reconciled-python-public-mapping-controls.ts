import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCheckedPublicMapping} from '../input/compiled-public-mapping.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {getPythonPublicMappingVerificationContext, getPythonInterfaceVerificationContext, type ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {createMappingSemanticCases} from './reconciled-mapping-controls.js';
import {MappingCapacity} from './reconciled-mapping-reference.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';

export function createPythonPublicMappingControls(node: CompiledProjectGraph['nodes'][number], graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan) {
  assertCompiledProjectSnapshot(graph);
  const context = getPythonPublicMappingVerificationContext(plan), module = context.modules.find(m => m.selector === node.selector), mapping = context.mappings.find(m => m.selector === node.selector);
  if (!graph.nodes.includes(node) || node.kind !== 'Mapping' || !module || !mapping) throw new TypeError('DS_PYTHON_PUBLIC_MAPPING_CONTROLS:registered source/module required');
  assertCheckedPublicMapping(mapping);
  if (canonicalJson(createCompiledProjectCertificate(graph)) !== canonicalJson(plan.certificate) || canonicalJson(graph.source_manifest) !== canonicalJson(plan.semantic_sources) ||
      canonicalJson(mapping.certificate) !== canonicalJson(plan.certificate) || mapping.boundary_sha256 !== plan.boundary_sha256 || mapping.field_compilation_sha256 !== plan.field_compilation_sha256 ||
      module.descriptor.mapping_sha256 !== mapping.mapping_sha256 || canonicalJson(module.descriptor.contract) !== canonicalJson(mapping.contract) || canonicalJson(module.descriptor.bindings) !== canonicalJson(mapping.bindings))
    throw new TypeError('DS_PYTHON_PUBLIC_MAPPING_CONTROLS:source/compilation identity');
  const interfaces = mapping.bindings.interface_selectors.map(selector => {
    const native = getPythonInterfaceVerificationContext(plan).find(m => m.selector === selector), authored = mapping.interfaces.find(i => i.source.selector === selector);
    if (!native || !authored || native.descriptor.contract_sha256 !== sha256(canonicalJson(authored.contract)) || native.descriptor.source.sha256 !== authored.source.sha256)
      throw new TypeError('DS_PYTHON_PUBLIC_MAPPING_CONTROLS:Interface source identity');
    return native;
  });
  try {
    const shared = createMappingSemanticCases(node, graph);
    if (!shared.pub || canonicalJson(shared.contract) !== canonicalJson(mapping.contract)) throw new TypeError('DS_PYTHON_PUBLIC_MAPPING_CONTROLS:public source contract');
    // Python's existing provider converts all public/domain input errors to this
    // one boundary error. Leave the complete shared source suite untouched.
    const cases: SemanticCase[] = [{id: 'binding', mode: 'mapping-descriptor', format: 'string', values: [], expected: {kind: 'value', value: canonicalJson(module.descriptor)}},
      ...shared.cases.map(c => c.expected.kind === 'error' ? {...c, expected: {kind: 'error' as const, name: 'TypeError' as const, message: 'MAPPING_INPUT'}} : c)];
    const row = {selector: node.selector, kind: 'Mapping' as const, state: 'ready' as const, adapter: 'python-public-mapping' as const,
      contract_sha256: sha256(canonicalJson(shared.contract)), module, mapping, interfaces, cases, recipes: shared.recipes};
    if (cases.length > 4096 || Buffer.byteLength(canonicalJson(row)) > 8388608) throw new MappingCapacity('bounded Mapping native controls capacity exceeded');
    return row;
  } catch (error) {
    if (error instanceof MappingCapacity) return {selector: node.selector, kind: 'Mapping' as const, state: 'not_evaluable' as const, reason: error.message};
    throw error;
  }
}
