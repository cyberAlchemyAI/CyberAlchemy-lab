import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { resolve } from "node:path";
import { afterEach, describe, expect, it } from "vitest";

import { canonicalize } from "../contract-publication.js";
import {
  compareExactSets,
  createExactSet,
  diagnostic,
  logicalIdentityKey,
  sha256,
  validateArtifactHandle,
  validateExactSet,
  validateRedFixtureBundle,
  type ArtifactHandle,
  type AuthorityClass,
  type LogicalIdentity,
  type RedFixtureCase,
  type RedFixtureFreezeReceipt,
  type RedFixtureManifest,
} from "./validate-semantics.js";

const temporaryRoots: string[] = [];

afterEach(() => {
  for (const root of temporaryRoots.splice(0)) {
    rmSync(root, { recursive: true, force: true });
  }
});

function identity(kind: string, key: string): LogicalIdentity {
  return {
    schema_version: "bte-logical-identity/v1",
    domain: "domainspec-v2",
    namespace: "bte.dev",
    kind,
    key,
    version: 1,
  };
}

function authority(ownerKey = "development-validation"): AuthorityClass {
  return {
    schema_version: "bte-authority-class/v1",
    class: "evidence",
    owner: identity("producer", ownerKey),
    owner_digest: sha256(ownerKey),
  };
}

function fixtureRoot(): string {
  const root = mkdtempSync(resolve(tmpdir(), "domainspec-bte-l0b-"));
  temporaryRoots.push(root);
  mkdirSync(resolve(root, "fixtures"));
  return root;
}

function handle(
  root: string,
  path: string,
  options: {
    key?: string;
    producer?: string;
    authority?: AuthorityClass;
    schemaId?: string;
  } = {},
): ArtifactHandle {
  const bytes = readFileSync(resolve(root, path));
  const producer = options.producer ?? "development-validation";
  return {
    schema_version: "bte-artifact-handle/v1",
    root_id: "test-root",
    path,
    schema_id: options.schemaId ?? "urn:domainspec-v2:bte:fixture:v1",
    logical_identity: identity("fixture", options.key ?? path.replaceAll("/", "-")),
    sha256: sha256(bytes),
    bytes: bytes.byteLength,
    producer: {
      id: producer,
      version: "1.0.0",
      digest: sha256(producer),
    },
    authority: options.authority ?? authority(),
  };
}

