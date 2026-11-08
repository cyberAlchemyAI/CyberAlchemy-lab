import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {type TypedType} from '../typed-operation/contracts.js';
import {assertCheckedWorkflowBindings, type CheckedWorkflowBindings, type WorkflowValueExpression} from '../typed-operation/workflow-bindings.js';
import {assertCheckedWorkflowRecoveryPolicy, planSelectedWorkflowRecovery, WORKFLOW_FAILURE_JOURNAL_VERSION, WORKFLOW_RECOVERY_CONTRACT_SHA256, type CheckedWorkflowRecoveryPolicy} from '../typed-operation/workflow-recovery.js';
import {WORKFLOW_OUTCOME_CONTRACT_SHA256} from '../typed-operation/workflow-outcomes.js';
import {workflowObject} from '../typed-backend/workflow-occurrences.js';
import {planConfiguredRustOperations, RUST_OPERATION_SELECTION_VERSION, type RustOperationSelection, type RustOperationSources} from './configured-rust-operations.js';
import {rustPascal, rustSelectorModule, rustSelectorType, rustSnake, rustString} from './configured-rust-values.js';
import type {PlannedArtifact} from './contracts.js';

export const RUST_WORKFLOW_SELECTION_VERSION = 'domainspec.configured-rust-workflow-selection/v1-candidate';
export const RUST_WORKFLOW_PROTOCOL = 'rust.bound-workflow/v1-candidate';
export const RUST_WORKFLOW_CONTRACT_SHA256 = '201bcd2baf67219c13f1fb5953a50efafcb7ad1984268daf952cbdc3097c55cd';
export interface RustWorkflowSelection {readonly schema_version: typeof RUST_WORKFLOW_SELECTION_VERSION; readonly language: 'rust'; readonly module_root: string; readonly workflow: CheckedWorkflowBindings; readonly policy: CheckedWorkflowRecoveryPolicy; readonly actions: RustOperationSelection['actions']; readonly factories: RustOperationSelection['factories'];}
export interface RustWorkflowSources {readonly rust_contract: string; readonly outcome_contract: string; readonly recovery_contract: string; readonly operations: RustOperationSources;}
function fail(reason: string): never {throw new TypeError('DS_RUST_WORKFLOW:' + reason);}
function closed(value: unknown, keys: readonly string[]): void {
  if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail('plain input');
  const descriptors = Object.getOwnPropertyDescriptors(value); if (Reflect.ownKeys(descriptors).some(key => typeof key !== 'string' || !keys.includes(key)) || Object.values(descriptors).some(row => !Object.hasOwn(row, 'value') || !row.enumerable)) fail('inert input'); workflowObject(value, keys);
}
function rustType(type: TypedType): string {
  if (type.kind === 'scalar') return type.name === 'String' ? 'String' : type.name === 'Bool' ? 'bool' : 'u64';
  if (type.kind === 'named') return rustSelectorType(type.selector);
  if (type.kind === 'optional') return `Option<${rustType(type.element)}>`;
  if (type.kind === 'list') return `Vec<${rustType(type.element)}>`;
  if (type.kind === 'set') return `std::collections::BTreeSet<${rustType(type.element)}>`;
  return fail('anonymous sum Workflow value requires a named declaration');
}
function artifact(relative_path: string, content: string): PlannedArtifact {return {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)};}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}
export function rustWorkflowPath(root: string, selector: string): string {return `${root}/src/application/workflows/${rustSelectorModule(selector)}.rs`;}

