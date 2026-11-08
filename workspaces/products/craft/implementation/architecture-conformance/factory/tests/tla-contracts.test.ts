import { describe, expect, it } from "vitest";

import { decodeTlaCaseManifestV1 } from "../tla/decode-tla-case-manifest-v1.js";
import {
  assertTlaManifestBundleClosureV1,
  decodeTlaModelBundleV1,
} from "../tla/decode-tla-model-bundle-v1.js";
import { canonicalJson, sha256 } from "../shared/canonical.js";

const digest = "a".repeat(64);
const commit = "b".repeat(40);

const provenance = (upstreamPath: string) => ({
  upstream_repository_url: "https://example.invalid/formal-models.git",
  source_commit: commit,
  upstream_path: upstreamPath,
  license_id: "Apache-2.0",
  license_sha256: digest,
  notice_sha256: digest,
  origin: "copied" as const,
});

const modelContent = "---- MODULE Example ----\n====\n";
const configContent = "SPECIFICATION Spec\nINVARIANT TypeOK\n";

const baseBundle = () => ({
  schema_version: "TlaModelBundle/v1",
  bundle_id: "example.bundle.v1",
  corpus_id: "example.corpus",
  corpus_version: "1.0.0",
  files: [
    {
      path: "models/Example.cfg",
      utf8_bytes: Buffer.byteLength(configContent, "utf8"),
      sha256: sha256(configContent),
      content: configContent,
      provenance: provenance("upstream/Example.cfg"),
    },
    {
      path: "models/Example.tla",
      utf8_bytes: Buffer.byteLength(modelContent, "utf8"),
      sha256: sha256(modelContent),
      content: modelContent,
      provenance: provenance("upstream/Example.tla"),
    },
  ],
  claim_ceiling: "fixture identity only",
  authority_effect: "none",
});

const baseManifest = (bundleSha256: string) => ({
  schema_version: "TlaCaseManifest/v1",
  manifest_id: "example.manifest.v1",
  corpus_id: "example.corpus",
  corpus_version: "1.0.0",
  model_bundle_sha256: bundleSha256,
  execution_policy: {
    worker_count: 1,
    fingerprint_index: null,
    seed: null,
    network_access: "forbidden",
    environment: [],
  },
  cases: [{
    case_id: "example.corpus.base",
    accounting_id: "example.corpus.base",
    proof_role: "obligation",
    module_paths: ["models/Example.tla"],
    config_path: "models/Example.cfg",
    spec_name: "Spec",
    expected_class: "BOUNDED_NO_COUNTEREXAMPLE",
    expected_exit_status: 0,
    expected_property: null,
    required_trace_markers: [],
    finding_code: null,
    timeout_ms: 120_000,
    output_limit_bytes: 1_048_576,
    state_limit: 100_000,
  }],
  claim_ceiling: "bounded fixture evidence only",
  authority_effect: "none",
});

