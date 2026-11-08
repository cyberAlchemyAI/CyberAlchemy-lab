import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {
  evaluateCompiledObligationWitness,
  loadCompiledProjectGraph,
  ProjectModelError,
  validateCompiledProjectGraphObligations,
} from '../../src/input/project-model.ts';
import {relationshipEvidenceId} from '../../src/input/relationship-identity.ts';
import {commerceSourceRoot} from '../helpers/reconciled-commerce-corpus.ts';

const canonicalRoot = path.resolve(import.meta.dirname, '../../fixtures/input-roots/canonical-project');
const profilePath = path.resolve(import.meta.dirname, '../../../../definitions/minted-project/supported-profiles.yml');
const reconciliationRoot = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation');

function writeJson(file: string, value: unknown): void {
  fs.mkdirSync(path.dirname(file), {recursive: true});
  fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n');
}

function completeRelationshipGraphs(t: test.TestContext) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'domainspec-r14-relationships-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  fs.cpSync(commerceSourceRoot, root, {recursive: true});
  const featureFile = path.join(root, 'specs/commerce/feature.json');
  const feature = JSON.parse(fs.readFileSync(featureFile, 'utf8'));
  const featureEdges = [
    ['total-calculates-perform', 'calculates', 'total', 'perform'],
    ['order-contains-money', 'contains', 'order', 'money'],
    ['order-emits-posted', 'emits', 'order', 'posted'],
  ] as const;
  for (const [edge_id, relationship, source_node_id, target_node_id] of featureEdges) {
    feature.edges.push(edge_id);
    writeJson(path.join(root, `specs/commerce/edges/${edge_id}.json`), {
      schema_version: 'domainspec.edge/v1', edge_id, feature_id: 'commerce', relationship,
      source_node_id, target_node_id, scope: 'feature',
    });
  }
  writeJson(featureFile, feature);
  const projectFile = path.join(root, 'project.json'), project = JSON.parse(fs.readFileSync(projectFile, 'utf8'));
  project.cross_feature_edges.push('perform-produces-for-billing-customer');
  writeJson(path.join(root, 'edges/perform-produces-for-billing-customer.json'), {
    schema_version: 'domainspec.edge/v1', edge_id: 'perform-produces-for-billing-customer',
    source_feature_id: 'commerce', source_node_id: 'perform', target_feature_id: 'billing',
    target_node_id: 'customer', relationship: 'produces-for', scope: 'project',
  });
  writeJson(projectFile, project);
  return [{root, graph: loadCompiledProjectGraph(root)}, {root: canonicalRoot, graph: loadCompiledProjectGraph(canonicalRoot)}];
}

test('R14 all 17 backend signatures and all 44 frozen obligations have executable current witnesses', t => {
  const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8')).profiles.find((row: any) => row.id === 'complete-backend-criteria');
  const graphs = completeRelationshipGraphs(t);
  for (const {graph} of graphs) validateCompiledProjectGraphObligations(graph);
  const relationshipIds = [...new Set(graphs.flatMap(({graph}) => graph.relationships.map(row => row.relationship)))];
  assert.deepEqual(relationshipIds.sort(), [...profile.relationship_ids].sort());
  const pairs = new Map<string, any>();
  for (const {graph} of graphs) for (const witness of graph.obligation_witnesses) {
    const key = witness.predicate.relationship_id + ':' + witness.obligation_id;
    pairs.set(key, {graph, witness});
    assert.equal(evaluateCompiledObligationWitness(graph, witness).outcome, 'pass');
  }
  assert.equal(pairs.size, 44);
  for (const id of profile.relationship_ids) {
    const keys = [...pairs.keys()].filter(key => key.startsWith(id + ':'));
    assert.ok(keys.length > 0, id);
  }
});

