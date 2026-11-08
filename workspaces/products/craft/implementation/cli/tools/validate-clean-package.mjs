import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const cliRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const fixtureRoot = path.join(cliRoot, "fixtures/input-roots/canonical-project");

function run(command, args, cwd, extraEnvironment = {}) {
  const result = spawnSync(command, args, { cwd, encoding: "utf8", env: { ...process.env, npm_config_audit: "false", npm_config_fund: "false", npm_config_update_notifier: "false", ...extraEnvironment } });
  if (result.status !== 0) throw new Error(`${command} ${args.join(" ")} failed (${result.status})\n${result.stdout}\n${result.stderr}`);
  return result.stdout;
}

function pathExecutable(name) {
  const candidate = (process.env.PATH ?? "").split(path.delimiter).map((directory) => path.join(directory, name)).find((entry) => fs.existsSync(entry));
  assert.notEqual(candidate, undefined, `required validation tool is absent:${name}`);
  // rustup selects cargo/rustc from argv[0], so preserve the exact absolute
  // shim path instead of dereferencing it to the shared rustup binary.
  return path.resolve(candidate);
}

function configuredExecutable(environmentName, candidates) {
  const configured = process.env[environmentName];
  const candidate = configured === undefined
    ? candidates.find((entry) => fs.existsSync(entry))
    : path.resolve(configured);
  assert.notEqual(candidate, undefined, `required validation tool is absent:${environmentName}`);
  assert.equal(path.isAbsolute(candidate), true, `${environmentName} must be absolute`);
  assert.equal(fs.existsSync(candidate), true, `${environmentName} does not exist`);
  const resolved = fs.realpathSync(candidate);
  assert.equal(fs.statSync(resolved).isFile(), true, `${environmentName} must resolve to a regular file`);
  return resolved;
}

const exactValidationToolchain = Object.freeze({
  PATH: `${path.dirname(process.execPath)}${path.delimiter}/usr/bin${path.delimiter}/bin`,
  DOMAINSPEC_TSC: configuredExecutable("DOMAINSPEC_TSC", [
    path.resolve(cliRoot, "node_modules/.bin/tsc"),
    path.resolve(cliRoot, "../node_modules/.bin/tsc"),
  ]),
  DOMAINSPEC_PYTHON: pathExecutable("python3"),
  DOMAINSPEC_RUSTC: pathExecutable("rustc"),
  DOMAINSPEC_CARGO: pathExecutable("cargo"),
});
const doctorPath = [...new Set([
  path.dirname(process.execPath),
  path.dirname(exactValidationToolchain.DOMAINSPEC_TSC),
  path.dirname(exactValidationToolchain.DOMAINSPEC_PYTHON),
  path.dirname(exactValidationToolchain.DOMAINSPEC_RUSTC),
  path.dirname(exactValidationToolchain.DOMAINSPEC_CARGO),
  path.dirname(pathExecutable("lean")),
  "/usr/bin",
  "/bin",
])].join(path.delimiter);

function inventory(root) {
  const rows = [];
  function visit(relative) {
    for (const entry of fs.readdirSync(path.join(root, relative), { withFileTypes: true }).sort((left, right) => left.name.localeCompare(right.name))) {
      const child = relative ? `${relative}/${entry.name}` : entry.name;
      if (entry.isDirectory()) visit(child);
      else {
        const bytes = fs.readFileSync(path.join(root, child));
        rows.push({ relative_path: child, size_bytes: bytes.length, sha256: crypto.createHash("sha256").update(bytes).digest("hex") });
      }
    }
  }
  visit("");
  return rows;
}

