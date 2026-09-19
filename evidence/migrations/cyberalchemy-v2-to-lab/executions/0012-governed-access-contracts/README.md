# Governed System Building Access: candidate contracts completed

16 missing identities -> 16 explicit candidate contracts -> Capability candidate imported.

The bundle contains ten input/output contracts and six policy checks. Each contract has a closed JSON schema, a passing example and an explicit mapping to a named source concept. These are newly proposed carrier contracts, not renamed source identities or admitted KEP protocol extensions.

The schemas cover request/response/failure correlation, typed instantiation requests, supplied entitlement and workspace-authorization records, validated project descriptions, generated artifacts, read models and receipts. Policy checks cover request non-authority, create-only contained targets, customer custody, validation non-authority, read-only ontology inspection and non-inheritance of external effects.

Request-bundle checks compare caller, request digest, Product/project scope, node, language, target, entitlement, authorization references and expiry. Response checks compare request correlation, artifact and receipt digests and source/generator provenance. Paths are checked lexically; a real filesystem adapter still must enforce containment and atomic create-only publication.

## What the proposals mean

The version 1 schemas, field choices, integer Unix-second timestamps, closed enum choices and canonical JSON digest convention are local design proposals derived from the source requirements. They are not inherited protocol decisions. Original source meaning and all candidate dependencies remain attached.

A passing check means supplied data is structurally consistent. It does not prove caller identity, validate signatures, authenticate owner approval, establish entitlement, write artifacts, enforce custody, run a service or grant permission. Every example and result explicitly carries no authority and `action_authorized: false`.

## Result and evidence

[Candidate registry](candidate-registry.json) links all 16 exact identities to their schemas, examples and source concepts. [Capability result](result.json) preserves the original source record, the local contract bindings and the remaining operational blockers. [Current import set](imports.json) contains the prior 24 candidates plus this one. The new isolated store is `.local/capability-inventory-import-0012/imports.json`.

Twenty-four tests passed: one test per contract/policy rejects added fields, removed required fields and authority inflation; eight behavioral tests cover request/caller mismatch, scope and expiry, path escape, policy rejection, response correlation, failure envelopes and consistent data without authorization. The complete imported Product/Capability graph also validates.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evidence/migrations/cyberalchemy-v2-to-lab/executions/0012-governed-access-contracts -p test_contracts.py -v
```

## Remaining operational work

The KEP service-exchange Capability and ontology extension remain unadmitted. These local contract proposals need owner adoption and actual authentication, filesystem and service implementations before operational use. None of that prevents preserving the complete Capability as a candidate.

Current queue: **25 imported candidates / 20 blocked declarations**. [inventory.json](inventory.json) records exactly one transition from the previous queue. Earlier stores and source files remain unchanged.
