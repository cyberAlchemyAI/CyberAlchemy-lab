import { CompilationRejected, SFOL_PROFILE, type CompilerIssue, type ScalarType, type SfolFormula, type SfolUInt64Term } from "./model.js";
import { parseSfolFormula } from "./predicate-parser.js";
import { normalizeApplicationFormalSource } from "./formal-claim.js";
import { applicationIntegrationKinds } from "./application-integration.js";
import { selectAlchSourceProfile } from "./profile-architecture.js";
import { parseCommerceModuleSource } from "./commerce-source-parser.js";
import type { CommerceParsedModule } from "./commerce-source-model.js";

/** Explicit source dialect dispatch; commerce modules retain their own syntax
 * and do not acquire a legacy/service-v1 carrier. Open Questions: EC06/CONTEXT.md. */
export function parseAlchSourceDocument(source:string,relativePath:string):
 {readonly kind:'commerce-module';readonly parsed:CommerceParsedModule}|
 {readonly kind:'domain-source';readonly parsed:ParsedDomainSource} {
 const first=source.split(/\r?\n/).find(line=>line.trim()&&!line.trimStart().startsWith('#'))?.trimStart()??'';
 return /^module(?:\s|$)/.test(first)?{kind:'commerce-module',parsed:parseCommerceModuleSource(source,relativePath)}:{kind:'domain-source',parsed:parseDomainSource(source)};
}
export { parseCommerceModuleSource } from "./commerce-source-parser.js";

type Row = { line: number; text: string; indent?: number };
type Section = { kind: string; id: string; rows: Row[]; line: number };

export interface ParsedDomainSource {
  carrier: Record<string, unknown>;
  source_kind: "markdown-alchlang" | "plain-alchlang";
  source_profile: "application-v1" | "legacy-sfol-v1";
  profile_selection: "explicit" | "historical-default";
  diagnostics: CompilerIssue[];
}

function extractSource(markdown: string): { text: string; source_kind: ParsedDomainSource["source_kind"] } {
  const blocks = [...markdown.matchAll(/```alchlang\s*\n([\s\S]*?)```/g)];
  if (blocks.length > 1) throw new CompilationRejected([{ code: "SOURCE_BLOCK_COUNT", path: "$", message: "expected exactly one alchlang code block" }]);
  if (blocks.length === 1) return { text: blocks[0][1], source_kind: "markdown-alchlang" };
  if (markdown.includes("```")) throw new CompilationRejected([{ code: "SOURCE_BLOCK_COUNT", path: "$", message: "Markdown code fence must be labelled alchlang" }]);
  return { text: markdown, source_kind: "plain-alchlang" };
}

const words = (value: string): string[] => value.split(",").map((item) => item.trim()).filter(Boolean);
const scalarTypes = new Set<ScalarType>(["string", "integer", "decimal", "boolean", "identifier", "timestamp", "duration", "enum", "reference", "list", "record"]);

function parseSfolUInt64Term(source: string, inputs: ReadonlySet<string>): SfolUInt64Term {
  let cursor = 0;
  const skip = () => { while (/\s/.test(source[cursor] ?? "")) cursor += 1; };
  const parse = (): SfolUInt64Term => {
    skip();
    const rest = source.slice(cursor);
    const number = /^(0|[1-9]\d*)/.exec(rest);
    if (number) { cursor += number[0].length; return { node: "uint64_literal", value: number[0] }; }
    const name = /^[A-Za-z_][\w.-]*/.exec(rest);
    if (!name) throw new CompilationRejected([{ code: "CALCULATION_SYNTAX", path: `$@${cursor}`, message: "expected input, UInt64 literal, or arithmetic operator" }]);
    cursor += name[0].length; skip();
    if (source[cursor] !== "(") {
      if (!inputs.has(name[0])) throw new CompilationRejected([{ code: "UNRESOLVED_REFERENCE", path: `$@${cursor - name[0].length}`, message: `${name[0]} is not a declared calculation input` }]);
      return { node: "input_ref", ref: name[0] };
    }
    if (!["add", "subtract", "multiply", "divide"].includes(name[0])) throw new CompilationRejected([{ code: "UNKNOWN_CALCULATION_OPERATOR", path: `$@${cursor - name[0].length}`, message: `${name[0]} is not supported` }]);
    cursor += 1; const left = parse(); skip();
    if (source[cursor] !== ",") throw new CompilationRejected([{ code: "CALCULATION_SYNTAX", path: `$@${cursor}`, message: "expected comma" }]);
    cursor += 1; const right = parse(); skip();
    if (source[cursor] !== ")") throw new CompilationRejected([{ code: "CALCULATION_SYNTAX", path: `$@${cursor}`, message: "expected closing parenthesis" }]);
    cursor += 1;
    return { operator: name[0] as "add" | "subtract" | "multiply" | "divide", operands: [left, right] };
  };
  const expression = parse(); skip();
  if (cursor !== source.length) throw new CompilationRejected([{ code: "CALCULATION_SYNTAX", path: `$@${cursor}`, message: "unexpected trailing calculation input" }]);
  return expression;
}

