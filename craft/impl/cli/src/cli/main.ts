#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { addOperation, addRule, addThinBackend, type AddOperationInput, type AddRuleInput, type AddThinBackendInput, type ThinBackendKind } from "../authoring/add-operation.js";
import { decodeRuleExpression, decodeTypedRuleContract, type RuleExpression, type TypedParameter } from "../typed-operation/contracts.js";
import { observeTarget, observeTargetReceipt } from "../conformance/observe-target.js";
import { readInstantiationReceipt } from "../conformance/receipt.js";
import { planInstantiation } from "../generation/plan-instantiation.js";
import { publishInstantiation } from "../generation/publish-instantiation.js";
import { materializeCompiledProjectCertificate } from "../compilation/certificate.js";
import { planProjectBuild, publishProjectBuild, verifyProjectBuild } from "../generation/project-build.js";
import { checkLeanMetaTypeFormalization, materializeLeanMetaTypeFormalization } from "../formalization/projection.js";
import { loadCompiledProjectGraph, loadProjectNode, validateProjectRoot } from "../input/project-model.js";
import { normalizeLanguage } from "../meta-types/catalog.js";
import { loadSystemIntegrationSelection } from "../system-integration/compiler.js";
import { runInMemoryProject } from "../runtime/in-memory.js";
import { materializeRuntimeReceipt } from "../runtime/receipt.js";
import { runDurableOperation } from "../runtime/durable.js";
import { PostgresTransactionalOutbox } from "../runtime/postgres-outbox.js";
import { certifyProject, checkCertifiedProject } from "../assurance/certify.js";

export interface CliIo {
  readonly stdout: (value: string) => void;
  readonly stderr: (value: string) => void;
}

class CliUsageError extends Error {
  readonly exitCode = 22;
  readonly code = "MTCLI_USAGE";
  readonly pointer = "/argv";
}

function usage(message: string): never {
  throw new CliUsageError(message);
}

function objectOutput(io: CliIo, value: unknown): void {
  io.stdout(`${JSON.stringify(value, null, 2)}\n`);
}

function exactlyOneRoot(args: readonly string[], command: string): string {
  if (args.length !== 1) usage(`${command} requires exactly one explicit root`);
  const root = args[0];
  if (!root || !path.isAbsolute(root)) usage(`${command} requires an absolute root`);
  return root;
}

function parseCsvSet(value: string | undefined, option: string): readonly string[] {
  if (value === undefined) return Object.freeze([]);
  const entries = value.split(",").map((entry) => entry.trim());
  if (entries.some((entry) => entry.length === 0)) usage(`${option} must be a comma-separated list without empty entries`);
  if (new Set(entries).size !== entries.length) usage(`${option} must not contain duplicate entries`);
  return Object.freeze(entries);
}

function addOperationArgs(args: readonly string[]): AddOperationInput {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot)) usage("add operation requires one absolute source project root");
  const values = new Map<string, string>();
  const allowedOptions = [
    "--feature",
    "--name",
    "--description",
    "--reads",
    "--writes",
    "--effects",
    "--guard",
    "--failure-continuation",
  ];
  for (let index = 1; index < args.length; index += 2) {
    const option = args[index];
    const value = args[index + 1];
    if (!option || !allowedOptions.includes(option) || !value || value.startsWith("--")) {
      usage("add operation received an unsupported or unvalued option");
    }
    if (values.has(option)) usage(`duplicate option:${option}`);
    values.set(option, value);
  }
  for (const required of ["--feature", "--name", "--description", "--guard", "--failure-continuation"]) {
    if (!values.has(required)) usage(`add operation requires ${required}`);
  }
  return Object.freeze({
    sourceRoot,
    featureId: values.get("--feature")!,
    nodeId: values.get("--name")!,
    description: values.get("--description")!,
    reads: parseCsvSet(values.get("--reads"), "--reads"),
    writes: parseCsvSet(values.get("--writes"), "--writes"),
    effects: parseCsvSet(values.get("--effects"), "--effects"),
    guard: values.get("--guard")!,
    failureContinuation: values.get("--failure-continuation")!,
  });
}

