import assert from 'node:assert/strict';
import test from 'node:test';
import {workflowFixture} from '../helpers/workflow-verification.ts';
import {mixedWorkflowPublicFixture, runPublicWorkflowCoverage} from '../helpers/workflow-public-mixed.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {createWorkflowControls, workflowVerificationDefinitions} from '../../src/verification/reconciled-workflow-controls.ts';
import {createWorkflowBinding} from '../../src/verification/reconciled-workflow-binding.ts';
import {createWorkflowEffectAudit} from '../../src/verification/reconciled-workflow-effect-audit.ts';
import {prepareCrossGeneratorVerification, crossGeneratorPreparationBindings} from '../../src/verification/reconciled-cross-generator-public.ts';

test('scalar standalone and retained source families agree on every recipe, dimension, case and complete semantic commitment', t => {
  const f = workflowFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection);
  const node = f.graph.nodes.find(n => n.kind === 'Workflow')!;
  const standalone = createWorkflowControls(node, f.graph, plan);
  if (standalone.state !== 'ready') assert.fail(standalone.reason); assert.equal(standalone.state, 'ready');
  const preparation = prepareCrossGeneratorVerification(f.graph, plan);
  const selected = crossGeneratorPreparationBindings(preparation, f.graph, plan).bindings.workflow;
  if (selected.state !== 'prepared') assert.fail(selected.reason); assert.equal(selected.state, 'prepared');
  const retained = selected.value.controls.rows.find(r => r.selector === node.selector)!;
  if (retained.state !== 'ready') assert.fail(retained.reason); assert.equal(retained.state, 'ready');
  assert.equal(standalone.cases.length, 134); assert.equal(retained.cases.length, 133);
  assert.deepEqual(standalone.recipes, retained.recipes);
  assert.deepEqual(standalone.coverage, retained.dimensions);
  assert.deepEqual(standalone.search, retained.search);
  assert.deepEqual(standalone.cases[0], {id: 'binding', mode: 'workflow-descriptor', format: 'string', values: [], expected: {kind: 'value', value: canonicalJson(retained.descriptor)}});
  const expected = standalone.cases.slice(1).map(c => {
    assert.equal(c.mode, 'workflow'); assert.equal(c.format, 'string'); assert.equal(c.values.length, 1);
    assert.equal(c.expected.kind, 'value'); if (c.expected.kind !== 'value') assert.fail('complete semantic value required');
    assert.equal(c.expected.value, canonicalJson(JSON.parse(c.expected.value)));
    return {id: c.id, data: JSON.parse(c.values[0]!), semantic_sha256: sha256(c.expected.value)};
  });
  assert.deepEqual(retained.cases.map(c => ({id: c.id, data: c.data, semantic_sha256: c.expected.semantic_sha256})), expected);
  assert.equal(new Set(expected.map(c => c.id)).size, expected.length);
  t.diagnostic('All 133 ordered semantic commitments and the additional standalone descriptor agree; source comparison alone is not native execution proof.');
});

test('mixed Workflow graph preserves both lawful roots and the complete shared and distinct audit paths', t => {
  const f = mixedWorkflowPublicFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection);
  const definitions = workflowVerificationDefinitions(), nodes = f.graph.nodes.filter(n => n.kind === 'Workflow');
  assert.deepEqual(nodes.map(n => n.selector).sort(), ['commerce:flow', 'commerce:oversized-flow']);
  assert.equal(f.graph.nodes.length, 19);
  const bindings = nodes.map(n => createWorkflowBinding(n, f.graph, plan, definitions.binding));
  const original = bindings.find(b => b.workflow.bindings.selector === 'commerce:flow')!;
  const oversized = bindings.find(b => b.workflow.bindings.selector === 'commerce:oversized-flow')!;
  assert.equal(original.workflow.steps.length, 4); assert.equal(oversized.workflow.steps.length, 64);
  const occurrence = ({action_sha256, ...rest}: {action_sha256: string}) => rest;
  assert.deepEqual(oversized.workflow.bindings.compensations.map(occurrence), original.workflow.bindings.compensations.map(occurrence));
  assert.deepEqual(oversized.workflow.bindings.steps.slice(0, 4).map(occurrence), original.workflow.bindings.steps.map(occurrence));
  const shared = original.module_paths.filter(p => oversized.module_paths.includes(p));
  assert.ok(shared.length > 0);
  const distinct = oversized.module_paths.filter(p => !shared.includes(p));
  for (const own of [oversized.relative_path, oversized.provider_path, oversized.material_path]) assert.ok(distinct.includes(own));
  assert.ok(distinct.some(p => p.endsWith('/oversized-perform.ts')));
  const audit = createWorkflowEffectAudit(f.graph, plan, definitions.binding, definitions.effects);
  assert.deepEqual(audit.roots, ['commerce:flow', 'commerce:oversized-flow']);
  assert.deepEqual(audit.module_paths, [...new Set(bindings.flatMap(b => b.module_paths))].sort());
  assert.ok(audit.module_paths.length > original.module_paths.length);
});

