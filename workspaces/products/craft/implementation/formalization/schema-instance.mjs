// Side-effect-free evaluator for the JSON Schema subset used by this package.
// Unsupported keywords must not be introduced into selected schemas silently.
const supported = new Set(["$schema", "$id", "title", "description", "type", "additionalProperties", "required", "properties", "$defs", "$ref", "const", "enum", "allOf", "anyOf", "oneOf", "not", "if", "then", "else", "minLength", "pattern", "minimum", "minItems", "uniqueItems", "items"]);

export function assertSupportedSchema(schema) {
  const visit = (node) => {
    if (!node || typeof node !== "object" || Array.isArray(node)) throw new Error("invalid schema node");
    for (const [key, value] of Object.entries(node)) {
      if (!supported.has(key)) throw new Error(`unsupported schema keyword: ${key}`);
      if (["properties", "$defs"].includes(key)) Object.values(value).forEach(visit);
      else if (["allOf", "anyOf", "oneOf"].includes(key)) value.forEach(visit);
      else if (["not", "if", "then", "else", "items"].includes(key)) visit(value);
      else if (key === "additionalProperties" && typeof value === "object") visit(value);
    }
  };
  visit(schema);
}

const jsonType = value => value === null ? "null" : Array.isArray(value) ? "array" : Number.isInteger(value) ? "integer" : typeof value;
const typeMatches = (value, type) => type === "number" ? typeof value === "number" : type === "object" ? value !== null && typeof value === "object" && !Array.isArray(value) : jsonType(value) === type;
const deepEqual = (a, b) => JSON.stringify(a) === JSON.stringify(b);
function resolveLocalRef(ref, root) {
  if (typeof ref !== "string" || !ref.startsWith("#/")) throw new Error(`unsupported schema reference: ${ref}`);
  return ref.slice(2).split("/").reduce((cursor, token) => {
    const key = token.replaceAll("~1", "/").replaceAll("~0", "~");
    if (cursor === undefined || !Object.hasOwn(cursor, key)) throw new Error(`unresolved schema reference: ${ref}`);
    return cursor[key];
  }, root);
}

export function validateSchemaInstance(instance, schema, root = schema, at = "$") {
  const errors = [];
  if (schema.$ref) return validateSchemaInstance(instance, resolveLocalRef(schema.$ref, root), root, at);
  for (const branch of schema.allOf ?? []) errors.push(...validateSchemaInstance(instance, branch, root, at));
  if (schema.anyOf && !schema.anyOf.some(branch => validateSchemaInstance(instance, branch, root, at).length === 0)) errors.push(`${at}: does not satisfy anyOf`);
  if (schema.oneOf) {
    const count = schema.oneOf.filter(branch => validateSchemaInstance(instance, branch, root, at).length === 0).length;
    if (count !== 1) errors.push(`${at}: satisfies ${count} oneOf branches instead of one`);
  }
  if (schema.not && validateSchemaInstance(instance, schema.not, root, at).length === 0) errors.push(`${at}: satisfies forbidden not schema`);
  if (schema.if) {
    const matched = validateSchemaInstance(instance, schema.if, root, at).length === 0;
    if (matched && schema.then) errors.push(...validateSchemaInstance(instance, schema.then, root, at));
    if (!matched && schema.else) errors.push(...validateSchemaInstance(instance, schema.else, root, at));
  }
  if (Object.hasOwn(schema, "const") && !deepEqual(instance, schema.const)) errors.push(`${at}: expected constant ${JSON.stringify(schema.const)}`);
  if (schema.enum && !schema.enum.some(value => deepEqual(instance, value))) errors.push(`${at}: value is outside enum`);
  if (schema.type) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!types.some(type => typeMatches(instance, type))) return [...errors, `${at}: expected type ${types.join("|")}, got ${jsonType(instance)}`];
  }
  if (typeof instance === "string") {
    if (schema.minLength !== undefined && instance.length < schema.minLength) errors.push(`${at}: shorter than minLength ${schema.minLength}`);
    if (schema.pattern && !new RegExp(schema.pattern).test(instance)) errors.push(`${at}: does not match ${schema.pattern}`);
  }
  if (typeof instance === "number" && schema.minimum !== undefined && instance < schema.minimum) errors.push(`${at}: lower than minimum ${schema.minimum}`);
  if (Array.isArray(instance)) {
    if (schema.minItems !== undefined && instance.length < schema.minItems) errors.push(`${at}: has fewer than ${schema.minItems} items`);
    if (schema.uniqueItems && new Set(instance.map(JSON.stringify)).size !== instance.length) errors.push(`${at}: items are not unique`);
    if (schema.items) instance.forEach((value, index) => errors.push(...validateSchemaInstance(value, schema.items, root, `${at}[${index}]`)));
  }
  if (instance !== null && typeof instance === "object" && !Array.isArray(instance)) {
    const props = schema.properties ?? {};
    for (const key of schema.required ?? []) if (!Object.hasOwn(instance, key)) errors.push(`${at}: missing required property ${key}`);
    for (const [key, value] of Object.entries(instance)) {
      if (Object.hasOwn(props, key)) errors.push(...validateSchemaInstance(value, props[key], root, `${at}.${key}`));
      else if (schema.additionalProperties === false) errors.push(`${at}: unexpected property ${key}`);
      else if (schema.additionalProperties && typeof schema.additionalProperties === "object") errors.push(...validateSchemaInstance(value, schema.additionalProperties, root, `${at}.${key}`));
    }
  }
  return errors;
}
