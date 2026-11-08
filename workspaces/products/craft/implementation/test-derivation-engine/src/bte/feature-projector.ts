import {
  cpSync,
  readFileSync,
  realpathSync,
} from "node:fs";
import { dirname, relative, resolve, sep } from "node:path";

import {
  BACKEND_KINDS,
  BACKEND_RELATIONSHIPS,
  DEVELOPMENT_PROFILE_ID,
  collectDevelopmentProjectDiagnostics,
  type BackendKind,
  type BackendRelationship,
  type DevelopmentDiagnostic,
  type DevelopmentEdge,
  type DevelopmentNode,
  type DevelopmentProject,
} from "./development-engine.js";

export const PROJECTOR_DIAGNOSTIC_CODES = [
  "BTE_PROJECT_HEADER_INVALID",
  "BTE_PROJECT_ROW_INVALID",
  "BTE_PROJECT_PATH_ESCAPE",
  "BTE_PROJECT_ANCHOR_MISSING",
  "BTE_PROJECT_FORMATION_EVIDENCE_MISSING",
] as const;

export type ProjectorDiagnosticCode =
  (typeof PROJECTOR_DIAGNOSTIC_CODES)[number];

export type ProjectorDiagnostic = {
  code: ProjectorDiagnosticCode;
  subject: string;
  source_anchor: string;
  detail: string;
};

export type FeatureProjection = {
  schema_version: "bte-feature-projection/v1";
  source_root: string;
  project: DevelopmentProject;
  diagnostics: ProjectorDiagnostic[];
  conformance_diagnostics: DevelopmentDiagnostic[];
  census: {
    nodes: number;
    kinds: number;
    edges: number;
    families: number;
  };
};

type Table = {
  header: string[];
  rows: string[][];
  startLine: number;
};

function cells(line: string): string[] {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(
    (cell) => cell.trim(),
  );
}

function isSeparator(line: string): boolean {
  return cells(line).every((cell) => /^:?-+:?$/.test(cell.replaceAll(" ", "")));
}

function tableAfterHeading(
  text: string,
  headings: readonly string[],
): Table | null {
  const lines = text.split(/\r?\n/);
  const headingIndex = lines.findIndex((line) => headings.includes(line.trim()));
  if (headingIndex < 0) return null;
  const start = lines.findIndex(
    (line, index) => index > headingIndex && line.trim().startsWith("|"),
  );
  if (start < 0) return null;
  const header = cells(lines[start]!);
  let index = start + 1;
  if (isSeparator(lines[index] ?? "")) index += 1;
  const rows: string[][] = [];
  while (lines[index]?.trim().startsWith("|")) {
    if (!isSeparator(lines[index]!)) rows.push(cells(lines[index]!));
    index += 1;
  }
  return { header, rows, startLine: start + 1 };
}

function headerIndex(table: Table, aliases: readonly string[]): number {
  return table.header.findIndex((value) =>
    aliases.some((alias) => value.toLowerCase() === alias.toLowerCase()),
  );
}

function slug(value: string): string {
  return value
    .toLowerCase()
    .replace(/[`*_]/g, "")
    .replace(/[^a-z0-9 -]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-");
}

function link(value: string): { label: string; ref: string } | null {
  const match = value.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
  return match ? { label: match[1]!, ref: match[2]! } : null;
}

function sectionForAnchor(text: string, anchor: string): string | null {
  const lines = text.split(/\r?\n/);
  const start = lines.findIndex((line) => {
    const match = line.match(/^(#{1,6})\s+(.+)$/);
    return match ? slug(match[2]!) === anchor.toLowerCase() : false;
  });
  if (start < 0) return null;
  const level = lines[start]!.match(/^#+/)![0].length;
  let end = lines.length;
  for (let index = start + 1; index < lines.length; index += 1) {
    const match = lines[index]!.match(/^(#{1,6})\s+/);
    if (match && match[1]!.length <= level) {
      end = index;
      break;
    }
  }
  return lines.slice(start, end).join("\n");
}

function resolveContainedAnchor(
  root: string,
  reference: string,
): { path: string; anchor: string; section: string } | ProjectorDiagnostic {
  const [rawPath, anchor = ""] = reference.split("#", 2);
  const rootReal = realpathSync(root);
  const candidate = resolve(rootReal, rawPath || "SPEC.md");
  let candidateReal: string;
  try {
    candidateReal = realpathSync(candidate);
  } catch {
    return {
      code: "BTE_PROJECT_ANCHOR_MISSING",
      subject: reference,
      source_anchor: reference,
      detail: "referenced file does not exist",
    };
  }
  const relation = relative(rootReal, candidateReal);
  if (relation.startsWith(`..${sep}`) || relation === "..") {
    return {
      code: "BTE_PROJECT_PATH_ESCAPE",
      subject: reference,
      source_anchor: reference,
      detail: "reference escapes the feature root",
    };
  }
  const text = readFileSync(candidateReal, "utf8");
  const section = sectionForAnchor(text, anchor);
  if (!anchor || section === null) {
    return {
      code: "BTE_PROJECT_ANCHOR_MISSING",
      subject: reference,
      source_anchor: reference,
      detail: "referenced heading anchor does not exist",
    };
  }
  return { path: relation.replaceAll(sep, "/"), anchor, section };
}

function sectionTable(section: string, required: readonly string[]): Table | null {
  const lines = section.split(/\r?\n/);
  for (let index = 0; index < lines.length; index += 1) {
    if (!lines[index]!.trim().startsWith("|")) continue;
    const table = tableAfterHeading(
      `## local\n${lines.slice(index).join("\n")}`,
      ["## local"],
    );
    if (
      table &&
      required.every((name) =>
        table.header.some((cell) => cell.toLowerCase() === name.toLowerCase()),
      )
    ) return table;
  }
  return null;
}

