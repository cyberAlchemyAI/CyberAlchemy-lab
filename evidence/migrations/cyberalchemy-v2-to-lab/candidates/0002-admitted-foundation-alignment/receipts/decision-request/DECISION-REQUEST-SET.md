<!-- GENERATED FILE: canonical data is decision-request-set.json. -->

# CyberAlchemy-v2 to Lab Migration Decision Request Set

One interaction presents four ordered, independently governed decisions.

## 1. product-approval

- Request: `CAL-MIGRATION-0002-DR1-PRODUCT-APPROVAL`
- Owner: `role:cyberalchemy-lab-product-owner`
- Effect: approve exact tested migration product only
- Depends on: `none`

## 2. definition-admission

- Request: `CAL-MIGRATION-0002-DR2-DEFINITION-ADMISSION`
- Owner: `role:definition-owner`
- Effect: admit exact Repository Migration Manifest Definition and synchronized registry postimage
- Depends on: `CAL-MIGRATION-0002-DR1-PRODUCT-APPROVAL`

## 3. artifact-type-admission

- Request: `CAL-MIGRATION-0002-DR3-ARTIFACT-TYPE-ADMISSION`
- Owner: `role:artifact-type-owner`
- Effect: admit exact Repository Migration Manifest/v1 Artifact Type contract
- Depends on: `CAL-MIGRATION-0002-DR1-PRODUCT-APPROVAL, CAL-MIGRATION-0002-DR2-DEFINITION-ADMISSION`

## 4. migration-execution-authorization

- Request: `CAL-MIGRATION-0002-DR4-EXECUTION-AUTHORIZATION`
- Owner: `role:repository-migration-owner`
- Effect: authorize exact additive copy allowlist with no overwrite, source mutation, deletion, commit, push, publication, release, or deployment
- Depends on: `CAL-MIGRATION-0002-DR1-PRODUCT-APPROVAL, CAL-MIGRATION-0002-DR2-DEFINITION-ADMISSION, CAL-MIGRATION-0002-DR3-ARTIFACT-TYPE-ADMISSION`

## Exact command

```text
APPROVE-CYBERALCHEMY-V2-TO-LAB-MIGRATION-V2 set=8ecca74843474ce22cf513809b944f954d670c5f3d278c7f0a4f6d7c880a0bea manifest=98ae401dcc161eebc938ff46cdf2ce9b38f46ee839ad34b9eddb7e4f58637bb8 receipt=33d5855778018749d564b58926695581e2cc332e47f4cc79c6105d4df5ffa9f9 outcomes=DR1:approve,DR2:approve,DR3:approve,DR4:approve
```

## Claim ceiling

This request set presents four decisions once but grants none. Every outcome must be explicit and independently recorded before any effect.
