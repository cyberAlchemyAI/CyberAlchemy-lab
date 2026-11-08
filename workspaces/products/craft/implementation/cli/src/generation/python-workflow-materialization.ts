import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {assertCheckedWorkflowBindings, type CheckedWorkflowBindings} from '../typed-operation/workflow-bindings.js';
import {freezeWorkflow} from '../typed-backend/workflow-occurrences.js';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {eventReferenceIdentity} from './event-reference-identity.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {pythonPortableIdentifier, pythonStringLiteral} from './configured-python-enums.js';
import {pythonRelativeModule, pythonSnake} from './configured-python-owned-values.js';
import {WORKFLOW_MATERIALIZATION_CONTRACT_SHA256} from './workflow-materialization-source.js';
import {renderPythonWorkflowMaterialization} from './python-workflow-materialization-source.js';
import {renderPythonValueSupport} from './configured-python-value-source.js';
import {renderPythonFactSupport} from './configured-python-fact-source.js';
import {renderPythonEventValues} from './configured-python-event-values.js';

const fail = (why: string): never => {throw new TypeError('PYTHON_WORKFLOW_MATERIALIZATION:' + why);};

/** Native pure prerequisite for Workflow orchestration, not execution itself. */
export function planPythonWorkflowMaterialization(graph: CompiledProjectGraph, workflow: CheckedWorkflowBindings, fields: CompiledProjectFields | null, contractSource: string, moduleRoot: string) {
  assertCompiledProjectSnapshot(graph); assertCheckedWorkflowBindings(workflow); if (fields !== null) assertCompiledProjectFields(fields);
  if (canonicalJson(createCompiledProjectCertificate(graph)) !== canonicalJson(workflow.certificate)) fail('source certificate mismatch');
  if ((fields !== null && (fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION || fields.certificate.graph_sha256 !== workflow.certificate.graph_sha256)) ||
    (fields?.compilation_sha256 ?? null) !== workflow.field_compilation_sha256) fail('stale or incompatible fields');
  if (typeof contractSource !== 'string' || sha256(contractSource) !== WORKFLOW_MATERIALIZATION_CONTRACT_SHA256) fail('contract drift');
  if (typeof moduleRoot !== 'string') fail('module root');
  const segments = moduleRoot.split('/'); segments.forEach(pythonPortableIdentifier);
  if (['enum', 'typing', 'types', 'builtins', 'dataclasses', 'collections', 'json', 'sys', 'hashlib', 'weakref', 'codecs', 'encodings', 'math', 're'].includes(segments[0]!)) fail('standard library shadow');
  const root = segments.map(pythonSnake).join('/'), [feature, id] = workflow.bindings.selector.split(':') as [string, string];
  [feature, id].forEach(pythonPortableIdentifier);
  const relative_path = `${root}/features/${pythonSnake(feature)}/src/application/workflows/_material/${pythonSnake(id)}.py`;
  const artifacts: {relative_path: string; content: string; sha256: string; size_bytes: number}[] = [];
  const add = (relative_path: string, content: string) => {
    const a = {relative_path, content, sha256: sha256(content), size_bytes: Buffer.byteLength(content)}; artifacts.push(a); return a;
  };
  const runtime = [add(root + '/runtime/values.py', renderPythonValueSupport()), add(root + '/runtime/facts.py', renderPythonFactSupport())];
  if (workflow.event_inputs.length) runtime.push(add(root + '/runtime/event_values.py', renderPythonEventValues()));
  const selectors = [...new Set(workflow.event_inputs.flatMap(e => [e.contract.occurrence_id, ...e.contract.payload].flatMap(f => f.type_ref.kind === 'reference' ? [f.type_ref.selector] : [])))].sort();
  const references = selectors.map(selector => {
    const [feature, node] = selector.split(':') as [string, string]; [feature, node].forEach(pythonPortableIdentifier);
    const {scalar} = eventReferenceIdentity(graph, selector, fail);
    const a = add(`${root}/runtime/event_references/${pythonSnake(feature)}/${pythonSnake(node)}.py`, 'from typing import NewType as _NewType\n\nEventRef = _NewType(' + pythonStringLiteral(selector) + ', '+(scalar==='UInt64'?'int':'str')+')\n');
    return {selector, module: pythonRelativeModule(relative_path, a.relative_path), relative_path: a.relative_path, sha256: a.sha256,scalar};
  });
  const descriptor = freezeWorkflow({schema_version: 'domainspec.python-workflow-materialization-descriptor/v1-candidate',
    workflow_sha256: workflow.workflow_sha256, field_compilation_sha256: fields?.compilation_sha256 ?? null,
    contract_sha256: WORKFLOW_MATERIALIZATION_CONTRACT_SHA256, selector: workflow.bindings.selector,
    steps: workflow.steps.map(s => ({step_id: s.step_id, operation_ref: s.operation_ref, action_sha256: s.action_sha256})),
    compensations: workflow.compensations.map(c => ({compensation_id: c.compensation_id, for_step: c.for_step, operation_ref: c.operation_ref, action_sha256: c.action_sha256})),
    effect_contract: 'pure-typed-materialization', invariant_execution: 'not-performed', commit_evidence: 'not-established',
    event_construction: 'not-performed', authority_effect: 'none'});
  const source = add(relative_path, renderPythonWorkflowMaterialization(workflow, fields?.model ?? null,
    pythonRelativeModule(relative_path, root + '/runtime/values.py').replace(/\.values$/, ''), references, descriptor));
  for (const a of [...artifacts]) {
    const parts = a.relative_path.split('/');
    for (let i = 1; i < parts.length; i++) {const init = parts.slice(0, i).join('/') + '/__init__.py'; if (!artifacts.some(a => a.relative_path === init)) add(init, '');}
  }
  artifacts.sort((a, b) => a.relative_path < b.relative_path ? -1 : 1);
  const body = {schema_version: 'domainspec.python-workflow-materialization-plan/v1-candidate', workflow_sha256: workflow.workflow_sha256,
    module_root: root, relative_path, import_name: relative_path.slice(0, -3).replaceAll('/', '.'), descriptor, descriptor_sha256: sha256(canonicalJson(descriptor)),
    provider_sha256: source.sha256, runtime: runtime.map(a => ({relative_path: a.relative_path, sha256: a.sha256})), references:references.map(({scalar:_scalar,...reference})=>reference), artifacts, authority_effect: 'none'};
  return freezeWorkflow({...body, plan_sha256: sha256(canonicalJson(body))});
}
