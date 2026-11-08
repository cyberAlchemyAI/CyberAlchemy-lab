import path from "node:path";

import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { planIntegrationProjectV2, type IntegrationGenerationSourceV2 } from "../system-integration/generation-v2.js";
import { REQUIRED_PROVIDER_CAPABILITIES, REFERENCE_PROVIDER_RUNTIME, providerPackSelectionSha256, validateProviderPackSelectionV1, type ProviderPackSelectionV1 } from "../system-integration/provider-pack-v1.js";
import type { PlannedArtifact } from "./contracts.js";
import type { CompiledOperationRequestContractV1, CompiledRuntimeMappingBindingV1 } from "../system-integration/application-graph-v1.js";
import { PYTHON_PROVIDER_REQUIREMENTS_LOCK } from "./provider-python-lock.generated.js";
import { RUST_PROVIDER_CARGO_LOCK } from "./provider-rust-lock.generated.js";
import { TYPESCRIPT_PROVIDER_PACKAGE_LOCK } from "./provider-typescript-lock.generated.js";
import { assertWholeApplicationPlan, type WholeApplicationPathOwnerV1, type WholeApplicationPlanV1 } from "./whole-application-v1.js";

export interface ProviderApplicationPlanV1 {
  readonly schema_version: "domainspec.provider-application-plan/v1-candidate";
  readonly language: "typescript" | "python" | "rust";
  readonly project_id: string;
  readonly domain_source_manifest_sha256: string;
  readonly integration_source_sha256: string;
  readonly compilation_selection_sha256: string;
  readonly binding_sha256: string;
  readonly whole_application_plan_sha256: string;
  readonly provider_selection_sha256: string;
  readonly dependencies: readonly Readonly<{ role: string; library: string; version: string; source: "registry" | "platform" }>[];
  readonly artifacts: readonly PlannedArtifact[];
  readonly path_owners: readonly Readonly<{ relative_path: string; owner: WholeApplicationPathOwnerV1["owner"] | "provider-pack"; sha256: string }>[];
  readonly runtime_guarantees_observed: false;
  readonly claim_ceiling: "provider-code-formation-and-static-compilation-only";
  readonly authority_effect: "none";
  readonly plan_sha256: string;
}

export interface ProviderInboundRouteV1 { readonly method: "POST"; readonly path: string }

export class ProviderApplicationPlanError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(`${code}:${pointer}:${message}`);
    this.name = "ProviderApplicationPlanError";
  }
}

const snapshots = new WeakMap<ProviderApplicationPlanV1, string>();
type ProviderArtifactOwner = ProviderApplicationPlanV1["path_owners"][number]["owner"];
type ProviderArtifactRow = Readonly<{ artifact: PlannedArtifact; owner: ProviderArtifactOwner }>;
const fail = (code: string, pointer: string, message: string): never => { throw new ProviderApplicationPlanError(code, pointer, message); };
const freeze = <T>(value: T): T => { if (value !== null && typeof value === "object" && !Object.isFrozen(value)) { Object.freeze(value); for (const child of Object.values(value as Record<string, unknown>)) freeze(child); } return value; };
const artifact = (relative_path: string, content: string): PlannedArtifact => freeze({ relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content) });

function configurationSchema(selection: ProviderPackSelectionV1): PlannedArtifact {
  const properties = Object.fromEntries(selection.configuration.environment.map(item => [item.name, { type: "string", minLength: 1, writeOnly: item.classification === "secret-reference", "x-domainspec-classification": item.classification }]));
  return artifact(".domainspec/providers/configuration.schema.json", `${canonicalJson({ $schema: "https://json-schema.org/draft/2020-12/schema", type: "object", additionalProperties: false, required: selection.configuration.environment.map(item => item.name), properties })}\n`);
}

function providerManifest(selection: ProviderPackSelectionV1, dependencies: ProviderApplicationPlanV1["dependencies"]): PlannedArtifact {
  return artifact(".domainspec/providers/manifest.json", `${canonicalJson({ schema_version: "domainspec.provider-pack-manifest/v1-candidate", selection_id: selection.selection_id, pack_id: selection.pack_id, language: selection.language, capabilities: selection.capabilities, providers: selection.providers, dependencies, configuration_environment: selection.configuration.environment, messaging_destinations: selection.configuration.messaging_destinations, runtime_guarantees_observed: false, authority_effect: "none" })}\n`);
}

interface ProviderRuntimeGraphContracts {
  readonly mapping_bindings: readonly CompiledRuntimeMappingBindingV1[];
  readonly operation_requests: readonly CompiledOperationRequestContractV1[];
}

function messagingDestinationMap(selection: ProviderPackSelectionV1, source: IntegrationGenerationSourceV2): ReadonlyMap<string, string> {
  const expected = [...new Set(source.messaging.publication_bindings.map(binding => binding.channel_ref))].sort();
  const selected = [...selection.configuration.messaging_destinations].sort((left, right) => left.channel_ref.localeCompare(right.channel_ref));
  if (canonicalJson(selected.map(binding => binding.channel_ref)) !== canonicalJson(expected)) fail("DS_PROVIDER_MESSAGING_DESTINATION_COVERAGE", "/configuration/messaging_destinations", "destination bindings must exactly cover publication channels");
  return new Map(selected.map(binding => [binding.channel_ref, binding.environment_name]));
}

function publicationDestinationEnvironment(selection: ProviderPackSelectionV1, source: IntegrationGenerationSourceV2): string {
  if (source.messaging.publication_bindings.length !== 1) fail("DS_PROVIDER_PUBLICATION_CARDINALITY", "/messaging/publication_bindings", "reference provider generator currently requires one publication binding");
  return messagingDestinationMap(selection, source).get(source.messaging.publication_bindings[0]!.channel_ref)!;
}

function runtimePortManifest(source: IntegrationGenerationSourceV2, runtimeGraph: ProviderRuntimeGraphContracts, selection: ProviderPackSelectionV1): PlannedArtifact {
  const destinations = messagingDestinationMap(selection, source);
  const transactionFor = (bindingId: string): readonly string[] => Object.freeze(source.persistence.transaction_guarantees
    .filter(transaction => transaction.persistence_binding_refs.includes(bindingId))
    .map(transaction => transaction.binding_id)
    .sort());
  const ports = [
    ...source.persistence.persistence_bindings.map(binding => ({
      port_id: binding.binding_id,
      port_kind: "persistence" as const,
      contract_ref: binding.dependency_contract_ref,
      operations: ["load", "save"],
      logical_subject_refs: [...binding.logical_subject_refs].sort(),
      mapping_refs: [binding.logical_physical_mapping_ref],
      resource_ref: binding.resource_ref,
      transaction_refs: transactionFor(binding.binding_id),
    })),
    ...source.messaging.publication_bindings.map(binding => {
      const boundary = source.messaging.producer_acceptance_boundaries.find(item => item.boundary_id === binding.producer_acceptance_boundary_ref)!;
      return {
        port_id: binding.binding_id,
        port_kind: "message-publication" as const,
        contract_ref: binding.producer_contract_ref,
        operations: ["publish"],
        logical_subject_refs: [binding.logical_source_ref],
        mapping_refs: [binding.mapper_ref],
        message_type_ref: binding.message_type_ref,
        channel_ref: binding.channel_ref,
        destination_environment_name: destinations.get(binding.channel_ref),
        acceptance_boundary_ref: boundary.boundary_id,
        result_contract: {
          kind: "provider-acceptance-receipt" as const,
          claim_ceiling: boundary.claim_ceiling,
          observation_boundary: boundary.observation_boundary,
          delivery_observed: false as const,
          consumer_completion_observed: false as const,
        },
      };
    }),
    ...source.messaging.subscription_bindings.map(binding => ({
      port_id: binding.binding_id,
      port_kind: "message-subscription" as const,
      contract_ref: null,
      operations: ["consume"],
      logical_subject_refs: [binding.operation_ref],
      mapping_refs: [binding.mapper_ref],
      message_type_ref: binding.message_type_ref,
      channel_ref: binding.channel_ref,
      invokes_operation_ref: binding.operation_ref,
      acknowledgement_boundary_ref: binding.acknowledgement_boundary_ref,
    })),
    ...source.external_api.external_api_bindings.map(binding => {
      const contract = source.external_api.external_api_contracts.find(item => item.contract_id === binding.external_api_contract_ref)!;
      const operation = contract.operations.find(item => `${contract.contract_id}#${item.operation_id}` === binding.contract_operation_ref)!;
      return {
        port_id: binding.binding_id,
        port_kind: "external-api-outbound" as const,
        contract_ref: binding.external_api_contract_ref,
        operations: [operation.operation_id],
        logical_subject_refs: [operation.request_type_ref, operation.result_type_ref].sort(),
        mapping_refs: [binding.request_mapper_ref, binding.response_mapper_ref].sort(),
        provider_operation_ref: binding.provider_operation_ref,
        request_type_ref: operation.request_type_ref,
        result_type_ref: operation.result_type_ref,
      };
    }),
    ...source.external_api.inbound_endpoint_bindings.map(binding => ({
      port_id: binding.binding_id,
      port_kind: "external-api-inbound" as const,
      contract_ref: null,
      operations: ["receive"],
      logical_subject_refs: [binding.operation_ref],
      mapping_refs: [binding.request_mapper_ref, binding.response_mapper_ref].sort(),
      provider_operation_ref: binding.protocol_operation_ref,
      invokes_operation_ref: binding.operation_ref,
    })),
  ].sort((left, right) => left.port_id.localeCompare(right.port_id));
  const transactions = source.persistence.transaction_guarantees.map(transaction => ({
    transaction_id: transaction.binding_id,
    unit_of_work_contract_ref: transaction.unit_of_work_contract_ref,
    persistence_port_refs: [...transaction.persistence_binding_refs].sort(),
    participant_refs: [...transaction.participant_refs].sort(),
    atomicity_scope: transaction.atomicity_scope,
    selected_guarantees: [...transaction.selected_guarantees].sort(),
    local_commit_boundary_ref: transaction.local_commit_boundary_ref,
  })).sort((left, right) => left.transaction_id.localeCompare(right.transaction_id));
  const body = {
    schema_version: "domainspec.runtime-port-manifest/v1-candidate",
    source_id: source.source_id,
    required_execution_model: "async",
    ports,
    mapping_bindings: runtimeGraph.mapping_bindings,
    operation_requests: runtimeGraph.operation_requests,
    transactions,
    runtime_guarantees_observed: false,
    authority_effect: "none",
  } as const;
  return artifact(".domainspec/runtime-ports.json", `${canonicalJson({ ...body, manifest_sha256: sha256(canonicalJson(body)) })}\n`);
}

function runtimeGraphContracts(whole: WholeApplicationPlanV1): ProviderRuntimeGraphContracts {
  const artifact = whole.artifacts.find(item => item.relative_path === ".domainspec/application-graph.json");
  if (!artifact) return fail("DS_PROVIDER_RUNTIME_GRAPH", "/artifacts", "compiled application graph is missing");
  const graph = JSON.parse(artifact.content) as {
    readonly runtime_bindings?: readonly CompiledRuntimeMappingBindingV1[];
    readonly operation_requests?: readonly CompiledOperationRequestContractV1[];
  };
  if (!Array.isArray(graph.runtime_bindings)) return fail("DS_PROVIDER_RUNTIME_GRAPH", "/artifacts/.domainspec/application-graph.json/runtime_bindings", "runtime bindings are missing");
  if (!Array.isArray(graph.operation_requests)) return fail("DS_PROVIDER_RUNTIME_GRAPH", "/artifacts/.domainspec/application-graph.json/operation_requests", "operation request contracts are missing");
  return freeze({
    mapping_bindings: structuredClone(graph.runtime_bindings),
    operation_requests: structuredClone(graph.operation_requests),
  });
}

function dependencies(selection: ProviderPackSelectionV1): ProviderApplicationPlanV1["dependencies"] {
  return Object.freeze((Object.entries(selection.providers) as readonly [string, { library: string; version: string }][]).map(([role, value]) => freeze({ role, library: value.library, version: value.version, source: value.library.startsWith("platform-") || value.library === "node-http" ? "platform" as const : "registry" as const })));
}

interface ProviderMigrationArtifacts {
  readonly sql: string;
  readonly verification_sql: string;
  readonly manifest: string;
}

const REQUIRED_FAILURE_MATCHERS = Object.freeze([
  "postgresql:connection-unavailable",
  "postgresql:unique-violation",
  "broker:throttled",
  "broker:invalid-message",
  "http:timeout",
  "http:unauthorized",
  "http:malformed-response",
] as const);

function providerFailureOutcomes(source: IntegrationGenerationSourceV2): Readonly<Record<string, string>> {
  const profiles = [
    ...source.persistence.integration_kernel.provider_profiles,
    ...source.messaging.integration_kernel.provider_profiles,
    ...source.external_api.integration_kernel.provider_profiles,
  ];
  const requirements = [
    ["persistence", "postgresql", REQUIRED_PROVIDER_CAPABILITIES.persistence],
    ["messaging", "managed-broker", REQUIRED_PROVIDER_CAPABILITIES.messaging],
    ["outbound_http", "http-client", REQUIRED_PROVIDER_CAPABILITIES.outbound_http],
    ["inbound_http", "http-server", REQUIRED_PROVIDER_CAPABILITIES.inbound_http],
  ] as const;
  for (const [role, kind, capabilities] of requirements) {
    const compatible = profiles.some(profile => profile.provider_kind === kind && capabilities.every(capability => profile.capability_set.includes(capability)));
    if (!compatible) fail("DS_PROVIDER_CAPABILITY_INCOMPATIBLE", `/providers/${role}`, `integration source lacks ${kind}:${capabilities.join(",")}`);
  }
  const mappings = [
    ...source.persistence.integration_kernel.failure_mappings,
    ...source.messaging.integration_kernel.failure_mappings,
    ...source.external_api.integration_kernel.failure_mappings,
  ];
  const outcomes = new Map<string, string>();
  for (const mapping of mappings) for (const item of mapping.cases) {
    const prior = outcomes.get(item.provider_failure_matcher);
    if (prior !== undefined && prior !== item.failure_outcome_ref) fail("DS_PROVIDER_FAILURE_AMBIGUOUS", "/failure-mappings", `matcher has multiple outcomes:${item.provider_failure_matcher}`);
    outcomes.set(item.provider_failure_matcher, item.failure_outcome_ref);
  }
  for (const matcher of REQUIRED_FAILURE_MATCHERS) if (!outcomes.has(matcher)) fail("DS_PROVIDER_FAILURE_UNDECLARED", "/failure-mappings", `reference provider matcher is undeclared:${matcher}`);
  return freeze(Object.fromEntries([...outcomes].sort(([left], [right]) => left.localeCompare(right))));
}

function providerFailureCode(outcomes: Readonly<Record<string, string>>, matcher: typeof REQUIRED_FAILURE_MATCHERS[number]): string {
  return `${matcher}:${outcomes[matcher]}`;
}

function quoteSqlIdentifier(value: string): string {
  return `"${value.replaceAll('"', '""')}"`;
}

function quoteSqlString(value: string): string {
  return `'${value.replaceAll("'", "''")}'`;
}

