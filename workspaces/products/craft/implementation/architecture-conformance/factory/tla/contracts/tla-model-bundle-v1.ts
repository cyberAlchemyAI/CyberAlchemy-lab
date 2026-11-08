export type TlaModelFileOriginV1 = "copied" | "domainspec-authored";

export type TlaModelFileProvenanceV1 = Readonly<{
  upstream_repository_url: string;
  source_commit: string;
  upstream_path: string;
  license_id: string;
  license_sha256: string;
  notice_sha256: string;
  origin: TlaModelFileOriginV1;
}>;

export type TlaModelFileV1 = Readonly<{
  path: string;
  utf8_bytes: number;
  sha256: string;
  content: string;
  provenance: TlaModelFileProvenanceV1;
}>;

export type TlaModelBundleV1 = Readonly<{
  schema_version: "TlaModelBundle/v1";
  bundle_id: string;
  corpus_id: string;
  corpus_version: string;
  files: readonly TlaModelFileV1[];
  claim_ceiling: string;
  authority_effect: "none";
}>;
