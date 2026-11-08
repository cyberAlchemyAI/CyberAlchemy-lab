import { createHash } from "node:crypto";
import { mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { observeLocalNativeCases, replayLocalNativeCases,
  type LocalNativeCaseSelection } from "./local-native-case-observation.js";

const roots: string[] = [];
const sha = (bytes: Buffer | string) => createHash("sha256").update(bytes).digest("hex");
const runtimeBytes = readFileSync(process.execPath);
const runtimeRef = { path: process.execPath, sha256: sha(runtimeBytes), size_bytes: runtimeBytes.length };
afterEach(() => { for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true }); });

function fixture(adapterSource = `let input='';process.stdin.setEncoding('utf8');process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>process.stdout.write(JSON.stringify({value:JSON.parse(input).value*2})+'\\n'));`) {
  const root = mkdtempSync(join(tmpdir(), "tde-local-case-fixture-")); roots.push(root);
  const put = (name: string, bytes: string) => {
    writeFileSync(join(root, name), bytes);
    return { path: name, sha256: sha(bytes), size_bytes: Buffer.byteLength(bytes) };
  };
  const adapter = put("adapter.mjs", adapterSource);
  const first = put("first.json", '{"value":2}\n');
  const second = put("second.json", '{"value":3}\n');
  const selection: LocalNativeCaseSelection = {
    schema_version: "tde.local-native-case-selection/v1-candidate", mode: "trusted-local-no-isolation",
    runtime_ref: runtimeRef,
    adapter_ref: adapter,
    cases: [{ case_id: "case-1", input_ref: first }, { case_id: "case-2", input_ref: second }],
    policy: { timeout_ms: 10_000, max_output_bytes: 4096 },
  };
  return { root, selection, put };
}

