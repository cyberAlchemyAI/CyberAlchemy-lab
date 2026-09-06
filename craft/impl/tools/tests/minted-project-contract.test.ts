import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, isAbsolute, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

type JsonObject = Record<string, any>;

interface SchemaViolation {
  keyword: string;
  path: string;
  detail: string;
}

interface ContractManifest {
  schemas: Array<{
    file: string;
    schema_id: string;
    record: string;
    role: string;
    authority: string;
    version: string;
  }>;
}

interface SupportedProfile {
  id: string;
  version: string;
  status: string;
  source_layout: string;
  kinds: string[];
  formation_schemas: Record<string, string>;
  relationships: Array<{
    id: string;
    source_kind: string;
    target_kind: string;
    registry_status: string;
  }>;
}

interface SupportedProfiles {
  schema_version: string;
  registry_bindings: {
    kinds: { path: string; sha256: string };
    relationships: { path: string; sha256: string };
  };
  profiles: SupportedProfile[];
}

const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../..");
const domainspecRoot = resolve(implRoot, "..");
const schemaRoot = resolve(implRoot, "spec/minted-project");
const profilePath = resolve(domainspecRoot, "definitions/minted-project/supported-profiles.yml");
const fixtureRoot = resolve(
  implRoot,
  "test-derivation-engine/__fixtures__/minted-project/contract",
);
const positiveRoot = resolve(fixtureRoot, "positive/key-and-door");

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function sha256File(path: string): string {
  return sha256(readFileSync(path));
}

