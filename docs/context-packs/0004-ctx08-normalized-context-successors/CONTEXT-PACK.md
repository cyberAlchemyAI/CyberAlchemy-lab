<!-- GENERATED FILE: edit context-pack.json and rerun render.py. -->

# CTX08 normalized context successor candidate pack

> Machine-canonical pack; this Markdown is a generated projection.

- Pack: `CAL-CONTEXT-PACK-CTX08-0001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Objective

Author dependency-closed Governance and Ontology Lifecycle v3 Bounded Context candidates that use the admitted normalized v2 artifact type, preserve their exact admitted v2 languages, and record explicit non-inferential v2-to-v3 lineage.

## Authorship direction

- Principal: `person:<vrondelli>`
- Instruction: `author-normalized-governance-and-ontology-lifecycle-successor-context-epochs`
- Effect: `candidate-authorship-and-validation-only`

## Canonical candidates

| Artifact | Type | Owner | Path | Digest |
| --- | --- | --- | --- | --- |
| `cal.context.governance/v3` | `cal.artifact-type.bounded-context/v2` | `governance-context-owner` | `contexts/governance/v3/context.json` | `e085a9bf15e5d707108076aed86efd1684382652428db5b786fa741e99145dc3` |
| `cal.context.ontology-lifecycle/v3` | `cal.artifact-type.bounded-context/v2` | `ontology-lifecycle-context-owner` | `contexts/ontology-lifecycle/v3/context.json` | `4355473ab026ca3aadf59e7939a8eaf6d0fc719332417feeb97d538d6a87da84` |
| `cal.context-lineage.governance.v2-to-v3` | `cal.artifact-type.context-lineage-record/v1` | `context-lineage-owner` | `contexts/lineage/governance/v2/lineage.json` | `478b5a274e98325b94f5ca76e569697eb7cf4846077add74ce2046b49b2ce173` |
| `cal.context-lineage.ontology-lifecycle.v2-to-v3` | `cal.artifact-type.context-lineage-record/v1` | `context-lineage-owner` | `contexts/lineage/ontology-lifecycle/v2/lineage.json` | `49b692f76efbc7f8ab24ad4dc062082acb0e07212372770289ea4da902bf20bf` |

## Preserved admitted languages

| Language | Stable context | Path | Digest |
| --- | --- | --- | --- |
| `cal.language.governance/v2` | `cal.context.governance` | `contexts/governance/v2/language.json` | `ba84484be3f0d793e935ba4bbf960885ce1adcd2d2763aee940396ff290918d7` |
| `cal.language.ontology-lifecycle/v2` | `cal.context.ontology-lifecycle` | `contexts/ontology-lifecycle/v2/language.json` | `8d01b878d93fa1b502d57348b8c5cad3c25968504de0ef7df37b17e63dda2e55` |

## Normalization contract

- Canonical membership owner: `cal.artifact-type.context-map/v2`
- Language reuse: A representation-only context epoch may preserve the exact admitted Ubiquitous Language when its stable language identity, stable context identity, vocabulary, and owner bindings are unchanged.
- Lineage: Every new context epoch has one explicit v2-to-v3 lineage record; equivalence, admission, supersession, and migration are never inferred.
- Forbidden endpoint fields:
  - `context_map_refs`
  - `map_membership`
  - `canonical_reverse_membership_index`

## Promotion gate

- State: `not_evaluable-until-aggregate-and-conformance-validation-pass-and-owners-select`
- Required effect: One exact decision must bind both immutable context candidates, both lineage candidates, their generated projections, preserved language inputs, aggregate validation, and independent conformance.

## Residue

- residue:two-v3-context-owner-admissions-required
- residue:two-v2-to-v3-lineage-owner-admissions-required
- residue:normalized-successor-context-map-for-v3-endpoints-not-authored
- residue:source-and-rollback-bound-v2-to-v3-migration-amendment-not-authored
- residue:no-cutover-or-source-relocation-authorized

## Claim ceiling

PASS may establish only deterministic CTX08 candidate coherence. It does not admit either v3 context or lineage record, revise the admitted v2 languages, infer equivalence or supersession, construct or admit a Context Map, authorize migration or source relocation, commit, publish, deploy, or establish stable-release state.