function formationBody(
  kind: BackendKind,
  label: string,
  section: string,
): Record<string, unknown> | null {
  if (kind === "Value Object") {
    const table = sectionTable(section, ["Field", "Type"]);
    if (!table) return null;
    const fieldIndex = headerIndex(table, ["Field"]);
    const typeIndex = headerIndex(table, ["Type"]);
    const fields = table.rows.map((row) => ({
      name: row[fieldIndex],
      type: row[typeIndex],
      identity: false,
    }));
    if (!/\*\*Equality:\*\*/i.test(section)) return null;
    return {
      fields,
      equality: {
        strategy: "field-tuple",
        fields: fields.map(({ name }) => name),
      },
    };
  }
  if (kind === "Operation" && /\*\*Type:\*\*.*Operation.*mutation/i.test(section)) {
    return { state_change: "yes" };
  }
  if (kind === "Policy" && /\*\*Type:\*\*.*Policy/i.test(section)) {
    return { formal_return_type: "strategy" };
  }
  if (kind === "State Machine") {
    const table = sectionTable(section, ["From", "Event", "To"]);
    if (!table) return null;
    const from = headerIndex(table, ["From"]);
    const to = headerIndex(table, ["To"]);
    const states = [
      ...new Set(
        table.rows.flatMap((row) => [row[from], row[to]]).filter(
          (state): state is string => Boolean(state && state !== "[new]"),
        ),
      ),
    ].sort();
    return states.length >= 2 ? { has_transitions: "yes", states } : null;
  }
  if (kind === "Interface" && /^##\s+External:/m.test(section)) {
    return { interface_kind: "external" };
  }
  if (kind === "Query" && /\*\*Type:\*\*.*Query.*read-only/i.test(section)) {
    return { state_change: "no" };
  }
  if (kind === "Event" && /(Generated|Created|Applied|Changed)$/.test(label)) {
    return { temporal: "past" };
  }
  if (kind === "Mapping") {
    const direction = section.match(
      /\*\*Direction:\*\*\s*(Inbound|Outbound|Bidirectional)/i,
    )?.[1]?.toLowerCase();
    return direction ? { direction } : null;
  }
  if (kind === "Workflow" && /\*\*Type:\*\*\s*Workflow/i.test(section)) {
    const table = sectionTable(section, ["#", "Step", "Operation"]);
    if (!table) return null;
    const operation = headerIndex(table, ["Operation"]);
    const steps = [
      ...new Set(table.rows.map((row) => row[operation]).filter(Boolean)),
    ];
    return steps.length > 0 ? { scope: "intra-feature", steps } : null;
  }
  return null;
}

function projectorDiagnostic(
  code: ProjectorDiagnosticCode,
  subject: string,
  sourceAnchor: string,
  detail: string,
): ProjectorDiagnostic {
  return { code, subject, source_anchor: sourceAnchor, detail };
}

