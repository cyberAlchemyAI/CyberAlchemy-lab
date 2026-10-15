# EVF verification-tier enforcement implementation plan

Status: planning candidate. Authority effect: none. Task Session excluded.

## Objective

Make every EVF invocation name and satisfy an exact verification contract. A
requested tier becomes claimable only when its inherited obligations, applicable
provider capabilities, exact bindings, controls, receipts and review gates have
all been evaluated. Missing or conflicting evidence fails closed without
rewriting a property counterexample as an execution failure.

## Fixed design decisions

1. Use `verification_tier: V0..V4`; retain project lifecycle `L*` and verifier
   stage `S*` as separate fields.
2. Require `requested_tier`, `profile_id`, `profile_digest`, `property_ref`,
   `subject_ref`, `property_traits`, bounds and effect ceiling on every call.
3. Select provider capabilities from property traits. Tool brands are profile
   bindings, not universal definitions.
4. Keep `contract_state` separate from `property_outcome`. A validly found
   counterexample may satisfy the requested verification contract.
5. Forbid voting, fixture evidence as product evidence, optimistic unknowns and
   automatic tier downgrade.
6. Preserve all historical TDE L0/L1/L2 and Auth S0-S12 artifacts unchanged.
7. Implement V0-V2 first from existing Souffle/Alloy/hardening evidence. Add V3
   trait adapters and V4 repair assurance only after the core enforcement kernel
   passes its negative controls.

## Invocation contract

```json
{
  "requested_tier": "V2",
  "enforcement_profile_ref": "...",
  "enforcement_profile_sha256": "...",
  "property_ref": "...",
  "subject_ref": "...",
  "property_traits": ["recursive-relational", "bounded-structural"],
  "bounds_ref": "...",
  "effect_ceiling": "read-only isolated verification"
}
```

The terminal result must include:

```json
{
  "requested_tier": "V2",
  "verified_tier": "V2",
  "contract_state": "satisfied",
  "property_outcome": "counterexample",
  "provider_receipts": [],
  "claim_ceiling": "...",
  "authority_effect": "none"
}
```

When V2 cannot be satisfied, `verified_tier` is `null`. An optional
`available_lower_tier` is informational and cannot be executed or asserted
without a new attributable caller selection.

## Delivery slices

| Slice | Work | Exit evidence |
| --- | --- | --- |
| S0 — schema and axis separation | Define closed request/result schemas, V0-V4 inheritance, property traits, provider capabilities and typed outcomes. | Invalid or ambiguous L/S-only requests are rejected; schema tests pass. |
| S1 — enforcement kernel V0 | Bind profile, property, subject, bounds, translations and real provider identity; execute one route and validate its receipt. | Current TDE Souffle obligation maps to V0 without changing historical evidence. |
| S2 — corroboration V1 | Require two applicable independently implemented routes and a non-voting join. | Current TDE Souffle/Alloy result maps through a new compatibility receipt; missing/disagreeing providers do not satisfy V1. |
| S3 — hardening V2 | Add freshness, drift, replay, tamper, timeout, output, denominator, oracle and execution controls. | Existing fifteen TDE controls plus the five repair-assurance control classes cannot produce degraded success. |
| S4 — trait completeness V3 | Add TLA+/TLC, Lean and subject-specific executable adapters selected only by applicable traits. | Removing an applicable capability makes V3 `not_evaluable`; irrelevant tools are not required. |
| S5 — repair assurance V4 | Bind natural counterexample, defect, repair scope, patch, retest, mutation calibration and separate replay. | Natural and seeded faults remain distinct; author/reviewer disagreement stays visible. |
| S6 — migration and independent replay | Create additive compatibility manifests for TDE and Auth, run full controls, then assign a separate technical reviewer. | Historical bytes match; fresh reviewer agrees or records conflict. |

## Enforcement order

```text
parse closed request
  -> resolve exact profile and inheritance
  -> validate property traits and required capabilities
  -> freeze property, subject, translations, tools and bounds
  -> preflight every required provider
  -> execute isolated provider routes
  -> validate raw evidence and receipts
  -> run tier-required negative controls
  -> compute non-voting comparison
  -> compute contract_state
  -> compute property_outcome independently
  -> emit bounded claim envelope or typed non-claim
```

No stage may construct `verified_tier` before all prior stages have durable,
digest-bound results.

## Negative-control matrix

| Boundary | Required failures |
| --- | --- |
| Request | missing tier; unknown tier; L2 or S12 supplied as tier; profile digest mismatch |
| Property | missing meaning owner; property/subject mismatch; undeclared trait; changed bounds |
| Provider | missing applicable provider; wrong version/hash; fixture substituted; shared route falsely labeled independent |
| Evidence | stale receipt; tampered raw output; duplicate/missing observation; cross-property replay |
| Execution | launch failure; timeout; output overflow; interruption; recovery from partial attempt |
| Join | provider disagreement; unknown; different obligation; optimistic voting |
| Downgrade | V3 request with only V2 evidence; lower tier emitted without a fresh caller decision |
| Repair | seeded mutant labeled natural; repair before counterexample; counterexample overwritten; reviewer reads mutable author evidence |

Every control must yield `invalid_request`, `not_evaluable` or
`conflicting_evidence` as appropriate. None may yield a verified tier.

## Migration rules

- TDE L0 may produce a new V0 compatibility receipt only after exact source and
  Souffle evidence verification.
- TDE L1 may produce V1 only when Souffle and Alloy receipts bind one obligation
  and the route-independence rule is satisfied.
- TDE L2 may produce V2 only after its full hardening matrix is replayed.
- Auth S0-S12 remain verifier stages. The current Auth package receives no
  retroactive V3 or V4 label; a new profile must declare its traits and satisfy
  the corresponding capability matrix.
- Repair Assurance lifecycle L2/L3/L4 labels remain unchanged and never imply a
  verification tier.

## Write and effect boundary

A future implementation may add new EVF schemas, enforcement kernel, provider
capability registry, adapters, compatibility receipts, isolated test evidence
and documentation. It must not edit historical evidence, silently install or
admit providers, contact customers, publish, release, deploy or grant product
authority. Exact tool installation and external downloads require their own
authorized scope.

## Completion criteria

- all V0-V4 schemas and inheritance checks pass;
- all applicable-capability and irrelevant-capability tests pass;
- all negative controls produce the declared non-success contract state;
- property counterexamples remain valid property outcomes;
- no silent downgrade path exists;
- compatibility mapping leaves historical hashes unchanged;
- a fresh technical reviewer reproduces the selected positive and negative
  paths; and
- the product owner receives an attributable promote, revise, narrow or stop
  decision package.

## Blockers and open questions

- Goals validation currently blocks admission of this planning candidate.
- The EVF method owner must define route independence when translations share
  semantic code.
- The Repair Assurance product owner must decide whether V4 requires a natural
  repair branch to execute or permits a truthful not-applicable branch.
- The migration owner must select exact compatibility record paths and schemas.

