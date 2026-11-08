// Candidate logical-definition IR checker. This does not interpret carriers,
// occurrences, a BusinessMeaning, or owner acceptance.
export class TypedDefinitionError extends Error {
  constructor(code, path, message) {
    super(`${code} ${path}: ${message}`);
    this.name = 'TypedDefinitionError';
    this.code = code;
    this.path = path;
  }
}

const fail = (code, path, message) => { throw new TypedDefinitionError(code, path, message); };
const ident = /^[A-Za-z_][A-Za-z0-9_]*$/;
const reserved = new Set(['forall', 'exists', 'not', 'and', 'or', 'implies', 'iff', 'true', 'false']);
const id = (value, path) => {
  if (typeof value !== 'string' || !ident.test(value) || value.startsWith('_ir_') || reserved.has(value))
    fail('IR_IDENTIFIER', path, 'expected an ordinary identifier outside the reserved expansion namespace');
  return value;
};
const definitionId = (value, path) => {
  if (typeof value !== 'string' || !/^[A-Z][A-Z0-9-]+$/.test(value))
    fail('IR_IDENTIFIER', path, 'expected a stable definition ID');
  return value;
};
const object = (value, path, keys) => {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail('IR_SHAPE', path, 'expected object');
  if (Object.keys(value).sort().join('|') !== [...keys].sort().join('|'))
    fail('IR_SHAPE', path, `expected exactly ${keys.join(', ')}`);
  return value;
};
const list = (value, path) => {
  if (!Array.isArray(value)) fail('IR_SHAPE', path, 'expected array');
  return value;
};
const unique = (values, path) => {
  if (new Set(values).size !== values.length) fail('IR_DUPLICATE', path, 'duplicate identity');
};

