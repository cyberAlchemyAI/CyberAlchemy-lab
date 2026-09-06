import { createHash } from "node:crypto";
import { lstat, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { basename, join, resolve } from "node:path";

import ts from "typescript";

import {
  readValidatedHandle,
  type ValidatedHandle,
} from "../../../kernel/contracts/validated-handle.js";
import type { RuleObservationV1 } from "../../../families/outcome-function/contracts/rule-contracts.js";
import type { NormalizedRulePackageV1 } from "../../../families/outcome-function/providers/decode-rule-contracts.js";
import { inspectTypeScriptRuleSource } from "../../adapter/rule/index.js";
import { observeCompiledTypeScriptRule } from "../../runtime/rule/index.js";

export type TypeScriptRuleExecutionV1 = Readonly<{
  schema_version: "TypeScriptRuleExecution/v1";
  base_source_sha256: string;
  execution_source_sha256: string;
  mutation_id: string | null;
  compiler: Readonly<{ name: "typescript"; version: string; tool_sha256: string; config_sha256: string }>;
  workspace: Readonly<{
    workspace_id: string;
    isolation_scope: "proof-session";
    isolated: true;
    symlinks: false;
    cleaned: true;
  }>;
  exit_status: 0 | 1;
  diagnostics: readonly Readonly<{ code: string; message: string }>[];
  observation: RuleObservationV1 | null;
  authority_effect: "none";
}>;

export type TypeScriptRuleExecutionVariantV1 = Readonly<{
  variantId: string;
  executionSource?: string;
  mutationId?: string;
}>;

export type TypeScriptRuleProofSessionV1 = Readonly<{
  schema_version: "TypeScriptRuleProofSession/v1";
  result: "pass" | "block";
  workspace: TypeScriptRuleExecutionV1["workspace"];
  compiler: TypeScriptRuleExecutionV1["compiler"];
  variants: readonly Readonly<{
    variant_id: string;
    execution: TypeScriptRuleExecutionV1;
  }>[];
  diagnostics: readonly Readonly<{
    variant_id: string | null;
    code: string;
    message: string;
  }>[];
  authority_effect: "none";
}>;

const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");
const compilerConfig = Object.freeze({
  target: "ES2022",
  module: "NodeNext",
  moduleResolution: "NodeNext",
  strict: true,
  noEmitOnError: true,
});
export const typeScriptRuleCompilerConfigSha256 = sha256(JSON.stringify(compilerConfig));
type NormalizedDiagnostic = Readonly<{ code: string; message: string }>;

const diagnosticMessage = (item: ts.Diagnostic): string =>
  ts.flattenDiagnosticMessageText(item.messageText, " ")
    .replaceAll(/\s+/gu, " ").trim();

const compareDiagnostics = (left: ts.Diagnostic, right: ts.Diagnostic): number =>
  left.code - right.code ||
  (left.start ?? -1) - (right.start ?? -1) ||
  Buffer.from(diagnosticMessage(left)).compare(Buffer.from(diagnosticMessage(right)));

const normalizeDiagnostics = (items: readonly ts.Diagnostic[]): readonly NormalizedDiagnostic[] =>
  Object.freeze([...items].sort(compareDiagnostics).map((item) => Object.freeze({
    code: `TS${item.code}`,
    message: diagnosticMessage(item),
  })));

const diagnostic = (code: string, message: string): NormalizedDiagnostic =>
  Object.freeze({ code, message });

const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};

const compilerOptions = (rootDir: string, outDir: string): ts.CompilerOptions => ({
  target: ts.ScriptTarget.ES2022,
  module: ts.ModuleKind.NodeNext,
  moduleResolution: ts.ModuleResolutionKind.NodeNext,
  strict: true,
  noEmitOnError: true,
  rootDir,
  outDir,
});

