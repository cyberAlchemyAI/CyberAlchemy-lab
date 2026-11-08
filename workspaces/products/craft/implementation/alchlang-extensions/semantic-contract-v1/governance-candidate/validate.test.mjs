import assert from "node:assert/strict";
import {createHash} from "node:crypto";
import {cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync} from "node:fs";
import {tmpdir} from "node:os";
import {resolve} from "node:path";
import test from "node:test";

import {validateGovernanceCandidate} from "./validate.mjs";

const candidateRoot = import.meta.dirname;
const extensionRoot = resolve(candidateRoot, "..");
const repositoryRoot = resolve(extensionRoot, "../../../../../../..");
const sha256 = (path) => createHash("sha256").update(readFileSync(path)).digest("hex");

function withCandidateCopy(run) {
  const root = mkdtempSync(resolve(tmpdir(), "alch-governance-candidate-"));
  const copy = resolve(root, "governance-candidate");
  cpSync(candidateRoot, copy, {recursive: true});
  try { run(copy); } finally { rmSync(root, {recursive: true, force: true}); }
}

function rewriteAndRebind(copy, filename, mutate) {
  const path = resolve(copy, filename);
  const value = JSON.parse(readFileSync(path, "utf8"));
  mutate(value);
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
  const manifestPath = resolve(copy, "manifest.json");
  const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
  manifest.candidate_files.find((row) => row.path === filename).sha256 = sha256(path);
  writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
}

test("current governance candidate passes without claiming governed conformance", () => {
  const result = validateGovernanceCandidate();
  assert.equal(result.overall, "PASS");
  assert.equal(result.governed_conformance_status, "not_evaluable");
  assert.equal(result.constitution_adopted, false);
  assert.equal(result.authority_effect, "none");
});

test("a digest-valid silent fallback policy is rejected", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "degraded-mode-policy.json", (policy) => {
      policy.silent_fallback_allowed = true;
    });
    const result = validateGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "degraded-no-silent-fallback").outcome, "BLOCK");
  });
});

test("a digest-valid implicit adoption selection is rejected", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "adoption-request.json", (request) => {
      request.decision_state = "selected";
      request.selected_option_id = "ALCH-SPC-ADOPT-EXACT-CANDIDATE";
      request.constitution_adopted = true;
    });
    const result = validateGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "adoption-awaiting-owner").outcome, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "adoption-authority-none").outcome, "BLOCK");
  });
});

test("a missing declared Alch source blocks without an alternate path", () => {
  const emptyExtension = mkdtempSync(resolve(tmpdir(), "alch-governance-missing-source-"));
  try {
    const result = validateGovernanceCandidate({extensionRoot: emptyExtension, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "alch-constitution-id").outcome, "BLOCK");
  } finally {
    rmSync(emptyExtension, {recursive: true, force: true});
  }
});
