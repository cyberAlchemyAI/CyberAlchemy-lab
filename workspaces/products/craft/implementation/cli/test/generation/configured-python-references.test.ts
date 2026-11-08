import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {compileSelectedProjectFields, EXACT_FIELD_CONTRACT_SHA256, EXACT_PROJECT_FIELD_SELECTION_VERSION} from '../../src/input/compiled-field-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {planConfiguredPythonFactories, PYTHON_FACTORY_VERSION, PYTHON_REFERENCE_FACTORY_VERSION} from '../../src/generation/configured-python-factories.ts';
import {planConfiguredPythonAlgebraicEnums, PYTHON_ALGEBRAIC_ENUM_VERSION} from '../../src/generation/configured-python-algebraic-enums.ts';

const project = path.resolve(import.meta.dirname, '../../../..'), wp = 'development/reconciliation-v1/profile-compiler-reconciliation/';
const read = (file: string) => fs.readFileSync(path.join(project, file), 'utf8');
const sources = {configuration: read(wp + 'configuration.json'), base: read('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'), python: read('development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json'),
  rule_contract: read(wp + 'string-order-rule-contract.json'), collection_contract: read(wp + 'rule-collection-value-contract.json'), predicate_contract: read(wp + 'rule-collection-predicate-contract.json'), numeric_contract: read(wp + 'rule-numeric-contract.json'), exact_contract: read(wp + 'rule-exact-contract.json'), literal_contract: read(wp + 'rule-exact-literal-contract.json'), structured_contract: read(wp + 'rule-structured-value-contract.json'),
  field_contract: read('development/reconciliation-v1/contracts/exact-field-and-reference-model.json'), factory_contract: read(wp + 'factory-structured-rule-contract.json'), reference_contract: read(wp + 'reference-field-factory-contract.json')};
