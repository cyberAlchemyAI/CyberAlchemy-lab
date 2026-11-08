import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";

export type RelationshipSignature = {
  id: string;
  source_type?: string;
  source_types?: string[];
  target_type?: string;
  target_types?: string[];
  feature_scope?: RelationshipScope[];
  multiplicity?: "one_to_one" | "one_to_many" | "one_to_many_ordered" | "many_to_one" | "many_to_many";
  generated_source_projection?: GeneratedSourceProjection;
  status?: string;
  projection?: {
    markdown?: string;
  };
  [key: string]: unknown;
};

export type RelationshipScope =
  | "same-feature"
  | "cross-feature"
  | "ui"
  | "ui-backend";

export type AuthoredRelationshipScope = "same-feature" | "cross-feature";

export type GeneratedSourceProjection = {
  attribute: string;
  value_shape: "concept-reference-set";
  derivation: "outgoing-targets";
  authorship: "forbidden";
};

export type GeneratedRelationshipView = {
  id: string;
  source_type?: string;
  target_type?: string;
  from_signature?: string;
  [key: string]: unknown;
};

export type DeprecatedRelationshipAlias = {
  id: string;
  replacement: string;
  reason: string;
};

export type RelationshipAuthority = {
  version: number;
  authority: string;
  status: string;
  signature_count: number;
  signatures: RelationshipSignature[];
  generated_views?: GeneratedRelationshipView[];
  deprecated?: DeprecatedRelationshipAlias[];
  [key: string]: unknown;
};

export type LoadedRelationshipAuthority = {
  path: string;
  authority: RelationshipAuthority;
  signaturesById: Map<string, RelationshipSignature[]>;
  activeSignatureCount: number;
  generatedViewsById: Map<string, GeneratedRelationshipView>;
  deprecatedAliasesById: Map<string, DeprecatedRelationshipAlias>;
};

export type TableRow = {
  cells: string[];
  line: number;
};

export type MarkdownTable = {
  headers: string[];
  rows: TableRow[];
};

export type RelationshipViolation = {
  specPath: string;
  line: number;
  section: string;
  value: string;
  className: "noncanonical-edge" | "unknown-concept" | "unconstructible-edge";
  detail: string;
  suggestions: string[];
};

export type RelationshipFileResult = {
  violations: RelationshipViolation[];
  edgesChecked: number;
  concepts: number;
};

export type SchemaParticipationViolation = {
  schemaPath: string;
  line: number;
  metaType: string;
  direction: "source_of" | "target_of";
  expected: string[];
  actual: string[];
  detail: string;
};

type ConceptCatalogEntry = {
  id: string;
  type: string;
  line: number;
};

type AuthoredRelationshipEdge = {
  from: string;
  edge: string;
  to: string;
  scope: AuthoredRelationshipScope;
  line: number;
  section: string;
};

