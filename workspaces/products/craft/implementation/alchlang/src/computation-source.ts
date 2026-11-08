import { createHash } from "node:crypto";
import { CompilationRejected } from "./model.js";
import { snapshotComputationBindings } from "./computation-bindings.js";

export const COMPUTATION_CAPABILITY = "alchlang.computation/v1-candidate" as const;
export const COMPUTATION_BINDINGS = "alchlang.computation-bindings/v1-candidate" as const;
export const COMPUTATION_SEMANTICS = "domainspec.iteration-expression/v1-candidate" as const;
export interface ComputationSourceOptions { capability: typeof COMPUTATION_CAPABILITY }
export type ComputationCompanionIdentityKind = "raw-utf8" | "canonical-json";
type Obj = Record<string, any>;
export interface ComputationLocation { line: number; column: number }
export interface ComputationDeclaration { name: string; kind: string; meaning: string; source_sha256: string; source_line: number }
export interface ParsedComputationSource {
  source_profile: "application-v1";
  capability: typeof COMPUTATION_CAPABILITY;
  owner: string;
  contract: Obj;
  declarations: ComputationDeclaration[];
  source_map: Record<string, ComputationLocation>;
}
export const computationDigest = (text: string): string => createHash("sha256").update(text).digest("hex");
function fail(code: string, line: number, column: number, message: string): never {
  throw new CompilationRejected([{ code, path: `$line:${line}:column:${column}`, message }]);
}
interface Token { text: string; line: number; column: number }
function tokenize(text: string, startLine: number): Token[] {
  const result: Token[] = []; let i = 0; let line = startLine; let column = 1;
  while (i < text.length) {
    const char = text[i]!;
    if (/\s/.test(char)) { if (char === "\n") { line++; column = 1; } else column++; i++; continue; }
    if (char === "#") { while (i < text.length && text[i] !== "\n") { i++; column++; } continue; }
    let word: string;
    if (char === '"') {
      let end = i + 1;
      for (; end < text.length; end++) { if (text[end] === "\\") end++; else if (text[end] === '"') break; else if (text[end] === "\n") fail("COMPUTATION_SYNTAX", line, column, "string literal cannot contain a raw newline"); }
      if (end >= text.length) fail("COMPUTATION_SYNTAX", line, column, "unterminated string");
      word = text.slice(i, end + 1);
      try { JSON.parse(word); } catch { fail("COMPUTATION_SYNTAX", line, column, "invalid JSON string literal"); }
    } else {
      const match = /^(?:=>|==|<=|>=|!=|[A-Za-z_][A-Za-z0-9_-]*|0|[1-9][0-9]*|[(){}\[\],:.;+*\/<>!=-])/.exec(text.slice(i));
      if (!match) fail("COMPUTATION_SYNTAX", line, column, "unexpected expression character");
      word = match[0];
    }
    result.push({ text: word, line, column }); i += word.length; column += word.length;
    if (result.length > 32768) fail("COMPUTATION_SOURCE_BOUND", line, column, "too many expression tokens");
  }
  result.push({ text: "", line, column }); return result;
}
const operators: Record<string, string> = { "==": "eq", "<": "lt", "<=": "lte", ">": "gt", ">=": "gte", "+": "add", "-": "subtract", "*": "multiply", "/": "divide", and: "and", or: "or" };
const precedence: Record<string, number> = { or: 1, and: 2, "==": 3, "<": 3, "<=": 3, ">": 3, ">=": 3, "+": 4, "-": 4, "*": 5, "/": 5 };
const binaryNames = new Set(["eq", "lt", "lte", "gt", "gte", "add", "subtract", "multiply", "divide", "and", "or"]);

