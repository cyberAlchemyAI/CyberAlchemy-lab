#!/usr/bin/env tsx
/**
 * validate-meta-types-noncollapse.ts — DomainSpec v2 node non-collapse checker (PROPOSED). CLI wrapper.
 *
 * Pure logic lives in tools/lib/meta-type-noncollapse.ts. This file does the I/O: load the current schemas
 * and the DS-D8 relationship AUTHORITY, resolve edge participation from the authority (never raw schema
 * slices), then print verdicts + the acceptance matrix. Touches no live authority — a checker only.
 *
 * Usage (run from impl/):
 *   tsx tools/validate-meta-types-noncollapse.ts                       # verdict + exit code
 *   tsx tools/validate-meta-types-noncollapse.ts --report             # full pairwise matrix
 *   tsx tools/validate-meta-types-noncollapse.ts --exception-allowlist rule,policy,calculation
 */

import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join, relative, resolve } from "node:path";

import { loadRelationshipAuthority } from "./lib/relationship-signatures";
import {
  ATTESTATION,
  DEFAULT_EXCEPTION_ALLOWLIST,
  STRUCTURE_READING,
  type EdgeMaps,
  type Schema,
  normalize,
  summarize,
} from "./lib/meta-type-noncollapse";

const args = process.argv.slice(2);
const report = args.includes("--report");
const schemaDir = resolve(process.cwd(), getArg("--schema-dir") || "spec/meta-types");
const relationshipsPath = resolve(
  process.cwd(),
  getArg("--relationships") || "../definitions/relationships/relationships.yml",
);
const allowlistArg = getArg("--exception-allowlist");
const allowlist =
  allowlistArg === undefined
    ? DEFAULT_EXCEPTION_ALLOWLIST
    : new Set(allowlistArg.split(",").map((s) => normalize(s)).filter(Boolean));

const schemas = loadSchemas(schemaDir);
if (schemas.length === 0) {
  console.error(`validate-meta-types-noncollapse: no .schema.yml under ${toRelative(schemaDir)}`);
  process.exit(1);
}

const edges = buildEdgeMaps(relationshipsPath);
const summary = summarize(schemas, edges, allowlist);

console.log(`validate-meta-types-noncollapse: ${schemas.length} meta-types, ${summary.pairs.length} pairs`);
console.log(`  classification: ${STRUCTURE_READING.size} structure-reading + ${ATTESTATION.size} attestation keywords (total)`);
if (summary.unclassified.length) {
  console.log(`  [FAIL] unclassified rule keyword(s):`);
  for (const u of summary.unclassified) console.log(`    - ${u}`);
}
console.log(`  exception-lane (owner-enumerated): ${summary.exceptionLane.join(", ") || "<none>"}`);
console.log(`  attestation-only, not exempt: ${summary.attestationOnlyNotExempt.join(", ") || "<none>"}`);
console.log(`  collapse-candidate(s): ${summary.collapses.length || "none"}`);
for (const c of summary.collapses) console.log(`    - ${c.a} ~ ${c.b}`);

if (report) {
  console.log(`\n  --- full pairwise matrix ---`);
  for (const p of summary.pairs) {
    console.log(`    ${p.verdict === "collapse" ? "COLLAPSE" : "distinct"}  ${p.a} ~ ${p.b}  (${p.via})`);
  }
}

// acceptance criteria (against today's registry, default allow-list)
const hasCollapse = (x: string, y: string) =>
  summary.collapses.some(
    (c) =>
      (normalize(c.a) === normalize(x) && normalize(c.b) === normalize(y)) ||
      (normalize(c.a) === normalize(y) && normalize(c.b) === normalize(x)),
  );
const enumFact = summary.facts.find((f) => f.name === "enum");
const checks = [
  {
    name: "Current registry baseline has no collapse candidates",
    ok: summary.collapses.length === 0,
    detail: "authority-selected orchestration collapse is no longer an active pair lock",
  },
  { name: "MUST NOT fire Entity~Value Object", ok: !hasCollapse("Entity", "Value Object"), detail: "separated by identity, not typedness" },
  {
    name: "MUST route Rule/Policy/Calculation to exception-lane",
    ok: ["rule", "policy", "calculation"].every((t) => summary.exceptionLane.map(normalize).includes(t)),
    detail: "owner-enumerated formal_return_type sort",
  },
  {
    name: "Rule classification is TOTAL (no unclassified keyword)",
    ok: summary.unclassified.length === 0,
    detail: `all ${STRUCTURE_READING.size + ATTESTATION.size} supported keywords mapped`,
  },
  {
    name: "Enum has a defined structural witness (not classifier-undefined)",
    ok: !!enumFact && enumFact.structKeys.size > 0 && !hasCollapseInvolving("enum"),
    detail: "table-has-column classified structure-reading; Enum in no collapse",
  },
];
console.log(`\n  --- acceptance criteria ---`);
let allOk = summary.unclassified.length === 0;
for (const c of checks) {
  allOk = allOk && c.ok;
  console.log(`    [${c.ok ? "PASS" : "FAIL"}] ${c.name} — ${c.detail}`);
}
process.exit(allOk ? 0 : 1);

