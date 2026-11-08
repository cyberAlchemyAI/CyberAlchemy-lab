# Design evidence: maximize Open Ontologies code reuse

Source review only. No builds, dependency installation, source copying into Lab, or tests were performed.
OO source: /tmp/cal-open-ontologies.ANeAQC/repo at c7fd75f9491253c56e4d4f408ceac179de343e48.
Lab source: current definition-assurance-v1 and relational-checker v3 implementation.

## Recommendation

Copy/pin the whole upstream Rust crate and its proof-source package unchanged, then call a very small purpose-built worker. Do not hand-extract a fresh mini reasoner out of three modules. Reuse upstream's reasoning, certificate indexing, per-goal slicing, checking, closure comparisons and report distinctions as code.

Keep the Lab's existing definition resolver, typed interpretation/translation, required-obligation accounting, source currentness, supervised invocation, fresh-evidence issuance and lifecycle handling. Introduce a new named analytical provider rather than altering accepted E00-E06 profiles or pretending OO answers are existing finite-model answers.

Recommended initial callable operations:
1. preserve_required_goals: source RDF, one candidate view, explicit positive ground goals.
2. compare_closures: source RDF and candidate view, with derivations and loss reporting.
3. inspect_consequences: exact before/extension inputs, explicit delta-or-replacement mode.

These operations write only disposable engine/evidence outputs in the owned job. No plan/apply, rollback, graph push, arbitrary query/update, dynamic tool invocation, plugin, web import, external-model route or canonical event writer is exposed by the worker.

## Copy boundary

Prefer an immutable upstream source mirror under a versioned third-party home, with a provenance manifest that records URL, full commit, selected paths, byte sizes, SHA-256, license, and patch-free source comparison.

