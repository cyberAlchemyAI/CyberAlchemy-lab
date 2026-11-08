import { CompilationRejected } from "./model.js";
import { digest, json, symbol } from "./domainspec-profile.js";
import type { ApplicationType, ApplicationPublicType } from "./application-source.js";
import type { RealizationArgument } from "./application-realization.js";
import type { lowerApplicationRuleProjections } from "./application-rule-projection.js";
import { compileApplicationRealizationGraph } from "./application-realization-graph.js";

type Type = { kind: "scalar"; name: string } | { kind: "named"; selector: string }
  | { kind: "event-input"; selector: string }
  | { kind: "contract"; interface_selector: string; contract_id: string }
  | { kind: "reference"; selector: string; projection: string[] }
  | { kind: "projection"; owner: { kind: "named"; selector: string }; fields: string[] }
  | { kind: "sum"; variants: Array<{ name: string; ontology_variant: string; payload: Type | null }> }
  | { kind: "optional" | "list" | "set"; element: Type };
interface Value { type: Type; value: { op: "path"; root: string; properties: string[] } }
const fail = (line: number, message: string): never => {
  throw new CompilationRejected([{ code: "APPLICATION_REALIZATION_TYPE", path: `$line:${line}`, message }]);
};

/** Resolve exact value connections, not construction, Query execution or FormalClaim proof. */
export function checkApplicationRealizationTypes(projection: ReturnType<typeof lowerApplicationRuleProjections>) {
  const { formation } = projection, model = formation.model;
  const selector = (id: string) => `${formation.feature}:${formation.symbols[id]}`;
  const declarations = new Map(model.declarations.map(d => [d.id, d]));
  const bySelector = new Map(model.declarations.map(d => [selector(d.id), d]));
  const node = (ref: string) => {
    const [feature, id] = ref.split(":");
    return JSON.parse(projection.projectFiles[`specs/${feature}/nodes/${id}.json`]!).body.typed_contract;
  };
  const type = (value: ApplicationType): Type => {
    if (value.kind === "scalar") return value;
    if (value.kind === "declaration") return { kind: "named", selector: selector(value.ref) };
    if (value.kind === "public-contract") return { kind: "contract", interface_selector: selector(value.interface), contract_id: symbol(value.contract) };
    if (value.kind === "reference") return { kind: "reference", selector: selector(value.entity), projection: [symbol(value.field, "_")] };
    if (value.kind === "sum") return node(selector(value.enum));
    return { kind: value.kind, element: type(value.element) };
  };
  const publicType = (value: ApplicationPublicType, owner: string): Type => {
    if (value.kind === "contract") return { kind: "contract", interface_selector: owner, contract_id: symbol(value.ref) };
    if (value.kind === "scalar" || value.kind === "declaration" || value.kind === "reference" || value.kind === "sum") return type(value);
    return { kind: value.kind, element: publicType(value.element, owner) };
  };
  const equal = (actual: Type, expected: Type, line: number) => {
    if (json(actual) !== json(expected)) fail(line, "connection types differ; no implicit cardinality, identity or structural conversion");
  };
  return (model.realizations ?? []).map(realization => {
    const operation = declarations.get(realization.operation)!;
    if (operation.kind !== "operation") return fail(realization.source_line, "expected Operation");
    const roots = new Map<string, Type>([[realization.input, type(operation.input)]]);
    for (const event of realization.event_inputs) roots.set(event.name, { kind: "event-input", selector: selector(event.event) });
    for (const read of realization.reads) roots.set(read.name, { kind: "named", selector: selector(read.entity) });
    for (const query of realization.queries) {
      const declaration = declarations.get(query.query)!;
      if (declaration.kind !== "query") return fail(query.source_line, "expected Query");
      const contract = node(selector(query.query));
      const source = node(selector(declaration.source.entity));
      const fields = contract?.projection;
      if (!Array.isArray(fields) || !fields.length || fields.some((field: unknown) => typeof field !== "string" || !source.properties.some((p: any) => p.name === field)) || new Set(fields).size !== fields.length) return fail(query.source_line, "Query projection must select distinct declared source fields");
      const owner = { kind: "named" as const, selector: selector(declaration.source.entity) };
      if (contract.source !== owner.selector) return fail(query.source_line, "Query source differs from its authored declaration");
      const element: Type = fields.length === source.properties.length ? owner : { kind: "projection", owner, fields: [...fields].sort() };
      const cardinality = contract.schema_version === "domainspec.typed-query/v1" ? "list" : contract.schema_version === "domainspec.typed-query/v2" ? contract.result_cardinality : undefined;
      if (cardinality !== "list" && cardinality !== "optional") return fail(query.source_line, "unsupported Query result cardinality");
      if (declaration.output.kind !== cardinality) return fail(query.source_line, "Query cardinality differs from its authored declaration");
      if (query.absence_failure && cardinality !== "optional") return fail(query.source_line, "absence failure requires an optional Query result");
      roots.set(query.name, query.absence_failure ? element : { kind: cardinality, element });
    }
    for (const mapping of realization.mappings) {
      const declaration = declarations.get(mapping.mapping)!;
      if (declaration.kind !== "mapping") return fail(mapping.source_line, "expected Mapping");
      const [owner, contract] = declaration.target.split(".");
      roots.set(mapping.name, contract ? { kind: "contract", interface_selector: selector(owner!), contract_id: symbol(contract) } : { kind: "named", selector: selector(owner!) });
    }
    const portableRoots = [...roots.keys()].map(name => symbol(name, "_"));
    if (new Set(portableRoots).size !== roots.size) fail(realization.source_line, "value names collide after target normalization");
    const pathValue = (path: string[], line: number): Value => {
      let current = roots.get(path[0]!);
      if (!current) return fail(line, "unknown value root");
      const properties: string[] = [];
      for (const fieldName of path.slice(1)) {
        if (current.kind === "contract") {
          const owner = current.interface_selector, contractId = current.contract_id;
          const declaration = bySelector.get(owner);
          const contract = declaration?.kind === "interface" ? declaration.contracts.find(c => symbol(c.id) === contractId) : undefined;
          const field = contract?.fields.find(f => f.name === fieldName);
          if (!field) return fail(line, "unknown public contract field");
          const formed = node(owner).contracts.find((c: any) => c.contract_id === contractId).fields.find((f: any) => f.name === symbol(fieldName, "_"));
          properties.push(formed.ontology_field); current = publicType(field.type, owner);
        } else if (current.kind === "named" || current.kind === "reference" || current.kind === "projection") {
          const owner = current.kind === "projection" ? current.owner.selector : current.selector;
          const declaration = bySelector.get(owner);
          if (current.kind === "projection" && !current.fields.includes(symbol(fieldName, "_"))) return fail(line, "Query projection does not contain this field");
          if (current.kind === "reference" && !current.projection.includes(symbol(fieldName, "_"))) return fail(line, "identity reference cannot dereference Entity state");
          if (declaration?.kind !== "entity" && declaration?.kind !== "value-object") return fail(line, "value has no supported data field traversal");
          const field = declaration.fields.find(f => f.name === fieldName);
          if (!field) return fail(line, "unknown data field");
          const formed = node(owner).properties.find((p: any) => p.name === symbol(fieldName, "_"));
          properties.push(formed.ontology_property); current = type(field.type);
        } else if (current.kind === "event-input") return fail(line, "Event input remains opaque until explicit Event construction");
        else return fail(line, "scalar or collection path traversal is forbidden; optional values require explicit absence handling");
      }
      return { type: current, value: { op: "path", root: symbol(path[0]!, "_"), properties } };
    };
    const args = (actual: RealizationArgument[], expected: Array<{ name: string; type: Type }>, line: number) => {
      const names = actual.map(a => symbol(a.parameter, "_"));
      if (new Set(names).size !== names.length || json([...names].sort()) !== json(expected.map(a => a.name).sort())) fail(line, "argument coverage differs from typed contract");
      return actual.map(a => {
        const value = pathValue(a.path, a.source_line), parameter = symbol(a.parameter, "_");
        equal(value.type, expected.find(p => p.name === parameter)!.type, a.source_line);
        return { parameter, ...value };
      });
    };
    const reads = realization.reads.map(read => {
      const entity = declarations.get(read.entity)!;
      if (entity.kind !== "entity" || !entity.identity) return fail(read.source_line, "keyed read requires explicit Entity identity");
      const key = pathValue(read.key, read.source_line);
      equal(key.type, type(entity.fields.find(f => f.name === entity.identity)!.type), read.source_line);
      return { name: read.name, entity: selector(read.entity), key };
    });
    const queries = realization.queries.map(query => {
      const declaration = declarations.get(query.query)!;
      if (declaration.kind !== "query") return fail(query.source_line, "expected Query");
      return { name: query.name, query: selector(query.query), source: selector(declaration.source.entity), contract_sha256: digest(json(node(selector(query.query)))), arguments: args(query.arguments, declaration.inputs.map(i => ({ name: symbol(i.name, "_"), type: type(i.type) })), query.source_line), output: roots.get(query.name)!, ...(query.absence_failure ? { absence_failure: query.absence_failure } : {}) };
    });
    const mappings = realization.mappings.map(mapping => {
      const declaration = declarations.get(mapping.mapping)!;
      if (declaration.kind !== "mapping") return fail(mapping.source_line, "expected Mapping");
      return { name: mapping.name, mapping: selector(mapping.mapping), contract_sha256: digest(json(node(selector(mapping.mapping)))), arguments: args(mapping.arguments, declaration.inputs.map(i => ({ name: symbol(i.name, "_"), type: type(i.type) })), mapping.source_line), output: roots.get(mapping.name)! };
    });
    const guards = realization.guards.map(guard => {
      const contract = node(selector(guard.rule));
      if (contract?.schema_version !== "domainspec.typed-rule/v2") return fail(guard.source_line, "guard requires the exact typed Rule projection");
      return { rule: selector(guard.rule), contract_sha256: digest(json(contract)), arguments: args(guard.arguments, contract.parameters, guard.source_line) };
    });
    const writes = realization.writes.map(write => {
      const value = pathValue(write.path, write.source_line);
      equal(value.type, { kind: "named", selector: selector(write.entity) }, write.source_line);
      return { entity: selector(write.entity), mode: write.mode, ...value };
    });
    const events = realization.events.map(event => {
      const value = pathValue(event.path, event.source_line);
      equal(value.type, { kind: "event-input", selector: selector(event.event) }, event.source_line);
      return { event: selector(event.event), ...value };
    });
    const result = pathValue(realization.result, realization.source_line);
    equal(result.type, type(operation.output), realization.source_line);
    const checked = { id: realization.id, operation: selector(realization.operation), input: { name: realization.input, type: type(operation.input) },
      event_inputs: realization.event_inputs.map(e => ({ name: symbol(e.name, "_"), event: selector(e.event) })), reads, queries, mappings, guards, writes, events, result,
      atomicity: realization.atomicity, continuation: realization.continuation, execution: "not-performed" as const, authority_effect: "none" as const };
    return { ...checked, graph: compileApplicationRealizationGraph(checked) };
  });
}
