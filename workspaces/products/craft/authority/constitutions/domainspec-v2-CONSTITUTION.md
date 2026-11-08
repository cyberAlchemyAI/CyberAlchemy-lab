<!-- MINT-ACT OUTPUT (L1) for domainspec-v2. Cast from templates/constitution.md. INTERNAL/private.
     This file IS the localized home of method authority (source posture, promotion, non-collapse,
     layering law, convergence) — owned here, NOT delegated to any framework. INHERITS the meta-rules
     (claim<=evidence, finding-to-development, status-non-collapse, anti-laundering, load-bearing-term
     tracking); LOCALIZES the object rules (the 3 governances). The per-rule reformulation of v1's
     CONSTITUTION.md C1-C11 (impl/spec/CONSTITUTION.md) is REFORMULATION-PENDING (IMPORT-MANIFEST). -->

# DomainSpec v2 Credibility Constitution

Status: active local constitution
Owner: constitution-governance
Authority level: repository-local constitution
Selectors: `**`

## Scope

This constitution governs the credibility of DomainSpec v2 work. **It is the local home of method
authority** (source posture, promotion discipline, non-collapse, layering law, convergence
judgement) — owned here, NOT delegated to v1 or to CyberAlchemy v2.

## Governance Grouping (split plan)

The rules below are **pre-tagged by governance** (the `⟵ domain-originated (…)` labels). This table is
the **split manifest**: the rules stay in this one file for now and move to per-governance artifacts when
the reformulation lands. **Timing decision (2026-06-30, owner via `constitution-governance` split mode):**
split **at reformulation (OQ-2)**, not before — layering and drift are one rule each today, so separate
files now would be placeholders. Until then the grouping is explicit here and the seam is mechanical.

| Group → split target | Owner route | Rules |
| --- | --- | --- |
| **Base / credibility** — stays in `domainspec-v2-CONSTITUTION.md` | `constitution-governance` | C1–C4, C8, C12, C(meta-1..4) |
| `constitutions/validation-governance-CONSTITUTION.md` | `validation-governance` | C5, C9, C10, C11 |
| `constitutions/layering-governance-CONSTITUTION.md` | `layering-governance` | C6 |
| `constitutions/drift-governance-CONSTITUTION.md` | `drift-governance` | C7 |

- **Composition order** (narrowest first): task-pack → governance constitution → this base → repo default.
- **Edge-Law cross-binding — preserve on split:** C6 (layering = the *law*) and C11 (validation = the
  *check* of that law) are coupled; on split, keep an explicit C6↔C11 reference so the law→check→trend
  chain (see `AUTHORITY-MODEL.md` "Governance Chain") is not lost across files.
- **Do not over-fragment:** split by governance, never per-rule.

## Rules

### domainspec-v2-C1. Primary Source Boundary
Validation mode: review

The official primary source is the DomainSpec v2 root authority and definition surface plus
the per-feature pack. Root `authority/` owns governance; root `definitions/` owns canonical
language terms, relationship/edge-signature authority, and tracked load-bearing definitions.
Implementation artifacts under `impl/` are implementation surfaces, executable consumers, or
projections/views of root authority unless a root owner decision explicitly promotes one.
Every other source is supporting, related, analogy, local inference, or open residue. v1 and
cav2 are supporting (harvested precedent), never authority.

### domainspec-v2-C2. Claim ≤ Evidence
Validation mode: review

No artifact may claim a safer, more complete, more proven, or more "validated/converged" result
than the cited evidence supports.

### domainspec-v2-C3. Candidate Before Commitment
Validation mode: review

A proposed obligation, layer-rule, or convergence-criterion stays in research/candidate state until
its source, derivation, and authority gates are named (promotion-policy).

### domainspec-v2-C4. Separation Of Concerns
Validation mode: review

Validation governance, layering governance, and drift governance are kept separate; and the spec,
the implementation, and governance authority are kept separate unless an external owner decision
explicitly binds them.

