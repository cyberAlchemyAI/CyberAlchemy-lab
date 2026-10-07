# Reference slice review

## Proposed model

The candidate contains `28` primary artifact instances, `21` semantic histories, `21` governance histories, `12` Ontology Nodes, `9` Ontology Edges, and `44` global Typed Relations.

The primary path is:

1. Product `product:cyberalchemy-lab` defines the durable value boundary.
2. Project `project:cyberalchemy-v2-to-lab-migration` coordinates the bounded v2 migration and contributes to the Product.
3. Product Capability `product-capability:cyberalchemy-lab:governed-knowledge-lifecycle` states the repeatable outcome.
4. Implementation `implementation:cyberalchemy-lab-governed-repository-toolchain` realizes that Capability without becoming it.
5. Research Inquiry `research-inquiry:v2-to-lab-semantic-preservation` asks the bounded question.
6. Experiment Design `experiment-design:reference-slice-contract-validation` tests `hypothesis:reference-slice-preserves-orthogonality`; Experiment Run `experiment-run:reference-slice-contract-validation:2026-10-06` realizes the Design.
7. Evidence Set `evidence-set:reference-slice-validation` derives from the Run; Finding `finding:reference-slice-schema-and-relation-closure` derives from the Evidence Set and answers the Inquiry only within its claim ceiling.
8. Agent Instance `agent-instance:reference-slice-authoring:2026-10-06` acts for `principal:repository-owner` within Agent Session `agent-session:reference-slice-authoring:2026-10-06` and performs the Work and validation Run.
9. Durable continuity remains Project State `project-state:cyberalchemy-v2-to-lab-migration:decision-0070`. The Agent consumes bounded Context and Ontology Views selected from that state.

## Real Typed Relation example

```json
{
  "authority_effect": "none",
  "challenge_route": "challenge-contract:cyberalchemy-lab-reference-slice",
  "claim_ceiling": "Candidate global Typed Relation for the exact reference slice endpoints; validation creates no connection authority or runtime effect.",
  "evidence_refs": [
    "evidence-set:reference-slice-validation"
  ],
  "kind": "typed-relation",
  "lifecycle_state": "candidate",
  "name": "Reference slice relation.realizes",
  "node_id": "typed-relation:reference-slice:implementation-realizes-capability",
  "owner_ref": "role:repository-owner",
  "payload": {
    "qualifiers": {
      "exact_target_version_ref": "product-capability:cyberalchemy-lab:governed-knowledge-lifecycle@candidate.1",
      "realization_role": "repository-toolchain"
    },
    "relation_evidence_refs": [
      "evidence-set:reference-slice-validation"
    ],
    "relation_kind_ref": "relation.realizes",
    "relation_lifecycle_state": "candidate",
    "source": {
      "kind": "implementation",
      "ref": "implementation:cyberalchemy-lab-governed-repository-toolchain",
      "version_ref": "implementation:cyberalchemy-lab-governed-repository-toolchain@candidate.1"
    },
    "target": {
      "kind": "product-capability",
      "ref": "product-capability:cyberalchemy-lab:governed-knowledge-lifecycle",
      "version_ref": "product-capability:cyberalchemy-lab:governed-knowledge-lifecycle@candidate.1"
    }
  },
  "relation_refs": [],
  "schema_version": "cyberalchemy-lab-typed-relation/v2",
  "scope_ref": "scope:cyberalchemy-lab-reference-slice",
  "successor_refs": []
}
```

This relation says only that one implementation realizes one Product Capability at an exact target version. It does not establish conformance, effectiveness, adoption, activation, or Product value.

## Agent memory rule demonstrated

The Agent Instance is ephemeral. Short memory is embedded inside `agent-session:reference-slice-authoring:2026-10-06` with `expires_with_session: true`. Long-term continuity belongs to `project-state:cyberalchemy-v2-to-lab-migration:decision-0070` and is selected through `context-view:reference-slice-authoring:2026-10-06` plus `ontology-view:cyberalchemy-lab-reference-slice:2026-10-06`.

## Review boundary

This is a validated candidate example. It admits no artifact or relation, activates no Agent or runtime, performs no migration or cutover, and requires a separate exact owner-reviewed admission proposal.
