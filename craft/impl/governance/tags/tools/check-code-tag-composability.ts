#!/usr/bin/env tsx

// @ts-nocheck

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  loadRelationshipAuthority,
  type LoadedRelationshipAuthority,
  type RelationshipSignature,
} from "../../../tools/lib/relationship-signatures";
import { normalizeTypeName, toRelative } from "./lib/code-tag-rules";
import type {
  ExtractedTag,
  ExtractionOutput,
  Mode,
  Severity,
  TagIssue,
} from "./lib/code-tag-types";

type ComposabilityRule = {
  edge: string;
  fromType: string;
  toType: string;
  direction: "target-calls-source" | "source-calls-target";
  code: string;
  severity: Severity;
  expectation: string;
};

type CallSemantics = {
  direction: ComposabilityRule["direction"];
  code: string | ((targetType: string) => string);
  severity: Severity;
  expectation: (sourceType: string, targetType: string) => string;
};

type RelationshipStatusEntry = {
  id: string;
  replacement?: string;
  reason?: string;
};

const callSemanticsByEdge = new Map<string, CallSemantics>([
  [
    "enforces",
    {
      direction: "target-calls-source",
      code: "CT-COMP-001",
      severity: "HIGH",
      expectation: (_sourceType, targetType) =>
        `${targetType} calls its enforcing rule`,
    },
  ],
  [
    "calculates",
    {
      direction: "target-calls-source",
      code: "CT-COMP-002",
      severity: "HIGH",
      expectation: (_sourceType, targetType) =>
        `${targetType} calls its calculation`,
    },
  ],
  [
    "applies",
    {
      direction: "target-calls-source",
      code: "CT-COMP-003",
      severity: "MEDIUM",
      expectation: (_sourceType, targetType) =>
        `${targetType} calls its policy`,
    },
  ],
  [
    "exposes",
    {
      direction: "source-calls-target",
      code: (targetType) =>
        targetType === "query" ? "CT-COMP-005" : "CT-COMP-004",
      severity: "HIGH",
      expectation: (_sourceType, targetType) =>
        `Interface calls exposed ${targetType}`,
    },
  ],
  [
    "mutates",
    {
      direction: "source-calls-target",
      code: "CT-COMP-006",
      severity: "HIGH",
      expectation: (_sourceType, targetType) =>
        `Binding calls target ${targetType}`,
    },
  ],
  [
    "fetches",
    {
      direction: "source-calls-target",
      code: "CT-COMP-007",
      severity: "HIGH",
      expectation: (_sourceType, targetType) =>
        `Binding calls target ${targetType}`,
    },
  ],
  [
    "orchestrates",
    {
      direction: "source-calls-target",
      code: "CT-COMP-008",
      severity: "HIGH",
      expectation: (_sourceType, targetType) =>
        `Workflow calls orchestrated ${targetType}`,
    },
  ],
]);

const args = process.argv.slice(2);
const mode = (getArg("--mode") || "strict") as Mode;
const inputPath = resolve(
  process.cwd(),
  getArg("--input") || "governance/tags/code-tags.json",
);
const outputPath = getArg("--output")
  ? resolve(process.cwd(), getArg("--output") || "")
  : null;
const jsonOnly = hasFlag("--json");
const relationshipAuthorityPath = resolve(
  process.cwd(),
  getArg("--relationships") || "../definitions/relationships/relationships.yml",
);

if (!existsSync(inputPath)) {
  fail([
    issue(
      "CT-COMP-000",
      "CRITICAL",
      `Input not found: ${toRelative(inputPath)}`,
      toRelative(inputPath),
      1,
    ),
  ]);
}

let loadedRelationships: LoadedRelationshipAuthority;
try {
  loadedRelationships = loadRelationshipAuthority(relationshipAuthorityPath);
} catch (error) {
  fail([
    issue(
      "CT-COMP-013",
      "CRITICAL",
      String(error),
      toRelative(relationshipAuthorityPath),
      1,
    ),
  ]);
}

