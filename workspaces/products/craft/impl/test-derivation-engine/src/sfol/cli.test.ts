import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { afterEach, describe, expect, it, vi } from "vitest";

import { digestSfolValue } from "./cases/index.js";
import { runSfolCli } from "./cli.js";

afterEach(() => vi.restoreAllMocks());

describe("SFOL CLI optional EVF boundary", () => {
  it("closes a v2 request without EVF and emits explicit not_requested residue", () => {
    const temporary = mkdtempSync(resolve(tmpdir(), "sfol-cli-optional-evf-"));
    try {
      const proofUnsigned = { schema_version: "proof/v1", status: "pass" };
      const requestPath = resolve(temporary, "close-v2.json");
      writeFileSync(requestPath, `${JSON.stringify({
        api_version: "domainspec-sfol-tde-api/v2",
        proof_receipt: { ...proofUnsigned, receipt_digest: digestSfolValue(proofUnsigned) }
      }, null, 2)}\n`);
      let output = "";
      vi.spyOn(process.stdout, "write").mockImplementation(((chunk: unknown) => {
        output += String(chunk);
        return true;
      }) as typeof process.stdout.write);

      expect(runSfolCli(["close", "--in", requestPath, "--check"])).toBe(0);
      expect(JSON.parse(output)).toMatchObject({ ok: true, value: { evf_status: "not_requested", detection_matrix_digest: null } });
    } finally {
      rmSync(temporary, { recursive: true, force: true });
    }
  });

  it("keeps the v1 CLI request shape EVF-required", () => {
    const temporary = mkdtempSync(resolve(tmpdir(), "sfol-cli-required-evf-"));
    try {
      const proofUnsigned = { schema_version: "proof/v1", status: "pass" };
      const requestPath = resolve(temporary, "close-v1.json");
      writeFileSync(requestPath, `${JSON.stringify({
        api_version: "domainspec-sfol-tde-api/v1",
        proof_receipt: { ...proofUnsigned, receipt_digest: digestSfolValue(proofUnsigned) }
      }, null, 2)}\n`);
      vi.spyOn(process.stderr, "write").mockImplementation((() => true) as typeof process.stderr.write);

      expect(runSfolCli(["close", "--in", requestPath, "--check"])).toBe(2);
    } finally {
      rmSync(temporary, { recursive: true, force: true });
    }
  });
});
