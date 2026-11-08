---
node_type: decision
is_session: false
status: pass
boundary: INTERNAL — DomainSpec v2 DS-D8 enforcement scope authority
created: 2026-07-22
decision_id: DEC-DSV2-ENFORCES-CROSS-FEATURE-SCOPE
target_scope: Rule-to-Operation enforcement across feature boundaries
source: operator direction "lets do the enforces", reconciled with existing tuple semantics and deprecation authority
---

# Decision: `enforces` admits cross-feature placement

## Conflict

The active `enforces` tuple admitted only `same-feature`, while its semantics,
human companion, learning view, code-tag projection, and the `enforces-cross`
deprecation record all said that cross-feature enforcement uses the canonical
`enforces` verb with scope carried separately. The machine tuple therefore
rejected the replacement prescribed by its own authority.

## Decision

1. `enforces` remains the only canonical Rule-to-Operation gating verb.
2. Its DS-D8 `feature_scope` admits both `same-feature` and `cross-feature`.
3. Markdown placement carries location: `Feature Concept Graph` is same-feature;
   `Cross-Feature Dependencies` is cross-feature.
4. `enforces-cross` remains deprecated and rejected with replacement guidance.
5. Multiplicity remains `many_to_many`; scope admission does not change semantic
   responsibility cardinality.

## Application

```text
same-feature:
  CanCreatePlayer --[enforces]--> CreatePlayer

cross-feature:
  compliance.AccessRule --[enforces]--> payments.ProcessRefund
```

Rejected spelling:

```text
compliance.AccessRule --[enforces-cross]--> payments.ProcessRefund
```

The cross-feature Rule remains independently owned by its feature. The edge
states that the target Operation must satisfy that Rule before mutation; it does
not merge feature ownership, duplicate the Operation, or create a new Rule kind.

## Evidence and validation contract

- root DS-D8 authority carries both location tokens on `enforces`;
- same-feature production witnesses remain valid;
- a positive cross-feature fixture validates the canonical base verb;
- the deprecated alias remains a negative control;
- endpoint, composition, content, compiler, and generated-view checks pass; and
- the definition drift audit closes the former consumer conflict.

## Boundary

The Markdown relationship validator and minted-project compiler validate
feature placement from specification structure. The code-tag checker validates
the canonical verb, endpoint kinds, and call obligation but does not infer
feature boundaries from code symbols alone.

## Validation evidence

- DS-D8 and the human companion agree on same/cross-feature scope.
- The focused relationship suite passes 15/15, including the new canonical
  cross-feature witness and existing endpoint negatives.
- Definitions aggregation passes with 37 concepts, 34 edges, zero duplicate
  IDs, and zero type drift.
- Documentation, relationship, content, TypeScript, and sample-lint checks pass.
- Tooling passes 160/160; code-tag tests pass 15/15; engine tests pass 107/107.
- Create Player and Key and Door digest-bound generated views were regenerated
  deterministically.

There is no remaining promotion blocker for this decision.

## Source evidence

- `projects/domainspec-v2/definitions/relationships/relationships.yml`
- `projects/domainspec-v2/definitions/relationships/relationships.md`
- `projects/domainspec-v2/impl/spec/meta-types/LEARNING-ORDER.md`
- `projects/domainspec-v2/impl/governance/tags/CODE-TAG-COMPOSABILITY-PATTERNS.md`
- `projects/domainspec-v2/definitions/DEFINITION-DRIFT-AUDIT.md`
