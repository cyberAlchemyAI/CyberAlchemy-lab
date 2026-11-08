// Candidate bridge from checked logical definitions to an independently parsed
// fol-core translation. Run with the repository's lock-checked AlchLang tsx
// toolchain: the parser imports TypeScript modules through .js specifiers.
// fol-core has no truth literals, so a logical true/false root fails closed.
// This checks formula structure, not model interpretation, source authority,
// proof, or owner acceptance.
import { isDeepStrictEqual } from 'node:util';
import { checkTypedDefinitionLogicIR } from './typed-definition-logic-ir.mjs';
import { parseFormalProposition } from '../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/formal-claim.ts';

export class TypedDefinitionFolBridgeError extends Error {
  constructor(code, path, message) {
    super(`${code} ${path}: ${message}`);
    this.name = 'TypedDefinitionFolBridgeError';
    this.code = code;
    this.path = path;
  }
}

const fail = (code, path, message) => { throw new TypedDefinitionFolBridgeError(code, path, message); };
const exact = (value, path, keys) => {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      Object.keys(value).sort().join('|') !== [...keys].sort().join('|'))
    fail('BRIDGE_SHAPE', path, `expected exactly ${keys.join(', ')}`);
  return value;
};
const ident = value => typeof value === 'string' && /^[A-Za-z_][A-Za-z0-9_]*$/.test(value);
const clauseId = value => typeof value === 'string' && /^[a-z][a-z0-9-]*$/.test(value);
const same = (left, right) => isDeepStrictEqual(left, right);