### domainspec-v2-C5. Derivation Is From The Spec ⟵ *domain-originated (validation, Obs-A rule-level)*
Validation mode: hybrid

Every derived obligation and its EXPECTED value is read **from the spec**, never by running the
implementation (no circular self-validation). A passing derived test is **build-time fidelity**,
necessary but **not** runtime conformance and **not** correctness.

### domainspec-v2-C6. Forbidden Edges Are Unconstructible ⟵ *domain-originated (layering, Obs-A rule-level)*
Validation mode: hybrid

A relation the layer-law / Edge-Law forbids must be **unconstructible** (typed so no catalog edge
admits the endpoint pair), not merely flagged after the fact. No dependency may cross the adapter
line ([AXIOMS A2](../AXIOMS.md#axiom-a2-decisions-belong-to-the-domain-not-adapters)). A layer
*assignment* is not a dependency-law *verdict*.

### domainspec-v2-C7. Convergence Is A Trend, Not A Signal ⟵ *domain-originated (drift, Obs-A rule-level)*
Validation mode: hybrid

Convergence is an evidence-backed reduction of drift over time across the relevant surface(s) — never
a single passing check. **No modeling surface may hold a write-edge to a node's promotion-status**
(the write-authority proviso). Saturn (the control loop) acts on drift; it is not the authority that
defines it.

### domainspec-v2-C8. Open-Core Boundary ⟵ *domain-originated (Obs-A rule-level)*
Validation mode: review

The deterministic engine's **results and behavior are free/citable**; its `src/rules` δ-algorithm is
**withheld** (an optimization edge, kept private — never published to public `arcanum/`). Demonstration
is not disclosure. The defensible moat is attestation + governance-data, not the engine algorithm.

### domainspec-v2-C9. Link & Import Integrity ⟵ *validation governance (build-from-owned)*
Validation mode: hybrid

Every doc link and cross-doc reference in a feature pack must resolve to a real target; a broken link or
dangling import **blocks**. Method: `validate-doc-links.ts` (v1-owned; Batch-2 import per
`IMPORT-MANIFEST.md`). Link integrity is a build-time fidelity check — it proves references resolve, not
that the referenced content is correct.

### domainspec-v2-C10. Spec Completeness ⟵ *validation governance (build-from-owned)*
Validation mode: hybrid

A typed spec is **complete** only when its required canonical tables are present and well-formed AND every
Formal cell is deterministically classifiable — no unresolved `needs-formal` / `coverage_gap`. Method:
engine `lint` (non-canonical-tables + needs-formal classes). Completeness is **distinct from C5**: C5
governs WHERE expected values come from (the spec, not the impl); C10 governs whether the spec is WHOLE.
Completeness is necessary, not sufficient, for correctness.

> **Edge Law — the LAW is layering's, the CHECK is validation's.** The *authority* over which typed
> edges are admissible is **layering governance** (rule C6 — forbidden edges unconstructible); the act
> of *confirming* a spec's declared relations conform to it is **validation** (rule C11 below, method
> `validate-relationships.ts`). kind × governance: one validator serving the layering law via a
> validation check — the ratified governance chain (layering=law → validation=check) made concrete.

### domainspec-v2-C11. Relationship / Edge-Law Conformance ⟵ *validation governance (build-from-owned)*
Validation mode: hybrid

Every declared relation in a feature pack must conform to the layering **edge-law** — the
`RELATIONSHIPS.md` typed-edge vocabulary + endpoint signatures; a non-conforming or forbidden edge
**blocks**. Method: `validate-relationships.ts` (v1-owned; Batch-2 import per `IMPORT-MANIFEST.md`).
This is the **check** side of the chain; the **law** it enforces is owned by layering governance (C6).
Conformance proves a relation is *admissible*, not that the related concepts are correct.

### domainspec-v2-C12. Independent Structural Approval Is A Pre-Merge Gate
Validation mode: hybrid

Rondelli is the DomainSpec v2 semantic and primary owner. Victor Boscaro is the
distinct structural verifier. Victor's approval is not required to accept
Define, Design, or Plan artifacts; it is required immediately before merging
any exact candidate whose changed paths include `projects/domainspec-v2/**`.

The merge package must bind target branch, base and head identities, a complete
changed-byte inventory, current validation evidence, claim ceiling, and the
verification level assigned by Rondelli. Victor's approval binds those exact
values. Any change invalidates the approval and blocks merge until Victor
approves the replacement candidate.

Victor may block structural inadmissibility but gains no semantic, obligation-
discharge, promotion, publication, release, deployment, or production
authority. Validation uses the fail-closed schema, validator, and fixtures under
`authority/pre-merge/`; the governing owner decision is
`authority/decisions/2026-08-24-victor-pre-merge-structural-approval.md`.
The deterministic check validates the referenced response contract and exact
candidate, not human identity; the merge owner must separately confirm that the
referenced response came directly from Victor.

Accepted example: Rondelli accepts Design and implementation proceeds through
current execution gates; Victor approves the frozen validated bytes before
merge. Rejected examples: requiring Victor at Design, inferring his response
from Rondelli's acceptance, or changing a byte after Victor's approval.

### domainspec-v2-C(meta-1). Finding-To-Development Contract
Validation mode: hybrid

Any artifact converting a harvested finding into definition, design, plan, fixture, schema, or
implementation-adjacent work must carry: a canonical definition ID (or an explicit reason none exists
yet); allowed/blocked use; source posture + local bridge status; the required workflow witness /
failure fixture / typed negative; authority + promotion boundary; open residue that would block
policy/launch use. It must not treat a refined finding as a mechanism, policy, contract, authority, or
launch readiness.

### domainspec-v2-C(meta-2). Local Status Non-Collapse
Validation mode: hybrid

`domainspec-v2-pass/flag/block` may route local work but must NOT create validation proof,
implementation readiness, governance weight, policy effect, **authority effect**, or launch
readiness. Keep `source_posture`, `evidence_status`, `confidence_status`, `authority_effect`,
`policy_effect`, `implementation_status`, `lifecycle_stage` separate.

### domainspec-v2-C(meta-3). No Reciprocal Authority Laundering ⟵ *Obs-B positive control*
Validation mode: review

No claim may be promoted here **or in a reciprocal v1/cav2 return package through a cyclic citation
chain alone.** A return package is at most candidate evidence for an external owner route; it must
name source IDs, blocked uses, unresolved findings, public/private scrub status, and the independent
owner route that decides reuse. It **transfers no framework authority**, proves no v2 result, and
implements no behavior unless a separate task route did so.

### domainspec-v2-C(meta-4). Load-Bearing Term Tracking
Validation mode: hybrid

Every load-bearing term (a symbol in a Formal cell, a fixture FAIL-region, a candidate obligation, a
decidable rule, the normative content of a claim) must resolve to a tracked definition ID. A
load-bearing term first cited without a tracked entry is created as a `candidate` definition with an
`Open / to-ground:` field and moved through the definitions lifecycle. Citing one with no tracked
entry is a drift defect the definition-drift audit must flag.

## Open Questions

### OQ-1. Standalone build-proof of the validation surface
Candidate: `pnpm install && pnpm test && pnpm run lint:docs` green in `impl/test-derivation-engine`
(blocked on the sandbox toolchain at mint time — see IMPORT-MANIFEST). Status: OPEN.

### OQ-2. Per-rule reformulation of v1 CONSTITUTION.md (C1–C11)
Candidate: crosswalk each v1 C-rule into a v2 object rule above. **This is also when the Governance
Grouping (split plan) executes** — each governance group moves to its own constitution artifact, this file
slims to the base/credibility tier, and the C6↔C11 edge-law binding is preserved as a cross-reference.
Status: OPEN (REFORMULATION-PENDING).
