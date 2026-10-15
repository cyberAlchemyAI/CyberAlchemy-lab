# Proposed Session boundary composition

This successor keeps the 34 public contracts, all 239 inherited test methods,
original source period and maximum 900 second Session lifetime.

## Opening

The pure opening preflight uses `fact-read-scope-v2`. Its guarded source copy
comes from the original implementation and registry. Full source and package
verification occurs on entry and exit. Each policy use reads the actual policy,
checks revocation and checks the real clock. Durable dispatch remains forbidden
inside the copy scope. Original source callbacks are unchanged.

## Termination

Initial authentication captures the verified original period binding and
accountable Principal. This identity record conveys no permission. Every close
rechecks the actual policy bytes, owner, mode, closed schema, scope, operation
grant, budgets and expiry. It rereads the exact original period bytes and checks
their path, hash, Principal and original absolute time interval.

These checks allow termination after Project State drifts. They preserve the
existing ability to dispose Session memory without reconstructing a new
Context View. Normal use still requires current source checks. Revoked or
expired policies cannot use this path.

## Example

An Agent opens a Session from a verified Context View and Ontology View. A new
Project State makes those views stale. Further work requires fresh views. The
host can still close the existing Session and erase its short memory while its
original policy is current. The close receipt records disposal; it grants no
new work and cannot restore the Agent.

## Evidence required

The helper's complete 22 case run must pass before this successor is frozen and
used in owned runtime fixtures. Its six additional cases exercise real policy
reads, owned Project State drift, revocation, mode drift, captured identity
tampering and unchanged permission boundaries. The original integration,
metadata/export, review and Session lifecycle obligations remain required.

This boundary proposal does not authenticate a Machine Agent through the
transport. That integration remains a separate unfinished obligation.
