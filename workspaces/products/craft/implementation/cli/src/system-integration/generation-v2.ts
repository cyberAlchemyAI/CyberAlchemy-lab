import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { PlannedArtifact } from "../generation/contracts.js";
import { compileExternalApiCompositionV2 } from "./external-api-v2.js";
import type { ExternalApiCompositionV2 } from "./external-api-v2-types.js";
import { compileMessagingCompositionV2 } from "./messaging-v2.js";
import type { MessagingCompositionV2 } from "./messaging-v2-types.js";
import { compilePersistenceCompositionV2 } from "./persistence-v2.js";
import type { PersistenceCompositionV2 } from "./persistence-v2-types.js";
import { validateIntegrationDisclosurePolicyV1, validateOrodiObservationBindingV1, type IntegrationDisclosurePolicyV1, type OrodiObservationBindingV1 } from "./observation-v2.js";
import { INTEGRATION_PROJECT_LAYOUT_V1, integrationResponsibilityPathsV1, type IntegrationGenerationLanguage } from "./integration-project-layout-v1.js";

export interface IntegrationGenerationSourceV2 {
  readonly schema_version: "domainspec.integration-generation-source/v2-candidate";
  readonly source_id: string;
  readonly persistence: PersistenceCompositionV2;
  readonly messaging: MessagingCompositionV2;
  readonly external_api: ExternalApiCompositionV2;
  readonly disclosure_policy: IntegrationDisclosurePolicyV1;
  readonly orodi_binding: OrodiObservationBindingV1;
}

export class IntegrationGenerationError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "IntegrationGenerationError";
  }
}

export interface IntegrationSemanticManifestV1 {
  readonly schema_version: "domainspec.integration-semantic-manifest/v1-candidate";
  readonly source_id: string;
  readonly definition_pack_sha256: string;
  readonly composition_digests: Readonly<{ persistence: string; messaging: string; external_api: string }>;
  readonly contracts: readonly string[];
  readonly integration_bindings: readonly string[];
  readonly provider_profiles: readonly string[];
  readonly provider_realizations: readonly string[];
  readonly mappings: readonly string[];
  readonly message_types: readonly string[];
  readonly channels: readonly Readonly<{ channel_id: string; channel_kind: string }>[];
  readonly migrations: readonly string[];
  readonly observation_edge_sequence: readonly ["runtime", "observer", "orodi-adapter", "orodi-evaluator"];
  readonly orodi_return_edge: "prohibited";
  readonly authority_effect: "none";
}

export interface IntegrationProjectPlanV2 {
  readonly schema_version: "domainspec.integration-project-plan/v2-candidate";
  readonly language: IntegrationGenerationLanguage;
  readonly output_layout: typeof INTEGRATION_PROJECT_LAYOUT_V1.schema_version;
  readonly semantic_manifest: IntegrationSemanticManifestV1;
  readonly artifacts: readonly PlannedArtifact[];
  readonly plan_digest: string;
  readonly runtime_guarantees_observed: false;
  readonly authority_effect: "none";
}

type CompiledSource = Readonly<{
  persistence: ReturnType<typeof compilePersistenceCompositionV2>;
  messaging: ReturnType<typeof compileMessagingCompositionV2>;
  externalApi: ReturnType<typeof compileExternalApiCompositionV2>;
  disclosure: IntegrationDisclosurePolicyV1;
  orodi: OrodiObservationBindingV1;
}>;

function artifact(relative_path: string, content: string): PlannedArtifact {
  return Object.freeze({ relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content) });
}

function freeze<T>(value: T): T {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value as Record<string, unknown>)) freeze(child);
  }
  return value;
}

function unique(values: readonly string[]): readonly string[] {
  return Object.freeze([...new Set(values)].sort());
}

function symbol(value: string): string {
  const words = value.split(/[^A-Za-z0-9]+/).filter(Boolean);
  const result = words.map(word => word[0]!.toUpperCase() + word.slice(1)).join("");
  return /^[A-Za-z]/.test(result) ? result : `Integration${result}`;
}

function fail(code: string, pointer: string, message: string): never {
  throw new IntegrationGenerationError(code, pointer, message);
}

