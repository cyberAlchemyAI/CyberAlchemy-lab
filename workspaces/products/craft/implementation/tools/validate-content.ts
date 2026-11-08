#!/usr/bin/env tsx
/**
 * validate-content.ts — DomainSpec v2 content validator (MT0: Entity exemplar).
 *
 * Checks each concept in an aspect file against the per-meta-type criterion loaded from
 * `spec/meta-types/**\/*.schema.yml` (SCHEMA-CONSTITUTION format). MT0 scope = the Entity criterion
 * (identity + typedness) applied as a decidable table-walk. It validates SHAPE only; it never imports
 * or re-derives the engine `src/rules` δ-algorithm (moat), and never checks semantic satisfiability.
 *
 * Build-from-owned: markdown-table parsing is modeled on `tools/validate-relationships.ts`.
 *
 * Usage:
 *   tsx tools/validate-content.ts                         # walk spec/features/**\/SPEC.md
 *   tsx tools/validate-content.ts --file <aspect.md>      # check one aspect file
 *   tsx tools/validate-content.ts --schema-dir spec/meta-types --mode strict|warn
 */

import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join, relative, resolve } from "node:path";

import {
  loadRelationshipAuthority,
  validateRelationshipSpecFile,
} from "./lib/relationship-signatures";
import {
  type CriterionSubject,
  evaluateCriteria,
  loadMetaTypeSchemas,
  type MetaTypeSchema,
} from "./lib/meta-type-criteria";

type Schema = MetaTypeSchema;
type TableRow = { cells: string[]; authoredCells: string[]; line: number };
type MarkdownTable = { headers: string[]; rows: TableRow[] };
type Violation = {
  file: string;
  concept: string;
  type: string;
  reason: string;
  line: number;
};

const args = process.argv.slice(2);
const mode = getArg("--mode") || "strict";
const schemaDir = resolve(process.cwd(), getArg("--schema-dir") || "spec/meta-types");
const relationshipsPath = resolve(
  process.cwd(),
  getArg("--relationships") || "../definitions/relationships/relationships.yml",
);
const singleFile = getArg("--file");
const featuresRoot = resolve(process.cwd(), getArg("--features-root") || "spec/features");

const loadedSchemas = loadSchemasOrExit();
const schemasByType = new Map(
  loadedSchemas.map((entry) => [entry.schema.meta_type.toLowerCase(), entry]),
);
if (schemasByType.size === 0) {
  console.error(
    `validate-content: no .schema.yml found under ${toRelative(schemaDir)}`,
  );
  process.exit(1);
}

const targets = resolveTargets();
if (targets.length === 0) {
  console.log("validate-content: no aspect files to check");
  process.exit(0);
}

const violations: Violation[] = [];
let conceptsChecked = 0;
let edgesChecked = 0;
const relationshipAuthority = loadRelationshipAuthority(relationshipsPath);

function loadSchemasOrExit() {
  try {
    return loadMetaTypeSchemas<Schema>(schemaDir);
  } catch (error) {
    console.log(
      `[content:${mode}] ${error instanceof Error ? error.message : String(error)}`,
    );
    process.exit(1);
  }
}

