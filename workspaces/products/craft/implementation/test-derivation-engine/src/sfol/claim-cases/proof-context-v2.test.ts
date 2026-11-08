import { createHash } from "node:crypto";
import { copyFileSync, cpSync, mkdtempSync, mkdirSync, readFileSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";

import { assessSelectedSfolProofContextV2, replaySelectedSfolProofContextV2,
  type SelectedSfolProofContextV2Selection } from "./proof-context-v2.js";
import { canonicalJson } from "../../../../cli/src/input/source-manifest.js";
import type { SelectedSfolRef } from "./index.js";

const root = fileURLToPath(new URL("../../../../../../../../", import.meta.url));
const paths = {
  clause_manifest: "auth-foundation/formalization/cases/AF-ADMIT-AUTHORIZATION-COMMAND-001/SFOL-CLAUSE-ADMISSION-MANIFEST.v1.json",
  graph: "auth-foundation/implementation/standard-conformance/command-boundary-compiled-operation-graph.json",
  build: "auth-foundation/implementation/command-boundary-runtime/.domainspec/instantiations/auth-command-boundary.admit-authorization-command.json",
  profile: "craft/projects/domainspec-v2/impl/test-derivation-engine/src/sfol/language/profiles.ts",
  scaffold: "auth-foundation/development/auth-service-d65-r2-plan/completion-v1/graph-scaffolds/command-boundary-source.json",
  source_root: "auth-foundation/implementation/command-boundary-source",
} as const;
const temps: string[] = [];
afterEach(() => { for (const path of temps.splice(0)) rmSync(path, { recursive: true, force: true }); });
const sha = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");
function ref(base: string, path: string): SelectedSfolRef {
  const bytes = readFileSync(join(base, path));
  return { path, sha256: sha(bytes), size_bytes: bytes.length };
}
function selection(base: string): SelectedSfolProofContextV2Selection {
  return {
    historical: {
      clause_manifest: ref(base, paths.clause_manifest), graph: ref(base, paths.graph),
      build: ref(base, paths.build), profile: ref(base, paths.profile), source_manifest: null,
    },
    scaffold: ref(base, paths.scaffold), source_root: paths.source_root,
  };
}
function copied(): string {
  const base = mkdtempSync(join(tmpdir(), "tde-sfol-proof-v2-"));
  temps.push(base);
  for (const path of [paths.clause_manifest, paths.graph, paths.build, paths.profile, paths.scaffold]) {
    mkdirSync(dirname(join(base, path)), { recursive: true });
    copyFileSync(join(root, path), join(base, path));
  }
  cpSync(join(root, paths.source_root), join(base, paths.source_root), { recursive: true });
  return base;
}

describe("selected SFOL proof-context v2 diagnostic", () => {
  it("matches the embedded 18-row source set while retaining historical build drift and blocked ceiling", () => {
    const selected = selection(root);
    const result = assessSelectedSfolProofContextV2(root, selected);
    expect(result.selected_source_count).toBe(18);
    expect(result.eligible_source_count).toBe(18);
    expect(result.source_alignment).toBe("match");
    expect([result.graph_status, result.profile_status, result.build_status]).toEqual(["match", "match", "drift"]);
    expect(result.status).toBe("incomplete-or-drifted");
    expect(result.neutral_set_eligible).toBe(false);
    expect(result.f5_eligibility).toBe("blocked-missing-domainspec-v4-chain");
    expect(replaySelectedSfolProofContextV2(root, selected, result)).toEqual(result);
  });

  it("rejects rehashed scaffold manifest tampering against historical pin", () => {
    const base = copied();
    const path = join(base, paths.scaffold);
    const scaffold = JSON.parse(readFileSync(path, "utf8"));
    const manifest = scaffold.graph.source_manifest;
    manifest.sources[0].size_bytes += 1;
    manifest.total_size_bytes += 1;
    manifest.aggregate_sha256 = sha(Buffer.from(manifest.sources.map((source: {
      source_type: string; source_id: string; feature_id: string | null;
      relative_path: string; size_bytes: number; sha256: string;
    }) => `${source.source_type}\t${source.source_id}\t${source.feature_id ?? "-"}\t${source.relative_path}\t${source.size_bytes}\t${source.sha256}\n`).join("")));
    const { manifest_sha256: _old, ...body } = manifest;
    manifest.manifest_sha256 = sha(Buffer.from(canonicalJson(body)));
    writeFileSync(path, JSON.stringify(scaffold));
    expect(() => assessSelectedSfolProofContextV2(base, selection(base))).toThrow(/INVALID_MANIFEST/);
  });

  it("rejects changed and missing source files", () => {
    const base = copied();
    const path = join(base, paths.source_root, "project.json");
    writeFileSync(path, `${readFileSync(path, "utf8")} `);
    expect(() => assessSelectedSfolProofContextV2(base, selection(base))).toThrow(/SOURCE_DRIFT/);
    rmSync(path);
    expect(() => assessSelectedSfolProofContextV2(base, selection(base))).toThrow(/SOURCE_DRIFT/);
  });

  it("rejects symlinked and extra eligible semantic input files", () => {
    const base = copied();
    const path = join(base, paths.source_root, "project.json");
    rmSync(path);
    symlinkSync(join(root, paths.source_root, "project.json"), path);
    expect(() => assessSelectedSfolProofContextV2(base, selection(base))).toThrow(/SOURCE_DRIFT/);
    rmSync(path);
    copyFileSync(join(root, paths.source_root, "project.json"), path);
    mkdirSync(join(base, paths.source_root, "edges"), { recursive: true });
    writeFileSync(join(base, paths.source_root, "edges/extra.json"), "{}\n");
    expect(() => assessSelectedSfolProofContextV2(base, selection(base))).toThrow(/SOURCE_DRIFT/);
  });

  it("keeps changed current build distinct from the historical raw SHA pin", () => {
    const base = copied();
    const path = join(base, paths.build);
    writeFileSync(path, `${readFileSync(path, "utf8")} `);
    expect(assessSelectedSfolProofContextV2(base, selection(base)).build_status).toBe("drift");
  });

  it("rejects a forged held result on replay", () => {
    const selected = selection(root);
    const held = assessSelectedSfolProofContextV2(root, selected);
    const forged = { ...held, build_status: "match" } as typeof held;
    expect(() => replaySelectedSfolProofContextV2(root, selected, forged)).toThrow(/REPLAY_MISMATCH/);
  });

  it("does not substitute an arbitrary local source root or hide a second selected manifest", () => {
    const selected = selection(root);
    expect(() => assessSelectedSfolProofContextV2(root,
      { ...selected, source_root: "auth-foundation/implementation/other-source" })).toThrow(/INVALID_SELECTION/);
    expect(() => assessSelectedSfolProofContextV2(root,
      { ...selected, historical: { ...selected.historical, source_manifest: selected.scaffold } })).toThrow(/INVALID_SELECTION/);
  });
});
