# Definitions and records workflow repair

The repair follows the nine findings in ../definitions-records-audit-2026-11-12. All nine findings are fixed and the final workflow checks pass. See WORKFLOW-VERIFICATION.json for exact receipts, counts and verification boundaries.

The authority chain is recorded in DEFINITIONS.json, CONTRACTS.json, ONTOLOGY.json, BRIDGE.json, SYSTEM.json, DESIGN-CHAIN.json and REFINEMENT-CHAIN.json. Define prepared, inspected and replayed both contract packages using 14 exact admitted definitions. No global definition identity or admitted meaning was added or changed.

| Finding | Implemented repair | Evidence |
| --- | --- | --- |
| D-01 | Await complete CLI stdout before exit. | Exact piped source-byte regression |
| D-02 | Distinguish frozen design selections from current admitted authority. | Define docs/CURRENT-AUTHORITY.json and current reader |
| L-01 | Authenticate publication, selector, complete snapshot and history before catalog observation. | PUBLICATION-VERIFICATION.json; corrupted receipt regression |
| L-02 | Require layout v2 through trusted Lab policy for new publications. | REGRESSION-VERIFICATION.json |
| L-03 | Bind all four directory assets and verify the original Define package; check evidence on placement retry. | DIRECTORY-PACKAGE-VERIFICATION.json: 188 directories |
| L-04 | Inspect and reconcile public pointers, canonical assets, generated indexes/catalogs and record custody views; recover interrupted reconciliation. | DIRECTORY-PUBLICATION-RECEIPT.json; isolated interruption/corruption regressions |
| L-05 | Maintained handoff, full target commitment, owner-reviewed evolution, lifecycle orchestration and Define-authored acknowledgement; checkpoints cannot grant completion. | HANDOFF-CONSUMER-VERIFICATION.json; LIFECYCLE-VERIFICATION.json |
| L-06 | Derive the qualified dependency graph from actual definitions, native subjects, carriers, schemas, generators, directory assets and readers; report external coverage separately. | operational/consumer-universe.json |
| L-07 | Keep semantic Project distinct from technical host and native authority scope; enforce full record-owner review and per-kind custody; bind three absent Product identities. | workspace-records and NATIVE-HOST-CONTRACT.json |

## Ownership boundary

Define owns candidate meaning preparation, exact package inspection/materialization/reconstruction, scoped readiness, handoff reports and reported acknowledgements. Its behavior remains authored in Define AlchLang.

The shared Lab owns construction, owner-authority verification, native permission/application, authenticated publication, workspace routing, canonical views, custody, dependency qualification and recovery. Shared behavior is maintained once under implementation/lab-workflows/records-workflow and the existing shared runtime. No runtime is installed or copied into a Product workspace.

## Preserved authority and operating records

The 188 current Definition/v2 identities and all 377 admitted versions remain byte-identical to the verified pre-repair registry. Original owner decisions, receipts and source cuts remain immutable.

The existing Craft, Ontology, Trusted Dataset Materialization and Lab Product references are reused. Define, People and Teams and Lab Website now have their genuinely absent Product operating identities and linked draft theses. These six records have local-admitted-current standing in the selected native store. The theses remain draft and untested. This is not an automatic repository-global semantic admission or market-validation claim.

The native host contract explicitly retains each owning workspace and its own workspace scope. The existing native authority domain remains separate; no semantic Project is fabricated for Product-only work.

## Verification boundaries

The dependency universe is an explicit inventory, not a whole-repository completeness claim. External consumer declarations are reported separately from unresolved dependencies inside the selected scope.

Source/capability and concurrent compiler-cache refusals are retained in PRE-PUBLICATION-REFUSALS.json. The successful publication receipt supersedes the refused attempt without modifying its bytes. Runtime code remains singular; recovery archives contain data and immutable verification evidence, not additional runtime installations or private keys.

Final verification: 62 generated AlchLang guard checks, 84 native checks, 29 Define CLI workflow checks, 22 causal regressions and 19 historical hardening checks passed. The actual nine-stage lifecycle, original-operation replay and Define acknowledgement passed. Runtime readiness is ready; native sources are current; all 789 canonical views reconcile.
