import {assertCompiledProjectSnapshot, selectCompiledProjectNode, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertReconciledPythonProjectPlan, getPythonCalculationVerificationContext, getPythonDataVerificationContext, getPythonDecisionVerificationContext, getPythonFactoryVerificationContext, type ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import {decodeExactCalculation} from '../typed-backend/calculation-exact.js';
import {decodeTypedCalculationContract} from '../typed-backend/contracts.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {freezePythonProject as freeze} from '../generation/reconciled-python-selection.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {expectedCalculation, type Calculation, type CalculationOutcome} from './calculation-reference.js';
import {createQuerySemanticCases} from './reconciled-query-controls.js';
import {createMappingSemanticCases} from './reconciled-mapping-controls.js';
import {createRuleSemanticCases} from './reconciled-rule-controls.js';
import {createPolicySemanticCases} from './reconciled-policy-controls.js';
import {RuleFactsCapacity} from './reconciled-rule-facts.js';
import {RuleWitnessCapacity} from './reconciled-rule-reference.js';
import {createPythonPlainEnumControls} from './reconciled-python-enum-controls.js';
import {createPythonSumControls} from './reconciled-python-sum-controls.js';
import {createPythonFactoryControls} from './reconciled-python-factory-controls.js';
import {createPythonEventControls} from './reconciled-python-event-controls.js';
import {createPythonStateMachineControls} from './reconciled-python-state-machine-controls.js';
import {createPythonOperationControls} from './reconciled-python-operation-controls.js';
import {createPythonWorkflowControls} from './reconciled-python-workflow-controls.js';
import {createPythonInterfaceControls} from './reconciled-python-interface-controls.js';
import {createPythonPublicMappingControls} from './reconciled-python-public-mapping-controls.js';

export const PYTHON_SEMANTIC_VERIFICATION_SHA256 = '30f5866b07c58074e64ab300637948fb0f8b1237eb301525a3a4615fb38729a1';
export const PYTHON_DATA_SEMANTIC_SHA256 = 'b3487fa4251af241bc1c8b3eb1102f23861d1034a1cefb07ec739f9cc7b116d0';
export const PYTHON_DECISION_SEMANTIC_SHA256 = 'f2ced095ae120816fe223e18d0ee6127a79a9c29cf90df38ddfdf7c58fb1dd3c';
export const PYTHON_ENUM_SEMANTIC_SHA256 = 'c5afd515b061d26ec6c1c883c7b1125d3a3a6644eca516f76ce2b7274c68c39b';
export const PYTHON_OWNED_OBSERVATION_SHA256 = '92c7b8f5fda40049e100fc14af038ad2cde209a6bf7d39d28333424b2f039e5b';
export const PYTHON_SUM_SEMANTIC_SHA256 = 'b0c179f40edaed209c656232fdba6a7c3241d66a8d0ce53eb517194738de1efd';
export const PYTHON_FACTORY_SEMANTIC_SHA256 = 'd9d75f813f8526638cdca065fe7e6799b836b5f3e6cca84b0b132984d711313e';
export const PYTHON_EVENT_SEMANTIC_SHA256 = '2faa5dee0702021b06d470e06242878023f1b09d115835d47a6121bbdf77b47b';
export const PYTHON_STATE_MACHINE_SEMANTIC_SHA256 = '1c743e92986bc0cc050333ef741edc897e60f6455fe7792d67fc965a4220702c';
export const PYTHON_OPERATION_SEMANTIC_SHA256 = '937f3316f24bc16bb3fa83f926346fcefa35def5591dfe8431fdbea2d021d818';
export const PYTHON_WORKFLOW_SEMANTIC_SHA256 = 'ec3c977f62ce7de921812e7a3bad9f4c1ad2910ca1cf8991fa5cc0d624c2f6d8';
export const PYTHON_INTERFACE_SEMANTIC_SHA256 = '8442d778717c5bdc4809eb32fec893c2ab66ba0ebca6e270b1868ccf8f376dbb';
export const PYTHON_PUBLIC_MAPPING_SEMANTIC_SHA256 = '9fd05ddaf92fcdf1b22896e6c4b25878f978836de7f75fb43bba1f9d88a4b8d8';
const fail = (s: string): never => {throw new TypeError('DS_PYTHON_SEMANTIC_CONTROLS:' + s);};
type Case = {id: string; mode: string; format: 'int' | 'string'; values: string[]; expected: CalculationOutcome; bad?: {index: number; kind: string}};
function cases(contract: Calculation): Case[] {
  const length = contract.inputs.length, base = Array.from({length}, () => '1'), vectors = new Map<string, string[]>();
  const add = (values: string[]) => vectors.set(canonicalJson(values), values);
  for (const v of ['0', '1', '2', '3', '9007199254740991', '9007199254740992', '18446744073709551614', '18446744073709551615']) add(base.map(() => v));
  add(base.map((_, i) => String(i + 1))); add(base.map((_, i) => String(length - i + 3)));
  for (let i = 0; i < length; i++) for (const v of ['0', '2', '3', '9007199254740992', '18446744073709551615']) {const values = [...base]; values[i] = v; add(values);}
  const result: Case[] = [], error = {kind: 'error' as const, name: 'TypeError' as const, message: 'CALCULATION_INPUT'};
  const push = (mode: string, format: Case['format'], values: string[], expected: CalculationOutcome, bad?: Case['bad']) => result.push({id: 'case-' + result.length, mode, format, values, expected, ...(bad ? {bad} : {})});
  for (const values of vectors.values()) for (const format of ['int', 'string'] as const) push('record', format, values, expectedCalculation(contract, values));
  for (const mode of ['null', 'array', 'extra', 'subclass', ...(length ? ['missing', 'key-subclass'] : [])]) push(mode, 'int', base, error);
  for (let index = 0; index < length; index++) for (const kind of ['negative', 'overflow', 'padded', 'decimal', 'signed', 'empty', 'nan', 'infinity', 'float', 'fraction', 'null', 'boolean', 'int-subclass', 'str-subclass', 'unicode', 'newline', 'mapping', 'array']) push('record', 'int', base, error, {index, kind});
  if (result.length > 4096) fail('per-node case capacity');
  return result;
}

/** Source-bound metadata preparation. Missing executors remain explicit rows. */
export function createPythonSemanticControls(graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan) {
  assertCompiledProjectSnapshot(graph); assertReconciledPythonProjectPlan(plan);
  if (canonicalJson(createCompiledProjectCertificate(graph)) !== canonicalJson(plan.certificate) || canonicalJson(graph.source_manifest) !== canonicalJson(plan.semantic_sources)) fail('graph/plan identity');
  if (sha256(getReconciledSource('python_semantic')) !== PYTHON_SEMANTIC_VERIFICATION_SHA256) fail('definition drift');
  if (sha256(getReconciledSource('python_data_semantic')) !== PYTHON_DATA_SEMANTIC_SHA256) fail('data definition drift');
  const context = getPythonCalculationVerificationContext(plan);
  const data = getPythonDataVerificationContext(plan);
  const decisions = getPythonDecisionVerificationContext(plan);
  if (sha256(getReconciledSource('python_decision_semantic')) !== PYTHON_DECISION_SEMANTIC_SHA256) fail('decision definition drift');
  if (sha256(getReconciledSource('python_enum_semantic')) !== PYTHON_ENUM_SEMANTIC_SHA256) fail('Enum definition drift');
  if (sha256(getReconciledSource('python_owned_observation')) !== PYTHON_OWNED_OBSERVATION_SHA256) fail('owned observation definition drift');
  if (sha256(getReconciledSource('python_sum_semantic')) !== PYTHON_SUM_SEMANTIC_SHA256) fail('sum definition drift');
  if (sha256(getReconciledSource('python_factory_semantic')) !== PYTHON_FACTORY_SEMANTIC_SHA256) fail('factory definition drift');
  if (sha256(getReconciledSource('python_event_semantic')) !== PYTHON_EVENT_SEMANTIC_SHA256) fail('Event definition drift');
  if (sha256(getReconciledSource('python_state_machine_semantic')) !== PYTHON_STATE_MACHINE_SEMANTIC_SHA256) fail('State Machine definition drift');
  if (sha256(getReconciledSource('python_operation_semantic')) !== PYTHON_OPERATION_SEMANTIC_SHA256) fail('Operation definition drift');
  if (sha256(getReconciledSource('python_workflow_semantic')) !== PYTHON_WORKFLOW_SEMANTIC_SHA256) fail('Workflow definition drift');
  if (sha256(getReconciledSource('python_interface_semantic')) !== PYTHON_INTERFACE_SEMANTIC_SHA256) fail('Interface definition drift');
  if (sha256(getReconciledSource('python_public_mapping_semantic')) !== PYTHON_PUBLIC_MAPPING_SEMANTIC_SHA256) fail('public Mapping definition drift');
  const rows = graph.nodes.map(node => {
    if (node.kind === 'Mapping' && (node.body.typed_contract as {schema_version?: string}).schema_version === 'domainspec.typed-mapping/v3') return createPythonPublicMappingControls(node, graph, plan);
    if (node.kind === 'Interface') return createPythonInterfaceControls(node, graph, plan);
    if (node.kind === 'Workflow') return createPythonWorkflowControls(node, graph, plan);
    if (node.kind === 'Operation') return createPythonOperationControls(node, graph, plan);
    if (node.kind === 'State Machine') return createPythonStateMachineControls(node, graph, plan);
    if (node.kind === 'Event') return createPythonEventControls(node, graph, plan);
    if (node.kind === 'Entity' || node.kind === 'Value Object') return createPythonFactoryControls(node, graph, plan);
    if (node.kind === 'Enum') {
      const plain = createPythonPlainEnumControls(node, graph, plan);
      return plain.state === 'ready' ? plain : createPythonSumControls(node, graph, plan);
    }
    if (node.kind === 'Rule' || node.kind === 'Policy') {
      const pending = (reason: string) => ({selector: node.selector, kind: node.kind, state: 'not_evaluable' as const, reason});
      try {
        if (node.kind === 'Rule') {
          const module = decisions.rules.find(m => m.selector === node.selector) ?? fail('missing private Rule binding');
          const shared = createRuleSemanticCases(node, graph);
          if (canonicalJson(shared.rule) !== canonicalJson(node.body.typed_contract) || module.closure_sha256 !== selectCompiledProjectNode(graph, node.selector).typed_closure?.closure_sha256) fail('Rule source/closure mismatch');
          return {selector: node.selector, kind: node.kind, state: 'ready' as const, module, contract: shared.rule, cases: shared.cases, recipes: shared.recipes};
        }
        const module = decisions.policies.find(m => m.selector === node.selector) ?? fail('missing private Policy binding');
        const shared = createPolicySemanticCases(node, graph);
        if (sha256(canonicalJson(shared.contract)) !== module.descriptor.contract_sha256 || (data.model?.model_sha256 ?? null) !== module.descriptor.field_model_sha256) fail('Policy source/model mismatch');
        if (shared.targets.size < 2) return pending('bounded Policy cases lack distinct-target input-sensitivity witnesses; no unreachable-branch claim');
        return {selector: node.selector, kind: node.kind, state: 'ready' as const, module, contract: shared.contract, cases: shared.cases, recipes: shared.recipes,
          source_predicted_targets: [...shared.targets].sort(), source_predicted_branches: [...shared.branches].sort((a, b) => a - b)};
      } catch (error) {
        if (error instanceof RuleFactsCapacity || error instanceof RuleWitnessCapacity) return pending(error.message);
        throw error;
      }
    }
    if (node.kind === 'Query' || node.kind === 'Mapping' && (node.body.typed_contract as {schema_version?: string}).schema_version !== 'domainspec.typed-mapping/v3') {
      const module = (node.kind === 'Query' ? data.queries : data.mappings).find(m => m.selector === node.selector) ?? fail('missing private data binding');
      const shared = node.kind === 'Query' ? createQuerySemanticCases(node, graph) : createMappingSemanticCases(node, graph);
      if (sha256(canonicalJson(shared.contract)) !== module.descriptor.contract_sha256 || data.model?.model_sha256 !== module.descriptor.field_model_sha256) fail('data source/model mismatch');
      return {selector: node.selector, kind: node.kind, state: 'ready' as const, module, contract: shared.contract, cases: shared.cases, recipes: shared.recipes};
    }
    if (node.kind !== 'Calculation') return {selector: node.selector, kind: node.kind, state: 'not_evaluable' as const, reason: 'semantic executor not yet integrated'};
    const module = context?.modules.find(m => m.selector === node.selector) ?? fail('missing private Calculation binding');
    const raw = node.body.typed_contract as {schema_version?: unknown};
    const contract = raw.schema_version === 'domainspec.typed-calculation/v2' ? decodeExactCalculation(raw) : decodeTypedCalculationContract(raw);
    if (canonicalJson(contract) !== canonicalJson(context!.contracts[node.selector]) || sha256(canonicalJson(contract)) !== module.descriptor.contract_sha256) fail('Calculation source mismatch');
    return {selector: node.selector, kind: node.kind, state: 'ready' as const, module, contract, cases: cases(contract)};
  });
  const case_count = rows.reduce((n, r) => n + (r.state === 'ready' ? r.cases.length : 0), 0);
  const body = {schema_version: 'domainspec.python-semantic-controls/v1-candidate' as const, definition_sha256: PYTHON_SEMANTIC_VERIFICATION_SHA256, data_definition_sha256: PYTHON_DATA_SEMANTIC_SHA256, decision_definition_sha256: PYTHON_DECISION_SEMANTIC_SHA256, project_plan_sha256: plan.plan_sha256, rows, case_count, support_path: context?.support_path ?? null, data_model: data.model, runtime_dir: data.runtime_dir,
    enum_definition_sha256: PYTHON_ENUM_SEMANTIC_SHA256,
    owned_observation_sha256: PYTHON_OWNED_OBSERVATION_SHA256,
    sum_definition_sha256: PYTHON_SUM_SEMANTIC_SHA256,
    factory_definition_sha256: PYTHON_FACTORY_SEMANTIC_SHA256,
    event_definition_sha256: PYTHON_EVENT_SEMANTIC_SHA256,
    state_machine_definition_sha256: PYTHON_STATE_MACHINE_SEMANTIC_SHA256,
    operation_definition_sha256: PYTHON_OPERATION_SEMANTIC_SHA256,
    workflow_definition_sha256: PYTHON_WORKFLOW_SEMANTIC_SHA256,
    interface_definition_sha256: PYTHON_INTERFACE_SEMANTIC_SHA256,
    public_mapping_definition_sha256: PYTHON_PUBLIC_MAPPING_SEMANTIC_SHA256,
    factory_modules: getPythonFactoryVerificationContext(plan), factory_bindings: plan.selection.factories,
    rule_modules: decisions.rules, rule_contracts: Object.fromEntries(graph.nodes.filter(n => n.kind === 'Rule').map(n => [n.selector, n.body.typed_contract]))};
  if (case_count > 65536 || Buffer.byteLength(canonicalJson(body)) > 8388608) fail('control capacity');
  return freeze({...body, controls_sha256: sha256(canonicalJson(body))});
}
export type PythonSemanticControls = ReturnType<typeof createPythonSemanticControls>;
