import { digestValue } from "./canonical-json.js";
import { assertExactTupleDenominator } from "./validate-facts.js";
import { fail, type FactProjection, type PropertyDefinition } from "./types.js";

export type AlloyTranslation = {
  readonly model: string;
  readonly command_label: "NoViolation";
  readonly exact_scope: { readonly Node: number };
  readonly selected_tuples: readonly (readonly [string, string])[];
  readonly model_digest: string;
};

export function translateAlloy(
  projection: FactProjection,
  property: PropertyDefinition,
): AlloyTranslation {
  const atom = (id: string): string => {
    const value = projection.atom_map[id];
    if (value === undefined) {
      fail("PROVIDER_SCOPE_INVALID", "translation", `missing Alloy atom for ${id}`);
    }
    return value;
  };
  const atoms = projection.nodes.map((node) => atom(node.node_id));
  const tuples = projection.selected_edges.map(([from, to]) => [from, to] as const);
  assertExactTupleDenominator(projection.selected_edges, tuples);
  const relation = tuples.map(([from, to]) => `${atom(from)}->${atom(to)}`).join(" + ") || "none";
  const sources = property.subject.required_sources.map(atom).join(" + ");
  const target = atom(property.subject.target);
  const model = [
    "module evf_l2_exact_instance",
    "",
    "abstract sig Node {}",
    `one sig ${atoms.join(", ")} extends Node {}`,
    "",
    `fun SelectedEdge : Node -> Node { ${relation} }`,
    `fun RequiredSource : set Node { ${sources} }`,
    `fun Target : one Node { ${target} }`,
    "",
    "fun Reach : Node -> Node { ^SelectedEdge }",
    "pred Violation[r: Node] { r in RequiredSource and Target not in r.Reach }",
    "assert NoViolation { no r: RequiredSource | Violation[r] }",
    `check NoViolation for exactly ${atoms.length} Node`,
    "",
  ].join("\n");
  const exactScope = { Node: atoms.length };
  return {
    model,
    command_label: "NoViolation",
    exact_scope: exactScope,
    selected_tuples: tuples,
    model_digest: digestValue({
      provider: "alloy-6.2.0",
      solver: "sat4j",
      facts_digest: projection.facts_digest,
      selected_relation_digest: projection.selected_relation_digest,
      scope_digest: projection.scope_digest,
      exact_scope: exactScope,
      model,
    }),
  };
}