const { rulesByEdge, unsupportedActiveSignatures } =
  buildDynamicRules(loadedRelationships);
const generatedById = loadedRelationships.generatedViewsById;
const deprecatedById = toStatusMap(
  loadedRelationships.authority.deprecated as RelationshipStatusEntry[] | undefined,
);
const deferredById = toStatusMap(
  loadedRelationships.authority.deferred as RelationshipStatusEntry[] | undefined,
);

const extraction = readExtraction(inputPath);
const rootPath = getRootPath(extraction);
const tags = extraction.tags;

const conceptToTags = new Map<string, ExtractedTag[]>();
for (const tag of tags) {
  const id = (tag.concept.id || "").trim();
  if (!id) {
    continue;
  }

  const existing = conceptToTags.get(id) || [];
  existing.push(tag);
  conceptToTags.set(id, existing);
}

let checks = 0;
let passedChecks = 0;
const issues: TagIssue[] = [];
const sourceCache = new Map<string, string>();

for (const sourceTag of tags) {
  const sourceType = normalizeTypeName(sourceTag.concept.type || "");
  for (const edge of sourceTag.edges) {
    const edgeLabel = (edge.edge || "").trim();
    const targetConceptId = (edge.to || "").trim();

    if (!edgeLabel || !targetConceptId) {
      continue;
    }

    const edgeClass = classifyEdgeLabel({
      edgeLabel,
      loaded: loadedRelationships,
      generatedById,
      deprecatedById,
      deferredById,
    });
    if (edgeClass.kind !== "active") {
      issues.push(
        issue(
          edgeClass.code,
          edgeClass.severity,
          edgeClass.message,
          sourceTag.file,
          sourceTag.line,
          sourceTag,
          targetConceptId,
        ),
      );
      continue;
    }

    const conceptTargets = conceptToTags.get(targetConceptId) || [];
    if (conceptTargets.length === 0) {
      issues.push(
        issue(
          "CT-COMP-010",
          "MEDIUM",
          `Cannot evaluate '${edgeLabel}' composability: target concept '${targetConceptId}' is not tagged in code`,
          sourceTag.file,
          sourceTag.line,
          sourceTag,
          targetConceptId,
        ),
      );
      continue;
    }

    const validTargets = conceptTargets.filter((targetTag) =>
      edgeClass.signatures.some((signature) =>
        signatureAllows(
          signature,
          sourceType,
          normalizeTypeName(targetTag.concept.type || ""),
        ),
      ),
    );
    if (validTargets.length === 0) {
      const actualTargetTypes = Array.from(
        new Set(
          conceptTargets.map((targetTag) => targetTag.concept.type || "unknown"),
        ),
      ).join(" / ");
      issues.push(
        issue(
          "CT-COMP-023",
          "HIGH",
          `Unconstructible DS-D8 endpoint: '${sourceTag.concept.type}' --[${edgeLabel}]--> '${actualTargetTypes}' is not an active root signature`,
          sourceTag.file,
          sourceTag.line,
          sourceTag,
          targetConceptId,
        ),
      );
      continue;
    }

    const edgeRules = rulesByEdge.get(edgeLabel) || [];
    if (edgeRules.length === 0) {
      issues.push(
        issue(
          "CT-COMP-024",
          "MEDIUM",
          `DS-D8 coverage gap: active relationship '${edgeLabel}' has valid endpoints but no code-call semantics`,
          sourceTag.file,
          sourceTag.line,
          sourceTag,
          targetConceptId,
        ),
      );
      continue;
    }

    for (const edgeRule of edgeRules) {
      if (sourceType !== edgeRule.fromType) {
        continue;
      }

      const targets = conceptTargets.filter(
        (targetTag) =>
          normalizeTypeName(targetTag.concept.type || "") === edgeRule.toType,
      );

      if (targets.length === 0) {
        // For overloaded edges (e.g. exposes -> operation/query),
        // skip rule variants whose target type does not match this edge endpoint.
        continue;
      }

      checks += 1;

      let matched = false;

      if (edgeRule.direction === "target-calls-source") {
        const sourceSymbol = (sourceTag.symbol || "").trim();
        if (!hasValidSymbol(sourceSymbol)) {
          issues.push(
            issue(
              "CT-COMP-011",
              "MEDIUM",
              `Cannot evaluate '${edgeRule.edge}' composability because source symbol is missing or unknown`,
              sourceTag.file,
              sourceTag.line,
              sourceTag,
              targetConceptId,
            ),
          );
          continue;
        }

        matched = targets.some((targetTag) =>
          tagCallsSymbol(targetTag, sourceSymbol, rootPath, sourceCache),
        );
      } else {
        const callableTargets = targets.filter((targetTag) =>
          hasValidSymbol((targetTag.symbol || "").trim()),
        );

        if (callableTargets.length === 0) {
          issues.push(
            issue(
              "CT-COMP-012",
              "MEDIUM",
              `Cannot evaluate '${edgeRule.edge}' composability: target concept '${targetConceptId}' has no resolvable symbol`,
              sourceTag.file,
              sourceTag.line,
              sourceTag,
              targetConceptId,
            ),
          );
          continue;
        }

        matched = callableTargets.some((targetTag) =>
          tagCallsSymbol(
            sourceTag,
            (targetTag.symbol || "").trim(),
            rootPath,
            sourceCache,
          ),
        );
      }

      if (!matched) {
        issues.push(
          issue(
            edgeRule.code,
            edgeRule.severity,
            `Composability mismatch: ${edgeRule.expectation} for '${sourceTag.concept.id}' -> '${targetConceptId}' (${edgeRule.edge})`,
            sourceTag.file,
            sourceTag.line,
            sourceTag,
            targetConceptId,
          ),
        );
        continue;
      }

      passedChecks += 1;
    }
  }
}