for (const file of targets) {
  const lines = readFileSync(file, "utf-8").split(/\r?\n/);
  const relationshipResult = validateRelationshipSpecFile(file, relationshipAuthority);
  edgesChecked += relationshipResult.edgesChecked;
  for (const relationshipViolation of relationshipResult.violations) {
    violations.push({
      file: relationshipViolation.specPath,
      concept: relationshipViolation.value,
      type: "Relationship",
      reason: `${relationshipViolation.className}: ${relationshipViolation.detail}`,
      line: relationshipViolation.line,
    });
  }

  const registry = parseTableForSection(lines, "Concept Registry");
  if (!registry) {
    continue; // no declared concepts here (e.g. the sample fixture) — nothing to validate
  }
  const headerMap = toHeaderMap(registry.headers);
  const conceptIdx = headerMap.get("concept");
  const typeIdx = headerMap.get("type");
  if (conceptIdx === undefined || typeIdx === undefined) {
    continue;
  }

  for (const row of registry.rows) {
    const concept = (row.cells[conceptIdx] || "").trim();
    const type = (row.cells[typeIdx] || "").trim();
    if (!concept || !type) {
      continue;
    }
    const loadedSchema = schemasByType.get(type.toLowerCase());
    if (!loadedSchema) {
      continue; // meta-type not yet formalized (MT0 formalizes only Entity)
    }
    conceptsChecked += 1;

    const table = parseTableForSection(lines, concept);
    const sectionLines = getSectionLines(lines, concept);

    const subject = toCriterionSubject(file, concept, table, sectionLines);
    for (const failure of evaluateCriteria(
      loadedSchema.path,
      loadedSchema.schema.criterion,
      subject,
    )) {
      violations.push({
        file: toRelative(file),
        concept,
        type,
        reason: failure.message,
        line: table?.rows[0]?.line ?? row.line,
      });
    }
  }
}

if (violations.length === 0) {
  console.log(
    `validate-content: PASS (` +
      `${conceptsChecked} concept(s) checked, ` +
      `${edgesChecked} edge(s) checked in ${targets.length} file(s); ` +
      `schemas=${schemasByType.size})`,
  );
  process.exit(0);
}

for (const v of violations) {
  console.log(
    `[content:${mode}] ${v.file}:${v.line} | concept=${v.concept} | type=${v.type} | ${v.reason}`,
  );
}
console.log(`[content:${mode}] violations=${violations.length}`);

process.exit(mode === "warn" ? 0 : 1);

// ---------------------------------------------------------------------------
// criterion adapter (Markdown table/section -> normalized shared-kernel subject)
// ---------------------------------------------------------------------------

function toCriterionSubject(
  file: string,
  concept: string,
  table: MarkdownTable | null,
  sectionLines: string[],
): CriterionSubject {
  const subject: CriterionSubject = {
    kind: "markdown",
    path: `${toRelative(file)}#${concept}`,
    text: sectionLines.join("\n"),
  };
  if (!table) {
    return subject;
  }

  subject.table = {
    columns: table.headers,
    rows: table.rows.map((row) => row.authoredCells),
  };
  subject.columns = Object.fromEntries(
    table.headers.map((header, index) => [
      header,
      table.rows.map((row) => row.authoredCells[index]),
    ]),
  );

  const headerMap = toHeaderMap(table.headers);
  const attributeIndex = headerMap.get("attribute");
  const valueIndex = headerMap.get("value");
  if (attributeIndex !== undefined) {
    subject.attributes = table.rows.map((row) => ({
      key: row.cells[attributeIndex] ?? "",
      value: valueIndex === undefined ? undefined : row.authoredCells[valueIndex],
    }));
  }
  return subject;
}

// ---------------------------------------------------------------------------
// aspect-file targets
// ---------------------------------------------------------------------------

function resolveTargets(): string[] {
  if (singleFile) {
    const p = resolve(process.cwd(), singleFile);
    if (!existsSync(p)) {
      console.error(`validate-content: --file not found: ${singleFile}`);
      process.exit(1);
    }
    return [p];
  }
  if (!existsSync(featuresRoot)) {
    return [];
  }
  return walk(featuresRoot)
    .filter((p) => p.endsWith("/SPEC.md"))
    .sort();
}

// ---------------------------------------------------------------------------
// markdown-table parsing (build-from-owned: tools/validate-relationships.ts)
// ---------------------------------------------------------------------------

