<!-- GENERATED FILE: canonical data is record.json. -->

# Authority Boundary fixture

- Identity: `authority-boundary:example-001`
- Kind: `authority-boundary`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "accountable_principal_ref": "principal:lab-owner",
  "allowed_effect_kinds": [
    "definition-admission",
    "artifact-type-admission",
    "relation-kind-successor-admission"
  ],
  "authority_scope_ref": "decision-scope:governance-transaction-surface",
  "challenge_route_ref": "route:lab-governance-challenge",
  "effective_period": "until-revoked-or-superseded",
  "excluded_effect_kinds": [
    "runtime-activation",
    "external-publication",
    "deployment"
  ],
  "owner_role_ref": "role:lab-owner",
  "revocation_state": "not-revoked"
}
```

## Declared relation roles

- `source` on `relation.scopes-authority-over` with `decision-scope` `decision-scope:example-001`

## Claim ceiling

Realistic Authority Boundary example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