const scalar = (name = 'String'): any => ({kind: 'scalar', name}), named = (id: string): any => ({kind: 'named', selector: 'commerce:' + id}), wrap = (kind: string, element: any): any => ({kind, element});
const property = (owner: string, name: string, type: any, identity = false) => ({name, type, identity, cardinality: type.kind === 'optional' ? 'optional' : type.kind === 'list' ? 'many' : type.kind === 'set' ? 'many-unique' : 'one', meaning: name, ontology_property: 'FIXTURE-' + owner + '#' + name});
function fixture(t: any) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-python-references-')); t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const source = path.join(temp, 'source'), nodes: string[] = [], factories: any[] = [];
  const write = (file: string, content: unknown) => {const p = path.join(source, file); fs.mkdirSync(path.dirname(p), {recursive: true}); fs.writeFileSync(p, JSON.stringify(content) + '\n');};
  const node = (id: string, kind: string, body: object) => {nodes.push(id); write(`specs/commerce/nodes/${id}.json`, {schema_version: 'domainspec.node/v1', feature_id: 'commerce', node_id: id, kind, body: {description: id, ...body}});};
  const record = (id: string, kind: string, properties: any[], validatorField = 'id') => {
    node(id, kind, {fields: properties.map(p => p.name), ...(kind === 'Value Object' ? {invariant_refs: ['commerce:valid']} : {}), typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'FIXTURE-' + id.toUpperCase(), properties}});
    factories.push({selector: 'commerce:' + id, base_validators: [{rule: 'commerce:valid', arguments: [{parameter: 'value', field: validatorField}]}], extensions: []});
  };
  record('key', 'Value Object', [property('KEY', 'namespace', scalar()), property('KEY', 'serial', scalar('UInt64'))], 'namespace');
  record('customer', 'Entity', [property('CUSTOMER', 'id', named('key'), true), property('CUSTOMER', 'label', scalar())], 'label');
  record('account', 'Entity', [property('ACCOUNT', 'id', scalar(), true), property('ACCOUNT', 'peer', wrap('optional', scalar())), property('ACCOUNT', 'self', wrap('optional', scalar())), property('ACCOUNT', 'peers', wrap('list', scalar())), property('ACCOUNT', 'members', wrap('set', scalar())), property('ACCOUNT', 'labels', wrap('list', scalar()))]);
  record('peer', 'Entity', [property('PEER', 'id', scalar(), true), property('PEER', 'account', wrap('optional', scalar()))]);
  record('contact', 'Entity', [property('CONTACT', 'id', scalar(), true), property('CONTACT', 'customer_ref', named('key')), property('CONTACT', 'customer_list', wrap('list', named('key'))), property('CONTACT', 'customer_set', wrap('set', named('key'))), property('CONTACT', 'optional_customer', wrap('optional', named('key'))), property('CONTACT', 'serial_copy', scalar('UInt64')), property('CONTACT', 'label_copy', scalar()), property('CONTACT', 'labels_copy', wrap('list', scalar())), property('CONTACT', 'flag', named('none')), property('CONTACT', 'token', named('token'))]);
  const enums = ['none', 'true', 'false', 'concept-none', 'concept-true', 'concept-false'];
  for (const id of enums) node(id, 'Enum', {values: ['Yes'], typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'FIXTURE-' + id.toUpperCase(), variants: [{name: 'Yes', ontology_variant: 'FIXTURE-' + id.toUpperCase() + '#Yes', payload: null}]}});
  node('token', 'Enum', {values: ['Flag'], typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'FIXTURE-TOKEN', variants: [{name: 'Flag', ontology_variant: 'FIXTURE-TOKEN#Flag', payload: named('none')}]}});
  node('valid', 'Rule', {predicate: 'structured:domainspec.typed-rule/v1', typed_contract: {schema_version: 'domainspec.typed-rule/v1', ontology_rule: 'RULE-VALID', parameters: [{name: 'value', type: scalar()}], expression: {op: 'not', term: {op: 'eq', left: {op: 'path', root: 'value', properties: []}, right: {op: 'literal', type: 'String', value: ''}}}}});
  write('project.json', {schema_version: 'domainspec.project/v1', project_id: 'python-references', features: ['commerce'], cross_feature_edges: []});
  write('specs/commerce/feature.json', {schema_version: 'domainspec.feature/v1', feature_id: 'commerce', nodes, edges: []});
  const graph = loadCompiledProjectGraph(source);
  const bind = (owner: string, field: string, target: string, projection = ['id'], kind = 'identity-reference') => ({owner: 'commerce:' + owner, field, kind, target: 'commerce:' + target, projection});
  const bindings = [bind('account', 'peer', 'peer'), bind('account', 'self', 'account'), bind('account', 'peers', 'peer'), bind('account', 'members', 'peer'), bind('peer', 'account', 'account'),
    ...['customer_ref', 'customer_list', 'customer_set', 'optional_customer'].map(f => bind('contact', f, 'customer')),
    bind('contact', 'serial_copy', 'customer', ['id', 'serial'], 'field-projection'), bind('contact', 'label_copy', 'customer', ['label'], 'field-projection'), bind('contact', 'labels_copy', 'account', ['labels'], 'field-projection')];
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: createCompiledProjectCertificate(graph).graph_sha256, roots: ['commerce:contact', ...enums.map(e => 'commerce:' + e)], bindings: bindings as any}, sources.field_contract);
  const selection = {schema_version: PYTHON_REFERENCE_FACTORY_VERSION, language: 'python' as const, module_root: 'domain-app', field_compilation_sha256: fields.compilation_sha256, factories};
  return {temp, source, graph, fields, selection};
}

