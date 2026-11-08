import assert from "node:assert/strict";
import crypto from "node:crypto";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";

const repo = path.resolve(defaultDomainSpecPackageRoot(), "../../../../..");
const root = "craft/projects/domainspec-v2/development/authoring-to-runtime-v1";
const matrixPath = path.join(repo, root, "evidence/e05-cross-layer-evidence/obligation-matrix.v3-candidate.json");
const predecessorPath = path.join(repo, root, "evidence/e05-cross-layer-evidence/obligation-matrix.v2-candidate.json");
const schemaPath = path.join(repo, root, "evidence-obligation-matrix.v2.schema.json");
const sha256 = (file: string) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const read = (file: string) => fs.readFileSync(path.join(repo, file), "utf8");

function validateMatrix(value: any): void {
  assert.equal(value.schema_version, "alchlang.evidence-obligation-matrix/v2-candidate");
  assert.equal(value.task, "E05");
  assert.equal(value.result, "blocked");
  assert.equal(value.authority_effect, "none");
  assert.equal(sha256(predecessorPath), "09454f92902dbc11f0eb2ab7f0d9308a01a09b7b6a5baedbde138d855f41261b");
  const predecessor = JSON.parse(fs.readFileSync(predecessorPath, "utf8"));
  const expected = structuredClone(predecessor);
  expected.current_boundaries.E03.path = `${root}/evidence/e03-evf-evidence-join/qualification.v4-candidate.json`;
  expected.current_boundaries.E03.sha256 = sha256(path.join(repo, expected.current_boundaries.E03.path));
  expected.current_boundaries.E04.path = `${root}/evidence/e04-runtime-observation-join/qualification.v4-candidate.json`;
  expected.current_boundaries.E04.sha256 = sha256(path.join(repo, expected.current_boundaries.E04.path));
  assert.deepEqual(value, expected);
  assert.deepEqual(value.assessments, predecessor.assessments);
  assert.deepEqual(value.coverage, predecessor.coverage);
  assert.deepEqual(value.test_files, predecessor.test_files);
  assert.equal(value.current_boundaries.E03.path, `${root}/evidence/e03-evf-evidence-join/qualification.v4-candidate.json`);
  assert.equal(value.current_boundaries.E04.path, `${root}/evidence/e04-runtime-observation-join/qualification.v4-candidate.json`);
  const validation = spawnSync("python3", ["-c",
    "import json,jsonschema,sys; jsonschema.Draft202012Validator(json.load(open(sys.argv[1]))).validate(json.load(sys.stdin))",
    schemaPath], { encoding: "utf8", timeout: 10000, input: JSON.stringify(value) });
  assert.equal(validation.status, 0, validation.stderr || String(validation.error));
  assert.equal(value.base_matrix.path, `${root}/evidence/e05-cross-layer-evidence/obligation-matrix.json`);
  for (const binding of [value.base_matrix, ...Object.values(value.current_boundaries), ...value.test_files] as Array<{ path: string; sha256: string }>) {
    assert.equal(sha256(path.join(repo, binding.path)), binding.sha256, binding.path);
  }
  const base = JSON.parse(read(value.base_matrix.path));
  assert.equal(base.obligations.length, 32);
  assert.deepEqual(value.assessments.map((item: any) => item.id), base.obligations.map((item: any) => item.id));
  assert.deepEqual(Object.fromEntries(["E01", "E02", "E03", "E04"].map(task =>
    [task, value.assessments.filter((item: any) => item.id.startsWith(task)).length])), value.coverage.by_task);
  assert.deepEqual(value.assessments.filter((item: any) => item.status === "blocked").map((item: any) => item.id),
    ["E03-O02", "E03-O03", "E03-O04", "E03-O05"]);
  const boundTests = new Set(value.test_files.map((binding: any) => binding.path));
  for (let index = 0; index < 32; index += 1) {
    const obligation = base.obligations[index];
    const assessment = value.assessments[index];
    assert.equal(obligation.evidence_kind, "behavioral", obligation.id);
    assert.equal(obligation.representation_only, false, obligation.id);
    assert.ok(boundTests.has(obligation.test_file), `${obligation.id}: test file not exact-bound`);
    const selector = assessment.test_name ?? obligation.test_name;
    assert.ok(read(obligation.test_file).includes(`test("${selector}"`), `${obligation.id}: missing current behavioral test selector`);
    assert.ok(read(base.source_boundaries[obligation.source_task].path).includes(`| ${obligation.source_obligation} |`),
      `${obligation.id}: missing original obligation`);
    if (assessment.status === "pass") assert.equal(assessment.gap, null, obligation.id);
    else assert.ok(assessment.gap.length > 0, obligation.id);
  }
  assert.deepEqual(value.coverage, { obligations: 32, by_task: { E01: 8, E02: 8, E03: 8, E04: 8 },
    satisfied: 28, blocked: 4, unexplained_gaps: 0, representation_only_substitutes: 0 });
  assert.match(value.claim_ceiling, /do not demonstrate provider-authenticated execution pass/u);
}

test("E05 successor assesses all 32 original predicates and explains four execution-pass gaps", () => {
  validateMatrix(JSON.parse(fs.readFileSync(matrixPath, "utf8")));
});

test("E05 successor rejects stale bindings, omitted predicates and false green promotion", () => {
  const original = JSON.parse(fs.readFileSync(matrixPath, "utf8"));
  for (const mutate of [
    (value: any) => { value.test_files[0].sha256 = "0".repeat(64); },
    (value: any) => { value.current_boundaries.E01.path = value.current_boundaries.E02.path;
      value.current_boundaries.E01.sha256 = value.current_boundaries.E02.sha256; },
    (value: any) => { value.assessments.pop(); },
    (value: any) => { value.assessments[17].status = "pass"; value.assessments[17].gap = null; },
    (value: any) => { value.assessments[0].gap = "unexplained"; },
  ]) {
    const changed = structuredClone(original);
    mutate(changed);
    assert.throws(() => validateMatrix(changed));
  }
});