test('mixed Workflow preparation retains the complete ready family and a real whole-family capacity failure', t => {
  const f = mixedWorkflowPublicFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection);
  const preparation = prepareCrossGeneratorVerification(f.graph, plan);
  const selected = crossGeneratorPreparationBindings(preparation, f.graph, plan).bindings.workflow;
  if (selected.state !== 'prepared') assert.fail(selected.reason); assert.equal(selected.state, 'prepared');
  const rows = selected.value.controls.rows;
  assert.equal(rows.length, 2);
  const ready = rows.find(r => r.selector === 'commerce:flow')!, unavailable = rows.find(r => r.selector === 'commerce:oversized-flow')!;
  if (ready.state !== 'ready') assert.fail(ready.reason); assert.equal(ready.state, 'ready');
  assert.equal(ready.cases.length, 12472);
  assert.equal(ready.cases.reduce((count, c) => count + c.expected.calls.length, 0), 20369);
  assert.equal(ready.batches.length, 4);
  assert.equal(unavailable.state, 'not_evaluable'); if (unavailable.state !== 'not_evaluable') assert.fail('expected actual capacity boundary');
  assert.equal(unavailable.reason, 'bounded Workflow serialized family exceeds 32 MiB');
  assert.ok(!Object.hasOwn(unavailable, 'cases'), 'never retain a smaller passing prefix');
  assert.ok(preparation.rows.some(r => r.family === 'workflow' && r.selector === unavailable.selector && r.state === 'not_evaluable'));
  t.diagnostic(JSON.stringify({ready: ready.selector, cases: ready.cases.length, unavailable: unavailable.selector, reason: unavailable.reason}));
});

test('native scalar public evidence binds both complete standalone and retained semantic lanes', t => {
  const f = workflowFixture(t);
  t.diagnostic(runPublicWorkflowCoverage(f, `
const node=graph.nodes.find(n=>n.kind==='Workflow'),standalone=createWorkflowControls(node,graph,plan);
assert.equal(standalone.state,'ready');assert.equal(standalone.cases.length,134);
const before=canonicalJson(standalone),r=execute(),coverage=r.workflow_public_coverage;
assert.equal(canonicalJson(createWorkflowControls(node,graph,plan)),before);
assert.equal(r.checks.find(c=>c.id==='workflow-public-evidence-currentness').result,'pass');
const row=coverage.binding.rows.find(row=>row.selector===node.selector),e=row.evidence;
assert.equal(row.retained_status,'observed');assert.equal(row.standalone.state,'ready');assert.equal(e.case_count,133);
assert.equal(e.recipes_sha256,sha256(canonicalJson(standalone.recipes)));
assert.deepEqual(e.dimensions,standalone.coverage);assert.deepEqual(e.search,standalone.search);
assert.equal(e.descriptor_sha256,sha256(standalone.cases[0].expected.value));
assert.equal(e.case_ids_sha256,sha256(canonicalJson(standalone.cases.slice(1).map(c=>c.id))));
assert.equal(e.semantic_commitments_sha256,sha256(canonicalJson(standalone.cases.slice(1).map(c=>({id:c.id,semantic_sha256:sha256(c.expected.value)})))));
const original=coverage.standalone_checks.find(c=>c.id==='selected-generator-semantic-controls');
assert.ok(original.executed);assert.notEqual(original.result,'fail');
assert.ok(original.evidence.tested.some(c=>c.selector===node.selector&&c.kind==='Workflow'&&c.case_count===134&&c.contract_sha256===standalone.contract_sha256));
const fulfillment=coverage.semantic_fulfillment.find(c=>c.selector===node.selector);
assert.equal(fulfillment.result,'pass');assert.deepEqual(fulfillment.origins,['original-standalone-native','original-retained-workflow']);
assert.equal(r.checks.find(c=>c.id==='verification-workspace-cleanup').result,'pass');assert.deepEqual(fs.readdirSync(scratch),[]);
console.log(JSON.stringify({standalone_cases:134,retained_cases:133,full_commitments_match:true,origins:fulfillment.origins}));
`));
});

