# C11 — Isolated provisioning and operator instructions

Status: candidate criteria complete. All 13 cases passed in 19.490 seconds. No source drift.

Exact evidence: `implementation/lab-provisioning/candidates/v1/receipts/C11/0001.json`. Source manifest and public observations: `implementation/lab-provisioning/candidates/v1/packages/0001/`.

The rehearsal initialized an owned disposable Project branch with the independently pinned frozen v2 engine and exact D75 source profile. Public configuration records the candidate operator, store identity, explicit local scope, public key, allowed category and effect. Configuration, baseline and committed HEAD have independent replay pins.

A separately signed S01 catalog genesis contains 144 contracts and six unadmitted candidate subjects. Its response is explicitly fixture-only with no human outcome. Catalog genesis does not extend the Project engine's dispatcher or admit a Method.

The full suite observed unchanged committed export bytes, fresh-process Project/catalog replay, existing-store rejection, incompatible-profile rejection, invalid-scope rejection, independent pin rejection, verified genesis recovery, private-key exclusion from every store/export, mode 0600 custody, and cleanup of the owned root and key. Repository `.local/` ignore behavior was checked. One initial category-selection failure is retained under the candidate attempts directory.

The frozen Project engine accepts carrier categories, not semantic Work kinds. The configuration selects `artifact-instance` and `admit`; bounded Work selection remains a caller obligation. A general Work-only trusted authority adapter is not established. Actual operator/location selection, final admitted engine scope and permanent provisioning remain S02/R08/A02 obligations.

Permanent private-custody, export, rollback and recovery instructions are in `implementation/lab-provisioning/candidates/v1/OPERATOR.md`. No permanent store, service, capability adoption, canonical admission or external effect occurred. The disposable branch was closed after verification; C12 must construct and identify its own candidate execution branch.

Next: C12 genuine bounded candidate development Work with actual source-derived evidence, distinct local/repository effects and no persisted Session memory.