export function planConfiguredRustWorkflow(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields, selection: RustWorkflowSelection, sources: RustWorkflowSources) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); assertCompiledProjectFields(fields); closed(selection, ['schema_version', 'language', 'module_root', 'workflow', 'policy', 'actions', 'factories']); closed(sources, ['rust_contract', 'outcome_contract', 'recovery_contract', 'operations']);
  if (selection.schema_version !== RUST_WORKFLOW_SELECTION_VERSION || selection.language !== 'rust' || sha256(sources.rust_contract) !== RUST_WORKFLOW_CONTRACT_SHA256 || sha256(sources.outcome_contract) !== WORKFLOW_OUTCOME_CONTRACT_SHA256 || sha256(sources.recovery_contract) !== WORKFLOW_RECOVERY_CONTRACT_SHA256) fail('selection or contract drift');
  const workflow = selection.workflow, policy = selection.policy; assertCheckedWorkflowBindings(workflow); assertCheckedWorkflowRecoveryPolicy(policy); if (policy.workflow !== workflow) fail('policy Workflow identity');
  const certificate = createCompiledProjectCertificate(graph); if (workflow.certificate.graph_sha256 !== certificate.graph_sha256 || workflow.boundary_sha256 !== boundary.boundary_sha256 || workflow.field_compilation_sha256 !== fields.compilation_sha256) fail('stale Workflow'); selection.module_root.split('/').forEach(rustSnake);
  const operations = planConfiguredRustOperations(graph, boundary, fields, {schema_version: RUST_OPERATION_SELECTION_VERSION, language: 'rust', module_root: selection.module_root, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256, actions: selection.actions, factories: selection.factories}, sources.operations);
  const required = new Map([...workflow.steps, ...workflow.compensations].map(row => [row.operation_ref, row.action_sha256])); if (operations.modules.length !== required.size || operations.modules.some(module => required.get(module.selector) !== module.action_sha256)) fail('exact Operation closure');
  const declarations = new Map(fields.model.declarations.map(row => [row.selector, row])), properties = new Map([...declarations.values()].flatMap(row => row.kind === 'Enum' ? [] : row.contract.properties.map(property => [property.ontology_property, {owner: row.selector, property}] as const)));
  const uniqueOperations = [...new Set(workflow.steps.map(step => step.operation_ref))].sort();
  const generatedClocks = workflow.event_inputs.filter(input => input.contract.occurred_at_policy === 'generated');
  const groupedParameters = workflow.bindings.inputs.length + workflow.event_inputs.length + generatedClocks.length + uniqueOperations.length > 7;
  const parameterReference = (name: string) => groupedParameters ? `execution.${name}` : name;
  type Bound = {type: TypedType; reference: string; owned: string};
  const workflowInputs = new Map(workflow.bindings.inputs.map(input => {const name = rustSnake(input.name), reference = parameterReference(name); return [input.name, {type: input.type, reference, owned: `Clone::clone(${reference})`} as Bound];}));
  const usedInputs = new Set<string>();
  const results = new Map<string, Bound>();
  const expression = (value: WorkflowValueExpression): Bound => {
    if (value.op === 'literal') {const type: TypedType = {kind: 'scalar', name: value.type}; const owned = value.type === 'String' ? `String::from(${rustString(String(value.value))})` : value.type === 'Bool' ? String(value.value) : `${BigInt(value.value)}u64`; return {type, owned, reference: `&(${owned})`};}
    if (value.op === 'variant') {const owner = [...declarations.values()].find(row => row.kind === 'Enum' && row.contract.variants.some(variant => variant.ontology_variant === value.selector)); if (!owner || owner.kind !== 'Enum') return fail('unknown Enum variant'); const variant = owner.contract.variants.find(row => row.ontology_variant === value.selector)!; if (variant.payload !== null) return fail('payload variant unsupported'); const owned = `${rustSelectorType(owner.selector)}::${rustPascal(variant.name)}`; return {type: {kind: 'named', selector: owner.selector}, owned, reference: `&(${owned})`};}
    if (value.op === 'to_set') {const inner = expression(value.value); if (inner.type.kind !== 'list') return fail('to_set requires list'); const owned = `${inner.reference}.iter().cloned().collect::<std::collections::BTreeSet<_>>()`; return {type: {kind: 'set', element: inner.type.element}, owned, reference: `&(${owned})`};}
    if(value.op === 'input')usedInputs.add(value.name);
    let current = value.op === 'input' ? workflowInputs.get(value.name) : results.get(value.step_id); if (!current) return fail('unavailable Workflow value'); let type = current.type, reference = current.reference;
    for (const ontology of value.properties) {const found = properties.get(ontology); if (!found || type.kind !== 'named' || type.selector !== found.owner) return fail('property owner mismatch:' + ontology); reference += `.${rustSnake(found.property.name)}()`; type = found.property.type;}
    return {type, reference, owned: `Clone::clone(${reference})`};
  };
  const recoveryConstants: string[] = [];
  const recoveryFor = (index: number) => {
    const failed = workflow.steps[index]!, planned = planSelectedWorkflowRecovery(policy, {schema_version: WORKFLOW_FAILURE_JOURNAL_VERSION, workflow_execution_id: 'compile-execution', failure_occurrence_id: 'compile-failure', completed_step_ids: workflow.steps.slice(0, index).map(row => row.step_id), failed_step_id: failed.step_id, failed_commit_status: 'not-committed'});
    const rows = planned.recovery_intent?.plan ?? [], name = `RECOVERY_${index}`;
    if(rows.length)recoveryConstants.push(`const ${name}: &[RecoveryStep] = &[${rows.map(row => `RecoveryStep { compensation_id: ${rustString(row.compensation_id)}, for_step: ${rustString(row.for_step)}, operation_ref: ${rustString(row.operation_ref)}, action_sha256: ${rustString(row.action_sha256)} }`).join(', ')}];`); return rows.length ? `RecoveryDisposition::Required(${name})` : 'RecoveryDisposition::NotRequired';
  };
  const operationBySelector = new Map(operations.modules.map(module => [module.selector, module]));
  const steps = workflow.steps.map((step, index) => {
    const operation = operationBySelector.get(step.operation_ref) ?? fail('missing Operation module'), resultName = `result_${rustSnake(step.step_id)}`, args = step.arguments.map(argument => expression(argument.value).reference);
    const events = step.events.map(event => `${parameterReference(rustSnake(event.input))}.clone()`), clocks = step.events.flatMap(event => workflow.event_inputs.find(input => input.name === event.input)?.contract.occurred_at_policy === 'generated' ? [parameterReference(`clock_${rustSnake(event.input)}`)] : []), store = parameterReference(`store_${rustSnake(step.operation_ref.split(':')[1]!)}`);
    const call = `crate::application::operations::${rustSelectorModule(step.operation_ref)}::${operation.symbol}(${[...args, ...events, ...clocks, store].join(', ')})`;
    const outcome = `crate::application::operations::${rustSelectorModule(step.operation_ref)}::${operation.outcome}`, recovery = recoveryFor(index), completed = workflow.steps.slice(0, index).map(row => rustString(row.step_id)).join(', ');
    results.set(step.step_id, {type: step.signature.result, reference: `&${resultName}`, owned: `${resultName}.clone()`});
    const stop = (disposition: string, extra: string) => `return ${rustPascal(workflow.bindings.selector.split(':')[1]!)}Outcome::Stopped { step_id: ${rustString(step.step_id)}, operation_ref: ${rustString(step.operation_ref)}, disposition: FailureDisposition::${disposition}, ${extra}completed_steps: vec![${completed}], recovery: ${disposition === 'Indeterminate' ? 'RecoveryDisposition::ReconciliationRequired' : recovery} }`;
    return `    let ${resultName} = match ${call}.await {\n        ${outcome}::Committed(value) => value,\n        ${outcome}::Rejected { stage, code, .. } => { ${stop('Rejected', 'stage, code, ')} },\n        ${outcome}::Failed { stage, code, .. } => { ${stop('Failed', 'stage, code, ')} },\n        ${outcome}::Indeterminate { stage, code } => { ${stop('Indeterminate', 'stage, code, ')} },\n    };`;
  }).join('\n');
  const result = expression(workflow.bindings.result.value), name = rustPascal(workflow.bindings.selector.split(':')[1]!), outcome = `${name}Outcome`, relative_path = rustWorkflowPath(selection.module_root, workflow.bindings.selector);
  const usedEvents = new Set(workflow.steps.flatMap(step => step.events.map(event => event.input)));
  const inputParameters = workflow.bindings.inputs.map(input => `${usedInputs.has(input.name)?'':'_'}${rustSnake(input.name)}: &${rustType(input.type)}`), eventParameters = workflow.event_inputs.map(input => `${usedEvents.has(input.name)?'':'_'}${rustSnake(input.name)}: &crate::domain::events::${rustSelectorModule(input.event_ref)}::${rustPascal(input.event_ref.split(':')[1]!)}Input`), clockParameters = generatedClocks.map(input => `${usedEvents.has(input.name)?'':'_'}clock_${rustSnake(input.name)}: &impl Fn() -> String`);
  const storeParameters = uniqueOperations.map(selector => {const module = operationBySelector.get(selector)!; return `store_${rustSnake(selector.split(':')[1]!)}: &impl crate::application::operations::${rustSelectorModule(selector)}::${module.store}`;});
  const groupedGenerics = [...generatedClocks.map((_input, index) => `C${index}: Fn() -> String`), ...uniqueOperations.map((selector, index) => {const module = operationBySelector.get(selector)!; return `S${index}: crate::application::operations::${rustSelectorModule(selector)}::${module.store}`;})];
  const groupedFields = [
    ...workflow.bindings.inputs.map(input => `    pub ${rustSnake(input.name)}: &'a ${rustType(input.type)},`),
    ...workflow.event_inputs.map(input => `    pub ${rustSnake(input.name)}: &'a crate::domain::events::${rustSelectorModule(input.event_ref)}::${rustPascal(input.event_ref.split(':')[1]!)}Input,`),
    ...generatedClocks.map((input, index) => `    pub clock_${rustSnake(input.name)}: &'a C${index},`),
    ...uniqueOperations.map((selector, index) => `    pub store_${rustSnake(selector.split(':')[1]!)}: &'a S${index},`),
  ];
  const execution = `${name}Execution`;
  const groupedDefinition = groupedParameters ? `pub struct ${execution}<'a, ${groupedGenerics.join(', ')}> {\n${groupedFields.join('\n')}\n}\n\n` : '';
  const executeParameters = groupedParameters ? `execution: ${execution}<'_, ${groupedGenerics.map(row => row.split(':')[0]!.trim()).join(', ')}>` : [...inputParameters, ...eventParameters, ...clockParameters, ...storeParameters].join(', ');
  const executeGenerics = groupedParameters ? `<${groupedGenerics.join(', ')}>` : '';
  const content = `// Generated DomainSpec Rust Workflow.\npub const DOMAINSPEC_SELECTOR: &str = ${rustString(workflow.bindings.selector)};\npub const DOMAINSPEC_PROTOCOL_ID: &str = ${rustString(RUST_WORKFLOW_PROTOCOL)};\npub const DOMAINSPEC_WORKFLOW_SHA256: &str = ${rustString(workflow.workflow_sha256)};\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq)]\npub struct RecoveryStep { pub compensation_id: &'static str, pub for_step: &'static str, pub operation_ref: &'static str, pub action_sha256: &'static str }\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq)]\npub enum RecoveryDisposition { NotRequired, Required(&'static [RecoveryStep]), ReconciliationRequired }\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq)]\npub enum FailureDisposition { Rejected, Failed, Indeterminate }\n\n#[derive(Clone, Debug)]\npub enum ${outcome} { Succeeded(${rustType(workflow.bindings.result.type)}), Stopped { step_id: &'static str, operation_ref: &'static str, disposition: FailureDisposition, stage: &'static str, code: &'static str, completed_steps: Vec<&'static str>, recovery: RecoveryDisposition } }\n\n${recoveryConstants.join('\n')}\n\n${groupedDefinition}pub async fn execute${executeGenerics}(${executeParameters}) -> ${outcome} {\n${steps}\n    ${outcome}::Succeeded(${result.owned})\n}\n`;
  const ownArtifact = artifact(relative_path, content), artifacts = [...operations.artifacts, ownArtifact].sort((left, right) => left.relative_path < right.relative_path ? -1 : 1);
  const module = {selector: workflow.bindings.selector, symbol: 'execute', outcome, relative_path, workflow_sha256: workflow.workflow_sha256, policy_sha256: policy.policy_sha256, operation_dependencies: uniqueOperations, compensation_execution: false as const};
  const body = {schema_version: 'domainspec.configured-rust-workflow-plan/v1-candidate' as const, selection: {...selection, actions: operations.selection.actions, factories: operations.selection.factories}, certificate, contract_sha256: RUST_WORKFLOW_CONTRACT_SHA256, protocol_id: RUST_WORKFLOW_PROTOCOL, operation_plan_sha256: operations.plan_sha256, modules: [module], artifacts, authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
