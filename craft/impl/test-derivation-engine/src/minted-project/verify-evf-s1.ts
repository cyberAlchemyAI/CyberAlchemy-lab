import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { dirname, isAbsolute, relative, resolve } from "node:path";
import { pathToFileURL } from "node:url";

import {
  ExactBindingResolutionError,
  resolveExactBinding,
} from "../bindings/index.js";
import { emitEvfS1StrictTests } from "../emit/tests.js";
import {
  assertExactRef,
  assertRuntimeSourcePresent,
  deriveEnforcesObligations,
  exactRef,
  loadEvfS1Bundle,
  type EvfS1Bundle,
} from "./derive.js";
import { executeEnforcesCases, type UnlockRuntime } from "./enforces-execution.js";
import {
  buildNegativeReceipt,
  buildPositiveReceipt,
  receiptDigest,
  verifyReceipt,
  type EvolvableValidationReceipt,
  type NegativeControlReceipt,
} from "./evolvable-validation-receipt.js";
import { decodeBooleanEquality } from "./typed-predicate.js";
import {
  ACCEPTANCE_VECTOR,
  EVF_PATHS,
  EXECUTION_CARDINALITY,
  EvfS1Error,
  fail,
  type EvfFailureCode,
  type ExactRef,
  type GeneratedObligation,
  type KeyDoorOutput,
  type RuntimeObservation,
} from "./types.js";

type MutantContract = {
  mutant_id: string;
  class: "semantic-bypass" | "structural" | "freshness" | "receipt" | "aggregate";
  required_rejection_code: EvfFailureCode;
  receipt_path: string;
};

type ValidationContract = {
  schema_version: "evf.s1-validation-contract/v1";
  contract_id: "evf.SWU-GCP-001.validation.v1";
  required_test_targets: string[];
  mutants: MutantContract[];
};

export interface EvfS1VerificationResult {
  readonly status: "pass";
  readonly swu_id: "SWU-GCP-001";
  readonly mode: "candidate-local-fast-lane";
  readonly acceptance_vector: typeof ACCEPTANCE_VECTOR;
  readonly child_result_id: typeof EXECUTION_CARDINALITY.child_result_id;
  readonly mutant_kills: 16;
  readonly negative_receipts: 16;
  readonly positive_receipt_issued: true;
  readonly release_admission: "not-granted";
  readonly claim_ceiling: "candidate-local-SWU-GCP-001-causal-proof-only";
  readonly evidence_root: string;
}

const DEFAULT_EVIDENCE_ROOT =
  "projects/domainspec-v2/development/evolvable-validation-framework/" +
  "evidence/SWU-GCP-001/attempt-001";

const IMPLEMENTATION_TEST_TARGETS = [
  "projects/domainspec-v2/impl/test-derivation-engine/src/formal/key-door-predicate.test.ts",
  "projects/domainspec-v2/impl/test-derivation-engine/src/bindings/key-door-binding.test.ts",
  "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/key-door-vertical.test.ts",
  "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/enforces-derivation.test.ts",
  "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/enforces-execution.test.ts",
  "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/key-door-receipt.test.ts",
  "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/verify-evf-s1.test.ts",
] as const;

const GENERATED_TEST_TARGET =
  `${DEFAULT_EVIDENCE_ROOT}/generated-tests/key-door-enforces.generated.test.ts`;

