export type MetaTypeFactoryReadinessMatrix = Readonly<{
  schema_version: "MetaTypeFactoryReadinessMatrix/v1";
  status: "non-authorizing-read-model";
  counts: Readonly<{
    total: number;
    bounded_proof_complete: number;
    mapping_prerequisite: number;
    queued: number;
    owner_admission_required: number;
    owner_disposition_required: number;
    tombstone: number;
    scaffolder_ready: number;
  }>;
  meta_types: readonly unknown[];
  claim_ceiling: string;
  authority_effect: "none";
  matrix_sha256: string;
  [key: string]: unknown;
}>;

export const buildReadinessMatrix: (options?: Readonly<{
  sourceBytes?: string;
}>) => Promise<MetaTypeFactoryReadinessMatrix>;