export function loadRelationshipAuthority(
  authorityPath: string,
): LoadedRelationshipAuthority {
  if (!existsSync(authorityPath)) {
    throw new Error(`relationship authority not found: ${toRelative(authorityPath)}`);
  }

  const raw = readFileSync(authorityPath, "utf-8");
  let parsed: RelationshipAuthority;
  try {
    parsed = JSON.parse(raw) as RelationshipAuthority;
  } catch (error) {
    throw new Error(
      `relationship authority must be JSON-compatible YAML: ${toRelative(authorityPath)} (${String(error)})`,
    );
  }

  if (!Array.isArray(parsed.signatures)) {
    throw new Error(
      `relationship authority has no signatures array: ${toRelative(authorityPath)}`,
    );
  }

  const signaturesById = new Map<string, RelationshipSignature[]>();
  let activeSignatureCount = 0;
  for (const signature of parsed.signatures) {
    if (!signature.id) {
      throw new Error(`relationship authority contains a signature without id`);
    }
    if (signature.status === "deprecated" || signature.status === "deferred") {
      continue;
    }
    if (!signaturesById.has(signature.id)) {
      signaturesById.set(signature.id, []);
    }
    signaturesById.get(signature.id)?.push(signature);
    activeSignatureCount += 1;
  }

  const generatedViewsById = new Map<string, GeneratedRelationshipView>();
  for (const view of parsed.generated_views || []) {
    if (view.id) {
      generatedViewsById.set(view.id, view);
    }
  }

  const deprecatedAliasesById = new Map<string, DeprecatedRelationshipAlias>();
  for (const alias of parsed.deprecated || []) {
    if (!alias.id || !alias.replacement || !alias.reason) {
      throw new Error(`relationship authority contains an incomplete deprecated alias`);
    }
    if (signaturesById.has(alias.id) || generatedViewsById.has(alias.id)) {
      throw new Error(`deprecated relationship alias collides with active/generated id: ${alias.id}`);
    }
    if (!signaturesById.has(alias.replacement)) {
      throw new Error(
        `deprecated relationship alias ${alias.id} has noncanonical replacement ${alias.replacement}`,
      );
    }
    if (deprecatedAliasesById.has(alias.id)) {
      throw new Error(`duplicate deprecated relationship alias: ${alias.id}`);
    }
    deprecatedAliasesById.set(alias.id, alias);
  }

  if (parsed.signature_count !== activeSignatureCount) {
    throw new Error(
      `relationship authority signature_count=${parsed.signature_count} but active signatures=${activeSignatureCount}`,
    );
  }

  return {
    path: authorityPath,
    authority: parsed,
    signaturesById,
    activeSignatureCount,
    generatedViewsById,
    deprecatedAliasesById,
  };
}

export function validateRelationshipSpecFile(
  specPath: string,
  loaded: LoadedRelationshipAuthority,
): RelationshipFileResult {
  const raw = readFileSync(specPath, "utf-8");
  const lines = raw.split(/\r?\n/);
  const concepts = parseConceptRegistry(lines);
  const violations: RelationshipViolation[] = [];
  const authoredEdges: AuthoredRelationshipEdge[] = [];
  let edgesChecked = 0;

  for (const sectionName of ["Feature Concept Graph", "Concept Graph"]) {
    const table = parseTableForSection(lines, sectionName);
    if (!table) {
      continue;
    }

    const headerMap = toHeaderMap(table.headers);
    const fromIndex = headerMap.get("from");
    const edgeIndex = headerMap.get("edge") ?? headerMap.get("relationship");
    const toIndex = headerMap.get("to");
    if (fromIndex === undefined || edgeIndex === undefined || toIndex === undefined) {
      continue;
    }

    for (const row of table.rows) {
      const from = cleanCell(row.cells[fromIndex] || "");
      const edge = cleanCell(row.cells[edgeIndex] || "");
      const to = cleanCell(row.cells[toIndex] || "");
      if (!from || !edge || !to || isPlaceholder(from) || isPlaceholder(edge) || isPlaceholder(to)) {
        continue;
      }
      edgesChecked += 1;
      authoredEdges.push({
        from,
        edge,
        to,
        scope: "same-feature",
        line: row.line,
        section: sectionName,
      });
      violations.push(
        ...validateTriple({
          loaded,
          concepts,
          lines,
          specPath,
          line: row.line,
          section: sectionName,
          scope: "same-feature",
          from,
          edge,
          to,
        }),
      );
    }
  }

  const dependencyTable = parseTableForSection(lines, "Cross-Feature Dependencies");
  if (dependencyTable) {
    const headerMap = toHeaderMap(dependencyTable.headers);
    const fromIndex = headerMap.get("from") ?? headerMap.get("source");
    const edgeIndex = headerMap.get("edge") ?? headerMap.get("relationship");
    const toIndex = headerMap.get("to") ?? headerMap.get("target");

    if (edgeIndex !== undefined) {
      for (const row of dependencyTable.rows) {
        const edge = cleanCell(row.cells[edgeIndex] || "");
        if (!edge || isPlaceholder(edge)) {
          continue;
        }

        if (fromIndex !== undefined && toIndex !== undefined) {
          const from = cleanCell(row.cells[fromIndex] || "");
          const to = cleanCell(row.cells[toIndex] || "");
          if (!from || !to || isPlaceholder(from) || isPlaceholder(to)) {
            continue;
          }
          edgesChecked += 1;
          authoredEdges.push({
            from,
            edge,
            to,
            scope: "cross-feature",
            line: row.line,
            section: "Cross-Feature Dependencies",
          });
          violations.push(
            ...validateTriple({
              loaded,
              concepts,
              lines,
              specPath,
              line: row.line,
              section: "Cross-Feature Dependencies",
              scope: "cross-feature",
              from,
              edge,
              to,
            }),
          );
        } else if (!loaded.signaturesById.has(edge)) {
          const deprecated = loaded.deprecatedAliasesById.get(edge);
          violations.push({
            specPath: toRelative(specPath),
            line: row.line,
            section: "Cross-Feature Dependencies",
            value: edge,
            className: "noncanonical-edge",
            detail: deprecated
              ? `Deprecated relationship label "${edge}" is not canonical: ${deprecated.reason}`
              : `Relationship label "${edge}" is not canonical`,
            suggestions: deprecated
              ? [deprecated.replacement]
              : suggestCanonicalEdges(edge, loaded.signaturesById),
          });
        }
      }
    }
  }

  violations.push(
    ...validateGeneratedProjectionAuthorship({
      loaded,
      concepts,
      lines,
      specPath,
    }),
  );
  violations.push(
    ...validateMultiplicity({ loaded, concepts, specPath, authoredEdges }),
  );

  return {
    violations,
    edgesChecked,
    concepts: concepts.size,
  };
}

