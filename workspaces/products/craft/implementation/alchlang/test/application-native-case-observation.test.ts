import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";
import { finalizeApplicationExecutionRequest } from "../src/application-execution-request.js";
import { assertApplicationNativeCasesCurrent, observeApplicationNativeCases } from "../src/application-native-case-observation.js";

type Ref = { path: string; sha256: string; size_bytes: number; current: true };
const sha = (value: string | Buffer) => createHash("sha256").update(value).digest("hex");
const nodeBytes = readFileSync(process.execPath);
const localExecutable: Ref = { path: process.execPath, sha256: sha(nodeBytes), size_bytes: nodeBytes.length, current: true };
const canonical = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") {
    const item = value as Record<string, unknown>;
    return `{${Object.keys(item).sort().map(key => `${JSON.stringify(key)}:${canonical(item[key])}`).join(",")}}`;
  }
  return JSON.stringify(value) ?? "null";
};
const adapterSource = (body = "process.stdout.write(JSON.stringify({case_id: row.case_id, native_output: row.normalized_inputs.value * 2}));") =>
  `#!/usr/bin/env node\nlet text = ""; process.stdin.on("data", chunk => text += chunk); process.stdin.on("end", () => { const row = JSON.parse(text); ${body} });\n`;

function fixture(script = adapterSource(), timeoutMs = 1000, maxOutputBytes = 10000) {
  const sources = new Map<string, Buffer>();
  const putBytes = (path: string, bytes: Buffer): Ref => {
    sources.set(path, bytes);
    return { path, sha256: sha(bytes), size_bytes: bytes.length, current: true };
  };
  const put = (path: string, value: unknown): Ref => putBytes(path, Buffer.from(`${JSON.stringify(value)}\n`));
  const claim = put("fixture/claim.json", { schema_version: "synthetic-claim", claim_id: "claim-1" });
  const profile = put("fixture/derivation-profile.json", { id: "synthetic-profile" });
  const route = put("fixture/route.json", { route_id: "route:tde" });
  const provider = put("fixture/provider.json", { provider_id: "synthetic-provider" });
  const policy = put("fixture/capability-policy.json", { policy_id: "synthetic-policy" });
  const capability = put("fixture/capability.json", {
    schema_version: "domainspec-v2.formal-claim-capability-assessment/v1-candidate", assessment_id: "synthetic-capability",
    owner: "validation-governance", formal_claim_ref: claim, policy_ref: policy, classification: "executable-bounded",
    needs_formal_reasons: [], admitted_for_tde_execution: true, provider_route: "tde", currentness: "current",
    authority_effect: "none", claim_ceiling: "classification-and-routing-only-no-execution-claim",
  });
  const runtime = put("fixture/runtime.json", {
    schema_version: "domainspec-v2.provider-runtime-binding/v1-candidate", runtime_binding_id: "runtime-1",
    provider_owner: "fixture-owner", provider_id: "synthetic-provider", provider_version: "1",
    provider_digest: sha("synthetic-provider"), profile_ref: provider, input_artifact_ref: route,
    command: ["synthetic-provider"], working_directory: "run", environment_allowlist: [], fixture_refs: [],
    limits: { timeout_ms: timeoutMs, memory_ceiling_bytes: 1000000, max_output_bytes: maxOutputBytes },
    network: "forbidden", supported_outcomes: ["passed", "failed"], currentness: "current",
    authority_effect: "none", claim_ceiling: "runtime-binding-only-no-execution-claim",
  });
  const context = put("fixture/context.json", {
    schema_version: "domainspec-v2.evaluation-context/v1-candidate", context_id: "synthetic-context", version: "1",
    status: "accepted", formal_claim_ref: claim, interpretation_model_ref: null, route_binding_ref: route,
    provider_profile_ref: provider, runtime_ref: runtime, assumptions: [], limits: ["synthetic finite cases"],
    context_ceiling: "synthetic only", authority_effect: "none",
  });
  const base = put("fixture/base-request.json", {
    schema_version: "alchlang.verification-request/v1-candidate", request_id: "synthetic-request", request_state: "ready",
    formal_claim_ref: claim, evaluation_context_ref: context, route_binding_ref: route, provider_profile_ref: provider,
    runtime_ref: runtime, execution_policy: { timeout_ms: timeoutMs, memory_ceiling_bytes: 1000000,
      max_output_bytes: maxOutputBytes, network: "forbidden", working_directory: "run", environment_allowlist: [] },
    authority_effect: "none", release_admission: "not-granted", claim_ceiling: "synthetic only", residue: [],
  });
  const rows = ["case-1", "case-2"].map((caseId, index) => ({
    obligation_id: "O-1", case_id: caseId, kind: "property", normalized_inputs: { value: index + 1 },
    expected_relation_or_oracle: "holds", source_basis: ["synthetic-claim"], case_class: "positive",
    status: "ready", claim_ceiling: "synthetic only",
  }));
  const obligations = put("fixture/obligation-set.json", {
    schema_version: "domainspec-v2.neutral-obligation-set/v1-candidate", obligation_set_id: "synthetic-set",
    owner: "TDE", formal_claim_ref: claim, capability_assessment_ref: capability, projection_ref: null,
    derivation_profile_ref: profile, derivation_status: "derived", obligations: rows, residue: [],
    determinism: { algorithm_ref: profile, input_digest: sha("in"), output_digest: sha("out") },
    authority_effect: "none", claim_ceiling: "synthetic only",
  });
  const projection = put("fixture/projection.json", {
    schema_version: "domainspec-v2.formalization-projection/v1-candidate", projection_id: "synthetic-projection",
    owner: "synthetic-formalization", formal_claim_ref: claim, capability_assessment_ref: capability,
    obligation_set_ref: obligations, purpose: "tde-executable-slice", target_profile_ref: profile,
    source_semantics_digest: sha("source"), projected_semantics_digest: sha("projected"),
    domain_and_bound: "two synthetic cases", preservation_kind: "exact-equivalent", currentness: "current",
    authority_effect: "none", claim_ceiling: "synthetic only",
  });
  const preservation = put("fixture/preservation.json", {
    schema_version: "domainspec-v2.preservation-binding/v1-candidate", binding_id: "synthetic-preservation",
    owner: "synthetic-formalization", projection_ref: projection, direction: "bidirectional", kind: "review-backed",
    preserved_semantics: ["synthetic finite cases"], known_losses: [], unsupported_constructs: [],
    validation_method: "synthetic fixture", certificate_ref: null, status: "preserved", authority_effect: "none",
    claim_ceiling: "synthetic only",
  });
  const selection = { base_request_ref: base, obligation_set_ref: obligations, projection_ref: projection,
    preservation_binding_ref: preservation };
  const finalized = finalizeApplicationExecutionRequest(selection, sources);
  const request = put("fixture/finalized-request.json", finalized);
  const adapter = putBytes("fixture/local-adapter", Buffer.from(script));
  return { sources, selection, finalized, request, adapter,
    input: { opt_in: "trusted-local-native-case-observation" as const, selection, finalized_request_ref: request,
      local_adapter_ref: adapter, local_executable_ref: localExecutable } };
}