const native = String.raw`
import ast
import importlib
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
from typing import Annotated, get_args, get_origin, get_type_hints
root, prefix = Path(sys.argv[1]), sys.argv[2]
sys.path.insert(0, str(root))
def load(role, name):
    return importlib.import_module(prefix + ".features.commerce.src.domain." + role + "." + name)
def qualified(name):
    return prefix + ".features.commerce.src.domain.entities." + name
def success(result):
    assert result.ok is True, result
    return result.value
# Either side of a circular identity binding can load first without its target.
if prefix.startswith("relocated"):
    peer = load("entities", "peer")
    assert qualified("account") not in sys.modules, "RUNTIME_TARGET_IMPORT"
    success(peer.create_peer_factory().create({"id": "peer-1", "account": "missing-account"}))
else:
    account = load("entities", "account")
    assert qualified("peer") not in sys.modules, "RUNTIME_TARGET_IMPORT"
account = load("entities", "account")
factory = account.create_account_factory()
a = success(factory.create(dict(id="a", peer="missing-peer", self="missing-self", peers=["x", "x"], members=["z", "y"], labels=["hello", "hello"])))
b = success(factory.reconstruct(dict(id="a", peers=[], members=[], labels=[])))
assert a == b and hash(a) == hash(b)
assert a.fields.peer == "missing-peer" and a.fields.peers == ("x", "x") and a.fields.members == ("y", "z")
assert b.fields.peer is None
failure = factory.create(dict(id="", peers=[], members=[], labels=[]))
assert failure.ok is False and failure.failure_codes == ("RULE_FAIL:commerce:valid",)
assert factory.create(dict(id="a", peers=[], members=["x", "x"], labels=[])).failure_codes == ("INVALID_FIELDS",)
bindings = {b.field: b for b in account.AccountFieldBindings}
assert bindings["peer"].kind == "identity-reference" and bindings["peer"].target == "commerce:peer" and bindings["peer"].projection == ("id",)
assert bindings["self"].target == "commerce:account"
try:
    bindings["peer"].target = "other"
    raise AssertionError("MUTABLE_BINDING")
except FrozenInstanceError:
    pass
annotations = get_type_hints(account.AccountFields, include_extras=True)
assert get_origin(annotations["peer"]) is Annotated and get_args(annotations["peer"])[1] is bindings["peer"]
assert get_type_hints(account.AccountFields)["peers"] == tuple[str, ...]
contact = load("entities", "contact")
assert qualified("customer") not in sys.modules, "RUNTIME_TARGET_IMPORT"
key_module = load("value_objects", "key")
key = success(key_module.create_key_factory().create({"namespace": "missing-customer", "serial": "18446744073709551615"}))
names = {"none": "Concept_None", "true": "Concept_True", "false": "Concept_False", "concept_none": "ConceptNone", "concept_true": "ConceptTrue", "concept_false": "ConceptFalse"}
members = []
for name, symbol in names.items():
    module = load("enums", name)
    cls = getattr(module, symbol)
    member = getattr(module, "parse_" + name)("Yes")
    assert type(member) is cls and member.name == "Yes"
    assert getattr(module, "emit_" + name)(member) == "Yes"
    assert module.ENUM_ID == "commerce:" + name.replace("_", "-")
    members.append(member)
assert len(set(members)) == 6
flag = members[0]
token = load("enums", "token_sum").create_token({"variant": "Flag", "payload": flag})
raw = dict(id="contact-1", customer_ref=key, customer_list=[key, key], customer_set=[key], serial_copy="9", label_copy="not-a-live-label", labels_copy=["a", "a"], flag=flag, token=token)
value = success(contact.create_contact_factory().create(raw))
assert value.fields.customer_ref is key and value.fields.customer_list == (key, key) and value.fields.customer_set == (key,)
assert value.fields.optional_customer is None and value.fields.serial_copy == 9 and value.fields.label_copy == "not-a-live-label"
assert value.fields.labels_copy == ("a", "a") and value.fields.token.payload is flag
assert contact.create_contact_factory().create({**raw, "serial_copy": True}).failure_codes == ("INVALID_FIELDS",)
assert contact.create_contact_factory().create({**raw, "customer_ref": {"namespace": "missing-customer", "serial": 1}}).failure_codes == ("INVALID_FIELDS",)
assert contact.create_contact_factory().create({**raw, "customer_set": [key, key]}).failure_codes == ("INVALID_FIELDS",)
metadata = {b.field: b for b in contact.ContactFieldBindings}
assert metadata["customer_ref"].target == "commerce:customer", "TARGET_BINDING"
assert metadata["serial_copy"].kind == "field-projection" and metadata["serial_copy"].projection == ("id", "serial")
assert metadata["labels_copy"].projection == ("labels",)
types = get_type_hints(contact.ContactFields, include_extras=True)
assert get_args(types["customer_ref"])[0] is key_module.KeySnapshot
assert get_args(types["serial_copy"])[0] is int
assert get_args(types["labels_copy"])[0] == tuple[str, ...]
assert key_module.KeyFieldBindings == ()
assert qualified("customer") not in sys.modules, "TARGET_EXECUTION"
tree = ast.parse(root.joinpath(*prefix.split("."), "features/commerce/src/domain/entities/contact.py").read_text())
assert not any(isinstance(n, ast.ImportFrom) and n.module and n.module.endswith("customer") for n in tree.body)
print("PYTHON_REFERENCES_OK")
`;
function materialize(f: ReturnType<typeof fixture>, p: ReturnType<typeof planConfiguredPythonFactories>, name: string, transform = (file: string, source: string) => source) {
  const root = path.join(f.temp, name);
  for (const a of p.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, transform(a.relative_path, a.content), {flag: 'wx'});}
  const script = path.join(root, 'observe.py'); fs.writeFileSync(script, native);
  return () => execFileSync('/usr/bin/python3', ['-I', '-B', script, root, p.selection.module_root.replaceAll('-', '_').replaceAll('/', '.')], {encoding: 'utf8', stdio: 'pipe'}).trim();
}

