# Craft/AlchLang Lab submission fixture

This is a bounded technical Lab slice built from a new `application-v1` `.alch`
source through the **installed** `@cyberalchemy/alchlang@0.7.0-candidate.0`
CLI. `lab-submission.alch` declares a `Submission` Entity, named eligibility
Rule, list/optional Queries and a read-bound `SubmitSubmission` Operation.
The generated TypeScript performs a typed identity read, checks the current
row's `accepted` flag, and settles one in-memory replacement batch. The flag
is **synthetic fixture data**, not a signed owner decision or authorization.

The source and 10 exact companion files live in `source/`, including synthetic
meaning/acceptance records marked `authority_effect: none`. The fixture was
derived from the installed package's `examples/meta-types/rule-query` contract
using `materialize.mjs`, with Lab names and fresh digest closure. That
preparer imports the same installed candidate's lowering functions. It is
one-shot and refuses to overwrite `source/`; preserve it as provenance. The
`generated/` tree came from the installed public CLI, not handwritten code.

From this checkout, with the exact installed consumer at
`/home/vlad_/projects/cyberAlchemy-v2/release-candidates/business-authoring-v1/qualification/consumer`:

```bash
cd /home/vlad_/projects/cyberAlchemy-v2/release-candidates/business-authoring-v1/qualification/consumer
node_modules/.bin/alchlang check /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/craft-alchlang-ingress-working/source/lab-submission.alch
node_modules/.bin/alchlang verify /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/craft-alchlang-ingress-working/source/lab-submission.alch --out /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/craft-alchlang-ingress-working/generated
cd /home/vlad_/projects/CyberAlchemy-lab
node implementation/lab-runtime/craft-alchlang-ingress-working/run.mjs
```

Initial build used `alchlang build` with the same source and `--out` target
above while the output was absent. The installed `check`, `build`, and
`verify` all returned success with zero unsupported residue, 6 graph nodes,
9 generated TypeScript artifacts, source SHA-256
`2c20973f693b9fd764bf451ca97c60efb25f030a4f9b14451996fc49d824932a`,
inputs SHA-256
`4739436b22a7cdf07f9f345623fb226a0cd815e20ee5a75cacdff79024948e81`,
and output manifest SHA-256
`c6ef26e2a09b2b5c1b8a182f2618c4482a3e753595d1760daf717fe1d1b324dc`.

`run.mjs` rechecks source and exact output, compiles the generated TypeScript
with TypeScript 6.0.3, exercises Rule and optional-Query behavior, and runs
the generated Operation against an explicit in-memory transaction fixture.
`RUN.json` records six outcomes: committed, guard-refused, missing, commit
rejected, commit uncertain, and malformed input. Only the first creates a
committed batch. Its scratch JavaScript is removed after the run.

This slice does not include an HTTP/ASGI ingress, real issuer, signature,
principal, owner disposition, durable replay reservation, protected Source8
inputs, native Lab workflow, database, host installation, or external effect.
It does not close T31 or T33 or alter the original task ledger. Those paths
require their own exact authority and integration evidence.

## Open Questions

The actual Lab ingress route still needs a separately selected source contract,
trusted issuers, replay custody and durable publication before this technical
Operation could be joined to it. The current generated Operation is useful as
an executable type/guard/settlement pattern, not as that join.