function providerMigrations(source: IntegrationGenerationSourceV2): ProviderMigrationArtifacts {
  const mapping = source.persistence.persistence_mappings;
  const conversionTargets = new Map(mapping.flatMap(item => item.conversion_rules.map(rule => [rule.conversion_id, rule.target_shape] as const)));
  const domainTables = mapping.flatMap(item => item.physical_models.map(model => {
    const modelReferenceName = model.model_id.replace(/^physical-model:/, "");
    const prefix = `physical:${modelReferenceName}/`;
    const primary = new Set(item.identity_mappings.filter(field => field.physical_field_ref.startsWith(prefix)).map(field => field.physical_field_ref.slice(prefix.length)));
    const fields = new Map<string, Readonly<{ type: string; required: boolean }>>();
    for (const field of item.field_mappings.filter(field => field.physical_field_ref.startsWith(prefix))) {
      const name = field.physical_field_ref.slice(prefix.length);
      const target = field.conversion_ref === null ? null : conversionTargets.get(field.conversion_ref);
      const type = target?.endsWith(":bigint") === true ? "BIGINT" : field.storage_shape === "array" ? "JSONB" : "TEXT";
      fields.set(name, freeze({ type, required: field.logical_shape !== "optional" }));
    }
    for (const relation of item.relation_mappings.filter(relation => relation.source_field_ref.startsWith(prefix))) {
      const name = relation.source_field_ref.slice(prefix.length);
      if (!fields.has(name)) fields.set(name, freeze({ type: "TEXT", required: true }));
    }
    for (const index of item.index_mappings.filter(index => index.model_ref === model.model_id)) {
      for (const reference of index.field_refs) if (reference.startsWith(prefix) && !fields.has(reference.slice(prefix.length))) fields.set(reference.slice(prefix.length), freeze({ type: "TEXT", required: false }));
    }
    for (const name of primary) if (!fields.has(name)) fields.set(name, freeze({ type: "TEXT", required: true }));
    if (fields.size === 0) fail("DS_PROVIDER_MIGRATION_EMPTY_MODEL", `/persistence/physical_models/${model.model_id}`, "physical model has no resolvable fields");
    const columns = [...fields].sort(([left], [right]) => left.localeCompare(right)).map(([name, definition]) => ({ name, ...definition, primary: primary.has(name) }));
    return { id: model.model_id, name: model.physical_name, columns, indexes: item.index_mappings.filter(index => index.model_ref === model.model_id), relations: item.relation_mappings.filter(relation => relation.source_field_ref.startsWith(prefix)) };
  })).sort((left, right) => left.name.localeCompare(right.name));
  type ProviderTable = typeof domainTables[number];
  const infrastructureTables: ProviderTable[] = [];
  if (source.messaging.publication_bindings.length > 0 || source.persistence.transaction_guarantees.some(transaction => transaction.participant_refs.includes("participant:outbox-row"))) infrastructureTables.push({
    id: "physical-model:domainspec-outbox", name: "domainspec_outbox",
    columns: [
      { name: "id", type: "TEXT", required: true, primary: true },
      { name: "publication_id", type: "TEXT", required: true, primary: false },
      { name: "message_type_ref", type: "TEXT", required: true, primary: false },
      { name: "channel_ref", type: "TEXT", required: true, primary: false },
      { name: "payload", type: "JSONB", required: true, primary: false },
      { name: "status", type: "TEXT", required: true, primary: false },
      { name: "created_at", type: "TIMESTAMP WITH TIME ZONE", required: true, primary: false },
      { name: "accepted_at", type: "TIMESTAMP WITH TIME ZONE", required: false, primary: false },
    ],
    indexes: [{ index_id: "index:domainspec-outbox-pending", model_ref: "physical-model:domainspec-outbox", physical_name: "domainspec_outbox_pending_idx", field_refs: ["physical:domainspec-outbox/status", "physical:domainspec-outbox/created_at"], unique: false, order: "ordered" }],
    relations: [],
  });
  if (source.messaging.subscription_bindings.length > 0) infrastructureTables.push({
    id: "physical-model:domainspec-inbox", name: "domainspec_inbox",
    columns: [
      { name: "id", type: "TEXT", required: true, primary: true },
      { name: "subscription_id", type: "TEXT", required: true, primary: false },
      { name: "message_type_ref", type: "TEXT", required: true, primary: false },
      { name: "channel_ref", type: "TEXT", required: true, primary: false },
      { name: "payload", type: "JSONB", required: true, primary: false },
      { name: "received_at", type: "TIMESTAMP WITH TIME ZONE", required: true, primary: false },
      { name: "completed_at", type: "TIMESTAMP WITH TIME ZONE", required: false, primary: false },
    ],
    indexes: [{ index_id: "index:domainspec-inbox-subscription", model_ref: "physical-model:domainspec-inbox", physical_name: "domainspec_inbox_subscription_idx", field_refs: ["physical:domainspec-inbox/subscription_id", "physical:domainspec-inbox/id"], unique: true, order: "ordered" }],
    relations: [],
  });
  if (source.messaging.channels.some(channel => channel.channel_kind === "dead-letter")) infrastructureTables.push({
    id: "physical-model:domainspec-dead-letter", name: "domainspec_dead_letter",
    columns: [
      { name: "id", type: "TEXT", required: true, primary: true },
      { name: "source_channel_ref", type: "TEXT", required: true, primary: false },
      { name: "message_type_ref", type: "TEXT", required: true, primary: false },
      { name: "payload", type: "JSONB", required: true, primary: false },
      { name: "failure_class", type: "TEXT", required: true, primary: false },
      { name: "failed_at", type: "TIMESTAMP WITH TIME ZONE", required: true, primary: false },
      { name: "redriven_at", type: "TIMESTAMP WITH TIME ZONE", required: false, primary: false },
    ],
    indexes: [{ index_id: "index:domainspec-dead-letter-channel", model_ref: "physical-model:domainspec-dead-letter", physical_name: "domainspec_dead_letter_channel_idx", field_refs: ["physical:domainspec-dead-letter/source_channel_ref", "physical:domainspec-dead-letter/failed_at"], unique: false, order: "ordered" }],
    relations: [],
  });
  const tables = [...domainTables, ...infrastructureTables].sort((left, right) => left.name.localeCompare(right.name));
  const duplicate = tables.find((table, index) => tables.findIndex(candidate => candidate.name === table.name) !== index);
  if (duplicate) fail("DS_PROVIDER_MIGRATION_MODEL_COLLISION", "/persistence/physical_models", `duplicate physical table:${duplicate.name}`);
  const tableStatements = tables.map(table => {
    const definitions = table.columns.map(column => `${quoteSqlIdentifier(column.name)} ${column.type}${column.primary ? " PRIMARY KEY" : column.required ? " NOT NULL" : ""}`);
    return `CREATE TABLE IF NOT EXISTS ${quoteSqlIdentifier(table.name)} (${definitions.join(", ")});`;
  });
  const constraintRows = tables.flatMap(table => table.relations.map(relation => {
    const target = tables.find(candidate => candidate.id === relation.target_model_ref)!;
    const sourcePrefix = `physical:${table.id.replace(/^physical-model:/, "")}/`;
    const targetPrefix = `physical:${target.id.replace(/^physical-model:/, "")}/`;
    const sourceColumn = relation.source_field_ref.slice(sourcePrefix.length);
    const targetColumn = relation.target_field_ref.slice(targetPrefix.length);
    const name = `domainspec_fk_${sha256(canonicalJson(relation)).slice(0, 16)}`;
    return { name, table: table.name, sourceColumn, target: target.name, targetColumn };
  })).sort((left, right) => left.name.localeCompare(right.name));
  const constraintStatements = constraintRows.map(row => `DO $$BEGIN IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname=${quoteSqlString(row.name)} AND conrelid=to_regclass(${quoteSqlString(row.table)})) THEN ALTER TABLE ${quoteSqlIdentifier(row.table)} ADD CONSTRAINT ${quoteSqlIdentifier(row.name)} FOREIGN KEY (${quoteSqlIdentifier(row.sourceColumn)}) REFERENCES ${quoteSqlIdentifier(row.target)} (${quoteSqlIdentifier(row.targetColumn)}); END IF; END$$;`);
  const indexRows = tables.flatMap(table => table.indexes.map(index => ({ table, index }))).sort((left, right) => left.index.index_id.localeCompare(right.index.index_id));
  const indexStatements = indexRows.map(({ table, index }) => {
    const prefix = `physical:${table.id.replace(/^physical-model:/, "")}/`;
    const columns = index.field_refs.map(reference => {
      if (!reference.startsWith(prefix)) fail("DS_PROVIDER_MIGRATION_INDEX", `/persistence/index_mappings/${index.index_id}`, "index field does not belong to its physical model");
      return quoteSqlIdentifier(reference.slice(prefix.length));
    });
    return `CREATE ${index.unique ? "UNIQUE " : ""}INDEX IF NOT EXISTS ${quoteSqlIdentifier(index.physical_name)} ON ${quoteSqlIdentifier(table.name)} (${columns.join(", ")});`;
  });
  const migrationIds = source.persistence.migrations.map(item => item.migration_id).sort();
  const statements = [
    "BEGIN;",
    "CREATE TABLE IF NOT EXISTS domainspec_migrations (id TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);",
    ...tableStatements,
    ...constraintStatements,
    ...indexStatements,
    ...migrationIds.map(id => `INSERT INTO domainspec_migrations (id) VALUES (${quoteSqlString(id)}) ON CONFLICT (id) DO NOTHING;`),
    "COMMIT;",
  ];
  const sql = `${statements.join("\n")}\n`;
  const verificationSql = `${tables.map(table => {
    const expected = table.columns.map(column => `(${quoteSqlString(column.name)},${quoteSqlString(column.type.toLowerCase())},${quoteSqlString(column.primary || column.required ? "NO" : "YES")})`).join(",");
    return `DO $$BEGIN IF to_regclass(${quoteSqlString(table.name)}) IS NULL THEN RAISE EXCEPTION 'missing table: ${table.name}'; END IF; IF EXISTS (SELECT * FROM (VALUES ${expected}) AS expected(column_name,data_type,is_nullable) EXCEPT SELECT column_name,data_type,is_nullable FROM information_schema.columns WHERE table_schema=current_schema() AND table_name=${quoteSqlString(table.name)}) THEN RAISE EXCEPTION 'column contract mismatch: ${table.name}'; END IF; END$$;`;
  }).join("\n")}\n${constraintRows.map(row => `DO $$BEGIN IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname=${quoteSqlString(row.name)} AND conrelid=to_regclass(${quoteSqlString(row.table)}) AND contype='f') THEN RAISE EXCEPTION 'foreign key contract mismatch: ${row.name}'; END IF; END$$;`).join("\n")}\n${indexRows.map(({ index }) => `DO $$BEGIN IF to_regclass(${quoteSqlString(index.physical_name)}) IS NULL THEN RAISE EXCEPTION 'missing index: ${index.physical_name}'; END IF; END$$;`).join("\n")}\n${migrationIds.map(id => `DO $$BEGIN IF NOT EXISTS (SELECT 1 FROM domainspec_migrations WHERE id=${quoteSqlString(id)}) THEN RAISE EXCEPTION 'missing migration ledger row: ${id}'; END IF; END$$;`).join("\n")}\n`;
  const manifest = `${canonicalJson({ schema_version: "domainspec.provider-migration-manifest/v1-candidate", source_migrations: migrationIds, physical_models: tables.map(table => table.name), forward_sql: "migrations/0001_domainspec_reference.sql", verification_sql: "migrations/0001_domainspec_reference.verify.sql", execution: "deferred", transactional: true, dependency_order: "tables-before-foreign-keys", runtime_guarantees_observed: false, authority_effect: "none" })}\n`;
  return freeze({ sql, verification_sql: verificationSql, manifest });
}

function genericTypescriptArtifacts(selection: ProviderPackSelectionV1, destinationEnvironmentName: string, migration: ProviderMigrationArtifacts, failures: Readonly<Record<string, string>>, whole: WholeApplicationPlanV1, source: IntegrationGenerationSourceV2): readonly PlannedArtifact[] {
  const graph = runtimeGraphContracts(whole);
  const endpoints = source.external_api.inbound_endpoint_bindings;
  if (endpoints.length !== 1) fail("DS_PROVIDER_INBOUND_CARDINALITY", "/external_api/inbound_endpoint_bindings", "reference provider generator currently requires one inbound endpoint");
  const endpoint = endpoints[0]!;
  const binding = (mappingRef: string, direction: ProviderRuntimeGraphContracts["mapping_bindings"][number]["direction"]) => {
    const rows = graph.mapping_bindings.filter(row => row.mapping_ref === mappingRef && row.direction === direction);
    if (rows.length !== 1) fail("DS_PROVIDER_RUNTIME_MAPPING", `/application_graph/runtime_bindings/${mappingRef}`, `expected one ${direction} runtime Mapping binding`);
    return rows[0]!;
  };
  const request = binding(endpoint.request_mapper_ref, "protocol-to-application");
  const response = binding(endpoint.response_mapper_ref, "application-to-protocol");
  const subscriptions = source.messaging.subscription_bindings.map(item => ({ item, request: binding(item.mapper_ref, "message-to-application") }));
  const publications = source.messaging.publication_bindings.map(item => ({ item, mapping: binding(item.mapper_ref, "logical-to-message") }));
  if (publications.length !== 1) fail("DS_PROVIDER_PUBLICATION_CARDINALITY", "/messaging/publication_bindings", "reference provider generator currently requires one publication binding");
  const publication = publications[0]!;
  const packageJson = { name: "domainspec-generated-reference-application", version: "0.0.0", private: true, type: "module",
    scripts: { start: "tsc --noEmit false --outDir dist && node dist/providers/reference/main.js" }, engines: { node: REFERENCE_PROVIDER_RUNTIME.typescript.node },
    dependencies: { nats: selection.providers.messaging.version, pg: selection.providers.persistence.version }, devDependencies: { "@types/node": "26.6.0", "@types/pg": "8.23.1", typescript: "7.0.2" } };
  const config = `export interface ReferenceConfiguration { ${selection.configuration.environment.map(item => `readonly ${item.name}:string;`).join(" ")} }\nconst REQUIRED=${canonicalJson(selection.configuration.environment.map(item => item.name))} as const;\nexport function decodeReferenceConfiguration(environment:Readonly<Record<string,string|undefined>>):ReferenceConfiguration { const missing=REQUIRED.filter(name=>!environment[name]); if(missing.length)throw new Error(\`PROVIDER_CONFIGURATION_MISSING:\${missing.join(",")}\`); return Object.freeze(Object.fromEntries(REQUIRED.map(name=>[name,environment[name]!])) as unknown as ReferenceConfiguration); }\n`;
  const persistence = `import type {Pool,PoolClient} from "pg";
import {REFERENCE_MIGRATION_SQL} from "./migration.js";
const CONNECTION_FAILURE=${JSON.stringify(providerFailureCode(failures, "postgresql:connection-unavailable"))};
const UNIQUE_FAILURE=${JSON.stringify(providerFailureCode(failures, "postgresql:unique-violation"))};
export interface ProviderBatch {readonly writes:readonly Readonly<{target:string;mode:string;value:unknown}>[];readonly events:readonly Readonly<{target:string;value:unknown}>[];}
export interface ProviderTransaction {read(request:Readonly<{target:string;key:unknown}>):Promise<unknown>;querySource(request:Readonly<{target:string}>):Promise<readonly unknown[]>;commit(batch:ProviderBatch):Promise<Readonly<{status:"committed"|"rejected"|"indeterminate"}>>;rollback():Promise<void>;}
function failure(error:unknown):Error{return new Error((error as {code?:unknown})?.code==="23505"?UNIQUE_FAILURE:CONNECTION_FAILURE);}
class Postgresql16Transaction implements ProviderTransaction {private settled=false;constructor(private readonly client:PoolClient){}
async read(_request:Readonly<{target:string;key:unknown}>):Promise<unknown>{throw new Error("PROVIDER_KEYED_READ_NOT_OBSERVED");}
async querySource(_request:Readonly<{target:string}>):Promise<readonly unknown[]>{throw new Error("PROVIDER_QUERY_NOT_OBSERVED");}
async commit(batch:ProviderBatch):Promise<Readonly<{status:"committed"|"rejected"|"indeterminate"}>>{if(this.settled)return Object.freeze({status:"indeterminate"});if(batch.writes.length||batch.events.length){try{await this.client.query("ROLLBACK");this.settled=true;this.client.release();return Object.freeze({status:"rejected"});}catch{this.settled=true;this.client.release();return Object.freeze({status:"indeterminate"});}}try{await this.client.query("COMMIT");this.settled=true;this.client.release();return Object.freeze({status:"committed"});}catch{this.settled=true;this.client.release();return Object.freeze({status:"indeterminate"});}}
async rollback():Promise<void>{if(this.settled)return;try{await this.client.query("ROLLBACK");}finally{this.settled=true;this.client.release();}}}
export class Postgresql16ApplicationStore {constructor(private readonly pool:Pool){}async begin():Promise<ProviderTransaction>{const client=await this.pool.connect();try{await client.query("BEGIN");return new Postgresql16Transaction(client);}catch(error){client.release();throw failure(error);}}async migrate():Promise<void>{try{await this.pool.query(REFERENCE_MIGRATION_SQL);}catch(error){throw failure(error);}}}
`;
  const messageArguments = publication.mapping.inputs.map(input => `${JSON.stringify(input.parameter)}:readPath(event,${JSON.stringify(input.source.path)})`).join(",");
  const messaging = `import {headers,type JetStreamClient} from "nats";import type {Pool} from "pg";import {RUNTIME_MAPPING_INVOCATIONS} from "../../integrations/runtime-bindings.js";
const THROTTLED_FAILURE=${JSON.stringify(providerFailureCode(failures, "broker:throttled"))};const ACCEPTANCE_BOUNDARY=${JSON.stringify(source.messaging.producer_acceptance_boundaries.find(item => item.boundary_id === publication.item.producer_acceptance_boundary_ref)!.boundary_id)};
const invoke=(RUNTIME_MAPPING_INVOCATIONS as unknown as Readonly<Record<string,(value:Readonly<Record<string,unknown>>)=>unknown>>)[${JSON.stringify(publication.mapping.binding_id)}]!;
function readPath(value:unknown,parts:readonly string[]):unknown{let current=value;for(const part of parts){if(current===null||typeof current!=="object")throw new TypeError("PROVIDER_MAPPING_PATH");current=(current as Record<string,unknown>)[part];}return current;}
const jsonValue=(value:unknown):unknown=>JSON.parse(JSON.stringify(value,(_key,item)=>typeof item==="bigint"?item.toString():item));
export interface ProviderAcceptanceReceipt {readonly acceptance_boundary_ref:string;readonly provider_acknowledgement_ref:string;readonly claim_ceiling:"provider-accepted";readonly delivery_observed:false;readonly consumer_completion_observed:false;}
export class NatsJetStreamApplicationPublisher {constructor(private readonly connection:JetStreamClient,private readonly destination:string){}async publish(event:unknown):Promise<ProviderAcceptanceReceipt>{let id:unknown;try{id=readPath(event,["occurrence","event-id"]);}catch{throw new Error("PROVIDER_EVENT_ID_REQUIRED");}if(typeof id!=="string"||!id)throw new Error("PROVIDER_EVENT_ID_REQUIRED");try{const message=invoke({${messageArguments}});const metadata=headers();metadata.set("Nats-Msg-Id",id);const acknowledgement=await this.connection.publish(this.destination,new TextEncoder().encode(JSON.stringify(jsonValue(message))),{headers:metadata});return Object.freeze({acceptance_boundary_ref:ACCEPTANCE_BOUNDARY,provider_acknowledgement_ref:\`${'${acknowledgement.stream}:${acknowledgement.seq}'}\`,claim_ceiling:"provider-accepted",delivery_observed:false,consumer_completion_observed:false});}catch{throw new Error(THROTTLED_FAILURE);}}async publishPending(_pool:Pool):Promise<readonly ProviderAcceptanceReceipt[]>{throw new Error("PROVIDER_OUTBOX_DRAIN_NOT_OBSERVED");}}
`;
  const outbound = `const TIMEOUT_FAILURE=${JSON.stringify(providerFailureCode(failures, "http:timeout"))};const UNAUTHORIZED_FAILURE=${JSON.stringify(providerFailureCode(failures, "http:unauthorized"))};const MALFORMED_FAILURE=${JSON.stringify(providerFailureCode(failures, "http:malformed-response"))};export class FetchApplicationGateway {constructor(private readonly baseUrl:string){}async invoke(operation:string,input:unknown,idempotencyKey:string):Promise<unknown>{if(typeof idempotencyKey!=="string"||!idempotencyKey)throw new Error("PROVIDER_IDEMPOTENCY_KEY_REQUIRED");if(!/^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/.test(idempotencyKey))throw new Error("PROVIDER_IDEMPOTENCY_KEY_INVALID");let body:string;try{const serialized=JSON.stringify(input,(_key,value)=>typeof value==="bigint"?value.toString():value);if(typeof serialized!=="string")throw new TypeError("body");body=serialized;}catch{throw new Error("PROVIDER_REQUEST_SERIALIZATION_INVALID");}let response:Response;try{response=await fetch(new URL(operation,this.baseUrl),{method:"POST",headers:{"content-type":"application/json","Idempotency-Key":idempotencyKey},body});}catch{throw new Error(TIMEOUT_FAILURE);}if(response.status===401||response.status===403)throw new Error(UNAUTHORIZED_FAILURE);if(!response.ok)throw new Error(MALFORMED_FAILURE);try{return await response.json();}catch{throw new Error(MALFORMED_FAILURE);}}}\n`;
  const inbound = `import {createHmac,timingSafeEqual} from "node:crypto";import {createServer,type Server} from "node:http";const SIGNATURE_HEADER="x-domainspec-signature";export interface WebhookHandlerResult{readonly statusCode:number;readonly body?:unknown;}export type LifecycleStatus="starting"|"ready"|"stopping"|"stopped";const jsonValue=(value:unknown):unknown=>JSON.parse(JSON.stringify(value,(_key,item)=>typeof item==="bigint"?item.toString():item));export function isValidWebhookSignature(body:Uint8Array,signature:string|undefined,secret:string):boolean{if(signature===undefined||!/^[0-9a-fA-F]{64}$/.test(signature))return false;const expected=createHmac("sha256",secret).update(body).digest();const received=Buffer.from(signature,"hex");return received.length===expected.length&&timingSafeEqual(received,expected);}export function createWebhookServer(bindAddress:string,secret:string,onWebhook:(body:string)=>Promise<WebhookHandlerResult|void>,health:()=>LifecycleStatus=()=>"starting"):Server{void bindAddress;return createServer(async(request,response)=>{if(request.method==="GET"&&request.url==="/health"){const status=health();response.writeHead(status==="ready"?200:503,{"content-type":"application/json"}).end(JSON.stringify({status}));return;}if(request.method!=="POST"||request.url!=="/webhook"){response.writeHead(405).end();return;}const chunks:Buffer[]=[];let size=0;for await(const chunk of request){const bytes=Buffer.isBuffer(chunk)?chunk:Buffer.from(chunk);size+=bytes.length;if(size>65536){response.writeHead(413).end();return;}chunks.push(bytes);}const body=Buffer.concat(chunks);const header=request.headers[SIGNATURE_HEADER];const signature=typeof header==="string"?header:undefined;if(!isValidWebhookSignature(body,signature,secret)){response.writeHead(401).end();return;}try{const result=await onWebhook(body.toString("utf8"));if(result===undefined){response.writeHead(202).end();return;}response.writeHead(result.statusCode,{"content-type":"application/json"}).end(JSON.stringify(jsonValue(result.body)));}catch{response.writeHead(500).end();}});}export const INBOUND_BIND_ADDRESS_REFERENCE="INBOUND_BIND_ADDRESS";\n`;
  const responseArguments = response.inputs.map(input => `${JSON.stringify(input.parameter)}:readPath(outcome.value,${JSON.stringify(input.source.path)})`).join(",");
  const subscriptionMethods = subscriptions.map(({ item, request: subscription }) => `async handleMessage${item.subscription_id.replace(/[^A-Za-z0-9]+/g, "_")}(body:unknown):Promise<OperationOutcome>{return handler(${JSON.stringify(subscription.binding_id)})(body,Object.freeze({store:this.store}));}`).join("\n");
  const application = `import {APPLICATION_REQUEST_HANDLERS} from "../../integrations/application-request-handlers.js";import {RUNTIME_MAPPING_INVOCATIONS} from "../../integrations/runtime-bindings.js";import type {WebhookHandlerResult} from "./inbound-http.js";import type {Postgresql16ApplicationStore} from "./persistence.js";type OperationOutcome=Readonly<{status:string;value?:unknown;stage?:unknown;code?:unknown}>;type Handler=(body:unknown,dependencies:Readonly<{store:Postgresql16ApplicationStore}>)=>Promise<OperationOutcome>;const handlers=APPLICATION_REQUEST_HANDLERS as unknown as Readonly<Record<string,Handler>>;const mappings=RUNTIME_MAPPING_INVOCATIONS as unknown as Readonly<Record<string,(value:Readonly<Record<string,unknown>>)=>unknown>>;const handler=(id:string):Handler=>{const value=handlers[id];if(!value)throw new Error("PROVIDER_REQUEST_HANDLER_MISSING:"+id);return value;};function readPath(value:unknown,parts:readonly string[]):unknown{let current=value;for(const part of parts){if(current===null||typeof current!=="object")throw new TypeError("PROVIDER_MAPPING_PATH");current=(current as Record<string,unknown>)[part];}return current;}export class GeneratedApplicationRuntime{constructor(private readonly store:Postgresql16ApplicationStore){}async handleWebhook(body:unknown):Promise<WebhookHandlerResult>{const outcome=await handler(${JSON.stringify(request.binding_id)})(body,Object.freeze({store:this.store}));if(outcome.status!=="committed")return Object.freeze({statusCode:outcome.status==="rejected"?422:503,body:Object.freeze({status:outcome.status,stage:outcome.stage,code:outcome.code})});return Object.freeze({statusCode:200,body:mappings[${JSON.stringify(response.binding_id)}]!({${responseArguments}})});}${subscriptionMethods}}\n`;
  const bootstrap = `import type {Pool} from "pg";import type {JetStreamClient} from "nats";import {GeneratedApplicationRuntime} from "./application.js";import {Postgresql16ApplicationStore} from "./persistence.js";import {NatsJetStreamApplicationPublisher} from "./messaging.js";import {FetchApplicationGateway} from "./outbound-http.js";import {createWebhookServer,type LifecycleStatus} from "./inbound-http.js";import {decodeReferenceConfiguration} from "./configuration.js";export function composeReferenceApplication(environment:Readonly<Record<string,string|undefined>>,clients:{readonly database:Pool;readonly messaging:JetStreamClient;readonly onWebhook?:(body:string)=>Promise<void>;readonly health?:()=>LifecycleStatus}){const configuration=decodeReferenceConfiguration(environment);const health=clients.health??(()=>"starting" as const);const store=new Postgresql16ApplicationStore(clients.database);const application=new GeneratedApplicationRuntime(store);const publisher=new NatsJetStreamApplicationPublisher(clients.messaging,configuration.${destinationEnvironmentName});const outbound=new FetchApplicationGateway(configuration.PAYMENT_BASE_URL);const webhooks=createWebhookServer(configuration.INBOUND_BIND_ADDRESS,configuration.WEBHOOK_SECRET,async body=>{await clients.onWebhook?.(body);return application.handleWebhook(JSON.parse(body));},health);return Object.freeze({configuration,store,publisher,outbound,application,webhooks,migrate:()=>store.migrate(),flushOutbox:()=>publisher.publishPending(clients.database),health:()=>Object.freeze({status:health()})});}\n`;
  const entrypoint = `import type {Server} from "node:http";import {connect,type JetStreamClient,type NatsConnection} from "nats";import {Pool} from "pg";import {composeReferenceApplication} from "./bootstrap.js";import {decodeReferenceConfiguration} from "./configuration.js";import type {LifecycleStatus} from "./inbound-http.js";type RuntimeDatabase=Pool&{end():Promise<void>};export interface RuntimeConnectors{database(url:string):Promise<RuntimeDatabase>;messaging(url:string):Promise<Readonly<{connection:NatsConnection;jetstream:JetStreamClient}>>;listen(server:Server,address:string):Promise<void>;close(server:Server):Promise<void>;}export interface RunningReferenceApplication{readonly health:()=>Readonly<{status:LifecycleStatus}>;stop():Promise<void>;}function bindAddress(value:string){const parsed=new URL(\`http://\${value}\`);return Object.freeze({host:parsed.hostname,port:Number(parsed.port)});}const DEFAULT_CONNECTORS:RuntimeConnectors=Object.freeze({async database(url:string){const pool=new Pool({connectionString:url}) as RuntimeDatabase;await pool.query("SELECT 1");return pool;},async messaging(url:string){const connection=await connect({servers:url});return Object.freeze({connection,jetstream:connection.jetstream()});},async listen(server:Server,address:string){const {host,port}=bindAddress(address);await new Promise<void>((resolve,reject)=>{server.once("error",reject);server.listen(port,host,resolve);});},async close(server:Server){if(server.listening)await new Promise<void>((resolve,reject)=>server.close((error?:Error)=>error?reject(error):resolve()));}});export async function startReferenceApplication(environment:Readonly<Record<string,string|undefined>>,connectors:RuntimeConnectors=DEFAULT_CONNECTORS):Promise<RunningReferenceApplication>{const configuration=decodeReferenceConfiguration(environment);let status:LifecycleStatus="starting",database:RuntimeDatabase|undefined,nats:Readonly<{connection:NatsConnection;jetstream:JetStreamClient}>|undefined,server:Server|undefined;database=await connectors.database(configuration.DATABASE_URL);nats=await connectors.messaging(configuration.NATS_URL);const application=composeReferenceApplication(environment,{database,messaging:nats.jetstream,health:()=>status});server=application.webhooks;await application.migrate();await connectors.listen(server,configuration.INBOUND_BIND_ADDRESS);status="ready";return Object.freeze({health:()=>Object.freeze({status}),stop:async()=>{status="stopping";if(server)await connectors.close(server);if(nats)await nats.connection.drain();if(database)await database.end();status="stopped";}});}export async function runReferenceApplication(environment:Readonly<Record<string,string|undefined>>):Promise<void>{await startReferenceApplication(environment);}\n`;
  return Object.freeze([
    artifact("package.json", `${canonicalJson(packageJson)}\n`), artifact("package-lock.json", TYPESCRIPT_PROVIDER_PACKAGE_LOCK), artifact("src/providers/reference/configuration.ts", config), artifact("src/providers/reference/application.ts", application),
    artifact("src/providers/reference/migration.ts", `export const REFERENCE_MIGRATION_SQL=${JSON.stringify(migration.sql)} as const;\n`), artifact("src/providers/reference/persistence.ts", persistence), artifact("src/providers/reference/messaging.ts", messaging), artifact("src/providers/reference/outbound-http.ts", outbound), artifact("src/providers/reference/inbound-http.ts", inbound),
    artifact("src/providers/reference/bootstrap.ts", bootstrap), artifact("src/providers/reference/entrypoint.ts", entrypoint), artifact("src/providers/reference/main.ts", `import {runReferenceApplication} from "./entrypoint.js";runReferenceApplication(process.env).catch(error=>{console.error(error);process.exitCode=1;});\n`), artifact("migrations/0001_domainspec_reference.sql", migration.sql), artifact("migrations/0001_domainspec_reference.verify.sql", migration.verification_sql), artifact("migrations/manifest.json", migration.manifest), artifact(".domainspec/providers/failure-mappings.json", `${canonicalJson(failures)}\n`),
  ]);
}

