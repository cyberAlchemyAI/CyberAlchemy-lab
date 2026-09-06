import type { TlaCaseManifestV1 } from "./contracts/tla-case-manifest-v1.js";
import type {
  TlaModelBundleV1,
  TlaModelFileProvenanceV1,
  TlaModelFileV1,
} from "./contracts/tla-model-bundle-v1.js";
import {
  canonicalJson,
  exactKeys,
  fail,
  isRecord,
  safeRelativePath,
  sha256,
} from "../shared/canonical.js";

const idPattern = /^[a-z0-9][a-z0-9._-]*$/u;
const sha256Pattern = /^[a-f0-9]{64}$/u;
const commitPattern = /^[a-f0-9]{40,64}$/u;
const drivePathPattern = /^[A-Za-z]:\//u;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

const string = (value: unknown, detail: string): string =>
  typeof value === "string" && value.length > 0
    ? value
    : fail("FACTORY_TLA_MODEL_BUNDLE_INVALID", detail);

const safeVirtualPath = (value: string): boolean =>
  safeRelativePath(value) && !drivePathPattern.test(value) && !value.includes("\0");

const parseCanonical = (source: string): unknown => {
  if (typeof source !== "string" || source.length === 0) {
    fail("FACTORY_TLA_CONTRACT_NON_CANONICAL", "source");
  }
  let value: unknown;
  try {
    value = JSON.parse(source);
  } catch {
    fail("FACTORY_TLA_CONTRACT_NON_CANONICAL", "json");
  }
  if (canonicalJson(value) !== source) {
    fail("FACTORY_TLA_CONTRACT_NON_CANONICAL", "bytes");
  }
  return value;
};

const decodeProvenance = (value: unknown): TlaModelFileProvenanceV1 => {
  const record = isRecord(value)
    ? value
    : fail("FACTORY_TLA_MODEL_BUNDLE_INVALID", "provenance");
  exactKeys(record, [
    "upstream_repository_url",
    "source_commit",
    "upstream_path",
    "license_id",
    "license_sha256",
    "notice_sha256",
    "origin",
  ], "FACTORY_TLA_MODEL_BUNDLE_INVALID");
  const repositoryUrl = string(record.upstream_repository_url, "repository-url");
  const sourceCommit = string(record.source_commit, "source-commit");
  const upstreamPath = string(record.upstream_path, "upstream-path");
  const origin = record.origin === "copied" || record.origin === "domainspec-authored"
    ? record.origin
    : fail("FACTORY_TLA_MODEL_BUNDLE_INVALID", "provenance-origin");
  if (!URL.canParse(repositoryUrl) || !commitPattern.test(sourceCommit) ||
      !safeVirtualPath(upstreamPath) || !sha256Pattern.test(string(record.license_sha256, "license-sha256")) ||
      !sha256Pattern.test(string(record.notice_sha256, "notice-sha256"))) {
    fail("FACTORY_TLA_MODEL_BUNDLE_INVALID", "provenance");
  }
  return Object.freeze({
    upstream_repository_url: repositoryUrl,
    source_commit: sourceCommit,
    upstream_path: upstreamPath,
    license_id: string(record.license_id, "license-id"),
    license_sha256: record.license_sha256 as string,
    notice_sha256: record.notice_sha256 as string,
    origin,
  });
};

const decodeFile = (value: unknown): TlaModelFileV1 => {
  const record = isRecord(value)
    ? value
    : fail("FACTORY_TLA_MODEL_BUNDLE_INVALID", "file");
  exactKeys(record, ["path", "utf8_bytes", "sha256", "content", "provenance"],
    "FACTORY_TLA_MODEL_BUNDLE_INVALID");
  const path = string(record.path, "path");
  if (!safeVirtualPath(path) || (!path.endsWith(".tla") && !path.endsWith(".cfg"))) {
    fail("FACTORY_TLA_BUNDLE_PATH_INVALID", path);
  }
  const content = string(record.content, "content");
  if (!content.endsWith("\n") || content.includes("\r")) {
    fail("FACTORY_TLA_MODEL_BUNDLE_INVALID", "content-newline");
  }
  const utf8Bytes = Buffer.byteLength(content, "utf8");
  if (record.utf8_bytes !== utf8Bytes || record.sha256 !== sha256(content)) {
    fail("FACTORY_TLA_MODEL_BUNDLE_INVALID", "content-identity");
  }
  return Object.freeze({
    path,
    utf8_bytes: utf8Bytes,
    sha256: record.sha256 as string,
    content,
    provenance: decodeProvenance(record.provenance),
  });
};

export const decodeTlaModelBundleV1 = (source: string): TlaModelBundleV1 => {
  const value = parseCanonical(source);
  const record = isRecord(value)
    ? value
    : fail("FACTORY_TLA_MODEL_BUNDLE_INVALID", "root");
  exactKeys(record, [
    "schema_version",
    "bundle_id",
    "corpus_id",
    "corpus_version",
    "files",
    "claim_ceiling",
    "authority_effect",
  ], "FACTORY_TLA_MODEL_BUNDLE_INVALID");
  const fileValues = Array.isArray(record.files)
    ? record.files
    : fail("FACTORY_TLA_MODEL_BUNDLE_INVALID", "files");
  if (record.schema_version !== "TlaModelBundle/v1" || record.authority_effect !== "none" ||
      !idPattern.test(string(record.bundle_id, "bundle-id")) ||
      !idPattern.test(string(record.corpus_id, "corpus-id")) ||
      fileValues.length === 0) {
    fail("FACTORY_TLA_MODEL_BUNDLE_INVALID", "header");
  }
  const files = fileValues.map((item: unknown) => decodeFile(item));
  const paths = files.map(({ path }) => path);
  if (!paths.every((path, index) => index === 0 || compareUtf8(paths[index - 1]!, path) < 0)) {
    fail("FACTORY_TLA_BUNDLE_PATH_INVALID", "duplicate-or-order");
  }
  return Object.freeze({
    schema_version: "TlaModelBundle/v1",
    bundle_id: record.bundle_id as string,
    corpus_id: record.corpus_id as string,
    corpus_version: string(record.corpus_version, "corpus-version"),
    files: Object.freeze(files),
    claim_ceiling: string(record.claim_ceiling, "claim-ceiling"),
    authority_effect: "none",
  });
};

export const assertTlaManifestBundleClosureV1 = (
  manifest: TlaCaseManifestV1,
  bundle: TlaModelBundleV1,
): void => {
  if (manifest.corpus_id !== bundle.corpus_id ||
      manifest.corpus_version !== bundle.corpus_version ||
      manifest.model_bundle_sha256 !== sha256(canonicalJson(bundle))) {
    fail("FACTORY_TLA_INPUT_JOIN_INVALID", "identity");
  }
  const referenced = [...new Set(manifest.cases.flatMap((entry) =>
    [...entry.module_paths, entry.config_path]))].sort(compareUtf8);
  const actual = bundle.files.map(({ path }) => path);
  if (canonicalJson(referenced) !== canonicalJson(actual)) {
    fail("FACTORY_TLA_INPUT_JOIN_INVALID", "file-closure");
  }
};