function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function addRecipeEvidence(source) {
  writeJson(path.join(source, "specs/alpha/nodes/settlement-requested.json"), {
    schema_version: "domainspec.node/v1",
    node_id: "settlement-requested",
    feature_id: "alpha",
    kind: "Event",
    body: {
      description: "A settlement was requested.",
      event_type: "settlement-requested",
      version: "1",
      occurrence_id: { field_id: "occurrence-id", type_ref: { kind: "primitive", name: "uuid" }, required: true },
      occurred_at_policy: "generated",
      payload: [],
    },
  });
  writeJson(path.join(source, "specs/alpha/edges/settle-produces-settlement-requested.json"), {
    schema_version: "domainspec.edge/v1",
    edge_id: "settle-produces-settlement-requested",
    feature_id: "alpha",
    relationship: "produces",
    source_node_id: "settle",
    target_node_id: "settlement-requested",
    scope: "feature",
  });
  const featurePath = path.join(source, "specs/alpha/feature.json");
  const feature = JSON.parse(fs.readFileSync(featurePath, "utf8"));
  feature.nodes.push("settlement-requested");
  feature.nodes.sort();
  feature.edges.push("settle-produces-settlement-requested");
  feature.edges.sort();
  writeJson(featurePath, feature);
  writeJson(path.join(source, "specs/beta/nodes/record-settlement-request.json"), {
    schema_version: "domainspec.node/v1", node_id: "record-settlement-request", feature_id: "beta", kind: "Operation",
    body: { description: "Consume one settlement request Event idempotently.", reads: ["settlement-inbox"], writes: ["settlement-audit"], effects: [], guard: "message-id-not-processed", failure_continuation: "retry" },
  });
  const betaPath = path.join(source, "specs/beta/feature.json");
  const beta = JSON.parse(fs.readFileSync(betaPath, "utf8"));
  beta.nodes.push("record-settlement-request"); beta.nodes.sort(); writeJson(betaPath, beta);
  writeJson(path.join(source, "edges/settlement-requested-triggers-record.json"), { schema_version: "domainspec.edge/v1", edge_id: "settlement-requested-triggers-record", source_feature_id: "alpha", source_node_id: "settlement-requested", target_feature_id: "beta", target_node_id: "record-settlement-request", relationship: "triggers-cross", scope: "project" });
  const projectPath = path.join(source, "project.json");
  const project = JSON.parse(fs.readFileSync(projectPath, "utf8"));
  project.cross_feature_edges.push("settlement-requested-triggers-record"); project.cross_feature_edges.sort(); writeJson(projectPath, project);
  const bindingPath = path.join(source, "integrations/settle-runtime.json");
  const binding = JSON.parse(fs.readFileSync(bindingPath, "utf8"));
  binding.message_channels = [
    { channel_id: "settlement-events", purpose: "delivery", allowed_event_refs: ["alpha:settlement-requested"], publisher_operation_refs: ["alpha:settle"], consumer_operation_refs: ["beta:record-settlement-request"], evidence_boundary: "formation-only-no-delivery-claim" },
    { channel_id: "settlement-events-dead-letter", purpose: "dead-letter", allowed_event_refs: ["alpha:settlement-requested"], publisher_operation_refs: [], consumer_operation_refs: [], evidence_boundary: "terminal-route-configuration-only" },
  ];
  binding.delivery_policies = [{ policy_id: "settlement-delivery", semantics: "at-least-once", acknowledgement_boundary: "provider-accepted", ordering_scope: "none", visibility_timeout_seconds: 60, retention_seconds: 345600, max_receive_count: 5, dead_letter_channel_ref: "settlement-events-dead-letter", deduplication_owner_ref: "consumer:inbox-message-id", evidence_boundary: "provider-acceptance-is-not-application-commit" }];
  binding.transport_failure_policies = [{ policy_id: "settlement-transport-failure", retry_eligibility: "idempotent-message-id-only", max_attempts: 5, backoff: "exponential-bounded", unknown_outcome: "reconcile-by-message-id", terminal_action: "dead-letter", evidence_boundary: "bounded-attempt-observation-only" }];
  binding.transport_bindings = [{ binding_id: "settlement-message-transport", mode: "message", direction: "publish-subscribe", operation_ref: "alpha:settle", event_ref: "alpha:settlement-requested", channel_ref: "settlement-events", delivery_policy_ref: "settlement-delivery", failure_policy_ref: "settlement-transport-failure", envelope_profile_ref: "envelope:domainspec-event-json-v1", evidence_boundary: "intent-send-acceptance-delivery-and-commit-remain-distinct" }];
  writeJson(bindingPath, binding);
}

