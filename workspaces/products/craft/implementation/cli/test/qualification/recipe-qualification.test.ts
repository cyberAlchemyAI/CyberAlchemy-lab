import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { runCli } from "../../src/cli/main.ts";
import { canonicalJson } from "../../src/input/source-manifest.ts";
import { decodeDeploymentRecipeRequest, type DeploymentRecipeRequestV1 } from "../../src/recipe/contracts.ts";
import { planDeploymentRecipe } from "../../src/recipe/plan.ts";
import { publishDeploymentRecipe } from "../../src/recipe/publish.ts";
import { RECIPE_QUALIFICATION_ADAPTER_PROTOCOL, RECIPE_QUALIFICATION_DOCKER_IMAGE, RECIPE_QUALIFICATION_TERRAFORM_IMAGE, createRecipeQualificationProfile, parseRecipeQualificationProfileJson } from "../../src/qualification/contracts.ts";
import { planRecipeQualification } from "../../src/qualification/plan.ts";
import { qualifyDeploymentRecipe, verifyRecipeQualification } from "../../src/qualification/execute.ts";
import { createCompleteL1Project } from "../helpers/l1-project.ts";

const DIGEST = "a".repeat(64);

function write(file: string, content: string): void { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, content); }
function writeJson(file: string, value: unknown): void { write(file, `${JSON.stringify(value, null, 2)}\n`); }

function consumer(): string {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-qualification-consumer-"));
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
    schema_version: "domainspec.deployment-recipe-request/v1", request_id: "settlement-production-recipe", target: "aws-ecs-fargate-postgres-v1",
    application: { language: "typescript", source_root: "application", lockfile: "package-lock.json", base_image: `node:26.8.1-bookworm-slim@sha256:${DIGEST}`, api: { entrypoint: ["node", "dist/api.js"], port: 8080, health_path: "/healthz" }, worker: { entrypoint: ["node", "dist/outbox-worker.js"] }, consumer: { entrypoint: ["node", "dist/queue-consumer.js"] }, domain_migrations_root: "database/domain-migrations" },
    integration_binding_ids: ["settle-runtime"], environment: { name_variable: "environment_name", aws_region_variable: "aws_region" }, authority_effect: "none",
  });
}

function profile(terraformVersion = "1.16.0") {
  return createRecipeQualificationProfile({
    schema_version: "domainspec.recipe-qualification-profile/v1", profile_id: "domainspec.recipe-qualification.l0", ontology_id: "domainspec.recipe-qualification-ontology@1", qualification_level: "recipe-executable-v1", recipe_target: "aws-ecs-fargate-postgres-v1",
    required_checks: ["recipe-byte-verify", "terraform-fmt-check", "terraform-init-backendless", "terraform-validate", "docker-buildx-bake-check"], optional_checks: [],
    toolchain: { terraform: { version: terraformVersion, adapter_protocol: RECIPE_QUALIFICATION_ADAPTER_PROTOCOL, image: RECIPE_QUALIFICATION_TERRAFORM_IMAGE }, docker: { version: "28.0.1", buildx_version: "0.21.3", adapter_protocol: RECIPE_QUALIFICATION_ADAPTER_PROTOCOL, image: RECIPE_QUALIFICATION_DOCKER_IMAGE } }, network_policy: "provider-registry-read-only", normalization_profile: "domainspec.recipe-qualification-normalization/v1", effect_ceiling: "no-external-effect", authority_effect: "none",
  });
}

function tools(root: string): { terraform: string; docker: string; bin: string } {
  const bin = path.join(root, "bin");
  const terraform = path.join(bin, "terraform");
  const docker = path.join(bin, "docker");
  write(terraform, `#!/bin/sh
if [ "$1" = "domainspec-adapter-identity" ]; then printf '%s\\n' '{"adapter_protocol":"domainspec.oci-tool-adapter/v1","image":"${RECIPE_QUALIFICATION_TERRAFORM_IMAGE}"}'; exit 0; fi
if [ "$1" = "version" ]; then printf '%s\\n' '{"terraform_version":"1.16.0"}'; exit 0; fi
if [ "$1" = "init" ]; then exit 0; fi
if [ "$1" = "fmt" ] || [ "$1" = "validate" ]; then exit 0; fi
exit 31
`);
  write(docker, `#!/bin/sh
if [ "$1" = "domainspec-adapter-identity" ]; then printf '%s\\n' '{"adapter_protocol":"domainspec.oci-tool-adapter/v1","image":"${RECIPE_QUALIFICATION_DOCKER_IMAGE}"}'; exit 0; fi
if [ "$1" = "version" ]; then printf '%s\\n' '28.0.1'; exit 0; fi
if [ "$1" = "buildx" ] && [ "$2" = "version" ]; then printf '%s\\n' 'github.com/docker/buildx v0.21.3'; exit 0; fi
if [ "$1" = "buildx" ] && [ "$2" = "bake" ]; then exit 0; fi
exit 32
`);
  fs.chmodSync(terraform, 0o755); fs.chmodSync(docker, 0o755);
  return { terraform, docker, bin };
}