export function validateSchemaParticipation(
  schemaDir: string,
  loaded: LoadedRelationshipAuthority,
): SchemaParticipationViolation[] {
  if (!existsSync(schemaDir)) {
    return [];
  }

  const expected = buildExpectedParticipation(loaded);
  const violations: SchemaParticipationViolation[] = [];
  for (const schemaPath of walk(schemaDir).filter((path) => path.endsWith(".schema.yml"))) {
    const raw = readFileSync(schemaPath, "utf-8");
    const metaType = parseScalar(raw, "meta_type");
    if (!metaType) {
      continue;
    }

    const normalizedType = normalizeTypeName(metaType);
    const expectedSource = expected.sourceOf.get(normalizedType) || [];
    const expectedTarget = expected.targetOf.get(normalizedType) || [];
    const actualSource = parseInlineArray(raw, "source_of");
    const actualTarget = parseInlineArray(raw, "target_of");

    if (!sameSet(actualSource, expectedSource)) {
      violations.push({
        schemaPath: toRelative(schemaPath),
        line: findLine(raw, "source_of"),
        metaType,
        direction: "source_of",
        expected: expectedSource,
        actual: actualSource,
        detail: `${metaType}.source_of does not match root relationship signatures`,
      });
    }

    if (!sameSet(actualTarget, expectedTarget)) {
      violations.push({
        schemaPath: toRelative(schemaPath),
        line: findLine(raw, "target_of"),
        metaType,
        direction: "target_of",
        expected: expectedTarget,
        actual: actualTarget,
        detail: `${metaType}.target_of does not match root relationship signatures`,
      });
    }
  }

  return violations;
}

export function findSpecFiles(root: string): string[] {
  if (!existsSync(root)) {
    return [];
  }
  return walk(root).filter((path) => path.endsWith("/SPEC.md"));
}

export function parseTableForSection(
  lines: string[],
  sectionName: string,
): MarkdownTable | null {
  const sectionRanges = findSectionRanges(lines);
  const section = sectionRanges.find(
    (entry) =>
      normalizeSectionName(entry.name) === normalizeSectionName(sectionName),
  );

  if (!section) {
    return null;
  }

  let start = section.start;
  while (start < section.end && !lines[start]?.trim().startsWith("|")) {
    start += 1;
  }

  if (start >= section.end) {
    return null;
  }

  const headerLine = lines[start] || "";
  const separatorLine = lines[start + 1] || "";
  if (!separatorLine.trim().startsWith("|")) {
    return null;
  }

  const headers = parseTableRow(headerLine);
  const separatorCells = parseTableRow(separatorLine);
  if (
    headers.length === 0 ||
    separatorCells.length === 0 ||
    !separatorCells.every(
      (cell) => /^:?-{3,}:?$/.test(cell) || cell.length === 0,
    )
  ) {
    return null;
  }

  const rows: TableRow[] = [];
  let rowIndex = start + 2;
  while (rowIndex < section.end) {
    const line = lines[rowIndex] || "";
    if (!line.trim().startsWith("|")) {
      break;
    }

    const cells = parseTableRow(line);
    if (!cells.every((cell) => /^:?-{3,}:?$/.test(cell) || cell.length === 0)) {
      rows.push({
        cells,
        line: rowIndex + 1,
      });
    }

    rowIndex += 1;
  }

  return {
    headers,
    rows,
  };
}

