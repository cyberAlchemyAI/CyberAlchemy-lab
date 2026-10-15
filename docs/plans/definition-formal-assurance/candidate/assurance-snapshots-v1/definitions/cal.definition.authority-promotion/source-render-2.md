<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Authority Promotion

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.authority-promotion`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.shared-authority`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Authority Promotion is the normalized definition identified by semantic.authority-promotion, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D48 without silently merging it with another target.

Bound source-semantic basis:

Authority promotion lifecycle is the single staged path by which any
authority-bearing candidate may acquire authority — `source evidence -> candidate
-> owner-routed review -> promoted authority -> (optional) invariant/constitution
pressure` — with per-stage gates, an owner route, and a stopping/demotion rule. It
is the generalization that `../promotion-policy.md`'s ladder instantiates and that
`CAV2-D43` (patterns), `CAV2-D46` (experience), and the Arcanum Discipline Growth
Rule (disciplines) are instances of.

When an authority-bearing candidate originates in a domain and is proposed as
reusable CAV2 authority, the minimum generalization path is:

```text
domain-owned source or candidate
  -> originating-domain exercise and evidence
  -> CAV2 import candidate
  -> generalized proposal with changes and residue stated
  -> exercise in another independently owned domain or materially distinct context
  -> challenge and contrary-evidence review
  -> CAV2 owner decision
  -> promoted, versioned CAV2 authority
  -> separate adoption by each domain that chooses to use that version
```

This branch applies to domain-originated definitions, rules, methods,
specifications, knowledge structures, validators, and patterns proposed for
CAV2-wide reuse only through an existing authority kind and its owner route.
Proof objects, Lean results, Cedar or Datalog results, tests, observations, and
receipts may support such a candidate as evidence; they do not self-promote.

```text
```text
APL = (stages, per_stage_gates, owner_route, stop_rule)
instances = { CAV2-D43, CAV2-D46, Discipline Growth Rule }
promotion-policy ladder = the cross-kind default

generalized_for_CAV2(c, d0)
  => origin_owner(c) = d0
  and exercised_in(c, d0)
  and exists d1: independently_owned(d1)
                 and materially_distinct(d1, d0)
                 and exercised_in(c, d1)
  and challenge_reviewed(c)
  and CAV2_owner_promoted(c)

promoted_in_CAV2(c, version) =/=> adopted_by_domain(c, version, d)
```

A kind's lifecycle is valid only when it names its stages, gates, owner route, and
stop/demotion rule; `CAV2-D38` bounds any claim of completed promotion to the
evidence.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.authority-promotion | Stable normalized identity for Authority Promotion. |
| CAV2-D48 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- Not "everything has a lifecycle" — scoped to **authority-bearing kinds**. Evidence
(`CAV2-D34` / non-collapse rule 1), residue (`CAV2-D18`), ledger events, one-off
logs, and generated projections are inputs or terminal artifacts, not
lifecycle-bearing. The originating domain retains authority over its local
object. CAV2 promotion creates CAV2 authority for one named version; it neither
rewrites the originating domain nor activates that version in another domain.
Each domain owner makes a separate, version-exact adoption decision.

The exact upstream provenance record and any later adoption record are separate
events with separate owners. They do not create a permanent semantic adapter,
synchronized crosswalk, mapping owner, or live coupling between CAV2 and a
domain.

Naming this lifecycle does **not** enact deterministic enforcement. Closure is
enacted in review mode by `CAV2-D49` plus the
[AUTHORITY-MODEL catch-all row](../AUTHORITY-MODEL.md#authority-kinds); its
deterministic kind-enumeration scan remains pending.

### Testable conditions

- The candidate identity remains cal.definition.authority-promotion.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

Domains can teach the base, but one local success cannot rewrite the base or
another domain. The idea must survive evidence, a materially different context,
challenge, CAV2 owner review, and separate adoption.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Authority Promotion is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2 this is the parent of the per-kind lifecycles already promoted
(`D43` patterns, `D46` experience) and the disciplines ladder. Naming it is
**build-from-owned**: the shape is visible across owned sources but the unifying
object is named in none of them, so this is a generalization inference — owner-gated,
not a mechanical lift (review CR-4).

Candidate Mint/Foundry experiment evidence illustrates the autonomy boundary:
domains may inherit CAV2's organizing machinery while owning and improving
their local content. DomainSpec, Lean, Cedar, Datalog, and other formal or
operational work may therefore propose reusable methods or knowledge without
transferring their source semantics or treating a checker result as a CAV2
promotion decision.

### Examples

- Resolve semantic.authority-promotion by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Authority Promotion.

## Applicability

Use when a new authority-bearing kind needs a promotion path: reuse a named
instance (`D43`/`D46`/Growth Rule) or justify a new lifecycle. It turns "how does
this earn authority?" into a declared, owner-routed path.

For a domain-originated proposal, keep four decisions separate: the originating
domain owns its local meaning and submission posture; the exercising domain owns
its bounded result; the CAV2 owner decides CAV2 promotion; and each consuming
domain decides whether to adopt the promoted version. A failed cross-context
exercise narrows, revises, or rejects the CAV2 proposal and leaves visible
residue; it does not erase the original domain object.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- Not "everything has a lifecycle" — scoped to **authority-bearing kinds**. Evidence
(`CAV2-D34` / non-collapse rule 1), residue (`CAV2-D18`), ledger events, one-off
logs, and generated projections are inputs or terminal artifacts, not
lifecycle-bearing. The originating domain retains authority over its local
object. CAV2 promotion creates CAV2 authority for one named version; it neither
rewrites the originating domain nor activates that version in another domain.
Each domain owner makes a separate, version-exact adoption decision.

The exact upstream provenance record and any later adoption record are separate
events with separate owners. They do not create a permanent semantic adapter,
synchronized crosswalk, mapping owner, or live coupling between CAV2 and a
domain.

Naming this lifecycle does **not** enact deterministic enforcement. Closure is
enacted in review mode by `CAV2-D49` plus the
[AUTHORITY-MODEL catch-all row](../AUTHORITY-MODEL.md#authority-kinds); its
deterministic kind-enumeration scan remains pending.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D48 | ## CAV2-D48: Authority Promotion Lifecycle | `cbcae7a26d4d78577a870b3b6e41861b403c7b01a53b961300fe31cf82035457` | `candidate-unadmitted` |

## Primary consumers

- semantic.artifact
- semantic.canonical-representation-invariant
- semantic.closed-authority-kind-invariant
- semantic.hypothesis
- semantic.parent-instance-authority-separation-invariant
- semantic.premise
- semantic.schema

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.authority-promotion@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.authority-promotion | cyberalchemy-v2:CAV2-D48 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-authority-promotion/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
