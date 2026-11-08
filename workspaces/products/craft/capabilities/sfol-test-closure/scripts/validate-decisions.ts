import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const capabilityRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const decisionsRoot = resolve(capabilityRoot, "decisions");

type FileBinding = { path: string; sha256: string };
type Prerequisite = {
  decision_id: string;
  candidate_path: string;
  candidate_digest: string;
  required_option: string;
};
type Candidate = {
  schema_version: string;
  decision_id: string;
  decision_kind: string;
  subject: FileBinding & { identity: string };
  owner_route: string;
  question: string;
  source_bindings: FileBinding[];
  prerequisite_decisions: Prerequisite[];
  options: Array<{ option_id: string; effect: string; authority_effect: string }>;
  selection_contract: {
    separate_selection_required: boolean;
    bind_candidate_digest: string;
    bind_subject_sha256: string;
    required_fields: string[];
    mutation_policy: string;
  };
  status: string;
  authority_effect: string;
  claim_limit: string;
  candidate_digest: string;
};
type Selection = {
  schema_version: string;
  selection_id: string;
  decision_id: string;
  candidate_digest: string;
  subject_sha256: string;
  selected_option: string;
  owner_identity: string;
  owner_route: string;
  decision_source: string;
  decided_at: string;
  authority_effect: string;
  prerequisite_selection_digests?: string[];
  additional_source_bindings?: FileBinding[];
  claim_limit: string;
  selection_digest: string;
};

