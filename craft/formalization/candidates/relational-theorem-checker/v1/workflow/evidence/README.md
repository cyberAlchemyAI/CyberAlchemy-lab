# Candidate evidence replay and readiness

R03 derives the required obligations from the bound proposal, validates every artifact role and byte identity, replays the actual checks, and aggregates their verified results. JSON schema validation and transport validation are preliminary checks; neither establishes semantic readiness.

`bundle-verifier BUNDLE --proposal PROPOSAL` and `aggregate-verifier BUNDLE --proposal PROPOSAL` both run the full verifier. The latter reports the `replay-evidence` command. It never accepts a client-owned result table to aggregate. Each command writes one outcome to stdout and progress to stderr. R04 supplies the common review CLI and its input-error adapter.

The Python entrypoint is `aggregate.verify(proposal, bundle=None)`. Omitting the bundle requests fresh built-in checking of every mandatory obligation. `bundle_contract.make_bundle(proposal)` generates a complete request from current dependencies. An entry with `method: builtin` and no artifacts is a request to compute evidence, not a claim that the check passed.

Declaration-source bindings in both snapshots are fenced before classification or the older source-projection helpers can read them. Each source must resolve inside the workspace, match its original-byte digest and decode as a strict JSON object within 4 MiB. External symlinks, duplicate JSON members and oversized files reject before semantic execution. This strengthens the local successor without changing accepted predecessor bytes.

Compiled carrier schemas pass the Draft 2020-12 metaschema check before coverage is accepted. A declaration with no allowed endpoint pairs retains its formal meaning: its carrier uses a single false schema alternative, rejecting every instance of that kind. Existing instances and useful old models remain valid. No artificial nonempty-pair restriction is added to the formal profile. Each complete replay saves its actual compiled carrier schema.

The named execution profiles are:

| Profile | Verified scope |
| --- | --- |
| Unchanged or instance-only | Captured 41-kind closed-string carrier, actual graph invariants, exact supported F0 semantics and references, preservation/conservativity and inhabited model |
| Fresh-kind extension | The same scope plus the captured pure `trace-label-for` annotation declaration and actual extension hypotheses; 42 kinds and 551 ordered pairs in the fixture |
| Rule-only extension | Unchanged graph/registry, empty old-rule baseline, fresh ordinary unary `ReviewSignal` heads and positive old-predicate bodies, finite typed domain, checked complete closure, protected lineage, exact non-entailment witness and model expansion |

Other legacy relation meanings, endpoint widening, mixed graph/rule edits, old-predicate heads, fresh recursion, nonempty prior rule sets and broader inference semantics require another supported profile. Structural coverage does not establish all source semantics. The unary `Conforms` projection and static candidate epoch retain the I06 interpretation boundary.

`evidence-bundle-schema.json` describes the transport. Required IDs, names, hard flags, scopes, allowed methods and complete dependency objects are independently derived and compared by the runtime. Clients cannot select a smaller obligation inventory or weaken its policy. The scoped-model wrapper binds unchanged raw witness bytes using `scoped-model-schema.json`; it explicitly distinguishes a checked finite model from a universal theorem. Bounded-search documents preserve provider output as untrusted data. Completion, exhaustion or a provider `found` flag supplies no proof or readiness.

Submitted proof requests go through R02's exact-type, transitive-assumption, isolated kernel replay, including its full pre/post dependency checks. Built-in proof families are independently audited against the trusted required type and then instantiated with the actual extension hypotheses. Countermodel-checker soundness alone cannot replace a valid scoped countermodel. Registry and inference models are checked against their exact current theory; a countermodel for another ground implication cannot discharge the required implication.

Selected-data compatibility, invariant preservation and model conservativity remain distinct dimensions. Invalid selected data may coexist with valid general preservation and model expansion. Rule extensions require their actual rule conservativity in addition to registry conservativity. Every mandatory obligation must have completed, current, allowed verified evidence before `ready-for-review`; omitted, stale, unsupported or unknown evidence prevents readiness.

Fresh builds use private temporary directories. Captured and generated registry modules compile with one Lean worker and a bounded 180-second budget per module; module audits record the actual elapsed time and source/output identities. Captured sources and generated proof statements are unchanged. Generated source and axiom policies are checked explicitly. Other predecessor and isolated proof budgets retain their existing policies. A timeout yields unknown and prevents readiness.

Persisted source, module audits, individual obligation evidence and final outcomes live in `runs/`. Full source/profile/graph/rule/proof/runtime manifests are compared before and after execution. A changed hash or newer timestamp cannot repair an old receipt. The current local filesystem ownership model, Python projections, source interpretation, assessment truth, pinned Lean kernel and OS remain trusted. No HTTP artifact service, admission decision or live deployment is provided.

Generated source snapshots are scoped to their obligation. The inhabited-model and independence proofs have different filenames. Before readiness is returned, the verifier rechecks every registered generated source and evidence-file binding, so an overwritten earlier snapshot becomes stale rather than remaining accepted.

`python3 run_transport_controls.py` exercises closed transport and method/role checks. `python3 run_evidence.py` replays five complete positive cases across four computed profiles (including an empty-denotation fresh kind), an actual selected-data violation, actual wrong proofs and models, and omission/staleness/policy/search/source-boundary controls. `python3 schema_contract.py` validates the documented schemas against the complete example bundles. The acceptance receipt describes candidate author review; human assessment of meaning and diagnostic usefulness remains R06/G4 work.
