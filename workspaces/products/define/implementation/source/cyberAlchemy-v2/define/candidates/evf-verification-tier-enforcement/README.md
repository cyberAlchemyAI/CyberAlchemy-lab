# EVF verification-tier enforcement candidate

Status: candidate definition. Authority effect: none.

## Problem

EVF currently uses several valid but different axes:

- TDE EVF uses L0, L1 and L2 for provider and evidence hardening;
- the Repair Assurance DAG uses L2, L3 and L4 for delivery layers; and
- Auth EVF uses S0 through S12 for verifier stages.

A caller asking for “L2 verification” can therefore name more than one contract.
Labels alone also do not guarantee that required tools, exact inputs, controls,
receipts and review actually ran.

## Candidate decision

Introduce a separate `verification_tier` axis named `V0` through `V4`. Every
EVF call must provide an exact tier, versioned enforcement profile, property,
subject, property traits and bounds. The runtime must compute the requirements
from the tier and traits, execute every applicable verifier, validate the raw
receipts, and refuse to claim the requested tier when anything is missing,
stale, substituted, conflicting or fixture-only.

Lifecycle layer and verifier stage remain separate fields:

```text
verification_tier: V0..V4
lifecycle_layer: project-owned label such as L2/L3/L4
verifier_stage: provider-owned label such as S0..S12
```

## Required result separation

The enforcement result has two independent outcomes:

1. `contract_state`: whether the requested verification contract was executed
   completely and truthfully; and
2. `property_outcome`: what the evidence says about the property.

A counterexample can therefore have `contract_state: satisfied`. Conversely,
passing tests with a missing required provider have
`contract_state: not_evaluable`; they cannot produce a verified tier.

## No silent downgrade

If V3 is requested and only V2 can be completed, EVF returns the V3 request as
`not_evaluable`. It may report V2 as an available lower contract, but it cannot
assert V2 or continue under V2 until the caller explicitly selects it.

## Candidate artifacts

- [Definition Pack](EVF-VERIFICATION-TIER-DEFINITION-PACK.v1-candidate.json)
- [Tier matrix](verification-tier-matrix.v1-candidate.json)

## Implementation boundary

This candidate does not modify EVF runtimes. A later Plan must define schemas,
profile inheritance, dispatch, verifier adapters, receipts, negative controls,
claim-envelope construction and migration of existing TDE/Auth profiles. A
separately authorized Implement route must then build and test that runtime.

## Open Questions

- Should V1 require two distinct engines or two independently authored semantic
  routes when engines share a translation source?
- Which property traits are mandatory for every caller and who approves them?
- Can an independently replayed V2 result qualify for V4 when no natural defect
  exists, or should V4 require the repair branch to have been exercised?
- How should existing TDE L0/L1/L2 labels be displayed after migration without
  rewriting historical receipts?

