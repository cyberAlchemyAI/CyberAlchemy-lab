<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->

# CTX06 Definition drift audit

> Generated candidate projection; it is not canonical.

## Summary

- Candidate Definition Count: `2`
- Undefined Critical Terms: `0`
- Conflicting Current Consumer Groups: `4`
- Historical Epochs Rewritten: `0`
- Wrong Workspace Voices: `0`
- Definition Evaluation Blockers Before Owner Decision: `0`
- Owner Decision Required: `True`
- Successor Implementation Blockers: `4`

## Findings

### CTX06-DRIFT-001 (semantic-cycle, resolved-in-candidate)

Bounded Context/v1 canonically includes context_map_refs while Context Map/v1 canonically includes exact endpoint context_refs. Updating either side to an exact successor version creates another required successor on the opposite side.

Target: `cal.definition.bounded-context and cal.definition.context-map`

Remediation: Admit Bounded Context/v2 and Context Map/v2 together: maps solely own endpoint membership, while reverse membership is generated.

Blocking for: Successor Context Map construction until the two candidate Definitions are admitted.

### CTX06-DRIFT-002 (conflicting-operational-consumers, open)

The admitted Bounded Context/v1 artifact type and shared CTX01 schema require context_map_refs, contradicting the proposed normalized ownership rule.

Target: `authority/artifact-types/bounded-context/v1 and tooling/schemas/ctx01/v1/schema.json`

Remediation: After Definition admission, author a Bounded Context/v2 artifact type and schema that forbid canonical map backreferences; preserve v1 bytes for historical conformance.

Blocking for: Normalized context instance construction, not Definition candidate evaluation.

### CTX06-DRIFT-003 (admitted-epoch-remediation, open)

Both admitted CTX05 successor contexts contain a canonical reference to the v1 map. Their exact bytes and admission evidence must remain immutable.

Target: `contexts/governance/v2 and contexts/ontology-lifecycle/v2`

Remediation: After normalized artifact-type admission, author new context epochs without map backreferences and bind them through explicit lineage; do not rewrite CTX05.

Blocking for: Normalized successor endpoints, not Definition candidate evaluation.

### CTX06-DRIFT-004 (historical-compatibility, open)

Historical validators and the admitted plan intentionally bind the former context_map_refs contract and exact CTX05 bytes.

Target: `docs/decisions/0023, docs/decisions/0025, and contexts/migrations/governance-ontology-lifecycle-v1-to-v2/v1`

Remediation: Keep historical evidence unchanged. Author a new migration amendment and validators for normalized successor epochs after their prerequisites are admitted.

Blocking for: Future migration execution, not historical validity or Definition candidate evaluation.

### CTX06-DRIFT-005 (missing-generated-surface, open)

No deterministic generated reverse-membership index exists yet.

Target: `tooling/generators/context-map-membership-index`

Remediation: After Context Map/v2 artifact-type admission, author a generator whose only inputs are admitted Context Map records and whose output is disposable projection state.

Blocking for: Convenience reverse lookup, not canonical Context Map semantics.

### CTX06-DRIFT-006 (decision-gate, open)

The live canonical registry remains byte-identical with eight admitted v1 definitions; the two CTX06 successors have no authority effect.

Target: `authority/definitions/registry.json`

Remediation: Review the two exact successor digests and complete postimage, then make a separate definition-owner decision to admit, revise, defer, or stop.

Blocking for: Canonical CTX06 semantic authority.

## Claim ceiling

This audit identifies and routes the Context Map backreference cycle. It does not replace the live audit, admit either successor Definition, revise historical artifacts, authorize implementation or migration, or establish a stable release.
