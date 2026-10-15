# T03 real remaining-lease margin proposal

The selected production successor should check a measured reserve inside `Vault.claim`, after the original journal lock and prior/result lookup, immediately before `self.object(raw)`. This is the first fresh operation-material write, followed by allocation and claim publication. The first diagnostic full-learning run remains measurement: this package changes no current runtime and supplies no qualified empirical policy.

This package contains a concrete pure decision helper, a closed policy schema, exact unchanged target preimages and an integration proposal. It does not contain a runnable production adapter or selected API postimages. That adapter must be reviewed against the independently frozen current family and actual measurements; no runtime input selection or threshold is inferred here. The unqualified template deliberately fails the helper and schema.

## Current boundaries inspected

`Service._call` retains authentication, current schema/code/profile, Actor, request byte/action budgets and the strictest outer/budget/context deadline. It checks the existing key before application/assessment preflight. Exact recorded outcomes return without another creation, and pending keys require operation inspection. Application/assessment selection runs its original full preflight before the durable claim.

`Vault.claim(call, raw, context, *, deadline=None)` acquires `self.lock()`, whose original entry/exit guards reread the private grant/workspace. It checks prior/result again and checks the real deadline immediately before `self.object(raw)`. This deadline check detects expiry; it does not reserve time for the remaining learning sequence. A margin check outside this lock can become stale while the lock is acquired. Its insertion must leave the method signature, prior/result path, namespace/fingerprint, action limit, original real deadline check, writes and return tuple unchanged.

Application and assessment `prepare` methods use `guarded.calculation`. The sealed read scope ends before the original full schema/vault checks and buffered evidence commit. `resource.guard`, current-source checks, final reply checks and all existing preclaim/posteffect checks remain necessary. A forecast never replaces them. Delays after a claim can still make the operation indeterminate; retain the original journal and follow the existing T04 inspection/recovery rules. The forecast does not authorize redispatch.

`SessionAttachment.guard` independently verifies the actual distinct parent/operator Services, original channels, shared view/Schemas, full source, current Principal/policies/workspaces and the original live parent resource. The actual resource lives in `attachment.sessions.live`; its `expires` is fixed and its original `guard` must run. Its Context delivery, original Source period, parent grant and operator grant are separate lifetime bounds. Assessment's operator grant has no Session control, so the parent attachment must supply the actual Session; an operator-policy deadline alone cannot prove remaining Session life.

The complete positive driver revision 3 retains application, exact retry, operation inspection, recorded assessment, attached close preserving the parent, parent inspection and parent close. Separate security cohorts remain mandatory. The coarse complete-helper phase includes operator provisioning/preparation outside API calls; its costs must be covered rather than silently omitted.

## Production integration contract

1. Construct a distinct successor with a separately selected `observed_margin` adapter/helper and schema; update full source/profile/schema execution eligibility and the Service code-file guard. Preserve every original row. Exact preimages are recorded in `preimage-selection.json`.
2. Add a private owner link from the new Service to its new Vault. The proposed additive constructor statement is `self.vault.observed_margin_host = self`; the existing constructor signature is unchanged. A new independently selected startup composition supplies a frozen timing selection object. API request fields, Actor claims and idempotency keys supply no timing policy and cannot switch modes.
3. Select `diagnostic-measurement` versus `enforce-observed-margin` in that protected startup input. Diagnostic mode is explicitly reported as measurement with no margin qualification. It must preserve the original learning/security path and periods. The currently authored driver and original runtime can collect the first measurements without this gate; do not block that run for unknown calibration values.
4. In enforce mode, absence, malformed/unqualified evidence, unknown load, missing bound, identity mismatch or expired calibration refuses before fresh operation-material/allocation/claim writes. No permissive numeric default or expiry extension exists. Only fresh `lesson.apply` and `lesson.assess` claims use this scoped first implementation; other operations and original historical retries retain their original semantics. This is not a general claim of guarding every Lab effect.
5. Inside the existing claim lock, after the original prior/action/deadline checks, import the independently selected adapter and call `before_claim(self, call, context, deadline)`. The adapter resolves the actual Service from the private owner link, verifies its actual selected type/Vault/channel, checks the actual attachment/resource and retains every original guard. It must not reacquire `vault.lock`: a second flock descriptor can deadlock against the held lock.
6. The adapter freshly captures the independently pinned policy and current load observation from the expressly owned external control root, with no-follow retained ancestor descriptors, exact root inode/UID/mode, regular bounded mode-0600 leaf, SHA and before/after attachment checks. No old/private body is copied or logged. Capture software requires its own independent code pin and true selected origin. Do not substitute a check-then-read pathname import.
7. Freshly verify each empirical evidence binding, current full source/profile and installed dependency selection. Read the exact actual cut and branch; obtain direct original Source-period, Context-delivery, Session, parent grant and operator grant deadlines. The strictest request/budget/verified context deadline remains the `deadline` passed by Service. Reject missing actual identities or dates rather than filling them from historical expectations.
8. Perform the final original liveness checks and obtain real UTC **after** policy/evidence/source/load checks. Feed the pure helper these direct observations. No clock replacement, permission renewal, callback substitution, Session reconstruction or persistent trust cache is permitted. All bytes/observations are local to this invocation.
9. Translate unavailable calibration to the original declared `closure-missing`, mismatch to `integrity-failed`, and an insufficient reserve to `budget-exceeded`, with a constant sanitized message. Verify these codes against the selected operation contracts before integrating. Since the call has not claimed, `effect_started` remains false and T04 must classify the refusal accordingly. Recording a preclaim margin event must not introduce a journal/object write before this decision.

