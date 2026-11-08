import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { IntegrationGenerationLanguage } from "./integration-project-layout-v1.js";

export const REFERENCE_PROVIDER_PACK_ID = "domainspec.reference-postgresql16-nats-http/v1-candidate" as const;
export const REQUIRED_PROVIDER_CAPABILITIES = Object.freeze({
  persistence: Object.freeze(["local-transaction", "typed-query"]),
  messaging: Object.freeze(["dead-letter", "topic"]),
  outbound_http: Object.freeze(["json", "tls"]),
  inbound_http: Object.freeze(["signed-webhook", "tls"]),
} as const);
// The requirements emitted by the reference application manifests, not host detection.
export const REFERENCE_PROVIDER_RUNTIME = Object.freeze({
  typescript: Object.freeze({ node: "26.8.1" }),
  python: Object.freeze({ python: ">=3.11" }),
  rust: Object.freeze({ "rust-edition": "2024" }),
});
export const PROVIDER_CAPABILITIES = Object.freeze(["persistence", "messaging", "outbound-http", "inbound-http"] as const);
export const PROVIDER_ENVIRONMENT = Object.freeze([
  Object.freeze({ name: "DATABASE_URL", classification: "secret-reference", required: true as const }),
  Object.freeze({ name: "INBOUND_BIND_ADDRESS", classification: "endpoint-reference", required: true as const }),
  Object.freeze({ name: "NATS_URL", classification: "endpoint-reference", required: true as const }),
  Object.freeze({ name: "PAYMENT_BASE_URL", classification: "endpoint-reference", required: true as const }),
  Object.freeze({ name: "WEBHOOK_SECRET", classification: "secret-reference", required: true as const }),
] as const);

export interface ProviderEnvironmentReferenceV1 { readonly name: string; readonly classification: "endpoint-reference" | "secret-reference"; readonly required: true; }
export interface MessagingDestinationBindingV1 { readonly channel_ref: string; readonly environment_name: string; }

export interface ProviderLibraryV1 { readonly provider_id: string; readonly library: string; readonly version: string; }
export interface ProviderPackSelectionV1 {
  readonly schema_version: "domainspec.provider-pack-selection/v1-candidate";
  readonly selection_id: string;
  readonly pack_id: typeof REFERENCE_PROVIDER_PACK_ID;
  readonly language: IntegrationGenerationLanguage;
  readonly capabilities: typeof PROVIDER_CAPABILITIES;
  readonly providers: Readonly<{ persistence: ProviderLibraryV1; messaging: ProviderLibraryV1; outbound_http: ProviderLibraryV1; inbound_http: ProviderLibraryV1 }>;
  readonly configuration: Readonly<{
    environment: readonly ProviderEnvironmentReferenceV1[];
    messaging_destinations: readonly MessagingDestinationBindingV1[];
  }>;
  readonly authority_effect: "none";
}

export const REFERENCE_PROVIDER_MATRIX = Object.freeze({
  typescript: Object.freeze({
    persistence: Object.freeze({ provider_id: "postgresql:16", library: "pg", version: "8.23.0" }),
    messaging: Object.freeze({ provider_id: "nats:jetstream", library: "nats", version: "2.29.3" }),
    outbound_http: Object.freeze({ provider_id: "http:outbound", library: "platform-fetch", version: "node-26" }),
    inbound_http: Object.freeze({ provider_id: "http:inbound", library: "node-http", version: "node-26" }),
  }),
  python: Object.freeze({
    persistence: Object.freeze({ provider_id: "postgresql:16", library: "psycopg", version: "3.3.5" }),
    messaging: Object.freeze({ provider_id: "nats:jetstream", library: "nats-py", version: "2.15.0" }),
    outbound_http: Object.freeze({ provider_id: "http:outbound", library: "httpx", version: "0.28.1" }),
    inbound_http: Object.freeze({ provider_id: "http:inbound", library: "starlette", version: "1.6.0" }),
  }),
  rust: Object.freeze({
    persistence: Object.freeze({ provider_id: "postgresql:16", library: "sqlx", version: "0.9.0" }),
    messaging: Object.freeze({ provider_id: "nats:jetstream", library: "async-nats", version: "0.50.0" }),
    outbound_http: Object.freeze({ provider_id: "http:outbound", library: "reqwest", version: "0.13.5" }),
    inbound_http: Object.freeze({ provider_id: "http:inbound", library: "axum", version: "0.8.9" }),
  }),
} as const);

export class ProviderPackSelectionError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(`${code}:${pointer}:${message}`);
    this.name = "ProviderPackSelectionError";
  }
}

const snapshots = new WeakMap<ProviderPackSelectionV1, string>();
const selectionPattern = /^provider-selection:[a-z0-9]+(?:-[a-z0-9]+)*$/;
const channelPattern = /^channel:[a-z0-9]+(?:-[a-z0-9]+)*$/;
const environmentNamePattern = /^[A-Z][A-Z0-9_]*$/;

