// Candidate occurrence-model shape checker. It emits proof obligations; it does
// not establish that the declared record is the selected typed Context.
import { checkTypedDefinitionLogicIR } from './typed-definition-logic-ir.mjs';

export class TypedDefinitionModelError extends Error {
  constructor(code, path, message) {
    super(`${code} ${path}: ${message}`);
    this.name = 'TypedDefinitionModelError';
    this.code = code;
    this.path = path;
  }
}

const fail = (code, path, message) => { throw new TypedDefinitionModelError(code, path, message); };
const namePattern = /^[A-Za-z_][A-Za-z0-9_]*$/;
const name = (value, path) => {
  if (typeof value !== 'string' || !namePattern.test(value))
    fail('MODEL_NAME', path, 'expected a type or field identifier');
  return value;
};
const object = (value, path, keys) => {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      Object.keys(value).sort().join('|') !== [...keys].sort().join('|'))
    fail('MODEL_SHAPE', path, `expected exactly ${keys.join(', ')}`);
  return value;
};
const list = (value, path, limit) => {
  if (!Array.isArray(value) || !value.length || value.length > limit)
    fail('MODEL_SHAPE', path, `expected 1–${limit} entries`);
  return value;
};
const fixed = (actual, expected, path) => {
  if (actual !== expected) fail('MODEL_CONSTRUCTOR', path, `expected ${expected}`);
};
const unique = (values, path) => {
  if (new Set(values).size !== values.length) fail('MODEL_DUPLICATE', path, 'duplicate identity');
};

