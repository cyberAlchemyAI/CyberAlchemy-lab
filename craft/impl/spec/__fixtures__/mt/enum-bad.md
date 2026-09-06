# Fixture — Enum (invalid: field table, not a value list)

Negative fixture: declared **Enum** but modeled as a typed field table (no `Value` column).
Expected: **REJECTED as Enum**.

## Concept Registry
| Concept | Type |
| --- | --- |
| Status | Enum |

## Status
| Field | Type | Required | Identity | Description |
| --- | --- | --- | --- | --- |
| code | String | yes |  | status code |
| label | String | yes |  | display label |
