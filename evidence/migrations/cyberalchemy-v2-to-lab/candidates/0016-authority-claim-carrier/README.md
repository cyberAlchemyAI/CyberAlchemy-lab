# Authority Claim carrier

Named owner + exact object + operation + scope -> exact model and supporting basis -> required owner gate.

An Authority Claim is an explicit, challengeable assertion about who may perform an operation over an object in a named scope. This candidate preserves the Authority Claim meaning separately from Authority and Responsibility, and checks both normalized D34 and D69 source selectors.

The record names its owner, owner route, authority surface, governed object, operation, effect, basis and challenge route. Content hashes bind the exact Definition object, candidate Authority Model and every supporting file. The Definition's versioned identity must agree with the object reference. Duplicate basis paths and identity collapse are rejected.

The prior Authority Model checker evaluates the requested operation and effect. A matching route must agree with the claim's owner route. Unknown operations, blocked effects and scope mismatches retain their blocking or not-applicable outcomes. The Authority Model's frozen materials are checked before its code is used.

The example asserts a request to review a candidate Definition under the illustrative model. Its evidence establishes only that the model's local checks passed. It is not a real owner grant or an adoption of the illustrative scope.

This bounded profile supports Definition objects and the prior closed authority-routing model only. Claim posture and owner identity are supplied assertions, not authenticated facts. The claimed scope is checked against the model; this does not establish that it is authorized over the object's own semantic scope. Evidence and decision basis labels are retained without evaluating sufficiency or decision authority. Team membership, delegation, real gate verdicts and non-Definition governed objects remain unsupported.

A successful result establishes exact bindings and a modeled route requiring a gate. It never establishes authenticated authority, sufficient basis, a gate verdict or permission to act. The challenge route remains a named continuation route, not an executed action.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0016-authority-claim-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0016-authority-claim-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0016-authority-claim-carrier/artifact-types/authority-claim/v1/fixtures/valid/authority-claim-record.json
```

CLI status 0 means an exact-bound claim reaches a required owner gate, 1 means blocked or not applicable, and 2 means invalid input. Status 0 grants no authority.

Validation passes 14 behavioral tests and 8 invalid contract fixtures. It verifies 27 Definition dependencies and their 25 source sections, both normalized D34/D69 selectors, eight inherited source-lineage residues and the existing narrow D53 binding. Generated files reproduce and the predecessor snapshot remains unchanged.

The 195-target ledger now has 13 admitted targets, 90 constructed candidates and 92 remaining scaffolds. Next: `type.responsibility`.

The user's `next` authorizes construction and testing. A later acceptance of a claim would concern a particular owner's authority over an exact object and operation in a named scope, on a sufficient basis and through the responsible gate. This candidate does not accept that claim.