export function parseTableRow(line: string): string[] {
  const trimmed = line.trim();
  if (!trimmed.startsWith("|")) {
    return [];
  }

  const withoutEdges = trimmed.replace(/^\|/, "").replace(/\|$/, "");
  return withoutEdges.split("|").map((cell) => cell.trim());
}

export function toHeaderMap(headers: string[]): Map<string, number> {
  const map = new Map<string, number>();
  headers.forEach((header, index) => {
    map.set(normalizeHeader(header), index);
  });
  return map;
}

export function normalizeTypeName(input: string): string {
  return input
    .trim()
    .toLowerCase()
    .replace(/\[[^\]]*\]/g, "")
    .replace(/[^a-z0-9]+/g, "");
}

export function toRelative(absPath: string): string {
  return relative(process.cwd(), absPath).replace(/\\/g, "/");
}

function validateTriple(input: {
  loaded: LoadedRelationshipAuthority;
  concepts: Map<string, ConceptCatalogEntry>;
  lines: string[];
  specPath: string;
  line: number;
  section: string;
  scope: AuthoredRelationshipScope;
  from: string;
  edge: string;
  to: string;
}): RelationshipViolation[] {
  const { loaded, concepts, lines, specPath, line, section, scope, from, edge, to } = input;
  const value = `${from} --[${edge}]--> ${to}`;

  if (loaded.generatedViewsById.has(edge)) {
    return [
      {
        specPath: toRelative(specPath),
        line,
        section,
        value,
        className: "noncanonical-edge",
        detail: `Generated inverse "${edge}" is a navigation view, not a canonical relationship signature`,
        suggestions: [],
      },
    ];
  }


  const deprecated = loaded.deprecatedAliasesById.get(edge);
  if (deprecated) {
    return [
      {
        specPath: toRelative(specPath),
        line,
        section,
        value,
        className: "noncanonical-edge",
        detail: `Deprecated relationship label "${edge}" is not canonical: ${deprecated.reason}`,
        suggestions: [deprecated.replacement],
      },
    ];
  }

  const signatures = loaded.signaturesById.get(edge) || [];
  if (signatures.length === 0) {
    return [
      {
        specPath: toRelative(specPath),
        line,
        section,
        value,
        className: "noncanonical-edge",
        detail: `Relationship label "${edge}" is not canonical`,
        suggestions: suggestCanonicalEdges(edge, loaded.signaturesById),
      },
    ];
  }

  const fromConcept = concepts.get(from);
  if (!fromConcept) {
    return [
      {
        specPath: toRelative(specPath),
        line,
        section,
        value,
        className: "unknown-concept",
        detail: `Source concept "${from}" is not declared in the Concept Registry`,
        suggestions: [],
      },
    ];
  }

  const toConcept = concepts.get(to);
  if (!toConcept) {
    return [
      {
        specPath: toRelative(specPath),
        line,
        section,
        value,
        className: "unknown-concept",
        detail: `Target concept "${to}" is not declared in the Concept Registry`,
        suggestions: [],
      },
    ];
  }

  const sourceType = normalizeTypeName(fromConcept.type);
  const targetType = normalizeTypeName(toConcept.type);
  const endpointSignatures = signatures.filter((signature) => {
    const sourceTypes = signatureTypes(signature, "source");
    const targetTypes = signatureTypes(signature, "target");
    return sourceTypes.has(sourceType) && targetTypes.has(targetType);
  });

  if (endpointSignatures.length === 0) {
    return [
      {
        specPath: toRelative(specPath),
        line,
        section,
        value,
        className: "unconstructible-edge",
        detail:
          `Endpoint signature mismatch for "${edge}": ` +
          `${from} has type ${fromConcept.type}, ${to} has type ${toConcept.type}; ` +
          `expected ${displaySignatureVariants(signatures)}`,
        suggestions: [],
      },
    ];
  }

  const matchingSignature = endpointSignatures.find((signature) =>
    admitsAuthoredScope(signature, scope),
  );
  if (!matchingSignature) {
    const admittedScopes = [...new Set(endpointSignatures.flatMap((signature) => signature.feature_scope || []))]
      .sort()
      .join("|") || "<none>";
    return [
      {
        specPath: toRelative(specPath),
        line,
        section,
        value,
        className: "unconstructible-edge",
        detail: `Feature scope mismatch for "${edge}": authored as ${scope}; expected ${admittedScopes}`,
        suggestions: [],
      },
    ];
  }

  return [];
}

