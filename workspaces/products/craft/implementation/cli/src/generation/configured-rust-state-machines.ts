import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {checkTypedStateMachine, decodeTypedStateMachineContract} from '../typed-backend/state-machine.js';
import {decodeTypedRuleContract, type TypedRuleContract, type TypedType, type ValueExpression} from '../typed-operation/contracts.js';
import {planConfiguredRustRules, RUST_RULE_CONTRACT_SHA256, RUST_RULE_SELECTION_VERSION} from './configured-rust-rules.js';
import {rustPascal, rustSelectorModule, rustSelectorType, rustSnake, rustString} from './configured-rust-values.js';
import type {PlannedArtifact} from './contracts.js';

export const RUST_STATE_MACHINE_SELECTION_VERSION = 'domainspec.configured-rust-state-machines-selection/v1-candidate';
export const RUST_STATE_MACHINE_PROTOCOL = 'rust.bound-state-machine/v1-candidate';
export const RUST_STATE_MACHINE_CONTRACT_SHA256 = 'e98350b7bc394174f00f87e1adc543a97931d59056da198b0a401dc5e863be73';
export interface RustStateMachineSelection {readonly schema_version: typeof RUST_STATE_MACHINE_SELECTION_VERSION; readonly language: 'rust'; readonly module_root: string; readonly roots: readonly string[]; readonly boundary_sha256: string; readonly field_compilation_sha256: string | null;}
export interface RustStateMachineSources {readonly rust_contract: string; readonly rule_contract: string;}
function fail(reason: string): never {throw new TypeError('DS_RUST_STATE_MACHINE:' + reason);}
function artifact(relative_path: string, content: string): PlannedArtifact {return {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)};}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}
function rustType(type: TypedType): string {
  if (type.kind === 'scalar') return type.name === 'String' ? 'String' : type.name === 'Bool' ? 'bool' : 'u64';
  if (type.kind === 'named') return rustSelectorType(type.selector);
  if (type.kind === 'optional') return `Option<${rustType(type.element)}>`;
  if (type.kind === 'list') return `Vec<${rustType(type.element)}>`;
  if (type.kind === 'set') return `std::collections::BTreeSet<${rustType(type.element)}>`;
  return fail('anonymous sum input requires a named declaration');
}
export function rustStateMachinePath(root: string, selector: string): string {return `${root}/src/domain/state_machines/${rustSelectorModule(selector)}.rs`;}

