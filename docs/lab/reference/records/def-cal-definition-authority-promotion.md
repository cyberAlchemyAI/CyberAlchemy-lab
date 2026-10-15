[Documentation home](../../README.md)

# Authority Promotion

<a id="def-cal-definition-authority-promotion"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Authority Promotion

# Authority Promotion

A staged route from source evidence and a proposal to owner-reviewed authority. Generalizing domain work requires additional exercise, challenge and review; later adoption has its own scope.

**When it applies**

Use when a new authority-bearing kind needs a promotion path: reuse a named instance (`D43`/`D46`/Growth Rule) or justify a new lifecycle. It turns "how does this earn authority?" into a declared, owner-routed path.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-authority-promotion-section-2"></a>

## Source explanatory wording

Domains can teach the base, but one local success cannot rewrite the base or another domain. The idea must survive evidence, a materially different context, challenge, CAV2 owner review, and separate adoption.

<a id="def-cal-definition-authority-promotion-section-3"></a>

## Exact governing statement

Authority Promotion is the normalized definition identified by semantic.authority-promotion, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D48 without silently merging it with another target.

Bound source-semantic basis:

Authority promotion lifecycle is the single staged path by which any authority-bearing candidate may acquire authority — `source evidence -> candidate -> owner-routed review -> promoted authority -> (optional) invariant/constitution pressure` — with per-stage gates, an owner route, and a stopping/demotion rule. It is the generalization that `Promotion policy`'s ladder instantiates and that `CAV2-D43` (patterns), `CAV2-D46` (experience), and the Arcanum Discipline Growth Rule (disciplines) are instances of.

When an authority-bearing candidate originates in a domain and is proposed as reusable CAV2 authority, the minimum generalization path is:

```text domain-owned source or candidate -> originating-domain exercise and evidence -> CAV2 import candidate -> generalized proposal with changes and residue stated -> exercise in another independently owned domain or materially distinct context -> challenge and contrary-evidence review -> CAV2 owner decision -> promoted, versioned CAV2 authority -> separate adoption by each domain that chooses to use that version ```

This branch applies to domain-originated definitions, rules, methods, specifications, knowledge structures, validators, and patterns proposed for CAV2-wide reuse only through an existing authority kind and its owner route. Proof objects, Lean results, Cedar or Datalog results, tests, observations, and receipts may support such a candidate as evidence; they do not self-promote.

````
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
````

- Not "everything has a lifecycle" — scoped to **authority-bearing kinds**. Evidence (`CAV2-D34` / non-collapse rule 1), residue (`CAV2-D18`), ledger events, one-off logs, and generated projections are inputs or terminal artifacts, not lifecycle-bearing. The originating domain retains authority over its local object. CAV2 promotion creates CAV2 authority for one named version; it neither rewrites the originating domain nor activates that version in another domain. Each domain owner makes a separate, version-exact adoption decision. The exact upstream provenance record and any later adoption record are separate events with separate owners. They do not create a permanent semantic adapter, synchronized crosswalk, mapping owner, or live coupling between CAV2 and a domain. Naming this lifecycle does **not** enact deterministic enforcement. Closure is enacted in review mode by `CAV2-D49` plus the [AUTHORITY-MODEL catch-all row](Authority model#authority-kinds); its deterministic kind-enumeration scan remains pending.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/authority-promotion/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.authority-promotion@1.0.0-candidate.1

**Content fingerprint · SHA-256**

ddf9a7b42b4847bd5d4042e3c297b5a0742e9050fa7d03478a467904ba87a8e7

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use when a new authority-bearing kind needs a promotion path: reuse a named\ninstance (`D43`/`D46`/Growth Rule) or justify a new lifecycle. It turns \"how does\nthis earn authority?\" into a declared, owner-routed path.\n\nFor a domain-originated proposal, keep four decisions separate: the originating\ndomain owns its local meaning and submission posture; the exercising domain owns\nits bounded result; the CAV2 owner decides CAV2 promotion; and each consuming\ndomain decides whether to adopt the promoted version. A failed cross-context\nexercise narrows, revises, or rejects the CAV2 proposal and leaves visible\nresidue; it does not erase the original domain object.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
