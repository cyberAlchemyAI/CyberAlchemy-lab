#!/usr/bin/env node
import {runComputationCommand} from './computation.js';
import {checkApplicationOntology,buildApplicationOntology} from '../application/compiler.js';
import {validateOutputLayout, type OutputLayout} from "../generation/output-layout.js";
import { validateRealizationProfile, type RealizationProfile } from "../generation/exact-uint64.js";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { addCalculation, addMapping, addOperation, addPolicy, addQuery, addRule, addThinBackend, type AddCalculationInput, type AddMappingInput, type AddOperationInput, type AddPolicyInput, type AddQueryInput, type AddRuleInput, type AddThinBackendInput, type ThinBackendKind } from "../authoring/add-operation.js";
import { decodeRuleExpression, decodeTypedOperationContract, decodeTypedRuleContract, type RuleExpression, type TypedParameter } from "../typed-operation/contracts.js";
import { observeTarget, observeTargetReceipt } from "../conformance/observe-target.js";
import { readInstantiationReceipt } from "../conformance/receipt.js";
import { planInstantiation } from "../generation/plan-instantiation.js";
import { publishInstantiation } from "../generation/publish-instantiation.js";
import { planProjectInstantiation } from "../generation/project-instantiation.js";
import { publishProjectInstantiation } from "../generation/publish-project.js";
import {planSelectedReconciledProject as planReconciledProject,selectedRealizationMatches} from '../generation/selected-reconciled-project.js';
import {readReconciledCompilationSelection,verifyReconciledProject,ReconciledOutputError} from '../generation/reconciled-output.js';
import { materializeCompiledProjectCertificate } from "../compilation/certificate.js";
import { planProjectBuild, publishProjectBuild, verifyProjectBuild } from "../generation/project-build.js";
import { planWholeApplicationV1 } from "../generation/whole-application-v1.js";
import { publishWholeApplicationV1, verifyWholeApplicationV1 } from "../generation/whole-application-output-v1.js";
import { composeProviderApplicationV1 } from "../generation/provider-application-v1.js";
import { publishProviderApplicationV1, verifyProviderApplicationV1 } from "../generation/provider-application-output-v1.js";
import { verifyProviderApplicationRuntimeV1, type ProviderApplicationRuntimeEvidenceOptionsV1 } from "../generation/provider-application-runtime-evidence-v1.js";
import { checkLeanMetaTypeFormalization, materializeLeanMetaTypeFormalization } from "../formalization/projection.js";
import { loadCompiledProjectGraph, loadProjectNode, validateProjectRoot } from "../input/project-model.js";
import { normalizeLanguage } from "../meta-types/catalog.js";
import { loadSystemIntegrationSelection } from "../system-integration/compiler.js";
import type { IntegrationGenerationSourceV2 } from "../system-integration/generation-v2.js";
import { decodeCalculationSemantics, decodeMappingFields, decodePolicyDecisions } from "../static-semantics/contracts.js";
import { verifyProject } from "../verification/verify-project.js";
import { deriveConstructionTestPlan } from "../verification/test-derivation-plan.js";
import { runInMemoryProject } from "../runtime/in-memory.js";
import { materializeRuntimeReceipt } from "../runtime/receipt.js";
import { runDurableOperation } from "../runtime/durable.js";
import { PostgresTransactionalOutbox } from "../runtime/postgres-outbox.js";
import { certifyProject, checkCertifiedProject } from "../assurance/certify.js";
import { CLI_HELP, PRODUCT_CAPABILITIES, inspectProductEnvironment } from "../product/capabilities.js";
import { CLI_VERSION } from "../version.js";
import { MAX_SOURCE_FILE_BYTES, readBoundedFileSync } from "../input/limits.js";
import { readDeploymentRecipeRequest } from "../recipe/contracts.js";
import { deploymentRecipePlanSummary, planDeploymentRecipe } from "../recipe/plan.js";
import { publishDeploymentRecipe, verifyDeploymentRecipe } from "../recipe/publish.js";
import { readRecipeQualificationProfile } from "../qualification/contracts.js";
import { planRecipeQualification, recipeQualificationPlanSummary } from "../qualification/plan.js";
import { qualifyDeploymentRecipe, verifyRecipeQualification } from "../qualification/execute.js";

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

function addQueryArgs(args: readonly string[]): AddQueryInput {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot)) usage("add query requires one absolute source project root");
  const values = new Map<string, string>();
  const allowedOptions = ["--feature", "--name", "--description", "--reads", "--typed-contract-json"];
  for (let index = 1; index < args.length; index += 2) {
    const option = args[index];
    const value = args[index + 1];
    if (!option || !allowedOptions.includes(option) || value === undefined || value.startsWith("--")) usage("add query received an unsupported or unvalued option");
    if (values.has(option)) usage(`duplicate option:${option}`);
    values.set(option, value);
  }
  for (const required of allowedOptions) if (!values.has(required)) usage(`add query requires ${required}`);
  return Object.freeze({
    sourceRoot,
    featureId: values.get("--feature")!,
    nodeId: values.get("--name")!,
    description: values.get("--description")!,
    reads: parseCsvSet(values.get("--reads"), "--reads"),
    typedContract: decodeTypedOperationContract(parseJsonOption(values.get("--typed-contract-json")!, "--typed-contract-json")),
  });
}

