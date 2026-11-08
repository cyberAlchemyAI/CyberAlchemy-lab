# LC-U02-05 Source-only timing candidate, version 0005

The sealed version 0004 disposable attempt failed at `source`: the Source
child reached the 180-second cap, returned a forced timeout after 180,227 ms,
and was reaped with its original process group absent. Reader, Mapper, and
the guard/refusal child were not reached. That receipt remains a FAIL and is
not evidence for the version 0004 guard behavior.

Version 0005 copies the version 0004 Source→Reader→Mapper read-only→build
guard/refusal controller. Its only behavior change is a **Source-only** maximum
of 240 seconds. Reader, Mapper read-only, and build guard/refusal retain their
180-second maxima. A stage-aware helper clamps every child cap to the
remaining time under the unchanged 900-second aggregate watchdog; the child
launcher and sanitized observation validator both reject a 240-second cap
for a later stage. A Source timeout, even at the new cap, remains a forced
cleanup and FAIL. The result name is newly allocated as
`phase-mapper-build-refusal-result-0005.json`; the 0004 receipt and code are
preserved.

The stage-specific cap does not weaken the inherited no-replace publication,
group-identity cleanup, unknown-state scratch retention, fresh Source/Reader/
Mapper byte checks, read-only guard child, or first sealed build-effect
refusal. Pure and synthetic tests exercise Source 240 acceptance, later-stage
240 rejection before launch, aggregate clamping, and a real short forced
timeout. No version 0005 preflight or fixture effect has been run. Independent
exact-byte review is required before any controlled attempt.

A future PASS would remain disposable guard/refusal evidence only. It would
not prove Mapper package construction, native invocation, Context, escaped
session absence, protected host containment, activation, or LC-U02-05
acceptance. The LC-U03-02 cgroup oracle and actual protected authorities
remain necessary for host qualification.