function schemaValidate(schema: string, value: unknown, root: string): void {
  const valuePath = path.join(root, `${path.basename(schema)}.value.json`); writeJson(valuePath, value);
  const script = "import json,sys; from jsonschema import Draft202012Validator; schema=json.load(open(sys.argv[1])); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(json.load(open(sys.argv[2])))";
  const result = spawnSync("python3", ["-c", script, path.resolve("contracts", schema), valuePath], { cwd: path.resolve("."), encoding: "utf8" });
  assert.equal(result.status, 0, result.stderr);
}

test("qualification emits deterministic certificate and host receipt for the exact compiled recipe", () => {
  const fixture = createCompleteL1Project(); const consumerRoot = consumer(); const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-qualification-pass-")); const target = path.join(parent, "recipe"); const fake = tools(parent);
  try {
    publishDeploymentRecipe(planDeploymentRecipe(fixture.root, request(), consumerRoot), target);
    const before = planRecipeQualification(fixture.root, request(), consumerRoot, target, profile());
    const left = qualifyDeploymentRecipe(fixture.root, request(), consumerRoot, target, profile(), path.join(parent, "left"), { terraformExecutable: fake.terraform, dockerExecutable: fake.docker });
    const right = qualifyDeploymentRecipe(fixture.root, request(), consumerRoot, target, profile(), path.join(parent, "right"), { terraformExecutable: fake.terraform, dockerExecutable: fake.docker });
    assert.equal(left.certificate.result, "pass");
    assert.equal(left.plan.plan_sha256, before.plan_sha256);
    assert.equal(left.certificate.certificate_sha256, right.certificate.certificate_sha256);
    assert.equal(left.receipt.receipt_sha256, right.receipt.receipt_sha256);
    assert.deepEqual(left.certificate.observations.map(({ check_id, result }) => ({ check_id, result })), ["recipe-byte-verify", "terraform-fmt-check", "terraform-init-backendless", "terraform-validate", "docker-buildx-bake-check"].map((check_id) => ({ check_id, result: "pass" })));
    assert.match(left.certificate.observations.find(({ check_id }) => check_id === "terraform-init-backendless")!.provider_lock_sha256!, /^[a-f0-9]{64}$/);
    assert.equal(verifyRecipeQualification(fixture.root, request(), consumerRoot, target, profile(), path.join(parent, "left")).result, "pass");
    schemaValidate("recipe-qualification-profile.schema.json", profile(), parent);
    schemaValidate("recipe-qualification-plan.schema.json", left.plan, parent);
    schemaValidate("recipe-qualification-certificate.schema.json", left.certificate, parent);
    schemaValidate("recipe-qualification-run-receipt.schema.json", left.receipt, parent);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(consumerRoot, { recursive: true, force: true }); fs.rmSync(parent, { recursive: true, force: true }); }
});

test("qualification collects fail and not_evaluable without skipped checks", () => {
  const fixture = createCompleteL1Project(); const consumerRoot = consumer(); const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-qualification-results-")); const target = path.join(parent, "recipe"); const fake = tools(parent);
  try {
    publishDeploymentRecipe(planDeploymentRecipe(fixture.root, request(), consumerRoot), target);
    const mismatch = qualifyDeploymentRecipe(fixture.root, request(), consumerRoot, target, profile("9.9.9"), path.join(parent, "mismatch"), { terraformExecutable: fake.terraform, dockerExecutable: fake.docker });
    assert.equal(mismatch.certificate.result, "fail");
    assert.equal(mismatch.certificate.observations.find(({ check_id }) => check_id === "terraform-fmt-check")!.result, "fail");
    assert.equal(mismatch.certificate.observations.find(({ check_id }) => check_id === "terraform-validate")!.result, "not_evaluable");
    assert.deepEqual(mismatch.certificate.observations.find(({ check_id }) => check_id === "terraform-validate")!.causal_blockers, ["terraform-init-backendless"]);
    const unavailable = qualifyDeploymentRecipe(fixture.root, request(), consumerRoot, target, profile(), path.join(parent, "unavailable"), { terraformExecutable: "/usr/bin/false", dockerExecutable: "/usr/bin/false" });
    assert.equal(unavailable.certificate.result, "not_evaluable");
    assert.equal(unavailable.certificate.observations.length, 5);
    assert.equal(unavailable.certificate.observations.some(({ result }) => result === "not_evaluable"), true);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(consumerRoot, { recursive: true, force: true }); fs.rmSync(parent, { recursive: true, force: true }); }
});

