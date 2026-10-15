# API workflow descriptions

Status: proposed sequences; example messages are shape illustrations with placeholder authority, identities and handlers. No sequence below was executed by creating this package.

## Discover all definitions and understand their status

1. `lab.status` captures the permitted source profile and current cut.
2. `catalog.get` discovers the exact current Definition carrier and historical versions.
3. `artifact.query` selects definitions at that cut, with a canonical or verified projection basis, limit/depth/byte bounds and a bound cursor.
4. `artifact.inspect` requests chosen sections: body, exact contract, effective admission evidence, lifecycle, relations, provenance and gaps. Metadata-only inspection carries no body.
5. The reader distinguishes effective admission, immutable body label, implementation observation and outcome. A contract being current does not admit every instance using it.

Example invocation: [artifact.query](examples/artifact.query/request.json). Example selected inspection: [artifact.inspect](examples/artifact.inspect/request.json). These use illustrative references; substitute actual authorized bindings only during implementation operation.

## Ephemeral Agent engineering work

`context.get` → `session.open` → `artifact.inspect` / `artifact.query` → `action.evaluate` → `action.dispatch` → `change.prepare` → `change.validate` → `proposal.review` → actual owner outcomes → `checkpoint.resolve` → `admission.apply` → `projection.refresh` / `ontology.project` / selected `files.materialize` → `session.close`.

Independent engineering satisfaction and Work Outcome Assessment must be evidenced before claims of completed Work. The selected workflow mappings, actor routes and method/implementation contracts must exist. Unbound workflow templates cannot be run just because their JSON is valid. Context and short memory confer no extra action authority.

## Failures, challenges and operational lessons

- Observed failure → `classification.prepare` → `failure.assess` → exact candidate review/admission where required.
- Eligible contestation → `challenge.submit` → response under Challenge Contract → actual resolution Decision → `challenge.resolve` → selected exact consequences.
- Evidence-based lesson candidate through `change.prepare` → assessed review/admission → `lesson.select` for a later assignment → `lesson.apply` → `lesson.assess` using actual outcomes and counterevidence.

Classification, cause, lesson applicability and observed improvement remain distinct. The generic candidate pipeline supports the already bound artifact contracts; it does not introduce a universal body type.

## Typed extension and selected migration

`typed.extension.prepare` binds unique semantics, orthogonal axis, exact endpoint/qualifier contracts, noncollapse evidence and affected carrier successors. Missing endpoint mappings block the affected use. Extension admission occurs through the same exact final review and canonical transaction; it cannot be inferred from schema validity.

`package.import` prepares source/target mappings and complete selected-item dispositions. `ontology.project` represents committed eligible source subjects under its independent ontology cut/authority. Imported source evidence and ontology representation do not grant target repository authority.

## Capability and release

`capability.adoption.prepare` prepares exact realization/adoption declarations with conformance, operational scope and observation contracts. Actual pilot work needs its own currently valid action authority. `release.prepare` reviews a candidate with exact package bytes, acceptance, privacy, pilot and environment evidence. A reviewed owner release Decision is required before selected `installation.execute`; installation has zero activation/external effects.

## Timeout and recovery

1. An uncertain `action.dispatch`, `admission.apply`, `ontology.project`, file generation or installation result preserves its input/key/effect evidence.
2. Use `operation.inspect` with the exact call binding or scoped operation/key. Do not send a changed body with the same key.
3. If completed, return the recorded result after current read authorization. If pending, wait/inspect within budgets. If uncertain, invoke `action.reconcile` only under the selected exact recovery contract.
4. Verify actual state and allowed residue. Rebuild disposable projections or managed outputs where their contracts permit it. Preserve committed history.
5. A missing operation record after a crash is not proof that no effect occurred. Reconcile expected state before any authorized retry.

See the [uncertain transport timeout](examples/transport-uncertain-timeout.json) and [operation lookup](examples/operation.inspect/request.json).