test("observes and replays two exact post-TDE cases without promotion", async () => {
  const candidate = fixture();
  const receipt = await observeApplicationNativeCases(candidate.input, candidate.sources);
  assert.deepEqual(receipt.observations.map(item => item.case_id), ["case-1", "case-2"]);
  assert.deepEqual(receipt.observations.map(item => item.native_output), [2, 4]);
  assert.equal(receipt.finalized_request_id, candidate.finalized.request_id);
  assert.equal(receipt.case_domain_sha256, candidate.finalized.case_domain_sha256);
  assert.equal(receipt.witness_input_set_sha256, candidate.finalized.witness_input_set_sha256);
  assert.equal(receipt.evf_join, "forbidden");
  assert.equal(receipt.can_satisfy_obligation, false);
  assert.equal(receipt.runtime_guarantees_observed, false);
  assert.equal(receipt.provider_equivalence, "unverified");
  assert.equal(receipt.network_enforcement, "unverified");
  assert.equal(receipt.memory_enforcement, "unverified");
  assert.equal(receipt.execution_status, "complete");
  assert.equal(receipt.observed_case_count, 2);
  assert.equal(receipt.observations[0].witness_input_digest,
    sha(canonical({ obligation_id: "O-1", case_id: "case-1", normalized_inputs: { value: 1 }, expected_relation_or_oracle: "holds" })));
  assert.ok(receipt.residue.length >= 4);
  await assertApplicationNativeCasesCurrent(candidate.input, candidate.sources, receipt);
});

test("rejects absent opt-in, changed request, changed case and stale source Buffer", async () => {
  const absent = fixture();
  await assert.rejects(observeApplicationNativeCases({ ...absent.input, opt_in: "no" as any }, absent.sources), /APPLICATION_NATIVE_OPT_IN/);
  const request = fixture();
  request.sources.get(request.request.path)![4] ^= 1;
  await assert.rejects(observeApplicationNativeCases(request.input, request.sources), /APPLICATION_NATIVE_STALE/);
  const caseChange = fixture();
  caseChange.sources.get(caseChange.selection.obligation_set_ref.path)![20] ^= 1;
  await assert.rejects(observeApplicationNativeCases(caseChange.input, caseChange.sources), /APPLICATION_EXECUTION_STALE/);
  const source = fixture();
  source.sources.get("fixture/claim.json")![4] ^= 1;
  await assert.rejects(observeApplicationNativeCases(source.input, source.sources), /APPLICATION_EXECUTION_STALE/);
  const adapter = fixture();
  adapter.sources.get(adapter.adapter.path)![20] ^= 1;
  await assert.rejects(observeApplicationNativeCases(adapter.input, adapter.sources), /APPLICATION_NATIVE_STALE/);
  const executable = fixture();
  executable.input.local_executable_ref = { ...localExecutable, sha256: sha("different") };
  await assert.rejects(observeApplicationNativeCases(executable.input, executable.sources), /APPLICATION_NATIVE_EXECUTABLE/);
});

