import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { FORMAL_IDENTITY_ALGORITHM_BYTES, businessAcceptanceSubjectDigest } from "../../src/formal-claim-lowering.js";
const sha = (text: string | Buffer) => createHash("sha256").update(text).digest("hex");
const canonical = (value: any): string => Array.isArray(value) ? `[${value.map(canonical).join(",")}]` : value && typeof value === "object" ? `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k])}`).join(",")}}` : JSON.stringify(value);
export const source = `domain commerce "Commerce"
profile application-v1
owner fixture-owner
formal-claim EligibleClaim:
  profile fol-core/1-candidate
  sort Order
  predicate Eligible(Order)
  proposition forall o: Order: Eligible(o)
  ceiling "Synthetic eligibility only."
rule EligibleOrder:
  claim EligibleClaim
`;

// Synthetic owner/acceptance records are fixture data, never an actual product decision.
export function formalLoweringFixture() {
  const sources = new Map<string, Buffer>();
  const put = (path: string, value: unknown) => {
    const bytes = Buffer.from(typeof value === "string" ? value : JSON.stringify(value));
    sources.set(path, bytes); return { path, sha256: sha(bytes), size_bytes: bytes.length, current: true as const };
  };
  const meaning = {
    schema_version: "domainspec-v2.business-meaning/v1-candidate", meaning_id: "Meaning:fixture", version: "1", owner: "fixture-owner", status: "accepted",
    domain_context: "Synthetic orders", rule: "An eligible order satisfies the declared condition", applies_when: ["fixture"], actors: [], inputs: ["Order"], outcomes: ["eligible"],
    examples: [{ case_id: "yes", given: "eligible order", when: "checked", then: "eligible", why: "fixture" }],
    counterexamples: [{ case_id: "no", given: "ineligible order", when: "checked", then: "ineligible", why: "fixture" }], boundaries: ["synthetic only"],
    acceptance: { status: "accepted", owner_ref: "fixture-owner", acceptance_ref: "", acceptance_digest: "" },
    claim_ceiling: "Synthetic only", authority_effect: "none",
  };
  const acceptMeaning = (value: typeof meaning, decisionPath = "fixture/acceptance.json") => {
    const acceptance = put(decisionPath, {
      schema_version: "domainspec-v2.business-acceptance-decision/v1-candidate",
      decision_id: "fixture-decision", owner: value.owner, outcome: "accepted",
      subject: { meaning_id: value.meaning_id, version: value.version,
        canonicalization: "domainspec-json-keysort-excluding-acceptance-v1", digest_algorithm: "sha256",
        digest: businessAcceptanceSubjectDigest(value) }, authority_effect: "none"
    });
    value.acceptance = { status: "accepted", owner_ref: value.owner, acceptance_ref: acceptance.path, acceptance_digest: acceptance.sha256 };
    return acceptance;
  };
  const acceptance = acceptMeaning(meaning);
  const business = put("fixture/meaning.json", meaning);
  const definition = { definition_id: "FIXTURE-ORDER", status: "accepted", term: "Order", definition_kind: "entity",
    formal: { definition: "A synthetic order", expression: "Order", notation: [{ symbol: "Order", meaning: "synthetic order" }], operational_interpretation: "fixture only" },
    plain_language: "Synthetic order", domain_context: "fixture", depends_on: [], business_fact_refs: ["#/rule"], interpretation_refs: ["#/types"], source_concept_refs: [], forbidden_collapses: ["Not production data"] };
  const authority = put("fixture/definitions.json", { definitions: [definition] });
  const graph = {
    schema_version: "domainspec-v2.formal-claim-definition-binding/v1-candidate", binding_id: "fixture-definition-binding",
    claim_identity: { claim_id: "FormalClaim:fixture", claim_version: "1" }, definition_authority_ref: authority,
    definition_nodes: [{ definition_id: definition.definition_id, definition_pointer: "#/definitions/0", status: "accepted", definition_digest: sha(canonical(definition)) }],
    relations: [{ relation_id: "fixture-uses-order", relation_type: "uses_definition", source_claim_id: "FormalClaim:fixture", target_definition_id: definition.definition_id,
      definition_pointer: "#/definitions/0", binding_effect: "semantic-dependency", inference: "explicit" }],
    definition_closure: { definition_ids: [definition.definition_id], canonicalization: "domainspec-json-keysort-v1", digest_algorithm: "sha256", digest: sha(canonical([definition])) },
    resolution_policy: { edge_source: "explicit-author-declaration", name_inference: "forbidden", missing_definition: "block", transitive_dependencies: "required", definition_body_authority: "definition_authority_ref" },
    authority_effect: "none", claim_ceiling: "Synthetic closure only",
  };
  const bindingRef = put("fixture/definition-binding.json", graph);
  const profile = put("fixture/profile.json", JSON.parse(readFileSync(new URL("../../../../../../../../craft/projects/domainspec-v2/formalization/profiles/formal-language-profiles.json", import.meta.url), "utf8")));
  const algorithm = put("fixture/identity.json", FORMAL_IDENTITY_ALGORITHM_BYTES);
  const input = { schema_version: "alchlang.formal-claim-bindings/v1", source_sha256: sha(source), owner: "fixture-owner",
    formal_claims: { EligibleClaim: { claim_id: "FormalClaim:fixture", claim_version: "1", supersedes: null,
      business_meaning_ref: business, business_acceptance_ref: acceptance, definition_binding_ref: bindingRef,
      formal_language_profile_ref: profile, identity_algorithm_ref: algorithm } } };
  return { sources, put, input, graph, definition, source, acceptMeaning };
}