export const executeTypeScriptRuleProofSession = async (input: Readonly<{
  rule: ValidatedHandle<NormalizedRulePackageV1>;
  baseSource: string;
  variants: readonly TypeScriptRuleExecutionVariantV1[];
}>): Promise<TypeScriptRuleProofSessionV1> => {
  if (input.variants.length === 0) return fail("TS_RULE_PROOF_SESSION_EMPTY");
  const variantIds = input.variants.map(({ variantId }) => variantId);
  if (variantIds.some((id) => id.length === 0) ||
      new Set(variantIds).size !== variantIds.length) {
    return fail("TS_RULE_PROOF_SESSION_VARIANT_INVALID");
  }
  const rule = readValidatedHandle(input.rule);
  const inspection = inspectTypeScriptRuleSource({
    modulePath: rule.binding.source_ref.path,
    source: input.baseSource,
    symbolName: rule.binding.symbol_name,
  });
  if (inspection.source_sha256 !== rule.binding.source_ref.sha256) {
    return fail("TS_RULE_BASE_SOURCE_STALE");
  }
  if (!inspection.supported) {
    return fail(inspection.diagnostics[0]?.code ?? "TS_RULE_SOURCE_UNSUPPORTED");
  }
  const workspace = await mkdtemp(join(tmpdir(), "domainspec-rule-ts-session-"));
  const sourceRoot = resolve(workspace, "source");
  const outputRoot = resolve(workspace, "dist");
  const require = createRequire(import.meta.url);
  const compilerPath = require.resolve("typescript");
  try {
    await Promise.all([
      mkdir(sourceRoot, { recursive: true }),
      mkdir(outputRoot, { recursive: true }),
      writeFile(resolve(workspace, "package.json"), "{\"type\":\"module\"}\n", {
        encoding: "utf8",
        flag: "wx",
      }),
    ]);
    const prepared = await Promise.all(input.variants.map(async (variant, index) => {
      const directory = `variant-${String(index).padStart(4, "0")}`;
      const sourceDirectory = resolve(sourceRoot, directory);
      const outputDirectory = resolve(outputRoot, directory);
      await Promise.all([
        mkdir(sourceDirectory, { recursive: true }),
        mkdir(outputDirectory, { recursive: true }),
      ]);
      const executionSource = variant.executionSource ?? input.baseSource;
      const sourcePath = resolve(sourceDirectory, "rule.ts");
      await writeFile(sourcePath, executionSource, { encoding: "utf8", flag: "wx" });
      return Object.freeze({
        directory,
        variantId: variant.variantId,
        sourcePath,
        outputPath: resolve(outputDirectory, "rule.js"),
        executionSource,
        mutationId: variant.mutationId,
      });
    }));
    const compilerSha256 = sha256(await readFile(compilerPath));
    const program = ts.createProgram(
      prepared.map(({ sourcePath }) => sourcePath),
      compilerOptions(sourceRoot, outputRoot),
    );
    const sourceByPath = new Map(prepared.map((variant) =>
      [variant.sourcePath, variant] as const));
    const globalDiagnostics: ts.Diagnostic[] = [
      ...program.getConfigFileParsingDiagnostics(),
      ...program.getOptionsDiagnostics(),
      ...program.getGlobalDiagnostics(),
    ];
    const diagnosticsByVariant = new Map<string, ts.Diagnostic[]>();
    for (const variant of prepared) {
      const sourceFile = program.getSourceFile(variant.sourcePath) ??
        fail("TS_RULE_PROOF_SESSION_SOURCE_MISSING");
      diagnosticsByVariant.set(variant.variantId, [
        ...program.getSyntacticDiagnostics(sourceFile),
        ...program.getSemanticDiagnostics(sourceFile),
      ]);
    }
    const preEmitBlocked = globalDiagnostics.length > 0 ||
      [...diagnosticsByVariant.values()].some((items) => items.length > 0);
    const emitted = preEmitBlocked
      ? { emitSkipped: true, diagnostics: [] as readonly ts.Diagnostic[] }
      : program.emit();
    for (const item of emitted.diagnostics) {
      const variant = item.file === undefined ? undefined : sourceByPath.get(item.file.fileName);
      if (variant === undefined) globalDiagnostics.push(item);
      else diagnosticsByVariant.get(variant.variantId)!.push(item);
    }
    if (emitted.emitSkipped && globalDiagnostics.length === 0 &&
        [...diagnosticsByVariant.values()].every((items) => items.length === 0)) {
      return fail("TS_RULE_PROOF_SESSION_EMIT_SKIPPED");
    }
    const blocked = emitted.emitSkipped || globalDiagnostics.length > 0 ||
      [...diagnosticsByVariant.values()].some((items) => items.length > 0);
    const observations = new Map<string, RuleObservationV1>();
    if (!blocked) {
      for (const variant of prepared) {
        const stat = await lstat(variant.outputPath).catch(() => undefined);
        if (stat === undefined || !stat.isFile() || stat.isSymbolicLink()) {
          return fail("TS_RULE_PROOF_SESSION_OUTPUT_MISSING");
        }
        observations.set(variant.variantId, await observeCompiledTypeScriptRule({
          outputPath: variant.outputPath,
          symbolName: rule.binding.symbol_name,
          bindingId: rule.binding.binding_id,
          bindingSourceSha256: rule.binding.source_ref.sha256,
          cases: rule.cases.cases,
        }));
      }
    }
    if (sha256(await readFile(compilerPath)) !== compilerSha256) {
      return fail("TS_RULE_COMPILER_CHANGED_DURING_SESSION");
    }
    const workspaceEvidence = Object.freeze({
      workspace_id: basename(workspace),
      isolation_scope: "proof-session" as const,
      isolated: true as const,
      symlinks: false as const,
      cleaned: true as const,
    });
    const compilerEvidence = Object.freeze({
      name: "typescript" as const,
      version: ts.version,
      tool_sha256: compilerSha256,
      config_sha256: typeScriptRuleCompilerConfigSha256,
    });
    const sessionDiagnostics = Object.freeze([
      ...normalizeDiagnostics(globalDiagnostics).map((item) => Object.freeze({
        variant_id: null,
        ...item,
      })),
      ...prepared.flatMap((variant) =>
        normalizeDiagnostics(diagnosticsByVariant.get(variant.variantId) ?? []).map((item) =>
          Object.freeze({ variant_id: variant.variantId, ...item }))),
    ]);
    const variants = Object.freeze(prepared.map((variant) => {
      const ownDiagnostics = normalizeDiagnostics([
        ...globalDiagnostics,
        ...(diagnosticsByVariant.get(variant.variantId) ?? []),
      ]);
      const executionDiagnostics = blocked && ownDiagnostics.length === 0
        ? Object.freeze([diagnostic(
            "TS_RULE_PROOF_SESSION_ATOMIC_BLOCKED",
            "another proof-session variant blocked atomic emission",
          )])
        : ownDiagnostics;
      const execution = Object.freeze({
        schema_version: "TypeScriptRuleExecution/v1" as const,
        base_source_sha256: inspection.source_sha256,
        execution_source_sha256: sha256(variant.executionSource),
        mutation_id: variant.mutationId ?? null,
        compiler: compilerEvidence,
        workspace: workspaceEvidence,
        exit_status: blocked ? 1 as const : 0 as const,
        diagnostics: executionDiagnostics,
        observation: observations.get(variant.variantId) ?? null,
        authority_effect: "none" as const,
      });
      return Object.freeze({ variant_id: variant.variantId, execution });
    }));
    return Object.freeze({
      schema_version: "TypeScriptRuleProofSession/v1" as const,
      result: blocked ? "block" as const : "pass" as const,
      workspace: workspaceEvidence,
      compiler: compilerEvidence,
      variants,
      diagnostics: sessionDiagnostics,
      authority_effect: "none" as const,
    });
  } finally {
    await rm(workspace, { recursive: true, force: true });
  }
};

export const executeTypeScriptRule = async (input: Readonly<{
  rule: ValidatedHandle<NormalizedRulePackageV1>;
  baseSource: string;
  executionSource?: string;
  mutationId?: string;
}>): Promise<TypeScriptRuleExecutionV1> => {
  const session = await executeTypeScriptRuleProofSession({
    rule: input.rule,
    baseSource: input.baseSource,
    variants: [Object.freeze({
      variantId: input.mutationId ?? "direct",
      executionSource: input.executionSource,
      mutationId: input.mutationId,
    })],
  });
  return session.variants[0]?.execution ?? fail("TS_RULE_PROOF_SESSION_RESULT_MISSING");
};