function json<T>(path: string): T {
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

function stableBytes(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function findRepositoryRoot(start: string): string {
  let cursor = resolve(start);
  for (;;) {
    if (
      existsSync(resolve(cursor, "AGENTS.md")) &&
      existsSync(resolve(cursor, "projects/domainspec-v2"))
    ) {
      return cursor;
    }
    const parent = dirname(cursor);
    if (parent === cursor) {
      fail("RUNTIME_TARGET_UNADMITTED", "cannot resolve repository root");
    }
    cursor = parent;
  }
}

function moduleSpecifier(fromFile: string, targetFile: string): string {
  let specifier = relative(dirname(fromFile), targetFile).replaceAll("\\", "/");
  if (!specifier.startsWith(".")) specifier = `./${specifier}`;
  return specifier.replace(/\.ts$/, ".js");
}

function writeStable(
  path: string,
  bytes: string,
  created: string[],
): void {
  mkdirSync(dirname(path), { recursive: true });
  if (existsSync(path)) {
    if (readFileSync(path, "utf8") !== bytes) {
      fail("ARTIFACT_STALE", `existing candidate evidence differs: ${path}`);
    }
    return;
  }
  writeFileSync(path, bytes, "utf8");
  created.push(path);
}

function writeStableJson(path: string, value: unknown, created: string[]): void {
  writeStable(path, stableBytes(value), created);
}

export function assertRequiredTestTargets(
  actual: readonly string[],
  required: readonly string[],
): void {
  if (
    actual.length !== required.length ||
    actual.some((path, index) => path !== required[index])
  ) {
    fail("VERIFIER_TARGET_OMITTED", "terminal verifier target list is not exact and ordered");
  }
}

function exactCode(action: () => unknown): EvfFailureCode | "NO_FAILURE" {
  try {
    action();
    return "NO_FAILURE";
  } catch (error) {
    if (error instanceof EvfS1Error) return error.code;
    if (error instanceof ExactBindingResolutionError) return error.code;
    throw error;
  }
}

function assertChildIdentity(
  childResultId: string,
  generatedTestId: string,
  obligationId: string,
  obligation: GeneratedObligation,
): void {
  if (
    childResultId !== EXECUTION_CARDINALITY.child_result_id ||
    generatedTestId !== EXECUTION_CARDINALITY.generated_test_id ||
    obligationId !== obligation.obligation_id
  ) {
    fail("RESULT_ID_MISMATCH", "child result does not join to the generated obligation");
  }
}

function assertionForMutant(input: {
  mutant: MutantContract;
  repoRoot: string;
  bundle: EvfS1Bundle;
  obligation: GeneratedObligation;
  observations: readonly [RuntimeObservation, RuntimeObservation];
  validationRef: ExactRef;
  requiredTargets: readonly string[];
}): () => unknown {
  const { mutant, repoRoot, bundle, obligation, observations, validationRef, requiredTargets } = input;
  const zeroDigest = "0".repeat(64);
  const falseAst = {
    ...bundle.predicate.predicate.ast,
    right: { ...bundle.predicate.predicate.ast.right, value: false },
  };
  const alwaysUnlock: UnlockRuntime = (): KeyDoorOutput => ({
    status: "unlocked",
    door_locked: false,
  });
  const alwaysDeny: UnlockRuntime = (): KeyDoorOutput => ({
    status: "denied",
    door_locked: true,
  });

  switch (mutant.mutant_id) {
    case "M01-predicate-operator-ne":
      return () => decodeBooleanEquality({ ...bundle.predicate.predicate.ast, kind: "ne" });
    case "M02-predicate-literal-false":
      return () => executeEnforcesCases(decodeBooleanEquality(falseAst), bundle.fixtures.cases, undefined);
    case "M03-runtime-always-unlock":
      return () => executeEnforcesCases(bundle.predicate.predicate.ast, bundle.fixtures.cases, alwaysUnlock);
    case "M04-runtime-always-deny":
      return () => executeEnforcesCases(bundle.predicate.predicate.ast, bundle.fixtures.cases, alwaysDeny);
    case "M05-runtime-unlocked-still-locked":
      return () => executeEnforcesCases(
        bundle.predicate.predicate.ast,
        bundle.fixtures.cases,
        () => ({ status: "unlocked", door_locked: true }),
      );
    case "M06-runtime-denied-but-open":
      return () => executeEnforcesCases(
        bundle.predicate.predicate.ast,
        bundle.fixtures.cases,
        () => ({ status: "denied", door_locked: false }),
      );
    case "M07-edge-wrong-target":
      return () => deriveEnforcesObligations(repoRoot, bundle, {
        edge: { ...bundle.binding.edge, target_node_id: "key-and-door.DoorUnlocked" },
      });
    case "M08-edge-direction-reversed":
      return () => deriveEnforcesObligations(repoRoot, bundle, {
        edge: {
          ...bundle.binding.edge,
          source_node_id: bundle.binding.edge.target_node_id,
          target_node_id: bundle.binding.edge.source_node_id,
        },
      });
    case "M09-signature-wrong":
      return () => deriveEnforcesObligations(repoRoot, bundle, {
        signature: {
          source_type: "Operation",
          target_type: "Rule",
          direction: "canonical",
          status: "active",
        },
      });
    case "M10-source-digest-stale":
      return () => assertExactRef(
        repoRoot,
        { ...bundle.binding.lineage_refs.rule_source, sha256: zeroDigest },
        "SOURCE_DIGEST_STALE",
      );
    case "M11-predicate-digest-stale":
      return () => assertExactRef(
        repoRoot,
        { ...bundle.binding.predicate_ref, sha256: zeroDigest },
        "BINDING_STALE",
      );
    case "M12-binding-digest-stale":
      return () => assertExactRef(
        repoRoot,
        { ...bundle.binding.runtime_contract_ref, sha256: zeroDigest },
        "BINDING_STALE",
      );
    case "M13-fixture-digest-stale":
      return () => assertExactRef(
        repoRoot,
        { ...bundle.binding.fixture_ref, sha256: zeroDigest },
        "BINDING_STALE",
      );
    case "M14-result-id-mismatch":
      return () => assertChildIdentity(
        "evf.s1.child-result.wrong.v1",
        EXECUTION_CARDINALITY.generated_test_id,
        obligation.obligation_id,
        obligation,
      );
    case "M15-receipt-digest-tamper":
      return () => {
        const receipt = buildPositiveReceipt({ exactRefs: [validationRef], observations });
        const digest = receiptDigest(receipt);
        const tampered = structuredClone(receipt) as unknown as { acceptance_vector: { mutants_killed: number } };
        tampered.acceptance_vector.mutants_killed = 15;
        verifyReceipt(tampered as unknown as EvolvableValidationReceipt, digest);
      };
    case "M16-verifier-target-omitted":
      return () => assertRequiredTestTargets(requiredTargets.slice(0, -1), requiredTargets);
    default:
      return () => fail("S1_ACCEPTANCE_VECTOR_MISMATCH", `unknown mutant ${mutant.mutant_id}`);
  }
}

function survivorCode(className: MutantContract["class"]): EvfFailureCode {
  if (className === "semantic-bypass") return "SEMANTIC_BYPASS_MUTANT_SURVIVED";
  if (className === "structural") return "STRUCTURAL_MUTANT_SURVIVED";
  if (className === "aggregate") return "S1_ACCEPTANCE_VECTOR_MISMATCH";
  return "STALE_ARTIFACT_MUTANT_SURVIVED";
}

function runMutants(input: {
  contract: ValidationContract;
  repoRoot: string;
  bundle: EvfS1Bundle;
  obligation: GeneratedObligation;
  observations: readonly [RuntimeObservation, RuntimeObservation];
  validationRef: ExactRef;
}): readonly { contract: MutantContract; receipt: NegativeControlReceipt }[] {
  if (input.contract.mutants.length !== 16) {
    fail("S1_ACCEPTANCE_VECTOR_MISMATCH", "validation contract must define sixteen mutants");
  }
  return input.contract.mutants.map((mutant) => {
    const actual = exactCode(assertionForMutant({
      mutant,
      repoRoot: input.repoRoot,
      bundle: input.bundle,
      obligation: input.obligation,
      observations: input.observations,
      validationRef: input.validationRef,
      requiredTargets: input.contract.required_test_targets,
    }));
    if (actual === "NO_FAILURE") {
      fail(survivorCode(mutant.class), `mutant survived: ${mutant.mutant_id}`);
    }
    if (actual !== mutant.required_rejection_code) {
      fail(
        survivorCode(mutant.class),
        `${mutant.mutant_id} rejected with ${actual}, expected ${mutant.required_rejection_code}`,
      );
    }
    const receipt = buildNegativeReceipt({
      mutantId: mutant.mutant_id,
      stableCode: actual,
      exactRefs: [input.validationRef],
    });
    verifyReceipt(receipt);
    return { contract: mutant, receipt };
  });
}

function runGeneratedTest(
  repoRoot: string,
  generatedPath: string,
): { readonly childResultId: string; readonly generatedTestId: string } {
  const binary = resolve(repoRoot, "projects/domainspec-v2/impl/node_modules/.bin/vitest");
  if (!existsSync(binary)) fail("RUNTIME_EXECUTION_FAILED", "local Vitest binary is absent");
  const generatedFromRepo = relative(repoRoot, generatedPath);
  const testRoot =
    generatedFromRepo.startsWith("..") || isAbsolute(generatedFromRepo)
      ? dirname(generatedPath)
      : repoRoot;
  const child = spawnSync(
    binary,
    [
      "run",
      "--root",
      testRoot,
      generatedPath,
      "--reporter=json",
      "--maxWorkers=1",
      "--minWorkers=1",
    ],
    {
      cwd: repoRoot,
      encoding: "utf8",
      timeout: 300_000,
      maxBuffer: 8 * 1024 * 1024,
      env: { ...process.env, NO_COLOR: "1" },
    },
  );
  if (child.error || child.status !== 0) {
    fail(
      "RUNTIME_EXECUTION_FAILED",
      `generated child test failed (${child.status ?? "spawn"}): ${child.stderr || child.stdout}`,
    );
  }
  let report: {
    numTotalTests?: number;
    numPassedTests?: number;
    numFailedTests?: number;
    numPendingTests?: number;
    numTodoTests?: number;
    testResults?: Array<{
      name?: string;
      assertionResults?: Array<{
        ancestorTitles?: unknown;
        title?: unknown;
        status?: unknown;
      }>;
    }>;
  };
  try {
    report = JSON.parse(child.stdout) as typeof report;
  } catch {
    fail("RESULT_ID_MISMATCH", "child Vitest JSON result is unreadable");
  }
  const testResult = report.testResults?.[0];
  const assertion = testResult?.assertionResults?.[0];
  if (
    report.numTotalTests !== 1 ||
    report.numPassedTests !== 1 ||
    report.numFailedTests !== 0 ||
    report.numPendingTests !== 0 ||
    report.numTodoTests !== 0 ||
    report.testResults?.length !== 1 ||
    testResult?.assertionResults?.length !== 1 ||
    resolve(String(testResult.name)) !== resolve(generatedPath) ||
    assertion?.status !== "passed" ||
    !Array.isArray(assertion.ancestorTitles) ||
    assertion.ancestorTitles.length !== 1 ||
    assertion.ancestorTitles[0] !== EXECUTION_CARDINALITY.child_result_id ||
    assertion.title !== EXECUTION_CARDINALITY.generated_test_id
  ) {
    fail("RESULT_ID_MISMATCH", "child Vitest did not return exactly one passing test result");
  }
  return {
    childResultId: assertion.ancestorTitles[0],
    generatedTestId: assertion.title,
  } as { readonly childResultId: string; readonly generatedTestId: string };
}

function validateReceiptFiles(repoRoot: string, paths: readonly string[]): void {
  const schema = resolve(repoRoot, EVF_PATHS.receiptSchema);
  const code = [
    "from pathlib import Path",
    "import json,sys",
    "from jsonschema.validators import validator_for",
    "schema=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))",
    "validator=validator_for(schema)(schema)",
    "[validator.validate(json.loads(Path(p).read_text(encoding='utf-8'))) for p in sys.argv[2:]]",
  ].join("; ");
  const child = spawnSync("python3", ["-c", code, schema, ...paths], {
    cwd: repoRoot,
    encoding: "utf8",
    timeout: 120_000,
    maxBuffer: 4 * 1024 * 1024,
  });
  if (child.error || child.status !== 0) {
    fail("RECEIPT_TAMPERED", `receipt schema validation failed: ${child.stderr || child.stdout}`);
  }
}

function evidencePaths(root: string, negativePaths: readonly string[]): string[] {
  return [
    resolve(root, "executor-receipt.json"),
    resolve(root, "validation-receipt.json"),
    resolve(root, "target-result-inventory.json"),
    resolve(root, "generated-tests/key-door-enforces.generated.test.ts"),
    resolve(root, "positive/evolvable-validation-receipt.json"),
    ...negativePaths,
  ];
}

function receiptPath(repoRoot: string, outputRoot: string, contractPath: string): string {
  if (outputRoot === resolve(repoRoot, DEFAULT_EVIDENCE_ROOT)) return resolve(repoRoot, contractPath);
  return resolve(outputRoot, "negative", contractPath.split("/").at(-1)!);
}

export function runEvfS1Verification(options: {
  readonly repoRoot?: string;
  readonly outputRoot?: string;
} = {}): EvfS1VerificationResult {
  const repoRoot = options.repoRoot ? resolve(options.repoRoot) : findRepositoryRoot(process.cwd());
  const outputRoot = options.outputRoot
    ? (isAbsolute(options.outputRoot) ? options.outputRoot : resolve(repoRoot, options.outputRoot))
    : resolve(repoRoot, DEFAULT_EVIDENCE_ROOT);
  const created: string[] = [];
  try {
    const contractPath = resolve(repoRoot, EVF_PATHS.validationContract);
    const contract = json<ValidationContract>(contractPath);
    if (
      contract.schema_version !== "evf.s1-validation-contract/v1" ||
      contract.contract_id !== "evf.SWU-GCP-001.validation.v1"
    ) {
      fail("TARGET_BASELINE_DRIFT", "validation contract identity is invalid");
    }
    const requiredTargets = [...IMPLEMENTATION_TEST_TARGETS, GENERATED_TEST_TARGET];
    assertRequiredTestTargets(requiredTargets, contract.required_test_targets);

    const bundle = loadEvfS1Bundle(repoRoot);
    const obligations = deriveEnforcesObligations(repoRoot, bundle);
    let binding;
    try {
      binding = resolveExactBinding(
        obligations[0]!.obligation_id,
        [bundle.binding],
        "evf.key-door.binding.v1",
      );
    } catch (error) {
      if (error instanceof ExactBindingResolutionError) fail(error.code, error.message);
      throw error;
    }
    const ast = decodeBooleanEquality(bundle.predicate.predicate.ast);
    const runtimeRef = assertRuntimeSourcePresent(repoRoot, binding);
    const observations = executeEnforcesCases(ast, bundle.fixtures.cases);

    const generatedPath = resolve(outputRoot, "generated-tests/key-door-enforces.generated.test.ts");
    const runtimePath = resolve(repoRoot, binding.runtime_source_binding.path);
    const predicatePath = resolve(
      repoRoot,
      "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/typed-predicate.ts",
    );
    const executionPath = resolve(
      repoRoot,
      "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/enforces-execution.ts",
    );
    const generated = emitEvfS1StrictTests({
      obligationIds: obligations.map((item) => item.obligation_id),
      binding,
      ast,
      cases: bundle.fixtures.cases,
      runtimeModule: moduleSpecifier(generatedPath, runtimePath),
      predicateModule: moduleSpecifier(generatedPath, predicatePath),
      executionModule: moduleSpecifier(generatedPath, executionPath),
    });
    writeStable(generatedPath, generated.file, created);
    const childIdentity = runGeneratedTest(repoRoot, generatedPath);
    assertChildIdentity(
      childIdentity.childResultId,
      childIdentity.generatedTestId,
      obligations[0]!.obligation_id,
      obligations[0]!,
    );

    const executorPath = resolve(outputRoot, "executor-receipt.json");
    const executorReceipt = {
      schema_version: "evf.s1-child-result-envelope/v1",
      child_result_id: EXECUTION_CARDINALITY.child_result_id,
      generated_test_id: generated.testId,
      obligation_id: obligations[0]!.obligation_id,
      status: "pass",
      generated_test_ref: exactRef(repoRoot, relative(repoRoot, generatedPath)),
      runtime_source_ref: runtimeRef,
      runtime_observation_case_ids: EXECUTION_CARDINALITY.runtime_observation_case_ids,
      runtime_function_call_count: 2,
      aggregate_assertion_id: EXECUTION_CARDINALITY.aggregate_assertion_id,
      aggregate_assertion_count: 1,
      release_admission: "not-granted",
    } as const;
    writeStableJson(executorPath, executorReceipt, created);

    const validationRef = exactRef(repoRoot, EVF_PATHS.validationContract);
    const kills = runMutants({
      contract,
      repoRoot,
      bundle,
      obligation: obligations[0]!,
      observations,
      validationRef,
    });
    const negativePaths: string[] = [];
    for (const kill of kills) {
      const path = receiptPath(repoRoot, outputRoot, kill.contract.receipt_path);
      writeStableJson(path, kill.receipt, created);
      negativePaths.push(path);
    }

    const positivePath = resolve(outputRoot, "positive/evolvable-validation-receipt.json");
    const positive = buildPositiveReceipt({
      exactRefs: [
        exactRef(repoRoot, EVF_PATHS.predicate),
        exactRef(repoRoot, EVF_PATHS.fixture),
        exactRef(repoRoot, EVF_PATHS.binding),
        exactRef(repoRoot, EVF_PATHS.runtimeContract),
        exactRef(repoRoot, EVF_PATHS.ospec),
        runtimeRef,
        exactRef(repoRoot, relative(repoRoot, generatedPath)),
        exactRef(repoRoot, relative(repoRoot, executorPath)),
      ],
      observations,
    });
    verifyReceipt(positive);
    writeStableJson(positivePath, positive, created);
    validateReceiptFiles(repoRoot, [...negativePaths, positivePath]);

    const validationPath = resolve(outputRoot, "validation-receipt.json");
    const validationReceipt = {
      schema_version: "evf.s1-candidate-local-validation/v1",
      status: "pass",
      swu_id: "SWU-GCP-001",
      mode: "candidate-local-fast-lane",
      validation_contract_ref: validationRef,
      generated_test_ref: exactRef(repoRoot, relative(repoRoot, generatedPath)),
      executor_receipt_ref: exactRef(repoRoot, relative(repoRoot, executorPath)),
      positive_receipt_ref: exactRef(repoRoot, relative(repoRoot, positivePath)),
      acceptance_vector: ACCEPTANCE_VECTOR,
      mutant_ids: kills.map((entry) => entry.contract.mutant_id),
      stable_codes: kills.map((entry) => entry.receipt.stable_code),
      release_admission: "not-granted",
      claim_ceiling: "candidate-local-SWU-GCP-001-causal-proof-only",
    } as const;
    writeStableJson(validationPath, validationReceipt, created);

    const inventoryPath = resolve(outputRoot, "target-result-inventory.json");
    const allPaths = evidencePaths(outputRoot, negativePaths);
    if (allPaths.length !== 21 || new Set(allPaths).size !== 21) {
      fail("S1_ACCEPTANCE_VECTOR_MISMATCH", "project evidence path denominator is not exactly 21");
    }
    const inventory = {
      schema_version: "evf.s1-target-result-inventory/v1",
      swu_id: "SWU-GCP-001",
      target_count: 21,
      self: {
        path: relative(repoRoot, inventoryPath),
        digest_policy: "self-path-recorded-self-digest-excluded",
      },
      targets: allPaths
        .filter((path) => path !== inventoryPath)
        .map((path) => exactRef(repoRoot, relative(repoRoot, path))),
      status: "pass",
      release_admission: "not-granted",
    } as const;
    writeStableJson(inventoryPath, inventory, created);

    return {
      status: "pass",
      swu_id: "SWU-GCP-001",
      mode: "candidate-local-fast-lane",
      acceptance_vector: ACCEPTANCE_VECTOR,
      child_result_id: EXECUTION_CARDINALITY.child_result_id,
      mutant_kills: 16,
      negative_receipts: 16,
      positive_receipt_issued: true,
      release_admission: "not-granted",
      claim_ceiling: "candidate-local-SWU-GCP-001-causal-proof-only",
      evidence_root: relative(repoRoot, outputRoot),
    };
  } catch (error) {
    for (const path of created.reverse()) {
      if (existsSync(path) && statSync(path).isFile()) rmSync(path);
    }
    throw error;
  }
}

function outputRootArg(argv: readonly string[]): string | undefined {
  const index = argv.indexOf("--output-root");
  return index >= 0 ? argv[index + 1] : undefined;
}

const invokedDirectly =
  process.argv[1] !== undefined &&
  import.meta.url === pathToFileURL(resolve(process.argv[1])).href;

if (invokedDirectly) {
  try {
    const result = runEvfS1Verification({ outputRoot: outputRootArg(process.argv.slice(2)) });
    process.stdout.write(`${JSON.stringify(result)}\n`);
  } catch (error) {
    const failure =
      error instanceof EvfS1Error
        ? {
            status: "blocked-or-failed",
            code: error.code,
            phase: error.phase,
            artifact_refs: [],
            positive_receipt_issued: false,
            message: error.message,
          }
        : {
            status: "blocked-or-failed",
            code: "S1_ACCEPTANCE_VECTOR_MISMATCH",
            phase: "aggregate",
            artifact_refs: [],
            positive_receipt_issued: false,
            message: error instanceof Error ? error.message : String(error),
          };
    process.stderr.write(`${JSON.stringify(failure)}\n`);
    process.exitCode = error instanceof EvfS1Error ? error.exitCode : 1;
  }
}
