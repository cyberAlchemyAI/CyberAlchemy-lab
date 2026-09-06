#!/usr/bin/env tsx
/**
 * Build the Definitions Governance M2-C1 project-level Concept Registry read model.
 *
 * Authority stays in each feature SPEC plus DS-D1/DS-D8. This tool only emits a
 * deterministic, non-authoritative aggregation and refuses invalid relationship
 * edges. When an authored registry omits its optional ID column, the read model
 * uses the feature-qualified `<feature>.<Concept>` projection ID.
 */

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, relative, resolve } from "node:path";
import { pathToFileURL } from "node:url";

import {
  findSpecFiles,
  loadRelationshipAuthority,
  parseTableForSection,
  toHeaderMap,
  toRelative,
  validateRelationshipSpecFile,
  type AuthoredRelationshipScope,
} from "./lib/relationship-signatures";
import { loadMetaTypeSchemas } from "./lib/meta-type-criteria";

type SourceRef = { path: string; line: number };
type AggregatedConcept = {
  id: string;
  concept: string;
  type: string;
  feature: string;
  id_source: "authored" | "feature-qualified-projection";
  source: SourceRef;
};
type AggregatedEdge = {
  feature: string;
  from: string;
  relationship: string;
  to: string;
  scope: AuthoredRelationshipScope;
  source: SourceRef;
};
type DuplicateId = { id: string; declarations: AggregatedConcept[] };
type TypeDrift = {
  concept: string;
  types: string[];
  declarations: AggregatedConcept[];
};
type ExcludedConcept = AggregatedConcept & { reason: string };

export type ConceptRegistryAggregation = {
  schema_version: 1;
  authority: "derived-read-model";
  generated_by: "npm run definitions:aggregate";
  concept_id_policy: string;
  sources: {
    feature_root: string;
    ds_d1_schemas: string;
    ds_d8_relationships: string;
    feature_specs: string[];
  };
  registry: Record<string, AggregatedConcept[]>;
  edges: AggregatedEdge[];
  report: {
    concept_count: number;
    edge_count: number;
    duplicate_ids: DuplicateId[];
    type_drift: TypeDrift[];
    excluded_concepts: ExcludedConcept[];
    relationship_violations: Array<{
      path: string;
      line: number;
      class: string;
      detail: string;
    }>;
  };
};

