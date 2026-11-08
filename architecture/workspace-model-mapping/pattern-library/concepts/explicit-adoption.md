# Explicit adoption with preserved history

Meaning: a changed release and an instance's adoption are separately attributable transitions.

Evidence: [v2 source-profile repair](../../../../implementation/lab-runtime/v2/SOURCE-PROFILE-REPAIR.md) retains old baselines; [installation operations](../../../../product/lab/release-candidates/v1/packaging/R02/OPERATIONS.md) preserve retained-reader rollback and explicit profile changes.

Use: pin contracts/components/profiles/environment, define carry/adapt/exclude dispositions, preserve before/after identity and history, and record actual migration/adoption outcomes.

Failure to avoid: silently refreshing shared pins or equating package installation with changed semantic authority. An uncertain effect must be reconciled before retry.
