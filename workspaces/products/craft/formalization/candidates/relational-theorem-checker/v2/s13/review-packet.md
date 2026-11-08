# Relational theorem checker: worked review

The implemented candidate checks a finite, explicitly selected relational/logic profile. It now supports exact contextual observations, sealed source producers, positive recursive fresh definitions, nonempty old-rule baselines, explicit delegation/inheritance mappings, condition activation, and two-step local shadow application. Machine qualification and human meaning/use review are separate.

## The concrete relations

The source says `capability:reviewer@v1` conforms to `contract:review@v1` in scope `static`. That produces `ConformsTo(subject,target,scope)` only when the assertion belongs to the graph and its assessment has matching endpoints, target revision, scope and supplied accepted status. `TargetKind(target,contract)` independently records the target type. Every observation retains its member assertion/assessment or node support. Multiple supports remain visible even when the fact is deduplicated.

The pilot rule reads **both** exact observations and derives `ContractReview(subject)`. `ContractReady(subject)` follows from it; a positive cycle feeds back to `ContractReview`. These are informational conclusions. Source observations cannot be supplied as caller facts or written by ordinary rules, and derived information cannot become an independent admission root.

The positive case returns `ContractReady(subject)`. Its trace is [shown here](exact-contract-scope-kind-explanation.json), ending at the exact conformance assertion/assessment and target-kind node. The second case requests declared scope `other-scope` with the same target and kind. That scope is present in the fixed before/after domain but has no conformance observation. It produces no ContractReady fact: The rule requests declared other-scope; the source conformance assessment supplies static scope. The empty fresh cycle has no seed. See the [wrong-scope explanation](wrong-scope-unseeded-fresh-cycle-explanation.json). The old unary `Conforms(subject)` still exists, but it cannot satisfy that exact target/scope premise.

## What the theorem actually says

For every old semantic model M, if the independently checked extension hypotheses hold, there is an expanded model N satisfying the extended rules, and every old atom has the same truth in N and M:

`∀ M, SemanticModel(before,F,M) → ∃ N, SemanticModel(after,F,N) ∧ ∀ old a, (N(a) ↔ M(a))`.

The checked hypotheses preserve the old graph, domain, roots, facts, context, interpretation, predicates and rules; new heads are fresh ordinary derived predicates with positive bodies. Recursion is allowed. The proof constructs a least fresh closure relative to **arbitrary M**, rather than assuming that M equals one sampled closure. A separate finite theorem proves that reference saturation terminates with an exact closure when its pending head inventory is complete. A checked query derivation and a complete closure remain different claims.

A generic Horn model may contain extra observation truths. The stronger **source-faithful** class fixes sealed observations exactly to source meanings and is separately named/proved. Richer graph/domain migrations use a distinct initial-view embedding theorem; they do not reuse fixed-domain model conservativity.

## The semantic stress relation

`inherits-contract` first resolves the exact binding and contract revision. That gives a **potential norm** with binding/contract origin. Even a condition named `always` is not executed or assumed true. Only a matching positive, consistent evaluation for the exact condition revision, context, subject, target, scope and epoch makes the norm **active**. Unknown, missing, false or conflicting selected statuses do not activate it. Active require/forbid conflicts retain both origins and do not enable arbitrary conclusions. Neither inheritance nor activation establishes fulfillment, conformance or admission.

`acts-for` maps exact agent/principal/delegation, scope, half-open period, revocation and supplied policy/gate data. The expiry boundary and revocation controls deny effectiveness; missing policy/gate interpretation and permitted-but-unimplemented redelegation chains remain unknown. Its source endpoint kinds lie outside F0, so the registry source selection is a separately tested boundary.

## Evidence and limits

[The pilot report](pilot-report.json) binds actual rich positive/negative proofs, fresh mapped checks, the complete hard inventory and the prior actual two-step shadow run. [Full qualification](../s10/qualification-audit.json) audits source/definition/proof closure and retained v1 guarantees. [Performance measurements](../s11/performance-baseline.md) distinguish complete cold/warm qualification from evaluator-only probes. The measured benchmark was cold: 129.66 seconds, 2.3 GiB observed child peak RSS; warm: 82.18 seconds, 2.31 GiB observed child peak RSS. These are local observations; larger workloads have no general time or memory guarantee. Work and per-stage time ceilings do not impose an OS memory cap. The unchanged 60-second compiler-stage limit stopped the first second-successor registration before publication; splitting the same concrete declarations/proofs into independent modules completed that bounded case. This is not a weaker theorem or a broader completion-time guarantee.

The following limits remain explicit:

1. All 41 source relations were reviewed, but only selected fragments are implemented. The [source map](../s18/source-map.json) retains deferred meanings and inherited unsupported obligations.
2. Assessment, root-receipt, policy/gate and condition truth are supplied inputs. Hash binding and logic do not authenticate those external claims.
3. The language is finite positive Horn logic with fresh ordinary heads. Old-head changes, mixed edits, negation, functions, entity generation, overrides and redelegation chains need other profiles/proofs.
4. JSON/normalization/source selection are tested boundaries. Pure values, exact independent types and proof declarations are checked/replayed by the same pinned Lean kernel, not a second kernel.
5. Work ceilings can return unknown. Partial closure cannot prove absence or readiness. Local shadow locking coordinates cooperative writers; an external writer can race the final check/rename, with postcheck/reconciliation limits stated in the [application report](../s09/application-qualification.json).
6. Machine and author checks do not supply human semantic, diagnostic or bounded-use approval. Original v1 R06/G4 remain pending. There is no live authority, publication or deployment effect.

## API and review request

[CLI/Python API contracts](../s08/API.md) cover projection, recursive qualification, stress mapping and explanations. [The shadow adapter](../s09/shadow-adapter.py) additionally initializes/reviews/applies candidate snapshots inside its local runs directory, with bounded split witness stages. [Execution status](../execution/status.json) records task acceptance and the optional optimization decision; the qualified reference remains selected.

Please assess whether these meanings match the intended model, whether the worked diagnostics explain the failures, and whether bounded local shadow use is appropriate under the stated limits. Use [the feedback template](feedback-template.md). Actual feedback is required to finish S14; no response is inferred from machine passes or the request to implement the plan.
