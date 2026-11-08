import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const exampleRoot = path.dirname(fileURLToPath(import.meta.url));
const packageRoot = path.resolve(exampleRoot, "../..");
const cli = path.join(packageRoot, "dist/cli/main.js");

function usage(message) {
  if (message) process.stderr.write(`${message}\n\n`);
  process.stderr.write("Usage: node test-typescript.mjs --output <new-directory>\n");
  process.stderr.write("Builds, verifies, natively compiles, and exercises the signed TypeScript loopback.\n");
  process.exit(message ? 2 : 0);
}

function executable(name) {
  const candidate = (process.env.PATH ?? "")
    .split(path.delimiter)
    .map(directory => path.resolve(directory, name))
    .find(file => {
      try {
        fs.accessSync(file, fs.constants.X_OK);
        return fs.statSync(file).isFile();
      } catch {
        return false;
      }
    });
  if (!candidate) throw new Error(`${name} executable was not found on PATH`);
  return candidate;
}

function runCli(name, args, observations) {
  const result = spawnSync(process.execPath, [cli, ...args], {
    cwd: packageRoot,
    encoding: "utf8",
    maxBuffer: 32 * 1024 * 1024,
  });
  if (result.status !== 0) {
    const detail = (result.stderr || result.stdout || result.error?.message || `exit ${result.status}`).trim();
    throw new Error(`${name} failed: ${detail}`);
  }
  let value;
  try {
    value = JSON.parse(result.stdout);
  } catch {
    throw new Error(`${name} did not emit one JSON result`);
  }
  fs.writeFileSync(path.join(observations, `${name}.json`), `${JSON.stringify(value, null, 2)}\n`, { flag: "wx", mode: 0o600 });
  return value;
}

const args = process.argv.slice(2);
if (args.length === 1 && (args[0] === "--help" || args[0] === "-h")) usage();
if (args.length !== 2 || args[0] !== "--output" || args[1].startsWith("-")) usage("--output must name one new directory");
if (!fs.existsSync(cli)) throw new Error(`compiled CLI not found at ${cli}; run npm run build first`);

const outputRoot = path.resolve(args[1]);
const outputParent = path.dirname(outputRoot);
if (!fs.existsSync(outputParent) || !fs.statSync(outputParent).isDirectory()) throw new Error(`output parent does not exist: ${outputParent}`);
if (fs.existsSync(outputRoot)) throw new Error(`output directory already exists: ${outputRoot}`);
fs.mkdirSync(outputRoot, { mode: 0o700 });

const observations = path.join(outputRoot, "observations");
const target = path.join(outputRoot, "application");
fs.mkdirSync(observations, { mode: 0o700 });

const source = path.join(exampleRoot, "source");
const compilationSelection = path.join(exampleRoot, "selections/typescript.json");
const integrationSource = path.join(exampleRoot, "integrations/application.json");
const providerSelection = path.join(exampleRoot, "providers/typescript.json");
const common = [
  source,
  "--language", "typescript",
  "--target-root", target,
  "--compilation-selection", compilationSelection,
  "--integration-source", integrationSource,
  "--provider-selection", providerSelection,
];

const build = runCli("build", ["build", ...common], observations);
const verifyBefore = runCli("verify-before", ["verify", ...common], observations);
const runtimeReceipt = path.join(observations, "runtime-evidence.json");
const runtime = runCli("verify-runtime", [
  "verify-runtime",
  ...common,
  "--temporary-parent", outputRoot,
  "--receipt", runtimeReceipt,
  "--node-executable", process.execPath,
  "--npm-executable", executable("npm"),
], observations);
const verifyAfter = runCli("verify-after", ["verify", ...common], observations);
const evidence = JSON.parse(fs.readFileSync(runtimeReceipt, "utf8"));

const passed =
  build.result === "pass" &&
  verifyBefore.result === "pass" &&
  runtime.result === "pass" &&
  verifyAfter.result === "pass" &&
  evidence.native_compilation?.result === "pass" &&
  evidence.listener_startup?.boundary === "loopback-only" &&
  evidence.signed_webhook_behavior?.invalid_signature_status === 401 &&
  evidence.signed_webhook_behavior?.valid_signature_status === 202 &&
  evidence.signed_webhook_behavior?.handler_invocations === 1 &&
  evidence.target_mutated === false &&
  evidence.temporary_resources_removed === true;
if (!passed) throw new Error("smoke evidence did not satisfy the exact TypeScript loopback contract");

const summary = {
  schema_version: "domainspec.reconciled-commerce-typescript-smoke/v1-candidate",
  result: "pass",
  generated_application: target,
  observations,
  runtime_evidence: runtimeReceipt,
  native_compilation: "pass",
  signed_loopback: {
    invalid_signature_status: 401,
    valid_signature_status: 202,
    handler_invocations: 1,
  },
  provider_dependencies: evidence.provider_dependencies,
  production_runtime_guarantees_observed: false,
  authority_effect: "none",
};
fs.writeFileSync(path.join(outputRoot, "smoke-summary.json"), `${JSON.stringify(summary, null, 2)}\n`, { flag: "wx", mode: 0o600 });
process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`);
