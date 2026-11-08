import { parseDomainSource } from "./parser.js";
import { CompilationRejected } from "./model.js";
import { digest, json, symbol } from "./domainspec-profile.js";
import type { ApplicationFormalSource } from "./formal-claim.js";
import type { ApplicationType } from "./application-source.js";
import type { DomainSpecCompiler } from "./domainspec-cli.js";

type Obj = Record<string, any>;
const fail = (code: string, path: string, message: string): never => { throw new CompilationRejected([{ code, path, message }]); };
function exact(value: unknown, keys: string[], at: string): Obj {
  if (!value || typeof value !== "object" || Array.isArray(value) || json(Object.keys(value).sort()) !== json([...keys].sort())) return fail("APPLICATION_PERSISTENCE_BINDING", at, "unexpected or missing binding member");
  return value as Obj;
}
function same(values: string[], expected: string[], at: string): void {
  if (new Set(values).size !== values.length || json([...values].sort()) !== json([...expected].sort())) fail("APPLICATION_PERSISTENCE_COVERAGE", at, "binding coverage differs from source");
}

/** Local pure formation. Explicit physical/provider choices remain companion inputs until I05/I07. */
export function lowerApplicationPersistence(source: string, input: unknown, compiler: Pick<DomainSpecCompiler, "compilePersistenceComposition">) {
  const binding = exact(input, ["schema_version", "source_sha256", "composition", "declarations"], "$persistence");
  if (binding.schema_version !== "alchlang.application-persistence/v1-candidate" || binding.source_sha256 !== digest(source)) fail("APPLICATION_PERSISTENCE_SOURCE", "$persistence", "source or binding version differs");
  const parsed = parseDomainSource(source);
  if (parsed.source_profile !== "application-v1") fail("APPLICATION_PERSISTENCE_PROFILE", "$", "explicit application profile required");
  const model = parsed.carrier as unknown as ApplicationFormalSource;
  const declarations = model.integrations.filter(d => d.kind === "persistence");
  if (!declarations.length) fail("APPLICATION_PERSISTENCE_COVERAGE", "$", "no authored persistence declaration");
  const choices = exact(binding.declarations, declarations.map(d => d.id), "$persistence/declarations");
  const composition = compiler.compilePersistenceComposition(binding.composition);
  for (const transaction of composition.transaction_guarantees) {
    const resources = transaction.persistence_binding_refs.map((ref: string) => composition.persistence_bindings.find((p: Obj) => p.binding_id === ref)!.resource_ref);
    if (new Set(resources).size !== 1) fail("APPLICATION_PERSISTENCE_TRANSACTION", "$transactions", "single-resource-local cannot span distinct resources");
  }
  const feature = symbol(model.domain_id), selector = (id: string) => `${feature}:${symbol(id)}`;
  const byId = new Map(model.declarations.map(d => [d.id, d]));
  const normalized = model.declarations.map(d => selector(d.id));
  if (new Set(normalized).size !== normalized.length) fail("APPLICATION_SYMBOL_COLLISION", "$", "domain identities collide");
  const shape = (type: ApplicationType): string => {
    if (type.kind === "scalar") return "scalar";
    if (type.kind === "reference") return "entity-reference";
    if (type.kind === "sum") return "sum";
    if (type.kind === "optional" || type.kind === "list" || type.kind === "set") return type.kind;
    if (type.kind === "declaration") {
      const kind = byId.get(type.ref)?.kind;
      if (kind === "value-object" || kind === "enum") return kind;
    }
    return fail("APPLICATION_PERSISTENCE_SHAPE", "$", "type has no exact supported persistence shape; Entity embedding is not an identity reference");
  };
  const selectedBindings: string[] = [], selectedTransactions: string[] = [], selectedMappings: string[] = [];
  const references = declarations.map(declaration => {
    const at = `$line:${declaration.source_line}`;
    const choice = exact(choices[declaration.id], ["persistence_binding_ref", "transaction_binding_ref"], at);
    const entity = byId.get(declaration.entity.ref);
    if (entity?.kind !== "entity" || !entity.identity) return fail("APPLICATION_PERSISTENCE_ENTITY", at, "stores must select an Entity with explicit identity");
    const entityRef = selector(entity.id);
    const persistence = composition.persistence_bindings.find((p: Obj) => p.binding_id === choice.persistence_binding_ref);
    const transaction = composition.transaction_guarantees.find((p: Obj) => p.binding_id === choice.transaction_binding_ref);
    if (!persistence || !transaction) return fail("APPLICATION_PERSISTENCE_REFERENCE", at, "explicit persistence and transaction bindings required");
    same(persistence.logical_subject_refs, [entityRef], at);
    if (!transaction.persistence_binding_refs.includes(persistence.binding_id) || transaction.atomicity_scope !== declaration.transaction.scope || transaction.implementation_profile_ref !== persistence.implementation_profile_ref) fail("APPLICATION_PERSISTENCE_TRANSACTION", at, "local transaction and persistence bindings differ");
    const kernelBinding = composition.integration_kernel.integration_bindings.find((p: Obj) => p.binding_id === persistence.integration_binding_ref);
    if (kernelBinding?.logical_boundary_ref !== entityRef) fail("APPLICATION_PERSISTENCE_ENTITY", at, "kernel boundary differs from stores Entity");
    const mapping = composition.persistence_mappings.find((p: Obj) => p.mapping_id === persistence.logical_physical_mapping_ref)!;
    const fields = entity.fields.map(f => `${entityRef}#${symbol(f.name, "_")}`);
    same(mapping.field_mappings.map((f: Obj) => f.logical_property_ref), fields, at);
    same(mapping.identity_mappings.map((f: Obj) => f.logical_property_ref), [`${entityRef}#${symbol(entity.identity, "_")}`], at);
    for (const field of entity.fields) {
      const stored = mapping.field_mappings.find((f: Obj) => f.logical_property_ref === `${entityRef}#${symbol(field.name, "_")}`)!;
      if (stored.logical_shape !== shape(field.type)) fail("APPLICATION_PERSISTENCE_SHAPE", at, "logical field shape differs from authored type");
    }
    const queries = declaration.queries.map(ref => {
      const query = byId.get(ref.ref);
      if (query?.kind !== "query" || query.source.entity !== entity.id) return fail("APPLICATION_PERSISTENCE_QUERY", `$line:${ref.source_line}`, "serves must select a Query over the stored Entity");
      return { selector: selector(query.id), result_cardinality: query.output.kind, source_line: ref.source_line };
    });
    const operations = declaration.operations.map(ref => {
      const operation = byId.get(ref.ref);
      if (operation?.kind !== "operation" || !operation.writes.includes(entity.id)) return fail("APPLICATION_PERSISTENCE_OPERATION", `$line:${ref.source_line}`, "write consumer must explicitly write the stored Entity");
      return { selector: selector(operation.id), source_line: ref.source_line };
    });
    selectedBindings.push(persistence.binding_id); selectedTransactions.push(transaction.binding_id); selectedMappings.push(mapping.mapping_id);
    return { source_id: declaration.id, source_line: declaration.source_line, entity: entityRef, persistence_binding_ref: persistence.binding_id, transaction_binding_ref: transaction.binding_id, queries, operations };
  });
  same(selectedBindings, composition.persistence_bindings.map((p: Obj) => p.binding_id), "$bindings");
  same([...new Set(selectedTransactions)], composition.transaction_guarantees.map((p: Obj) => p.binding_id), "$transactions");
  same([...new Set(selectedMappings)], composition.persistence_mappings.map((p: Obj) => p.mapping_id), "$mappings");
  const sourceComposition = JSON.parse(json(binding.composition));
  const compositionFile = json(sourceComposition), compiledFile = json(composition);
  const trace = { schema_version: "alchlang.application-persistence-trace/v1-candidate", source_sha256: digest(source), binding_sha256: digest(json(input)), composition_sha256: digest(compositionFile), references,
    compiled_composition_sha256: digest(compiledFile), deferred_integrations: model.integrations.filter(d => d.kind !== "persistence").map(d => ({ id: d.id, kind: d.kind })), runtime_guarantees_observed: false, authority_effect: "none" };
  return { sourceComposition, composition, trace, files: { "persistence-composition.json": compositionFile, "persistence-compiled.json": compiledFile, "persistence-trace.json": json(trace) } };
}

export function assertApplicationPersistenceCurrent(source: string, binding: unknown, compiler: Pick<DomainSpecCompiler, "compilePersistenceComposition">, candidate: ReturnType<typeof lowerApplicationPersistence>): void {
  if (json(candidate) !== json(lowerApplicationPersistence(source, binding, compiler))) fail("APPLICATION_PERSISTENCE_STALE", "$", "candidate differs from exact current source and bindings");
}
