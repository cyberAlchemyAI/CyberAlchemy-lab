import { CompilationRejected } from "./model.js";
import { symbol } from "./domainspec-profile.js";
import { checkApplicationRealizationTypes } from "./application-realization-types.js";
import type { lowerApplicationRuleProjections } from "./application-rule-projection.js";

/** Derive named value connections separately from effect bindings. No execution occurs. */
export function deriveApplicationRealizationCompositions(projection: ReturnType<typeof lowerApplicationRuleProjections>) {
  const fail = (id: string, message: string): never => { throw new CompilationRejected([
    { code: "APPLICATION_REALIZATION_UNSUPPORTED", path: `$realization/${id}`, message },
  ]); };
  return checkApplicationRealizationTypes(projection).map(row => {
    const input = symbol(row.input.name, "_");
    if (row.reads.some(read => read.key.value.root !== input)) fail(row.id, "existing action read keys must depend on the input, not another read");
    if (new Set(row.reads.map(read => read.entity)).size !== row.reads.length) fail(row.id, "existing action slots require one read per Entity");
    if (row.queries.some(query => row.reads.some(read => read.entity === query.source))) fail(row.id, "one Entity slot cannot supply both a keyed read and a Query collection");
    const action = {
      schema_version: "domainspec.operation-action-bindings/v1-candidate",
      selector: row.operation,
      inputs: [{ name: input, type: row.input.type }],
      reads: row.reads.map(read => ({ slot: read.entity, target: read.entity, parameter: symbol(read.name, "_"), key: read.key.value })),
      guards: row.guards.map(guard => ({ selector: guard.rule, arguments: guard.arguments.map(arg => ({ parameter: arg.parameter, value: arg.value })) })),
      writes: row.writes.map(write => ({ slot: write.entity, target: write.entity, mode: write.mode, value: write.value })),
      events: row.events.map(event => {
        const source = row.event_inputs.find(input => input.name === event.value.root && input.event === event.event);
        if (!source || event.value.properties.length) return fail(row.id, "Event slots require the whole explicitly declared Event input");
        return { slot: event.event, target: event.event, parameter: source.name };
      }), result: { type: row.result.type, value: row.result.value },
      atomicity: row.atomicity, continuation: row.continuation,
    };
    const bindings = [
      ...row.queries.map(query => ({ kind: "query" as const, name: symbol(query.name, "_"), selector: query.query, source_slot: query.source,
        arguments: query.arguments.map(arg => ({ parameter: arg.parameter, value: arg.value })), absence: query.absence_failure ? "require-present" as const : "preserve" as const })),
      ...row.mappings.map(mapping => ({ kind: "mapping" as const, name: symbol(mapping.name, "_"), selector: mapping.mapping,
        arguments: mapping.arguments.map(arg => ({ parameter: arg.parameter, value: arg.value })) })),
    ].sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0);
    for (const binding of bindings) binding.arguments.sort((a, b) => a.parameter < b.parameter ? -1 : a.parameter > b.parameter ? 1 : 0);
    return { action, composition: { schema_version: "domainspec.operation-value-composition/v1-candidate", operation_ref: row.operation, bindings },
      absence_failures: row.queries.filter(query => query.absence_failure !== undefined)
        .map(query => ({ binding: symbol(query.name, "_"), code: query.absence_failure! }))
        .sort((a, b) => a.binding < b.binding ? -1 : a.binding > b.binding ? 1 : 0) };
  });
}

/** Preserve the closed legacy route until project-level composed generation joins it. */
export function deriveApplicationRealizationActions(projection: ReturnType<typeof lowerApplicationRuleProjections>) {
  return deriveApplicationRealizationCompositions(projection).map(row => {
    if (row.composition.bindings.length) throw new CompilationRejected([{ code: "APPLICATION_REALIZATION_UNSUPPORTED", path: `$realization/${row.action.selector}`,
      message: "Query and Mapping connections require the composed project path; they cannot enter the legacy action-only generator" }]);
    return row.action;
  });
}
