import { assertCheckedComposedOperationAction, type CheckedComposedOperationAction } from '../typed-operation/action-bindings.js';
import type { CompositionValueType } from '../typed-operation/value-composition-types.js';
import type { ValueExpression } from '../typed-operation/contracts.js';
import { assertInterfaceData } from '../typed-backend/interface.js';
import { qualifyPublicType, type MappingValueType } from '../typed-backend/mapping-public.js';
import { canonicalJson, sha256 } from '../input/source-manifest.js';
import type { FieldReferenceModel } from '../input/field-reference-model.js';
import type { createStructuredValueRenderer } from './configured-value-types.js';
import { createStructuredValueExpressionRenderer } from './configured-value-expressions.js';
import { createPublicMappingValues } from './public-mapping-values.js';

export interface OperationValueImport { readonly selector: string; readonly kind: 'query' | 'mapping'; readonly path: string; readonly symbol: string; readonly local: string; readonly contract_sha256: string }
export interface OperationPublicValueImport { readonly selector: string; readonly path: string; readonly local: string; readonly contract_sha256: string }
export interface OperationAbsenceFailure { readonly binding: string; readonly code: string }
export interface ComposedBoundValue { readonly type: CompositionValueType; readonly code: string }
const q = JSON.stringify;
const fail = (message: string): never => { throw new Error('DS_COMPOSED_OPERATION:' + message); };
const matches = (value: unknown, pattern: RegExp): value is string => typeof value === 'string' && pattern.exec(value)?.[0] === value;
const exactSet = (a: readonly string[], b: readonly string[], reason: string) => { if (canonicalJson([...new Set(a)].sort()) !== canonicalJson([...new Set(b)].sort())) fail(reason); };

/** Static lowering only: named modules execute their existing Query/Mapping
 * semantics. No expression interpreter or provider discovery is emitted.
 */
