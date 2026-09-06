#!/usr/bin/env node

import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { validateFoundationContract } from "./impl/cli/tools/validate-foundation-contract.mjs";

const projectRoot = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(projectRoot, "../..");
const readJson = (path) => JSON.parse(readFileSync(resolve(repoRoot, path), "utf8"));
const readText = (path) => readFileSync(resolve(repoRoot, path), "utf8");
const sha256 = (path) => createHash("sha256").update(readFileSync(resolve(repoRoot, path))).digest("hex");
const runtime = readJson("projects/domainspec-v2/RUNTIME.json");
let checks = 0;

function assert(condition, message) {
  checks += 1;
  if (!condition) throw new Error(message);
}

assert(runtime.schema_version === "domainspec.project-runtime/v2", "runtime schema drift");
assert(runtime.runtime_id === "domainspec-v2-node@26.8.1", "runtime identity drift");
assert(runtime.authority_effect === "project-local-runtime-selection", "runtime authority drift");
assert(process.versions.node === runtime.node.version, `Node runtime drift: expected ${runtime.node.version}, got ${process.versions.node}`);
assert(process.platform === runtime.node.platform && process.arch === runtime.node.arch, "runtime platform drift");
assert(readText("projects/domainspec-v2/.node-version").trim() === runtime.node.version, ".node-version drift");
assert(sha256(runtime.owner_decision.path) === runtime.owner_decision.sha256, "runtime owner decision digest drift");
assert(sha256(runtime.node.toolchain_manifest) === runtime.node.toolchain_manifest_sha256, "toolchain manifest digest drift");

const toolchain = readJson(runtime.node.toolchain_manifest);
assert(toolchain.node.version === runtime.node.version, "toolchain Node version drift");
assert(toolchain.container_image === runtime.node.image, "toolchain image identity drift");
assert(toolchain.package_managers.pnpm === runtime.package_managers.development_workspace.version, "pnpm toolchain drift");
assert(toolchain.package_managers.npm === runtime.package_managers.private_cli_build_contract.version, "npm toolchain drift");

const impl = readJson(runtime.package_managers.development_workspace.manifest);
assert(impl.engines?.node === runtime.node.version, "implementation workspace Node engine drift");
assert(impl.packageManager === `pnpm@${runtime.package_managers.development_workspace.version}`, "development packageManager drift");
assert(runtime.package_managers.development_workspace.dependency_authority === "repository-pnpm-workspace", "development dependency authority drift");
assert(runtime.package_managers.development_workspace.resolution_root === ".", "development resolution root drift");
assert(existsSync(resolve(repoRoot, runtime.package_managers.development_workspace.lockfile)), "development lockfile absent");

const testDerivationEngine = readJson(runtime.package_managers.test_derivation_engine.manifest);
assert(testDerivationEngine.engines?.node === runtime.node.version, "test derivation engine Node engine drift");
assert(
  testDerivationEngine.packageManager === `pnpm@${runtime.package_managers.test_derivation_engine.version}`,
  "test derivation engine packageManager drift",
);
assert(runtime.package_managers.test_derivation_engine.dependency_authority === "repository-pnpm-workspace", "test derivation engine dependency authority drift");
assert(runtime.package_managers.test_derivation_engine.resolution_root === ".", "test derivation engine resolution root drift");
assert(existsSync(resolve(repoRoot, runtime.package_managers.test_derivation_engine.lockfile)), "test derivation engine lockfile absent");

const cli = readJson(runtime.package_managers.private_cli_build_contract.manifest);
assert(cli.engines?.node === runtime.node.version, "CLI Node engine drift");
assert(cli.engines?.npm === runtime.package_managers.private_cli_build_contract.version, "CLI npm engine drift");
assert(runtime.package_managers.private_cli_build_contract.dependency_authority === "standalone-npm-clean-package", "CLI dependency authority drift");
assert(runtime.package_managers.private_cli_build_contract.container_execution_lockfile === "pnpm-lock.yaml", "CLI container execution lock drift");
assert(runtime.package_managers.private_cli_build_contract.clean_root_build_proven === true, "CLI clean build proof missing");
assert(existsSync(resolve(repoRoot, runtime.package_managers.private_cli_build_contract.lockfile)), "CLI build lockfile absent");

