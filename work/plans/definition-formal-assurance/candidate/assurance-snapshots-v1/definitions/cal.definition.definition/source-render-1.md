<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Definition is a versioned, owner-scoped semantic artifact that assigns a term one normative meaning within an exact authority scope. It is structurally complete only when stable identity, applicability, exclusions, a scientific/formal normative voice, explicitly non-normative plain-language and domain-context voices, boundaries, admitted source posture, primary consumers, a synchronized registry postimage, generated index, and a current drift route are declared. Only an exact owner promotion decision can make one exact Definition version canonical authority.

```text
DefinitionComplete(d) iff StableId(d) and ExactScope(d) and FormalVoice(d) and NonNormativePlainVoice(d) and NonNormativeDomainVoice(d) and Boundaries(d) and AdmittedSources(d) and RegistryPostimage(d) and GeneratedIndex(d) and CurrentDriftRoute(d). DefinitionComplete(d) does not imply Admitted(d).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| d | One exact Definition version. |

### Boundary conditions

- A changed normative meaning requires a new Definition version.
- Interpretive voices cannot weaken or expand the normative voice.
- Schema validity and evidence do not perform promotion.

### Testable conditions

- The machine record validates against Definition/v1.
- The generated projection is byte-identical across two renders.
- The candidate appears exactly once in the proposed registry and generated index.

## Plain-language voice

The project-owned record that says exactly what a term means, where that meaning applies, and how drift can be challenged. A passing candidate is not canonical until its owner admits it.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

CyberAlchemy Lab stores each Definition as canonical JSON with generated Markdown. Legacy CyberAlchemy-v2 definitions can supply admitted evidence, but they do not become Lab authority by copying or citation.

### Examples

- cal.definition.definition is the foundational Definition/v1 instance candidate.
- The generated DEFINITIONS-INDEX.md is a lookup projection, not a second semantic authority.

## Applicability

Normative meanings intentionally shared across CyberAlchemy Lab authority and construction surfaces.

### Exclusions

- Context-local expressions that have no shared semantic role.
- Generated summaries, glossary hints, and source quotations.

## Boundaries

- A glossary entry, ontology node, source quotation, generated index row, or narrative explanation is not a Definition by itself.
- Definition identity, artifact type, semantic kind, authority kind, lifecycle posture, owner scope, and bounded-context membership are independent axes.
- One canonical field must never be silently inferred from another; dependent classifications require explicit typed relations; convenience labels are generated projections.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| CAL-SOURCE-ADMISSION-CAV2-D21 | CAV2-D21 | `71bd5c6fcc08eeced7b8530ab2c07c42f5904f8e7d9405f2073d47c43c5b51bd` | `admitted` |
| CAL-SOURCE-ADMISSION-CAV2-D33 | CAV2-D33 | `00e89bd7b1bd552cbd25870f67fa9a28e33e92ffd4d1f95d4e4309b20082d44f` | `admitted` |
| CAL-SOURCE-ADMISSION-CAV2-D51 | CAV2-D51 | `59fed72830f998c5b82bac83f2679ac0597da98d037f561d7300aa2e86f33c02` | `admitted` |

## Primary consumers

- authority/definitions/registry.json
- authority/artifact-types/definition/v1
- docs/definition-packs

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.definition`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.definition@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |
| relation.originates-from | cal.definition.definition@1.0.0-candidate.1 | CAL-SOURCE-ADMISSION-CAV2-D33 | role:definition-owner |

## Evidence

- CAL-DECISION-0015-DEFINITION-V1-ADMISSION
- CAL-DECISION-0013-FOUNDATION-01-ADMISSION

## Residue

- owner-promotion-decision-required

## Claim ceiling

This is a validated-candidate input only. It does not make Definition canonical, mutate the live registry, admit another term, authorize implementation, or establish release readiness.
