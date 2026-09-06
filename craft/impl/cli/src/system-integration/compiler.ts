import fs from "node:fs";
import path from "node:path";

import type { SupportedLanguage } from "../meta-types/types.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { FROZEN_SYSTEM_INTEGRATION, languageProfile } from "./profile.js";
import type { SystemIntegrationBindingManifestV1, SystemIntegrationSelectionV1 } from "./types.js";

const PROFILE_ID = "domainspec.system-integration-profile/provider-neutral-v1" as const;
const ID = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const REF = /^[a-z][a-z0-9]*(?:[-.:/][a-z0-9]+)*$/;
const SUBJECT = /^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$/;

type UnknownRecord = Record<string, unknown>;

export class SystemIntegrationError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "SystemIntegrationError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new SystemIntegrationError(code, pointer, message);
}

function isObject(value: unknown): value is UnknownRecord {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function exactKeys(value: unknown, expected: readonly string[], pointer: string): asserts value is UnknownRecord {
  if (!isObject(value)) fail("SIC_SCHEMA", pointer, "expected object");
  if (canonicalJson(Object.keys(value).sort()) !== canonicalJson([...expected].sort())) fail("SIC_SCHEMA", pointer, "unexpected or missing member");
}

function requiredString(value: unknown, pointer: string): string {
  if (typeof value !== "string" || value.length === 0) fail("SIC_SCHEMA", pointer, "expected nonempty string");
  return value;
}

function reference(value: unknown, pointer: string): string {
  const result = requiredString(value, pointer);
  if (!REF.test(result)) fail("SIC_SCHEMA", pointer, "invalid integration reference");
  return result;
}

function stringSet(value: unknown, pointer: string, minimum = 1, references = false): readonly string[] {
  if (!Array.isArray(value) || value.length < minimum) fail("SIC_SCHEMA", pointer, `expected at least ${minimum} values`);
  const rows = value.map((entry, index) => references ? reference(entry, `${pointer}/${index}`) : requiredString(entry, `${pointer}/${index}`));
  if (new Set(rows).size !== rows.length) fail("SIC_SCHEMA", pointer, "duplicate array member");
  return Object.freeze([...rows].sort());
}

function recordArray(value: unknown, pointer: string): UnknownRecord[] {
  if (!Array.isArray(value) || value.some((entry) => !isObject(entry))) fail("SIC_SCHEMA", pointer, "expected record array");
  return value as UnknownRecord[];
}

function sortRecords<T extends UnknownRecord>(records: readonly T[], identity: string): readonly T[] {
  return Object.freeze([...records].sort((left, right) => String(left[identity]).localeCompare(String(right[identity]))));
}

function identities(records: readonly UnknownRecord[], field: string, pointer: string): Set<string> {
  const result = new Set<string>();
  records.forEach((record, index) => {
    const id = reference(record[field], `${pointer}/${index}/${field}`);
    if (result.has(id)) fail("SIC_SCHEMA", `${pointer}/${index}/${field}`, `duplicate identity:${id}`);
    result.add(id);
  });
  return result;
}

export function validateSystemIntegrationBindingSet(value: unknown): Readonly<Record<string, unknown>> {
  if (isObject(value) && Object.keys(value).some((key) => key.endsWith("digest"))) fail("SIC_AUTHORED_DIGEST_FORBIDDEN", "$bindingSet", "portable input cannot author compiler digests");
  exactKeys(value, ["schema_version", "binding_set_id", "profile_id", "subject_ref", "dependency_contracts", "persistence_bindings", "transaction_guarantee_bindings", "failure_outcome_bindings", "durable_workflow_runtime_bindings", "authority_effect"], "$bindingSet");
  if (value.schema_version !== "domainspec.system-integration-binding-set/v1" || value.profile_id !== PROFILE_ID || value.authority_effect !== "none") fail("SIC_SCHEMA", "$bindingSet", "binding-set envelope mismatch");
  const bindingSetId = reference(value.binding_set_id, "/binding_set_id");
  if (!ID.test(bindingSetId)) fail("SIC_SCHEMA", "/binding_set_id", "binding-set id must be a canonical identifier");
  const subjectRef = requiredString(value.subject_ref, "/subject_ref");
  if (!SUBJECT.test(subjectRef)) fail("SIC_SCHEMA", "/subject_ref", "subject must be feature-id:node-id");

  const dependencyContracts = recordArray(value.dependency_contracts, "/dependency_contracts").map((record, index) => {
    const pointer = `/dependency_contracts/${index}`;
    exactKeys(record, ["contract_id", "concern", "consumer_roles", "operation_signatures", "failure_surface", "implementation_profile_ref", "domain_interface_ref"], pointer);
    const contractId = reference(record.contract_id, `${pointer}/contract_id`);
    const concern = requiredString(record.concern, `${pointer}/concern`);
    if (/^port$/i.test(concern) || /(?:^|[-_.])port$/i.test(contractId)) fail("SIC_UNIVERSAL_PORT_FORBIDDEN", pointer, "dependency contract must name one concern");
    if (record.implementation_profile_ref !== PROFILE_ID) fail("SIC_PROFILE_UNRESOLVED", `${pointer}/implementation_profile_ref`, "dependency profile mismatch");
    if (record.domain_interface_ref !== null && (typeof record.domain_interface_ref !== "string" || !/^DS-D1\.11:[a-z][a-z0-9-]*$/.test(record.domain_interface_ref))) fail("SIC_DOMAIN_INTERFACE_MISUSE", `${pointer}/domain_interface_ref`, "domain Interface ref must be explicit DS-D1.11 or null");
    return Object.freeze({ contract_id: contractId, concern, consumer_roles: stringSet(record.consumer_roles, `${pointer}/consumer_roles`), operation_signatures: stringSet(record.operation_signatures, `${pointer}/operation_signatures`), failure_surface: stringSet(record.failure_surface, `${pointer}/failure_surface`), implementation_profile_ref: PROFILE_ID, domain_interface_ref: record.domain_interface_ref });
  });

  const persistenceBindings = recordArray(value.persistence_bindings, "/persistence_bindings").map((record, index) => {
    const pointer = `/persistence_bindings/${index}`;
    exactKeys(record, ["binding_id", "logical_subject_refs", "dependency_contract_ref", "adapter_ref", "resource_ref", "implementation_profile_ref", "logical_physical_mapping_ref", "evidence_boundary"], pointer);
    if (record.implementation_profile_ref !== PROFILE_ID) fail("SIC_PROFILE_UNRESOLVED", `${pointer}/implementation_profile_ref`, "persistence profile mismatch");
    return Object.freeze({ binding_id: reference(record.binding_id, `${pointer}/binding_id`), logical_subject_refs: stringSet(record.logical_subject_refs, `${pointer}/logical_subject_refs`, 1, true), dependency_contract_ref: reference(record.dependency_contract_ref, `${pointer}/dependency_contract_ref`), adapter_ref: reference(record.adapter_ref, `${pointer}/adapter_ref`), resource_ref: reference(record.resource_ref, `${pointer}/resource_ref`), implementation_profile_ref: PROFILE_ID, logical_physical_mapping_ref: reference(record.logical_physical_mapping_ref, `${pointer}/logical_physical_mapping_ref`), evidence_boundary: requiredString(record.evidence_boundary, `${pointer}/evidence_boundary`) });
  });

  const failureOutcomeBindings = recordArray(value.failure_outcome_bindings, "/failure_outcome_bindings").map((record, index) => {
    const pointer = `/failure_outcome_bindings/${index}`;
    if (["retry_selection", "continuation", "failure_continuation"].some((key) => key in record)) fail("SIC_FAILURE_CONTINUATION_FORBIDDEN", pointer, "failure classification cannot select continuation");
    exactKeys(record, ["binding_id", "concern_ref", "provider_outcome_ref", "outcome_class", "evidence_refs", "continuation_owner_ref"], pointer);
    if (!["retryable", "non-retryable", "unknown"].includes(String(record.outcome_class))) fail("SIC_SCHEMA", `${pointer}/outcome_class`, "invalid failure outcome class");
    return Object.freeze({ binding_id: reference(record.binding_id, `${pointer}/binding_id`), concern_ref: reference(record.concern_ref, `${pointer}/concern_ref`), provider_outcome_ref: reference(record.provider_outcome_ref, `${pointer}/provider_outcome_ref`), outcome_class: record.outcome_class, evidence_refs: stringSet(record.evidence_refs, `${pointer}/evidence_refs`, 1, true), continuation_owner_ref: reference(record.continuation_owner_ref, `${pointer}/continuation_owner_ref`) });
  });

  const transactionGuaranteeBindings = recordArray(value.transaction_guarantee_bindings, "/transaction_guarantee_bindings").map((record, index) => {
    const pointer = `/transaction_guarantee_bindings/${index}`;
    exactKeys(record, ["binding_id", "unit_of_work_contract_ref", "participant_refs", "atomicity_scope", "selected_guarantees", "implementation_profile_ref", "failure_outcome_binding_ref", "evidence_boundary"], pointer);
    if (record.implementation_profile_ref !== PROFILE_ID) fail("SIC_PROFILE_UNRESOLVED", `${pointer}/implementation_profile_ref`, "transaction profile mismatch");
    const guarantees = stringSet(record.selected_guarantees, `${pointer}/selected_guarantees`);
    for (const guarantee of guarantees) if (!["atomicity", "isolation", "durability", "conflict-detection", "rollback-restoration"].includes(guarantee)) fail("SIC_SCHEMA", `${pointer}/selected_guarantees`, `unknown guarantee:${guarantee}`);
    return Object.freeze({ binding_id: reference(record.binding_id, `${pointer}/binding_id`), unit_of_work_contract_ref: reference(record.unit_of_work_contract_ref, `${pointer}/unit_of_work_contract_ref`), participant_refs: stringSet(record.participant_refs, `${pointer}/participant_refs`, 2, true), atomicity_scope: requiredString(record.atomicity_scope, `${pointer}/atomicity_scope`), selected_guarantees: guarantees, implementation_profile_ref: PROFILE_ID, failure_outcome_binding_ref: reference(record.failure_outcome_binding_ref, `${pointer}/failure_outcome_binding_ref`), evidence_boundary: requiredString(record.evidence_boundary, `${pointer}/evidence_boundary`) });
  });

  const durableWorkflowRuntimeBindings = recordArray(value.durable_workflow_runtime_bindings, "/durable_workflow_runtime_bindings").map((record, index) => {
    const pointer = `/durable_workflow_runtime_bindings/${index}`;
    exactKeys(record, ["binding_id", "workflow_profile_ref", "persistence_binding_refs", "transaction_guarantee_binding_refs", "failure_outcome_binding_refs", "scheduler_contract_ref", "clock_contract_ref", "wakeup_contract_ref", "replay_contract_ref", "version_compatibility_ref", "evidence_boundary"], pointer);
    if (record.wakeup_contract_ref !== null) reference(record.wakeup_contract_ref, `${pointer}/wakeup_contract_ref`);
    return Object.freeze({ binding_id: reference(record.binding_id, `${pointer}/binding_id`), workflow_profile_ref: reference(record.workflow_profile_ref, `${pointer}/workflow_profile_ref`), persistence_binding_refs: stringSet(record.persistence_binding_refs, `${pointer}/persistence_binding_refs`, 1, true), transaction_guarantee_binding_refs: stringSet(record.transaction_guarantee_binding_refs, `${pointer}/transaction_guarantee_binding_refs`, 1, true), failure_outcome_binding_refs: stringSet(record.failure_outcome_binding_refs, `${pointer}/failure_outcome_binding_refs`, 1, true), scheduler_contract_ref: reference(record.scheduler_contract_ref, `${pointer}/scheduler_contract_ref`), clock_contract_ref: reference(record.clock_contract_ref, `${pointer}/clock_contract_ref`), wakeup_contract_ref: record.wakeup_contract_ref, replay_contract_ref: reference(record.replay_contract_ref, `${pointer}/replay_contract_ref`), version_compatibility_ref: reference(record.version_compatibility_ref, `${pointer}/version_compatibility_ref`), evidence_boundary: requiredString(record.evidence_boundary, `${pointer}/evidence_boundary`) });
  });

  const dependencyIds = identities(dependencyContracts, "contract_id", "/dependency_contracts");
  const persistenceIds = identities(persistenceBindings, "binding_id", "/persistence_bindings");
  const failureIds = identities(failureOutcomeBindings, "binding_id", "/failure_outcome_bindings");
  const transactionIds = identities(transactionGuaranteeBindings, "binding_id", "/transaction_guarantee_bindings");
  identities(durableWorkflowRuntimeBindings, "binding_id", "/durable_workflow_runtime_bindings");
  for (const binding of persistenceBindings) if (!dependencyIds.has(binding.dependency_contract_ref)) fail("SIC_REFERENCE_UNRESOLVED", "/persistence_bindings", `dependency contract unresolved:${binding.dependency_contract_ref}`);
  for (const binding of failureOutcomeBindings) if (!dependencyIds.has(binding.concern_ref)) fail("SIC_REFERENCE_UNRESOLVED", "/failure_outcome_bindings", `failure concern unresolved:${binding.concern_ref}`);
  for (const binding of transactionGuaranteeBindings) {
    if (!dependencyIds.has(binding.unit_of_work_contract_ref)) fail("SIC_REFERENCE_UNRESOLVED", "/transaction_guarantee_bindings", `Unit of Work contract unresolved:${binding.unit_of_work_contract_ref}`);
    if (!failureIds.has(binding.failure_outcome_binding_ref)) fail("SIC_REFERENCE_UNRESOLVED", "/transaction_guarantee_bindings", `failure binding unresolved:${binding.failure_outcome_binding_ref}`);
  }
  for (const binding of durableWorkflowRuntimeBindings) {
    for (const id of binding.persistence_binding_refs) if (!persistenceIds.has(id)) fail("SIC_DURABLE_BINDING_INCOMPLETE", "/durable_workflow_runtime_bindings", `persistence binding unresolved:${id}`);
    for (const id of binding.transaction_guarantee_binding_refs) if (!transactionIds.has(id)) fail("SIC_DURABLE_BINDING_INCOMPLETE", "/durable_workflow_runtime_bindings", `transaction binding unresolved:${id}`);
    for (const id of binding.failure_outcome_binding_refs) if (!failureIds.has(id)) fail("SIC_DURABLE_BINDING_INCOMPLETE", "/durable_workflow_runtime_bindings", `failure binding unresolved:${id}`);
    for (const id of [binding.scheduler_contract_ref, binding.clock_contract_ref, binding.replay_contract_ref]) if (!dependencyIds.has(id)) fail("SIC_DURABLE_BINDING_INCOMPLETE", "/durable_workflow_runtime_bindings", `dependency contract unresolved:${id}`);
    if (typeof binding.wakeup_contract_ref === "string" && !dependencyIds.has(binding.wakeup_contract_ref)) fail("SIC_DURABLE_BINDING_INCOMPLETE", "/durable_workflow_runtime_bindings", `wakeup contract unresolved:${binding.wakeup_contract_ref}`);
  }

  return Object.freeze({ schema_version: "domainspec.system-integration-binding-set/v1", binding_set_id: bindingSetId, profile_id: PROFILE_ID, subject_ref: subjectRef, dependency_contracts: sortRecords(dependencyContracts, "contract_id"), persistence_bindings: sortRecords(persistenceBindings, "binding_id"), transaction_guarantee_bindings: sortRecords(transactionGuaranteeBindings, "binding_id"), failure_outcome_bindings: sortRecords(failureOutcomeBindings, "binding_id"), durable_workflow_runtime_bindings: sortRecords(durableWorkflowRuntimeBindings, "binding_id"), authority_effect: "none" });
}

export function compileSystemIntegrationManifest(value: unknown, language: SupportedLanguage): SystemIntegrationBindingManifestV1 {
  const canonicalBindings = validateSystemIntegrationBindingSet(value);
  const selectedLanguage = languageProfile(language);
  const body = Object.freeze({
    schema_version: "domainspec.system-integration-binding-manifest/v1" as const,
    binding_set_id: String(canonicalBindings.binding_set_id),
    subject_ref: String(canonicalBindings.subject_ref),
    profile: Object.freeze({ profile_id: PROFILE_ID, profile_digest: FROZEN_SYSTEM_INTEGRATION.profile_digest, language_profile_id: selectedLanguage.value.language_profile_id, language_profile_digest: selectedLanguage.digest, architecture_id: FROZEN_SYSTEM_INTEGRATION.profile.architecture.architecture_id, architecture_sha256: FROZEN_SYSTEM_INTEGRATION.profile.architecture.sha256 }),
    language,
    source_digest: sha256(canonicalJson(value)),
    canonical_bindings: canonicalBindings,
    runtime_guarantees_observed: false as const,
    authority_effect: "none" as const,
  });
  return Object.freeze({ ...body, binding_digest: sha256(canonicalJson(body)) });
}

export function validateSystemIntegrationManifest(value: unknown, language?: SupportedLanguage): SystemIntegrationBindingManifestV1 {
  exactKeys(value, ["schema_version", "binding_set_id", "subject_ref", "profile", "language", "source_digest", "canonical_bindings", "runtime_guarantees_observed", "authority_effect", "binding_digest"], "/manifest");
  if (value.schema_version !== "domainspec.system-integration-binding-manifest/v1" || !["typescript", "python", "rust"].includes(String(value.language))) fail("SIC_SCHEMA", "/manifest", "manifest envelope mismatch");
  const manifestLanguage = value.language as SupportedLanguage;
  if (language && manifestLanguage !== language) fail("SIC_PROFILE_UNRESOLVED", "/manifest/language", "manifest language mismatch");
  exactKeys(value.profile, ["profile_id", "profile_digest", "language_profile_id", "language_profile_digest", "architecture_id", "architecture_sha256"], "/manifest/profile");
  const selectedLanguage = languageProfile(manifestLanguage);
  if (value.profile.profile_id !== PROFILE_ID || value.profile.profile_digest !== FROZEN_SYSTEM_INTEGRATION.profile_digest || value.profile.language_profile_id !== selectedLanguage.value.language_profile_id || value.profile.language_profile_digest !== selectedLanguage.digest || value.profile.architecture_id !== FROZEN_SYSTEM_INTEGRATION.profile.architecture.architecture_id || value.profile.architecture_sha256 !== FROZEN_SYSTEM_INTEGRATION.profile.architecture.sha256) fail("SIC_PROFILE_UNRESOLVED", "/manifest/profile", "manifest profile binding mismatch");
  const canonicalBindings = validateSystemIntegrationBindingSet(value.canonical_bindings);
  if (canonicalJson(canonicalBindings) !== canonicalJson(value.canonical_bindings)) fail("SIC_SCHEMA", "/manifest/canonical_bindings", "manifest bindings are not canonical");
  for (const field of ["source_digest", "binding_digest"] as const) if (typeof value[field] !== "string" || !/^[a-f0-9]{64}$/.test(value[field])) fail("SIC_SCHEMA", `/manifest/${field}`, "invalid digest");
  if (value.runtime_guarantees_observed !== false || value.authority_effect !== "none") fail("SIC_SCHEMA", "/manifest", "manifest claim ceiling inflated");
  const { binding_digest: ignored, ...body } = value;
  if (sha256(canonicalJson(body)) !== value.binding_digest) fail("SIC_BINDING_DIGEST_MISMATCH", "/manifest/binding_digest", "manifest binding digest drift");
  return value as unknown as SystemIntegrationBindingManifestV1;
}

function words(value: string): string[] {
  return value.split(/[^A-Za-z0-9]+/).filter(Boolean);
}

function pascal(value: string): string {
  const result = words(value).map((word) => `${word[0]?.toUpperCase() ?? ""}${word.slice(1)}`).join("") || "Dependency";
  return /^[A-Za-z_]/.test(result) ? result : `Dependency${result}`;
}

export function renderSystemIntegrationContract(manifestValue: SystemIntegrationBindingManifestV1): string {
  const manifest = validateSystemIntegrationManifest(manifestValue);
  const contracts = manifest.canonical_bindings.dependency_contracts as readonly { readonly concern: string }[];
  const json = canonicalJson(manifest);
  let content: string;
  if (manifest.language === "typescript") {
    const declarations = contracts.map(({ concern }) => `export type ${pascal(concern)}Contract = Readonly<{ readonly concern: ${JSON.stringify(concern)}; readonly operations: readonly string[]; readonly failures: readonly string[] }>;`).join("\n");
    content = `// generated by DomainSpec system-integration provider-neutral-v1\n// domainspec-system-integration-binding-digest: ${manifest.binding_digest}\n${declarations}\nexport const domainSpecSystemIntegrationManifestJson = ${JSON.stringify(json)} as const;\nexport const domainSpecSystemIntegrationRuntimeGuaranteesObserved = false as const;\n`;
  } else if (manifest.language === "python") {
    const declarations = contracts.map(({ concern }) => `class ${pascal(concern)}Contract(Protocol):\n    concern: Literal[${JSON.stringify(concern)}]\n    operations: tuple[str, ...]\n    failures: tuple[str, ...]\n`).join("\n");
    content = `# generated by DomainSpec system-integration provider-neutral-v1\n# domainspec-system-integration-binding-digest: ${manifest.binding_digest}\nfrom typing import Final, Literal, Protocol\n\n${declarations}\nDOMAIN_SPEC_SYSTEM_INTEGRATION_MANIFEST_JSON: Final[str] = ${JSON.stringify(json)}\nDOMAIN_SPEC_SYSTEM_INTEGRATION_RUNTIME_GUARANTEES_OBSERVED: Final[bool] = False\n`;
  } else {
    const declarations = contracts.map(({ concern }) => `pub trait ${pascal(concern)}Contract { fn concern(&self) -> &'static str { ${JSON.stringify(concern)} } fn operations(&self) -> &'static [&'static str]; fn failures(&self) -> &'static [&'static str]; }`).join("\n");
    content = `// generated by DomainSpec system-integration provider-neutral-v1\n// domainspec-system-integration-binding-digest: ${manifest.binding_digest}\n${declarations}\npub const DOMAIN_SPEC_SYSTEM_INTEGRATION_MANIFEST_JSON: &str = ${JSON.stringify(json)};\npub const DOMAIN_SPEC_SYSTEM_INTEGRATION_RUNTIME_GUARANTEES_OBSERVED: bool = false;\n`;
  }
  if (/\bPort\b/.test(content)) fail("SIC_UNIVERSAL_PORT_FORBIDDEN", "/generated", "generated source contains a universal dependency abstraction");
  return content;
}

export function verifySystemIntegrationContract(content: string, manifestValue: SystemIntegrationBindingManifestV1): true {
  const manifest = validateSystemIntegrationManifest(manifestValue);
  if (!content.includes(`domainspec-system-integration-binding-digest: ${manifest.binding_digest}`) || !content.includes(JSON.stringify(canonicalJson(manifest))) || /\bPort\b/.test(content)) fail("SIC_GENERATED_PROFILE_DRIFT", "/generated", "generated system-integration contract drifted");
  if (content !== renderSystemIntegrationContract(manifest)) fail("SIC_GENERATED_PROFILE_DRIFT", "/generated", "generated source is not the exact selected profile output");
  return true;
}

export function generatedSystemIntegrationPath(bindingSetId: string, language: SupportedLanguage): string {
  if (!ID.test(bindingSetId)) fail("SIC_SCHEMA", "/binding_set_id", "invalid binding-set id");
  return `src/domainspec/system-integration/${language}/${bindingSetId}.${languageProfile(language).value.generated_extension}`;
}

export function loadSystemIntegrationSelection(sourceRoot: string, bindingSetId: string, profileSelector: string, subjectRef: string, language: SupportedLanguage): SystemIntegrationSelectionV1 {
  if (profileSelector !== "provider-neutral-v1") fail("SIC_PROFILE_UNRESOLVED", "/integration-profile", `unsupported integration profile:${profileSelector}`);
  if (!ID.test(bindingSetId)) fail("SIC_SCHEMA", "/integration-binding-set", "invalid binding-set id");
  const relativePath = `integrations/${bindingSetId}.json`;
  const absolute = path.resolve(sourceRoot, relativePath);
  const relative = path.relative(sourceRoot, absolute);
  if (relative.startsWith("..") || path.isAbsolute(relative)) fail("SIC_SCHEMA", "/integration-binding-set", "binding-set path escapes source root");
  let stats: fs.Stats;
  try { stats = fs.lstatSync(absolute); } catch { fail("SIC_SCHEMA", `/${relativePath}`, "binding-set file is missing"); }
  if (stats.isSymbolicLink() || !stats.isFile() || fs.realpathSync(absolute) !== absolute) fail("SIC_SCHEMA", `/${relativePath}`, "binding-set must be a regular contained file without symlinks");
  const bytes = fs.readFileSync(absolute);
  let value: unknown;
  try { value = JSON.parse(bytes.toString("utf8")); } catch { fail("SIC_SCHEMA", `/${relativePath}`, "binding-set is not valid JSON"); }
  const manifest = compileSystemIntegrationManifest(value, language);
  if (manifest.binding_set_id !== bindingSetId || manifest.subject_ref !== subjectRef) fail("SIC_REFERENCE_KIND_MISMATCH", `/${relativePath}`, "binding-set identity or subject does not match the selected node");
  const generatedRelativePath = generatedSystemIntegrationPath(bindingSetId, language);
  return Object.freeze({ profile_selector: "provider-neutral-v1", binding_source: Object.freeze({ relative_path: relativePath, sha256: sha256(bytes) }), manifest, generated_relative_path: generatedRelativePath, generated_content: renderSystemIntegrationContract(manifest) });
}
