<!-- GENERATED FILE: edit artifact.json and rerun generator.py. -->

# Ubiquitous Language artifact type v1

> Generated from `artifact.json`; this view is not canonical.

- Artifact type: `cal.artifact-type.ubiquitous-language/v1`
- Candidate version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Definition: `cal.definition.ubiquitous-language`

## Representation contract

- Canonical machine file: `language.json`
- Generated human file: `LANGUAGE.md`
- Stable identity field: `language_id`
- Schema: `cal.schema.ubiquitous-language/v1`

## Distinct validation purpose

Proves one context-owned expression system with explicit concept dispositions, ambiguity, interpretation, usage, and revision routes.

## Orthogonality rules

| Rule | Mode | Requirement |
| --- | --- | --- |
| `CTX01-UL-01` | `deterministic` | Every language binds to exactly one explicit Bounded Context. |
| `CTX01-UL-02` | `hybrid` | Equal spelling across contexts never implies equal meaning. |
| `CTX01-UL-03` | `deterministic` | Expression bindings are unique and ambiguity remains explicit. |

## Four facets

### Classification

Language identity and context membership are explicit without becoming global Definition authority.

### Schema

The closed schema requires context, concepts, expressions, interpretation, usage, owners, ambiguity, and revision state.

### Human Continuation

LANGUAGE.md is generated and exposes all context-local bindings and unresolved ambiguity.

### Machine Checkable

Schema, unique expression, dependency, hostile fixture, and projection checks are executable.

## Remaining residue

- `CTX01-UL-R1` — No artifact-type-owner admission decision binds this candidate. Consequence: No Ubiquitous Language instance may rely on this candidate as an admitted type.
- `CTX01-UL-R2` — No context-local language owner roles are bound. Consequence: Governance and Ontology Lifecycle language instances remain blocked.

## Claim ceiling

This package is a Ubiquitous Language/v1 artifact-type candidate. PASS does not admit the type, create a language, or assert shared cross-context meaning.