const workspace = readJson("package.json");
assert(workspace.packageManager === `pnpm@${runtime.package_managers.development_workspace.version}`, "repository workspace packageManager drift");
for (const member of [
  "projects/domainspec-v2/impl",
  "projects/domainspec-v2/impl/cli",
  "projects/domainspec-v2/impl/test-derivation-engine",
]) assert(workspace.workspaces.includes(member), `DomainSpec workspace member missing:${member}`);
const cliLock = readJson(runtime.package_managers.private_cli_build_contract.lockfile);
assert(cliLock.packages?.[""]?.name === cli.name, "CLI lockfile package identity drift");
assert(cliLock.packages?.[""]?.engines?.node === runtime.node.version, "CLI lockfile Node engine drift");

const contract = readJson("projects/domainspec-v2/impl/cli/contracts/foundation-contract.json");
const contractResult = validateFoundationContract(contract);
assert(contractResult.result === "pass" && contract.schema_version.endsWith("/v2"), "foundation contract is not the sealed v2 candidate");
assert(contract.supported_surface.runtime.node === `v${runtime.node.version}`, "foundation runtime drift");
assert(contract.supported_surface.build.package_manager === `npm@${runtime.package_managers.private_cli_build_contract.version}`, "foundation npm drift");
assert(contract.decision_bindings.runtime_decision.sha256 === runtime.owner_decision.sha256, "foundation runtime decision binding drift");

for (const path of [
  "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/examples/enum/composition/cases.json",
  "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/examples/enum/provenance/cases.json",
]) {
  assert(readJson(path).runner_contract.runtime_version === runtime.node.version, `live fixture runtime drift: ${path}`);
}
assert(
  readJson("projects/domainspec-v2/development/implementation-conformance/ontology-experiment/examples/enum/provenance/evaluations.expected.json").runtime === `node-${runtime.node.version}`,
  "live expected-runtime projection drift",
);

const baseline = readJson(runtime.canonical_meta_type_baseline.manifest);
assert(baseline.baseline_id === runtime.canonical_meta_type_baseline.id, "canonical baseline identity drift");
assert(baseline.baseline_digest === runtime.canonical_meta_type_baseline.digest, "canonical baseline digest drift");
assert(sha256(runtime.canonical_meta_type_baseline.manifest) === runtime.canonical_meta_type_baseline.manifest_sha256, "canonical baseline manifest digest drift");
assert(baseline.denominators.frozen_evidence_files === runtime.canonical_meta_type_baseline.frozen_evidence_files, "canonical baseline inventory drift");
const currentState = readJson("projects/domainspec-v2/definitions/meta-types/current-implementation.json");
assert(currentState.baseline.id === runtime.canonical_meta_type_baseline.id, "runtime and current-state baseline identity drift");
assert(currentState.baseline.baseline_digest === runtime.canonical_meta_type_baseline.digest, "runtime and current-state baseline digest drift");

const historicalReceipt = readJson(runtime.historical_runtime_policy.preserved_node_22_receipt);
assert(historicalReceipt.validator?.runtime === "node-v22.13.0", "historical Node 22 receipt was rewritten");
assert(readText(runtime.historical_runtime_policy.preserved_node_24_decision).includes("v24.19.0"), "historical Node 24 decision was rewritten");

const supportingRuntime = spawnSync("python3", ["-c", "from jsonschema import Draft202012Validator; import yaml; print('pass')"], { encoding: "utf8" });
assert(supportingRuntime.status === 0 && supportingRuntime.stdout.trim() === "pass", "container schema helpers unavailable");

process.stdout.write(`${JSON.stringify({
  status: "pass",
  runtime_id: runtime.runtime_id,
  node: process.version,
  platform: `${process.platform}-${process.arch}`,
  checks,
  canonical_meta_type_baseline: runtime.canonical_meta_type_baseline.id,
  canonical_baseline_projection_exact: true,
  authority_effect: "none"
}, null, 2)}\n`);