test('R14 all 44 obligations reject semantic graph mutants rather than changed expected answers', t => {
  const graphs = completeRelationshipGraphs(t);
  const cases = new Map<string, {graph: any; witness: any}>();
  for (const {graph} of graphs) for (const witness of graph.obligation_witnesses) {
    const key = witness.predicate.relationship_id + ':' + witness.obligation_id;
    if (!cases.has(key)) cases.set(key, {graph, witness});
  }
  assert.equal(cases.size, 44);
  assert.deepEqual([...new Set([...cases.values()].map(row => row.witness.family))].sort(), ['deprecation', 'endpoint', 'generated-projection', 'inverse-collapse', 'multiplicity', 'scope']);
  let killed = 0;
  for (const [id, row] of cases) {
    const family = row.witness.family;
    const graph: any = structuredClone(row.graph), witness: any = structuredClone(row.witness);
    const edge = graph.relationships.find((candidate: any) => candidate.edge_id === witness.edge_id && candidate.scope === witness.witness.scope);
    assert.ok(edge, family);
    if (family === 'endpoint') {
      const isSource = witness.obligation_id.endsWith('_source');
      const allowed = isSource ? witness.predicate.allowed_source_types : witness.predicate.allowed_target_types;
      const invalid = ['Entity', 'Value Object', 'Enum', 'Rule', 'Calculation', 'Policy', 'Query', 'Operation', 'Workflow', 'State Machine', 'Mapping', 'Event', 'Interface'].find(kind => !allowed.includes(kind));
      assert.ok(invalid);
      const endpoint = isSource ? edge.source : edge.target;
      endpoint.kind = invalid;
      witness.witness[isSource ? 'source_type' : 'target_type'] = invalid;
      const selector = isSource ? witness.witness.source_selector : witness.witness.target_selector;
      graph.nodes.find((node: any) => node.selector === selector).kind = invalid;
    } else if (family === 'scope') {
      edge.scope = edge.scope === 'feature' ? 'project' : 'feature';
      witness.witness.scope = edge.scope;
      witness.witness_id = `${relationshipEvidenceId(edge, graph.relationships)}:${witness.obligation_id}`;
    } else if (family === 'multiplicity') {
      const clone = structuredClone(edge);
      clone.edge_id += '-duplicate';
      if (witness.obligation_id === 'reject_multiple_targets_per_source') {
        clone.target.node_id += '-other';
        graph.nodes.push({...structuredClone(graph.nodes.find((node: any) => node.selector === witness.witness.target_selector)), selector: `${clone.target.feature_id}:${clone.target.node_id}`, node_id: clone.target.node_id});
      } else {
        clone.source.node_id += '-other';
        graph.nodes.push({...structuredClone(graph.nodes.find((node: any) => node.selector === witness.witness.source_selector)), selector: `${clone.source.feature_id}:${clone.source.node_id}`, node_id: clone.source.node_id});
      }
      graph.relationships.push(clone);
    } else if (family === 'generated-projection') {
      const source = graph.nodes.find((node: any) => node.selector === witness.witness.source_selector), attribute = witness.predicate.generated_projection_attribute;
      if (witness.obligation_id === 'reject_authored_generated_projection') source.authored_forbidden_projection_attributes.push(attribute);
      else source.generated_relationship_projections[attribute] = [];
    } else if (family === 'inverse-collapse') {
      graph.relationships.push({...structuredClone(edge), edge_id: edge.edge_id + '-inverse', relationship: 'owns', source: structuredClone(edge.target), target: structuredClone(edge.source)});
    } else {
      edge.relationship = 'queries';
      witness.witness_id = `${relationshipEvidenceId(edge, graph.relationships)}:${witness.obligation_id}`;
    }
    assert.throws(
      () => evaluateCompiledObligationWitness(graph, witness),
      error => error instanceof ProjectModelError && error.code === 'MTCLI_COMPILED_OBLIGATION_ENFORCEMENT',
      id,
    );
    killed++;
  }
  assert.equal(killed, 44);
});

test('R14 every relationship endpoint is backed by current three-language native cells and the compound corpus', () => {
  const matrix = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'parallel/r14-assurance/assurance-matrix.json'), 'utf8'));
  const r12 = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'evidence/r12-realization-matrix/qualification.json'), 'utf8'));
  const r13 = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'R13-QUALIFICATION.json'), 'utf8'));
  const cells = new Map(r12.cells.map((row: any) => [row.cell, row.result]));
  assert.equal(r13.result, 'pass');
  assert.equal(r13.denominators.scenarios, 22);
  assert.equal(matrix.backend_rows.length, 17);
  for (const row of matrix.backend_rows) for (const type of [...row.source_types, ...row.target_types]) {
    for (const language of ['typescript', 'python', 'rust']) assert.equal(cells.get(`${type}/${language}`), 'pass', `${row.id}:${type}/${language}`);
  }
});

test('R14 qualification closes every declared assurance denominator without authority promotion', () => {
  const matrix = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'parallel/r14-assurance/assurance-matrix.json'), 'utf8'));
  const qualification = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'R14-QUALIFICATION.json'), 'utf8'));
  const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8')).profiles.find((row: any) => row.id === 'complete-backend-criteria');
  const relationshipIds = matrix.backend_rows.map((row: any) => row.id);
  const obligationCount = matrix.backend_rows.reduce((sum: number, row: any) => sum + row.obligations.length, 0);
  const crossCuttingIds = matrix.cross_cutting_obligations.map((row: any) => row.id);
  const mutantIds = matrix.compiling_mutant_specifications.map((row: any) => row.id);

  assert.equal(qualification.result, 'pass');
  assert.equal(qualification.authority_effect, 'none');
  assert.equal(qualification.publication, false);
  assert.equal(qualification.admission, false);
  assert.equal('open_questions' in qualification, false);
  assert.deepEqual(qualification.relationships.map((row: any) => row.id), relationshipIds);
  assert.deepEqual(relationshipIds, profile.relationship_ids);
  assert.equal(qualification.denominators.relationships, 17);
  assert.equal(qualification.denominators.obligations, obligationCount);
  assert.equal(qualification.denominators.positive_witnesses_passed, obligationCount);
  assert.equal(qualification.denominators.semantic_mutants_killed, obligationCount);
  assert.deepEqual(qualification.cross_cutting.map((row: any) => row.id), crossCuttingIds);
  assert.equal(qualification.cross_cutting.every((row: any) => row.result === 'pass' && row.evidence.length > 0), true);
  assert.deepEqual(qualification.compiling_mutants.map((row: any) => row.id), mutantIds);
  assert.equal(qualification.compiling_mutants.every((row: any) => row.result === 'pass' && row.evidence_class && row.evidence.length > 0), true);
  assert.deepEqual(qualification.native_join.languages, ['typescript', 'python', 'rust']);
  assert.equal(qualification.native_join.r12.cells_passed, 39);
  assert.equal(qualification.native_join.r13.scenarios_passed, 22);
  assert.equal(qualification.selected_campaign.tests_passed, 57);
  assert.equal(qualification.selected_campaign.tests_failed, 0);
});
