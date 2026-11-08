import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

import { planReferenceRuntimeV1, ReferenceRuntimePlanError } from "../../src/generation/reference-runtime-v1.ts";
import { composeProviderApplicationV1 } from "../../src/generation/provider-application-v1.ts";
import { planWholeApplicationV1 } from "../../src/generation/whole-application-v1.ts";

const example = path.resolve("examples/reconciled-commerce");
const read = (relative: string): unknown => JSON.parse(fs.readFileSync(path.join(example, relative), "utf8"));
const provider = () => composeProviderApplicationV1(
  planWholeApplicationV1(path.join(example, "source"), read("selections/typescript.json") as never, read("integrations/application.json") as never),
  read("providers/typescript.json"),
  read("integrations/application.json"),
);

test("reference runtime plan appends an owned bounded runtime without changing provider bytes", () => {
  const predecessor = provider();
  const plan = planReferenceRuntimeV1(predecessor);
  assert.equal(plan.provider_application_plan_sha256, predecessor.plan_sha256);
  assert.equal(plan.runtime_guarantees_observed, false);
  assert.equal(plan.claim_ceiling, "generated-reference-runtime-formation-only");
  assert.equal(plan.authority_effect, "none");
  assert.equal(plan.artifacts.length, predecessor.artifacts.length + 4);
  for (const original of predecessor.artifacts) assert.equal(plan.artifacts.find(item => item.relative_path === original.relative_path)?.sha256, original.sha256);
  assert.deepEqual(plan.path_owners.filter(row => row.owner === "reference-runtime").map(row => row.relative_path), [
    ".domainspec/runtime/scenario.json",
    "migrations/0002_domainspec_reference_runtime.sql",
    "src/reference-runtime/proof.ts",
    "src/reference-runtime/runtime.ts",
  ]);
  const proof = plan.artifacts.find(item => item.relative_path === "src/reference-runtime/proof.ts")!.content;
  assert.match(proof, /composeReferenceApplication/);
  assert.match(proof, /onWebhook:async\(\)=>\{webhookInvocations\+\+;\}/);
  assert.match(proof, /webhookSignature\(secret,webhookBody\)/);
  assert.match(proof, /new URL\("\/webhook",providerBaseUrl\)/);
  assert.match(proof, /SCENARIO_MODE/);
  assert.match(proof, /http:unauthorized:commerce:perform/);
  const runtime = plan.artifacts.find(item => item.relative_path === "src/reference-runtime/runtime.ts")!.content;
  assert.match(runtime, /Postgresql16OrderStore/);
  assert.match(runtime, /NatsJetStreamOrderPublisher/);
  assert.doesNotMatch(runtime, /INSERT INTO domainspec_outbox \(message_id,subject,payload\)/);
  const migration = plan.artifacts.find(item => item.relative_path === "migrations/0002_domainspec_reference_runtime.sql")!.content;
  assert.match(migration, /domainspec_runtime_inbox/);
  assert.match(migration, /domainspec_runtime_dead_letters/);
  assert.doesNotMatch(migration, /CREATE TABLE IF NOT EXISTS domainspec_outbox/);
  assert.match(runtime, /publishPending\(pool\)/);
  assert.ok(Object.isFrozen(plan));
  assert.equal(planReferenceRuntimeV1(predecessor).plan_sha256, plan.plan_sha256);
});

test("reference runtime rejects unsupported language without weakening provider plans", () => {
  const whole = planWholeApplicationV1(path.join(example, "source"), read("selections/python.json") as never, read("integrations/application.json") as never);
  const python = composeProviderApplicationV1(whole, read("providers/python.json"), read("integrations/application.json"));
  assert.throws(() => planReferenceRuntimeV1(python), (error: unknown) => error instanceof ReferenceRuntimePlanError && error.code === "DS_REFERENCE_RUNTIME_LANGUAGE");
});