function valuedOptions(args: readonly string[], command: string, allowed: readonly string[]): ReadonlyMap<string, string> {
  const values = new Map<string, string>();
  for (let index = 1; index < args.length; index += 2) {
    const option = args[index]; const value = args[index + 1];
    if (!option || !allowed.includes(option) || value === undefined || value.startsWith("--")) usage(`${command} received an unsupported or unvalued option`);
    if (values.has(option)) usage(`duplicate option:${option}`);
    values.set(option, value);
  }
  for (const required of allowed) if (!values.has(required)) usage(`${command} requires ${required}`);
  return values;
}

function staticSourceRoot(args: readonly string[], command: string): string {
  const root = args[0];
  if (!root || !path.isAbsolute(root)) usage(`${command} requires one absolute source project root`);
  return root;
}

function addCalculationArgs(args: readonly string[]): AddCalculationInput {
  const sourceRoot = staticSourceRoot(args, "add calculation");
  const values = valuedOptions(args, "add calculation", ["--feature", "--name", "--description", "--inputs", "--semantics-json", "--calculates"]);
  const inputs = parseCsvSet(values.get("--inputs"), "--inputs");
  return Object.freeze({ sourceRoot, featureId: values.get("--feature")!, nodeId: values.get("--name")!, description: values.get("--description")!, inputs, semantics: decodeCalculationSemantics(parseJsonOption(values.get("--semantics-json")!, "--semantics-json"), inputs), calculates: parseCsvSet(values.get("--calculates"), "--calculates") });
}

function addPolicyArgs(args: readonly string[]): AddPolicyInput {
  const sourceRoot = staticSourceRoot(args, "add policy");
  const values = valuedOptions(args, "add policy", ["--feature", "--name", "--description", "--strategies", "--decisions-json", "--default-strategy", "--applies"]);
  const strategies = parseCsvSet(values.get("--strategies"), "--strategies");
  return Object.freeze({ sourceRoot, featureId: values.get("--feature")!, nodeId: values.get("--name")!, description: values.get("--description")!, strategies, decisions: decodePolicyDecisions(parseJsonOption(values.get("--decisions-json")!, "--decisions-json"), strategies), defaultStrategy: values.get("--default-strategy")!, applies: parseCsvSet(values.get("--applies"), "--applies") });
}

function addMappingArgs(args: readonly string[]): AddMappingInput {
  const sourceRoot = staticSourceRoot(args, "add mapping");
  const values = valuedOptions(args, "add mapping", ["--feature", "--name", "--description", "--source", "--target", "--direction", "--totality", "--fields-json"]);
  const direction = values.get("--direction");
  if (direction !== "inbound" && direction !== "outbound" && direction !== "bidirectional") usage("--direction must be inbound, outbound, or bidirectional");
  const totality = values.get("--totality");
  if (totality !== "total" && totality !== "partial") usage("--totality must be total or partial");
  return Object.freeze({ sourceRoot, featureId: values.get("--feature")!, nodeId: values.get("--name")!, description: values.get("--description")!, sourceNodeId: values.get("--source")!, targetNodeId: values.get("--target")!, direction, totality, fields: decodeMappingFields(parseJsonOption(values.get("--fields-json")!, "--fields-json")) });
}

const THIN_COMMANDS: Readonly<Record<string, ThinBackendKind>> = Object.freeze({ query: "Query", calculation: "Calculation", mapping: "Mapping", policy: "Policy" });

function addThinBackendArgs(kind: ThinBackendKind, args: readonly string[]): AddThinBackendInput {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot)) usage(`add ${kind.toLowerCase()} requires one absolute source project root`);
  const values = new Map<string, string>();
  const allowed = ["--feature", "--name", "--description", "--contract-json", "--calculates"];
  for (let index = 1; index < args.length; index += 2) {
    const option = args[index]; const value = args[index + 1];
    if (!option || !allowed.includes(option) || value === undefined || value.startsWith("--")) usage(`add ${kind.toLowerCase()} received an unsupported or unvalued option`);
    if (values.has(option)) usage(`duplicate option:${option}`);
    values.set(option, value);
  }
  for (const option of ["--feature", "--name", "--description", "--contract-json"]) if (!values.has(option)) usage(`add ${kind.toLowerCase()} requires ${option}`);
  if (kind !== "Calculation" && values.has("--calculates")) usage("--calculates is only valid for Calculation");
  return Object.freeze({ sourceRoot, featureId: values.get("--feature")!, nodeId: values.get("--name")!, description: values.get("--description")!, kind, typedContract: parseJsonOption(values.get("--contract-json")!, "--contract-json"), calculates: parseCsvSet(values.get("--calculates"), "--calculates") });
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

function instantiateProjectArgs(args: readonly string[]): { readonly sourceRoot: string; readonly languages: readonly ("typescript" | "python" | "rust")[]; readonly targetRoot: string } {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot)) usage("instantiate-project requires one absolute source project root");
  const values = valuedOptions(args, "instantiate-project", ["--languages", "--target-root"]);
  const languages = parseCsvSet(values.get("--languages"), "--languages").map((language) => normalizeLanguage(language));
  if (languages.length < 1 || languages.length > 3 || new Set(languages).size !== languages.length) usage("instantiate-project requires one or more unique supported languages");
  const targetRoot = values.get("--target-root")!;
  if (!path.isAbsolute(targetRoot)) usage("--target-root must be absolute");
  return Object.freeze({ sourceRoot, languages: Object.freeze(languages), targetRoot });
}