function typescriptArtifacts(selection: ProviderPackSelectionV1, destinationEnvironmentName: string, migration: ProviderMigrationArtifacts, failures: Readonly<Record<string, string>>, whole: WholeApplicationPlanV1, source: IntegrationGenerationSourceV2): readonly PlannedArtifact[] {
  if (!whole.artifacts.some(item => item.relative_path === "src/features/commerce/application/operations/perform.ts")) return genericTypescriptArtifacts(selection, destinationEnvironmentName, migration, failures, whole, source);
  const packageJson = {
    name: "domainspec-generated-reference-application",
    version: "0.0.0",
    private: true,
    type: "module",
    scripts: { start: "tsc --noEmit false --outDir dist && node dist/providers/reference/main.js" },
    engines: { node: REFERENCE_PROVIDER_RUNTIME.typescript.node },
    dependencies: { nats: selection.providers.messaging.version, pg: selection.providers.persistence.version },
    devDependencies: { "@types/node": "26.6.0", "@types/pg": "8.23.1", typescript: "7.0.2" },
  };
  const config = `export interface ReferenceConfiguration { ${selection.configuration.environment.map(item => `readonly ${item.name}:string;`).join(" ")} }\nconst REQUIRED=${canonicalJson(selection.configuration.environment.map(item => item.name))} as const;\nexport function decodeReferenceConfiguration(environment:Readonly<Record<string,string|undefined>>):ReferenceConfiguration { const missing=REQUIRED.filter(name=>!environment[name]); if(missing.length)throw new Error(\`PROVIDER_CONFIGURATION_MISSING:\${missing.join(",")}\`); return Object.freeze(Object.fromEntries(REQUIRED.map(name=>[name,environment[name]!])) as unknown as ReferenceConfiguration); }\n`;
  const persistence = `import type {Pool,PoolClient} from "pg";
import type {OperationBatch,OperationDependencies,ReadRequest,Transaction} from "../../features/commerce/application/operations/perform.js";
import {REFERENCE_MIGRATION_SQL} from "./migration.js";
const CONNECTION_FAILURE=${JSON.stringify(providerFailureCode(failures, "postgresql:connection-unavailable"))};
const UNIQUE_FAILURE=${JSON.stringify(providerFailureCode(failures, "postgresql:unique-violation"))};
type OperationStore=OperationDependencies["store"];
const jsonValue=(value:unknown):unknown=>JSON.parse(JSON.stringify(value,(_key,item)=>typeof item==="bigint"?item.toString():item));
function persistenceFailure(error:unknown):Error{return new Error((error as {code?:unknown})?.code==="23505"?UNIQUE_FAILURE:CONNECTION_FAILURE);}
class Postgresql16Transaction implements Transaction {
  private settled=false;
  constructor(private readonly client:PoolClient){}
  async read(_request:ReadRequest):Promise<unknown>{throw new Error("READ_NOT_DECLARED");}
  async commit(batch:OperationBatch):Promise<Readonly<{status:"committed"|"rejected"|"indeterminate"}>>{
    if(this.settled)return Object.freeze({status:"indeterminate"});
    let commitAttempted=false;
    try{
      for(const write of batch.writes){
        const order=write.value;
        await this.client.query('INSERT INTO "customers" ("id","name") VALUES ($1,$2) ON CONFLICT ("id") DO UPDATE SET "name"=EXCLUDED."name"',[String(order.customer.id),order.customer.name]);
        await this.client.query('INSERT INTO "orders" ("id","customer-id","billing-customer-id","choice","labels","lines","money") VALUES ($1,$2,$3,$4,$5::jsonb,$6::jsonb,$7) ON CONFLICT ("id") DO UPDATE SET "customer-id"=EXCLUDED."customer-id","billing-customer-id"=EXCLUDED."billing-customer-id","choice"=EXCLUDED."choice","labels"=EXCLUDED."labels","lines"=EXCLUDED."lines","money"=EXCLUDED."money"',[String(order.id),String(order.customer.id),String(order.billing_customer_id),JSON.stringify(jsonValue(order.choice)),JSON.stringify(jsonValue(order.labels)),JSON.stringify(jsonValue(order.lines)),String(order.money.quantity)]);
        await this.client.query('DELETE FROM "order_tags" WHERE "order-id"=$1',[String(order.id)]);
        for(const tag of order.tags)await this.client.query('INSERT INTO "order_tags" ("order-id","tag") VALUES ($1,$2)',[String(order.id),tag]);
      }
      for(const event of batch.events)await this.client.query('INSERT INTO "domainspec_outbox" ("id","publication_id","message_type_ref","channel_ref","payload","status","created_at") VALUES ($1,$2,$3,$4,$5::jsonb,$6,$7)',[event.value.occurrence["event-id"],"publication:order-submitted","message-type:order-submitted-v1","channel:order-events-topic",JSON.stringify(jsonValue(event.value)),"pending",event.value.occurredAt]);
      commitAttempted=true;
      await this.client.query("COMMIT");
      this.settled=true;this.client.release();
      return Object.freeze({status:"committed"});
    }catch{
      if(commitAttempted){this.settled=true;this.client.release();return Object.freeze({status:"indeterminate"});}
      try{await this.client.query("ROLLBACK");}finally{this.settled=true;this.client.release();}
      return Object.freeze({status:"rejected"});
    }
  }
  async rollback():Promise<void>{if(this.settled)return;try{await this.client.query("ROLLBACK");}finally{this.settled=true;this.client.release();}}
}
export class Postgresql16OrderStore implements OperationStore {
  constructor(private readonly pool:Pool){}
  async begin():Promise<Transaction>{const client=await this.pool.connect();try{await client.query("BEGIN");return new Postgresql16Transaction(client);}catch(error){client.release();throw persistenceFailure(error);}}
  async migrate():Promise<void>{try{await this.pool.query(REFERENCE_MIGRATION_SQL);}catch(error){throw persistenceFailure(error);}}
}
`;
  const messaging = `import {headers,type JetStreamClient} from "nats";
import type {Pool} from "pg";
import type {EventIntent} from "../../features/commerce/application/operations/perform.js";
import type {ProviderAcceptanceReceipt} from "../../features/integration/application/contracts.js";
import {invokeMessageMappingOrderSubmittedOut} from "../../integrations/runtime-bindings.js";
const THROTTLED_FAILURE=${JSON.stringify(providerFailureCode(failures, "broker:throttled"))};
const ACCEPTANCE_BOUNDARY="acceptance:order-event-publish" as const;
type PostedEvent=EventIntent["value"];
const jsonValue=(value:unknown):unknown=>JSON.parse(JSON.stringify(value,(_key,item)=>typeof item==="bigint"?item.toString():item));
export class NatsJetStreamOrderPublisher {
  constructor(private readonly connection:JetStreamClient,private readonly destination:string){}
  async publish(event:PostedEvent):Promise<ProviderAcceptanceReceipt>{
    try{
      const message=invokeMessageMappingOrderSubmittedOut({order:event.payload["order-id"]});
      const metadata=headers();metadata.set("Nats-Msg-Id",event.occurrence["event-id"]);
      const acknowledgement=await this.connection.publish(this.destination,new TextEncoder().encode(JSON.stringify(jsonValue(message))),{headers:metadata});
      return Object.freeze({acceptance_boundary_ref:ACCEPTANCE_BOUNDARY,provider_acknowledgement_ref:\`${'${acknowledgement.stream}:${acknowledgement.seq}'}\`,claim_ceiling:"provider-accepted",delivery_observed:false,consumer_completion_observed:false});
    }catch{throw new Error(THROTTLED_FAILURE);}
  }
  async publishPending(pool:Pool,limit=100):Promise<readonly ProviderAcceptanceReceipt[]>{
    const client=await pool.connect();
    try{
      await client.query("BEGIN");
      const selected=await client.query<{id:string;payload:PostedEvent}>('SELECT "id","payload" FROM "domainspec_outbox" WHERE "status"=$1 ORDER BY "created_at","id" FOR UPDATE SKIP LOCKED LIMIT $2',["pending",limit]);
      const receipts:ProviderAcceptanceReceipt[]=[];
      for(const row of selected.rows){const event=(typeof row.payload==="string"?JSON.parse(row.payload):row.payload) as PostedEvent;const receipt=await this.publish(event);await client.query('UPDATE "domainspec_outbox" SET "status"=$1,"accepted_at"=CURRENT_TIMESTAMP WHERE "id"=$2',["accepted",row.id]);receipts.push(receipt);}
      await client.query("COMMIT");
      return Object.freeze(receipts);
    }catch(error){await client.query("ROLLBACK");throw error;}
    finally{client.release();}
  }
}
`;
  const outbound = `import type {OperationValue} from "../../features/commerce/application/operations/perform.js";
import {invokeApiMappingAuthorizeRequest,invokeApiMappingAuthorizeResponse} from "../../integrations/runtime-bindings.js";
const TIMEOUT_FAILURE=${JSON.stringify(providerFailureCode(failures, "http:timeout"))};
const UNAUTHORIZED_FAILURE=${JSON.stringify(providerFailureCode(failures, "http:unauthorized"))};
const MALFORMED_FAILURE=${JSON.stringify(providerFailureCode(failures, "http:malformed-response"))};
const jsonValue=(value:unknown):unknown=>JSON.parse(JSON.stringify(value,(_key,item)=>typeof item==="bigint"?item.toString():item));
export class FetchPaymentGateway {
  constructor(private readonly baseUrl:string){}
  async authorize(input:OperationValue):Promise<OperationValue>{
    const requestBody=invokeApiMappingAuthorizeRequest({order:input.id});
    let response:Response;
    try{response=await fetch(new URL("/authorize",this.baseUrl),{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(jsonValue(requestBody))});}catch{throw new Error(TIMEOUT_FAILURE);}
    if(response.status===401||response.status===403)throw new Error(UNAUTHORIZED_FAILURE);
    if(!response.ok)throw new Error(MALFORMED_FAILURE);
    try{return invokeApiMappingAuthorizeResponse({amount:await response.json()});}catch{throw new Error(MALFORMED_FAILURE);}
  }
}
`;
  const inbound = `import {createHmac,timingSafeEqual} from "node:crypto";
import {createServer,type Server} from "node:http";
const SIGNATURE_HEADER="x-domainspec-signature";
export interface WebhookHandlerResult { readonly statusCode:number; readonly body?:unknown; }
export type LifecycleStatus="starting"|"ready"|"stopping"|"stopped";
const jsonValue=(value:unknown):unknown=>JSON.parse(JSON.stringify(value,(_key,item)=>typeof item==="bigint"?item.toString():item));
export function isValidWebhookSignature(body:Uint8Array,signature:string|undefined,secret:string):boolean{if(signature===undefined||!/^[0-9a-fA-F]{64}$/.test(signature))return false;const expected=createHmac("sha256",secret).update(body).digest();const received=Buffer.from(signature,"hex");return received.length===expected.length&&timingSafeEqual(received,expected);}
export function createWebhookServer(bindAddress:string,secret:string,onWebhook:(body:string)=>Promise<WebhookHandlerResult|void>,health:()=>LifecycleStatus=()=>"starting"):Server{void bindAddress;return createServer(async(request,response)=>{if(request.method==="GET"&&request.url==="/health"){const status=health();response.writeHead(status==="ready"?200:503,{"content-type":"application/json"}).end(JSON.stringify({status}));return;}if(request.method!=="POST"||request.url!=="/webhook"){response.writeHead(405).end();return;}const chunks:Buffer[]=[];for await(const chunk of request)chunks.push(Buffer.isBuffer(chunk)?chunk:Buffer.from(chunk));const body=Buffer.concat(chunks);const header=request.headers[SIGNATURE_HEADER];const signature=typeof header==="string"?header:undefined;if(!isValidWebhookSignature(body,signature,secret)){response.writeHead(401).end();return;}try{const result=await onWebhook(body.toString("utf8"));if(result===undefined){response.writeHead(202).end();return;}response.writeHead(result.statusCode,{"content-type":"application/json"}).end(JSON.stringify(jsonValue(result.body)));}catch{response.writeHead(500).end();}});}
export const INBOUND_BIND_ADDRESS_REFERENCE=bindAddressReference();
function bindAddressReference():string{return "INBOUND_BIND_ADDRESS";}
`;
  const application = `import type {OperationOutcome} from "../../features/commerce/application/operations/perform.js";
import {APPLICATION_REQUEST_HANDLERS} from "../../integrations/application-request-handlers.js";
import {invokeApiMappingPaymentWebhookResponse} from "../../integrations/runtime-bindings.js";
import type {WebhookHandlerResult} from "./inbound-http.js";
import type {Postgresql16OrderStore} from "./persistence.js";
function operationFailure(outcome:Exclude<OperationOutcome,{status:"committed"}>):WebhookHandlerResult{return Object.freeze({statusCode:outcome.status==="rejected"?422:503,body:Object.freeze({status:outcome.status,stage:outcome.stage,code:outcome.code})});}
export class CommerceApplicationRuntime {
  constructor(private readonly store:Postgresql16OrderStore){}
  async handleWebhook(body:unknown):Promise<WebhookHandlerResult>{const outcome=await APPLICATION_REQUEST_HANDLERS["api-mapping:payment-webhook-request"](body,Object.freeze({store:this.store}));return outcome.status==="committed"?Object.freeze({statusCode:200,body:invokeApiMappingPaymentWebhookResponse({order:outcome.value})}):operationFailure(outcome);}
  async handleOrderSubmittedMessage(body:unknown):Promise<OperationOutcome>{return APPLICATION_REQUEST_HANDLERS["message-mapping:order-submitted-in"](body,Object.freeze({store:this.store}));}
}
`;
  const bootstrap = `import type {Pool} from "pg";
import type {JetStreamClient} from "nats";
import {CommerceApplicationRuntime} from "./application.js";
import {Postgresql16OrderStore} from "./persistence.js";
import {NatsJetStreamOrderPublisher} from "./messaging.js";
import {FetchPaymentGateway} from "./outbound-http.js";
import {createWebhookServer,type LifecycleStatus} from "./inbound-http.js";
import {decodeReferenceConfiguration} from "./configuration.js";
export function composeReferenceApplication(environment:Readonly<Record<string,string|undefined>>,clients:{readonly database:Pool;readonly messaging:JetStreamClient;readonly onWebhook?:(body:string)=>Promise<void>;readonly health?:()=>LifecycleStatus}){const configuration=decodeReferenceConfiguration(environment);const health=clients.health??(()=>"starting" as const);const store=new Postgresql16OrderStore(clients.database);const application=new CommerceApplicationRuntime(store);const publisher=new NatsJetStreamOrderPublisher(clients.messaging,configuration.${destinationEnvironmentName});const payments=new FetchPaymentGateway(configuration.PAYMENT_BASE_URL);const webhooks=createWebhookServer(configuration.INBOUND_BIND_ADDRESS,configuration.WEBHOOK_SECRET,async body=>{await clients.onWebhook?.(body);return application.handleWebhook(JSON.parse(body));},health);return Object.freeze({configuration,store,publisher,payments,application,webhooks,migrate:()=>store.migrate(),flushOutbox:()=>publisher.publishPending(clients.database),health:()=>Object.freeze({status:health()})});}
`;
  const entrypoint = `import type {Server} from "node:http";
import {connect,type JetStreamClient,type NatsConnection} from "nats";
import {Pool} from "pg";
import {composeReferenceApplication} from "./bootstrap.js";
import {decodeReferenceConfiguration} from "./configuration.js";
import type {LifecycleStatus} from "./inbound-http.js";
type RuntimeDatabase=Pool&{end():Promise<void>};
export interface RuntimeConnectors { database(url:string):Promise<RuntimeDatabase>; messaging(url:string):Promise<Readonly<{connection:NatsConnection;jetstream:JetStreamClient}>>; listen(server:Server,address:string):Promise<void>; close(server:Server):Promise<void>; }
export interface RunningReferenceApplication { readonly health:()=>Readonly<{status:LifecycleStatus}>; stop():Promise<void>; }
function bindAddress(value:string):Readonly<{host:string;port:number}>{const parsed=new URL(\`http://\${value}\`);const port=Number(parsed.port);if(!parsed.hostname||!Number.isInteger(port)||port<0||port>65535)throw new Error("PROVIDER_BIND_ADDRESS_INVALID");return Object.freeze({host:parsed.hostname,port});}
const DEFAULT_CONNECTORS:RuntimeConnectors=Object.freeze({
  async database(url:string){const pool=new Pool({connectionString:url}) as RuntimeDatabase;try{await pool.query("SELECT 1");return pool;}catch(error){await pool.end();throw error;}},
  async messaging(url:string){const connection=await connect({servers:url});return Object.freeze({connection,jetstream:connection.jetstream()});},
  async listen(server:Server,address:string){const {host,port}=bindAddress(address);await new Promise<void>((resolve,reject)=>{const onError=(error:Error)=>{server.off("listening",onListening);reject(error);};const onListening=()=>{server.off("error",onError);resolve();};server.once("error",onError);server.once("listening",onListening);server.listen(port,host);});},
  async close(server:Server){if(!server.listening)return;await new Promise<void>((resolve,reject)=>server.close((error?:Error)=>error?reject(error):resolve()));},
});
export async function startReferenceApplication(environment:Readonly<Record<string,string|undefined>>,connectors:RuntimeConnectors=DEFAULT_CONNECTORS):Promise<RunningReferenceApplication>{
  const configuration=decodeReferenceConfiguration(environment);let status:LifecycleStatus="starting";let database:RuntimeDatabase|undefined;let nats:Readonly<{connection:NatsConnection;jetstream:JetStreamClient}>|undefined;let server:Server|undefined;let stopped=false;
  const health=()=>status;
  const cleanup=async()=>{if(stopped)return;stopped=true;status="stopping";const failures:unknown[]=[];if(server)try{await connectors.close(server);}catch(error){failures.push(error);}if(nats)try{await nats.connection.drain();}catch(error){failures.push(error);}if(database)try{await database.end();}catch(error){failures.push(error);}status="stopped";if(failures.length)throw new AggregateError(failures,"PROVIDER_SHUTDOWN_FAILED");};
  try{database=await connectors.database(configuration.DATABASE_URL);nats=await connectors.messaging(configuration.NATS_URL);const application=composeReferenceApplication(environment,{database,messaging:nats.jetstream,health});server=application.webhooks;await application.migrate();await connectors.listen(server,configuration.INBOUND_BIND_ADDRESS);status="ready";return Object.freeze({health:()=>Object.freeze({status}),stop:cleanup});}catch(error){try{await cleanup();}catch(cleanupError){throw new AggregateError([error,cleanupError],"PROVIDER_STARTUP_FAILED");}throw error;}
}
export async function runReferenceApplication(environment:Readonly<Record<string,string|undefined>>):Promise<void>{const running=await startReferenceApplication(environment);await new Promise<void>((resolve,reject)=>{let requested=false;const stop=()=>{if(requested)return;requested=true;void running.stop().then(resolve,reject);};process.once("SIGINT",stop);process.once("SIGTERM",stop);});}
`;
  const main = `import {runReferenceApplication} from "./entrypoint.js";
runReferenceApplication(process.env).catch(error=>{console.error(error);process.exitCode=1;});
`;
  return Object.freeze([
    artifact("package.json", `${canonicalJson(packageJson)}\n`),
    artifact("package-lock.json", TYPESCRIPT_PROVIDER_PACKAGE_LOCK),
    artifact("src/providers/reference/configuration.ts", config),
    artifact("src/providers/reference/application.ts", application),
    artifact("src/providers/reference/migration.ts", `export const REFERENCE_MIGRATION_SQL=${JSON.stringify(migration.sql)} as const;\n`),
    artifact("src/providers/reference/persistence.ts", persistence),
    artifact("src/providers/reference/messaging.ts", messaging),
    artifact("src/providers/reference/outbound-http.ts", outbound),
    artifact("src/providers/reference/inbound-http.ts", inbound),
    artifact("src/providers/reference/bootstrap.ts", bootstrap),
    artifact("src/providers/reference/entrypoint.ts", entrypoint),
    artifact("src/providers/reference/main.ts", main),
    artifact("migrations/0001_domainspec_reference.sql", migration.sql),
    artifact("migrations/0001_domainspec_reference.verify.sql", migration.verification_sql),
    artifact("migrations/manifest.json", migration.manifest),
    artifact(".domainspec/providers/failure-mappings.json", `${canonicalJson(failures)}\n`),
  ]);
}

