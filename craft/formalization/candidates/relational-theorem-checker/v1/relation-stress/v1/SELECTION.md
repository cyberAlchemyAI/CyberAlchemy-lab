# Two relations for stretching the formalization

Status: candidate selection analysis, 2026-10-08. The analysis below records the selection stage, when these profiles and theorem targets were proposals. The subsequent candidate [implementation](implementation/README.md) now includes checked laws, countermodels and local JSON operations; its [result](implementation/RESULT.md) states the verified scope. Existing F0 acceptance and the three-kind formal profile are unchanged. Neither package admits rules or implements real authorization.

## Selection and source evidence

The governance-transaction-surface registry contains 41 relation kinds and 550 explicitly ordered endpoint pairs. The accompanying audit verifies every relation source against its registered hash and pair count. This selection prioritizes new kinds of proof obligations over endpoint count; it is not a universal ranking of semantic complexity.

| Experiment | Relation | Exact endpoint pair | What makes it demanding |
|---|---|---|---|
| Semantic interpretation | `acts-for` | `agent-instance → principal` | Representation depends on an exact delegation, scope, effective period and revocation state; meaning changes with the evaluation snapshot. |
| Logical consequence | `inherits-contract` | `capability-instance → contract` | An exact binding propagates obligations, while inherited obligations alone must not produce conformance, adoption or ownership. |

Source paths, hashes and replayable shape examples appear in `schema-stress-audit.json`. The registry admits relation-kind definitions only. Its effective `admitted-current` status does not admit the example assertions. The current delegation, binding and contract schemas are also recorded separately from their source files' candidate posture and runtime activation state.

`evidence-bears-on` is a strong later epistemic experiment: supporting or contradicting evidence does not establish truth. `successor-of` is a useful later ordering experiment: explicit supersession raises cycle and currentness questions. `derives-from` records provenance; it must not be silently interpreted as logical entailment.

## Semantic experiment: acts-for

The relation asks: “Which Principal is this Agent Instance acting for under one exact Delegation?” Its required qualifiers are `delegation_ref`, `scope_ref`, `effective_period`, and `revocation_state`. Each currently requires only a nonempty string. The delegation carrier additionally declares the agent and principal, scopes, allowed actions, policy references, approval gates, and whether redelegation is allowed. Those references are not interpreted by JSON Schema.

Separate two predicates:

```text
RecordedActsFor(G, edge)
EffectiveRepresentation(G, edge, action, scope, snapshot)
```

The first records a bounded representation assertion with provenance. The second evaluates a proposed interpretation at a specific snapshot. A historical assertion may remain recorded after its delegation expires; expiration does not erase history.

The proposed semantics must resolve an exact delegation revision; bind its principal and agent to the edge endpoints; interpret the requested scope and action; evaluate the effective period and revocation at the snapshot; and resolve any required policies and gates. Missing or ambiguous interpretation returns unknown with reasons. Eligibility is a semantic evaluation, not execution permission or authenticated real-world authority.

For the first temporal profile, use exact scope membership, a discrete epoch and half-open intervals `[start,end)`. Define a separate revocation event effective at an epoch. These are proposed choices, not meanings already encoded in the string fields. Later scope containment or interval/session adapters require explicit rules and fresh proofs.

The meaningful theorem target is a restriction-preservation theorem, rather than merely extracting clauses from the definition:

```text
RestrictionOf(D₂,D₁)
∧ MatchesExactDelegation(e₂,D₂)
∧ MatchesExactDelegation(e₁,D₁)
∧ EffectiveRepresentation(G,e₂,action,scope,t)
⇒ EffectiveRepresentation(G,e₁,action,scope,t)
```

Here `RestrictionOf` requires the same agent and principal, a subset of scopes and actions, a narrower period, and at least as restrictive revocation, policy and gate conditions. Both revisions must resolve in the same complete interpretation snapshot; only their restriction fields may differ. `MatchesExactDelegation` checks that each edge names and matches its own revision, so this theorem does not license a version substitution. Acceptance under a stricter delegation cannot create powers absent from the broader one. Define the restriction relation independently and prove this law for arbitrary finite action/scope sets and epochs.

A second theorem target is revocation stability: if a delegation is revoked at `r`, with no explicit restoring transition or successor delegation, that same delegation is ineffective at every `t ≥ r`. Prove the general law and test the boundary epochs; do not just assume the conclusion in an abstract resolver.

Five stressors and required surviving behavior:

| Stressor | Required behavior |
|---|---|
| Revoked or expired delegation with a retained edge | Preserve the historical edge; refuse current effectiveness. |
| Edge names the wrong principal, agent or revision | Reject the effective interpretation with the binding mismatch. |
| Scope or action is widened | Produce no new eligibility unless the exact delegation permits it. |
| Revocation changes between evaluation and use | Bind results to the evaluated snapshot; require a fresh evaluation at the use boundary. |
| Forbidden redelegation or unresolved policy/gate | Do not compose authority automatically; return an explicit rejection or unknown. |

Illustrative intended countermodel: an agent represents a principal for `read-repository` until epoch 10; at epoch 11 the recorded edge still exists but current representation is ineffective. Under this proposed temporal interpretation, an inference from a recorded edge to perpetual effectiveness is false. The schema replay demonstrates only structural acceptance of expired and uninterpreted values; it does not prove this temporal countermodel.