test("profiles and published evidence fail closed under hostile mutation", () => {
  const fixture = createCompleteL1Project(); const consumerRoot = consumer(); const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-qualification-hostile-")); const target = path.join(parent, "recipe"); const fake = tools(parent);
  try {
    assert.throws(() => parseRecipeQualificationProfileJson('{"schema_version":"domainspec.recipe-qualification-profile/v1","schema_version":"domainspec.recipe-qualification-profile/v1"}'), (error: unknown) => (error as { code?: string }).code === "MTCLI_QUALIFICATION_DUPLICATE_KEY");
    const stale = JSON.parse(JSON.stringify(profile())); stale.profile_id = "changed";
    assert.throws(() => parseRecipeQualificationProfileJson(JSON.stringify(stale)), (error: unknown) => (error as { code?: string }).code === "MTCLI_QUALIFICATION_PROFILE_DIGEST");
    publishDeploymentRecipe(planDeploymentRecipe(fixture.root, request(), consumerRoot), target);
    const publication = qualifyDeploymentRecipe(fixture.root, request(), consumerRoot, target, profile(), path.join(parent, "qualification"), { terraformExecutable: fake.terraform, dockerExecutable: fake.docker });
    fs.appendFileSync(path.join(publication.qualification_root, "evidence/terraform-validate.stdout.txt"), "tamper\n");
    assert.equal(verifyRecipeQualification(fixture.root, request(), consumerRoot, target, profile(), publication.qualification_root).result, "fail");
    fs.appendFileSync(path.join(target, "infrastructure/terraform/main.tf"), "# target drift\n");
    assert.throws(() => planRecipeQualification(fixture.root, request(), consumerRoot, target, profile()), (error: unknown) => (error as { code?: string }).code === "MTCLI_QUALIFICATION_RECIPE_STALE");
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(consumerRoot, { recursive: true, force: true }); fs.rmSync(parent, { recursive: true, force: true }); }
});

test("qualification is sensitive to selected source bytes and insensitive to unrelated bytes", () => {
  const fixture = createCompleteL1Project(); const consumerRoot = consumer(); const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-qualification-sensitivity-"));
  try {
    const firstTarget = path.join(parent, "first"); publishDeploymentRecipe(planDeploymentRecipe(fixture.root, request(), consumerRoot), firstTarget);
    const first = planRecipeQualification(fixture.root, request(), consumerRoot, firstTarget, profile());
    write(path.join(fixture.root, "unrelated.txt"), "not selected\n");
    assert.equal(planRecipeQualification(fixture.root, request(), consumerRoot, firstTarget, profile()).plan_sha256, first.plan_sha256);
    const operationPath = path.join(fixture.root, "specs/alpha/nodes/settle.json"); const operation = JSON.parse(fs.readFileSync(operationPath, "utf8")); operation.body.description = "Selected source changed."; writeJson(operationPath, operation);
    const secondTarget = path.join(parent, "second"); publishDeploymentRecipe(planDeploymentRecipe(fixture.root, request(), consumerRoot), secondTarget);
    const second = planRecipeQualification(fixture.root, request(), consumerRoot, secondTarget, profile());
    assert.notEqual(second.subject.source_manifest_sha256, first.subject.source_manifest_sha256);
    assert.notEqual(second.plan_sha256, first.plan_sha256);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(consumerRoot, { recursive: true, force: true }); fs.rmSync(parent, { recursive: true, force: true }); }
});

