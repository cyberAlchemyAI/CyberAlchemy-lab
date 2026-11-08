import { digest, json } from "../../src/domainspec-profile.js";
import { lowerApplicationDomain } from "../../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections } from "../../src/application-rule-projection.js";
import { formalLoweringFixture } from "./formal-lowering-fixture.js";

/** Explicit synthetic author choices, not compiler defaults or accepted product meaning. */
export function executableFixture() {
  const f = formalLoweringFixture();
  const source = f.source.replace("  proposition forall o: Order: Eligible(o)", "  constant current: Order\n  proposition Eligible(current)") + `formal-claim IdentityClaim:
  profile fol-core/1-candidate
  sort Identity
  constant identity: Identity
  proposition identity = identity
  ceiling "Synthetic typed identity reflexivity only."
rule IdentityValid:
  claim IdentityClaim
entity Order:
  id UInt64
  identity id
  accepted Bool
operation SubmitOrder:
  input Order
  output Order
  reads Order
  writes Order
  requires EligibleOrder
`;
  const identityGraph = structuredClone(f.graph);
  identityGraph.binding_id = "fixture-identity-binding";
  identityGraph.claim_identity.claim_id = "FormalClaim:identity";
  identityGraph.relations[0]!.source_claim_id = "FormalClaim:identity";
  const identityRef = f.put("fixture/identity-definition-binding.json", identityGraph);
  const claimBindings = { ...f.input.formal_claims,
    IdentityClaim: { ...f.input.formal_claims.EligibleClaim, claim_id: "FormalClaim:identity", definition_binding_ref: identityRef } };
  const bindings = { schema_version: "alchlang.application-bindings/v1", source_sha256: digest(source), owner: "fixture-owner",
    formal: { ...f.input, source_sha256: digest(source), formal_claims: claimBindings }, declarations: {
      Order: { ontology: "FIXTURE-ORDER", meaning: "Synthetic order.", properties: {
        id: { ontology: "FIXTURE-ORDER#id", meaning: "Typed identity." }, accepted: { ontology: "FIXTURE-ORDER#accepted", meaning: "Eligibility flag." } } },
      EligibleOrder: { ontology: "FIXTURE-ELIGIBILITY", meaning: "Explicit current-order eligibility." },
      IdentityValid: { ontology: "FIXTURE-IDENTITY", meaning: "Typed identity reflexivity, without additional business restrictions." },
      SubmitOrder: { ontology: "FIXTURE-SUBMIT", meaning: "Replace an eligible existing order with the supplied value.", failure_continuation: "return-submission-error" },
    } };
  const formation = lowerApplicationDomain(source, bindings, f.sources);
  const claimIdentity = (id: string) => formation.trace.declarations.find(c => c.source_id === id)!.identity_inputs_digest;
  const interpretation = { schema_version: "alchlang.ground-rule-interpretation/v1-candidate", formation_sha256: digest(json(formation)), rules: {
    EligibleOrder: { claim_identity_inputs_digest: claimIdentity("EligibleClaim"), context_id: "fixture-current-order", ceiling: "Ground eligibility only.",
      sorts: { Order: "Order" }, constants: { current: "order" }, predicates: { Eligible: "accepted" } },
    IdentityValid: { claim_identity_inputs_digest: claimIdentity("IdentityClaim"), context_id: "fixture-uint64-identity", ceiling: "Typed identity reflexivity only.",
      sorts: { Identity: "UInt64" }, constants: { identity: "identity" }, predicates: {} },
  } };
  const projection = lowerApplicationRuleProjections(source, bindings, f.sources, interpretation);
  const named = { kind: "named", selector: "commerce:order" };
  const at = (root: string, ...properties: string[]) => ({ op: "path", root, properties });
  const execution = { schema_version: "alchlang.application-execution/v1-candidate", projection_sha256: digest(json(projection)), selection: {
    schema_version: "domainspec.reconciled-compilation/v1-candidate", profile_id: "domainspec.reconciled-typescript/v1-candidate", language: "typescript",
    module_root: "application", layout_version: "domainspec.existing-profile-layout/v1-candidate", value_profile: "domainspec.typescript-exact-uint64/v1",
    field_bindings: [], factories: [{ selector: "commerce:order", base_validators: [{ rule: "commerce:identity-valid", arguments: [{ parameter: "identity", field: "id" }] }], extensions: [] }],
    operations: [{ schema_version: "domainspec.operation-action-bindings/v1-candidate", selector: "commerce:submit-order",
      inputs: [{ name: "request", type: named }], reads: [{ slot: "commerce:order", target: "commerce:order", parameter: "current", key: at("request", "FIXTURE-ORDER#id") }],
      guards: [{ selector: "commerce:eligible-order", arguments: [{ parameter: "order", value: at("current") }] }],
      writes: [{ slot: "commerce:order", target: "commerce:order", mode: "replace", value: at("request") }], events: [],
      result: { type: named, value: at("request") }, atomicity: "state-and-outbox", continuation: "awaited-settlement" }], workflows: [],
  } };
  return { source, bindings, sources: f.sources, interpretation, execution };
}