function pythonArtifacts(selection: ProviderPackSelectionV1, destinationEnvironmentName: string, packageRoot: string, migration: ProviderMigrationArtifacts, failures: Readonly<Record<string, string>>): readonly PlannedArtifact[] {
  const dependencies = [`psycopg[binary]==${selection.providers.persistence.version}`, `nats-py==${selection.providers.messaging.version}`, `httpx==${selection.providers.outbound_http.version}`, `starlette==${selection.providers.inbound_http.version}`, "uvicorn==0.53.0"];
  const pyproject = `[build-system]\nrequires = ["setuptools==80.9.0"]\nbuild-backend = "setuptools.build_meta"\n\n[project]\nname = "domainspec-generated-reference-application"\nversion = "0.0.0"\nrequires-python = "${REFERENCE_PROVIDER_RUNTIME.python.python}"\ndependencies = [${dependencies.map(value => JSON.stringify(value)).join(", ")}]\n\n[project.scripts]\ndomainspec-application = "${packageRoot}.providers.reference.main:main"\n`;
  const prefix = `src/${packageRoot}/providers/reference`;
  const config = `from dataclasses import dataclass\nfrom typing import Mapping\n\n_REQUIRED = ${JSON.stringify(selection.configuration.environment.map(item => item.name))}\n@dataclass(frozen=True, slots=True)\nclass ReferenceConfiguration:\n${selection.configuration.environment.map(item => `    ${item.name}: str`).join("\n")}\n\ndef decode_reference_configuration(environment: Mapping[str, str]) -> ReferenceConfiguration:\n    missing = [name for name in _REQUIRED if not environment.get(name)]\n    if missing:\n        raise ValueError("PROVIDER_CONFIGURATION_MISSING:" + ",".join(missing))\n    return ReferenceConfiguration(**{name: environment[name] for name in _REQUIRED})\n`;
  const persistence = `from collections.abc import Mapping\nfrom dataclasses import asdict, is_dataclass\nfrom typing import Any\nimport json\nimport psycopg\nfrom psycopg.errors import UniqueViolation\nfrom .migration import REFERENCE_MIGRATION_SQL\n\nCONNECTION_FAILURE=${JSON.stringify(providerFailureCode(failures, "postgresql:connection-unavailable"))}\nUNIQUE_FAILURE=${JSON.stringify(providerFailureCode(failures, "postgresql:unique-violation"))}\n\ndef _json_value(value):\n    if is_dataclass(value):\n        return _json_value(asdict(value))\n    if isinstance(value, Mapping):\n        return {key: _json_value(item) for key, item in value.items()}\n    if hasattr(value, "entries"):\n        return {key: _json_value(item) for key, item in value.entries}\n    if isinstance(value, (list, tuple)):\n        return [_json_value(item) for item in value]\n    return value\n\ndef _failure(error):\n    return RuntimeError(UNIQUE_FAILURE if isinstance(error, UniqueViolation) or getattr(error, "sqlstate", None) == "23505" else CONNECTION_FAILURE)\n\nclass Postgresql16Transaction:\n    def __init__(self, connection):\n        self._connection = connection\n        self._settled = False\n    async def read(self, request):\n        raise RuntimeError("READ_NOT_DECLARED")\n    async def _execute(self, sql, parameters=()):\n        async with self._connection.cursor() as cursor:\n            await cursor.execute(sql, parameters)\n    async def commit(self, batch):\n        if self._settled:\n            return {"status": "indeterminate"}\n        commit_attempted = False\n        try:\n            for write in batch.writes:\n                order = write["value"]\n                await self._execute('INSERT INTO "customers" ("id","name") VALUES (%s,%s) ON CONFLICT ("id") DO UPDATE SET "name"=EXCLUDED."name"', (str(order["customer"]["id"]), order["customer"]["name"]))\n                await self._execute('INSERT INTO "orders" ("id","customer-id","billing-customer-id","choice","labels","lines","money") VALUES (%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s) ON CONFLICT ("id") DO UPDATE SET "customer-id"=EXCLUDED."customer-id","billing-customer-id"=EXCLUDED."billing-customer-id","choice"=EXCLUDED."choice","labels"=EXCLUDED."labels","lines"=EXCLUDED."lines","money"=EXCLUDED."money"', (str(order["id"]), str(order["customer"]["id"]), str(order["billing_customer_id"]), json.dumps(_json_value(order["choice"]), separators=(",", ":")), json.dumps(_json_value(order["labels"]), separators=(",", ":")), json.dumps(_json_value(order["lines"]), separators=(",", ":")), str(order["money"]["quantity"])))\n                await self._execute('DELETE FROM "order_tags" WHERE "order-id"=%s', (str(order["id"]),))\n                for tag in order["tags"]:\n                    await self._execute('INSERT INTO "order_tags" ("order-id","tag") VALUES (%s,%s)', (str(order["id"]), tag))\n            for event in batch.events:\n                value = event["value"]\n                await self._execute('INSERT INTO "domainspec_outbox" ("id","publication_id","message_type_ref","channel_ref","payload","status","created_at") VALUES (%s,%s,%s,%s,%s::jsonb,%s,%s)', (value.occurrence["event-id"], "publication:order-submitted", "message-type:order-submitted-v1", "channel:order-events-topic", json.dumps(_json_value(value), separators=(",", ":")), "pending", value.occurredAt))\n            commit_attempted = True\n            await self._execute("COMMIT")\n            self._settled = True\n            return {"status": "committed"}\n        except Exception:\n            if commit_attempted:\n                self._settled = True\n                return {"status": "indeterminate"}\n            try:\n                await self._execute("ROLLBACK")\n            finally:\n                self._settled = True\n            return {"status": "rejected"}\n    async def rollback(self):\n        if self._settled:\n            return\n        try:\n            await self._execute("ROLLBACK")\n        finally:\n            self._settled = True\n\nclass Postgresql16OrderStore:\n    def __init__(self, connection: psycopg.AsyncConnection[Any]):\n        self._connection = connection\n    async def begin(self):\n        try:\n            async with self._connection.cursor() as cursor:\n                await cursor.execute("BEGIN")\n            return Postgresql16Transaction(self._connection)\n        except Exception as error:\n            raise _failure(error) from None\n    async def migrate(self) -> None:\n        try:\n            async with self._connection.cursor() as cursor:\n                await cursor.execute(REFERENCE_MIGRATION_SQL)\n        except Exception as error:\n            raise _failure(error) from None\n`;
  const messaging = `from collections.abc import Mapping\nfrom dataclasses import asdict, is_dataclass\nimport json\nfrom nats.js.client import JetStreamContext\nfrom ${packageRoot}.integrations.runtime_bindings import invoke_message_mapping_order_submitted_out\n\nTHROTTLED_FAILURE=${JSON.stringify(providerFailureCode(failures, "broker:throttled"))}\nACCEPTANCE_BOUNDARY="acceptance:order-event-publish"\n\ndef _json_value(value):\n    if is_dataclass(value):\n        return _json_value(asdict(value))\n    if isinstance(value, Mapping):\n        return {key: _json_value(item) for key, item in value.items()}\n    if hasattr(value, "entries"):\n        return {key: _json_value(item) for key, item in value.entries}\n    if isinstance(value, (list, tuple)):\n        return [_json_value(item) for item in value]\n    return value\n\nclass NatsJetStreamOrderPublisher:\n    def __init__(self, connection: JetStreamContext, destination: str):\n        self._connection, self._destination = connection, destination\n    async def publish(self, event):\n        try:\n            message = invoke_message_mapping_order_submitted_out({"order": event.payload["order-id"]})\n            acknowledgement = await self._connection.publish(self._destination, json.dumps(_json_value(message), separators=(",", ":"), sort_keys=True).encode("utf-8"), headers={"Nats-Msg-Id": event.occurrence["event-id"]})\n        except Exception:\n            raise RuntimeError(THROTTLED_FAILURE) from None\n        return {"acceptance_boundary_ref": ACCEPTANCE_BOUNDARY, "provider_acknowledgement_ref": f"{acknowledgement.stream}:{acknowledgement.seq}", "claim_ceiling": "provider-accepted", "delivery_observed": False, "consumer_completion_observed": False}\n    async def publish_pending(self, connection, limit=100):\n        async with connection.cursor() as cursor:\n            try:\n                await cursor.execute("BEGIN")\n                await cursor.execute('SELECT "id","payload" FROM "domainspec_outbox" WHERE "status"=%s ORDER BY "created_at","id" FOR UPDATE SKIP LOCKED LIMIT %s', ("pending", limit))\n                rows = await cursor.fetchall()\n                receipts = []\n                for row in rows:\n                    event = row[1] if not isinstance(row[1], str) else json.loads(row[1])\n                    receipt = await self.publish(_event_value(event))\n                    await cursor.execute('UPDATE "domainspec_outbox" SET "status"=%s,"accepted_at"=CURRENT_TIMESTAMP WHERE "id"=%s', ("accepted", row[0]))\n                    receipts.append(receipt)\n                await cursor.execute("COMMIT")\n                return tuple(receipts)\n            except Exception:\n                await cursor.execute("ROLLBACK")\n                raise\n\ndef _event_value(value):\n    class Event:\n        pass\n    event = Event()\n    event.occurrence = value["occurrence"]\n    event.occurredAt = value["occurredAt"]\n    event.payload = value["payload"]\n    event.type = value["type"]\n    event.version = value["version"]\n    return event\n`;
  const outbound = `from collections.abc import Mapping\nfrom dataclasses import asdict, is_dataclass\nimport httpx\nfrom ${packageRoot}.integrations.runtime_bindings import invoke_api_mapping_authorize_request, invoke_api_mapping_authorize_response\n\nTIMEOUT_FAILURE=${JSON.stringify(providerFailureCode(failures, "http:timeout"))}\nUNAUTHORIZED_FAILURE=${JSON.stringify(providerFailureCode(failures, "http:unauthorized"))}\nMALFORMED_FAILURE=${JSON.stringify(providerFailureCode(failures, "http:malformed-response"))}\n\ndef _json_value(value):\n    if is_dataclass(value):\n        return _json_value(asdict(value))\n    if isinstance(value, Mapping):\n        return {key: _json_value(item) for key, item in value.items()}\n    if hasattr(value, "entries"):\n        return {key: _json_value(item) for key, item in value.entries}\n    if isinstance(value, (list, tuple)):\n        return [_json_value(item) for item in value]\n    return value\n\nclass HttpxPaymentGateway:\n    def __init__(self, client: httpx.AsyncClient, base_url: str):\n        self._client, self._base_url = client, base_url\n    async def authorize(self, input):\n        request_body = invoke_api_mapping_authorize_request({"order": input["id"]})\n        try:\n            response = await self._client.post(self._base_url + "/authorize", json=_json_value(request_body))\n        except httpx.TimeoutException:\n            raise RuntimeError(TIMEOUT_FAILURE) from None\n        except httpx.HTTPError:\n            raise RuntimeError(MALFORMED_FAILURE) from None\n        if response.status_code in (401, 403):\n            raise RuntimeError(UNAUTHORIZED_FAILURE)\n        if not response.is_success:\n            raise RuntimeError(MALFORMED_FAILURE)\n        try:\n            return invoke_api_mapping_authorize_response({"amount": response.json()})\n        except (TypeError, ValueError, KeyError):\n            raise RuntimeError(MALFORMED_FAILURE) from None\n`;
  const inbound = `from collections.abc import Mapping\nfrom dataclasses import asdict, is_dataclass\nimport hashlib\nimport hmac\nimport json\nimport re\nfrom starlette.applications import Starlette\nfrom starlette.requests import Request\nfrom starlette.responses import JSONResponse, Response\nfrom starlette.routing import Route\n\n_SIGNATURE_HEADER = "x-domainspec-signature"\ndef _json_value(value):\n    if is_dataclass(value):\n        return _json_value(asdict(value))\n    if isinstance(value, Mapping):\n        return {key: _json_value(item) for key, item in value.items()}\n    if hasattr(value, "entries"):\n        return {key: _json_value(item) for key, item in value.entries}\n    if isinstance(value, (list, tuple)):\n        return [_json_value(item) for item in value]\n    return value\n\ndef is_valid_webhook_signature(body: bytes, signature: str | None, secret: str) -> bool:\n    if signature is None or re.fullmatch(r"[0-9a-fA-F]{64}", signature) is None:\n        return False\n    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()\n    return hmac.compare_digest(expected, signature.lower())\n\ndef create_webhook_application(secret, on_webhook, health=lambda: "starting"):\n    async def webhook(request: Request) -> Response:\n        body = await request.body()\n        if not is_valid_webhook_signature(body, request.headers.get(_SIGNATURE_HEADER), secret):\n            return Response(status_code=401)\n        result = await on_webhook(body)\n        if result is None:\n            return Response(status_code=202)\n        content = json.dumps(_json_value(result.get("body")), separators=(",", ":")).encode("utf-8")\n        return Response(content=content, status_code=result["status_code"], media_type="application/json")\n    async def health_endpoint(_request: Request) -> Response:\n        status = health()\n        return JSONResponse({"status": status}, status_code=200 if status == "ready" else 503)\n    return Starlette(routes=[Route("/webhook", webhook, methods=["POST"]), Route("/health", health_endpoint, methods=["GET"])])\n`;
  const application = `from collections.abc import Mapping\nfrom ${packageRoot}.features.commerce.application.operations.perform import operation_perform\nfrom ${packageRoot}.integrations.runtime_bindings import invoke_api_mapping_payment_webhook_request, invoke_api_mapping_payment_webhook_response, invoke_message_mapping_order_submitted_in\n\ndef _plain(value):\n    if isinstance(value, Mapping):\n        return {key: _plain(item) for key, item in value.items()}\n    if hasattr(value, "entries"):\n        return {key: _plain(item) for key, item in value.entries}\n    if isinstance(value, (list, tuple)):\n        return [_plain(item) for item in value]\n    return value\n\ndef _source_record(value):\n    if type(value) is not dict or any(type(key) is not str for key in value):\n        raise TypeError("RUNTIME_SOURCE_BODY")\n    return value\n\ndef _request_from(source, amount):\n    return {"amount": _plain(amount), "notice_input": source["notice_input"]}\n\ndef _operation_failure(outcome):\n    return {"status_code": 422 if outcome.status == "rejected" else 503, "body": {"status": outcome.status, "stage": outcome.stage, "code": outcome.code}}\n\nclass CommerceApplicationRuntime:\n    def __init__(self, store):\n        self._store = store\n    async def handle_webhook(self, body):\n        source = _source_record(body)\n        amount = invoke_api_mapping_payment_webhook_request({"amount": source["amount"]})\n        outcome = await operation_perform(_request_from(source, amount), {"store": self._store})\n        if outcome.status != "committed":\n            return _operation_failure(outcome)\n        return {"status_code": 200, "body": invoke_api_mapping_payment_webhook_response({"order": outcome.value})}\n    async def handle_order_submitted_message(self, body):\n        source = _source_record(body)\n        amount = invoke_message_mapping_order_submitted_in({"amount": source["amount"]})\n        return await operation_perform(_request_from(source, amount), {"store": self._store})\n`;
  const bootstrap = `import json\nfrom .application import CommerceApplicationRuntime\nfrom .configuration import decode_reference_configuration\nfrom .persistence import Postgresql16OrderStore\nfrom .messaging import NatsJetStreamOrderPublisher\nfrom .outbound_http import HttpxPaymentGateway\nfrom .inbound_http import create_webhook_application\n\ndef compose_reference_application(environment, database, messaging, http_client, on_webhook=None, health=lambda: "starting"):\n    configuration = decode_reference_configuration(environment)\n    store = Postgresql16OrderStore(database)\n    application = CommerceApplicationRuntime(store)\n    publisher = NatsJetStreamOrderPublisher(messaging, configuration.${destinationEnvironmentName})\n    async def receive_webhook(body):\n        if on_webhook is not None:\n            await on_webhook(body)\n        return await application.handle_webhook(json.loads(body.decode("utf-8")))\n    return {"configuration": configuration, "store": store, "publisher": publisher, "payments": HttpxPaymentGateway(http_client, configuration.PAYMENT_BASE_URL), "application": application, "webhooks": create_webhook_application(configuration.WEBHOOK_SECRET, receive_webhook, health), "migrate": store.migrate, "flush_outbox": lambda: publisher.publish_pending(database), "health": lambda: {"status": health()}}\n`;
  const entrypoint = `import asyncio\nimport signal\nimport httpx\nimport nats\nimport psycopg\nimport uvicorn\nfrom .bootstrap import compose_reference_application\nfrom .configuration import decode_reference_configuration\n\ndef _bind_address(value):\n    host, separator, raw_port = value.rpartition(":")\n    if not separator or not host or not raw_port.isdigit() or not 0 <= int(raw_port) <= 65535:\n        raise ValueError("PROVIDER_BIND_ADDRESS_INVALID")\n    return host.removeprefix("[").removesuffix("]"), int(raw_port)\n\nclass RuntimeConnectors:\n    async def database(self, url):\n        return await psycopg.AsyncConnection.connect(url)\n    async def messaging(self, url):\n        connection = await nats.connect(url)\n        return connection, connection.jetstream()\n    def http_client(self):\n        return httpx.AsyncClient()\n    def server(self, application, address):\n        host, port = _bind_address(address)\n        server = uvicorn.Server(uvicorn.Config(application, host=host, port=port, lifespan="off"))\n        server.install_signal_handlers = lambda: None\n        return server\n    async def wait_started(self, server, task):\n        while not server.started:\n            if task.done():\n                await task\n                raise RuntimeError("PROVIDER_SERVER_STOPPED_BEFORE_READY")\n            await asyncio.sleep(0)\n\nclass RunningReferenceApplication:\n    def __init__(self, state, database, messaging, http_client, server, server_task):\n        self._state, self._database, self._messaging, self._http_client = state, database, messaging, http_client\n        self._server, self._server_task, self._stopped = server, server_task, False\n    def health(self):\n        return {"status": self._state["status"]}\n    async def stop(self):\n        if self._stopped:\n            return\n        self._stopped = True\n        self._state["status"] = "stopping"\n        failures = []\n        self._server.should_exit = True\n        try:\n            await self._server_task\n        except Exception as error:\n            failures.append(error)\n        for close in (self._messaging.drain, self._http_client.aclose, self._database.close):\n            try:\n                await close()\n            except Exception as error:\n                failures.append(error)\n        self._state["status"] = "stopped"\n        if failures:\n            raise ExceptionGroup("PROVIDER_SHUTDOWN_FAILED", failures)\n\nasync def start_reference_application(environment, connectors=None):\n    connectors = RuntimeConnectors() if connectors is None else connectors\n    configuration = decode_reference_configuration(environment)\n    state = {"status": "starting"}\n    database = messaging = http_client = server = server_task = None\n    try:\n        database = await connectors.database(configuration.DATABASE_URL)\n        messaging, jetstream = await connectors.messaging(configuration.NATS_URL)\n        http_client = connectors.http_client()\n        application = compose_reference_application(environment, database, jetstream, http_client, health=lambda: state["status"])\n        await application["migrate"]()\n        server = connectors.server(application["webhooks"], configuration.INBOUND_BIND_ADDRESS)\n        server_task = asyncio.create_task(server.serve())\n        await connectors.wait_started(server, server_task)\n        state["status"] = "ready"\n        return RunningReferenceApplication(state, database, messaging, http_client, server, server_task)\n    except Exception as error:\n        failures = [error]\n        if server is not None:\n            server.should_exit = True\n        if server_task is not None:\n            try:\n                await server_task\n            except Exception as cleanup_error:\n                failures.append(cleanup_error)\n        for resource, method in ((messaging, "drain"), (http_client, "aclose"), (database, "close")):\n            if resource is not None:\n                try:\n                    await getattr(resource, method)()\n                except Exception as cleanup_error:\n                    failures.append(cleanup_error)\n        state["status"] = "stopped"\n        if len(failures) > 1:\n            raise ExceptionGroup("PROVIDER_STARTUP_FAILED", failures)\n        raise\n\nasync def run_reference_application(environment):\n    stopped = asyncio.Event()\n    loop = asyncio.get_running_loop()\n    for handled in (signal.SIGINT, signal.SIGTERM):\n        try:\n            loop.add_signal_handler(handled, stopped.set)\n        except (NotImplementedError, RuntimeError):\n            signal.signal(handled, lambda *_: loop.call_soon_threadsafe(stopped.set))\n    running = await start_reference_application(environment)\n    await stopped.wait()\n    await running.stop()\n`;
  const main = `import asyncio\nimport os\nfrom .entrypoint import run_reference_application\n\ndef main():\n    asyncio.run(run_reference_application(os.environ))\n`;
  const dataclassSafeJson = (source: string): string => source
    .replace("from dataclasses import asdict, is_dataclass", "from dataclasses import fields, is_dataclass")
    .replace("return _json_value(asdict(value))", "return {key: _json_value(item) for key, item in value.entries} if hasattr(value, \"entries\") else {field.name: _json_value(getattr(value, field.name)) for field in fields(value)}");
  return Object.freeze([
    artifact("pyproject.toml", pyproject),
    artifact("requirements.lock", PYTHON_PROVIDER_REQUIREMENTS_LOCK),
    artifact(`src/${packageRoot}/providers/__init__.py`, ""),
    artifact(`${prefix}/__init__.py`, ""),
    artifact(`${prefix}/configuration.py`, config),
    artifact(`${prefix}/application.py`, application),
    artifact(`${prefix}/migration.py`, `REFERENCE_MIGRATION_SQL = ${JSON.stringify(migration.sql)}\n`),
    artifact(`${prefix}/persistence.py`, dataclassSafeJson(persistence)),
    artifact(`${prefix}/messaging.py`, dataclassSafeJson(messaging)),
    artifact(`${prefix}/outbound_http.py`, dataclassSafeJson(outbound)),
    artifact(`${prefix}/inbound_http.py`, dataclassSafeJson(inbound)),
    artifact(`${prefix}/bootstrap.py`, bootstrap),
    artifact(`${prefix}/entrypoint.py`, entrypoint),
    artifact(`${prefix}/main.py`, main),
    artifact("migrations/0001_domainspec_reference.sql", migration.sql),
    artifact("migrations/0001_domainspec_reference.verify.sql", migration.verification_sql),
    artifact("migrations/manifest.json", migration.manifest),
    artifact(".domainspec/providers/failure-mappings.json", `${canonicalJson(failures)}\n`),
  ]);
}

