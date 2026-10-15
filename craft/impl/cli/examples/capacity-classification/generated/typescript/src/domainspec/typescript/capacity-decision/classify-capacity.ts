// domainspec-meta: {"baseline_digest":"bfbc335d151ab8b29150dc95f246c2bc0954cff179ece5ce51222b2d1455abda","baseline_id":"domainspec-meta-types-current-implemented@10","binding_sha256":"a535cadb3cb9318e7058ee00d9d244d7e4def98cbd5bb79da13b169819180a32","language":"typescript","meta_type_id":"DS-D1.6","meta_type_label":"Calculation","provider_sha256":"3be262ce45616155de67ec6754527bc2227dc973e21823550dc889d1745ccadd","source_sha256":"c5f4cb0f65e59ef1d1e5290e7ff768fe38bbee90f4d82795a8bb3ee87a4111af"}
// domainspec-body: {"description":"Classify a supplied snapshot: Accept when requested units are strictly below available units; otherwise Reject. This pure derivation reserves no capacity.","inputs":["snapshot"],"typed_contract":{"expression":{"condition":{"arguments":[{"parameter":"snapshot","value":{"op":"path","properties":[],"root":"snapshot"}}],"op":"rule_ref","selector":"capacity-decision:within-capacity"},"else":{"payload":null,"variant":"Reject"},"op":"if","then":{"payload":null,"variant":"Accept"}},"inputs":[{"name":"snapshot","type":{"kind":"named","selector":"capacity-decision:capacity-snapshot"}}],"ontology_calculation":"CAPACITY-CALC-CLASSIFY","result":{"kind":"named","selector":"capacity-decision:capacity-decision"},"schema_version":"domainspec.typed-calculation/v2"}}
// domainspec-relationships: []
// domainspec-calculation-semantics: "domainspec.typed-calculation/v2"
// domainspec-typed-closure-sha256: "05dbda85a04b79e541da93324fdecd6dc0b8590417b88c805b1ac4116b97a41c"
const domainspecRuleRoot = "capacity-decision:classify-capacity";
const domainspecRuleProperties: Readonly<Record<string, string>> = Object.freeze({"CAPACITY-SNAPSHOT#available_units":"available_units","CAPACITY-SNAPSHOT#request_id":"request_id","CAPACITY-SNAPSHOT#requested_units":"requested_units"});
const domainspecRuleContracts: Readonly<Record<string, any>> = Object.freeze({"capacity-decision:within-capacity":{"expression":{"left":{"op":"path","properties":["CAPACITY-SNAPSHOT#requested_units"],"root":"snapshot"},"op":"lt","right":{"op":"path","properties":["CAPACITY-SNAPSHOT#available_units"],"root":"snapshot"}},"ontology_rule":"CAPACITY-RULE-WITHIN-AVAILABLE","parameters":[{"name":"snapshot","type":{"kind":"named","selector":"capacity-decision:capacity-snapshot"}}],"schema_version":"domainspec.typed-rule/v1"}});
function domainspecStable(value: unknown): string {
  if (value instanceof Set) return JSON.stringify([...value].map(domainspecStable).sort());
  if (Array.isArray(value)) return JSON.stringify(value.map(domainspecStable));
  if (value !== null && typeof value === "object") return JSON.stringify(Object.fromEntries(Object.entries(value as Record<string, unknown>).sort(([left], [right]) => left.localeCompare(right)).map(([key, child]) => [key, domainspecStable(child)])));
  return JSON.stringify(value) ?? "undefined";
}
function domainspecValue(expression: any, environment: Readonly<Record<string, unknown>>): any {
  if (expression.op === "literal") return expression.value;
  if (expression.op === "variant") return expression.selector;
  if (expression.op === "to_set") return new Set((domainspecValue(expression.value, environment) as readonly unknown[]).map(domainspecStable));
  let current: any = environment[expression.root];
  for (const property of expression.properties as readonly string[]) {
    const field = domainspecRuleProperties[property];
    if (field === undefined) throw new Error("unresolved Rule property:" + property);
    current = Array.isArray(current) ? current.map((entry) => entry?.[field]) : current?.[field];
  }
  return current;
}
function domainspecEqual(left: unknown, right: unknown): boolean { return domainspecStable(left) === domainspecStable(right); }
function domainspecCollection(value: unknown): readonly unknown[] { return value instanceof Set ? [...value] : Array.isArray(value) ? value : (() => { throw new Error("Rule quantifier requires a collection"); })(); }
function domainspecEvaluateExpression(expression: any, environment: Readonly<Record<string, unknown>>): boolean {
  if (expression.op === "all" || expression.op === "any") return expression.op === "all" ? expression.terms.every((term: any) => domainspecEvaluateExpression(term, environment)) : expression.terms.some((term: any) => domainspecEvaluateExpression(term, environment));
  if (expression.op === "not") return !domainspecEvaluateExpression(expression.term, environment);
  if (["eq", "lt", "set_equal", "contains"].includes(expression.op)) {
    const left = domainspecValue(expression.left, environment); const right = domainspecValue(expression.right, environment);
    if (expression.op === "lt") return typeof left === "number" && typeof right === "number" && left < right;
    if (expression.op === "contains") return (left instanceof Set && left.has(domainspecStable(right))) || (Array.isArray(left) && left.some((entry) => domainspecEqual(entry, right)));
    return domainspecEqual(left, right);
  }
  if (["exactly_one", "exists", "unique"].includes(expression.op)) {
    const values = domainspecCollection(domainspecValue(expression.collection, environment));
    if (expression.op === "unique") return new Set(values.map((value) => domainspecStable(domainspecValue(expression.where.left, { ...environment, [expression.binding]: value })))).size === values.length;
    const matches = values.filter((value) => domainspecEvaluateExpression(expression.where, { ...environment, [expression.binding]: value })).length;
    return expression.op === "exactly_one" ? matches === 1 : matches > 0;
  }
  if (expression.op === "rule_ref") return domainspecEvaluate(expression.selector, Object.fromEntries(expression.arguments.map((argument: any) => [argument.parameter, domainspecValue(argument.value, environment)])));
  throw new Error("unsupported Rule operator:" + String(expression.op));
}
function domainspecEvaluate(selector: string, environment: Readonly<Record<string, unknown>>): boolean {
  const contract = domainspecRuleContracts[selector];
  if (contract === undefined) throw new Error("unresolved Rule reference:" + selector);
  if (!contract.parameters.every((parameter: any) => Object.hasOwn(environment, parameter.name))) throw new Error("missing Rule parameter:" + selector);
  return domainspecEvaluateExpression(contract.expression, environment);
}
const domainspecCalculationTypes: any = {"inputs":[{"name":"snapshot","type":{"kind":"named","selector":"capacity-decision:capacity-snapshot"}}],"types":{"capacity-decision:capacity-decision":{"ontology_node":"CAPACITY-DECISION","schema_version":"domainspec.typed-sum/v1","variants":[{"name":"Accept","ontology_variant":"CAPACITY-DECISION#Accept","payload":null},{"name":"Reject","ontology_variant":"CAPACITY-DECISION#Reject","payload":null}]},"capacity-decision:capacity-snapshot":{"ontology_node":"CAPACITY-SNAPSHOT","properties":[{"cardinality":"one","identity":true,"meaning":"Stable identity of the capacity request.","name":"request_id","ontology_property":"CAPACITY-SNAPSHOT#request_id","type":{"kind":"scalar","name":"String"}},{"cardinality":"one","identity":false,"meaning":"Units requested by the operation.","name":"requested_units","ontology_property":"CAPACITY-SNAPSHOT#requested_units","type":{"kind":"scalar","name":"UInt64"}},{"cardinality":"one","identity":false,"meaning":"Units available at the decision boundary.","name":"available_units","ontology_property":"CAPACITY-SNAPSHOT#available_units","type":{"kind":"scalar","name":"UInt64"}}],"schema_version":"domainspec.typed-record/v1"},"capacity-decision:classify-capacity":{"expression":{"condition":{"arguments":[{"parameter":"snapshot","value":{"op":"path","properties":[],"root":"snapshot"}}],"op":"rule_ref","selector":"capacity-decision:within-capacity"},"else":{"payload":null,"variant":"Reject"},"op":"if","then":{"payload":null,"variant":"Accept"}},"inputs":[{"name":"snapshot","type":{"kind":"named","selector":"capacity-decision:capacity-snapshot"}}],"ontology_calculation":"CAPACITY-CALC-CLASSIFY","result":{"kind":"named","selector":"capacity-decision:capacity-decision"},"schema_version":"domainspec.typed-calculation/v2"},"capacity-decision:within-capacity":{"expression":{"left":{"op":"path","properties":["CAPACITY-SNAPSHOT#requested_units"],"root":"snapshot"},"op":"lt","right":{"op":"path","properties":["CAPACITY-SNAPSHOT#available_units"],"root":"snapshot"}},"ontology_rule":"CAPACITY-RULE-WITHIN-AVAILABLE","parameters":[{"name":"snapshot","type":{"kind":"named","selector":"capacity-decision:capacity-snapshot"}}],"schema_version":"domainspec.typed-rule/v1"}}};
function domainspecValidateCalculationValue(type: any, value: any): void {
  if (type.kind === "scalar") {
    const valid = type.name === "String" ? typeof value === "string" : type.name === "Bool" ? typeof value === "boolean" : Number.isSafeInteger(value) && value >= 0;
    if (!valid) throw new Error("invalid Calculation scalar:" + type.name);
    return;
  }
  if (type.kind === "optional" && value === null) return;
  if (type.kind === "optional") return domainspecValidateCalculationValue(type.element, value);
  if (type.kind === "list" || type.kind === "set") {
    if (!Array.isArray(value)) throw new Error("Calculation collection requires an array");
    if (type.kind === "set" && new Set(value.map(domainspecStable)).size !== value.length) throw new Error("duplicate Calculation set member");
    value.forEach((child: any) => domainspecValidateCalculationValue(type.element, child)); return;
  }
  const contract = type.kind === "named" ? domainspecCalculationTypes.types[type.selector] : type;
  if (value === null || typeof value !== "object" || Array.isArray(value) || !contract) throw new Error("invalid Calculation named value");
  if (contract.schema_version === "domainspec.typed-record/v1") {
    const names = contract.properties.map((property: any) => property.name).sort();
    if (JSON.stringify(Object.keys(value).sort()) !== JSON.stringify(names)) throw new Error("Calculation record fields must match the contract");
    contract.properties.forEach((property: any) => domainspecValidateCalculationValue(property.type, value[property.name])); return;
  }
  const variant = contract.variants?.find((candidate: any) => candidate.name === value.variant);
  if (!variant || JSON.stringify(Object.keys(value).sort()) !== JSON.stringify(["payload", "variant"])) throw new Error("invalid Calculation variant");
  if (variant.payload === null) { if (value.payload !== null) throw new Error("unexpected Calculation variant payload"); }
  else domainspecValidateCalculationValue(variant.payload, value.payload);
}
function domainspecValidateCalculationInputs(inputs: Readonly<Record<string, unknown>>): void {
  if (inputs === null || typeof inputs !== "object" || Array.isArray(inputs)) throw new Error("Calculation inputs require an object");
  const names = domainspecCalculationTypes.inputs.map((parameter: any) => parameter.name).sort();
  if (JSON.stringify(Object.keys(inputs).sort()) !== JSON.stringify(names)) throw new Error("Calculation inputs must match the contract");
  domainspecCalculationTypes.inputs.forEach((parameter: any) => domainspecValidateCalculationValue(parameter.type, inputs[parameter.name]));
}
export function classifyCapacity(inputs: Readonly<Record<string, unknown>>): Readonly<{ variant: string; payload: null }> {
  domainspecValidateCalculationInputs(inputs);
  const expression: any = {"condition":{"arguments":[{"parameter":"snapshot","value":{"op":"path","properties":[],"root":"snapshot"}}],"op":"rule_ref","selector":"capacity-decision:within-capacity"},"else":{"payload":null,"variant":"Reject"},"op":"if","then":{"payload":null,"variant":"Accept"}};
  const branch = domainspecEvaluateExpression(expression.condition, inputs) ? expression.then : expression.else;
  return Object.freeze({ variant: branch.variant, payload: null });
}
