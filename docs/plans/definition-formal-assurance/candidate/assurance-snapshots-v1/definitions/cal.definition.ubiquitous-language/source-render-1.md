<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Ubiquitous Language

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.ubiquitous-language`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-context-metamodel`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Ubiquitous Language is the owner-governed set of expressions, concepts, relations, interpretation rules, usage surfaces, ambiguities, and revision routes used to express one Bounded Context's model. Each load-bearing expression resolves to one current concept disposition within that context or remains explicitly unresolved.

```text
UbiquitousLanguage = (id, bounded_context_ref, concept_refs, expression_bindings, relation_bindings, interpretation_rules, usage_surfaces, owner_refs, ambiguity_records, revision_state); CurrentBinding => BelongsTo(bounded_context_ref); SharedSpelling does not imply SharedMeaning.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| CurrentBinding | One expression-to-concept binding active in the named context version. |

### Boundary conditions

- The language belongs to exactly one Bounded Context identity at a time.
- Cross-context reuse needs an explicit bridge or mapping.
- Ambiguity is recorded, not silently collapsed.

### Testable conditions

- Every current expression binding names its context and concept disposition.
- Cross-context equal labels are not treated as equal meanings without a map.

## Plain-language voice

The shared vocabulary used to discuss and build one bounded part of the domain.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

Governance and Ontology Lifecycle must own distinct language artifacts; terms such as decision, event, lifecycle, and state cross the boundary only through explicit mappings.

### Examples

- Governance can define admission while Ontology Lifecycle maps that meaning into event history without owning the admission decision.

## Applicability

Owned expressions used to articulate one exact Bounded Context model.

### Exclusions

- Repository-wide dictionaries and programming languages.
- Unowned glossaries or claims of universal shared understanding.

## Boundaries

- A Ubiquitous Language is not a repository-wide dictionary, canonical definition registry, glossary file, ontology, programming language, maintenance discipline, or proof of common understanding.
- Its generated human view is not an independent source of meaning.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| CAL-SOURCE-ADMISSION-CTX00-LANGUAGE-CONCEPTS | whole-json | `e8cc7d26fffb69bc9b94eb8ecd70259c04b45f3683f52941084b7a07f37d436d` | `admitted` |
| CAL-SOURCE-ADMISSION-CTX00-GOVERNANCE-LANGUAGE | whole-json | `253530491c2555c75ce9fa6e5a90cb40ecbd6ca5b3e55e557c28360e6df02c13` | `admitted` |

## Primary consumers

- contexts/*/language
- contexts/*/context.json
- contexts/*/maps

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.ubiquitous-language`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.ubiquitous-language@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- CAL-DECISION-0017-CTX00-SOURCE-ADMISSION

## Residue

- ubiquitous-language-artifact-type-required
- context-language-owner-bindings-required

## Claim ceiling

This candidate defines Ubiquitous Language meaning only; it does not admit any context-local language or assert shared meaning across contexts.