test('native mixed public evidence preserves unavailable Workflow paths with qualified selected Operation witnesses', t => {
  const f = mixedWorkflowPublicFixture(t);
  t.diagnostic(runPublicWorkflowCoverage(f, `
const definitions=workflowVerificationDefinitions();
const sourceBindings=graph.nodes.filter(n=>n.kind==='Workflow').map(n=>createWorkflowBinding(n,graph,plan,definitions.binding));
const required=[...new Set(sourceBindings.flatMap(b=>b.module_paths))].sort();
const readySource=sourceBindings.find(b=>b.workflow.bindings.selector==='commerce:flow');
const missingSource=sourceBindings.find(b=>b.workflow.bindings.selector==='commerce:oversized-flow');
const shared=readySource.module_paths.filter(p=>missingSource.module_paths.includes(p));assert.ok(shared.length>0);
const missing=required.filter(p=>!readySource.module_paths.includes(p));assert.ok(missing.length>0);
const r=execute(),coverage=r.workflow_public_coverage,binding=coverage.binding;
assert.equal(r.result,'incomplete');
assert.deepEqual(r.checks.filter(c=>c.result==='fail').map(c=>c.id),[]);
const failedFamilies=r.cross_generator_coverage.execution.families.filter(f=>f.result==='fail');
assert.equal(failedFamilies.length,0);
const operationFamily=r.cross_generator_coverage.execution.families.find(f=>f.family==='operation');assert.equal(operationFamily.result,'pass');
assert.equal(binding.node_count,19);assert.equal(binding.workflow_count,2);assert.equal(binding.retained_status,'incomplete');
assert.equal(r.checks.find(c=>c.id==='workflow-public-evidence-binding').result,'pass');
assert.equal(r.checks.find(c=>c.id==='workflow-public-evidence-currentness').result,'pass');assert.deepEqual(coverage.retained_blocked_by,[]);
const ready=binding.rows.find(row=>row.selector==='commerce:flow'),unavailable=binding.rows.find(row=>row.selector==='commerce:oversized-flow');
assert.equal(ready.retained_status,'observed');assert.equal(ready.evidence.case_count,12472);assert.equal(ready.evidence.call_count,20369);
assert.equal(unavailable.retained_status,'not_evaluable');assert.equal(unavailable.evidence,null);assert.match(unavailable.reason,/exceeds 32 MiB/);
assert.equal(binding.facets.length,6);
for(const facet of binding.facets){
 const facetRequired=facet.facet.endsWith(':orchestration')?sourceBindings.map(b=>b.provider_path).sort():required;
 const facetObserved=facetRequired.filter(p=>readySource.module_paths.includes(p));
 assert.equal(facet.status,'not_evaluable');assert.deepEqual(facet.required_source_paths,facetRequired);
 assert.deepEqual(facet.missing_source_paths,facetRequired.filter(p=>!facetObserved.includes(p)));assert.deepEqual(facet.missing_workflow_selectors,['commerce:oversized-flow']);
 assert.deepEqual(facet.observed.map(o=>o.source_path),facetObserved);
 if(!facet.facet.endsWith(':orchestration'))assert.ok(shared.every(p=>facet.observed.some(o=>o.source_path===p)));
}
assert.equal(coverage.semantic_fulfillment.length,19);
assert.equal(coverage.semantic_fulfillment.find(row=>row.selector==='commerce:flow').result,'pass');
const unmet=coverage.semantic_fulfillment.find(row=>row.selector==='commerce:oversized-flow');assert.equal(unmet.result,'not_evaluable');assert.deepEqual(unmet.origins,[]);
for(const audit of coverage.audit_fulfillment){
 const facetRequired=audit.id.includes('orchestration')?sourceBindings.map(b=>b.provider_path).sort():required;
 assert.equal(audit.result,'not_evaluable');assert.deepEqual(audit.evidence.required_source_paths,facetRequired);
 assert.deepEqual(audit.evidence.missing_source_paths,facetRequired.filter(p=>!readySource.module_paths.includes(p)));assert.deepEqual(audit.evidence.missing_workflow_selectors,['commerce:oversized-flow']);
}
assert.equal(r.checks.find(c=>c.id==='selected-generator-semantic-controls').result,'not_evaluable');
assert.equal(r.checks.find(c=>c.id==='verification-workspace-cleanup').result,'pass');assert.deepEqual(fs.readdirSync(scratch),[]);
console.log(JSON.stringify({nodes:19,workflows:2,observed_cases:12472,shared_paths:shared.length,missing_paths:missing.length,unavailable:unmet.selector,operation_family:operationFamily.result,overall:r.result}));
`));
});
