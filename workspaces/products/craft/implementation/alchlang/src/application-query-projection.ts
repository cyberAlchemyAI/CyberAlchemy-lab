import { CompilationRejected } from "./model.js";
import { digest, json } from "./domainspec-profile.js";
import type { lowerApplicationDomain } from "./application-domain-lowering.js";

type Obj = Record<string, unknown>;
type Path = { op: "path"; root: string; properties: string[] };
type Shape = {
  query_ref: string; ontology_query: string;
  inputs: { name: string; type: Obj }[];
  source: { parameter: string; selector: string };
  output: { kind: string };
  rule_ref: string;
  bindings: { parameter: string; value: Path; type: Obj; source_line: number }[];
};
const fail = (code: string, path: string, message: string): never => {
  throw new CompilationRejected([{ code, path, message }]);
};

/** Substitute checked Rule arguments into the existing bounded Query contract.
 * This is a compiler projection, not a second proposition language or evaluator.
 * Inputs are the current formation and Rule files produced in this lowering run.
 */
export function projectApplicationQueries(formation: ReturnType<typeof lowerApplicationDomain>, projectFiles: Record<string, string>) {
  const projections: Obj[] = [];
  const nodePath = (selector: string) => {
    const [feature, id] = selector.split(":");
    return `specs/${feature}/nodes/${id}.json`;
  };
  for (const untyped of formation.queryShapes.queries) {
    const shape = untyped as unknown as Shape;
    const at = `$queries/${shape.query_ref}`;
    const rulePath = nodePath(shape.rule_ref);
    const ruleBytes = projectFiles[rulePath];
    if (!ruleBytes) fail("APPLICATION_QUERY_RULE", at, "projected Rule is missing");
    const rule = JSON.parse(ruleBytes!).body.typed_contract;
    if (rule?.schema_version !== "domainspec.typed-rule/v2") fail("APPLICATION_QUERY_RULE", at, "Query requires the exact typed Rule projection");
    const parameters = rule.parameters as { name: string; type: Obj }[];
    const names = shape.bindings.map(b => b.parameter).sort();
    if (json(names) !== json(parameters.map(p => p.name).sort())) {
      fail("APPLICATION_QUERY_ARGUMENTS", at, "Query arguments must cover the selected Rule parameters exactly");
    }
    for (const parameter of parameters) {
      const binding = shape.bindings.find(b => b.parameter === parameter.name)!;
      if (json(binding.type) !== json(parameter.type)) fail("APPLICATION_QUERY_ARGUMENT_TYPE", `$line:${binding.source_line}`, "Query argument type differs from the selected Rule parameter");
    }
    const source = JSON.parse(projectFiles[nodePath(shape.source.selector)]!).body.typed_contract;
    const fields = source.properties as { name: string; ontology_property: string; type: Obj }[];
    const value = (expression: Obj): Obj => {
      if (expression.op === "literal") return { kind: "literal", type: expression.type, value: expression.value };
      if (expression.op !== "path") return fail("APPLICATION_QUERY_FILTER_UNSUPPORTED", at, "Rule value has no exact bounded Query representation");
      const binding = shape.bindings.find(b => b.parameter === expression.root);
      if (!binding) return fail("APPLICATION_QUERY_ARGUMENTS", at, "Rule path has no explicit argument binding");
      const properties = [...binding.value.properties, ...(expression.properties as string[])];
      if (binding.value.root === shape.source.parameter) {
        if (properties.length !== 1) return fail("APPLICATION_QUERY_FILTER_UNSUPPORTED", at, "backend Query requires one exact source field; no whole-row or nested-path coercion");
        const field = fields.find(f => f.ontology_property === properties[0]);
        if (!field) return fail("APPLICATION_QUERY_FILTER_UNSUPPORTED", at, "bound ontology property is not a source field");
        return { kind: "field", name: field.name };
      }
      if (properties.length || !shape.inputs.some(p => p.name === binding.value.root)) {
        return fail("APPLICATION_QUERY_FILTER_UNSUPPORTED", at, "backend Query requires an explicit whole input; no implicit input-property extraction");
      }
      return { kind: "parameter", name: binding.value.root };
    };
    let count = 0;
    const predicate = (expression: Obj): Obj => {
      if (++count > 1024) return fail("APPLICATION_QUERY_FILTER_LIMIT", at, "Query projection exceeds the Rule projection bound");
      if (expression.op === "eq") return { op: "eq", left: value(expression.left as Obj), right: value(expression.right as Obj) };
      if (expression.op === "not") return { op: "not", term: predicate(expression.term as Obj) };
      if (expression.op === "all" || expression.op === "any") return { op: expression.op, terms: (expression.terms as Obj[]).map(predicate) };
      return fail("APPLICATION_QUERY_FILTER_UNSUPPORTED", at, "Rule predicate has no exact bounded Query representation");
    };
    const filter = predicate(rule.expression);
    if (shape.output.kind !== "list" && shape.output.kind !== "optional") fail("APPLICATION_QUERY_CARDINALITY", at, "explicit list or optional result required");
    const targetPath = nodePath(shape.query_ref);
    const node = JSON.parse(projectFiles[targetPath]!);
    node.body.typed_contract = { ...(shape.output.kind === "optional"
      ? { schema_version: "domainspec.typed-query/v2", result_cardinality: "optional" }
      : { schema_version: "domainspec.typed-query/v1" }), ontology_query: shape.ontology_query,
      source: shape.source.selector, inputs: shape.inputs, filter,
      projection: fields.map(f => f.name), order_by: null, limit: null };
    projectFiles[targetPath] = json(node);
    projections.push({ query_ref: shape.query_ref, rule_ref: shape.rule_ref, rule_path: rulePath,
      rule_sha256: digest(ruleBytes!), query_shape_sha256: digest(json(shape)),
      target_path: targetPath, target_sha256: digest(projectFiles[targetPath]!),
      output: shape.output, preservation: "exact-argument-substitution-under-selected-rule-interpretation",
      authority_effect: "none" });
  }
  return projections;
}
