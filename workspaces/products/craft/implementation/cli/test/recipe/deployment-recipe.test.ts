import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { runCli } from "../../src/cli/main.ts";
import { canonicalJson } from "../../src/input/source-manifest.ts";
import { decodeDeploymentRecipeRequest, parseDeploymentRecipeRequestJson, type DeploymentRecipeRequestV1 } from "../../src/recipe/contracts.ts";
import { deploymentRecipePlanSummary, planDeploymentRecipe } from "../../src/recipe/plan.ts";
import { publishDeploymentRecipe, validateDeploymentRecipeReceipt, verifyDeploymentRecipe } from "../../src/recipe/publish.ts";
import { createCompleteL1Project } from "../helpers/l1-project.ts";

const DIGEST = "a".repeat(64);

function write(file: string, content: string): void { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, content); }
function writeJson(file: string, value: unknown): void { write(file, `${JSON.stringify(value, null, 2)}\n`); }
function readJson(file: string): Record<string, unknown> { return JSON.parse(fs.readFileSync(file, "utf8")) as Record<string, unknown>; }

function consumer(): string {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-recipe-consumer-"));
  writeJson(path.join(root, "application/package.json"), { name: "settlement-service", version: "1.0.0", private: true, type: "module", scripts: { build: "tsc -p tsconfig.json" } });
  writeJson(path.join(root, "application/package-lock.json"), { name: "settlement-service", version: "1.0.0", lockfileVersion: 3, requires: true, packages: { "": { name: "settlement-service", version: "1.0.0" } } });
  writeJson(path.join(root, "application/tsconfig.json"), { compilerOptions: { target: "ES2022", module: "NodeNext", moduleResolution: "NodeNext", rootDir: "src", outDir: "dist", strict: true }, include: ["src/**/*.ts"] });
  write(path.join(root, "application/src/api.ts"), "import http from 'node:http';\nhttp.createServer((_, response) => { response.statusCode = 204; response.end(); }).listen(8080);\n");
  write(path.join(root, "application/src/outbox-worker.ts"), "process.on('SIGTERM', () => process.exit(0));\nsetInterval(() => undefined, 1000);\n");
  write(path.join(root, "application/src/queue-consumer.ts"), "process.on('SIGTERM', () => process.exit(0));\nsetInterval(() => undefined, 1000);\n");
  write(path.join(root, "database/domain-migrations/0001_settlement.sql"), "CREATE TABLE settlement (settlement_id text PRIMARY KEY);\n");
  return root;
}

function request(): DeploymentRecipeRequestV1 {
  return decodeDeploymentRecipeRequest({
    schema_version: "domainspec.deployment-recipe-request/v1",
    request_id: "settlement-production-recipe",
    target: "aws-ecs-fargate-postgres-v1",
    application: {
      language: "typescript", source_root: "application", lockfile: "package-lock.json",
      base_image: `node:26.8.1-bookworm-slim@sha256:${DIGEST}`,
      api: { entrypoint: ["node", "dist/api.js"], port: 8080, health_path: "/healthz" },
      worker: { entrypoint: ["node", "dist/outbox-worker.js"] },
      consumer: { entrypoint: ["node", "dist/queue-consumer.js"] },
      domain_migrations_root: "database/domain-migrations",
    },
    integration_binding_ids: ["settle-runtime"],
    environment: { name_variable: "environment_name", aws_region_variable: "aws_region" },
    authority_effect: "none",
  });
}

function schemaValidate(schema: string, value: unknown, root: string): void {
  const valuePath = path.join(root, `${path.basename(schema)}.value.json`);
  writeJson(valuePath, value);
  const result = spawnSync("python3", ["-c", "import json,jsonschema,sys;jsonschema.Draft202012Validator(json.load(open(sys.argv[1]))).validate(json.load(open(sys.argv[2])))", path.resolve("contracts", schema), valuePath], { cwd: path.resolve("."), encoding: "utf8" });
  assert.equal(result.status, 0, result.stderr);
}

