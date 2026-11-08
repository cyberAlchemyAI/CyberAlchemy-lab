import { createHash } from "node:crypto";
import { copyFileSync, mkdtempSync, mkdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";

import { deriveSelectedSfolClaimCases, replaySelectedSfolClaimCases,
  type SelectedSfolClaimSources, type SelectedSfolRef } from "./index.js";

const repositoryRoot = fileURLToPath(new URL("../../../../../../../../", import.meta.url));
const authRoot = join(repositoryRoot, "auth-foundation");
const prefix = "formalization/cases/AF-ADMIT-AUTHORIZATION-COMMAND-001/";
const decisionPath = "formalization/decisions/AF-ADMIT-AUTHORIZATION-COMMAND-001/sfol-formal-claim-admission-001.json";
const claimPath = `${prefix}FORMAL-CLAIM-SFOL.v1.json`;
const modulePath = `${prefix}SFOL-MODULE.v1.json`;
const manifestPath = `${prefix}SFOL-CLAUSE-ADMISSION-MANIFEST.v1.json`;
const pinned = {
  decision: "c321f051840f56a8cacd5e1b3a29efddc4708f1d438d356a0927237d33199fa5",
  claim: "50ce8c6d7aa49050345cac5ef192b8485dfc3cfb5541c153e382cd4c4d2bd37e",
  module: "e9ba011a399d61e5310d1863306681c0c9907bcfb95ce85f53107dd18ee28742",
  manifest: "f3a8c7ca8598d3eccaef749df376537c7c902c5f42bc8101694dcffdf06a5431",
} as const;
const booleanDomain = [{ tag: "boolean", value: false }, { tag: "boolean", value: true }] as const;
const sha = (value: Buffer | string) => createHash("sha256").update(value).digest("hex");
const tempRoots: string[] = [];
afterEach(() => { for (const path of tempRoots.splice(0)) rmSync(path, { recursive: true, force: true }); });

function ref(root: string, path: string, digest: string): SelectedSfolRef {
  const size = statSync(join(root, path)).size;
  expect(sha(readFileSync(join(root, path)))).toBe(digest);
  return { path, sha256: digest, size_bytes: size };
}

function selection(root = authRoot): SelectedSfolClaimSources {
  return {
    decision: ref(root, decisionPath, pinned.decision),
    claim: ref(root, claimPath, pinned.claim),
    module: ref(root, modulePath, pinned.module),
    clause_manifest: ref(root, manifestPath, pinned.manifest),
    domain: { inputs: {
      unique_trusted_authentication_evidence: booleanDomain,
      unique_complete_route_binding: booleanDomain,
      candidate_command_provenance: booleanDomain,
    } },
    max_cases: 8,
  };
}

function selectedCopy(): { root: string; selected: SelectedSfolClaimSources } {
  const root = mkdtempSync(join(tmpdir(), "tde-sfol-selected-cases-"));
  tempRoots.push(root);
  for (const path of [decisionPath, claimPath, modulePath, manifestPath]) {
    mkdirSync(dirname(join(root, path)), { recursive: true });
    copyFileSync(join(authRoot, path), join(root, path));
  }
  return { root, selected: selection(root) };
}

describe("selected admitted SFOL claim cases", () => {
  it("derives and replays the real admitted Auth three-Boolean clause as eight typed cases", () => {
    const selected = selection();
    const first = deriveSelectedSfolClaimCases(authRoot, selected);
    const second = deriveSelectedSfolClaimCases(authRoot, selected);
    expect(first).toEqual(second);
    expect(first.cases).toHaveLength(8);
    expect(first.oracles).toHaveLength(8);
    const persisted = JSON.parse(readFileSync(join(authRoot, `${prefix}TDE-CASES.v2.json`), "utf8"));
    expect(first.cases).toEqual(persisted.cases);
    expect(first.domain_digest).toBe(persisted.domain_digest);
    expect(first.denominator_digest).toBe(persisted.denominator_digest);
    expect(first.ruleset_digest).toBe(persisted.ruleset.digest);
    expect(first.cases.map(item => item.case_id)).toEqual(first.cases.map(item => item.case_id).sort());
    expect(first.oracles.filter(item => item.expected_value.tag === "boolean" && item.expected_value.value)).toHaveLength(1);
    expect(first.oracles.filter(item => item.expected_value.tag === "boolean" && !item.expected_value.value)).toHaveLength(7);
    expect(first.domain_scope).toBe("full-boolean-valuation-of-selected-clause-inputs");
    expect(first.proof_context_verification).toBe("not-performed");
    expect(first.oracle_provenance).toBe("same-typed-sfol-evaluator");
    expect(first.f5_eligibility).toBe("blocked-missing-domainspec-v4-chain");
    expect(first.claim_ceiling).toContain("no DomainSpec v4 neutral set");
    expect("obligations" in first).toBe(false);
    expect("observations" in first).toBe(false);
    expect(replaySelectedSfolClaimCases(authRoot, selected, first)).toEqual(first);
  });

  it("rejects selected source drift and an altered admission even if its ref is recomputed", () => {
    const { root, selected } = selectedCopy();
    const decisionFile = join(root, decisionPath);
    const changed = JSON.parse(readFileSync(decisionFile, "utf8"));
    changed.authority_effect = "not-admitted";
    writeFileSync(decisionFile, JSON.stringify(changed));
    expect(() => deriveSelectedSfolClaimCases(root, selected)).toThrow(/SOURCE_DRIFT/);
    const replaced = { ...selected, decision: { path: decisionPath, sha256: sha(readFileSync(decisionFile)), size_bytes: statSync(decisionFile).size } };
    expect(() => deriveSelectedSfolClaimCases(root, replaced)).toThrow(/ADMISSION_MISMATCH/);
  });

  it("rejects a changed claim, module and manifest against the exact selection", () => {
    for (const path of [claimPath, modulePath, manifestPath]) {
      const { root, selected } = selectedCopy();
      writeFileSync(join(root, path), `${readFileSync(join(root, path), "utf8")} `);
      expect(() => deriveSelectedSfolClaimCases(root, selected)).toThrow(/SOURCE_DRIFT/);
    }
  });

  it("rejects missing, extra, reordered or rewritten cases and oracles on replay", () => {
    const selected = selection();
    const current = deriveSelectedSfolClaimCases(authRoot, selected);
    for (const edit of [
      (value: any) => { value.cases.pop(); },
      (value: any) => { value.cases.push(value.cases[0]); },
      (value: any) => { value.cases.reverse(); },
      (value: any) => { value.cases[0].inputs.candidate_command_provenance.value = true; },
      (value: any) => { value.oracles[0].expected_value.value = true; },
    ]) {
      const changed = structuredClone(current) as any;
      edit(changed);
      changed.case_set_digest = sha(JSON.stringify(changed));
      expect(() => replaySelectedSfolClaimCases(authRoot, selected, changed)).toThrow(/REPLAY_MISMATCH/);
    }
  });

  it("rejects an insufficient finite-case budget", () => {
    const selected = selection();
    expect(() => deriveSelectedSfolClaimCases(authRoot, { ...selected, max_cases: 7 }))
      .toThrow(/DERIVATION_FAILED/);
  });

  it("requires an explicit domain for every declared input", () => {
    const selected = selection();
    const domain = structuredClone(selected.domain);
    delete (domain.inputs as Record<string, unknown>).candidate_command_provenance;
    expect(() => deriveSelectedSfolClaimCases(authRoot, { ...selected, domain }))
      .toThrow(/DERIVATION_FAILED/);
  });

  it("refuses a narrowed Boolean domain instead of calling one valuation complete", () => {
    const selected = selection();
    const domain = structuredClone(selected.domain);
    (domain.inputs as Record<string, unknown>).candidate_command_provenance = [{ tag: "boolean", value: true }];
    expect(() => deriveSelectedSfolClaimCases(authRoot, { ...selected, domain }))
      .toThrow(/DERIVATION_FAILED/);
  });
});