function validateGeneratedProjectionAuthorship(input: {
  loaded: LoadedRelationshipAuthority;
  concepts: Map<string, ConceptCatalogEntry>;
  lines: string[];
  specPath: string;
}): RelationshipViolation[] {
  const { loaded, concepts, lines, specPath } = input;
  const violations: RelationshipViolation[] = [];

  for (const concept of concepts.values()) {
    const sourceType = normalizeTypeName(concept.type);
    for (const signatures of loaded.signaturesById.values()) {
      for (const signature of signatures) {
        const projection = signature.generated_source_projection;
        if (!projection || !signatureTypes(signature, "source").has(sourceType)) {
          continue;
        }
        const row = findConceptAttributeRow(lines, concept.id, projection.attribute);
        if (row) {
          violations.push({
            specPath: toRelative(specPath),
            line: row.line,
            section: concept.id,
            value: `${concept.id}.${projection.attribute}`,
            className: "unconstructible-edge",
            detail:
              `Generated projection ${projection.attribute} must not be authored; ` +
              `derive it from ${concept.id} --[${signature.id}]--> target`,
            suggestions: [],
          });
        }
      }
    }
  }

  return violations;
}

function validateMultiplicity(input: {
  loaded: LoadedRelationshipAuthority;
  concepts: Map<string, ConceptCatalogEntry>;
  specPath: string;
  authoredEdges: AuthoredRelationshipEdge[];
}): RelationshipViolation[] {
  const { loaded, concepts, specPath, authoredEdges } = input;
  const violations: RelationshipViolation[] = [];

  for (const signature of loaded.authority.signatures) {
    if (
      signature.status === "deprecated" ||
      signature.status === "deferred" ||
      signature.multiplicity !== "one_to_one"
    ) {
      continue;
    }
    const relevant = authoredEdges.filter((edge) => {
      if (edge.edge !== signature.id || !admitsAuthoredScope(signature, edge.scope)) {
        return false;
      }
      const source = concepts.get(edge.from);
      const target = concepts.get(edge.to);
      return Boolean(
        source &&
        target &&
        signatureTypes(signature, "source").has(normalizeTypeName(source.type)) &&
        signatureTypes(signature, "target").has(normalizeTypeName(target.type)),
      );
    });

    for (const [source, edges] of groupEdges(relevant, (edge) => edge.from)) {
      if (edges.length <= 1) {
        continue;
      }
      const targets = [...new Set(edges.map((edge) => edge.to))].sort();
      violations.push({
        specPath: toRelative(specPath),
        line: edges[1]?.line ?? edges[0]!.line,
        section: edges[1]?.section ?? edges[0]!.section,
        value: `${source} --[${signature.id}]--> ${targets.join(", ")}`,
        className: "unconstructible-edge",
        detail:
          `Multiplicity violation for "${signature.id}": source ${source} has ${edges.length} ` +
          `outgoing edges; one_to_one permits at most one`,
        suggestions: [],
      });
    }

    for (const [target, edges] of groupEdges(relevant, (edge) => edge.to)) {
      if (edges.length <= 1) {
        continue;
      }
      const sources = [...new Set(edges.map((edge) => edge.from))].sort();
      violations.push({
        specPath: toRelative(specPath),
        line: edges[1]?.line ?? edges[0]!.line,
        section: edges[1]?.section ?? edges[0]!.section,
        value: `${sources.join(", ")} --[${signature.id}]--> ${target}`,
        className: "unconstructible-edge",
        detail:
          `Multiplicity violation for "${signature.id}": target ${target} has ${edges.length} ` +
          `incoming edges; one_to_one permits at most one`,
        suggestions: [],
      });
    }
  }

  return violations;
}