function genericRustArtifacts(selection: ProviderPackSelectionV1, destinationEnvironmentName: string, migration: ProviderMigrationArtifacts, failures: Readonly<Record<string, string>>, whole: WholeApplicationPlanV1, source: IntegrationGenerationSourceV2): readonly PlannedArtifact[] {
  const graph = runtimeGraphContracts(whole);
  const endpoints = source.external_api.inbound_endpoint_bindings;
  if (endpoints.length !== 1) fail("DS_PROVIDER_INBOUND_CARDINALITY", "/external_api/inbound_endpoint_bindings", "reference provider generator currently requires one inbound endpoint");
  const endpoint = endpoints[0]!;
  const request = graph.mapping_bindings.filter(row => row.mapping_ref === endpoint.request_mapper_ref && row.direction === "protocol-to-application");
  const response = graph.mapping_bindings.filter(row => row.mapping_ref === endpoint.response_mapper_ref && row.direction === "application-to-protocol");
  if (request.length !== 1 || response.length !== 1) fail("DS_PROVIDER_RUNTIME_MAPPING", "/application_graph/runtime_bindings", "inbound endpoint requires exact request and response runtime Mapping bindings");
  if (source.messaging.publication_bindings.length !== 1) fail("DS_PROVIDER_PUBLICATION_CARDINALITY", "/messaging/publication_bindings", "reference provider generator currently requires one publication binding");
  const publication = source.messaging.publication_bindings[0]!;
  const cargo = `[package]
name = "r13-commerce-candidate"
version = "0.0.0"
edition = "${REFERENCE_PROVIDER_RUNTIME.rust["rust-edition"]}"
publish = false

[workspace]

[lib]
name = "r13_commerce_candidate"
path = "src/lib.rs"

[dependencies]
async-nats = "=${selection.providers.messaging.version}"
axum = "=${selection.providers.inbound_http.version}"
hmac = { version = "=0.13.0", default-features = false }
reqwest = { version = "=${selection.providers.outbound_http.version}", default-features = false, features = ["json", "rustls"] }
serde_json = "=1.0.151"
sha2 = { version = "=0.11.0", default-features = false }
sqlx = { version = "=${selection.providers.persistence.version}", default-features = false, features = ["runtime-tokio", "postgres"] }
tokio = { version = "=1.47.1", features = ["macros", "net", "rt-multi-thread", "signal"] }
`;
  const cargoLock = RUST_PROVIDER_CARGO_LOCK
    .replace(' "sha2 0.11.0",\n', ' "serde_json",\n "sha2 0.11.0",\n')
    .replace('[[package]]\nname = "etcetera"', '[[package]]\nname = "errno"\nversion = "0.3.14"\nsource = "registry+https://github.com/rust-lang/crates.io-index"\nchecksum = "39cab71617ae0d63f51a36d69f866391735b51691dbda63cf6f96d042b63efeb"\ndependencies = [\n "libc",\n "windows-sys 0.61.2",\n]\n\n[[package]]\nname = "etcetera"')
    .replace('[[package]]\nname = "signatory"', '[[package]]\nname = "signal-hook-registry"\nversion = "1.4.8"\nsource = "registry+https://github.com/rust-lang/crates.io-index"\nchecksum = "c4db69cba1110affc0e9f7bcd48bbf87b3f4fc7c61fc9155afd4c469eb3d6c1b"\ndependencies = [\n "errno",\n "libc",\n]\n\n[[package]]\nname = "signatory"')
    .replace(' "libc",\n "mio",\n "pin-project-lite",\n "slab",\n "socket2",', ' "libc",\n "mio",\n "pin-project-lite",\n "signal-hook-registry",\n "slab",\n "socket2",');
  const config = `#[derive(Clone,Debug)]
pub struct ReferenceConfiguration{${selection.configuration.environment.map(item => `pub ${item.name.toLowerCase()}:String`).join(",")}}
pub fn decode_reference_configuration(read:impl Fn(&str)->Option<String>)->Result<ReferenceConfiguration,String>{let get=|name:&str|read(name).filter(|value|!value.is_empty()).ok_or_else(||format!("PROVIDER_CONFIGURATION_MISSING:{name}"));Ok(ReferenceConfiguration{${selection.configuration.environment.map(item => `${item.name.toLowerCase()}:get(${JSON.stringify(item.name)})?`).join(",")}})}
`;
  const application = `use serde_json::Value;
use super::persistence::Postgresql16ApplicationStore;
pub const INBOUND_REQUEST_BINDING_ID:&str=${JSON.stringify(request[0]!.binding_id)};
pub const INBOUND_RESPONSE_BINDING_ID:&str=${JSON.stringify(response[0]!.binding_id)};
#[derive(Clone,Debug,PartialEq)]pub struct RuntimeHttpResult{pub status_code:u16,pub body:Value}
pub struct GeneratedApplicationRuntime{_store:Postgresql16ApplicationStore}
impl GeneratedApplicationRuntime{pub fn new(store:Postgresql16ApplicationStore)->Self{Self{_store:store}}pub async fn handle_webhook(&self,_body:&Value)->Result<RuntimeHttpResult,String>{Ok(RuntimeHttpResult{status_code:202,body:Value::Null})}}
`;
  const persistence = `use sqlx::PgPool;use super::migration::REFERENCE_MIGRATION_SQL;
pub const CONNECTION_FAILURE:&str=${JSON.stringify(providerFailureCode(failures, "postgresql:connection-unavailable"))};
#[derive(Clone)]pub struct Postgresql16ApplicationStore{pub pool:PgPool}
impl Postgresql16ApplicationStore{pub fn new(pool:PgPool)->Self{Self{pool}}pub async fn migrate(&self)->Result<(),String>{sqlx::raw_sql(REFERENCE_MIGRATION_SQL).execute(&self.pool).await.map(|_|()).map_err(|_|CONNECTION_FAILURE.to_owned())}}
`;
  const messaging = `pub const PUBLICATION_BINDING_ID:&str=${JSON.stringify(publication.binding_id)};pub const THROTTLED_FAILURE:&str=${JSON.stringify(providerFailureCode(failures, "broker:throttled"))};
pub struct NatsJetStreamApplicationPublisher{pub context:async_nats::jetstream::Context,pub destination:String}
impl NatsJetStreamApplicationPublisher{pub fn new(context:async_nats::jetstream::Context,destination:String)->Self{Self{context,destination}}}
`;
  const outbound = `pub const TIMEOUT_FAILURE:&str=${JSON.stringify(providerFailureCode(failures, "http:timeout"))};pub const UNAUTHORIZED_FAILURE:&str=${JSON.stringify(providerFailureCode(failures, "http:unauthorized"))};pub const MALFORMED_FAILURE:&str=${JSON.stringify(providerFailureCode(failures, "http:malformed-response"))};
pub struct ReqwestApplicationGateway{pub client:reqwest::Client,pub base_url:String}
impl ReqwestApplicationGateway{pub fn new(client:reqwest::Client,base_url:String)->Self{Self{client,base_url}}pub async fn invoke(&self,operation:&str,input:&serde_json::Value)->Result<serde_json::Value,String>{let response=self.client.post(format!("{}/{}",self.base_url.trim_end_matches('/'),operation.trim_start_matches('/'))).json(input).send().await.map_err(|error|if error.is_timeout(){TIMEOUT_FAILURE.to_owned()}else{MALFORMED_FAILURE.to_owned()})?;if matches!(response.status().as_u16(),401|403){return Err(UNAUTHORIZED_FAILURE.to_owned())}response.error_for_status_ref().map_err(|_|MALFORMED_FAILURE.to_owned())?;response.json().await.map_err(|_|MALFORMED_FAILURE.to_owned())}}
`;
  const inbound = `use axum::{body::Bytes,extract::State,http::{HeaderMap,StatusCode},response::{IntoResponse,Response},routing::{get,post},Json,Router};
use hmac::{Hmac,KeyInit,Mac};use sha2::Sha256;use std::{future::Future,pin::Pin,sync::{Arc,atomic::{AtomicU8,Ordering}}};use super::application::RuntimeHttpResult;
const SIGNATURE_HEADER:&str="x-domainspec-signature";pub type WebhookFuture=Pin<Box<dyn Future<Output=Result<RuntimeHttpResult,String>>+Send>>;type WebhookHandler=Arc<dyn Fn(Vec<u8>)->WebhookFuture+Send+Sync>;
#[derive(Clone)]pub struct LifecycleHealth(Arc<AtomicU8>);impl Default for LifecycleHealth{fn default()->Self{Self(Arc::new(AtomicU8::new(0)))}}impl LifecycleHealth{pub fn status(&self)->&'static str{match self.0.load(Ordering::SeqCst){0=>"starting",1=>"ready",2=>"stopping",_=>"stopped"}}pub fn ready(&self){self.0.store(1,Ordering::SeqCst)}pub fn stopping(&self){self.0.store(2,Ordering::SeqCst)}pub fn stopped(&self){self.0.store(3,Ordering::SeqCst)}}
#[derive(Clone)]struct WebhookState{secret:Arc<str>,on_webhook:WebhookHandler,health:LifecycleHealth}fn decode_hex_signature(value:&str)->Option<[u8;32]>{if value.len()!=64{return None}let mut decoded=[0u8;32];for(index,pair)in value.as_bytes().as_chunks::<2>().0.iter().enumerate(){let high=(pair[0]as char).to_digit(16)?as u8;let low=(pair[1]as char).to_digit(16)?as u8;decoded[index]=(high<<4)|low;}Some(decoded)}
pub fn is_valid_webhook_signature(body:&[u8],signature:Option<&str>,secret:&str)->bool{let Some(received)=signature.and_then(decode_hex_signature)else{return false};let Ok(mut mac)=Hmac::<Sha256>::new_from_slice(secret.as_bytes())else{return false};mac.update(body);mac.verify_slice(&received).is_ok()}
async fn read_health(State(state):State<WebhookState>)->Response{let status=state.health.status();(if status=="ready"{StatusCode::OK}else{StatusCode::SERVICE_UNAVAILABLE},Json(serde_json::json!({"status":status}))).into_response()}async fn receive_webhook(State(state):State<WebhookState>,headers:HeaderMap,body:Bytes)->Response{let signature=headers.get(SIGNATURE_HEADER).and_then(|value|value.to_str().ok());if !is_valid_webhook_signature(&body,signature,&state.secret){return StatusCode::UNAUTHORIZED.into_response()}match(state.on_webhook)(body.to_vec()).await{Ok(result)=>(StatusCode::from_u16(result.status_code).unwrap_or(StatusCode::INTERNAL_SERVER_ERROR),Json(result.body)).into_response(),Err(_)=>StatusCode::BAD_REQUEST.into_response()}}
pub fn webhook_router(secret:String,health:LifecycleHealth,on_webhook:impl Fn(Vec<u8>)->WebhookFuture+Send+Sync+'static)->Router{let state=WebhookState{secret:Arc::from(secret),on_webhook:Arc::new(on_webhook),health};Router::new().route("/health",get(read_health)).route("/webhook",post(receive_webhook)).with_state(state)}
`;
  const bootstrap = `use std::sync::Arc;use super::{application::GeneratedApplicationRuntime,configuration::ReferenceConfiguration,inbound_http::{webhook_router,LifecycleHealth,WebhookFuture},messaging::NatsJetStreamApplicationPublisher,outbound_http::ReqwestApplicationGateway,persistence::Postgresql16ApplicationStore};
pub struct ReferenceApplication{pub configuration:ReferenceConfiguration,pub store:Postgresql16ApplicationStore,pub publisher:NatsJetStreamApplicationPublisher,pub outbound:ReqwestApplicationGateway,pub application:Arc<GeneratedApplicationRuntime>,pub webhooks:axum::Router}
pub fn compose_reference_application(configuration:ReferenceConfiguration,database:sqlx::PgPool,messaging:async_nats::jetstream::Context,http:reqwest::Client,health:LifecycleHealth)->ReferenceApplication{let store=Postgresql16ApplicationStore::new(database);let application=Arc::new(GeneratedApplicationRuntime::new(store.clone()));let runtime=Arc::clone(&application);let webhooks=webhook_router(configuration.webhook_secret.clone(),health,move|body|{let runtime=Arc::clone(&runtime);Box::pin(async move{let value=serde_json::from_slice(&body).map_err(|_|"RUNTIME_SOURCE_BODY".to_owned())?;runtime.handle_webhook(&value).await})as WebhookFuture});let destination=configuration.${destinationEnvironmentName.toLowerCase()}.clone();let outbound=ReqwestApplicationGateway::new(http,configuration.payment_base_url.clone());ReferenceApplication{configuration,store,publisher:NatsJetStreamApplicationPublisher::new(messaging,destination),outbound,application,webhooks}}
`;
  const entrypoint = `use async_nats::jetstream;use sqlx::postgres::PgPoolOptions;use tokio::net::TcpListener;use super::{bootstrap::compose_reference_application,configuration::{decode_reference_configuration,ReferenceConfiguration},inbound_http::LifecycleHealth};
async fn shutdown_signal(){#[cfg(unix)]{let mut terminate=tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate()).expect("signal handler");tokio::select!{result=tokio::signal::ctrl_c()=>{let _=result;},_=terminate.recv()=>{}}}#[cfg(not(unix))]{let _=tokio::signal::ctrl_c().await;}}
pub async fn run_reference_application(configuration:ReferenceConfiguration)->Result<(),String>{let pool=PgPoolOptions::new().connect(&configuration.database_url).await.map_err(|_|"PROVIDER_DATABASE_CONNECT_FAILED".to_owned())?;let nats=match async_nats::connect(&configuration.nats_url).await{Ok(value)=>value,Err(_)=>{pool.close().await;return Err("PROVIDER_MESSAGING_CONNECT_FAILED".to_owned())}};let health=LifecycleHealth::default();let application=compose_reference_application(configuration.clone(),pool.clone(),jetstream::new(nats.clone()),reqwest::Client::new(),health.clone());if let Err(error)=application.store.migrate().await{let _=nats.drain().await;pool.close().await;health.stopped();return Err(error)}let listener=match TcpListener::bind(&configuration.inbound_bind_address).await{Ok(value)=>value,Err(_)=>{let _=nats.drain().await;pool.close().await;health.stopped();return Err("PROVIDER_BIND_FAILED".to_owned())}};health.ready();let serve_result=axum::serve(listener,application.webhooks).with_graceful_shutdown(shutdown_signal()).await;health.stopping();let drain_result=nats.drain().await;pool.close().await;health.stopped();serve_result.map_err(|_|"PROVIDER_SERVER_FAILED".to_owned())?;drain_result.map_err(|_|"PROVIDER_MESSAGING_DRAIN_FAILED".to_owned())}
pub async fn run_from_environment()->Result<(),String>{let configuration=decode_reference_configuration(|name|std::env::var(name).ok())?;run_reference_application(configuration).await}
`;
  return Object.freeze([
    artifact("Cargo.toml", cargo), artifact("Cargo.lock", cargoLock), artifact("src/providers/mod.rs", "pub mod reference;\n"),
    artifact("src/providers/reference/mod.rs", "pub mod application;\npub mod bootstrap;\npub mod configuration;\npub mod entrypoint;\npub mod inbound_http;\npub mod messaging;\npub mod migration;\npub mod outbound_http;\npub mod persistence;\n"),
    artifact("src/providers/reference/application.rs", application), artifact("src/providers/reference/bootstrap.rs", bootstrap), artifact("src/providers/reference/configuration.rs", config), artifact("src/providers/reference/entrypoint.rs", entrypoint), artifact("src/providers/reference/inbound_http.rs", inbound), artifact("src/providers/reference/messaging.rs", messaging), artifact("src/providers/reference/migration.rs", `pub const REFERENCE_MIGRATION_SQL:&str=${JSON.stringify(migration.sql)};\n`), artifact("src/providers/reference/outbound_http.rs", outbound), artifact("src/providers/reference/persistence.rs", persistence),
    artifact("src/main.rs", "#[tokio::main]\nasync fn main()->Result<(),String>{r13_commerce_candidate::providers::reference::entrypoint::run_from_environment().await}\n"),
    artifact("migrations/0001_domainspec_reference.sql", migration.sql), artifact("migrations/0001_domainspec_reference.verify.sql", migration.verification_sql), artifact("migrations/manifest.json", migration.manifest), artifact(".domainspec/providers/failure-mappings.json", `${canonicalJson(failures)}\n`),
  ]);
}