export function planConfiguredRustStateMachines(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields | null, selection: RustStateMachineSelection, sources: RustStateMachineSources) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); if (fields) assertCompiledProjectFields(fields); assertInterfaceData(selection); assertInterfaceData(sources);
  if (Object.keys(sources).sort().join('|') !== 'rule_contract|rust_contract' || sha256(sources.rust_contract) !== RUST_STATE_MACHINE_CONTRACT_SHA256 || sha256(sources.rule_contract) !== RUST_RULE_CONTRACT_SHA256) fail('contract drift');
  const certificate = createCompiledProjectCertificate(graph);
  if (selection.schema_version !== RUST_STATE_MACHINE_SELECTION_VERSION || selection.language !== 'rust' || selection.boundary_sha256 !== boundary.boundary_sha256 || selection.field_compilation_sha256 !== (fields?.compilation_sha256 ?? null) || boundary.certificate.graph_sha256 !== certificate.graph_sha256 || fields && (fields.certificate.graph_sha256 !== certificate.graph_sha256 || fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION)) fail('unsupported or stale selection');
  selection.module_root.split('/').forEach(rustSnake);
  if (!Array.isArray(selection.roots) || !selection.roots.length || selection.roots.length > 256 || new Set(selection.roots).size !== selection.roots.length) fail('bounded unique roots required');
  const declarations = fields?.model.declarations ?? [], nodes = graph.nodes.map(node => ({selector: node.selector, kind: node.kind, rule: node.kind === 'Rule' && node.body.typed_contract ? decodeTypedRuleContract(node.body.typed_contract) : null}));
  const contracts = [...selection.roots].sort().map(selector => {
    const node = graph.nodes.find(row => row.selector === selector); if (node?.kind !== 'State Machine' || !node.body.typed_contract) return fail('typed State Machine required:' + selector);
    const contract = decodeTypedStateMachineContract(node.body.typed_contract); checkTypedStateMachine(contract, declarations, nodes); return {selector, contract};
  });
  const ruleRoots = [...new Set(contracts.flatMap(row => row.contract.transitions.flatMap(transition => transition.guard ? [transition.guard.selector] : [])))].sort();
  const rules = ruleRoots.length ? planConfiguredRustRules(graph, fields, {schema_version: RUST_RULE_SELECTION_VERSION, language: 'rust', module_root: selection.module_root, roots: ruleRoots, field_compilation_sha256: fields?.compilation_sha256 ?? null}, sources.rule_contract) : null;
  const properties = new Map(declarations.flatMap(row => row.kind === 'Enum' ? [] : row.contract.properties.map(property => [property.ontology_property, {owner: row.selector, property}] as const)));
  const ruleContracts = new Map<string, TypedRuleContract>(nodes.filter(node => node.rule !== null).map(node => [node.selector, node.rule!]));
  const modules = contracts.map(({selector, contract}) => {
    const state = (value: string) => rustPascal(value), trigger = (value: string) => rustPascal(value.split(':').join('-'));
    const scope = new Map(contract.inputs.map(input => [input.name, input.type]));
    const expression = (value: ValueExpression): string => {
      if (value.op === 'literal') return value.type === 'String' ? `String::from(${rustString(String(value.value))})` : value.type === 'Bool' ? String(value.value) : `${BigInt(value.value)}u64`;
      if (value.op === 'variant') {const owner = declarations.find(row => row.kind === 'Enum' && row.contract.variants.some(variant => variant.ontology_variant === value.selector)); if (!owner || owner.kind !== 'Enum') return fail('unknown Enum variant'); const variant = owner.contract.variants.find(row => row.ontology_variant === value.selector)!; if (variant.payload !== null) return fail('payload variant expression unsupported'); return `${rustSelectorType(owner.selector)}::${rustPascal(variant.name)}`;}
      if (value.op === 'to_set') return `${expression(value.value)}.iter().cloned().collect::<std::collections::BTreeSet<_>>()`;
      let type = scope.get(value.root); if (!type) return fail('unknown parameter:' + value.root); let code = rustSnake(value.root);
      for (const ontology of value.properties) {const found = properties.get(ontology); if (!found || type.kind !== 'named' || found.owner !== type.selector) return fail('property owner mismatch:' + ontology); code += `.${rustSnake(found.property.name)}()`; type = found.property.type;}
      return code;
    };
    const branches = contract.transitions.map(transition => {
      let guard = 'true';
      if (transition.guard) {const rule = ruleContracts.get(transition.guard.selector) ?? fail('missing guard Rule'); const supplied = new Map(transition.guard.arguments.map(argument => [argument.parameter, argument.value])); const args = rule.parameters.map(parameter => {const value = supplied.get(parameter.name) ?? fail('missing guard argument'); const rendered = expression(value); return ['literal', 'variant', 'to_set'].includes(value.op) ? `&(${rendered})` : rendered;}).join(', '); guard = `crate::domain::rules::${rustSelectorModule(transition.guard.selector)}::${rustSnake(transition.guard.selector.split(':')[1]!)}(${args})`;}
      const intents = transition.output_intents.map(intent => `OutputIntent { slot: ${rustString(intent.slot)}, event_ref: ${rustString(intent.event_ref)} }`).join(', ');
      return `        (State::${state(transition.source_state)}, Trigger::${trigger(transition.trigger_event_ref)}) => {\n            if !(${guard}) { return TransitionOutcome::Rejected { state, reason: RejectionReason::Guard }; }\n            TransitionOutcome::Transitioned { state: State::${state(transition.target_state)}, transition_id: ${rustString(transition.transition_id)}, output_intents: vec![${intents}] }\n        }`;
    }).join(',\n');
    const parameters = contract.inputs.map(input => `${rustSnake(input.name)}: &${rustType(input.type)}`).join(', ');
    const content = `// Generated DomainSpec Rust State Machine.\npub const DOMAINSPEC_SELECTOR: &str = ${rustString(selector)};\npub const DOMAINSPEC_PROTOCOL_ID: &str = ${rustString(RUST_STATE_MACHINE_PROTOCOL)};\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash)]\npub enum State { ${[...contract.states].sort().map(state).join(', ')} }\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash)]\npub enum Trigger { ${[...new Set(contract.transitions.map(row => row.trigger_event_ref))].sort().map(trigger).join(', ')} }\n\npub const INITIAL_STATE: State = State::${state(contract.initial)};\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq)]\npub struct OutputIntent { pub slot: &'static str, pub event_ref: &'static str }\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq)]\npub enum RejectionReason { Guard, NoTransition }\n\n#[derive(Clone, Debug, PartialEq, Eq)]\npub enum TransitionOutcome { Transitioned { state: State, transition_id: &'static str, output_intents: Vec<OutputIntent> }, Rejected { state: State, reason: RejectionReason } }\n\npub fn reduce(state: State, trigger: Trigger${parameters ? ', ' + parameters : ''}) -> TransitionOutcome {\n    match (state, trigger) {\n${branches},\n        _ => TransitionOutcome::Rejected { state, reason: RejectionReason::NoTransition },\n    }\n}\n`;
    const relative_path = rustStateMachinePath(selection.module_root, selector); return {selector, relative_path, symbol: 'reduce', rule_dependencies: contract.transitions.flatMap(row => row.guard ? [row.guard.selector] : []), event_dependencies: [...new Set(contract.transitions.flatMap(row => [row.trigger_event_ref, ...row.output_intents.map(intent => intent.event_ref)]))].sort(), artifact: artifact(relative_path, content)};
  });
  const artifacts = [...(rules?.artifacts ?? []), ...modules.map(module => module.artifact)].sort((left, right) => left.relative_path < right.relative_path ? -1 : 1);
  const body = {schema_version: 'domainspec.configured-rust-state-machines-plan/v1-candidate' as const, selection: {...selection, roots: [...selection.roots].sort()}, certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields?.compilation_sha256 ?? null, contract_sha256: RUST_STATE_MACHINE_CONTRACT_SHA256, protocol_id: RUST_STATE_MACHINE_PROTOCOL, rule_plan_sha256: rules?.plan_sha256 ?? null, modules: modules.map(({artifact: _artifact, ...module}) => module), artifacts, authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
