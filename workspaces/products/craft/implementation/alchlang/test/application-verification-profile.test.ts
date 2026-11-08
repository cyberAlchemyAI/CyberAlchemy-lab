import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { lowerApplicationVerificationProfiles } from "../src/application-verification-profile.js";
import { parseDomainSource } from "../src/parser.js";
import { formalLoweringFixture, source as formalSource } from "./fixtures/formal-lowering-fixture.js";

const sha = (bytes: string | Buffer) => createHash("sha256").update(bytes).digest("hex");
const profileBody = (provider = "provider:smt-qf") => `
verification-profile EligibleVerification:
  claim EligibleClaim
  context EvaluationContext:eligible-fixture version 1
  interpretation none
  route route:tde-execution
  provider ${provider}
  runtime runtime:smt-fixture
  timeout-ms 5000
  memory-ceiling-bytes 268435456
  max-output-bytes 1048576
  network forbidden
  working-directory sandbox/verification
  environment-allow LANG
  assumption "Finite synthetic order scope."
  limit "Request formation only; no provider result."
  ceiling "Synthetic verification request only."
`;

function verificationFixture(provider = "provider:smt-qf") {
  const fixture = formalLoweringFixture(); const source = formalSource + profileBody(provider);
  const route = fixture.put("fixture/route.json", { route_id: "route:tde-execution", status: "candidate" });
  const providerRef = fixture.put(`fixture/${provider.replaceAll(":", "-")}.json`, { provider_id: provider, status: "candidate" });
  const runtime = fixture.put("fixture/runtime.json", { runtime_id: "runtime:smt-fixture", version: "1", status: "candidate" });
  const formal = { ...fixture.input, source_sha256: sha(source) };
  const input: any = { schema_version: "alchlang.verification-profile-bindings/v1", source_sha256: sha(source), owner: "fixture-owner", formal,
    verification_profiles: { EligibleVerification: {
      interpretation: null,
      route: { selector: "route:tde-execution", ref: route },
      provider: { selector: provider, ref: providerRef },
      runtime: { selector: "runtime:smt-fixture", ref: runtime },
    } } };
  return { ...fixture, source, input, providerRef };
}

test("lowers an exact evaluation context, bounded request and deterministic source trace", () => {
  const fixture = verificationFixture();
  const result = lowerApplicationVerificationProfiles(fixture.source, fixture.input, fixture.sources);
  assert.deepEqual(result, lowerApplicationVerificationProfiles(fixture.source, structuredClone(fixture.input), fixture.sources));
  assert.equal(result.contexts.length, 1); assert.equal(result.requests.length, 1);
  const context = result.contexts[0]! as any; const request = result.requests[0]! as any;
  assert.equal(context.schema_version, "domainspec-v2.evaluation-context/v1-candidate");
  assert.equal(context.formal_claim_ref.sha256, sha(result.formal.files["formalization/claims/EligibleClaim.json"]!));
  assert.equal(context.interpretation_model_ref, null); assert.equal(context.status, "draft");
  assert.equal(request.schema_version, "alchlang.verification-request/v1-candidate");
  assert.equal(request.request_state, "ready"); assert.equal(request.release_admission, "not-granted");
  assert.equal(request.execution_policy.network, "forbidden");
  assert.equal(result.trace.provider_execution_observed, false); assert.equal(result.trace.evaluation_result_observed, false);
  const declaration = result.trace.declarations[0]! as any;
  assert.equal(declaration.request_ref.sha256, sha(result.files[declaration.request_ref.path]!));
  assert.equal(result.files["verification-profiles/trace.json"], JSON.stringify(result.trace, null, 2) + "\n");
});