This experiment extends beyond the current static positive-rule L3 profile. A temporal profile and its trust/snapshot contract must be formalized first.

## Logic experiment: inherits-contract

The relation explicitly “records inherited obligations without transferring parent ownership or proving conformance.” Its qualifiers are `binding_ref` and `contract_version_ref`, currently nonempty strings. The binding carrier declares its instance, parent model revision, inherited contract references, overrides and state. The contract carrier declares obligation, prohibition and permission references, but provides no logical syntax for their contents.

The first candidate logic should derive obligations as positive data facts. Define an exact resolver and a finite obligation language before adding rules. Initially reject unresolved overrides and mark them unknown; do not silently erase inherited obligations. Scope and version are part of every fact.

```text
Inherited(i,c@v,b)
∧ BindingMatches(b,i,c@v,scope)
∧ ApplicableObligation(c@v,o,condition,scope)
⇒ Required(i,o,condition,scope,c@v,b)
```

This is an obligation-propagation rule, not evidence that `o` has occurred. `BindingMatches` must independently check the binding's state, instance and inherited contract membership. `ApplicableObligation` must resolve and interpret the contract's exact obligation reference. Neither premise may hide a precomputed `Required` conclusion.

The central theorem target is obligation-derivation soundness:

```text
BaseFactsSatisfied(M,G)
∧ RulesSound(M,R)
∧ Derives(R,G,Required(i,o,condition,scope,c@v,b))
⇒ M satisfies Required(i,o,condition,scope,c@v,b)
```

Prove it by induction on finite derivation certificates. Also prove this concrete rule's soundness from the independently defined contract interpretation; the generic theorem alone is insufficient. Require exact premise references, rule revisions and substitutions. A complete finite closure can additionally prove no eligible obligation is missed; absence from a partial or timed-out closure establishes nothing.

For a stronger concrete conclusion, require obligation-origin preservation: every derived `Required(i,o,condition,scope,c@v,b)` has a base inheritance fact for that exact instance, contract revision and binding, and an independently resolved applicable obligation at that exact contract revision and scope. This holds for a rule set whose only obligation-producing rules are the propagation rule and origin-preserving forwarding rules, and whose base `Required` facts already have checked origin witnesses. Audit every producer rule, then prove the law by derivation induction. An arbitrary new rule may invalidate it; a rule-set hash/version belongs in its proof contract.

The indispensable countermodel target is:

```text
Inherited(i,c@v,b) ∧ Required(i,o,...) ∧ ¬ConformsAt(i,c@v,scope)
```

Choose a consistent obligation such as requiring a receipt, and an instance with no receipt. This witnesses that inheritance does not entail conformance. It does not prohibit an independent conformance assessment from coexisting with inheritance. Compatibility with the existing assessed `ConformsAt` predicate requires an explicit bridge; the current L0 checker does not verify execution of every obligation.

Five stressors and required surviving behavior:

| Stressor | Required behavior |
|---|---|
| Two inherited contracts require and forbid the same action in the same conditions | Retain both normative facts and report a conflict; derive no arbitrary fact or automatic conformance. |
| Binding refers to another instance or contract revision | Stop propagation at the mismatch. |
| Override attempts to remove an inherited obligation | Require explicitly interpreted override rules and justification. |
| Rule chain converts `Required` into `Satisfied` or `ConformsAt` | Reject the rule or demand separate satisfaction evidence. |
| Missing obligation interpretation, cyclic certificate or interrupted closure | Return unknown/incomplete or reject the certificate; do not certify non-derivability. |

`Required(action)` and `Forbidden(action)` are separate positive predicates. Their coexistence records a normative conflict, rather than inserting a proposition and its classical negation into an explosive proof context. Satisfaction and policy for resolving the conflict are separate questions; no general deontic logic completeness claim follows.

The registered endpoint pair prevents blind transitivity: a contract is not a capability instance, so an `inherits-contract` edge cannot simply be composed with another edge of the same kind. Cascading inheritance would need a separately declared, well-typed binding rule. Symmetry is also not justified.

## Evidence ceiling and implementation order

`replay_schema_stress.py` validates five selected source fixtures and nine deliberately demanding mutations against the current schemas, plus two negative controls. The two relation fixture checks cover their exact qualifier contracts; the three carrier fixture checks cover the complete carrier schemas. Passing mutations demonstrate that structural schemas do not settle the questioned interpretation. In particular, a contract listing one unresolved token in both obligation and prohibition references does not establish a genuine logical contradiction until the token's meaning and applicability are defined.

No stress theorem in this document has been proved. No relation is added to the accepted three-kind Lean profile. The next formalization steps are:

1. Freeze the two semantic contracts: temporal delegation interpretation and finite obligation interpretation, with exact revisions, scopes, unknown cases and evidence boundaries.
2. Construct independent positive models and countermodels for each.
3. Prove restriction preservation and revocation stability for `acts-for`; prove rule soundness and inheritance/conformance non-entailment for `inherits-contract`.
4. Implement decision procedures and replayable certificates, then prove checker soundness against those definitions.
5. Add hostile controls for all ten stressors. Extend public schemas/APIs and the accepted plan only after the new profiles satisfy their own gates.

The unresolved design choices are the interpretation of existing period/session strings, authenticated snapshot provenance, policy/gate semantics, the obligation language and satisfaction evidence, and override precedence. The proposed minimal profiles allow formal investigation without claiming these choices have already been settled by the registry.
