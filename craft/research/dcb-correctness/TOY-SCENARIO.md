# Toy Scenario: Knowledge Graph Stale Anchor

## Scenario

The Knowledge Graph feature has a definition-opening workflow that depends on
source documents, anchors, projections, and UI/test evidence.

The stale-evidence problem:

1. A projection snapshot `S1` contains a concept anchor:

   ```text
   concept:DefinitionPointer -> domain.md#definitionpointer
   ```

2. A test or verification claim is assembled against `S1`.
3. The source document changes after `S1`; the anchor is renamed or moved.
4. The old correctness claim is still around.
5. Static checks may pass if they only verify the old UI mapping or old test
   source reference.
6. A DCB-style correctness boundary should reject accepting the old claim,
   because a matching source fact changed after the claim's read marker.

## Static Validator Baseline

A static validator can catch:

- malformed source refs;
- broken anchors if link validation runs;
- missing code tags;
- docs-only/code-only drift;
- incorrect test source annotations.

But a stale report can still be misused unless the claim acceptance step knows
what facts were read and whether they changed.

## DCB-Style Check

Read tags:

```text
feature:knowledge-graph-visualization
concept:DefinitionPointer
aspect:domain
operation:OpenDefinition
projection:S1
```

Read marker:

```text
m2
```

New event:

```text
SpecFactChanged(tags=[feature:knowledge-graph-visualization, concept:DefinitionPointer], marker=m3)
```

Append condition:

```text
No matching fact for read_tags changed after m2.
```

Expected result:

```text
Reject CorrectnessClaimAccepted(c1)
Reason: concept:DefinitionPointer changed after read marker m2.
```

## Why This Toy Is Enough

It demonstrates a difference between:

- validating the current shape of artifacts; and
- accepting a correctness claim based on facts that may have gone stale.

That is the narrow value DCB can add to DomainSpec.