const candidateNames = [
  "definition-admission-candidate.json",
  "product-capability-adoption-candidate.json",
  "business-ontology-admission-candidate.json",
  "domainspec-source-acceptance-candidate.json",
  "product-capability-v2-adoption-candidate.json",
  "business-ontology-v2-admission-candidate.json"
] as const;
const expectedCandidates = {
  "definition-admission-candidate.json": {
    decision_id: "DSV2-DEC-SFOL-DEFINITIONS-001",
    decision_kind: "definition-admission",
    subject_identity: "DSV2-DEF-SFOL-TEST-CLOSURE-001",
    affirmative_option: "ADMIT-EXACT",
    source_paths: ["definition-candidates.json"],
    prerequisite_ids: [],
    candidate_digest: "6a159ccf30b6c05654b72bbbfd10117266aaa0bcf498c7e5a30af3300331a335"
  },
  "product-capability-adoption-candidate.json": {
    decision_id: "DSV2-DEC-SFOL-CAPABILITY-001",
    decision_kind: "product-capability-adoption",
    subject_identity: "DSV2-CAP-SFOL-TEST-CLOSURE",
    affirmative_option: "ADOPT-EXACT",
    source_paths: ["product-capability.json"],
    prerequisite_ids: ["DSV2-DEC-SFOL-DEFINITIONS-001"],
    candidate_digest: "26221d25523cb4fe9d92b0e9c473cc5bf290b93c45dfa529b01198a8839e238b"
  },
  "business-ontology-admission-candidate.json": {
    decision_id: "DSV2-DEC-SFOL-BUSINESS-ONTOLOGY-001",
    decision_kind: "business-ontology-admission",
    subject_identity: "DSV2-ONTOLOGY-SFOL-TEST-CLOSURE",
    affirmative_option: "ADMIT-EXACT",
    source_paths: ["business-ontology.json", "property-denominator.json"],
    prerequisite_ids: ["DSV2-DEC-SFOL-DEFINITIONS-001", "DSV2-DEC-SFOL-CAPABILITY-001"],
    candidate_digest: "33a0947ff5b8009466fa1bf9b95ada4a3fb0246b46261900507b283af95bd0c1"
  },
  "domainspec-source-acceptance-candidate.json": {
    decision_id: "DSV2-DEC-SFOL-DOMAINSPEC-SOURCE-001",
    decision_kind: "domainspec-source-acceptance",
    subject_identity: "sfol-test-closure@cce24ec830000f7fc805d4de270f6be7998fc1cf38faf3f369980abb61217594",
    affirmative_option: "ACCEPT-EXACT",
    source_paths: ["domainspec/project.json", "domainspec/development-profile.json", "generated/source-manifest.json", "generated/compiled-graph.json", "generated/build-receipt.json", "decisions/definition-admission-selection.json", "decisions/product-capability-adoption-selection.json", "decisions/business-ontology-admission-selection.json"],
    prerequisite_ids: ["DSV2-DEC-SFOL-DEFINITIONS-001", "DSV2-DEC-SFOL-CAPABILITY-001", "DSV2-DEC-SFOL-BUSINESS-ONTOLOGY-001"],
    candidate_digest: "a4824b954804a018267dad80384c458eeb2455d45c5496a040619d1899513af5"
  },
  "product-capability-v2-adoption-candidate.json": {
    decision_id: "DSV2-DEC-SFOL-CAPABILITY-V2-001",
    decision_kind: "product-capability-adoption",
    subject_identity: "DSV2-CAP-SFOL-TEST-CLOSURE-V2",
    affirmative_option: "ADOPT-EXACT",
    source_paths: ["product-capability.v2-candidate.json"],
    prerequisite_ids: ["DSV2-DEC-SFOL-DEFINITIONS-001"],
    candidate_digest: "0c61e529c2254efd5218044295210644219312965d402f39c1306a4b2b8458fd"
  },
  "business-ontology-v2-admission-candidate.json": {
    decision_id: "DSV2-DEC-SFOL-BUSINESS-ONTOLOGY-V2-001",
    decision_kind: "business-ontology-admission",
    subject_identity: "DSV2-ONTOLOGY-SFOL-TEST-CLOSURE-V2",
    affirmative_option: "ADMIT-EXACT",
    source_paths: ["business-ontology.v2-candidate.json", "property-denominator.v2-candidate.json"],
    prerequisite_ids: ["DSV2-DEC-SFOL-DEFINITIONS-001", "DSV2-DEC-SFOL-CAPABILITY-V2-001"],
    candidate_digest: "3808df3b3b95909a39f9bd503f04c7157556829c7820a83e7eb191d2c0fd2af5"
  }
} as const;
const expectedTopLevelKeys = [
  "authority_effect",
  "candidate_digest",
  "claim_limit",
  "decision_id",
  "decision_kind",
  "options",
  "owner_route",
  "prerequisite_decisions",
  "question",
  "schema_version",
  "selection_contract",
  "source_bindings",
  "status",
  "subject"
];
const requiredSelectionFields = [
  "decision_id",
  "candidate_digest",
  "subject_sha256",
  "selected_option",
  "owner_identity",
  "decided_at"
];
const selectionKeys = [
  "authority_effect",
  "candidate_digest",
  "claim_limit",
  "decided_at",
  "decision_id",
  "decision_source",
  "owner_identity",
  "owner_route",
  "schema_version",
  "selected_option",
  "selection_digest",
  "selection_id",
  "subject_sha256"
];

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function sha256File(path: string): string {
  return sha256(readFileSync(path));
}

