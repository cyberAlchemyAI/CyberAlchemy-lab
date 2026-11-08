import { appendFileSync, copyFileSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { deriveR4CaseProjection, replayR4CaseProjection } from "./r4-case-projection.js";
import { L1_CURRENT_PROJECTION, L1_PATHS } from "./derive.js";
import { L1Error, R4_IDENTITY } from "./types.js";
import { R4_CURRENT_BINDING } from "./verify-r4-current.js";

const repoRoot = fileURLToPath(new URL("../../../../../../..", import.meta.url));

function shadowRoot(): string {
  const root = mkdtempSync(join(tmpdir(), "tde-r4-projection-"));
  const original = deriveR4CaseProjection(repoRoot);
  const binding = JSON.parse(readFileSync(resolve(repoRoot, R4_CURRENT_BINDING), "utf8")) as Record<string, unknown>;
  const manifest = JSON.parse(readFileSync(resolve(repoRoot, L1_CURRENT_PROJECTION.sourceManifest), "utf8")) as {
    inputs: { path: string }[];
  };
  const paths = new Set([
    L1_CURRENT_PROJECTION.graph, L1_CURRENT_PROJECTION.sourceManifest,
    L1_PATHS.relationshipRegistry, L1_PATHS.kindsRegistry, L1_PATHS.profile,
    R4_CURRENT_BINDING, original.algorithm_ref.path,
    ...manifest.inputs.map(item => `${L1_PATHS.featureRoot}/${item.path}`),
  ]);
  for (const value of Object.values(binding)) {
    if (value && typeof value === "object" && "path" in value && typeof value.path === "string") paths.add(value.path);
  }
  for (const path of paths) {
    const target = resolve(root, path);
    mkdirSync(dirname(target), { recursive: true });
    copyFileSync(resolve(repoRoot, path), target);
  }
  return root;
}

function expectReplayTamper(value: unknown): void {
  try {
    replayR4CaseProjection(repoRoot, value);
  } catch (error) {
    expect(error).toBeInstanceOf(L1Error);
    expect((error as L1Error).code).toBe("RECEIPT_TAMPERED");
    return;
  }
  throw new Error("expected R4 projection replay rejection");
}

describe("R4 authored case projection", () => {
  it("projects five exact current authored cases for one obligation without claiming FormalClaim or observation", () => {
    const result = deriveR4CaseProjection(repoRoot);
    expect(replayR4CaseProjection(repoRoot, result)).toEqual(result);
    expect(result.obligation_id).toBe(R4_IDENTITY.obligation_id);
    expect(result.cases).toHaveLength(5);
    expect(new Set(result.cases.map(row => row.obligation_id))).toEqual(new Set([R4_IDENTITY.obligation_id]));
    expect(result.cases.map(row => row.expected_boolean)).toEqual([true, false, false, true, true]);
    expect(result.cases.map(row => row.control_class)).toEqual([
      "truth-table", "truth-table", "truth-table", "other-date", "other-type",
    ]);
    expect(result.authority_effect).toBe("none");
    expect(result.claim_ceiling).toContain("no-formal-claim-or-runtime-observation");
    expect("derivation_status" in result).toBe(false);
    expect("formal_claim_ref" in result).toBe(false);
  });

  it("replay rejects altered source, algorithm, case, input, oracle and digest projections", () => {
    const result = deriveR4CaseProjection(repoRoot);
    const changes = [
      (item: any) => { item.graph_handle.source_set_digest = "0".repeat(64); },
      (item: any) => { item.binding_ref.sha256 = "0".repeat(64); },
      (item: any) => { item.semantic_ref.sha256 = "0".repeat(64); },
      (item: any) => { item.fixture_ref.sha256 = "0".repeat(64); },
      (item: any) => { item.algorithm_ref.sha256 = "0".repeat(64); },
      (item: any) => { item.cases.pop(); },
      (item: any) => { item.cases[0].case_id = "different-case"; },
      (item: any) => { item.cases[0].normalized_inputs.totalAppliedMakeup = 0; },
      (item: any) => { item.cases[0].expected_boolean = false; },
      (item: any) => { item.cases[0].obligation_id = "invented-obligation"; },
      (item: any) => { item.input_digest = "0".repeat(64); },
      (item: any) => { item.output_digest = "0".repeat(64); },
      (item: any) => { item.claim_ceiling = "full-runtime-equivalence"; },
    ];
    for (const change of changes) {
      const candidate = structuredClone(result);
      change(candidate);
      expectReplayTamper(candidate);
    }
  });

  it("rejects changed on-disk graph, semantic and fixture bytes in an isolated selected-source copy", () => {
    const cases = [
      [L1_CURRENT_PROJECTION.graph, "SOURCE_GRAPH_DIGEST_STALE"],
      [L1_PATHS.r4Semantic, "PREDICATE_DIGEST_STALE"],
      [L1_PATHS.r4Fixture, "FIXTURE_DIGEST_STALE"],
    ] as const;
    for (const [path, code] of cases) {
      const root = shadowRoot();
      try {
        expect(deriveR4CaseProjection(root)).toEqual(deriveR4CaseProjection(repoRoot));
        appendFileSync(resolve(root, path), " ");
        try {
          deriveR4CaseProjection(root);
        } catch (error) {
          expect(error).toBeInstanceOf(L1Error);
          expect((error as L1Error).code).toBe(code);
          continue;
        }
        throw new Error(`expected ${code} for changed ${path}`);
      } finally {
        rmSync(root, { recursive: true, force: true });
      }
    }
  });
});
