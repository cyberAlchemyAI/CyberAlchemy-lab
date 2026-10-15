# Classification failures and proposed repairs

The completed API50 classification suite ran 16 cases: 14 passed and two failed.
Its failed terminal, original assertions and source remain preserved. This
analysis does not qualify either repair or close R03.

## Independent axis target count

`test_09_independent_axis_is_preserved` expects five proposal targets. The actual
result contains nine. The current fixture explicitly adds a typed relation for
each proposed Classification Value and Classification Assignment: `member-of`
for a Value and `governed-by` for an Assignment. The independent-axis fixture
starts with five domain targets and adds four relation targets. Its closed
transaction therefore contains nine targets. The single-axis fixture starts with
three domain targets and adds two relation targets, retaining the five-target
expectation in `test_01_exact_original_ChangeProposal_result`.

Proposed qualification change: keep the original test file unchanged and prepare
a separately bound successor for only the independent-axis count assertion,
five to nine. Add exact comparison with the independently supplied proposal and
assert the five domain/four relation split and original relation signatures. Run
the complete classification suite. This source analysis alone does not prove a
runtime pass or authorize dropping any relation target.

## Failed validation evidence for an incomplete core

`test_12_wrong_original_stable_core_is_not_classified` expects the failed native
validation report to remain available. It is absent. The validator produces a
failed report when the independently supplied stable core differs, before it has
validated every target core. `classification-preparation-v7` treats that incomplete
core result as an uncertain operation and raises an ordinary error inside its
staged calculation. Scope cleanup discards its evidence buffer.

The operation must remain pending: the retained
`test_16_uncertain_core_failure_stays_pending_without_redispatch` requires an
indeterminate first response, recovery-required retry, no classifier result and
no command result journal. Retaining the failed validation report need not finish
that command or assert that a classification passed.

Proposed implementation: add an explicit exception for this native validation
refusal. Catch it only inside the composition wrapper, let full original source
and policy exit checks run, commit the staged native verification evidence after
those checks, then rethrow outside the calculation. Preserve the pending command,
its retry behavior and all original assertions. Unexpected errors or failed source
exit checks still discard the buffer. No classification result, decision, authority
grant or admission is generated from the failed report.

Qualify both original bad-core cases plus the full separately bound classification
suite against the exact implementation successor. Candidate evidence writes remain
inside the existing construction authorization.