function groupEdges(
  edges: AuthoredRelationshipEdge[],
  key: (edge: AuthoredRelationshipEdge) => string,
): Map<string, AuthoredRelationshipEdge[]> {
  const grouped = new Map<string, AuthoredRelationshipEdge[]>();
  for (const edge of edges) {
    const value = key(edge);
    grouped.set(value, [...(grouped.get(value) ?? []), edge]);
  }
  return grouped;
}

function findConceptAttributeRow(
  lines: string[],
  concept: string,
  attribute: string,
): TableRow | undefined {
  const table = parseTableForSection(lines, concept);
  if (!table) {
    return undefined;
  }
  const headerMap = toHeaderMap(table.headers);
  const attributeIndex = headerMap.get("attribute");
  if (attributeIndex === undefined) {
    return undefined;
  }
  return table.rows.find(
    (entry) => cleanCell(entry.cells[attributeIndex] || "") === attribute,
  );
}

function admitsAuthoredScope(
  signature: RelationshipSignature,
  authoredScope: AuthoredRelationshipScope,
): boolean {
  const declared = signature.feature_scope || [];
  if (authoredScope === "cross-feature") {
    return declared.includes("cross-feature");
  }
  return declared.some((scope) =>
    scope === "same-feature" || scope === "ui" || scope === "ui-backend"
  );
}

function parseConceptRegistry(lines: string[]): Map<string, ConceptCatalogEntry> {
  const concepts = new Map<string, ConceptCatalogEntry>();
  const sectionCandidates = ["Concept Registry", "Concepts", "Domain Concepts"];

  for (const section of sectionCandidates) {
    const table = parseTableForSection(lines, section);
    if (!table) {
      continue;
    }

    const headerMap = toHeaderMap(table.headers);
    const conceptIndex = headerMap.get("concept") ?? headerMap.get("name");
    const idIndex = headerMap.get("id");
    const typeIndex = headerMap.get("type");
    if ((conceptIndex === undefined && idIndex === undefined) || typeIndex === undefined) {
      continue;
    }

    for (const row of table.rows) {
      const type = cleanCell(row.cells[typeIndex] || "");
      if (!type || isPlaceholder(type)) {
        continue;
      }

      for (const index of [conceptIndex, idIndex]) {
        if (index === undefined) {
          continue;
        }
        const id = cleanCell(row.cells[index] || "");
        if (!id || isPlaceholder(id) || concepts.has(id)) {
          continue;
        }
        concepts.set(id, {
          id,
          type,
          line: row.line,
        });
      }
    }
  }

  return concepts;
}

function buildExpectedParticipation(loaded: LoadedRelationshipAuthority): {
  sourceOf: Map<string, string[]>;
  targetOf: Map<string, string[]>;
} {
  const sourceOf = new Map<string, Set<string>>();
  const targetOf = new Map<string, Set<string>>();

  for (const signatures of loaded.signaturesById.values()) {
    for (const signature of signatures) {
      for (const sourceType of signatureTypes(signature, "source")) {
      if (!sourceOf.has(sourceType)) {
        sourceOf.set(sourceType, new Set());
      }
      sourceOf.get(sourceType)?.add(signature.id);
      }

      for (const targetType of signatureTypes(signature, "target")) {
      if (!targetOf.has(targetType)) {
        targetOf.set(targetType, new Set());
      }
      targetOf.get(targetType)?.add(signature.id);
      }
    }
  }

  return {
    sourceOf: mapSetToSortedArray(sourceOf),
    targetOf: mapSetToSortedArray(targetOf),
  };
}

