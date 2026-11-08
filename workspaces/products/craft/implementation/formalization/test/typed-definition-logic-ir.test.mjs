import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { checkTypedDefinitionLogicIR, TypedDefinitionError } from '../typed-definition-logic-ir.mjs';

const variable = name => ({ kind: 'variable', name });
const fn = (name, ...args) => ({ kind: 'function', name, arguments: args });
const predicate = (name, ...args) => ({ kind: 'predicate', name, arguments: args });
const ref = (symbol, ...args) => ({ kind: 'ref', symbol, arguments: args });
const base = () => ({
  schema_version: 'domainspec-v2.typed-definition-logic-ir/v1-candidate',
  signature: {
    sorts: ['Context', 'String'],
    functions: [{ name: 'RequestID', parameter_sorts: ['Context'], result_sort: 'String' }],
    predicates: [{ name: 'Trusted', parameter_sorts: ['Context'] }],
    constants: [{ name: 'empty', sort: 'String' }],
  },
  definitions: [
    { definition_id: 'DEF-Q', symbol: 'Q', parameters: [{ name: 'c', sort: 'Context' }], depends_on: [],
      body: { kind: 'and', left: predicate('Trusted', variable('c')),
        right: { kind: 'not', operand: { kind: 'equal', left: fn('RequestID', variable('c')),
          right: { kind: 'constant', name: 'empty' } } } } },
    { definition_id: 'DEF-P', symbol: 'P', parameters: [{ name: 'c', sort: 'Context' }], depends_on: ['DEF-Q'],
      body: ref('Q', variable('c')) },
  ],
  roots: ['DEF-P'], authority_effect: 'none',
});
const check = value => checkTypedDefinitionLogicIR(value);
const rejects = (value, code) => assert.throws(() => check(value), error =>
  error instanceof TypedDefinitionError && error.code === code, code);

test('schema and checker accept one typed, closed logical-definition graph', () => {
  const value = base();
  const schema = fileURLToPath(new URL('../schemas/typed-definition-logic-ir.v1-candidate.schema.json', import.meta.url));
  const validation = spawnSync('python3', ['-c',
    'import json,sys,jsonschema; jsonschema.Draft202012Validator(json.load(open(sys.argv[1]))).validate(json.load(sys.stdin))', schema],
    { input: JSON.stringify(value), encoding: 'utf8', timeout: 10000 });
  assert.equal(validation.status, 0, validation.stderr || String(validation.error));
  const result = check(value);
  assert.equal(result.status, 'checked-logical-ir-only');
  assert.equal(result.model_obligations_checked, false);
  assert.deepEqual(result.expanded_roots['DEF-P'].body, value.definitions[0].body);
  assert.equal(JSON.stringify(result.expanded_roots).includes('"kind":"ref"'), false);
});

test('real Auth-style hyphenated definition identities are supported', () => {
  const value = base();
  value.definitions[0].definition_id = 'AUTH-CB-DEF-QUALIFYING-AUTH-V2';
  value.definitions[1].depends_on = ['AUTH-CB-DEF-QUALIFYING-AUTH-V2'];
  assert.equal(check(value).definition_count, 2);
});

test('unknown constructor and trailing unknown field fail closed', () => {
  const unknown = base(); unknown.definitions[0].body.kind = 'invented';
  rejects(unknown, 'IR_CONSTRUCTOR');
  const extra = base(); extra.definitions[0].body.extra = 'ignored?';
  rejects(extra, 'IR_SHAPE');
});

test('sort, arity and unbound variable errors reject before expansion', () => {
  const sort = base(); sort.definitions[0].body.left.arguments[0] = { kind: 'constant', name: 'empty' };
  rejects(sort, 'IR_SORT');
  const arity = base(); arity.definitions[0].body.left.arguments = [];
  rejects(arity, 'IR_ARITY');
  const unbound = base(); unbound.definitions[0].body.left.arguments[0] = variable('other');
  rejects(unbound, 'IR_UNBOUND');
});

test('declared dependency mismatch, cycle and orphan definitions reject', () => {
  const partial = base(); partial.definitions[1].depends_on = [];
  rejects(partial, 'IR_DEPENDENCY');
  const cycle = base(); cycle.definitions[0].body = ref('P', variable('c'));
  cycle.definitions[0].depends_on = ['DEF-P'];
  rejects(cycle, 'IR_CYCLE');
  const orphan = base(); orphan.roots = ['DEF-Q'];
  rejects(orphan, 'IR_ORPHAN');
});

