import fs from 'node:fs';
import path from 'node:path';
import type {TestContext} from 'node:test';
import {workflowValuesFixture} from './workflow-values.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';

/** The full existing compound family plus Policy, State Machine and a plain Enum. */
export function crossGeneratorPublicFixture(t: TestContext) {
  const f = workflowValuesFixture(t, {events: true}), source = path.join(f.root, 'source');
  const manifestFile = path.join(source, 'specs/commerce/feature.json'), manifest = JSON.parse(fs.readFileSync(manifestFile, 'utf8'));
  const node = (id: string, kind: string, body: unknown) => {
    manifest.nodes.push(id);
    fs.writeFileSync(path.join(source, 'specs/commerce/nodes/' + id + '.json'), JSON.stringify({schema_version: 'domainspec.node/v1', feature_id: 'commerce', node_id: id, kind, body}));
  };
  const edge = (from: string, relationship: string, to: string) => {
    const id = from + '-' + relationship + '-' + to; manifest.edges.push(id);
    fs.writeFileSync(path.join(source, 'specs/commerce/edges/' + id + '.json'), JSON.stringify({schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id: id, source_node_id: from, target_node_id: to, relationship, scope: 'feature'}));
  };
  const inputs = [{name: 'amount', type: {kind: 'scalar', name: 'UInt64'}}];
  const guard = {selector: 'commerce:positive', arguments: [{parameter: 'value', value: {op: 'path', root: 'amount', properties: []}}]};
  node('dispatch', 'Policy', {description: 'Select a declared Operation without executing it.', typed_contract: {
    schema_version: 'domainspec.typed-policy/v2', ontology_policy: 'TEST-DISPATCH', inputs,
    cases: [{target: 'commerce:perform', rule: guard}], default_target: 'commerce:undo'
  }});
  edge('dispatch', 'applies', 'perform'); edge('dispatch', 'applies', 'undo');
  node('lifecycle', 'State Machine', {description: 'Declared event state transitions.', typed_contract: {
    schema_version: 'domainspec.typed-state-machine/v1', ontology_state_machine: 'TEST-LIFECYCLE', inputs,
    states: ['draft', 'posted', 'released'], initial: 'draft', transitions: [
      {transition_id: 'post', source_state: 'draft', target_state: 'posted', trigger_event_ref: 'commerce:posted', guard, output_intents: []},
      {transition_id: 'release', source_state: 'posted', target_state: 'released', trigger_event_ref: 'commerce:released', guard: null, output_intents: []}
    ]
  }});
  edge('posted', 'transitions', 'lifecycle'); edge('released', 'transitions', 'lifecycle');
  node('priority', 'Enum', {description: 'Plain Enum producer.', values: ['Normal', 'Urgent'], typed_contract: {
    schema_version: 'domainspec.typed-sum/v1', ontology_node: 'TEST-PRIORITY', variants: ['Normal', 'Urgent'].map(name => ({name, payload: null, ontology_variant: 'TEST-PRIORITY#' + name}))
  }});
  fs.writeFileSync(manifestFile, JSON.stringify(manifest));
  const graph = loadCompiledProjectGraph(source);
  return {...f, source, graph};
}