export function checkTypedDefinitionFolBridge(logicalIR, lowering, translation) {
  const checked = checkTypedDefinitionLogicIR(logicalIR);
  const config = exact(lowering, '$/lowering', ['schema_version', 'clauses', 'authority_effect']);
  if (config.schema_version !== 'domainspec-v2.typed-definition-fol-bridge/v1-candidate' ||
      config.authority_effect !== 'none') fail('BRIDGE_VERSION', '$/lowering', 'unsupported candidate lowering');
  if (!Array.isArray(config.clauses) || config.clauses.length !== Object.keys(checked.expanded_roots).length)
    fail('BRIDGE_COVERAGE', '$/lowering/clauses', 'every logical root must emit exactly one clause');
  const predicates = new Map(logicalIR.signature.predicates.map(row => [row.name, row.parameter_sorts]));
  const emittedPredicates = new Map();
  const usedRoots = new Set(), usedClauses = new Set();
  for (const [index, raw] of config.clauses.entries()) {
    const path = `$/lowering/clauses/${index}`;
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) fail('BRIDGE_SHAPE', path, 'expected clause');
    const entry = raw.kind === 'definition'
      ? exact(raw, path, ['kind', 'clause_id', 'root_definition_id', 'predicate'])
      : exact(raw, path, ['kind', 'clause_id', 'root_definition_id']);
    if (!['definition', 'assertion'].includes(entry.kind) || !clauseId(entry.clause_id) ||
        typeof entry.root_definition_id !== 'string') fail('BRIDGE_SHAPE', path, 'unsupported clause binding');
    if (usedClauses.has(entry.clause_id) || usedRoots.has(entry.root_definition_id))
      fail('BRIDGE_DUPLICATE', path, 'duplicate clause or root');
    usedClauses.add(entry.clause_id); usedRoots.add(entry.root_definition_id);
    if (!Object.hasOwn(checked.expanded_roots, entry.root_definition_id))
      fail('BRIDGE_ROOT', path, `unresolved logical root ${entry.root_definition_id}`);
    const root = checked.expanded_roots[entry.root_definition_id];
    if (entry.kind === 'assertion' && root.parameters.length)
      fail('BRIDGE_ARITY', path, 'assertion root must be closed');
    if (entry.kind === 'definition') {
      if (!ident(entry.predicate) || !predicates.has(entry.predicate))
        fail('BRIDGE_PREDICATE', path, 'defined predicate must be in the checked signature');
      if (emittedPredicates.has(entry.predicate)) fail('BRIDGE_DUPLICATE', path, 'predicate defined twice');
      if (!same(predicates.get(entry.predicate), root.parameters.map(parameter => parameter.sort)))
        fail('BRIDGE_SORT', path, 'defined predicate signature differs from root parameters');
      emittedPredicates.set(entry.predicate, index);
    }
  }
  if (usedRoots.size !== Object.keys(checked.expanded_roots).length)
    fail('BRIDGE_COVERAGE', '$/lowering/clauses', 'unemitted logical root');

  const signature = {
    sorts: logicalIR.signature.sorts.map(name => ({ name })),
    functions: logicalIR.signature.functions,
    predicates: logicalIR.signature.predicates,
    constants: logicalIR.signature.constants,
  };
  if (!translation || typeof translation !== 'object' || Array.isArray(translation) ||
      !same(translation.formal_signature, signature) || !Array.isArray(translation.clauses) ||
      translation.clauses.length !== config.clauses.length)
    fail('BRIDGE_TRANSLATION', '$/translation', 'signature or clause count differs from checked lowering');

  const fnSorts = new Map(signature.functions.map(row => [row.name, row.result_sort]));
  const constants = new Map(signature.constants.map(row => [row.name, row.sort]));
  const annotateTerm = (node, scope) => {
    if (node.kind === 'variable') return { ...node, sort: scope.get(node.name) };
    if (node.kind === 'constant') return { ...node, sort: constants.get(node.name) };
    return { ...node, sort: fnSorts.get(node.name), arguments: node.arguments.map(arg => annotateTerm(arg, scope)) };
  };
  const annotate = (node, scope) => {
    if (node.kind === 'predicate') return { ...node, arguments: node.arguments.map(arg => annotateTerm(arg, scope)) };
    if (node.kind === 'equal') return { kind: 'equal', left: annotateTerm(node.left, scope), right: annotateTerm(node.right, scope) };
    if (node.kind === 'not') return { kind: 'not', operand: annotate(node.operand, scope) };
    if (['and', 'or', 'implies', 'iff'].includes(node.kind))
      return { kind: node.kind, left: annotate(node.left, scope), right: annotate(node.right, scope) };
    if (['forall', 'exists'].includes(node.kind)) return { kind: node.kind, variable: node.variable,
      sort: node.sort, body: annotate(node.body, new Map([...scope, [node.variable, node.sort]])) };
    fail('BRIDGE_CONSTRUCTOR', '$/lowering', `unexpected expanded constructor ${node.kind}`);
  };
  const predicateUses = (node, found = new Set()) => {
    if (node.kind === 'predicate') found.add(node.name);
    else if (node.kind === 'not') predicateUses(node.operand, found);
    else if (['and', 'or', 'implies', 'iff'].includes(node.kind)) {
      predicateUses(node.left, found); predicateUses(node.right, found);
    } else if (['forall', 'exists'].includes(node.kind)) predicateUses(node.body, found);
    return found;
  };
  const derived = config.clauses.map((entry, index) => {
    const path = `$/lowering/clauses/${index}`;
    const root = checked.expanded_roots[entry.root_definition_id];
    for (const name of predicateUses(root.body)) {
      const at = emittedPredicates.get(name);
      if (at !== undefined && at >= index)
        fail('BRIDGE_FORWARD_REFERENCE', path, `defined predicate ${name} is used before its clause`);
    }
    let body = annotate(root.body, new Map(root.parameters.map(p => [p.name, p.sort])));
    if (entry.kind === 'definition') body = { kind: 'iff',
      left: { kind: 'predicate', name: entry.predicate,
        arguments: root.parameters.map(p => ({ kind: 'variable', name: p.name, sort: p.sort })) },
      right: body };
    for (const parameter of [...root.parameters].reverse()) body = {
      kind: 'forall', variable: parameter.name, sort: parameter.sort, body,
    };
    return { clause_id: entry.clause_id, ast: body };
  });
  for (const [index, row] of translation.clauses.entries()) {
    if (!row || typeof row !== 'object' || Array.isArray(row) ||
        Object.keys(row).sort().join('|') !== 'clause_id|source' ||
        row.clause_id !== derived[index].clause_id || typeof row.source !== 'string' || !row.source.trim())
      fail('BRIDGE_TRANSLATION', `$/translation/clauses/${index}`, 'clause ID or source missing');
  }
  const conjunction = asts => asts.reduce((left, right) => left === null ? right : { kind: 'and', left, right }, null);
  const generatedAst = conjunction(derived.map(row => row.ast));
  const parsedAst = parseFormalProposition(translation.clauses.map(row => `(${row.source})`).join(' and '), signature);
  // The logical checker alpha-renames expanded binders. Canonicalize both sides
  // without changing conjunction order or other connective semantics.
  const alpha = (node, env = new Map(), serial = { n: 0 }) => {
    if (node.kind === 'variable') return { ...node, name: env.get(node.name) ?? node.name };
    if (node.kind === 'constant') return node;
    if (node.kind === 'function') return { ...node, arguments: node.arguments.map(arg => alpha(arg, env, serial)) };
    if (node.kind === 'predicate') return { ...node, arguments: node.arguments.map(arg => alpha(arg, env, serial)) };
    if (node.kind === 'equal') return { kind: 'equal', left: alpha(node.left, env, serial), right: alpha(node.right, env, serial) };
    if (node.kind === 'not') return { kind: 'not', operand: alpha(node.operand, env, serial) };
    if (['and', 'or', 'implies', 'iff'].includes(node.kind)) return { kind: node.kind,
      left: alpha(node.left, env, serial), right: alpha(node.right, env, serial) };
    if (['forall', 'exists'].includes(node.kind)) {
      const fresh = `_bound_${serial.n++}`;
      return { kind: node.kind, variable: fresh, sort: node.sort,
        body: alpha(node.body, new Map([...env, [node.variable, fresh]]), serial) };
    }
    fail('BRIDGE_CONSTRUCTOR', '$/translation', `unsupported parsed constructor ${node.kind}`);
  };
  if (!same(alpha(generatedAst), alpha(parsedAst)))
    fail('BRIDGE_AST_MISMATCH', '$/translation/clauses', 'independently parsed FOL differs from typed definition lowering');
  return { status: 'checked-logical-ir-to-fol-ast', clause_ids: derived.map(row => row.clause_id),
    root_definition_ids: config.clauses.map(row => row.root_definition_id),
    defined_predicates: [...emittedPredicates.keys()], fol_core_comparison_checked: true,
    model_obligations_checked: false, source_binding_checked: false, authority_effect: 'none' };
}