export function checkTypedDefinitionModelIR(input, logicalIR) {
  // Use the checked logical signature rather than a second model-authored FOL
  // signature. This still does not prove the signature matches accepted meaning.
  const logical = checkTypedDefinitionLogicIR(logicalIR);
  const root = object(input, '$', ['schema_version', 'context', 'scope', 'occurrences', 'authority_effect']);
  fixed(root.schema_version, 'domainspec-v2.typed-definition-model-ir/v1-candidate', '$/schema_version');
  fixed(root.authority_effect, 'none', '$/authority_effect');
  const context = object(root.context, '$/context', ['sort', 'carrier', 'fields']);
  const contextSort = name(context.sort, '$/context/sort');
  if (!logicalIR.signature.sorts.includes(contextSort))
    fail('MODEL_SORT', '$/context/sort', 'Context sort absent from checked logical signature');
  fixed(context.carrier, 'full-typed-record-with-finite-lists', '$/context/carrier');
  const fields = list(context.fields, '$/context/fields', 128).map((raw, i) => {
    const path = `$/context/fields/${i}`;
    const field = object(raw, path, ['name', 'kind', 'type']);
    name(field.name, `${path}/name`);
    name(field.type, `${path}/type`);
    if (!['scalar', 'record', 'list'].includes(field.kind))
      fail('MODEL_CONSTRUCTOR', `${path}/kind`, 'unsupported context field kind');
    return field;
  });
  unique(fields.map(field => field.name), '$/context/fields');
  const listFields = fields.filter(field => field.kind === 'list');
  if (!listFields.length) fail('MODEL_COVERAGE', '$/context/fields', 'no occurrence-bearing list declared');
  const byField = new Map(listFields.map(field => [field.name, field]));
  const scope = object(root.scope, '$/scope', ['kind', 'normal_completion']);
  fixed(scope.kind, 'entire-context-carrier', '$/scope/kind');
  fixed(scope.normal_completion, 'separate-correspondence-obligation', '$/scope/normal_completion');

  const logicalSorts = new Set(logicalIR.signature.sorts);
  const predicates = new Map(logicalIR.signature.predicates.map(row => [row.name, row.parameter_sorts]));
  const occurrences = list(root.occurrences, '$/occurrences', 64).map((raw, i) => {
    const path = `$/occurrences/${i}`;
    const entry = object(raw, path, ['sort', 'list_field', 'row_type', 'carrier', 'identity', 'membership', 'projection', 'qualifier_definition_id']);
    const sort = name(entry.sort, `${path}/sort`);
    const field = name(entry.list_field, `${path}/list_field`);
    const rowType = name(entry.row_type, `${path}/row_type`);
    if (sort === contextSort || !logicalSorts.has(sort))
      fail('MODEL_SORT', `${path}/sort`, 'occurrence sort must be distinct and present in logical signature');
    if (!byField.has(field) || byField.get(field).type !== rowType)
      fail('MODEL_COVERAGE', `${path}/list_field`, 'occurrence must cover one declared list with its exact row type');
    fixed(entry.carrier, 'context-row-position-product', `${path}/carrier`);
    fixed(entry.identity, 'context-and-zero-based-position', `${path}/identity`);
    fixed(entry.projection, 'total-tuple-row', `${path}/projection`);
    const member = object(entry.membership, `${path}/membership`, ['kind', 'predicate', 'start', 'nonmembers']);
    fixed(member.kind, 'tagged-zip-index', `${path}/membership/kind`);
    fixed(member.start, 0, `${path}/membership/start`);
    fixed(member.nonmembers, 'ghost-and-foreign-excluded', `${path}/membership/nonmembers`);
    const predicate = name(member.predicate, `${path}/membership/predicate`);
    if (JSON.stringify(predicates.get(predicate)) !== JSON.stringify([contextSort, sort]))
      fail('MODEL_SIGNATURE', `${path}/membership/predicate`, 'membership predicate must have Context × occurrence signature');
    const qualifierId = entry.qualifier_definition_id;
    if (typeof qualifierId !== 'string' || !/^[A-Z][A-Z0-9-]+$/.test(qualifierId))
      fail('MODEL_QUALIFIER', `${path}/qualifier_definition_id`, 'expected stable definition ID');
    const qualifier = logical.expanded_roots[qualifierId];
    if (!qualifier || qualifier.parameters.length !== 2 ||
        qualifier.parameters[0].sort !== contextSort || qualifier.parameters[1].sort !== sort)
      fail('MODEL_QUALIFIER', `${path}/qualifier_definition_id`, 'qualifier must be a checked logical root with Context × occurrence parameters');
    const [contextParameter, occurrenceParameter] = qualifier.parameters.map(parameter => parameter.name);
    const directConjuncts = body => body.kind === 'and'
      ? [...directConjuncts(body.left), ...directConjuncts(body.right)] : [body];
    const hasMember = directConjuncts(qualifier.body).some(body => body.kind === 'predicate' &&
      body.name === predicate && body.arguments.length === 2 &&
      body.arguments[0].kind === 'variable' && body.arguments[0].name === contextParameter &&
      body.arguments[1].kind === 'variable' && body.arguments[1].name === occurrenceParameter);
    if (!hasMember)
      fail('MODEL_QUALIFIER', `${path}/qualifier_definition_id`, 'qualifier must contain direct matching membership conjunct');
    return { sort, list_field: field, row_type: rowType, member_predicate: predicate,
      qualifier_definition_id: qualifierId };
  });
  unique(occurrences.map(row => row.sort), '$/occurrences');
  unique(occurrences.map(row => row.list_field), '$/occurrences');
  unique(occurrences.map(row => row.member_predicate), '$/occurrences');
  unique(occurrences.map(row => row.qualifier_definition_id), '$/occurrences');
  if (occurrences.length !== listFields.length ||
      listFields.some(field => !occurrences.some(row => row.list_field === field.name)))
    fail('MODEL_COVERAGE', '$/occurrences', 'every declared Context list requires exactly one occurrence carrier');

  const obligations = [
    { id: 'full-context-correspondence', status: 'unproved', subject: contextSort,
      statement: 'Declared Context fields equal the entire selected typed Context; no outcome-dependent subcarrier.' },
    { id: 'context-and-row-inhabitance', status: 'unproved', subject: contextSort,
      statement: 'Context and each occurrence row type are inhabited, so their product carriers are nonempty.' },
    { id: 'fixed-scope-and-normal-completion', status: 'unproved', subject: contextSort,
      statement: 'Every selected representable Context is in scope; evaluator normal completion is separate.' },
    ...occurrences.flatMap(row => [
      { id: `${row.list_field}-position-bijection`, status: 'unproved', subject: row.sort,
        statement: 'Every valid zero-based list position appears exactly once; equal row values retain distinct positions.' },
      { id: `${row.list_field}-membership-and-projections`, status: 'unproved', subject: row.sort,
        statement: 'Ghost and foreign positions are nonmembers; all field projections are total and exact on members.' },
      { id: `${row.list_field}-qualifier-source-correspondence`, status: 'unproved', subject: row.qualifier_definition_id,
        statement: 'Every other qualifier field condition matches the selected typed evaluator and FOL clause.' },
    ]),
  ];
  return { status: 'checked-model-ir-shape-only', schema_version: root.schema_version,
    logical_ir_status: logical.status, context_sort: contextSort, occurrence_count: occurrences.length,
    obligations, typed_context_carrier_correspondence_proved: false,
    logical_qualifier_membership_binding_checked: true,
    logical_qualifier_full_definition_checked: false,
    lean_obligations_proved: false, normal_completion_checked: false,
    model_obligations_checked: false, authority_effect: 'none' };
}
