import {getReconciledSource as source} from './reconciled-sources.js';

/** Exact compiler-owned bytes; no runtime development-directory lookup. */
export function reconciledPythonSources() {
  const common = {configuration: source('configuration'), base: source('base'), python: source('python')};
  const rules = {...common, rule_contract: source('rule'), collection_contract: source('rule_collection'), predicate_contract: source('rule_predicate'), numeric_contract: source('rule_numeric'), exact_contract: source('rule_exact'), literal_contract: source('rule_literal'), structured_contract: source('rule_structured'), field_contract: source('field')};
  const factories = {...rules, factory_contract: source('factory')};
  const events = {...common, event_contract: source('event')};
  const operations = {operation_contract: source('operation'), factory_contract: source('factory'), reference_contract: source('reference_factory'), rules, events};
  const interfaces = {...common, interface_contract: source('interface'), version_contract: source('interface_version'), field_contract: source('field')};
  return {common, rules, factories, events, operations, interfaces,
    publicMappings: {...interfaces, public_mapping_contract: source('public_mapping_value_object'), generation_contract: source('public_boundary')},
    workflows: {workflow_contract: source('workflow'), materialization_contract: source('workflow_materialization'), outcome_contract: source('workflow_outcome'), recovery_contract: source('workflow_recovery'), operations}};
}
