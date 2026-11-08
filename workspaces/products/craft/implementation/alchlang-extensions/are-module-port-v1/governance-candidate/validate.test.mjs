import assert from "node:assert/strict";
import {createHash} from "node:crypto";
import {cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync} from "node:fs";
import {tmpdir} from "node:os";
import {resolve} from "node:path";
import test from "node:test";

import {validateModulePortGovernanceCandidate} from "./validate.mjs";

const candidateRoot = import.meta.dirname;
const extensionRoot = resolve(candidateRoot, "..");
const repositoryRoot = resolve(extensionRoot, "../../../../../../..");
const sha256 = (path) => createHash("sha256").update(readFileSync(path)).digest("hex");

function withCandidateCopy(run) {
  const root = mkdtempSync(resolve(tmpdir(), "are-module-port-governance-"));
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

test("exact activation realization passes with local enforcement and no effect authority", () => {
  const result = validateModulePortGovernanceCandidate();
  assert.equal(result.overall, "PASS");
  assert.equal(result.governed_conformance_status, "not_evaluable");
  assert.equal(result.product_approved, true);
  assert.equal(result.constitution_adopted, true);
  assert.equal(result.runtime_admitted, true);
  assert.equal(result.binding_admitted, true);
  assert.equal(result.operational_authorized, true);
  assert.equal(result.activation_eligible, true);
  assert.equal(result.activation_selected, true);
  assert.equal(result.cutover_completed, true);
  assert.equal(result.enforcement_active, true);
  assert.equal(result.effect_authorized, false);
});

test("Rust binding admission is selected exactly without enabling enforcement", () => {
  const result = validateModulePortGovernanceCandidate();
  assert.equal(result.overall, "PASS");
  assert.equal(result.checks.find((row) => row.check_id === "rust-binding-evidence-pass").outcome, "PASS");
  assert.equal(result.checks.find((row) => row.check_id === "rust-binding-admission-selected-exactly").outcome, "PASS");
  assert.equal(result.binding_admitted, true);
  assert.equal(result.enforcement_active, true);
});

test("Rust binding admission cannot be broadened into activation", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "rust-binding-admission-request.json", (request) => {
      request.enforcement_active = true;
      request.effect_authorized = true;
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "rust-binding-admission-grants-no-enforcement").outcome, "BLOCK");
  });
});

test("operational authorization cannot be broadened into activation or effects", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "operational-authorization.json", (request) => {
      request.activation_selected = true;
      request.enforcement_active = true;
      request.effect_authorized = true;
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "operational-authorization-grants-no-activation").outcome, "BLOCK");
  });
});

test("operational authorization remains bound to the exact admitted binding", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "operational-authorization.json", (request) => {
      request.subject_binding_admission_sha256 = "0".repeat(64);
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "operational-authorization-selected-exactly").outcome, "BLOCK");
  });
});

test("realized activation cannot be broadened into effect authority", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "activation-request.json", (request) => {
      request.effect_authorized = true;
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "activation-realized-without-effect-authority").outcome, "BLOCK");
  });
});

test("cutover evidence cannot substitute an unbound implementation", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "cutover-realization-evidence.json", (evidence) => {
      evidence.source_files[0].sha256 = "0".repeat(64);
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "cutover-source-digests").outcome, "BLOCK");
  });
});

test("packaged verifier evidence cannot substitute binary bytes", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "packaged-verifier-evidence.json", (evidence) => {
      evidence.binary.sha256 = "0".repeat(64);
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "packaged-verifier-binary-bound").outcome, "BLOCK");
  });
});

test("packaged verifier evidence cannot authorize fallback or effects", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "packaged-verifier-evidence.json", (evidence) => {
      evidence.fallback_allowed = true;
      evidence.effect_authorized = true;
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "packaged-verifier-no-runtime-toolchain-or-effects").outcome, "BLOCK");
  });
});

test("signed envelope evidence cannot claim release publication or effects", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "signed-distribution-envelope-evidence.json", (evidence) => {
      evidence.release_eligible = true;
      evidence.published = true;
      evidence.effect_authorized = true;
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "signed-envelope-no-release-or-effects").outcome, "BLOCK");
  });
});

test("signed envelope evidence cannot substitute signature or bundle bytes", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "signed-distribution-envelope-evidence.json", (evidence) => {
      evidence.bundle_manifest.sha256 = "0".repeat(64);
      evidence.signature.sha256 = "f".repeat(64);
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "signed-envelope-bytes-bound").outcome, "BLOCK");
  });
});

test("a digest-valid partial composition policy is rejected", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "degraded-mode-policy.json", (policy) => { policy.partial_composition_allowed = true; });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "degraded-no-partial-port").outcome, "BLOCK");
  });
});

test("product approval cannot be broadened into Constitution adoption", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "product-approval-request.json", (request) => {
      request.constitution_adopted = true;
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "product-grants-no-authority").outcome, "BLOCK");
  });
});

test("a fabricated Constitution adoption selection is rejected", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "adoption-request.json", (request) => {
      request.selected_option_id = "fabricated";
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "adoption-selected-exactly").outcome, "BLOCK");
  });
});

test("Constitution adoption cannot be broadened into runtime admission", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "adoption-request.json", (request) => {
      request.runtime_admitted = true;
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "adoption-grants-no-runtime-authority").outcome, "BLOCK");
  });
});

test("fabricated runtime admission and activation are independently rejected", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "runtime-admission-request.json", (request) => {
      request.decision_state = "selected";
      request.selected_option_id = "fabricated";
      request.runtime_admitted = true;
    });
    rewriteAndRebind(copy, "activation-request.json", (request) => {
      request.decision_state = "selected";
      request.selected_option_id = "fabricated";
      request.runtime_admitted = true;
      request.enforcement_active = true;
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "admission-selected-exactly").outcome, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "activation-selected-exactly").outcome, "BLOCK");
  });
});

test("runtime admission eligibility remains bound to exact configuration evidence", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "runtime-admission-request.json", (request) => {
      request.subject_configuration_digest = "0".repeat(64);
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "admission-selected-exactly").outcome, "BLOCK");
  });
});

test("runtime admission cannot be broadened into activation", () => {
  withCandidateCopy((copy) => {
    rewriteAndRebind(copy, "runtime-admission-request.json", (request) => {
      request.enforcement_active = true;
      request.effect_authorized = true;
    });
    const result = validateModulePortGovernanceCandidate({candidateRoot: copy, extensionRoot, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "admission-grants-no-activation").outcome, "BLOCK");
  });
});

test("missing canonical Alch source blocks without alternate authority", () => {
  const emptyExtension = mkdtempSync(resolve(tmpdir(), "are-module-port-missing-alch-"));
  try {
    const result = validateModulePortGovernanceCandidate({extensionRoot: emptyExtension, repositoryRoot});
    assert.equal(result.overall, "BLOCK");
    assert.equal(result.checks.find((row) => row.check_id === "alch-constitution-id").outcome, "BLOCK");
  } finally { rmSync(emptyExtension, {recursive: true, force: true}); }
});