export function createOperationCompositionRenderer(action: CheckedComposedOperationAction, model: FieldReferenceModel,
  values: ReturnType<typeof createStructuredValueRenderer>, scope: Map<string, ComposedBoundValue>,
  imports: readonly OperationValueImport[], publicImports: readonly OperationPublicValueImport[], absenceFailures: readonly OperationAbsenceFailure[]) {
  assertCheckedComposedOperationAction(action);
  assertInterfaceData(model);
  assertInterfaceData(imports); assertInterfaceData(publicImports); assertInterfaceData(absenceFailures);
  const composition = action.value_composition;
  const { model_sha256, ...modelBody } = model;
  if (model_sha256 !== composition.field_model_sha256 || sha256(canonicalJson(modelBody)) !== model_sha256) fail('field model mismatch');
  const safeImport = (p: { path: string; local: string }, pattern: RegExp) => {
    if (!matches(p.local, pattern) || !matches(p.path, /^(?:\.\/|\.\.\/)[^\u0000-\u001f\\]+\.js$/)) fail('invalid native dependency');
  };
  if (new Set(imports.map(i => i.selector)).size !== imports.length || new Set(imports.map(i => i.local)).size !== imports.length) fail('duplicate value import');
  exactSet(imports.map(i => i.selector), composition.values.map(v => v.selector), 'value import coverage');
  for (const dependency of imports) {
    safeImport(dependency, /^valueCall[0-9]+$/);
    if (!matches(dependency.symbol, /^[A-Za-z_$][A-Za-z0-9_$]*$/)) fail('invalid callable symbol');
    const row = composition.references.connections.find(c => c.binding.selector === dependency.selector)!;
    if (dependency.kind !== row.binding.kind || dependency.contract_sha256 !== row.contract_sha256) fail('value import contract mismatch');
  }
  if (new Set(publicImports.map(i => i.selector)).size !== publicImports.length || new Set(publicImports.map(i => i.local)).size !== publicImports.length) fail('duplicate public import');
  for (const dependency of publicImports) {
    safeImport(dependency, /^valuePublic[0-9]+$/);
    const api = composition.public_contracts.find(i => i.selector === dependency.selector);
    if (!api || sha256(canonicalJson(api.contract)) !== dependency.contract_sha256) fail('public import contract mismatch');
  }
  const required = composition.references.composition.bindings.filter(b => b.kind === 'query' && b.absence === 'require-present').map(b => b.name);
  if (new Set(absenceFailures.map(f => f.binding)).size !== absenceFailures.length) fail('duplicate absence binding');
  exactSet(required, absenceFailures.map(f => f.binding), 'explicit absence failure coverage');
  if (absenceFailures.some(f => !matches(f.code, /^[A-Z][A-Z0-9_]{0,127}$/))) fail('invalid absence outcome code');
  const usedPublic = new Set<string>();
  const publicValues = createPublicMappingValues(model, composition.public_contracts, new Map(publicImports.map(i => [i.selector, i.local])), fail, values);
  const markPublic = (type: MappingValueType): void => {
    if (type.kind === 'contract') usedPublic.add(type.interface_selector);
    else if (type.kind === 'sum') type.variants.forEach(v => { if (v.payload) markPublic(v.payload); });
    else if (type.kind === 'optional' || type.kind === 'list' || type.kind === 'set') markPublic(type.element);
  };
  const materialType = (type: CompositionValueType): MappingValueType => {
    if (type.kind === 'projection') return fail('partial projection has no declared set identity');
    if (type.kind === 'sum') return { ...type, variants: type.variants.map(v => ({ ...v, payload: v.payload ? materialType(v.payload) : null })) };
    if (type.kind === 'optional' || type.kind === 'list' || type.kind === 'set') return { ...type, element: materialType(type.element) };
    if (type.kind === 'scalar' || type.kind === 'named' || type.kind === 'reference' || type.kind === 'contract') return type;
    return fail('unsupported material value type');
  };
  const protocol = (type: CompositionValueType) => { const t = materialType(type); markPublic(t); return publicValues.ensure(t).protocol; };
  const properties = (type: CompositionValueType): readonly { name: string; ontology_property: string; type: CompositionValueType }[] => {
    if (type.kind === 'projection') return properties(type.owner).filter(p => type.fields.includes(p.name));
    if (type.kind === 'contract') {
      const api = composition.public_contracts.find(i => i.selector === type.interface_selector);
      const contract = api?.contract.contracts.find(c => c.contract_id === type.contract_id) ?? fail('missing public shape');
      return contract.fields.map(f => ({ name: f.name, ontology_property: f.ontology_field, type: qualifyPublicType(f.type, type.interface_selector) }));
    }
    if (type.kind === 'named' || type.kind === 'reference') {
      const d = values.get(type.selector); if (d.kind === 'Enum') return fail('Enum has no fields');
      return type.kind === 'reference' ? d.contract.properties.filter(f => f.identity && f.name === type.projection[0]) : d.contract.properties;
    }
    return fail('unsupported value traversal');
  };
  let next = 0;
  const literal = createStructuredValueExpressionRenderer(values, model, () => 'valueItem' + next++, fail);
  const expression = (node: ValueExpression, currentScope: ReadonlyMap<string, ComposedBoundValue>): ComposedBoundValue => {
    if (node.op === 'literal' || node.op === 'variant') return literal(node, new Map());
    if (node.op === 'to_set') {
      const source = expression(node.value, currentScope); if (source.type.kind !== 'list') return fail('to_set requires list');
      values.use('to-set'); return { type: { kind: 'set', element: source.type.element }, code: 'ruleToSet(' + source.code + ',' + protocol(source.type.element) + ')' };
    }
    let current = currentScope.get(node.root) ?? fail('missing value root');
    for (const property of node.properties) {
      const kind = current.type.kind, collection = kind === 'list' || kind === 'set';
      const owner = current.type.kind === 'list' || current.type.kind === 'set' ? current.type.element : current.type;
      const field = properties(owner).find(p => p.ontology_property === property) ?? fail('missing projected field');
      if (owner.kind === 'reference') { current = { type: collection ? { kind: kind as 'list' | 'set', element: field.type } : field.type, code: current.code }; continue; }
      if (collection) {
        const item = 'valueItem' + next++, mapped = current.code + '.map(' + item + '=>' + item + '[' + q(field.name) + '])';
        if (kind === 'set') values.use('to-set');
        current = { type: { kind: kind as 'list' | 'set', element: field.type }, code: kind === 'set' ? 'ruleToSet(' + mapped + ',' + protocol(field.type) + ')' : 'Object.freeze(' + mapped + ')' };
      } else current = { type: field.type, code: current.code + '[' + q(field.name) + ']' };
    }
    return current;
  };
  const lines: string[] = [];
  for (const [index, step] of composition.values.entries()) {
    const row = composition.references.connections.find(r => r.binding.name === step.name)!;
    const dependency = imports.find(i => i.selector === step.selector)!;
    const args = '{' + row.binding.arguments.map(a => '[' + q(a.parameter) + ']:' + expression(a.value, scope).code).join(',') + '}';
    const name = 'computed' + index;
    if (row.binding.kind === 'query' && 'query_source' in row) {
      lines.push('    stage=' + q('query-source:' + row.binding.name) + ';\n    const source' + index + '=await transaction.querySource(Object.freeze({slot:' + q(row.binding.source_slot) + ',target:' + q(row.query_source!.selector) + '}));\n');
      lines.push('    stage=' + q('query:' + row.binding.selector) + ';\n    let ' + name + ':ReturnType<typeof ' + dependency.local + '>;\n    try{' + name + '=' + dependency.local + '(source' + index + ' as Parameters<typeof ' + dependency.local + '>[0],' + args + ');}catch(error){\n      if(error instanceof Error&&Object.getOwnPropertyDescriptor(error,"message")?.value==="QUERY_CARDINALITY")return abort("failed","QUERY_CARDINALITY");\n      throw error;\n    }\n');
      if (row.binding.absence === 'require-present') lines.push('    if(' + name + '===null)return abort("failed",' + q(absenceFailures.find(f => f.binding === step.name)!.code) + ');\n');
    } else lines.push('    stage=' + q('mapping:' + row.binding.selector) + ';\n    const ' + name + '=' + dependency.local + '(' + args + ');\n');
    scope.set(step.name, { type: step.output, code: name });
  }
  return {
    expression, preparation: lines.join(''),
    sourceRequest: composition.references.source_slots.filter(s => s.mode === 'collection').map(s => 'Readonly<{slot:' + q(s.slot) + ';target:' + q(s.target) + '}>').join('|') || 'never',
    imports: () => imports.map(i => 'import {' + i.symbol + ' as ' + i.local + '} from ' + q(i.path) + ';\n').join('')
      + publicImports.filter(i => usedPublic.has(i.selector)).map(i => 'import * as ' + i.local + ' from ' + q(i.path) + ';\n').join(''),
    source: (body: string) => publicValues.source(body),
  };
}
