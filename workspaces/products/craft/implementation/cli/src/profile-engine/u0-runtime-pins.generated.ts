// GENERATED from actual compiled U0 native assets. No future hashes.
// Open Questions: docs/U0-SHARED-CONTRACTS.md.
export const U0_RUNTIME_PINS_V4={
  "assets": [
    {
      "role": "decoder",
      "path": "runtime/u0-json-decode.js",
      "sha256": "2a1d448e89e3600ba9e85cb7aa2dfb5c721fe7f849077f0db0527cf4cb566859",
      "bytes": 7421,
      "exports": [
        "decodeU0Json"
      ]
    },
    {
      "role": "values",
      "path": "runtime/u0-values.js",
      "sha256": "a699b02060c5ade37e420a0432613d759f31b87386dd6c82910e32c1883d8c0c",
      "bytes": 3145,
      "exports": [
        "formU0Submission",
        "copyU0Submission"
      ]
    },
    {
      "role": "encoder",
      "path": "runtime/u0-json-encode.js",
      "sha256": "9e4c0cda10ea6757f2dbd9f3e4606eb3d52b3602aafddeb1f9010e7e05405cae",
      "bytes": 6615,
      "exports": [
        "checkU0EncoderConfiguration",
        "encodeU0Outcome",
        "encodeU0AdapterError",
        "u0WireBounds"
      ]
    },
    {
      "role": "handler",
      "path": "runtime/application-http.mjs",
      "sha256": "5ee919c322baa783aa5708ce214f99955f3e9884958b29eb828f844b0fc197be",
      "bytes": 8715,
      "exports": [
        "createU0HttpHandler",
        "inspectU0HttpResponse"
      ]
    }
  ],
  "build": {
    "node": "26.12.1",
    "typescript": "6.0.3"
  }
} as const;