function parseJsonOption(value: string, option: string): unknown {
  try {
    return JSON.parse(value);
  } catch {
    usage(`${option} must contain valid JSON`);
  }
}

function addRuleArgs(args: readonly string[]): AddRuleInput {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot)) usage("add rule requires one absolute source project root");
  const values = new Map<string, string>();
  const allowedOptions = ["--feature", "--name", "--description", "--ontology-rule", "--parameters-json", "--expression-json"];
  for (let index = 1; index < args.length; index += 2) {
    const option = args[index];
    const value = args[index + 1];
    if (!option || !allowedOptions.includes(option) || value === undefined || value.startsWith("--")) usage("add rule received an unsupported or unvalued option");
    if (values.has(option)) usage(`duplicate option:${option}`);
    values.set(option, value);
  }
  for (const required of allowedOptions) if (!values.has(required)) usage(`add rule requires ${required}`);
  const candidate = decodeTypedRuleContract({
    schema_version: "domainspec.typed-rule/v1",
    ontology_rule: values.get("--ontology-rule"),
    parameters: parseJsonOption(values.get("--parameters-json")!, "--parameters-json"),
    expression: parseJsonOption(values.get("--expression-json")!, "--expression-json"),
  });
  return Object.freeze({
    sourceRoot,
    featureId: values.get("--feature")!,
    nodeId: values.get("--name")!,
    description: values.get("--description")!,
    ontologyRule: candidate.ontology_rule,
    parameters: candidate.parameters as readonly TypedParameter[],
    expression: decodeRuleExpression(candidate.expression) as RuleExpression,
  });
}

const THIN_COMMANDS: Readonly<Record<string, ThinBackendKind>> = Object.freeze({ query: "Query", calculation: "Calculation", mapping: "Mapping", policy: "Policy" });

function addThinBackendArgs(kind: ThinBackendKind, args: readonly string[]): AddThinBackendInput {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot)) usage(`add ${kind.toLowerCase()} requires one absolute source project root`);
  const values = new Map<string, string>();
  const allowed = ["--feature", "--name", "--description", "--contract-json"];
  for (let index = 1; index < args.length; index += 2) {
    const option = args[index]; const value = args[index + 1];
    if (!option || !allowed.includes(option) || value === undefined || value.startsWith("--")) usage(`add ${kind.toLowerCase()} received an unsupported or unvalued option`);
    if (values.has(option)) usage(`duplicate option:${option}`);
    values.set(option, value);
  }
  for (const option of allowed) if (!values.has(option)) usage(`add ${kind.toLowerCase()} requires ${option}`);
  return Object.freeze({ sourceRoot, featureId: values.get("--feature")!, nodeId: values.get("--name")!, description: values.get("--description")!, kind, typedContract: parseJsonOption(values.get("--contract-json")!, "--contract-json") });
}

interface InstantiateArgs {
  readonly sourceRoot: string;
  readonly node: string;
  readonly language: "typescript" | "python" | "rust";
  readonly targetRoot: string;
  readonly integrationProfile: string | null;
  readonly integrationBindingSet: string | null;
}

function instantiateArgs(args: readonly string[]): InstantiateArgs {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot)) usage("instantiate requires one absolute source project root");
  const values = new Map<string, string>();
  const allowedOptions = ["--node", "--language", "--target-root", "--integration-profile", "--integration-binding-set"];
  for (let index = 1; index < args.length; index += 2) {
    const option = args[index];
    const value = args[index + 1];
    if (!option || !allowedOptions.includes(option) || !value || value.startsWith("--")) usage("instantiate requires valued --node, --language, --target-root, and optional system-integration profile options");
    if (values.has(option)) usage(`duplicate option:${option}`);
    values.set(option, value);
  }
  for (const required of ["--node", "--language", "--target-root"]) if (!values.has(required)) usage("instantiate requires --node, --language, and --target-root");
  const integrationProfile = values.get("--integration-profile") ?? null;
  const integrationBindingSet = values.get("--integration-binding-set") ?? null;
  if ((integrationProfile === null) !== (integrationBindingSet === null)) usage("--integration-profile and --integration-binding-set must be supplied together");
  if (values.size !== (integrationProfile === null ? 3 : 5)) usage("instantiate received an unsupported option set");
  const targetRoot = values.get("--target-root")!;
  if (!path.isAbsolute(targetRoot)) usage("--target-root must be absolute");
  return Object.freeze({
    sourceRoot,
    node: values.get("--node")!,
    language: normalizeLanguage(values.get("--language")),
    targetRoot,
    integrationProfile,
    integrationBindingSet,
  });
}

