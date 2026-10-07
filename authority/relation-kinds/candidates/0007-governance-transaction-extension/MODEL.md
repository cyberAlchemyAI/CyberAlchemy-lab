<!-- GENERATED FILE: canonical data is model.json. -->

# Governance transaction relation extension

- Relation Kinds: `41`
- New axis: `relation.materializes-consequence`
- Added exact endpoint pairs: `12`
- Authority effect: `none`

## Exact extensions

### `relation.member-of`

Which governed container or scope is this member part of?

- `decision` -> `decision-bundle`

### `relation.governed-by`

Which Policy or Constitution governs this subject?

- `admission-transaction` -> `policy`
- `authority-boundary` -> `policy`
- `decision-bundle` -> `policy`
- `decision-checkpoint` -> `policy`
- `user-decision-preference` -> `policy`
- `workflow-decision-profile` -> `policy`

### `relation.scopes-authority-over`

What governed scope is bounded by this explicit Authority Claim or Authority Boundary?

- `authority-boundary` -> `decision-scope`

### `relation.materializes-consequence`

Which declared deterministic consequence did this Admission Transaction materialize?

- `admission-transaction` -> `generated-output`
- `admission-transaction` -> `project-governance-event-history`
- `admission-transaction` -> `project-semantic-event-history`
- `admission-transaction` -> `project-state`

## No-collapse conclusions

- `relation.materializes-consequence` vs `relation.produces`: Materialization is the transaction-scoped deterministic application of an authorized bundle; production attributes an output to an Agent Action and does not imply authorized application.
- `relation.materializes-consequence` vs `relation.declares-effect-on`: A Decision declares an effect on an exact target; an Admission Transaction materializes only consequences already covered by that declaration.
- `relation.member-of` vs `payload references`: Decision membership in a closed bundle is set membership. Presentation at a checkpoint and profile allowance remain typed payload references because they answer different contract questions.

## Claim ceiling

This candidate extends the admitted relation surface for governance transaction carriers. It admits no Relation Kind, endpoint pair, Typed Relation, Artifact Type, instance, decision, or runtime effect.
