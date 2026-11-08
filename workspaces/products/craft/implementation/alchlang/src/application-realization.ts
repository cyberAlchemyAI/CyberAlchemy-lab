import { CompilationRejected } from "./model.js";
import type { ApplicationSourceSection } from "./formal-claim.js";
import type { ApplicationDeclaration } from "./application-source.js";

export interface RealizationArgument { parameter: string; path: string[]; source_line: number }
export interface ApplicationRealization {
  id: string; source_line: number; operation: string; input: string;
  event_inputs: Array<{ name: string; event: string; source_line: number }>;
  reads: Array<{ name: string; entity: string; key: string[]; source_line: number }>;
  queries: Array<{ name: string; query: string; arguments: RealizationArgument[]; source_line: number; absence_failure?: string }>;
  mappings: Array<{ name: string; mapping: string; arguments: RealizationArgument[]; source_line: number }>;
  guards: Array<{ rule: string; arguments: RealizationArgument[]; source_line: number }>;
  writes: Array<{ entity: string; mode: "create" | "replace"; path: string[]; source_line: number }>;
  events: Array<{ event: string; path: string[]; source_line: number }>;
  result: string[]; atomicity: "state-and-outbox"; continuation: "awaited-settlement";
}
const name = "[A-Za-z_][\\w-]*", valuePath = `${name}(?:\\.${name})*`;
const fail = (line: number, message: string): never => {
  throw new CompilationRejected([{ code: "APPLICATION_REALIZATION", path: `$line:${line}`, message }]);
};

