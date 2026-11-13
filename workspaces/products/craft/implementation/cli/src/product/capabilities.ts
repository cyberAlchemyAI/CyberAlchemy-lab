import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

import {
  CLI_PACKAGE_NAME,
  CLI_VERSION,
  SUPPORTED_ARCH,
  SUPPORTED_NODE_VERSION,
  SUPPORTED_PLATFORM,
} from "../version.js";
import { MAX_JSON_DEPTH, MAX_PROJECT_NODES, MAX_PROJECT_RELATIONSHIPS, MAX_PROJECT_SOURCES, MAX_SOURCE_FILE_BYTES, SUBPROCESS_TIMEOUT_MS } from "../input/limits.js";

export const STABLE_COMMANDS = Object.freeze([
  "add",
  "instantiate",
  "instantiate-project",
  "verify-project",
  "verify-runtime",
  "compile",
  "build",
  "verify",
  "formalize",
  "formalize-check",
  "certify",
  "certify-check",
  "lint",
  "receipt",
  "capabilities",
  "doctor",
  "recipe-plan",
  "recipe-generate",
  "recipe-verify",
  "recipe-qualification-plan",
  "recipe-qualify",
  "recipe-qualification-verify",
] as const);

export const EXPERIMENTAL_COMMANDS = Object.freeze(["run", "derive-tests"] as const);
export const AUTHORING_META_TYPES = Object.freeze(["Operation", "Query", "Calculation", "Rule", "Policy", "Mapping"] as const);
export const COMPILED_META_TYPES = Object.freeze([
  "Entity", "Value Object", "Enum", "Operation", "Query", "Calculation", "Rule",
  "Policy", "Workflow", "Interface", "Event", "Mapping", "State Machine",
] as const);

export const PRODUCT_CAPABILITIES = Object.freeze({
  schema_version: "domainspec.product-capabilities/v1" as const,
  product: Object.freeze({ package: CLI_PACKAGE_NAME, version: CLI_VERSION, lifecycle: "stable" as const }),
  product_spine: "authored-source-to-compiled-graph-to-generated-targets-and-certificates" as const,
  stable_commands: STABLE_COMMANDS,
  experimental_commands: EXPERIMENTAL_COMMANDS,
  authoring: Object.freeze({
    structured_cli_meta_types: AUTHORING_META_TYPES,
    source_json_meta_types: COMPILED_META_TYPES,
  }),
  compiled_meta_types: COMPILED_META_TYPES,
  supported_languages: Object.freeze(["typescript", "python", "rust"] as const),
  limits: Object.freeze({ source_file_bytes: MAX_SOURCE_FILE_BYTES, project_sources: MAX_PROJECT_SOURCES, project_nodes: MAX_PROJECT_NODES, project_relationships: MAX_PROJECT_RELATIONSHIPS, json_depth: MAX_JSON_DEPTH, subprocess_timeout_ms: SUBPROCESS_TIMEOUT_MS }),
  runtime: Object.freeze({ lifecycle: "experimental" as const, package_subpath: "@domainspec-v2/cli/experimental/runtime" as const }),
  deployment_recipe: Object.freeze({ lifecycle: "candidate" as const, target: "aws-ecs-fargate-postgres-v1" as const, messaging: Object.freeze({ lifecycle: "candidate" as const, provider: "aws-sqs" as const, guarantees: Object.freeze(["at-least-once", "provider-acceptance-only"] as const) }), effects: "none" as const }),
  recipe_qualification: Object.freeze({ lifecycle: "candidate" as const, ontology_id: "domainspec.recipe-qualification-ontology@1" as const, qualification_level: "recipe-executable-v1" as const, result_domain: Object.freeze(["pass", "fail", "not_evaluable"] as const), effect_ceiling: "no-external-effect" as const, effects: "none" as const }),
  computation: Object.freeze({lifecycle: "candidate" as const, command: "computation" as const, source_contract: "domainspec.computation-source/v1-candidate" as const, semantics: "ordered-metered-v1-candidate" as const, target: "typescript" as const, pure: true as const, effects: "none" as const}),
  test_derivation: Object.freeze({ lifecycle: "candidate" as const, command: "derive-tests" as const, source: "checked-compiled-project-graph" as const, output: "source-bound-construction-test-plan" as const, definition_byte_join: "pending" as const, executable_tests: false as const, evidence_join: "pending" as const, effects: "none" as const }),
  profile_engine: Object.freeze({lifecycle:'candidate' as const,library:'profileEngine' as const,frontend:'alchlang profile' as const,workflow:Object.freeze(['select','check','plan','generate','view','verify'] as const),target:'node-http' as const,project_versions:Object.freeze(['craft.profile-project/v1','craft.profile-project/v2-candidate'] as const),business_applications:'Mapping-to-Operation; no reads/writes/events' as const,profile_extension:'registered mechanisms through locked metadata/assets' as const,external_effects:'read-only GET functions and zero-effects application invocation' as const,claim_ceiling:'checked generation; formal claims and operational admission unproved' as const,deferred:Object.freeze(['local hosting','TDE','EVF','publication'] as const)}),
  authority_effect: "none" as const,
});