/** A bounded syntax parser only. Craft owns type checking and execution. */
class ExpressionParser {
  cursor = 0; depth = 0; nodes = 0; typeDepth = 0;
  readonly locations = new WeakMap<Obj, ComputationLocation>();
  constructor(readonly tokens: Token[]) {}
  current(): Token { return this.tokens[this.cursor]!; }
  take(value?: string): Token {
    // A type's closing '>' can touch assignment '=' or lambda '=>'.
    // Resolve only at an explicit type delimiter; comparisons keep maximal munch.
    if (value === ">" && this.current().text === ">=") {
      const t = this.current(); const arrow = this.tokens[this.cursor + 1]?.text === ">";
      this.tokens.splice(this.cursor, arrow ? 2 : 1, { ...t, text: ">" }, { text: arrow ? "=>" : "=", line: t.line, column: t.column + 1 });
    }
    const token = this.current(); if (value !== undefined && token.text !== value) fail("COMPUTATION_SYNTAX", token.line, token.column, `expected ${value}, received ${token.text || "end of expression"}`);
    this.cursor++; return token;
  }
  name(): string { const t = this.take(); if (!/^[a-z][a-z0-9_]*$/.test(t.text) || t.text.length > 128) fail("COMPUTATION_NAME", t.line, t.column, "expected lowercase declared identifier"); return t.text; }
  natural(): number { const t = this.take(); if (!/^(0|[1-9][0-9]*)$/.test(t.text) || BigInt(t.text) > 262144n) fail("COMPUTATION_BOUND", t.line, t.column, "expected exact bounded natural number"); return Number(t.text); }
  type(): Obj {
    if (++this.typeDepth > 32) { const t = this.current(); fail("COMPUTATION_SOURCE_BOUND", t.line, t.column, "type nesting limit exceeded"); }
    const value = this.typeBody(); this.typeDepth--; return value;
  }
  typeBody(): Obj {
    const t = this.take();
    if (t.text === "UInt64" || t.text === "Bool") return { kind: "scalar", name: t.text };
    if (t.text === "String") { this.take("["); const max_bytes = this.natural(); this.take("]"); return { kind: "string", max_bytes }; }
    if (t.text === "List") { this.take("<"); const element = this.type(); this.take(","); const max_items = this.natural(); this.take(">"); return { kind: "list", element, max_items }; }
    if (t.text === "Outcome") { this.take("<"); const state = this.type(); this.take(","); const intent = this.type(); this.take(","); const max_intents = this.natural(); this.take(">"); return { kind: "outcome", state, intent, max_intents }; }
    if (!/^[a-z][a-z0-9_]*$/.test(t.text)) fail("COMPUTATION_TYPE", t.line, t.column, "expected Bool, UInt64, String[bound], List<type,bound>, or declared record");
    return { kind: "record", name: t.text };
  }
  binder(): Obj { const name = this.name(); this.take(":"); return { name, type: this.type() }; }
  node(value: Obj, token: Token): Obj { if (++this.nodes > 4096) fail("COMPUTATION_SOURCE_BOUND", token.line, token.column, "expression node limit exceeded"); this.locations.set(value, { line: token.line, column: token.column }); return value; }
  expression(minimum = 0): Obj {
    const token = this.current(); if (++this.depth > 32) fail("COMPUTATION_SOURCE_BOUND", token.line, token.column, "expression nesting limit exceeded");
    let left = this.primary();
    while ((precedence[this.current().text] ?? -1) >= minimum) {
      const operation = this.take(); const right = this.expression(precedence[operation.text]! + 1);
      left = this.node({ op: "binary", operator: operators[operation.text], left, right }, operation);
    }
    this.depth--; return left;
  }
  primary(): Obj {
    const t = this.take(); let value: Obj;
    if (t.text === "(") { value = this.expression(); this.take(")"); }
    else if (/^(0|[1-9][0-9]*)$/.test(t.text)) value = this.node({ op: "literal", type: { kind: "scalar", name: "UInt64" }, value: t.text }, t);
    else if (t.text === "true" || t.text === "false") value = this.node({ op: "literal", type: { kind: "scalar", name: "Bool" }, value: t.text === "true" }, t);
    else if (t.text.startsWith('"')) { this.take(":"); const type = this.type(); if (type.kind !== "string") fail("COMPUTATION_TYPE", t.line, t.column, "string literal needs explicit String[bound]"); value = this.node({ op: "literal", type, value: JSON.parse(t.text) }, t); }
    else if (t.text === "not" && this.current().text !== "(") value = this.node({ op: "unary", operator: "not", value: this.expression(6) }, t);
    else if (!/^[a-z][a-z0-9_-]*$/.test(t.text)) fail("COMPUTATION_SYNTAX", t.line, t.column, "expected expression");
    else if (this.current().text === "{") {
      this.take("{"); const fields: Obj = {};
      while (this.current().text !== "}") { const name = this.name(); this.take(":"); if (Object.hasOwn(fields, name)) fail("COMPUTATION_DUPLICATE", t.line, t.column, `duplicate record field ${name}`); fields[name] = this.expression(); if (this.current().text !== "}") this.take(","); }
      this.take("}"); value = this.node({ op: "record", type_name: t.text, fields }, t);
    } else if (this.current().text === "(") value = this.construct(t);
    else value = this.node({ op: "var", name: t.text }, t);
    while (this.current().text === ".") { const dot = this.take("."); value = this.node({ op: "field", value, field: this.name() }, dot); }
    return value;
  }
  construct(t: Token): Obj {
    this.take("("); let value: Obj;
    const expression = () => this.expression(); const comma = () => this.take(",");
    const spelling = t.text.replaceAll("-", "_").replace(/^checked_/, "");
    const name = spelling === "for" ? "indexed_fold" : spelling;
    if (binaryNames.has(name)) { const left = expression(); comma(); value = { op: "binary", operator: name, left, right: expression() }; }
    else if (name === "not") value = { op: "unary", operator: "not", value: expression() };
    else if (name === "if") { const condition = expression(); comma(); const then = expression(); comma(); value = { op: "if", condition, then, else: expression() }; }
    else if (name === "let") { const binding = this.binder(); this.take("="); const assigned = expression(); comma(); value = { op: "let", binding, value: assigned, body: expression() }; }
    else if (name === "map" || name === "filter") { const source = expression(); comma(); const item = this.binder(); this.take("=>"); value = { op: name, source, item, [name === "map" ? "body" : "predicate"]: expression() }; }
    else if (name === "fold" || name === "indexed_fold") { const source = expression(); comma(); const initial = expression(); comma(); const state = this.binder(); comma(); const item = this.binder(); const index = name === "indexed_fold" ? (comma(), this.binder()) : undefined; this.take("=>"); value = { op: name, source, initial, state, item, ...(index ? { index } : {}), body: expression() }; }
    else if (name === "repeat") { const count = expression(); comma(); const max_iterations = this.natural(); comma(); const initial = expression(); comma(); const state = this.binder(); comma(); const index = this.binder(); this.take("=>"); value = { op: name, count, max_iterations, initial, state, index, body: expression() }; }
    else if (name === "while_bounded" || name === "until_bounded") { const max_iterations = this.natural(); comma(); const initial = expression(); comma(); const state = this.binder(); this.take("=>"); const guard = expression(); this.take("=>"); value = { op: name, max_iterations, initial, state, guard, body: expression() }; }
    else if (name === "range") { const start = expression(); comma(); const end = expression(); comma(); const step = expression(); comma(); value = { op: name, start, end, step, max_iterations: this.natural() }; }
    else if (name === "sort") {
      const source = expression(); comma(); const item = this.binder(); this.take("=>"); const keys: Obj[] = [];
      while (this.current().text === "key") { this.take("key"); this.take("("); const key = expression(); comma(); const direction = this.take().text; comma(); const mode = this.take().text; this.take(")"); keys.push({ value: key, direction, mode }); if (this.current().text !== ")") comma(); }
      value = { op: name, source, item, keys };
    }
    else if (name === "policy") {
      const declaration = this.name(); comma(); const cases: Obj[] = [];
      while (this.current().text === "case") { this.take("case"); this.take("("); const condition = expression(); comma(); const action = expression(); this.take(")"); if (action.op !== "call") fail("COMPUTATION_POLICY", t.line, t.column, "policy case requires named Calculation call"); cases.push({ condition, calculation: action.declaration, arguments: action.arguments }); comma(); }
      this.take("default"); this.take("("); const action = expression(); this.take(")"); if (action.op !== "call") fail("COMPUTATION_POLICY", t.line, t.column, "policy default requires named Calculation call"); value = { op: name, declaration, cases, otherwise: { calculation: action.declaration, arguments: action.arguments } };
    }
    else if (name === "match") {
      const matched = expression(); comma(); const binding = this.binder(); this.take("=>"); const cases: Obj[] = [];
      while (this.current().text === "case") { this.take("case"); this.take("("); const when = expression(); comma(); const then = expression(); this.take(")"); cases.push({ when, then }); comma(); }
      this.take("default"); this.take("("); const otherwise = expression(); this.take(")"); value = { op: name, value: matched, binding, cases, otherwise };
    }
    else if (name === "state_machine") {
      const declaration = this.name(); comma(); const state = expression(); comma(); const event = expression(); comma(); const state_binding = this.binder(); comma(); const event_binding = this.binder(); comma(); const intent_type = this.type(); comma(); const max_intents = this.natural(); comma(); const transitions: Obj[] = [];
      while (this.current().text === "transition") { this.take("transition"); this.take("("); const guard = expression(); comma(); const next = expression(); comma(); this.take("["); const intents: Obj[] = []; while (this.current().text !== "]") { intents.push(expression()); if (this.current().text !== "]") comma(); } this.take("]"); this.take(")"); transitions.push({ guard, next, intents }); comma(); }
      this.take("default"); this.take("("); const otherwise = this.take().text; this.take(")"); value = { op: name, declaration, state, event, state_binding, event_binding, transitions, otherwise, intent_type, max_intents };
    }
    else { const args: Obj[] = []; while (this.current().text !== ")") { args.push(expression()); if (this.current().text !== ")") comma(); } value = { op: "call", declaration: t.text, arguments: args }; }
    this.take(")"); return this.node(value, t);
  }
  finish(): void { if (this.current().text !== "") { const t = this.current(); fail("COMPUTATION_SYNTAX", t.line, t.column, "unexpected trailing expression"); } }
}

