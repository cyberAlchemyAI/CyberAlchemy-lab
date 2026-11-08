import fs from 'node:fs';
import path from 'node:path';
import {pythonInterfaceFixture, scalar, local, wrap, publicField} from './reconciled-python-interface-fixture.ts';

/** Complete source-only projects with actual application/Interface relationships. */
export function pythonPublicMappingFixture(t: any, variant = 'scalar') {
  const domain = variant === 'domain';
  const type = variant === 'collections' ? wrap('list', local('detail')) : domain ? {kind: 'named', selector: 'alpha:choice'} : scalar('UInt64');
  const f = pythonInterfaceFixture(t, 'backward', type, domain);
  const file = (p: string) => path.join(f.source, p);
  const write = (p: string, value: unknown) => {fs.mkdirSync(path.dirname(file(p)), {recursive: true}); fs.writeFileSync(file(p), JSON.stringify(value) + '\n');};
  const feature = JSON.parse(fs.readFileSync(file('specs/alpha/feature.json'), 'utf8'));
  const ref = (contract_id: string, selector = 'alpha:api'): any => ({kind: 'contract', interface_selector: selector, contract_id});
  const at = (root: string, ...properties: string[]): any => ({op: 'path', root, properties});
  const bind = (target: string, value: any, fallback: any = null) => ({target, value, default: fallback});
  const use = {interface_selector: 'alpha:api', operation_id: 'perform', side: 'result'};
  const input = (name: string, type: any, use: any = null) => ({name, type, use});
  const summary = {contract_id: 'summary', ontology_contract: 'TEST-SUMMARY', fields: [publicField('value', type), publicField('memo', scalar()), publicField('explicit_total', scalar('UInt64'))]};
  if (variant === 'collections') summary.fields.push(publicField('amounts', wrap('list', scalar('UInt64'))), publicField('unique_amounts', wrap('set', scalar('UInt64'))), publicField('dedup', wrap('set', local('detail'))));
  f.contract.contracts.push(summary);
  f.save();
  const contracts: Record<string, any> = {};
  const full: any = {schema_version: 'domainspec.typed-mapping/v3', ontology_mapping: 'TEST-MAPPING-FULL', inputs: [input('response', ref('response'), use), input('memo', wrap('optional', scalar())), input('fallback', scalar()), input('order_total', scalar('UInt64'))], target: ref('summary'), target_use: null, total: true,
    fields: [bind('value', at('response', 'TEST-PUBLIC#value')), bind('memo', at('memo'), at('fallback')), bind('explicit_total', at('order_total'))]};
  if (variant === 'collections') full.fields.push(bind('amounts', at('response', 'TEST-PUBLIC#value', 'TEST-PUBLIC#amount')), bind('unique_amounts', {op: 'to_set', value: at('response', 'TEST-PUBLIC#value', 'TEST-PUBLIC#amount')}), bind('dedup', {op: 'to_set', value: at('response', 'TEST-PUBLIC#value')}));
  contracts.full = full;
  contracts.partial = {...full, ontology_mapping: 'TEST-MAPPING-PARTIAL', total: false, fields: [bind('memo', at('memo'), at('fallback'))]};
  contracts.empty = {...full, ontology_mapping: 'TEST-MAPPING-EMPTY', inputs: [], target: ref('empty'), fields: []};
  if (domain) {
    feature.nodes.push('record');
    write('specs/alpha/nodes/record.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: 'record', kind: 'Entity', body: {description: 'Record identity', fields: ['id', 'amount'], typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'TEST-RECORD', properties: ['id', 'amount'].map(name => ({name, type: scalar(name === 'id' ? 'String' : 'UInt64'), cardinality: 'one', identity: name === 'id', meaning: name, ontology_property: 'TEST-RECORD#' + name}))}}});
    f.selection.factories.push({selector: 'alpha:record', base_validators: [{rule: 'alpha:allowed', arguments: [{parameter: 'value', field: 'amount'}]}], extensions: []});
    contracts.domain = {...full, ontology_mapping: 'TEST-MAPPING-DOMAIN', inputs: [input('amount', scalar('UInt64'))], target: {kind: 'named', selector: 'alpha:record'}, total: false, fields: [bind('amount', at('amount'))]};
  }
  const save = () => {
    for (const [name, contract] of Object.entries(contracts)) {
      const id = 'map-' + name, target = contract.target.kind === 'named' ? contract.target.selector.split(':')[1] : 'api', edge_id = id + '-maps-' + target;
      if (!feature.nodes.includes(id)) feature.nodes.push(id);
      if (!feature.edges.includes(edge_id)) feature.edges.push(edge_id);
      write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind: 'Mapping', body: {description: id, target: 'alpha:' + target, typed_contract: contract}});
      write('specs/alpha/edges/' + edge_id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'alpha', edge_id, relationship: 'maps', source_node_id: id, target_node_id: target, scope: 'feature'});
    }
    write('specs/alpha/feature.json', feature);
  };
  save();
  return {...f, contracts, save};
}