function formalizeArgs(args: readonly string[], command: "formalize" | "formalize-check"): { readonly sourceRoot: string; readonly targetPath: string } {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot) || args.length !== 3 || args[1] !== "--target" || !path.isAbsolute(args[2] ?? "")) {
    usage(`${command} requires one absolute source project root and --target <absolute-file>`);
  }
  return Object.freeze({ sourceRoot, targetPath: args[2]! });
}

function verifyProjectArgs(args: readonly string[]): { readonly sourceRoot: string; readonly targetRoot: string } {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot) || args.length !== 3 || args[1] !== "--target-root" || !path.isAbsolute(args[2] ?? "")) {
    usage("verify-project requires one absolute source project root and --target-root <absolute-directory>");
  }
  return Object.freeze({ sourceRoot, targetRoot: args[2]! });
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

function projectBuildArgs(args: readonly string[], command: "build" | "verify"): { readonly sourceRoot: string; readonly language: "typescript" | "python" | "rust"; readonly targetRoot: string; readonly outputLayout?: OutputLayout | undefined; readonly realizationProfile?: RealizationProfile | undefined } {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot)) usage(`${command} requires one absolute source project root`);
  const values = new Map<string, string>();
  for (let index = 1; index < args.length; index += 2) {
    const option = args[index]; const value = args[index + 1];
    if (!option || !["--language", "--target-root", "--realization-profile", "--output-layout"].includes(option) || !value || value.startsWith("--")) usage(`${command} requires valued --language and --target-root`);
    if (values.has(option)) usage(`duplicate option:${option}`);
    values.set(option, value);
  }
  if ((values.size < 2 || values.size > 4) || !values.has("--language") || !values.has("--target-root")) usage(`${command} requires --language and --target-root`);
  const targetRoot = values.get("--target-root")!;
  if (!path.isAbsolute(targetRoot)) usage("--target-root must be absolute");
  return Object.freeze({ sourceRoot, outputLayout: validateOutputLayout(values.get("--output-layout")), language: normalizeLanguage(values.get("--language")), targetRoot, realizationProfile: validateRealizationProfile(values.get("--realization-profile"), normalizeLanguage(values.get("--language"))) });
}

function providerRuntimeArgs(args: readonly string[]): {
  readonly sourceRoot: string;
  readonly language: "typescript" | "python" | "rust";
  readonly realizationProfile?: RealizationProfile | undefined;
  readonly options: ProviderApplicationRuntimeEvidenceOptionsV1;
} {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot) || path.resolve(sourceRoot) !== sourceRoot) usage("verify-runtime requires one normalized absolute source project root");
  if (args.length % 2 !== 1) usage("verify-runtime requires valued options");
  const allowed = ["--language", "--target-root", "--temporary-parent", "--receipt", "--realization-profile", "--node-executable", "--npm-executable", "--python-executable", "--docker-executable", "--python-image", "--cargo-executable"];
  const values = new Map<string, string>();
  for (let index = 1; index < args.length; index += 2) {
    const option = args[index]; const value = args[index + 1];
    if (!option || !allowed.includes(option) || !value || value.startsWith("--") || values.has(option)) usage("verify-runtime requires unique known valued options");
    if (option !== "--language" && option !== "--realization-profile" && option !== "--python-image" && (!path.isAbsolute(value) || path.resolve(value) !== value)) usage("verify-runtime path and executable options must be normalized absolute paths");
    values.set(option, value);
  }
  const common = ["--language", "--target-root", "--temporary-parent", "--receipt"];
  if (common.some(option => !values.has(option))) usage(`verify-runtime requires ${common.join(", ")}`);
  const language = normalizeLanguage(values.get("--language"));
  const localPython = values.has("--python-executable");
  const containerPython = values.has("--docker-executable") && values.has("--python-image");
  if (language === "python" && localPython === containerPython) usage("verify-runtime for python requires exactly one of --python-executable or the --docker-executable/--python-image pair");
  const languageOptions = language === "typescript" ? ["--node-executable", "--npm-executable"] : language === "python" ? (localPython ? ["--python-executable"] : ["--docker-executable", "--python-image"]) : ["--cargo-executable"];
  if (languageOptions.some(option => !values.has(option))) usage(`verify-runtime for ${language} requires ${languageOptions.join(", ")}`);
  const permitted = new Set([...common, "--realization-profile", ...languageOptions]);
  if ([...values.keys()].some(option => !permitted.has(option))) usage(`verify-runtime received a tool option for a different language`);
  const realizationProfile = validateRealizationProfile(values.get("--realization-profile"), language);
  return Object.freeze({
    sourceRoot,
    language,
    realizationProfile,
    options: Object.freeze({
      target_root: values.get("--target-root")!,
      temporary_parent: values.get("--temporary-parent")!,
      receipt_path: values.get("--receipt")!,
      ...(language === "typescript" ? { node_executable: values.get("--node-executable")!, npm_executable: values.get("--npm-executable")! } : {}),
      ...(language === "python" && localPython ? { python_executable: values.get("--python-executable")! } : {}),
      ...(language === "python" && containerPython ? { docker_executable: values.get("--docker-executable")!, python_image: values.get("--python-image")! } : {}),
      ...(language === "rust" ? { cargo_executable: values.get("--cargo-executable")! } : {}),
    }),
  });
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