test('R10 Python references bind exact targets after generation without widening v1 or changing value semantics', t => {
  const f = fixture(t), p = planConfiguredPythonFactories(f.graph, f.fields, f.selection, sources);
  assert.equal(p.schema_version, 'domainspec.configured-python-factories-plan/v2-candidate'); assert.equal(p.reference_bindings!.length, 12);
  assert.equal(p.authority_effect, 'none');
  for (const b of p.reference_bindings!) {assert.equal(b.target_artifact_sha256, p.artifacts.find(a => a.relative_path === b.target_path)!.sha256); assert.ok(Object.isFrozen(b.projection));}
  const {plan_sha256, ...body} = p; assert.equal(plan_sha256, sha256(canonicalJson(body)));
  const {reference_contract, ...old} = sources;
  assert.throws(() => planConfiguredPythonFactories(f.graph, f.fields, {...f.selection, schema_version: PYTHON_FACTORY_VERSION}, old), /reference bindings require/);
  assert.throws(() => planConfiguredPythonFactories(f.graph, f.fields, f.selection, old), /closed/);
  assert.throws(() => planConfiguredPythonFactories(f.graph, f.fields, f.selection, {...sources, reference_contract: reference_contract + ' '}), /drift/);
  const sumFields = compileSelectedProjectFields(f.graph, {...f.fields.selection, roots: ['commerce:token'], bindings: []}, sources.field_contract);
  for (const module_root of ['weakref', 'hashlib']) assert.throws(() => planConfiguredPythonAlgebraicEnums(f.graph, sumFields, {schema_version: PYTHON_ALGEBRAIC_ENUM_VERSION, language: 'python', module_root, field_compilation_sha256: sumFields.compilation_sha256}, {configuration: sources.configuration, base: sources.base, python: sources.python, field_contract: sources.field_contract}), /shadows Python standard library/);
  const changedFields = compileSelectedProjectFields(f.graph, {...f.fields.selection, bindings: f.fields.selection.bindings.map(b => b.owner === 'commerce:account' && b.field === 'peer' ? {...b, target: 'commerce:account'} : b)}, sources.field_contract);
  const changed = planConfiguredPythonFactories(f.graph, changedFields, {...f.selection, field_compilation_sha256: changedFields.compilation_sha256}, sources);
  assert.notEqual(changed.plan_sha256, p.plan_sha256);
  assert.equal(changed.modules.find(m => m.selector === 'commerce:account')!.component_contract_sha256, p.modules.find(m => m.selector === 'commerce:account')!.component_contract_sha256);
  fs.rmSync(f.source, {recursive: true}); assert.deepEqual(planConfiguredPythonFactories(f.graph, f.fields, f.selection, sources), p);
});

test('R10 native references retain wrappers projections and ownership without target imports; reserved Enum names compile', t => {
  const f = fixture(t);
  for (const module_root of ['domain-app', 'relocated/nested']) assert.equal(materialize(f, planConfiguredPythonFactories(f.graph, f.fields, {...f.selection, module_root}, sources), module_root.replaceAll('/', '-'))(), 'PYTHON_REFERENCES_OK');
});

test('R10 native reference observers reject compiling target-metadata and runtime-import mutants', t => {
  const f = fixture(t), p = planConfiguredPythonFactories(f.graph, f.fields, f.selection, sources);
  const mutants = [
    {name: 'target', leaf: '/entities/contact.py', from: '_FieldBinding("commerce:contact", "customer_ref", "identity-reference", "commerce:customer"', to: '_FieldBinding("commerce:contact", "customer_ref", "identity-reference", "commerce:account"', failure: /TARGET_BINDING/},
    {name: 'target-import', leaf: '/entities/account.py', from: 'from __future__ import annotations', to: 'from __future__ import annotations\nfrom . import peer', failure: /RUNTIME_TARGET_IMPORT/},
  ];
  for (const m of mutants) {
    let changes = 0;
    const observe = materialize(f, p, m.name, (file, source) => {if (file.endsWith(m.leaf) && source.includes(m.from)) {changes++; return source.replace(m.from, m.to);} return source;});
    assert.equal(changes, 1); assert.throws(observe, (e: any) => e.status === 1 && m.failure.test(e.stderr));
  }
});
