import { canonicalJson, digestValue } from "./canonical-json.js";
import { extractFacts } from "./extract.js";
import {
  fail,
  type FactProjection,
  type MintedGraph,
  type PropertyDefinition,
} from "./types.js";

export function validateProjection(
  graph: MintedGraph,
  property: PropertyDefinition,
  candidate: FactProjection,
): FactProjection {
  const expected = extractFacts(graph, property);
  const checks: readonly [unknown, unknown, string][] = [
    [candidate.nodes, expected.nodes, "node projection differs"],
    [candidate.edges, expected.edges, "edge projection differs"],
    [candidate.selected_edges, expected.selected_edges, "selected relation differs"],
    [candidate.atom_map, expected.atom_map, "canonical atom map differs"],
  ];
  for (const [observed, wanted, message] of checks) {
    if (canonicalJson(observed) !== canonicalJson(wanted)) {
      fail("FACT_PROJECTION_DRIFT", "projection", message);
    }
  }
  if (
    candidate.facts_digest !== digestValue({ nodes: candidate.nodes, edges: candidate.edges }) ||
    candidate.facts_digest !== expected.facts_digest ||
    candidate.universe_digest !== expected.universe_digest ||
    candidate.selected_relation_digest !== expected.selected_relation_digest ||
    candidate.scope_digest !== expected.scope_digest
  ) {
    fail("FACT_DIGEST_MISMATCH", "projection", "projection digest mismatch");
  }
  return candidate;
}

export function assertExactTupleDenominator(
  projected: readonly (readonly [string, string])[],
  translated: readonly (readonly [string, string])[],
): void {
  if (canonicalJson(projected) !== canonicalJson(translated)) {
    fail("FACT_PROJECTION_DRIFT", "translation", "provider translation omitted or invented tuples");
  }
}
