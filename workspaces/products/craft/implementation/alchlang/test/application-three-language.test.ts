import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { compileApplicationWhole } from "../src/application-whole.js";
import { wholeApplicationFixtureForLanguage } from "./fixtures/application-whole-fixture.js";

const languages = ["typescript", "python", "rust"] as const;

function materialize(root: string, files: Readonly<Record<string, string>>): void {
  for (const [relative, bytes] of Object.entries(files)) {
    const file = path.join(root, relative);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, bytes);
  }
}

function normalizedOutcome(result: ReturnType<typeof compileApplicationWhole>) {
  const providers = result.application.artifacts.find(row => row.relative_path === ".domainspec/providers/manifest.json");
  assert.ok(providers);
  const providerManifest = JSON.parse(providers.content);
  const graph = result.runtimeBinding.binding.application_graph;
  return {
    integration_source_sha256: result.runtimeBinding.binding.integration_source_sha256,
    nodes: graph.nodes.map((row: any) => [row.node_id, row.node_kind, row.node_origin, row.semantic_sha256]).sort(),
    edges: graph.edges.map((row: any) => [row.edge_id, row.relationship, row.relationship_authority, row.source_node_id, row.target_node_id]).sort(),
    operation_requests: graph.operation_requests.map((row: any) => [row.request_ref, row.operation_ref]).sort(),
    runtime_bindings: graph.runtime_bindings.map((row: any) => [row.binding_id, row.mapping_ref]).sort(),
    providers: Object.entries(providerManifest.providers).map(([role, provider]: [string, any]) => [role, provider.provider_id]).sort(),
    persistence: result.executable.persistence!.trace.references,
    messaging: result.executable.messaging!.trace.references,
    external_api: result.executable.externalApi!.trace.references,
  };
}

test("one Alch application forms the same persistence, messaging and API semantics for all three explicit targets", async t => {
  const outcomes: unknown[] = [];
  for (const language of languages) {
    const fixture = await wholeApplicationFixtureForLanguage(language);
    const root = fs.mkdtempSync(path.join(os.tmpdir(), `alch-c05-${language}-`));
    t.after(() => fs.rmSync(root, { recursive: true, force: true }));
    materialize(root, fixture.candidate.projectFiles);
    const graph = fixture.compiler.compileProject(root).graph;
    const result = compileApplicationWhole(fixture.candidate, graph, fixture.observation, fixture.compiler);
    assert.equal(result.wholeApplication.language, language);
    assert.equal(result.application.language, language);
    assert.equal(result.application.runtime_guarantees_observed, false);
    assert.deepEqual(result.runtimeBinding.providers.map((row: any) => [
      row.role,
      row.binding_ref,
      row.logical_boundary_ref,
      row.provider.provider_id,
    ]).sort(), [
      ["inbound_http", "binding:payment-webhook-endpoint", "commerce:submit-order", "http:inbound"],
      ["messaging", "binding:consume-order-submitted", "commerce:receive-notice", "nats:jetstream"],
      ["messaging", "binding:publish-order-submitted", "commerce:order-submitted", "nats:jetstream"],
      ["outbound_http", "binding:authorize-payment-api", "commerce:order-api", "http:outbound"],
      ["persistence", "binding:order-persistence", "commerce:order", "postgresql:16"],
    ]);
    assert.ok(result.application.artifacts.some(row => row.relative_path.includes("providers/reference/persistence")));
    assert.ok(result.application.artifacts.some(row => row.relative_path.includes("providers/reference/messaging")));
    assert.ok(result.application.artifacts.some(row => row.relative_path.includes("providers/reference/inbound")));
    const inbound = result.application.artifacts.find(row => row.relative_path.includes("providers/reference/inbound"));
    assert.ok(inbound);
    assert.match(inbound.content, /"\/orders"/);
    assert.doesNotMatch(inbound.content, /"\/webhook"/);
    assert.ok(result.application.artifacts.some(row => row.relative_path.includes("providers/reference/outbound")));
    outcomes.push(normalizedOutcome(result));
  }
  assert.deepEqual(outcomes[1], outcomes[0]);
  assert.deepEqual(outcomes[2], outcomes[0]);
});
