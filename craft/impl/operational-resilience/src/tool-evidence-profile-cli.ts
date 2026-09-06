import { lstatSync, readFileSync } from "node:fs";

import { validateToolEvidenceProfile } from "./validate-tool-evidence-profile.js";

const USAGE = "usage: tool-evidence-profile-cli validate <descriptor.json> --inventory <family-inventory.json> --attribute-policy <policy.json> --referents <referents.json> --at <RFC3339-Z>";
const REQUIRED_FLAGS = Object.freeze([
  "--inventory",
  "--attribute-policy",
  "--referents",
  "--at",
] as const);

type RequiredFlag = (typeof REQUIRED_FLAGS)[number];

function fail(message: string): never {
  throw new Error(message);
}

function parseArguments(argv: readonly string[]): Readonly<{
  descriptor: string;
  inventory: string;
  policy: string;
  referents: string;
  evaluatedAt: string;
}> {
  if (argv[0] !== "validate" || typeof argv[1] !== "string" || argv[1].length === 0) {
    fail(`CLI_USAGE_INVALID: ${USAGE}`);
  }
  const values = new Map<RequiredFlag, string>();
  let cursor = 2;
  while (cursor < argv.length) {
    const flag = argv[cursor] as RequiredFlag | undefined;
    const value = argv[cursor + 1];
    if (!flag || !(REQUIRED_FLAGS as readonly string[]).includes(flag) || typeof value !== "string" || value.length === 0 || value.startsWith("--")) {
      fail(`CLI_ARGUMENT_UNSUPPORTED: unsupported or incomplete argument at position ${cursor}: ${argv[cursor] ?? "<missing>"}`);
    }
    if (values.has(flag)) fail(`CLI_ARGUMENT_DUPLICATE: duplicate argument: ${flag}`);
    values.set(flag, value);
    cursor += 2;
  }
  for (const flag of REQUIRED_FLAGS) {
    if (!values.has(flag)) fail(`CLI_ARGUMENT_MISSING: missing required argument: ${flag}`);
  }
  return {
    descriptor: argv[1],
    inventory: values.get("--inventory")!,
    policy: values.get("--attribute-policy")!,
    referents: values.get("--referents")!,
    evaluatedAt: values.get("--at")!,
  };
}

function readExactRegularFile(path: string, label: string): Uint8Array {
  if (/^[a-z][a-z0-9+.-]*:\/\//iu.test(path)) {
    fail(`CLI_LOCAL_FILE_REQUIRED: ${label} must be one caller-supplied local file path`);
  }
  let status;
  try {
    status = lstatSync(path);
  } catch {
    fail(`CLI_FILE_UNREADABLE: ${label} cannot be read: ${path}`);
  }
  if (status.isSymbolicLink() || !status.isFile()) {
    fail(`CLI_REGULAR_FILE_REQUIRED: ${label} must be a regular non-symlink file: ${path}`);
  }
  return readFileSync(path);
}

export function runToolEvidenceProfileCli(argv: readonly string[]): number {
  try {
    const args = parseArguments(argv);
    const result = validateToolEvidenceProfile({
      descriptor: readExactRegularFile(args.descriptor, "descriptor"),
      family_inventory: readExactRegularFile(args.inventory, "family inventory"),
      attribute_policy: readExactRegularFile(args.policy, "attribute policy"),
      referent_inventory: readExactRegularFile(args.referents, "referent inventory"),
      evaluated_at: args.evaluatedAt,
    });
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
    return result.verdict === "pass" ? 0 : 1;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(`${message}\n`);
    return 2;
  }
}

if (process.argv[1]?.endsWith("tool-evidence-profile-cli.ts") || process.argv[1]?.endsWith("tool-evidence-profile-cli.js")) {
  process.exitCode = runToolEvidenceProfileCli(process.argv.slice(2));
}
