#!/usr/bin/env tsx

import { existsSync } from "node:fs";
import { resolve } from "node:path";

import {
  findSpecFiles,
  loadRelationshipAuthority,
  toRelative,
  validateRelationshipSpecFile,
  validateSchemaParticipation,
} from "./lib/relationship-signatures";

type PrintableViolation = {
  specPath: string;
  line: number;
  section: string;
  value: string;
  className: string;
  detail: string;
  suggestions: string[];
};

const args = process.argv.slice(2);
const mode = getArg("--mode") || "strict";
const featuresRoot = resolve(
  process.cwd(),
  getArg("--features-root") || "spec/features",
);
const relationshipsPath = resolve(
  process.cwd(),
  getArg("--relationships") || "../definitions/relationships/relationships.yml",
);
const schemaDir = resolve(process.cwd(), getArg("--schema-dir") || "spec/meta-types");

const loaded = loadRelationshipAuthority(relationshipsPath);
const specFiles = findSpecFiles(featuresRoot);
const violations: PrintableViolation[] = [];
let edgesChecked = 0;

if (!existsSync(featuresRoot)) {
  console.log(
    `validate-relationships: no features found at ${toRelative(featuresRoot)}`,
  );
} else {
  for (const specPath of specFiles) {
    const result = validateRelationshipSpecFile(specPath, loaded);
    edgesChecked += result.edgesChecked;
    violations.push(...result.violations);
  }
}

for (const schemaViolation of validateSchemaParticipation(schemaDir, loaded)) {
  violations.push({
    specPath: schemaViolation.schemaPath,
    line: schemaViolation.line,
    section: "Schema Edge Participation",
    value: `${schemaViolation.metaType}.${schemaViolation.direction}`,
    className: "unconstructible-edge",
    detail:
      `${schemaViolation.detail}; expected=[${schemaViolation.expected.join(",")}] ` +
      `actual=[${schemaViolation.actual.join(",")}]`,
    suggestions: [],
  });
}

if (violations.length === 0) {
  console.log(
    `validate-relationships: PASS (` +
      `${specFiles.length} specs checked, ` +
      `edgesChecked=${edgesChecked}, ` +
      `canonicalSignatures=${loaded.activeSignatureCount})`,
  );
  process.exit(0);
}

const canonicalList = [...loaded.signaturesById.keys()].sort().join(", ");
for (const violation of violations) {
  const suggestionText =
    violation.suggestions.length > 0
      ? ` | suggested=${violation.suggestions.join(",")}`
      : " | suggested=<none>";
  console.log(
    `[relationship:${mode}] ${violation.specPath}:${violation.line} | ` +
      `class=${violation.className} | section=${violation.section} | ` +
      `value=${violation.value} | ${violation.detail}${suggestionText}`,
  );
}
console.log(
  `[relationship:${mode}] violations=${violations.length} canonicalSignatures=[${canonicalList}]`,
);

if (mode === "warn") {
  process.exit(0);
}

process.exit(1);

function getArg(name: string): string | undefined {
  const index = args.indexOf(name);
  if (index < 0) {
    return undefined;
  }
  return args[index + 1];
}
