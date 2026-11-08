# Candidate relation checker CLI

Run the executable `cli` in this directory. All four commands emit one UTF-8
JSON outcome on stdout, with progress on stderr. They preserve the accepted
R01 exit-code precedence and have no authority effect.

```sh
cli check-instance REQUEST.json --profile f0-three-kind/v1
cli check-instance REGISTRY_REQUEST.json --profile captured-registry-structure/v1
cli check-extension PROPOSAL.json --bundle BUNDLE.json
cli check-proof SUBMISSION.json --proposal PROPOSAL.json
cli replay-evidence BUNDLE.json --proposal PROPOSAL.json
ci-example check-extension PROPOSAL.json --bundle BUNDLE.json
```

Use the executable's full path or invoke it from this directory. Proof and
bundle replay require explicit proposal context: the predecessor's conceptual
single-input command does not imply that a hash can reconstruct a proposal.
The adapter keeps the accepted predecessor contract bytes unchanged.

The default instance request is the accepted execution-input/v1 envelope,
including its optional relation addition, assessments and supplied roots.
For the structural profile, the closed envelope has
`schema_version: relational-checker.registry-instance-input/v1-candidate` and
`graph`, where the graph has the captured rich nodes, identified/versioned
assertions, assessments and admission_roots. This profile checks the independent
Registry.Inv against all 41 captured relation kinds and 109 node kinds. It
does not establish their inherited qualifier/reference meanings. The F0
profile retains three-kind semantics, exact evidence scope and identity,
with supplied assessment truth as an assumption.

Extension and replay commands execute R03 verification of every independently
generated hard obligation. The optional bundle chooses permitted evidence
methods; it cannot select fewer obligations or self-authorize readiness.
The proof command invokes the independent R02 checker for the exact required
statement. A rejected proof is invalid evidence, and does not disprove that
statement. Single instance and proof checks always report readiness
not-applicable.

`ci-example` executes the local checker and independently compares the required
inventory before accepting completed/current ready-for-review output. It does
not accept an outcome file supplied by a client. A successful single check,
unsupported profile, stale baseline, missing obligation or failed proof cannot
produce a CI review pass. Review readiness is a candidate recommendation;
human meaning/usefulness review and any authority action remain separate.

Inputs must resolve inside this workspace, remain within 4 MiB and decode as
strict JSON. Original-byte request and current accepted-export identities are
checked before and after execution. Generated evidence is retained in `runs/`
under unique owned directories. Exact offending assertion/kind diagnostics
include an obligation, input location and corrective action. Host runtime,
hashing, OS, source interpretation and externally supplied truth remain trust
assumptions. Full source semantics and deployment are outside these profiles.
