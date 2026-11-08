# Lab Operational Runtime/v1

Effective status: **owner admitted by Decision 0075**, 2026-10-07.

[Decision and scope](../../docs/decisions/0075-lab-operational-runtime-v1-admission/DECISION.md) · [Exact reviewed target](../../docs/decisions/0075-lab-operational-runtime-v1-admission/target.json) · [Application receipt](../../docs/decisions/0075-lab-operational-runtime-v1-admission/receipts/application.json) · [Operator guide](v1/README.md)

Admission is supplied by an external overlay. The original 24 reviewed files, their candidate-era notices and their validation receipt remain unchanged. Their implementation status is now admitted for the exact local inspection, authorized local transaction, replay/recovery and ephemeral context scope.

The repository's current Project State is D75; the admitted executable's source profile is D74. Read output from this version is scoped to that frozen baseline. Updating the executable profile to inspect and operate from D75 requires an explicit successor implementation/profile review. No existing local store is silently rebased.

The six protocol schemas are implementation interfaces, not newly admitted canonical semantic contracts. Admission does not provision an operator key, create a permanent store, start a service or activate an external consumer.

A [Lab Operational Runtime/v2 source-profile candidate](v2/REVIEW.md) now selects
D75 and preserves the admitted v1 package. Its source inspection and successor
regression evidence are separate from the exact evidence admitted for v1. The
candidate does not change this admission or activate a local store or service.