/** Closed value-connection declarations; no execution, type proof or source-order effects. */
export function normalizeApplicationRealizations(sections: ApplicationSourceSection[], declarations: ApplicationDeclaration[], rules: ReadonlySet<string>): ApplicationRealization[] {
  const byId = new Map(declarations.map(d => [d.id, d]));
  const selected = new Set<string>();
  return sections.map(section => {
    let operation: string | undefined, input: string | undefined, result: string[] | undefined;
    let atomicity: ApplicationRealization["atomicity"] | undefined, continuation: ApplicationRealization["continuation"] | undefined;
    const reads: ApplicationRealization["reads"] = [], queries: ApplicationRealization["queries"] = [], mappings: ApplicationRealization["mappings"] = [];
    const guards: ApplicationRealization["guards"] = [], writes: ApplicationRealization["writes"] = [], events: ApplicationRealization["events"] = [];
    const eventInputs: ApplicationRealization["event_inputs"] = [];
    const absences = new Map<string, { code: string; line: number }>();
    const argumentsOf = (text: string, line: number): RealizationArgument[] => {
      const args = text.trim() ? text.split(",").map(part => {
        const m = new RegExp(`^\\s*(${name})\\s*<-\\s*(${valuePath})\\s*$`).exec(part);
        if (!m) return fail(line, "arguments must be named value connections: parameter <- value.path");
        return { parameter: m[1]!, path: m[2]!.split("."), source_line: line };
      }) : [];
      if (new Set(args.map(a => a.parameter)).size !== args.length) fail(line, "duplicate argument");
      return args;
    };
    for (const row of section.rows) {
      let m: RegExpExecArray | null;
      if ((m = new RegExp(`^(operation|input) (${name})$`).exec(row.text))) {
        if (m[1] === "operation") { if (operation) fail(row.line, "duplicate operation"); operation = m[2]!; }
        else { if (input) fail(row.line, "duplicate input"); input = m[2]!; }
      } else if ((m = new RegExp(`^event-input (${name}) (${name})$`).exec(row.text))) {
        eventInputs.push({ name: m[1]!, event: m[2]!, source_line: row.line });
      } else if ((m = new RegExp(`^read (${name}) <- (${name}) key (${valuePath})$`).exec(row.text))) {
        reads.push({ name: m[1]!, entity: m[2]!, key: m[3]!.split("."), source_line: row.line });
      } else if ((m = new RegExp(`^(query|map) (${name}) <- (${name})\\((.*)\\)$`).exec(row.text))) {
        const args = argumentsOf(m[4]!, row.line);
        if (m[1] === "query") queries.push({ name: m[2]!, query: m[3]!, arguments: args, source_line: row.line });
        else mappings.push({ name: m[2]!, mapping: m[3]!, arguments: args, source_line: row.line });
      } else if ((m = new RegExp(`^on-absence (${name}) fail ([A-Z][A-Z0-9_]{0,127})$`).exec(row.text))) {
        if (absences.has(m[1]!)) fail(row.line, "duplicate Query absence policy");
        absences.set(m[1]!, { code: m[2]!, line: row.line });
      } else if ((m = new RegExp(`^guard (${name})\\((.*)\\)$`).exec(row.text))) {
        guards.push({ rule: m[1]!, arguments: argumentsOf(m[2]!, row.line), source_line: row.line });
      } else if ((m = new RegExp(`^write (${name}) (create|replace) <- (${valuePath})$`).exec(row.text))) {
        writes.push({ entity: m[1]!, mode: m[2] as "create" | "replace", path: m[3]!.split("."), source_line: row.line });
      } else if ((m = new RegExp(`^event (${name}) <- (${valuePath})$`).exec(row.text))) {
        events.push({ event: m[1]!, path: m[2]!.split("."), source_line: row.line });
      } else if ((m = new RegExp(`^result <- (${valuePath})$`).exec(row.text))) {
        if (result) fail(row.line, "duplicate result"); result = m[1]!.split(".");
      } else if (row.text === "atomicity state-and-outbox") {
        if (atomicity) fail(row.line, "duplicate atomicity"); atomicity = "state-and-outbox";
      } else if (row.text === "continuation awaited-settlement") {
        if (continuation) fail(row.line, "duplicate continuation"); continuation = "awaited-settlement";
      } else fail(row.line, "unsupported realization clause; imperative code and inline expressions are forbidden");
    }
    if (!operation || !input || !result || !atomicity || !continuation) return fail(section.line, "operation, input, result, atomicity and continuation must be explicit");
    const contract = byId.get(operation);
    if (contract?.kind !== "operation") return fail(section.line, "operation must select a declared Operation");
    if (selected.has(operation)) fail(section.line, "multiple realizations for one Operation require an explicit selection mechanism");
    selected.add(operation);
    const same = (actual: string[], expected: string[], role: string) => {
      if (new Set(actual).size !== actual.length || JSON.stringify([...actual].sort()) !== JSON.stringify([...expected].sort())) fail(section.line, `${role} coverage differs from Operation`);
    };
    for (const row of reads) if (byId.get(row.entity)?.kind !== "entity") fail(row.source_line, "read requires a declared Entity");
    for (const row of queries) if (byId.get(row.query)?.kind !== "query") fail(row.source_line, "query requires a declared Query");
    for (const [binding, policy] of absences) {
      const query = queries.find(row => row.name === binding);
      if (!query) return fail(policy.line, "on-absence must select a Query value binding");
      const declaration = byId.get(query.query)!;
      if (declaration.kind !== "query" || declaration.output.kind !== "optional") return fail(policy.line, "on-absence requires an optional Query result");
      query.absence_failure = policy.code;
    }
    for (const row of mappings) if (byId.get(row.mapping)?.kind !== "mapping") fail(row.source_line, "map requires a declared Mapping");
    for (const row of guards) if (!rules.has(row.rule)) fail(row.source_line, "guard requires a declared Rule");
    for (const row of writes) if (byId.get(row.entity)?.kind !== "entity") fail(row.source_line, "write requires a declared Entity");
    for (const row of events) if (byId.get(row.event)?.kind !== "event") fail(row.source_line, "event requires a declared Event");
    for (const row of eventInputs) if (byId.get(row.event)?.kind !== "event") fail(row.source_line, "event-input requires a declared Event");
    // Several explicit queries may share an Entity source; preserve each query identity.
    const queryEntities = queries.map(row => { const query = byId.get(row.query)!; return query.kind === "query" ? query.source.entity : ""; });
    same([...new Set([...reads.map(r => r.entity), ...queryEntities])], contract.reads, "read");
    same(writes.map(r => r.entity), contract.writes, "write"); same(events.map(r => r.event), contract.produces, "event"); same(guards.map(r => r.rule), contract.requires, "guard");
    const bindings = [input, ...eventInputs.map(r => r.name), ...reads.map(r => r.name), ...queries.map(r => r.name), ...mappings.map(r => r.name)];
    if (new Set(bindings).size !== bindings.length) fail(section.line, "duplicate value binding");
    const dependencies = new Map<string, string[]>([[input, []]]);
    for (const r of eventInputs) dependencies.set(r.name, []);
    for (const r of reads) dependencies.set(r.name, [r.key[0]!]);
    for (const r of [...queries, ...mappings]) dependencies.set(r.name, r.arguments.map(a => a.path[0]!));
    const paths = [...reads.map(r => r.key), ...[...queries, ...mappings, ...guards].flatMap(r => r.arguments.map(a => a.path)), ...writes.map(r => r.path), ...events.map(r => r.path), result];
    for (const p of paths) if (!dependencies.has(p[0]!)) fail(section.line, `unknown value binding ${p[0]}`);
    const active = new Set<string>(), done = new Set<string>();
    const visit = (id: string): void => {
      if (active.has(id)) fail(section.line, "cyclic value connections");
      if (done.has(id)) return; active.add(id);
      for (const dependency of dependencies.get(id)!) visit(dependency);
      active.delete(id); done.add(id);
    };
    bindings.forEach(visit);
    for (const row of [...queries, ...mappings]) {
      const target = byId.get("query" in row ? row.query : row.mapping)!;
      if (target.kind === "query" || target.kind === "mapping") same(row.arguments.map(a => a.parameter), target.inputs.map(p => p.name), "argument");
    }
    for (const r of eventInputs) if (!events.some(e => e.path[0] === r.name)) fail(r.source_line, "unused Event input");
    return { id: section.id, source_line: section.line, operation, input, event_inputs: eventInputs, reads, queries, mappings, guards, writes, events, result, atomicity, continuation };
  });
}
