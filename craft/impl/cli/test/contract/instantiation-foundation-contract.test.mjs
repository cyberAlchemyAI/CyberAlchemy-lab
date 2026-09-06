import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { canonicalJson } from "../../tools/validate-foundation-contract.mjs";
import {
  Candidate3ContractError,
  sealCandidate3Contract,
  sha256,
  validateCandidate3Contract
} from "../../contracts/validate-foundation-contract.candidate-3.mjs";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(testDir, "../../../../../..");
const contractPath = path.resolve(testDir, "../../contracts/foundation-contract.candidate-3.json");
const schemaPath = path.resolve(testDir, "../../contracts/foundation-contract.candidate-3.schema.json");
const candidate2ContractPath = path.resolve(testDir, "../../contracts/foundation-contract.json");
const candidate2SchemaPath = path.resolve(testDir, "../../contracts/foundation-contract.schema.json");
const accepted = JSON.parse(fs.readFileSync(contractPath, "utf8"));
const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));

function expectCode(mutant, code) {
  assert.throws(
    () => validateCandidate3Contract(sealCandidate3Contract(mutant)),
    (error) => error instanceof Candidate3ContractError && error.code === code
  );
}

test("candidate-3 guarded instantiation contract passes", () => {
  assert.equal(validateCandidate3Contract(accepted).result, "pass");
  assert.equal(accepted.baseline_binding.baseline_id, "domainspec-meta-types-current-implemented@2");
  assert.equal(accepted.baseline_binding.selected_realization.meta_type_id, "DS-D1.1");
  assert.equal(accepted.baseline_binding.selected_realization.language, "typescript");
});

test("candidate-2 contract and schema remain exact immutable predecessors", () => {
  assert.equal(sha256(fs.readFileSync(candidate2ContractPath)), accepted.supersedes.contract.sha256);
  assert.equal(sha256(fs.readFileSync(candidate2SchemaPath)), accepted.supersedes.schema.sha256);
});

test("all decision, baseline, and selected-realization bindings match live bytes", () => {
  for (const binding of Object.values(accepted.decision_bindings)) {
    assert.equal(sha256(fs.readFileSync(path.resolve(repoRoot, binding.path))), binding.sha256);
  }
  assert.equal(
    sha256(fs.readFileSync(path.resolve(repoRoot, accepted.baseline_binding.manifest.path))),
    accepted.baseline_binding.manifest.sha256
  );
  for (const binding of ["source", "provider", "binding"]) {
    const selected = accepted.baseline_binding.selected_realization[binding];
    assert.equal(sha256(fs.readFileSync(path.resolve(repoRoot, selected.path))), selected.sha256);
  }
});

test("the selected row is exactly present in the frozen baseline", () => {
  const baseline = JSON.parse(fs.readFileSync(path.resolve(repoRoot, accepted.baseline_binding.manifest.path), "utf8"));
  assert.equal(baseline.baseline_id, accepted.baseline_binding.baseline_id);
  assert.equal(baseline.baseline_digest, accepted.baseline_binding.baseline_digest);
  assert.equal(
    baseline.realization_rows.filter((row) =>
      row.meta_type_id === accepted.baseline_binding.selected_realization.meta_type_id &&
      row.language === accepted.baseline_binding.selected_realization.language &&
      canonicalJson(row) === canonicalJson(accepted.baseline_binding.selected_realization)
    ).length,
    1
  );
});

test("instantiate surface is exact and all writes are guarded create-only", () => {
  const command = accepted.supported_surface.commands.find((entry) => entry.name === "instantiate");
  assert.deepEqual(command, {
    name: "instantiate",
    arguments: ["<explicit-project-root>"],
    options: [
      { name: "--node", value: "<feature-id>:<node-id>", required: true },
      { name: "--language", value: "typescript", required: true },
      { name: "--target-root", value: "<explicit-new-empty-directory>", required: true }
    ]
  });
  assert.equal(accepted.supported_surface.writes.mode, "guarded-atomic-create-only");
  assert.equal(accepted.supported_surface.writes.preexisting_output, "reject");
  assert.equal(accepted.supported_surface.writes.undeclared_write, "reject");
});

test("unknown contract members and weakened write safety fail closed", () => {
  expectCode({ ...accepted, extension_bag: {} }, "MTCLI_CONTRACT_SCHEMA");
  const overwrite = structuredClone(accepted);
  overwrite.supported_surface.writes.preexisting_output = "overwrite";
  expectCode(overwrite, "MTCLI_CONTRACT_WRITE_SCOPE");
  const partial = structuredClone(accepted);
  partial.supported_surface.writes.partial_publication = "best-effort";
  expectCode(partial, "MTCLI_CONTRACT_WRITE_SCOPE");
});

test("baseline, realization, and command drift fail closed", () => {
  const baseline = structuredClone(accepted);
  baseline.baseline_binding.baseline_digest = "f".repeat(64);
  expectCode(baseline, "MTCLI_CONTRACT_BASELINE");
  const realization = structuredClone(accepted);
  realization.baseline_binding.selected_realization.source.sha256 = "f".repeat(64);
  expectCode(realization, "MTCLI_CONTRACT_BASELINE");
  const command = structuredClone(accepted);
  command.supported_surface.commands[2].options.pop();
  expectCode(command, "MTCLI_CONTRACT_WRITE_SCOPE");
});

test("contract evidence cannot inflate implementation or relationship claims", () => {
  for (const field of ["instantiate_implementation", "generated_target_conformance", "relationship_enforcement", "behavioral_effect_enforcement"]) {
    const mutant = structuredClone(accepted);
    mutant.claim_ceiling[field] = true;
    expectCode(mutant, "MTCLI_CONTRACT_CLAIM_CEILING");
  }
});

test("stale self-digests fail closed", () => {
  assert.throws(() => validateCandidate3Contract({ ...accepted, input_digest: "0".repeat(64) }), (error) => error.code === "MTCLI_CONTRACT_INPUT_DIGEST");
  assert.throws(() => validateCandidate3Contract({ ...accepted, contract_digest: "0".repeat(64) }), (error) => error.code === "MTCLI_CONTRACT_DIGEST");
});
