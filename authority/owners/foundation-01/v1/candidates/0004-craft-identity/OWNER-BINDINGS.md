<!-- GENERATED FILE: edit owner-bindings.json and run build.py. -->

# Craft Identity Owner Bindings

> Candidate only; these bindings are not active.

- Preserved role: `craft-product-owner` -> `person:<vrondelli>`

## Proposed separate assignments

| Role | Principal | Scope |
| --- | --- | --- |
| `craft-project-owner` | `person:<vrondelli>` | Craft Project identity, purpose, scope, goals, evidence coordination, and lifecycle decisions; excludes Product meaning, Method meaning, Definition admission, identity-graph membership, implementation, publication, and deployment. |
| `craft-method-owner` | `person:<vrondelli>` | Binding and applying the admitted Craft Method within an exact Product or Project scope; excludes changing Method Definition meaning, Product or Project ownership, execution authority, conformance, publication, and deployment. |
| `craft-goal-owner` | `person:<vrondelli>` | Craft Goal outcome, rationale, success conditions, evidence requirements, and lifecycle decision; excludes Project coordination, Product or Method meaning, execution authority, and treating validation as achievement. |
| `identity-graph-owner` | `person:<vrondelli>` | Exact typed relation kind, endpoints, membership, and graph consistency; excludes endpoint meaning or admission, ownership inference, context inference, implementation, publication, and deployment. |

## Separation rule

A shared principal does not merge roles. Each assignment retains an independent scope, decision record, evidence obligation, and claim ceiling; no owner, identity, relation, lifecycle, or authority field is inferred from another.

## Claim ceiling

This candidate preserves the admitted Craft Product owner and proposes four additional independently scoped bindings. It does not activate any role or admit any artifact.