export interface ProductDoctorCheck {
  readonly id: string;
  readonly required: boolean;
  readonly result: "pass" | "fail";
  readonly detail: string;
}

function executable(name: string): string | null {
  const entry = (process.env.PATH ?? "").split(path.delimiter)
    .map((directory) => path.join(directory, name))
    .find((candidate) => fs.existsSync(candidate));
  return entry ? path.resolve(entry) : null;
}

function toolCheck(id: string, executableName: string, args: readonly string[], required: boolean): ProductDoctorCheck {
  const command = executable(executableName);
  if (command === null) return Object.freeze({ id, required, result: "fail", detail: `${executableName} is not on PATH` });
  const result = spawnSync(command, [...args], { encoding: "utf8", timeout: 15_000 });
  const detail = (result.stdout || result.stderr || result.error?.message || `exit ${result.status}`).trim().split("\n")[0]!;
  return Object.freeze({ id, required, result: result.status === 0 ? "pass" : "fail", detail });
}

export function inspectProductEnvironment(): Readonly<{
  schema_version: "domainspec.product-doctor/v1";
  result: "pass" | "fail";
  checks: readonly ProductDoctorCheck[];
  authority_effect: "none";
}> {
  const checks = Object.freeze([
    Object.freeze({ id: "node-version", required: true, result: process.version === SUPPORTED_NODE_VERSION ? "pass" as const : "fail" as const, detail: `${process.version}; expected ${SUPPORTED_NODE_VERSION}` }),
    Object.freeze({ id: "platform", required: true, result: process.platform === SUPPORTED_PLATFORM ? "pass" as const : "fail" as const, detail: `${process.platform}; expected ${SUPPORTED_PLATFORM}` }),
    Object.freeze({ id: "architecture", required: true, result: process.arch === SUPPORTED_ARCH ? "pass" as const : "fail" as const, detail: `${process.arch}; expected ${SUPPORTED_ARCH}` }),
    toolCheck("typescript", "tsc", ["--version"], true),
    toolCheck("python", "python3", ["--version"], true),
    toolCheck("rust", "rustc", ["--version"], true),
    toolCheck("cargo", "cargo", ["--version"], true),
    toolCheck("lean", "lean", ["--version"], true),
    toolCheck("postgres-client", "psql", ["--version"], false),
    toolCheck("docker", "docker", ["--version"], false),
    toolCheck("terraform", "terraform", ["version"], false),
  ]);
  const result = checks.some((check) => check.required && check.result === "fail") ? "fail" : "pass";
  return Object.freeze({ schema_version: "domainspec.product-doctor/v1", result, checks, authority_effect: "none" });
}

