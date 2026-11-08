import { CompilationRejected } from "./model.js";
import { digest, json, symbol } from "./domainspec-profile.js";

interface Value { type: unknown; value: { op: "path"; root: string; properties: string[] } }
interface Argument extends Value { parameter: string }
interface Connections {
  id: string; operation: string; input: { name: string; type: unknown };
  event_inputs: Array<{ name: string; event: string }>;
  reads: Array<{ name: string; entity: string; key: Value }>;
  queries: Array<{ name: string; query: string; arguments: Argument[]; output: unknown }>;
  mappings: Array<{ name: string; mapping: string; arguments: Argument[]; output: unknown }>;
  guards: Array<{ rule: string; arguments: Argument[] }>;
  writes: Array<Value & { entity: string; mode: "create" | "replace" }>;
  events: Array<Value & { event: string }>;
  result: Value; atomicity: string; continuation: string;
}
export interface ApplicationRealizationGraphNode { id: string; kind: string; depends_on: string[]; binding: unknown }
const compare = (a: string, b: string) => a < b ? -1 : a > b ? 1 : 0;
const sorted = (values: string[]) => [...new Set(values)].sort(compare);
const normalize = (value: unknown): unknown => Array.isArray(value) ? value.map(normalize)
  : value && typeof value === "object" ? Object.fromEntries(Object.entries(value).sort(([a], [b]) => compare(a, b)).map(([k, v]) => [k, normalize(v)])) : value;
const freeze = <T>(value: T): T => {
  if (value && typeof value === "object") { Object.values(value).forEach(freeze); Object.freeze(value); }
  return value;
};

/** Data dependencies only. Layers are dependency frontiers, not a parallel runtime schedule. */
export function compileApplicationRealizationGraph(connections: Connections) {
  const fail = (message: string): never => { throw new CompilationRejected([
    { code: "APPLICATION_REALIZATION_GRAPH", path: `$realization/${connections.id}`, message },
  ]); };
  const nodes: ApplicationRealizationGraphNode[] = [], roots = new Map<string, string>();
  const root = (name: string, kind: string) => {
    const normalized = symbol(name, "_");
    if (roots.has(normalized)) fail("duplicate normalized value root");
    const id = `${kind}:${normalized}`; roots.set(normalized, id); return id;
  };
  const inputId = root(connections.input.name, "input");
  for (const row of connections.event_inputs) root(row.name, "event-input");
  for (const row of connections.reads) root(row.name, "read");
  for (const row of connections.queries) root(row.name, "query");
  for (const row of connections.mappings) root(row.name, "mapping");
  const valueRoot = (value: Value) => roots.get(value.value.root) ?? fail(`missing value root ${value.value.root}`);
  const namedRoot = (name: string) => roots.get(symbol(name, "_"))!;
  const args = (rows: Argument[]) => [...rows].sort((a, b) => compare(a.parameter, b.parameter));
  const add = (id: string, kind: string, dependencies: string[], binding: unknown) => {
    if (nodes.some(node => node.id === id)) fail("duplicate graph node");
    nodes.push({ id, kind, depends_on: sorted(dependencies), binding: normalize(binding) });
  };
  add(inputId, "input", [], connections.input);
  for (const row of connections.event_inputs) add(namedRoot(row.name), "event-input", [], row);
  const inputs = [inputId, ...connections.event_inputs.map(row => namedRoot(row.name))];
  add("transaction", "transaction-boundary", inputs, { atomicity: connections.atomicity, continuation: connections.continuation });
  for (const row of connections.reads) add(namedRoot(row.name), "entity-read", ["transaction", valueRoot(row.key)], row);
  for (const row of connections.queries) add(namedRoot(row.name), "query", ["transaction", ...row.arguments.map(valueRoot)], { ...row, arguments: args(row.arguments) });
  for (const row of connections.mappings) add(namedRoot(row.name), "mapping", ["transaction", ...row.arguments.map(valueRoot)], { ...row, arguments: args(row.arguments) });
  const values = [...connections.reads, ...connections.queries, ...connections.mappings].map(row => namedRoot(row.name));
  const guards = connections.guards.map(row => `guard:${row.rule}`);
  for (const row of connections.guards) add(`guard:${row.rule}`, "rule-guard", ["transaction", ...values, ...row.arguments.map(valueRoot)], { ...row, arguments: args(row.arguments) });
  const writes = connections.writes.map(row => `write:${row.entity}`);
  for (const row of connections.writes) add(`write:${row.entity}`, "write-validation", ["transaction", ...values, ...guards, valueRoot(row)], row);
  const events = connections.events.map(row => `event:${row.event}`);
  for (const row of connections.events) add(`event:${row.event}`, "event-construction", ["transaction", ...values, ...guards, ...writes, valueRoot(row)], row);
  add("result", "result-validation", ["transaction", ...values, ...guards, ...writes, ...events, valueRoot(connections.result)], connections.result);
  add("commit", "commit-intent", ["result", ...writes, ...events], { atomicity: connections.atomicity, continuation: connections.continuation });
  nodes.sort((a, b) => compare(a.id, b.id));
  const ids = new Set(nodes.map(node => node.id));
  for (const node of nodes) for (const dependency of node.depends_on) if (!ids.has(dependency)) fail("unresolved dependency");
  const pending = new Map(nodes.map(node => [node.id, node])), complete = new Set<string>(), layers: string[][] = [];
  while (pending.size) {
    const ready = [...pending.values()].filter(node => node.depends_on.every(id => complete.has(id))).map(node => node.id).sort(compare);
    if (!ready.length) fail("cyclic dependency graph");
    layers.push(ready); for (const id of ready) { complete.add(id); pending.delete(id); }
  }
  const body = { schema_version: "alchlang.realization-dependency-graph/v1-candidate", realization: connections.id,
    operation: connections.operation, nodes, layers, execution: "not-performed", authority_effect: "none" };
  return freeze({ ...body, graph_sha256: digest(json(normalize(body))) });
}
