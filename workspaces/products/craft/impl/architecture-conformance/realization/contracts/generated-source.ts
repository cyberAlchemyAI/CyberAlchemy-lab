export type GeneratedSourceManifest = Readonly<{
  schema_version: "GeneratedSourceManifest/v1";
  module_path: string;
  source_sha256: string;
  source_byte_length: number;
  export_name: string;
  type_name: string;
  provider_module_specifier: string;
  emitted_members: readonly Readonly<{
    member_id: string;
    target_identifier: string;
    semantic_value: string;
  }>[];
  format_version: "typescript-printer/v1";
  authority_effect: "none";
}>;

export type GeneratedSource = Readonly<{
  source: string;
  manifest: GeneratedSourceManifest;
}>;