function hasCollapseInvolving(typeNorm: string): boolean {
  return summary.collapses.some((c) => normalize(c.a) === typeNorm || normalize(c.b) === typeNorm);
}

// --- I/O helpers -------------------------------------------------------------------------------
function buildEdgeMaps(authorityPath: string): EdgeMaps {
  const auth = loadRelationshipAuthority(authorityPath);
  const sourceEdges = new Map<string, Set<string>>();
  const targetEdges = new Map<string, Set<string>>();
  for (const [edgeId, sigs] of auth.signaturesById.entries()) {
    for (const sig of sigs) {
      for (const t of sigTypes(sig, "source")) addEdge(sourceEdges, t, edgeId);
      for (const t of sigTypes(sig, "target")) addEdge(targetEdges, t, edgeId);
    }
  }
  return { sourceEdges, targetEdges };
}
function sigTypes(sig: Record<string, unknown>, side: "source" | "target"): string[] {
  const arr = side === "source" ? sig.source_types : sig.target_types;
  const scalar = side === "source" ? sig.source_type : sig.target_type;
  const values = Array.isArray(arr) ? (arr as string[]) : typeof scalar === "string" ? [scalar] : [];
  return values.map(normalize).filter(Boolean);
}
function addEdge(map: Map<string, Set<string>>, type: string, edge: string) {
  if (!map.has(type)) map.set(type, new Set());
  map.get(type)!.add(edge);
}
function loadSchemas(dir: string): Schema[] {
  if (!existsSync(dir)) return [];
  return walk(dir)
    .filter((p) => p.endsWith(".schema.yml"))
    .sort()
    .map((f) => parseSchemaYml(readFileSync(f, "utf-8"), toRelative(f)) as Schema)
    .filter((s) => typeof s.meta_type === "string" && s.meta_type);
}
// minimal SCHEMA-CONSTITUTION reader (build-from-owned: validate-content.ts)
function parseSchemaYml(raw: string, where: string): Record<string, unknown> {
  const root: Record<string, unknown> = {};
  const stack: Array<{ indent: number; node: Record<string, unknown> }> = [{ indent: -1, node: root }];
  const lines = raw.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i] ?? "";
    if (rawLine.trim() === "" || rawLine.trim().startsWith("#")) continue;
    if (rawLine.includes("\t")) throw new Error(`${where}:${i + 1}: tabs not allowed`);
    const indent = rawLine.length - rawLine.trimStart().length;
    const content = rawLine.trim();
    const colon = content.indexOf(":");
    if (colon < 0) throw new Error(`${where}:${i + 1}: expected 'key:' — got "${content}"`);
    const key = content.slice(0, colon).trim();
    const rest = content.slice(colon + 1).trim();
    while (stack.length > 1 && (stack[stack.length - 1]?.indent ?? -1) >= indent) stack.pop();
    const parent = stack[stack.length - 1]?.node ?? root;
    if (rest === "") {
      const obj: Record<string, unknown> = {};
      parent[key] = obj;
      stack.push({ indent, node: obj });
    } else {
      parent[key] = parseScalarOrList(rest);
    }
  }
  return root;
}
function parseScalarOrList(value: string): string | string[] {
  if (value.startsWith("[") && value.endsWith("]")) {
    const inner = value.slice(1, -1).trim();
    return inner === "" ? [] : inner.split(",").map((s) => unquote(s.trim()));
  }
  return unquote(value);
}
function unquote(s: string): string {
  if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) return s.slice(1, -1);
  return s;
}
function walk(root: string): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const p = join(root, entry.name);
    if (entry.isDirectory()) out.push(...walk(p));
    else if (entry.isFile()) out.push(p);
  }
  return out;
}
function getArg(name: string): string | undefined {
  const i = args.indexOf(name);
  return i < 0 ? undefined : args[i + 1];
}
function toRelative(absPath: string): string {
  return relative(process.cwd(), absPath).replace(/\\/g, "/");
}