export function checkTypedDefinitionLogicIR(input) {
  const root = object(input, '$', ['schema_version', 'signature', 'definitions', 'roots', 'authority_effect']);
  if (root.schema_version !== 'domainspec-v2.typed-definition-logic-ir/v1-candidate' || root.authority_effect !== 'none')
    fail('IR_VERSION', '$', 'unsupported candidate version or authority effect');
  const signature = object(root.signature, '$/signature', ['sorts', 'functions', 'predicates', 'constants']);
  const sorts = list(signature.sorts, '$/signature/sorts').map((x, i) => id(x, `$/signature/sorts/${i}`));
  if (!sorts.length) fail('IR_SORT', '$/signature/sorts', 'at least one sort required');
  unique(sorts, '$/signature/sorts');
  const hasSort = (sort, path) => {
    if (!sorts.includes(id(sort, path))) fail('IR_SORT', path, `undeclared sort ${sort}`);
    return sort;
  };
  const symbols = new Set(sorts);
  const declare = (name, path) => {
    id(name, path);
    if (symbols.has(name)) fail('IR_DUPLICATE', path, `duplicate symbol ${name}`);
    symbols.add(name);
  };
  const functions = new Map();
  for (const [i, raw] of list(signature.functions, '$/signature/functions').entries()) {
    const path = `$/signature/functions/${i}`;
    const entry = object(raw, path, ['name', 'parameter_sorts', 'result_sort']);
    declare(entry.name, `${path}/name`);
    const parameters = list(entry.parameter_sorts, `${path}/parameter_sorts`).map((s, j) => hasSort(s, `${path}/parameter_sorts/${j}`));
    functions.set(entry.name, { parameters, result: hasSort(entry.result_sort, `${path}/result_sort`) });
  }
  const predicates = new Map();
  for (const [i, raw] of list(signature.predicates, '$/signature/predicates').entries()) {
    const path = `$/signature/predicates/${i}`;
    const entry = object(raw, path, ['name', 'parameter_sorts']);
    declare(entry.name, `${path}/name`);
    predicates.set(entry.name, list(entry.parameter_sorts, `${path}/parameter_sorts`).map((s, j) => hasSort(s, `${path}/parameter_sorts/${j}`)));
  }
  const constants = new Map();
  for (const [i, raw] of list(signature.constants, '$/signature/constants').entries()) {
    const path = `$/signature/constants/${i}`;
    const entry = object(raw, path, ['name', 'sort']);
    declare(entry.name, `${path}/name`);
    constants.set(entry.name, hasSort(entry.sort, `${path}/sort`));
  }
  const definitions = new Map();
  const rawDefinitions = list(root.definitions, '$/definitions');
  if (rawDefinitions.length > 128) fail('IR_LIMIT', '$/definitions', 'more than 128 definitions');
  for (const [i, raw] of rawDefinitions.entries()) {
    const path = `$/definitions/${i}`;
    const entry = object(raw, path, ['definition_id', 'symbol', 'parameters', 'body', 'depends_on']);
    const selectedId = definitionId(entry.definition_id, `${path}/definition_id`);
    if (definitions.has(selectedId)) fail('IR_DUPLICATE', path, 'duplicate definition ID');
    declare(entry.symbol, `${path}/symbol`);
    const parameters = list(entry.parameters, `${path}/parameters`).map((rawParameter, j) => {
      const parameter = object(rawParameter, `${path}/parameters/${j}`, ['name', 'sort']);
      return { name: id(parameter.name, `${path}/parameters/${j}/name`), sort: hasSort(parameter.sort, `${path}/parameters/${j}/sort`) };
    });
    unique(parameters.map(parameter => parameter.name), `${path}/parameters`);
    for (const parameter of parameters) if (symbols.has(parameter.name)) fail('IR_IDENTIFIER', path, 'parameter collides with a signature symbol');
    const declaredDependencies = list(entry.depends_on, `${path}/depends_on`).map((v, j) => definitionId(v, `${path}/depends_on/${j}`));
    unique(declaredDependencies, `${path}/depends_on`);
    definitions.set(selectedId, { path, symbol: entry.symbol, parameters, body: entry.body, declaredDependencies });
  }
  if (!definitions.size) fail('IR_SHAPE', '$/definitions', 'at least one definition required');
  for (const definition of definitions.values())
    for (const parameter of definition.parameters)
      if (symbols.has(parameter.name)) fail('IR_IDENTIFIER', definition.path, 'parameter collides with a declared symbol');
  const bySymbol = new Map([...definitions].map(([definitionId, value]) => [value.symbol, { definitionId, ...value }]));
  const roots = list(root.roots, '$/roots').map((v, i) => definitionId(v, `$/roots/${i}`));
  if (!roots.length) fail('IR_SHAPE', '$/roots', 'at least one root required');
  unique(roots, '$/roots');
  for (const definitionId of roots) if (!definitions.has(definitionId)) fail('IR_UNRESOLVED', '$/roots', `unknown root ${definitionId}`);

  const term = (raw, scope, path, depth = 0) => {
    if (depth > 256) fail('IR_LIMIT', path, 'term nesting exceeds 256');
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) fail('IR_SHAPE', path, 'expected term');
    if (raw.kind === 'variable') {
      object(raw, path, ['kind', 'name']);
      if (!scope.has(id(raw.name, `${path}/name`))) fail('IR_UNBOUND', path, `unbound variable ${raw.name}`);
      return scope.get(raw.name);
    }
    if (raw.kind === 'constant') {
      object(raw, path, ['kind', 'name']);
      if (!constants.has(id(raw.name, `${path}/name`))) fail('IR_UNRESOLVED', path, `unknown constant ${raw.name}`);
      return constants.get(raw.name);
    }
    if (raw.kind === 'function') {
      object(raw, path, ['kind', 'name', 'arguments']);
      const fn = functions.get(id(raw.name, `${path}/name`));
      if (!fn) fail('IR_UNRESOLVED', path, `unknown function ${raw.name}`);
      args(raw.arguments, fn.parameters, scope, `${path}/arguments`, depth + 1);
      return fn.result;
    }
    fail('IR_CONSTRUCTOR', path, `unsupported term constructor ${raw.kind}`);
  };
  const args = (raw, expected, scope, path, depth = 0) => {
    const values = list(raw, path);
    if (values.length !== expected.length) fail('IR_ARITY', path, `expected ${expected.length} arguments`);
    values.forEach((value, i) => {
      const actual = term(value, scope, `${path}/${i}`, depth + 1);
      if (actual !== expected[i]) fail('IR_SORT', `${path}/${i}`, `expected ${expected[i]}, got ${actual}`);
    });
  };
  const formula = (raw, scope, path, refs, depth = 0) => {
    if (depth > 256) fail('IR_LIMIT', path, 'formula nesting exceeds 256');
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) fail('IR_SHAPE', path, 'expected formula');
    switch (raw.kind) {
      case 'true': case 'false': object(raw, path, ['kind']); return;
      case 'predicate': {
        object(raw, path, ['kind', 'name', 'arguments']);
        const expected = predicates.get(id(raw.name, `${path}/name`));
        if (!expected) fail('IR_UNRESOLVED', path, `unknown primitive predicate ${raw.name}`);
        args(raw.arguments, expected, scope, `${path}/arguments`, depth + 1); return;
      }
      case 'ref': {
        object(raw, path, ['kind', 'symbol', 'arguments']);
        const target = bySymbol.get(id(raw.symbol, `${path}/symbol`));
        if (!target) fail('IR_UNRESOLVED', path, `unknown definition ${raw.symbol}`);
        args(raw.arguments, target.parameters.map(p => p.sort), scope, `${path}/arguments`, depth + 1);
        refs.add(target.definitionId); return;
      }
      case 'equal': {
        object(raw, path, ['kind', 'left', 'right']);
        const left = term(raw.left, scope, `${path}/left`, depth + 1);
        const right = term(raw.right, scope, `${path}/right`, depth + 1);
        if (left !== right) fail('IR_SORT', path, 'equality sorts differ'); return;
      }
      case 'not': object(raw, path, ['kind', 'operand']); formula(raw.operand, scope, `${path}/operand`, refs, depth + 1); return;
      case 'and': case 'or': case 'implies': case 'iff':
        object(raw, path, ['kind', 'left', 'right']);
        formula(raw.left, scope, `${path}/left`, refs, depth + 1);
        formula(raw.right, scope, `${path}/right`, refs, depth + 1); return;
      case 'forall': case 'exists': {
        object(raw, path, ['kind', 'variable', 'sort', 'body']);
        const name = id(raw.variable, `${path}/variable`);
        const sort = hasSort(raw.sort, `${path}/sort`);
        if (scope.has(name) || symbols.has(name)) fail('IR_IDENTIFIER', path, 'bound variable shadows a parameter or signature symbol');
        formula(raw.body, new Map([...scope, [name, sort]]), `${path}/body`, refs, depth + 1); return;
      }
      default: fail('IR_CONSTRUCTOR', path, `unsupported formula constructor ${raw.kind}`);
    }
  };

  const edges = new Map();
  for (const [definitionId, definition] of definitions) {
    const refs = new Set();
    formula(definition.body, new Map(definition.parameters.map(p => [p.name, p.sort])), `${definition.path}/body`, refs);
    const actual = [...refs].sort();
    if (JSON.stringify(actual) !== JSON.stringify([...definition.declaredDependencies].sort()))
      fail('IR_DEPENDENCY', definition.path, `declared dependencies differ from body references for ${definitionId}`);
    edges.set(definitionId, actual);
  }
  const active = new Set(), visited = new Set();
  const visit = definitionId => {
    if (active.has(definitionId)) fail('IR_CYCLE', '$/definitions', `cycle at ${definitionId}`);
    if (visited.has(definitionId)) return;
    active.add(definitionId);
    for (const target of edges.get(definitionId)) visit(target);
    active.delete(definitionId); visited.add(definitionId);
  };
  roots.forEach(visit);
  if (visited.size !== definitions.size) fail('IR_ORPHAN', '$/definitions', 'definition is not reachable from a root');

  let serial = 0;
  let expandedNodes = 0;
  const countNode = () => {
    if (++expandedNodes > 10000) fail('IR_EXPANSION_LIMIT', '$/definitions', 'expanded logical IR exceeds 10000 nodes');
  };
  const copyTerm = (value, depth = 0) => {
    if (depth > 256) fail('IR_EXPANSION_LIMIT', '$/definitions', 'expanded term nesting exceeds 256');
    countNode();
    return value.kind === 'function'
      ? { ...value, arguments: value.arguments.map(arg => copyTerm(arg, depth + 1)) }
      : { ...value };
  };
  const substituteTerm = (value, bindings, depth = 0) => {
    if (depth > 256) fail('IR_EXPANSION_LIMIT', '$/definitions', 'expanded term nesting exceeds 256');
    if (value.kind === 'variable' && bindings.has(value.name)) return copyTerm(bindings.get(value.name), depth);
    countNode();
    return value.kind === 'function'
      ? { ...value, arguments: value.arguments.map(arg => substituteTerm(arg, bindings, depth + 1)) }
      : { ...value };
  };
  const expand = (raw, bindings, depth = 0) => {
    if (depth > 256) fail('IR_EXPANSION_LIMIT', '$/definitions', 'expansion nesting exceeds 256');
    countNode();
    if (raw.kind === 'ref') {
      const target = bySymbol.get(raw.symbol);
      const actual = raw.arguments.map(arg => substituteTerm(arg, bindings));
      return expand(target.body, new Map(target.parameters.map((parameter, i) => [parameter.name, actual[i]])), depth + 1);
    }
    if (raw.kind === 'forall' || raw.kind === 'exists') {
      const fresh = `_ir_${++serial}`;
      const nested = new Map(bindings);
      nested.set(raw.variable, { kind: 'variable', name: fresh });
      return { kind: raw.kind, variable: fresh, sort: raw.sort, body: expand(raw.body, nested, depth + 1) };
    }
    if (raw.kind === 'predicate') return { ...raw, arguments: raw.arguments.map(arg => substituteTerm(arg, bindings)) };
    if (raw.kind === 'equal') return { kind: 'equal', left: substituteTerm(raw.left, bindings), right: substituteTerm(raw.right, bindings) };
    if (raw.kind === 'not') return { kind: 'not', operand: expand(raw.operand, bindings, depth + 1) };
    if (['and', 'or', 'implies', 'iff'].includes(raw.kind)) return { kind: raw.kind, left: expand(raw.left, bindings, depth + 1), right: expand(raw.right, bindings, depth + 1) };
    return structuredClone(raw);
  };
  const expanded_roots = Object.fromEntries(roots.map(definitionId => {
    const definition = definitions.get(definitionId);
    return [definitionId, { parameters: definition.parameters, body: expand(definition.body, new Map()) }];
  }));
  return { status: 'checked-logical-ir-only', schema_version: root.schema_version,
    definition_count: definitions.size, expanded_roots, model_obligations_checked: false,
    fol_core_comparison_checked: false,
    authority_effect: 'none' };
}