export const CLI_HELP = `DomainSpec v2 ${CLI_VERSION}

Pure computation candidate:
  computation check|build|verify|run <absolute-contract.json> [--out <absolute-directory>] [--input <absolute-json>]
  Explicit domainspec.iteration-expression/v1-candidate contract; native output is standalone TypeScript.

Usage: domainspec-v2 <command> [arguments]

Stable commands:
  add <operation|query|calculation|rule|policy|mapping> ...
  lint <absolute-root>
  compile <absolute-source-root> --target <absolute-file>
  instantiate <absolute-source-root> --node <selector> --language <language> --target-root <absolute-directory>
  instantiate-project <absolute-source-root> --languages <csv> --target-root <absolute-directory>
  build <absolute-source-root> --language <language> --target-root <absolute-directory>
  verify <absolute-source-root> --language <language> --target-root <absolute-directory>
  verify-project <absolute-source-root> --target-root <absolute-directory>
  verify-runtime <absolute-source-root> --language <language> --target-root <absolute-directory> --temporary-parent <absolute-directory> --receipt <absolute-new-file> <language tools>
  formalize|formalize-check <absolute-source-root> --target <absolute-file>
  certify|certify-check <absolute-source-root> --target <absolute-directory>
  receipt <absolute-root>
  capabilities
  doctor
  recipe-plan <absolute-source-root> --request <absolute-file> --consumer-root <absolute-directory>
  recipe-generate <absolute-source-root> --request <absolute-file> --consumer-root <absolute-directory> --target-root <absolute-new-directory>
  recipe-verify <absolute-source-root> --request <absolute-file> --consumer-root <absolute-directory> --target-root <absolute-directory>
  recipe-qualification-plan <absolute-source-root> --request <absolute-file> --consumer-root <absolute-directory> --target-root <absolute-directory> --profile <absolute-file>
  recipe-qualify <absolute-source-root> --request <absolute-file> --consumer-root <absolute-directory> --target-root <absolute-directory> --profile <absolute-file> --qualification-root <absolute-new-directory>
  recipe-qualification-verify <absolute-source-root> --request <absolute-file> --consumer-root <absolute-directory> --target-root <absolute-directory> --profile <absolute-file> --qualification-root <absolute-directory>

Reconciled compilation selection (TypeScript, Python, or Rust; existing defaults unchanged):
  instantiate|instantiate-project|build|verify ... --compilation-selection <absolute-json-file>
  The command language must match the selection; instantiate-project accepts exactly one selected language.
  Selected verify accepts optional --node <selector> and checks artifact currentness only.
  Whole-project build|verify|verify-project accept --output-layout domainspec.application-layout/v1 or domainspec.project-layout/v1.
  Selected verify-project performs native verification with explicit language-specific absolute tool paths.
  Reconciled node instantiation does not accept a system-integration overlay.
  Whole-project instantiate-project|build|verify|verify-runtime accept --integration-source <absolute-json-file>.
  Add --provider-selection <absolute-json-file> with --integration-source to generate an explicit concrete provider pack.
  Provider selection never occurs implicitly and provider compilation does not establish runtime behavior.
  Provider verify-runtime requires both selections and writes bounded native compile plus loopback HTTP evidence outside the generated target.
  TypeScript tools: --node-executable <absolute-file> --npm-executable <absolute-file>.
  Python tool: --python-executable <absolute-file>, or --docker-executable <absolute-file> --python-image <image-reference>.
  Rust tool: --cargo-executable <absolute-file>.
  The runtime evidence does not observe live PostgreSQL, NATS, outbound HTTP, delivery, consumer completion, or production guarantees.

Experimental commands:
  run <absolute-source-root> --request <absolute-file> --receipt <absolute-file> [--provider <id>]
  derive-tests <absolute-source-root>

Global options:
  -h, --help     Show this help
  -v, --version  Show the package version
`;