function parseType(text: string, line: number): Obj { const p = new ExpressionParser(tokenize(text, line)); const value = p.type(); p.finish(); return value; }
function parseBinder(text: string, line: number): Obj { const p = new ExpressionParser(tokenize(text, line)); const value = p.binder(); p.finish(); return value; }
const limitNames = ["max_input_bytes", "max_output_bytes", "max_value_bytes", "max_items", "max_iterations", "max_ast_nodes", "max_ast_depth", "max_call_depth", "fuel"];

export function parseComputationSource(source: string, options: ComputationSourceOptions): ParsedComputationSource {
  if (options?.capability !== COMPUTATION_CAPABILITY) fail("COMPUTATION_CAPABILITY_REQUIRED", 1, 1, `select ${COMPUTATION_CAPABILITY} explicitly`);
  if (Buffer.byteLength(source, "utf8") > 262144) fail("COMPUTATION_SOURCE_BOUND", 1, 1, "source exceeds 262144 UTF-8 bytes");
  const lines = source.split(/\r?\n/); const roots: Obj = {}; const sections: { kind: string; name: string; line: number; lines: string[]; rows: { text: string; line: number }[] }[] = [];
  let current: typeof sections[number] | undefined;
  for (let index = 0; index < lines.length; index++) {
    const raw = lines[index]!; const line = index + 1;
    if (!raw.trim() || raw.trimStart().startsWith("#")) { if (current) current.lines.push(raw); continue; }
    if (/^\s/.test(raw)) { if (!current) fail("COMPUTATION_SYNTAX", line, 1, "indented clause requires declaration"); current.lines.push(raw); current.rows.push({ text: raw.trim(), line }); continue; }
    const section = /^(record|calculation|rule|mapping|policy|state-machine) ([a-z][a-z0-9_]*):$/.exec(raw);
    if (section) { current = { kind: section[1]!, name: section[2]!, line, lines: [raw], rows: [] }; sections.push(current); continue; }
    current = undefined;
    const root = /^(profile|capability|semantics|revision|stage|domain|owner|compute|rounding|limits) (.+)$/.exec(raw);
    if (!root) fail("COMPUTATION_SYNTAX", line, 1, "unsupported computation declaration");
    if (Object.hasOwn(roots, root[1]!)) fail("COMPUTATION_DUPLICATE", line, 1, `duplicate ${root[1]}`);
    roots[root[1]!] = root[2]!;
  }
  for (const name of ["profile", "capability", "semantics", "revision", "stage", "domain", "owner", "compute", "rounding", "limits"]) if (!Object.hasOwn(roots, name)) fail("COMPUTATION_REQUIRED", 1, 1, `missing explicit ${name}`);
  if (roots.profile !== "application-v1" || roots.capability !== COMPUTATION_CAPABILITY || roots.semantics !== COMPUTATION_SEMANTICS || roots.revision !== "ordered-metered-v1-candidate") fail("COMPUTATION_PROFILE", 1, 1, "unsupported root profile, syntax capability, semantics, or revision");
  if (roots.stage !== "full-computation") fail("COMPUTATION_STAGE", 1, 1, "this explicit syntax capability requires full-computation stage");
  if (!/^[a-z][a-z0-9-]*$/.test(roots.domain) || !/^[a-z][a-z0-9_]*$/.test(roots.compute) || !/^[A-Za-z_][A-Za-z0-9_.-]*$/.test(roots.owner)) fail("COMPUTATION_IDENTITY", 1, 1, "invalid domain, root computation, or owner identity");
  const limits: Obj = {};
  for (const part of roots.limits.split(/\s+/) as string[]) { const pair = /^([a-z_]+)=(0|[1-9][0-9]*)$/.exec(part); if (!pair || !limitNames.includes(pair[1]!) || Object.hasOwn(limits, pair[1]!) || BigInt(pair[2]!) > 262144n) fail("COMPUTATION_LIMITS", 1, 1, "limits require exact unique bounded key=number entries"); limits[pair[1]!] = Number(pair[2]); }
  if (Object.keys(limits).length !== limitNames.length) fail("COMPUTATION_LIMITS", 1, 1, "all resource limits must be declared explicitly");
  const records: Obj[] = []; const functions: Obj[] = []; const declarations: ComputationDeclaration[] = []; const source_map: Record<string, ComputationLocation> = {}; const parsedBodies = new Map<string, ExpressionParser>();
  const seen = new Set<string>();
  for (const section of sections) {
    if (seen.has(section.name)) fail("COMPUTATION_DUPLICATE", section.line, 1, `duplicate declaration ${section.name}`); seen.add(section.name);
    const fields: Obj = {}; const parameters: Obj[] = []; let result: Obj | undefined; let meaning: string | undefined; let pure = false; let body: Obj | undefined;
    for (let rowIndex = 0; rowIndex < section.rows.length; rowIndex++) {
      const row = section.rows[rowIndex]!;
      if (row.text.startsWith("meaning ")) { if (meaning !== undefined) fail("COMPUTATION_DUPLICATE", row.line, 1, "duplicate meaning"); try { meaning = JSON.parse(row.text.slice(8)); } catch { fail("COMPUTATION_MEANING", row.line, 1, "meaning requires explicit JSON string"); } if (typeof meaning !== "string" || !meaning.trim()) fail("COMPUTATION_MEANING", row.line, 1, "meaning must be nonempty"); }
      else if (row.text === "pure") { if (pure) fail("COMPUTATION_DUPLICATE", row.line, 1, "duplicate pure clause"); pure = true; }
      else if (row.text.startsWith("field ") && section.kind === "record") { const binder = parseBinder(row.text.slice(6), row.line); if (Object.hasOwn(fields, binder.name)) fail("COMPUTATION_DUPLICATE", row.line, 1, "duplicate field"); fields[binder.name] = binder.type; }
      else if (row.text.startsWith("input ") && section.kind !== "record") { const binder = parseBinder(row.text.slice(6), row.line); if (parameters.some(p => p.name === binder.name)) fail("COMPUTATION_DUPLICATE", row.line, 1, "duplicate input"); parameters.push(binder); }
      else if (row.text.startsWith("result ") && section.kind !== "record") { if (result) fail("COMPUTATION_DUPLICATE", row.line, 1, "duplicate result"); result = parseType(row.text.slice(7), row.line); }
      else if (/^expression(?::| )/.test(row.text) && section.kind !== "record") {
        if (body) fail("COMPUTATION_DUPLICATE", row.line, 1, "duplicate expression");
        const expressionText = lines[row.line - 1]!.replace(/^\s*expression(?::| )\s*/, prefix => " ".repeat(prefix.length));
        const remaining = lines.slice(row.line, section.rows.at(-1)!.line);
        const parser = new ExpressionParser(tokenize([expressionText, ...remaining].join("\n"), row.line)); body = parser.expression(); parser.finish(); parsedBodies.set(section.name, parser); rowIndex = section.rows.length;
      } else fail("COMPUTATION_SYNTAX", row.line, 1, `unsupported ${section.kind} clause`);
    }
    if (!meaning) fail("COMPUTATION_MEANING", section.line, 1, "each declaration requires explicit meaning");
    const kind = section.kind === "record" ? "Record" : section.kind === "state-machine" ? "StateMachine" : section.kind[0]!.toUpperCase() + section.kind.slice(1);
    declarations.push({ name: section.name, kind, meaning, source_sha256: computationDigest(section.lines.join("\n")), source_line: section.line });
    if (section.kind === "record") { if (!Object.keys(fields).length) fail("COMPUTATION_TYPE", section.line, 1, "closed record requires fields"); records.push({ name: section.name, fields }); }
    else { if (!pure || !result || !body) fail("COMPUTATION_REQUIRED", section.line, 1, "computation declarations require pure, result, and expression"); functions.push({ name: section.name, kind, pure: true, parameters, result, body }); }
  }
  const root = functions.find(f => f.name === roots.compute);
  if (!root || root.kind !== "Calculation") fail("COMPUTATION_ROOT", 1, 1, "compute must reference an explicitly declared Calculation");
  const contract: Obj = { schema_version: roots.semantics, semantics_revision: roots.revision, stage: roots.stage, source_node: `${roots.domain}:${roots.compute.replaceAll("_", "-")}`, records, inputs: root.parameters, functions: functions.filter(f => f !== root), result: root.result, rounding: roots.rounding, limits, expression: root.body };
  const mapExpression = (node: Obj, path: string, parser: ExpressionParser) => { const location = parser.locations.get(node); if (location) source_map[path] = location; for (const [key, child] of Object.entries(node)) { if (child && typeof child === "object") { if (Array.isArray(child)) child.forEach((value, index) => { if (value && typeof value === "object") mapExpression(value, `${path}.${key}[${index}]`, parser); }); else mapExpression(child as Obj, `${path}.${key}`, parser); } } };
  mapExpression(root.body, "$.expression", parsedBodies.get(root.name)!);
  contract.functions.forEach((f: Obj, index: number) => mapExpression(f.body, `$.functions[${index}].body`, parsedBodies.get(f.name)!));
  return { source_profile: "application-v1", capability: COMPUTATION_CAPABILITY, owner: roots.owner, contract, declarations, source_map };
}

