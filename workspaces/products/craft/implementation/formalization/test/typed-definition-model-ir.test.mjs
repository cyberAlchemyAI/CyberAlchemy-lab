import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { checkTypedDefinitionModelIR, TypedDefinitionModelError } from '../typed-definition-model-ir.mjs';

const variable = name => ({ kind: 'variable', name });
const predicate = (name, ...args) => ({ kind: 'predicate', name, arguments: args });
const logical = () => ({
  schema_version: 'domainspec-v2.typed-definition-logic-ir/v1-candidate',
  signature: { sorts: ['Context', 'AuthOccurrence', 'RouteOccurrence'], functions: [], constants: [],
    predicates: [
      { name: 'AuthMember', parameter_sorts: ['Context', 'AuthOccurrence'] },
      { name: 'RouteMember', parameter_sorts: ['Context', 'RouteOccurrence'] },
    ] },
  definitions: [
    { definition_id: 'DEF-QA', symbol: 'QA',
      parameters: [{ name: 'c', sort: 'Context' }, { name: 'a', sort: 'AuthOccurrence' }],
      depends_on: [], body: { kind: 'and',
        left: predicate('AuthMember', variable('c'), variable('a')), right: { kind: 'true' } } },
    { definition_id: 'DEF-QR', symbol: 'QR',
      parameters: [{ name: 'c', sort: 'Context' }, { name: 'r', sort: 'RouteOccurrence' }],
      depends_on: [], body: { kind: 'and',
        left: predicate('RouteMember', variable('c'), variable('r')), right: { kind: 'true' } } },
  ],
  roots: ['DEF-QA', 'DEF-QR'], authority_effect: 'none',
});
const model = () => ({
  schema_version: 'domainspec-v2.typed-definition-model-ir/v1-candidate',
  context: { sort: 'Context', carrier: 'full-typed-record-with-finite-lists', fields: [
    { name: 'request', kind: 'record', type: 'Request' },
    { name: 'candidate', kind: 'record', type: 'Candidate' },
    { name: 'authRows', kind: 'list', type: 'Evidence' },
    { name: 'routeRows', kind: 'list', type: 'RouteBinding' },
  ] },
  scope: { kind: 'entire-context-carrier', normal_completion: 'separate-correspondence-obligation' },
  occurrences: [
    { sort: 'AuthOccurrence', list_field: 'authRows', row_type: 'Evidence',
      qualifier_definition_id: 'DEF-QA',
      carrier: 'context-row-position-product', identity: 'context-and-zero-based-position',
      membership: { kind: 'tagged-zip-index', predicate: 'AuthMember', start: 0,
        nonmembers: 'ghost-and-foreign-excluded' }, projection: 'total-tuple-row' },
    { sort: 'RouteOccurrence', list_field: 'routeRows', row_type: 'RouteBinding',
      qualifier_definition_id: 'DEF-QR',
      carrier: 'context-row-position-product', identity: 'context-and-zero-based-position',
      membership: { kind: 'tagged-zip-index', predicate: 'RouteMember', start: 0,
        nonmembers: 'ghost-and-foreign-excluded' }, projection: 'total-tuple-row' },
  ], authority_effect: 'none',
});
const check = (value, theory = logical()) => checkTypedDefinitionModelIR(value, theory);
const rejects = (value, code, theory = logical()) => assert.throws(() => check(value, theory), error =>
  error instanceof TypedDefinitionModelError && error.code === code, code);

test('closed schema and checker emit only unproved occurrence obligations', () => {
  const value = model();
  const schema = fileURLToPath(new URL('../schemas/typed-definition-model-ir.v1-candidate.schema.json', import.meta.url));
  const validation = spawnSync('python3', ['-c',
    'import json,sys,jsonschema; jsonschema.Draft202012Validator(json.load(open(sys.argv[1]))).validate(json.load(sys.stdin))', schema],
  { input: JSON.stringify(value), encoding: 'utf8', timeout: 10000 });
  assert.equal(validation.status, 0, validation.stderr || String(validation.error));
  const result = check(value);
  assert.equal(result.status, 'checked-model-ir-shape-only');
  assert.equal(result.occurrence_count, 2);
  assert.equal(result.obligations.length, 9);
  assert.ok(result.obligations.every(row => row.status === 'unproved'));
  assert.equal(result.logical_qualifier_membership_binding_checked, true);
  for (const key of ['typed_context_carrier_correspondence_proved',
    'logical_qualifier_full_definition_checked', 'lean_obligations_proved',
    'normal_completion_checked', 'model_obligations_checked']) assert.equal(result[key], false);
});

