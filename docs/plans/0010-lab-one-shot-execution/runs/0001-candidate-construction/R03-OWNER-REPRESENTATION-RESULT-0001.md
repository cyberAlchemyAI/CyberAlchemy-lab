# Proposed owner representation for the final Lab review

**Status: candidate construction passed; not admitted.** The full plan remains **35/46 criteria** closed and **12/34 public APIs** implemented.

## What was found

The selected signed runtime source has 582 subjects but no Role, Role Assignment or Owner Registry instances. The canonical legacy owner registry contains 20 separate assignment rows; D29 binds its exact registry postimage. The absence is in runtime representation and selection, not a claim that the repository has no owner decisions.

## What was prepared

| Artifact | Count | State |
|---|---:|---|
| Role/v1 | 20 | draft, candidate unadmitted |
| Role Assignment/v1 | 20 | proposed, candidate unadmitted |
| Principal/v1 | 1 | proposed identity, candidate |
| Principal Reference/v1 | 1 | proposed declared identity link, candidate |

All 42 original JSON artifacts are in [owner-routing-v2](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/owner-routing-v2/artifacts/proposal.json). Their exact body hashes and original schema bindings are listed in the proposal. Separate target Decision cores remain to be prepared; none are represented as completed.

The legacy stable subject `person:<vrondelli>` is preserved. The new proposed `principal:legacy-owner-vrondelli` is distinct from `principal:repository-owner` and `principal:lab-owner`. No alias or authentication is inferred.

Each scope is an explicit protocol scope that retains the original prose. That prose is not converted into Project scope or runtime permission. New proposed assignment periods begin at the recorded proposal timestamp; the missing legacy period remains explicitly unknown. This changes no original operational Assignment period.

Principal/v1 requires an identity declaration. The new Principal Reference points to the new Principal, with reciprocal declared body links and an integrity digest of the exact Principal bytes. These declarations are not admitted Typed Relation instances or authentication evidence.

## All preserved owner scopes

| Original role | Original scope |
|---|---|
| artifact-mechanics-owner | Source direction, schema and generator binding mechanics; excludes semantic and admission decisions. |
| artifact-type-owner | Artifact Type/v1 contracts and registered type bindings; excludes source and definition admission. |
| definition-owner | Definition meaning, stable identity, registry postimages, and definition lifecycle decisions. |
| source-admission-owner | Exact external source selector admission; excludes semantic promotion and evidence validation. |
| evidence-conformance-owner | Independent evaluation contracts and receipts; excludes selecting semantic truth or granting admission. |
| lab-architecture-owner | Cross-context architecture, orthogonal identity axes, recursion boundaries, and repository placement policy; excludes context-local meaning, owner admission, migration execution, and implementation authority. |
| governance-context-owner | Governance Bounded Context identity, semantic boundary, domain-model scope, contracts, and challenge route; excludes Ontology Lifecycle meaning and cross-context relationship selection. |
| ontology-lifecycle-context-owner | Ontology Lifecycle Bounded Context identity, semantic boundary, event-history and replay model scope, contracts, and challenge route; excludes Governance authority meaning and cross-context relationship selection. |
| governance-language-owner | Governance context-local term, expression, relation, interpretation, and ambiguity bindings; excludes Ontology Lifecycle language and canonical Definition promotion. |
| ontology-lifecycle-language-owner | Ontology Lifecycle context-local term, expression, relation, interpretation, and ambiguity bindings; excludes Governance language and canonical Definition promotion. |
| coordination-context-owner | Recursive coordination-context identity, purpose, subject scope, consumer set, and bounded-context membership; excludes domain-model ownership and durable session-runtime authority. |
| context-map-owner | Versioned Context Map membership and explicit directional relationship contracts; excludes endpoint context admission and silent derivation of endpoint classifications. |
| capability-instance-owner | Exact capability-instance identity, extension scope, recursion stop, and instance-local authority claim; excludes parent Product Capability adoption, implementation binding acceptance, and conformance approval. |
| context-migration-owner | Context Migration Manifest scope, dispositions, dependency order, expected postimages, rollback boundary, and owner gates; excludes source admission, context admission, destructive execution, and publication. |
| context-lineage-owner | Historical predecessor and successor context identity evidence, preserved and changed scope, and challenge route; excludes inferring equivalence, admission, supersession, or migration completion. |
| craft-product-owner | Craft Product vocabulary, workflow interaction meaning, and Product lineage; excludes Definition admission, source admission, Governance Authority and Gate semantics, Bounded Context selection, implementation, publication, and deployment. |
| craft-project-owner | Craft Project identity, purpose, scope, goals, evidence coordination, and lifecycle decisions; excludes Product meaning, Method meaning, Definition admission, identity-graph membership, implementation, publication, and deployment. |
| craft-method-owner | Binding and applying the admitted Craft Method within an exact Product or Project scope; excludes changing Method Definition meaning, Product or Project ownership, execution authority, conformance, publication, and deployment. |
| craft-goal-owner | Craft Goal outcome, rationale, success conditions, evidence requirements, and lifecycle decision; excludes Project coordination, Product or Method meaning, execution authority, and treating validation as achievement. |
| identity-graph-owner | Exact typed relation kind, endpoints, membership, and graph consistency; excludes endpoint meaning or admission, ownership inference, context inference, implementation, publication, and deployment. |

