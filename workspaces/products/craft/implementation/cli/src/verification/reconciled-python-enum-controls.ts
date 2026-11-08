import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {createPythonOwnedValueContext} from './reconciled-python-value-context.js';
import {decodeTypedSumContract} from '../typed-operation/contracts.js';

/** Native representation controls; authored names/IDs come from the shared
 * checked value context, never by reading generated declarations. */
export function createPythonPlainEnumControls(node: CompiledProjectGraph['nodes'][number], graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan) {
  if (node.kind !== 'Enum') throw new TypeError('DS_PYTHON_ENUM_CONTROLS:Enum required');
  if (decodeTypedSumContract(node.body.typed_contract).variants.some(v => v.payload !== null)) return {selector: node.selector, kind: node.kind, state: 'not_evaluable' as const,
    reason: 'payload-bearing sum execution and owned factory dependencies not yet integrated'};
  const context = createPythonOwnedValueContext(node.selector, graph, plan), root = context.root;
  if (root.kind !== 'Enum' || !root.plain) throw new TypeError('DS_PYTHON_ENUM_CONTROLS:plain Enum binding required');
  const names = root.contract.variants.map(v => v.name).sort();
  const cases: {id: string; mode: string; values: string[]; expected: {kind: 'value'; value: string}}[] = [];
  const push = (mode: string, values: string[], value: unknown) => cases.push({id: 'case-' + cases.length, mode, values, expected: {kind: 'value', value: canonicalJson(value)}});
  push('definition', [], {names, wire_values: names, enum_id: node.selector, protocol_id: 'python.nominal-enum-explicit-wire/v1', nominal: true, aliases: false});
  for (const name of names) push('member', [name], {wire: name, ontology_variant: root.contract.variants.find(v => v.name === name)!.ontology_variant,
    stable: true, copy_stable: true, exact_type: true, other_members: names.map(n => n === name), foreign_equal: false, string_equal: false});
  for (const mode of ['unknown', 'null', 'undefined', 'number', 'boolean', 'boxed', 'object', 'array', 'symbol', 'coercion', 'foreign', 'member'])
    push('invalid-wire', [mode], {name: '_EnumWireError', code: 'DOMAINSPEC_ENUM_UNKNOWN_WIRE', enum_id: node.selector, input_preserved: true});
  for (const mode of ['raw', 'clone', 'plain', 'null', 'undefined', 'getter', 'foreign', 'number', 'boolean', 'boxed', 'array', 'symbol', 'coercion', 'string-enum'])
    push('unowned', [mode], {emit: 'DOMAINSPEC_ENUM_MEMBER_INVALID', member_id: 'DOMAINSPEC_ENUM_MEMBER_INVALID', input_preserved: true});
  return {selector: node.selector, kind: node.kind, state: 'ready' as const, adapter: 'python-plain-enum' as const,
    module: {selector: node.selector, relative_path: root.relative_path, symbol: root.symbol, callable_stem: node.selector.split(':')[1]!.replaceAll('-', '_')},
    contract: root.contract, contract_sha256: sha256(canonicalJson(root.contract)), module_paths: context.module_paths, cases};
}