function validateSourceEnvelope(source: unknown): asserts source is IntegrationGenerationSourceV2 {
  if (source === null || typeof source !== "object" || Array.isArray(source)) fail("INTEGRATION_GENERATION_SCHEMA", "/", "expected object");
  const value = source as Record<string, unknown>;
  const expected = ["schema_version", "source_id", "persistence", "messaging", "external_api", "disclosure_policy", "orodi_binding"].sort();
  if (canonicalJson(Object.keys(value).sort()) !== canonicalJson(expected)) fail("INTEGRATION_GENERATION_SCHEMA", "/", "unexpected or missing member");
  if (value.schema_version !== "domainspec.integration-generation-source/v2-candidate") fail("INTEGRATION_GENERATION_SCHEMA", "/schema_version", "unsupported generation source");
  if (typeof value.source_id !== "string" || !/^[A-Za-z][A-Za-z0-9]*(?:[-.:/#][A-Za-z0-9]+)*$/.test(value.source_id)) fail("INTEGRATION_GENERATION_SCHEMA", "/source_id", "expected a stable source reference");
}

function compileSource(source: IntegrationGenerationSourceV2): CompiledSource {
  validateSourceEnvelope(source);
  const persistence = compilePersistenceCompositionV2(source.persistence);
  const messaging = compileMessagingCompositionV2(source.messaging);
  const externalApi = compileExternalApiCompositionV2(source.external_api);
  const disclosure = validateIntegrationDisclosurePolicyV1(source.disclosure_policy);
  const orodi = validateOrodiObservationBindingV1(source.orodi_binding);
  if (orodi.disclosure_policy_ref !== disclosure.policy_id) throw Object.assign(new Error("INTEGRATION_GENERATION_DISCLOSURE_BINDING"), { code: "INTEGRATION_GENERATION_DISCLOSURE_BINDING", exitCode: 22 });
  const digests = new Set([persistence.integration_kernel.definition_pack_sha256, messaging.integration_kernel.definition_pack_sha256, externalApi.integration_kernel.definition_pack_sha256]);
  if (digests.size !== 1) throw Object.assign(new Error("INTEGRATION_GENERATION_DEFINITION_DRIFT"), { code: "INTEGRATION_GENERATION_DEFINITION_DRIFT", exitCode: 22 });
  return freeze({ persistence, messaging, externalApi, disclosure, orodi });
}

function semanticManifest(sourceId: string, source: CompiledSource): IntegrationSemanticManifestV1 {
  const kernels = [source.persistence.integration_kernel, source.messaging.integration_kernel, source.externalApi.integration_kernel];
  return freeze({
    schema_version: "domainspec.integration-semantic-manifest/v1-candidate",
    source_id: sourceId,
    definition_pack_sha256: kernels[0]!.definition_pack_sha256,
    composition_digests: { persistence: source.persistence.composition_digest, messaging: source.messaging.composition_digest, external_api: source.externalApi.composition_digest },
    contracts: unique([
      ...source.persistence.persistence_bindings.map(item => item.dependency_contract_ref),
      ...source.messaging.publication_bindings.map(item => item.producer_contract_ref),
      ...source.externalApi.external_api_contracts.map(item => item.contract_id),
    ]),
    integration_bindings: unique(kernels.flatMap(kernel => kernel.integration_bindings.map(item => item.binding_id))),
    provider_profiles: unique(kernels.flatMap(kernel => kernel.provider_profiles.map(item => item.profile_id))),
    provider_realizations: unique(kernels.flatMap(kernel => kernel.provider_realizations.map(item => item.realization_id))),
    mappings: unique([
      ...source.persistence.persistence_mappings.map(item => item.mapping_id),
      ...source.messaging.message_mappings.map(item => item.mapper_ref),
      ...source.externalApi.api_mappings.map(item => item.mapper_ref),
    ]),
    message_types: unique(source.messaging.message_types.map(item => item.message_type_id)),
    channels: Object.freeze(source.messaging.channels.map(item => Object.freeze({ channel_id: item.channel_id, channel_kind: item.channel_kind })).sort((a, b) => a.channel_id.localeCompare(b.channel_id))),
    migrations: unique(source.persistence.migrations.map(item => item.migration_id)),
    observation_edge_sequence: ["runtime", "observer", "orodi-adapter", "orodi-evaluator"],
    orodi_return_edge: "prohibited",
    authority_effect: "none",
  });
}

function contractRows(source: CompiledSource): readonly Readonly<{ name: string; kind: "persistence" | "publisher" | "external-api"; operations: readonly string[] }>[] {
  const rows = [
    ...source.persistence.persistence_bindings.map(item => ({ name: symbol(item.dependency_contract_ref), kind: "persistence" as const, operations: ["load", "save"] })),
    ...source.messaging.publication_bindings.map(item => ({ name: symbol(item.producer_contract_ref), kind: "publisher" as const, operations: ["publish"] })),
    ...source.externalApi.external_api_contracts.map(item => ({ name: symbol(item.contract_id), kind: "external-api" as const, operations: item.operations.map(operation => operation.operation_id) })),
  ];
  const byName = new Map<string, typeof rows[number]>();
  for (const row of rows.sort((a, b) => a.name.localeCompare(b.name))) {
    const previous = byName.get(row.name);
    if (previous && canonicalJson(previous) !== canonicalJson(row)) throw new Error(`INTEGRATION_GENERATION_CONTRACT_COLLISION:${row.name}`);
    byName.set(row.name, row);
  }
  return Object.freeze([...byName.values()]);
}

function descriptorGroups(source: CompiledSource) {
  const kernels = [source.persistence.integration_kernel, source.messaging.integration_kernel, source.externalApi.integration_kernel];
  return {
    providers: { profiles: kernels.flatMap(kernel => kernel.provider_profiles), realizations: kernels.flatMap(kernel => kernel.provider_realizations) },
    mappings: { persistence: source.persistence.persistence_mappings, messaging: source.messaging.message_mappings, external_api: source.externalApi.api_mappings },
    configuration: { authentication_bindings: source.externalApi.authentication_bindings, serialization_profiles: kernels.flatMap(kernel => kernel.serialization_profiles) },
    migrations: source.persistence.migrations,
    observation: { disclosure_policy: source.disclosure, orodi_binding: source.orodi },
  };
}

function renderTypeScript(source: CompiledSource, manifest: IntegrationSemanticManifestV1): readonly PlannedArtifact[] {
  const paths = integrationResponsibilityPathsV1("typescript");
  const contracts = contractRows(source).map(row => {
    const methods = row.operations.map(operation => `  readonly ${JSON.stringify(operation)}: (input: Readonly<Record<string, unknown>>) => ${row.kind === "publisher" ? "Promise<ProviderAcceptanceReceipt>" : "Promise<unknown>"};`).join("\n");
    return `export interface ${row.name} {\n${methods}\n}`;
  }).join("\n\n");
  const acceptance = `export interface ProviderAcceptanceReceipt {\n  readonly acceptance_boundary_ref:string;\n  readonly provider_acknowledgement_ref:string;\n  readonly claim_ceiling:"provider-accepted";\n  readonly delivery_observed:false;\n  readonly consumer_completion_observed:false;\n}\n`;
  const groups = descriptorGroups(source);
  return Object.freeze([
    artifact(paths.application_contracts, `${acceptance}\n${contracts}\n`),
    artifact(paths.provider_adapters, `export const PROVIDER_BINDINGS = ${canonicalJson(groups.providers)} as const;\n`),
    artifact(paths.mappings, `export const INTEGRATION_MAPPINGS = ${canonicalJson(groups.mappings)} as const;\n`),
    artifact(paths.configuration, `export const INTEGRATION_CONFIGURATION = ${canonicalJson(groups.configuration)} as const;\n`),
    artifact(paths.migrations, `export const DATABASE_MIGRATIONS = ${canonicalJson(groups.migrations)} as const;\n`),
    artifact(paths.observation, `export const INTEGRATION_OBSERVATION = ${canonicalJson(groups.observation)} as const;\n`),
    artifact(paths.semantic_manifest, `${canonicalJson(manifest)}\n`),
    artifact("tsconfig.json", `${canonicalJson({ compilerOptions: { target: "ES2022", module: "NodeNext", moduleResolution: "NodeNext", strict: true, noEmit: true }, include: ["src/**/*.ts", "migrations/**/*.ts"] })}\n`),
  ].sort((a, b) => a.relative_path.localeCompare(b.relative_path)));
}

function pythonJson(name: string, value: unknown): string {
  return `import json as _json\n${name} = _json.loads(${JSON.stringify(canonicalJson(value))})\n`;
}

function renderPython(source: CompiledSource, manifest: IntegrationSemanticManifestV1): readonly PlannedArtifact[] {
  const paths = integrationResponsibilityPathsV1("python");
  const contracts = contractRows(source).map(row => {
    const methods = row.operations.map(operation => `    async def ${operation.replaceAll("-", "_")}(self, input: Mapping[str, object]) -> ${row.kind === "publisher" ? "ProviderAcceptanceReceipt" : "object"}: ...`).join("\n");
    return `class ${row.name}(Protocol):\n${methods}`;
  }).join("\n\n");
  const acceptance = `class ProviderAcceptanceReceipt(TypedDict):\n    acceptance_boundary_ref: str\n    provider_acknowledgement_ref: str\n    claim_ceiling: Literal["provider-accepted"]\n    delivery_observed: Literal[False]\n    consumer_completion_observed: Literal[False]\n`;
  const groups = descriptorGroups(source);
  return Object.freeze([
    artifact(paths.application_contracts, `from typing import Literal, Mapping, Protocol, TypedDict\n\n${acceptance}\n${contracts}\n`),
    artifact(paths.provider_adapters, pythonJson("PROVIDER_BINDINGS", groups.providers)),
    artifact(paths.mappings, pythonJson("INTEGRATION_MAPPINGS", groups.mappings)),
    artifact(paths.configuration, pythonJson("INTEGRATION_CONFIGURATION", groups.configuration)),
    artifact(paths.migrations, pythonJson("DATABASE_MIGRATIONS", groups.migrations)),
    artifact(paths.observation, pythonJson("INTEGRATION_OBSERVATION", groups.observation)),
    artifact(paths.semantic_manifest, `${canonicalJson(manifest)}\n`),
    artifact("pyproject.toml", `[project]\nname = "domainspec-generated-integrations"\nversion = "0.0.0"\nrequires-python = ">=3.11"\n`),
  ].sort((a, b) => a.relative_path.localeCompare(b.relative_path)));
}

function rustJson(name: string, value: unknown): string {
  return `pub const ${name}: &str = r###"${canonicalJson(value)}"###;\n`;
}

function renderRust(source: CompiledSource, manifest: IntegrationSemanticManifestV1): readonly PlannedArtifact[] {
  const paths = integrationResponsibilityPathsV1("rust");
  const contracts = contractRows(source).map(row => {
    const methods = row.operations.map(operation => `    fn ${operation.replaceAll("-", "_")}<'a>(&'a self, input: &'a str) -> ${row.kind === "publisher" ? "ProviderAcceptanceFuture<'a>" : "ContractFuture<'a>"};`).join("\n");
    return `pub trait ${row.name} {\n${methods}\n}`;
  }).join("\n\n");
  const groups = descriptorGroups(source);
  const files = [
    artifact(paths.application_contracts, `use std::{future::Future,pin::Pin};\npub type ContractFuture<'a>=Pin<Box<dyn Future<Output=Result<String,String>>+Send+'a>>;\npub type ProviderAcceptanceFuture<'a>=Pin<Box<dyn Future<Output=Result<ProviderAcceptanceReceipt,String>>+Send+'a>>;\n#[derive(Clone,Debug,PartialEq,Eq)]\npub struct ProviderAcceptanceReceipt { pub acceptance_boundary_ref:&'static str, pub provider_acknowledgement_ref:String, pub claim_ceiling:&'static str, pub delivery_observed:bool, pub consumer_completion_observed:bool }\n\n${contracts}\n`),
    artifact(paths.provider_adapters, rustJson("PROVIDER_BINDINGS_JSON", groups.providers)),
    artifact(paths.mappings, rustJson("INTEGRATION_MAPPINGS_JSON", groups.mappings)),
    artifact(paths.configuration, rustJson("INTEGRATION_CONFIGURATION_JSON", groups.configuration)),
    artifact(paths.migrations, rustJson("DATABASE_MIGRATIONS_JSON", groups.migrations)),
    artifact(paths.observation, rustJson("INTEGRATION_OBSERVATION_JSON", groups.observation)),
    artifact(paths.semantic_manifest, `${canonicalJson(manifest)}\n`),
    artifact("Cargo.toml", `[package]\nname = "domainspec-generated-integrations"\nversion = "0.0.0"\nedition = "2021"\n\n[lib]\npath = "src/lib.rs"\n\n[workspace]\n`),
    artifact("src/lib.rs", "pub mod config;\npub mod features;\npub mod integrations;\npub mod observability;\n"),
    artifact("src/config/mod.rs", "pub mod integrations;\n"),
    artifact("src/config/integrations/mod.rs", "pub mod manifest;\n"),
    artifact("src/features/mod.rs", "pub mod integration;\n"),
    artifact("src/features/integration/mod.rs", "pub mod application;\n"),
    artifact("src/features/integration/application/mod.rs", "pub mod contracts;\n"),
    artifact("src/integrations/mod.rs", "pub mod mappings;\npub mod providers;\n"),
    artifact("src/integrations/mappings/mod.rs", "pub mod definitions;\n"),
    artifact("src/integrations/providers/mod.rs", "pub mod bindings;\n"),
    artifact("src/observability/mod.rs", "pub mod integrations;\n"),
    artifact("src/observability/integrations/mod.rs", "pub mod observation;\n"),
  ];
  return Object.freeze(files.sort((a, b) => a.relative_path.localeCompare(b.relative_path)));
}

export function planIntegrationProjectV2(source: IntegrationGenerationSourceV2, language: IntegrationGenerationLanguage): IntegrationProjectPlanV2 {
  if (!(["typescript", "python", "rust"] as const).includes(language)) fail("INTEGRATION_GENERATION_LANGUAGE", "/language", "unsupported generation language");
  const compiled = compileSource(source);
  const manifest = semanticManifest(source.source_id, compiled);
  const artifacts = language === "typescript" ? renderTypeScript(compiled, manifest) : language === "python" ? renderPython(compiled, manifest) : renderRust(compiled, manifest);
  const body = { schema_version: "domainspec.integration-project-plan/v2-candidate" as const, language, output_layout: INTEGRATION_PROJECT_LAYOUT_V1.schema_version, semantic_manifest: manifest, artifacts, runtime_guarantees_observed: false as const, authority_effect: "none" as const };
  return freeze({ ...body, plan_digest: sha256(canonicalJson(body)) });
}
