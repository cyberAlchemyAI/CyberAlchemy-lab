const NODE_SELECTOR = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const ONTOLOGY_SELECTOR = /^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+(?:#[A-Za-z][A-Za-z0-9_]*)?$/;
const LOCAL_NAME = /^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;
const VARIANT_NAME = /^[A-Z][A-Za-z0-9]*$/;
const MAX_EXPRESSION_DEPTH = 16;

export type ScalarName = "String" | "Bool" | "UInt64";

export type TypedType =
  | Readonly<{ kind: "scalar"; name: ScalarName }>
  | Readonly<{ kind: "named"; selector: string }>
  | Readonly<{ kind: "set"; element: TypedType }>
  | Readonly<{ kind: "list"; element: TypedType }>
  | Readonly<{ kind: "optional"; element: TypedType }>
  | Readonly<{ kind: "sum"; variants: readonly TypedVariant[] }>;

export interface TypedVariant {
  readonly ontology_variant: string;
  readonly name: string;
  readonly payload: TypedType | null;
}

export interface TypedProperty {
  readonly ontology_property: string;
  readonly name: string;
  readonly type: TypedType;
  readonly cardinality: "one" | "optional" | "many" | "many-unique";
  readonly identity: boolean;
  readonly meaning: string;
}

export interface TypedRecordContract {
  readonly schema_version: "domainspec.typed-record/v1";
  readonly ontology_node: string;
  readonly properties: readonly TypedProperty[];
}

export interface TypedSumContract {
  readonly schema_version: "domainspec.typed-sum/v1";
  readonly ontology_node: string;
  readonly variants: readonly TypedVariant[];
}

export type ValueExpression =
  | Readonly<{ op: "literal"; type: ScalarName; value: string | boolean | number }>
  | Readonly<{ op: "variant"; selector: string }>
  | Readonly<{ op: "to_set"; value: ValueExpression }>
  | Readonly<{ op: "path"; root: string; properties: readonly string[] }>;

export type RuleExpression =
  | Readonly<{ op: "all" | "any"; terms: readonly RuleExpression[] }>
  | Readonly<{ op: "not"; term: RuleExpression }>
  | Readonly<{ op: "eq" | "lt"; left: ValueExpression; right: ValueExpression }>
  | Readonly<{ op: "exactly_one" | "unique" | "exists"; binding: string; collection: ValueExpression; where: RuleExpression }>
  | Readonly<{ op: "set_equal" | "contains"; left: ValueExpression; right: ValueExpression }>
  | Readonly<{ op: "rule_ref"; selector: string; arguments: readonly TypedRuleArgument[] }>;

export interface TypedRuleArgument {
  readonly parameter: string;
  readonly value: ValueExpression;
}

export interface TypedParameter {
  readonly name: string;
  readonly type: TypedType;
}

export interface TypedRuleContract {
  readonly schema_version: "domainspec.typed-rule/v1";
  readonly ontology_rule: string;
  readonly parameters: readonly TypedParameter[];
  readonly expression: RuleExpression;
}

export interface TypedOperationContract {
  readonly schema_version: "domainspec.typed-operation/v1";
  readonly ontology_operation: string;
  readonly inputs: readonly TypedParameter[];
  readonly output: TypedType;
  readonly guard: string;
  readonly reads: readonly string[];
  readonly writes: readonly string[];
  readonly effects: readonly string[];
  readonly failure_continuation: string;
  readonly success_result: TypedResultConstructor;
  readonly failure_result: TypedResultConstructor;
}

export interface TypedNestedVariantResultConstructor {
  readonly variant: string;
  readonly payload_variant: string | null;
}

export interface TypedValueResultConstructor {
  readonly variant: string;
  readonly payload: ValueExpression | null;
}

export type TypedResultConstructor = TypedNestedVariantResultConstructor | TypedValueResultConstructor;

export class TypedContractError extends Error {
  readonly exitCode = 22;

  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "TypedContractError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new TypedContractError(code, pointer, message);
}

function isObject(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function exactKeys(value: unknown, expected: readonly string[], pointer: string): asserts value is Record<string, unknown> {
  if (!isObject(value)) fail("MTCLI_TYPED_SCHEMA", pointer, "expected object");
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (JSON.stringify(actual) !== JSON.stringify(wanted)) fail("MTCLI_TYPED_SCHEMA", pointer, "unexpected or missing member");
}

function string(value: unknown, pointer: string): string {
  if (typeof value !== "string" || value.length === 0) fail("MTCLI_TYPED_SCHEMA", pointer, "expected nonempty string");
  return value;
}

function localName(value: unknown, pointer: string): string {
  const result = string(value, pointer);
  if (!LOCAL_NAME.test(result)) fail("MTCLI_TYPED_NAME", pointer, "expected lower snake-case name");
  return result;
}

function ontologySelector(value: unknown, pointer: string, propertyRequired = false): string {
  const result = string(value, pointer);
  if (!ONTOLOGY_SELECTOR.test(result) || (propertyRequired && !result.includes("#"))) {
    fail("MTCLI_TYPED_ONTOLOGY_SELECTOR", pointer, propertyRequired ? "expected ontology property selector" : "expected ontology selector");
  }
  return result;
}

function nodeSelector(value: unknown, pointer: string): string {
  const result = string(value, pointer);
  if (!NODE_SELECTOR.test(result)) fail("MTCLI_TYPED_NODE_SELECTOR", pointer, "expected feature-id:node-id selector");
  return result;
}

function unique<T>(values: readonly T[], key: (value: T) => string, pointer: string): void {
  const seen = new Set<string>();
  for (const value of values) {
    const identity = key(value);
    if (seen.has(identity)) fail("MTCLI_TYPED_DUPLICATE", pointer, `duplicate member:${identity}`);
    seen.add(identity);
  }
}

export function decodeTypedType(value: unknown, pointer = "/type", depth = 0): TypedType {
  if (depth > MAX_EXPRESSION_DEPTH) fail("MTCLI_TYPED_DEPTH", pointer, "type nesting exceeds maximum depth");
  if (!isObject(value) || typeof value.kind !== "string") fail("MTCLI_TYPED_TYPE", pointer, "typed value requires a kind");
  if (value.kind === "scalar") {
    exactKeys(value, ["kind", "name"], pointer);
    if (!["String", "Bool", "UInt64"].includes(String(value.name))) fail("MTCLI_TYPED_TYPE", `${pointer}/name`, "unsupported scalar");
    return Object.freeze({ kind: "scalar", name: value.name as ScalarName });
  }
  if (value.kind === "named") {
    exactKeys(value, ["kind", "selector"], pointer);
    return Object.freeze({ kind: "named", selector: nodeSelector(value.selector, `${pointer}/selector`) });
  }
  if (value.kind === "set" || value.kind === "list" || value.kind === "optional") {
    exactKeys(value, ["kind", "element"], pointer);
    const element = decodeTypedType(value.element, `${pointer}/element`, depth + 1);
    if (element.kind === "optional") fail("MTCLI_TYPED_TYPE", `${pointer}/element`, "nested optional is unsupported");
    return Object.freeze({ kind: value.kind, element });
  }
  if (value.kind === "sum") {
    exactKeys(value, ["kind", "variants"], pointer);
    if (!Array.isArray(value.variants) || value.variants.length === 0) fail("MTCLI_TYPED_TYPE", `${pointer}/variants`, "sum requires variants");
    const variants = value.variants.map((entry, index): TypedVariant => {
      const itemPointer = `${pointer}/variants/${index}`;
      exactKeys(entry, ["ontology_variant", "name", "payload"], itemPointer);
      const name = string(entry.name, `${itemPointer}/name`);
      if (!VARIANT_NAME.test(name)) fail("MTCLI_TYPED_NAME", `${itemPointer}/name`, "expected PascalCase variant name");
      return Object.freeze({
        ontology_variant: ontologySelector(entry.ontology_variant, `${itemPointer}/ontology_variant`, true),
        name,
        payload: entry.payload === null ? null : decodeTypedType(entry.payload, `${itemPointer}/payload`, depth + 1),
      });
    });
    unique(variants, (variant) => variant.name, `${pointer}/variants`);
    unique(variants, (variant) => variant.ontology_variant, `${pointer}/variants`);
    return Object.freeze({ kind: "sum", variants: Object.freeze(variants) });
  }
  fail("MTCLI_TYPED_TYPE", `${pointer}/kind`, `unsupported type constructor:${value.kind}`);
}

export function decodeTypedProperty(value: unknown, pointer = "/property"): TypedProperty {
  exactKeys(value, ["ontology_property", "name", "type", "cardinality", "identity", "meaning"], pointer);
  const type = decodeTypedType(value.type, `${pointer}/type`);
  if (!["one", "optional", "many", "many-unique"].includes(String(value.cardinality))) fail("MTCLI_TYPED_CARDINALITY", `${pointer}/cardinality`, "unsupported cardinality");
  const cardinality = value.cardinality as TypedProperty["cardinality"];
  if ((cardinality === "optional") !== (type.kind === "optional")) fail("MTCLI_TYPED_CARDINALITY", pointer, "Optional type and optional cardinality must agree");
  if ((cardinality === "many-unique") !== (type.kind === "set")) fail("MTCLI_TYPED_CARDINALITY", pointer, "Set type and many-unique cardinality must agree");
  if ((cardinality === "many") !== (type.kind === "list")) fail("MTCLI_TYPED_CARDINALITY", pointer, "List type and many cardinality must agree");
  if (typeof value.identity !== "boolean") fail("MTCLI_TYPED_SCHEMA", `${pointer}/identity`, "identity must be Boolean");
  if (value.identity && cardinality !== "one") fail("MTCLI_TYPED_IDENTITY", pointer, "identity property must have one cardinality");
  return Object.freeze({
    ontology_property: ontologySelector(value.ontology_property, `${pointer}/ontology_property`, true),
    name: localName(value.name, `${pointer}/name`),
    type,
    cardinality,
    identity: value.identity,
    meaning: string(value.meaning, `${pointer}/meaning`),
  });
}

export function decodeTypedRecordContract(value: unknown, pointer = "/typed_contract"): TypedRecordContract {
  exactKeys(value, ["schema_version", "ontology_node", "properties"], pointer);
  if (value.schema_version !== "domainspec.typed-record/v1") fail("MTCLI_TYPED_SCHEMA", `${pointer}/schema_version`, "unsupported typed record schema");
  if (!Array.isArray(value.properties) || value.properties.length === 0) fail("MTCLI_TYPED_SCHEMA", `${pointer}/properties`, "record requires properties");
  const properties = value.properties.map((entry, index) => decodeTypedProperty(entry, `${pointer}/properties/${index}`));
  unique(properties, (property) => property.name, `${pointer}/properties`);
  unique(properties, (property) => property.ontology_property, `${pointer}/properties`);
  return Object.freeze({
    schema_version: "domainspec.typed-record/v1",
    ontology_node: ontologySelector(value.ontology_node, `${pointer}/ontology_node`),
    properties: Object.freeze(properties),
  });
}

export function decodeTypedSumContract(value: unknown, pointer = "/typed_contract"): TypedSumContract {
  exactKeys(value, ["schema_version", "ontology_node", "variants"], pointer);
  if (value.schema_version !== "domainspec.typed-sum/v1") fail("MTCLI_TYPED_SCHEMA", `${pointer}/schema_version`, "unsupported typed sum schema");
  const decoded = decodeTypedType({ kind: "sum", variants: value.variants }, `${pointer}/sum`);
  if (decoded.kind !== "sum") fail("MTCLI_TYPED_TYPE", pointer, "typed sum did not decode as sum");
  return Object.freeze({
    schema_version: "domainspec.typed-sum/v1",
    ontology_node: ontologySelector(value.ontology_node, `${pointer}/ontology_node`),
    variants: decoded.variants,
  });
}

function decodeValueExpression(value: unknown, pointer: string): ValueExpression {
  if (!isObject(value) || typeof value.op !== "string") fail("MTCLI_TYPED_RULE", pointer, "value expression requires op");
  if (value.op === "literal") {
    exactKeys(value, ["op", "type", "value"], pointer);
    if (!["String", "Bool", "UInt64"].includes(String(value.type))) fail("MTCLI_TYPED_RULE", `${pointer}/type`, "unsupported literal type");
    const type = value.type as ScalarName;
    const valid = type === "String"
      ? typeof value.value === "string"
      : type === "Bool"
        ? typeof value.value === "boolean"
        : Number.isSafeInteger(value.value) && Number(value.value) >= 0;
    if (!valid) fail("MTCLI_TYPED_RULE", `${pointer}/value`, "literal does not match its scalar type");
    return Object.freeze({ op: "literal", type, value: value.value as string | boolean | number });
  }
  if (value.op === "path") {
    exactKeys(value, ["op", "root", "properties"], pointer);
    if (!Array.isArray(value.properties)) fail("MTCLI_TYPED_RULE", `${pointer}/properties`, "path requires a property-selector array");
    const properties = value.properties.map((entry, index) => ontologySelector(entry, `${pointer}/properties/${index}`, true));
    return Object.freeze({ op: "path", root: localName(value.root, `${pointer}/root`), properties: Object.freeze(properties) });
  }
  if (value.op === "variant") {
    exactKeys(value, ["op", "selector"], pointer);
    return Object.freeze({ op: "variant", selector: ontologySelector(value.selector, `${pointer}/selector`, true) });
  }
  if (value.op === "to_set") {
    exactKeys(value, ["op", "value"], pointer);
    return Object.freeze({ op: "to_set", value: decodeValueExpression(value.value, `${pointer}/value`) });
  }
  fail("MTCLI_TYPED_RULE", `${pointer}/op`, `unsupported value operator:${value.op}`);
}

export function decodeRuleExpression(value: unknown, pointer = "/expression", depth = 0): RuleExpression {
  if (depth > MAX_EXPRESSION_DEPTH) fail("MTCLI_TYPED_DEPTH", pointer, "rule nesting exceeds maximum depth");
  if (!isObject(value) || typeof value.op !== "string") fail("MTCLI_TYPED_RULE", pointer, "rule expression requires op");
  if (value.op === "all" || value.op === "any") {
    exactKeys(value, ["op", "terms"], pointer);
    if (!Array.isArray(value.terms) || value.terms.length === 0) fail("MTCLI_TYPED_RULE", `${pointer}/terms`, `${value.op} requires terms`);
    return Object.freeze({ op: value.op, terms: Object.freeze(value.terms.map((term, index) => decodeRuleExpression(term, `${pointer}/terms/${index}`, depth + 1))) });
  }
  if (value.op === "not") {
    exactKeys(value, ["op", "term"], pointer);
    return Object.freeze({ op: "not", term: decodeRuleExpression(value.term, `${pointer}/term`, depth + 1) });
  }
  if (value.op === "eq" || value.op === "lt" || value.op === "set_equal" || value.op === "contains") {
    exactKeys(value, ["op", "left", "right"], pointer);
    return Object.freeze({ op: value.op, left: decodeValueExpression(value.left, `${pointer}/left`), right: decodeValueExpression(value.right, `${pointer}/right`) });
  }
  if (value.op === "exactly_one" || value.op === "unique" || value.op === "exists") {
    exactKeys(value, ["op", "binding", "collection", "where"], pointer);
    return Object.freeze({ op: value.op, binding: localName(value.binding, `${pointer}/binding`), collection: decodeValueExpression(value.collection, `${pointer}/collection`), where: decodeRuleExpression(value.where, `${pointer}/where`, depth + 1) });
  }
  if (value.op === "rule_ref") {
    exactKeys(value, ["op", "selector", "arguments"], pointer);
    if (!Array.isArray(value.arguments)) fail("MTCLI_TYPED_RULE", `${pointer}/arguments`, "Rule reference requires an argument array");
    const arguments_ = value.arguments.map((entry, index): TypedRuleArgument => {
      const argumentPointer = `${pointer}/arguments/${index}`;
      exactKeys(entry, ["parameter", "value"], argumentPointer);
      return Object.freeze({
        parameter: localName(entry.parameter, `${argumentPointer}/parameter`),
        value: decodeValueExpression(entry.value, `${argumentPointer}/value`),
      });
    });
    unique(arguments_, (argument) => argument.parameter, `${pointer}/arguments`);
    return Object.freeze({ op: "rule_ref", selector: nodeSelector(value.selector, `${pointer}/selector`), arguments: Object.freeze(arguments_) });
  }
  fail("MTCLI_TYPED_RULE", `${pointer}/op`, `unsupported rule operator:${value.op}`);
}

function decodeParameters(value: unknown, pointer: string): readonly TypedParameter[] {
  if (!Array.isArray(value) || value.length === 0) fail("MTCLI_TYPED_SCHEMA", pointer, "expected nonempty parameter array");
  const parameters = value.map((entry, index): TypedParameter => {
    const itemPointer = `${pointer}/${index}`;
    exactKeys(entry, ["name", "type"], itemPointer);
    return Object.freeze({ name: localName(entry.name, `${itemPointer}/name`), type: decodeTypedType(entry.type, `${itemPointer}/type`) });
  });
  unique(parameters, (parameter) => parameter.name, pointer);
  return Object.freeze(parameters);
}

export function decodeTypedRuleContract(value: unknown, pointer = "/typed_contract"): TypedRuleContract {
  exactKeys(value, ["schema_version", "ontology_rule", "parameters", "expression"], pointer);
  if (value.schema_version !== "domainspec.typed-rule/v1") fail("MTCLI_TYPED_SCHEMA", `${pointer}/schema_version`, "unsupported typed Rule schema");
  return Object.freeze({
    schema_version: "domainspec.typed-rule/v1",
    ontology_rule: ontologySelector(value.ontology_rule, `${pointer}/ontology_rule`),
    parameters: decodeParameters(value.parameters, `${pointer}/parameters`),
    expression: decodeRuleExpression(value.expression, `${pointer}/expression`),
  });
}

function stringSet(value: unknown, pointer: string, nodeSelectors: boolean): readonly string[] {
  if (!Array.isArray(value)) fail("MTCLI_TYPED_SCHEMA", pointer, "expected array");
  const values = value.map((entry, index) => nodeSelectors ? nodeSelector(entry, `${pointer}/${index}`) : string(entry, `${pointer}/${index}`));
  unique(values, (entry) => entry, pointer);
  return Object.freeze(values);
}

export function decodeTypedOperationContract(value: unknown, pointer = "/typed_contract"): TypedOperationContract {
  exactKeys(value, ["schema_version", "ontology_operation", "inputs", "output", "guard", "reads", "writes", "effects", "failure_continuation", "success_result", "failure_result"], pointer);
  if (value.schema_version !== "domainspec.typed-operation/v1") fail("MTCLI_TYPED_SCHEMA", `${pointer}/schema_version`, "unsupported typed Operation schema");
  return Object.freeze({
    schema_version: "domainspec.typed-operation/v1",
    ontology_operation: ontologySelector(value.ontology_operation, `${pointer}/ontology_operation`),
    inputs: decodeParameters(value.inputs, `${pointer}/inputs`),
    output: decodeTypedType(value.output, `${pointer}/output`),
    guard: nodeSelector(value.guard, `${pointer}/guard`),
    reads: stringSet(value.reads, `${pointer}/reads`, true),
    writes: stringSet(value.writes, `${pointer}/writes`, true),
    effects: stringSet(value.effects, `${pointer}/effects`, true),
    failure_continuation: string(value.failure_continuation, `${pointer}/failure_continuation`),
    success_result: decodeResultConstructor(value.success_result, `${pointer}/success_result`),
    failure_result: decodeResultConstructor(value.failure_result, `${pointer}/failure_result`),
  });
}

function decodeResultConstructor(value: unknown, pointer: string): TypedResultConstructor {
  if (!isObject(value)) fail("MTCLI_TYPED_SCHEMA", pointer, "expected object");
  const valueForm = Object.hasOwn(value, "payload");
  exactKeys(value, valueForm ? ["variant", "payload"] : ["variant", "payload_variant"], pointer);
  const variant = string(value.variant, `${pointer}/variant`);
  if (!VARIANT_NAME.test(variant)) fail("MTCLI_TYPED_NAME", `${pointer}/variant`, "expected PascalCase variant name");
  if (valueForm) {
    return Object.freeze({
      variant,
      payload: value.payload === null ? null : decodeValueExpression(value.payload, `${pointer}/payload`),
    });
  }
  let payloadVariant: string | null = null;
  if (value.payload_variant !== null) {
    payloadVariant = string(value.payload_variant, `${pointer}/payload_variant`);
    if (!VARIANT_NAME.test(payloadVariant)) fail("MTCLI_TYPED_NAME", `${pointer}/payload_variant`, "expected PascalCase payload variant name");
  }
  return Object.freeze({ variant, payload_variant: payloadVariant });
}
