# Design choices for the amended Define integration plan

Status: selected in this planning revision, pending the applicable exact owner reviews. No implementation or authority contract is admitted by this document.

This closes the design alternatives exposed by audit 0004. Each choice has implementation and verification obligations in the amended work map. A planned mitigation is not evidence that a runtime risk has disappeared.

## C01 — Formal meaning and assurance

The revised Definition Pack draft declares a finite nonempty required concept set, a total function `delta: C -> D`, a matching payload function, and explicitly grouped reference obligations. `ValidationScopeDeclared(V)` is an independent required conjunction. Duplicate disposition rows are rejected before constructing the function; overwriting a duplicate map key cannot establish uniqueness.

The proposed operational interpretation binds each predicate to an observable carrier or evaluation obligation. Assurance reports distinguish structural checks, finite interpreted-model checks, semantic fidelity review and any stronger separately supported proof. Textual difference and supplied rationales are preliminary evidence only.

For the two new meanings, review covers comparisons with every current registered meaning and follows the declared dependency/consumer impact inventory. The report lists exact source clauses, interpreted clauses, assumptions, domains, controls, outcomes and coverage. Required clauses that remain uninterpretable or unevaluable block the claimed assurance/readiness; they cannot be omitted to obtain PASS. Temporal or permission claims require their selected operational/extension support. No whole-repository or unrestricted semantic-consistency proof is promised by a finite check.

Early work prepares the finite/structural results and the fidelity review package. The actual semantic owner confirms the governing interpretation in its exact decision; that future determination is not required to build a candidate prototype and is not recorded as an early PASS. A pre-decision evaluation can be eligible only when its required non-decision checks pass and its owner-selection check remains explicitly pending under the bound profile.

See [the revised Pack draft](definitions/definition-pack/DEFINITION.md) and [its interpretation](formal-interpretation.json).

## C02 — Semantic-owner trust

The first release uses the existing **explicit human-owner decision in the trusted conversation** mechanism for repository admission. The precedent is the exact authorization record for Lab Operational Runtime/v1. Its declared principal and scope must still be reconciled with the applicable admitted role assignment and authority boundary; a historical decision cannot authorize new targets.

The Define CLI prepares and reviews exact targets. It cannot create human-owner evidence, authenticate a human from a supplied JSON string, or promote repository definitions using a provisioned local operator key. Any owner-controlled repository application is a separately authorized, attended action based on the actual human message and exact reviewed manifest. Persisted authorization is a record of that event, not proof that an arbitrary file really came from a human. The trusted host/user channel and owner-controlled repository custody are explicit assumptions of this route.

Local signing remains limited to the provisioned local branch. Shared-scope semantic promotion requires the exact applicable human-owner effect. Caller `actor_ref`, `allowed_effects`, routing labels and `user_confirmed` remain declared inputs. Automated repository promotion by a machine signing key is outside this release until a separate admitted principal/key enrollment or delegation establishes that right.

## C03 — One byte buffer for source validation

Each selected file is opened within its declared root, read once into a bounded byte buffer, hashed, strictly decoded as UTF-8, and parsed from that same buffer. The decoder rejects duplicate object keys, nonfinite values, unsupported numeric precision and excessive nesting according to the applicable protocol.

The captured snapshot retains the original bytes/digest and decoded record. Later checks compare current material with the captured digest; they never reopen a path to supply the document for a digest already recorded. Immutable epoch material is selected once. Changed mutable inputs invalidate preparation and require a new capture.

This decoder is part of the early preview's candidate source provider and is reused by the later successor reader. Existing admitted source and runtime files are preserved as history.

## C04 — Publish a selected immutable epoch

The repository application path stages one immutable, digest-closed admission bundle containing the selected semantic records, registry/index/drift material, profiles, source selections, histories, state and receipts. The existing **current Project State lookup** is the one visibility pointer. Its `admission_bundle` binding selects the complete epoch; it stays a derived address/lookup with `authority_effect: none` and `replay_source: false`. Authority remains in the exact admitted bundle and its owner decisions.

The successor reader resolves all current material through the selected bundle/source map. It validates the lookup, bundle, admitted input/effect evidence and exact material digests. It must not combine a new State with the old hardcoded vocabulary root or arbitrary workspace files. The new representation/source-direction binding and all declared consumer updates are explicit review targets; moving registry currentness into selected epoch material is not an implicit change to canonical ownership.

Workspace registry/index/drift compatibility paths become explicitly generated compatibility surfaces under that reviewed binding. They are refreshed after the pointer commits and are not a second authority or inputs to the successor's currentness decision. Existing readers that require the historical mutable registry equality can report stale/unsupported; they cannot label a mixed epoch current. If the required representation change or consumer compatibility is rejected, repository advancement is blocked.

