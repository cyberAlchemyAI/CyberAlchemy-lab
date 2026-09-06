<!-- Generated from decision.json. Do not edit. -->

# Cohesive Lab ontology-system Product approval

- Decision: `CAL-ONTOLOGY-SYSTEM-PRODUCT-APPROVAL-0044`
- Gate: `G-CAL-COHESIVE-ONTOLOGY-SYSTEM-PRODUCT-APPROVAL`
- Status: `selected`
- Decided at: `2026-09-06T02:53:35Z`
- Authority effect: `product-approval-only`

## Exact approved subject

- Product: `CA2-PRODUCT-ONTOLOGY/v1`
- Candidate: `CAL-ONTOLOGY-AS-PRODUCT-CANDIDATE-0005-COHESIVE-LAB-SYSTEM`
- Candidate digest: `0aae6913d90fc836ff88d0714da695629a92cef81881f8569582eff8666dead5`
- Ontology-system digest: `977ab3235bc52b3feddc2e8c4e7103349d763ab802f5982534ac409fd1e2c8c9`
- Product-test receipt digest: `26baa86798ebdcadf68f4925c9d0ddf66bc9b1e3b6bff4ba1e7cc3d46c523c42`

## Decision source

`CLOSYS-PAPP-1 candidate=0aae6913d90fc836ff88d0714da695629a92cef81881f8569582eff8666dead5 receipt=26baa86798ebdcadf68f4925c9d0ddf66bc9b1e3b6bff4ba1e7cc3d46c523c42`

## Product approval

- State: `approved`
- Scope: The exact frozen and tested CAL-ONTOLOGY-AS-PRODUCT-CANDIDATE-0005-COHESIVE-LAB-SYSTEM bytes only.
- Tests: `9/9` cases, including `8/8` hostile probes and `2` deterministic runs
- System graph: `14` components and `15` relations
- Catalog: `20` packages and `10` review groups
- Residue: `5` typed records

## Next frontier

- Stage: `post-product-approval-cohesive-root-admission-candidate`
- Eligible: `true`
- Permitted effect: prepare and validate one exact non-effectful admission candidate
- Excluded effect: No admission occurs until the ontology-system owner selects a separately digest-bound admission option.

## Non-effects

- This decision does not mutate the frozen Product candidate, ontology-system record, tests, or receipts.
- This decision does not admit the cohesive ontology-system root.
- This decision does not bulk-admit any child ontology, package, Definition, Artifact Type, Context, source, or implementation binding.
- This decision does not select among the eleven profile-qualified domainspec-product-ontology@1 records.
- This decision does not claim that the Ontology Product is realized by the D65 runtime.
- This decision does not adopt or activate a runtime or Context Map.
- This decision does not authorize or perform migration, cutover, source retirement, or destructive action.
- This decision does not authorize publication, release, deployment, credentials, or external effects.
- This decision authorizes only preparation and validation of a separate non-effectful root-admission candidate.

## Claim ceiling

The exact frozen and tested cohesive Lab ontology-system candidate is approved as a Product increment. No cohesive root or child ontology is admitted, no runtime is adopted, and no activation, migration, cutover, publication, release, deployment, source retirement, credential, destructive action, or external effect is authorized.
