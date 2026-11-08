# Temporal delegation and obligation stress profiles

This candidate package implements the two selected experiments. Start with [the DAG](PLAN.md), [the semantic contracts](SEMANTICS.md), and [the result](RESULT.md). It keeps the accepted F0 profile and authority records separate.

## Run it

From the repository root, evaluate the supplied delegation snapshot:

```bash
python3 craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/stress_cli.py --request craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/examples/acts-for.json
```

Compute inherited obligations and their origins, conflicts and replayable certificate:

```bash
python3 craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/stress_cli.py --request craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/examples/inherits-contract.json
```

Replay the example certificate:

```bash
python3 craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/stress_cli.py --request craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/examples/certificate.json
```

The same requests can be sent on stdin. Output is one JSON response. Exit code 0 means the request was evaluated, including semantic no/unknown/invalid verdicts; 2 means transport rejection; 3 means compiler/toolchain execution was unavailable. A runtime query timeout returns unknown. The CLI builds fresh modules in a temporary directory; it does not trust a stale local build cache.

Requires the existing candidate-local Lean 4.33.1 toolchain and the installed Python `jsonschema` package. No global toolchain, service or external account is configured. Reproduce the complete proof and test audit:

```bash
python3 craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/validate_stress.py --write
```

Omit `--write` for a fresh validation without changing receipts. The validator checks parent source bindings, the pinned compiler/kernel, core import hashes, exact theorem assignments, transitive axioms, countermodels, strict transports and hostile controls.

## Interfaces and behavior

The [API contract](api-contract.json) defines three local operations; the [request schema](schemas/request.schema.json) and [response schema](schemas/response.schema.json) reject unknown properties and variants. These are candidate-local extensions, not modifications to the earlier global interface package.

All revisions are explicit. Epochs are supplied naturals, not timestamps inferred from the current clock. Scopes and condition atoms use exact equality. Every response includes a reason; temporal responses also include the exact snapshot and epoch. Redelegation chains, missing policy/gate interpretation and overrides produce unknown. A forbidden redelegation returns no.

For closure requests, `budget` bounds candidate enumeration plus potential conflict-pair comparisons, measured as `candidateCount + factCount²`. It is not a CPU-time guarantee. A separate 30-second query timeout returns unknown. An incomplete result has no facts, conflicts or complete certificate. A certificate proves its listed steps, not that it lists every fact; use `close-inherits-contract` for the complete fixed-profile closure. A returned yes with conflicts means computation completed and retained both norms, not that the contract is satisfiable or the instance conforms.

## Checked claims

[StressLaws.lean](StressLaws.lean) proves restriction preservation, irrevocable revocation stability, origin preservation by derivation induction, and independence from conformance assessments. It imports only the independent semantic modules.

[StressProofs.lean](StressProofs.lean) proves delegation checker soundness and conditional completeness, exact obligation closure, inheritance checker preconditions and budget bounds, and certificate soundness. [StressWitnesses.lean](StressWitnesses.lean) proves inhabited profiles and countermodels: historical representation after expiration, inheritance without conformance, conflict without explosion, invalid cycle and exhausted budget. [StressStatementAudit.lean](StressStatementAudit.lean) fixes six independent required theorem types and prints every audited declaration's transitive axioms.

The logic intentionally has two rules: propagate a resolved norm and forward that same fact. Adding arbitrary rule producers, overrides, executable conditions or temporal restoration requires a new semantic contract and new proofs. The JSON adapter and compiled evaluator are tested trust boundaries; the proofs establish the typed model, not authenticated real-world authority or runtime compliance.
