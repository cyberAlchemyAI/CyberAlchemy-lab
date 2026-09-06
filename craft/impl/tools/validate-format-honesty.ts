/**
 * validate-format-honesty.ts — DomainSpec v2 serialization-format honesty checker.
 *
 * Invariant: a file's extension must predict the parser that succeeds on it.
 *
 *   .yml / .yaml that parses as JSON  -> VIOLATION (json-content-yaml-name)
 *   .json that fails to parse as JSON -> VIOLATION (broken-json)
 *
 * Deliberately requires NO YAML parser. Both violation classes are decidable with
 * JSON.parse alone, which keeps impl/ at zero runtime dependencies. This matters:
 * the defect that motivated this checker (2026-08-19) was produced by a reader that
 * hand-parsed YAML after a failed JSON.parse and silently returned wrong data.
 *
 * A .yml that fails JSON.parse is NOT inspected further. This checker asserts name
 * honesty, never YAML validity — that would need the parser it refuses to add.
 *
 * With --baseline, current findings are acknowledged only when their path and kind
 * exactly match the baseline. Added, removed, or reclassified findings are drift.
 * Without --baseline, every finding remains a strict violation.
 *
 * Usage:
 *   tsx tools/validate-format-honesty.ts
 *   tsx tools/validate-format-honesty.ts --report
 *   tsx tools/validate-format-honesty.ts --json
 *   tsx tools/validate-format-honesty.ts --root <dir>
 *   tsx tools/validate-format-honesty.ts --baseline <file>
 *
 * Exit: 0 honest/exact baseline · 4 violations or baseline drift ·
 *       22 unreadable root · 23 invalid baseline
 */
import { readdirSync, readFileSync, statSync, existsSync } from "node:fs";
import { extname, isAbsolute, join, relative, resolve } from "node:path";

/** Excluded from the governed surface. Declared, not hidden: changing this changes the count. */
const EXCLUDED_SEGMENTS = [
  "node_modules", ".git",
  "refinement-runs", "governance-sidecar", "goal-runs", "session-evidence",
  "runs", "staged", "projections", "material", "preimages", "postimages",
];

const BASELINE_SCHEMA = "domainspec.format-honesty-baseline.v1";
const BASELINE_COMPARISON = "exact-finding-set";
const BASELINE_PATH_BASE = "scan-root-relative-posix";
const VIOLATION_KINDS = ["json-content-yaml-name", "broken-json"] as const;

export type ViolationKind = typeof VIOLATION_KINDS[number];
export type Violation = { path: string; kind: ViolationKind; detail: string };
export type Report = {
  root: string;
  scanned: number;
  violations: Violation[];
  excludedSegments: string[];
  ignoreMarker: string;
};
export type BaselineFinding = Pick<Violation, "path" | "kind">;
export type Baseline = {
  schemaVersion: typeof BASELINE_SCHEMA;
  comparison: typeof BASELINE_COMPARISON;
  pathBase: typeof BASELINE_PATH_BASE;
  expectedCount: number;
  findings: BaselineFinding[];
};
export type ReclassifiedFinding = {
  path: string;
  baselineKind: ViolationKind;
  actualKind: ViolationKind;
};
export type Evaluation = {
  mode: "strict" | "baseline";
  exactMatch: boolean;
  exitCode: 0 | 4;
  acknowledged: Violation[];
  added: Violation[];
  removed: BaselineFinding[];
  reclassified: ReclassifiedFinding[];
};

const getArg = (flag: string): string | undefined => {
  const i = process.argv.indexOf(flag);
  return i >= 0 ? process.argv[i + 1] : undefined;
};

function isExcluded(rel: string): boolean {
  return rel.split("/").some((seg) => EXCLUDED_SEGMENTS.includes(seg));
}

/**
 * A directory containing this marker is skipped with its whole subtree. Used for
 * deliberately malformed test data. The marker is a real file in the repository,
 * so an exclusion is visible where it applies instead of hidden in this source.
 */
const IGNORE_MARKER = ".format-honesty-ignore";

function walk(root: string, dir: string, out: string[]): void {
  if (existsSync(join(dir, IGNORE_MARKER))) return;
  for (const entry of readdirSync(dir)) {
    const abs = join(dir, entry);
    const rel = relative(root, abs);
    if (isExcluded(rel)) continue;
    let st;
    try { st = statSync(abs); } catch { continue; }
    if (st.isDirectory()) walk(root, abs, out);
    else if (st.isFile()) out.push(abs);
  }
}

