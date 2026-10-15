# Read-only CLI and coverage review

I04.1 is a candidate implementation unit. Its prerequisite I03 and E04 receipts and exact input/output bytes were rechecked before mutation, together with 201 captured source files and 1,134 previously sealed candidate files. The implementation adds commands and a coverage view; it does not complete the formalization episode or grant any semantic authority.

## Interface and selection

The CLI is `craft/formalization/candidates/definition-assurance-v1/cli.py`. Supply `--repo` and optionally `--format json` or `--format human` before the command. All commands emit their result to stdout. The CLI has no publication, admission, registry-edit or output-overwrite command. It disables Python bytecode writing before importing its implementation modules. Tests may construct and publish isolated temporary fixtures to exercise the existing verifier; those fixture writes are outside the live repository and are cleaned up.

`capture` reconstructs and rechecks the current source snapshot, including registry, selected admission decisions, current definitions and historical versions. The returned snapshot is content, not a new admission. No existing candidate snapshot is overwritten. The end-to-end test compares the captured result with the selected current snapshot and forbids invocation of the publisher.

`check --input PATH --input-sha SHA --kind KIND` reads an exact selected input and checks its fixed local contract. For an interpretation it also compiles and verifies static IR. An optional `--snapshot PATH --snapshot-sha SHA` binds its source to the selected current snapshot and rechecks live bytes. Without a selected snapshot, source currentness is explicitly unselected. Static typing cannot establish truth, required populations, source fidelity or completeness of the translation.

`verify --bundle PATH --selection PATH --selection-sha SHA` invokes the existing independent bundle verifier against the selected live source root. This regenerates the selected requirement denominator, checks exact referenced bytes and supplied models, and retains pending gates. A successful command means verified candidate accounting. It remains false for mechanized proof and semantic readiness. A test exercises an actual finite witness, publication of a temporary bundle and independent verification through the CLI, without mocking the verifier.

`diff --selection PATH --selection-sha SHA` regenerates revision requirements using the existing revision engine. A successfully generated diff is not an accepted revision, inherited proof or permission to mutate the source. The real unchanged-selection example retains pending fidelity and false evidence verification. User-selected reference changes, missing files, path traversal and symlinks produce a nonzero unresolved result.

`report --snapshot PATH --snapshot-sha SHA --delivery PATH --delivery-sha SHA` selects both the source denominator and the exact prior delivery inventory. It checks every selected manifest byte, current source references, interpretation contracts, correspondence and regenerated typed IR, then rechecks selected inputs and source currentness at the closing boundary. It uses the installed, hash-matched correspondence checker; the selected repository cannot substitute an arbitrary checker implementation. The command does not execute a solver or freshly evaluate the recorded projection models.

JSON provides the full structured record. Human output includes every current identity, its draft status, encoded and deferred counts, required and unresolved populations, scope limits and next candidate unit. The human views of the other commands are formatted JSON, preserving the complete result and diagnostics. A zero exit code denotes successful candidate capture, accounting, typing, revision generation or coverage inspection, according to the command. It never denotes completion of the full formalization episode.

## Coverage and claim boundaries

Coverage uses the 183 current definition identities and 189 admitted source versions. It includes a row for every current identity. Eight identities have source-accounted typed partial definition drafts; 175 have no per-definition draft in the selected delivery. All eight retain pending whole translation and owner fidelity. There are zero owner-accepted whole translations and zero whole-definition proofs.

The eight foundation drafts account for 180 source units and 287 clauses: 79 encoded, 69 explanatory and 139 deferred. They select 68 required and 97 unresolved population policies, with no selected assumptions. Required nonempty carriers and predicate existence remain distinct. Complete character accounting does not imply a complete logical translation. Declared ownership, a valid schema, a preserved digest and a finite witness remain different evidence aspects.

The earlier I03 projection has seven separate identities. Its three selected revision cases retain their recorded statuses, query counts, premise accounts and exact result references. The counterfactual case preserves `relation:TRACE-Position:left-difference` as a reported finite-scope failure with unverified exhaustion. A bounded search result cannot become an unbounded nonexistence theorem. The report has an explicit failure ledger and checks it against the exact result rows, so a rehashed summary that omits this failure is rejected.

The projection receives zero whole-definition credit. Fifteen distinct identities have either a partial foundation draft or a partial projection. This union is reported for inspection and expressly excluded from whole-translation coverage. The earlier projection's 176 missing projection identities are its own denominator; they cannot replace the 175 missing per-definition foundation drafts or suggest that shared source meanings have been resolved.

The foundation review remains PARTIAL with an unready joint exit. Its 26 missing counterpart packets and two unclassified semantic components are exposed. No reviewed carrier alignment or fixed-point meaning is inferred from the nominal finite model. Remaining premise review includes deferred normative, temporal and operational commitments; the CLI supplies no assumptions to force a desirable conclusion. The next candidate unit is I05.1, subject to its I04 and A10 prerequisites and the actual DAG/receipts. Reporting a next unit does not discharge its prerequisites.

## Failure recovery and verification

One initial report selection mistakenly included archived `t.json` attempt files as top-level current drafts. That failed selection and its implementation were preserved, and selection was restricted to the exact identity/t.json level. All archived files remain in the preserved manifest inventory, without becoming current translations.

The initial verification test used a protected fixture publication path and called a nonexistent fixture cleanup method. Its failing test code and logs are preserved. The corrected test uses the existing candidate publication prefix inside its temporary repository and unittest fixture cleanup. Neither correction changes admitted source or previously sealed evidence.

Nine end-to-end tests cover full-denominator reporting, readable coverage, capture without publication, typed interpretation checks, actual revision generation, actual independent bundle verification, stale/missing/traversal/symlink inputs, altered candidate or omitted inventory entries, forged foundational readiness and omission of the recorded projection failure. Selected source and predecessor bytes are verified before and after relevant controls. The delivery additionally binds actual CLI outputs, implementation, tests, review and receipts by digest.

I04.1 can complete its implementation criteria while every foundation translation remains partial. Full-source fidelity, semantic dependency completeness, reviewed populations, cross-definition meaning alignment, proof obligations, all remaining identities, clean replay and the final complete episode review remain outstanding.
