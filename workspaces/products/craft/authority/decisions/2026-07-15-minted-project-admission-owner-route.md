# Decision Gate — Minted Project Admission Owner Route

Status: `DEFERRED`; Option 3 selected by operator  
Target: `SWU-MNP-007`

## Blocking Question

How should the manual admission task obtain its required owner roster and
private admission-evidence home without inferring approval from conformance?

## Evidence

- SWU-MNP-006 conformance passes but explicitly records
  `release_admission: not-granted`.
- SWU-MNP-007 requires FPR-01/FPR-04 decisions, the current guard receipt, exact
  artifact digests, a later owner-selected private evidence folder, and manual
  definitions/validation/layering/FPR/independent-verification approvals.
- Only an owner-reviewed receipt may open release/rollout work; no fixture may
  move without a separately approved destination and migration task.

## Options

### 1. Resolve the live FPR authority model — Recommended

Read the current FPR-01/FPR-04 owner and guard surfaces, derive the existing
owner roster and private evidence home, and prepare an unsigned admission packet.
Benefit: follows the already-governed authority chain. Cost: packet preparation
can continue, but execution must stop again for actual owner reviews/signatures.

### 2. Supply owners and evidence home explicitly

The operator names the definitions, validation, layering, FPR, and independent
verification owners plus the private output folder. Benefit: direct and precise.
Risk: an ad hoc roster may diverge from the live FPR authority unless reconciled.

### 3. Defer SWU-MNP-007

Leave conformance complete and admission unscheduled. Benefit: no premature
governance work or implied release claim. Cost: no admission/migration packet is
prepared and the work-pack remains intentionally open at L3.

### 4. Explain / more context

Non-committal. Expand the authority chain and concrete downstream artifacts,
then re-present the same options.

## Selection

- Selected option: 3, defer SWU-MNP-007.
- Rationale: prioritize the implemented compiler/view/minter/conformance code;
  admission governance is intentionally out of the current work stream.
- Source: operator response `decide later, i want the code, not governance right now`
  on 2026-07-15.
- Remaining blocker: none for the implementation stream; owner/evidence-home
  routing remains required if admission is resumed.