function exact(value: unknown, keys: string[], path: string): Obj {
  if (!value || typeof value !== "object" || Array.isArray(value) || JSON.stringify(Object.keys(value).sort()) !== JSON.stringify([...keys].sort())) throw new CompilationRejected([{ code: "COMPUTATION_BINDING_SHAPE", path, message: "unexpected or missing companion members" }]);
  return value as Obj;
}

function bindingFailure(code: string, path: string, message: string): never {
  throw new CompilationRejected([{ code, path, message }]);
}

// Input is a detached, frozen snapshot; this encoder never receives caller data.
function compactSortedBindings(snapshot: unknown): string {
  if (snapshot === null || typeof snapshot !== "object") return JSON.stringify(snapshot)!;
  if (Array.isArray(snapshot)) return "[" + Array.from(snapshot, compactSortedBindings).join(",") + "]";
  const object = snapshot as Obj;
  return "{" + Object.keys(object).sort().map(key => JSON.stringify(key) + ":" + compactSortedBindings(object[key])).join(",") + "}";
}

/** Serialize companion object data, not source agreement or approval of its meaning. */
export function serializeComputationCompanion(value: unknown): string {
  const binding = exact(snapshotComputationBindings(value), ["schema_version", "capability", "semantics", "source_sha256", "owner", "declarations"], "$bindings");
  const digest = (value: unknown) => typeof value === "string" && /^[a-f0-9]{64}$/.test(value);
  if (binding.schema_version !== COMPUTATION_BINDINGS || binding.capability !== COMPUTATION_CAPABILITY || binding.semantics !== COMPUTATION_SEMANTICS || !digest(binding.source_sha256) || typeof binding.owner !== "string" || !/^[A-Za-z_][A-Za-z0-9_.-]*$/.test(binding.owner)) {
    bindingFailure("COMPUTATION_BINDING_SOURCE", "$bindings", "unsupported companion metadata or invalid source/owner identity");
  }
  if (!binding.declarations || typeof binding.declarations !== "object" || Array.isArray(binding.declarations) || Object.keys(binding.declarations).length === 0) {
    bindingFailure("COMPUTATION_BINDING_SHAPE", "$bindings/declarations", "nonempty companion declaration map required");
  }
  for (const name of Object.keys(binding.declarations)) {
    const path = `$bindings/declarations/${name}`;
    if (!/^[a-z][a-z0-9_]{0,127}$/.test(name)) bindingFailure("COMPUTATION_BINDING_DECLARATION", path, "invalid declaration name");
    const row = exact(binding.declarations[name], ["kind", "meaning", "source_sha256"], path);
    if (!["Record", "Rule", "Mapping", "Calculation", "Policy", "StateMachine"].includes(row.kind) || typeof row.meaning !== "string" || !row.meaning.trim() || !digest(row.source_sha256)) {
      bindingFailure("COMPUTATION_BINDING_DECLARATION", path, "valid declaration kind, nonempty meaning and SHA256 required");
    }
  }
  return compactSortedBindings(binding);
}

