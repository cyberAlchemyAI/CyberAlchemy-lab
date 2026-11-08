# Relational theorem checker interfaces

**Status: candidate definitions.** This package authors schemas, behavioral contracts and API specifications across L0-L4. It includes structural conformance tooling and synthetic examples. F0 now has a [pure Lean reference checker and general soundness proof](../formal/RESULT.md), with candidate acceptance and author self-review. The JSON decoder, HTTP service and CLI remain unimplemented; no layer evidence gate is marked complete.

## Inspect

- [Interactive schema and API explorer](index.html)
- [Schema catalog](SCHEMAS.md) and [behavioral contracts](CONTRACTS.md)
- [OpenAPI specification](api/openapi.json) and [API flows](API.md)
- [CLI contract](api/cli-contract.json)
- [DAG traceability](TRACEABILITY.md) and [original plan](../../../../../../docs/plans/relational-theorem-checker/dag-plan/PLAN.md)
- [Validation report](receipts/interface-validation.json)

## Profile policy

The generated companion carrier preserves all 41 selected relation kinds and 550 relation-specific ordered-pair entries, including materializes-consequence. It imports original qualifier shapes: conformance_evidence_refs remains a string. Generic graph/proposal contracts can represent a future changed registry; its actual qualifier and endpoint semantics must be validated against that proposed registry, not silently against the frozen companion.
The L0 profile is explicitly draft. Formalization is the first plan phase: P01 semantics, P03 formal predicates, P04 Lean reference checker and P05 soundness review precede B00/P02 execution capture and interface/decoder alignment. Existing schemas/APIs are draft projections to align with that accepted formal model. The required-semantics text is not a formal theorem; imported forbidden-inference text is preserved, not proved.
Normalized kind versions use sha256:<source digest> because the selected source records do not supply a uniform version field. This content identity is an explicit projection convention, not a newly admitted semantic version.

## Validation

```bash
python3 -B craft/formalization/candidates/relational-theorem-checker/v1/interfaces/validate_interfaces.py
```

Validation checks all schema meta-definitions and local references, positive/negative fixtures, generated registry fidelity, OpenAPI structure, contract/DAG coverage and declared structural cross-record boundaries. It does not execute Lean, solve model obligations, authenticate protected roots or certify semantic correctness.
Examples containing synthetic identities are shape fixtures, not deployable requests or accepted evidence. The bound package example sources and registry digests are real; semantic status remains imported/draft.

## Version and identity policy

Every instance envelope declares a candidate schema version. Objects are closed except intentional qualifier/substitution maps. Hash SHA-256 over exact UTF-8 bytes; reject duplicate JSON keys, invalid UTF-8 and untrusted digest claims before interpreting a document. Hash references do not grant artifact access. No network fetch or arbitrary filesystem path evaluation is part of reference resolution.
The schema namespace is a logical identifier and is resolved locally; no publication at cyberalchemy.local is claimed.

## Standards

The definitions use [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-core) and [OpenAPI 3.1.1](https://spec.openapis.org/oas/v3.1.1.html).
