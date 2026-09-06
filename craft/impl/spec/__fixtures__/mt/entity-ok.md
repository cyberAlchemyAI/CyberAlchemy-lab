# Fixture — Entity (valid)

Positive fixture for the Entity meta-type criterion (`entity.schema.yml`). Expected: **PASS**.

## Concept Registry
| Concept | Type |
| --- | --- |
| PaymentTransaction | Entity |

## PaymentTransaction
An identity-bearing, lifecycle-tracked domain object.

| Field | Type | Required | Identity | Description |
| --- | --- | --- | --- | --- |
| id | UUID | yes | yes | unique transaction identity |
| amount | Money | yes |  | charged amount |
| status | PaymentStatus | yes |  | lifecycle state |