function fail(code: string, pointer: string, message: string): never { throw new ProviderPackSelectionError(code, pointer, message); }
function keys(value: unknown, expected: readonly string[], pointer: string): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) fail("DS_PROVIDER_SELECTION_SCHEMA", pointer, "closed object required");
  const actual = Object.keys(value).sort();
  if (canonicalJson(actual) !== canonicalJson([...expected].sort())) fail("DS_PROVIDER_SELECTION_SCHEMA", pointer, "unexpected, missing, or credential-valued field");
  return value as Record<string, unknown>;
}
function freeze<T>(value: T): T { if (value !== null && typeof value === "object" && !Object.isFrozen(value)) { Object.freeze(value); for (const child of Object.values(value as Record<string, unknown>)) freeze(child); } return value; }

export function validateProviderPackSelectionV1(value: unknown, language?: IntegrationGenerationLanguage): ProviderPackSelectionV1 {
  const root = keys(value, ["schema_version", "selection_id", "pack_id", "language", "capabilities", "providers", "configuration", "authority_effect"], "/");
  if (root.schema_version !== "domainspec.provider-pack-selection/v1-candidate" || root.pack_id !== REFERENCE_PROVIDER_PACK_ID || root.authority_effect !== "none") fail("DS_PROVIDER_SELECTION_SCHEMA", "/schema_version", "unsupported provider selection");
  if (root.language !== "typescript" && root.language !== "python" && root.language !== "rust") fail("DS_PROVIDER_SELECTION_LANGUAGE", "/language", "unsupported provider language");
  if (language !== undefined && root.language !== language) fail("DS_PROVIDER_SELECTION_LANGUAGE", "/language", "provider and application languages differ");
  if (typeof root.selection_id !== "string" || !selectionPattern.test(root.selection_id)) fail("DS_PROVIDER_SELECTION_SCHEMA", "/selection_id", "invalid selection identity");
  if (canonicalJson(root.capabilities) !== canonicalJson(PROVIDER_CAPABILITIES)) fail("DS_PROVIDER_SELECTION_CAPABILITY", "/capabilities", "reference pack requires the complete exact capability set");
  const providerRoot = keys(root.providers, ["persistence", "messaging", "outbound_http", "inbound_http"], "/providers");
  const expected = REFERENCE_PROVIDER_MATRIX[root.language];
  for (const role of ["persistence", "messaging", "outbound_http", "inbound_http"] as const) {
    const provider = keys(providerRoot[role], ["provider_id", "library", "version"], `/providers/${role}`);
    if (canonicalJson(provider) !== canonicalJson(expected[role])) fail("DS_PROVIDER_SELECTION_REALIZATION", `/providers/${role}`, "provider realization does not match the pinned reference matrix");
  }
  const configuration = keys(root.configuration, ["environment", "messaging_destinations"], "/configuration");
  if (!Array.isArray(configuration.environment) || configuration.environment.length <= PROVIDER_ENVIRONMENT.length) fail("DS_PROVIDER_SELECTION_CONFIGURATION", "/configuration/environment", "base environment references and at least one messaging destination reference are required");
  if (canonicalJson(configuration.environment.slice(0, PROVIDER_ENVIRONMENT.length)) !== canonicalJson(PROVIDER_ENVIRONMENT)) fail("DS_PROVIDER_SELECTION_CONFIGURATION", "/configuration/environment", "configuration must begin with the exact base environment references and contain no values");
  const environmentNames = new Set<string>();
  for (const [index, rawReference] of configuration.environment.entries()) {
    const reference = keys(rawReference, ["name", "classification", "required"], `/configuration/environment/${index}`);
    if (typeof reference.name !== "string" || !environmentNamePattern.test(reference.name) || (reference.classification !== "endpoint-reference" && reference.classification !== "secret-reference") || reference.required !== true) fail("DS_PROVIDER_SELECTION_CONFIGURATION", `/configuration/environment/${index}`, "invalid environment reference");
    if (environmentNames.has(reference.name)) fail("DS_PROVIDER_SELECTION_CONFIGURATION", `/configuration/environment/${index}/name`, "environment reference names must be unique");
    environmentNames.add(reference.name);
    if (index >= PROVIDER_ENVIRONMENT.length && reference.classification !== "endpoint-reference") fail("DS_PROVIDER_SELECTION_CONFIGURATION", `/configuration/environment/${index}/classification`, "messaging destinations must be endpoint references");
  }
  if (!Array.isArray(configuration.messaging_destinations) || configuration.messaging_destinations.length === 0) fail("DS_PROVIDER_SELECTION_CONFIGURATION", "/configuration/messaging_destinations", "at least one messaging destination binding is required");
  const channelRefs = new Set<string>();
  const destinationEnvironmentNames = new Set<string>();
  for (const [index, rawDestination] of configuration.messaging_destinations.entries()) {
    const destination = keys(rawDestination, ["channel_ref", "environment_name"], `/configuration/messaging_destinations/${index}`);
    if (typeof destination.channel_ref !== "string" || !channelPattern.test(destination.channel_ref)) fail("DS_PROVIDER_SELECTION_CONFIGURATION", `/configuration/messaging_destinations/${index}/channel_ref`, "invalid logical channel reference");
    if (typeof destination.environment_name !== "string" || !environmentNamePattern.test(destination.environment_name) || !environmentNames.has(destination.environment_name)) fail("DS_PROVIDER_SELECTION_CONFIGURATION", `/configuration/messaging_destinations/${index}/environment_name`, "destination must reference a declared environment name");
    if (channelRefs.has(destination.channel_ref)) fail("DS_PROVIDER_SELECTION_CONFIGURATION", `/configuration/messaging_destinations/${index}/channel_ref`, "logical channel destinations must be unique");
    if (destinationEnvironmentNames.has(destination.environment_name)) fail("DS_PROVIDER_SELECTION_CONFIGURATION", `/configuration/messaging_destinations/${index}/environment_name`, "destination environment names must be unique");
    channelRefs.add(destination.channel_ref); destinationEnvironmentNames.add(destination.environment_name);
  }
  const extraEnvironmentNames = new Set([...environmentNames].filter(name => !PROVIDER_ENVIRONMENT.some(reference => reference.name === name)));
  if (canonicalJson([...extraEnvironmentNames].sort()) !== canonicalJson([...destinationEnvironmentNames].sort())) fail("DS_PROVIDER_SELECTION_CONFIGURATION", "/configuration", "destination environment references and messaging bindings must have exact coverage");
  const result = freeze(structuredClone(value) as ProviderPackSelectionV1);
  snapshots.set(result, sha256(canonicalJson(result)));
  return result;
}

