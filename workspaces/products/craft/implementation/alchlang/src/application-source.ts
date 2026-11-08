import { CompilationRejected } from "./model.js";
import type { ApplicationSourceSection } from "./formal-claim.js";
import { normalizeApplicationInterface } from "./application-interface.js";

export type ApplicationType =
  | { kind: "scalar"; name: "String" | "Bool" | "UInt64" }
  | { kind: "declaration"; ref: string }
  | { kind: "public-contract"; interface: string; contract: string }
  | { kind: "reference"; entity: string; field: string }
  | { kind: "sum"; enum: string }
  | { kind: "optional" | "list" | "set"; element: ApplicationType };
export interface ApplicationField { name: string; type: ApplicationType; source_line: number }
interface DeclarationMetadata { id: string; source_line: number; ontology: string | null; meaning: string | null }
export interface ApplicationDataDeclaration extends DeclarationMetadata {
  kind: "entity" | "value-object";
  fields: ApplicationField[];
  identity: string | null;
}
export interface ApplicationEventDeclaration extends DeclarationMetadata {
  kind: "event";
  fields: ApplicationField[];
  event_type: string | null;
  version: string | null;
  occurrence_id: ApplicationField | null;
  occurred_at_policy: "required" | "generated" | null;
}
export interface ApplicationEnumDeclaration extends DeclarationMetadata {
  kind: "enum";
  values: Array<{ name: string; meaning: string | null; source_line: number }>;
}
export interface ApplicationOperationDeclaration extends DeclarationMetadata {
  kind: "operation";
  input: ApplicationType;
  output: ApplicationType;
  reads: string[];
  writes: string[];
  produces: string[];
  requires: string[];
}
export interface ApplicationMappingDeclaration extends DeclarationMetadata {
  kind: "mapping";
  inputs: ApplicationField[];
  target: string;
  total: boolean;
  fields: Array<{ target: string; path: string[]; source_line: number }>;
}
export interface ApplicationQueryDeclaration extends DeclarationMetadata {
  kind: "query";
  inputs: ApplicationField[];
  source: { name: string; entity: string; source_line: number };
  output: ApplicationType;
  rule: string;
  bindings: Array<{ parameter: string; path: string[]; source_line: number }>;
}
export type ApplicationNumericExpression =
  | { op: "literal"; value: string }
  | { op: "input"; name: string }
  | { op: "add" | "subtract" | "multiply" | "divide"; left: ApplicationNumericExpression; right: ApplicationNumericExpression };
export interface ApplicationCalculationDeclaration extends DeclarationMetadata {
  kind: "calculation";
  inputs: ApplicationField[];
  result: { kind: "scalar"; name: "UInt64" };
  expression: ApplicationNumericExpression;
  rounding: "floor" | "ceil" | "reject";
}
export interface ApplicationPolicyDeclaration extends DeclarationMetadata {
  kind: "policy";
  inputs: ApplicationField[];
  input_names: string[];
  cases: Array<{ rule: string; target: string; source_line: number }>;
  bindings: Array<{ rule: string; parameter: string; path: string[]; source_line: number }>;
  default_target: string;
  applies: string[];
}
export interface ApplicationWorkflowDeclaration extends DeclarationMetadata {
  kind: "workflow";
  scope: "intra-feature" | "cross-feature";
  steps: string[];
  inputs: ApplicationField[];
  rules: string[];
  bindings: Array<{ rule: string; parameter: string; path: string[]; source_line: number }>;
}
export interface ApplicationStateMachineDeclaration extends DeclarationMetadata {
  kind: "state-machine";
  subject: string | null;
  inputs: ApplicationField[];
  states: string[];
  initial: string;
  transitions: Array<{ id: string; from: string; to: string; rule: string | null; trigger_event: string | null; result_event: string | null;
    bindings: Array<{ parameter: string; path: string[]; source_line: number }>; source_line: number }>;
}
export type ApplicationPublicType = Extract<ApplicationType, { kind: "scalar" | "declaration" | "reference" | "sum" }>
  | { kind: "contract"; ref: string }
  | { kind: "optional" | "list" | "set"; element: ApplicationPublicType };
export interface ApplicationInterfaceDeclaration extends DeclarationMetadata {
  kind: "interface";
  boundary_kind: "external" | "internal";
  version: string;
  compatibility: "exact" | "backward";
  contracts: { id: string; source_line: number; fields: { name: string; type: ApplicationPublicType; source_line: number }[] }[];
  members: { operation: string; request: ApplicationPublicType; result: ApplicationPublicType; source_line: number }[];
}
export type ApplicationDeclaration = ApplicationDataDeclaration | ApplicationEventDeclaration | ApplicationEnumDeclaration | ApplicationOperationDeclaration | ApplicationMappingDeclaration | ApplicationQueryDeclaration | ApplicationCalculationDeclaration | ApplicationPolicyDeclaration | ApplicationWorkflowDeclaration | ApplicationStateMachineDeclaration | ApplicationInterfaceDeclaration;
const namePattern = /^[A-Za-z_][\w-]*$/;
function reject(code: string, line: number, message: string): never {
  throw new CompilationRejected([{ code, path: `$line:${line}`, message }]);
}