test('a structural or-true mutation remains visible in expanded AST', () => {
  const original = check(base()).expanded_roots['DEF-P'].body;
  const mutant = base();
  mutant.definitions[0].body = { kind: 'or', left: mutant.definitions[0].body, right: { kind: 'true' } };
  const expanded = check(mutant).expanded_roots['DEF-P'].body;
  assert.notDeepEqual(expanded, original);
  assert.equal(expanded.kind, 'or');
  assert.equal(expanded.right.kind, 'true');
});

test('macro expansion renames nested binders without capturing the caller witness', () => {
  const value = {
    schema_version: 'domainspec-v2.typed-definition-logic-ir/v1-candidate',
    signature: { sorts: ['Context'], functions: [], constants: [],
      predicates: [{ name: 'R', parameter_sorts: ['Context', 'Context'] }] },
    definitions: [
      { definition_id: 'DEF-D', symbol: 'D', parameters: [{ name: 'p', sort: 'Context' }], depends_on: [],
        body: { kind: 'exists', variable: 'x', sort: 'Context', body: predicate('R', variable('p'), variable('x')) } },
      { definition_id: 'DEF-P', symbol: 'P', parameters: [], depends_on: ['DEF-D'],
        body: { kind: 'forall', variable: 'x', sort: 'Context', body: ref('D', variable('x')) } },
    ], roots: ['DEF-P'], authority_effect: 'none',
  };
  const expanded = check(value).expanded_roots['DEF-P'].body;
  assert.equal(expanded.kind, 'forall');
  assert.equal(expanded.body.kind, 'exists');
  assert.notEqual(expanded.variable, expanded.body.variable);
  assert.equal(expanded.body.body.arguments[0].name, expanded.variable);
  assert.equal(expanded.body.body.arguments[1].name, expanded.body.variable);
});

test('exponential DAG expansion is rejected before materializing an unbounded AST', () => {
  const definitions = [{ definition_id: 'DEF-0', symbol: 'D0', parameters: [{ name: 'c', sort: 'Context' }],
    depends_on: [], body: predicate('R', variable('c')) }];
  for (let index = 1; index <= 14; index++) definitions.push({
    definition_id: `DEF-${index}`, symbol: `D${index}`,
    parameters: [{ name: 'c', sort: 'Context' }], depends_on: [`DEF-${index - 1}`],
    body: { kind: 'and', left: ref(`D${index - 1}`, variable('c')),
      right: ref(`D${index - 1}`, variable('c')) },
  });
  rejects({ schema_version: 'domainspec-v2.typed-definition-logic-ir/v1-candidate',
    signature: { sorts: ['Context'], functions: [], constants: [],
      predicates: [{ name: 'R', parameter_sorts: ['Context'] }] },
    definitions, roots: ['DEF-14'], authority_effect: 'none' }, 'IR_EXPANSION_LIMIT');
});

test('macro argument substitution counts exponentially cloned term nodes', () => {
  const definitions = [{ definition_id: 'DEF-0', symbol: 'D0', parameters: [{ name: 'p', sort: 'S' }],
    depends_on: [], body: predicate('R', variable('p')) }];
  for (let index = 1; index <= 15; index++) definitions.push({
    definition_id: `DEF-${index}`, symbol: `D${index}`,
    parameters: [{ name: 'p', sort: 'S' }], depends_on: [`DEF-${index - 1}`],
    body: ref(`D${index - 1}`, fn('F', variable('p'), variable('p'))),
  });
  rejects({ schema_version: 'domainspec-v2.typed-definition-logic-ir/v1-candidate',
    signature: { sorts: ['S'], functions: [{ name: 'F', parameter_sorts: ['S', 'S'], result_sort: 'S' }],
      constants: [], predicates: [{ name: 'R', parameter_sorts: ['S'] }] },
    definitions, roots: ['DEF-15'], authority_effect: 'none' }, 'IR_EXPANSION_LIMIT');
});

test('fol-core reserved names cannot become signature or definition symbols', () => {
  const value = base(); value.definitions[0].symbol = 'forall';
  rejects(value, 'IR_IDENTIFIER');
});
