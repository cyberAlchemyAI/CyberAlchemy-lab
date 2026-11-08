export const CLI_PACKAGE_NAME = "@domainspec-v2/cli" as const;
export const CLI_VERSION = "0.0.0-candidate.5" as const;
export const FOUNDATION_CONTRACT_SCHEMA =
  "domainspec.stable-foundation-cli.foundation-contract/v3" as const;
export const SUPPORTED_NODE_VERSION = "v26.8.1" as const;
export const SUPPORTED_PLATFORM = "linux" as const;
export const SUPPORTED_ARCH = "x64" as const;
export const AUTHORITY_EFFECT = "none" as const;

export const CLI_IDENTITY = Object.freeze({
  packageName: CLI_PACKAGE_NAME,
  version: CLI_VERSION,
  foundationContractSchema: FOUNDATION_CONTRACT_SCHEMA,
  runtime: Object.freeze({
    node: SUPPORTED_NODE_VERSION,
    platform: SUPPORTED_PLATFORM,
    arch: SUPPORTED_ARCH
  }),
  authorityEffect: AUTHORITY_EFFECT
});