function recipeArgs(args: readonly string[], command: "recipe-plan" | "recipe-generate" | "recipe-verify"): { readonly sourceRoot: string; readonly requestPath: string; readonly consumerRoot: string; readonly targetRoot: string | null } {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot)) usage(`${command} requires one absolute source project root`);
  const required = command === "recipe-plan" ? ["--request", "--consumer-root"] : ["--request", "--consumer-root", "--target-root"];
  const values = new Map<string, string>();
  for (let index = 1; index < args.length; index += 2) {
    const option = args[index]; const value = args[index + 1];
    if (!option || !required.includes(option) || !value || !path.isAbsolute(value)) usage(`${command} requires absolute ${required.join(", ")}`);
    if (values.has(option)) usage(`duplicate option:${option}`);
    values.set(option, value);
  }
  if (values.size !== required.length || required.some((option) => !values.has(option))) usage(`${command} requires absolute ${required.join(", ")}`);
  return Object.freeze({ sourceRoot, requestPath: values.get("--request")!, consumerRoot: values.get("--consumer-root")!, targetRoot: values.get("--target-root") ?? null });
}

function qualificationArgs(args: readonly string[], command: "recipe-qualification-plan" | "recipe-qualify" | "recipe-qualification-verify"): { readonly sourceRoot: string; readonly requestPath: string; readonly consumerRoot: string; readonly targetRoot: string; readonly profilePath: string; readonly qualificationRoot: string | null } {
  const sourceRoot = args[0];
  if (!sourceRoot || !path.isAbsolute(sourceRoot)) usage(`${command} requires one absolute source project root`);
  const required = command === "recipe-qualification-plan" ? ["--request", "--consumer-root", "--target-root", "--profile"] : ["--request", "--consumer-root", "--target-root", "--profile", "--qualification-root"];
  const values = new Map<string, string>();
  for (let index = 1; index < args.length; index += 2) {
    const option = args[index]; const value = args[index + 1];
    if (!option || !required.includes(option) || !value || !path.isAbsolute(value)) usage(`${command} requires absolute ${required.join(", ")}`);
    if (values.has(option)) usage(`duplicate option:${option}`);
    values.set(option, value);
  }
  if (values.size !== required.length || required.some((option) => !values.has(option))) usage(`${command} requires absolute ${required.join(", ")}`);
  return Object.freeze({ sourceRoot, requestPath: values.get("--request")!, consumerRoot: values.get("--consumer-root")!, targetRoot: values.get("--target-root")!, profilePath: values.get("--profile")!, qualificationRoot: values.get("--qualification-root") ?? null });
}

