// GENERATED from actual existing bytes by tools/materialize-commerce-sdk-v5.mjs.
// Open Questions: docs/COMMERCE-SDK-V5.md. No native availability or build claim.
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'){for(const x of Object.values(v))freeze(x);Object.freeze(v);}return v;};
export const COMMERCE_SDK_PINS_V5=freeze({
  "schema_version": "craft.commerce-sdk-resource-pins/v5-candidate",
  "package_name": "@domainspec-v2/cli",
  "package_version": "1.3.0",
  "required_node": "26.8.1",
  "toolchain_observation": {
    "typescript": "7.0.2",
    "node": "26.8.1",
    "qualification": "tools-observed;public-build-receipt-still-required"
  },
  "members": [
    {
      "path": "contracts/commerce-values-v1.schema.json",
      "sha256": "c19c7733ba0c259e0bb8d10709ae66521e2ab2d14f441fba02a86127b3d76a45",
      "bytes": 36980
    },
    {
      "path": "contracts/iteration-expression-v2.schema.json",
      "sha256": "99c302eb7dc5945fd3e7884e3c1092eae1958090c514c709e73f2981e5d64666",
      "bytes": 41511
    },
    {
      "path": "contracts/commerce-entry-v1.schema.json",
      "sha256": "1383c7c274a2297a45fb094ac9cd14e4daf37741db6e5c5c0072f68e08345242",
      "bytes": 48700
    },
    {
      "path": "contracts/commerce-read-v1.schema.json",
      "sha256": "caa817b54733ef3078b73a8618ca0b9d7ef431ee569e084543acf8da77629740",
      "bytes": 47279
    },
    {
      "path": "contracts/commerce-effects-v1.schema.json",
      "sha256": "3095240afa90b48f74c0f8bf98aa31efde8f887513755aef487b434030ab3352",
      "bytes": 67268
    },
    {
      "path": "contracts/commerce-workflow-v1.schema.json",
      "sha256": "ff6d9a035ad5a0941591afc1647cece44be0a716fd486b01dc50c3742202bc32",
      "bytes": 53925
    },
    {
      "path": "contracts/profile-package-v5.schema.json",
      "sha256": "d7df9d480035ad72fa95db98441dd68d5c155c72dabad22a905176cf27f0b754",
      "bytes": 8333
    },
    {
      "path": "contracts/commerce-module-v1.schema.json",
      "sha256": "0926170386b3371435415b1e6b4fe39a6ced3c278d7e83e289f31aa337fe60f3",
      "bytes": 53298
    },
    {
      "path": "contracts/commerce-application-v1.schema.json",
      "sha256": "82cc18176dfdfed6327e60f646ced290b8d53874bf0b02022bbd932b890e30a9",
      "bytes": 10584
    },
    {
      "path": "profiles/commerce-local-v1-candidate/technical-contract.json",
      "sha256": "80a463f59e929172c1e20d0654f8024cd67298115be0af55c3c5f85d00745c78",
      "bytes": 1966
    },
    {
      "path": "profiles/commerce-local-v1-candidate/runtime/values-and-codecs.ts",
      "sha256": "b6f847e2e4b37253f6e9dfe5bdcc1edb924d99e8f62796bf58c5010f95f63148",
      "bytes": 20421
    },
    {
      "path": "profiles/commerce-local-v1-candidate/runtime/values-api-v5.ts",
      "sha256": "492fbf2e37fd7f6235664a4d12ee00bb178e530127eeb120f5f4dd007df52fdd",
      "bytes": 858
    },
    {
      "path": "profiles/commerce-local-v1-candidate/runtime/pure-api-v5.ts",
      "sha256": "bf68dfc71571fc5916e6b10edffa599ad018910aebd01a330387258c947ff7d9",
      "bytes": 3726
    }
  ],
  "authority_effect": "none"
} as const);
