---
title: L0 — working semantic proof
status: not-started
dependsOn: []
---

# L0 — working semantic proof

**Decision question:** After this layer, we know whether an executable relation-addition check can be proved sound against an independently defined graph invariant.

**Minimum working unit:** three relation kinds, a small synthetic graph, one addition, a generic soundness theorem for the supported finite profile, and a receipt binding the demonstration to its inputs.

## Purpose and boundary

This layer closes the largest uncertainty first: whether the proposed system proves a semantic property or merely repeats its own validation result. The theorem must establish an independent proposition. It must not define validity as `check=true` and then prove the same condition.

Select `conforms-to`, `declares-effect-on`, and `materializes-consequence`. Together they expose three distinct ideas: scoped evidence assertions, declarations of effects, and records of application outputs. Their valid endpoints and qualifiers come from exact source records referenced by the selected registry.

The existing Typed Relation/v2 carrier excludes materialization. Use a separately named candidate companion input profile for this experiment. Its mapping to the selected records must be explicit; it does not amend the frozen carrier or admit an instance. The coverage reconciliation remains L1 work.

## Inputs and outputs

Inputs are exact source-record bindings, a fixed theory profile, an exact node inventory, a valid starting graph, and an addition proposal. Synthetic external-evidence facts must be identified as fixture facts, not observations of real services.

Proposed outputs are `Semantics`, `Checker`, `Soundness`, and `Fixture` Lean modules; normalized input JSON; a source-to-field mapping; a required theorem statement; positive and negative controls; and an evidence receipt. These names describe future modules rather than existing implementations.

## Formal model

Represent each assertion with an identity, kind, exact endpoint references, and a typed qualifier value. For this first slice, three qualifier constructors are sufficient. Define:

- `EndpointValid(T,e)`: both references resolve and their ordered kinds occur in the selected exact pair set.
- `QualifierValid(T,e)`: required keys and value shapes match the selected contract, with no extra keys.
- `VersionScopeValid(T,e)`: selected qualifier versions/scopes match the resolved endpoints where the semantics explicitly requires this.
- `InstanceValid(T,e)`: conjunction of the selected independent requirements.
- `Inv(T,G)`: all assertions are valid and assertion identities are unique.

Do not add undeclared cardinality or acyclicity constraints. They are relation-specific decisions, not universal graph requirements.

For reference-valued qualifiers, distinguish syntactic presence from resolution and evidential sufficiency. A digest-shaped string is not proof that bytes were hashed. A conformance evidence reference is not proof of real-world conformance. The first theorem concerns the declared model and selected fixture interpretation.

## Algorithm and proof obligations

Use full recomputation first: construct the candidate graph, validate every selected invariant, and collect exact failure locations. This avoids an unproved assumption that checking the newly added edge alone preserves global invariants.

Required theorem sketches, not compiled Lean declarations:

```text
instance_check_sound:
  checkInstance(T,e)=true -> InstanceValid(T,e)

graph_check_sound:
  checkGraph(T,G)=true -> Inv(T,G)

addition_preserves:
  Inv(T,G) -> checkAddition(T,G,delta)=true
  -> Inv(T,apply(G,delta))
```

If `checkAddition` fully rechecks the output graph, its theorem can follow directly from `graph_check_sound`; the old-invariant premise need not be artificially retained if unused. The interface should state which proof shape it actually implements.

Validate successful evaluation through the chosen proof-producing method and audit its assumptions. Executing compiled code and serializing `true` is not by itself a kernel proof of that particular evaluation.

## Ordered implementation work

1. Freeze the slice and resolve exact meanings of version/scope qualifiers.
2. Define independent predicates and the candidate companion input contract.
3. Implement decoding/normalization and a field-by-field source mapping.
4. Implement a total finite checker, with explicit failures for malformed or unsupported input.
5. Prove checker soundness and addition preservation.
6. Supply a nonempty model witness and a complete demonstration receipt.
7. Review the meaning-to-statement mapping and transitive proof dependencies.

Parsing and hashing remain explicit trusted components until separately verified. Reusing the existing certificate kernel can bind outputs, but does not discharge these boundaries.

## Validation and acceptance

| Control | Required outcome |
| --- | --- |
| Valid assertion and addition | Accepted with the selected invariant theorem and exact bindings |
| Conformance phantom pair | Rejected for endpoint-pair violation |
| Missing/extra qualifier | Rejected for qualifier-contract violation |
| Duplicate assertion identity | Rejected without silently replacing an earlier assertion |
| Wrong exact target version | Rejected when the selected semantics requires target equality |
| Changed input with an old receipt | Receipt unusable for the new graph/proposal |
| Incomplete proof or assumed target theorem | Fails the proof acceptance policy |

Completion requires a checked generic theorem, the nonempty demonstration, all selected controls, and explicit parser/runtime assumptions. A successful fixture alone is insufficient.

## Outcome, cost, and promotion

The operator can inspect a valid addition and understand the precise cause of a rejected one. Risk reduced: structural validation being advertised as semantic proof. Cost is medium to high, driven by semantic agreement and the first correctness theorem.

Continue to L1 when the complete slice passes. Narrow a qualifier interpretation if it requires external evidence not available in the selected profile, keeping that limitation visible. Preserve all L0 invariants and exact-binding guarantees in later layers.

## Deferred scope

Full registry semantics, model extension proofs, inference rules, solver automation, incremental validation, live governance writes, and large-graph performance. L0 does not establish that materialization was actually performed or that its outputs are correct outside the fixture model.