## Actual example: Definition owner

One human can supply the Definition owner voice and the Artifact Type owner voice at the same final checkpoint. Each voice still resolves its own member, role, scope and evidence. An Agent does not generate that owner response.

This example is the actual materialized proposed Role:

```json
{
  "authority_boundary": "Exact original scope retained as prose; no permission inferred from this proposed Role.",
  "authority_effect": "none",
  "challenge_route": "protocol:owner-representation-review",
  "claim_ceiling": "Proposed representation of an exact legacy owner row. No admission, current Role Assignment, owner response, actor authentication or runtime grant.",
  "eligible_authority_relation_kinds": [],
  "exclusions": [
    "No implicit Principal aliases",
    "No current assignment or runtime grant",
    "No owner response"
  ],
  "functions": [
    "Definition meaning, stable identity, registry postimages, and definition lifecycle decisions."
  ],
  "kind": "role",
  "lifecycle_state": "draft",
  "name": "definition-owner",
  "node_id": "role:definition-owner",
  "owner_ref": "person:<vrondelli>",
  "owner_route": "protocol:owner-representation-review",
  "purpose": "Definition meaning, stable identity, registry postimages, and definition lifecycle decisions.",
  "responsibility_refs": [
    "protocol:legacy-owner-scope:CAL-ASSIGN-DEFINITION-OWNER"
  ],
  "scope_ref": "protocol:legacy-owner-scope:CAL-ASSIGN-DEFINITION-OWNER",
  "status": "candidate-unadmitted",
  "successor_refs": []
}
```

Its proposed assignment is:

```json
{
  "assignee_kind": "person-reference",
  "assignee_ref": "person:<vrondelli>",
  "assignment_basis_ref": "protocol:proposed-owner-representation:CAL-ASSIGN-DEFINITION-OWNER",
  "assignment_state": "proposed",
  "authority_claim_refs": [],
  "authority_effect": "none",
  "challenge_route": "protocol:owner-representation-review",
  "claim_ceiling": "Proposed representation of an exact legacy owner row. No admission, current Role Assignment, owner response, actor authentication or runtime grant.",
  "kind": "role-assignment",
  "node_id": "role-assignment:legacy:CAL-ASSIGN-DEFINITION-OWNER",
  "owner_ref": "person:<vrondelli>",
  "owner_route": "protocol:owner-representation-review",
  "period": {
    "end": null,
    "start": "2026-10-10T01:30:49Z"
  },
  "responsibility_refs": [
    "protocol:legacy-owner-scope:CAL-ASSIGN-DEFINITION-OWNER"
  ],
  "role_ref": "role:definition-owner",
  "scope_ref": "protocol:legacy-owner-scope:CAL-ASSIGN-DEFINITION-OWNER",
  "status": "candidate-unadmitted",
  "successor_refs": []
}
```

The `assignee_ref` equals the new Principal’s stable subject exactly. Its `assignment_state` is proposed and its authority claims are empty. It cannot satisfy a gate that requires a current admitted assignment.

## Verification and retained failures

- First frozen construction ran 11 checks and failed in schema setup: Principal/v1 requires a nonempty identity relationship. That source and complete failure log remain unchanged.
- The successor ran all 12 checks successfully: 42 exact existing schemas, all 20 original rows and scopes, identity closure, owned disk roundtrip, duplicate-role and assignment rejection, Principal alias rejection, voice separation and unknown-period handling.
- A 1,238-file frozen proof retains original sources, both attempts, actual terminal records, logs and every new original artifact byte.
- The separate Session diagnostics completed with failed test observations. They captured eligibility expiry during source/permission checks; instrumentation can affect timing. They are diagnosis evidence, not a full-suite verdict or a completed runtime repair.

## Remaining integration

1. Prepare each new target’s exact independent Decision core and declared dependencies. Retain every member in S02.
2. Implement public `proposal.review` with independently resolved governing roles, trusted host selection, durable idempotency and full original contract checks. Proposed assignments must never masquerade as current authority.
3. Finish the running full API suites, diagnose and repair remaining Session failures in an immutable successor, and qualify the complete source/SQLite/context integration.
4. Complete all remaining API and original task obligations; assemble S02 and present the exact package once at R08.

Candidate construction continues under existing authorization. Actual admission, existing-store operations, activation and publication retain their stated authority boundaries.

## Exact evidence

- [Frozen proof](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/owner-routing-v2/proof-0001.json)
- [Passing checks](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/owner-routing-v2/checks.json)
- [Complete check log](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/owner-routing-v2/checks-0001.log)
- [Construction context](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/context-R03-owner-representation-0002.json)
- [Canonical legacy owner registry](/home/vlad_/projects/CyberAlchemy-lab/authority/owners/foundation-01/v1/candidates/0004-craft-identity/owners.json)