function postgresProvider(): PostgresTransactionalOutbox {
  const required = ["PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "PGPASSWORD"] as const;
  for (const key of required) if (!process.env[key]) usage(`postgres provider requires ${key}`);
  const configuredAttempts = process.env.OUTBOX_MAX_ATTEMPTS;
  return new PostgresTransactionalOutbox({ host: process.env.PGHOST!, port: Number(process.env.PGPORT), database: process.env.PGDATABASE!, user: process.env.PGUSER!, password: process.env.PGPASSWORD!, ...(configuredAttempts === undefined ? {} : { maxAttempts: Number(configuredAttempts) }) });
}

function isInstantiationTarget(root: string): boolean {
  return fs.existsSync(path.join(root, ".domainspec", "instantiations"));
}

function errorEnvelope(error: unknown): Record<string, unknown> {
  const candidate = error as Partial<Error> & { code?: unknown; pointer?: unknown;
    retained_stage?: unknown; retained_evidence_directory?: unknown };
  return {
    result: "fail",
    code: typeof candidate.code === "string" ? candidate.code : "MTCLI_UNEXPECTED",
    pointer: typeof candidate.pointer === "string" ? candidate.pointer : "$",
    message: error instanceof Error ? error.message : "unexpected failure",
    ...(candidate.retained_stage ? { retained_stage: candidate.retained_stage } : {}),
    ...(typeof candidate.retained_evidence_directory === "string" ?
      { retained_evidence_directory: candidate.retained_evidence_directory } : {}),
    authority_effect: "none",
  };
}

function readIntegrationGenerationSource(file: string): IntegrationGenerationSourceV2 {
  try {
    return JSON.parse(readBoundedFileSync(file, MAX_SOURCE_FILE_BYTES).toString("utf8")) as IntegrationGenerationSourceV2;
  } catch {
    usage(`--integration-source must identify readable JSON no larger than ${MAX_SOURCE_FILE_BYTES} bytes`);
  }
}

function readProviderSelection(file: string): unknown {
  try {
    return JSON.parse(readBoundedFileSync(file, MAX_SOURCE_FILE_BYTES).toString("utf8"));
  } catch {
    usage(`--provider-selection must identify readable JSON no larger than ${MAX_SOURCE_FILE_BYTES} bytes`);
  }
}

function reconciledCommand(command:string|undefined,args:readonly string[],io:CliIo):number|null {
  const hasIntegrationSource=args.includes('--integration-source');
  const hasProviderSelection=args.includes('--provider-selection');
  if(!args.includes('--compilation-selection')){
    if(hasIntegrationSource||hasProviderSelection)usage('--integration-source and --provider-selection require --compilation-selection and a reconciled whole-project command');
    return null;
  }
  if(!command||!['instantiate','instantiate-project','build','verify','verify-project','verify-runtime'].includes(command))usage('--compilation-selection is supported only by instantiate, instantiate-project, build, artifact-currentness verify, stronger verify-project, and provider verify-runtime');
  const index=args.indexOf('--compilation-selection');
  if(index<1||index%2!==1||args.lastIndexOf('--compilation-selection')!==index||!args[index+1]||args[index+1]!.startsWith('--'))usage('--compilation-selection requires one valued absolute JSON path');
  let integrationSourcePath:string|null=null,integrationIndex=-1;
  if(hasIntegrationSource){
    if(!['instantiate-project','build','verify','verify-runtime'].includes(command))usage('--integration-source is supported only by reconciled instantiate-project, build, whole-project verify, and verify-runtime');
    integrationIndex=args.indexOf('--integration-source');
    const value=args[integrationIndex+1];
    if(integrationIndex<1||integrationIndex%2!==1||args.lastIndexOf('--integration-source')!==integrationIndex||!value||value.startsWith('--')||!path.isAbsolute(value)||path.resolve(value)!==value)usage('--integration-source requires one valued normalized absolute JSON path');
    integrationSourcePath=value;
  }
  let providerSelectionPath:string|null=null,providerIndex=-1;
  if(hasProviderSelection){
    if(!hasIntegrationSource)usage('--provider-selection requires --integration-source');
    if(!['instantiate-project','build','verify','verify-runtime'].includes(command))usage('--provider-selection is supported only by reconciled instantiate-project, build, whole-project verify, and verify-runtime');
    providerIndex=args.indexOf('--provider-selection');
    const value=args[providerIndex+1];
    if(providerIndex<1||providerIndex%2!==1||args.lastIndexOf('--provider-selection')!==providerIndex||!value||value.startsWith('--')||!path.isAbsolute(value)||path.resolve(value)!==value)usage('--provider-selection requires one valued normalized absolute JSON path');
    providerSelectionPath=value;
  }
  const removed=new Set([index,index+1,...(integrationIndex<0?[]:[integrationIndex,integrationIndex+1]),...(providerIndex<0?[]:[providerIndex,providerIndex+1])]);
  let ordinary=args.filter((_value,position)=>!removed.has(position));
  if(command==='verify-project'){
    const selection=readReconciledCompilationSelection(args[index+1]);
    const python=selection.language==='python',rust=selection.language==='rust';
    const source=ordinary[0],required=python
      ? ['--target-root','--python-executable','--temporary-parent','--lean-executable']
      : rust
        ? ['--target-root','--cargo-executable','--temporary-parent']
        : ['--target-root','--typescript-root','--node-type-root','--lean-executable'],allowed=[...required,'--output-layout'];
    if(!source||!path.isAbsolute(source)||path.resolve(source)!==source||ordinary.length%2!==1)usage('selected verify-project requires a normalized absolute source root and valued tool/target options');
    const values=new Map<string,string>();
    for(let i=1;i<ordinary.length;i+=2){
      const key=ordinary[i]!,value=ordinary[i+1];
      if(!allowed.includes(key)||values.has(key)||!value||value.startsWith('--'))usage('selected verify-project requires unique known valued options');
      if(key!=='--output-layout'&&(!path.isAbsolute(value)||path.resolve(value)!==value))usage('selected verify-project tool and target paths must be normalized absolute paths');
      values.set(key,value);
    }
    if(required.some(key=>!values.has(key)))usage('selected verify-project requires '+required.join(', '));
    const outputLayout=validateOutputLayout(values.get('--output-layout'));
    const report=python
      ? verifyProject(source,values.get('--target-root')!,selection,{
          python_executable:values.get('--python-executable')!,temporary_parent:values.get('--temporary-parent')!,target_root:values.get('--target-root')!,lean_executable:values.get('--lean-executable')!,
          ...(outputLayout===undefined?{}:{output_layout:outputLayout}),
        })
      : rust
        ? verifyProject(source,values.get('--target-root')!,selection,{
          cargo_executable:values.get('--cargo-executable')!,temporary_parent:values.get('--temporary-parent')!,target_root:values.get('--target-root')!,
          ...(outputLayout===undefined?{}:{output_layout:outputLayout}),
        })
        : verifyProject(source,values.get('--target-root')!,selection,{
          typescript_root:values.get('--typescript-root')!,node_type_root:values.get('--node-type-root')!,lean_executable:values.get('--lean-executable')!,
          ...(outputLayout===undefined?{}:{output_layout:outputLayout}),
        });
    objectOutput(io,report);return report.result==='pass'?0:1;
  }
  if(command==='verify-runtime'){
    if(integrationSourcePath===null||providerSelectionPath===null)usage('verify-runtime requires --integration-source and --provider-selection');
    const parsed=providerRuntimeArgs(ordinary);
    const selection=readReconciledCompilationSelection(args[index+1]);
    if(parsed.language!==selection.language||!selectedRealizationMatches(selection,parsed.realizationProfile))usage('command language or numeric realization conflicts with the reconciled selection');
    const result=verifyProviderApplicationRuntimeV1(parsed.sourceRoot,selection,readIntegrationGenerationSource(integrationSourcePath),readProviderSelection(providerSelectionPath),parsed.options);
    objectOutput(io,result);return 0;
  }
  let sourceRoot:string,targetRoot:string,language:string,roots:readonly string[]|null=null,realizationProfile:RealizationProfile|undefined,outputLayout:OutputLayout|undefined;
  if(command==='instantiate'){
    const parsed=instantiateArgs(ordinary);if(parsed.integrationProfile!==null)usage('reconciled selection does not support a system-integration overlay');
    ({sourceRoot,targetRoot,language}=parsed);roots=[parsed.node];
  }else if(command==='instantiate-project'){
    const parsed=instantiateProjectArgs(ordinary);if(parsed.languages.length!==1)usage('reconciled project selection requires one language');
    ({sourceRoot,targetRoot}=parsed);language=parsed.languages[0]!;
  }else{
    if(command==='verify'&&ordinary.includes('--node')){
      const nodeIndex=ordinary.indexOf('--node');
      if(nodeIndex<1||nodeIndex%2!==1||ordinary.lastIndexOf('--node')!==nodeIndex||!ordinary[nodeIndex+1]||ordinary[nodeIndex+1]!.startsWith('--'))usage('selected verify requires one valued --node selector');
      roots=[ordinary[nodeIndex+1]!];ordinary=[...ordinary.slice(0,nodeIndex),...ordinary.slice(nodeIndex+2)];
    }
    const parsed=projectBuildArgs(ordinary,command as 'build'|'verify');if(parsed.outputLayout!==undefined&&roots!==null)usage('reconciled structured output layouts require whole-project output');
    ({sourceRoot,targetRoot,language,realizationProfile,outputLayout}=parsed);
  }
  const selection=readReconciledCompilationSelection(args[index+1]);
  if(language!==selection.language||!selectedRealizationMatches(selection,realizationProfile))usage('command language or numeric realization conflicts with the reconciled selection');
  if(integrationSourcePath!==null){
    if(roots!==null||outputLayout!==undefined)usage('--integration-source requires whole-project output with the compiler-owned layout');
    const integrationSource=readIntegrationGenerationSource(integrationSourcePath);
    const providerSelection=providerSelectionPath===null?null:readProviderSelection(providerSelectionPath);
    if(command==='verify'){
      const result=providerSelection===null
        ? verifyWholeApplicationV1(sourceRoot,selection,integrationSource,targetRoot)
        : verifyProviderApplicationV1(sourceRoot,selection,integrationSource,providerSelection,targetRoot);
      objectOutput(io,result);return result.result==='pass'?0:1;
    }
    const whole=planWholeApplicationV1(sourceRoot,selection,integrationSource);
    if(providerSelection!==null){
      const plan=composeProviderApplicationV1(whole,providerSelection,integrationSource);
      const publication=publishProviderApplicationV1(plan,targetRoot);
      objectOutput(io,{schema_version:'domainspec.provider-application-command-result/v1-candidate',command,result:'pass',target_root:publication.target_root,receipt_path:publication.receipt_path,whole_application_plan_sha256:plan.whole_application_plan_sha256,provider_application_plan_sha256:plan.plan_sha256,provider_selection_sha256:plan.provider_selection_sha256,receipt_sha256:publication.receipt.receipt_sha256,artifact_count:plan.artifacts.length,language:plan.language,runtime_guarantees_observed:false,authority_effect:'none'});return 0;
    }
    const publication=publishWholeApplicationV1(whole,targetRoot);
    objectOutput(io,{schema_version:'domainspec.whole-application-command-result/v1-candidate',command,result:'pass',target_root:publication.target_root,receipt_path:publication.receipt_path,whole_application_plan_sha256:whole.plan_sha256,receipt_sha256:publication.receipt.receipt_sha256,artifact_count:whole.artifacts.length,language:whole.language,authority_effect:'none'});return 0;
  }
  if(command==='build'||command==='verify'&&roots===null){
    try{
      if(command==='verify'){
        const result=verifyProjectBuild(sourceRoot,selection.language,targetRoot,realizationProfile,outputLayout,selection);
        objectOutput(io,result);return result.result==='pass'?0:1;
      }
      const publication=publishProjectBuild(planProjectBuild(sourceRoot,selection.language,realizationProfile,outputLayout,selection),targetRoot);
      objectOutput(io,{schema_version:'domainspec.reconciled-command-result/v1-candidate',command,result:'pass',...publication,authority_effect:'none'});return 0;
    }catch(error){const e=error as {pointer?:unknown;code?:unknown};throw new ReconciledOutputError(typeof e.code==='string'?e.code:'DS_RECONCILED_INPUT',typeof e.pointer==='string'?e.pointer:'/source',error instanceof Error?error.message:'invalid reconciled source');}
  }
  try{
    if(command==='instantiate-project'){
      const publication=publishProjectInstantiation(planProjectInstantiation(sourceRoot,[selection.language],selection),targetRoot);
      objectOutput(io,{schema_version:'domainspec.reconciled-command-result/v1-candidate',command,result:'pass',...publication,authority_effect:'none'});return 0;
    }
    const plan=planReconciledProject(sourceRoot,selection);
    if(command==='verify'){
      const result=verifyReconciledProject(plan,targetRoot,roots);objectOutput(io,result);return result.result==='pass'?0:1;
    }
    const publication=publishInstantiation(planInstantiation(roots![0]!,selection.language,null,realizationProfile,plan),targetRoot);
    objectOutput(io,{schema_version:'domainspec.reconciled-command-result/v1-candidate',command,result:'pass',...publication,authority_effect:'none'});return 0;
  }catch(error){const e=error as {pointer?:unknown;code?:unknown};throw new ReconciledOutputError(typeof e.code==='string'?e.code:'DS_RECONCILED_INPUT',typeof e.pointer==='string'?e.pointer:'/source',error instanceof Error?error.message:'invalid reconciled source');}
}

export function runCli(argv: readonly string[], io: CliIo = {
  stdout: (value) => process.stdout.write(value),
  stderr: (value) => process.stderr.write(value),
}): number {
  try {
    const [command, ...args] = argv;
    if (command === "computation") return runComputationCommand(args, io);
    const reconciled=reconciledCommand(command,args,io);if(reconciled!==null)return reconciled;
    if(command==='application-check'||command==='application-build'){
      const inputPath=args[0];if(!inputPath||!path.isAbsolute(inputPath))usage('application input must be an absolute JSON path');
      const options=valuedOptions(args,command,command==='application-build'?['--root','--target-root']:['--root']);
      const root=options.get('--root')!;if(!path.isAbsolute(root))usage('--root must be absolute');
      const input=JSON.parse(readBoundedFileSync(inputPath,16*1024*1024).toString('utf8'));
      if(command==='application-check')objectOutput(io,checkApplicationOntology(input,root));
      else {const target=options.get('--target-root')!;if(!path.isAbsolute(target))usage('--target-root must be absolute');objectOutput(io,buildApplicationOntology(input,root,target));}
      return 0;
    }

    if (command === undefined || command === "help" || command === "--help" || command === "-h") {
      io.stdout(CLI_HELP);
      io.stdout('\nProfile generation frontend: alchlang profile select|check|plan|generate|view|verify <project.json>. Craft exposes the registered profileEngine library. Native checking does not prove formal claims or runtime admission; local hosting, TDE, EVF and publication remain deferred.\n');
      return 0;
    }
    if (command === "--version" || command === "-v") {
      io.stdout(`${CLI_VERSION}\n`);
      return 0;
    }
    if (command === "capabilities") {
      if (args.length !== 0) usage("capabilities accepts no arguments");
      objectOutput(io, PRODUCT_CAPABILITIES);
      return 0;
    }
    if (command === "doctor") {
      if (args.length !== 0) usage("doctor accepts no arguments");
      const result = inspectProductEnvironment();
      objectOutput(io, result);
      return result.result === "pass" ? 0 : 1;
    }
    if (command === "add") {
      if (!args[0] || !["operation", "query", "calculation", "rule", "policy", "mapping"].includes(args[0])) usage("add requires a supported meta-type: operation, query, calculation, rule, policy, or mapping");
      const result = THIN_COMMANDS[args[0]] && args.includes("--contract-json")
        ? addThinBackend(addThinBackendArgs(THIN_COMMANDS[args[0]]!, args.slice(1)))
        : args[0] === "operation"
        ? addOperation(addOperationArgs(args.slice(1)))
        : args[0] === "query"
          ? addQuery(addQueryArgs(args.slice(1)))
          : args[0] === "calculation"
            ? addCalculation(addCalculationArgs(args.slice(1)))
            : args[0] === "rule"
              ? addRule(addRuleArgs(args.slice(1)))
              : args[0] === "policy"
                ? addPolicy(addPolicyArgs(args.slice(1)))
                : addMapping(addMappingArgs(args.slice(1)));
      objectOutput(io, {
        schema_version: `domainspec.add-${args[0]}-command-result/v1`,
        result: "pass",
        publication_protocol: result.publication_protocol,
        source_root: result.source_root,
        selector: result.selector,
        node_path: result.node_path,
        relationship_paths: result.relationship_paths,
        source_manifest_sha256: result.source_manifest.manifest_sha256,
        source_count: result.source_manifest.source_count,
        authority_effect: result.authority_effect,
      });
      return 0;
    }
    if (command === "recipe-plan" || command === "recipe-generate" || command === "recipe-verify") {
      const parsed = recipeArgs(args, command);
      const request = readDeploymentRecipeRequest(parsed.requestPath);
      if (command === "recipe-plan") {
        objectOutput(io, deploymentRecipePlanSummary(planDeploymentRecipe(parsed.sourceRoot, request, parsed.consumerRoot)));
        return 0;
      }
      if (command === "recipe-generate") {
        const plan = planDeploymentRecipe(parsed.sourceRoot, request, parsed.consumerRoot);
        const publication = publishDeploymentRecipe(plan, parsed.targetRoot!);
        objectOutput(io, { schema_version: "domainspec.deployment-recipe-command-result/v1", result: "pass", target_root: publication.target_root, receipt_path: publication.receipt_path, artifact_count: plan.artifacts.length, manifest_sha256: plan.manifest.manifest_sha256, plan_sha256: plan.plan_sha256, receipt_sha256: publication.receipt.receipt_sha256, authority_effect: "none" });
        return 0;
      }
      const verification = verifyDeploymentRecipe(parsed.sourceRoot, request, parsed.consumerRoot, parsed.targetRoot!);
      objectOutput(io, verification);
      return verification.result === "pass" ? 0 : 1;
    }
    if (command === "recipe-qualification-plan" || command === "recipe-qualify" || command === "recipe-qualification-verify") {
      const parsed = qualificationArgs(args, command);
      const request = readDeploymentRecipeRequest(parsed.requestPath);
      const profile = readRecipeQualificationProfile(parsed.profilePath);
      if (command === "recipe-qualification-plan") {
        objectOutput(io, recipeQualificationPlanSummary(planRecipeQualification(parsed.sourceRoot, request, parsed.consumerRoot, parsed.targetRoot, profile)));
        return 0;
      }
      if (command === "recipe-qualify") {
        const publication = qualifyDeploymentRecipe(parsed.sourceRoot, request, parsed.consumerRoot, parsed.targetRoot, profile, parsed.qualificationRoot!);
        objectOutput(io, { schema_version: "domainspec.recipe-qualification-command-result/v1", result: publication.certificate.result, qualification_root: publication.qualification_root, plan_sha256: publication.plan.plan_sha256, certificate_sha256: publication.certificate.certificate_sha256, receipt_sha256: publication.receipt.receipt_sha256, authority_effect: "none" });
        return publication.certificate.result === "pass" ? 0 : 1;
      }
      const verification = verifyRecipeQualification(parsed.sourceRoot, request, parsed.consumerRoot, parsed.targetRoot, profile, parsed.qualificationRoot!);
      objectOutput(io, verification);
      return verification.result === "pass" ? 0 : 1;
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
    if (command === "instantiate-project") {
      const parsed = instantiateProjectArgs(args);
      const plan = planProjectInstantiation(parsed.sourceRoot, parsed.languages);
      const publication = publishProjectInstantiation(plan, parsed.targetRoot);
      objectOutput(io, { schema_version: "domainspec.instantiate-project-command-result/v1", result: "pass", target_root: publication.target_root, receipt_path: publication.receipt_path, project_plan_sha256: plan.project_plan_sha256, receipt_sha256: publication.receipt.receipt_sha256, graph_certificate: plan.graph_certificate, artifact_count: plan.artifacts.length, authority_effect: "none" });
      return 0;
    }
    if (command === "verify-project") {
      const parsed = verifyProjectArgs(args);
      objectOutput(io, verifyProject(parsed.sourceRoot, parsed.targetRoot));
      return 0;
    }
    if (command === "compile") {
      const parsed = compileArgs(args);
      const certificate = materializeCompiledProjectCertificate(parsed.sourceRoot, parsed.targetPath);
      objectOutput(io, { schema_version: "domainspec.compile-command-result/v1", result: "pass", target_path: parsed.targetPath, certificate, authority_effect: "none" });
      return 0;
    }
    if (command === "derive-tests") {
      objectOutput(io, deriveConstructionTestPlan(loadCompiledProjectGraph(exactlyOneRoot(args, command))));
      return 0;
    }
    if (command === "certify" || command === "certify-check") {
      const parsed = certifyArgs(args, command);
      if (command === "certify") {
        const certificate = certifyProject(parsed.sourceRoot, parsed.targetDirectory);
        objectOutput(io, { schema_version: "domainspec.certify-command-result/v1", result: "pass", target_directory: parsed.targetDirectory, certificate, authority_effect: "none" });
        return 0;
      }
      const result = checkCertifiedProject(parsed.sourceRoot, parsed.targetDirectory);
      objectOutput(io, result);
      return result.current ? 0 : 1;
    }
    if (command === "build" || command === "verify") {
      const parsed = projectBuildArgs(args, command);
      if (command === "build") {
        const publication = publishProjectBuild(planProjectBuild(parsed.sourceRoot, parsed.language, parsed.realizationProfile, parsed.outputLayout), parsed.targetRoot);
        objectOutput(io, { schema_version: "domainspec.build-command-result/v1", result: "pass", ...publication, authority_effect: "none" });
        return 0;
      }
      const verification = verifyProjectBuild(parsed.sourceRoot, parsed.language, parsed.targetRoot, parsed.realizationProfile, parsed.outputLayout);
      objectOutput(io, verification);
      return verification.result === "pass" ? 0 : 1;
    }
    if (command === "run") {
      const parsed = runArgs(args);
      let request: unknown;
      try { request = JSON.parse(readBoundedFileSync(parsed.requestPath, MAX_SOURCE_FILE_BYTES).toString("utf8")); } catch { usage(`--request must identify readable JSON no larger than ${MAX_SOURCE_FILE_BYTES} bytes`); }
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
          schema_version: "domainspec.meta-type-formalization-command-result/v1",
          result: "pass",
          source_manifest_sha256: sourceManifest.manifest_sha256,
          ...result,
          authority_effect: "none",
        });
        return 0;
      }
      const result = checkLeanMetaTypeFormalization(projectGraph, parsed.targetPath);
      objectOutput(io, {
        schema_version: "domainspec.meta-type-formalization-command-result/v1",
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
    usage("expected command: add <meta-type>, instantiate, instantiate-project, verify-project, verify-runtime, compile, build, verify, run, formalize, formalize-check, certify, certify-check, lint, or receipt");
  } catch (error) {
    objectOutput({ ...io, stdout: io.stderr }, errorEnvelope(error));
    const candidate = error as { exitCode?: unknown };
    return typeof candidate.exitCode === "number" ? candidate.exitCode : 1;
  }
}

// Library consumers can use Node's stdin entrypoint (argv[1] is "-").
let invokedFile: string | undefined;
try { if (process.argv[1] && process.argv[1] !== "-") invokedFile = fs.realpathSync(process.argv[1]); }
catch { /* An unavailable consumer entrypoint does not invoke this CLI. */ }
if (invokedFile === fileURLToPath(import.meta.url)) {
  process.exitCode = runCli(process.argv.slice(2));
}
