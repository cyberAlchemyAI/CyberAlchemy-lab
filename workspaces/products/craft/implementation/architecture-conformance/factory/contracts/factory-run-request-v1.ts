export const FACTORY_PURPOSES = Object.freeze([
  "reference-reproduction",
  "new-kit-proof",
] as const);

export type FactoryPurpose = typeof FACTORY_PURPOSES[number];

export type FactorySourceRefV1 = Readonly<{
  path: string;
  sha256?: string;
}>;

export type FactoryRunNodeRequestV1 = Readonly<{
  node_id: string;
  kind: "direct-proof" | "join-proof" | "projection";
  provider_id: string;
  depends_on: readonly string[];
  input_refs: readonly Readonly<{
    role: string;
    ref: FactorySourceRefV1;
  }>[];
  claim_ceiling: string;
}>;

export type FactoryRunRequestV1 = Readonly<{
  schema_version: "FactoryRunRequest/v1";
  request_id: string;
  suite_id: string;
  purpose: FactoryPurpose;
  nodes: readonly FactoryRunNodeRequestV1[];
  claim_ceiling: string;
  authority_effect: "none";
}>;
