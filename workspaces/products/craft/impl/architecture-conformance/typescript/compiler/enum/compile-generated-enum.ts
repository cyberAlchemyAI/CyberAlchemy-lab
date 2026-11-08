import { createHash } from "node:crypto";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { basename, dirname, join, relative, resolve } from "node:path";
import { pathToFileURL } from "node:url";

import ts from "typescript";

import type {
  CompileExpectation,
  CompileResult,
} from "../../../realization/contracts/compile-result.js";
import type { GeneratedSource } from "../../../realization/contracts/generated-source.js";
import type { TypeScriptTargetBinding } from "../../../realization/contracts/typescript-target-binding.js";
import { deriveEnumTypeWitness } from "./derive-type-witness.js";

type CompileInput = Readonly<{
  repositoryRoot: string;
  generated: GeneratedSource;
  binding: TypeScriptTargetBinding;
  expectedTypeValues?: readonly string[];
}>;

const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const config = {
  target: "ES2022",
  module: "NodeNext",
  moduleResolution: "NodeNext",
  strict: true,
  skipLibCheck: true,
  noEmitOnError: true,
} as const;
export const typescriptCompilerConfigSha256 = sha256(JSON.stringify(config));

export const getTypeScriptCompileExpectation = async (): Promise<CompileExpectation> => {
  const compilerPath = createRequire(import.meta.url).resolve("typescript");
  const compilerBytes = await readFile(compilerPath);
  return Object.freeze({
    compiler: Object.freeze({
      name: "typescript" as const,
      version: ts.version,
      tool_sha256: sha256(compilerBytes),
      config_sha256: typescriptCompilerConfigSha256,
    }),
  });
};

const normalizedDiagnostics = (diagnostics: readonly ts.Diagnostic[]): readonly Readonly<{
  code: string;
  message: string;
}>[] => diagnostics.map((item) => Object.freeze({
  code: `TS${item.code}`,
  message: ts.flattenDiagnosticMessageText(item.messageText, " ")
    .replaceAll(/\s+/gu, " ").trim(),
})).sort((left, right) => left.code.localeCompare(right.code));

