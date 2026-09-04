<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->

# Definition and CTX-00 candidate drift audit

> Generated candidate projection; it is not canonical.

## Summary

- Candidate Definition Count: `8`
- Undefined Candidate Terms: `0`
- Conflicting Candidate Consumers: `0`
- Stale Source Selections: `0`
- Wrong Workspace Voices: `0`
- Definition Evaluation Blockers Before Owner Decision: `0`
- Owner Decision Required: `True`
- Successor Context Blockers: `2`

## Findings

### CTX00-CANDIDATE-DRIFT-001 (info, resolved-in-candidate)

The foundational Definition term now has one Definition/v1 candidate with all three voices, admitted source references, index presence, and a drift route.

Target: `cal.definition.definition`

Remediation: Preserve the exact candidate and include it in the same owner decision as the seven dependent CTX-00 definitions.

### CTX00-CANDIDATE-DRIFT-002 (info, resolved-in-candidate)

All external CTX-00 sources resolve to exact admitted selections and target concepts.

Target: `CAL-DECISION-0017-CTX00-SOURCE-ADMISSION`

Remediation: Reject any later digest or target-use widening without a new source-admission decision.

### CTX00-CANDIDATE-DRIFT-003 (info, resolved-in-candidate)

All eight shared metamodel definitions use the admitted definition-owner role; operational context and migration roles are kept outside semantic Definition authority.

Target: `role:definition-owner`

Remediation: Bind operational roles before creating their artifact instances, not by changing definition ownership.

### CTX00-CANDIDATE-DRIFT-004 (successor-blocker, open)

Artifact types for Bounded Context, Coordination Context, Ubiquitous Language, Context Map, Capability Instance, Context Migration Manifest, and Context Lineage Record do not yet exist.

Target: `authority/artifact-types`

Remediation: After definition promotion, author each artifact-type candidate with its own schema, generator, validator, and negative tests.

### CTX00-CANDIDATE-DRIFT-005 (successor-blocker, open)

Operational owner roles and the exact Governance to Ontology Lifecycle Context Map relationship pattern remain unselected.

Target: `contexts/governance and contexts/ontology-lifecycle`

Remediation: Bind non-collapsing operational owners, author both context candidates, then select the directional integration pattern.

### CTX00-CANDIDATE-DRIFT-006 (decision-gate, open)

The live canonical registry remains byte-identical and empty; this candidate postimage has no authority until an exact definition-owner promotion decision.

Target: `authority/definitions/registry.json`

Remediation: Review the eight exact candidate digests and the complete postimage/evidence set, then select admit, revise, defer, or stop.

## Claim ceiling

This candidate drift postimage evaluates the proposed eight-definition set. It neither replaces the live drift audit nor admits a Definition, artifact type, context, migration, or implementation.
