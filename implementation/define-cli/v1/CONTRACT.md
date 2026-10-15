# Define's Lab interfaces

## Input and output

A session requires a goal, originating intent, context, consumer, and nonempty required concepts. Each concept has exactly one resulting disposition: reuse, specialize, propose or open. Omitted answers remain open. Duplicate IDs, duplicate responses and undeclared responses are rejected.

The output retains `cav2.definition-pack-candidate/v1`. The successor result uses `cal.define-cli-result/v1`, validated against its closed JSON schema. The pure source-session API retains its original result shape. The Lab result additionally carries `lab_binding`: source snapshot, branch HEAD and the exact context envelope. The pack digest includes the context-envelope digest. The native CLI compiles only a Lab-bound result whose envelope is current and unexpired.

A candidate proposal has a normative statement, a plain explanation and a boundary. This is **not the complete admitted Lab Definition carrier**. The Lab requires its scientific/formal governing voice, plain-language and domain-context explanations, exact source evidence, scope and applicable owner decision. Prepare that record through the existing review contract. No automatic translation or admission is provided.

## Reused interfaces

| Function | Provider | Boundary |
| --- | --- | --- |
| Source capture, freshness, inspection | `lab-runtime/v2` source profile, `read_data`, `resolve` | Exact selected sources and current standing. |
| Context and ontology views | Existing `Session` carrier construction | Detached copy changes one input-reference deduplication; source runtime stays unchanged. |
| Ontology exploration | Existing `graph.query` | Depth 2, maximum 60 nodes / 100 edges; diagnostics retained. A bounded view is not global completeness. |
| Review | Existing `Store.review` | Exact proposal preparation on an explicitly selected store; no authorize/apply. |
| Agent transport | Selected RPC leaf providers + installed Codex app-server | Ephemeral thread, read-only sandbox, no ARE gateway or router. |
| Definition decisions | Eleven preserved compiled Define service entries | Deterministic structural and finite language checks. |
| Semantic handoff | Selected semantic-contract compiler + Lab Craft public API | Pure semantic functions lower to Calculation; current package/build versions must match. |
| Durable work sessions | Retained Define session runtime | Revisions, idempotency and local access effects; caller identity is not authenticated here. |

The Lab's separate C08 context compiler and C10 thirteen-member successor review candidate are not substituted into this path. C10 has a fixed specialized membership contract. Operational v2 provides the reusable interfaces this CLI consumes.

## Context and trust

The context envelope includes selected Project State, Context View, Ontology View, Ontology Cut and exact selected Definition records. It has a 256 KiB inline limit and a default 900-second lifetime. The source epoch binds source snapshot plus branch HEAD. Graph diagnostics, source standing and original decision references remain visible.

`CAL-DEFINE-EXPLICIT-ENTRY` identifies the user-selected CLI entry. It is not an ARE route registration, capability selection or permission grant. A digest detects byte changes; it does not authenticate the person supplying a record. Context and schema validation do not authorize actions.

Scripted language evidence requires explicit `user_confirmed: true`. This is a declaration by the script's author. It is not a signed owner approval. Grounding must point to user language; every pair of terms requires a non-collapse assessment; classification axes require independent questions or explicitly declared coupling. The actual final meanings are checked again. These finite checks cannot establish global semantic consistency or prove that every declared distinction is substantively correct.

## Writes and failure

Inspection, context, ontology and review do not change the Lab store. A requested candidate file is published without replacing an existing file. Compilation stages output and publishes with Linux `renameat2(RENAME_NOREPLACE)`. An existing directory, file or symlink is refused even if it appears after the initial target check. Unsupported kernels fail visibly; there is no replacing-rename fallback.

Exit status: 0 success; 2 legacy usage error; 3 runtime/input/dependency failure; 4 unresolved or blocked handoff. Failures remain visible. No source validator is reclassified as passing when its dependencies are stale.

The implementation makes no repository admission, release, deployment or live-provider completion claim.
