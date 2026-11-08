import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  loadRelationshipAuthority,
  validateRelationshipSpecFile,
  type RelationshipSignature,
} from "../lib/relationship-signatures";
import { validateJsonSchema } from "../minted-project/schema-validator";
import { parseUiProfile } from "../validate-ui-profile";

type NodeSource = {
  node_id: string;
  feature_id: string;
  kind: string;
  body: Record<string, any>;
  connections: Array<{ edge_id: string; type: string; to: string }>;
};

const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../..");
const featureRoot = resolve(implRoot, "spec/features/ui-profile-create-player");
const nodeRoot = resolve(featureRoot, "nodes");
const relationships = loadRelationshipAuthority(
  resolve(implRoot, "../definitions/relationships/relationships.yml"),
);
const profile = parseUiProfile(
  readFileSync(resolve(implRoot, "spec/ui-profile/profile.yml"), "utf8"),
);

function json<T = any>(path: string): T {
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

function nodes(): NodeSource[] {
  return readdirSync(nodeRoot)
    .filter((name) => name.endsWith(".json"))
    .sort()
    .map((name) => json<NodeSource>(join(nodeRoot, name)));
}

function signatureTypes(signature: RelationshipSignature, side: "source" | "target"): string[] {
  const singular = side === "source" ? signature.source_type : signature.target_type;
  const plural = side === "source" ? signature.source_types : signature.target_types;
  return singular ? [singular] : plural ?? [];
}

function endpointAdmitted(type: string, sourceKind: string, targetKind: string): boolean {
  return (relationships.signaturesById.get(type) ?? []).some(
    (signature) =>
      signatureTypes(signature, "source").includes(sourceKind) &&
      signatureTypes(signature, "target").includes(targetKind),
  );
}

test("feature manifest enumerates one valid source file per stable node", () => {
  const feature = json<any>(resolve(featureRoot, "feature.json"));
  assert.deepEqual(
    validateJsonSchema(resolve(implRoot, "spec/minted-project/feature.schema.json"), feature),
    [],
  );
  assert.equal(feature.source_layout, "per-node-connections");
  assert.equal(feature.node_sources.length, 17);
  assert.equal(new Set(feature.node_sources).size, 17);
  assert.deepEqual(
    [...feature.node_sources].sort(),
    readdirSync(nodeRoot)
      .filter((name) => name.endsWith(".json"))
      .map((name) => `nodes/${name}`)
      .sort(),
  );

  const seen = new Set<string>();
  for (const source of feature.node_sources as string[]) {
    const node = json<NodeSource>(resolve(featureRoot, source));
    assert.deepEqual(
      validateJsonSchema(resolve(implRoot, "spec/minted-project/node.schema.json"), node),
      [],
      source,
    );
    assert.equal(node.feature_id, feature.feature_id);
    assert.equal(seen.has(node.node_id), false, node.node_id);
    seen.add(node.node_id);
  }
});

test("every authored machine connection is active and endpoint-admitted", () => {
  const allNodes = nodes();
  const byId = new Map(allNodes.map((node) => [node.node_id, node]));
  const edgeIds = new Set<string>();
  let edges = 0;
  for (const source of allNodes) {
    for (const connection of source.connections) {
      const target = byId.get(connection.to);
      assert.ok(target, `${connection.edge_id} target missing`);
      assert.equal(edgeIds.has(connection.edge_id), false, connection.edge_id);
      edgeIds.add(connection.edge_id);
      assert.equal(
        endpointAdmitted(connection.type, source.kind, target!.kind),
        true,
        `${source.kind} --${connection.type}--> ${target!.kind}`,
      );
      edges += 1;
    }
  }
  assert.equal(edges, 20);
  const operation = byId.get("ui-profile-create-player.CreatePlayer")!;
  assert.equal("creation_targets" in operation.body, false);
  assert.ok(operation.connections.some((connection) => connection.type === "creates"));
  assert.equal(operation.connections.some((connection) => connection.type === "produces-for"), false);
  const generated = json<any>(resolve(featureRoot, "generated/graph.json"));
  const generatedOperation = generated.nodes.find(
    (node: NodeSource) => node.node_id === "ui-profile-create-player.CreatePlayer",
  );
  assert.deepEqual(generatedOperation.body.creation_targets, ["ui-profile-create-player.Player"]);
});

test("traceability covers all eleven required concepts without node coercion", () => {
  const trace = json<any>(resolve(featureRoot, "traceability.json"));
  assert.equal(trace.concepts.length, 11);
  assert.deepEqual(
    trace.concepts.map((entry: any) => entry.id).sort(),
    profile.concepts.map((entry) => entry.id).sort(),
  );
  const byId = new Map(nodes().map((node) => [node.node_id, node]));
  const adapter = trace.concepts.find((entry: any) => entry.id === "DS-D1.24");
  const adapterNode = byId.get(adapter.records[0])!;
  assert.equal(adapter.representation, "alias");
  assert.equal(adapterNode.kind, "Mapping");
  assert.equal(adapterNode.body.profile_metadata.ui_concept, "Adapter");
  assert.equal(nodes().some((node) => node.kind === "Adapter"), false);

  const state = trace.concepts.find((entry: any) => entry.id === "DS-D1.25");
  assert.equal(state.representation, "split");
  assert.equal(nodes().some((node) => node.kind === "State Indicator"), false);
  const domain = json<any>(resolve(featureRoot, state.records[0]));
  const request = json<any>(resolve(featureRoot, state.records[1]));
  assert.equal(domain.representation, "projection");
  assert.equal(byId.get(domain.target_node)?.kind, "State Machine");
  assert.equal(request.representation, "role");
  assert.equal(byId.get(request.target_node)?.kind, "Component");
  assert.ok(byId.get(request.target_node)?.body.profile_roles.includes("async-request-indicator"));
});

test("unresolved endpoint pressure remains typed residue and absent from graph", () => {
  const residue = json<any>(resolve(featureRoot, "residue.json"));
  assert.equal(residue.authority_effect, "none");
  assert.deepEqual(
    residue.items.map((item: any) => item.id),
    [
      "UIP-RES-SHAPES",
      "UIP-RES-REFLECTS",
      "UIP-RES-ACTION-BINDING",
      "UIP-RES-HOOK-BINDING",
      "UIP-RES-COMPONENT-FORM",
    ],
  );
  const edgeTypes = nodes().flatMap((node) => node.connections.map((connection) => connection.type));
  assert.equal(edgeTypes.includes("shapes"), false);
  assert.equal(edgeTypes.includes("reflects"), false);
  assert.ok(residue.items.every((item: any) => item.status === "owner-decision-required"));
});

test("synchronized Markdown view passes DS-D8 endpoint validation", () => {
  const result = validateRelationshipSpecFile(resolve(featureRoot, "SPEC.md"), relationships);
  assert.equal(result.violations.length, 0, JSON.stringify(result.violations, null, 2));
  assert.equal(result.edgesChecked, 20);
});

test("named endpoint mutants fail without changing source files", () => {
  assert.equal(endpointAdmitted("renders", "Page", "Form"), false);
  assert.equal(endpointAdmitted("shapes", "Mapping", "View Model"), false);
  assert.equal(endpointAdmitted("reflects", "Component", "State Machine"), false);
  assert.equal(endpointAdmitted("mutates", "Binding", "Query"), false);
  assert.equal(endpointAdmitted("invented-ui-edge", "Component", "Form"), false);
});
