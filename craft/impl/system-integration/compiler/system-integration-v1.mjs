import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const SYSTEM_PROFILE_ID = "domainspec.system-integration-profile/provider-neutral-v1";
export const LANGUAGES = Object.freeze(["typescript", "python", "rust"]);
export const PACKAGE_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const REPOSITORY_ROOT = path.resolve(PACKAGE_ROOT, "../../../..");

const PROFILE_PATH = "profiles/provider-neutral-v1/profile.json";
const LANGUAGE_PATHS = Object.freeze({
  typescript: "profiles/provider-neutral-v1/typescript.json",
  python: "profiles/provider-neutral-v1/python.json",
  rust: "profiles/provider-neutral-v1/rust.json",
});
const REF_PATTERN = /^[a-z][a-z0-9]*(?:[-.:/][a-z0-9]+)*$/;
const SUBJECT_PATTERN = /^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$/;

export class SystemIntegrationError extends Error {
  constructor(code, pointer, message) {
    super(message);
    this.name = "SystemIntegrationError";
    this.code = code;
    this.pointer = pointer;
    this.exitCode = 22;
  }
}

function fail(code, pointer, message) {
  throw new SystemIntegrationError(code, pointer, message);
}

export function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value !== null && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

export function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function readJson(root, relativePath) {
  const absolute = path.resolve(root, relativePath);
  const relative = path.relative(root, absolute);
  if (relative.startsWith("..") || path.isAbsolute(relative)) fail("SIC_SCHEMA", `/${relativePath}`, "path escapes package root");
  return JSON.parse(fs.readFileSync(absolute, "utf8"));
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function exactKeys(value, expected, pointer) {
  if (!isObject(value)) fail("SIC_SCHEMA", pointer, "expected object");
  if (canonicalJson(Object.keys(value).sort()) !== canonicalJson([...expected].sort())) fail("SIC_SCHEMA", pointer, "unexpected or missing member");
}

function string(value, pointer) {
  if (typeof value !== "string" || value.length === 0) fail("SIC_SCHEMA", pointer, "expected nonempty string");
  return value;
}

function ref(value, pointer) {
  const result = string(value, pointer);
  if (!REF_PATTERN.test(result)) fail("SIC_SCHEMA", pointer, "invalid integration reference");
  return result;
}

function strings(value, pointer, minimum = 1) {
  if (!Array.isArray(value) || value.length < minimum) fail("SIC_SCHEMA", pointer, `expected at least ${minimum} string values`);
  const result = value.map((entry, index) => string(entry, `${pointer}/${index}`));
  if (new Set(result).size !== result.length) fail("SIC_SCHEMA", pointer, "duplicate array member");
  return Object.freeze([...result].sort());
}

function refs(value, pointer, minimum = 1) {
  if (!Array.isArray(value) || value.length < minimum) fail("SIC_SCHEMA", pointer, `expected at least ${minimum} references`);
  const result = value.map((entry, index) => ref(entry, `${pointer}/${index}`));
  if (new Set(result).size !== result.length) fail("SIC_SCHEMA", pointer, "duplicate reference");
  return Object.freeze([...result].sort());
}

function records(value, pointer) {
  if (!Array.isArray(value)) fail("SIC_SCHEMA", pointer, "expected record array");
  return value;
}

function sortedRecords(value, identity) {
  return Object.freeze([...value].sort((left, right) => left[identity].localeCompare(right[identity])));
}

function ensureUnique(recordsValue, identity, pointer) {
  const ids = new Set();
  for (const [index, record] of recordsValue.entries()) {
    const id = ref(record[identity], `${pointer}/${index}/${identity}`);
    if (ids.has(id)) fail("SIC_SCHEMA", `${pointer}/${index}/${identity}`, `duplicate identity:${id}`);
    ids.add(id);
  }
  return ids;
}

export function loadProfilePackage(packageRoot = PACKAGE_ROOT) {
  const profile = readJson(packageRoot, PROFILE_PATH);
  exactKeys(profile, ["schema_version", "profile_id", "status", "implementation_state", "architecture", "owner_admission", "definition_ids", "contract_kinds", "language_profile_refs", "invariants", "claim_ceiling", "authority_effect"], "/profile");
  if (profile.schema_version !== "domainspec.system-integration-profile/v1" || profile.profile_id !== SYSTEM_PROFILE_ID || profile.status !== "canonical-target" || profile.authority_effect !== "none") fail("SIC_PROFILE_UNRESOLVED", "/profile", "unsupported system-integration profile");
  if (canonicalJson(profile.definition_ids) !== canonicalJson(["domainspec-v2-D45", "domainspec-v2-D46", "domainspec-v2-D47", "domainspec-v2-D48", "domainspec-v2-D49"])) fail("SIC_PROFILE_UNRESOLVED", "/profile/definition_ids", "D45-D49 denominator drift");
  if (profile.contract_kinds.length !== 5 || profile.language_profile_refs.length !== 3) fail("SIC_PROFILE_UNRESOLVED", "/profile", "profile denominator drift");
  for (const invariant of ["no-universal-port", "domain-interface-reference-only-for-ds-d1-interface", "repository-contract-distinct-from-persistence-binding", "unit-of-work-distinct-from-transaction-guarantee-binding", "failure-classification-does-not-select-retry", "durable-runtime-binding-only-for-durable-workflow-profile", "provider-runtime-guarantees-require-separate-observation"]) {
    if (!profile.invariants.includes(invariant)) fail("SIC_PROFILE_UNRESOLVED", "/profile/invariants", `missing invariant:${invariant}`);
  }
  if (profile.claim_ceiling.provider_selected_by_domainspec !== false || profile.claim_ceiling.runtime_guarantees_observed !== false || profile.claim_ceiling.durable_dispatch !== false) fail("SIC_PROFILE_UNRESOLVED", "/profile/claim_ceiling", "provider-neutral claim ceiling inflated");
  for (const source of [profile.architecture, profile.owner_admission]) {
    const absolute = path.resolve(REPOSITORY_ROOT, source.path);
    if (sha256(fs.readFileSync(absolute)) !== source.sha256) fail("SIC_PROFILE_UNRESOLVED", `/profile/${source.path}`, "source digest drift");
  }
  const languageProfiles = Object.fromEntries(LANGUAGES.map((language) => {
    const value = readJson(packageRoot, LANGUAGE_PATHS[language]);
    exactKeys(value, ["schema_version", "language_profile_id", "system_profile_ref", "language", "status", "implementation_state", "record_form", "dependency_contract_form", "composition_boundary", "domain_interface_mapping", "generated_extension", "forbidden_abstractions", "semantic_obligations", "authority_effect"], `/languages/${language}`);
    if (value.schema_version !== "domainspec.system-integration-language-profile/v1" || value.system_profile_ref !== SYSTEM_PROFILE_ID || value.language !== language || value.status !== "canonical-target" || value.authority_effect !== "none") fail("SIC_PROFILE_UNRESOLVED", `/languages/${language}`, "language profile mismatch");
    if (canonicalJson(value.semantic_obligations) !== canonicalJson(profile.definition_ids)) fail("SIC_PROFILE_UNRESOLVED", `/languages/${language}/semantic_obligations`, "language obligation drift");
    if (!value.forbidden_abstractions.includes("universal-Port") || !value.forbidden_abstractions.includes("implicit-Retry-selection")) fail("SIC_PROFILE_UNRESOLVED", `/languages/${language}/forbidden_abstractions`, "language profile weakened");
    return [language, Object.freeze({ value: Object.freeze(value), digest: sha256(canonicalJson(value)), path: LANGUAGE_PATHS[language] })];
  }));
  return Object.freeze({ profile: Object.freeze(profile), profile_digest: sha256(canonicalJson(profile)), profile_path: PROFILE_PATH, language_profiles: Object.freeze(languageProfiles) });
}

export function validateBindingSet(value) {
  if (isObject(value) && Object.keys(value).some((key) => key.endsWith("digest"))) fail("SIC_AUTHORED_DIGEST_FORBIDDEN", "$bindingSet", "portable binding set cannot author digests");
  exactKeys(value, ["schema_version", "binding_set_id", "profile_id", "subject_ref", "dependency_contracts", "persistence_bindings", "transaction_guarantee_bindings", "failure_outcome_bindings", "durable_workflow_runtime_bindings", "authority_effect"], "$bindingSet");
  if (value.schema_version !== "domainspec.system-integration-binding-set/v1" || value.profile_id !== SYSTEM_PROFILE_ID || value.authority_effect !== "none") fail("SIC_SCHEMA", "$bindingSet", "binding-set envelope mismatch");
  const bindingSetId = ref(value.binding_set_id, "/binding_set_id");
  const subjectRef = string(value.subject_ref, "/subject_ref");
  if (!SUBJECT_PATTERN.test(subjectRef)) fail("SIC_SCHEMA", "/subject_ref", "subject must be feature-id:node-id");

  const dependencyContracts = records(value.dependency_contracts, "/dependency_contracts").map((record, index) => {
    const pointer = `/dependency_contracts/${index}`;
    exactKeys(record, ["contract_id", "concern", "consumer_roles", "operation_signatures", "failure_surface", "implementation_profile_ref", "domain_interface_ref"], pointer);
    const contractId = ref(record.contract_id, `${pointer}/contract_id`);
    const concern = string(record.concern, `${pointer}/concern`);
    if (/^port$/i.test(concern) || /(?:^|[-_.])port$/i.test(contractId)) fail("SIC_UNIVERSAL_PORT_FORBIDDEN", pointer, "dependency contract must name one concern, not Port");
    if (record.implementation_profile_ref !== SYSTEM_PROFILE_ID) fail("SIC_PROFILE_UNRESOLVED", `${pointer}/implementation_profile_ref`, "dependency contract profile mismatch");
    if (record.domain_interface_ref !== null && (typeof record.domain_interface_ref !== "string" || !/^DS-D1\.11:[a-z][a-z0-9-]*$/.test(record.domain_interface_ref))) fail("SIC_DOMAIN_INTERFACE_MISUSE", `${pointer}/domain_interface_ref`, "domain Interface ref must be explicit DS-D1.11 or null");
    return Object.freeze({ contract_id: contractId, concern, consumer_roles: strings(record.consumer_roles, `${pointer}/consumer_roles`), operation_signatures: strings(record.operation_signatures, `${pointer}/operation_signatures`), failure_surface: strings(record.failure_surface, `${pointer}/failure_surface`), implementation_profile_ref: SYSTEM_PROFILE_ID, domain_interface_ref: record.domain_interface_ref });
  });

  const persistenceBindings = records(value.persistence_bindings, "/persistence_bindings").map((record, index) => {
    const pointer = `/persistence_bindings/${index}`;
    exactKeys(record, ["binding_id", "logical_subject_refs", "dependency_contract_ref", "adapter_ref", "resource_ref", "implementation_profile_ref", "logical_physical_mapping_ref", "evidence_boundary"], pointer);
    if (record.implementation_profile_ref !== SYSTEM_PROFILE_ID) fail("SIC_PROFILE_UNRESOLVED", `${pointer}/implementation_profile_ref`, "persistence binding profile mismatch");
    return Object.freeze({ binding_id: ref(record.binding_id, `${pointer}/binding_id`), logical_subject_refs: refs(record.logical_subject_refs, `${pointer}/logical_subject_refs`), dependency_contract_ref: ref(record.dependency_contract_ref, `${pointer}/dependency_contract_ref`), adapter_ref: ref(record.adapter_ref, `${pointer}/adapter_ref`), resource_ref: ref(record.resource_ref, `${pointer}/resource_ref`), implementation_profile_ref: SYSTEM_PROFILE_ID, logical_physical_mapping_ref: ref(record.logical_physical_mapping_ref, `${pointer}/logical_physical_mapping_ref`), evidence_boundary: string(record.evidence_boundary, `${pointer}/evidence_boundary`) });
  });

  const failureOutcomeBindings = records(value.failure_outcome_bindings, "/failure_outcome_bindings").map((record, index) => {
    const pointer = `/failure_outcome_bindings/${index}`;
    if (isObject(record) && ["retry_selection", "continuation", "failure_continuation"].some((key) => key in record)) fail("SIC_FAILURE_CONTINUATION_FORBIDDEN", pointer, "failure classification cannot select a continuation");
    exactKeys(record, ["binding_id", "concern_ref", "provider_outcome_ref", "outcome_class", "evidence_refs", "continuation_owner_ref"], pointer);
    if (!["retryable", "non-retryable", "unknown"].includes(record.outcome_class)) fail("SIC_SCHEMA", `${pointer}/outcome_class`, "invalid failure outcome class");
    return Object.freeze({ binding_id: ref(record.binding_id, `${pointer}/binding_id`), concern_ref: ref(record.concern_ref, `${pointer}/concern_ref`), provider_outcome_ref: ref(record.provider_outcome_ref, `${pointer}/provider_outcome_ref`), outcome_class: record.outcome_class, evidence_refs: refs(record.evidence_refs, `${pointer}/evidence_refs`), continuation_owner_ref: ref(record.continuation_owner_ref, `${pointer}/continuation_owner_ref`) });
  });

  const transactionGuaranteeBindings = records(value.transaction_guarantee_bindings, "/transaction_guarantee_bindings").map((record, index) => {
    const pointer = `/transaction_guarantee_bindings/${index}`;
    exactKeys(record, ["binding_id", "unit_of_work_contract_ref", "participant_refs", "atomicity_scope", "selected_guarantees", "implementation_profile_ref", "failure_outcome_binding_ref", "evidence_boundary"], pointer);
    if (record.implementation_profile_ref !== SYSTEM_PROFILE_ID) fail("SIC_PROFILE_UNRESOLVED", `${pointer}/implementation_profile_ref`, "transaction binding profile mismatch");
    const guarantees = strings(record.selected_guarantees, `${pointer}/selected_guarantees`);
    for (const guarantee of guarantees) if (!["atomicity", "isolation", "durability", "conflict-detection", "rollback-restoration"].includes(guarantee)) fail("SIC_SCHEMA", `${pointer}/selected_guarantees`, `unknown guarantee:${guarantee}`);
    return Object.freeze({ binding_id: ref(record.binding_id, `${pointer}/binding_id`), unit_of_work_contract_ref: ref(record.unit_of_work_contract_ref, `${pointer}/unit_of_work_contract_ref`), participant_refs: refs(record.participant_refs, `${pointer}/participant_refs`, 2), atomicity_scope: string(record.atomicity_scope, `${pointer}/atomicity_scope`), selected_guarantees: guarantees, implementation_profile_ref: SYSTEM_PROFILE_ID, failure_outcome_binding_ref: ref(record.failure_outcome_binding_ref, `${pointer}/failure_outcome_binding_ref`), evidence_boundary: string(record.evidence_boundary, `${pointer}/evidence_boundary`) });
  });

  const durableWorkflowRuntimeBindings = records(value.durable_workflow_runtime_bindings, "/durable_workflow_runtime_bindings").map((record, index) => {
    const pointer = `/durable_workflow_runtime_bindings/${index}`;
    exactKeys(record, ["binding_id", "workflow_profile_ref", "persistence_binding_refs", "transaction_guarantee_binding_refs", "failure_outcome_binding_refs", "scheduler_contract_ref", "clock_contract_ref", "wakeup_contract_ref", "replay_contract_ref", "version_compatibility_ref", "evidence_boundary"], pointer);
    if (record.wakeup_contract_ref !== null) ref(record.wakeup_contract_ref, `${pointer}/wakeup_contract_ref`);
    return Object.freeze({ binding_id: ref(record.binding_id, `${pointer}/binding_id`), workflow_profile_ref: ref(record.workflow_profile_ref, `${pointer}/workflow_profile_ref`), persistence_binding_refs: refs(record.persistence_binding_refs, `${pointer}/persistence_binding_refs`), transaction_guarantee_binding_refs: refs(record.transaction_guarantee_binding_refs, `${pointer}/transaction_guarantee_binding_refs`), failure_outcome_binding_refs: refs(record.failure_outcome_binding_refs, `${pointer}/failure_outcome_binding_refs`), scheduler_contract_ref: ref(record.scheduler_contract_ref, `${pointer}/scheduler_contract_ref`), clock_contract_ref: ref(record.clock_contract_ref, `${pointer}/clock_contract_ref`), wakeup_contract_ref: record.wakeup_contract_ref, replay_contract_ref: ref(record.replay_contract_ref, `${pointer}/replay_contract_ref`), version_compatibility_ref: ref(record.version_compatibility_ref, `${pointer}/version_compatibility_ref`), evidence_boundary: string(record.evidence_boundary, `${pointer}/evidence_boundary`) });
  });

  const dependencyIds = ensureUnique(dependencyContracts, "contract_id", "/dependency_contracts");
  const persistenceIds = ensureUnique(persistenceBindings, "binding_id", "/persistence_bindings");
  const failureIds = ensureUnique(failureOutcomeBindings, "binding_id", "/failure_outcome_bindings");
  const transactionIds = ensureUnique(transactionGuaranteeBindings, "binding_id", "/transaction_guarantee_bindings");
  ensureUnique(durableWorkflowRuntimeBindings, "binding_id", "/durable_workflow_runtime_bindings");
  for (const binding of persistenceBindings) if (!dependencyIds.has(binding.dependency_contract_ref)) fail("SIC_REFERENCE_UNRESOLVED", `/persistence_bindings/${binding.binding_id}/dependency_contract_ref`, "persistence dependency contract is unresolved");
  for (const binding of failureOutcomeBindings) if (!dependencyIds.has(binding.concern_ref)) fail("SIC_REFERENCE_UNRESOLVED", `/failure_outcome_bindings/${binding.binding_id}/concern_ref`, "failure concern is unresolved");
  for (const binding of transactionGuaranteeBindings) {
    if (!dependencyIds.has(binding.unit_of_work_contract_ref)) fail("SIC_REFERENCE_UNRESOLVED", `/transaction_guarantee_bindings/${binding.binding_id}/unit_of_work_contract_ref`, "Unit of Work contract is unresolved");
    if (!failureIds.has(binding.failure_outcome_binding_ref)) fail("SIC_REFERENCE_UNRESOLVED", `/transaction_guarantee_bindings/${binding.binding_id}/failure_outcome_binding_ref`, "failure binding is unresolved");
  }
  for (const binding of durableWorkflowRuntimeBindings) {
    for (const id of binding.persistence_binding_refs) if (!persistenceIds.has(id)) fail("SIC_DURABLE_BINDING_INCOMPLETE", `/durable_workflow_runtime_bindings/${binding.binding_id}`, `persistence binding unresolved:${id}`);
    for (const id of binding.transaction_guarantee_binding_refs) if (!transactionIds.has(id)) fail("SIC_DURABLE_BINDING_INCOMPLETE", `/durable_workflow_runtime_bindings/${binding.binding_id}`, `transaction binding unresolved:${id}`);
    for (const id of binding.failure_outcome_binding_refs) if (!failureIds.has(id)) fail("SIC_DURABLE_BINDING_INCOMPLETE", `/durable_workflow_runtime_bindings/${binding.binding_id}`, `failure binding unresolved:${id}`);
    for (const [field, id] of [["scheduler_contract_ref", binding.scheduler_contract_ref], ["clock_contract_ref", binding.clock_contract_ref], ["replay_contract_ref", binding.replay_contract_ref]]) if (!dependencyIds.has(id)) fail("SIC_DURABLE_BINDING_INCOMPLETE", `/durable_workflow_runtime_bindings/${binding.binding_id}/${field}`, `dependency contract unresolved:${id}`);
    if (binding.wakeup_contract_ref !== null && !dependencyIds.has(binding.wakeup_contract_ref)) fail("SIC_DURABLE_BINDING_INCOMPLETE", `/durable_workflow_runtime_bindings/${binding.binding_id}/wakeup_contract_ref`, "wakeup contract unresolved");
  }

  return Object.freeze({ schema_version: "domainspec.system-integration-binding-set/v1", binding_set_id: bindingSetId, profile_id: SYSTEM_PROFILE_ID, subject_ref: subjectRef, dependency_contracts: sortedRecords(dependencyContracts, "contract_id"), persistence_bindings: sortedRecords(persistenceBindings, "binding_id"), transaction_guarantee_bindings: sortedRecords(transactionGuaranteeBindings, "binding_id"), failure_outcome_bindings: sortedRecords(failureOutcomeBindings, "binding_id"), durable_workflow_runtime_bindings: sortedRecords(durableWorkflowRuntimeBindings, "binding_id"), authority_effect: "none" });
}

export function compileBindingManifest(value, language, profilePackage = loadProfilePackage()) {
  if (!LANGUAGES.includes(language)) fail("SIC_PROFILE_UNRESOLVED", "/language", `unsupported language:${language}`);
  const canonicalBindings = validateBindingSet(value);
  const languageProfile = profilePackage.language_profiles[language];
  const body = Object.freeze({ schema_version: "domainspec.system-integration-binding-manifest/v1", binding_set_id: canonicalBindings.binding_set_id, subject_ref: canonicalBindings.subject_ref, profile: Object.freeze({ profile_id: SYSTEM_PROFILE_ID, profile_digest: profilePackage.profile_digest, language_profile_id: languageProfile.value.language_profile_id, language_profile_digest: languageProfile.digest, architecture_id: profilePackage.profile.architecture.architecture_id, architecture_sha256: profilePackage.profile.architecture.sha256 }), language, source_digest: sha256(canonicalJson(value)), canonical_bindings: canonicalBindings, runtime_guarantees_observed: false, authority_effect: "none" });
  return Object.freeze({ ...body, binding_digest: sha256(canonicalJson(body)) });
}

function words(value) {
  return value.split(/[^A-Za-z0-9]+/).filter(Boolean);
}

function pascal(value) {
  const result = words(value).map((word) => `${word[0].toUpperCase()}${word.slice(1)}`).join("") || "Dependency";
  return /^[A-Za-z_]/.test(result) ? result : `Dependency${result}`;
}

function snake(value) {
  const result = words(value).map((word) => word.toLowerCase()).join("_") || "dependency";
  return /^[A-Za-z_]/.test(result) ? result : `dependency_${result}`;
}

export function generatedRelativePath(bindingSetId, language, profilePackage = loadProfilePackage()) {
  ref(bindingSetId, "/binding_set_id");
  if (!LANGUAGES.includes(language)) fail("SIC_PROFILE_UNRESOLVED", "/language", `unsupported language:${language}`);
  return `src/domainspec/system-integration/${language}/${bindingSetId}.${profilePackage.language_profiles[language].value.generated_extension}`;
}

export function renderLanguageContract(manifest) {
  const language = manifest.language;
  if (!LANGUAGES.includes(language)) fail("SIC_PROFILE_UNRESOLVED", "/manifest/language", "unsupported manifest language");
  const json = canonicalJson(manifest);
  const contracts = manifest.canonical_bindings.dependency_contracts;
  let content;
  if (language === "typescript") {
    const declarations = contracts.map((contract) => `export type ${pascal(contract.concern)}Contract = Readonly<{ readonly concern: ${JSON.stringify(contract.concern)}; readonly operations: readonly string[]; readonly failures: readonly string[] }>;`).join("\n");
    content = `// generated by DomainSpec system-integration provider-neutral-v1\n// domainspec-system-integration-binding-digest: ${manifest.binding_digest}\n${declarations}\nexport const domainSpecSystemIntegrationManifestJson = ${JSON.stringify(json)} as const;\nexport const domainSpecSystemIntegrationRuntimeGuaranteesObserved = false as const;\n`;
  } else if (language === "python") {
    const declarations = contracts.map((contract) => `class ${pascal(contract.concern)}Contract(Protocol):\n    concern: Literal[${JSON.stringify(contract.concern)}]\n    operations: tuple[str, ...]\n    failures: tuple[str, ...]\n`).join("\n");
    content = `# generated by DomainSpec system-integration provider-neutral-v1\n# domainspec-system-integration-binding-digest: ${manifest.binding_digest}\nfrom typing import Final, Literal, Protocol\n\n${declarations}\nDOMAIN_SPEC_SYSTEM_INTEGRATION_MANIFEST_JSON: Final[str] = ${JSON.stringify(json)}\nDOMAIN_SPEC_SYSTEM_INTEGRATION_RUNTIME_GUARANTEES_OBSERVED: Final[bool] = False\n`;
  } else {
    const declarations = contracts.map((contract) => `pub trait ${pascal(contract.concern)}Contract { fn concern(&self) -> &'static str { ${JSON.stringify(contract.concern)} } fn operations(&self) -> &'static [&'static str]; fn failures(&self) -> &'static [&'static str]; }`).join("\n");
    content = `// generated by DomainSpec system-integration provider-neutral-v1\n// domainspec-system-integration-binding-digest: ${manifest.binding_digest}\n${declarations}\npub const DOMAIN_SPEC_SYSTEM_INTEGRATION_MANIFEST_JSON: &str = ${JSON.stringify(json)};\npub const DOMAIN_SPEC_SYSTEM_INTEGRATION_RUNTIME_GUARANTEES_OBSERVED: bool = false;\n`;
  }
  if (/\bPort\b/.test(content)) fail("SIC_UNIVERSAL_PORT_FORBIDDEN", "/generated", "generated source contains universal Port abstraction");
  return content;
}

export function verifyLanguageContract(content, manifest) {
  if (typeof content !== "string" || !content.includes(`domainspec-system-integration-binding-digest: ${manifest.binding_digest}`) || !content.includes(JSON.stringify(canonicalJson(manifest)))) fail("SIC_GENERATED_PROFILE_DRIFT", "/generated", "generated source does not bind the selected manifest");
  if (/\bPort\b/.test(content)) fail("SIC_UNIVERSAL_PORT_FORBIDDEN", "/generated", "generated source contains universal Port abstraction");
  if (content.includes("runtime_guarantees_observed = true") || content.includes("RUNTIME_GUARANTEES_OBSERVED: bool = true")) fail("SIC_GENERATED_PROFILE_DRIFT", "/generated", "generated source inflates runtime guarantees");
  return true;
}

export function readBindingSetFile(filePath) {
  const stats = fs.lstatSync(filePath);
  if (stats.isSymbolicLink() || !stats.isFile()) fail("SIC_SCHEMA", "/binding-set", "binding-set path must be a regular file");
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}