/** Parse companion JSON while rejecting duplicate keys before JSON.parse can erase them. */
export function parseComputationCompanion(text: string): unknown {
  if (Buffer.byteLength(text, "utf8") > 262144) fail("COMPUTATION_BINDING_BOUND", 1, 1, "companion exceeds byte cap");
  let cursor = 0; let depth = 0;
  const skip = () => { while (/\s/.test(text[cursor] ?? "") && cursor < text.length) cursor++; };
  const string = (): string => { const start = cursor++; while (cursor < text.length) { if (text[cursor] === "\\") cursor += 2; else if (text[cursor++] === '"') return JSON.parse(text.slice(start, cursor)); } throw new Error("unterminated string"); };
  const scan = (): void => {
    skip(); if (++depth > 32) throw new Error("companion nesting cap exceeded");
    if (text[cursor] === "{") { cursor++; skip(); const seen = new Set<string>(); if (text[cursor] !== "}") for (;;) { skip(); if (text[cursor] !== '"') throw new Error("expected object key"); const key = string(); if (seen.has(key)) throw new Error(`duplicate companion key ${key}`); seen.add(key); skip(); if (text[cursor++] !== ":") throw new Error("expected colon"); scan(); skip(); if (text[cursor] !== ",") break; cursor++; } if (text[cursor++] !== "}") throw new Error("expected object close"); }
    else if (text[cursor] === "[") { cursor++; skip(); if (text[cursor] !== "]") for (;;) { scan(); skip(); if (text[cursor] !== ",") break; cursor++; } if (text[cursor++] !== "]") throw new Error("expected list close"); }
    else if (text[cursor] === '"') string();
    else { const match = /^(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)/.exec(text.slice(cursor)); if (!match) throw new Error("invalid JSON value"); cursor += match[0].length; }
    depth--;
  };
  let parsed: unknown;
  try { scan(); skip(); if (cursor !== text.length) throw new Error("trailing JSON"); parsed = JSON.parse(text); } catch (error) { throw new CompilationRejected([{ code: "COMPUTATION_BINDING_JSON", path: `$@${cursor}`, message: error instanceof Error ? error.message : "invalid JSON" }]); }
  return snapshotComputationBindings(parsed);
}