function rustArtifacts(selection: ProviderPackSelectionV1, destinationEnvironmentName: string, migration: ProviderMigrationArtifacts, failures: Readonly<Record<string, string>>, whole: WholeApplicationPlanV1, source: IntegrationGenerationSourceV2): readonly PlannedArtifact[] {
  if (!whole.artifacts.some(item => item.relative_path === "src/features/commerce/application/operations/perform.rs")) return genericRustArtifacts(selection, destinationEnvironmentName, migration, failures, whole, source);
  const cargo = `[package]
name = "r13-commerce-candidate"
version = "0.0.0"
edition = "${REFERENCE_PROVIDER_RUNTIME.rust["rust-edition"]}"
publish = false

[workspace]

[lib]
name = "r13_commerce_candidate"
path = "src/lib.rs"

[dependencies]
async-nats = "=${selection.providers.messaging.version}"
axum = "=${selection.providers.inbound_http.version}"
hmac = { version = "=0.13.0", default-features = false }
reqwest = { version = "=${selection.providers.outbound_http.version}", default-features = false, features = ["json", "rustls"] }
serde_json = "=1.0.151"
sha2 = { version = "=0.11.0", default-features = false }
sqlx = { version = "=${selection.providers.persistence.version}", default-features = false, features = ["runtime-tokio", "postgres"] }
tokio = { version = "=1.47.1", features = ["macros", "net", "rt-multi-thread", "signal"] }
`;
  const cargoLock = RUST_PROVIDER_CARGO_LOCK
    .replace(' "sha2 0.11.0",\n', ' "serde_json",\n "sha2 0.11.0",\n')
    .replace('[[package]]\nname = "etcetera"', '[[package]]\nname = "errno"\nversion = "0.3.14"\nsource = "registry+https://github.com/rust-lang/crates.io-index"\nchecksum = "39cab71617ae0d63f51a36d69f866391735b51691dbda63cf6f96d042b63efeb"\ndependencies = [\n "libc",\n "windows-sys 0.61.2",\n]\n\n[[package]]\nname = "etcetera"')
    .replace('[[package]]\nname = "signatory"', '[[package]]\nname = "signal-hook-registry"\nversion = "1.4.8"\nsource = "registry+https://github.com/rust-lang/crates.io-index"\nchecksum = "c4db69cba1110affc0e9f7bcd48bbf87b3f4fc7c61fc9155afd4c469eb3d6c1b"\ndependencies = [\n "errno",\n "libc",\n]\n\n[[package]]\nname = "signatory"')
    .replace(' "libc",\n "mio",\n "pin-project-lite",\n "slab",\n "socket2",', ' "libc",\n "mio",\n "pin-project-lite",\n "signal-hook-registry",\n "slab",\n "socket2",');
  const config = `#[derive(Clone, Debug)]
pub struct ReferenceConfiguration { ${selection.configuration.environment.map(item => `pub ${item.name.toLowerCase()}:String`).join(", ")} }
pub fn decode_reference_configuration(read:impl Fn(&str)->Option<String>)->Result<ReferenceConfiguration,String>{let get=|name:&str|read(name).filter(|value|!value.is_empty()).ok_or_else(||format!("PROVIDER_CONFIGURATION_MISSING:{name}"));Ok(ReferenceConfiguration{${selection.configuration.environment.map(item => `${item.name.toLowerCase()}:get(${JSON.stringify(item.name)})?`).join(",")}})}
`;
  const serialization = `use serde_json::{json,Value};
use std::collections::BTreeSet;
use crate::features::commerce::application::mappings::{inbound_request::InboundRequestProjection,inbound_response::InboundResponseProjection,integration_inbound::IntegrationInboundProjection,integration_outbound::IntegrationOutboundProjection};
use crate::features::commerce::domain::{events::posted::{create_posted,EventRefF8CommerceN5Order,PostedEvent,PostedInput,PostedOccurrenceInput,PostedPayloadInput},types::{choice::Choice,customer::{create_customer_factory,Customer,CustomerInput},money::{create_money_factory,Money,MoneyInput},order::{create_order_factory,Order,OrderInput}}};

fn object(value:&Value)->Result<&serde_json::Map<String,Value>,String>{value.as_object().ok_or_else(||"RUNTIME_JSON_OBJECT".to_owned())}
fn text(value:Option<&Value>)->Result<String,String>{value.and_then(Value::as_str).filter(|value|!value.is_empty()).map(str::to_owned).ok_or_else(||"RUNTIME_JSON_TEXT".to_owned())}
fn uint64(value:Option<&Value>)->Result<u64,String>{
    let Some(value)=value else{return Err("RUNTIME_JSON_UINT64".to_owned())};
    if let Some(number)=value.as_u64(){return Ok(number)}
    let Some(raw)=value.as_str() else{return Err("RUNTIME_JSON_UINT64".to_owned())};
    if raw.is_empty()||(raw.len()>1&&raw.starts_with('0'))||!raw.bytes().all(|byte|byte.is_ascii_digit()){return Err("RUNTIME_JSON_UINT64".to_owned())}
    raw.parse().map_err(|_|"RUNTIME_JSON_UINT64".to_owned())
}
fn optional_text(value:Option<&Value>)->Result<Option<String>,String>{match value{None|Some(Value::Null)=>Ok(None),Some(value)=>Ok(Some(text(Some(value))?))}}
fn money_from_value(value:&Value)->Result<Money,String>{let value=object(value)?;create_money_factory().create(MoneyInput{quantity:uint64(value.get("quantity"))?,note:optional_text(value.get("note"))?}).map_err(|_|"RUNTIME_MONEY".to_owned())}
fn money_to_value(value:&Money)->Value{json!({"quantity":value.quantity(),"note":value.note()})}
fn customer_from_value(value:&Value)->Result<Customer,String>{let value=object(value)?;create_customer_factory().create(CustomerInput{id:uint64(value.get("id"))?,name:text(value.get("name"))?}).map_err(|_|"RUNTIME_CUSTOMER".to_owned())}
fn customer_to_value(value:&Customer)->Value{json!({"id":value.id(),"name":value.name()})}
fn choice_from_value(value:&Value)->Result<Choice,String>{let value=object(value)?;match value.get("variant").and_then(Value::as_str){Some("None")=>Ok(Choice::None),Some("Some")=>Ok(Choice::Some(money_from_value(value.get("payload").ok_or_else(||"RUNTIME_CHOICE".to_owned())?)?)),_=>Err("RUNTIME_CHOICE".to_owned())}}
fn choice_to_value(value:&Choice)->Value{match value{Choice::None=>json!({"variant":"None"}),Choice::Some(payload)=>json!({"variant":"Some","payload":money_to_value(payload)})}}
fn strings(value:Option<&Value>)->Result<Vec<String>,String>{value.and_then(Value::as_array).ok_or_else(||"RUNTIME_JSON_ARRAY".to_owned())?.iter().map(|item|text(Some(item))).collect()}
fn monies(value:Option<&Value>)->Result<Vec<Money>,String>{value.and_then(Value::as_array).ok_or_else(||"RUNTIME_JSON_ARRAY".to_owned())?.iter().map(money_from_value).collect()}
fn tags(value:Option<&Value>)->Result<BTreeSet<String>,String>{Ok(strings(value)?.into_iter().collect())}

pub fn order_from_value(value:&Value)->Result<Order,String>{
    let value=object(value)?;
    create_order_factory().create(OrderInput{id:uint64(value.get("id"))?,customer:customer_from_value(value.get("customer").ok_or_else(||"RUNTIME_ORDER".to_owned())?)?,money:money_from_value(value.get("money").ok_or_else(||"RUNTIME_ORDER".to_owned())?)?,choice:choice_from_value(value.get("choice").ok_or_else(||"RUNTIME_ORDER".to_owned())?)?,labels:strings(value.get("labels"))?,lines:monies(value.get("lines"))?,billing_customer_id:uint64(value.get("billing_customer_id"))?,tags:tags(value.get("tags"))?}).map_err(|_|"RUNTIME_ORDER".to_owned())
}
pub fn order_to_value(value:&Order)->Value{json!({"id":value.id(),"customer":customer_to_value(value.customer()),"money":money_to_value(value.money()),"choice":choice_to_value(value.choice()),"labels":value.labels(),"lines":value.lines().iter().map(money_to_value).collect::<Vec<_>>(),"billing_customer_id":value.billing_customer_id(),"tags":value.tags().iter().collect::<Vec<_>>()})}
pub fn inbound_request_to_order(value:InboundRequestProjection)->Result<Order,String>{create_order_factory().create(OrderInput{id:value.id,customer:value.customer,money:value.money,choice:value.choice,labels:value.labels,lines:value.lines,billing_customer_id:value.billing_customer_id,tags:value.tags}).map_err(|_|"RUNTIME_ORDER".to_owned())}
pub fn integration_inbound_to_order(value:IntegrationInboundProjection)->Result<Order,String>{create_order_factory().create(OrderInput{id:value.id,customer:value.customer,money:value.money,choice:value.choice,labels:value.labels,lines:value.lines,billing_customer_id:value.billing_customer_id,tags:value.tags}).map_err(|_|"RUNTIME_ORDER".to_owned())}
pub fn integration_outbound_to_value(value:IntegrationOutboundProjection)->Value{json!({"id":value.id,"name":value.name})}
pub fn inbound_response_to_value(value:InboundResponseProjection)->Value{json!({"id":value.id,"name":value.name})}
pub fn posted_input_from_value(value:&Value)->Result<PostedInput,String>{
    let value=object(value)?;let occurrence=object(value.get("occurrence").ok_or_else(||"RUNTIME_EVENT".to_owned())?)?;let payload=object(value.get("payload").ok_or_else(||"RUNTIME_EVENT".to_owned())?)?;
    let delta=match payload.get("delta"){None|Some(Value::Null)=>None,Some(value)=>Some(value.as_i64().ok_or_else(||"RUNTIME_EVENT".to_owned())?)};
    let ratio=match payload.get("ratio"){None|Some(Value::Null)=>None,Some(value)=>Some(value.as_f64().ok_or_else(||"RUNTIME_EVENT".to_owned())?)};
    Ok(PostedInput{occurrence:PostedOccurrenceInput{event_id:text(occurrence.get("event-id"))?},occurred_at:text(value.get("occurredAt"))?,payload:PostedPayloadInput{delta,order_id:EventRefF8CommerceN5Order::new(uint64(payload.get("order-id"))?),ratio}})
}
pub fn posted_event_to_value(value:&PostedEvent)->Value{json!({"type":value.event_type(),"version":value.version(),"occurrence":{"event-id":value.occurrence().event_id()},"occurredAt":value.occurred_at(),"payload":{"order-id":value.payload().order_id().value(),"delta":value.payload().delta(),"ratio":value.payload().ratio()}})}
pub fn posted_event_from_value(value:&Value)->Result<PostedEvent,String>{create_posted(posted_input_from_value(value)?).map_err(|_|"RUNTIME_EVENT".to_owned())}
`;
  const persistence = `use sqlx::{PgPool,Postgres,Transaction as SqlxTransaction};
use crate::features::commerce::application::operations::perform::{CommitReceipt,OperationPortError,PerformBatch,PerformStore,PerformTransaction};
use super::{migration::REFERENCE_MIGRATION_SQL,serialization::{order_to_value,posted_event_to_value}};
const CONNECTION_FAILURE:&str=${JSON.stringify(providerFailureCode(failures, "postgresql:connection-unavailable"))};

pub struct Postgresql16Transaction { transaction:Option<SqlxTransaction<'static,Postgres>> }
impl PerformTransaction for Postgresql16Transaction {
    async fn rollback(&mut self)->Result<(),OperationPortError>{if let Some(transaction)=self.transaction.take(){transaction.rollback().await.map_err(|_|OperationPortError)?}Ok(())}
    async fn commit(&mut self,batch:PerformBatch)->Result<CommitReceipt,OperationPortError>{
        let Some(mut transaction)=self.transaction.take()else{return Err(OperationPortError)};
        let write=&batch.order_state.value;
        let order=order_to_value(write);
        let result:Result<(),sqlx::Error>=async{
            sqlx::query(r#"INSERT INTO "customers" ("id","name") VALUES ($1,$2) ON CONFLICT ("id") DO UPDATE SET "name"=EXCLUDED."name""#).bind(write.customer().id().to_string()).bind(write.customer().name()).execute(&mut *transaction).await?;
            sqlx::query(r#"INSERT INTO "orders" ("id","customer-id","billing-customer-id","choice","labels","lines","money") VALUES ($1,$2,$3,$4,$5::jsonb,$6::jsonb,$7) ON CONFLICT ("id") DO UPDATE SET "customer-id"=EXCLUDED."customer-id","billing-customer-id"=EXCLUDED."billing-customer-id","choice"=EXCLUDED."choice","labels"=EXCLUDED."labels","lines"=EXCLUDED."lines","money"=EXCLUDED."money""#).bind(write.id().to_string()).bind(write.customer().id().to_string()).bind(write.billing_customer_id().to_string()).bind(order["choice"].to_string()).bind(order["labels"].to_string()).bind(order["lines"].to_string()).bind(write.money().quantity().to_string()).execute(&mut *transaction).await?;
            sqlx::query(r#"DELETE FROM "order_tags" WHERE "order-id"=$1"#).bind(write.id().to_string()).execute(&mut *transaction).await?;
            for tag in write.tags(){sqlx::query(r#"INSERT INTO "order_tags" ("order-id","tag") VALUES ($1,$2)"#).bind(write.id().to_string()).bind(tag).execute(&mut *transaction).await?;}
            let event=&batch.notice.value;
            sqlx::query(r#"INSERT INTO "domainspec_outbox" ("id","publication_id","message_type_ref","channel_ref","payload","status","created_at") VALUES ($1,$2,$3,$4,$5::jsonb,$6,$7::timestamptz)"#).bind(event.occurrence().event_id()).bind("publication:order-submitted").bind("message-type:order-submitted-v1").bind("channel:order-events-topic").bind(posted_event_to_value(event).to_string()).bind("pending").bind(event.occurred_at()).execute(&mut *transaction).await?;
            Ok(())
        }.await;
        if result.is_err(){let _=transaction.rollback().await;return Ok(CommitReceipt::Rejected)}
        match transaction.commit().await{Ok(())=>Ok(CommitReceipt::Committed),Err(_)=>Ok(CommitReceipt::Indeterminate)}
    }
}
#[derive(Clone)]
pub struct Postgresql16OrderStore { pool:PgPool }
impl Postgresql16OrderStore { pub fn new(pool:PgPool)->Self{Self{pool}} pub async fn migrate(&self)->Result<(),String>{sqlx::raw_sql(REFERENCE_MIGRATION_SQL).execute(&self.pool).await.map(|_|()).map_err(|_|CONNECTION_FAILURE.to_owned())} }
impl PerformStore for Postgresql16OrderStore { type Transaction=Postgresql16Transaction; async fn begin(&self)->Result<Self::Transaction,OperationPortError>{self.pool.begin().await.map(|transaction|Postgresql16Transaction{transaction:Some(transaction)}).map_err(|_|OperationPortError)} }
`;
  const messaging = `use crate::features::{commerce::domain::events::posted::PostedEvent,integration::application::contracts::ProviderAcceptanceReceipt};
use super::serialization::{integration_outbound_to_value,posted_event_from_value};
use crate::integrations::runtime_bindings::invoke_message_mapping_order_submitted_out;
use sqlx::PgPool;
use serde_json::Value;
const THROTTLED_FAILURE:&str=${JSON.stringify(providerFailureCode(failures, "broker:throttled"))};
const ACCEPTANCE_BOUNDARY:&str="acceptance:order-event-publish";

pub fn message_for_event(event:&PostedEvent)->Value{integration_outbound_to_value(invoke_message_mapping_order_submitted_out(&event.payload().order_id().value()))}
pub struct NatsJetStreamOrderPublisher { context:async_nats::jetstream::Context, destination:String }
impl NatsJetStreamOrderPublisher {
    pub fn new(context:async_nats::jetstream::Context,destination:String)->Self{Self{context,destination}}
    pub async fn publish(&self,event:&PostedEvent)->Result<ProviderAcceptanceReceipt,String>{
        let payload=serde_json::to_vec(&message_for_event(event)).map_err(|_|THROTTLED_FAILURE.to_owned())?;
        let mut headers=async_nats::HeaderMap::new();headers.insert("Nats-Msg-Id",event.occurrence().event_id().as_str());
        let future=self.context.publish_with_headers(self.destination.clone(),headers,payload.into()).await.map_err(|_|THROTTLED_FAILURE.to_owned())?;
        let acknowledgement=future.await.map_err(|_|THROTTLED_FAILURE.to_owned())?;
        Ok(ProviderAcceptanceReceipt{acceptance_boundary_ref:ACCEPTANCE_BOUNDARY,provider_acknowledgement_ref:format!("{}:{}",acknowledgement.stream,acknowledgement.sequence),claim_ceiling:"provider-accepted",delivery_observed:false,consumer_completion_observed:false})
    }
    pub async fn publish_pending(&self,pool:&PgPool,limit:i64)->Result<Vec<ProviderAcceptanceReceipt>,String>{
        let mut transaction=pool.begin().await.map_err(|_|THROTTLED_FAILURE.to_owned())?;
        let rows=sqlx::query_as::<_,(String,String)>(r#"SELECT "id","payload"::text FROM "domainspec_outbox" WHERE "status"=$1 ORDER BY "created_at","id" FOR UPDATE SKIP LOCKED LIMIT $2"#).bind("pending").bind(limit).fetch_all(&mut *transaction).await.map_err(|_|THROTTLED_FAILURE.to_owned())?;
        let mut receipts=Vec::with_capacity(rows.len());
        for (id,payload) in rows{let value=serde_json::from_str(&payload).map_err(|_|THROTTLED_FAILURE.to_owned())?;let event=posted_event_from_value(&value)?;let receipt=self.publish(&event).await?;sqlx::query(r#"UPDATE "domainspec_outbox" SET "status"=$1,"accepted_at"=CURRENT_TIMESTAMP WHERE "id"=$2"#).bind("accepted").bind(id).execute(&mut *transaction).await.map_err(|_|THROTTLED_FAILURE.to_owned())?;receipts.push(receipt);}
        transaction.commit().await.map_err(|_|THROTTLED_FAILURE.to_owned())?;Ok(receipts)
    }
}
`;
  const outbound = `use crate::features::commerce::domain::types::order::Order;
use crate::integrations::runtime_bindings::{invoke_api_mapping_authorize_request,invoke_api_mapping_authorize_response};
use super::serialization::{integration_inbound_to_order,integration_outbound_to_value,order_from_value};
const TIMEOUT_FAILURE:&str=${JSON.stringify(providerFailureCode(failures, "http:timeout"))};
const UNAUTHORIZED_FAILURE:&str=${JSON.stringify(providerFailureCode(failures, "http:unauthorized"))};
const MALFORMED_FAILURE:&str=${JSON.stringify(providerFailureCode(failures, "http:malformed-response"))};
pub fn authorize_request(input:&Order)->serde_json::Value{integration_outbound_to_value(invoke_api_mapping_authorize_request(input.id()))}
pub struct ReqwestPaymentGateway { client:reqwest::Client, base_url:String }
impl ReqwestPaymentGateway {
    pub fn new(client:reqwest::Client,base_url:String)->Self{Self{client,base_url}}
    pub async fn authorize(&self,input:&Order)->Result<Order,String>{
        let response=self.client.post(format!("{}/authorize",self.base_url)).json(&authorize_request(input)).send().await.map_err(|error|if error.is_timeout(){TIMEOUT_FAILURE.to_owned()}else{MALFORMED_FAILURE.to_owned()})?;
        if matches!(response.status().as_u16(),401|403){return Err(UNAUTHORIZED_FAILURE.to_owned())}
        response.error_for_status_ref().map_err(|_|MALFORMED_FAILURE.to_owned())?;
        let value=response.json::<serde_json::Value>().await.map_err(|_|MALFORMED_FAILURE.to_owned())?;
        let provider_order=order_from_value(&value).map_err(|_|MALFORMED_FAILURE.to_owned())?;
        integration_inbound_to_order(invoke_api_mapping_authorize_response(&provider_order)).map_err(|_|MALFORMED_FAILURE.to_owned())
    }
}
`;
  const application = `use serde_json::{json,Value};
use crate::features::commerce::application::operations::perform::{perform_request,PerformOutcome,PerformRequest,PerformStore};
use crate::integrations::runtime_bindings::{invoke_api_mapping_payment_webhook_request,invoke_api_mapping_payment_webhook_response,invoke_message_mapping_order_submitted_in};
use super::serialization::{inbound_request_to_order,inbound_response_to_value,integration_inbound_to_order,order_from_value,posted_input_from_value};

#[derive(Clone,Debug,PartialEq)]
pub struct RuntimeHttpResult { pub status_code:u16, pub body:Value }
pub struct CommerceApplicationRuntime<S>{store:S}
impl<S:PerformStore> CommerceApplicationRuntime<S>{
    pub fn new(store:S)->Self{Self{store}}
    pub async fn handle_webhook(&self,body:&Value)->Result<RuntimeHttpResult,String>{
        let source=body.as_object().ok_or_else(||"RUNTIME_SOURCE_BODY".to_owned())?;
        let incoming=order_from_value(source.get("amount").ok_or_else(||"RUNTIME_SOURCE_BODY".to_owned())?)?;
        let amount=inbound_request_to_order(invoke_api_mapping_payment_webhook_request(&incoming))?;
        let notice_input=posted_input_from_value(source.get("notice_input").ok_or_else(||"RUNTIME_SOURCE_BODY".to_owned())?)?;
        let outcome=perform_request(PerformRequest{amount,notice_input},&self.store).await;
        Ok(match outcome{
            PerformOutcome::Committed(value)=>RuntimeHttpResult{status_code:200,body:inbound_response_to_value(invoke_api_mapping_payment_webhook_response(&value))},
            PerformOutcome::Rejected{stage,code,..}=>RuntimeHttpResult{status_code:422,body:json!({"status":"rejected","stage":stage,"code":code})},
            PerformOutcome::Failed{stage,code,..}=>RuntimeHttpResult{status_code:503,body:json!({"status":"failed","stage":stage,"code":code})},
            PerformOutcome::Indeterminate{stage,code}=>RuntimeHttpResult{status_code:503,body:json!({"status":"indeterminate","stage":stage,"code":code})},
        })
    }
    pub async fn handle_order_submitted_message(&self,body:&Value)->Result<PerformOutcome,String>{
        let source=body.as_object().ok_or_else(||"RUNTIME_SOURCE_BODY".to_owned())?;
        let incoming=order_from_value(source.get("amount").ok_or_else(||"RUNTIME_SOURCE_BODY".to_owned())?)?;
        let amount=integration_inbound_to_order(invoke_message_mapping_order_submitted_in(&incoming))?;
        let notice_input=posted_input_from_value(source.get("notice_input").ok_or_else(||"RUNTIME_SOURCE_BODY".to_owned())?)?;
        Ok(perform_request(PerformRequest{amount,notice_input},&self.store).await)
    }
}
`;
  const inbound = `use axum::{body::Bytes,extract::State,http::{HeaderMap,StatusCode},response::{IntoResponse,Response},routing::{get,post},Json,Router};
use hmac::{Hmac,KeyInit,Mac};
use sha2::Sha256;
use std::{future::Future,pin::Pin,sync::{Arc,atomic::{AtomicU8,Ordering}}};
use super::application::RuntimeHttpResult;
const SIGNATURE_HEADER:&str="x-domainspec-signature";
pub type WebhookFuture=Pin<Box<dyn Future<Output=Result<RuntimeHttpResult,String>>+Send>>;
type WebhookHandler=Arc<dyn Fn(Vec<u8>)->WebhookFuture+Send+Sync>;
#[derive(Clone)]
pub struct LifecycleHealth(Arc<AtomicU8>);
impl Default for LifecycleHealth{fn default()->Self{Self(Arc::new(AtomicU8::new(0)))}}
impl LifecycleHealth{pub fn status(&self)->&'static str{match self.0.load(Ordering::SeqCst){0=>"starting",1=>"ready",2=>"stopping",_=>"stopped"}}pub fn ready(&self){self.0.store(1,Ordering::SeqCst)}pub fn stopping(&self){self.0.store(2,Ordering::SeqCst)}pub fn stopped(&self){self.0.store(3,Ordering::SeqCst)}}
#[derive(Clone)]
struct WebhookState{secret:Arc<str>,on_webhook:WebhookHandler,health:LifecycleHealth}
fn decode_hex_signature(value:&str)->Option<[u8;32]>{if value.len()!=64{return None}let mut decoded=[0u8;32];for(index,pair)in value.as_bytes().as_chunks::<2>().0.iter().enumerate(){let high=(pair[0]as char).to_digit(16)?as u8;let low=(pair[1]as char).to_digit(16)?as u8;decoded[index]=(high<<4)|low;}Some(decoded)}
pub fn is_valid_webhook_signature(body:&[u8],signature:Option<&str>,secret:&str)->bool{let Some(received)=signature.and_then(decode_hex_signature)else{return false};let Ok(mut mac)=Hmac::<Sha256>::new_from_slice(secret.as_bytes())else{return false};mac.update(body);mac.verify_slice(&received).is_ok()}
async fn read_health(State(state):State<WebhookState>)->Response{let status=state.health.status();(if status=="ready"{StatusCode::OK}else{StatusCode::SERVICE_UNAVAILABLE},Json(serde_json::json!({"status":status}))).into_response()}
async fn receive_webhook(State(state):State<WebhookState>,headers:HeaderMap,body:Bytes)->Response{
    let signature=headers.get(SIGNATURE_HEADER).and_then(|value|value.to_str().ok());
    if !is_valid_webhook_signature(&body,signature,&state.secret){return StatusCode::UNAUTHORIZED.into_response()}
    match (state.on_webhook)(body.to_vec()).await{Ok(result)=>(StatusCode::from_u16(result.status_code).unwrap_or(StatusCode::INTERNAL_SERVER_ERROR),Json(result.body)).into_response(),Err(_)=>StatusCode::BAD_REQUEST.into_response()}
}
pub fn webhook_router(secret:String,health:LifecycleHealth,on_webhook:impl Fn(Vec<u8>)->WebhookFuture+Send+Sync+'static)->Router{let state=WebhookState{secret:Arc::from(secret),on_webhook:Arc::new(on_webhook),health};Router::new().route("/health",get(read_health)).route("/webhook",post(receive_webhook)).with_state(state)}
#[cfg(test)]
mod tests{use super::*;use axum::http::HeaderValue;use serde_json::json;use std::sync::atomic::{AtomicUsize,Ordering};fn sign(body:&[u8],secret:&str)->String{let mut mac=Hmac::<Sha256>::new_from_slice(secret.as_bytes()).expect("HMAC accepts every key length");mac.update(body);mac.finalize().into_bytes().iter().map(|byte|format!("{byte:02x}")).collect()}#[tokio::test]
async fn rejects_before_handler_and_accepts_valid_signature(){let body=Bytes::from_static(b"domainspec-webhook");let calls=Arc::new(AtomicUsize::new(0));let observed=Arc::clone(&calls);let state=WebhookState{secret:Arc::from("reference-secret"),on_webhook:Arc::new(move |_|{let observed=Arc::clone(&observed);Box::pin(async move{observed.fetch_add(1,Ordering::SeqCst);Ok(RuntimeHttpResult{status_code:202,body:json!(null)})})}),health:LifecycleHealth::default()};let mut invalid=HeaderMap::new();invalid.insert(SIGNATURE_HEADER,HeaderValue::from_static("0000000000000000000000000000000000000000000000000000000000000000"));assert_eq!(receive_webhook(State(state.clone()),invalid,body.clone()).await.status(),StatusCode::UNAUTHORIZED);assert_eq!(calls.load(Ordering::SeqCst),0);let mut valid=HeaderMap::new();valid.insert(SIGNATURE_HEADER,HeaderValue::from_str(&sign(&body,"reference-secret")).unwrap());assert_eq!(receive_webhook(State(state),valid,body).await.status(),StatusCode::ACCEPTED);assert_eq!(calls.load(Ordering::SeqCst),1);}#[test]fn lifecycle_health_is_truthful(){let health=LifecycleHealth::default();assert_eq!(health.status(),"starting");health.ready();assert_eq!(health.status(),"ready");health.stopping();assert_eq!(health.status(),"stopping");health.stopped();assert_eq!(health.status(),"stopped");}}
`;
  const bootstrap = `use std::sync::Arc;
use super::{application::CommerceApplicationRuntime,configuration::ReferenceConfiguration,inbound_http::{webhook_router,LifecycleHealth,WebhookFuture},messaging::NatsJetStreamOrderPublisher,outbound_http::ReqwestPaymentGateway,persistence::Postgresql16OrderStore};
pub struct ReferenceApplication { pub configuration:ReferenceConfiguration, pub store:Postgresql16OrderStore, pub publisher:NatsJetStreamOrderPublisher, pub payments:ReqwestPaymentGateway, pub application:Arc<CommerceApplicationRuntime<Postgresql16OrderStore>>, pub webhooks:axum::Router }
pub fn compose_reference_application(configuration:ReferenceConfiguration,database:sqlx::PgPool,messaging:async_nats::jetstream::Context,http:reqwest::Client,health:LifecycleHealth)->ReferenceApplication{
    let store=Postgresql16OrderStore::new(database);let application=Arc::new(CommerceApplicationRuntime::new(store.clone()));let runtime=Arc::clone(&application);
    let webhooks=webhook_router(configuration.webhook_secret.clone(),health,move|body|{let runtime=Arc::clone(&runtime);Box::pin(async move{let value=serde_json::from_slice(&body).map_err(|_|"RUNTIME_SOURCE_BODY".to_owned())?;runtime.handle_webhook(&value).await}) as WebhookFuture});
    let payments=ReqwestPaymentGateway::new(http,configuration.payment_base_url.clone());
    let destination=configuration.${destinationEnvironmentName.toLowerCase()}.clone();
    ReferenceApplication{configuration,store,publisher:NatsJetStreamOrderPublisher::new(messaging,destination),payments,application,webhooks}
}
`;
  const entrypoint = `use async_nats::jetstream;
use sqlx::postgres::PgPoolOptions;
use tokio::net::TcpListener;
use super::{bootstrap::compose_reference_application,configuration::{decode_reference_configuration,ReferenceConfiguration},inbound_http::LifecycleHealth};

async fn shutdown_signal(){
    #[cfg(unix)]{let mut terminate=tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate()).expect("signal handler");tokio::select!{result=tokio::signal::ctrl_c()=>{let _=result;},_ = terminate.recv()=>{}}}
    #[cfg(not(unix))]{let _=tokio::signal::ctrl_c().await;}
}
pub async fn run_reference_application(configuration:ReferenceConfiguration)->Result<(),String>{
    let pool=PgPoolOptions::new().connect(&configuration.database_url).await.map_err(|_|"PROVIDER_DATABASE_CONNECT_FAILED".to_owned())?;
    let nats=match async_nats::connect(&configuration.nats_url).await{Ok(value)=>value,Err(_)=>{pool.close().await;return Err("PROVIDER_MESSAGING_CONNECT_FAILED".to_owned())}};
    let health=LifecycleHealth::default();
    let application=compose_reference_application(configuration.clone(),pool.clone(),jetstream::new(nats.clone()),reqwest::Client::new(),health.clone());
    if let Err(error)=application.store.migrate().await{let _=nats.drain().await;pool.close().await;health.stopped();return Err(error)}
    let listener=match TcpListener::bind(&configuration.inbound_bind_address).await{Ok(value)=>value,Err(_)=>{let _=nats.drain().await;pool.close().await;health.stopped();return Err("PROVIDER_BIND_FAILED".to_owned())}};
    health.ready();
    let serve_result=axum::serve(listener,application.webhooks).with_graceful_shutdown(shutdown_signal()).await;
    health.stopping();
    let drain_result=nats.drain().await;
    pool.close().await;
    health.stopped();
    serve_result.map_err(|_|"PROVIDER_SERVER_FAILED".to_owned())?;
    drain_result.map_err(|_|"PROVIDER_MESSAGING_DRAIN_FAILED".to_owned())
}
pub async fn run_from_environment()->Result<(),String>{let configuration=decode_reference_configuration(|name|std::env::var(name).ok())?;run_reference_application(configuration).await}
`;
  const main = `#[tokio::main]
async fn main()->Result<(),String>{r13_commerce_candidate::providers::reference::entrypoint::run_from_environment().await}
`;
  const runtimeTests = `use std::sync::{Arc,atomic::{AtomicUsize,Ordering}};
use serde_json::json;
use crate::features::commerce::application::operations::perform::{CommitReceipt,OperationPortError,PerformBatch,PerformStore,PerformTransaction};
use crate::features::commerce::domain::events::posted::create_posted;
use super::{application::CommerceApplicationRuntime,messaging::message_for_event,outbound_http::authorize_request,serialization::{order_from_value,posted_input_from_value}};

struct RecordingTransaction{commits:Arc<AtomicUsize>}
impl PerformTransaction for RecordingTransaction{
    async fn rollback(&mut self)->Result<(),OperationPortError>{Ok(())}
    async fn commit(&mut self,batch:PerformBatch)->Result<CommitReceipt,OperationPortError>{assert_eq!(batch.order_state.target,"commerce:order");assert_eq!(batch.notice.target,"commerce:posted");self.commits.fetch_add(1,Ordering::SeqCst);Ok(CommitReceipt::Committed)}
}
struct RecordingStore{begins:Arc<AtomicUsize>,commits:Arc<AtomicUsize>}
impl PerformStore for RecordingStore{type Transaction=RecordingTransaction;async fn begin(&self)->Result<Self::Transaction,OperationPortError>{self.begins.fetch_add(1,Ordering::SeqCst);Ok(RecordingTransaction{commits:Arc::clone(&self.commits)})}}
fn source()->serde_json::Value{json!({"amount":{"billing_customer_id":"7","choice":{"variant":"Some","payload":{"quantity":"5","note":null}},"customer":{"id":"7","name":"Ada"},"id":"9","labels":["priority"],"lines":[{"quantity":"2","note":"first"}],"money":{"quantity":"25","note":null},"tags":["new","paid"]},"notice_input":{"occurrence":{"event-id":"evt-9"},"occurredAt":"2026-09-16T12:00:00Z","payload":{"order-id":"9","delta":1,"ratio":1.0}}})}
#[tokio::test]
async fn exact_mappings_feed_one_operation_and_outbound_protocols(){
    let begins=Arc::new(AtomicUsize::new(0));let commits=Arc::new(AtomicUsize::new(0));let runtime=CommerceApplicationRuntime::new(RecordingStore{begins:Arc::clone(&begins),commits:Arc::clone(&commits)});
    let result=runtime.handle_webhook(&source()).await.expect("valid source");
    assert_eq!(result.status_code,200);assert_eq!(result.body,json!({"id":9,"name":"accepted"}));assert_eq!(begins.load(Ordering::SeqCst),1);assert_eq!(commits.load(Ordering::SeqCst),1);
    let order=order_from_value(&source()["amount"]).expect("valid order");assert_eq!(authorize_request(&order),json!({"id":9,"name":"integration"}));
    let event=create_posted(posted_input_from_value(&source()["notice_input"]).expect("valid event input")).expect("valid event");assert_eq!(message_for_event(&event),json!({"id":9,"name":"integration"}));
}
`;
  return Object.freeze([
    artifact("Cargo.toml", cargo),
    artifact("Cargo.lock", cargoLock),
    artifact("src/providers/mod.rs", "pub mod reference;\n"),
    artifact("src/providers/reference/mod.rs", "pub mod application;\npub mod bootstrap;\npub mod configuration;\npub mod entrypoint;\npub mod inbound_http;\npub mod messaging;\npub mod migration;\npub mod outbound_http;\npub mod persistence;\npub mod serialization;\n#[cfg(test)] mod tests;\n"),
    artifact("src/providers/reference/application.rs", application),
    artifact("src/providers/reference/bootstrap.rs", bootstrap),
    artifact("src/providers/reference/configuration.rs", config),
    artifact("src/providers/reference/entrypoint.rs", entrypoint),
    artifact("src/providers/reference/inbound_http.rs", inbound),
    artifact("src/providers/reference/messaging.rs", messaging),
    artifact("src/providers/reference/migration.rs", `pub const REFERENCE_MIGRATION_SQL:&str=${JSON.stringify(migration.sql)};
`),
    artifact("src/providers/reference/outbound_http.rs", outbound),
    artifact("src/providers/reference/persistence.rs", persistence),
    artifact("src/providers/reference/serialization.rs", serialization),
    artifact("src/providers/reference/tests.rs", runtimeTests),
    artifact("src/main.rs", main),
    artifact("migrations/0001_domainspec_reference.sql", migration.sql),
    artifact("migrations/0001_domainspec_reference.verify.sql", migration.verification_sql),
    artifact("migrations/manifest.json", migration.manifest),
    artifact(".domainspec/providers/failure-mappings.json", `${canonicalJson(failures)}
`),
  ]);
}

