import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { checkTypedDefinitionFolBridge, TypedDefinitionFolBridgeError } from '../typed-definition-fol-bridge.mjs';

const variable = name => ({ kind: 'variable', name });
const constant = name => ({ kind: 'constant', name });
const fn = (name, ...args) => ({ kind: 'function', name, arguments: args });
const predicate = (name, ...args) => ({ kind: 'predicate', name, arguments: args });
const base = () => {
  const signature = {
    sorts: ['Context', 'String'],
    functions: [{ name: 'RequestID', parameter_sorts: ['Context'], result_sort: 'String' }],
    predicates: [
      { name: 'Base', parameter_sorts: ['Context'] },
      { name: 'Q', parameter_sorts: ['Context'] },
      { name: 'P', parameter_sorts: ['Context'] },
    ],
    constants: [{ name: 'empty', sort: 'String' }],
  };
  return {
    logical: {
      schema_version: 'domainspec-v2.typed-definition-logic-ir/v1-candidate', signature,
      definitions: [
        { definition_id: 'DEF-Q', symbol: 'QBody', parameters: [{ name: 'c', sort: 'Context' }],
          depends_on: [], body: predicate('Base', variable('c')) },
        { definition_id: 'DEF-P', symbol: 'PBody', parameters: [{ name: 'c', sort: 'Context' }],
          depends_on: [], body: { kind: 'and', left: predicate('Q', variable('c')),
            right: { kind: 'not', operand: { kind: 'equal', left: fn('RequestID', variable('c')),
              right: constant('empty') } } } },
        { definition_id: 'DEF-AXIOM', symbol: 'AxiomBody', parameters: [], depends_on: [],
          body: { kind: 'forall', variable: 'x', sort: 'Context',
            body: { kind: 'implies', left: predicate('P', variable('x')),
              right: predicate('Q', variable('x')) } } },
      ],
      roots: ['DEF-Q', 'DEF-P', 'DEF-AXIOM'], authority_effect: 'none',
    },
    lowering: {
      schema_version: 'domainspec-v2.typed-definition-fol-bridge/v1-candidate',
      clauses: [
        { kind: 'definition', clause_id: 'qualifying', root_definition_id: 'DEF-Q', predicate: 'Q' },
        { kind: 'definition', clause_id: 'ready-condition', root_definition_id: 'DEF-P', predicate: 'P' },
        { kind: 'assertion', clause_id: 'decision', root_definition_id: 'DEF-AXIOM' },
      ], authority_effect: 'none',
    },
    translation: {
      formal_signature: {
        sorts: signature.sorts.map(name => ({ name })),
        functions: signature.functions, predicates: signature.predicates, constants: signature.constants,
      },
      clauses: [
        { clause_id: 'qualifying', source: 'forall subject:Context: (Q(subject) iff Base(subject))' },
        { clause_id: 'ready-condition', source: 'forall c:Context: (P(c) iff (Q(c) and not (RequestID(c)=empty)))' },
        { clause_id: 'decision', source: 'forall context:Context: (P(context) implies Q(context))' },
      ],
    },
  };
};
const check = value => checkTypedDefinitionFolBridge(value.logical, value.lowering, value.translation);
const rejects = (value, code) => assert.throws(() => check(value), error =>
  error instanceof TypedDefinitionFolBridgeError && error.code === code, code);

test('closed candidate lowering schema accepts the binding used by the checker', () => {
  const schema = fileURLToPath(new URL('../schemas/typed-definition-fol-bridge.v1-candidate.schema.json', import.meta.url));
  const validation = spawnSync('python3', ['-c',
    'import json,sys,jsonschema; jsonschema.Draft202012Validator(json.load(open(sys.argv[1]))).validate(json.load(sys.stdin))', schema],
  { input: JSON.stringify(base().lowering), encoding: 'utf8', timeout: 10000 });
  assert.equal(validation.status, 0, validation.stderr || String(validation.error));
});

test('defined predicates are retained for later clauses and ASTs match modulo binder names', () => {
  const result = check(base());
  assert.equal(result.status, 'checked-logical-ir-to-fol-ast');
  assert.deepEqual(result.defined_predicates, ['Q', 'P']);
  assert.deepEqual(result.root_definition_ids, ['DEF-Q', 'DEF-P', 'DEF-AXIOM']);
  assert.equal(result.fol_core_comparison_checked, true);
  assert.equal(result.model_obligations_checked, false);
  assert.equal(result.source_binding_checked, false);
});

test('a syntactically valid weakened qualifier is rejected by structural comparison', () => {
  const value = base();
  value.translation.clauses[0].source = 'forall c:Context: (Q(c) iff (Base(c) or P(c)))';
  rejects(value, 'BRIDGE_AST_MISMATCH');
});

test('changed provenance-like field equality is rejected by structural comparison', () => {
  const value = base();
  value.translation.clauses[1].source = 'forall c:Context: (P(c) iff (Q(c) and RequestID(c)=empty))';
  rejects(value, 'BRIDGE_AST_MISMATCH');
});

test('missing or repeated roots, wrong sorts and duplicate predicate bindings fail closed', () => {
  const missing = base(); missing.lowering.clauses.pop(); rejects(missing, 'BRIDGE_COVERAGE');
  const repeated = base(); repeated.lowering.clauses[2].root_definition_id = 'DEF-Q';
  rejects(repeated, 'BRIDGE_DUPLICATE');
  const wrongSort = base(); wrongSort.lowering.clauses[0].predicate = 'Bad';
  wrongSort.logical.signature.predicates.push({ name: 'Bad', parameter_sorts: ['String'] });
  rejects(wrongSort, 'BRIDGE_SORT');
  const samePredicate = base(); samePredicate.lowering.clauses[1].predicate = 'Q';
  rejects(samePredicate, 'BRIDGE_DUPLICATE');
});

test('defined predicate may not be used before its own defining clause', () => {
  const value = base();
  value.lowering.clauses[0] = { kind: 'definition', clause_id: 'qualifying', root_definition_id: 'DEF-P', predicate: 'P' };
  value.lowering.clauses[1] = { kind: 'definition', clause_id: 'ready-condition', root_definition_id: 'DEF-Q', predicate: 'Q' };
  rejects(value, 'BRIDGE_FORWARD_REFERENCE');
});

test('translation signature and clause IDs must be exact', () => {
  const signature = base(); signature.translation.formal_signature.sorts.push({ name: 'Extra' });
  rejects(signature, 'BRIDGE_TRANSLATION');
  const clause = base(); clause.translation.clauses[1].clause_id = 'different';
  rejects(clause, 'BRIDGE_TRANSLATION');
});

test('inherited root names and unsupported truth literals reject with controlled diagnostics', () => {
  const inherited = base(); inherited.lowering.clauses[0].root_definition_id = '__proto__';
  rejects(inherited, 'BRIDGE_ROOT');
  const truth = base(); truth.logical.definitions[2].body = { kind: 'true' };
  rejects(truth, 'BRIDGE_CONSTRUCTOR');
});
