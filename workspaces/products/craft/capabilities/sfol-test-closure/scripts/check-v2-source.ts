import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { compileMintedProject } from "../../../impl/tools/minted-project/compiler.ts";

const capabilityRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourceRoot = resolve(capabilityRoot, "domainspec-v2");
const profilePath = resolve(sourceRoot, "development-profile.json");
const decisionsRoot = resolve(capabilityRoot, "decisions");

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function sha256File(path: string): string {
  return sha256(readFileSync(path));
}

function json(path: string): any {
  return JSON.parse(readFileSync(path, "utf8"));
}

function fail(code: string): never {
  throw new Error(code);
}

const capabilitySelectionPath = resolve(decisionsRoot, "product-capability-v2-adoption-selection.json");
const capabilitySelection = json(capabilitySelectionPath);
if (
  sha256File(capabilitySelectionPath) !== "0bb68b0a26f1c4af9ceab4a9d86976bfc0c1b0abf978a6f3f1682e6a7e4958ce" ||
  capabilitySelection.decision_id !== "DSV2-DEC-SFOL-CAPABILITY-V2-001" ||
  capabilitySelection.candidate_digest !== "0c61e529c2254efd5218044295210644219312965d402f39c1306a4b2b8458fd" ||
  capabilitySelection.subject_sha256 !== "3f9cba9440548191a45d85658da6aa5983cd2be1b0c67acf403580bee95365c6" ||
  capabilitySelection.selected_option !== "ADOPT-EXACT"
) fail("SFOL_V2_CAPABILITY_SELECTION_INVALID");

const ontologySelectionPath = resolve(decisionsRoot, "business-ontology-v2-admission-selection.json");
const ontologySelection = json(ontologySelectionPath);
if (
  sha256File(ontologySelectionPath) !== "08f2ea5cc776c4130130c368244be497a567919ff513043c44ee067567c62932" ||
  ontologySelection.decision_id !== "DSV2-DEC-SFOL-BUSINESS-ONTOLOGY-V2-001" ||
  ontologySelection.candidate_digest !== "3808df3b3b95909a39f9bd503f04c7157556829c7820a83e7eb191d2c0fd2af5" ||
  ontologySelection.subject_sha256 !== "61dfafb5adb03a2f7c43925d166ad64f452180aa317bfa52dd5785a224454fd5" ||
  ontologySelection.selected_option !== "ADMIT-EXACT" ||
  JSON.stringify(ontologySelection.prerequisite_selection_digests) !== JSON.stringify([
    "3f186a19a873b1dccb153e8440c87332b556c2e21b012d2998c306de3317bb02",
    capabilitySelection.selection_digest,
  ]) ||
  JSON.stringify(ontologySelection.additional_source_bindings) !== JSON.stringify([
    { path: "property-denominator.v2-candidate.json", sha256: "33e91a9e530c2ee1eb3cce7d56cd151160ead414ff0ca01991d5feff5aa30156" },
  ])
) fail("SFOL_V2_BUSINESS_ONTOLOGY_SELECTION_INVALID");

const options = {
  developmentProfileRegistry: {
    path: profilePath,
    handle: "sfol-test-closure-v2-development-explicit-v0.2",
  },
};
const first = compileMintedProject(sourceRoot, options);
const second = compileMintedProject(sourceRoot, options);
if (first.graphBytes !== second.graphBytes || first.sourceManifestBytes !== second.sourceManifestBytes) {
  fail("SFOL_V2_SOURCE_NONDETERMINISTIC_COMPILE");
}

const nodeIds = new Set(first.graph.nodes.map((node) => node.node_id));
for (const required of [
  "sfol-test-closure-v2.EvfSelection",
  "sfol-test-closure-v2.OptionalEvfClosureRule",
  "sfol-test-closure-v2.ApplyNegativeControls",
  "sfol-test-closure-v2.BuildTestClosure",
]) {
  if (!nodeIds.has(required)) fail(`SFOL_V2_SOURCE_NODE_MISSING:${required}`);
}
const nodeById = new Map(first.graph.nodes.map((node) => [node.node_id, node]));
const evfSelection = nodeById.get("sfol-test-closure-v2.EvfSelection");
if (
  evfSelection?.kind !== "Policy" ||
  evfSelection.intent !== "Select either not_requested base closure or required EVF evidence for one test-closure request." ||
  evfSelection.body.formal_return_type !== "strategy"
) fail("SFOL_V2_EVF_SELECTION_SEMANTICS_INVALID");
const evfRule = nodeById.get("sfol-test-closure-v2.OptionalEvfClosureRule");
if (
  evfRule?.kind !== "Rule" ||
  evfRule.intent !== "Permit explicit not_requested base closure, require passing content-valid evidence when EVF is selected, and reject invalid or failing supplied EVF evidence."
) fail("SFOL_V2_EVF_RULE_SEMANTICS_INVALID");
const buildClosure = nodeById.get("sfol-test-closure-v2.BuildTestClosure");
if (
  buildClosure?.kind !== "Operation" ||
  buildClosure.intent !== "Materialize exact stage-set, observation, evaluation, and EVF-status closure; require a passing detection matrix only for required EVF."
) fail("SFOL_V2_BUILD_CLOSURE_SEMANTICS_INVALID");
const evidenceClosure = nodeById.get("sfol-test-closure-v2.EvidenceClosure");
const evidenceFields = Array.isArray(evidenceClosure?.body.fields) ? evidenceClosure.body.fields : [];
if (!evidenceFields.some((field) => field && typeof field === "object" && field.name === "evf_status" && field.type === "not_requested-or-passed")) {
  fail("SFOL_V2_EVF_STATUS_FIELD_MISSING");
}
const edgeIds = new Set(first.graph.edges.map((edge) => edge.edge_id));
for (const required of [
  "sfol-test-closure-v2.edge.evf-selection-applies-close",
  "sfol-test-closure-v2.edge.evf-rule-enforces-challenge",
  "sfol-test-closure-v2.edge.evf-rule-enforces-close",
]) {
  if (!edgeIds.has(required)) fail(`SFOL_V2_SOURCE_EDGE_MISSING:${required}`);
}
if (first.graph.nodes.length !== 14 || first.graph.edges.length !== 9) {
  fail("SFOL_V2_SOURCE_DENOMINATOR_INVALID");
}

process.stdout.write(`${JSON.stringify({
  result: "pass",
  source_epoch: "sfol-test-closure-v2",
  source_set_digest: first.graph.source_set_digest,
  profile_sha256: sha256File(profilePath),
  compiled_graph_sha256: sha256(first.graphBytes),
  source_manifest_sha256: sha256(first.sourceManifestBytes),
  compile_runs: 2,
  byte_identical: true,
  nodes: first.graph.nodes.length,
  edges: first.graph.edges.length,
  generated_files_written: 0,
  authority_effect: "none",
}, null, 2)}\n`);
