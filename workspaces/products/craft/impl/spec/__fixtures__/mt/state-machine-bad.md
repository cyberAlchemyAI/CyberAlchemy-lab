# Fixture — State Machine (invalid: no transitions → is a flat Enum)

Declared State Machine but `has_transitions=no`. Expected: **REJECTED as State Machine**.

## Concept Registry
| Concept | Type |
| --- | --- |
| PaymentKind | State Machine |

## PaymentKind
| Attribute | Value |
| --- | --- |
| has_transitions | no |