describe("L0B semantic validation", () => {
  it("validates contained artifact bytes and rejects digest, producer, root, and traversal substitutions", () => {
    const root = fixtureRoot();
    writeFileSync(resolve(root, "fixtures/subject.json"), "{}\n");
    const exact = handle(root, "fixtures/subject.json");
    expect(validateArtifactHandle(exact, { "test-root": root })).toEqual({
      result: "pass",
      diagnostics: [],
    });

    const wrongDigest = structuredClone(exact);
    wrongDigest.sha256 = "0".repeat(64);
    expect(validateArtifactHandle(wrongDigest, { "test-root": root }).diagnostics.map(({ code }) => code))
      .toContain("BTE_DIGEST_MISMATCH");

    expect(
      validateArtifactHandle(exact, { "test-root": root }, { expectedProducer: "other" })
        .diagnostics.map(({ code }) => code),
    ).toContain("BTE_PRODUCER_MISMATCH");

    const undeclared = structuredClone(exact);
    undeclared.root_id = "missing-root";
    expect(validateArtifactHandle(undeclared, { "test-root": root }).diagnostics.map(({ code }) => code))
      .toContain("BTE_ROOT_UNDECLARED");

    const traversal = structuredClone(exact);
    traversal.path = "../subject.json";
    expect(validateArtifactHandle(traversal, { "test-root": root }).diagnostics.map(({ code }) => code))
      .toContain("BTE_PATH_TRAVERSAL");
  });

  it("rejects a symlink even when it points to bytes inside the declared root", () => {
    const root = fixtureRoot();
    writeFileSync(resolve(root, "fixtures/subject.json"), "{}\n");
    symlinkSync("subject.json", resolve(root, "fixtures/alias.json"));
    const aliased = handle(root, "fixtures/alias.json", { key: "alias" });
    expect(validateArtifactHandle(aliased, { "test-root": root }).diagnostics.map(({ code }) => code))
      .toContain("BTE_PATH_SYMLINK_ESCAPE");
  });

  it("recomputes exact-set membership and reports missing and extra identities", () => {
    const first = { logical_identity: identity("member", "a"), content_sha256: sha256("a") };
    const second = { logical_identity: identity("member", "b"), content_sha256: sha256("b") };
    const expected = createExactSet(identity("set", "expected"), [first, second]);
    const actual = createExactSet(identity("set", "actual"), [first]);
    expect(validateExactSet(expected)).toEqual({ result: "pass", diagnostics: [] });
    expect(compareExactSets(expected, actual).diagnostics.map(({ code }) => code))
      .toContain("BTE_RECOMPOSITION_MISSING");

    const extra = createExactSet(identity("set", "extra"), [
      first,
      { logical_identity: identity("member", "c"), content_sha256: sha256("c") },
    ]);
    expect(compareExactSets(actual, extra).diagnostics.map(({ code }) => code))
      .toContain("BTE_RECOMPOSITION_EXTRA");

    const stale = structuredClone(expected);
    stale.membership_digest = "0".repeat(64);
    expect(validateExactSet(stale).diagnostics.map(({ code }) => code))
      .toContain("BTE_DIGEST_MISMATCH");
  });

  it("accepts a development red bundle and detects stale, rewritten, and self-authored expectations", () => {
    const root = fixtureRoot();
    const publication = { schema_version: "dev-publication/v1", result: "pass" };
    const publicationBytes = `${canonicalize(publication)}\n`;
    writeFileSync(resolve(root, "publication.json"), publicationBytes);
    const publicationSha = sha256(publicationBytes);

    const fixtureBytes = '{"bad":"digest"}\n';
    writeFileSync(resolve(root, "fixtures/digest-mismatch.json"), fixtureBytes);
    const expectedDiagnostic = diagnostic(
      "BTE_DIGEST_MISMATCH",
      "digest-mismatch",
      "fixture digest must not match its declared content",
    );
    const redCase: RedFixtureCase = {
      case_id: "digest-mismatch",
      subject_contract_id: "urn:domainspec-v2:bte:artifact-handle:v1",
      fixture: handle(root, "fixtures/digest-mismatch.json"),
      expected_diagnostic: expectedDiagnostic,
    };
    const owner = authority();
    const manifest: RedFixtureManifest = {
      schema_version: "bte-red-fixture-manifest/v1",
      manifest_id: identity("manifest", "development-red-cases"),
      contract_publication_sha256: publicationSha,
      validation_owner: owner,
      cases: [redCase],
    };
    const manifestBytes = `${canonicalize(manifest)}\n`;
    writeFileSync(resolve(root, "manifest.json"), manifestBytes);
    const frozenCases = createExactSet(identity("set", "development-red-cases"), [
      {
        logical_identity: {
          schema_version: "bte-logical-identity/v1",
          domain: "domainspec-v2",
          namespace: "bte.red-fixtures",
          kind: "red-case",
          key: redCase.case_id,
          version: 1,
        },
        content_sha256: sha256(canonicalize(redCase)),
      },
    ]);
    const freeze: RedFixtureFreezeReceipt = {
      schema_version: "bte-red-fixture-freeze-receipt/v1",
      receipt_id: identity("receipt", "development-red-cases"),
      manifest_handle: handle(root, "manifest.json", {
        key: "development-red-cases",
        schemaId: "urn:domainspec-v2:bte:red-fixture-manifest:v1",
      }),
      contract_publication_receipt_handle: handle(root, "publication.json", {
        key: "development-publication",
        schemaId: "urn:domainspec-v2:bte:contract-publication-receipt:v1",
      }),
      validation_owner: owner,
      frozen_cases: frozenCases,
      admission: "not-granted",
    };

    expect(
      validateRedFixtureBundle({
        manifest,
        freeze,
        roots: { "test-root": root },
        publicationReceiptSha256: publicationSha,
        implementationProducerIds: ["bte-semantic-validator"],
      }),
    ).toEqual({ result: "pass", diagnostics: [] });

    const staleManifest = structuredClone(manifest);
    staleManifest.contract_publication_sha256 = "0".repeat(64);
    expect(
      validateRedFixtureBundle({
        manifest: staleManifest,
        freeze,
        roots: { "test-root": root },
        publicationReceiptSha256: publicationSha,
      }).diagnostics.map(({ code }) => code),
    ).toContain("BTE_CONTRACT_STALE");

    const selfAuthored = structuredClone(manifest);
    selfAuthored.validation_owner = authority("bte-semantic-validator");
    const selfFreeze = structuredClone(freeze);
    selfFreeze.validation_owner = selfAuthored.validation_owner;
    expect(
      validateRedFixtureBundle({
        manifest: selfAuthored,
        freeze: selfFreeze,
        roots: { "test-root": root },
        publicationReceiptSha256: publicationSha,
        implementationProducerIds: ["bte-semantic-validator"],
      }).diagnostics.map(({ code }) => code),
    ).toContain("BTE_EXPECTATION_SELF_AUTHORED");

    const rewritten = structuredClone(manifest);
    rewritten.cases[0]!.expected_diagnostic.detail = "changed after freeze";
    expect(
      validateRedFixtureBundle({
        manifest: rewritten,
        freeze,
        roots: { "test-root": root },
        publicationReceiptSha256: publicationSha,
      }).diagnostics.map(({ code }) => code),
    ).toContain("BTE_EXPECTATION_REWRITTEN");
  });

  it("keeps diagnostics stable and precedence ordered", () => {
    const first = diagnostic("BTE_PATH_TRAVERSAL", "subject", "first");
    const second = diagnostic("BTE_DIGEST_MISMATCH", "subject", "second");
    expect(second.precedence).toBeLessThan(first.precedence);
    expect(logicalIdentityKey(identity("case", "stable"))).toBe(
      "domainspec-v2/bte.dev/case/stable/1",
    );
  });
});

