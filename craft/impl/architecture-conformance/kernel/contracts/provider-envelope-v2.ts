import type { ExactRef } from "./exact-ref.js";

export type ProviderEnvelopeV2<T> = Readonly<{
  schema_version: "ProviderEnvelope/v2";
  provider_id: string;
  provider_version: string;
  provider_config_sha256: string;
  input_refs: readonly ExactRef[];
  output_schema_version: string;
  output: Readonly<T>;
  output_sha256: string;
  unsupported_residue: readonly string[];
  claim_ceiling: string;
  envelope_sha256: string;
  authority_effect: "none";
}>;
