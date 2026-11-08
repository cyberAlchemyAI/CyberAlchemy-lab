import { generatedOperationPatterns } from "./generated/operation-patterns.generated.js";
import type { OperationPattern, PatternAvailability } from "./registry-compiler.js";

export type { OperationPattern, PatternAvailability, PrerequisiteStatus } from "./registry-compiler.js";

export const operationPatterns: readonly OperationPattern[] = generatedOperationPatterns;

export function deriveAvailability(pattern: OperationPattern): PatternAvailability {
  return [pattern.meta_type, pattern.integration_binding, pattern.generator, pattern.conformance].every((item) => item.status === "closed") ? "available" : "blocked";
}

export function listOperationPatterns(filter: PatternAvailability | "all" = "all"): readonly OperationPattern[] {
  for (const pattern of operationPatterns) {
    if (deriveAvailability(pattern) !== pattern.availability) throw new Error(`PATTERN_AVAILABILITY_DRIFT:${pattern.pattern_id}`);
    if (pattern.availability === "available" && pattern.blockers.length) throw new Error(`AVAILABLE_PATTERN_HAS_BLOCKERS:${pattern.pattern_id}`);
    if (pattern.availability === "blocked" && !pattern.blockers.length) throw new Error(`BLOCKED_PATTERN_WITHOUT_CAUSE:${pattern.pattern_id}`);
  }
  return filter === "all" ? operationPatterns : operationPatterns.filter((pattern) => pattern.availability === filter);
}

export function requireGeneratablePattern(patternId: string): OperationPattern {
  const pattern = listOperationPatterns().find((item) => item.pattern_id === patternId);
  if (!pattern) throw new Error(`PATTERN_NOT_REGISTERED:${patternId}`);
  if (pattern.availability !== "available") throw new Error(`PATTERN_GENERATION_BLOCKED:${patternId}:${pattern.blockers.join("|")}`);
  return pattern;
}
