[Documentation home](../../README.md)

# Append-Only Event Ledger

<a id="def-cal-definition-append-only-event-ledger-pattern"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Append-Only Event Ledger

An ordered event-recording pattern that retains earlier entries and records corrections as new entries. Retrying the same action must not count it twice.

**When it applies**

Use append-only event ledger for imports, promotions, schema amendments, authority movement, idempotent generation, task receipts, validation runs, or runtime events when replay and audit matter. The ledger may project current state into indexes or ontology views, but the projection is derivative.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

Record what happened as a new line. If the same action is retried, it should not count twice. If something was wrong, add the correction instead of erasing the trace.

## Exact governing statement

Append-Only Event Ledger is the normalized architecture-pattern identified by semantic.append-only-event-ledger-pattern, owned within scope.repository-governance, and carried by type.architecture-pattern. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D26 without silently merging it with another target.

Bound source-semantic basis:

Append-only event ledger is a CyberAlchemy v2 ledger pattern for state-changing or authority-affecting operations where each change is recorded as an additive event instead of silently rewriting prior state.

An append-only event ledger must preserve:

- registered event kinds or event catalog membership - deterministic subject or stream identity - idempotency key or duplicate-guard rule for retryable operations - event payload or source reference - actor, owner, or route - timestamp or ordering handle - replay, projection, or human-audit interpretation

````
For an event stream `E = [e_1, ..., e_n]`, current projected state is:

```text
P(E) = fold(apply, initial_state, E)
```

A new event `e_{n+1}` may be appended when its event kind is admitted, its
subject identity is deterministic, and its idempotency handle prevents a retry
from producing a second semantic change. Corrections are represented by new
events, not untracked mutation of the old event.
````

- Append-only event ledger is not the same as `CAV2-D20` Craft method and does not promote the unresolved generic `ledger` primitive. It is one ledger pattern for operations where event order, retry behavior, and projection traceability matter.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/append-only-event-ledger-pattern/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.append-only-event-ledger-pattern@1.0.0-candidate.1

**Content fingerprint · SHA-256**

9960df95583e04ee8499fa233a156aee53c24173f4e34a4eedb6f7ac36e9231f

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use append-only event ledger for imports, promotions, schema amendments,\nauthority movement, idempotent generation, task receipts, validation runs, or\nruntime events when replay and audit matter. The ledger may project current\nstate into indexes or ontology views, but the projection is derivative.",
  "authority_scope_ref": "scope.repository-governance",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
