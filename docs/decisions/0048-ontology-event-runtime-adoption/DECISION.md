# Runtime adoption decision 0048

Status: adopted. Selected option: `EVRT-RADOPT-1`.

The user's “admit” selects the exact Rust lifecycle library as the runtime
provider behind admitted binding v2 for approved Ontology Product 0006.

Candidate SHA-256: `e326a4fb79829c78d796e63a876bca4ddcca7a1dd607024c486aa3f51c4a47c0`.

The frozen candidate and its README remain historical pre-decision evidence.
This external [decision](decision.json) supplies adoption status without changing
any accepted source bytes.

## Scope

The binding's materialize/observe commands calculate snapshots and Context
projections from per-subject events for the tested 14-node, 15-relation graph.
The runtime source, Cargo manifest, dependency lockfile and binding are fixed by
the candidate's exact references.

This does not adopt the standalone runtime CLI, activate a service, reinstate
repository enforcement, migrate legacy ontologies, or authorize publication,
cutover or deployment. All five candidate limitations remain in force.

## Work lanes

Product construction: Product 0006 is approved and binding v2 is admitted;
this decision changes no Product bytes and introduces no construction blocker.

Operational support: runtime adoption is recorded here. Activation target and
startup-envelope preparation remains with the runtime owner; activation itself
needs a separate exact decision. Legacy migration remains with source ontology
owners, and publication with the repository owner. These deferred tasks do not
block independent prototype construction.

## Verification

From the Lab root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 docs/decisions/0048-ontology-event-runtime-adoption/validate-decision.py
```

The validator checks the exact decision, source evidence, owner-gate selection,
fresh preacceptance with nested Product tests, and hostile decision mutations.
Validation verifies the recorded authorization; it grants no successor effects.