function signatureTypes(
  signature: RelationshipSignature,
  side: "source" | "target",
): Set<string> {
  const values =
    side === "source"
      ? signature.source_types || scalarToArray(signature.source_type)
      : signature.target_types || scalarToArray(signature.target_type);

  return new Set(values.map((value) => normalizeTypeName(value)).filter(Boolean));
}

function scalarToArray(value: unknown): string[] {
  if (typeof value !== "string") {
    return [];
  }
  return [value];
}

function displayTypes(types: Set<string>): string {
  return [...types].sort().join("|") || "<none>";
}

function displaySignatureVariants(signatures: RelationshipSignature[]): string {
  return signatures
    .map((signature) => {
      const sourceTypes = signatureTypes(signature, "source");
      const targetTypes = signatureTypes(signature, "target");
      return `${displayTypes(sourceTypes)} -> ${displayTypes(targetTypes)}`;
    })
    .join(" or ");
}

function mapSetToSortedArray(input: Map<string, Set<string>>): Map<string, string[]> {
  const out = new Map<string, string[]>();
  for (const [key, value] of input.entries()) {
    out.set(key, [...value].sort());
  }
  return out;
}

function parseScalar(raw: string, key: string): string | null {
  const match = new RegExp(`^${escapeRegExp(key)}:\\s*(.+)$`, "m").exec(raw);
  if (!match?.[1]) {
    return null;
  }
  return match[1].trim().replace(/^["']|["']$/g, "");
}

function parseInlineArray(raw: string, key: string): string[] {
  const match = new RegExp(`^\\s*${escapeRegExp(key)}:\\s*\\[([^\\]]*)\\]`, "m").exec(raw);
  if (!match?.[1]?.trim()) {
    return [];
  }
  return match[1]
    .split(",")
    .map((item) => item.trim().replace(/^["']|["']$/g, ""))
    .filter(Boolean)
    .sort();
}

function sameSet(a: string[], b: string[]): boolean {
  const left = [...a].sort();
  const right = [...b].sort();
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

function findLine(raw: string, key: string): number {
  const lines = raw.split(/\r?\n/);
  const index = lines.findIndex((line) => line.includes(`${key}:`));
  return index < 0 ? 1 : index + 1;
}

function cleanCell(value: string): string {
  return value
    .trim()
    .replace(/^`|`$/g, "")
    .replace(/\*\*/g, "")
    .trim();
}

function normalizeHeader(header: string): string {
  return cleanCell(header).toLowerCase().replace(/\s+/g, " ");
}

function normalizeSectionName(name: string): string {
  return name.trim().toLowerCase().replace(/\s+/g, " ");
}

function findSectionRanges(
  lines: string[],
): Array<{ name: string; start: number; end: number }> {
  const headings: Array<{ name: string; line: number }> = [];

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i] || "";
    const match = /^##+\s+(.+)$/.exec(line.trim());
    if (!match?.[1]) {
      continue;
    }

    headings.push({
      name: match[1].trim(),
      line: i,
    });
  }

  const sections: Array<{ name: string; start: number; end: number }> = [];
  for (let i = 0; i < headings.length; i += 1) {
    const current = headings[i];
    if (!current) {
      continue;
    }

    const next = headings[i + 1];
    sections.push({
      name: current.name,
      start: current.line + 1,
      end: next ? next.line : lines.length,
    });
  }

  return sections;
}

function walk(root: string): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const fullPath = join(root, entry.name);
    if (entry.isDirectory()) {
      out.push(...walk(fullPath));
    } else if (entry.isFile()) {
      out.push(fullPath);
    }
  }
  return out;
}

function isPlaceholder(value: string): boolean {
  return value.includes("{") && value.includes("}");
}

function suggestCanonicalEdges(
  value: string,
  signaturesById: Map<string, RelationshipSignature[]>,
): string[] {
  const normalized = value.trim().toLowerCase();
  if (!normalized) {
    return [];
  }

  return [...signaturesById.keys()]
    .filter((edge) => edge.includes(normalized) || normalized.includes(edge))
    .sort()
    .slice(0, 3);
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
