# Design amendments from implementation analysis

Status: proposal only. Date: 2026-10-09. These amendments refine the earlier design; they do not modify v1 semantics or discharge future theorem obligations. Each statement below is a required target to formalize and prove, not an already accepted Lean theorem.

## 1. Distinguish what a fact means from who may produce it

The inference role determines authority-root policy. It does not determine whether an ordinary atom has source-observation meaning. Introduce an orthogonal producer policy in the selected profile:

| Predicate class | Initial facts | Added rule heads | Meaning |
|---|---|---|---|
| Sealed source observations, such as ConformsTo and TargetKind | Only exact checked projector output with support | Forbidden | A named observation of the captured source graph |
| Derived ordinary signals, such as ReviewSignalFor | Only if explicitly allowed and bound; none in the first rule-only extension | Allowed for declared fresh predicates | Consequence of positive rules, within the named profile |
| Checked independent roots | Only exact independently supplied root inventory | Forbidden | Supplied provenance with all four exact coordinates |
| Root carriers/protected conclusions | Existing rooted-fact and lineage rules | Only under existing exact-root policy and supported change profile | Root-preserving information; no new authority |

A source observation can remain logically ordinary. Do not force its three-coordinate signature into the four-coordinate authority-root algebra. Sealing also applies to caller-submitted initial facts and aliases with a different display name: the profile binds predicate key, signature, meaning and producer policy, rather than relying on a prefix.

Required targets:

```text
ObservationInitialExact:
  QualifiedProfile(P,G,T,F) ->
  (ConformsTo(s,t,c) in F <-> MemberConformance(G,s,t,c))

ObservationDerivationExact:
  QualifiedProfile(P,G,T,F) and NoRuleHeads(T, P.sealedPredicates) ->
  (Derivable(T,F,ConformsTo(s,t,c)) <-> MemberConformance(G,s,t,c))

SupportLeavesValid:
  AcceptedDerivation(P,G,T,F,query,certificate) ->
  every sealed observation leaf has an exact checked source support;
  other leaves retain their explicitly declared supplied-truth/root assumptions
```

No rule may produce a sealed observation, including a constant-only rule with an empty body. Rules can read observations and produce fresh ordinary signals. An observation-free unseeded cycle produces no facts under least derivation semantics.

There are two model contracts to keep distinct. Generic SemanticModel may assign extra truths to ordinary predicates; its derivation/conservativity theorem remains valid for that logical model class. A source-faithful profile model additionally interprets sealed observations exactly as the captured source. Stronger business-meaning claims quantify over that profile model class. Do not quietly strengthen generic SemanticModel or imply that producer sealing alone constrains extra truths in every arbitrary model.

Tasks: S00, S15, S16, S03, S05, S10. Findings: I01, I07, I12.

## 2. Contextual projection has a declared vocabulary and support contract

Use the existing value sorts for the first successor:

```text
ConformsTo : [reference, reference, scope]
TargetKind : [reference, text]
```

Each reference carries id and exact version. The text value `contract` is a checked encoding of a declared node kind, not an implicit new sort. Define an injective selected kind-to-text vocabulary mapping, its domain membership and projection independently. A contract-specific rule requires exact TargetKind support or a separately contract-only projector.

A rich conformance observation requires a member assertion, the selected endpoint pair, exact target version, scope and accepted assessment binding. Node-kind observations require exact member nodes and local unique references. One atom can have several assertion/assessment supports; deduplicate atoms while retaining the complete support set. Include graph/profile/source-definition/assessment/projection identities in support records.

The unary Conforms view is existential only for the projected initial inventory. It is not a producer rule writing the old predicate under fresh-head extension, and it is not an equality theorem for all arbitrary old models. Explain a subject with one exact conformance differently from a query about another target or scope.

Tasks: S00, S02, S15, S16, S18. Findings: I03, I07, I08.

## 3. Separate inherited norms, activation and fulfillment

The retained stress Origin predicate propagates potential norms. Its condition is a label with a known interpretation, not an executed Boolean. The successor defines:

```text
PotentialNorm(G,e,n) := independently defined Origin(G, {edge=e, norm=n})
ActiveNorm(G,e,n,K) := PotentialNorm(G,e,n) and CheckedHolds(e.condition,K)
ActiveConflict(f,h,K) := ActiveNorm(f,K) and ActiveNorm(h,K)
                        and same subject/action/scope
                        and require-versus-forbid
```

PotentialNorm remains independent of supplied conformance rows and of condition truth. ActiveNorm has an exact evaluation key and holds witness. Fulfillment needs a separate action/receipt/outcome contract and remains deferred. A `permit` norm neither erases require/forbid conflict nor supplies organizational execution authority. Existing potential-conflict results stay valid under their current meaning.

Required targets include origin preservation, conformance independence, activation soundness, no activation from missing/false/mismatched/conflicting evaluations, and exact active-conflict support. More complicated condition algebra, hierarchy propagation and override precedence require separate meanings and proofs.

Tasks: S00, S04, S07, S08, S10. Finding: I05.

## 4. Assessment identity is not assessment agreement

Specify an evaluation key using the selected profile, condition definition revision, exact context/snapshot, relevant subject/target/scope and epoch when the meaning is temporal. Bind evaluator/interpretation and supporting source identities. Do not add an epoch to a timeless meaning merely for transport uniformity.

Proposed first-profile policy: allow several source supports for a consistent selected status; reject inconsistent selected holds/does-not-hold for the same key with an explicit conflict diagnostic that prevents positive projection. Unselected competing assessments need a separately explicit selection policy; the adapter cannot silently choose the first accepted row. A different context or epoch is another evaluation, not a contradictory status for the same key.