function canonicalize(value: any): string {
  if (Array.isArray(value)) {
    return `[${value.map(canonicalize).join(",")}]`;
  }
  if (value !== null && typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalize(value[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function isObject(value: unknown): value is JsonObject {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function hasProjectPathEscape(value: string): boolean {
  return (
    isAbsolute(value) ||
    /^[A-Za-z]:/.test(value) ||
    value.split(/[\\/]/).some((segment) => segment === "..")
  );
}

function validateSchema(
  schemaPath: string,
  value: unknown,
  instancePath = "$",
): SchemaViolation[] {
  const schema = readJson<JsonObject>(schemaPath);
  return validateValue(schema, value, instancePath, dirname(schemaPath));
}

function validateValue(
  schema: JsonObject,
  value: unknown,
  path: string,
  schemaDir: string,
): SchemaViolation[] {
  if (typeof schema.$ref === "string") {
    const referencedPath = resolve(schemaDir, schema.$ref);
    return validateSchema(referencedPath, value, path);
  }

  const violations: SchemaViolation[] = [];
  const fail = (keyword: string, detail: string): void => {
    violations.push({ keyword, path, detail });
  };

  if (Array.isArray(schema.allOf)) {
    for (const entry of schema.allOf) {
      if (isObject(entry)) {
        violations.push(...validateValue(entry, value, path, schemaDir));
      }
    }
  }
  if (isObject(schema.if) && isObject(schema.then)) {
    if (validateValue(schema.if, value, path, schemaDir).length === 0) {
      violations.push(...validateValue(schema.then, value, path, schemaDir));
    }
  }

  if (schema.type !== undefined) {
    const matches =
      (schema.type === "object" && isObject(value)) ||
      (schema.type === "array" && Array.isArray(value)) ||
      (schema.type === "string" && typeof value === "string") ||
      (schema.type === "boolean" && typeof value === "boolean") ||
      (schema.type === "number" && typeof value === "number") ||
      (schema.type === "integer" && Number.isInteger(value));
    if (!matches) {
      fail("type", `expected ${schema.type}`);
      return violations;
    }
  }

  if (schema.const !== undefined && !Object.is(value, schema.const)) {
    fail("const", `expected ${JSON.stringify(schema.const)}`);
  }
  if (Array.isArray(schema.enum) && !schema.enum.some((entry: unknown) => Object.is(entry, value))) {
    fail("enum", `expected one of ${JSON.stringify(schema.enum)}`);
  }

  if (typeof value === "string") {
    if (typeof schema.minLength === "number" && value.length < schema.minLength) {
      fail("minLength", `expected at least ${schema.minLength} characters`);
    }
    if (typeof schema.pattern === "string" && !new RegExp(schema.pattern).test(value)) {
      fail("pattern", `does not match ${schema.pattern}`);
    }
    if (schema["x-project-relative-path"] === true && hasProjectPathEscape(value)) {
      fail("x-project-relative-path", "path must remain under the consumer project root");
    }
  }

  if (Array.isArray(value)) {
    if (typeof schema.minItems === "number" && value.length < schema.minItems) {
      fail("minItems", `expected at least ${schema.minItems} items`);
    }
    if (schema.uniqueItems === true) {
      const identities = value.map(canonicalize);
      if (new Set(identities).size !== identities.length) {
        fail("uniqueItems", "array contains duplicate values");
      }
    }
    if (isObject(schema.items)) {
      value.forEach((entry, index) => {
        violations.push(...validateValue(schema.items, entry, `${path}[${index}]`, schemaDir));
      });
    }
    if (
      isObject(schema.contains) &&
      !value.some((entry) => validateValue(schema.contains, entry, path, schemaDir).length === 0)
    ) {
      fail("contains", "no array item satisfies the required formation condition");
    }
  }

  if (isObject(value)) {
    if (typeof schema.minProperties === "number" && Object.keys(value).length < schema.minProperties) {
      fail("minProperties", `expected at least ${schema.minProperties} properties`);
    }
    if (Array.isArray(schema.required)) {
      for (const required of schema.required as string[]) {
        if (!(required in value)) {
          violations.push({ keyword: "required", path, detail: `missing ${required}` });
        }
      }
    }
    const properties = isObject(schema.properties) ? schema.properties : {};
    for (const [key, entry] of Object.entries(value)) {
      if (key in properties && isObject(properties[key])) {
        violations.push(...validateValue(properties[key], entry, `${path}.${key}`, schemaDir));
      } else if (schema.additionalProperties === false) {
        violations.push({ keyword: "additionalProperties", path, detail: `unexpected ${key}` });
      }
    }
  }

  return violations;
}

function assertValid(schemaFile: string, value: unknown): void {
  const violations = validateSchema(resolve(schemaRoot, schemaFile), value);
  assert.deepEqual(violations, [], JSON.stringify(violations, null, 2));
}

function renderIndex(manifest: ContractManifest, profile: SupportedProfile): string {
  const kinds = profile.kinds.map((kind) => `\`${kind}\``).join(", ");
  const relationships = profile.relationships
    .map(
      (relationship) =>
        `\`${relationship.id}\` (${relationship.source_kind}→${relationship.target_kind})`,
    )
    .join(", ");
  const schemaRows = manifest.schemas.map(
    (schema) =>
      `| \`${schema.file}\` | \`${schema.schema_id}\` | \`${schema.record}\` | \`${schema.role}\` | \`${schema.authority}\` | \`${schema.version}\` |`,
  );
  const formationPath = (kind: string): string =>
    profile.formation_schemas[kind].replace("impl/spec/minted-project/", "");

  return [
    "# Minted Project Contract Index",
    "",
    "Generated from `contract-manifest.json` and",
    "`definitions/minted-project/supported-profiles.yml`. The contract test rejects",
    "manual drift between this human view and those machine sources.",
    "",
    "## Authority",
    "",
    "- Profile admission: `definitions/minted-project/supported-profiles.yml`.",
    "- Source and generated record form: this directory's JSON Schemas.",
    "- Concrete domain meaning: the minted consumer project's source records.",
    "- Graph, provenance, Markdown, and receipts: generated read models only.",
    "",
    "## Experimental Profile",
    "",
    "| Profile | Version | Status | Layout | Kinds | Relationships |",
    "| --- | --- | --- | --- | --- | --- |",
    `| \`${profile.id}\` | \`${profile.version}\` | \`${profile.status}\` | \`${profile.source_layout}\` | ${kinds} | ${relationships} |`,
    "",
    `Formation schemas: \`Entity\` → \`${formationPath("Entity")}\`, \`Event\` →`,
    `\`${formationPath("Event")}\`, \`Operation\` →`,
    `\`${formationPath("Operation")}\`, \`Rule\` →`,
    `\`${formationPath("Rule")}\`.`,
    "",
    "Registry bindings use SHA-256 over the exact current bytes of",
    "`definitions/meta-types/meta-types.yml` and",
    "`definitions/relationships/relationships.yml`. The project and build receipt",
    "also bind the exact supported-profile registry digest.",
    "",
    "## Contract Family",
    "",
    "| File | Schema ID | Record | Role | Authority | Version |",
    "| --- | --- | --- | --- | --- | --- |",
    ...schemaRows,
    "",
    "## Boundary Rules",
    "",
    "1. A source connection owns `edge_id`, `type`, and `to`; its containing node",
    "   supplies `from` during normalization.",
    "2. Profile membership is separate from kind existence and relationship status.",
    "3. Every project path is relative and must remain below the consumer root.",
    "4. Generated artifacts carry explicit generated authority posture and are never",
    "   repaired by hand.",
    "5. Digests are lowercase SHA-256. A source-set digest hashes canonical JSON for",
    "   the sorted `{path,digest}` input records with a final newline.",
    "",
  ].join("\n");
}

function sourceSetDigest(inputs: Array<{ path: string; digest: string }>): string {
  const sorted = [...inputs].sort((left, right) => left.path.localeCompare(right.path));
  return sha256(`${canonicalize(sorted)}\n`);
}

function assertLanguageBinding(
  project: JsonObject,
  registry: SupportedProfiles,
  profileDigest: string,
): SupportedProfile {
  const profile = registry.profiles.find(
    (candidate) =>
      candidate.id === project.language.profile.id &&
      candidate.version === project.language.profile.version,
  );
  assert.ok(profile, "profile-language-mismatch: unsupported profile id/version");
  assert.equal(
    project.language.profile.digest,
    profileDigest,
    "profile-language-mismatch: profile digest",
  );
  assert.equal(
    project.language.registries.kinds_digest,
    registry.registry_bindings.kinds.sha256,
    "profile-language-mismatch: kinds registry digest",
  );
  assert.equal(
    project.language.registries.relationships_digest,
    registry.registry_bindings.relationships.sha256,
    "profile-language-mismatch: relationships registry digest",
  );
  return profile;
}

function assertUnique(values: string[], code: string): void {
  assert.equal(new Set(values).size, values.length, code);
}

function runNegativeCase(path: string, expectedError: string, registry: SupportedProfiles): void {
  const fixture = readJson<JsonObject>(path);
  if (expectedError === "duplicate-id") {
    const ids = fixture.records.map((record: JsonObject) => `${record.record_type}:${record.id}`);
    if (new Set(ids).size !== ids.length) {
      throw new Error("duplicate-id");
    }
    return;
  }

  const violations = validateSchema(resolve(schemaRoot, fixture.record_schema), fixture.record);
  if (expectedError === "missing-machine-field") {
    if (violations.some((entry) => entry.keyword === "required" && entry.detail === "missing intent")) {
      throw new Error("missing-machine-field");
    }
  } else if (expectedError === "source-path-escape") {
    if (violations.some((entry) => entry.path.endsWith(".features[0]"))) {
      throw new Error("source-path-escape");
    }
  } else if (expectedError === "generated-authority-field") {
    if (
      violations.some(
        (entry) =>
          entry.keyword === "additionalProperties" && entry.detail === "unexpected authority",
      )
    ) {
      throw new Error("generated-authority-field");
    }
  } else if (expectedError === "profile-language-mismatch") {
    assert.deepEqual(violations, []);
    assertLanguageBinding(fixture.record, registry, sha256File(profilePath));
  }
  throw new Error(`negative-control-did-not-produce:${expectedError}`);
}

test("machine contract manifest, schemas, and profile registry agree", () => {
  const manifest = readJson<ContractManifest>(resolve(schemaRoot, "contract-manifest.json"));
  const registry = readJson<SupportedProfiles>(profilePath);
  assert.equal(registry.schema_version, "domainspec-supported-profiles/v1");
  assert.equal(registry.profiles.length, 1);
  assert.equal(registry.profiles[0].status, "experimental");
  assert.deepEqual(registry.profiles[0].kinds, ["Entity", "Event", "Operation", "Rule"]);
  assert.deepEqual(registry.profiles[0].formation_schemas, {
    Entity: "impl/spec/minted-project/formations/entity-body.schema.json",
    Event: "impl/spec/minted-project/formations/event-body.schema.json",
    Operation: "impl/spec/minted-project/formations/operation-body.schema.json",
    Rule: "impl/spec/minted-project/formations/rule-body.schema.json",
  });
  assert.deepEqual(
    registry.profiles[0].relationships.map(({ id, source_kind, target_kind }) => ({
      id,
      source_kind,
      target_kind,
    })),
    [
      { id: "enforces", source_kind: "Rule", target_kind: "Operation" },
      { id: "performs", source_kind: "Entity", target_kind: "Operation" },
      { id: "produces", source_kind: "Operation", target_kind: "Event" },
    ],
  );
  assert.equal(
    registry.registry_bindings.kinds.sha256,
    sha256File(resolve(domainspecRoot, registry.registry_bindings.kinds.path)),
  );
  assert.equal(
    registry.registry_bindings.relationships.sha256,
    sha256File(resolve(domainspecRoot, registry.registry_bindings.relationships.path)),
  );
  assert.equal(manifest.schemas.length, 12);
  for (const entry of manifest.schemas) {
    const schema = readJson<JsonObject>(resolve(schemaRoot, entry.file));
    assert.equal(schema.$id, entry.schema_id);
    assert.deepEqual(schema["x-domainspec"], {
      record: entry.record,
      role: entry.role,
      authority: entry.authority,
      version: entry.version,
      ...(entry.record === "connection" ? { derived_fields: ["from"] } : {}),
    });
  }
});

test("human contract index is an exact machine-derived view", () => {
  const manifest = readJson<ContractManifest>(resolve(schemaRoot, "contract-manifest.json"));
  const registry = readJson<SupportedProfiles>(profilePath);
  assert.equal(
    readFileSync(resolve(schemaRoot, "INDEX.md"), "utf8"),
    renderIndex(manifest, registry.profiles[0]),
  );
});

test("Key and Door closes source, graph, provenance, view, and receipt bindings", () => {
  const registry = readJson<SupportedProfiles>(profilePath);
  const project = readJson<JsonObject>(resolve(positiveRoot, "project.json"));
  assertValid("project.schema.json", project);
  const profile = assertLanguageBinding(project, registry, sha256File(profilePath));

  const featurePath = project.features[0] as string;
  const feature = readJson<JsonObject>(resolve(positiveRoot, featurePath));
  assertValid("feature.schema.json", feature);
  assert.equal(feature.source_layout, profile.source_layout);
  const nodes: Array<{ path: string; node: JsonObject }> = (
    feature.node_sources as string[]
  ).map((nodePath: string) => {
    const projectRelativePath = `${dirname(featurePath)}/${nodePath}`;
    const node = readJson<JsonObject>(resolve(positiveRoot, projectRelativePath));
    assertValid("node.schema.json", node);
    assert.equal(node.feature_id, feature.feature_id);
    assert.ok(profile.kinds.includes(node.kind), `unsupported profile kind: ${node.kind}`);
    return { path: projectRelativePath, node };
  });

  assertUnique(nodes.map(({ node }) => node.node_id), "duplicate-id:node");
  const nodeById = new Map<string, JsonObject>(
    nodes.map(({ node }) => [node.node_id as string, node]),
  );
  const sourceEdges: JsonObject[] = nodes.flatMap(({ node }) =>
    node.connections.map((connection: JsonObject) => ({ ...connection, from: node.node_id })),
  );
  assertUnique(sourceEdges.map((edge) => edge.edge_id), "duplicate-id:edge");
  for (const edge of sourceEdges) {
    const source = nodeById.get(edge.from);
    const target = nodeById.get(edge.to);
    assert.ok(source, `unknown source endpoint: ${edge.from}`);
    assert.ok(target, `unknown target endpoint: ${edge.to}`);
    assert.ok(
      profile.relationships.some(
        (relationship) =>
          relationship.id === edge.type &&
          relationship.registry_status === "active" &&
          relationship.source_kind === source.kind &&
          relationship.target_kind === target.kind,
      ),
      `relationship outside evaluated profile: ${edge.edge_id}`,
    );
  }

  const expectedRoot = resolve(positiveRoot, "expected");
  const graph = readJson<JsonObject>(resolve(expectedRoot, "graph.json"));
  const sourceManifest = readJson<JsonObject>(resolve(expectedRoot, "source-manifest.json"));
  const markdownView = readJson<JsonObject>(resolve(expectedRoot, "markdown-view.json"));
  const buildReceipt = readJson<JsonObject>(resolve(expectedRoot, "build-receipt.json"));
  assertValid("graph.schema.json", graph);
  assertValid("source-manifest.schema.json", sourceManifest);
  assertValid("markdown-view.schema.json", markdownView);
  assertValid("build-receipt.schema.json", buildReceipt);

  const byId = (left: JsonObject, right: JsonObject): number =>
    (left.node_id ?? left.edge_id).localeCompare(right.node_id ?? right.edge_id);
  assert.deepEqual(
    [...graph.nodes].sort(byId),
    nodes
      .map(({ node }) => {
        const {
          connections: _connections,
          schema_version: _schemaVersion,
          ...normalized
        } = node;
        return normalized;
      })
      .sort(byId),
  );
  assert.deepEqual([...graph.edges].sort(byId), [...sourceEdges].sort(byId));

  for (const input of sourceManifest.inputs) {
    assert.equal(input.digest, sha256File(resolve(positiveRoot, input.path)), input.path);
  }
  assert.equal(sourceManifest.source_set_digest, sourceSetDigest(sourceManifest.inputs));
  assert.equal(graph.source_set_digest, sourceManifest.source_set_digest);
  const graphIds = [
    ...graph.nodes.map((node: JsonObject) => node.node_id),
    ...graph.edges.map((edge: JsonObject) => edge.edge_id),
  ].sort();
  assertUnique(graphIds, "duplicate-id:graph");
  assert.deepEqual(
    sourceManifest.records.map((record: JsonObject) => record.graph_id).sort(),
    graphIds,
  );
  const digestByPath = new Map(
    sourceManifest.inputs.map((input: JsonObject) => [input.path, input.digest]),
  );
  for (const record of sourceManifest.records) {
    assert.equal(record.source_digest, digestByPath.get(record.source_path));
  }

  assert.equal(markdownView.graph_digest, sha256File(resolve(expectedRoot, "graph.json")));
  assert.equal(markdownView.content_digest, sha256File(resolve(expectedRoot, "SPEC.md")));
  assert.equal(buildReceipt.status, "pass");
  assert.equal(buildReceipt.source_set_digest, sourceManifest.source_set_digest);
  assert.deepEqual(buildReceipt.language, {
    profile_id: profile.id,
    profile_version: profile.version,
    profile_digest: sha256File(profilePath),
    kinds_digest: registry.registry_bindings.kinds.sha256,
    relationships_digest: registry.registry_bindings.relationships.sha256,
  });
  assert.deepEqual(buildReceipt.artifacts, {
    graph_digest: sha256File(resolve(expectedRoot, "graph.json")),
    source_manifest_digest: sha256File(resolve(expectedRoot, "source-manifest.json")),
    markdown_view_digest: sha256File(resolve(expectedRoot, "markdown-view.json")),
    markdown_content_digest: sha256File(resolve(expectedRoot, "SPEC.md")),
  });
});

test("five named negative controls fail for five distinct contract reasons", () => {
  const registry = readJson<SupportedProfiles>(profilePath);
  const manifest = readJson<JsonObject>(resolve(fixtureRoot, "negative/manifest.json"));
  assert.deepEqual(
    manifest.cases.map((entry: JsonObject) => entry.id),
    [
      "missing-machine-field",
      "duplicate-id",
      "source-path-escape",
      "profile-language-mismatch",
      "generated-authority-field",
    ],
  );
  for (const entry of manifest.cases) {
    assert.throws(
      () => runNegativeCase(resolve(fixtureRoot, "negative", entry.path), entry.expected_error, registry),
      new RegExp(entry.expected_error),
      entry.id,
    );
  }
});

test("generic contract schemas do not contain consumer-domain semantics", () => {
  const manifest = readJson<ContractManifest>(resolve(schemaRoot, "contract-manifest.json"));
  const genericFiles = [
    ...manifest.schemas.map((entry) => resolve(schemaRoot, entry.file)),
    resolve(schemaRoot, "contract-manifest.json"),
    resolve(schemaRoot, "INDEX.md"),
  ];
  const forbidden = ["financial-settlement", "agent-execution-orchestrator"];
  for (const file of genericFiles) {
    const content = readFileSync(file, "utf8").toLowerCase();
    for (const term of forbidden) {
      assert.ok(!content.includes(term), `${file} leaked consumer term ${term}`);
    }
  }
});
