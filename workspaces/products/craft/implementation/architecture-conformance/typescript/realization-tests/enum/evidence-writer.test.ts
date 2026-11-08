import { mkdir, mkdtemp, readFile, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { advanceProofState, createProofState } from "../../../realization/evidence/proof-state.js";
import { writeProofRun } from "../../../realization/evidence/write-proof-run.js";

describe("proof lifecycle and atomic evidence publication", () => {
  it("permits only the complete ordered lifecycle", () => {
    let state = createProofState();
    for (const next of ["generated", "compiled", "observed", "evaluated", "mutation-killed",
      "replayed", "proof-complete"] as const) state = advanceProofState(state, next);
    expect(state.current).toBe("proof-complete");
    expect(state.diagnostics).toEqual([]);
    expect(advanceProofState(state, "proof-complete").current).toBe("blocked");
    expect(advanceProofState(createProofState(), "compiled")).toMatchObject({
      current: "blocked",
      diagnostics: ["ARCH_PROOF_STATE_TRANSITION_INVALID:prepared->compiled"],
    });
  });

  it("publishes complete bytes by validate-then-atomic-rename and never overwrites", async () => {
    const root = await mkdtemp(join(tmpdir(), "domainspec-proof-writer-"));
    try {
      const published = await writeProofRun({
        root,
        runId: "order-status-v1",
        artifacts: {
          "source/order-status.ts": "export const x = 1;\n",
          "evaluation.json": "{}\n",
          "raw-index.json": "{\"schema_version\":\"TestRawIndex/v1\"}\n",
        },
        validate: async (temporary) => {
          expect(await readFile(resolve(temporary, "evaluation.json"), "utf8")).toBe("{}\n");
        },
      });
      expect(await readFile(resolve(published.runPath, "raw-index.json"), "utf8"))
        .toContain("TestRawIndex/v1");
      await expect(writeProofRun({
        root,
        runId: "order-status-v1",
        artifacts: { "x.json": "{}" },
      })).rejects.toMatchObject({ code: "ARCH_PROOF_OVERWRITE_FORBIDDEN" });
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });

  it("blocks path escape, partial targets, symlinks, and concurrent writers", async () => {
    const root = await mkdtemp(join(tmpdir(), "domainspec-proof-writer-hostile-"));
    try {
      await expect(writeProofRun({ root, runId: "escape", artifacts: { "../x": "x" } }))
        .rejects.toMatchObject({ code: "ARCH_PROOF_ARTIFACT_PATH_INVALID" });
      await mkdir(resolve(root, ".partial.tmp-leftover"));
      await expect(writeProofRun({ root, runId: "partial", artifacts: { "x": "x" } }))
        .rejects.toMatchObject({ code: "ARCH_PROOF_PARTIAL_TARGET_EXISTS" });
      await symlink(resolve(root, "missing"), resolve(root, "linked"));
      await expect(writeProofRun({ root, runId: "linked", artifacts: { "x": "x" } }))
        .rejects.toMatchObject({ code: "ARCH_PROOF_OVERWRITE_FORBIDDEN" });
      await mkdir(resolve(root, ".busy.lock"));
      await expect(writeProofRun({ root, runId: "busy", artifacts: { "x": "x" } }))
        .rejects.toMatchObject({ code: "ARCH_PROOF_WRITER_CONFLICT" });
      await writeFile(resolve(root, "keep"), "unrelated");
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });
});