export const compileGeneratedEnum = async (input: CompileInput): Promise<CompileResult> => {
  const repositoryRoot = resolve(input.repositoryRoot);
  const providerPath = resolve(repositoryRoot, input.binding.provider_ref.path);
  if (!providerPath.startsWith(`${repositoryRoot}/`)) {
    throw Object.assign(new Error("ARCH_ENUM_COMPILE_PROVIDER_PATH_INVALID"), {
      code: "ARCH_ENUM_COMPILE_PROVIDER_PATH_INVALID",
    });
  }
  const providerSource = await readFile(providerPath, "utf8");
  if (sha256(providerSource) !== input.binding.provider_ref.sha256) {
    throw Object.assign(new Error("ARCH_ENUM_COMPILE_PROVIDER_STALE"), {
      code: "ARCH_ENUM_COMPILE_PROVIDER_STALE",
    });
  }
  if (sha256(input.generated.source) !== input.generated.manifest.source_sha256) {
    throw Object.assign(new Error("ARCH_ENUM_COMPILE_SOURCE_STALE"), {
      code: "ARCH_ENUM_COMPILE_SOURCE_STALE",
    });
  }
  const workspace = await mkdtemp(join(tmpdir(), "domainspec-enum-compile-"));
  try {
  const sourcePath = resolve(workspace, input.binding.module_path);
  const providerTarget = resolve(workspace, "runtime/enum/index.ts");
  const outputRoot = resolve(workspace, "dist");
  if (!sourcePath.startsWith(`${workspace}/`) || !providerTarget.startsWith(`${workspace}/`)) {
    await rm(workspace, { recursive: true, force: true });
    throw Object.assign(new Error("ARCH_ENUM_COMPILE_WORKSPACE_ESCAPE"), {
      code: "ARCH_ENUM_COMPILE_WORKSPACE_ESCAPE",
    });
  }
  await Promise.all([
    mkdir(dirname(sourcePath), { recursive: true }),
    mkdir(dirname(providerTarget), { recursive: true }),
  ]);
  await Promise.all([
    writeFile(sourcePath, input.generated.source, { encoding: "utf8", flag: "wx" }),
    writeFile(providerTarget, providerSource, { encoding: "utf8", flag: "wx" }),
    writeFile(resolve(workspace, "package.json"), '{"type":"module"}\n', { flag: "wx" }),
  ]);
  const rootNames = [sourcePath, providerTarget];
  let witnessSourceSha256: string | null = null;
  const expectedUnion = input.expectedTypeValues === undefined
    ? []
    : [...input.expectedTypeValues].sort(compareUtf8);
  if (input.expectedTypeValues !== undefined) {
    const sourceFromWitness = `./${relative(workspace, sourcePath).replaceAll("\\", "/").replace(/\.ts$/u, ".js")}`;
    const witness = deriveEnumTypeWitness(
      sourceFromWitness,
      input.binding.export_name,
      input.binding.type_name,
      input.expectedTypeValues,
    );
    const witnessPath = resolve(workspace, "type-witness.ts");
    await writeFile(witnessPath, witness.source, { encoding: "utf8", flag: "wx" });
    rootNames.push(witnessPath);
    witnessSourceSha256 = witness.sha256;
  }
  const compilerOptions: ts.CompilerOptions = {
    target: ts.ScriptTarget.ES2022,
    module: ts.ModuleKind.NodeNext,
    moduleResolution: ts.ModuleResolutionKind.NodeNext,
    strict: true,
    skipLibCheck: true,
    noEmitOnError: true,
    rootDir: workspace,
    outDir: outputRoot,
  };
  const program = ts.createProgram(rootNames, compilerOptions);
  const preEmit = ts.getPreEmitDiagnostics(program);
  const emitted = preEmit.length === 0 ? program.emit() : { emitSkipped: true, diagnostics: [] };
  const diagnostics = normalizedDiagnostics([...preEmit, ...emitted.diagnostics]);
  let runtimeValues: string[] = [];
  let runtimeFrozen = false;
  if (diagnostics.length === 0 && !emitted.emitSkipped) {
    const outputPath = resolve(outputRoot, relative(workspace, sourcePath)).replace(/\.ts$/u, ".js");
    const module = await import(`${pathToFileURL(outputPath).href}?run=${Date.now()}`) as Record<string, unknown>;
    const runtimeEnum = module[input.binding.export_name];
    if (runtimeEnum !== null && typeof runtimeEnum === "object") {
      runtimeValues = Object.values(runtimeEnum as Record<string, string>).sort(compareUtf8);
      runtimeFrozen = Object.isFrozen(runtimeEnum);
    }
  }
  const compileExpectation = await getTypeScriptCompileExpectation();
  const result: CompileResult = {
    schema_version: "CompileResult/v1",
    source_sha256: input.generated.manifest.source_sha256,
    provider_sha256: input.binding.provider_ref.sha256,
    compiler: {
      ...compileExpectation.compiler,
    },
    workspace: {
      workspace_id: basename(workspace),
      isolated: true,
      symlinks: false,
      cleaned: true,
    },
    exit_status: diagnostics.length === 0 && !emitted.emitSkipped ? 0 : 1,
    diagnostics,
    type_witness: {
      mode: input.expectedTypeValues === undefined ? "compile-only" : "definition-exact",
      expected_union: expectedUnion,
      source_sha256: witnessSourceSha256,
      passed: diagnostics.length === 0,
    },
    runtime_values: runtimeValues,
    runtime_frozen: runtimeFrozen,
    authority_effect: "none",
  };
  await rm(workspace, { recursive: true, force: false });
  return Object.freeze(result);
  } catch (error) {
    await rm(workspace, { recursive: true, force: true });
    throw error;
  }
};