The first implementation targets the present Linux/WSL local filesystem. One owner-controlled cooperative writer lock covers pointer comparison, staging publication and commit. Under that lock, the writer compares the expected old lookup digest, validates and flushes immutable staged material, publishes it without replacement, then atomically replaces and flushes the lookup. A reader loads one lookup byte buffer and pins that epoch for its operation. Before commit, recovery discards only declared uncommitted staging; after commit, it preserves the committed epoch and regenerates compatibility surfaces. Semantic reversal requires a separately authorized successor/withdrawal route.

This is a scoped commit protocol, not protection from an arbitrary privileged process rewriting the repository. External edits or custody violations produce integrity/stale diagnostics. Unsupported storage guarantees fail explicitly. The launcher/provider transition is an exact reviewed compatibility action; the epoch-aware candidate is exercised before the current entry changes, and a transition can expose an explicit unavailable/stale state rather than a false current state.

## C05 — Inputs, decisions and generated outputs

Use three separate manifests:

1. **Reviewed inputs:** exact candidate bytes, source selections, contract/code/generator hashes, target cores, base epoch, requested effects and output recipe.
2. **Decision evidence:** the actual independently scoped owner outcomes, recorded only after the trusted human selection.
3. **Observed consequences:** outputs generated from those inputs and selected outcomes, followed by application receipts and final lookup binding.

Owner approval binds reviewed inputs, effects, preconditions and the exact generator/recipe. It does not pretend to bind a future signature or timestamp that does not yet exist. Fixed output postimages are prepared before selection where possible; authorization-dependent fields are explicitly enumerated by the recipe. No undeclared output is permitted.

The staged output manifest contains exact digests of its member files but no digest of itself. Files inside the bundle cannot embed the containing bundle's digest. An output source profile describes relative members and their hashes without hashing its own containing manifest. The external current lookup records the final bundle digest after materialization. A receipt may reference input/decision hashes and prior generated materials; an outer manifest can then hash that receipt. These edges form a directed content-dependency graph.

The executable reader and accepted generator recipe are frozen inputs. The final instantiated epoch profile is a declared generated consequence. It is verified against that recipe, not quietly introduced as new unreviewed code. Actual final bytes are checked before pointer publication; any change outside the selected recipe requires fresh review. Fixture, predicted and observed output digests are distinct kinds of evidence.

## C06 — Digest and parsing ownership

Python owns new authority envelope parsing, record digests and signature bytes. The existing `lab_runtime.common.digest` and `encoded` algorithms are the starting pinned serialization contracts for the successor, with strict single-buffer decoding and a versioned interpretation contract. Node does not independently recreate those authority digests; it passes bounded original bytes or exact frozen-file references and consumes Python's results as typed opaque bindings.

Every binding declares its digest kind: raw-file SHA-256, Python authority-record digest, or preserved legacy Node pack digest. These cannot be substituted for one another. Signature bytes are the exact bound Python `encoded` bytes. Legacy Node pack identity remains under its existing algorithm and discriminator.

New authority envelope counters are safe integers within `-(2^53-1)` through `2^53-1`; identifiers, times and digests are strings. Decimal quantities requiring exact precision use schema-declared strings. Referenced artifact payloads retain the numeric contract of their selected schema and are transported as original bytes to Python; they are not round-tripped through Node for authority hashing. Invalid/nonfinite or unsupported precision values are rejected at the strict boundary. Unicode source text is preserved; normalization for search does not rewrite governing statements or signed bytes.

## C07 — Final evidence and documentation

The complete verification matrix depends on the exact full realization binding. The early preview has a separate manifest and bounded evidence; it cannot substitute for full integration verification. Runtime/source manifests are frozen before their tests. Final documentation is then prepared and checked against the selected commands, protocols and candidate behavior before Product/adoption decisions.

Documentation explanations are kept separate from governing contracts. If a late edit changes code, a governing contract, meaning or a behavior described by the candidate, create a new candidate revision and reopen all impacted evidence. A documentation-only edit still requires its link/example/consistency check. The final review package binds both the tested runtime manifest and the checked documentation manifest.

## C08 — Outcome and revision guards

Task completion and selected decision outcome are separate facts. Product continuation requires the qualifying approval outcome. Semantic/profile/source/runtime member effects each require their own exact selected authorization and valid current scope. A local structural PASS is not either outcome.

`revise` creates a new candidate epoch and reopens dependent preparation, compatibility, verification and decision inputs. `defer` pauses only the dependent branch with a named route. `reject` terminates that target's proposed effect. A selected subset must be closed over its required dependencies; if recomposition changes bytes, member cores or bundle membership, generate the exact new bundle and obtain its applicable decisions. No automatic transfer of approval is inferred.

