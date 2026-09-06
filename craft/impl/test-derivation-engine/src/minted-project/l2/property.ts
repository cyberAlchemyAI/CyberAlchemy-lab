import { digestValue } from "./canonical-json.js";
import { fail, type PropertyDefinition } from "./types.js";

export const PROPERTY_ID =
  "evf.l2.financial-settlement.rule-to-payout-event-reachability";
export const PROPERTY_VERSION = "1";
export const REQUIRED_SOURCES = [
  "financial-settlement.NoDuplicateMakeupRule",
  "financial-settlement.PayoutEligibilityRule",
] as const;
export const TARGET = "financial-settlement.PayoutCreatedEvent";
export const SELECTED_PREDICATES = ["enforces", "produces"] as const;

export function validateProperty(property: PropertyDefinition): PropertyDefinition {
  if (
    property.schema_version !== "evf.graph-law-property/v1" ||
    property.property_id !== PROPERTY_ID ||
    property.property_version !== PROPERTY_VERSION ||
    property.property_class !== "reachability" ||
    property.result_semantics !== "universal-via-violation-query" ||
    property.evaluation_mode !== "exact-instance" ||
    property.subject.project_id !== "financial-settlement" ||
    property.subject.target !== TARGET ||
    property.selected_relation_digest_material.target !== TARGET ||
    property.selected_relation_digest_material.directed !== true ||
    property.selected_relation_digest_material.closure !==
      "non-reflexive-transitive-one-or-more" ||
    property.authority_effect !== "none" ||
    property.release_admission !== "not-granted"
  ) {
    fail("PROPERTY_DEFINITION_UNADMITTED", "admission", "property identity or claim boundary drifted", 2);
  }
  const same = (left: readonly string[], right: readonly string[]) =>
    left.length === right.length && left.every((entry, index) => entry === right[index]);
  if (
    !same(property.subject.required_sources, REQUIRED_SOURCES) ||
    !same(property.selected_relation_digest_material.required_sources, REQUIRED_SOURCES) ||
    !same(property.subject.selected_predicates, SELECTED_PREDICATES) ||
    !same(property.selected_relation_digest_material.selected_predicates, SELECTED_PREDICATES)
  ) {
    fail("PROPERTY_DEFINITION_UNADMITTED", "admission", "property domain or relation drifted", 2);
  }
  if (
    digestValue(property.selected_relation_digest_material) !==
    property.selected_relation_digest
  ) {
    fail("PROPERTY_DEFINITION_UNADMITTED", "admission", "selected relation digest is stale", 2);
  }
  return property;
}

export function isSelectedPredicate(value: string): boolean {
  return (SELECTED_PREDICATES as readonly string[]).includes(value);
}
