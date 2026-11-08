export type RawIndexEntryV2 = Readonly<{
  role: "raw-input" | "artifact";
  path: string;
  sha256: string;
  byte_length: number;
  encoding: "utf8" | "binary";
}>;

export type RawIndexV2 = Readonly<{
  schema_version: "RawIndex/v2";
  run_id: string;
  entries: readonly RawIndexEntryV2[];
  authority_effect: "none";
}>;
