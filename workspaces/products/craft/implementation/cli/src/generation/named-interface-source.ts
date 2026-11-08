import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {decodeNamedInterface, checkInterfacePublicClosure, NAMED_INTERFACE_DEFINITION_SHA256, type InterfacePublicType} from '../typed-backend/interface.js';
import {createStructuredValueRenderer} from './configured-value-types.js';
import {renderInterfaceVersionPolicy} from './interface-version-policy-source.js';

const q = JSON.stringify;
const fail = (message: string): never => {throw new Error('DS_NAMED_INTERFACE: ' + message);};
function frozenLiteral(value: unknown): string {
  if (Array.isArray(value)) return 'Object.freeze([' + value.map(frozenLiteral).join(',') + '])';
  if (value && typeof value === 'object') return 'Object.freeze({' + Object.entries(value).map(([k, v]) => '[' + q(k) + ']:' + frozenLiteral(v)).join(',') + '})';
  return q(value);
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);}
  return value;
}

/** Source-bound standalone contract generation; no publication, member execution or transport. */
export function renderNamedInterfaceSource(graph: CompiledProjectGraph, selector: string, fields: CompiledProjectFields | null = null) {
  assertCompiledProjectSnapshot(graph);
  const certificate = createCompiledProjectCertificate(graph);
  if (fields !== null) {
    assertCompiledProjectFields(fields);
    if (fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION) fail('exact field profile required');
    if (fields.certificate.graph_sha256 !== certificate.graph_sha256) fail('cross-graph value types');
  }
  const node = graph.nodes.find(n => n.selector === selector);
  if (!node || node.kind !== 'Interface' || node.body.typed_contract === undefined) return fail('typed Interface required');
  const contract = decodeNamedInterface(node.body.typed_contract);
  checkInterfacePublicClosure(contract, fields?.model.declarations ?? []);
  // Interfaces expose normalized types and shape protocols, not unused raw-input aliases.
  const values = createStructuredValueRenderer(fields?.model ?? null, fail, true);
  const contracts = [...contract.contracts].sort((a, b) => a.contract_id < b.contract_id ? -1 : 1);
  const operations = [...contract.operations].sort((a, b) => a.operation_id < b.operation_id ? -1 : 1);
  const rows: string[] = [], cache = new Map<string, {native: string; protocol: string}>();
  let sequence = 0;
  const ensure = (t: InterfacePublicType): {native: string; protocol: string} => {
    if (t.kind === 'scalar' || t.kind === 'named') return values.ensure(t);
    const key = canonicalJson(t), prior = cache.get(key); if (prior) return prior;
    const native = 'I' + sequence++, protocol = native + 'Value', result = {native, protocol};
    if (t.kind === 'contract') {
      const c = contracts.find(c => c.contract_id === t.contract_id) ?? fail('missing public contract');
      const fields = [...c.fields].sort((a, b) => a.name < b.name ? -1 : 1), children = fields.map(f => ensure(f.type));
      rows.push('type ' + native + '=Readonly<{' + fields.map((f, i) => 'readonly ' + q(f.name) + ':' + children[i]!.native).join(';') + '}>;\n' +
        'const ' + protocol + ':RuleProtocol<' + native + '>=Object.freeze({normalize:(input:unknown):' + native + '=>{\n' +
        '  const d=ruleData(input,' + q(fields.map(f => f.name)) + ');\n' +
        '  return Object.freeze({' + fields.map((f, i) => '[' + q(f.name) + ']:' + children[i]!.protocol + '.normalize(Object.hasOwn(d,' + q(f.name) + ')?d[' + q(f.name) + ']!.value:' + (f.type.kind === 'optional' ? 'null' : 'undefined') + ')').join(',') + '});\n' +
        '},key:(value:' + native + '):string=>rulePart(' + q(selector) + ')+rulePart(' + q(c.contract_id) + ')' + fields.map((f, i) => '+rulePart(' + q(f.name) + ')+rulePart(' + children[i]!.protocol + '.key(value[' + q(f.name) + ']))').join('') + '});\n');
    } else if (t.kind === 'sum') {
      values.use('sum');
      const variants = [...t.variants].sort((a, b) => a.name < b.name ? -1 : 1), children = variants.map(v => v.payload ? ensure(v.payload) : null);
      rows.push('type ' + native + '=' + variants.map((v, i) => 'Readonly<{variant:' + q(v.name) + (children[i] ? ';payload:' + children[i]!.native : '') + '}>').join('|') + ';\n' +
        'const ' + protocol + ':RuleProtocol<' + native + '>=ruleSum(Object.freeze({' + variants.map((v, i) => '[' + q(v.name) + ']:' + (children[i]?.protocol ?? 'null')).join(',') + '}));\n');
    } else {
      values.use(t.kind === 'optional' ? 'optional' : 'sequence');
      const child = ensure(t.element);
      rows.push('type ' + native + '=' + (t.kind === 'optional' ? '(' + child.native + ')|null' : 'ReadonlyArray<' + child.native + '>') + ';\n' +
        'const ' + protocol + ':RuleProtocol<' + native + '>=' + (t.kind === 'optional' ? 'ruleOptional(' + child.protocol + ')' : 'ruleSequence(' + child.protocol + ',' + (t.kind === 'set') + ')') + ';\n');
    }
    cache.set(key, result); return result;
  };
  const publicTypes = contracts.map(c => ensure({kind: 'contract', contract_id: c.contract_id}));
  const endpoints = operations.map(o => ({request: ensure(o.request), result: ensure(o.result)}));
  const relative_path = `specs/${node.feature_id}/nodes/${node.node_id}.json`;
  const source = graph.source_manifest.sources.find(s => s.relative_path === relative_path) ?? fail('missing source evidence');
  const descriptor = freeze({schema_version: 'domainspec.named-interface-descriptor/v1-candidate', selector,
    definition_sha256: NAMED_INTERFACE_DEFINITION_SHA256, graph_sha256: certificate.graph_sha256,
    source: {relative_path, sha256: source.sha256}, field_compilation_sha256: fields?.compilation_sha256 ?? null,
    contract_sha256: sha256(canonicalJson(contract)), contract,
    effect_contract: 'structural-interface-and-pure-shape-normalizers',
    invariant_execution: 'not-performed', transport_execution: 'not-performed', authority_effect: 'none'});
  const body = rows.join('') + renderInterfaceVersionPolicy(contract.version_policy) +
    'export type PublicContracts=Readonly<{' + contracts.map((c, i) => 'readonly ' + q(c.contract_id) + ':' + publicTypes[i]!.native).join(';') + '}>;\n' +
    'export type Interface=Readonly<{' + operations.map((o, i) => 'readonly ' + q(o.operation_id) + ':(request:' + endpoints[i]!.request.native + ')=>Promise<' + endpoints[i]!.result.native + '>').join(';') + '}>;\n' +
    'export const publicContracts=Object.freeze({' + contracts.map((c, i) => '[' + q(c.contract_id) + ']:' + publicTypes[i]!.protocol).join(',') + '});\n' +
    'export const endpointValues=Object.freeze({' + operations.map((o, i) => '[' + q(o.operation_id) + ']:Object.freeze({request:' + endpoints[i]!.request.protocol + ',result:' + endpoints[i]!.result.protocol + '})').join(',') + '});\n';
  // Rewrite only compiler-owned runtime diagnostics. Descriptor prose is
  // authored domain language and must remain byte-for-byte intact.
  const content = values.source(body).replaceAll('RULE_INPUT', 'INTERFACE_VALUE') +
    'export const descriptor=' + frozenLiteral(descriptor) + ';\n';
  return freeze({content, sha256: sha256(content), descriptor});
}