issues.sort(compareIssues);

const blockingIssues = issues.filter(
  (entry) => entry.severity === "CRITICAL" || entry.severity === "HIGH",
);

const payload = {
  ok: blockingIssues.length === 0,
  mode,
  input: toRelative(inputPath),
  root: toRelative(rootPath),
  relationshipAuthority: toRelative(loadedRelationships.path),
  activeSignatureCount: loadedRelationships.activeSignatureCount,
  generatedViewCount: generatedById.size,
  deprecatedCount: deprecatedById.size,
  deferredCount: deferredById.size,
  dynamicRuleCount: Array.from(rulesByEdge.values()).reduce(
    (sum, edgeRules) => sum + edgeRules.length,
    0,
  ),
  unsupportedActiveSignatureCount: unsupportedActiveSignatures.length,
  unsupportedActiveSignatures,
  checks,
  passedChecks,
  issues: issues.length,
  blockingIssues: blockingIssues.length,
  report: issues,
};

if (outputPath) {
  writeFileSync(outputPath, JSON.stringify(payload, null, 2) + "\n", "utf-8");
}

if (jsonOnly) {
  console.log(JSON.stringify(payload, null, 2));
} else {
  console.log(
    `check-code-tag-composability: authority=${payload.relationshipAuthority} activeSignatures=${payload.activeSignatureCount} dynamicRules=${payload.dynamicRuleCount} unsupportedActive=${payload.unsupportedActiveSignatureCount} checks=${payload.checks} passed=${payload.passedChecks} issues=${payload.issues} blocking=${payload.blockingIssues}`,
  );

  for (const entry of issues) {
    const remediation =
      " | remediation=governance/tags/CODE-TAG-REMEDIATION.md" +
      ` (code=${entry.code})`;
    console.log(
      `[code-tag-composability:${mode}] ${entry.file}:${entry.line} | severity=${entry.severity} | code=${entry.code} | ${entry.message}${remediation}`,
    );
  }
}

if (mode === "strict" && blockingIssues.length > 0) {
  process.exit(1);
}

process.exit(0);

