import fs from 'node:fs';
import path from 'node:path';
import {publicFixture, publicSelection} from './composition-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorPolicyControls} from '../../src/verification/reconciled-cross-generator-policy.ts';
const project = path.resolve(import.meta.dirname, '../../../..'), base = path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation');
const definition = fs.readFileSync(path.join(base, 'cross-generator-policy-contract.json'), 'utf8');
const boundaryDefinition = fs.readFileSync(path.join(base, 'cross-generator-verification-contract.json'), 'utf8');
const scalar = (name: string): any => ({kind: 'scalar', name});
const at = (root: string, properties: string[] = []): any => ({op: 'path', root, properties});
const lit = (type: string, value: unknown): any => ({op: 'literal', type, value});
const arg = (parameter: string, value: any) => ({parameter, value});
export function policyFixture(t: any, module_root = 'domain') {
  const f = publicFixture(t), manifest = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/feature.json'), 'utf8'));
  const node = (id: string, kind: string, body: any) => {manifest.nodes.push(id); f.write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind, body: {description: id, ...body}});};
  const rule = (id: string, parameters: any[], expression: any) => node(id, 'Rule', {predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'INTEROP-' + id.toUpperCase(), parameters, expression}});
  rule('high', [{name: 'amount', type: scalar('UInt64')}], {op: 'lt', left: lit('UInt64', '100'), right: at('amount')});
  rule('forward', [{name: 'amount', type: scalar('UInt64')}], {op: 'rule_ref', selector: 'alpha:high', arguments: [arg('amount', at('amount'))]});
  rule('enabled', [{name: 'value', type: scalar('Bool')}], {op: 'eq', left: at('value'), right: lit('Bool', true)});
  rule('contains', [{name: 'words', type: {kind: 'set', element: scalar('String')}}], {op: 'contains', left: at('words'), right: lit('String', 'approved')});
  const call = (id: string, args: any[]) => ({target: 'alpha:compute', rule: {selector: 'alpha:' + id, arguments: args}});
  const inputs = [{name: 'total', type: scalar('UInt64')}, {name: 'other', type: scalar('UInt64')}, {name: 'active', type: scalar('Bool')}];
  const first = call('forward', [arg('amount', at('total'))]), second = call('enabled', [arg('value', at('active'))]);
  const policies: Record<string, any> = {
    choose: {inputs, cases: [first, second]},
    repeated: {inputs, cases: [first, first, second]},
    constant: {inputs: [inputs[0]], cases: [call('high', [arg('amount', lit('UInt64', '101'))])]},
    structured: {inputs: [{name: 'value', type: {kind: 'named', selector: 'alpha:values'}}], cases: [call('high', [arg('amount', at('value', ['TEST-VALUES#left']))])]},
    collection: {inputs: [{name: 'words', type: {kind: 'list', element: scalar('String')}}], cases: [call('contains', [arg('words', {op: 'to_set', value: at('words')})])]},
  };
  for (const [id, body] of Object.entries(policies)) {
    node(id, 'Policy', {typed_contract: {schema_version: 'domainspec.typed-policy/v2', ontology_policy: 'INTEROP-' + id.toUpperCase(), ...body, default_target: 'alpha:perform'}});
    for (const target of ['compute', 'perform']) {
      const edge_id = id + '-applies-' + target; manifest.edges.push(edge_id);
      f.write('specs/alpha/edges/' + edge_id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'alpha', edge_id, relationship: 'applies', source_node_id: id, target_node_id: target, scope: 'feature'});
    }
  }
  f.write('specs/alpha/feature.json', manifest);
  const graph = loadCompiledProjectGraph(f.source), selection = publicSelection(module_root), plan = planCompiledReconciledProject(graph, selection);
  const boundary = createCrossGeneratorBoundary(graph, plan, boundaryDefinition);
  return {...f, graph, selection, plan, boundary, controls: createCrossGeneratorPolicyControls(graph, plan, boundary, definition)};
}