function createRecipeInputs(consumer) {
  const root = path.join(consumer, "recipe-input");
  writeJson(path.join(root, "application/package.json"), {
    name: "settlement-service",
    version: "1.0.0",
    private: true,
    type: "module",
    scripts: { build: "tsc -p tsconfig.json" },
  });
  writeJson(path.join(root, "application/package-lock.json"), {
    name: "settlement-service",
    version: "1.0.0",
    lockfileVersion: 3,
    requires: true,
    packages: { "": { name: "settlement-service", version: "1.0.0" } },
  });
  writeJson(path.join(root, "application/tsconfig.json"), {
    compilerOptions: { target: "ES2022", module: "NodeNext", moduleResolution: "NodeNext", rootDir: "src", outDir: "dist", strict: true },
    include: ["src/**/*.ts"],
  });
  fs.mkdirSync(path.join(root, "application/src"), { recursive: true });
  fs.writeFileSync(path.join(root, "application/src/api.ts"), "import http from 'node:http';\nhttp.createServer((_, response) => { response.statusCode = 204; response.end(); }).listen(8080);\n");
  fs.writeFileSync(path.join(root, "application/src/outbox-worker.ts"), "process.on('SIGTERM', () => process.exit(0));\nsetInterval(() => undefined, 1000);\n");
  fs.writeFileSync(path.join(root, "application/src/queue-consumer.ts"), "process.on('SIGTERM', () => process.exit(0));\nsetInterval(() => undefined, 1000);\n");
  fs.mkdirSync(path.join(root, "database/domain-migrations"), { recursive: true });
  fs.writeFileSync(path.join(root, "database/domain-migrations/0001_settlement.sql"), "CREATE TABLE settlement (settlement_id text PRIMARY KEY);\n");
  const requestPath = path.join(root, "deployment-recipe-request.json");
  writeJson(requestPath, {
    schema_version: "domainspec.deployment-recipe-request/v1",
    request_id: "settlement-production-recipe",
    target: "aws-ecs-fargate-postgres-v1",
    application: {
      language: "typescript",
      source_root: "application",
      lockfile: "package-lock.json",
      base_image: `node:26.8.1-bookworm-slim@sha256:${"a".repeat(64)}`,
      api: { entrypoint: ["node", "dist/api.js"], port: 8080, health_path: "/healthz" },
      worker: { entrypoint: ["node", "dist/outbox-worker.js"] },
      consumer: { entrypoint: ["node", "dist/queue-consumer.js"] },
      domain_migrations_root: "database/domain-migrations",
    },
    integration_binding_ids: ["settle-runtime"],
    environment: { name_variable: "environment_name", aws_region_variable: "aws_region" },
    authority_effect: "none",
  });
  return { root, requestPath };
}

