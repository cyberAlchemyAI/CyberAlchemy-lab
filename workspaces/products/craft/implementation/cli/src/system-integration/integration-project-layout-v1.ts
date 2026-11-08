export const INTEGRATION_PROJECT_LAYOUT_V1 = Object.freeze({
  schema_version: "domainspec.integration-project-layout/v1-candidate" as const,
  application_contracts: "src/features/integration/application",
  provider_adapters: "src/integrations/providers",
  serialization_and_physical_mappings: "src/integrations/mappings",
  configuration_and_credential_references: "src/config/integrations",
  database_migrations: "migrations",
  runtime_receipts_and_observation: "src/observability/integrations",
  semantic_manifest: ".domainspec/integrations/semantic-manifest.json",
  forbidden_generic_runtime_directory: "runtime",
  authority_effect: "none" as const,
});

export type IntegrationGenerationLanguage = "typescript" | "python" | "rust";

const EXTENSION: Readonly<Record<IntegrationGenerationLanguage, "ts" | "py" | "rs">> = Object.freeze({
  typescript: "ts",
  python: "py",
  rust: "rs",
});

export interface IntegrationResponsibilityPathsV1 {
  readonly application_contracts: string;
  readonly provider_adapters: string;
  readonly mappings: string;
  readonly configuration: string;
  readonly migrations: string;
  readonly observation: string;
  readonly semantic_manifest: string;
}

export function integrationResponsibilityPathsV1(language: IntegrationGenerationLanguage): IntegrationResponsibilityPathsV1 {
  const extension = EXTENSION[language];
  if (extension === undefined) throw Object.assign(new Error("INTEGRATION_LAYOUT_LANGUAGE: unsupported language"), { code: "INTEGRATION_LAYOUT_LANGUAGE", exitCode: 22 });
  const paths = Object.freeze({
    application_contracts: `${INTEGRATION_PROJECT_LAYOUT_V1.application_contracts}/contracts.${extension}`,
    provider_adapters: `${INTEGRATION_PROJECT_LAYOUT_V1.provider_adapters}/bindings.${extension}`,
    mappings: `${INTEGRATION_PROJECT_LAYOUT_V1.serialization_and_physical_mappings}/definitions.${extension}`,
    configuration: `${INTEGRATION_PROJECT_LAYOUT_V1.configuration_and_credential_references}/manifest.${extension}`,
    migrations: `${INTEGRATION_PROJECT_LAYOUT_V1.database_migrations}/manifest.${extension}`,
    observation: `${INTEGRATION_PROJECT_LAYOUT_V1.runtime_receipts_and_observation}/observation.${extension}`,
    semantic_manifest: INTEGRATION_PROJECT_LAYOUT_V1.semantic_manifest,
  });
  if ((Object.values(paths) as readonly string[]).some(path => path === "runtime" || path.startsWith("runtime/"))) throw new Error("INTEGRATION_LAYOUT_RUNTIME_DIRECTORY_FORBIDDEN");
  return paths;
}
