<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Architecture Pattern Fixture

- Identity: `EXAMPLE-APPEND-ONLY-LEDGER-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

### Applicability

```json
{
  "exclusions": "Does not establish retention legality, concurrent writer coordination, durable storage or projection correctness.",
  "required_context": {
    "history_policy": "preserve-prior-events"
  }
}
```

- **Artifact Type Ref**: `cal.artifact-type.architecture-pattern/v1`
- **Claim Ceiling**: `Bounded snapshot and declared-context checks only. No runtime enforcement, durability, concurrency, authority or pattern promotion proof.`
### Consequences

```json
[
  {
    "consequence_id": "history",
    "description": "Earlier events remain available for inspection.",
    "force_refs": [
      "traceability"
    ],
    "kind": "benefit"
  },
  {
    "consequence_id": "storage",
    "description": "History grows and requires a separate retention and projection strategy.",
    "force_refs": [
      "growth"
    ],
    "kind": "cost"
  }
]
```

### Constraints

```json
[
  "stable-scope",
  "unique-event-identities",
  "contiguous-sequence",
  "unchanged-prefix"
]
```

- **Context**: `An ordered local event history whose prior entries must remain available.`
### Forces

```json
[
  {
    "description": "Earlier recorded events must remain inspectable.",
    "force_id": "traceability"
  },
  {
    "description": "Retaining history increases storage and replay work.",
    "force_id": "growth"
  }
]
```

- **Owner Ref**: `role:architecture-owner`
- **Problem**: `Preserve an inspectable history as new events arrive.`
- **Profile**: `candidate:append-only-ledger-snapshots/v1`
- **Response**: `Append newly identified events after the existing sequence; represent corrections as later events.`
- **Schema Version**: `cal-architecture-pattern-record/v1`
- **Scope Ref**: `scope:example-history`
### Source Direction

```json
{
  "canonical": "architecture-pattern-record.json",
  "human_projection": "ARCHITECTURE-PATTERN.md",
  "projection_policy": "generated-only"
}
```

### Witness

```json
{
  "after": {
    "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0013-architecture-pattern-carrier/examples/after.json",
    "sha256": "eac4f8c751bf56b1cd95d00de20d3799c155ada7509ad4469a08ff320b743615"
  },
  "before": {
    "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0013-architecture-pattern-carrier/examples/before.json",
    "sha256": "25927eb26f820cfcc5ac73530ec32e658eebcbae567388e5b639099db911278c"
  },
  "context": {
    "history_policy": "preserve-prior-events"
  }
}
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