function formalizeArgs(args: readonly string[], command: "formalize" | "formalize-check"): { readonly sourceRoot: string; readonly targetPath: string } {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot) || args.length !== 3 || args[1] !== "--target" || !path.isAbsolute(args[2] ?? "")) {
    usage(`${command} requires one absolute source project root and --target <absolute-file>`);
  }
  return Object.freeze({ sourceRoot, targetPath: args[2]! });
}

function compileArgs(args: readonly string[]): { readonly sourceRoot: string; readonly targetPath: string } {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot) || args.length !== 3 || args[1] !== "--target" || !path.isAbsolute(args[2] ?? "")) usage("compile requires one absolute source project root and --target <absolute-file>");
  return Object.freeze({ sourceRoot, targetPath: args[2]! });
}

function certifyArgs(args: readonly string[], command: "certify" | "certify-check"): { readonly sourceRoot: string; readonly targetDirectory: string } {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot) || args.length !== 3 || args[1] !== "--target" || !path.isAbsolute(args[2] ?? "")) usage(`${command} requires one absolute source project root and --target <absolute-directory>`);
  return Object.freeze({ sourceRoot, targetDirectory: args[2]! });
}

function projectBuildArgs(args: readonly string[], command: "build" | "verify"): { readonly sourceRoot: string; readonly language: "typescript" | "python" | "rust"; readonly targetRoot: string } {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot)) usage(`${command} requires one absolute source project root`);
  const values = new Map<string, string>();
  for (let index = 1; index < args.length; index += 2) {
    const option = args[index]; const value = args[index + 1];
    if (!option || !["--language", "--target-root"].includes(option) || !value || value.startsWith("--")) usage(`${command} requires valued --language and --target-root`);
    if (values.has(option)) usage(`duplicate option:${option}`);
    values.set(option, value);
  }
  if (values.size !== 2 || !values.has("--language") || !values.has("--target-root")) usage(`${command} requires --language and --target-root`);
  const targetRoot = values.get("--target-root")!;
  if (!path.isAbsolute(targetRoot)) usage("--target-root must be absolute");
  return Object.freeze({ sourceRoot, language: normalizeLanguage(values.get("--language")), targetRoot });
}

function runArgs(args: readonly string[]): { readonly sourceRoot: string; readonly requestPath: string; readonly receiptPath: string; readonly provider: string | null } {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot)) usage("run requires one absolute source project root");
  const values = new Map<string, string>();
  for (let index = 1; index < args.length; index += 2) {
    const option = args[index]; const value = args[index + 1];
    if (!option || !["--request", "--receipt", "--provider"].includes(option) || !value || (option !== "--provider" && !path.isAbsolute(value))) usage("run requires absolute --request and --receipt files and an optional provider");
    if (values.has(option)) usage(`duplicate option:${option}`);
    values.set(option, value);
  }
  if (!values.has("--request") || !values.has("--receipt") || values.size > 3) usage("run requires absolute --request and --receipt files");
  return Object.freeze({ sourceRoot, requestPath: values.get("--request")!, receiptPath: values.get("--receipt")!, provider: values.get("--provider") ?? null });
}