function parseNumericExpression(source: string, line: number, inputs: ReadonlySet<string>): ApplicationNumericExpression {
  const tokens = source.match(/[A-Za-z_][\w-]*|0|[1-9][0-9]*|[(),]/g) ?? [];
  if (tokens.join("") !== source.replace(/\s/g, "")) reject("APPLICATION_CALCULATION", line, "invalid numeric expression");
  let index = 0; let nodes = 0;
  const read = (depth: number): ApplicationNumericExpression => {
    if (++nodes > 4096 || depth > 32) reject("APPLICATION_CALCULATION", line, "numeric expression exceeds bounds");
    const token = tokens[index++];
    if (!token) reject("APPLICATION_CALCULATION", line, "numeric expression is incomplete");
    if (/^(0|[1-9][0-9]*)$/.test(token)) {
      if (token.length > 20 || BigInt(token) > 18446744073709551615n) reject("APPLICATION_CALCULATION", line, "literal must be canonical UInt64");
      return { op: "literal", value: token };
    }
    if (["add", "subtract", "multiply", "divide"].includes(token)) {
      if (tokens[index++] !== "(") reject("APPLICATION_CALCULATION", line, "operator requires (left, right)");
      const left = read(depth + 1); if (tokens[index++] !== ",") reject("APPLICATION_CALCULATION", line, "operator requires two terms");
      const right = read(depth + 1); if (tokens[index++] !== ")") reject("APPLICATION_CALCULATION", line, "operator requires closing )");
      return { op: token as "add" | "subtract" | "multiply" | "divide", left, right };
    }
    if (!inputs.has(token)) reject("APPLICATION_CALCULATION", line, `undeclared numeric input ${token}`);
    return { op: "input", name: token };
  };
  const result = read(0); if (index !== tokens.length) reject("APPLICATION_CALCULATION", line, "unexpected trailing numeric expression");
  return result;
}

export function parseApplicationType(source: string, line: number): ApplicationType {
  const tokens = source.match(/->|[A-Za-z_][\w-]*|[<>.]/g) ?? [];
  if (tokens.join("") !== source.replace(/\s/g, "")) reject("APPLICATION_TYPE", line, `invalid type ${source}`);
  let index = 0;
  const read = (depth: number): ApplicationType => {
    if (depth > 32) reject("APPLICATION_TYPE_DEPTH", line, "type nesting exceeds 32");
    const token = tokens[index++];
    if (token === "->") {
      const entity = tokens[index++]; const dot = tokens[index++]; const field = tokens[index++];
      if (!entity || !field || !namePattern.test(entity) || !namePattern.test(field) || dot !== ".") reject("APPLICATION_TYPE", line, "expected -> Entity.identityField");
      return { kind: "reference", entity: entity!, field: field! };
    }
    if (token === "optional" || token === "list" || token === "set") {
      if (tokens[index++] !== "<") reject("APPLICATION_TYPE", line, "expected type constructor opening <");
      const element = read(depth + 1);
      if (tokens[index++] !== ">") reject("APPLICATION_TYPE", line, "expected type constructor closing >");
      return { kind: token, element };
    }
    if (token === "sum") {
      if (tokens[index++] !== "<") reject("APPLICATION_TYPE", line, "expected sum opening <");
      const enumName = tokens[index++];
      if (!enumName || !namePattern.test(enumName) || tokens[index++] !== ">") reject("APPLICATION_TYPE", line, "sum must select one declared Enum");
      return { kind: "sum", enum: enumName };
    }
    if (token === "String" || token === "Bool" || token === "UInt64") return { kind: "scalar", name: token };
    if (!token || !namePattern.test(token)) reject("APPLICATION_TYPE", line, "expected scalar or declared type");
    if (tokens[index] === ".") {
      index++; const contract = tokens[index++];
      if (!contract || !namePattern.test(contract)) reject("APPLICATION_TYPE", line, "expected Interface.PublicContract");
      return { kind: "public-contract", interface: token!, contract: contract! };
    }
    return { kind: "declaration", ref: token! };
  };
  const type = read(0);
  if (index !== tokens.length) reject("APPLICATION_TYPE", line, "unexpected trailing type tokens");
  return type;
}

