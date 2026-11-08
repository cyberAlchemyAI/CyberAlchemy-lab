import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {publicSelection} from '../helpers/composition-project.ts';
import {OPERATION_ACTION_BINDINGS_VERSION} from '../../src/typed-operation/action-bindings.ts';

export const scalar = (name = 'String'): any => ({kind: 'scalar', name});
export const local = (contract_id: string): any => ({kind: 'contract', contract_id});
export const wrap = (kind: string, element: any): any => ({kind, element});
export const publicField = (name: string, type: any): any => ({name, type, meaning: name, ontology_field: 'TEST-PUBLIC#' + name});

/** Source-only fixture: no TypeScript build or generated child artifacts. */
export function pythonInterfaceFixture(t: any, mode = 'backward', type: any = scalar('UInt64'), domain = false) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-python-interface-semantic-'));
  t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const source = path.join(temp, 'source'), nodes: string[] = [], edges: string[] = [];
  const write = (p: string, value: unknown) => {const file = path.join(source, p); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, JSON.stringify(value) + '\n');};
  const node = (id: string, kind: string, body: any) => {if (!nodes.includes(id)) nodes.push(id); write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind, body: {description: id, ...body}});};
  const edge = (from: string, relationship: string, to: string) => {const edge_id = from + '-' + relationship + '-' + to; edges.push(edge_id); write('specs/alpha/edges/' + edge_id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'alpha', edge_id, relationship, source_node_id: from, target_node_id: to, scope: 'feature'});};
  node('allowed', 'Rule', {predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'TEST-ALLOWED', parameters: [{name: 'value', type: scalar('UInt64')}], expression: {op: 'eq', left: {op: 'path', root: 'value', properties: []}, right: {op: 'path', root: 'value', properties: []}}}});
  node('perform', 'Operation', {reads: [], writes: [], effects: [], guard: 'allowed', failure_continuation: 'return-error'});
  edge('allowed', 'enforces', 'perform');
  const selection = publicSelection('relocated/interface-app');
  selection.factories = [];
  selection.operations = [{schema_version: OPERATION_ACTION_BINDINGS_VERSION, selector: 'alpha:perform', inputs: [{name: 'value', type: scalar('UInt64')}], reads: [], writes: [], guards: [{selector: 'alpha:allowed', arguments: [{parameter: 'value', value: {op: 'path', root: 'value', properties: []}}]}], events: [], result: {type: scalar('UInt64'), value: {op: 'path', root: 'value', properties: []}}, atomicity: 'state-and-outbox', continuation: 'awaited-settlement'}];
  if (domain) {
    node('never', 'Rule', {predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'TEST-NEVER', parameters: [{name: 'value', type: scalar('UInt64')}], expression: {op: 'eq', left: {op: 'literal', type: 'Bool', value: true}, right: {op: 'literal', type: 'Bool', value: false}}}});
    node('money', 'Value Object', {fields: ['amount'], invariant_refs: ['alpha:never'], typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'TEST-MONEY', properties: [{name: 'amount', type: scalar('UInt64'), identity: false, cardinality: 'one', meaning: 'amount', ontology_property: 'TEST-MONEY#amount'}]}});
    node('choice', 'Enum', {values: ['None', 'Some'], typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'TEST-CHOICE', variants: [{name: 'None', ontology_variant: 'TEST-CHOICE#None', payload: null}, {name: 'Some', ontology_variant: 'TEST-CHOICE#Some', payload: {kind: 'named', selector: 'alpha:money'}}]}});
    selection.factories = [{selector: 'alpha:money', base_validators: [{rule: 'alpha:never', arguments: [{parameter: 'value', field: 'amount'}]}], extensions: []}];
  }
  const contract: any = {schema_version: 'domainspec.typed-interface/v1', ontology_interface: 'TEST-API', boundary_kind: 'external', version_policy: {schema_version: 'domainspec.interface-version-policy/v1', mode, direction: 'consumer-to-provider', provider_version: mode === 'exact' ? '9'.repeat(64) + '.2.3' : '1.2.3'},
    contracts: [{contract_id: 'response', ontology_contract: 'TEST-RESPONSE', fields: [publicField('value', type)]}, {contract_id: 'shadow', ontology_contract: 'TEST-SHADOW', fields: [publicField('value', type)]}, {contract_id: 'detail', ontology_contract: 'TEST-DETAIL', fields: [publicField('amount', scalar('UInt64'))]}, {contract_id: 'empty', ontology_contract: 'TEST-EMPTY', fields: []}],
    operations: [{operation_id: 'perform', operation_ref: 'alpha:perform', request: type, result: local('response')}]};
  node('api', 'Interface', {typed_contract: contract}); edge('api', 'exposes', 'perform');
  const save = () => {node('api', 'Interface', {typed_contract: contract}); write('project.json', {schema_version: 'domainspec.project/v1', project_id: 'interface-semantics', features: ['alpha'], cross_feature_edges: []}); write('specs/alpha/feature.json', {schema_version: 'domainspec.feature/v1', feature_id: 'alpha', nodes, edges});};
  save();
  return {temp, source, selection, contract, save};
}