export function lowerComputationSource(source: string, companion: unknown, options: ComputationSourceOptions) {
  const snapshot = typeof companion === "string" ? parseComputationCompanion(companion) : snapshotComputationBindings(companion);
  const parsed = parseComputationSource(source, options);
  const binding = exact(snapshot, ["schema_version", "capability", "semantics", "source_sha256", "owner", "declarations"], "$bindings");
  if (binding.schema_version !== COMPUTATION_BINDINGS || binding.capability !== COMPUTATION_CAPABILITY || binding.semantics !== COMPUTATION_SEMANTICS || binding.source_sha256 !== computationDigest(source) || binding.owner !== parsed.owner) throw new CompilationRejected([{ code: "COMPUTATION_BINDING_SOURCE", path: "$bindings", message: "unsupported successor or stale source/owner binding" }]);
  const declarations = exact(binding.declarations, parsed.declarations.map(d => d.name), "$bindings/declarations");
  for (const declaration of parsed.declarations) {
    const row = exact(declarations[declaration.name], ["kind", "meaning", "source_sha256"], `$bindings/declarations/${declaration.name}`);
    if (row.kind !== declaration.kind || row.meaning !== declaration.meaning || row.source_sha256 !== declaration.source_sha256) throw new CompilationRejected([{ code: "COMPUTATION_BINDING_DECLARATION", path: `$bindings/declarations/${declaration.name}`, message: "kind, reviewed meaning, or declaration source differs" }]);
  }
  const declaration_meanings: Record<string, string> = {};
  parsed.contract.records.forEach((record: Obj, index: number) => { declaration_meanings[`$.records[${index}]`] = declarations[record.name].meaning; });
  parsed.contract.functions.forEach((declaration: Obj, index: number) => { declaration_meanings[`$.functions[${index}]`] = declarations[declaration.name].meaning; });
  const rootName = parsed.contract.source_node.split(":")[1].replaceAll("-", "_");
  const source_binding = { owner_ref: parsed.owner, meaning: declarations[rootName].meaning as string, declaration_meanings };
  const companion_identity_kind: ComputationCompanionIdentityKind = typeof companion === "string" ? "raw-utf8" : "canonical-json";
  const companion_text = typeof companion === "string" ? companion : compactSortedBindings(binding);
  return { contract: parsed.contract, source_binding, source_map: parsed.source_map, source_sha256: computationDigest(source), companion_sha256: computationDigest(companion_text), companion_text, companion_identity_kind, source_profile: parsed.source_profile, capability: parsed.capability, owner: parsed.owner };
}

export type LoweredComputationSource = ReturnType<typeof lowerComputationSource>;