test('scope is entire carrier and normal completion cannot filter it', () => {
  const filtered = model(); filtered.scope.kind = 'only-ready-contexts';
  rejects(filtered, 'MODEL_CONSTRUCTOR');
  const outcome = model(); outcome.scope.outcome_predicate = 'Decision';
  rejects(outcome, 'MODEL_SHAPE');
  const completion = model(); completion.scope.normal_completion = 'only-successful-executions';
  rejects(completion, 'MODEL_CONSTRUCTOR');
});

test('declared occurrence-bearing lists must be covered exactly once', () => {
  const missing = model(); missing.occurrences.pop();
  rejects(missing, 'MODEL_COVERAGE');
  const extra = model(); extra.occurrences[1].list_field = 'candidate';
  rejects(extra, 'MODEL_COVERAGE');
  const mismatch = model(); mismatch.occurrences[1].row_type = 'Evidence';
  rejects(mismatch, 'MODEL_COVERAGE');
  const duplicate = model(); duplicate.occurrences[1] = structuredClone(duplicate.occurrences[0]);
  rejects(duplicate, 'MODEL_DUPLICATE');
});

test('value identity, filtered membership, nonzero index and partial projection reject', () => {
  const valueIdentity = model(); valueIdentity.occurrences[0].identity = 'row-value';
  rejects(valueIdentity, 'MODEL_CONSTRUCTOR');
  const filtered = model(); filtered.occurrences[0].membership.kind = 'filtered-row-set';
  rejects(filtered, 'MODEL_CONSTRUCTOR');
  const oneBased = model(); oneBased.occurrences[0].membership.start = 1;
  rejects(oneBased, 'MODEL_CONSTRUCTOR');
  const partial = model(); partial.occurrences[0].projection = 'partial-member-only-row';
  rejects(partial, 'MODEL_CONSTRUCTOR');
  const ghosts = model(); ghosts.occurrences[0].membership.nonmembers = 'may-qualify';
  rejects(ghosts, 'MODEL_CONSTRUCTOR');
});

test('member predicates use independently checked logical sorts and arity', () => {
  const wrong = model(); wrong.occurrences[0].membership.predicate = 'RouteMember';
  rejects(wrong, 'MODEL_SIGNATURE');
  const wrongSort = model(); wrongSort.occurrences[0].sort = 'Context';
  rejects(wrongSort, 'MODEL_SORT');
  const wrongSignature = logical();
  wrongSignature.signature.predicates[0].parameter_sorts = ['AuthOccurrence', 'Context'];
  assert.throws(() => check(model(), wrongSignature), /IR_SORT/,
    'an ill-typed upstream logical definition must fail before model checking');
});

test('qualifier must directly conjoin matching membership on the same parameters', () => {
  const wrongRoot = model(); wrongRoot.occurrences[0].qualifier_definition_id = 'DEF-QR';
  rejects(wrongRoot, 'MODEL_QUALIFIER');
  const notRoot = logical(); notRoot.roots = ['DEF-QR']; notRoot.definitions.shift();
  rejects(model(), 'MODEL_QUALIFIER', notRoot);
  const noMember = logical(); noMember.definitions[0].body = { kind: 'true' };
  rejects(model(), 'MODEL_QUALIFIER', noMember);
  const orMember = logical(); orMember.definitions[0].body = { kind: 'or',
    left: predicate('AuthMember', variable('c'), variable('a')), right: { kind: 'true' } };
  rejects(model(), 'MODEL_QUALIFIER', orMember);
  const wrongWitness = logical(); wrongWitness.definitions[0].body.left.arguments =
    [variable('c'), variable('c')];
  assert.throws(() => check(model(), wrongWitness), /IR_SORT/);
  const boundMember = logical(); boundMember.definitions[0].body = { kind: 'forall',
    variable: 'a2', sort: 'AuthOccurrence',
    body: predicate('AuthMember', variable('c'), variable('a2')) };
  rejects(model(), 'MODEL_QUALIFIER', boundMember);
});

test('self-declared Context cannot smuggle an alternate carrier or unknown field', () => {
  const subset = model(); subset.context.carrier = 'contexts-that-completed';
  rejects(subset, 'MODEL_CONSTRUCTOR');
  const extra = model(); extra.context.fields[0].source_expression = 'unknown';
  rejects(extra, 'MODEL_SHAPE');
  const duplicate = model(); duplicate.context.fields[1].name = 'request';
  rejects(duplicate, 'MODEL_DUPLICATE');
});
