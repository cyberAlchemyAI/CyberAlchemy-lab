import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from './project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from './source-manifest.js';
import {assertWorkflowData, workflowObject, workflowList, workflowFail, freezeWorkflow, decodeWorkflowOccurrences, WORKFLOW_OCCURRENCES_VERSION, WORKFLOW_OCCURRENCE_DEFINITION_SHA256} from '../typed-backend/workflow-occurrences.js';

/** Pure explicit migration candidate. Never rewrites files or registers a checked replacement graph. */
export function planWorkflowOccurrenceMigration(graph: CompiledProjectGraph, selector: string, selection: unknown) {
  assertCompiledProjectSnapshot(graph); assertWorkflowData(selection);
  const selected = workflowObject(selection, ['ontology_workflow', 'step_ids', 'compensation_ids']);
  const stepIds = workflowList(selected.step_ids, 1), compensationIds = workflowList(selected.compensation_ids);
  const node = graph.nodes.find(n => n.selector === selector);
  if (!node || node.kind !== 'Workflow' || node.body.typed_contract !== undefined) return workflowFail('checked legacy Workflow required');
  const oldSteps = node.body.steps as readonly string[], oldCompensations = node.body.compensations as readonly string[];
  if (stepIds.length !== oldSteps.length || compensationIds.length !== oldCompensations.length) workflowFail('explicit IDs must align with legacy occurrences');
  const outgoing = graph.relationships.filter(r => r.relationship === 'orchestrates' && r.source.feature_id + ':' + r.source.node_id === selector);
  const resolve = (id: string): string => {
    const targets = outgoing.filter(r => r.target.node_id === id);
    if (targets.length !== 1) return workflowFail('ambiguous or missing legacy Operation: ' + id);
    return targets[0]!.target.feature_id + ':' + targets[0]!.target.node_id;
  };
  const compIds = new Map<string, unknown>();
  oldCompensations.forEach((id, i) => {
    if (id === 'none') {if (compensationIds[i] !== null) workflowFail('absent compensation requires null ID');}
    else {if (typeof compensationIds[i] !== 'string') workflowFail('explicit compensation ID required'); compIds.set(id, compensationIds[i]);}
  });
  const dependencies = node.body.compensation_dependencies as readonly string[];
  const contract = decodeWorkflowOccurrences({schema_version: WORKFLOW_OCCURRENCES_VERSION, ontology_workflow: selected.ontology_workflow,
    steps: oldSteps.map((id, i) => ({step_id: stepIds[i], operation_ref: resolve(id)})),
    compensations: oldCompensations.flatMap((id, i) => id === 'none' ? [] : [{compensation_id: compensationIds[i], for_step: stepIds[i], operation_ref: resolve(id),
      depends_on: dependencies.filter(d => d.split(':depends-on:')[0] === id).map(d => compIds.get(d.split(':depends-on:')[1]!))}]),
  });
  const relative_path = `specs/${node.feature_id}/nodes/${node.node_id}.json`;
  const source = graph.source_manifest.sources.find(s => s.relative_path === relative_path) ?? workflowFail('missing source evidence');
  const body = {schema_version: 'domainspec.workflow-occurrence-migration/v1-candidate', selector, certificate: createCompiledProjectCertificate(graph),
    definition_sha256: WORKFLOW_OCCURRENCE_DEFINITION_SHA256, source: {relative_path, sha256: source.sha256},
    selection: structuredClone(selection), candidate_body: {description: node.body.description, typed_contract: contract},
    relationship_changes: 'none', validation_ceiling: 'candidate-body-not-replacement-graph', writes_performed: false, authority_effect: 'none'};
  return freezeWorkflow({...body, migration_sha256: sha256(canonicalJson(body))});
}
