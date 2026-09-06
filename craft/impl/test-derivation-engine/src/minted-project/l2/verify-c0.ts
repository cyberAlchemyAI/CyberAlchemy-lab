import { readJson, repositoryRoot } from "./exact-ref.js";
import { extractFacts, validateLiveSourceBindings } from "./extract.js";
import { translateAlloy } from "./translate-alloy.js";
import { translateDatalog } from "./translate-datalog.js";
import { validateProjection } from "./validate-facts.js";
import type { EdgeFact, NodeFact } from "./types.js";

export function verifyC0(repoRoot = repositoryRoot()): {
  readonly status: "pass";
  readonly facts_digest: string;
  readonly universe_digest: string;
  readonly scope_digest: string;
  readonly node_count: number;
  readonly edge_count: number;
} {
  const { graph, property } = validateLiveSourceBindings(repoRoot);
  const projection = validateProjection(graph, property, extractFacts(graph, property));
  const expectedNodes = readJson<{ nodes: readonly NodeFact[] }>(
    repoRoot,
    "projects/domainspec-v2/development/evolvable-validation-framework/fixtures/SWU-GCP-004-C0/expected-node-facts.json",
  );
  const expectedEdges = readJson<{ edges: readonly EdgeFact[] }>(
    repoRoot,
    "projects/domainspec-v2/development/evolvable-validation-framework/fixtures/SWU-GCP-004-C0/expected-edge-facts.json",
  );
  if (
    JSON.stringify(projection.nodes) !== JSON.stringify(expectedNodes.nodes) ||
    JSON.stringify(projection.edges) !== JSON.stringify(expectedEdges.edges)
  ) throw new Error("C0 fixture denominator drift");
  translateDatalog(projection, property);
  translateAlloy(projection, property);
  return {
    status: "pass",
    facts_digest: projection.facts_digest,
    universe_digest: projection.universe_digest,
    scope_digest: projection.scope_digest,
    node_count: projection.nodes.length,
    edge_count: projection.edges.length,
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    process.stdout.write(`${JSON.stringify(verifyC0())}\n`);
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = typeof error === "object" && error !== null && "exitCode" in error
      ? Number((error as { exitCode: number }).exitCode)
      : 1;
  }
}
