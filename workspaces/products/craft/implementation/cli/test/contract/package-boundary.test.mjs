import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const cliRoot = path.resolve(testDir, "../..");
const packageJson = JSON.parse(fs.readFileSync(path.join(cliRoot, "package.json"), "utf8"));
const packageLock = JSON.parse(fs.readFileSync(path.join(cliRoot, "package-lock.json"), "utf8"));
const tsconfig = JSON.parse(fs.readFileSync(path.join(cliRoot, "tsconfig.json"), "utf8"));
const source = fs.readFileSync(path.join(cliRoot, "src/index.ts"), "utf8");
const versionSource = fs.readFileSync(path.join(cliRoot, "src/version.ts"), "utf8");

test("package identity and supported bin are exact", () => {
  assert.equal(packageJson.name, "@domainspec-v2/cli");
  assert.equal(packageJson.version, "1.0.0");
  assert.equal(packageJson.private, false);
  assert.equal(packageJson.type, "module");
  assert.deepEqual(packageJson.bin, { "domainspec-v2": "./dist/cli/main.js" });
});

test("stable root, experimental runtime, and whole-application planning subpaths are exported", () => {
  assert.deepEqual(packageJson.exports, {
    ".": { types: "./dist/index.d.ts", import: "./dist/index.js" },
    "./experimental/runtime": { types: "./dist/experimental/runtime.d.ts", import: "./dist/experimental/runtime.js" },
    "./whole-application": { types: "./dist/whole-application.d.ts", import: "./dist/whole-application.js" },
    "./reference-runtime": { types: "./dist/reference-runtime.d.ts", import: "./dist/reference-runtime.js" }
  });
  for (const required of [
    "dist",
    "lean",
    "contracts/deployment-recipe-request.schema.json",
    "contracts/deployment-recipe-manifest.schema.json",
    "contracts/deployment-recipe-receipt.schema.json",
    "contracts/recipe-qualification-profile.schema.json",
    "contracts/recipe-qualification-plan.schema.json",
    "contracts/recipe-qualification-certificate.schema.json",
    "contracts/recipe-qualification-run-receipt.schema.json",
    "contracts/release-candidate-manifest.schema.json",
    "contracts/provider-pack-selection-v1.schema.json",
    "contracts/provider-application-runtime-evidence-v1.schema.json",
    "contracts/integration-generation-source-v2.schema.json",
    "contracts/application-integration-binding-v1.schema.json",
    "contracts/compiled-application-graph-v1.schema.json",
    "contracts/whole-application-plan-v1.schema.json",
    "contracts/persistence-composition-v2.schema.json",
    "contracts/messaging-composition-v2.schema.json",
    "contracts/external-api-composition-v2.schema.json",
    "contracts/integration-observation-v1.schema.json",
    "contracts/integration-kernel-v2.schema.json",
    "tools/recipe-qualification/terraform",
    "tools/recipe-qualification/docker",
    "README.md",
    "USER-GUIDE.md",
    "WHOLE-APPLICATION.md",
    "examples/reconciled-commerce",
    "CHANGELOG.md",
    "COMPATIBILITY.md",
    "MIGRATION.md",
    "SECURITY.md",
  ]) assert.equal(packageJson.files.includes(required), true, required);
  assert.equal("workspaces" in packageJson, false);
  assert.equal("dependencies" in packageJson, false);
  assert.equal("devDependencies" in packageJson, false);
  for (const required of ["typecheck", "build", "test", "test:whole-application", "test:installed-whole-application", "schemas:check", "recipe-qualification:check", "recipe-qualification:l1", "test:contract", "validate:rust", "validate:clean-package", "verify:product", "pack:release"]) assert.equal(typeof packageJson.scripts[required], "string", required);
  assert.deepEqual(packageJson.publishConfig, { access: "restricted", provenance: true });
  assert.equal(packageJson.packageManager, "npm@11.19.0");
});

test("development and factory command surfaces are not re-exported", () => {
  for (const forbidden of ["roundtrip", "derive", "self-check", "emit-tests", "factory", "replay", "emitCompilerRefinementOutput", "createCompilerRefinementOutput", "FormalizationMaterializationHooks"]) {
    assert.equal(source.includes(forbidden), false, forbidden);
    assert.equal(JSON.stringify(packageJson.exports).includes(forbidden), false, forbidden);
  }
  assert.match(source, /from "\.\/version\.js"/);
  for (const runtimeExport of ["runInMemoryProject", "runDurableOperation", "PostgresTransactionalOutbox", "decodeRuntimeInvocation"]) assert.equal(source.includes(runtimeExport), false, runtimeExport);
  for (const stableExport of [
    "addOperation",
    "addQuery",
    "addCalculation",
    "addRule",
    "addPolicy",
    "addMapping",
    "migrateTypedPolicyV1",
    "migrateLegacyStateMachine",
    "planWorkflowOccurrenceMigration",
    "planDeploymentRecipe",
    "publishDeploymentRecipe",
    "verifyDeploymentRecipe",
    "validateDeploymentRecipeReceipt",
    "createRecipeQualificationProfile",
    "planRecipeQualification",
    "qualifyDeploymentRecipe",
    "verifyRecipeQualification",
  ]) assert.equal(source.includes(stableExport), true, stableExport);
});

