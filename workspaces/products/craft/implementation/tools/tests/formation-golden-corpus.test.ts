import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { validateMintedNodeFormation } from "../minted-project/meta-type-body-adapter";
import { compileMintedProject } from "../minted-project/compiler";

type GoldenCase = { id: string; kind: string; body: Record<string, unknown>; expected: string };
const implRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const corpus = JSON.parse(readFileSync(resolve(implRoot, "spec/minted-project/formation-golden-corpus.v1.json"), "utf8")) as { case_count: number; cases: GoldenCase[] };
const domainspecRoot = resolve(implRoot, "..");
const sha256 = (path: string) => createHash("sha256").update(readFileSync(path)).digest("hex");
const writeJson = (path: string, value: unknown) => writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);

test("all 26 DomainSpec formation cases execute through the canonical adapter", () => {
  assert.equal(corpus.cases.length, corpus.case_count);
  for (const item of corpus.cases) {
    const violations = validateMintedNodeFormation(item.kind, item.body, item.id);
    if (item.expected === "pass") assert.deepEqual(violations, [], item.id);
    else assert.ok(violations.some((violation) => violation.code === item.expected), `${item.id}: expected ${item.expected}; got ${violations.map((violation) => violation.code)}`);
  }
});

test("positive bodies do not pass when labeled as another backend meta-type", () => {
  const positives = corpus.cases.filter((item) => item.expected === "pass");
  assert.equal(positives.length, 13);
  let swaps = 0;
  for (const source of positives) for (const target of positives) {
    if (source.kind === target.kind) continue;
    swaps += 1;
    assert.notDeepEqual(validateMintedNodeFormation(target.kind, source.body, `${source.id}-as-${target.kind}`), [], `${source.kind} collapsed into ${target.kind}`);
  }
  assert.equal(swaps, 156);
});

test("unknown meta-types fail closed instead of selecting a nearby schema", () => {
  const violations = validateMintedNodeFormation("EntityLike", { fields: [{ name: "id", type: "string", identity: true }] }, "unknown");
  assert.equal(violations[0]?.code, "SCHEMA-MISSING");
});

test("a temporary development profile compiles all thirteen meta-types end to end", () => {
  const root = mkdtempSync(resolve(tmpdir(), "domainspec-thirteen-meta-types-"));
  try {
    mkdirSync(resolve(root, "nodes"));
    const positives = corpus.cases.filter((item) => item.expected === "pass");
    const schemaPaths = [
      "structural/entity", "structural/value-object", "structural/enum",
      "behavioral/operation", "behavioral/query", "behavioral/calculation", "behavioral/rule", "behavioral/policy", "behavioral/workflow",
      "connective/event", "connective/interface", "connective/mapping", "lifecycle/state-machine",
    ];
    const formationContracts = Object.fromEntries(positives.map((item, index) => [item.kind, { validator: "attribute-map", path: `impl/spec/meta-types/${schemaPaths[index]}.schema.yml` }]));
    const profilePath = resolve(root, "development-profile.json");
    const handle = "thirteen-meta-types-v0.1";
    writeJson(profilePath, {
      schema_version: "domainspec-development-minted-profile/v0.1", authority: "implementation-owned-development-profile", release_admission: "not-granted", handle,
      profile_binding: { path: "definitions/minted-project/supported-profiles.yml", sha256: sha256(resolve(domainspecRoot, "definitions/minted-project/supported-profiles.yml")), semantic_digest: "0".repeat(64) },
      registry_bindings: {
        kinds: { path: "definitions/meta-types/meta-types.yml", sha256: sha256(resolve(domainspecRoot, "definitions/meta-types/meta-types.yml")) },
        relationships: { path: "definitions/relationships/relationships.yml", sha256: sha256(resolve(domainspecRoot, "definitions/relationships/relationships.yml")) },
      },
      profiles: [{ id: "thirteen-meta-types", version: "0.1", status: "development-only", source_layout: "per-node-connections", kinds: positives.map((item) => item.kind), formation_contracts: formationContracts, relationships: [] }],
    });
    const nodeSources = positives.map((item, index) => `nodes/node-${index}.json`);
    writeJson(resolve(root, "feature.json"), { schema_version: "minted-feature/v1", feature_id: "meta-types", source_layout: "per-node-connections", node_sources: nodeSources });
    positives.forEach((item, index) => writeJson(resolve(root, nodeSources[index]), { schema_version: "minted-node/v1", node_id: `meta-types.Node${index}`, feature_id: "meta-types", kind: item.kind, intent: `Exercise ${item.kind}.`, body: item.body, connections: [] }));
    writeJson(resolve(root, "project.json"), {
      schema_version: "minted-project/v1", project_id: "meta-types",
      language: { profile: { id: "thirteen-meta-types", version: "0.1", digest: sha256(profilePath) }, registries: { kinds_digest: sha256(resolve(domainspecRoot, "definitions/meta-types/meta-types.yml")), relationships_digest: sha256(resolve(domainspecRoot, "definitions/relationships/relationships.yml")) } },
      features: ["feature.json"], generated_root: ".domainspec/generated",
    });
    const compiled = compileMintedProject(root, { developmentProfileRegistry: { path: profilePath, handle } });
    assert.equal(compiled.graph.nodes.length, 13);
    assert.deepEqual(new Set(compiled.graph.nodes.map((node) => node.kind)), new Set(positives.map((item) => item.kind)));
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
