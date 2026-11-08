export type ExactRef = Readonly<{
  id: string;
  schema_version: string;
  sha256: string;
}>;

export type ExactRefResolver = (
  ref: ExactRef,
) => string | Promise<string>;
