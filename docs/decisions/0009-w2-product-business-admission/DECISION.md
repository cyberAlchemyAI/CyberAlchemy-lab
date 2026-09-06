# W2 Product Capability And Business Ontology Admission

Decision: `CAL-W2ADM-0009`

Question: `G-W2-PRODUCT-BUSINESS-ADMISSION`

Selected option: `W2ADM-1`

Status: `selected`; bounded admission: `admitted`

Decision source: explicit user selection

Decision time: `2026-09-01T20:55:49Z`

## Decision

Admit the exact coupled W2 Product Capability and business ontology epoch for
the CyberAlchemy Lab ontology-lifecycle CAV2-D65 construction chain, then
reevaluate `G-W4` and its `G-W5` successor against that immutable epoch.

The admission is separate from the candidate files' status fields. Those
remain `candidate-unadmitted` because this is a bounded Lab construction
admission, not a public artifact release.

## Exact epoch

| Artifact | SHA-256 |
| --- | --- |
| `product-capability.json` | `b042e6e0165fde0196bb916ae8f77ef7e7f8d1cd15f1f700d2350a5e60bec3df` |
| `business-ontology.json` | `3ea266238a33616da279a5b3434a5e3b3482deac22ecee0ddc6ae65e67826eac` |
| W2 validation receipt | `0bcc0dd5a9c555ef575f337ff392a3f32ea50d9a41a6f5215a2811fee8aff783` |
| Pre-admission W4 gate | `6a5d14d06b84ae3ec8e50d3cf85f1e6cef9d013111c29ec33f47749209042534` |

The Decision Gate request digest is
`781d24c0996199b0b81a1955bd2dbc9eb5851faf119febcb11ea04ae3ac77c01`.
The prefilter was reproduced byte-for-byte before this record was written.

## Effect and boundary

This decision resolves the W2 Product Capability and business ontology owner
gate. It permits fresh evaluation of these exact bytes as CAV2-D65
predecessors. A passing `G-W4` evaluation may restore `G-W5` predecessor
readiness.

It does not:

- edit either candidate status field;
- publish or release the Product Capability or business ontology;
- make `G-W4` or `G-W5` pass without reevaluation;
- accept the Rust runtime or prove independent conformance; or
- authorize publication, deployment, migration, cutover, or external effects.