function buildDynamicRules(loaded: LoadedRelationshipAuthority): {
  rulesByEdge: Map<string, ComposabilityRule[]>;
  unsupportedActiveSignatures: string[];
} {
  const rulesByEdge = new Map<string, ComposabilityRule[]>();
  const unsupportedActiveSignatures: string[] = [];

  for (const signature of loaded.authority.signatures) {
    if (signature.status && signature.status !== "active") {
      continue;
    }

    const sources = signatureTypes(signature, "source");
    const targets = signatureTypes(signature, "target");
    const semantics = callSemanticsByEdge.get(signature.id);
    for (const fromType of sources) {
      for (const toType of targets) {
        const signatureKey = `${signature.id}:${fromType}->${toType}`;
        if (!semantics) {
          unsupportedActiveSignatures.push(signatureKey);
          continue;
        }

        const rule: ComposabilityRule = {
          edge: signature.id,
          fromType,
          toType,
          direction: semantics.direction,
          code:
            typeof semantics.code === "function"
              ? semantics.code(toType)
              : semantics.code,
          severity: semantics.severity,
          expectation: semantics.expectation(fromType, toType),
        };
        const existing = rulesByEdge.get(signature.id) || [];
        existing.push(rule);
        rulesByEdge.set(signature.id, existing);
      }
    }
  }

  unsupportedActiveSignatures.sort();
  return { rulesByEdge, unsupportedActiveSignatures };
}

function signatureTypes(
  signature: RelationshipSignature,
  side: "source" | "target",
): string[] {
  const singular =
    side === "source" ? signature.source_type : signature.target_type;
  const plural =
    side === "source" ? signature.source_types : signature.target_types;
  return [singular, ...(plural || [])]
    .filter((value): value is string => Boolean(value))
    .map(normalizeTypeName)
    .filter(Boolean);
}

function signatureAllows(
  signature: RelationshipSignature,
  sourceType: string,
  targetType: string,
): boolean {
  return (
    signatureTypes(signature, "source").includes(sourceType) &&
    signatureTypes(signature, "target").includes(targetType)
  );
}

function toStatusMap(
  entries: RelationshipStatusEntry[] | undefined,
): Map<string, RelationshipStatusEntry> {
  return new Map(
    (entries || [])
      .filter((entry) => Boolean(entry.id))
      .map((entry) => [entry.id, entry]),
  );
}

function classifyEdgeLabel({
  edgeLabel,
  loaded,
  generatedById,
  deprecatedById,
  deferredById,
}: {
  edgeLabel: string;
  loaded: LoadedRelationshipAuthority;
  generatedById: LoadedRelationshipAuthority["generatedViewsById"];
  deprecatedById: Map<string, RelationshipStatusEntry>;
  deferredById: Map<string, RelationshipStatusEntry>;
}):
  | { kind: "active"; signatures: RelationshipSignature[] }
  | { kind: "rejected"; code: string; severity: Severity; message: string } {
  const active = loaded.signaturesById.get(edgeLabel);
  if (active && active.length > 0) {
    return { kind: "active", signatures: active };
  }

  if (generatedById.has(edgeLabel)) {
    return {
      kind: "rejected",
      code: "CT-COMP-020",
      severity: "HIGH",
      message: `Generated relationship view '${edgeLabel}' is not a canonical authored edge`,
    };
  }

  const deprecated = deprecatedById.get(edgeLabel);
  if (deprecated) {
    const replacement = deprecated.replacement
      ? `; use '${deprecated.replacement}'`
      : "";
    return {
      kind: "rejected",
      code: "CT-COMP-021",
      severity: "HIGH",
      message: `Deprecated relationship '${edgeLabel}' cannot be authored${replacement}`,
    };
  }

  if (deferredById.has(edgeLabel)) {
    return {
      kind: "rejected",
      code: "CT-COMP-022",
      severity: mode === "strict" ? "HIGH" : "MEDIUM",
      message: `Deferred relationship candidate '${edgeLabel}' is not active DS-D8 authority`,
    };
  }

  return {
    kind: "rejected",
    code: "CT-COMP-025",
    severity: "HIGH",
    message: `Unknown relationship '${edgeLabel}' is not present in root DS-D8 authority`,
  };
}

