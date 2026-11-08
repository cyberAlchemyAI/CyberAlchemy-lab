import { createHash } from "node:crypto";
import { copyFileSync, mkdtempSync, mkdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";

import { assessSelectedSfolProofContext, replaySelectedSfolProofContext,
  type SelectedSfolProofContextSources } from "./proof-context.js";
import type { SelectedSfolRef } from "./index.js";

const root = fileURLToPath(new URL("../../../../../../../../", import.meta.url));
const paths = {
  clause_manifest: "auth-foundation/formalization/cases/AF-ADMIT-AUTHORIZATION-COMMAND-001/SFOL-CLAUSE-ADMISSION-MANIFEST.v1.json",
  graph: "auth-foundation/implementation/standard-conformance/command-boundary-compiled-operation-graph.json",
  build: "auth-foundation/implementation/command-boundary-runtime/.domainspec/instantiations/auth-command-boundary.admit-authorization-command.json",
  profile: "craft/projects/domainspec-v2/impl/test-derivation-engine/src/sfol/language/profiles.ts",
} as const;
const sha = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");
const tempRoots: string[] = [];
afterEach(() => { for (const path of tempRoots.splice(0)) rmSync(path, { recursive: true, force: true }); });
function ref(base: string, path: string): SelectedSfolRef {
  const bytes = readFileSync(join(base, path));
  return { path, sha256: sha(bytes), size_bytes: bytes.length };
}
function selection(base: string): SelectedSfolProofContextSources {
  return {
    clause_manifest: ref(base, paths.clause_manifest), graph: ref(base, paths.graph),
    build: ref(base, paths.build), profile: ref(base, paths.profile), source_manifest: null,
  };
}
function copied(): string {
  const base = mkdtempSync(join(tmpdir(), "tde-sfol-proof-context-"));
  tempRoots.push(base);
  for (const path of Object.values(paths)) {
    mkdirSync(dirname(join(base, path)), { recursive: true });
    copyFileSync(join(root, path), join(base, path));
  }
  return base;
}

describe("selected SFOL proof-context diagnostic", () => {
  it("reports real graph and profile matches, historical build drift, and absent source manifest", () => {
    const selected = selection(root);
    const result = assessSelectedSfolProofContext(root, selected);
    expect(result.checks.map(check => [check.role, check.status])).toEqual([
      ["graph", "match"], ["build", "drift"], ["profile", "match"], ["source_manifest", "unavailable"],
    ]);
    expect(result.status).toBe("incomplete-or-drifted");
    expect(result.f5_eligibility).toBe("blocked-missing-domainspec-v4-chain");
    expect(result.claim_ceiling).toContain("no upstream proof");
    expect(replaySelectedSfolProofContext(root, selected, result)).toEqual(result);
  });

  it("detects source drift before interpreting manifest pins", () => {
    const base = copied();
    const selected = selection(base);
    writeFileSync(join(base, paths.profile), `${readFileSync(join(base, paths.profile), "utf8")} `);
    expect(() => assessSelectedSfolProofContext(base, selected)).toThrow(/SOURCE_DRIFT/);
  });

  it("classifies a missing exact file as unavailable, not a match", () => {
    const base = copied();
    const selected = selection(base);
    rmSync(join(base, paths.profile));
    expect(assessSelectedSfolProofContext(base, selected).checks[2]?.status).toBe("unavailable");
  });

  it("does not turn a caller-rehashed, changed graph into a proof-context match", () => {
    const base = copied();
    const graphPath = join(base, paths.graph);
    const graph = JSON.parse(readFileSync(graphPath, "utf8"));
    graph.nodes = [];
    writeFileSync(graphPath, JSON.stringify(graph));
    const selected = selection(base);
    expect(statSync(graphPath).size).toBe(selected.graph.size_bytes);
    expect(assessSelectedSfolProofContext(base, selected).checks[0]?.status).toBe("drift");
  });

  it("does not accept a rehashed manifest with a forged graph pin", () => {
    const base = copied();
    const manifestPath = join(base, paths.clause_manifest);
    const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
    manifest.proof_context.graph_digest = "0".repeat(64);
    writeFileSync(manifestPath, JSON.stringify(manifest));
    const selected = selection(base);
    expect(assessSelectedSfolProofContext(base, selected).checks[0]?.status).toBe("drift");
  });

  it("rejects held-result forgery on replay", () => {
    const selected = selection(root);
    const held = assessSelectedSfolProofContext(root, selected);
    const forged = { ...held, status: "matched-selected-context" } as typeof held;
    expect(() => replaySelectedSfolProofContext(root, selected, forged)).toThrow(/REPLAY_MISMATCH/);
  });
});