describe("TLA canonical contracts", () => {
  it("decodes and deeply freezes a closed manifest and bundle", () => {
    const bundleSource = canonicalJson(baseBundle());
    const manifestSource = canonicalJson(baseManifest(sha256(bundleSource)));
    const manifest = decodeTlaCaseManifestV1(manifestSource);
    const bundle = decodeTlaModelBundleV1(bundleSource);

    expect(Object.isFrozen(manifest)).toBe(true);
    expect(Object.isFrozen(manifest.execution_policy)).toBe(true);
    expect(Object.isFrozen(manifest.execution_policy.environment)).toBe(true);
    expect(Object.isFrozen(manifest.cases)).toBe(true);
    expect(Object.isFrozen(manifest.cases[0])).toBe(true);
    expect(Object.isFrozen(manifest.cases[0]!.module_paths)).toBe(true);
    expect(Object.isFrozen(bundle)).toBe(true);
    expect(Object.isFrozen(bundle.files)).toBe(true);
    expect(Object.isFrozen(bundle.files[0]!.provenance)).toBe(true);
    expect(() => assertTlaManifestBundleClosureV1(manifest, bundle)).not.toThrow();
  });

  it("rejects noncanonical bytes and closed-shape violations", () => {
    const bundle = baseBundle();
    const canonical = canonicalJson(bundle);
    expect(() => decodeTlaModelBundleV1(`${canonical}\r\n`))
      .toThrow("FACTORY_TLA_CONTRACT_NON_CANONICAL");
    expect(() => decodeTlaModelBundleV1(JSON.stringify(bundle, null, 2)))
      .toThrow("FACTORY_TLA_CONTRACT_NON_CANONICAL");

    const unknown = { ...baseManifest(digest), invented: true };
    expect(() => decodeTlaCaseManifestV1(canonicalJson(unknown)))
      .toThrow("FACTORY_TLA_CASE_MANIFEST_INVALID");
  });

  it("rejects unsafe, duplicate, and identity-invalid virtual files", () => {
    for (const path of ["../escape.tla", "/absolute.tla", "C:/drive.tla", "bad\\path.tla"]) {
      const bundle = baseBundle();
      bundle.files[1]!.path = path;
      expect(() => decodeTlaModelBundleV1(canonicalJson(bundle)))
        .toThrow("FACTORY_TLA_BUNDLE_PATH_INVALID");
    }

    const duplicate = baseBundle();
    duplicate.files[1]!.path = duplicate.files[0]!.path;
    expect(() => decodeTlaModelBundleV1(canonicalJson(duplicate)))
      .toThrow("FACTORY_TLA_BUNDLE_PATH_INVALID");

    const digestMismatch = baseBundle();
    digestMismatch.files[0]!.sha256 = digest;
    expect(() => decodeTlaModelBundleV1(canonicalJson(digestMismatch)))
      .toThrow("FACTORY_TLA_MODEL_BUNDLE_INVALID");

    const missingNewline = baseBundle();
    missingNewline.files[0]!.content = missingNewline.files[0]!.content.trimEnd();
    missingNewline.files[0]!.utf8_bytes = Buffer.byteLength(missingNewline.files[0]!.content);
    missingNewline.files[0]!.sha256 = sha256(missingNewline.files[0]!.content);
    expect(() => decodeTlaModelBundleV1(canonicalJson(missingNewline)))
      .toThrow("FACTORY_TLA_MODEL_BUNDLE_INVALID");
  });

  it("rejects duplicate, foreign, and cross-corpus case identities", () => {
    const duplicate = baseManifest(digest);
    duplicate.cases.push(structuredClone(duplicate.cases[0]!));
    expect(() => decodeTlaCaseManifestV1(canonicalJson(duplicate)))
      .toThrow("FACTORY_TLA_CASE_ID_INVALID");

    for (const caseId of ["base", "foreign.corpus.base", "Example.corpus.base"]) {
      const manifest = baseManifest(digest);
      manifest.cases[0]!.case_id = caseId;
      expect(() => decodeTlaCaseManifestV1(canonicalJson(manifest)))
        .toThrow("FACTORY_TLA_CASE_ID_INVALID");
    }
  });

  it("rejects case nullability, timeout, and ordered-set drift", () => {
    const mutant = baseManifest(digest);
    Object.assign(mutant.cases[0]!, {
      case_id: "example.corpus.mutant",
      accounting_id: "example.corpus.mutant",
      proof_role: "mutant",
      expected_class: "EXPECTED_NAMED_COUNTEREXAMPLE",
      expected_exit_status: 12,
      expected_property: "TypeOK",
      required_trace_markers: ["Second", "First"],
      finding_code: "FINDING_EXAMPLE",
    });
    expect(() => decodeTlaCaseManifestV1(canonicalJson(mutant)))
      .toThrow("FACTORY_TLA_CASE_MANIFEST_INVALID");

    const wrongTimeout = baseManifest(digest);
    wrongTimeout.cases[0]!.timeout_ms = 1;
    expect(() => decodeTlaCaseManifestV1(canonicalJson(wrongTimeout)))
      .toThrow("FACTORY_TLA_CASE_MANIFEST_INVALID");
  });

  it("rejects manifest/bundle identity and exact file-closure drift", () => {
    const bundleSource = canonicalJson(baseBundle());
    const bundle = decodeTlaModelBundleV1(bundleSource);

    const wrongDigest = decodeTlaCaseManifestV1(canonicalJson(baseManifest(digest)));
    expect(() => assertTlaManifestBundleClosureV1(wrongDigest, bundle))
      .toThrow("FACTORY_TLA_INPUT_JOIN_INVALID");

    const manifestValue = baseManifest(sha256(bundleSource));
    manifestValue.cases[0]!.module_paths = ["models/Foreign.tla"];
    const wrongClosure = decodeTlaCaseManifestV1(canonicalJson(manifestValue));
    expect(() => assertTlaManifestBundleClosureV1(wrongClosure, bundle))
      .toThrow("FACTORY_TLA_INPUT_JOIN_INVALID");
  });
});
