# Design review and corrections

Three mapping agents supplied source evidence and then independently reviewed
the concrete design in their areas. Review notes are preserved:

- [Proof design review](evidence/proof-design-review.md).
- [Engine/interface review](evidence/engine-design-review.md).
- [Source-copy review](evidence/copy-design-review.md).

## Corrections incorporated

| Finding | Final design treatment |
| --- | --- |
| “Aliased values” could wrongly forbid two constants naming one element. | Reject accidental carrier/symbol-map collisions; explicitly permit distinct constants with the same denotation. |
| Model existence alone does not establish a positive query. | Require T, required populations and Q to hold in the same concrete model; verify the exact corresponding obligation. |
| Planner certificates use the process temporary directory. | Bind TMPDIR/TMP/TEMP to the owned job subtree and collect it; private data-dir alone is insufficient. |
| Batch plan is not an arbitrary profile/delta interface. | Bind its full-target replacement ABI, owl-rl and fixed scan/render caps; materialize G union delta for an additive request. |
| Mixed and supplied-rule certificates use different checkers. | Resolve checker kind/ABI from the selected profile and retain conditional supplied-rule verdicts. |

All copy-manifest paths, byte lengths, SHA-256 values, Git identities and modes
were independently checked against the exact clone. The source-copy review
found no blocking copy-policy issue; it retained real license/build/fixture
closure as implementation gates.

The reviewer notes describe the versions they inspected. The final corrections
above were applied by the main author and checked again. This is a source-based
design review, not execution of the new provider or validation of future code.

## Remaining implementation gates

Copied source/build receipts, actual compiler and checker runs, restricted
semantic-bridge proofs, exact per-request proof replay, the derived supervisor
ownership/contract adaptation, completed fixture/license envelopes and measured
resource behavior are still required. Existing source-meaning review and
whole-definition coverage are not closed by this design.
