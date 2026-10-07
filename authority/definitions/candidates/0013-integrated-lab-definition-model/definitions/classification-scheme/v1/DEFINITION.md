<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Classification Scheme

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.classification-scheme`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:classification-scheme-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Classification Scheme is a versioned governed contract of axes, allowed values, definitions, cardinality, applicability, exclusions, assignment and evidence rules, hierarchy, mappings, compatibility, owner, and challenge route. A new Scheme version does not silently reinterpret or reclassify assignments made under an older version.

```text
ClassificationScheme(x) => governed_identity_or_record(x) and bounded_scope(x); ClassificationScheme(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Classification Scheme Definition. |

### Boundary conditions

- A Classification Scheme is a versioned governed contract of axes, allowed values, definitions, cardinality, applicability, exclusions, assignment and evidence rules, hierarchy, mappings, compatibility, owner, and challenge route.
- A new Scheme version does not silently reinterpret or reclassify assignments made under an older version.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

### Testable conditions

- Every use of Classification Scheme resolves to this exact Definition version or an admitted successor.
- Every claimed instance or use stays within the applicability statement and exclusions.
- No consumer infers admission, authority, success, identity equivalence, or external effect from the term alone.

## Plain-language voice

A Classification Scheme is a versioned governed contract of axes, allowed values, definitions, cardinality, applicability, exclusions, assignment and evidence rules, hierarchy, mappings, compatibility, owner, and challenge route. A new Scheme version does not silently reinterpret or reclassify assignments made under an older version.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Classification Scheme supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- scheme:agent-action/v1 defines independent action-kind, effect-class, and result-posture axes with closed values.

## Applicability

A Classification Scheme is a versioned governed contract of axes, allowed values, definitions, cardinality, applicability, exclusions, assignment and evidence rules, hierarchy, mappings, compatibility, owner, and challenge route.

### Exclusions

- A new Scheme version does not silently reinterpret or reclassify assignments made under an older version.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- A new Scheme version does not silently reinterpret or reclassify assignments made under an older version.
- The term supplies meaning only; carrier shape, relation availability, runtime behavior, and authority effect require separate admitted contracts.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.classification-model-review@2026-10-05 | whole-file | `2f8147089d6b245d5696d132c3bf49f757bdd43cebe03ff032d92202946c7439` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.classification-scheme@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0013-integrated-lab-definition-model/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- .arcanum/ontology-vault/2026-10-05-classification-model-review.md
- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md
- .arcanum/ontology-vault/2026-10-06-lab-semantic-gap-audit.md

## Residue

- Definition-owner review and exact admission remain required.
- Artifact Type carrier, relation, qualifier, ontology, runtime, and consumer decisions remain separate.

## Claim ceiling

This candidate defines Classification Scheme for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