Keep at least:
- All src/*.rs (the whole main crate), Cargo.toml, Cargo.lock, LICENSE, README.md, package-referenced metadata and applicable .cargo configuration.
- The complete lean/ source package, lakefile.toml, lean-toolchain and its source license context. Build only the selected checker targets for the initial profile, but keep their full source closure.
- The relevant upstream tests and fixtures for projection preservation, closure differences, conservativity, certificate mutation, literal spelling and source scope. Record exact original paths. The research review did not classify every dataset license; do not indiscriminately copy case-study datasets.
- An upstream source/lock record for the required Oxigraph fork; use its exact revision rather than a floating branch.

A complete unchanged repository mirror is acceptable if storage/review policy prefers that over a curated source archive. Runtime use should remain narrow even if the source mirror is broad.

The direct source references show why extracting three files is fragile:
- projection_entailment references graph, projection_check, reason, runtime and verdict.
- closure_diff references graph, projection_entailment, reason, runtime and verdict.
- conservativity references closure_diff, graph and projection_entailment.
- reason additionally reaches boundary_core, justify, provenance, tableaux and temporal.
- graph reaches canon, ofn and reason.
These are lexical references, including test/comment references; they are evidence of coupling, not a compiler-resolved minimal closure.

The main library publicly compiles a broad crate even if the worker calls only three APIs. Keeping all upstream source saves implementation work but does not eliminate build time, dependency review or resource cost.

## Narrow worker: preserve upstream source or use existing CLI?

Preferred durable boundary: a separate tiny Rust worker crate importing the unchanged path dependency, with a closed request enum and one response envelope. It calls these existing public APIs:

- projection_entailment::parse_goals_turtle / parse_goals_tsv and check_entailment_preservation (projection_entailment.rs:284,317,1387).
- closure_diff::SourceClosure::build, SourceClosure::diff or closure_diff (closure_diff.rs:489,602,883).
- conservativity::conservativity_check (conservativity.rs:298).

The wrapper only validates transport/profile selection, constructs a new in-memory GraphStore, loads exact exported bytes, constructs fixed upstream options, calls the function, and serializes the native report. Lab-side accounting performs semantic/binding validation. This is a wrapper around upstream code, not a rewritten inference engine.

Cargo caveat: a [patch.crates-io] inside a dependency is not the controlling top-level patch. The worker/workspace ROOT must explicitly pin the same Oxigraph source revision as upstream:
37db8e1522585ed2f9aa994be6c5c716859af5c8.
Freeze and check the resolved complete lockfile for the wrapper, not just upstream's now-non-root Cargo.lock. If the upstream crate is built as its own standalone root instead, its own patch/lock are controlling. Use no optional features initially; do not silently replace the patched store with stock oxigraph.

An even smaller first executable seam can invoke the unchanged upstream CLI using a generated JSON batch: same-process load then preserve/closure-diff. Use --no-connect, a fresh --data-dir and fixed owned output paths. A standalone load followed by a separate standalone preserve loses the in-memory source (main.rs:3814-3820). No caller can submit raw batch commands. This option is excellent for proving the seam without a Rust wrapper, but direct library calls expose conservativity more cleanly; the existing plan CLI also performs persistence, logical risk work and unrelated planning.

## Checkers must be fixed dependencies

Copy upstream proof code, not just reports claiming it passed. Pin/build the relevant oo-cert and oo-horn targets from the exact lean/ package and leanprover/lean4:v4.33.1. Preserve upstream theorem scopes:
- oo-cert checks the supported built-in rule certificate.
- oo-horn checks derivations under supplied rules; those rules remain assumptions.
- A positive checked derivation says neither that source facts are true nor that a Lab action is authorized.

Pass a fixed absolute checker path in projection_entailment::Opts and closure_diff::DiffOptions. User input must not choose a checker binary.

Important special case: ConservativityOptions has no checker path field (conservativity.rs:134-149); conservativity_check creates DiffOptions with checker:None (347-350). To keep that code unchanged, the fixed worker must set OO_CERT to the trusted pinned checker in a sanitized per-process environment. Do not rely on arbitrary PATH/CWD discovery; find_checker falls back through explicit path, OO_CERT/OO_HORN, repository paths and PATH (projection_entailment.rs:742-776).

Upstream's CheckerRun computes a SHA-256 over ordered named input files before spawn (verdict.rs:139-151,168-184) and produces an earned result token. That is useful code to retain. The Lab still must pin the executable/definition closure, audit the actual arguments, bind exact input/output bytes and recheck them at completion. A caller-chosen program printing an expected theorem string must not become a trusted checker.

For maximum confidence, the Lab verification stage should replay selected certificates using the independently pinned OO checker, recording its command, input digests, output and exit. Preserve OO's native internal checker outcome separately from this Lab-side verification. This is additive to existing relational-core Lean replay, not a replacement.

## Where the Lab already supplies the surrounding machinery

Definition assurance:
- contracts.py:1-158 provides bounded strict JSON decoding and one fixed local schema. It prevents callers choosing schemas and rejects duplicate keys/nonfinite numbers/invalid Unicode.
- resolver.py:178-215 captures and reconstructs exact source/registry bindings and distinguishes current bytes from semantic truth.
- ir.py supplies typed source-qualified interpretation and composition. A new RDF export should begin after those checks, not from raw unqualified names.
- obligations.py:60-85 computes a complete required set, exact scopes and minimum evidence strengths.
- bundles.py:29-59 validates the fixed evidence contract and captured inputs; 62-91 supplies owned no-follow writes and no-replace publication.
- verifier.py:118-147 checks exact finite provider/input bindings and independently evaluates a supplied model. Lines 254-259 do not let a model witness discharge a universal requirement.
- invalidation.py records source/dependency/role/profile/build changes and rechecks cache candidates; a new OO provider must include its mapping, rules, binaries and proof sources in that closure.

Relational v3:
- p06/supervisor.py supplies process-group ownership, time/cancellation/output control, teardown and conditional resource enforcement.
- p06/API.md separates incomplete/refused runs from qualified outputs and never grants application authority.
- execution/extension_runtime.py:54-94 binds raw input, exact source/compiled imports, owned witness/output, deadlines and private process-local issuance. Saved results cannot mint a fresh event.
- p07/API.md adds independently anchored cache keys, create-only finalized evidence and read-only saved inspection.
- e04/store.py retains exact current-head/generation conflict checks and lifecycle commits.

These APIs are not currently generic extension slots:
- p06/supervisor.py:122-123 requires the owned run root to lie under v3.
- extension_runtime.py accepts only fixed E00-E06 and checks their accepted source receipts.
- definition-assurance-v1's current verifier only understands its selected finite evidence contract.

Therefore create a reviewed successor provider with its own fixed owned root and closed schemas. Reuse the supervisor/client mechanics through a small explicitly documented ownership/import adaptation or an approved shared support extraction. Do not modify accepted v3 source in place, add OO to E00-E06, or smuggle OO JSON into the finite provider's existing result schema.

## Required Lab adapters

A. Exact source selector:
Capture an immutable ontology cut or selected definition/interpretation inputs, meaning and review event references where used, and required goals. Bind raw request SHA-256, every source version/digest, branch/scope, selection exclusions, completeness and resource profile.

B. Versioned export mapping:
Use stable source-qualified IRIs; preserve subject version and digest, relation identity, direction, qualifier roles and selected vocabulary. Initially refuse blank-node-bearing or unsupported mappings rather than guess. An arbitrary n-ary typed atom is not automatically an RDF triple: reification and predicate encodings need explicit preservation obligations. OWL domain/range inference must not substitute for Lab closed endpoint-pair checks. Unsupported functions, quantifiers, negation, closed-world absence or guarded authority roots stay refused/outside-profile. Keep original values/literals and graph identities exact.

C. Fixed invocation:
Bind provider version, full upstream commit/source manifest, wrapper source/binary, Cargo resolution/fork revision, rule table/profile, Lean/checker source/binary, supported logical fragment and environment. Source selection plus reasoning should operate on the owned captured dataset, without later re-reading mutable Lab state or a shared live OO server.

D. Result verifier/accountant:
Retain native output and raw artifacts; hash them with SHA-256. Upstream closure_diff.asserted_digest uses FNV-1a for identification only (closure_diff.rs:436-446), so it is not an integrity commitment. Verify manifest references, source/export membership, native report identity, certificate inputs/checker outcome, completion/fixpoint and all required goals. Generate a new distinct provider evidence result with application_authorized:false and authority_effect:none. Treat translation fidelity as a separate condition from native proof validity.

E. Evidence publisher:
Use existing create-only bundle/currentness practices and process-local result issuance. Saved inspection and cache reuse return recorded-current, never fresh proof or authorization. Add OO mappings/rules/checkers/limits to invalidation keys. New independent-checker proof families should not invalidate or replace the existing Lab proof APIs merely because the same word "checked" appears.

## Result distinctions to preserve

Do not normalize these to one passed/failed boolean:

- asserted membership; inferred but unchecked; inferred and checked under built-in rules; inferred and checked under supplied rules;
- lost-under-profile; never-supported-in-source; projection-only inconsistency with subset/monotonicity assumptions; refused goal;
- certificate rejected; certificate unreadable; checker missing/unavailable; checker killed/failed;
- complete fixed point versus truncated computation; unsupported semantics versus resource exhaustion/cancellation;
- rule-table conservativity versus full logical/model conservativity;
- Lab mapping-valid versus mapping-unknown; source-current versus truth-authenticated; recorded evidence versus fresh process-local completion.

Native references: projection_entailment.rs:891-986; closure_diff.rs:156-215,342-383; conservativity.rs:63-91. A no-difference result under a partial rule profile cannot satisfy an existing Lab minimum strength demanding a broader universal theorem.

## Meaningful hostile controls for implementation

1. Preserve a genuinely derived goal from an exact source/view; remove one required premise and require lost-under-profile rather than checked preservation.
2. Ask a goal absent from both source and view; require never-supported-in-source, distinct from retrieval loss.
3. Inject a projection-only triple or swapped source; require source/subset diagnostic or stop-the-line, not a valid preservation result.
4. Change a Lab subject version/digest, qualifier, scope, encoded n-ary argument or export mapping while leaving its label fixed; reject before or during Lab verification.
5. Change a rule table without changing the declared profile; reject identity. Supplied rules must keep supplied-rule verdict wording.
6. Supply negative/universal/function-bearing unsupported requests and ensure they remain outside-profile; no vacuous green empty goal list.
7. Mutate a derivation premise or conclusion; actual OO checker must reject. Replace checker with a zero-exit fake printing the right theorem; Lab binary/source pin must reject it.
8. Swap or mutate certificate files between prehash, invocation and finalization; either retain the original immutable owned input or refuse currentness.
9. Delete/truncate a certificate or kill checker; distinguish unreadable/unavailable from rejection and from checked success.
10. Force iteration/scan/output/time limits; require incomplete/unknown and suppress absence/conservativity/fresh claims. Exercise one real child-process cancellation and verify every owned descendant exits.
11. Repeat two jobs simultaneously with separate directories; no crossed certificate/report/input identities. No daemon auto-connection or shared graph.
12. Reopen saved evidence/new client or replay a completion JSON; no fresh event. Change mapping/source/checker after a cached report; invalidate or recheck.
13. Protect canonical Lab event/decision bytes before and after every analytical job. The engine may write its owned artifacts only.
14. If blank nodes are later supported, require lexical/datatype/graph identity and canonicalization/relabeling cases with explicit budget refusal. Copy relevant upstream lexical-form regression fixtures.
15. Check differential equivalence against the Lab typed closure on a deliberately supported overlap; do not compare an RDF profile and a richer Lab theory as if they were the same semantics.

These tests concern new adapter/proof boundaries; they are not redundant copies of an implementation detail. Existing upstream tests should also remain runnable from the unchanged mirror.

## Decision summary

Reuse maximum existing implementation:
- Upstream complete source + lock + fixed fork + proof sources.
- Upstream preservation, closure and consequence-report functions unchanged.
- Existing Lab strict decoder/source capture/IR, evidence accounting, supervision, cache/currentness and lifecycle policies.
- New glue limited to a faithful export profile, a fixed owned worker invocation, a distinct native-result verifier/evidence schema and integration controls.

No replacement of canonical event history, typed closure/conservativity theorem, trusted statement replay, protected authority roots, owner acceptance or lifecycle commit machinery is justified by this engine reuse.
