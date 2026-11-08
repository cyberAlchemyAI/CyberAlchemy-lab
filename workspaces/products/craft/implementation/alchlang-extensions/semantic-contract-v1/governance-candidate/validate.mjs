#!/usr/bin/env node
import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {pathToFileURL} from "node:url";

const defaultCandidateRoot = import.meta.dirname;
const defaultExtensionRoot = resolve(defaultCandidateRoot, "..");
const defaultRepositoryRoot = resolve(defaultExtensionRoot, "../../../../../../..");
const sha256 = (path) => createHash("sha256").update(readFileSync(path)).digest("hex");
const readJson = (path) => JSON.parse(readFileSync(path, "utf8"));

export function validateGovernanceCandidate({
  candidateRoot = defaultCandidateRoot,
  extensionRoot = defaultExtensionRoot,
  repositoryRoot = defaultRepositoryRoot,
} = {}) {
  const checks = [];
  const check = (checkId, condition, detail) => checks.push({
    check_id: checkId,
    outcome: condition ? "PASS" : "BLOCK",
    ...(detail ? {detail} : {}),
  });

  let manifest;
  let compatibility;
  let degraded;
  let evidence;
  let adoption;
  let constitution;
  try {
    manifest = readJson(resolve(candidateRoot, "manifest.json"));
    compatibility = readJson(resolve(candidateRoot, "compatibility-policy.json"));
    degraded = readJson(resolve(candidateRoot, "degraded-mode-policy.json"));
    evidence = readJson(resolve(candidateRoot, "conformance-evidence.json"));
    adoption = readJson(resolve(candidateRoot, "adoption-request.json"));
    constitution = readFileSync(resolve(candidateRoot, "SEMANTIC-PRELUDE-CONSTITUTION.md"), "utf8");
  } catch (error) {
    return {
      schema_version: "alchlang.semantic-contract-governance-validation/v1",
      overall: "BLOCK",
      checks: [{check_id: "candidate-files-readable", outcome: "BLOCK", detail: error.message}],
      governed_conformance_status: "not_evaluable",
      authority_effect: "none",
    };
  }

  for (const row of manifest.candidate_files ?? []) {
    let observed = null;
    try { observed = sha256(resolve(candidateRoot, row.path)); } catch {}
    check(`digest:candidate:${row.path}`, observed === row.sha256, `expected ${row.sha256}; observed ${observed}`);
  }
  for (const row of manifest.dependency_files ?? []) {
    const base = row.base === "extension" ? extensionRoot : repositoryRoot;
    let observed = null;
    try { observed = sha256(resolve(base, row.path)); } catch {}
    check(`digest:${row.base}:${row.path}`, observed === row.sha256, `expected ${row.sha256}; observed ${observed}`);
  }

  let alchSource = "";
  try { alchSource = readFileSync(resolve(extensionRoot, "semantic-prelude.alch"), "utf8"); } catch {}
  check("alch-constitution-id", /constitution-ref "ALCH-CONSTITUTION-SEMANTIC-PRELUDE"/.test(alchSource));
  check("alch-constitution-version", /version "1-candidate"/.test(alchSource));
  check("alch-constitution-candidate", /status candidate/.test(alchSource) && /adopted false/.test(alchSource));
  check("alch-authority-effect-none", /authority-effect none/.test(alchSource));

  check("constitution-status-candidate", constitution.includes("Status: candidate"));
  check("constitution-selector", constitution.includes("Selectors: `profile:semantic-contract-v1`"));
  for (let index = 1; index <= 7; index += 1) {
    check(`constitution-rule-ALCH-SPC-${index}`, constitution.includes(`ALCH-SPC-${index}.`));
  }

  check("compatibility-profile", compatibility.profile === "semantic-contract-v1");
  check("compatibility-breaking-new-version", compatibility.breaking_change_action === "issue-a-new-profile-version");
  check("compatibility-no-silent-assumption", compatibility.silent_compatibility_assumption === false);
  check("compatibility-authority-none", compatibility.constitution_adopted === false && compatibility.authority_effect === "none");

  const expectedTriggers = [
    "compiled-runtime-missing",
    "compiled-runtime-unloadable",
    "source-or-runtime-digest-mismatch",
    "semantic-fixture-failure",
    "cross-consumer-parity-failure",
    "consumer-binding-not-declared",
  ];
  check("degraded-trigger-closure", JSON.stringify(degraded.trigger_conditions) === JSON.stringify(expectedTriggers));
  check("degraded-fail-closed", degraded.default_posture === "fail-closed-for-semantic-claims");
  check("degraded-no-silent-fallback", degraded.silent_fallback_allowed === false && degraded.host_reimplementation_allowed === false);
  check("degraded-not-activated", degraded.implemented_as_runtime_enforcement === false && degraded.constitution_adopted === false);
  check("degraded-authority-none", degraded.authority_effect === "none");

  check("evidence-local-pass", evidence.local_validation_status === "PASS" && evidence.validation_runs.every((row) => row.status === "PASS" && row.failed === 0));
  check("governed-conformance-not-evaluable", evidence.governed_conformance_status === "not_evaluable" && evidence.conformance_blockers.length >= 3);
  check("evidence-no-admission-or-effect", evidence.constitution_adopted === false && evidence.runtime_admitted === false && evidence.effect_authorized === false && evidence.authority_effect === "none");

  check("adoption-exact-constitution", adoption.constitution_sha256 === sha256(resolve(candidateRoot, "SEMANTIC-PRELUDE-CONSTITUTION.md")));
  check("adoption-exact-policies", adoption.compatibility_policy_sha256 === sha256(resolve(candidateRoot, "compatibility-policy.json")) && adoption.degraded_mode_policy_sha256 === sha256(resolve(candidateRoot, "degraded-mode-policy.json")));
  check("adoption-exact-evidence", adoption.conformance_evidence_sha256 === sha256(resolve(candidateRoot, "conformance-evidence.json")));
  check("adoption-awaiting-owner", adoption.decision_state === "awaiting-owner-decision" && adoption.selected_option_id === null);
  check("adoption-option-closure", JSON.stringify(adoption.options.map((row) => row.option_id)) === JSON.stringify([
    "ALCH-SPC-ADOPT-EXACT-CANDIDATE",
    "ALCH-SPC-DEFER-CANDIDATE",
    "ALCH-SPC-REJECT-CANDIDATE",
  ]));
  check("adoption-authority-none", adoption.constitution_adopted === false && adoption.effect_authorized === false && adoption.authority_effect === "none");
  check("manifest-authority-none", manifest.constitution_adopted === false && manifest.runtime_admitted === false && manifest.authority_effect === "none");

  const blocked = checks.filter((row) => row.outcome === "BLOCK").length;
  return {
    schema_version: "alchlang.semantic-contract-governance-validation/v1",
    candidate_id: manifest.candidate_id,
    overall: blocked === 0 ? "PASS" : "BLOCK",
    checks,
    local_validation_status: blocked === 0 ? "PASS" : "BLOCK",
    governed_conformance_status: "not_evaluable",
    constitution_adopted: false,
    runtime_admitted: false,
    authority_effect: "none",
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const result = validateGovernanceCandidate();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  process.exitCode = result.overall === "PASS" ? 0 : 1;
}
