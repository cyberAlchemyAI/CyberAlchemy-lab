#!/usr/bin/env node
import {createHash} from "node:crypto";
import {spawnSync} from "node:child_process";
import {readFileSync} from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";

const implementation = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repo = path.resolve(implementation, "../../../../../..");
const runner = path.join(implementation, "scripts/run-toolchain.mjs");
const testFile = path.join(implementation, "test/toolchain-runner.test.ts");
const imageManifest = JSON.parse(readFileSync(path.join(repo, "craft/toolchains/node-typescript/toolchain.json"), "utf8"));
const rustLock = JSON.parse(readFileSync(path.join(repo, "tools/toolchain/lock.json"), "utf8"));
const repositoryLauncher = path.join(repo, "tools/toolchain/run");
const sha256 = (file) => createHash("sha256").update(readFileSync(file)).digest("hex");

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {encoding: "utf8", maxBuffer: 32 * 1024 * 1024, ...options});
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`${command} ${args.join(" ")} failed (${result.status})\n${result.stdout}\n${result.stderr}`);
  return result.stdout;
}

const sysroot = run(repositoryLauncher, ["rustc", "--print", "sysroot"]).trim();
const hostEnv = {...process.env, ALCHLANG_CARGO: path.join(sysroot, "bin/cargo"), ALCHLANG_RUSTC: path.join(sysroot, "bin/rustc")};
const focusedArgs = [runner, "tsx", "--test", testFile];
const hostIdentities = JSON.parse(run(process.execPath, [runner, "--identity-all"], {cwd: implementation, env: hostEnv}));
const hostTap = run(process.execPath, focusedArgs, {cwd: implementation, env: hostEnv});

const image = imageManifest.container_image;
const imageId = run("docker", ["image", "inspect", image, "--format", "{{.Id}}"]).trim();
const uid = typeof process.getuid === "function" ? String(process.getuid()) : "1000";
const gid = typeof process.getgid === "function" ? String(process.getgid()) : "1000";
const containerRoot = "/workspace";
const containerImplementation = `${containerRoot}/language/capabilities/alchlang/plans/general-compiler-v1/implementation`;
const baseDockerArgs = ["run", "--rm", "--pull", "never", "--network", "none", "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--user", `${uid}:${gid}`, "--tmpfs", "/tmp:rw,nosuid,nodev,size=256m", "--mount", `type=bind,src=${repo},dst=${containerRoot},readonly`, "--mount", `type=bind,src=${sysroot},dst=/opt/rust,readonly`, "--workdir", containerImplementation, "--env", "HOME=/tmp", "--env", "ALCHLANG_CARGO=/opt/rust/bin/cargo", "--env", "ALCHLANG_RUSTC=/opt/rust/bin/rustc", image];
const containerRunner = `${containerImplementation}/scripts/run-toolchain.mjs`;
const containerTest = `${containerImplementation}/test/toolchain-runner.test.ts`;
const containerIdentities = JSON.parse(run("docker", [...baseDockerArgs, "node", containerRunner, "--identity-all"]));
const containerTap = run("docker", [...baseDockerArgs, "node", containerRunner, "tsx", "--test", containerTest]);

function portableIdentities(identities, root, rustScope) {
  return identities.map((identity) => identity.family === "node" ? {
    tool: identity.tool,
    family: identity.family,
    source: identity.source,
    executable_relative: path.relative(root, identity.executable),
    real_executable_relative: path.relative(root, identity.real_executable),
    lock_package: identity.lock_package,
    package_name: identity.package_name,
    package_version: identity.package_version,
  } : {
    tool: identity.tool,
    family: identity.family,
    source: identity.source,
    executable_scope: rustScope,
    expected_version: identity.expected_version,
    observed_version: identity.observed_version,
  });
}

function testCount(tap) {
  const match = tap.match(/(?:^|\n)[ℹ#]\s*tests\s+(\d+)/u);
  if (!match) throw new Error(`O01_TEST_COUNT_MISSING\n${tap}`);
  return Number(match[1]);
}
const hostTests = testCount(hostTap), containerTests = testCount(containerTap);
if (hostTests !== 5 || containerTests !== 5) throw new Error(`O01_TEST_COUNT:${hostTests}:${containerTests}`);
for (const identities of [hostIdentities, containerIdentities]) {
  if (identities[0].source !== "package-lock" || identities[1].source !== "package-lock") throw new Error("O01_NODE_IDENTITY");
  if (identities[2].observed_version !== rustLock.rust || identities[3].observed_version !== rustLock.rust) throw new Error("O01_RUST_IDENTITY");
}

process.stdout.write(`${JSON.stringify({
  schema_version: "alchlang.o01-toolchain-parity/v1-candidate",
  task: "O01",
  result: "pass",
  authority_effect: "none",
  host: {tests: hostTests, passed: hostTests, failed: 0, skipped: 0, identities: portableIdentities(hostIdentities, implementation, "repository-selected-sysroot")},
  container: {tests: containerTests, passed: containerTests, failed: 0, skipped: 0, image, image_id: imageId, network: "none", root_filesystem: "read-only", source_mount: "read-only", rust_mount: "read-only", identities: portableIdentities(containerIdentities, containerImplementation, "read-only-sysroot-mount")},
  bindings: {
    runner: {path: path.relative(repo, runner), sha256: sha256(runner)},
    focused_test: {path: path.relative(repo, testFile), sha256: sha256(testFile)},
    contract: {path: path.relative(repo, path.join(implementation, "TOOLCHAIN-HARNESS.md")), sha256: sha256(path.join(implementation, "TOOLCHAIN-HARNESS.md"))},
    package_manifest: {path: path.relative(repo, path.join(implementation, "package.json")), sha256: sha256(path.join(implementation, "package.json"))},
    qualifier: {path: path.relative(repo, path.join(implementation, "scripts/qualify-o01-toolchain.mjs")), sha256: sha256(path.join(implementation, "scripts/qualify-o01-toolchain.mjs"))},
    package_lock: {path: path.relative(repo, path.join(implementation, "package-lock.json")), sha256: sha256(path.join(implementation, "package-lock.json"))},
    rust_lock: {path: "tools/toolchain/lock.json", sha256: sha256(path.join(repo, "tools/toolchain/lock.json"))},
    node_toolchain: {path: "craft/toolchains/node-typescript/toolchain.json", sha256: sha256(path.join(repo, "craft/toolchains/node-typescript/toolchain.json"))},
  },
  hard_stops: {tool_download_performed: false, image_pull_or_build_performed: false, ambient_path_fallback_used: false, path_repair_or_symlink_created: false, product_semantics_changed: false, publication_or_deployment_performed: false, product_owner_testing_claimed: false},
  claim_ceiling: "O01 host/container tool-resolution parity only; no installed-consumer, publication, production, or product-approval claim.",
  open_questions: ["P02 owns clean installed-consumer qualification using this toolchain boundary.", "L4X owns deferred product-owner testing."],
}, null, 2)}\n`);