export function scan(root: string): Report {
  const files: string[] = [];
  walk(root, root, files);
  const violations: Violation[] = [];
  let scanned = 0;

  for (const abs of files) {
    const ext = extname(abs).toLowerCase();
    if (ext !== ".yml" && ext !== ".yaml" && ext !== ".json") continue;
    scanned++;
    const rel = relative(root, abs).split("\\").join("/");
    let raw: string;
    try { raw = readFileSync(abs, "utf8"); } catch { continue; }

    let parsesAsJson = true;
    try { JSON.parse(raw); } catch { parsesAsJson = false; }

    if ((ext === ".yml" || ext === ".yaml") && parsesAsJson) {
      violations.push({ path: rel, kind: "json-content-yaml-name",
        detail: `content parses as JSON but the name says ${ext}; rename to .json` });
    } else if (ext === ".json" && !parsesAsJson) {
      violations.push({ path: rel, kind: "broken-json",
        detail: "name says .json but content does not parse as JSON" });
    }
  }
  violations.sort((a, b) => a.path.localeCompare(b.path));
  return { root, scanned, violations, excludedSegments: EXCLUDED_SEGMENTS, ignoreMarker: IGNORE_MARKER };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function assertExactKeys(value: Record<string, unknown>, expected: readonly string[], where: string): void {
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (actual.length !== wanted.length || actual.some((key, index) => key !== wanted[index])) {
    throw new Error(`${where} must contain exactly: ${wanted.join(", ")}`);
  }
}

function parseBaselineFinding(value: unknown, index: number): BaselineFinding {
  if (!isRecord(value)) throw new Error(`baseline findings[${index}] must be an object`);
  assertExactKeys(value, ["path", "kind"], `baseline findings[${index}]`);
  const path = value.path;
  const kind = value.kind;
  if (typeof path !== "string" || path.length === 0 || isAbsolute(path) || path.includes("\\")) {
    throw new Error(`baseline findings[${index}].path must be a nonempty scan-root-relative POSIX path`);
  }
  if (path.split("/").some((segment) => segment === "" || segment === "." || segment === "..")) {
    throw new Error(`baseline findings[${index}].path must be normalized and may not traverse`);
  }
  if (!VIOLATION_KINDS.includes(kind as ViolationKind)) {
    throw new Error(`baseline findings[${index}].kind is not a supported violation kind`);
  }
  if (kind === "json-content-yaml-name" && !/\.ya?ml$/i.test(path)) {
    throw new Error(`baseline findings[${index}] kind does not match its extension`);
  }
  if (kind === "broken-json" && !/\.json$/i.test(path)) {
    throw new Error(`baseline findings[${index}] kind does not match its extension`);
  }
  return { path, kind: kind as ViolationKind };
}

export function parseBaseline(value: unknown): Baseline {
  if (!isRecord(value)) throw new Error("baseline must be an object");
  assertExactKeys(
    value,
    ["schemaVersion", "comparison", "pathBase", "expectedCount", "findings"],
    "baseline",
  );
  if (value.schemaVersion !== BASELINE_SCHEMA) {
    throw new Error(`baseline schemaVersion must be ${BASELINE_SCHEMA}`);
  }
  if (value.comparison !== BASELINE_COMPARISON) {
    throw new Error(`baseline comparison must be ${BASELINE_COMPARISON}`);
  }
  if (value.pathBase !== BASELINE_PATH_BASE) {
    throw new Error(`baseline pathBase must be ${BASELINE_PATH_BASE}`);
  }
  if (!Number.isSafeInteger(value.expectedCount) || (value.expectedCount as number) < 0) {
    throw new Error("baseline expectedCount must be a nonnegative safe integer");
  }
  if (!Array.isArray(value.findings)) throw new Error("baseline findings must be an array");
  const findings = value.findings.map(parseBaselineFinding);
  if (value.expectedCount !== findings.length) {
    throw new Error(`baseline expectedCount ${value.expectedCount} does not equal findings length ${findings.length}`);
  }
  const seenPaths = new Set<string>();
  for (let index = 0; index < findings.length; index++) {
    const finding = findings[index]!;
    if (seenPaths.has(finding.path)) throw new Error(`duplicate baseline path: ${finding.path}`);
    seenPaths.add(finding.path);
    if (index > 0 && findings[index - 1]!.path.localeCompare(finding.path) >= 0) {
      throw new Error("baseline findings must be strictly path-sorted");
    }
  }
  return {
    schemaVersion: BASELINE_SCHEMA,
    comparison: BASELINE_COMPARISON,
    pathBase: BASELINE_PATH_BASE,
    expectedCount: value.expectedCount as number,
    findings,
  };
}

export function loadBaseline(path: string): Baseline {
  let raw: string;
  try { raw = readFileSync(path, "utf8"); }
  catch (error) { throw new Error(`cannot read baseline ${path}: ${(error as Error).message}`); }
  let value: unknown;
  try { value = JSON.parse(raw); }
  catch (error) { throw new Error(`cannot parse baseline ${path}: ${(error as Error).message}`); }
  return parseBaseline(value);
}

export function evaluate(report: Report, baseline?: Baseline): Evaluation {
  if (!baseline) {
    const exactMatch = report.violations.length === 0;
    return {
      mode: "strict",
      exactMatch,
      exitCode: exactMatch ? 0 : 4,
      acknowledged: [],
      added: report.violations,
      removed: [],
      reclassified: [],
    };
  }

  const expected = new Map(baseline.findings.map((finding) => [finding.path, finding]));
  const actual = new Map(report.violations.map((finding) => [finding.path, finding]));
  const acknowledged: Violation[] = [];
  const added: Violation[] = [];
  const removed: BaselineFinding[] = [];
  const reclassified: ReclassifiedFinding[] = [];

  for (const finding of report.violations) {
    const baselineFinding = expected.get(finding.path);
    if (!baselineFinding) added.push(finding);
    else if (baselineFinding.kind === finding.kind) acknowledged.push(finding);
    else reclassified.push({
      path: finding.path,
      baselineKind: baselineFinding.kind,
      actualKind: finding.kind,
    });
  }
  for (const finding of baseline.findings) {
    if (!actual.has(finding.path)) removed.push(finding);
  }

  const exactMatch =
    acknowledged.length === baseline.expectedCount &&
    added.length === 0 &&
    removed.length === 0 &&
    reclassified.length === 0;
  return {
    mode: "baseline",
    exactMatch,
    exitCode: exactMatch ? 0 : 4,
    acknowledged,
    added,
    removed,
    reclassified,
  };
}

function main(): void {
  const root = resolve(getArg("--root") ?? process.cwd());
  if (!existsSync(root)) {
    console.error(`validate-format-honesty: root not found: ${root}`);
    process.exit(22);
  }

  const baselineArg = getArg("--baseline");
  const baselinePath = baselineArg ? resolve(process.cwd(), baselineArg) : undefined;
  let baseline: Baseline | undefined;
  if (baselinePath) {
    try { baseline = loadBaseline(baselinePath); }
    catch (error) {
      console.error(`validate-format-honesty: invalid baseline: ${(error as Error).message}`);
      process.exit(23);
    }
  }

  const report = scan(root);
  const result = evaluate(report, baseline);
  const asJson = process.argv.includes("--json");
  const full = process.argv.includes("--report");

  if (asJson) {
    console.log(JSON.stringify({
      ...report,
      verdict: {
        mode: result.mode,
        exactMatch: result.exactMatch,
        exitCode: result.exitCode,
      },
      baseline: baseline && baselinePath ? {
        path: relative(process.cwd(), baselinePath) || ".",
        schemaVersion: baseline.schemaVersion,
        expectedCount: baseline.expectedCount,
        acknowledged: result.acknowledged,
        added: result.added,
        removed: result.removed,
        reclassified: result.reclassified,
      } : null,
    }, null, 1));
  } else {
    console.log(`format honesty: scanned ${report.scanned} serialization files under ${relative(process.cwd(), root) || "."}`);
    if (baseline) {
      console.log(`  ${result.acknowledged.length} acknowledged baseline findings`);
      if (result.exactMatch) console.log("  exact baseline match — no added, removed, or reclassified findings");
      else {
        console.log(`  baseline drift: ${result.added.length} added, ${result.removed.length} removed, ${result.reclassified.length} reclassified`);
        if (full) {
          for (const finding of result.added) console.log(`  added         ${finding.kind}  ${finding.path}`);
          for (const finding of result.removed) console.log(`  removed       ${finding.kind}  ${finding.path}`);
          for (const finding of result.reclassified) {
            console.log(`  reclassified  ${finding.baselineKind} -> ${finding.actualKind}  ${finding.path}`);
          }
        } else console.log("  (re-run with --report to list drift)");
      }
    } else if (report.violations.length === 0) {
      console.log("  no violations — every extension predicts its parser");
    } else {
      const byKind = new Map<string, number>();
      for (const violation of report.violations) {
        byKind.set(violation.kind, (byKind.get(violation.kind) ?? 0) + 1);
      }
      for (const [kind, count] of byKind) console.log(`  ${count} x ${kind}`);
      if (full) {
        console.log();
        for (const violation of report.violations) console.log(`  ${violation.kind}  ${violation.path}`);
      } else console.log("  (re-run with --report to list them)");
    }
  }
  process.exit(result.exitCode);
}

if (process.argv[1] && import.meta.url === `file://${resolve(process.argv[1])}`) main();