test("compiled graph produces one deterministic, policy-bounded deployment recipe", () => {
  const fixture = createCompleteL1Project(); const left = consumer(); const right = consumer();
  try {
    const leftPlan = planDeploymentRecipe(fixture.root, request(), left);
    const rightPlan = planDeploymentRecipe(fixture.root, request(), right);
    assert.equal(leftPlan.plan_sha256, rightPlan.plan_sha256);
    assert.deepEqual(leftPlan.artifacts, rightPlan.artifacts);
    assert.deepEqual(leftPlan.components.map(({ component }) => component), ["api", "outbox-worker", "postgresql", "transactional-outbox", "message-channel", "message-publisher", "message-consumer"]);
    assert.equal(leftPlan.manifest.selected_relationship_edge_ids.includes("settle-produces-settlement-requested"), true);
    assert.equal(leftPlan.manifest.selected_relationship_edge_ids.includes("settlement-api-exposes-settle"), true);
    assert.equal(leftPlan.manifest.selected_relationship_edge_ids.includes("settlement-requested-triggers-record"), true);
    assert.equal(leftPlan.messaging.channel_id, "settlement-events");
    assert.equal(leftPlan.messaging.publish_max_attempts, 5);
    assert.equal(leftPlan.messaging.envelope_profile_ref, "envelope:domainspec-event-json-v1");
    assert.equal(leftPlan.messaging.deduplication_owner_ref, "consumer:inbox-message-id");
    assert.equal(leftPlan.artifacts.some(({ relative_path }) => relative_path === "images/api.Dockerfile"), true);
    assert.equal(leftPlan.artifacts.some(({ relative_path }) => relative_path === ".dockerignore"), true);
    assert.equal(leftPlan.artifacts.some(({ relative_path }) => relative_path === "infrastructure/terraform/database.tf"), true);
    const providerLock = leftPlan.artifacts.find(({ relative_path }) => relative_path === "infrastructure/terraform/.terraform.lock.hcl")!.content;
    assert.match(providerLock, /version\s+= "6\.63\.0"/);
    assert.match(providerLock, /h1:9cre7jh1lSs\/9igpgAcENMUAUlYW3HCtkav3up4oit0=/);
    assert.equal(leftPlan.artifacts.some(({ relative_path }) => relative_path === "infrastructure/terraform/messaging.tf"), true);
    assert.equal(leftPlan.artifacts.some(({ relative_path }) => relative_path === "images/consumer.Dockerfile"), true);
    const terraform = leftPlan.artifacts.filter(({ relative_path }) => relative_path.endsWith(".tf")).map(({ content }) => content).join("\n");
    assert.match(terraform, /publicly_accessible\s+= false/);
    assert.match(terraform, /storage_encrypted\s+= true/);
    assert.match(terraform, /manage_master_user_password\s+= true/);
    assert.doesNotMatch(terraform, /backend\s+"/);
    assert.doesNotMatch(terraform, /protocol\s*=\s*"-1"/);
    assert.match(terraform, /aws_vpc_security_group_ingress_rule/);
    assert.match(terraform, /aws_vpc_security_group_egress_rule/);
    assert.match(terraform, /outbox_pending/);
    assert.match(terraform, /outbox_dead/);
    assert.match(terraform, /aws_sqs_queue" "message/);
    assert.match(terraform, /sqs_managed_sse_enabled\s+= true/);
    assert.match(terraform, /aws_sqs_queue_redrive_allow_policy/);
    assert.match(terraform, /sqs:SendMessage/);
    assert.match(terraform, /sqs:ReceiveMessage/);
    assert.match(terraform, /message_queue_name\s+=/);
    assert.match(terraform, /sha256\(local\.message_queue_seed\)/);
    assert.match(terraform, /OUTBOX_MAX_ATTEMPTS/);
    const outboxMigration = leftPlan.artifacts.find(({ relative_path }) => relative_path === "database/domainspec/0001_outbox.sql")!.content;
    assert.match(outboxMigration, /max_attempts integer NOT NULL DEFAULT 5/);
    const boundary = JSON.parse(leftPlan.artifacts.find(({ relative_path }) => relative_path === "operations/message-boundary-contract.json")!.content);
    assert.deepEqual(boundary.stages, ["intent-observed", "send-attempt-observed", "provider-accepted", "delivered-or-redelivered", "application-committed"]);
    assert.equal(boundary.exactly_once_claimed, false);
    assert.equal(boundary.publish_max_attempts, 5);
    assert.equal(boundary.envelope_profile_ref, "envelope:domainspec-event-json-v1");
    assert.equal(boundary.deduplication_owner_ref, "consumer:inbox-message-id");
    const dockerfile = leftPlan.artifacts.find(({ relative_path }) => relative_path === "images/api.Dockerfile")!.content;
    assert.match(dockerfile, /@sha256:[a-f0-9]{64}/);
    assert.match(dockerfile, /USER node/);
    assert.match(dockerfile, /STOPSIGNAL SIGTERM/);
    assert.doesNotMatch(leftPlan.artifacts.map(({ content }) => content).join("\n"), /terraform apply|docker push|aws ecs update-service/);
    assert.deepEqual(validateDeploymentRecipeReceipt(fixture.root, request(), left, leftPlan.receipt), leftPlan.receipt);
    schemaValidate("deployment-recipe-request.schema.json", request(), left);
    schemaValidate("deployment-recipe-manifest.schema.json", leftPlan.manifest, left);
    schemaValidate("deployment-recipe-receipt.schema.json", leftPlan.receipt, left);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(left, { recursive: true, force: true }); fs.rmSync(right, { recursive: true, force: true }); }
});

test("publication is atomic, exact, non-overwriting, and independently verifiable", () => {
  const fixture = createCompleteL1Project(); const consumerRoot = consumer(); const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-recipe-output-")); const target = path.join(parent, "generated");
  try {
    const plan = planDeploymentRecipe(fixture.root, request(), consumerRoot);
    const published = publishDeploymentRecipe(plan, target);
    assert.equal(published.target_root, target);
    assert.equal(fs.existsSync(path.join(target, published.receipt_path)), true);
    assert.equal(verifyDeploymentRecipe(fixture.root, request(), consumerRoot, target).result, "pass");
    const terraformFormat = spawnSync("terraform", ["-chdir=infrastructure/terraform", "fmt", "-check", "-recursive"], { cwd: target, encoding: "utf8" });
    if (terraformFormat.error?.code !== "ENOENT") assert.equal(terraformFormat.status, 0, terraformFormat.stderr || terraformFormat.stdout);
    assert.throws(() => publishDeploymentRecipe(plan, target), (error: unknown) => (error as { code?: string }).code === "MTCLI_RECIPE_TARGET_EXISTS");
    fs.appendFileSync(path.join(target, "infrastructure/terraform/database.tf"), "# drift\n");
    const drift = verifyDeploymentRecipe(fixture.root, request(), consumerRoot, target);
    assert.equal(drift.result, "fail");
    assert.equal(drift.checks.find(({ id }) => id === "artifact:infrastructure/terraform/database.tf")?.result, "fail");
    write(path.join(target, "undeclared.txt"), "hostile\n");
    assert.equal(verifyDeploymentRecipe(fixture.root, request(), consumerRoot, target).checks.find(({ id }) => id === "artifact-set-exact")?.result, "fail");
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(consumerRoot, { recursive: true, force: true }); fs.rmSync(parent, { recursive: true, force: true }); }
});

test("all selected source, request, application, migration, and binding bytes are sensitive while unrelated bytes are not", () => {
  const fixture = createCompleteL1Project(); const consumerRoot = consumer();
  try {
    const original = planDeploymentRecipe(fixture.root, request(), consumerRoot);
    write(path.join(consumerRoot, "unrelated.txt"), "not selected\n");
    assert.equal(planDeploymentRecipe(fixture.root, request(), consumerRoot).plan_sha256, original.plan_sha256);
    fs.appendFileSync(path.join(consumerRoot, "application/src/api.ts"), "// selected change\n");
    const applicationChanged = planDeploymentRecipe(fixture.root, request(), consumerRoot);
    assert.notEqual(applicationChanged.plan_sha256, original.plan_sha256);
    fs.appendFileSync(path.join(consumerRoot, "database/domain-migrations/0001_settlement.sql"), "ALTER TABLE settlement ADD COLUMN status text;\n");
    const migrationChanged = planDeploymentRecipe(fixture.root, request(), consumerRoot);
    assert.notEqual(migrationChanged.plan_sha256, applicationChanged.plan_sha256);
    const changedRequest = JSON.parse(JSON.stringify(request()));
    changedRequest.application.api.health_path = "/readyz";
    const requestChanged = planDeploymentRecipe(fixture.root, changedRequest, consumerRoot);
    assert.notEqual(requestChanged.manifest.request_sha256, migrationChanged.manifest.request_sha256);
    assert.notEqual(requestChanged.manifest.target_implementation_sha256, migrationChanged.manifest.target_implementation_sha256);
    assert.notEqual(requestChanged.plan_sha256, migrationChanged.plan_sha256);
    const operationPath = path.join(fixture.root, "specs/alpha/nodes/settle.json");
    const operation = readJson(operationPath); (operation.body as Record<string, unknown>).description = "Changed selected operation."; writeJson(operationPath, operation);
    const sourceChanged = planDeploymentRecipe(fixture.root, request(), consumerRoot);
    assert.notEqual(sourceChanged.manifest.source_manifest_sha256, original.manifest.source_manifest_sha256);
    assert.notEqual(sourceChanged.plan_sha256, requestChanged.plan_sha256);
    const bindingPath = path.join(fixture.root, "integrations/settle-runtime.json");
    const binding = readJson(bindingPath);
    const persistence = binding.persistence_bindings as Record<string, unknown>[];
    persistence[0]!.adapter_ref = "target:replacement-settlement-adapter";
    writeJson(bindingPath, binding);
    const bindingChanged = planDeploymentRecipe(fixture.root, request(), consumerRoot);
    assert.equal(bindingChanged.manifest.source_manifest_sha256, sourceChanged.manifest.source_manifest_sha256);
    assert.notEqual(bindingChanged.manifest.selected_bindings[0]!.binding_digest, sourceChanged.manifest.selected_bindings[0]!.binding_digest);
    assert.notEqual(bindingChanged.manifest.target_implementation_sha256, sourceChanged.manifest.target_implementation_sha256);
    assert.notEqual(bindingChanged.plan_sha256, sourceChanged.plan_sha256);
    const messageBinding = readJson(bindingPath);
    const delivery = messageBinding.delivery_policies as Record<string, unknown>[];
    delivery[0]!.visibility_timeout_seconds = 90;
    writeJson(bindingPath, messageBinding);
    const messagePolicyChanged = planDeploymentRecipe(fixture.root, request(), consumerRoot);
    assert.equal(messagePolicyChanged.messaging.visibility_timeout_seconds, 90);
    assert.notEqual(messagePolicyChanged.plan_sha256, bindingChanged.plan_sha256);
    const failurePolicy = messageBinding.transport_failure_policies as Record<string, unknown>[];
    failurePolicy[0]!.max_attempts = 9;
    writeJson(bindingPath, messageBinding);
    const retryPolicyChanged = planDeploymentRecipe(fixture.root, request(), consumerRoot);
    assert.equal(retryPolicyChanged.messaging.publish_max_attempts, 9);
    assert.match(retryPolicyChanged.artifacts.find(({ relative_path }) => relative_path === "database/domainspec/0001_outbox.sql")!.content, /max_attempts integer NOT NULL DEFAULT 9/);
    assert.notEqual(retryPolicyChanged.manifest.target_implementation_sha256, messagePolicyChanged.manifest.target_implementation_sha256);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(consumerRoot, { recursive: true, force: true }); }
});

test("hostile requests and incomplete semantic evidence fail closed", () => {
  assert.throws(() => parseDeploymentRecipeRequestJson('{"schema_version":"domainspec.deployment-recipe-request/v1","schema_version":"domainspec.deployment-recipe-request/v1"}'), (error: unknown) => (error as { code?: string }).code === "MTCLI_RECIPE_DUPLICATE_KEY");
  const mutable = JSON.parse(JSON.stringify(request())); mutable.application.base_image = "node:26.8.1-bookworm-slim";
  assert.throws(() => decodeDeploymentRecipeRequest(mutable), (error: unknown) => (error as { code?: string }).code === "MTCLI_RECIPE_IMAGE");
  const traversal = JSON.parse(JSON.stringify(request())); traversal.application.source_root = "../application";
  assert.throws(() => decodeDeploymentRecipeRequest(traversal), (error: unknown) => (error as { code?: string }).code === "MTCLI_RECIPE_PATH");
  const collidingVariables = JSON.parse(JSON.stringify(request())); collidingVariables.environment.aws_region_variable = collidingVariables.environment.name_variable;
  assert.throws(() => decodeDeploymentRecipeRequest(collidingVariables), (error: unknown) => (error as { code?: string }).code === "MTCLI_RECIPE_VARIABLE");
  const longId = JSON.parse(JSON.stringify(request())); longId.request_id = `recipe-${"a".repeat(30)}`;
  assert.throws(() => decodeDeploymentRecipeRequest(longId), (error: unknown) => (error as { code?: string }).code === "MTCLI_RECIPE_ID");
  const canonical = path.resolve("fixtures/input-roots/canonical-project"); const consumerRoot = consumer();
  try {
    assert.throws(() => planDeploymentRecipe(canonical, request(), consumerRoot), (error: unknown) => (error as { code?: string }).code === "MTCLI_RECIPE_WORKER_EVIDENCE");
    write(path.join(consumerRoot, "application/.env"), "DATABASE_PASSWORD=forbidden\n");
    const fixture = createCompleteL1Project();
    try { assert.throws(() => planDeploymentRecipe(fixture.root, request(), consumerRoot), (error: unknown) => (error as { code?: string }).code === "MTCLI_RECIPE_SENSITIVE_INPUT"); }
    finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); }
    fs.rmSync(path.join(consumerRoot, "application/.env"));
    write(path.join(consumerRoot, "application/.npmrc"), "//registry.example.invalid/:_authToken=forbidden\n");
    const credentialFixture = createCompleteL1Project();
    try { assert.throws(() => planDeploymentRecipe(credentialFixture.root, request(), consumerRoot), (error: unknown) => (error as { code?: string }).code === "MTCLI_RECIPE_SENSITIVE_INPUT"); }
    finally { fs.rmSync(credentialFixture.parent, { recursive: true, force: true }); }
    const missingTriggerFixture = createCompleteL1Project();
    try {
      const project = readJson(path.join(missingTriggerFixture.root, "project.json"));
      project.cross_feature_edges = (project.cross_feature_edges as string[]).filter((id) => id !== "settlement-requested-triggers-record");
      writeJson(path.join(missingTriggerFixture.root, "project.json"), project);
      fs.rmSync(path.join(missingTriggerFixture.root, "edges/settlement-requested-triggers-record.json"));
      assert.throws(() => planDeploymentRecipe(missingTriggerFixture.root, request(), consumerRoot), (error: unknown) => (error as { code?: string }).code === "MTCLI_RECIPE_MESSAGE_TRIGGER");
    } finally { fs.rmSync(missingTriggerFixture.parent, { recursive: true, force: true }); }
  } finally { fs.rmSync(consumerRoot, { recursive: true, force: true }); }
});