Exact proposed insertion, retaining the original signature and deadline check:

```python
# Vault.claim, inside its existing lock, after original prior/action checks
if deadline is not None:
    from .auth import now
    if now() >= deadline:
        raise DeadlineBeforeClaim('Effect deadline expired during guarded journal-lock acquisition')
if call['operation'] in ('lesson.apply', 'lesson.assess'):
    from .observed_margin import before_claim
    before_claim(self, call, context, deadline)
original = self.object(raw)
```

The implementation must preserve original guards/effect semantics in all enclosing Service, attachment, application, assessment, calculation, buffer and reply callbacks. No changes to those original preparation method signatures are proposed. No predictive PASS is inferred from the preserved callback bytes.

## Reserve and evidence

Use integer microseconds, rounding measured upper estimates upward during policy authoring. The pure helper computes:

`remaining = min(effective_call, Session, Context_delivery, Source_period, parent_reader, operator_reader) - final_real_UTC`

`required = sum(remaining_phase_upper_bounds) + reviewed_uncertainty_reserve + measured_gate_overhead_upper_bound`

Proceed only when `remaining > required`. Equality refuses. The returned positive difference is the observed remaining margin; the helper never writes a new deadline. An empirical maximum is an observation, not a guarantee under arbitrary future load. The external uncertainty bound and declared load acceptance must be reviewed, not inferred from a single sample or from a percentile without a stated method.

At application preclaim, reserve application completion, exact retry, operation inspection, assessment operator preparation and assessment, attached close, parent inspection/close and cleanup. At assessment preclaim, reserve assessment completion and the later close/cleanup tail. Do not reserve only the current native call and then call the full learning sequence qualified. A whole-call measured upper bound is conservative when used for the remaining part of a call whose preflight/lock wait has already elapsed. It need not subtract unmeasured prefix costs. Overlapping/coarse measured phases must be explicitly bounded conservatively or measured more precisely; do not add nested inclusive profiler times as latency.

The policy binds full current source/profile, complete execution code/workload closure, dependency selection, declared **actual** load, instrumentation identity and actual source cut. A profiled refusal, unfinished learning run, native-only measurement, static benchmark, old source family or security-negative cost mixed into the positive lease cannot populate qualified positive bounds. The current full positive measurements do not yet exist. Every numerical bound and validity date in the template is therefore null.

The installed optional jsonschema date-time checker did not reject an invalid date string in a pure fixture. The new schema therefore also requires a UTC timestamp shape; the helper separately parses actual calendar/timezone semantics and refuses impossible dates. Preserved development counterevidence is not a claim about whole production contracts.

The schema's sample count minimum of one is structural; it is not a statistical adequacy rule. Accepting the measurement set and uncertainty bound is an independent review obligation. Gate overhead includes fresh policy/evidence/schema/load checks and any extra full original guards. Unknown overhead refuses. Parent process CPU alone excludes native child CPU; use complete monotonic elapsed phase times, which include child waits and scheduling, with their direct real-UTC lifetime observations.

## Avoiding a provenance cycle

A policy cannot embed the digest of a full source/profile that itself embeds that policy's bytes. Keep independently pinned timing policy/current-load data as protected external control inputs, analogous to an independently selected private grant, and freshly capture them at the effect boundary. Their guards are additional obligations; removing any original source/profile row is prohibited.

Freeze the software/helper/schema/composition before the matched diagnostic cohort. The startup mode/policy data may change only as explicit protected inputs, never as a production callback replacement. If adding measurement outputs/control rows changes a subsequently selected manifest, or code/profile/cut/dependencies/instrumentation/load change, the old measurements do not automatically apply. Require exact identity correspondence or a separately reviewed, measured conservative transfer bound that includes the changed full-guard workload and new gate overhead. This initial kernel supports exact identity equality only; it implements no transfer exception. First driver measurements remain useful diagnostic evidence even if further matched calibration is required.

## Required qualification

- Independent static review of adapter/private selection/capture/schema, unchanged signatures and exact preimage/delta pins before source selection.
- Pure closed-schema/null/type/identity/deadline arithmetic and missing-bound controls; synthetic numbers are never calibration.
- Actual unknown-policy, stale load, source/profile/code/cut/dependency/instrumentation tamper, missing evidence, exact-equality reserve and insufficient-reserve refusals before operation material/allocation/claim. Inspect the original current journal to prove no fresh claim; no original callback monkeypatch.
- Actual delayed lock acquisition proves the check uses the remaining original lease inside the lock. Actual retained original expiry/revocation/corruption/effect-in-read-scope refusals remain mandatory.
- Actual recorded retry and pending-key inspection retain their original behavior. Loss of resource or remaining deadline after a fresh claim remains indeterminate/recovery-required with retained original evidence.
- Real unprofiled complete positive lifetime under the declared load, with direct cut/branch/Context and all original deadlines, measured reserve and original disposal. Separate original security cohorts and whole all34 qualification remain required.

This is preparation for the remaining criterion, not T03/T35/API/plan completion or governing authority. No current shared file, runtime constructor, native call, Service/Session, lock or lease was changed or started.