test("provider selection changes context and request identity but never FormalClaim identity", () => {
  const first = verificationFixture(); const firstResult = lowerApplicationVerificationProfiles(first.source, first.input, first.sources);
  const second = verificationFixture("provider:lean-fixture"); const secondResult = lowerApplicationVerificationProfiles(second.source, second.input, second.sources);
  assert.equal(firstResult.formal.claims[0]!.claim.identity_inputs_digest, secondResult.formal.claims[0]!.claim.identity_inputs_digest);
  assert.notEqual((firstResult.trace.declarations[0]! as any).context_ref.sha256, (secondResult.trace.declarations[0]! as any).context_ref.sha256);
  assert.notEqual((firstResult.trace.declarations[0]! as any).request_ref.sha256, (secondResult.trace.declarations[0]! as any).request_ref.sha256);
  assert.equal(firstResult.formal.claims[0]!.interpretation_boundary.interpretation_model_is_part_of_claim, false);
});

test("emitted contexts and requests conform to their closed candidate schemas", () => {
  const fixture = verificationFixture(); const result = lowerApplicationVerificationProfiles(fixture.source, fixture.input, fixture.sources);
  const contextSchema = fileURLToPath(new URL("../../../../../../../craft/projects/domainspec-v2/formalization/schemas/evaluation-context.schema.json", import.meta.url));
  const requestSchema = fileURLToPath(new URL("../../../../../../../craft/projects/domainspec-v2/development/authoring-to-runtime-v1/verification-request.schema.json", import.meta.url));
  const script = "import json,sys,jsonschema; p=json.load(sys.stdin); [(jsonschema.Draft202012Validator(json.load(open(s))).validate(v)) for v,s in [(p['context'],sys.argv[1]),(p['request'],sys.argv[2])]]";
  const validation = spawnSync("python3", ["-c", script, contextSchema, requestSchema], { input: JSON.stringify({ context: result.contexts[0], request: result.requests[0] }), encoding: "utf8", timeout: 10000 });
  assert.equal(validation.status, 0, validation.stderr || String(validation.error));
});

test("missing, stale, mismatched and over-broad bindings fail closed", () => {
  for (const mode of ["missing", "stale", "selector", "coverage", "interpretation", "extra"]) {
    const fixture = verificationFixture(); const binding = fixture.input.verification_profiles.EligibleVerification;
    if (mode === "missing") fixture.sources.delete(binding.route.ref.path);
    if (mode === "stale") fixture.sources.set(binding.provider.ref.path, Buffer.from("changed"));
    if (mode === "selector") binding.provider.selector = "provider:other";
    if (mode === "coverage") Object.assign(fixture.input.verification_profiles, { Extra: structuredClone(binding) });
    if (mode === "interpretation") binding.interpretation = { selector: "interpretation:unexpected", ref: binding.route.ref };
    if (mode === "extra") Object.assign(binding, { result: "passed" });
    assert.throws(() => lowerApplicationVerificationProfiles(fixture.source, fixture.input, fixture.sources), /APPLICATION_VERIFICATION_|FORMAL_BINDING_/);
  }
});

test("verification syntax rejects unresolved claims, duplicate clauses and unsafe bounds", () => {
  const cases = [
    ["claim EligibleClaim", "claim MissingClaim"],
    ["route route:tde-execution", "route route:tde-execution\n  route route:other"],
    ["timeout-ms 5000", "timeout-ms 0"],
    ["network forbidden", "network allowed"],
    ["working-directory sandbox/verification", "working-directory ../escape"],
    ["limit \"Request formation only; no provider result.\"", ""],
  ] as const;
  for (const [from, to] of cases) {
    const fixture = verificationFixture();
    const changedProfile = profileBody().replace(from, to);
    assert.throws(() => parseDomainSource(formalSource + changedProfile), /APPLICATION_VERIFICATION_/);
  }
});

test("verification profiles are unavailable to the compatibility parser", () => {
  const legacy = `domain example\nowner fixture-owner\n${profileBody()}`;
  assert.throws(() => parseDomainSource(legacy), /ALCH_PROFILE_REQUIRED/);
});