export function aggregateConceptRegistry(input: {
  featuresRoot: string;
  metaTypeSchemaRoot: string;
  relationshipsPath: string;
}): ConceptRegistryAggregation {
  const featuresRoot = resolve(input.featuresRoot);
  const schemaRoot = resolve(input.metaTypeSchemaRoot);
  const relationshipsPath = resolve(input.relationshipsPath);
  const relationshipAuthority = loadRelationshipAuthority(relationshipsPath);
  const dsD1Types = new Set(
    loadMetaTypeSchemas(schemaRoot).map((entry) => entry.schema.meta_type),
  );

  const declarations: AggregatedConcept[] = [];
  const excludedConcepts: ExcludedConcept[] = [];
  const edges: AggregatedEdge[] = [];
  const relationshipViolations: ConceptRegistryAggregation["report"]["relationship_violations"] = [];
  const featureSpecs: string[] = [];

  for (const specPath of findSpecFiles(featuresRoot).sort()) {
    const lines = readFileSync(specPath, "utf-8").split(/\r?\n/);
    const table = parseTableForSection(lines, "Concept Registry");
    if (!table) {
      continue;
    }

    featureSpecs.push(toRelative(specPath));
    const feature = relative(featuresRoot, dirname(specPath)).replace(/\\/g, "/") || ".";
    const headerMap = toHeaderMap(table.headers);
    const conceptIndex = headerMap.get("concept");
    const idIndex = headerMap.get("id");
    const typeIndex = headerMap.get("type");
    if (conceptIndex === undefined || typeIndex === undefined) {
      throw new Error(`${toRelative(specPath)}: Concept Registry requires Concept and Type columns`);
    }

    const localIds = new Map<string, string>();
    for (const row of table.rows) {
      const concept = clean(row.cells[conceptIndex] || "");
      const type = clean(row.cells[typeIndex] || "");
      const authoredId = idIndex === undefined ? "" : clean(row.cells[idIndex] || "");
      if (!concept || !type) {
        continue;
      }
      const id = authoredId || `${feature}.${concept}`;
      const declaration: AggregatedConcept = {
        id,
        concept,
        type,
        feature,
        id_source: authoredId ? "authored" : "feature-qualified-projection",
        source: { path: toRelative(specPath), line: row.line },
      };
      localIds.set(concept, id);
      if (authoredId) {
        localIds.set(authoredId, id);
      }
      if (dsD1Types.has(type)) {
        declarations.push(declaration);
      } else {
        excludedConcepts.push({
          ...declaration,
          reason: `Type ${type} has no DS-D1 criterion schema`,
        });
      }
    }

    const validation = validateRelationshipSpecFile(specPath, relationshipAuthority);
    for (const violation of validation.violations) {
      relationshipViolations.push({
        path: violation.specPath,
        line: violation.line,
        class: violation.className,
        detail: violation.detail,
      });
    }

    for (const [section, scope] of [
      ["Feature Concept Graph", "same-feature"],
      ["Concept Graph", "same-feature"],
      ["Cross-Feature Dependencies", "cross-feature"],
    ] as const) {
      const edgeTable = parseTableForSection(lines, section);
      if (!edgeTable) {
        continue;
      }
      const edgeHeaders = toHeaderMap(edgeTable.headers);
      const fromIndex = edgeHeaders.get("from") ?? edgeHeaders.get("source");
      const relationshipIndex = edgeHeaders.get("edge") ?? edgeHeaders.get("relationship");
      const toIndex = edgeHeaders.get("to") ?? edgeHeaders.get("target");
      if (fromIndex === undefined || relationshipIndex === undefined || toIndex === undefined) {
        continue;
      }
      for (const row of edgeTable.rows) {
        const fromName = clean(row.cells[fromIndex] || "");
        const relationship = clean(row.cells[relationshipIndex] || "");
        const toName = clean(row.cells[toIndex] || "");
        if (!fromName || !relationship || !toName) {
          continue;
        }
        edges.push({
          feature,
          from: localIds.get(fromName) || fromName,
          relationship,
          to: localIds.get(toName) || toName,
          scope,
          source: { path: toRelative(specPath), line: row.line },
        });
      }
    }
  }

  const registry: Record<string, AggregatedConcept[]> = {};
  for (const declaration of sortDeclarations(declarations)) {
    (registry[declaration.id] ||= []).push(declaration);
  }
  const duplicateIds = Object.entries(registry)
    .filter(([, entries]) => entries.length > 1)
    .map(([id, entries]) => ({ id, declarations: entries }));

  const byConcept = new Map<string, AggregatedConcept[]>();
  for (const declaration of declarations) {
    const key = declaration.concept.toLowerCase();
    const entries = byConcept.get(key) || [];
    entries.push(declaration);
    byConcept.set(key, entries);
  }
  const typeDrift = [...byConcept.values()]
    .filter((entries) => new Set(entries.map((entry) => entry.type)).size > 1)
    .map((entries) => ({
      concept: entries[0]?.concept || "",
      types: [...new Set(entries.map((entry) => entry.type))].sort(),
      declarations: sortDeclarations(entries),
    }))
    .sort((a, b) => a.concept.localeCompare(b.concept));

  return {
    schema_version: 1,
    authority: "derived-read-model",
    generated_by: "npm run definitions:aggregate",
    concept_id_policy:
      "Use authored Concept Registry ID when present; otherwise derive <feature>.<Concept> without changing feature authority.",
    sources: {
      feature_root: toRelative(featuresRoot),
      ds_d1_schemas: toRelative(schemaRoot),
      ds_d8_relationships: toRelative(relationshipsPath),
      feature_specs: featureSpecs.sort(),
    },
    registry,
    edges: edges.sort((a, b) =>
      [a.feature, a.from, a.relationship, a.to].join("\0").localeCompare(
        [b.feature, b.from, b.relationship, b.to].join("\0"),
      ),
    ),
    report: {
      concept_count: declarations.length,
      edge_count: edges.length,
      duplicate_ids: duplicateIds,
      type_drift: typeDrift,
      excluded_concepts: sortDeclarations(excludedConcepts) as ExcludedConcept[],
      relationship_violations: relationshipViolations.sort((a, b) =>
        `${a.path}:${a.line}`.localeCompare(`${b.path}:${b.line}`),
      ),
    },
  };
}

function sortDeclarations<T extends AggregatedConcept>(entries: T[]): T[] {
  return [...entries].sort((a, b) =>
    [a.id, a.feature, a.source.path, String(a.source.line)].join("\0").localeCompare(
      [b.id, b.feature, b.source.path, String(b.source.line)].join("\0"),
    ),
  );
}

function clean(value: string): string {
  return value.trim().replace(/^`|`$/g, "");
}

function getArg(flag: string, fallback: string): string {
  const index = process.argv.indexOf(flag);
  return index >= 0 ? process.argv[index + 1] || fallback : fallback;
}

function main(): void {
  const aggregation = aggregateConceptRegistry({
    featuresRoot: getArg("--features-root", "spec/features"),
    metaTypeSchemaRoot: getArg("--schema-dir", "spec/meta-types"),
    relationshipsPath: getArg(
      "--relationships",
      "../definitions/relationships/relationships.yml",
    ),
  });
  const outputPath = resolve(
    process.cwd(),
    getArg("--output", "../definitions/CONCEPT-REGISTRY.json"),
  );
  mkdirSync(dirname(outputPath), { recursive: true });
  writeFileSync(outputPath, `${JSON.stringify(aggregation, null, 2)}\n`, "utf-8");

  const { report } = aggregation;
  const flagged =
    report.duplicate_ids.length +
    report.type_drift.length +
    report.relationship_violations.length;
  console.log(
    `definitions:aggregate: ${flagged === 0 ? "PASS" : "FAIL"} (` +
      `${report.concept_count} concept(s), ${report.edge_count} edge(s), ` +
      `${report.duplicate_ids.length} duplicate ID(s), ${report.type_drift.length} type drift(s), ` +
      `${report.excluded_concepts.length} excluded non-DS-D1 concept(s)) -> ${toRelative(outputPath)}`,
  );
  if (flagged > 0) {
    process.exitCode = 1;
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
