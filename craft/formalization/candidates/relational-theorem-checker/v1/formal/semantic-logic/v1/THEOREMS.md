# Theorems about the logic of the semantics

This additive candidate package proves consequences directly from the accepted L0 semantic definitions. It imports `RelationalSemantics`, not the checker or checker-soundness proofs. The original F0 semantics, source bindings and acceptance records are unchanged. The review is a Codex author self-review.

## Evidence consistency for conformance

Let `ConformsAt(G,e,scope,version,evidence)` mean that assertion `e` has kind `conforms-to`, those exact qualifier values, and satisfies `InstanceValid(G,e)`. It is a semantic claim about an assertion, including a proposed assertion; graph membership is a separate condition.

For every graph satisfying `Inv`, if two conformance assertions use the same evidence reference, they agree on their source, target, scope and target version:

```text
Inv(G)
∧ ConformsAt(G,e₁,scope₁,version₁,E)
∧ ConformsAt(G,e₂,scope₂,version₂,E)
⇒ source(e₁) = source(e₂)
  ∧ target(e₁) = target(e₂)
  ∧ scope₁ = scope₂
  ∧ version₁ = version₂
```

This is `conformance_evidence_functional` in [SemanticLogic.lean](SemanticLogic.lean). Each valid claim resolves to a matching assessment. The graph invariant requires assessment reference uniqueness, so both references resolve to the same assessment. Its exact bindings force the four equalities. The proof quantifies over arbitrary finite graphs and assertions and uses no successful-checker premise.

Consequently, the same evidence token cannot turn the fixture's `static` claim into a `runtime` claim or substitute a different subject or target version. Scope labels are opaque strings here; the theorem proves exact equality, not a containment relation between scopes. A checked positive model also allows two distinct assertion IDs to reuse matching evidence, and another allows a different scope with a separately bound assessment. Neither result establishes real runtime performance.

The uniqueness premise is necessary. A checked countermodel contains two assessments with the same token and different scopes. Both assertions separately satisfy `InstanceValid`, but `Inv` fails. Another theorem refutes unconditional scope functionality without that premise.

## Receipt consistency for materialization

Let `MaterializesAs(G,e,receipt,role,digest)` mean a valid materialization assertion with those qualifiers. For any `Inv(G)`, two such assertions sharing one receipt reference must agree on the transaction/source, output/target, role and digest:

```text
Inv(G) ∧ MaterializesAs(G,e₁,R,role₁,digest₁)
       ∧ MaterializesAs(G,e₂,R,role₂,digest₂)
⇒ source(e₁) = source(e₂) ∧ target(e₁) = target(e₂)
  ∧ role₁ = role₂ ∧ digest₁ = digest₂
```

This is `materialization_receipt_functional`. The companion binding theorem requires a matching target node content identity and accepted application assessment. String equality does not authenticate a receipt, prove cryptographic hashing or establish real output creation. The chosen L0 profile binds each receipt token to one assessed output/role; a future multi-output receipt model would require revised definitions and proofs.

## Conformance does not entail admission provenance

`HasAdmissionRoot(G,subject)` means a separately supplied root in `G` references that subject. It does not mean that the root's real authority has been authenticated.

The theorem `conformance_does_not_entail_admission_root` refutes the universal implication from valid, asserted conformance to a supplied admission root. Its witness is a graph satisfying `Inv`, containing a valid conformance assertion, with no admission roots.

```text
There exists G,e with Inv(G), e ∈ assertions(G), ConformsAt(G,e,...),
and no admission root for source(e).
Therefore: conformance ⊭ admission-root presence.
```

This is non-entailment, not a universal ban on admission. A second checked model has the same nodes, assessments and assertions plus a separate well-formed root. Both graphs satisfy `Inv`, and both have the same conformance claim. The general theorem `well_formed_admission_variation_preserves_inv` proves that replacing the root inventory preserves `Inv` when the replacement roots satisfy their semantic validity conditions. `admission_roots_do_not_change_instance_meaning` proves that root changes leave assertion validity unchanged.

## Verification and limits

[SemanticWitnesses.lean](SemanticWitnesses.lean) proves nine witness/countermodel statements by kernel reduction or explicit logical arguments. [SemanticStatementAudit.lean](SemanticStatementAudit.lean) separately fixes and checks four required theorem types and prints transitive axioms for all eight general laws, nine witness/countermodel declarations and four target assignments. The validator rejects weakened conclusions, false admission inference, same-evidence scope upgrade, ambiguous identity acceptance, `sorry` proofs and custom axioms.

These proofs establish internal consequences of the chosen semantics. They do not prove that the semantics capture every intended real-world meaning. There is no inference-rule execution or arbitrary derivation-chain closure theorem in this package; that remains the later L3 work.

Run from the repository root:

```bash
python3 craft/formalization/candidates/relational-theorem-checker/v1/formal/semantic-logic/v1/validate_semantic_logic.py --write
```

The runner checks the parent F0 source bindings, pinned Lean runtime and transitive core dependencies, builds fresh modules, checks exact theorem types, audits axioms and executes six negative controls. Without `--write`, it leaves audit records unchanged. Results are in [semantic-logic-audit.json](semantic-logic-audit.json) and [lean-replay.log](lean-replay.log).