test("deployment recipe commands remain stable while the capability stays candidate and non-effectful", () => {
  for (const command of ["recipe-plan", "recipe-generate", "recipe-verify"]) assert.equal(source.includes(command), false, `CLI command names belong in the capability surface, not the API barrel:${command}`);
  const capabilitiesSource = fs.readFileSync(path.join(cliRoot, "src/product/capabilities.ts"), "utf8");
  for (const command of ["recipe-plan", "recipe-generate", "recipe-verify"]) assert.equal(capabilitiesSource.includes(`"${command}"`), true, command);
  assert.match(capabilitiesSource, /deployment_recipe:[\s\S]*lifecycle: "candidate"[\s\S]*target: "aws-ecs-fargate-postgres-v1"[\s\S]*effects: "none"/);
});

test("recipe qualification commands remain stable while the capability stays candidate and non-effectful", () => {
  for (const command of ["recipe-qualification-plan", "recipe-qualify", "recipe-qualification-verify"]) assert.equal(source.includes(command), false, `CLI command names belong in the capability surface, not the API barrel:${command}`);
  const capabilitiesSource = fs.readFileSync(path.join(cliRoot, "src/product/capabilities.ts"), "utf8");
  for (const command of ["recipe-qualification-plan", "recipe-qualify", "recipe-qualification-verify"]) assert.equal(capabilitiesSource.includes(`"${command}"`), true, command);
  assert.match(capabilitiesSource, /recipe_qualification:[\s\S]*lifecycle: "candidate"[\s\S]*ontology_id: "domainspec\.recipe-qualification-ontology@1"[\s\S]*effect_ceiling: "no-external-effect"[\s\S]*effects: "none"/);
});

test("the standard typed Operation path has no specialized Auth generator", () => {
  for (const relativePath of [
    "tools/auth-kernel.mjs",
    "templates/auth-kernel/lib.rs.tmpl",
    "test/auth-kernel/auth-kernel.test.mjs",
  ]) {
    assert.equal(fs.existsSync(path.join(cliRoot, relativePath)), false, relativePath);
  }
  assert.equal(JSON.stringify(packageJson.scripts).includes("auth-kernel"), false);
});

test("runtime and platform declarations remain exact and non-authoritative", () => {
  assert.deepEqual(packageJson.engines, { node: "26.8.1", npm: "11.19.0" });
  assert.deepEqual(packageJson.os, ["linux"]);
  assert.deepEqual(packageJson.cpu, ["x64"]);
  assert.match(versionSource, /SUPPORTED_NODE_VERSION = "v26\.8\.1"/);
  assert.match(versionSource, /AUTHORITY_EFFECT = "none"/);
  assert.equal(packageLock.lockfileVersion, 3);
  assert.deepEqual(packageLock.packages[""].engines, packageJson.engines);
  assert.deepEqual(packageLock.packages[""].bin, { "domainspec-v2": "dist/cli/main.js" });
});

test("TypeScript boundary is strict NodeNext and source-only", () => {
  assert.equal(tsconfig.extends, "../../../../toolchains/node-typescript/tsconfig/node.json");
  assert.equal(tsconfig.compilerOptions.rootDir, "src");
  assert.equal(tsconfig.compilerOptions.outDir, "dist");
  assert.deepEqual(tsconfig.include, ["src/**/*.ts"]);
  const localTsc = path.resolve(cliRoot, "node_modules/.bin/tsc");
  const workspaceTsc = path.resolve(cliRoot, "../node_modules/.bin/tsc");
  const tsc = fs.existsSync(localTsc) ? localTsc : workspaceTsc;
  const result = spawnSync(tsc, ["--showConfig", "--project", path.join(cliRoot, "tsconfig.json")], { encoding: "utf8" });
  assert.equal(result.status, 0, result.stderr);
  const effective = JSON.parse(result.stdout);
  assert.equal(effective.compilerOptions.module, "nodenext");
  assert.equal(effective.compilerOptions.moduleResolution, "nodenext");
  assert.equal(effective.compilerOptions.strict, true);
});