const temporaryRoot = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-cli-clean-package-"));
try {
  const sourcePackage = JSON.parse(fs.readFileSync(path.join(cliRoot, "package.json"), "utf8"));
  assert.equal(sourcePackage.version, "1.0.0");
  assert.equal(sourcePackage.private, false);
  assert.deepEqual(sourcePackage.engines, { node: "26.8.1", npm: "11.19.0" });
  assert.equal(sourcePackage.packageManager, "npm@11.19.0");
  const packageRuns = ["pack-one", "pack-two"].map((name) => {
    const destination = path.join(temporaryRoot, name);
    fs.mkdirSync(destination);
    const output = JSON.parse(run("npm", ["pack", "--json", "--ignore-scripts", "--pack-destination", destination], cliRoot));
    assert.equal(output.length, 1);
    const packed = output[0];
    const tarball = path.join(destination, packed.filename);
    assert.equal(fs.existsSync(tarball), true);
    const bytes = fs.readFileSync(tarball);
    return {packed, tarball, sha256: crypto.createHash("sha256").update(bytes).digest("hex")};
  });
  const [{packed, tarball, sha256: tarballSha256}, secondPackage] = packageRuns;
  assert.equal(secondPackage.packed.filename, packed.filename);
  assert.equal(secondPackage.packed.size, packed.size);
  assert.equal(secondPackage.packed.shasum, packed.shasum);
  assert.equal(secondPackage.packed.integrity, packed.integrity);
  assert.deepEqual(secondPackage.packed.files, packed.files);
  assert.equal(secondPackage.sha256, tarballSha256);
  const packedPaths = packed.files.map(({ path: relativePath }) => relativePath).sort();
  assert.equal(packedPaths.includes("package.json"), true);
  assert.equal(packedPaths.includes("README.md"), true);
  for (const document of ["CHANGELOG.md", "COMPATIBILITY.md", "COMPILATION-ONTOLOGY.md", "USER-GUIDE.md", "MIGRATION.md", "SECURITY.md"]) assert.equal(packedPaths.includes(document), true, document);
  for (const example of [
    "examples/reconciled-commerce/README.md",
    "examples/reconciled-commerce/source/project.json",
    "examples/reconciled-commerce/selections/typescript.json",
    "examples/reconciled-commerce/selections/python.json",
    "examples/reconciled-commerce/selections/rust.json",
    "examples/reconciled-commerce/values.json",
    "examples/reconciled-commerce/scenarios.json",
  ]) assert.equal(packedPaths.includes(example), true, example);
  assert.equal(packedPaths.includes("dist/authoring/add-operation.js"), true);
  assert.equal(packedPaths.includes("dist/cli/main.js"), true);
  assert.equal(packedPaths.includes("dist/generation/project-instantiation.js"), true);
  assert.equal(packedPaths.includes("dist/generation/publish-project.js"), true);
  assert.equal(packedPaths.includes("dist/verification/verify-project.js"), true);
  assert.equal(packedPaths.includes("dist/generation/selected-reconciled-project.js"), true);
  assert.equal(packedPaths.includes("dist/generation/reconciled-python-project.js"), true);
  assert.equal(packedPaths.includes("dist/generation/reconciled-rust-project.js"), true);
  assert.equal(packedPaths.includes("dist/typed-backend/policy-compatibility.js"), true);
  assert.equal(packedPaths.includes("dist/typed-backend/state-machine-compatibility.js"), true);
  assert.equal(packedPaths.includes("dist/input/workflow-migration.js"), true);
  assert.equal(packedPaths.includes("dist/meta-types/frozen-catalog.generated.js"), true);
  assert.equal(packedPaths.includes("dist/system-integration/frozen-profile.generated.js"), true);
  assert.equal(packedPaths.includes("dist/system-integration/compiler.js"), true);
  assert.equal(packedPaths.includes("dist/recipe/contracts.js"), true);
  assert.equal(packedPaths.includes("dist/recipe/plan.js"), true);
  assert.equal(packedPaths.includes("dist/recipe/publish.js"), true);
  assert.equal(packedPaths.includes("dist/recipe/targets/aws-ecs-fargate-postgres-v1.js"), true);
  assert.equal(packedPaths.includes("dist/qualification/contracts.js"), true);
  assert.equal(packedPaths.includes("dist/qualification/plan.js"), true);
  assert.equal(packedPaths.includes("dist/qualification/execute.js"), true);
  assert.equal(packedPaths.includes("lean/DomainSpecMetaTypeKernel.lean"), true);
  assert.equal(packedPaths.includes("lean/DomainSpecMetaTypeCompilerRefinement.lean"), true);
  assert.equal(packedPaths.includes("lean/DomainSpecMetaTypeTypeScriptProjectionRefinement.lean"), true);
  assert.equal(packedPaths.includes("contracts/instantiation-receipt.schema.json"), true);
  assert.equal(packedPaths.includes("contracts/target-observation.schema.json"), true);
  assert.equal(packedPaths.includes("contracts/product-capabilities.schema.json"), true);
  assert.equal(packedPaths.includes("contracts/deployment-recipe-request.schema.json"), true);
  assert.equal(packedPaths.includes("contracts/deployment-recipe-manifest.schema.json"), true);
  assert.equal(packedPaths.includes("contracts/deployment-recipe-receipt.schema.json"), true);
  for (const contract of ["profile", "plan", "certificate", "run-receipt"]) assert.equal(packedPaths.includes(`contracts/recipe-qualification-${contract}.schema.json`), true, contract);
  assert.equal(packedPaths.includes("contracts/release-candidate-manifest.schema.json"), true);
  assert.equal(packedPaths.includes("tools/recipe-qualification/terraform"), true);
  assert.equal(packedPaths.includes("tools/recipe-qualification/docker"), true);
  const shippedAdapters = new Set(["tools/recipe-qualification/terraform", "tools/recipe-qualification/docker"]);
  assert.equal(packedPaths.some((relativePath) => relativePath.startsWith("src/") || relativePath.startsWith("test/") || (relativePath.startsWith("tools/") && !shippedAdapters.has(relativePath))), false);

  const cleanRuns = ["consumer-one", "consumer-two"].map((name) => {
    const consumer = path.join(temporaryRoot, name);
    fs.mkdirSync(consumer);
    fs.writeFileSync(path.join(consumer, "package.json"), `${JSON.stringify({ private: true, type: "module" })}\n`);
    run("npm", ["install", "--ignore-scripts", "--no-audit", "--no-fund", tarball], consumer);
    const installedAdapterRoot = path.join(consumer, "node_modules/@domainspec-v2/cli/tools/recipe-qualification");
    for (const [adapter, image] of [
      ["terraform", "hashicorp/terraform:1.16.0@sha256:fb5ea091b84f35e111e3a83eb8a6cdeb264bba11687c2eebc52253ade183022f"],
      ["docker", "docker:28.0.1-cli@sha256:043c259759666d273afa94a9c9175a87a11f16cde2f613f4c527e4395b703a1f"],
    ]) {
      const adapterPath = path.join(installedAdapterRoot, adapter);
      const identity = JSON.parse(run(adapterPath, ["domainspec-adapter-identity"], consumer));
      assert.deepEqual(identity, { adapter_protocol: "domainspec.oci-tool-adapter/v1", image });
      assert.equal(spawnSync(adapterPath, [adapter === "terraform" ? "apply" : "push"], { cwd: consumer, encoding: "utf8" }).status, 64);
    }
    run(process.execPath, ["--input-type=module", "-e", "const root = await import('@domainspec-v2/cli'); const forbidden = ['emitCompilerRefinementOutput', 'createCompilerRefinementOutput', 'toTypeScriptProjectionPayload', 'FormalizationMaterializationHooks', 'runInMemoryProject', 'runDurableOperation', 'PostgresTransactionalOutbox'].filter((name) => name in root); const required = ['addOperation', 'addQuery', 'addCalculation', 'addRule', 'addPolicy', 'addMapping', 'PRODUCT_CAPABILITIES', 'planDeploymentRecipe', 'publishDeploymentRecipe', 'verifyDeploymentRecipe', 'validateDeploymentRecipeReceipt', 'createRecipeQualificationProfile', 'planRecipeQualification', 'qualifyDeploymentRecipe', 'verifyRecipeQualification', 'decodeSelectedReconciledCompilation', 'planSelectedReconciledProject', 'planCompiledSelectedReconciledProject', 'publishReconciledProject', 'verifyReconciledProject', 'migrateTypedPolicyV1', 'migrateLegacyStateMachine', 'planWorkflowOccurrenceMigration'].filter((name) => !(name in root)); if (forbidden.length || required.length) throw new Error(JSON.stringify({forbidden,required})); const runtime = await import('@domainspec-v2/cli/experimental/runtime'); if (!('runInMemoryProject' in runtime) || !('PostgresTransactionalOutbox' in runtime) || !('SqsPostgresOutboxTransport' in runtime)) throw new Error('experimental runtime subpath incomplete');"], consumer);
    const source = path.join(consumer, "source");
    fs.cpSync(fixtureRoot, source, { recursive: true });
    addRecipeEvidence(source);
    const rulePath = path.join(source, "specs/beta/nodes/can-complete-settlement.json");
    const rule = JSON.parse(fs.readFileSync(rulePath, "utf8"));
    rule.body.predicate = "structured:domainspec.typed-rule/v1";
    rule.body.typed_contract = {
      schema_version: "domainspec.typed-rule/v1",
      ontology_rule: "TEST-RULE-CAN-COMPLETE",
      parameters: [{ name: "candidate", type: { kind: "scalar", name: "String" } }],
      expression: { op: "not", term: { op: "eq", left: { op: "path", root: "candidate", properties: [] }, right: { op: "literal", type: "String", value: "" } } },
    };
    fs.writeFileSync(rulePath, `${JSON.stringify(rule, null, 2)}\n`);
    const executable = path.join(consumer, "node_modules/.bin/domainspec-v2");
    assert.equal(run(executable, ["--version"], consumer).trim(), "1.0.0");
    const capabilities = JSON.parse(run(executable, ["capabilities"], consumer));
    assert.equal(capabilities.product.lifecycle, "stable");
    assert.deepEqual(capabilities.experimental_commands, ["run"]);
    const capabilitiesPath = path.join(consumer, "capabilities.json");
    fs.writeFileSync(capabilitiesPath, `${JSON.stringify(capabilities)}\n`);
    run("python3", ["-c", "import json,jsonschema,sys; jsonschema.Draft202012Validator(json.load(open(sys.argv[1]))).validate(json.load(open(sys.argv[2])))", path.join(consumer, "node_modules/@domainspec-v2/cli/contracts/product-capabilities.schema.json"), capabilitiesPath], consumer);
    const doctor = JSON.parse(run(executable, ["doctor"], consumer, { PATH: doctorPath }));
    assert.equal(doctor.result, "pass");
    const target = path.join(consumer, "target");
    const authoringResult = JSON.parse(run(executable, [
      "add", "operation", source,
      "--feature", "alpha",
      "--name", "create-order",
      "--description", "Create an order from the current cart.",
      "--reads", "customer.status,cart.total",
      "--writes", "order.id,order.status,order.total",
      "--effects", "OrderCreated",
      "--guard", "customer-is-active-and-cart-is-valid",
      "--failure-continuation", "return-create-order-error",
    ], consumer));
    const sourceLint = JSON.parse(run(executable, ["lint", source], consumer));
    const result = JSON.parse(run(executable, ["instantiate", source, "--node", "alpha:settle", "--language", "typescript", "--target-root", target, "--integration-profile", "provider-neutral-v1", "--integration-binding-set", "settle-runtime"], consumer));
    const formalizationTarget = path.join(consumer, "formalization", "CurrentDomainSpecMetaTypes.lean");
    const formalizationResult = JSON.parse(run(executable, ["formalize", source, "--target", formalizationTarget], consumer));
    const formalizationCheck = JSON.parse(run(executable, ["formalize-check", source, "--target", formalizationTarget], consumer));
    const projectTarget = path.join(consumer, "project-target");
    const projectResult = JSON.parse(run(executable, ["instantiate-project", source, "--languages", "typescript,python,rust", "--target-root", projectTarget], consumer));
    const verifiedTarget = path.join(consumer, "verified-target");
    const verificationResult = JSON.parse(run(executable, ["verify-project", source, "--target-root", verifiedTarget], consumer, exactValidationToolchain));
    const recipeInputs = createRecipeInputs(consumer);
    const recipeTarget = path.join(consumer, "deployment-recipe");
    const recipePlan = JSON.parse(run(executable, ["recipe-plan", source, "--request", recipeInputs.requestPath, "--consumer-root", recipeInputs.root], consumer));
    const recipeGeneration = JSON.parse(run(executable, ["recipe-generate", source, "--request", recipeInputs.requestPath, "--consumer-root", recipeInputs.root, "--target-root", recipeTarget], consumer));
    const recipeVerification = JSON.parse(run(executable, ["recipe-verify", source, "--request", recipeInputs.requestPath, "--consumer-root", recipeInputs.root, "--target-root", recipeTarget], consumer));
    return { consumer, executable, source, target, projectTarget, verifiedTarget, verificationResult, projectResult, formalizationTarget, formalizationResult, formalizationCheck, authoringResult, sourceLint, result, recipeInputs, recipeTarget, recipePlan, recipeGeneration, recipeVerification };
  });
  const authoringResults = cleanRuns.map(({ authoringResult }) => authoringResult);
  assert.equal(authoringResults.every(({ result, selector, source_count }) => result === "pass" && selector === "alpha:create-order" && source_count >= 24), true);
  assert.equal(authoringResults[0].source_manifest_sha256, authoringResults[1].source_manifest_sha256);
  assert.equal(cleanRuns.every(({ sourceLint, authoringResult }) => sourceLint.result === "pass" && sourceLint.source_manifest.manifest_sha256 === authoringResult.source_manifest_sha256), true);
  assert.equal(
    fs.readFileSync(path.join(cleanRuns[0].source, authoringResults[0].node_path), "utf8"),
    fs.readFileSync(path.join(cleanRuns[1].source, authoringResults[1].node_path), "utf8"),
  );
  const commandResults = cleanRuns.map(({ result }) => result);
  assert.equal(commandResults.every(({ result }) => result === "pass"), true);
  assert.equal(cleanRuns.every(({ formalizationResult, formalizationCheck }) => formalizationResult.result === "pass" && formalizationCheck.result === "pass"), true);
  assert.equal(cleanRuns.every(({ projectResult, verificationResult }) => projectResult.result === "pass" && verificationResult.result === "pass" && verificationResult.skipped_check_count === 0 && verificationResult.inferred_evidence_count === 0), true);
  assert.equal(cleanRuns[0].projectResult.project_plan_sha256, cleanRuns[1].projectResult.project_plan_sha256);
  assert.equal(cleanRuns[0].verificationResult.project_plan_sha256, cleanRuns[1].verificationResult.project_plan_sha256);
  assert.equal(cleanRuns.every(({ recipePlan, recipeGeneration, recipeVerification }) => recipePlan.authority_effect === "none" && recipeGeneration.result === "pass" && recipeVerification.result === "pass"), true);
  assert.equal(cleanRuns[0].recipePlan.plan_sha256, cleanRuns[1].recipePlan.plan_sha256);
  assert.equal(cleanRuns[0].recipePlan.manifest_sha256, cleanRuns[1].recipePlan.manifest_sha256);
  assert.equal(cleanRuns[0].recipePlan.receipt_sha256, cleanRuns[1].recipePlan.receipt_sha256);
  assert.deepEqual(inventory(cleanRuns[0].recipeTarget), inventory(cleanRuns[1].recipeTarget));
  assert.equal(cleanRuns[0].formalizationResult.render_payload_sha256, cleanRuns[1].formalizationResult.render_payload_sha256);
  assert.equal(cleanRuns[0].formalizationResult.project_graph_sha256, cleanRuns[1].formalizationResult.project_graph_sha256);
  assert.equal(cleanRuns[0].formalizationResult.lean_module_set_sha256, cleanRuns[1].formalizationResult.lean_module_set_sha256);
  assert.equal(cleanRuns[0].formalizationResult.proof_unit_sha256, cleanRuns[1].formalizationResult.proof_unit_sha256);
  assert.deepEqual(inventory(path.dirname(cleanRuns[0].formalizationTarget)), inventory(path.dirname(cleanRuns[1].formalizationTarget)));
  const deterministicInventory = inventory(cleanRuns[0].target);
  assert.deepEqual(deterministicInventory, inventory(cleanRuns[1].target));
  const lint = JSON.parse(run(cleanRuns[0].executable, ["lint", cleanRuns[0].target], cleanRuns[0].consumer));
  assert.equal(lint.result, "pass");
  const receipt = JSON.parse(run(cleanRuns[1].executable, ["receipt", cleanRuns[1].target], cleanRuns[1].consumer));
  assert.equal(receipt.observation.result, "pass");
  assert.equal(receipt.receipt.input.source_manifest_sha256, authoringResults[1].source_manifest_sha256);
  const mutatedArtifact = commandResults[0].observation.observed_artifacts[0].relative_path;
  fs.appendFileSync(path.join(cleanRuns[0].target, mutatedArtifact), "// clean-package causal drift\n");
  const failureRun = spawnSync(cleanRuns[0].executable, ["lint", cleanRuns[0].target], { cwd: cleanRuns[0].consumer, encoding: "utf8" });
  assert.equal(failureRun.status, 1, failureRun.stderr);
  const failureObservation = JSON.parse(failureRun.stdout);
  assert.equal(failureObservation.result, "fail");
  assert.equal(failureObservation.code, "MTCLI_OBSERVE_EXACT_REALIZATION");
  const schemaCases = [
    [path.join(cliRoot, "contracts/instantiation-receipt.schema.json"), receipt.receipt, "instantiation-receipt.json"],
    [path.join(cliRoot, "contracts/target-observation.schema.json"), receipt.observation, "target-observation.json"],
    [path.join(cliRoot, "contracts/target-observation.schema.json"), failureObservation, "target-observation-failure.json"],
    [path.join(cliRoot, "contracts/deployment-recipe-request.schema.json"), JSON.parse(fs.readFileSync(cleanRuns[0].recipeInputs.requestPath, "utf8")), "deployment-recipe-request.json"],
    [path.join(cliRoot, "contracts/deployment-recipe-manifest.schema.json"), JSON.parse(fs.readFileSync(path.join(cleanRuns[0].recipeTarget, "deployment-manifest.json"), "utf8")), "deployment-recipe-manifest.json"],
    [path.join(cliRoot, "contracts/deployment-recipe-receipt.schema.json"), JSON.parse(fs.readFileSync(path.join(cleanRuns[0].recipeTarget, ".domainspec/deployment-recipe-receipt.json"), "utf8")), "deployment-recipe-receipt.json"],
  ];
  for (const [schemaPath, value, filename] of schemaCases) {
    const valuePath = path.join(temporaryRoot, filename);
    fs.writeFileSync(valuePath, `${JSON.stringify(value)}\n`);
    run("python3", ["-c", "import json,jsonschema,sys; jsonschema.Draft202012Validator(json.load(open(sys.argv[1]))).validate(json.load(open(sys.argv[2])))", schemaPath, valuePath], temporaryRoot);
  }

  process.stdout.write(`${JSON.stringify({
    schema_version: "domainspec.clean-package-validation/v1",
    result: "pass",
    package: { filename: packed.filename, size_bytes: packed.size, sha256: tarballSha256, npm_sha1: packed.shasum, integrity: packed.integrity, files: packedPaths },
    package_run_count: packageRuns.length,
    package_byte_equivalent: true,
    clean_run_count: cleanRuns.length,
    authored_operation: {
      selector: authoringResults[0].selector,
      node_path: authoringResults[0].node_path,
      source_manifest_sha256: authoringResults[0].source_manifest_sha256,
    },
    deterministic_target_inventory: deterministicInventory,
    plan_sha256: commandResults[0].plan_sha256,
    receipt_sha256: commandResults[0].receipt_sha256,
    formalization: {
      render_payload_sha256: cleanRuns[0].formalizationResult.render_payload_sha256,
      project_graph_sha256: cleanRuns[0].formalizationResult.project_graph_sha256,
      lean_module_set_sha256: cleanRuns[0].formalizationResult.lean_module_set_sha256,
      proof_unit_sha256: cleanRuns[0].formalizationResult.proof_unit_sha256,
      file_count: inventory(path.dirname(cleanRuns[0].formalizationTarget)).length,
    },
    project_plan_sha256: cleanRuns[0].projectResult.project_plan_sha256,
    deployment_recipe: {
      target: "aws-ecs-fargate-postgres-v1",
      plan_sha256: cleanRuns[0].recipePlan.plan_sha256,
      manifest_sha256: cleanRuns[0].recipePlan.manifest_sha256,
      receipt_sha256: cleanRuns[0].recipePlan.receipt_sha256,
      artifact_count: inventory(cleanRuns[0].recipeTarget).length,
      authority_effect: "none",
    },
    project_verification_checks: cleanRuns[0].verificationResult.checks.map(({ id, result }) => ({ id, result })),
    authority_effect: "none",
  }, null, 2)}\n`);
} finally {
  assert.equal(temporaryRoot.startsWith(path.join(os.tmpdir(), "domainspec-cli-clean-package-")), true);
  fs.rmSync(temporaryRoot, { recursive: true, force: true });
}