function tagCallsSymbol(
  tag: ExtractedTag,
  symbol: string,
  root: string,
  cache: Map<string, string>,
): boolean {
  const absolutePath = resolveArtifactPath(root, tag.file);
  if (!existsSync(absolutePath)) {
    return false;
  }

  let raw = cache.get(absolutePath);
  if (raw === undefined) {
    const loaded = readFileSync(absolutePath, "utf-8");
    cache.set(absolutePath, loaded);
    raw = loaded;
  }

  const callPattern = new RegExp(`\\b${escapeRegExp(symbol)}\\s*\\(`);
  return callPattern.test(raw);
}

function hasValidSymbol(symbol: string): boolean {
  const trimmed = symbol.trim();
  return Boolean(trimmed) && trimmed !== "unknown";
}

function resolveArtifactPath(root: string, filePath: string): string {
  if (filePath.startsWith("/")) {
    return filePath;
  }
  return resolve(root, filePath);
}

function readExtraction(input: string): ExtractionOutput {
  const raw = readFileSync(input, "utf-8");
  const parsed = JSON.parse(raw) as Partial<ExtractionOutput> | ExtractedTag[];

  if (Array.isArray(parsed)) {
    return {
      meta: {
        generatedAt: new Date().toISOString(),
        mode: "warn",
        include: [],
        root: process.cwd(),
      },
      tags: parsed,
      issues: [],
      stats: {
        scannedFiles: 0,
        taggedSymbols: parsed.length,
        issues: 0,
      },
    };
  }

  return {
    meta: parsed.meta || {
      generatedAt: new Date().toISOString(),
      mode: "warn",
      include: [],
      root: process.cwd(),
    },
    tags: parsed.tags || [],
    issues: parsed.issues || [],
    stats: parsed.stats || {
      scannedFiles: 0,
      taggedSymbols: (parsed.tags || []).length,
      issues: (parsed.issues || []).length,
    },
  };
}

function getRootPath(extraction: ExtractionOutput): string {
  const explicitRoot = (getArg("--root") || "").trim();
  if (explicitRoot) {
    return resolve(process.cwd(), explicitRoot);
  }

  const extractedRoot = (extraction.meta.root || "").trim();
  if (extractedRoot) {
    return extractedRoot.startsWith("/")
      ? extractedRoot
      : resolve(process.cwd(), extractedRoot);
  }

  return process.cwd();
}

function issue(
  code: string,
  severity: Severity,
  message: string,
  file: string,
  line: number,
  tag?: ExtractedTag,
  conceptId?: string,
): TagIssue {
  return {
    code,
    severity,
    message,
    file,
    line,
    symbol: tag?.symbol,
    conceptId: conceptId || tag?.concept.id,
  };
}

function compareIssues(left: TagIssue, right: TagIssue): number {
  const severityRank: Record<Severity, number> = {
    CRITICAL: 0,
    HIGH: 1,
    MEDIUM: 2,
  };

  const leftRank = severityRank[left.severity];
  const rightRank = severityRank[right.severity];
  if (leftRank !== rightRank) {
    return leftRank - rightRank;
  }

  if (left.file !== right.file) {
    return left.file.localeCompare(right.file);
  }

  if (left.line !== right.line) {
    return left.line - right.line;
  }

  return left.code.localeCompare(right.code);
}

function getArg(name: string): string | undefined {
  const index = args.indexOf(name);
  if (index < 0) {
    return undefined;
  }
  return args[index + 1];
}

function hasFlag(name: string): boolean {
  return args.includes(name);
}

function fail(entries: TagIssue[]): never {
  for (const entry of entries) {
    const remediation =
      " | remediation=governance/tags/CODE-TAG-REMEDIATION.md" +
      ` (code=${entry.code})`;
    console.log(
      `[code-tag-composability:strict] ${entry.file}:${entry.line} | severity=${entry.severity} | code=${entry.code} | ${entry.message}${remediation}`,
    );
  }
  process.exit(1);
  throw new Error("unreachable");
}

function escapeRegExp(input: string): string {
  return input.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