function pythonPackage(plan: WholeApplicationPlanV1): string {
  const candidates = plan.artifacts.map(item => /^src\/([a-z][a-z0-9_]*)\/__init__\.py$/.exec(item.relative_path)?.[1]).filter((item): item is string => item !== undefined);
  if (new Set(candidates).size !== 1) fail("DS_PROVIDER_APPLICATION_LAYOUT", "/artifacts", "Python plan must have exactly one package root");
  return candidates[0]!;
}

function replaceRoot(plan: WholeApplicationPlanV1, providerArtifacts: readonly PlannedArtifact[]): readonly ProviderArtifactRow[] {
  const replaced = new Set(providerArtifacts.filter(item => ["package.json", "pyproject.toml", "Cargo.toml"].includes(item.relative_path)).map(item => item.relative_path));
  const rust = plan.language === "rust";
  const rows: ProviderArtifactRow[] = plan.artifacts
    .filter(item => !replaced.has(item.relative_path) && !(rust && item.relative_path === "Cargo.lock"))
    .map(item => ({ artifact: item, owner: plan.path_owners.find(row => row.relative_path === item.relative_path)!.owner }));
  if (rust) {
    const lib = plan.artifacts.find(item => item.relative_path === "src/lib.rs")!;
    const merged = artifact("src/lib.rs", `${[...new Set([...lib.content.split("\n").filter(Boolean), "pub mod providers;"])].sort().join("\n")}\n`);
    const index = rows.findIndex(row => row.artifact.relative_path === "src/lib.rs");
    rows.splice(index, 1, { artifact: merged, owner: "whole-application-composer" });
  }
  rows.push(...providerArtifacts.map(item => ({ artifact: item, owner: ["package.json", "pyproject.toml", "Cargo.toml"].includes(item.relative_path) ? "whole-application-composer" as const : "provider-pack" as const })));
  return rows;
}

