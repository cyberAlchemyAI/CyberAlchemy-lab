import { createHash } from "node:crypto";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import type { GenericReplayManifestV2 } from "../contracts/generic-replay-v2.js";
import {
  createGenericReplayManifestV2,
  replayFromRawInputsV2,
} from "./generic-replay-v2.js";
import { writeEvidenceBundleV2 } from "./write-evidence-bundle-v2.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../..");
const childEntryPath =
  "projects/domainspec-v2/impl/architecture-conformance/kernel/testing/replay-fixture-child.ts";
const configPath =
  "projects/domainspec-v2/impl/architecture-conformance/kernel/testing/fixtures/replay-config.json";
const componentPath =
  "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/write-evidence-bundle-v2.ts";
const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");

const prepare = async () => {
  const root = await mkdtemp(join(tmpdir(), "generic-replay-test-"));
  const published = await writeEvidenceBundleV2({
    root,
    runId: "fixture-proof",
    rawInputs: { "a.txt": "alpha\n", "b.txt": "beta\n" },
    artifacts: { "receipt.json": '{"status":"pass"}\n' },
  });
  const expectedOutputSha256 = sha256(
    published.index.entries
      .filter(({ role }) => role === "raw-input")
      .sort((left, right) => Buffer.from(left.path).compare(Buffer.from(right.path)))
      .map(({ path, sha256: digest }) => `${path}\u0000${digest}`)
      .join("\n"),
  );
  const manifest = await createGenericReplayManifestV2({
    repositoryRoot,
    childEntryPath,
    componentPaths: { evidence_writer: componentPath },
    configPaths: { replay_fixture: configPath },
    expectedOutputSha256,
  });
  return { root, published, manifest } as const;
};

describe("generic pinned raw-input replay transport", () => {
  it("recomposes from staged raw inputs in a separate pinned child", async () => {
    const prepared = await prepare();
    try {
      const result = await replayFromRawInputsV2({
        repositoryRoot,
        runPath: prepared.published.runPath,
        rawIndex: prepared.published.index,
        rawIndexSha256: prepared.published.indexSha256,
        manifest: prepared.manifest,
      });
      expect(result.status).toBe("pass");
      expect(result.child_pid).not.toBe(process.pid);
      expect(result.claims).toEqual({
        semantic_recomposition: "pass",
        process_isolation: "pass",
        byte_identity: "not-claimed",
      });
    } finally {
      await rm(prepared.root, { recursive: true, force: true });
    }
  }, 30_000);

  it("blocks receipt-only and tampered raw inputs", async () => {
    const prepared = await prepare();
    try {
      const receiptOnly = {
        ...prepared.published.index,
        entries: prepared.published.index.entries.map((entry) => ({
          ...entry,
          role: "artifact" as const,
        })),
      };
      await expect(replayFromRawInputsV2({
        repositoryRoot,
        runPath: prepared.published.runPath,
        rawIndex: receiptOnly,
        rawIndexSha256: sha256(`${JSON.stringify(receiptOnly, null, 2)}\n`),
        manifest: prepared.manifest,
      })).rejects.toMatchObject({ code: "FACTORY_REPLAY_RECEIPT_ONLY_FORBIDDEN" });

      await writeFile(
        resolve(prepared.published.runPath, "raw/a.txt"),
        "tampered\n",
      );
      await expect(replayFromRawInputsV2({
        repositoryRoot,
        runPath: prepared.published.runPath,
        rawIndex: prepared.published.index,
        rawIndexSha256: prepared.published.indexSha256,
        manifest: prepared.manifest,
      })).rejects.toMatchObject({ code: "FACTORY_REPLAY_RAW_INPUT_TAMPERED" });
    } finally {
      await rm(prepared.root, { recursive: true, force: true });
    }
  });

  it("blocks changed component, config, and tool pins", async () => {
    const prepared = await prepare();
    try {
      const altered = (
        manifest: GenericReplayManifestV2,
        field: "component" | "config" | "tool",
      ): GenericReplayManifestV2 => field === "component"
        ? {
            ...manifest,
            components: {
              ...manifest.components,
              evidence_writer: {
                ...manifest.components.evidence_writer!,
                sha256: "0".repeat(64),
              },
            },
          }
        : field === "config"
          ? {
              ...manifest,
              configs: {
                ...manifest.configs,
                replay_fixture: {
                  ...manifest.configs.replay_fixture!,
                  sha256: "0".repeat(64),
                },
              },
            }
          : {
              ...manifest,
              toolchain: {
                ...manifest.toolchain,
                node: { ...manifest.toolchain.node, sha256: "0".repeat(64) },
              },
            };
      for (const [field, code] of [
        ["component", "FACTORY_REPLAY_COMPONENT_TAMPERED"],
        ["config", "FACTORY_REPLAY_CONFIG_TAMPERED"],
        ["tool", "FACTORY_REPLAY_TOOLCHAIN_TAMPERED"],
      ] as const) {
        await expect(replayFromRawInputsV2({
          repositoryRoot,
          runPath: prepared.published.runPath,
          rawIndex: prepared.published.index,
          rawIndexSha256: prepared.published.indexSha256,
          manifest: altered(prepared.manifest, field),
        })).rejects.toMatchObject({ code });
      }
    } finally {
      await rm(prepared.root, { recursive: true, force: true });
    }
  }, 30_000);
});
