export const UI_REPAIR_VIOLATION_REGISTRY = "ui-repair-violations/v1";

export const UI_REPAIR_VIOLATION_CODES = [
  "ATTRIBUTE-MISSING",
  "ATTRIBUTE-EMPTY",
  "ATTRIBUTE-WHITESPACE",
  "DUPLICATE-KEY",
  "CRITERIA-CONFLICT",
  "FIXED-VALUE-MISMATCH",
  "NONSTRING-VALUE",
  "UNKNOWN-RULE",
] as const;

export type UiRepairViolationCode = (typeof UI_REPAIR_VIOLATION_CODES)[number];

type CriterionLike = {
  rule?: unknown;
  key?: unknown;
  value?: unknown;
  values?: unknown;
};

const SUPPORTED_RULES = new Set([
  "section-contains",
  "attribute-one-of",
  "table-has-column",
  "attribute-equals",
  "attribute-present",
  "attribute-nonempty/v1",
  "at-least-one",
  "none",
  "all-nonempty",
]);

export function uiRepairViolation(code: UiRepairViolationCode, detail: string): string {
  return `[${UI_REPAIR_VIOLATION_REGISTRY}:${code}] ${detail}`;
}

export function attributeNonemptyViolation(
  present: boolean,
  value: unknown,
): UiRepairViolationCode | null {
  if (!present) return "ATTRIBUTE-MISSING";
  if (typeof value !== "string") return "NONSTRING-VALUE";
  if (value.length === 0) return "ATTRIBUTE-EMPTY";
  if (value.trim().length === 0) return "ATTRIBUTE-WHITESPACE";
  return null;
}

export function assertNoDuplicateSchemaKey(
  parent: Record<string, unknown>,
  key: string,
  where: string,
  line: number,
): void {
  if (Object.hasOwn(parent, key)) {
    throw new Error(
      uiRepairViolation(
        "DUPLICATE-KEY",
        `${where}:${line}: duplicate key '${key}' is not allowed; no precedence is defined`,
      ),
    );
  }
}

export function assertCriterionPreflight(criteria: unknown, where: string): void {
  if (criteria === undefined) return;
  if (!isRecord(criteria)) {
    throw new Error(uiRepairViolation("UNKNOWN-RULE", `${where}: criterion must be a map`));
  }

  const entries = Object.entries(criteria).map(([name, raw]) => {
    if (!isRecord(raw)) {
      throw new Error(
        uiRepairViolation("UNKNOWN-RULE", `${where}: criterion '${name}' must be a map`),
      );
    }
    const criterion = raw as CriterionLike;
    const rule = typeof criterion.rule === "string" ? criterion.rule : "";
    if (!SUPPORTED_RULES.has(rule)) {
      throw new Error(
        uiRepairViolation("UNKNOWN-RULE", `${where}: criterion '${name}' uses unsupported rule '${rule}'`),
      );
    }
    return { name, criterion, rule, key: normalizeKey(criterion.key) };
  });

  for (let leftIndex = 0; leftIndex < entries.length; leftIndex += 1) {
    const left = entries[leftIndex]!;
    if (!left.key) continue;
    for (let rightIndex = leftIndex + 1; rightIndex < entries.length; rightIndex += 1) {
      const right = entries[rightIndex]!;
      if (left.key !== right.key) continue;
      const reason = conflictReason(left, right);
      if (reason) {
        throw new Error(
          uiRepairViolation(
            "CRITERIA-CONFLICT",
            `${where}: criteria '${left.name}' and '${right.name}' conflict for attribute '${left.key}': ${reason}`,
          ),
        );
      }
    }
  }
}

function conflictReason(
  left: { rule: string; criterion: CriterionLike },
  right: { rule: string; criterion: CriterionLike },
): string | null {
  if (left.rule === "attribute-equals" && right.rule === "attribute-equals") {
    const leftValue = normalizeValue(left.criterion.value);
    const rightValue = normalizeValue(right.criterion.value);
    return leftValue !== rightValue ? `unequal fixed values '${leftValue}' and '${rightValue}'` : null;
  }

  if (left.rule === "attribute-equals" && right.rule === "attribute-one-of") {
    return equalsOneOfConflict(left.criterion, right.criterion);
  }
  if (left.rule === "attribute-one-of" && right.rule === "attribute-equals") {
    return equalsOneOfConflict(right.criterion, left.criterion);
  }
  if (left.rule === "attribute-one-of" && right.rule === "attribute-one-of") {
    const leftValues = normalizedValues(left.criterion.values);
    const rightValues = normalizedValues(right.criterion.values);
    return leftValues.some((value) => rightValues.includes(value))
      ? null
      : "allowed-value sets have no intersection";
  }
  return null;
}

function equalsOneOfConflict(equals: CriterionLike, oneOf: CriterionLike): string | null {
  const fixed = normalizeValue(equals.value);
  const allowed = normalizedValues(oneOf.values);
  return allowed.includes(fixed) ? null : `fixed value '${fixed}' is outside [${allowed.join(", ")}]`;
}

function normalizedValues(value: unknown): string[] {
  return Array.isArray(value) ? value.map(normalizeValue) : [];
}

function normalizeKey(value: unknown): string {
  return typeof value === "string" ? value.trim().toLowerCase() : "";
}

function normalizeValue(value: unknown): string {
  return typeof value === "string" ? value.trim().toLowerCase() : String(value ?? "");
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}