export function projectFeatureDirectory(featureRoot: string): FeatureProjection {
  const root = realpathSync(featureRoot);
  const spec = readFileSync(resolve(root, "SPEC.md"), "utf8");
  const diagnostics: ProjectorDiagnostic[] = [];
  const conceptTable = tableAfterHeading(spec, [
    "## Concepts",
    "## Concept Registry",
  ]);
  const graphTable = tableAfterHeading(spec, ["## Feature Concept Graph"]);
  if (!conceptTable || !graphTable) {
    diagnostics.push(
      projectorDiagnostic(
        "BTE_PROJECT_HEADER_INVALID",
        "SPEC.md",
        "SPEC.md",
        "required Concepts/Concept Registry or Feature Concept Graph table is missing",
      ),
    );
  }

  const nodes: DevelopmentNode[] = [];
  if (conceptTable) {
    const concept = headerIndex(conceptTable, ["Concept"]);
    const id = headerIndex(conceptTable, ["ID"]);
    const kind = headerIndex(conceptTable, ["Type"]);
    const description = headerIndex(conceptTable, ["Description"]);
    for (const [rowIndex, row] of conceptTable.rows.entries()) {
      const conceptLink = link(row[concept] ?? "");
      const nodeId = row[id] ?? "";
      const nodeKind = row[kind] as BackendKind;
      const rowAnchor = `SPEC.md#concepts:row-${rowIndex + 1}`;
      if (
        !conceptLink ||
        !nodeId ||
        !BACKEND_KINDS.includes(nodeKind)
      ) {
        diagnostics.push(
          projectorDiagnostic(
            "BTE_PROJECT_ROW_INVALID",
            nodeId || `concept-row-${rowIndex + 1}`,
            rowAnchor,
            "concept link, stable ID, or backend kind is invalid",
          ),
        );
        continue;
      }
      const resolved = resolveContainedAnchor(root, conceptLink.ref);
      if ("code" in resolved) {
        diagnostics.push({ ...resolved, subject: nodeId });
        continue;
      }
      const body = formationBody(nodeKind, conceptLink.label, resolved.section);
      if (!body) {
        diagnostics.push(
          projectorDiagnostic(
            "BTE_PROJECT_FORMATION_EVIDENCE_MISSING",
            nodeId,
            conceptLink.ref,
            `${nodeKind} formation evidence is incomplete`,
          ),
        );
      }
      nodes.push({
        node_id: nodeId,
        feature_id: "financial-settlement",
        kind: nodeKind,
        intent: row[description] || conceptLink.label,
        body: body ?? {},
        source_anchor: conceptLink.ref,
      });
    }
  }

  const edges: DevelopmentEdge[] = [];
  if (graphTable) {
    const from = headerIndex(graphTable, ["From"]);
    const family = headerIndex(graphTable, ["Edge"]);
    const to = headerIndex(graphTable, ["To"]);
    const evidence = headerIndex(graphTable, ["Evidence", "Source Evidence"]);
    const orderedCounts = new Map<string, number>();
    for (const [rowIndex, row] of graphTable.rows.entries()) {
      const edgeFamily = row[family] as BackendRelationship;
      const rowAnchor = `SPEC.md#feature-concept-graph:row-${rowIndex + 1}`;
      const evidenceRef = row[evidence] ?? "";
      if (
        !row[from] ||
        !row[to] ||
        !BACKEND_RELATIONSHIPS.includes(edgeFamily) ||
        !evidenceRef
      ) {
        diagnostics.push(
          projectorDiagnostic(
            "BTE_PROJECT_ROW_INVALID",
            `graph-row-${rowIndex + 1}`,
            rowAnchor,
            "graph endpoints, family, or evidence is invalid",
          ),
        );
        continue;
      }
      const resolved = resolveContainedAnchor(root, evidenceRef);
      if ("code" in resolved) diagnostics.push({ ...resolved, subject: rowAnchor });
      const slot = `${row[from]}/${edgeFamily}`;
      const ordinal = orderedCounts.get(slot) ?? 0;
      orderedCounts.set(slot, ordinal + 1);
      edges.push({
        edge_id: `financial-settlement.edge.${String(rowIndex + 1).padStart(3, "0")}.${edgeFamily}`,
        family: edgeFamily,
        from: row[from]!,
        to: row[to]!,
        ...(edgeFamily === "orchestrates" ? { ordinal } : {}),
        source_anchor: evidenceRef || rowAnchor,
      });
    }
  }

  const project: DevelopmentProject = {
    schema_version: "bte-development-project/v1",
    project_id: "financial-settlement",
    profile_id: DEVELOPMENT_PROFILE_ID,
    coverage_mode: "declared-subset",
    nodes,
    edges,
  };
  const conformance = collectDevelopmentProjectDiagnostics(project);
  return {
    schema_version: "bte-feature-projection/v1",
    source_root: root,
    project,
    diagnostics: diagnostics.sort(
      (left, right) =>
        left.source_anchor.localeCompare(right.source_anchor) ||
        left.code.localeCompare(right.code),
    ),
    conformance_diagnostics: conformance.diagnostics,
    census: {
      nodes: nodes.length,
      kinds: new Set(nodes.map(({ kind }) => kind)).size,
      edges: edges.length,
      families: new Set(edges.map(({ family }) => family)).size,
    },
  };
}

export function copyFeatureFixture(source: string, target: string): void {
  cpSync(source, target, { recursive: true });
}