export function assertProviderPackSelectionV1(value: unknown): asserts value is ProviderPackSelectionV1 {
  if (value === null || typeof value !== "object" || snapshots.get(value as ProviderPackSelectionV1) !== sha256(canonicalJson(value))) fail("DS_PROVIDER_SELECTION_SNAPSHOT", "/selection", "selection was not validated by this process or has changed");
}

export function providerPackSelectionSha256(value: ProviderPackSelectionV1): string {
  assertProviderPackSelectionV1(value);
  return sha256(canonicalJson(value));
}

/** Validate explicit runtime assertions without changing the provider-selection schema. */
export function compileProviderRuntimeProfileV1(input: unknown, requirements: unknown) {
  const selection = validateProviderPackSelectionV1(input);
  const expected = REFERENCE_PROVIDER_RUNTIME[selection.language];
  keys(requirements, Object.keys(expected), "/runtime");
  if (canonicalJson(requirements) !== canonicalJson(expected)) fail("DS_PROVIDER_RUNTIME_REQUIREMENTS", "/runtime", "requirements differ from the selected pack's generated manifest");
  return freeze({ selection, requirements: expected, selection_sha256: providerPackSelectionSha256(selection),
    requirements_sha256: sha256(canonicalJson(expected)), runtime_guarantees_observed: false as const, authority_effect: "none" as const });
}

/** The named pack owns library versions; each provider role must still be selected explicitly. */
export function resolveProviderRuntimeProfileV1(input: unknown, requirements: unknown) {
  const root = keys(input, ["schema_version", "selection_id", "pack_id", "language", "capabilities", "providers", "configuration", "authority_effect"], "/");
  if (root.schema_version !== "domainspec.provider-profile-request/v1-candidate" || root.pack_id !== REFERENCE_PROVIDER_PACK_ID || root.authority_effect !== "none") fail("DS_PROVIDER_SELECTION_SCHEMA", "/", "unsupported explicit provider pack request");
  if (root.language !== "typescript" && root.language !== "python" && root.language !== "rust") fail("DS_PROVIDER_SELECTION_LANGUAGE", "/language", "unsupported provider language");
  const requested = keys(root.providers, ["persistence", "messaging", "outbound_http", "inbound_http"], "/providers");
  const matrix = REFERENCE_PROVIDER_MATRIX[root.language];
  for (const role of ["persistence", "messaging", "outbound_http", "inbound_http"] as const) {
    if (requested[role] !== matrix[role].provider_id) fail("DS_PROVIDER_SELECTION_REALIZATION", `/providers/${role}`, "explicit provider does not match the named pack and role");
  }
  return compileProviderRuntimeProfileV1({ ...root, schema_version: "domainspec.provider-pack-selection/v1-candidate", providers: matrix }, requirements);
}
