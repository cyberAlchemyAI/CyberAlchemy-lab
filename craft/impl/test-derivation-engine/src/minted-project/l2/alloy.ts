import { canonicalJson } from "./canonical-json.js";
import { translateAlloy } from "./translate-alloy.js";
import { fail, type ExactRef, type FactProjection, type NormalizedOutcome, type PropertyDefinition } from "./types.js";

export type AlloyCliResult = {
  readonly command_label: "NoViolation";
  readonly outcome: "sat" | "unsat" | "unknown";
  readonly solution_count: number | null;
  readonly counterexample: unknown | null;
  readonly raw: unknown;
};

export function alloyArgv(
  javaExecutable: string,
  alloyJar: string,
  outputPath: string,
  modelPath: string,
): readonly string[] {
  if ([javaExecutable, alloyJar, outputPath, modelPath].some((entry) => entry.length === 0)) {
    fail("PROVIDER_INPUT_DIGEST_MISMATCH", "execution", "empty Alloy invocation field");
  }
  return [
    javaExecutable,
    "-jar",
    alloyJar,
    "exec",
    "-q",
    "-f",
    "-s",
    "sat4j",
    "-t",
    "json",
    "-o",
    outputPath,
    "-c",
    "NoViolation",
    modelPath,
  ];
}

function record(value: unknown, label = "Alloy value"): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", `${label} must be a JSON object`);
  }
  return value as Record<string, unknown>;
}

export type AlloySolutionFile = {
  readonly name: string;
  readonly bytes: string;
};

export function parseAlloyJson(
  bytes: string,
  solutionFiles: readonly AlloySolutionFile[],
  expected: {
    readonly source: string;
    readonly scopes: readonly string[];
    readonly solver: "sat4j";
  },
): AlloyCliResult {
  let parsed: unknown;
  try {
    parsed = JSON.parse(bytes);
  } catch {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "Alloy CLI output is not JSON");
  }
  const value = record(parsed, "Alloy receipt");
  if (value.solver !== expected.solver) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "Alloy receipt solver is not exact Sat4j");
  }
  const commands = record(value.commands, "Alloy commands");
  if (Object.keys(commands).length !== 1 || !("NoViolation" in commands)) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "Alloy receipt command denominator is not exact");
  }
  const command = record(commands.NoViolation, "Alloy NoViolation command");
  if (
    command.name !== "NoViolation" ||
    command.type !== "check" ||
    command.source !== expected.source ||
    canonicalJson(command.scopes) !== canonicalJson(expected.scopes)
  ) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "Alloy command source, scope, or kind drifted");
  }
  const embedded = command.solution;
  if (embedded !== undefined && !Array.isArray(embedded)) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "Alloy receipt solution field is malformed");
  }
  if (Array.isArray(embedded) && embedded.length === 0) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "Alloy UNSAT evidence must omit the solution field");
  }
  const embeddedSolutions = (embedded ?? []) as unknown[];
  const sortedFiles = [...solutionFiles].sort((left, right) => left.name.localeCompare(right.name));
  sortedFiles.forEach((file, index) => {
    if (file.name !== `NoViolation-solution-${index}.json`) {
      fail("PROVIDER_OUTPUT_INVALID", "mapping", "Alloy solution-file denominator is not exact");
    }
  });
  if (embeddedSolutions.length !== sortedFiles.length) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "Alloy embedded and file solution counts disagree");
  }
  const parsedFiles = sortedFiles.map((file) => {
    try {
      return record(JSON.parse(file.bytes), file.name);
    } catch (error) {
      if (error instanceof Error && "code" in error) throw error;
      fail("PROVIDER_OUTPUT_INVALID", "mapping", `Alloy solution file is invalid JSON: ${file.name}`);
    }
  });
  for (let index = 0; index < embeddedSolutions.length; index += 1) {
    const summary = record(embeddedSolutions[index], "embedded Alloy solution");
    const file = parsedFiles[index]!;
    const instanceValues = (value: unknown): readonly Record<string, unknown>[] => {
      if (!Array.isArray(value)) {
        fail("PROVIDER_OUTPUT_INVALID", "mapping", "Alloy solution instances are malformed");
      }
      const values = value.map((entry) =>
        record(record(entry, "Alloy solution instance").values, "Alloy solution values")
      );
      if (values.length === 0 || values.every((entry) => Object.keys(entry).length === 0)) {
        fail("PROVIDER_OUTPUT_INVALID", "mapping", "Alloy SAT solution evidence is empty");
      }
      return values;
    };
    if (
      summary.duration !== file.duration ||
      summary.utctime !== file.utctime ||
      canonicalJson(instanceValues(summary.instances)) !==
        canonicalJson(instanceValues(file.instances))
    ) {
      fail("PROVIDER_OUTPUT_INVALID", "mapping", "Alloy embedded solution and file evidence disagree");
    }
  }
  const explicitUnknown = command.status === "unknown";
  const rawOutcome = explicitUnknown
    ? "unknown"
    : embeddedSolutions.length > 0
      ? "sat"
      : "unsat";
  const solutionCount = explicitUnknown ? null : embeddedSolutions.length;
  const counterexample = rawOutcome === "sat" ? parsedFiles : null;
  return {
    command_label: "NoViolation",
    outcome: rawOutcome,
    solution_count: solutionCount,
    counterexample,
    raw: { receipt: parsed, solution_files: parsedFiles },
  };
}

export function mapAlloyOutcome(outcome: AlloyCliResult["outcome"]): NormalizedOutcome {
  if (outcome === "sat") return "counterexample";
  if (outcome === "unsat") return "no-counterexample";
  return "unresolved";
}

export function assertExactInstanceModel(
  model: string,
  projection: FactProjection,
  property: PropertyDefinition,
): void {
  const expected = translateAlloy(projection, property).model;
  if (model !== expected) {
    fail("PROVIDER_SCOPE_INVALID", "translation", "Alloy model is not the exact generated instance");
  }
}

export function alloyNativeResult(
  result: AlloyCliResult,
  scope: Readonly<Record<string, unknown>>,
  scopeDigest: string,
  cliReceiptRef: ExactRef,
  evidenceRef: ExactRef | null,
) {
  if (result.outcome === "sat" && evidenceRef === null) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "SAT result requires counterexample exact ref");
  }
  if (result.outcome !== "sat" && evidenceRef !== null) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "non-SAT result cannot claim counterexample exact ref");
  }
  return {
    kind: "alloy-command" as const,
    command_kind: "check" as const,
    command_label: "NoViolation" as const,
    scope,
    scope_digest: scopeDigest,
    outcome: result.outcome,
    instance_or_counterexample_ref: evidenceRef,
    solution_count: result.solution_count,
    cli_receipt_ref: cliReceiptRef,
  };
}

export function typedAlloyEvidence(result: AlloyCliResult): Readonly<Record<string, unknown>> {
  return result.outcome === "sat"
    ? { present: true, command_label: "NoViolation", counterexample: result.counterexample }
    : { present: false, command_label: "NoViolation", reason: result.outcome };
}

export function sameAlloyResult(left: AlloyCliResult, right: AlloyCliResult): boolean {
  return canonicalJson(left) === canonicalJson(right);
}
