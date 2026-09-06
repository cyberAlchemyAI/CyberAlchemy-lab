<!-- GENERATED FILE: edit drift-audit.json and run ../build.py. -->

# CML08-P0 Prototype Definition Drift Audit

> Prototype audit only; no semantic promotion.

## Summary

- Prototype Definition Count: `12`
- Live Registry Collisions: `0`
- Undefined Prototype Terms After P0: `0`
- Conflicting Consumers: `0`
- Open Authority Promotions: `0`

## Findings

### CML08-P0-DRIFT-001 — resolved-in-prototype

Target: `twelve D65 construction terms`

The Lab had no product-construction prototype registry for the current D65 vocabulary.

Remediation: Use definitions.json for epoch-001 prototype construction only; do not add these IDs to the authority registry.

### CML08-P0-DRIFT-002 — preserved-boundary

Target: `CAV2-D67 Product Capability`

The active CyberAlchemy-v2 Product Capability definition is source authority; the Lab record specializes it only as a non-authoritative prototype.

Remediation: Keep CAV2-D67 source binding exact and prohibit Product Feature or Capability Instance identity collapse.

### CML08-P0-DRIFT-003 — superseded-planning-language

Target: `CAL-CML08-12-CRAFT-FIRST-CAPABILITY-VERTICAL-0001`

The predecessor chain used admission-oriented construction language and combined product evaluation with later operational requests.

Remediation: Preserve predecessor bytes historically and use successor chain 0002 for current prototype construction.

### CML08-P0-DRIFT-004 — future-consumer-not-yet-authored

Target: `CML08-P1 Agent-Facing Ontology Scaffold`

P1 has no scaffold artifact yet and therefore cannot drift against these prototypes.

Remediation: Author P1 only after this P0 package reports TESTED_PROTOTYPE and bind all twelve definition digests.

## Claim ceiling

This audit checks prototype-definition collisions, missing terms, and known planning consumers only. It does not promote meaning or assert repository-wide semantic closure.
