import { digestValue } from "./canonical-json.js";
import { assertExactTupleDenominator } from "./validate-facts.js";
import { fail, type FactProjection, type PropertyDefinition } from "./types.js";

function field(value: string): string {
  if (/[\t\r\n]/u.test(value)) {
    fail("FACT_PROJECTION_DRIFT", "translation", "Datalog fact field contains a delimiter");
  }
  return value;
}

function lines(rows: readonly (readonly string[])[]): string {
  return rows.map((row) => row.map(field).join("\t")).join("\n") + "\n";
}

export type DatalogTranslation = {
  readonly files: {
    readonly "Node.facts": string;
    readonly "Edge.facts": string;
    readonly "RequiredSource.facts": string;
    readonly "Target.facts": string;
  };
  readonly selected_tuples: readonly (readonly [string, string])[];
  readonly translation_digest: string;
};

export function translateDatalog(
  projection: FactProjection,
  property: PropertyDefinition,
): DatalogTranslation {
  const files = {
    "Node.facts": lines(
      projection.nodes.map((node) => [node.node_id, node.feature_id, node.kind]),
    ),
    "Edge.facts": lines(
      projection.edges.map((edge) => [
        edge.edge_id,
        edge.predicate,
        edge.from,
        edge.to,
      ]),
    ),
    "RequiredSource.facts": lines(
      property.subject.required_sources.map((source) => [source]),
    ),
    "Target.facts": lines([[property.subject.target]]),
  };
  const translated = projection.edges
    .filter((edge) => property.subject.selected_predicates.includes(edge.predicate))
    .map((edge) => [edge.from, edge.to] as const)
    .filter(
      (entry, index, all) =>
        all.findIndex(([from, to]) => from === entry[0] && to === entry[1]) === index,
    )
    .sort((left, right) =>
      left[0] < right[0] ? -1 : left[0] > right[0] ? 1 :
      left[1] < right[1] ? -1 : left[1] > right[1] ? 1 : 0
    );
  assertExactTupleDenominator(projection.selected_edges, translated);
  return {
    files,
    selected_tuples: translated,
    translation_digest: digestValue({
      provider: "souffle-2.5",
      facts_digest: projection.facts_digest,
      selected_relation_digest: projection.selected_relation_digest,
      files,
    }),
  };
}