function canonicalize(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record).sort().map((key) => `${JSON.stringify(key)}:${canonicalize(record[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function fail(code: string, detail: string): never {
  throw new Error(`${code}:${detail}`);
}

function assertExactKeys(value: Record<string, unknown>, expected: string[], label: string): void {
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (JSON.stringify(actual) !== JSON.stringify(wanted)) fail("DECISION_SCHEMA_KEYS", label);
}

function resolveCapabilityPath(relativePath: string): string {
  const absolute = resolve(capabilityRoot, relativePath);
  if (absolute !== capabilityRoot && !absolute.startsWith(`${capabilityRoot}/`)) {
    fail("DECISION_PATH_ESCAPE", relativePath);
  }
  return absolute;
}

function resolveDomainspecPath(relativePath: string): string {
  const domainspecRoot = resolve(capabilityRoot, "domainspec");
  const absolute = resolve(domainspecRoot, relativePath);
  if (absolute !== domainspecRoot && !absolute.startsWith(`${domainspecRoot}/`)) fail("DECISION_SOURCE_INPUT_ESCAPE", relativePath);
  return absolute;
}

function candidateDigest(candidate: Candidate): string {
  const { candidate_digest: _excluded, ...unsigned } = candidate;
  return sha256(JSON.stringify(unsigned));
}

function selectionDigest(selection: Selection): string {
  const { selection_digest: _excluded, ...unsigned } = selection;
  return sha256(JSON.stringify(unsigned));
}

// Parsing this file proves the normative closed schema remains valid JSON. The
// checks below intentionally enforce the exact v1 subset used by these packets
// without introducing a schema-runtime dependency into the capability gate.
const schemaPath = resolve(decisionsRoot, "owner-decision-envelope.schema.json");
const decisionSchema = JSON.parse(readFileSync(schemaPath, "utf8"));
if (decisionSchema.$id !== "domainspec.owner-decision-envelope/v1" || decisionSchema.additionalProperties !== false) {
  fail("DECISION_NORMATIVE_SCHEMA", "owner-decision-envelope.schema.json");
}
const selectionSchemaPath = resolve(decisionsRoot, "owner-decision-selection.schema.json");
const selectionSchema = JSON.parse(readFileSync(selectionSchemaPath, "utf8"));
if (selectionSchema.$id !== "domainspec.owner-decision-selection/v1" || selectionSchema.additionalProperties !== false) {
  fail("DECISION_SELECTION_SCHEMA", "owner-decision-selection.schema.json");
}

const candidates = new Map<string, { candidate: Candidate; name: typeof candidateNames[number] }>();
for (const name of candidateNames) {
  const candidate = JSON.parse(readFileSync(resolve(decisionsRoot, name), "utf8")) as Candidate;
  const expected = expectedCandidates[name];
  assertExactKeys(candidate as unknown as Record<string, unknown>, expectedTopLevelKeys, name);
  assertExactKeys(candidate.subject as unknown as Record<string, unknown>, ["identity", "path", "sha256"], `${name}:subject`);
  candidate.source_bindings.forEach((binding, index) => assertExactKeys(binding as unknown as Record<string, unknown>, ["path", "sha256"], `${name}:source:${index}`));
  candidate.prerequisite_decisions.forEach((prerequisite, index) => assertExactKeys(prerequisite as unknown as Record<string, unknown>, ["decision_id", "candidate_path", "candidate_digest", "required_option"], `${name}:prerequisite:${index}`));
  candidate.options.forEach((option, index) => assertExactKeys(option as unknown as Record<string, unknown>, ["option_id", "effect", "authority_effect"], `${name}:option:${index}`));
  assertExactKeys(candidate.selection_contract as unknown as Record<string, unknown>, ["separate_selection_required", "bind_candidate_digest", "bind_subject_sha256", "required_fields", "mutation_policy"], `${name}:selection_contract`);
  if (candidate.schema_version !== "domainspec.owner-decision-envelope/v1") fail("DECISION_SCHEMA_VERSION", name);
  if (candidate.decision_id !== expected.decision_id || candidate.decision_kind !== expected.decision_kind || candidate.subject.identity !== expected.subject_identity) {
    fail("DECISION_IDENTITY_DRIFT", name);
  }
  if (candidate.status !== "awaiting-owner-decision" || candidate.authority_effect !== "none") {
    fail("DECISION_AUTHORITY_INFLATION", name);
  }
  if (candidate.candidate_digest !== candidateDigest(candidate) || candidate.candidate_digest !== expected.candidate_digest) {
    fail("DECISION_CANDIDATE_DIGEST", name);
  }
  if (candidates.has(candidate.decision_id)) fail("DECISION_ID_DUPLICATE", candidate.decision_id);
  if (candidate.options.length < 3 || new Set(candidate.options.map((option) => option.option_id)).size !== candidate.options.length) {
    fail("DECISION_OPTIONS_INVALID", name);
  }
  if (!(candidate.options.some((option) => option.option_id === "REJECT") && candidate.options.some((option) => option.option_id === "DEFER"))) {
    fail("DECISION_FAIL_CLOSED_OPTIONS_MISSING", name);
  }
  if (!candidate.options.some((option) => option.option_id === expected.affirmative_option && option.authority_effect === "owner-decision-required")) {
    fail("DECISION_AFFIRMATIVE_OPTION_INVALID", name);
  }
  if (JSON.stringify(candidate.source_bindings.map((binding) => binding.path)) !== JSON.stringify(expected.source_paths)) {
    fail("DECISION_SOURCE_SET", name);
  }
  if (JSON.stringify(candidate.prerequisite_decisions.map((item) => item.decision_id)) !== JSON.stringify(expected.prerequisite_ids)) {
    fail("DECISION_PREREQUISITE_SET", name);
  }
  const selection = candidate.selection_contract;
  if (!selection.separate_selection_required || selection.bind_candidate_digest !== "exact" || selection.bind_subject_sha256 !== "exact") {
    fail("DECISION_SELECTION_BINDING_WEAK", name);
  }
  if (JSON.stringify(selection.required_fields) !== JSON.stringify(requiredSelectionFields)) fail("DECISION_SELECTION_FIELDS", name);
  if (selection.mutation_policy !== "candidate-immutable-new-digest-requires-new-review") fail("DECISION_MUTATION_POLICY", name);
  if (sha256File(resolveCapabilityPath(candidate.subject.path)) !== candidate.subject.sha256) fail("DECISION_SUBJECT_DRIFT", name);
  for (const binding of candidate.source_bindings) {
    if (sha256File(resolveCapabilityPath(binding.path)) !== binding.sha256) fail("DECISION_SOURCE_DRIFT", `${name}:${binding.path}`);
  }
  candidates.set(candidate.decision_id, { candidate, name });
}

for (const [decisionId, record] of candidates) {
  const { candidate } = record;
  for (const prerequisite of candidate.prerequisite_decisions) {
    const predecessorRecord = candidates.get(prerequisite.decision_id);
    if (!predecessorRecord) fail("DECISION_PREREQUISITE_MISSING", `${decisionId}:${prerequisite.decision_id}`);
    const predecessor = predecessorRecord.candidate;
    if (predecessor.candidate_digest !== prerequisite.candidate_digest) fail("DECISION_PREREQUISITE_DIGEST", decisionId);
    if (resolveCapabilityPath(prerequisite.candidate_path) !== resolve(decisionsRoot, predecessorRecord.name)) fail("DECISION_PREREQUISITE_PATH", decisionId);
    if (!predecessor.options.some((option) => option.option_id === prerequisite.required_option)) {
      fail("DECISION_PREREQUISITE_OPTION", decisionId);
    }
  }
}

const definitionSelectionPath = resolve(decisionsRoot, "definition-admission-selection.json");
const definitionSelection = JSON.parse(readFileSync(definitionSelectionPath, "utf8")) as Selection;
assertExactKeys(definitionSelection as unknown as Record<string, unknown>, selectionKeys, "definition-admission-selection.json");
const selectedCandidate = candidates.get(definitionSelection.decision_id)?.candidate;
if (!selectedCandidate) fail("DECISION_SELECTION_TARGET", definitionSelection.decision_id);
if (definitionSelection.schema_version !== "domainspec.owner-decision-selection/v1" || definitionSelection.selection_id !== "DSV2-SEL-SFOL-DEFINITIONS-001") {
  fail("DECISION_SELECTION_IDENTITY", definitionSelection.selection_id);
}
if (definitionSelection.candidate_digest !== selectedCandidate.candidate_digest || definitionSelection.subject_sha256 !== selectedCandidate.subject.sha256) {
  fail("DECISION_SELECTION_BINDING", definitionSelection.selection_id);
}
if (definitionSelection.selected_option !== "ADMIT-EXACT" || !selectedCandidate.options.some((option) => option.option_id === definitionSelection.selected_option)) {
  fail("DECISION_SELECTION_OPTION", definitionSelection.selection_id);
}
if (definitionSelection.owner_route !== selectedCandidate.owner_route || definitionSelection.owner_identity !== "repository-user") {
  fail("DECISION_SELECTION_OWNER", definitionSelection.selection_id);
}
if (definitionSelection.authority_effect !== "definition-admission-only" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(definitionSelection.decided_at)) {
  fail("DECISION_SELECTION_EFFECT", definitionSelection.selection_id);
}
if (definitionSelection.selection_digest !== selectionDigest(definitionSelection) || definitionSelection.selection_digest !== "3f186a19a873b1dccb153e8440c87332b556c2e21b012d2998c306de3317bb02") {
  fail("DECISION_SELECTION_DIGEST", definitionSelection.selection_id);
}

const capabilitySelectionPath = resolve(decisionsRoot, "product-capability-adoption-selection.json");
const capabilitySelection = JSON.parse(readFileSync(capabilitySelectionPath, "utf8")) as Selection;
assertExactKeys(capabilitySelection as unknown as Record<string, unknown>, [...selectionKeys, "prerequisite_selection_digests"], "product-capability-adoption-selection.json");
const capabilityCandidate = candidates.get(capabilitySelection.decision_id)?.candidate;
if (!capabilityCandidate) fail("DECISION_SELECTION_TARGET", capabilitySelection.decision_id);
if (capabilitySelection.schema_version !== "domainspec.owner-decision-selection/v1" || capabilitySelection.selection_id !== "DSV2-SEL-SFOL-CAPABILITY-001") {
  fail("DECISION_SELECTION_IDENTITY", capabilitySelection.selection_id);
}
if (capabilitySelection.candidate_digest !== capabilityCandidate.candidate_digest || capabilitySelection.subject_sha256 !== capabilityCandidate.subject.sha256) {
  fail("DECISION_SELECTION_BINDING", capabilitySelection.selection_id);
}
if (capabilitySelection.selected_option !== "ADOPT-EXACT" || !capabilityCandidate.options.some((option) => option.option_id === capabilitySelection.selected_option)) {
  fail("DECISION_SELECTION_OPTION", capabilitySelection.selection_id);
}
if (capabilitySelection.owner_route !== capabilityCandidate.owner_route || capabilitySelection.owner_identity !== "repository-user") {
  fail("DECISION_SELECTION_OWNER", capabilitySelection.selection_id);
}
if (capabilitySelection.authority_effect !== "product-capability-adoption-only" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(capabilitySelection.decided_at)) {
  fail("DECISION_SELECTION_EFFECT", capabilitySelection.selection_id);
}
if (JSON.stringify(capabilitySelection.prerequisite_selection_digests) !== JSON.stringify([definitionSelection.selection_digest])) {
  fail("DECISION_SELECTION_PREREQUISITE", capabilitySelection.selection_id);
}
if (capabilitySelection.selection_digest !== selectionDigest(capabilitySelection) || capabilitySelection.selection_digest !== "ddc8a4839103501bd74aa1512cd1a48db2433a09befe254dc4c551ce9706204a") {
  fail("DECISION_SELECTION_DIGEST", capabilitySelection.selection_id);
}

const businessOntologySelectionPath = resolve(decisionsRoot, "business-ontology-admission-selection.json");
const businessOntologySelection = JSON.parse(readFileSync(businessOntologySelectionPath, "utf8")) as Selection;
assertExactKeys(businessOntologySelection as unknown as Record<string, unknown>, [...selectionKeys, "prerequisite_selection_digests", "additional_source_bindings"], "business-ontology-admission-selection.json");
businessOntologySelection.additional_source_bindings?.forEach((binding, index) => assertExactKeys(binding as unknown as Record<string, unknown>, ["path", "sha256"], `business-ontology-admission-selection.json:source:${index}`));
const businessOntologyCandidate = candidates.get(businessOntologySelection.decision_id)?.candidate;
if (!businessOntologyCandidate) fail("DECISION_SELECTION_TARGET", businessOntologySelection.decision_id);
if (businessOntologySelection.schema_version !== "domainspec.owner-decision-selection/v1" || businessOntologySelection.selection_id !== "DSV2-SEL-SFOL-BUSINESS-ONTOLOGY-001") {
  fail("DECISION_SELECTION_IDENTITY", businessOntologySelection.selection_id);
}
if (businessOntologySelection.candidate_digest !== businessOntologyCandidate.candidate_digest || businessOntologySelection.subject_sha256 !== businessOntologyCandidate.subject.sha256) {
  fail("DECISION_SELECTION_BINDING", businessOntologySelection.selection_id);
}
if (businessOntologySelection.selected_option !== "ADMIT-EXACT" || !businessOntologyCandidate.options.some((option) => option.option_id === businessOntologySelection.selected_option)) {
  fail("DECISION_SELECTION_OPTION", businessOntologySelection.selection_id);
}
if (businessOntologySelection.owner_route !== businessOntologyCandidate.owner_route || businessOntologySelection.owner_identity !== "repository-user") {
  fail("DECISION_SELECTION_OWNER", businessOntologySelection.selection_id);
}
if (businessOntologySelection.authority_effect !== "business-ontology-admission-only" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(businessOntologySelection.decided_at)) {
  fail("DECISION_SELECTION_EFFECT", businessOntologySelection.selection_id);
}
if (JSON.stringify(businessOntologySelection.prerequisite_selection_digests) !== JSON.stringify([definitionSelection.selection_digest, capabilitySelection.selection_digest])) {
  fail("DECISION_SELECTION_PREREQUISITE", businessOntologySelection.selection_id);
}
const expectedAdditionalSources = [{ path: "property-denominator.json", sha256: "db481764813e3f61398d89683b497855ee504173b1cffdfa7ee30450be3cb68d" }];
if (JSON.stringify(businessOntologySelection.additional_source_bindings) !== JSON.stringify(expectedAdditionalSources)) {
  fail("DECISION_SELECTION_ADDITIONAL_SOURCES", businessOntologySelection.selection_id);
}
for (const binding of businessOntologySelection.additional_source_bindings ?? []) {
  if (sha256File(resolveCapabilityPath(binding.path)) !== binding.sha256) fail("DECISION_SELECTION_SOURCE_DRIFT", binding.path);
}
if (businessOntologySelection.selection_digest !== selectionDigest(businessOntologySelection) || businessOntologySelection.selection_digest !== "e34dd8004f3fe0c8d301ee488591030b2ced36c67b2206e20913abe113edae20") {
  fail("DECISION_SELECTION_DIGEST", businessOntologySelection.selection_id);
}

const capabilityV2SelectionPath = resolve(decisionsRoot, "product-capability-v2-adoption-selection.json");
const capabilityV2Selection = JSON.parse(readFileSync(capabilityV2SelectionPath, "utf8")) as Selection;
assertExactKeys(capabilityV2Selection as unknown as Record<string, unknown>, [...selectionKeys, "prerequisite_selection_digests"], "product-capability-v2-adoption-selection.json");
const capabilityV2Candidate = candidates.get(capabilityV2Selection.decision_id)?.candidate;
if (!capabilityV2Candidate) fail("DECISION_SELECTION_TARGET", capabilityV2Selection.decision_id);
if (capabilityV2Selection.schema_version !== "domainspec.owner-decision-selection/v1" || capabilityV2Selection.selection_id !== "DSV2-SEL-SFOL-CAPABILITY-V2-001") {
  fail("DECISION_SELECTION_IDENTITY", capabilityV2Selection.selection_id);
}
if (capabilityV2Selection.candidate_digest !== capabilityV2Candidate.candidate_digest || capabilityV2Selection.subject_sha256 !== capabilityV2Candidate.subject.sha256) {
  fail("DECISION_SELECTION_BINDING", capabilityV2Selection.selection_id);
}
if (capabilityV2Selection.selected_option !== "ADOPT-EXACT" || !capabilityV2Candidate.options.some((option) => option.option_id === capabilityV2Selection.selected_option)) {
  fail("DECISION_SELECTION_OPTION", capabilityV2Selection.selection_id);
}
if (capabilityV2Selection.owner_route !== capabilityV2Candidate.owner_route || capabilityV2Selection.owner_identity !== "repository-user") {
  fail("DECISION_SELECTION_OWNER", capabilityV2Selection.selection_id);
}
if (capabilityV2Selection.authority_effect !== "product-capability-adoption-only" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(capabilityV2Selection.decided_at)) {
  fail("DECISION_SELECTION_EFFECT", capabilityV2Selection.selection_id);
}
if (JSON.stringify(capabilityV2Selection.prerequisite_selection_digests) !== JSON.stringify([definitionSelection.selection_digest])) {
  fail("DECISION_SELECTION_PREREQUISITE", capabilityV2Selection.selection_id);
}
if (capabilityV2Selection.selection_digest !== selectionDigest(capabilityV2Selection) || capabilityV2Selection.selection_digest !== "ddfc23a15b90b3920409589faeb1854202d1f8e57225067a8550d9190bd26fd1") {
  fail("DECISION_SELECTION_DIGEST", capabilityV2Selection.selection_id);
}

const businessOntologyV2SelectionPath = resolve(decisionsRoot, "business-ontology-v2-admission-selection.json");
const businessOntologyV2Selection = JSON.parse(readFileSync(businessOntologyV2SelectionPath, "utf8")) as Selection;
assertExactKeys(businessOntologyV2Selection as unknown as Record<string, unknown>, [...selectionKeys, "prerequisite_selection_digests", "additional_source_bindings"], "business-ontology-v2-admission-selection.json");
businessOntologyV2Selection.additional_source_bindings?.forEach((binding, index) => assertExactKeys(binding as unknown as Record<string, unknown>, ["path", "sha256"], `business-ontology-v2-admission-selection.json:source:${index}`));
const businessOntologyV2Candidate = candidates.get(businessOntologyV2Selection.decision_id)?.candidate;
if (!businessOntologyV2Candidate) fail("DECISION_SELECTION_TARGET", businessOntologyV2Selection.decision_id);
if (businessOntologyV2Selection.schema_version !== "domainspec.owner-decision-selection/v1" || businessOntologyV2Selection.selection_id !== "DSV2-SEL-SFOL-BUSINESS-ONTOLOGY-V2-001") {
  fail("DECISION_SELECTION_IDENTITY", businessOntologyV2Selection.selection_id);
}
if (businessOntologyV2Selection.candidate_digest !== businessOntologyV2Candidate.candidate_digest || businessOntologyV2Selection.subject_sha256 !== businessOntologyV2Candidate.subject.sha256) {
  fail("DECISION_SELECTION_BINDING", businessOntologyV2Selection.selection_id);
}
if (businessOntologyV2Selection.selected_option !== "ADMIT-EXACT" || !businessOntologyV2Candidate.options.some((option) => option.option_id === businessOntologyV2Selection.selected_option)) {
  fail("DECISION_SELECTION_OPTION", businessOntologyV2Selection.selection_id);
}
if (businessOntologyV2Selection.owner_route !== businessOntologyV2Candidate.owner_route || businessOntologyV2Selection.owner_identity !== "repository-user") {
  fail("DECISION_SELECTION_OWNER", businessOntologyV2Selection.selection_id);
}
if (businessOntologyV2Selection.authority_effect !== "business-ontology-admission-only" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(businessOntologyV2Selection.decided_at)) {
  fail("DECISION_SELECTION_EFFECT", businessOntologyV2Selection.selection_id);
}
if (JSON.stringify(businessOntologyV2Selection.prerequisite_selection_digests) !== JSON.stringify([definitionSelection.selection_digest, capabilityV2Selection.selection_digest])) {
  fail("DECISION_SELECTION_PREREQUISITE", businessOntologyV2Selection.selection_id);
}
const expectedV2AdditionalSources = [{ path: "property-denominator.v2-candidate.json", sha256: "33e91a9e530c2ee1eb3cce7d56cd151160ead414ff0ca01991d5feff5aa30156" }];
if (JSON.stringify(businessOntologyV2Selection.additional_source_bindings) !== JSON.stringify(expectedV2AdditionalSources)) {
  fail("DECISION_SELECTION_ADDITIONAL_SOURCES", businessOntologyV2Selection.selection_id);
}
for (const binding of businessOntologyV2Selection.additional_source_bindings ?? []) {
  if (sha256File(resolveCapabilityPath(binding.path)) !== binding.sha256) fail("DECISION_SELECTION_SOURCE_DRIFT", binding.path);
}
if (businessOntologyV2Selection.selection_digest !== selectionDigest(businessOntologyV2Selection) || businessOntologyV2Selection.selection_digest !== "1d544c406395935a34983dd202234048c0fbaa0b41d8f93c1cb3c3047c2712e5") {
  fail("DECISION_SELECTION_DIGEST", businessOntologyV2Selection.selection_id);
}

const admittedSelections = new Map([definitionSelection, capabilitySelection, businessOntologySelection].map((selection) => [selection.decision_id, selection]));
const sourceCandidate = candidates.get("DSV2-DEC-SFOL-DOMAINSPEC-SOURCE-001")?.candidate;
if (!sourceCandidate) fail("DECISION_SOURCE_CANDIDATE_MISSING", "DSV2-DEC-SFOL-DOMAINSPEC-SOURCE-001");
for (const prerequisite of sourceCandidate.prerequisite_decisions) {
  const selection = admittedSelections.get(prerequisite.decision_id);
  if (!selection || selection.selected_option !== prerequisite.required_option) {
    fail("DECISION_SOURCE_PREREQUISITE_UNSELECTED", prerequisite.decision_id);
  }
}
const sourceManifest = JSON.parse(readFileSync(resolveCapabilityPath("generated/source-manifest.json"), "utf8"));
const buildReceipt = JSON.parse(readFileSync(resolveCapabilityPath("generated/build-receipt.json"), "utf8"));
const compiledGraph = JSON.parse(readFileSync(resolveCapabilityPath("generated/compiled-graph.json"), "utf8"));
const sourceProject = JSON.parse(readFileSync(resolveCapabilityPath("domainspec/project.json"), "utf8"));
const sourceRecords = sourceManifest.inputs.map((record: { path: string; digest: string }) => {
  if (sha256File(resolveDomainspecPath(record.path)) !== record.digest) fail("DECISION_SOURCE_INPUT_DRIFT", record.path);
  return { path: record.path, digest: record.digest };
}).sort((left: { path: string }, right: { path: string }) => left.path.localeCompare(right.path));
const recomputedSourceSetDigest = sha256(`${canonicalize(sourceRecords)}\n`);
if (
  sourceManifest.project_id !== "sfol-test-closure" ||
  sourceManifest.source_set_digest !== "cce24ec830000f7fc805d4de270f6be7998fc1cf38faf3f369980abb61217594" ||
  recomputedSourceSetDigest !== sourceManifest.source_set_digest ||
  sourceProject.language?.profile?.digest !== sha256File(resolveCapabilityPath("domainspec/development-profile.json")) ||
  compiledGraph.source_set_digest !== sourceManifest.source_set_digest ||
  buildReceipt.source_set_digest !== sourceManifest.source_set_digest ||
  buildReceipt.source_manifest_sha256 !== sha256File(resolveCapabilityPath("generated/source-manifest.json")) ||
  buildReceipt.compiled_graph_sha256 !== sha256File(resolveCapabilityPath("generated/compiled-graph.json")) ||
  buildReceipt.development_profile_sha256 !== sha256File(resolveCapabilityPath("domainspec/development-profile.json")) ||
  buildReceipt.compile_runs !== 2 || buildReceipt.byte_identical !== true || buildReceipt.authority_effect !== "none"
) {
  fail("DECISION_SOURCE_PROVENANCE_CLOSURE", sourceCandidate.decision_id);
}

process.stdout.write(`${JSON.stringify({
  result: "pass",
  authority_effect: "none",
  schema_digest: sha256File(schemaPath),
  selection_schema_digest: sha256File(selectionSchemaPath),
  decision_candidates: candidateNames.map((name) => {
    const candidate = JSON.parse(readFileSync(resolve(decisionsRoot, name), "utf8")) as Candidate;
    return { decision_id: candidate.decision_id, candidate_digest: candidate.candidate_digest };
  }),
  selections: [definitionSelection, capabilitySelection, businessOntologySelection, capabilityV2Selection, businessOntologyV2Selection].map((selection) => ({
    selection_id: selection.selection_id,
    decision_id: selection.decision_id,
    selected_option: selection.selected_option,
    selection_digest: selection.selection_digest,
    authority_effect: selection.authority_effect
  }))
}, null, 2)}\n`);
