#!/usr/bin/env node
// Required tools stay explicit; no skipped provider checks or global installation.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

const cli = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const options = {};
for (let i = 2; i < process.argv.length; i += 2) {
  const key = process.argv[i]; const value = process.argv[i + 1];
  assert.ok(["--lean-bin-dir", "--postgres-bin-dir", "--postgres-image", "--report-dir"].includes(key) && value, `unknown or incomplete option:${key}`);
  assert.equal(key in options, false, `duplicate option:${key}`);
  options[key] = value;
}
const reportDirectory = options["--report-dir"];
assert.ok(reportDirectory && path.isAbsolute(reportDirectory), "--report-dir must name a new absolute directory");
assert.equal(fs.existsSync(reportDirectory), false, "refuse to replace a full-suite record");
const extraDirectories = [options["--lean-bin-dir"], options["--postgres-bin-dir"]].filter(Boolean);
for (const directory of extraDirectories) assert.ok(path.isAbsolute(directory) && fs.statSync(directory).isDirectory(), `invalid tool directory:${directory}`);
const env = { ...process.env, PATH: [...extraDirectories, process.env.PATH].join(":"), ELAN_TOOLCHAIN: "leanprover/lean4:v4.33.1" };
if (options["--postgres-image"]) env.DOMAINSPEC_TEST_POSTGRES_IMAGE = options["--postgres-image"];
const tools = {};
for (const [command, arguments_] of [
  ["lean", ["--version"]], ["psql", ["--version"]], ["pg_isready", ["--version"]],
  ["docker", ["version", "--format", "{{.Server.Version}}"]], ["node", ["--version"]], ["rustc", ["--version"]],
]) {
  const result = spawnSync(command, arguments_, { encoding: "utf8", env, timeout: 10_000 });
  assert.equal(result.status, 0, `${command} prerequisite failed: ${result.error?.message ?? result.stderr}`);
  tools[command] = result.stdout.trim();
}
assert.match(tools.lean, /^Lean \(version 4\.33\.1,/);
assert.equal(tools.node, "v26.8.1");
fs.mkdirSync(reportDirectory);
const digest = (file) => createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const sourceFiles = [];
function collect(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) collect(file);
    else if (entry.isFile()) sourceFiles.push(file);
  }
}
for (const directory of ["src", "contracts", "test", "lean"]) collect(path.join(cli, directory));
collect(path.join(cli, "examples/capacity-classification/specs"));
sourceFiles.push(path.join(cli, "examples/capacity-classification/project.json"));
sourceFiles.push(path.join(cli, "package.json"), fileURLToPath(import.meta.url));
const sourceHashes = Object.fromEntries(sourceFiles.map((file) => [path.relative(cli, file), digest(file)]));
const report = {
  schema_version: "craft.full-suite-execution/v1", authority_effect: "none", result: "running",
  started_at: new Date().toISOString(), workspace: cli, tools, tool_directories: extraDirectories,
  postgres_image: env.DOMAINSPEC_TEST_POSTGRES_IMAGE ?? "postgres:16", source_hashes: sourceHashes, commands: [],
};
const reportFile = path.join(reportDirectory, "execution.json");
const save = () => fs.writeFileSync(reportFile, `${JSON.stringify(report, null, 2)}\n`);
save();
for (const [name, arguments_] of [["build", ["run", "build"]], ["tests", ["test"]], ["contract-tests", ["run", "test:contract"]]]) {
  console.log(JSON.stringify({ running: name, log: path.join(reportDirectory, `${name}.log`) }));
  const log = path.join(reportDirectory, `${name}.log`);
  const descriptor = fs.openSync(log, "wx");
  const started = Date.now();
  const command = await new Promise((resolve) => {
    const child = spawn("npm", arguments_, { cwd: cli, env, stdio: ["ignore", descriptor, descriptor] });
    child.on("error", (error) => resolve({ exit_code: null, error: error.message }));
    child.on("close", (code, signal) => resolve({ exit_code: code, signal }));
  });
  fs.closeSync(descriptor);
  const text = fs.readFileSync(log, "utf8");
  const counts = Object.fromEntries(["tests", "pass", "fail", "skipped"].map((key) => {
    const match = new RegExp(`(?:^|\\n)(?:ℹ |# )${key} (\\d+)(?:\\r?\\n|$)`).exec(text);
    return [key, match ? Number(match[1]) : null];
  }));
  const result = { name, command: ["npm", ...arguments_], ...command, elapsed_ms: Date.now() - started, log: path.basename(log), sha256: digest(log), ...(name === "build" ? {} : { counts }) };
  report.commands.push(result);
  const unchanged = sourceFiles.every((file) => digest(file) === sourceHashes[path.relative(cli, file)]);
  report.source_unchanged_during_run = unchanged;
  if (command.exit_code !== 0 || !unchanged || (name !== "build" && (counts.fail !== 0 || counts.skipped !== 0 || counts.pass !== counts.tests || !counts.tests))) {
    report.result = "fail"; report.finished_at = new Date().toISOString(); save();
    console.error(JSON.stringify({ result: "fail", command: name, report: reportFile })); process.exitCode = 1; break;
  }
  save();
}
if (!process.exitCode) {
  report.result = "pass"; report.finished_at = new Date().toISOString(); save();
  console.log(JSON.stringify({ result: "pass", report: reportFile, commands: report.commands.map(({ name, counts }) => ({ name, counts })) }));
}
