import type { CompiledProjectGraph } from '../input/project-model.js';
import type { CompiledCompositionBoundary } from '../input/composition-boundary.js';
import type { CompiledProjectFields } from '../input/compiled-field-model.js';
import { compileOperationValueReferences } from '../typed-operation/value-composition-references.js';
import { compileOperationValueTypes } from '../typed-operation/value-composition-types.js';
import { compileComposedOperationActionBindings } from '../typed-operation/action-bindings.js';
import { planConfiguredComposedOperations, type ComposedOperationSelection } from './configured-composed-operations.js';
import { getReconciledSource } from './reconciled-sources.js';
import {compileComposedWorkflowBindings} from '../typed-operation/workflow-bindings.js';
import type {ComposedWorkflowAction} from '../typed-operation/composed-settlement.js';
import {planConfiguredComposedWorkflow,type ComposedWorkflowSelection} from './configured-workflows.js';

/** Candidate composition checking with compiler-owned, packaged contracts.
 * No source-directory reads, provider execution or publication are performed.
 */
export function compileComposedOperation(
  graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields,
  composition: unknown, action: unknown,
) {
  const references = compileOperationValueReferences(graph, boundary, fields, composition, action, getReconciledSource('operation_value_composition'));
  const typed = compileOperationValueTypes(graph, fields, references);
  return compileComposedOperationActionBindings(graph, boundary, fields, typed, getReconciledSource('operation_action'));
}

/** Plan native artifacts from checked actions; this does not write or execute them. */
export function planComposedOperations(
  graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields,
  selection: ComposedOperationSelection,
) {
  return planConfiguredComposedOperations(graph, boundary, fields, selection, getReconciledSource('composed_operation'));
}

export function compileComposedWorkflow(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,fields:CompiledProjectFields,actions:readonly ComposedWorkflowAction[],bindings:unknown){
  return compileComposedWorkflowBindings(graph,boundary,fields,actions,bindings,getReconciledSource('workflow_binding'),getReconciledSource('composed_workflow'));
}
export function planComposedWorkflow(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,fields:CompiledProjectFields,selection:ComposedWorkflowSelection){
  return planConfiguredComposedWorkflow(graph,boundary,fields,selection,getReconciledSource('composed_workflow'));
}