test("qualification CLI plans, runs, and verifies through fixed adapters", () => {
  const fixture = createCompleteL1Project(); const consumerRoot = consumer(); const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-qualification-cli-")); const target = path.join(parent, "recipe"); const fake = tools(parent); const requestPath = path.join(parent, "request.json"); const profilePath = path.join(parent, "profile.json"); const qualificationRoot = path.join(parent, "qualification");
  writeJson(requestPath, request()); writeJson(profilePath, profile()); publishDeploymentRecipe(planDeploymentRecipe(fixture.root, request(), consumerRoot), target);
  const invoke = (args: string[]) => { const output: string[] = []; const errors: string[] = []; const status = runCli(args, { stdout: (value) => output.push(value), stderr: (value) => errors.push(value) }); return { status, value: JSON.parse(output.at(-1) ?? errors.at(-1) ?? "{}") as Record<string, unknown> }; };
  const originalTerraformAdapter = process.env.DOMAINSPEC_TERRAFORM_ADAPTER; const originalDockerAdapter = process.env.DOMAINSPEC_DOCKER_ADAPTER;
  process.env.DOMAINSPEC_TERRAFORM_ADAPTER = fake.terraform; process.env.DOMAINSPEC_DOCKER_ADAPTER = fake.docker;
  try {
    const base = [fixture.root, "--request", requestPath, "--consumer-root", consumerRoot, "--target-root", target, "--profile", profilePath];
    assert.equal(invoke(["recipe-qualification-plan", ...base]).status, 0);
    const qualified = invoke(["recipe-qualify", ...base, "--qualification-root", qualificationRoot]); assert.equal(qualified.status, 0); assert.equal(qualified.value.result, "pass");
    const verified = invoke(["recipe-qualification-verify", ...base, "--qualification-root", qualificationRoot]); assert.equal(verified.status, 0); assert.equal(verified.value.result, "pass");
  } finally {
    if (originalTerraformAdapter === undefined) delete process.env.DOMAINSPEC_TERRAFORM_ADAPTER; else process.env.DOMAINSPEC_TERRAFORM_ADAPTER = originalTerraformAdapter;
    if (originalDockerAdapter === undefined) delete process.env.DOMAINSPEC_DOCKER_ADAPTER; else process.env.DOMAINSPEC_DOCKER_ADAPTER = originalDockerAdapter;
    fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(consumerRoot, { recursive: true, force: true }); fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("L1 OCI adapters expose immutable identities and reject forbidden invocations before Docker", () => {
  const terraform = path.resolve("tools/recipe-qualification/terraform"); const docker = path.resolve("tools/recipe-qualification/docker");
  for (const [adapter, image] of [[terraform, RECIPE_QUALIFICATION_TERRAFORM_IMAGE], [docker, RECIPE_QUALIFICATION_DOCKER_IMAGE]] as const) {
    const identity = spawnSync(adapter, ["domainspec-adapter-identity"], { encoding: "utf8" });
    assert.equal(identity.status, 0, identity.stderr); assert.deepEqual(JSON.parse(identity.stdout), { adapter_protocol: RECIPE_QUALIFICATION_ADAPTER_PROTOCOL, image });
  }
  assert.equal(spawnSync(terraform, ["plan"], { encoding: "utf8" }).status, 64);
  assert.equal(spawnSync(terraform, ["apply"], { encoding: "utf8" }).status, 64);
  assert.equal(spawnSync(docker, ["buildx", "bake", "--push"], { encoding: "utf8" }).status, 64);
  assert.equal(spawnSync(docker, ["push", "forbidden"], { encoding: "utf8" }).status, 64);
});

test("Docker qualification streams its checked tree across a nested daemon boundary", () => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-qualification-nested-docker-"));
  const bin = path.join(parent, "bin"); const target = path.join(parent, "target"); const log = path.join(parent, "docker.log"); const tarList = path.join(parent, "tar.list");
  const fakeDocker = path.join(bin, "docker");
  write(path.join(target, "images/docker-bake.hcl"), "group \"default\" { targets = [] }\n");
  write(fakeDocker, `#!/bin/sh
set -eu
printf '%s\\n' "$*" >> "$FAKE_DOCKER_LOG"
case "$1" in
  create) printf '%s\\n' 'qualification-container' ;;
  start) tar -tf - > "$FAKE_TAR_LIST"; grep -qx './images/docker-bake.hcl' "$FAKE_TAR_LIST" ;;
  rm) exit 0 ;;
  *) exit 90 ;;
esac
`);
  fs.chmodSync(fakeDocker, 0o755);
  try {
    const adapter = path.resolve("tools/recipe-qualification/docker");
    const result = spawnSync(adapter, ["buildx", "bake", "--file", "images/docker-bake.hcl", "--check"], {
      cwd: target,
      encoding: "utf8",
      env: { ...process.env, PATH: `${bin}:${process.env.PATH ?? ""}`, FAKE_DOCKER_LOG: log, FAKE_TAR_LIST: tarList },
    });
    assert.equal(result.status, 0, result.stderr);
    assert.match(fs.readFileSync(log, "utf8"), /^create .*--interactive/m);
    assert.match(fs.readFileSync(log, "utf8"), /^start --attach --interactive qualification-container$/m);
    assert.match(fs.readFileSync(log, "utf8"), /^rm --force qualification-container$/m);
    assert.match(fs.readFileSync(tarList, "utf8"), /^\.\/images\/docker-bake\.hcl$/m);
    assert.doesNotMatch(fs.readFileSync(adapter, "utf8"), /--volume "\$PWD:\/workspace"/);
  } finally { fs.rmSync(parent, { recursive: true, force: true }); }
});
