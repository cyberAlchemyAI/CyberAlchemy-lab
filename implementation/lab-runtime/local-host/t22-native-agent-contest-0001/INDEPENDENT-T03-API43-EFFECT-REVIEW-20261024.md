# Independent API43 derived-effect review

Read-only review of `api-integration-v43-t03-derived-effect-0001`, application
helper v7 and independent assessment helper v4 on 24 October 2026. This review
does not claim an independently executed positive T03 lifecycle or fault test.

No demonstrated blocking authorization/dataflow defect was found in the reviewed
branch. Full native source proof remains required at entry. The derived guard
then rechecks the seven physical Source/Reader/Mapper/Context manifests/packages,
their closed inputs, baseline materials and private archive, with the Context
package independently pinned by the selected API manifest. It also rechecks
private grants, original source period and actual UTC at derived writes. The
current-legacy assessment branch in `auth.policy_guard` checks its source period
even when invoked by `termination_guard(check_source=False)`.

Application requires the same actual parent resource, active Session row, parent
grant and source cut. Independent metadata assessment selects its own current
Source and grant and exact completed application journal. It does not borrow the
parent's Session, memory, registry or lease. This is metadata assessment, with
diagnostic margin measurement and no empirical margin qualification claim.

`guarded_candidate.calculation` invokes the effect guard before/after every
published object. `Vault.finish` holds the journal lock across the guarded
completion marker and removes only its exact newly written marker, with directory
fsync, if the post-write guard fails. Claim and partial evidence remain available
for indeterminate inspection. The original completion path remains unchanged for
other policy families.

Two assumptions were returned to the implementer for test/claim clarification:

1. The guard retains Session/grant/source expiry, but not the effective call
   deadline. The original Service can record an outcome and return indeterminate
   when that request deadline expires after claim. Claims must distinguish this
   existing operation semantics from strict no-write-after-request-deadline
   semantics; permission expiry is a separate boundary.
2. Callback code checks occur before claim. The effect guard's disk verification
   does not by itself demonstrate continuous protection against a hostile
   in-process mutation of `DerivedEffectGuard` methods after claim. Such a claim
   needs an effect-time code identity guard and causal attack test, or an explicit
   managed-callback assumption. No after-claim mutation attack was executed here.

Actual live application, assessment, independent completed-journal readback,
fault injection and a third fresh Session consuming the assessed result remain
separate required observations. Selection or producer staging alone cannot prove
those outcomes or causal learning improvement.