/** Closed declaration decoding for the current application construction stage. */
export function normalizeApplicationDeclarations(sections: ApplicationSourceSection[], ruleIds: ReadonlySet<string>, externalWriteMembers: ReadonlySet<string> = new Set()): ApplicationDeclaration[] {
  const declarations = sections.map((section): ApplicationDeclaration => {
    const metadata: DeclarationMetadata = { id: section.id, source_line: section.line, ontology: null, meaning: null };
    const rows: ApplicationSourceSection["rows"] = [];
    for (const row of section.rows) {
      const match = section.kind === "interface" && row.indent !== section.rows[0]?.indent ? null : /^(ontology|meaning)\s+("(?:[^"\\]|\\.)*")$/.exec(row.text);
      if (!match) { rows.push(row); continue; }
      const key = match[1] as "ontology" | "meaning";
      if (metadata[key] !== null) reject("APPLICATION_METADATA", row.line, `duplicate ${key}`);
      try { metadata[key] = JSON.parse(match[2]!); } catch { reject("APPLICATION_METADATA", row.line, "invalid quoted text"); }
      if (!metadata[key]?.trim()) reject("APPLICATION_METADATA", row.line, "empty metadata");
    }
    if (section.kind === "interface") return { ...metadata, ...normalizeApplicationInterface({ ...section, rows }, parseApplicationType) };
    if (section.kind === "entity" || section.kind === "value-object" || section.kind === "event") {
      const fields: ApplicationField[] = []; let identity: string | null = null;
      let eventType: string | null = null; let version: string | null = null;
      let occurrence: ApplicationField | null = null; let occurredAt: "required" | "generated" | null = null;
      for (const row of rows) {
        if (section.kind === "event") {
          const clause = /^(event-type|version|occurrence-id|occurred-at)\s+(.+)$/.exec(row.text);
          if (clause) {
            const value = clause[2]!;
            if (clause[1] === "event-type") {
              if (eventType !== null || !/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(value)) reject("APPLICATION_EVENT", row.line, "declare one canonical event-type");
              eventType = value;
            } else if (clause[1] === "version") {
              if (version !== null || !/^[1-9][0-9]*$/.test(value)) reject("APPLICATION_EVENT", row.line, "declare one positive integer Event version");
              version = value;
            } else if (clause[1] === "occurred-at") {
              if (occurredAt !== null || !["required", "generated"].includes(value)) reject("APPLICATION_EVENT", row.line, "declare one required or generated occurrence time policy");
              occurredAt = value as "required" | "generated";
            } else {
              const field = /^([A-Za-z_][\w-]*)\s+(.+)$/.exec(value);
              if (occurrence || !field) reject("APPLICATION_EVENT", row.line, "declare one occurrence-id name Type");
              const type = parseApplicationType(field![2]!, row.line);
              if (type.kind === "optional" || type.kind === "list" || type.kind === "set") reject("APPLICATION_EVENT", row.line, "occurrence identity must be one required value");
              occurrence = { name: field![1]!, type, source_line: row.line };
            }
            continue;
          }
        }
        const id = /^identity\s+([A-Za-z_][\w-]*)$/.exec(row.text);
        if (id) {
          if (section.kind !== "entity" || identity !== null) reject("APPLICATION_IDENTITY", row.line, "identity belongs to an Entity and is declared once");
          identity = id[1]!; continue;
        }
        const field = /^([A-Za-z_][\w-]*)(?::\s*|\s+)(.+)$/.exec(row.text);
        if (!field) reject("APPLICATION_FIELD", row.line, "expected fieldName Type or fieldName -> Entity.identityField");
        if (fields.some(f => f.name === field![1])) reject("APPLICATION_FIELD", row.line, "duplicate field name");
        fields.push({ name: field![1]!, type: parseApplicationType(field![2]!, row.line), source_line: row.line });
      }
      if (!fields.length && section.kind !== "event") reject("APPLICATION_FIELD", section.line, "data declaration requires fields");
      if (identity && !fields.some(f => f.name === identity && f.type.kind === "scalar")) reject("APPLICATION_IDENTITY", section.line, "identity must select a declared scalar field");
      if (section.kind === "event") return { ...metadata, kind: "event", fields, event_type: eventType,
        version, occurrence_id: occurrence, occurred_at_policy: occurredAt };
      return { ...metadata, kind: section.kind, fields, identity };
    }
    if (section.kind === "enum") {
      const values: ApplicationEnumDeclaration["values"] = [];
      for (const row of rows) {
        const match = /^value\s+([A-Za-z_][\w-]*)(?:\s+("(?:[^"\\]|\\.)*"))?$/.exec(row.text);
        if (!match) reject("APPLICATION_ENUM", row.line, "expected value Name with optional quoted meaning");
        if (values.some(v => v.name === match![1])) reject("APPLICATION_ENUM", row.line, "duplicate enum value");
        let meaning: string | null = null;
        try { meaning = match![2] ? JSON.parse(match![2]) : null; } catch { reject("APPLICATION_ENUM", row.line, "invalid enum meaning"); }
        values.push({ name: match![1]!, meaning, source_line: row.line });
      }
      if (!values.length) reject("APPLICATION_ENUM", section.line, "enum requires values");
      return { ...metadata, kind: "enum", values };
    }
    if (section.kind === "query") {
      const inputs: ApplicationField[] = []; const bindings: ApplicationQueryDeclaration["bindings"] = [];
      let source: ApplicationQueryDeclaration["source"] | undefined; let output: ApplicationType | undefined; let rule: string | undefined;
      for (const row of rows) {
        let match: RegExpExecArray | null;
        if ((match = /^input\s+([A-Za-z_][\w-]*)\s+(.+)$/.exec(row.text))) {
          if (inputs.some(p => p.name === match![1])) reject("APPLICATION_QUERY", row.line, "duplicate Query input");
          inputs.push({ name: match[1]!, type: parseApplicationType(match[2]!, row.line), source_line: row.line });
        } else if ((match = /^source\s+([A-Za-z_][\w-]*)\s+([A-Za-z_][\w-]*)$/.exec(row.text))) {
          if (source) reject("APPLICATION_QUERY", row.line, "duplicate Query source");
          source = { name: match[1]!, entity: match[2]!, source_line: row.line };
        } else if ((match = /^output\s+(.+)$/.exec(row.text))) {
          if (output) reject("APPLICATION_QUERY", row.line, "duplicate Query output"); output = parseApplicationType(match[1]!, row.line);
        } else if ((match = /^where\s+([A-Za-z_][\w-]*)$/.exec(row.text))) {
          if (rule) reject("APPLICATION_QUERY", row.line, "Query selects one declared Rule"); rule = match[1]!;
        } else if ((match = /^bind\s+([A-Za-z_][\w-]*)\s+<-\s+([A-Za-z_][\w-]*(?:\.[A-Za-z_][\w-]*)*)$/.exec(row.text))) {
          if (bindings.some(b => b.parameter === match![1])) reject("APPLICATION_QUERY", row.line, "duplicate Rule input binding");
          bindings.push({ parameter: match[1]!, path: match[2]!.split("."), source_line: row.line });
        } else reject("APPLICATION_QUERY", row.line, "expected named input/source, output, declared Rule and explicit bind; no inline formula or call");
      }
      if (!source || !output || !rule || !bindings.length) reject("APPLICATION_QUERY", section.line, "Query needs an explicit source, output, Rule and input bindings");
      if (!ruleIds.has(rule!)) reject("APPLICATION_QUERY_RULE", section.line, "Query condition must reference a declared Rule");
      if (inputs.some(p => p.name === source!.name)) reject("APPLICATION_QUERY", section.line, "source row name collides with an input");
      return { ...metadata, kind: "query", inputs, source: source!, output: output!, rule: rule!, bindings };
    }
    if (section.kind === "mapping") {
      const inputs: ApplicationField[] = []; const fields: ApplicationMappingDeclaration["fields"] = [];
      let target: string | undefined; let total: boolean | undefined;
      for (const row of rows) {
        let match: RegExpExecArray | null;
        if ((match = /^input\s+([A-Za-z_][\w-]*)\s+(.+)$/.exec(row.text))) {
          if (inputs.some(p => p.name === match![1])) reject("APPLICATION_MAPPING", row.line, "duplicate Mapping input");
          inputs.push({ name: match[1]!, type: parseApplicationType(match[2]!, row.line), source_line: row.line });
        } else if ((match = /^target\s+([A-Za-z_][\w-]*(?:\.[A-Za-z_][\w-]*)?)$/.exec(row.text))) {
          if (target !== undefined) reject("APPLICATION_MAPPING", row.line, "duplicate Mapping target"); target = match[1]!;
        } else if ((match = /^total\s+(true|false)$/.exec(row.text))) {
          if (total !== undefined) reject("APPLICATION_MAPPING", row.line, "duplicate Mapping totality"); total = match[1] === "true";
        } else if ((match = /^field\s+([A-Za-z_][\w-]*)\s+<-\s+([A-Za-z_][\w-]*(?:\.[A-Za-z_][\w-]*)*)$/.exec(row.text))) {
          if (fields.some(f => f.target === match![1])) reject("APPLICATION_MAPPING", row.line, "duplicate Mapping target field");
          fields.push({ target: match[1]!, path: match[2]!.split("."), source_line: row.line });
        } else reject("APPLICATION_MAPPING", row.line, "expected named input, target, total or field target <- input.path; implicit calls are forbidden");
      }
      if (!inputs.length || !target || total === undefined || !fields.length) reject("APPLICATION_MAPPING", section.line, "Mapping requires explicit inputs, target, totality and field bindings");
      return { ...metadata, kind: "mapping", inputs, target: target!, total: total!, fields };
    }
    if (section.kind === "calculation") {
      const inputs: ApplicationField[] = []; let result: string | undefined; let expression: ApplicationNumericExpression | undefined; let rounding: ApplicationCalculationDeclaration["rounding"] | undefined;
      for (const row of rows) {
        let match: RegExpExecArray | null;
        if ((match = /^input\s+([A-Za-z_][\w-]*)\s+(.+)$/.exec(row.text))) {
          if (inputs.some(input => input.name === match![1])) reject("APPLICATION_CALCULATION", row.line, "duplicate Calculation input");
          const type = parseApplicationType(match[2]!, row.line);
          if (type.kind !== "scalar" || type.name !== "UInt64") reject("APPLICATION_CALCULATION", row.line, "Calculation inputs must be UInt64");
          inputs.push({ name: match[1]!, type, source_line: row.line });
        } else if ((match = /^result\s+(\S+)$/.exec(row.text))) {
          if (result !== undefined || match[1] !== "UInt64") reject("APPLICATION_CALCULATION", row.line, "declare one UInt64 result"); result = match[1];
        } else if ((match = /^expression\s+(.+)$/.exec(row.text))) {
          if (expression !== undefined) reject("APPLICATION_CALCULATION", row.line, "duplicate expression");
          expression = parseNumericExpression(match[1]!, row.line, new Set(inputs.map(input => input.name)));
        } else if ((match = /^rounding\s+(floor|ceil|reject)$/.exec(row.text))) {
          if (rounding !== undefined) reject("APPLICATION_CALCULATION", row.line, "duplicate rounding"); rounding = match[1] as ApplicationCalculationDeclaration["rounding"];
        } else reject("APPLICATION_CALCULATION", row.line, "expected input, UInt64 result, expression or rounding");
      }
      if (!inputs.length || result !== "UInt64" || !expression || !rounding) reject("APPLICATION_CALCULATION", section.line, "Calculation requires inputs, UInt64 result, expression and rounding");
      return { ...metadata, kind: "calculation", inputs, result: { kind: "scalar", name: "UInt64" }, expression, rounding };
    }
    if (section.kind === "policy") {
      const inputs: ApplicationField[] = []; const inputNames: string[] = []; const cases: ApplicationPolicyDeclaration["cases"] = [];
      const bindings: ApplicationPolicyDeclaration["bindings"] = []; let defaultTarget: string | undefined; let applies: string[] | undefined;
      for (const row of rows) {
        let match: RegExpExecArray | null;
        if ((match = /^input\s+([A-Za-z_][\w-]*)\s+(.+)$/.exec(row.text))) {
          if (inputs.some(input => input.name === match![1])) reject("APPLICATION_POLICY", row.line, "duplicate Policy input");
          inputs.push({ name: match[1]!, type: parseApplicationType(match[2]!, row.line), source_line: row.line });
          inputNames.push(match[1]!);
        } else if ((match = /^inputs\s+(.+)$/.exec(row.text))) {
          if (inputNames.length) reject("APPLICATION_POLICY", row.line, "duplicate Policy inputs");
          for (const name of match[1]!.split(",").map(value => value.trim())) {
            if (!namePattern.test(name) || inputNames.includes(name)) reject("APPLICATION_POLICY", row.line, "expected unique Policy input names");
            inputNames.push(name);
          }
        } else if ((match = /^case\s+([A-Za-z_][\w-]*)\s*->\s*([A-Za-z_][\w-]*)$/.exec(row.text))) {
          if (cases.some(item => item.rule === match![1])) reject("APPLICATION_POLICY", row.line, "duplicate Policy Rule case");
          cases.push({ rule: match[1]!, target: match[2]!, source_line: row.line });
        } else if ((match = /^bind\s+([A-Za-z_][\w-]*)\.([A-Za-z_][\w-]*)\s+<-\s+([A-Za-z_][\w-]*(?:\.[A-Za-z_][\w-]*)*)$/.exec(row.text))) {
          if (bindings.some(item => item.rule === match![1] && item.parameter === match![2])) reject("APPLICATION_POLICY", row.line, "duplicate Policy Rule argument binding");
          bindings.push({ rule: match[1]!, parameter: match[2]!, path: match[3]!.split("."), source_line: row.line });
        } else if ((match = /^default\s+([A-Za-z_][\w-]*)$/.exec(row.text))) {
          if (defaultTarget !== undefined) reject("APPLICATION_POLICY", row.line, "duplicate Policy default"); defaultTarget = match[1];
        } else if ((match = /^applies\s+(.+)$/.exec(row.text))) {
          if (applies !== undefined) reject("APPLICATION_POLICY", row.line, "duplicate Policy applies list");
          applies = match[1]!.split(",").map(value => value.trim());
          if (!applies.length || applies.some(value => !namePattern.test(value)) || new Set(applies).size !== applies.length) reject("APPLICATION_POLICY", row.line, "expected unique Policy targets");
        } else if (/^case\s+/.test(row.text)) reject("POLICY_RULE_REFERENCE", row.line, "Policy cases must reference one declared Rule");
        else reject("APPLICATION_POLICY", row.line, "expected inputs, case Rule -> target, explicit Rule binding, default target or applies list");
      }
      if (!cases.length || !defaultTarget) reject("APPLICATION_POLICY", section.line, "Policy requires cases and a default target");
      const targets = [...new Set([...cases.map(item => item.target), defaultTarget])];
      if (applies && JSON.stringify([...applies].sort()) !== JSON.stringify([...targets].sort())) reject("APPLICATION_POLICY", section.line, "applies must exactly cover case and default targets");
      return { ...metadata, kind: "policy", inputs, input_names: inputNames, cases, bindings, default_target: defaultTarget!, applies: applies ?? targets };
    }
    if (section.kind === "workflow") {
      let scope: ApplicationWorkflowDeclaration["scope"] | undefined; let steps: string[] | undefined;
      const inputs: ApplicationField[] = []; const rules: string[] = []; const bindings: ApplicationWorkflowDeclaration["bindings"] = [];
      for (const row of rows) {
        let match: RegExpExecArray | null;
        if ((match = /^scope\s+(intra-feature|cross-feature)$/.exec(row.text))) {
          if (scope !== undefined) reject("APPLICATION_WORKFLOW", row.line, "duplicate Workflow scope"); scope = match[1] as ApplicationWorkflowDeclaration["scope"];
        } else if ((match = /^input\s+([A-Za-z_][\w-]*)\s+(.+)$/.exec(row.text))) {
          if (inputs.some(input => input.name === match![1])) reject("APPLICATION_WORKFLOW", row.line, "duplicate Workflow input");
          inputs.push({ name: match[1]!, type: parseApplicationType(match[2]!, row.line), source_line: row.line });
        } else if ((match = /^requires\s+([A-Za-z_][\w-]*)$/.exec(row.text))) {
          if (rules.includes(match[1]!)) reject("APPLICATION_WORKFLOW", row.line, "duplicate Workflow Rule"); rules.push(match[1]!);
        } else if ((match = /^bind\s+([A-Za-z_][\w-]*)\.([A-Za-z_][\w-]*)\s+<-\s+([A-Za-z_][\w-]*(?:\.[A-Za-z_][\w-]*)*)$/.exec(row.text))) {
          if (bindings.some(item => item.rule === match![1] && item.parameter === match![2])) reject("APPLICATION_WORKFLOW", row.line, "duplicate Workflow Rule argument binding");
          bindings.push({ rule: match[1]!, parameter: match[2]!, path: match[3]!.split("."), source_line: row.line });
        } else if ((match = /^steps\s+(.+)$/.exec(row.text))) {
          if (steps !== undefined) reject("APPLICATION_WORKFLOW", row.line, "duplicate Workflow steps"); steps = match[1]!.split(",").map(value => value.trim());
          if (steps.some(value => !namePattern.test(value))) reject("APPLICATION_WORKFLOW", row.line, "invalid Workflow step");
        } else if (/^(guard|where|when)\s+/.test(row.text)) reject("GUARD_RULE_REFERENCE", row.line, "Workflow conditions use requires Rule with explicit bindings");
        else reject("APPLICATION_WORKFLOW", row.line, "expected scope, input, requires Rule, explicit Rule binding or ordered steps");
      }
      if (!scope || !steps || steps.length < 2) reject("APPLICATION_WORKFLOW", section.line, "Workflow requires scope and at least two ordered steps");
      return { ...metadata, kind: "workflow", scope, steps, inputs, rules, bindings };
    }
    if (section.kind === "states" || section.kind === "state-machine") {
      let initial: string | undefined; let subject: string | null = null; const inputs: ApplicationField[] = [];
      const transitions: ApplicationStateMachineDeclaration["transitions"] = []; const states: string[] = [];
      const state = (value: string) => { if (!states.includes(value)) states.push(value); };
      for (let index = 0; index < rows.length; index++) {
        const row = rows[index]!;
        let match: RegExpExecArray | null;
        if ((match = /^subject\s+([A-Za-z_][\w-]*)$/.exec(row.text))) {
          if (subject !== null) reject("APPLICATION_STATE_MACHINE", row.line, "duplicate State Machine subject"); subject = match[1]!;
        } else if ((match = /^input\s+([A-Za-z_][\w-]*)\s+(.+)$/.exec(row.text))) {
          if (inputs.some(input => input.name === match![1])) reject("APPLICATION_STATE_MACHINE", row.line, "duplicate State Machine input");
          inputs.push({ name: match[1]!, type: parseApplicationType(match[2]!, row.line), source_line: row.line });
        } else if ((match = /^initial\s+([A-Za-z_][\w-]*)$/.exec(row.text))) {
          if (initial !== undefined) reject("APPLICATION_STATE_MACHINE", row.line, "duplicate initial state"); initial = match[1]; state(initial!);
        } else if ((match = /^state\s+([A-Za-z_][\w-]*)$/.exec(row.text))) {
          state(match[1]!);
        } else if ((match = /^transition\s+([A-Za-z_][\w-]*):$/.exec(row.text))) {
          const transitionIndent = row.indent ?? 0; const body: typeof rows = [];
          while (rows[index + 1] && (rows[index + 1]!.indent ?? 0) > transitionIndent) body.push(rows[++index]!);
          let from: string | null = null; let to: string | null = null; let rule: string | null = null; let trigger: string | null = null; let result: string | null = null;
          const transitionBindings: ApplicationStateMachineDeclaration["transitions"][number]["bindings"] = [];
          for (const item of body) {
            let clause: RegExpExecArray | null;
            if ((clause = /^(from|to|on|guard|emits)\s+([A-Za-z_][\w-]*)$/.exec(item.text))) {
              const key = clause[1]!, value = clause[2]!;
              if (key === "from") { if (from !== null) reject("APPLICATION_STATE_MACHINE", item.line, "duplicate transition source"); from = value; }
              else if (key === "to") { if (to !== null) reject("APPLICATION_STATE_MACHINE", item.line, "duplicate transition target"); to = value; }
              else if (key === "on") { if (trigger !== null) reject("APPLICATION_STATE_MACHINE", item.line, "duplicate transition trigger"); trigger = value; }
              else if (key === "guard") { if (rule !== null) reject("APPLICATION_STATE_MACHINE", item.line, "duplicate transition guard"); rule = value; }
              else { if (result !== null) reject("APPLICATION_STATE_MACHINE", item.line, "duplicate transition result Event"); result = value; }
            } else if ((clause = /^bind\s+([A-Za-z_][\w-]*)\s+<-\s+([A-Za-z_][\w-]*(?:\.[A-Za-z_][\w-]*)*)$/.exec(item.text))) {
              if (transitionBindings.some(binding => binding.parameter === clause![1])) reject("APPLICATION_STATE_MACHINE", item.line, "duplicate guard argument binding");
              transitionBindings.push({ parameter: clause[1]!, path: clause[2]!.split("."), source_line: item.line });
            } else if (/^guard\s+/.test(item.text)) reject("GUARD_RULE_REFERENCE", item.line, "State Machine guard must reference one declared Rule");
            else reject("APPLICATION_STATE_MACHINE", item.line, "expected from, to, on, guard, emits or explicit bind");
          }
          if (!from || !to || !trigger) reject("APPLICATION_STATE_MACHINE", row.line, "transition requires from, to and trigger Event");
          if (transitions.some(item => item.id === match![1])) reject("APPLICATION_STATE_MACHINE", row.line, "duplicate transition identity");
          transitions.push({ id: match[1]!, from, to, rule, trigger_event: trigger, result_event: result, bindings: transitionBindings, source_line: row.line });
          state(from); state(to);
        } else if ((match = /^([A-Za-z_][\w-]*)\s*->\s*([A-Za-z_][\w-]*)(?:\s+when\s+([A-Za-z_][\w-]*))?(?:\s+emits\s+([A-Za-z_][\w-]*))?$/.exec(row.text))) {
          const transition = { id: `${match[1]}-to-${match[2]}`, from: match[1]!, to: match[2]!, rule: match[3] ?? null,
            trigger_event: null, result_event: match[4] ?? null, bindings: [], source_line: row.line };
          if (transitions.some(item => item.from === transition.from && item.to === transition.to)) reject("APPLICATION_STATE_MACHINE", row.line, "duplicate transition");
          transitions.push(transition); state(transition.from); state(transition.to);
        } else if (/^guard\s+/.test(row.text)) reject("GUARD_RULE_REFERENCE", row.line, "State Machine guard must reference one declared Rule");
        else reject("APPLICATION_STATE_MACHINE", row.line, "expected subject, input, state, initial, transition block or compatibility transition");
      }
      if (!initial || !transitions.length) reject("APPLICATION_STATE_MACHINE", section.line, "State Machine requires an initial state and transitions");
      return { ...metadata, kind: "state-machine", subject, inputs, states, initial, transitions };
    }
    if (section.kind === "operation") {
      let input: ApplicationType | undefined; let output: ApplicationType | undefined;
      const refs: Pick<ApplicationOperationDeclaration, "reads" | "writes" | "produces" | "requires"> = { reads: [], writes: [], produces: [], requires: [] };
      for (const row of rows) {
        const match = /^(input|output|reads|writes|produces|requires)\s+(.+)$/.exec(row.text);
        if (!match) reject("APPLICATION_OPERATION", row.line, "expected input, output, reads, writes, produces or requires");
        const key = match![1]!; const value = match![2]!;
        if (key === "input" || key === "output") {
          if ((key === "input" ? input : output) !== undefined) reject("APPLICATION_OPERATION", row.line, `duplicate ${key}`);
          const type = parseApplicationType(value, row.line); if (key === "input") input = type; else output = type;
        } else {
          const list = refs[key as keyof typeof refs];
          for (const ref of value.split(",").map(x => x.trim())) {
            if (!namePattern.test(ref) || list.includes(ref)) reject("APPLICATION_REFERENCE", row.line, "expected unique declaration references");
            list.push(ref);
          }
        }
      }
      if (!input || !output) reject("APPLICATION_OPERATION", section.line, "Operation requires explicit input and output types");
      return { ...metadata, kind: "operation", input: input!, output: output!, ...refs };
    }
    return reject("APPLICATION_DECLARATION_UNSUPPORTED", section.line, `${section.kind} is not yet implemented in the application profile`);
  });
  const byId = new Map(declarations.map(d => [d.id, d]));
  const checkType = (type: ApplicationType, line: number, allowPublic = false): void => {
    if (type.kind === "scalar") return;
    if (type.kind === "optional" || type.kind === "list" || type.kind === "set") return checkType(type.element, line, allowPublic);
    if (type.kind === "sum") {
      const target = byId.get(type.enum);
      if (target?.kind !== "enum" || target.values.some(value => !/^[A-Z][A-Za-z0-9]*$/.test(value.name))) reject("APPLICATION_SUM", line, "sum must select an Enum with canonical variant names");
      return;
    }
    if (type.kind === "public-contract") {
      const owner = byId.get(type.interface);
      if (!allowPublic || owner?.kind !== "interface" || !owner.contracts.some(c => c.id === type.contract)) reject("APPLICATION_PUBLIC_TYPE", line, "public type must name an existing Interface contract in a supported public context");
      return;
    }
    if (type.kind === "declaration") {
      const kind = byId.get(type.ref)?.kind;
      if (!kind || !["entity", "value-object", "enum", "event"].includes(kind)) reject("APPLICATION_TYPE_REFERENCE", line, `${type.ref} is not a declared data type`);
      return;
    }
    if (type.kind === "reference") {
      const target = byId.get(type.entity);
      if (target?.kind !== "entity" || target.identity !== type.field) reject("APPLICATION_IDENTITY_REFERENCE", line, "reference must select the target Entity's explicit identity field");
    }
  };
  for (const declaration of declarations) {
    if (declaration.kind === "interface") {
      for (const contract of declaration.contracts) if (byId.has(contract.id)) reject("APPLICATION_INTERFACE", contract.source_line, "local public contract must not shadow a domain declaration");
      const active = new Set<string>(), done = new Set<string>();
      const publicType = (type: ApplicationPublicType | ApplicationType, line: number): void => {
        if (type.kind === "scalar") return;
        if (type.kind === "public-contract") return reject("APPLICATION_INTERFACE_TYPE", line, "shared domain values cannot embed public contracts");
        if (type.kind === "reference") reject("APPLICATION_INTERFACE_TYPE", line, "public contract does not implicitly convert Entity identity references; declare its public scalar shape explicitly");
        if (type.kind === "sum") {
          const value = byId.get(type.enum);
          if (value?.kind !== "enum") reject("APPLICATION_INTERFACE_TYPE", line, "public sum must select a declared Enum");
          return;
        }
        if (type.kind === "contract") {
          const id = "public:" + type.ref;
          if (active.has(id)) reject("APPLICATION_INTERFACE_CYCLE", line, "recursive public value embedding");
          if (done.has(id)) return;
          const contract = declaration.contracts.find(c => c.id === type.ref);
          if (!contract) reject("APPLICATION_INTERFACE_TYPE", line, "unknown local public contract");
          active.add(id); contract!.fields.forEach(f => publicType(f.type, f.source_line)); active.delete(id); done.add(id); return;
        }
        if (type.kind === "declaration") {
          const value = byId.get(type.ref);
          if (value?.kind !== "value-object" && value?.kind !== "enum") reject("APPLICATION_INTERFACE_TYPE", line, "public domain values must be declared Value Objects or Enums, never Entity snapshots");
          const id = "domain:" + type.ref;
          if (active.has(id)) reject("APPLICATION_INTERFACE_CYCLE", line, "recursive domain value embedding");
          if (done.has(id)) return;
          active.add(id); if (value!.kind === "value-object") value!.fields.forEach(f => publicType(f.type, f.source_line)); active.delete(id); done.add(id); return;
        }
        publicType(type.element, line);
      };
      declaration.contracts.forEach(c => publicType({ kind: "contract", ref: c.id }, c.source_line));
      for (const member of declaration.members) {
        const kind = byId.get(member.operation)?.kind;
        if (kind !== "operation" && kind !== "query" && !(declaration.boundary_kind === "external" && externalWriteMembers.has(`${declaration.id}#${member.operation}`))) reject("APPLICATION_INTERFACE_MEMBER", member.source_line, "exposes must select a declared Operation or Query, or an authored external-write member");
        publicType(member.request, member.source_line); publicType(member.result, member.source_line);
      }
    } else if (declaration.kind === "query") {
      declaration.inputs.forEach(input => checkType(input.type, input.source_line));
      checkType(declaration.output, declaration.source_line);
      if (byId.get(declaration.source.entity)?.kind !== "entity") reject("APPLICATION_QUERY_SOURCE", declaration.source_line, "Query source must be a declared Entity");
      const output = declaration.output;
      if ((output.kind !== "optional" && output.kind !== "list") || output.element.kind !== "declaration" || output.element.ref !== declaration.source.entity) {
        reject("APPLICATION_QUERY_OUTPUT", declaration.source_line, "Query output must explicitly select optional<SourceEntity> or list<SourceEntity>");
      }
      for (const binding of declaration.bindings) {
        if (binding.path[0] !== declaration.source.name && !declaration.inputs.some(p => p.name === binding.path[0])) reject("APPLICATION_QUERY_BINDING", binding.source_line, "Rule argument must select the source row or an explicit Query input");
      }
    } else if (declaration.kind === "mapping") {
      declaration.inputs.forEach(input => checkType(input.type, input.source_line, true));
      const [ownerId, contractId] = declaration.target.split(".");
      const owner = byId.get(ownerId!);
      const targetFields = contractId
        ? owner?.kind === "interface" ? owner.contracts.find(c => c.id === contractId)?.fields : undefined
        : owner?.kind === "entity" || owner?.kind === "value-object" ? owner.fields : undefined;
      if (!targetFields) return reject("APPLICATION_MAPPING_TARGET", declaration.source_line, "Mapping target must be a declared Entity, Value Object or qualified public contract");
      for (const field of declaration.fields) {
        if (!targetFields.some(f => f.name === field.target)) reject("APPLICATION_MAPPING_TARGET", field.source_line, "unknown target field");
        if (!declaration.inputs.some(input => input.name === field.path[0])) reject("APPLICATION_MAPPING_INPUT", field.source_line, "path must start with a declared Mapping input");
      }
      if (declaration.total && declaration.fields.length !== targetFields.length) reject("APPLICATION_MAPPING_TOTAL", declaration.source_line, "total Mapping must cover every target field");
    } else if (declaration.kind === "operation") {
      checkType(declaration.input, declaration.source_line); checkType(declaration.output, declaration.source_line);
      for (const ref of [...declaration.reads, ...declaration.writes]) if (byId.get(ref)?.kind !== "entity") reject("APPLICATION_REFERENCE", declaration.source_line, `${ref} is not an Entity`);
      for (const ref of declaration.produces) if (byId.get(ref)?.kind !== "event") reject("APPLICATION_REFERENCE", declaration.source_line, `${ref} is not an Event`);
      for (const ref of declaration.requires) if (!ruleIds.has(ref)) reject("APPLICATION_REFERENCE", declaration.source_line, `${ref} is not a Rule`);
    } else if (declaration.kind === "calculation") {
      declaration.inputs.forEach(input => checkType(input.type, input.source_line));
    } else if (declaration.kind === "policy") {
      declaration.inputs.forEach(input => checkType(input.type, input.source_line));
      if (!declaration.input_names.length) reject("APPLICATION_POLICY", declaration.source_line, "Policy requires explicit inputs");
      for (const item of declaration.cases) {
        if (!ruleIds.has(item.rule)) reject("APPLICATION_REFERENCE", item.source_line, `${item.rule} is not a Rule`);
        if (!["operation", "calculation"].includes(byId.get(item.target)?.kind ?? "")) reject("APPLICATION_REFERENCE", item.source_line, `${item.target} is not an Operation or Calculation`);
      }
      for (const binding of declaration.bindings) {
        if (!declaration.cases.some(item => item.rule === binding.rule)) reject("APPLICATION_POLICY", binding.source_line, `${binding.rule} is not a Policy case Rule`);
        if (!declaration.input_names.includes(binding.path[0]!)) reject("APPLICATION_POLICY", binding.source_line, "Policy Rule binding must start with a declared input");
      }
      if (!["operation", "calculation"].includes(byId.get(declaration.default_target)?.kind ?? "")) reject("APPLICATION_REFERENCE", declaration.source_line, `${declaration.default_target} is not an Operation or Calculation`);
    } else if (declaration.kind === "workflow") {
      for (const ref of declaration.steps) if (byId.get(ref)?.kind !== "operation") reject("APPLICATION_REFERENCE", declaration.source_line, `${ref} is not an Operation`);
      declaration.inputs.forEach(input => checkType(input.type, input.source_line));
      for (const ref of declaration.rules) if (!ruleIds.has(ref)) reject("APPLICATION_REFERENCE", declaration.source_line, `${ref} is not a Rule`);
      for (const binding of declaration.bindings) {
        if (!declaration.rules.includes(binding.rule)) reject("APPLICATION_WORKFLOW", binding.source_line, `${binding.rule} is not a Workflow Rule`);
        if (!declaration.inputs.some(input => input.name === binding.path[0])) reject("APPLICATION_WORKFLOW", binding.source_line, "Workflow Rule binding must start with a declared input");
      }
    } else if (declaration.kind === "state-machine") {
      declaration.inputs.forEach(input => checkType(input.type, input.source_line));
      if (declaration.subject && byId.get(declaration.subject)?.kind !== "entity") reject("APPLICATION_REFERENCE", declaration.source_line, `${declaration.subject} is not an Entity`);
      for (const transition of declaration.transitions) {
        if (transition.rule && !ruleIds.has(transition.rule)) reject("APPLICATION_REFERENCE", transition.source_line, `${transition.rule} is not a Rule`);
        for (const event of [transition.trigger_event, transition.result_event]) if (event && byId.get(event)?.kind !== "event") reject("APPLICATION_REFERENCE", transition.source_line, `${event} is not an Event`);
        for (const binding of transition.bindings) if (!declaration.inputs.some(input => input.name === binding.path[0])) reject("APPLICATION_STATE_MACHINE", binding.source_line, "guard binding must start with a declared State Machine input");
      }
    } else if (declaration.kind !== "enum") {
      declaration.fields.forEach(f => checkType(f.type, f.source_line));
      if (declaration.kind === "event" && declaration.occurrence_id) checkType(declaration.occurrence_id.type, declaration.occurrence_id.source_line);
    }
  }
  return declarations;
}
