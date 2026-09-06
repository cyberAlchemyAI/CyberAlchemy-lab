<!-- GENERATED FILE: edit lineage.json and rerun generator.py. -->

# Context Lineage Record: cal.context-lineage.governance.v2-to-v3

> Generated from `lineage.json`; this view is not canonical.

- Identity: `cal.context-lineage.governance.v2-to-v3`
- Version: `1.1.0-candidate.1`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.context-lineage-record/v1`
- Semantic kind: `context-lineage-record`
- Authority effect: `none`

## Predecessor Context Ref

cal.context.governance/v2

## Successor Context Refs

- cal.context.governance/v3

## Lineage Kind

successor

## Source Version

1.1.0-candidate.1

## Destination Versions

- 2.0.0-candidate.1

## Preserved Scope

Governance context identity, semantic owner, domain-model reference, exact admitted v2 Ubiquitous Language ownership, owned meanings, challenge route, and exclusions from Ontology Lifecycle remain unchanged.

## Changed Scope

The successor uses the admitted Bounded Context/v2 contract, removes canonical context_map_refs, updates Bounded Context and Context Map Definition bindings to v2, and makes canonical map-membership ownership external to the endpoint artifact.

## Decision Ref

candidate:CAL-CONTEXT-PACK-CTX08-0001#authorship-direction

## Effective Boundary

Candidate authorship only. The admitted v2 context remains authoritative until a separate exact governance-context-owner decision admits the v3 epoch; no successor Context Map or migration cutover is inferred.

## Challenge Route

role:context-lineage-owner

## Owner Ref

role:context-lineage-owner

## Equivalence Inferred

`false`

## Admission Inferred

`false`

## Evidence

- CAL-DECISION-0025-GOVERNANCE-ONTOLOGY-LIFECYCLE-SUCCESSOR-PROMOTION
- CAL-DECISION-0027-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPE-PROMOTION
- cal.context.governance/v2
- cal.language.governance/v2

## Residue

- residue:governance-v3-context-owner-admission-required
- residue:governance-v2-to-v3-lineage-owner-admission-required
- residue:successor-context-map-and-migration-amendment-not-authored

## Claim ceiling

This candidate records only a proposed Governance v2-to-v3 successor relation. It does not infer equivalence, admission, supersession, Context Map membership, migration completion, or authority; mutate v2; authorize deletion, implementation, publication, or deployment; or establish stable-release state.