Historical receipts remain historical. New actions check current assignments, source epoch and preconditions; historical replay uses its recorded contemporaneous basis. After an uncertain application outcome, inspect the committed selection/receipt before retrying. Idempotent retry requires the same exact proposal and authorization; it cannot mint a different approval timestamp and call it the same attempt.

## C09 — Consumer compatibility

Preserve existing run/chat output, legacy pack identity and compiler behavior. The new preparation envelope has its own closed version; it adapts a legacy pack plus explicit supplemental input into a **Lab pack candidate v2** with reference standing, named intended use, readiness and lineage. Adaptation material is saved and hashed. The legacy source pack is immutable input, not relabeled v2.

The preparation path accepts the supported Lab pack v2, or performs this explicit legacy adaptation first. Missing values become visible gaps and can block preparation or a named use. The existing Alch compiler continues to accept supported legacy v1 input under its existing no-open-question readiness. Lab pack v2 compilation is explicitly unsupported in this first release. No global readiness flag is relaxed to bypass that limitation.

Legacy durable work-session records keep their exact schema and revision/idempotency behavior. New preparation records link to them through an explicit adapter or stand alone; existing stores are not silently migrated. A declared actor in a saved session is not authenticated owner evidence. Independent work episodes receive explicit caller-supplied job/session identity; a content hash of goal/intent alone cannot merge them. Machine Agent Sessions remain ephemeral, and durable state belongs to Project State or declared work records.

## C10 — Impact and semantic change

Build a version-exact declared impact inventory over current Definitions, carrier semantic bindings, profiles, policies, methods, mappings, sessions and documentation. Search identifiers, version references and source selectors; add declared narrative consumers and record the boundaries of the search. Iterate reachable declared dependencies to closure.

Every affected binding receives one disposition: exact historical preservation, evidenced compatibility, explicit update, deprecation, block, or owner-qualified deferred residue. A foundational Definition successor cannot be promoted while a required current consumer has an incompatible unresolved binding. Typed connections are separately checked against exact allowed endpoint pairs and carrier roles. New global connections remain subject to the admitted extension rule.

Parameter specialization within an existing meaning yields an application binding. A new or changed normative meaning requires an explicit identity/successor classification and complete Definition preparation. Pack partial selection does not resolve unselected concepts or authorize their consumers.

Upstream proposal text is candidate lineage/evidence in this plan. It is not included among admitted governing premises for the new drafts. If a later target needs an upstream selector to govern, it must add a separate exact source-admission effect; no whole-package source promotion is inferred.

## C11 — Initial limits and batching

These are initial contract ceilings to verify, not performance measurements:

| Surface | Initial ceiling |
| --- | --- |
| Pack input / supplemental input | 1 MiB each |
| Total preparation request | 4 MiB |
| Selected source file / captured source snapshot | 16 MiB / 64 MiB |
| One emitted preparation package | 16 MiB |
| Required concepts per pack | 24 |
| Within-pack term pairs | 276 |
| JSON nesting / schema-reference depth | 64 / 8 |
| Resolved reference records per preparation batch | 256 |
| Comparison obligations per assurance batch | 512 |
| Work-history entries per exported session batch | 256 |
| Local validation/preparation subprocess | 60 seconds |
| Inline Agent context | Existing 256 KiB budget and 900-second default TTL |
| Ontology preview | Existing depth 2, at most 60 nodes / 100 edges |

Byte/depth/count limits are enforced before expensive parsing and pair evaluation. Larger declared sets use explicit batches with a frozen whole-set identity, completed member/range accounting and unresolved continuation. Cross-batch semantic dependencies and comparisons remain obligations; batching cannot silently imply global coverage. Timeout/over-limit results are explicit incomplete outcomes. Increasing a ceiling requires an amendment and new resource evidence. Existing legacy runtime behavior is preserved; these limits govern the new preparation path.

## C12 — Three deliverables

1. **M1 — Read-only preparation preview:** corrected draft meanings, v2 preparation checks, strict candidate source decoding, supported pack adaptation, all disposition routes, complete candidate output or blockers, field lineage and no-overwrite package publication. Freeze this preview without a signing key, provisioned store, repository writer or changed admission epoch.
2. **M2 — Guarded exact review:** applicable owner evidence, scopes, policy/challenge mechanism, exact independent targets, postimages and non-mutating review. Candidate local/epoch adapters are prepared and checked in isolated fixtures. Rejected and partial outcomes are visible.
3. **M3 — Authorized application and visibility:** full candidate manifests, Product/test/docs closure, independent exact owner decisions, attended repository application, coherent epoch selection, recovery and refreshed state/views.

The first writer is limited to the selected Definition integration and its declared profile/representation/state consequences. General authentication services, arbitrary multi-product admission platforms, full historical migration and new global ontology models are outside this plan. The milestones permit concrete review before the full application path exists; the final exact admission package can still use one human checkpoint with independent member Decisions.
