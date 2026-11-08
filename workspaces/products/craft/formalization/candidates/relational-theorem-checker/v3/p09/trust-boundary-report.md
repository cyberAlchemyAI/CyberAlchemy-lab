# What P09 qualifies

This review covers the composed v3 public interface for the existing finite positive recursive profile. Executed results and exact bindings are in `qualification-suite.json` and `regression-report.json`; the task remains incomplete until those reports exist, pass, and are accepted. The reports distinguish newly executed checks from the 342 unique controls inherited by exact current acceptance bindings from P00–P08.

The representative proposal adds three information rules to the old rule `Conforms(x) → BaselineSignal(x)`:

```text
BaselineSignal(x) → FreshReview(x)
FreshReview(x)    → FreshReady(x)
FreshReady(x)    → FreshReview(x)
```

The cycle can propagate a checked seed. It cannot create a seed merely by referring to itself. The concrete positive example derives readiness for the already conforming reviewer. The concrete negative example has no `FreshReady(contract:review)` in the complete selected closure. That absence is about this finite input and its rule semantics. It does not claim that the contract cannot be reviewed in another context.

The second proposal adds `FreshReady(x) → EpochMarker(0)`. This deliberately exercises a different term sort and the actual query-number regression through a freshly checked, committed successor. Both layouts use the same graph, fixed catalog, semantic profile, operator policy and constructor provenance. The richer target/scope cyclic source remains covered by the accepted P08 actual application evidence. A representative successful layout comparison does not establish that every richer workload fits the same time budget.

The principal logical theorem is model conservativity: under the exact checked rule-only extension hypotheses, every model of the old root-constrained Horn theory has an expansion to the new theory preserving the meanings of all old predicates. This is a quantified Lean theorem, not a comparison of two sampled closures. Complete least-closure computation supplies a different concrete theorem: every reported derived atom has a valid derivation, and the complete closure contains exactly the derivable atoms in the selected finite profile. The source-faithful subclass additionally requires the old sealed interpretation to equal its exact projection; that hypothesis cannot be manufactured by a new rule.

The semantic part checks exact source projection and supports. Conformance and checked admission roots originate in the independent assessment/context interpretation required by the profile. A caller fact or derived head cannot become such a root. `FreshReady` and `EpochMarker` are information predicates: their names do not grant authority, establish fulfillment, or authenticate real-world evidence. An active norm requires checked condition truth and valid period/context. A potential norm alone is insufficient; an active require/forbid pair remains a conflict with both origins retained. No conflict diagnostic establishes fulfillment or admission.

The twenty rule-only obligations retain these distinct methods:

| Obligation | What is established |
| --- | --- |
| snapshot-shape | Tested closed transport and typed profile validity |
| source-current | Exact selected bytes are current |
| profile-catalog-current | Exact full catalog, policy and import/toolchain closure |
| reference-immutability | Structural witness preserving referenced identities |
| producer-policy | Kernel witness forbidding derived sealed heads |
| projection-exact | General theorem for source projection |
| kind-projection-exact | General theorem for kind projection |
| unary-view-exact | General theorem for the existential unary view |
| sealed-derivation-exact | General theorem relating sealed observations and derivation |
| source-support-exact | Concrete witness for every sealed observation's supports |
| typed-theory | Concrete validity witnesses for theory and initial facts |
| protected-lineage | General theorem preserving checked-root lineage |
| derivation-soundness | General theorem that derivations satisfy the Horn semantics |
| closure-adequacy | General theorem connecting complete closure and derivability |
| complete-closure | Concrete closedness and derivation witnesses |
| source-interpretation | Concrete independent mapping witnesses |
| condition-consistency | Concrete checked condition consistency |
| old-frame-identical | Structural witness for unchanged old graph/facts/domain/roots/context |
| recursive-extension-hypotheses | Concrete witness satisfying the extension premises |
| every-old-model-expansion | General conservativity theorem for every old model |

All required statement types are fixed independently of submitted manifests and checked in actual replay. Allowed foundational axioms are limited to `propext`, `Classical.choice` and `Quot.sound`; a custom axiom or admitted proof is not accepted. Combined and staged module partition may differ while these targets remain fixed. A successful qualification is not twenty independent implementations of a theorem checker: replay uses the same pinned Lean kernel.

P09 adds five abstract interface theorems: equal typed atoms have the same diagnosis; selecting an equal checked atom does not invent a derivation; elapsed budget has resource cause; explicit cancellation before deadline has cancellation cause; refusal grants no claim permission. The executable JSON parser, canonicalization lookup and supervisor composition are covered by finite controls. They are not proven implementations of those abstract functions for every possible input or operating system.

Freshness is operational and deliberately separate from saved evidence. A full invocation, checked source/proof closure, complete cleanup and current owned record create a private process-local event. Saved inspection can report `recorded-current` without creating that event. Shadow application requires the exact reviewed head, a new proposal event, a separately checked successor registration, every selected mapped context, and a one-time transaction handle. JSON response validation cannot substitute for these checks. A success response additionally identifies matching heads and a committed transaction; recovery can preserve a prior commit but does not create new proof freshness.

The test policy permits 60 seconds per atomic tool, 600 seconds per run, 4 MiB of output and one supervised worker. Its 4 GiB memory setting is advisory on this host: aggregate RSS is observed, not hard-limited. Required cgroup enforcement without a delegated writable backend refuses before launching a worker. Process cleanup and crash-window tests support the stated cooperating-host transaction guarantees. They do not prove resilience to arbitrary filesystem corruption, power loss, a malicious host or races outside the ownership/locking assumptions.

The failed staged application retained in the layout suite exhausted the atomic-tool deadline during fresh general-theorem replay and left its store at generation zero. Its diagnostic is evidence of refusal, not proof completion. A fresh retry must discharge all obligations before either application can be reported successful. The failed run remains separately bound; its intermediate compiled modules do not count as a complete qualification.

External assessment truth, tested JSON normalization/source generation, the pinned compiler/kernel/import closure, hash execution, and the cooperating host remain assumptions. This finite regression qualification is suitable evidence for bounded local candidate work. It does not establish independent-kernel assurance, externally authenticated conformance, deployment approval, live admission authority, general latency guarantees or implementation of the seven selected extensions.
