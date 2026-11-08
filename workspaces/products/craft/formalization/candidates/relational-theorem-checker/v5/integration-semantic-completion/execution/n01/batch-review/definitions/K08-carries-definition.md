# K08 — carries-definition

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **checked exact semantic binding**.

**Meaning in plain language.** An artifact type carries one exact definition and its content commitment. The type and definition retain distinct identities and ownership.

**Question answered.** Which exact Definition version supplies this Artifact Type's governed meaning?

**Formal definition.**

```text
Meaning_K08(W,e,f) := ∃ w ∈ W.DefinitionCarriage. Base_K08(W,e,f,w) ∧ (w.artifactType = s ∧ w.definition = t ∧ t = resolve(q.definition_version_ref) ∧ w.bytes = bytes(W,t) ∧ hash(w.bytes)=q.definition_sha256 ∧ w.digestPolicy = f.digestPolicy)
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a DefinitionCarriage record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `artifactType` | Artifact Type exact revision |
| `definition` | Definition exact revision |
| `bytes` | resolved immutable definition content bytes |
| `digestPolicy` | exact named byte representation and hash algorithm |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`bytes`: The exact immutable resolved content bytes under the frame byte representation; source authenticity is a separately stated assumption.

`hash`: The pinned content-commitment algorithm applied to those exact bytes. Equality is checked under the named byte/hash assumptions and is not an authenticity or semantic-correctness theorem.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `definition_version_ref` | `w.definition` | exact carried Definition revision |
| `definition_sha256` | `hash(w.bytes)` | commitment to the exact definition bytes under the pinned representation/hash assumption |

**Operational behavior.** Record exact definition carriage; preserve admissions, ownership and distinct endpoint identities.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Candidate Artifact Type A binds Definition D@1 with matching bytes, while A remains unadmitted.

**Insufficient case.** D@1 with substituted bytes cannot reuse its original content binding.

**Useful correction.** Resolve the specified definition bytes and recompute the commitment under the named digest policy; do not substitute a same-named revision.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| admission | An already authorized atomic transaction placed an endpoint in the admitted state. | `relation.carries-definition:forbidden:0` |
| authority-transfer | A separately authorized transfer changes the authority holder for this envelope. | `relation.carries-definition:forbidden:1` |
| endpoint-identity-collapse | The independent governed identity model puts the endpoints in one identity class. | `relation.carries-definition:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Content authenticity and raw definition capture remain assumptions to discharge; hash equality alone does not establish semantic correctness or ownership.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/carries-definition.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K08-carries-definition.json)

**Exact ordered pairs (1).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| artifact-type | definition | artifact-type to definition: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