test("replay rejects forged receipt even when its digest is recomputed", async () => {
  const candidate = fixture();
  const receipt = await observeApplicationNativeCases(candidate.input, candidate.sources);
  const forged: any = structuredClone(receipt);
  forged.observations[0].native_output = 999;
  const { receipt_sha256: _old, ...body } = forged;
  forged.receipt_sha256 = sha(canonical(body));
  await assert.rejects(assertApplicationNativeCasesCurrent(candidate.input, candidate.sources, forged), /APPLICATION_NATIVE_REPLAY/);
});

test("records timeout, nonzero exit and oversized output as incomplete non-promoting receipts; rejects nondeterministic replay", async () => {
  const timeout = fixture(adapterSource("setTimeout(() => process.stdout.write(JSON.stringify({case_id:row.case_id,native_output:true})), 250);"), 40);
  const timedOut = await observeApplicationNativeCases(timeout.input, timeout.sources);
  assert.deepEqual(timedOut.incomplete_case, { case_id: "case-1", kind: "timeout" });
  assert.equal(timedOut.execution_status, "incomplete");
  assert.equal(timedOut.local_execution_observed, false);
  assert.equal(timedOut.can_satisfy_obligation, false);
  const nonzero = fixture(adapterSource("process.exit(7);"));
  assert.deepEqual((await observeApplicationNativeCases(nonzero.input, nonzero.sources)).incomplete_case,
    { case_id: "case-1", kind: "nonzero-exit" });
  const oversized = fixture(adapterSource("process.stdout.write('x'.repeat(500));"), 1000, 80);
  assert.deepEqual((await observeApplicationNativeCases(oversized.input, oversized.sources)).incomplete_case,
    { case_id: "case-1", kind: "output-limit" });
  const malformed = fixture(adapterSource("process.stdout.write(JSON.stringify({case_id:'other',native_output:true}));"));
  assert.deepEqual((await observeApplicationNativeCases(malformed.input, malformed.sources)).incomplete_case,
    { case_id: "case-1", kind: "malformed-output" });
  const nondeterministic = fixture(adapterSource("process.stdout.write(JSON.stringify({case_id:row.case_id,native_output:Math.random()}));"));
  const receipt = await observeApplicationNativeCases(nondeterministic.input, nondeterministic.sources);
  await assert.rejects(assertApplicationNativeCasesCurrent(nondeterministic.input, nondeterministic.sources, receipt), /APPLICATION_NATIVE_REPLAY/);
});

test("detects a source-map Buffer changed during adapter execution", async () => {
  const candidate = fixture(adapterSource("setTimeout(() => process.stdout.write(JSON.stringify({case_id:row.case_id,native_output:true})), 100);"));
  setTimeout(() => { candidate.sources.get("fixture/claim.json")![3] ^= 1; }, 40);
  await assert.rejects(observeApplicationNativeCases(candidate.input, candidate.sources), /APPLICATION_NATIVE_SOURCE_MUTATED/);
});

test("detects a mutable input reference changed during adapter execution", async () => {
  const candidate = fixture(adapterSource("setTimeout(() => process.stdout.write(JSON.stringify({case_id:row.case_id,native_output:true})), 100);"));
  setTimeout(() => { candidate.input.finalized_request_ref.sha256 = sha("forged"); }, 40);
  await assert.rejects(observeApplicationNativeCases(candidate.input, candidate.sources), /APPLICATION_NATIVE_INPUT_MUTATED/);
});

test("bounds the trusted-local diagnostic before launching cases", async () => {
  const timeout = fixture(adapterSource(), 30_001);
  await assert.rejects(observeApplicationNativeCases(timeout.input, timeout.sources), /APPLICATION_NATIVE_POLICY/);
  const output = fixture(adapterSource(), 1000, 1_048_577);
  await assert.rejects(observeApplicationNativeCases(output.input, output.sources), /APPLICATION_NATIVE_POLICY/);
});

test("cleans same-group descendants after a successful direct child", async () => {
  const candidate = fixture(adapterSource("const {spawn}=require('node:child_process'); const child=spawn('/bin/sleep',['5'],{stdio:'ignore'}); child.unref(); process.stdout.write(JSON.stringify({case_id:row.case_id,native_output:child.pid}));"));
  const receipt = await observeApplicationNativeCases(candidate.input, candidate.sources);
  for (const row of receipt.observations) {
    const pid = row.native_output as number;
    try {
      const stat = readFileSync(`/proc/${pid}/stat`, "utf8");
      assert.match(stat, /^\d+ \(.+\) Z /, `same-group descendant ${pid} is still running`);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
    } finally {
      try { process.kill(pid, "SIGKILL"); } catch { /* already gone */ }
    }
  }
});
