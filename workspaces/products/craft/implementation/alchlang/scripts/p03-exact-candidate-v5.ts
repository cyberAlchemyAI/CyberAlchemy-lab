#!/usr/bin/env node
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {
  buildCandidate as buildV4,
  validateCandidate as validateV4,
  createQualification as qualifyV4,
  compareArtifactReplay,
} from "./p03-exact-candidate-v4.js";

export {compareArtifactReplay, inspectArchive, validatePredecessorSemantics} from "./p03-exact-candidate-v4.js";

type Candidate = Record<string, any>;
type Row = {path: string; size_bytes: number; sha256: string};
const ownPath = fileURLToPath(import.meta.url);
const implementation = path.resolve(path.dirname(ownPath), "..");
const repo = path.resolve(implementation, "../../../../../..");
const evidence = path.join(repo, "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p03-exact-candidate");
const previousCandidate = path.join(evidence, "successor-v4-candidate/candidate.json");
const previousQualification = path.join(evidence, "successor-v4-candidate/qualification.json");
const candidatePath = path.join(evidence, "successor-v5-candidate/candidate.json");
const qualificationPath = path.join(evidence, "successor-v5-candidate/qualification.json");
const read = (p: string) => JSON.parse(fs.readFileSync(p, "utf8"));
const canonical = (value: any): string => Array.isArray(value) ? `[${value.map(canonical).join(",")}]`
  : value !== null && typeof value === "object" ? `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k])}`).join(",")}}`
  : JSON.stringify(value) ?? "null";
const hash = (value: string | Buffer) => crypto.createHash("sha256").update(value).digest("hex");
const relative = (p: string) => path.relative(repo, p).split(path.sep).join("/");
const sorted = (rows: Row[]) => [...rows].sort((a, b) => a.path.localeCompare(b.path));
function row(p: string): Row {
  assert.equal(fs.lstatSync(p).isFile(), true, `P03_V5_NON_REGULAR:${p}`);
  assert.equal(fs.realpathSync(p), p, `P03_V5_SYMLINK:${p}`);
  const bytes = fs.readFileSync(p);
  return {path: relative(p), size_bytes: bytes.length, sha256: hash(bytes)};
}
function additions() {
  return {tool: row(ownPath), receipts: sorted([row(previousCandidate), row(previousQualification)])};
}
function seal(input: Candidate): Candidate {
  assert.ok(input && typeof input === "object" && !Array.isArray(input));
  const value = structuredClone(input);
  delete value.candidate_id;
  delete value.manifest_sha256;
  value.candidate_id = `alchlang-domainspec-p03-${hash(canonical(value)).slice(0, 16)}`;
  value.manifest_sha256 = hash(canonical(value));
  return value;
}
function tools(value: Candidate) {
  const matches = value.source_groups.filter((g: any) => g.id === "candidate-tools");
  assert.equal(matches.length, 1, "P03_V5_TOOL_GROUP");
  return matches[0];
}
function extend(base: Candidate, extra: ReturnType<typeof additions>) {
  const value = structuredClone(base);
  const group = tools(value);
  assert.ok(!group.files.some((r: Row) => r.path === extra.tool.path));
  group.files = sorted([...group.files, extra.tool]);
  group.inventory_sha256 = hash(canonical(group.files));
  assert.ok(!value.receipts.some((r: Row) => extra.receipts.some(e => r.path === e.path)));
  value.receipts = sorted([...value.receipts, ...extra.receipts]);
  return seal(value);
}

export function validateCandidate(value: Candidate, checkCurrent = true) {
  const checks: Array<{id: string; result: "pass" | "fail"}> = [];
  const check = (id: string, fn: () => boolean) => {
    try { checks.push({id, result: fn() ? "pass" : "fail"}); }
    catch { checks.push({id, result: "fail"}); }
  };
  check("candidate-id", () => value.candidate_id === seal(value).candidate_id);
  check("manifest-self-digest", () => value.manifest_sha256 === seal(value).manifest_sha256);
  check("v5-expanded-tool-inventory", () => {
    const group = tools(value);
    return group.inventory_sha256 === hash(canonical(group.files))
      && canonical(group.files) === canonical(sorted(group.files))
      && group.files.length === new Set(group.files.map((r: Row) => r.path)).size;
  });
  check("v5-exact-added-bindings", () => {
    const extra = additions();
    const own = tools(value).files.filter((r: Row) => r.path === extra.tool.path);
    const receipts = value.receipts.filter((r: Row) => extra.receipts.some(e => e.path === r.path));
    return canonical(own) === canonical([extra.tool])
      && canonical(receipts) === canonical(extra.receipts)
      && canonical(value.receipts) === canonical(sorted(value.receipts))
      && value.receipts.length === new Set(value.receipts.map((r: Row) => r.path)).size;
  });
  try {
    // Check the expanded v5 envelope before discarding ONLY its declared additions.
    // Otherwise a forged own-runner/receipt row could disappear into a valid v4 projection.
    const extra = additions();
    const projected = structuredClone(value);
    const group = tools(projected);
    group.files = group.files.filter((r: Row) => r.path !== extra.tool.path);
    group.inventory_sha256 = hash(canonical(group.files));
    projected.receipts = projected.receipts.filter((r: Row) => !extra.receipts.some(e => e.path === r.path));
    const inherited = validateV4(seal(projected), checkCurrent);
    checks.push(...inherited.checks.filter(c => !["candidate-id", "manifest-self-digest"].includes(c.id)));
  } catch { checks.push({id: "v4-exact-projection", result: "fail"}); }
  return {schema_version: "alchlang.p03-currentness-validation/v5-candidate",
    result: checks.every(c => c.result === "pass") ? "pass" : "fail",
    checks, artifact_replay_performed: false, authority_effect: "none"};
}

export function buildCandidate(date = new Date().toISOString().slice(0, 10)): Candidate {
  const before = additions();
  let base: Candidate;
  try { base = buildV4(date); }
  finally { assert.deepEqual(additions(), before, "P03_V5_SELECTED_CUSTODY_DRIFT"); }
  const value = extend(base, before);
  const validation = validateCandidate(value, true);
  assert.equal(validation.result, "pass", JSON.stringify(validation));
  return value;
}

export function createQualification(candidate: Candidate) {
  const value = qualifyV4(candidate);
  return {...value,
    schema_version: "alchlang.p03-exact-candidate-qualification/v5-candidate",
    candidate: {...value.candidate, path: relative(candidatePath)},
    supersedes_previous_candidate: row(previousCandidate),
    supersedes_previous_qualification: row(previousQualification),
    bindings: {...value.bindings, materializer_and_validator: row(ownPath),
      previous_materializer: row(path.join(implementation, "scripts/p03-exact-candidate-v4.ts"))},
  };
}
export function validateQualification(value: Candidate, candidate: Candidate) {
  try { assert.deepEqual(value, createQualification(candidate)); return {result: "pass"}; }
  catch { return {result: "fail"}; }
}

function main() {
  const args = process.argv.slice(2);
  if (args.some(a => a.startsWith("--write"))) throw Error("P03_HISTORICAL_WRITE_DISABLED: v5 measurement is stdout-only");
  if (args.length !== 1 || !["--measure", "--check", "--replay"].includes(args[0]!))
    throw Error("usage: p03-exact-candidate-v5.ts --measure|--check|--replay");
  if (args[0] === "--measure") {
    const candidate = buildCandidate();
    process.stdout.write(JSON.stringify({candidate, qualification: createQualification(candidate)}, null, 2) + "\n");
    return;
  }
  const candidate = read(candidatePath);
  if (args[0] === "--replay") {
    const measured = buildCandidate(candidate.date);
    compareArtifactReplay(candidate, measured);
    assert.deepEqual(read(qualificationPath), createQualification(measured), "P03_QUALIFICATION_REPLAY_MISMATCH");
    process.stdout.write(JSON.stringify({result: "pass", artifact_replay_performed: true,
      candidate_id: candidate.candidate_id, source_rows: candidate.source_groups.reduce((n: number, g: any) => n + g.files.length, 0),
      archive_rows: candidate.package_archives.reduce((n: number, g: any) => n + g.files.length, 0),
      generated_rows: candidate.generated_projects.reduce((n: number, g: any) => n + g.files.length, 0),
      lifecycle_result: "blocked", authority_effect: "none"}) + "\n");
    return;
  }
  const result = validateCandidate(candidate, true);
  result.checks.push({id: "qualification-current", result: validateQualification(read(qualificationPath), candidate).result as "pass" | "fail"});
  result.result = result.checks.every(c => c.result === "pass") ? "pass" : "fail";
  process.stdout.write(JSON.stringify(result, null, 2) + "\n");
  if (result.result !== "pass") process.exitCode = 1;
}
if (process.argv[1] && path.resolve(process.argv[1]) === ownPath) main();