export function assertProviderApplicationPlanV1(value: unknown): asserts value is ProviderApplicationPlanV1 {
  if (value === null || typeof value !== "object" || snapshots.get(value as ProviderApplicationPlanV1) !== sha256(canonicalJson(value))) fail("DS_PROVIDER_APPLICATION_SNAPSHOT", "/plan", "provider plan was not formed by this process or changed");
}

export function composeProviderApplicationV1(whole: WholeApplicationPlanV1, rawSelection: unknown, rawIntegrationSource: unknown, route?: ProviderInboundRouteV1): ProviderApplicationPlanV1 {
  assertWholeApplicationPlan(whole);
  const selection = validateProviderPackSelectionV1(rawSelection, whole.language);
  planIntegrationProjectV2(rawIntegrationSource as IntegrationGenerationSourceV2, whole.language);
  const integrationSource = JSON.parse(canonicalJson(rawIntegrationSource)) as IntegrationGenerationSourceV2;
  if (sha256(canonicalJson(integrationSource)) !== whole.integration_source_sha256) fail("DS_PROVIDER_INTEGRATION_SOURCE", "/integration-source", "provider source differs from the whole-application binding");
  const failures = providerFailureOutcomes(integrationSource);
  const destinationEnvironmentName = publicationDestinationEnvironment(selection, integrationSource);
  const migration = providerMigrations(integrationSource);
  const dependencyRows = dependencies(selection);
  const generated = whole.language === "typescript" ? typescriptArtifacts(selection, destinationEnvironmentName, migration, failures, whole, integrationSource) : whole.language === "python" ? pythonArtifacts(selection, destinationEnvironmentName, pythonPackage(whole), migration, failures) : rustArtifacts(selection, destinationEnvironmentName, migration, failures, whole, integrationSource);
  if (route && (route.method !== "POST" || !/^\/[A-Za-z0-9/_-]+$/.test(route.path) || route.path === "/health" || route.path.includes("//"))) {
    fail("DS_PROVIDER_INBOUND_ROUTE", "/route", "reference provider requires one safe static POST route");
  }
  const routed = route ? generated.map(row => {
    if (!/\/(?:inbound-http\.ts|inbound_http\.(?:py|rs))$/.test(row.relative_path)) return row;
    const marker = '"/webhook"';
    if (row.content.split(marker).length !== 2) fail("DS_PROVIDER_INBOUND_ROUTE", `/artifacts/${row.relative_path}`, "expected exactly one default inbound route");
    return artifact(row.relative_path, row.content.replace(marker, JSON.stringify(route.path)));
  }) : generated;
  const providerArtifacts = Object.freeze([...routed, configurationSchema(selection), providerManifest(selection, dependencyRows), runtimePortManifest(integrationSource, runtimeGraphContracts(whole), selection)]);
  const rows = [...replaceRoot(whole, providerArtifacts)].sort((left, right) => left.artifact.relative_path.localeCompare(right.artifact.relative_path));
  const exact = new Map<string, string>(); const folded = new Map<string, string>();
  for (const row of rows) {
    const relative = row.artifact.relative_path;
    if (!relative || path.posix.normalize(relative) !== relative || relative.startsWith("/") || relative.includes("\\") || relative.split("/").includes("..")) fail("DS_PROVIDER_APPLICATION_PATH", `/artifacts/${relative}`, "unsafe path");
    if (exact.has(relative)) fail("DS_PROVIDER_APPLICATION_COLLISION", `/artifacts/${relative}`, `path also owned by ${exact.get(relative)}`);
    const fold = relative.toLocaleLowerCase("en-US");
    if (folded.has(fold)) fail("DS_PROVIDER_APPLICATION_CASE_COLLISION", `/artifacts/${relative}`, `case-folded collision with ${folded.get(fold)}`);
    exact.set(relative, row.owner); folded.set(fold, relative);
  }
  const body = {
    schema_version: "domainspec.provider-application-plan/v1-candidate" as const,
    language: whole.language,
    project_id: whole.project_id,
    domain_source_manifest_sha256: whole.domain_source_manifest_sha256,
    integration_source_sha256: whole.integration_source_sha256,
    compilation_selection_sha256: whole.selection_sha256,
    binding_sha256: whole.binding_sha256,
    whole_application_plan_sha256: whole.plan_sha256,
    provider_selection_sha256: providerPackSelectionSha256(selection),
    dependencies: dependencyRows,
    artifacts: Object.freeze(rows.map(row => row.artifact)),
    path_owners: Object.freeze(rows.map(row => freeze({ relative_path: row.artifact.relative_path, owner: row.owner, sha256: row.artifact.sha256 }))),
    runtime_guarantees_observed: false as const,
    claim_ceiling: "provider-code-formation-and-static-compilation-only" as const,
    authority_effect: "none" as const,
  };
  const result = freeze({ ...body, plan_sha256: sha256(canonicalJson(body)) });
  snapshots.set(result, sha256(canonicalJson(result)));
  return result;
}