describe("trusted-local native case observation precursor", () => {
  it("runs each exact input, owns native output, and replays without any satisfying claim", async () => {
    const { root, selection } = fixture();
    const receipt = await observeLocalNativeCases(root, selection);
    expect(receipt.status).toBe("observed");
    expect(receipt.observations.map(row => Buffer.from(row.stdout_base64, "base64").toString()))
      .toEqual(['{"value":4}\n', '{"value":6}\n']);
    expect(receipt.observations.map(row => row.case_id)).toEqual(["case-1", "case-2"]);
    expect(receipt.isolation_verification).toBe("unverified");
    expect(receipt.oracle_verification).toBe("not-performed");
    expect(receipt.evf_join).toBe("forbidden");
    expect(receipt.can_satisfy_obligation).toBe(false);
    expect("normalized_outcome" in receipt).toBe(false);
    expect(await replayLocalNativeCases(root, selection, receipt)).toEqual(receipt);
  }, 30_000);

  it("rejects missing, duplicate, reordered and changed selected cases", async () => {
    const { root, selection } = fixture();
    for (const cases of [[], [selection.cases[0]!, selection.cases[0]!],
      [selection.cases[1]!, selection.cases[0]!]]) {
      await expect(observeLocalNativeCases(root, { ...selection, cases }))
        .rejects.toMatchObject({ code: "PROVIDER_SCOPE_INVALID" });
    }
    const receipt = await observeLocalNativeCases(root, selection);
    writeFileSync(join(root, "first.json"), '{"value":9}\n');
    await expect(replayLocalNativeCases(root, selection, receipt))
      .rejects.toMatchObject({ code: "TARGET_BASELINE_DRIFT" });
  }, 30_000);

  it("rejects a forged receipt even when its digest is recomputed", async () => {
    const { root, selection } = fixture();
    const receipt = await observeLocalNativeCases(root, selection);
    const forged = structuredClone(receipt) as any;
    forged.observations[0].stdout_base64 = Buffer.from('{"value":999}\n').toString("base64");
    forged.observations[0].stdout_sha256 = sha(Buffer.from(forged.observations[0].stdout_base64, "base64"));
    const { receipt_digest: _digest, ...unsigned } = forged;
    forged.receipt_digest = sha(JSON.stringify(unsigned));
    await expect(replayLocalNativeCases(root, selection, forged))
      .rejects.toMatchObject({ code: "PROVIDER_RECEIPT_TAMPERED" });
  });

  it("preserves nonzero, timeout and oversized output as incomplete observations", async () => {
    for (const [source, policy] of [
      ["process.exit(7);", { timeout_ms: 10_000, max_output_bytes: 4096 }],
      ["setTimeout(()=>{},10000);", { timeout_ms: 25, max_output_bytes: 4096 }],
      ["process.stdout.write('x'.repeat(8192));", { timeout_ms: 10_000, max_output_bytes: 32 }],
    ] as const) {
      const { root, selection } = fixture(source);
      const receipt = await observeLocalNativeCases(root, { ...selection, policy });
      expect(receipt.status).toBe("incomplete");
      expect(receipt.observations).toHaveLength(1);
      expect(receipt.can_satisfy_obligation).toBe(false);
      await expect(replayLocalNativeCases(root, selection, receipt))
        .rejects.toMatchObject({ code: "PROVIDER_RECEIPT_TAMPERED" });
    }
  }, 30_000);

  it("rejects replay drift from a nondeterministic native adapter", async () => {
    const { root, selection } = fixture("process.stdout.write(String(process.hrtime.bigint()));");
    const receipt = await observeLocalNativeCases(root, selection);
    await expect(replayLocalNativeCases(root, selection, receipt))
      .rejects.toMatchObject({ code: "PROVIDER_RECEIPT_TAMPERED" });
  }, 30_000);

  it("rejects a receipt-selected adapter before it can execute", async () => {
    const { root, selection, put } = fixture();
    const receipt = await observeLocalNativeCases(root, selection);
    const marker = join(root, "forged-adapter-ran");
    const forgedAdapter = put("forged.mjs", `import{writeFileSync}from'node:fs';writeFileSync(${JSON.stringify(marker)},'ran');`);
    const forgedSelection = { ...selection, adapter_ref: forgedAdapter };
    const forged = { ...receipt, selection: forgedSelection } as any;
    await expect(replayLocalNativeCases(root, selection, forged))
      .rejects.toMatchObject({ code: "PROVIDER_RECEIPT_TAMPERED" });
    expect(() => statSync(marker)).toThrow();
  });

  it("refuses policy fields that would falsely imply network or memory enforcement", async () => {
    const { root, selection } = fixture();
    await expect(observeLocalNativeCases(root, { ...selection,
      policy: { ...selection.policy, network: "forbidden", memory_ceiling_bytes: 1024 } } as any))
      .rejects.toMatchObject({ code: "PROVIDER_SCOPE_INVALID" });
  });

  it("terminates descendants left in the selected adapter's process group", async () => {
    const { root, selection, put } = fixture();
    const marker = join(root, "descendant-survived");
    const childSource = `setTimeout(()=>require('node:fs').writeFileSync(${JSON.stringify(marker)},'late'),500)`;
    const adapter = put("group-adapter.mjs",
      `import{spawn}from'node:child_process';spawn(process.execPath,['-e',${JSON.stringify(childSource)}],{stdio:'ignore'}).unref();process.stdout.write('observed');`);
    const receipt = await observeLocalNativeCases(root, { ...selection, adapter_ref: adapter });
    expect(receipt.status).toBe("observed");
    await new Promise(resolve => setTimeout(resolve, 750));
    expect(() => statSync(marker)).toThrow();
  });

  it("rejects selected adapter bytes changed during invocation", async () => {
    const { root, selection, put } = fixture();
    const original = join(root, "mutable-adapter.mjs");
    const adapter = put("mutable-adapter.mjs",
      `import{writeFileSync}from'node:fs';writeFileSync(${JSON.stringify(original)},'changed');process.stdout.write('observed');`);
    await expect(observeLocalNativeCases(root, { ...selection, adapter_ref: adapter }))
      .rejects.toMatchObject({ code: "TARGET_BASELINE_DRIFT" });
  });
});
