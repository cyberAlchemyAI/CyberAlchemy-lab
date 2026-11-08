# Craft: selected current evidence

The selected upstream reports have now been imported. A separate [local qualification](../../../craft/work/outcomes/current-verification/lab-qualification.json) records the relocated journey and reader checks; see [implementation results](IMPLEMENTATION.md).

Reviewed on 2026-11-05 against the current upstream development registry, revision 716. Keep the latest applicable consolidated result pair. Do not import the output tree or previous attempts.

## Export selection

The separate [EVIDENCE-EXPORT.json](EVIDENCE-EXPORT.json) allowlist adds three files, 9,414,524 bytes (about 9.4 MB), under the existing Work outcomes concept:

```text
craft/work/outcomes/current-verification/
├── index.json
├── construction-proof.json
└── installed-proof.json
```

| Prepared file | Why it matters |
|---|---|
| [index.json](selected-evidence/craft/work/outcomes/current-verification/index.json) | Exact source identities, scoped claims, currentness checks, exclusions, and all 69 development-entry verification summaries. This is new selection context, not a new passing test. |
| [construction-proof.json](selected-evidence/craft/work/outcomes/current-verification/construction-proof.json) | Exact original consolidated proof, finished 2026-11-03: 57 tests passed across selected source contracts, application composition, physical custody, regressions, typecheck and installed consumers. |
| [installed-proof.json](selected-evidence/craft/work/outcomes/current-verification/installed-proof.json) | Exact original installed result: finite binding negatives, connected integrations and six application recovery cases. Its 23 tests are included in the 57; they are not 23 additional tests. |

Original result bytes are unchanged. Only their proposed destination names differ. Their original paths and hashes are in the index and allowlist. Referenced source/build metadata and package archives are not copied; this is a scoped report export, not an independent offline replay bundle.

The checked package tuple is working Core 1.3.0, AlchLang 0.7.0-candidate.0, AI profiles 0.1.0 and four original runtime packages, using Node 26.12.1. It is distinct from the frozen Core 1.3.1 / AlchLang 0.7.0-candidate.1 release. The exact seven package digests are retained.

## What was checked now

- All 1,490 recorded source inputs in the consolidated proof still match current upstream bytes.
- All 250 recorded source/test inputs in the installed proof still match.
- All 1,215 distribution source inputs still match; all seven referenced package archives match their declared digests. Archives remain external.
- The consolidated proof's installed-result, source-report and distribution references match their declared digests.
- The three selected registry claims have unchanged direct references, dependency inputs and matching claim fingerprints.

These groups overlap and must not be added to infer a count of unique source files. This review compares bytes and references; it does not rerun the original functional tests.

The three current registry claims are `craft.profile-application-system`, `craft.application.contract-workbench` and `craft.application.customer-success`. This is a bounded source/installed composition result. Other application paths exercised in the suite do not acquire broader capability-wide passing claims.

## Evidence left out

The registry has 69 development entries, with five passing summaries and 64 `not-run` summaries. The Product proposal's 37 capability records are a different catalog. Neither number is an overall product test result.

The two remaining passing registry summaries (`are.agent-harness` and `craft.credential-lifecycle`) point to the older technical-profile proof. Its full recorded source closure now has **75 changed files**. The current registry's narrow references are unchanged, but that does not requalify the entire old proof against the present source tuple. Do not export it as current validation. The index preserves this exclusion without copying the old result.

Also omitted: prior connected attempts, before-fix copies, older service/knowledge/CRM/error/policy reports, registry history, duplicated finalization reports, build archives, runtime installations, captured sessions and raw output directories. The two selected original JSON proofs embed their own command outputs; no separate log tree is copied. Current integration finalization is useful metadata, not an additional application execution result.

## Claim limits

The selected results use recorded provider/model/reviewer responses. Real providers, measured model quality, hosting, deployment, publication, TDE and EVF are deferred. This does not remove TDE or EVF functional source from the main import.

Connected store reopen and original-owner resource reacquisition were exercised. Full process-crash qualification of the connected applications was not established. The contract workbench compares declared structure with human review; it does not establish legal equivalence. Customer-success thresholds and account/activity inputs are local examples, not live account telemetry.

The prepared functional source includes explicit path/build-configuration rebindings and external shared inputs. Original upstream success does not become relocated Lab success. The new Lab tuple must be built and tested before acceptance. Neither the export nor the original reports grant approval, activation or runtime authority.

## Applying the proposal

Keep [IMPORT.json](IMPORT.json) as the unchanged functional payload allowlist and [APPLY.json](APPLY.json) as its existing-target handling. Use [EVIDENCE-EXPORT.json](EVIDENCE-EXPORT.json) only for the three additional current Work outcome files. They currently collide with no live target. The guarded local import has completed; publication and global consumer cutover have not run.

The functional ontology manifest remains a functional-input manifest. Selecting these Work outcomes does not silently turn them into ontology admission, refresh old source authority, or qualify the named-view adapter.

## Open questions

- Qualify the final relocated source/build/native/runtime tuple before claiming Lab acceptance.
- If current harness or credential proof is required, rerun the exact selected scope and replace the old result; do not import a broad stale PASS.
- Source-pin/path reconciliation and the named ontology consumer adapter remain the integration work identified in the [main plan](PLAN.md).
