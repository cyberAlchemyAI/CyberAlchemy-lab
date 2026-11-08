import type {RuleExpression, TypedRuleContract, TypedType, ValueExpression} from '../typed-operation/contracts.js';
import {isCanonicalUInt64Decimal} from '../typed-operation/contracts.js';
import type {ConfiguredRuleModule} from './configured-rules.js';

// v4 source emitter only: consumes checked expressions, never interprets them at runtime.
type BoundValue = Readonly<{type: TypedType; code: string}>;
type Scope = ReadonlyMap<string, BoundValue>;
const fail = (message: string): never => { throw new Error('DS_CONFIGURED_RULE:' + message); };
const scalar = (type: TypedType, numeric=false): type is Readonly<{kind:'scalar';name:'String'|'Bool'|'UInt64'}> =>
  type.kind === 'scalar' && (type.name === 'String' || type.name === 'Bool' || numeric && type.name === 'UInt64');
const collection = (type: TypedType, numeric=false): type is Readonly<{kind:'list'|'set';element:Readonly<{kind:'scalar';name:'String'|'Bool'|'UInt64'}>}> =>
  (type.kind === 'list' || type.kind === 'set') && scalar(type.element,numeric);
const same = (left: TypedType, right: TypedType, numeric=false): boolean =>
  scalar(left,numeric) && scalar(right,numeric) ? left.name === right.name :
    collection(left,numeric) && collection(right,numeric) && left.kind === right.kind && left.element.name === right.element.name;
const nativeScalar = (name:string,exact=false) => name === 'Bool' ? 'boolean' : name === 'UInt64' ? exact ? 'bigint' : 'number' : 'string';

export function collectionPredicateSource(rule: TypedRuleContract, imports: ConfiguredRuleModule['imports'], numeric=false, exact=false): string {
  if (rule.schema_version === 'domainspec.typed-rule/v2' && (!numeric || !exact)) fail('typed Rule v2 requires exact numeric realization');
  let next = 0;
  const fresh = () => `q${next++}`;
  const value = (expression: ValueExpression, scope: Scope): BoundValue => {
    if (expression.op === 'literal' && expression.type === 'UInt64' && rule.schema_version === 'domainspec.typed-rule/v2') {
      if (!isCanonicalUInt64Decimal(expression.value)) return fail('invalid exact UInt64 literal');
      return {type:{kind:'scalar',name:'UInt64'},code:expression.value+'n'};
    }
    if (expression.op === 'literal' && (expression.type === 'String' || expression.type === 'Bool' || numeric && expression.type === 'UInt64'))
      return {type:{kind:'scalar',name:expression.type},code:JSON.stringify(expression.value)+(exact && expression.type==='UInt64'?'n':'')};
    if (expression.op === 'path' && expression.properties.length === 0) {
      const bound = scope.get(expression.root);
      if (bound) return bound;
    }
    if (expression.op === 'to_set') {
      const source = value(expression.value, scope);
      if (!collection(source.type,numeric) || source.type.kind !== 'list') return fail('to_set requires a scalar list');
      const nativeType = nativeScalar(source.type.element.name,exact);
      return {type:{kind:'set',element:source.type.element},
        code:`normalizeRuleCollection<${nativeType}>([...new Set(${source.code})],${JSON.stringify(nativeType)},true)`};
    }
    return fail('v4 supports scalar literals, direct scoped paths and scalar-list to_set only');
  };
  const expression = (node: RuleExpression, scope: Scope): string => {
    if (node.op === 'all' || node.op === 'any')
      return '(' + node.terms.map(term => expression(term, scope)).join(node.op === 'all' ? ' && ' : ' || ') + ')';
    if (node.op === 'not') return `!(${expression(node.term, scope)})`;
    if (node.op === 'rule_ref') {
      const dependency = imports.find(item => item.selector === node.selector);
      if (!dependency) return fail('unplanned Rule reference:' + node.selector);
      const args = [...node.arguments].sort((a,b) => a.parameter < b.parameter ? -1 : a.parameter > b.parameter ? 1 : 0);
      return `${dependency.local}({${args.map(arg => `[${JSON.stringify(arg.parameter)}]:${value(arg.value, scope).code}`).join(',')}})`;
    }
    if (node.op === 'eq' || node.op === 'lt' || node.op === 'contains' || node.op === 'set_equal') {
      const left = value(node.left, scope), right = value(node.right, scope);
      if (node.op === 'contains') {
        if (!collection(left.type,numeric) || !same(left.type.element, right.type,numeric)) return fail('contains requires a collection and same-type scalar element');
        const member = fresh();
        return `${left.code}.some(${member}=>${member}===${right.code})`;
      }
      if (!same(left.type, right.type,numeric)) return fail('incompatible v4 comparison operands');
      if (node.op === 'lt') {
        if (!scalar(left.type,numeric) || !(left.type.name === 'String' || numeric && left.type.name === 'UInt64')) return fail('lt requires String or explicitly selected UInt64 operands');
        return `(${left.code} < ${right.code})`;
      }
      if (node.op === 'set_equal' && left.type.kind !== 'set') return fail('set_equal requires scalar sets');
      if (scalar(left.type,numeric)) return `(${left.code} === ${right.code})`;
      if (!collection(left.type,numeric)) return fail('unsupported v4 equality');
      // Lists retain order; every set value is already canonicalized at its boundary.
      const a = fresh(), b = fresh(), member = fresh(), index = fresh();
      const nativeType = nativeScalar(left.type.element.name,exact);
      return `((${a}:readonly ${nativeType}[],${b}:readonly ${nativeType}[])=>${a}.length===${b}.length&&${a}.every((${member},${index})=>${member}===${b}[${index}]))(${left.code},${right.code})`;
    }
    if (node.op === 'exists' || node.op === 'exactly_one' || node.op === 'unique') {
      const source = value(node.collection, scope);
      if (!collection(source.type,numeric)) return fail('v4 quantifier requires a scalar collection');
      const binding = fresh(), nested = new Map(scope);
      nested.set(node.binding, {type:source.type.element, code:binding});
      if (node.op === 'unique') {
        if (node.where.op !== 'eq' || node.where.left.op !== 'path' || JSON.stringify(node.where.left) !== JSON.stringify(node.where.right))
          return fail('unique requires an identical path key');
        const key = value(node.where.left, nested);
        if (!scalar(key.type,numeric)) return fail('v4 unique requires a scalar key');
        return `(new Set(${source.code}.map(${binding}=>${key.code})).size===${source.code}.length)`;
      }
      const predicate = expression(node.where, nested);
      return node.op === 'exists' ? `${source.code}.some(${binding}=>${predicate})` :
        `(${source.code}.filter(${binding}=>${predicate}).length===1)`;
    }
    return fail('unsupported v4 operator');
  };
  return expression(rule.expression, new Map(rule.parameters.map((parameter,index) =>
    [parameter.name, {type:parameter.type,code:`p${index}`}])));
}