function parseTableForSection(
  lines: string[],
  sectionName: string,
): MarkdownTable | null {
  const sectionRanges = findSectionRanges(lines);
  const section = sectionRanges.find(
    (entry) => normalizeSectionName(entry.name) === normalizeSectionName(sectionName),
  );
  if (!section) {
    return null;
  }

  let start = section.start;
  while (start < section.end && !lines[start]?.trim().startsWith("|")) {
    start += 1;
  }
  if (start >= section.end) {
    return null;
  }

  const headerLine = lines[start] || "";
  const separatorLine = lines[start + 1] || "";
  if (!separatorLine.trim().startsWith("|")) {
    return null;
  }

  const headers = parseTableRow(headerLine);
  const separatorCells = parseTableRow(separatorLine);
  if (
    headers.length === 0 ||
    separatorCells.length === 0 ||
    !separatorCells.every((cell) => /^:?-{3,}:?$/.test(cell) || cell.length === 0)
  ) {
    return null;
  }

  const rows: TableRow[] = [];
  let rowIndex = start + 2;
  while (rowIndex < section.end) {
    const line = lines[rowIndex] || "";
    if (!line.trim().startsWith("|")) {
      break;
    }
    const authoredCells = parseAuthoredTableRow(line);
    const cells = authoredCells.map((cell) => cell.trim());
    if (!cells.every((cell) => /^:?-{3,}:?$/.test(cell) || cell.length === 0)) {
      rows.push({ cells, authoredCells, line: rowIndex + 1 });
    }
    rowIndex += 1;
  }

  return { headers, rows };
}

function parseTableRow(line: string): string[] {
  const trimmed = line.trim();
  if (!trimmed.startsWith("|")) {
    return [];
  }
  const withoutEdges = trimmed.replace(/^\|/, "").replace(/\|$/, "");
  return withoutEdges.split("|").map((cell) => cell.trim());
}

function parseAuthoredTableRow(line: string): string[] {
  const trimmed = line.trim();
  if (!trimmed.startsWith("|")) return [];
  const withoutEdges = trimmed.replace(/^\|/, "").replace(/\|$/, "");
  return withoutEdges.split("|").map((cell) => {
    let authored = cell;
    if (authored.startsWith(" ")) authored = authored.slice(1);
    if (authored.endsWith(" ")) authored = authored.slice(0, -1);
    return authored;
  });
}

function toHeaderMap(headers: string[]): Map<string, number> {
  const map = new Map<string, number>();
  headers.forEach((header, index) => {
    map.set(header.trim().toLowerCase(), index);
  });
  return map;
}

function normalizeSectionName(name: string): string {
  return name.trim().toLowerCase().replace(/\s+/g, " ");
}

function getSectionLines(lines: string[], sectionName: string): string[] {
  const section = findSectionRanges(lines).find(
    (entry) => normalizeSectionName(entry.name) === normalizeSectionName(sectionName),
  );
  if (!section) {
    return [];
  }
  return lines.slice(section.start, section.end);
}

function findSectionRanges(
  lines: string[],
): Array<{ name: string; start: number; end: number }> {
  const headings: Array<{ name: string; line: number }> = [];
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i] || "";
    const match = /^##+\s+(.+)$/.exec(line.trim());
    if (!match?.[1]) {
      continue;
    }
    headings.push({ name: match[1].trim(), line: i });
  }

  const sections: Array<{ name: string; start: number; end: number }> = [];
  for (let i = 0; i < headings.length; i += 1) {
    const current = headings[i];
    if (!current) {
      continue;
    }
    const next = headings[i + 1];
    sections.push({
      name: current.name,
      start: current.line + 1,
      end: next ? next.line : lines.length,
    });
  }
  return sections;
}

function walk(root: string): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const fullPath = join(root, entry.name);
    if (entry.isDirectory()) {
      out.push(...walk(fullPath));
    } else if (entry.isFile()) {
      out.push(fullPath);
    }
  }
  return out;
}

function getArg(name: string): string | undefined {
  const index = args.indexOf(name);
  if (index < 0) {
    return undefined;
  }
  return args[index + 1];
}

function toRelative(absPath: string): string {
  return relative(process.cwd(), absPath).replace(/\\/g, "/");
}