function postgresProvider(): PostgresTransactionalOutbox {
  const required = ["PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "PGPASSWORD"] as const;
  for (const key of required) if (!process.env[key]) usage(`postgres provider requires ${key}`);
  return new PostgresTransactionalOutbox({ host: process.env.PGHOST!, port: Number(process.env.PGPORT), database: process.env.PGDATABASE!, user: process.env.PGUSER!, password: process.env.PGPASSWORD! });
}

function isInstantiationTarget(root: string): boolean {
  return fs.existsSync(path.join(root, ".domainspec", "instantiations"));
}

function errorEnvelope(error: unknown): Record<string, unknown> {
  const candidate = error as Partial<Error> & { code?: unknown; pointer?: unknown };
  return {
    result: "fail",
    code: typeof candidate.code === "string" ? candidate.code : "MTCLI_UNEXPECTED",
    pointer: typeof candidate.pointer === "string" ? candidate.pointer : "$",
    message: error instanceof Error ? error.message : "unexpected failure",
    authority_effect: "none",
  };
}

export function runCli(argv: readonly string[], io: CliIo = {
  stdout: (value) => process.stdout.write(value),
  stderr: (value) => process.stderr.write(value),
}): number {
  try {
    const [command, ...args] = argv;
    if (command === "add") {
      const kind = args[0];
      if (kind !== "operation" && kind !== "rule" && !THIN_COMMANDS[kind ?? ""]) usage("add requires a supported meta-type: operation, query, calculation, rule, policy, or mapping");
      const result = kind === "operation" ? addOperation(addOperationArgs(args.slice(1))) : kind === "rule" ? addRule(addRuleArgs(args.slice(1))) : addThinBackend(addThinBackendArgs(THIN_COMMANDS[kind!]!, args.slice(1)));
      objectOutput(io, {
        schema_version: `domainspec.add-${kind}-command-result/v1`,
        result: "pass",
        source_root: result.source_root,
        selector: result.selector,
        node_path: result.node_path,
        source_manifest_sha256: result.source_manifest.manifest_sha256,
        source_count: result.source_manifest.source_count,
        authority_effect: result.authority_effect,
      });
      return 0;
    }
    if (command === "instantiate") {
      const parsed = instantiateArgs(args);
      const node = loadProjectNode(parsed.sourceRoot, parsed.node);
      const systemIntegration = parsed.integrationProfile === null || parsed.integrationBindingSet === null
        ? null
        : loadSystemIntegrationSelection(node.project_root, parsed.integrationBindingSet, parsed.integrationProfile, `${node.feature_id}:${node.node_id}`, parsed.language);
      const plan = planInstantiation(node, parsed.language, systemIntegration);
      const publication = publishInstantiation(plan, parsed.targetRoot);
      const observation = observeTarget(publication.target_root);
      objectOutput(io, {
        schema_version: "domainspec.instantiate-command-result/v1",
        result: "pass",
        target_root: publication.target_root,
        receipt_path: publication.receipt_path,
        plan_sha256: plan.plan_sha256,
        receipt_sha256: publication.receipt.receipt_sha256,
        system_integration_binding_digest: plan.system_integration?.manifest.binding_digest ?? null,
        observation,
        authority_effect: "none",
      });
      return 0;
    }
    if (command === "compile") {
      const parsed = compileArgs(args);
      const certificate = materializeCompiledProjectCertificate(parsed.sourceRoot, parsed.targetPath);
      objectOutput(io, { schema_version: "domainspec.compile-command-result/v1", result: "pass", target_path: parsed.targetPath, certificate, authority_effect: "none" });
      return 0;
    }
    if (command === "certify") {
      const parsed = certifyArgs(args, command);
      const certificate = certifyProject(parsed.sourceRoot, parsed.targetDirectory);
      objectOutput(io, {
        schema_version: "domainspec.certify-command-result/v1-candidate",
        result: "pass",
        target_directory: parsed.targetDirectory,
        certificate,
        authority_effect: "none",
      });
      return 0;
    }
    if (command === "certify-check") {
      const parsed = certifyArgs(args, command);
      const result = checkCertifiedProject(parsed.sourceRoot, parsed.targetDirectory);
      objectOutput(io, result);
      return result.current ? 0 : 1;
    }
    if (command === "build") {
      const parsed = projectBuildArgs(args, "build");
      const publication = publishProjectBuild(planProjectBuild(parsed.sourceRoot, parsed.language), parsed.targetRoot);
      objectOutput(io, { schema_version: "domainspec.build-command-result/v1", result: "pass", ...publication, authority_effect: "none" });
      return 0;
    }
    if (command === "verify") {
      const parsed = projectBuildArgs(args, "verify");
      const verification = verifyProjectBuild(parsed.sourceRoot, parsed.language, parsed.targetRoot);
      objectOutput(io, verification);
      return verification.result === "pass" ? 0 : 1;
    }
    if (command === "run") {
      const parsed = runArgs(args);
      let request: unknown;
      try { request = JSON.parse(fs.readFileSync(parsed.requestPath, "utf8")); } catch { usage("--request must identify readable JSON"); }
      const schemaVersion = (request as { schema_version?: unknown })?.schema_version;
      const receipt = schemaVersion === "domainspec.durable-operation-invocation/v1"
        ? materializeRuntimeReceipt(runDurableOperation(parsed.sourceRoot, request, parsed.provider === "postgres-transactional-outbox-v1" ? postgresProvider() : usage("durable run requires --provider postgres-transactional-outbox-v1")), parsed.receiptPath)
        : materializeRuntimeReceipt(parsed.provider === null || parsed.provider === "in-memory-v1" ? runInMemoryProject(parsed.sourceRoot, request) : usage("in-memory run received an unsupported provider"), parsed.receiptPath);
      objectOutput(io, { schema_version: "domainspec.run-command-result/v1", result: "pass", receipt_path: parsed.receiptPath, receipt, authority_effect: "none" });
      return 0;
    }
    if (command === "formalize" || command === "formalize-check") {
      const parsed = formalizeArgs(args, command);
      const projectGraph = loadCompiledProjectGraph(parsed.sourceRoot);
      const sourceManifest = projectGraph.source_manifest;
      if (command === "formalize") {
        const result = materializeLeanMetaTypeFormalization(projectGraph, parsed.targetPath);
        objectOutput(io, {
          schema_version: "domainspec.meta-type-formalization-command-result/v1-candidate",
          result: "pass",
          source_manifest_sha256: sourceManifest.manifest_sha256,
          ...result,
          authority_effect: "none",
        });
        return 0;
      }
      const result = checkLeanMetaTypeFormalization(projectGraph, parsed.targetPath);
      objectOutput(io, {
        schema_version: "domainspec.meta-type-formalization-command-result/v1-candidate",
        result: result.current ? "pass" : "fail",
        source_manifest_sha256: sourceManifest.manifest_sha256,
        ...result,
        authority_effect: "none",
      });
      return result.current ? 0 : 1;
    }
    if (command === "lint") {
      const root = exactlyOneRoot(args, "lint");
      if (isInstantiationTarget(root)) {
        const observation = observeTargetReceipt(root);
        objectOutput(io, observation);
        return observation.result === "pass" ? 0 : 1;
      }
      objectOutput(io, {
        schema_version: "domainspec.source-project-lint/v1",
        result: "pass",
        source_manifest: validateProjectRoot(root),
        authority_effect: "none",
      });
      return 0;
    }
    if (command === "receipt") {
      const root = exactlyOneRoot(args, "receipt");
      if (isInstantiationTarget(root)) {
        const observation = observeTargetReceipt(root);
        if (observation.result === "fail") {
          objectOutput(io, { observation });
          return 1;
        }
        objectOutput(io, { receipt: readInstantiationReceipt(root), observation });
      } else {
        objectOutput(io, validateProjectRoot(root));
      }
      return 0;
    }
    usage("expected command: add, instantiate, compile, build, verify, run, formalize, formalize-check, certify, certify-check, lint, or receipt");
  } catch (error) {
    objectOutput({ ...io, stdout: io.stderr }, errorEnvelope(error));
    const candidate = error as { exitCode?: unknown };
    return typeof candidate.exitCode === "number" ? candidate.exitCode : 1;
  }
}

if (process.argv[1] && fs.realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exitCode = runCli(process.argv.slice(2));
}