export function parseDomainSource(markdown: string): ParsedDomainSource {
  const extracted = extractSource(markdown);
  const rootProfile = selectAlchSourceProfile(extracted.text);
  const rows = extracted.text.split(/\r?\n/).map((text, index) => ({ line: index + 1, text: text.replace(/\s+$/, "") })).filter((row) => row.text.trim() && !row.text.trimStart().startsWith("#"));
  const issues: CompilerIssue[] = [];
  let domainId = ""; let title = ""; let owner = "";
  let domainDeclarations = 0; let ownerDeclarations = 0;
  let logicProfile: string = SFOL_PROFILE;
  let logicDeclared = false;
  let applicationProfile = false;
  let compatibilityProfile = false;
  const sections: Section[] = [];
  let current: Section | null = null;
  let latestEntity = ""; let anonymousRule = 0;
  for (const row of rows) {
    if (/^\s/.test(row.text)) {
      if (!current) issues.push({ code: "TEXT_SYNTAX", path: `$line:${row.line}`, message: "indented line without a section" });
      else current.rows.push({ line: row.line, text: row.text.trim(), indent: row.text.length - row.text.trimStart().length });
      continue;
    }
    const domain = /^domain\s+([A-Za-z_][\w.-]*)(?:\s+"([^"]+)")?$/.exec(row.text);
    if (domain) { domainDeclarations++; domainId = domain[1]; title = domain[2] ?? domain[1]; current = null; continue; }
    const ownerMatch = /^owner\s+([A-Za-z_][\w.-]*)$/.exec(row.text);
    if (ownerMatch) { ownerDeclarations++; owner = ownerMatch[1]; current = null; continue; }
    if (row.text === "profile application-v1") {
      if (applicationProfile) issues.push({ code: "ALCH_PROFILE_CONFLICT", path: `$line:${row.line}`, message: "application profile declared more than once" });
      applicationProfile = true; current = null; continue;
    }
    if (row.text === "profile legacy-sfol-v1") {
      if (compatibilityProfile) issues.push({ code: "ALCH_PROFILE_CONFLICT", path: `$line:${row.line}`, message: "compatibility profile declared more than once" });
      compatibilityProfile = true; current = null; continue;
    }
    const logicMatch = /^logic\s+([A-Za-z_][\w.-]*)$/.exec(row.text);
    if (logicMatch) {
      if (logicDeclared) issues.push({ code: "SFOL_PROFILE", path: `$line:${row.line}`, message: "logic profile may be declared only once" });
      logicDeclared = true;
      logicProfile = logicMatch[1];
      if (logicProfile !== SFOL_PROFILE) issues.push({ code: "SFOL_PROFILE", path: `$line:${row.line}`, message: `only ${SFOL_PROFILE} is supported` });
      current = null;
      continue;
    }
    const enforcement = /^([A-Za-z_][\w.-]*)\s+--enforces-->\s+([A-Za-z_][\w.-]*)$/.exec(row.text);
    if (enforcement) {
      current = { kind: "rule-enforcement", id: enforcement[1]!, rows: [{ line: row.line, text: enforcement[2]!, indent: 0 }], line: row.line };
      sections.push(current); continue;
    }
    if (/^guard\s+/.test(row.text)) {
      issues.push({ code: "GUARD_RULE_REFERENCE", path: `$line:${row.line}`, message: "guard must occur in a declared consumer and reference one Rule" });
      current = null; continue;
    }
    const header = /^(formal-claim|entity|value-object|enum|actor|states|state-machine|invariant|rule|boundary|permission|action|operation|effect|event|example|query|calculation|mapping|policy|workflow|interface|subscription|publication|inbound-endpoint|outbound-call|outbound-write|persistence|runtime-profile|realization|verification-profile)\s+([A-Za-z_][\w.-]*):?$/.exec(row.text);
    if (header) { current = { kind: header[1], id: header[2], rows: [], line: row.line }; sections.push(current); if (header[1] === "entity") latestEntity = header[2]; continue; }
    if (/^states?:$/.test(row.text) && latestEntity) { current = { kind: "states", id: latestEntity, rows: [], line: row.line }; sections.push(current); continue; }
    if (row.text === "rule:") { current = { kind: "rule", id: `anonymous-rule-${++anonymousRule}`, rows: [], line: row.line }; sections.push(current); continue; }
    issues.push({ code: "TEXT_SYNTAX", path: `$line:${row.line}`, message: `unsupported declaration ${JSON.stringify(row.text)}` });
  }
  if (!domainId) issues.push({ code: "TEXT_REQUIRED", path: "$", message: "missing: domain <id> \"<title>\"" });
  if (!owner) issues.push({ code: "MISSING_OWNER", path: "$", message: "missing explicit owner <route>" });
  if (rootProfile.profile.id === "application-v1") {
    if (compatibilityProfile) issues.push({ code: "ALCH_PROFILE_CONFLICT", path: "$", message: "target and compatibility profiles cannot be combined" });
    if (domainDeclarations !== 1 || ownerDeclarations !== 1) issues.push({ code: "APPLICATION_IDENTITY", path: "$", message: "application source requires exactly one domain and one owner" });
    if (logicDeclared) issues.push({ code: "ALCH_PROFILE_CONFLICT", path: "$", message: "application-v1 cannot select legacy inline logic" });
    if (issues.length) throw new CompilationRejected(issues);
    return { source_kind: extracted.source_kind, source_profile: "application-v1", profile_selection: "explicit", diagnostics: [], carrier: { ...normalizeApplicationFormalSource({ id: domainId, title, owner }, sections) } };
  }
  if (domainDeclarations !== 1 || ownerDeclarations !== 1) issues.push({ code: "SOURCE_IDENTITY", path: "$", message: "source requires exactly one domain and one owner" });
  for (const section of sections.filter(s => s.kind === "formal-claim")) issues.push({ code: "ALCH_PROFILE_REQUIRED", path: `$line:${section.line}`, message: "FormalClaim declarations require profile application-v1" });
  for (const section of sections.filter(s => applicationIntegrationKinds.has(s.kind) || s.kind === "runtime-profile" || s.kind === "realization" || s.kind === "verification-profile")) issues.push({ code: "ALCH_PROFILE_REQUIRED", path: `$line:${section.line}`, message: "integration, runtime, realization and verification declarations require profile application-v1" });

  const terms: any[] = []; const facts: any[] = []; const states: any[] = []; const transitions: any[] = [];
  const rules: any[] = []; const actions: any[] = []; const effects: any[] = []; const permissions: any[] = []; const events: any[] = []; const examples: any[] = []; const boundaries: any[] = []; const edges: any[] = [];
  const queries: any[] = []; const calculations: any[] = []; const mappings: any[] = []; const policies: any[] = [];
  const valueObjects: any[] = []; const enums: any[] = []; const workflows: any[] = []; const interfaces: any[] = [];
  const factTypes = new Map<string, ScalarType>();

  for (const section of sections.filter((item) => item.kind === "entity")) {
    terms.push({ term_id: section.id, kind: "entity", meaning: `Declared entity ${section.id}.` });
    for (const row of section.rows) {
      const field = /^([A-Za-z_][\w.-]*):\s*(\w+)(?:\s+(required|optional))?$/.exec(row.text);
      if (!field || !scalarTypes.has(field[2] as ScalarType)) { issues.push({ code: "TEXT_FIELD", path: `$line:${row.line}`, message: "expected field: <type> [required|optional]" }); continue; }
      const type = field[2] as ScalarType; factTypes.set(field[1], type);
      facts.push({ fact_id: field[1], subject_ref: section.id, type, required: field[3] !== "optional", owner_route: owner });
    }
  }
  for (const section of sections.filter((item) => item.kind === "value-object")) {
    const fields: any[] = []; let equalityFields: string[] = [];
    for (const row of section.rows) {
      const equality = /^equality\s+(.+)$/.exec(row.text);
      if (equality) { equalityFields = words(equality[1]); continue; }
      const field = /^([A-Za-z_][\w.-]*):\s*(\w+)(?:\s+(required|optional))?$/.exec(row.text);
      if (!field || !scalarTypes.has(field[2] as ScalarType)) { issues.push({ code: "TEXT_VALUE_OBJECT", path: `$line:${row.line}`, message: "expected field: <type> [required|optional] or equality <field,...>" }); continue; }
      fields.push({ fact_id: field[1], subject_ref: null, type: field[2], required: field[3] !== "optional", owner_route: owner });
    }
    if (!fields.length) issues.push({ code: "VALUE_OBJECT_FIELDS", path: `$line:${section.line}`, message: "value-object requires at least one typed field" });
    if (!equalityFields.length) issues.push({ code: "VALUE_OBJECT_EQUALITY", path: `$line:${section.line}`, message: "value-object requires an equality field set" });
    valueObjects.push({ value_object_id: section.id, fields, equality_fields: equalityFields, source_refs: [`text:${section.line}`] });
    terms.push({ term_id: section.id, kind: "value-object", meaning: `Declared value object ${section.id}.` });
  }
  for (const section of sections.filter((item) => item.kind === "enum")) {
    const values: any[] = [];
    for (const row of section.rows) {
      const value = /^value\s+([A-Za-z_][\w.-]*)\s+"([^"]+)"$/.exec(row.text);
      if (!value) { issues.push({ code: "TEXT_ENUM", path: `$line:${row.line}`, message: "expected value <name> \"<description>\"" }); continue; }
      values.push({ value_id: value[1], description: value[2] });
    }
    if (!values.length) issues.push({ code: "ENUM_VALUES", path: `$line:${section.line}`, message: "enum requires at least one described value" });
    enums.push({ enum_id: section.id, values, source_refs: [`text:${section.line}`] });
    terms.push({ term_id: section.id, kind: "enum", meaning: `Declared enum ${section.id}.` });
  }
  for (const section of sections.filter((item) => item.kind === "actor")) {
    if (section.rows.length) issues.push({ code: "TEXT_ACTOR", path: `$line:${section.line}`, message: "actor declarations have no body" });
    terms.push({ term_id: section.id, kind: "actor", meaning: `Declared actor ${section.id}.` });
  }
  for (const section of sections.filter((item) => item.kind === "states")) {
    let initial = "";
    for (const row of section.rows) {
      const initialMatch = /^initial\s+([A-Za-z_][\w.-]*)$/.exec(row.text);
      if (initialMatch) { initial = initialMatch[1]; continue; }
      const transition = /^([A-Za-z_][\w.-]*)\s*->\s*([A-Za-z_][\w.-]*)(?:\s+when\s+([A-Za-z_][\w.-]*))?(?:\s+emits\s+([A-Za-z_][\w.-]*))?$/.exec(row.text);
      if (!transition) { issues.push({ code: "TEXT_TRANSITION", path: `$line:${row.line}`, message: "expected <from> -> <to> [when <rule>] [emits <event>]" }); continue; }
      for (const state of [transition[1], transition[2]]) if (!states.some((item) => item.state_id === state && item.subject_ref === section.id)) states.push({ state_id: state, subject_ref: section.id });
      transitions.push({ transition_id: `${section.id}-${transition[1]}-${transition[2]}`, subject_ref: section.id, from_state_ref: transition[1], to_state_ref: transition[2], trigger_ref: null, guard_rule_refs: transition[3] ? [transition[3]] : [], authority_boundary_ref: null, resulting_event_refs: transition[4] ? [transition[4]] : [] });
    }
    if (initial && !states.some((item) => item.state_id === initial && item.subject_ref === section.id)) states.push({ state_id: initial, subject_ref: section.id });
    for (const state of states.filter((item) => item.subject_ref === section.id)) if (!terms.some((term) => term.term_id === state.state_id)) terms.push({ term_id: state.state_id, kind: "state", meaning: `State ${state.state_id} of ${section.id}.` });
    if (initial) edges.push({ edge_id: `${section.id}-initial-${initial}`, type: "occupies", source_ref: section.id, target_ref: initial });
  }
  for (const section of sections.filter((item) => item.kind === "rule")) {
    if (section.rows.length !== 1) { issues.push({ code: "TEXT_RULE", path: `$line:${section.line}`, message: "rule requires exactly one predicate line" }); continue; }
    try {
      const named = /\s+is\s+considered\s+([A-Za-z_][\w.-]*)\.?$/i.exec(section.rows[0].text);
      const ruleId = section.id.startsWith("anonymous-rule-") && named ? named[1] : section.id;
      const cleaned = section.rows[0].text.replace(/^A\s+\w+\s+with\s+/i, "").replace(/\s+is\s+considered\s+[A-Za-z_][\w.-]*\.?$/i, "");
      const condition = parseSfolFormula(cleaned, factTypes);
      rules.push({ rule_id: ruleId, scope_refs: [], fact_refs: [...factTypes.keys()].filter((id) => JSON.stringify(condition).includes(`\"${id}\"`)), condition, consequence: "satisfied", exception_refs: [], owner_route: owner, source_refs: [`text:${section.line}`] });
    } catch (error) { if (error instanceof CompilationRejected) issues.push(...error.issues.map((issue) => ({ ...issue, path: `$line:${section.rows[0].line}${issue.path}` }))); else throw error; }
  }
  for (const section of sections.filter((item) => item.kind === "boundary")) {
    const declaredOwner = section.rows.find((row) => row.text.startsWith("owner "))?.text.slice(6);
    if (declaredOwner !== owner) issues.push({ code: "MISSING_OWNER", path: `$line:${section.line}`, message: "boundary owner must equal the declared domain owner" });
    boundaries.push({ boundary_id: section.id, owner_route: declaredOwner ?? "" });
  }
  for (const section of sections.filter((item) => item.kind === "event")) {
    const values = Object.fromEntries(section.rows.map((row) => { const match = /^(subject|payload|boundary)\s+(.+)$/.exec(row.text); if (!match) issues.push({ code: "TEXT_EVENT", path: `$line:${row.line}`, message: "expected subject, payload or boundary" }); return match ? [match[1], match[2]] : ["", ""]; }));
    events.push({ event_id: section.id, subject_refs: values.subject ? [values.subject] : [], payload_facts: words(values.payload ?? ""), trigger_refs: [], authority_boundary_ref: values.boundary ?? null, source_refs: [`text:${section.line}`] });
  }
  for (const section of sections.filter((item) => item.kind === "permission")) {
    const values = Object.fromEntries(section.rows.map((row) => { const match = /^(actor|action|when|boundary)\s+(.+)$/.exec(row.text); if (!match) issues.push({ code: "TEXT_PERMISSION", path: `$line:${row.line}`, message: "expected actor, action, when or boundary" }); return match ? [match[1], match[2]] : ["", ""]; }));
    const rule = rules.find((item) => item.rule_id === values.when);
    if (!rule) issues.push({ code: "UNRESOLVED_REFERENCE", path: `$line:${section.line}`, message: `permission rule ${values.when} is not declared` });
    permissions.push({ permission_id: section.id, actor_refs: values.actor ? [values.actor] : [], action_refs: values.action ? [values.action] : [], target_refs: [], scope_refs: [], condition: rule?.condition ?? { node: "literal", value_type: "boolean", value: false }, exception_refs: [], confirmation_policy_ref: null, authority_boundary_ref: values.boundary ?? "" });
  }
  for (const section of sections.filter((item) => item.kind === "effect")) {
    const values = Object.fromEntries(section.rows.map((row) => {
      const match = /^(pattern|binding|writes|emits|guarantee|on-failure|boundary)\s+(.+)$/.exec(row.text);
      if (!match) issues.push({ code: "TEXT_EFFECT", path: `$line:${row.line}`, message: "expected pattern, binding, writes, emits, guarantee, on-failure or boundary" });
      return match ? [match[1], match[2]] : ["", ""];
    }));
    for (const required of ["pattern", "binding", "writes", "emits", "guarantee", "on-failure", "boundary"]) {
      if (!values[required]) issues.push({ code: "TEXT_EFFECT_REQUIRED", path: `$line:${section.line}`, message: `effect ${section.id} requires ${required}` });
    }
    effects.push({ effect_id: section.id, pattern_ref: values.pattern ?? "", integration_binding_ref: values.binding ?? "", write_refs: words(values.writes ?? ""), event_refs: words(values.emits ?? ""), guarantee: values.guarantee ?? "", failure_continuation: values["on-failure"] ?? "", authority_boundary_ref: values.boundary ?? "" });
    terms.push({ term_id: section.id, kind: "effect", meaning: `Declared effect ${section.id}.` });
  }
  for (const section of sections.filter((item) => item.kind === "action" || item.kind === "operation")) {
    const multi: Record<string, string[]> = {};
    let stateChange = section.kind === "operation" ? "" : "no";
    for (const row of section.rows) {
      const stateChangeMatch = /^state-change\s+(yes|no)$/.exec(row.text);
      if (stateChangeMatch) { stateChange = stateChangeMatch[1]; continue; }
      const allowed = /^allowed only when\s+(.+)$/.exec(row.text);
      if (allowed) { try { const ruleId = `${section.id}-allowed`; const condition = parseSfolFormula(allowed[1], factTypes); rules.push({ rule_id: ruleId, scope_refs: [], fact_refs: [], condition, consequence: "satisfied", exception_refs: [], owner_route: owner, source_refs: [`text:${row.line}`] }); (multi.requires ??= []).push(ruleId); } catch (error) { if (error instanceof CompilationRejected) issues.push(...error.issues); else throw error; } continue; }
      const confirmation = /^requires human confirmation when\s+.+\s+is\s+([A-Za-z_][\w.-]*)\.?$/.exec(row.text);
      if (confirmation) { const rule = rules.find((item) => item.rule_id === confirmation[1]); if (!rule) issues.push({ code: "UNRESOLVED_REFERENCE", path: `$line:${row.line}`, message: `confirmation rule ${confirmation[1]} is not declared` }); else { if (!terms.some((term) => term.term_id === "Human")) terms.push({ term_id: "Human", kind: "actor", meaning: "Explicit human confirmation actor." }); const permissionId = `${section.id}-human-confirmation`; permissions.push({ permission_id: permissionId, actor_refs: ["Human"], action_refs: [section.id], target_refs: [], scope_refs: [], condition: rule.condition, exception_refs: [], confirmation_policy_ref: null, authority_boundary_ref: "" }); (multi.permission ??= []).push(permissionId); } continue; }
      const performs = /^performs\s+([A-Za-z_][\w.-]*)\s+using\s+([A-Za-z_][\w.-]*)$/.exec(row.text);
      if (performs) { (multi.performs ??= []).push(`${performs[1]}::${performs[2]}`); continue; }
      const match = /^(actor|subject|input|reads|writes|effects|requires|permission|boundary|emits)\s+(.+)$/.exec(row.text); if (!match) { issues.push({ code: "TEXT_ACTION", path: `$line:${row.line}`, message: "expected actor, subject, input, reads, writes, effects, requires, permission, boundary, emits, state-change yes, or performs <effect> using <binding>" }); continue; } (multi[match[1]] ??= []).push(...words(match[2]));
    }
    if (section.kind === "operation" && stateChange !== "yes") issues.push({ code: "OPERATION_STATE_CHANGE", path: `$line:${section.line}`, message: "operation requires state-change yes" });
    if (section.kind === "operation" && !(multi.writes?.length)) issues.push({ code: "OPERATION_WRITE_SET", path: `$line:${section.line}`, message: "operation requires a declared writes set" });
    actions.push({ action_id: section.id, declaration_kind: section.kind, actor_refs: multi.actor ?? [], subject_refs: multi.subject ?? [], input_facts: multi.input ?? [], read_refs: multi.reads ?? multi.subject ?? [], write_refs: multi.writes ?? [], effect_refs: multi.effects ?? [], precondition_rule_refs: multi.requires ?? [], permission_refs: multi.permission ?? [], confirmation_policy_ref: null, outcome_refs: multi.emits ?? [], performs: (multi.performs ?? []).map((value) => { const [effect_ref, integration_binding_ref] = value.split("::"); return { effect_ref, integration_binding_ref }; }), authority_boundary_ref: multi.boundary?.[0] ?? "" });
    if (section.kind === "operation") terms.push({ term_id: section.id, kind: "operation", meaning: `Declared operation ${section.id}.` });
  }
  for (const section of sections.filter((item) => item.kind === "example")) {
    const values = Object.fromEntries(section.rows.map((row) => { const match = /^(kind|expected|rules)\s+(.+)$/.exec(row.text); if (!match) issues.push({ code: "TEXT_EXAMPLE", path: `$line:${row.line}`, message: "expected kind, expected or rules" }); return match ? [match[1], match[2]] : ["", ""]; }));
    examples.push({ example_id: section.id, kind: values.kind ?? "positive", facts: {}, expected_interpretation: values.expected ?? "", affected_rule_refs: words(values.rules ?? ""), boundary_witness_refs: [], source_refs: [`text:${section.line}`] });
  }
  for (const section of sections.filter((item) => item.kind === "query")) {
    let source = ""; let inputs: string[] = []; let predicate: SfolFormula | null = null; const order_by: any[] = []; let limit: number | null = null; let projection: string[] = [];
    for (const row of section.rows) {
      const match = /^(source|inputs|where|order|limit|project)\s+(.+)$/.exec(row.text);
      if (!match) { issues.push({ code: "TEXT_QUERY", path: `$line:${row.line}`, message: "expected source, inputs, where, order, limit or project" }); continue; }
      try {
        if (match[1] === "source") source = match[2];
        else if (match[1] === "inputs") inputs = words(match[2]);
        else if (match[1] === "where") predicate = parseSfolFormula(match[2], factTypes);
        else if (match[1] === "order") { const order = /^([A-Za-z_][\w.-]*)\s+(asc|desc)$/.exec(match[2]); if (!order) throw new CompilationRejected([{ code: "QUERY_ORDER", path: "$", message: "expected order <field> asc|desc" }]); order_by.push({ field_ref: order[1], direction: order[2] }); }
        else if (match[1] === "limit") limit = Number(match[2]);
        else projection = words(match[2]);
      } catch (error) { if (error instanceof CompilationRejected) issues.push(...error.issues.map((issue) => ({ ...issue, path: `$line:${row.line}${issue.path}` }))); else throw error; }
    }
    queries.push({ query_id: section.id, source_ref: source, input_facts: inputs, predicate, order_by, limit, projection, source_refs: [`text:${section.line}`] });
  }
  for (const section of sections.filter((item) => item.kind === "calculation")) {
    let inputs: string[] = []; let expression: SfolUInt64Term | null = null; let rounding = "reject";
    for (const row of section.rows) {
      const match = /^(inputs|expression|rounding)\s+(.+)$/.exec(row.text);
      if (!match) { issues.push({ code: "TEXT_CALCULATION", path: `$line:${row.line}`, message: "expected inputs, expression or rounding" }); continue; }
      try {
        if (match[1] === "inputs") inputs = words(match[2]);
        else if (match[1] === "expression") expression = parseSfolUInt64Term(match[2], new Set(inputs));
        else rounding = match[2];
      } catch (error) { if (error instanceof CompilationRejected) issues.push(...error.issues.map((issue) => ({ ...issue, path: `$line:${row.line}${issue.path}` }))); else throw error; }
    }
    calculations.push({ calculation_id: section.id, input_facts: inputs, expression, rounding, source_refs: [`text:${section.line}`] });
  }
  for (const section of sections.filter((item) => item.kind === "mapping")) {
    let source = ""; let target = ""; let total = true; const clauses: any[] = [];
    for (const row of section.rows) {
      const simple = /^(source|target|total)\s+(.+)$/.exec(row.text);
      if (simple) { if (simple[1] === "source") source = simple[2]; else if (simple[1] === "target") target = simple[2]; else total = simple[2] === "true"; continue; }
      const copy = /^field\s+([A-Za-z_][\w.-]*)\s+<-\s+([A-Za-z_][\w.-]*)$/.exec(row.text);
      if (copy) { clauses.push({ target_field: copy[1], source_field: copy[2], default_value: null }); continue; }
      const fallback = /^field\s+([A-Za-z_][\w.-]*)\s+default\s+(\w+)\s+(.+)$/.exec(row.text);
      if (fallback && scalarTypes.has(fallback[2] as ScalarType)) { try { clauses.push({ target_field: fallback[1], source_field: null, default_value: { value_type: fallback[2], value: JSON.parse(fallback[3]) } }); } catch { issues.push({ code: "MAPPING_DEFAULT", path: `$line:${row.line}`, message: "default value must be JSON" }); } continue; }
      issues.push({ code: "TEXT_MAPPING", path: `$line:${row.line}`, message: "expected source, target, total, field <target> <- <source>, or field <target> default <type> <json>" });
    }
    mappings.push({ mapping_id: section.id, source_ref: source, target_ref: target, total, clauses, source_refs: [`text:${section.line}`] });
  }
  for (const section of sections.filter((item) => item.kind === "policy")) {
    let inputs: string[] = []; const cases: any[] = []; let defaultTarget = "";
    for (const row of section.rows) {
      const input = /^inputs\s+(.+)$/.exec(row.text); if (input) { inputs = words(input[1]); continue; }
      const item = /^case\s+(.+)\s+->\s+([A-Za-z_][\w.-]*)$/.exec(row.text);
      if (item) { try { cases.push({ predicate: parseSfolFormula(item[1], factTypes), target_ref: item[2] }); } catch (error) { if (error instanceof CompilationRejected) issues.push(...error.issues.map((issue) => ({ ...issue, path: `$line:${row.line}${issue.path}` }))); else throw error; } continue; }
      const fallback = /^default\s+([A-Za-z_][\w.-]*)$/.exec(row.text); if (fallback) { defaultTarget = fallback[1]; continue; }
      issues.push({ code: "TEXT_POLICY", path: `$line:${row.line}`, message: "expected inputs, case <predicate> -> <target>, or default <target>" });
    }
    policies.push({ policy_id: section.id, input_facts: inputs, cases, default_target_ref: defaultTarget, source_refs: [`text:${section.line}`] });
  }
  for (const section of sections.filter((item) => item.kind === "workflow")) {
    let scope = ""; let steps: string[] = [];
    for (const row of section.rows) {
      const scopeMatch = /^scope\s+(intra-feature|cross-feature)$/.exec(row.text); if (scopeMatch) { scope = scopeMatch[1]; continue; }
      const stepsMatch = /^steps\s+(.+)$/.exec(row.text); if (stepsMatch) { steps = words(stepsMatch[1]); continue; }
      issues.push({ code: "TEXT_WORKFLOW", path: `$line:${row.line}`, message: "expected scope intra-feature|cross-feature or steps <operation,...>" });
    }
    if (!scope) issues.push({ code: "WORKFLOW_SCOPE", path: `$line:${section.line}`, message: "workflow requires one admitted scope" });
    if (steps.length < 2) issues.push({ code: "WORKFLOW_STEPS", path: `$line:${section.line}`, message: "workflow requires at least two ordered steps" });
    workflows.push({ workflow_id: section.id, scope, step_refs: steps, source_refs: [`text:${section.line}`] });
    terms.push({ term_id: section.id, kind: "workflow", meaning: `Declared workflow ${section.id}.` });
  }
  for (const section of sections.filter((item) => item.kind === "interface")) {
    let interfaceKind = ""; let exposures: string[] = [];
    for (const row of section.rows) {
      const kindMatch = /^kind\s+(internal|external)$/.exec(row.text); if (kindMatch) { interfaceKind = kindMatch[1]; continue; }
      const exposesMatch = /^exposes\s+(.+)$/.exec(row.text); if (exposesMatch) { exposures = words(exposesMatch[1]); continue; }
      issues.push({ code: "TEXT_INTERFACE", path: `$line:${row.line}`, message: "expected kind internal|external or exposes <operation-or-query,...>" });
    }
    if (!interfaceKind) issues.push({ code: "INTERFACE_KIND", path: `$line:${section.line}`, message: "interface requires kind internal or external" });
    if (!exposures.length) issues.push({ code: "INTERFACE_EXPOSURES", path: `$line:${section.line}`, message: "interface requires at least one exposed operation or query" });
    interfaces.push({ interface_id: section.id, interface_kind: interfaceKind, exposure_refs: exposures, source_refs: [`text:${section.line}`] });
    terms.push({ term_id: section.id, kind: "interface", meaning: `Declared interface ${section.id}.` });
  }
  if (issues.length) throw new CompilationRejected(issues);
  return {
    source_kind: extracted.source_kind,
    source_profile: "legacy-sfol-v1",
    profile_selection: rootProfile.selection,
    diagnostics: [{ code: rootProfile.selection === "explicit" ? "ALCH_LEGACY_COMPATIBILITY" : "ALCH_LEGACY_DEFAULT", path: "$",
      message: rootProfile.selection === "explicit" ? "Explicit legacy SFOL compatibility syntax; not application-v1." : "Historical SFOL compatibility default retained; declare profile legacy-sfol-v1 to make selection explicit. No migration was performed." }],
    carrier: {
      schema_version: "cav2.alchlang.carrier/v2-candidate",
      logic_profile: logicProfile,
      identity: { domain_id: domainId, title }, owners: [{ owner_route: owner }], terms, edges, facts, value_objects: valueObjects, enums, rules, events, states, transitions, effects, actions, permissions, queries, calculations, mappings, policies, workflows, interfaces, examples,
      authority: { authority_effect: "none", boundaries }, residue: []
    }
  };
}