Missing or uninterpreted evaluation is unknown. An explicit checked negative status is not absence-as-negation. Invalid shape or conflicting selected evidence is invalid; unresolved interpretation is unknown. Accepted flags and clock/issuer truth remain supplied assumptions unless another contract verifies them.

Do not retrofit global uniqueness to all F0 assessments: F0 already prevents ambiguity by token and binds tokens to exact endpoints/scope. The improvement is a scoped successor evaluation policy, especially needed for stress conformance and new condition records.

Tasks: S00, S04, S07, S10. Finding: I04.

## 5. Establish baseline and change contracts before code generation

A registered baseline binds graph, registry, typed theory/domain/predicates/rules/initial facts/roots, profile, interpretation records, source manifests, epoch, verifier/toolchain/policy and exact required statement catalog. Baseline registration means independently qualified candidate state, not organizational admission. Keep canonical object identities and exact file-byte hashes distinct.

| Change class | Conditions | Required scope |
|---|---|---|
| Rule-only fresh definitions | Same domain, roots, old predicates, old rules and old initial facts; fresh permitted derived heads | General recursive expansion plus concrete hypothesis/producer checks |
| Richer baseline capture | New source facts, values or selected vocabulary | Independent source projection, domain accounting and declared migration relationship |
| Condition/assessment update | New evaluation context or status evidence | Exact source/context binding and affected outcome invalidation |
| Fresh structural kind | Exact appended registry declaration | Retained structural preservation, plus separately selected semantic interpretation if any |
| Mixed or old-meaning mutation | Old predicates/rules/qualifiers/meaning changed | Unsupported until a separately specified preservation/transition profile exists |

S15 defines the contracts and catalogs. S18 qualifies source and richer-data transitions. S05/S06 then implement generators against them. S09 qualifies two-step shadow application using the existing contracts. This removes the earlier dependency inversion.

Local uniqueness of NodeRef is not a global content immutability theorem. The selected baseline policy must either check that the same reference retains kind/content across snapshots or demand a new revision. External resolver behavior, authenticity and hash assumptions remain visible. A receipt from the old baseline cannot discharge successor obligations.

Tasks: S15, S18, S05, S06, S09. Findings: I02, I08, I09, I10.

## 6. Treat source adapters as proof-bearing boundaries

Every legacy qualifier maps to an independently fixed typed field, deliberately opaque value, supplied external assumption or unsupported feature. Some typed stress fields have no direct legacy qualifier and must come from separately bound interpretation/delegation/contract records. Do not reconstruct an action list or truth assessment from a nonempty string.

Conformance has a concrete shape mismatch: the registry declares conformance_evidence_refs, while F0 consumes one exact evidence token. Choose a selected supported witness/list interpretation and prove it; do not turn an arbitrary list into a single string without a correspondence statement. The broader registry endpoint vocabulary also needs an explicit selected fragment. F0 AdmissionRoot has no automatic mapping to the inference reference/effect/scope/epoch tuple.

Structural source schemas, normalized registry, typed Lean input and actual executable profile are distinct layers. Decoder/generator differential checks can establish bounded empirical agreement, but only a separate equivalence proof justifies claiming their full correspondence. Bind trusted imports and exact required statements before expanding the verifier allowlist.

Tasks: S04, S15, S18, S05, S07, S10. Findings: I08, I10.

## 7. Resource checks must precede expensive construction

The reference enumerator considers `d^k` substitutions for each k-variable rule, then checks sorts. A safe preflight count can use this reference bound; a proved typed enumerator can later use the product of per-sort value counts. The finite atom-universe bound similarly sums products of argument-domain cardinalities for declared predicates. These are count bounds, not predicted seconds or memory usage.

For the stress profile, candidate count is inheritance count times the total number of contract norms. A conservative conflict-pair bound uses the square of that candidate bound, avoiding closure construction merely to decide that work exceeds the envelope. Retain exact evaluation once admitted; an overconservative preflight refusal is unknown, not a semantic negative.

S17 introduces small measured probes and stage limits before rich integration. S11 measures qualified end-to-end work. S12 is conditional on a measured bottleneck and requires equality/correspondence evidence before enabling optimized semantics. If early feasibility already fails, tighten the supported envelope or bring necessary proved optimization forward; do not wait for the final pilot to discover infeasibility. No semantic-readiness cache is introduced.

Tasks: S17, S11, S12. Finding: I06.

## 8. Return a claim whose obligations were actually checked

| Returned claim | Necessary evidence | What remains outside that claim |
|---|---|---|
| Candidate edge is valid | Exact selected InstanceValid/checkInstance | Edge inventory membership or effect execution |
| Observed contextual conformance | Exact source membership, checked projection/support and selected assessment binding | External issuer truth, other targets/scopes, admission |
| Query derivable | Accepted certificate under exact theory/initial facts and producer profile | Complete closure or world-level truth |
| Query not derivable in this profile | Accepted complete exact closure and typed query absence | Explicit false condition or failure in reality |
| Implication not entailed | Checked model containing exact premise and excluding exact conclusion | Conclusion always false |
| Inherited potential norm | Exact Origin support and composed graph validity where requested | True condition, conformance or fulfillment |
| Active inherited norm | Potential norm plus exact consistent holds witness | Action completion or organizational permission |
| Stress certificate valid | Origin and shape of its listed facts | Whole graph validity, requested query and complete closure unless separately checked |
| Shadow proposal ready | Every generated hard obligation current and freshly replayed, exact before-state | Human approval, organizational authority or live deployment |

Explanations include claim kind, profile/model class, exact supports/substitution, supplied assumptions, currentness, resource completion and pending human status. An unsuccessful certificate search or budget timeout returns unknown. Separate execution status from semantic verdict and readiness.

Tasks: S08, S10. Findings: I07, I11, I12.
