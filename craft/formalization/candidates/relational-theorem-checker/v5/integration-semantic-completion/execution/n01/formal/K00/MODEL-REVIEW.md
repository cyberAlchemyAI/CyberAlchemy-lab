K00 candidate model review

The human user accepted the exact K00 intended meaning as semantic owner. That
assessment is captured separately in `../../assessments/K00.json`; the questioned
definition and review manifest are unchanged. The Lean files added afterward
are supporting candidate preparation, not a new accepted definition revision.

`ActsForCandidate.lean` defines an independent resolved delegation model. Each
right binds action, subject and scope. A finite inductive delegation chain must
reach an independently supplied authority root, preserve every ancestor's scope
and rights, satisfy owned gates, remain active and have exact as-of revocation
evidence. Redelegation requires the parent's permission. Interval windows and
observed session windows have separate semantics.

`ActsForWitnesses.lean` constructs a satisfiable two-level delegation. It checks
expiry, wrong agent, unknown/revoked status, an unknown required gate, missing
session observation, mismatched session snapshot and a rootless world. It also
constructs three countermodels: representation with distinct identity classes,
unchanged file ownership and no grant for writing. Authority is searched across
all supplied delegations rather than only the named delegation's rights.

The replay driver rebuilds the two imports and both new modules separately in
two clean output directories with the pinned compiler and library. It inspects
every theorem's axioms and refuses `sorry`, `admit`, custom axioms or
`native_decide`. Failed preparation attempts are preserved in `repair-attempts`.
See `verification.json` for actual counts, hashes, compiler output and timing.

Remaining work required before any inherited discharge:

- Raw source decoding and the four exact qualifier-to-record refinements are
  absent. Action and subject are explicit fields in the candidate primary
  witness; the source/provenance adapter must establish where they come from.
- The model assumes independently captured typed catalogs. It does not yet prove
  non-equivocation, authenticated ownership or complete profile/context/snapshot
  binding for delegation, scope, authority and observation catalogs. Conditions
  use the previously checked owned-definition resolver.
- Finite scope membership represents the owned scope interpretation. The source
  resolver must establish its complete membership, inclusion and exclusions;
  traversal/resource limits and opaque token interpretation remain separate.
- Session activity is checked at the window level. A complete session-backed
  representation witness and source refinement remain to be added.
- Exact-time revocation is used here. Conflict handling, observation freshness
  and historical/live policies need their owned policy contracts and replay.
- Recording preserves a typed protected-state object in this model. The append
  function does not yet enforce qualification, revision idempotence, conflicting
  content refusal, full-rule closure or crash-safe public execution.
- Countermodels are checked only in this explicit delegation fragment. Additional
  relation rules, direct authority routes, policy conflicts and any other grants
  must be included in the complete pinned theory. The finite universe must be
  established as the owner's complete universe, not the caller's reduced list.
- Independent-checker replay is still pending under N11. Human acceptance of
  the candidate meaning does not supply any of these mathematical or integration
  checks.

This result advances candidate formalization while N01's other assessments stay
open. It discharges zero inherited IDs and accepts no additional plan task.
