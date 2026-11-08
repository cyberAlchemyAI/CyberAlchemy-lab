import {
  lstat,
  mkdtemp,
  readFile,
  readdir,
  rm,
  unlink,
  writeFile,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

import { describe, expect, it } from "vitest";

import {
  validateRawIndexV2,
  writeEvidenceBundleV2,
} from "./write-evidence-bundle-v2.js";

const bundle = (root: string, runId = "proof-example") =>
  writeEvidenceBundleV2({
    root,
    runId,
    rawInputs: {
      "definition.json": '{"schema_version":"Definition/v1"}\n',
      "provider.bin": new Uint8Array([0, 1, 2, 255]),
    },
    artifacts: {
      "evaluation.json": '{"verdict":"pass"}\n',
      "mutations/one.json": '{"status":"killed"}\n',
    },
  });

describe("generic atomic evidence bundle and raw index", () => {
  it("publishes every raw and derived byte through one reachable exact index", async () => {
    const root = await mkdtemp(join(tmpdir(), "factory-evidence-"));
    try {
      const published = await bundle(root);
      expect(published.index.entries).toHaveLength(4);
      expect(new Set(published.index.entries.map(({ role }) => role))).toEqual(
        new Set(["raw-input", "artifact"]),
      );
      await expect(
        validateRawIndexV2(published.runPath, published.index),
      ).resolves.toBeUndefined();
      expect(await readFile(
        resolve(published.runPath, "raw/definition.json"),
        "utf8",
      )).toContain("Definition/v1");
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });

  it("never publishes a partial run when pre-publication validation fails", async () => {
    const root = await mkdtemp(join(tmpdir(), "factory-evidence-partial-"));
    try {
      await expect(writeEvidenceBundleV2({
        root,
        runId: "injected-failure",
        rawInputs: { "input.json": "{}\n" },
        artifacts: { "output.json": "{}\n" },
        validate: () => {
          throw new Error("INJECTED_VALIDATION_FAILURE");
        },
      })).rejects.toThrow("INJECTED_VALIDATION_FAILURE");
      await expect(lstat(resolve(root, "injected-failure"))).rejects.toMatchObject({
        code: "ENOENT",
      });
      expect(await readdir(root)).toEqual([]);
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });

  it("detects missing, tampered, and unindexed bytes", async () => {
    const root = await mkdtemp(join(tmpdir(), "factory-evidence-hostile-"));
    try {
      const tampered = await bundle(root, "tampered");
      await writeFile(
        resolve(tampered.runPath, "artifacts/evaluation.json"),
        '{"verdict":"fail"}\n',
      );
      await expect(
        validateRawIndexV2(tampered.runPath, tampered.index),
      ).rejects.toMatchObject({
        code: "FACTORY_EVIDENCE_REFERENCED_BYTES_TAMPERED",
      });

      const missing = await bundle(root, "missing");
      await unlink(resolve(missing.runPath, "raw/definition.json"));
      await expect(
        validateRawIndexV2(missing.runPath, missing.index),
      ).rejects.toMatchObject({
        code: "FACTORY_EVIDENCE_REFERENCED_BYTES_MISSING",
      });

      const unindexed = await bundle(root, "unindexed");
      await writeFile(resolve(unindexed.runPath, "orphan.txt"), "orphan");
      await expect(
        validateRawIndexV2(unindexed.runPath, unindexed.index),
      ).rejects.toMatchObject({ code: "FACTORY_EVIDENCE_UNINDEXED_FILE" });
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });

  it("blocks path escape, empty sides, and overwrite", async () => {
    const root = await mkdtemp(join(tmpdir(), "factory-evidence-boundary-"));
    try {
      await expect(writeEvidenceBundleV2({
        root,
        runId: "escape",
        rawInputs: { "../outside": "x" },
        artifacts: { "output": "x" },
      })).rejects.toMatchObject({ code: "FACTORY_EVIDENCE_ARTIFACT_SET_INVALID" });
      await expect(writeEvidenceBundleV2({
        root,
        runId: "empty",
        rawInputs: {},
        artifacts: { "output": "x" },
      })).rejects.toMatchObject({ code: "FACTORY_EVIDENCE_ARTIFACT_SET_INVALID" });
      await bundle(root, "once");
      await expect(bundle(root, "once")).rejects.toMatchObject({
        code: "FACTORY_EVIDENCE_OVERWRITE_FORBIDDEN",
      });
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });
});
