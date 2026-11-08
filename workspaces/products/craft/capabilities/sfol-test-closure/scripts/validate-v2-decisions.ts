import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const capabilityRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const decisionsRoot = resolve(capabilityRoot, "decisions");
function sha256(value: string | Buffer): string { return createHash("sha256").update(value).digest("hex"); }
function file(path: string): string { return sha256(readFileSync(resolve(capabilityRoot, path))); }
function json(path: string): any { return JSON.parse(readFileSync(resolve(capabilityRoot, path), "utf8")); }
function candidateDigest(candidate: any): string { const { candidate_digest: _ignored, ...unsigned } = candidate; return sha256(JSON.stringify(unsigned)); }
function selectionDigest(selection: any): string { const { selection_digest: _ignored, ...unsigned } = selection; return sha256(JSON.stringify(unsigned)); }
function fail(code: string): never { throw new Error(code); }
function assertBindings(record: any, label: string): void {
  for (const binding of record.source_bindings ?? []) {
    if (file(binding.path) !== binding.sha256) fail(`${label}_SOURCE_DRIFT:${binding.path}`);
  }
}

const profile = json("decisions/profile-eligibility-candidate.json");
if (
  profile.decision_kind !== "domainspec-profile-eligibility" ||
  profile.subject.sha256 !== file("domainspec-v2/development-profile.json") ||
  profile.source_bindings[1].sha256 !== file("domainspec-v2/project.json") ||
  profile.candidate_digest !== candidateDigest(profile) ||
  profile.candidate_digest !== "23fa1cd1dad32f24c7ce1e72333b02d47f233464e5d329aa59cddb7f275ed709" ||
  profile.status !== "awaiting-owner-decision" ||
  profile.authority_effect !== "none"
) fail("SFOL_V2_PROFILE_DECISION_INVALID");
assertBindings(profile, "SFOL_V2_PROFILE_DECISION");

const source = json("decisions/domainspec-source-acceptance-v2-candidate.json");
if (
  source.decision_kind !== "domainspec-source-acceptance" ||
  source.subject.sha256 !== file("domainspec-v2/project.json") ||
  source.candidate_digest !== candidateDigest(source) ||
  source.status !== "awaiting-owner-decision" ||
  source.authority_effect !== "none" ||
  !source.prerequisite_decisions.some((item: any) => item.decision_id === profile.decision_id && item.candidate_digest === profile.candidate_digest)
) fail("SFOL_V2_SOURCE_DECISION_INVALID");
assertBindings(source, "SFOL_V2_SOURCE_DECISION");

const system = json("decisions/system-ontology-v2-admission-candidate.json");
if (
  system.decision_kind !== "system-ontology-admission" ||
  system.subject.sha256 !== file("generated-v2/system-ontology.json") ||
  system.candidate_digest !== candidateDigest(system) ||
  system.status !== "awaiting-owner-decision" ||
  system.authority_effect !== "none"
) fail("SFOL_V2_SYSTEM_DECISION_INVALID");
assertBindings(system, "SFOL_V2_SYSTEM_DECISION");

const selectionKeySet = ["authority_effect", "candidate_digest", "claim_limit", "decided_at", "decision_id", "decision_source", "owner_identity", "owner_route", "schema_version", "selected_option", "selection_digest", "selection_id", "subject_sha256"];
function assertSelection(path: string, candidate: any, selection: any, expected: { selection_id: string; option: string; authority_effect: string; prerequisites?: string[] }): void {
  if (JSON.stringify(Object.keys(selection).sort()) !== JSON.stringify([...selectionKeySet, ...(expected.prerequisites ? ["prerequisite_selection_digests"] : [])].sort())) fail(`SFOL_V2_SELECTION_KEYS:${path}`);
  if (
    selection.schema_version !== "domainspec.owner-decision-selection/v1" ||
    selection.selection_id !== expected.selection_id ||
    selection.decision_id !== candidate.decision_id ||
    selection.candidate_digest !== candidate.candidate_digest ||
    selection.subject_sha256 !== candidate.subject.sha256 ||
    selection.selected_option !== expected.option ||
    selection.owner_identity !== "repository-user" ||
    selection.owner_route !== candidate.owner_route ||
    selection.authority_effect !== expected.authority_effect ||
    !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(selection.decided_at) ||
    selection.selection_digest !== selectionDigest(selection)
  ) fail(`SFOL_V2_SELECTION_BINDING:${path}`);
  if (expected.prerequisites && JSON.stringify(selection.prerequisite_selection_digests) !== JSON.stringify(expected.prerequisites)) fail(`SFOL_V2_SELECTION_PREREQUISITES:${path}`);
}

const profileSelection = json("decisions/profile-eligibility-selection.json");
assertSelection("profile-eligibility-selection.json", profile, profileSelection, {
  selection_id: "DSV2-SEL-SFOL-PROFILE-ELIGIBILITY-V2-001",
  option: "ELIGIBLE-EXACT",
  authority_effect: "domainspec-profile-eligibility-only",
});
const sourceSelection = json("decisions/domainspec-source-acceptance-v2-selection.json");
assertSelection("domainspec-source-acceptance-v2-selection.json", source, sourceSelection, {
  selection_id: "DSV2-SEL-SFOL-DOMAINSPEC-SOURCE-V2-001",
  option: "ACCEPT-EXACT",
  authority_effect: "domainspec-source-acceptance-only",
  prerequisites: [
    "3f186a19a873b1dccb153e8440c87332b556c2e21b012d2998c306de3317bb02",
    "ddfc23a15b90b3920409589faeb1854202d1f8e57225067a8550d9190bd26fd1",
    "1d544c406395935a34983dd202234048c0fbaa0b41d8f93c1cb3c3047c2712e5",
    profileSelection.selection_digest,
  ],
});
const systemSelection = json("decisions/system-ontology-v2-admission-selection.json");
assertSelection("system-ontology-v2-admission-selection.json", system, systemSelection, {
  selection_id: "DSV2-SEL-SFOL-SYSTEM-ONTOLOGY-V2-001",
  option: "ADMIT-EXACT",
  authority_effect: "system-ontology-admission-only",
  prerequisites: [
    "3f186a19a873b1dccb153e8440c87332b556c2e21b012d2998c306de3317bb02",
    "ddfc23a15b90b3920409589faeb1854202d1f8e57225067a8550d9190bd26fd1",
    "1d544c406395935a34983dd202234048c0fbaa0b41d8f93c1cb3c3047c2712e5",
    profileSelection.selection_digest,
    sourceSelection.selection_digest,
  ],
});

process.stdout.write(`${JSON.stringify({
  result: "pass",
  authority_effect: "none",
  profile_decision: { decision_id: profile.decision_id, candidate_digest: profile.candidate_digest, status: profile.status },
  source_decision: { decision_id: source.decision_id, candidate_digest: source.candidate_digest, status: source.status },
  system_decision: { decision_id: system.decision_id, candidate_digest: system.candidate_digest, status: system.status },
  selections_written: 3,
  selections: [profileSelection, sourceSelection, systemSelection].map((selection) => ({ selection_id: selection.selection_id, selected_option: selection.selected_option, selection_digest: selection.selection_digest, authority_effect: selection.authority_effect })),
}, null, 2)}\n`);