test("CLI plans, generates, and verifies without invoking deployment tools", () => {
  const fixture = createCompleteL1Project(); const consumerRoot = consumer(); const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-recipe-cli-")); const requestPath = path.join(parent, "request.json"); const target = path.join(parent, "generated");
  writeJson(requestPath, request());
  try {
    const invoke = (args: string[]): { readonly status: number; readonly output: Record<string, unknown> } => { const out: string[] = []; const errors: string[] = []; const status = runCli(args, { stdout: (value) => out.push(value), stderr: (value) => errors.push(value) }); return { status, output: JSON.parse(out.at(-1) ?? errors.at(-1) ?? "{}") as Record<string, unknown> }; };
    const planned = invoke(["recipe-plan", fixture.root, "--request", requestPath, "--consumer-root", consumerRoot]);
    assert.equal(planned.status, 0); assert.equal(planned.output.authority_effect, "none");
    assert.deepEqual(planned.output, deploymentRecipePlanSummary(planDeploymentRecipe(fixture.root, request(), consumerRoot)));
    const generated = invoke(["recipe-generate", fixture.root, "--request", requestPath, "--consumer-root", consumerRoot, "--target-root", target]);
    assert.equal(generated.status, 0); assert.equal(generated.output.result, "pass");
    const verified = invoke(["recipe-verify", fixture.root, "--request", requestPath, "--consumer-root", consumerRoot, "--target-root", target]);
    assert.equal(verified.status, 0); assert.equal(verified.output.result, "pass");
    const rejectedTarget = path.join(parent, "rejected");
    const hostile = JSON.parse(JSON.stringify(request())); hostile.application.base_image = "node:latest"; writeJson(requestPath, hostile);
    const rejected = invoke(["recipe-generate", fixture.root, "--request", requestPath, "--consumer-root", consumerRoot, "--target-root", rejectedTarget]);
    assert.equal(rejected.status, 22); assert.equal(rejected.output.code, "MTCLI_RECIPE_IMAGE"); assert.equal(fs.existsSync(rejectedTarget), false);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(consumerRoot, { recursive: true, force: true }); fs.rmSync(parent, { recursive: true, force: true }); }
});
