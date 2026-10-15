# Prepare local Work in an isolated branch

Understand a local proposal, approval, commit and replay without claiming repository admission.

Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.

## Standing of this journey

The admitted v1 implementation supports authorized local transactions, but this handbook has not replayed a fresh effectful Work journey. Treat this page as the parser-backed preparation and acceptance checklist for that future witness. The [read-only walkthrough](first-inspection.md) is the currently observed tutorial.

Use a new owned branch and a separately selected operator key outside the repository. Obtain explicit authority for that local scope before authorization/application. A local owner string and public key define that branch's approval boundary; they do not prove an organizational role or authorize a repository Decision.

## Select the inputs before creating anything

| Input | Required decision |
| --- | --- |
| Runtime/profile | Choose exact v1/D74 or a separately reviewed v2/D75 candidate; never rebase an existing store |
| Store path and ID | New exclusive path, selected local scope and current HEAD |
| Operator identity and key | Actual independently provisioned local approver, private bytes outside Git |
| Work proposal | Exact inputs, planned outputs, carrier, version, scope and expected source snapshot |
| Approval | Complete proposal/Decision cores/time/owner/store/policy/challenge/HEAD binding |

The [example subcommand](../../../../../../../runtime-narrative-preparation-0001/evidence/implementation/lab-runtime/v1/lab_runtime/cli.py) produces planned candidate Work, not a completed task. The [contract](../../../../../../../runtime-narrative-preparation-0001/evidence/implementation/lab-runtime/v1/CONTRACT.md) defines the fields that review must assess.

## Follow the original transaction boundary

The parser route is keygen, init, example, review, authorize, apply, then verify/status. Global --store selects the owned branch for every command. keygen rejects private paths inside the repository; init refuses an existing store. review calculates proposed consequences without approving them; authorize signs exact bytes; apply verifies that signature and current HEAD before commit.

One supported transaction can carry independent targets and Decision cores. It records local histories and consequences together. Its receipt and local Project State identify their store scope. A later repository adoption or activated service needs a separate exact governing decision.

Do not use placeholders as working credentials or treat the command names as permission. Have the exact path/identity/body selected and reviewed before execution. The complete command grammar remains in [the preserved v1 operator guide](../../../../../../../runtime-narrative-preparation-0001/evidence/implementation/lab-runtime/v1/README.md).

````mermaid
flowchart LR
  P[Exact candidate proposal] --> R[Review consequences]
  R --> A[Local owner's exact signed approval]
  A --> T[Validated staged transaction]
  T --> H[Atomic HEAD commit]
  H --> C[Cold replay and receipt]
  H -. separate .-> D[Derived graph or files]
  R -. different authority .-> O[Repository owner decision]
````

An exact local proposal is reviewed, independently authorized, staged and committed at HEAD. Cold replay checks the committed chain. Derived outputs and repository admission have separate boundaries.

Explanatory component/sequence map, not a declaration of new ontology relation kinds or qualified runtime execution.

## Observe completion and residue

For a future witness, retain the actual proposal/approval hashes, expected and resulting HEAD, independent Decision cores, terminal, cold replay and current-source checks. Record whether Work remains planned, was performed, or has a separately assessed outcome. A successful local admission receipt is not Work satisfaction.

If interrupted, inspect the owned store before deleting anything. Committed history survives; recognized uncommitted staging may be reconciled under expected HEAD. Unknown residue is retained. Do not recycle a proposal ID with different material, or overwrite earlier evidence after a failure.

## Review and cleanup criteria

The tutorial is eligible for a successful walkthrough only after a fresh isolated execution, exact authority selection, receipt, replay/recovery and cleanup have been observed. Dispose only its own known disposable roots/keys under the accepted retention policy; preserve committed public evidence and any uncertainty. Link [recovery](../how-to/recover-and-retry.md) and [the canonical Work definition](../../../../../../../../../../../../lab/reference/records/def-cal-definition-work.md) when reviewing the result.

## Selected public evidence

- [docs/decisions/0075-lab-operational-runtime-v1-admission/DECISION.md](../../../../../../../runtime-narrative-preparation-0001/evidence/docs/decisions/0075-lab-operational-runtime-v1-admission/DECISION.md). SHA-256 ef48fbf62925cd86d2e60c6c2e40a3b4bacbeeafe5498b2f53a3573bb8b9a4c0; 3432 bytes. Public technical snapshot; no authority transfer.

- [implementation/lab-runtime/v1/lab_runtime/cli.py](../../../../../../../runtime-narrative-preparation-0001/evidence/implementation/lab-runtime/v1/lab_runtime/cli.py). SHA-256 43799f3efb2c53a4c9b39c99a681ecc7134182094aa06c14d66a378b594ba056; 11813 bytes. Public technical snapshot; no authority transfer.

- [implementation/lab-runtime/v1/CONTRACT.md](../../../../../../../runtime-narrative-preparation-0001/evidence/implementation/lab-runtime/v1/CONTRACT.md). SHA-256 583b063a83e026861d6c060473a1a2509289cae059ddfd11f4af666599dd7980; 5956 bytes. Public technical snapshot; no authority transfer.

- [implementation/lab-runtime/v1/README.md](../../../../../../../runtime-narrative-preparation-0001/evidence/implementation/lab-runtime/v1/README.md). SHA-256 78623efb7024181573099ca08e979534156b80a3768ca2a800639feb8cb43891; 9506 bytes. Public technical snapshot; no authority transfer.

- [implementation/lab-runtime/v1/lab_runtime/store.py](../../../../../../../runtime-narrative-preparation-0001/evidence/implementation/lab-runtime/v1/lab_runtime/store.py). SHA-256 ed2eaafd299f6ec942016e078c029a847b54269c7eb91bb970275ac0bdaf1910; 18220 bytes. Public technical snapshot; no authority transfer.
