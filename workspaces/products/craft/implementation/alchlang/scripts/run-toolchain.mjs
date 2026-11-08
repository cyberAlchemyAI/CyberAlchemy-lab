#!/usr/bin/env node
import {spawnSync} from "node:child_process";
import {existsSync, readFileSync, realpathSync} from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";

export const packageRoot = path.resolve(import.meta.dirname, "..");
export const checkoutRoot = path.resolve(packageRoot, "../../../..", "cyberAlchemy-v2");
const nodeTools = new Set(["tsc", "tsx"]);
const rustTools = new Set(["cargo", "rustc"]);

function readJson(file) {
  return JSON.parse(readFileSync(file, "utf8"));
}

function fail(code, detail = "") {
  throw new Error(`${code}${detail ? `: ${detail}` : ""}`);
}

function binTarget(entry, tool) {
  if (!entry?.bin) return null;
  if (typeof entry.bin === "string") return entry.bin;
  return entry.bin[tool] ?? null;
}

export function resolveNodeTool(tool, root = packageRoot) {
  if (!nodeTools.has(tool)) fail("ALCHLANG_NODE_TOOL_UNSUPPORTED", tool);
  const lockPath = path.join(root, "package-lock.json");
  const executable = path.join(root, "node_modules/.bin", tool);
  if (!existsSync(lockPath)) fail("ALCHLANG_TOOLCHAIN_LOCK_MISSING", lockPath);
  if (!existsSync(executable)) fail("ALCHLANG_PACKAGE_TOOL_MISSING", executable);
  const lock = readJson(lockPath);
  const matches = Object.entries(lock.packages ?? {}).flatMap(([key, entry]) => {
    const relative = binTarget(entry, tool);
    if (!key || !relative) return [];
    const expected = path.join(root, key, relative);
    if (!existsSync(expected) || realpathSync(expected) !== realpathSync(executable)) return [];
    return [{lock_package: key, package_name: entry.name ?? path.basename(key), package_version: entry.version}];
  });
  if (matches.length !== 1) fail("ALCHLANG_PACKAGE_TOOL_LOCK_MISMATCH", `${tool}:${matches.length}`);
  const match = matches[0];
  return {
    tool,
    family: "node",
    source: "package-lock",
    executable,
    real_executable: realpathSync(executable),
    lock_path: lockPath,
    lock_package: match.lock_package,
    package_name: match.package_name,
    package_version: match.package_version,
    command: executable,
    args_prefix: [],
  };
}

function observedRustVersion(command, argsPrefix, tool, env) {
  const result = spawnSync(command, [...argsPrefix, "--version"], {encoding: "utf8", env});
  if (result.error) fail("ALCHLANG_RUST_TOOL_EXECUTION", result.error.message);
  if (result.status !== 0) fail("ALCHLANG_RUST_TOOL_EXECUTION", String(result.stderr || result.stdout).trim());
  const match = String(result.stdout).trim().match(new RegExp(`^${tool} (\\d+\\.\\d+\\.\\d+)(?:\\s|$)`, "u"));
  if (!match) fail("ALCHLANG_RUST_TOOL_VERSION", String(result.stdout).trim());
  return match[1];
}

export function resolveRustTool(tool, env = process.env, root = checkoutRoot) {
  if (!rustTools.has(tool)) fail("ALCHLANG_RUST_TOOL_UNSUPPORTED", tool);
  const lockPath = path.join(root, "tools/toolchain/lock.json");
  const launcher = path.join(root, "tools/toolchain/run");
  if (!existsSync(lockPath) || !existsSync(launcher)) fail("ALCHLANG_RUST_TOOLCHAIN_MISSING", root);
  const expectedVersion = readJson(lockPath).rust;
  const variable = tool === "cargo" ? "ALCHLANG_CARGO" : "ALCHLANG_RUSTC";
  const explicit = env[variable];
  let command;
  let argsPrefix;
  let source;
  if (explicit) {
    command = path.resolve(explicit);
    argsPrefix = [];
    source = "explicit-version-bound";
    if (!existsSync(command)) fail("ALCHLANG_RUST_TOOL_MISSING", command);
  } else {
    command = launcher;
    argsPrefix = [tool];
    source = "repository-lock-launcher";
  }
  const observedVersion = observedRustVersion(command, argsPrefix, tool, env);
  if (observedVersion !== expectedVersion) fail("ALCHLANG_RUST_TOOL_VERSION_MISMATCH", `${observedVersion} != ${expectedVersion}`);
  return {
    tool,
    family: "rust",
    source,
    executable: command,
    real_executable: realpathSync(command),
    lock_path: lockPath,
    expected_version: expectedVersion,
    observed_version: observedVersion,
    command,
    args_prefix: argsPrefix,
  };
}

export function resolveTool(tool, env = process.env) {
  if (nodeTools.has(tool)) return resolveNodeTool(tool);
  if (rustTools.has(tool)) return resolveRustTool(tool, env);
  fail("ALCHLANG_TOOL_UNSUPPORTED", tool ?? "missing");
}

function publicIdentity(identity) {
  const {command: _command, args_prefix: _argsPrefix, ...value} = identity;
  return value;
}

export function main(argv = process.argv.slice(2), env = process.env) {
  if (argv[0] === "--identity") {
    if (!argv[1] || argv.length !== 2) fail("ALCHLANG_TOOL_IDENTITY_USAGE", "--identity tsc|tsx|cargo|rustc");
    process.stdout.write(`${JSON.stringify(publicIdentity(resolveTool(argv[1], env)))}\n`);
    return 0;
  }
  if (argv[0] === "--identity-all") {
    if (argv.length !== 1) fail("ALCHLANG_TOOL_IDENTITY_USAGE", "--identity-all");
    process.stdout.write(`${JSON.stringify(["tsc", "tsx", "cargo", "rustc"].map((tool) => publicIdentity(resolveTool(tool, env))))}\n`);
    return 0;
  }
  const [tool, ...args] = argv;
  const identity = resolveTool(tool, env);
  const result = spawnSync(identity.command, [...identity.args_prefix, ...args], {cwd: process.cwd(), env, stdio: "inherit"});
  if (result.error) throw result.error;
  return result.status ?? 1;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    process.exit(main());
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exit(1);
  }
}
