[Documentation home](../../README.md)

# Role

<a id="def-cal-definition-role"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Role

A named position and its responsibilities, separately from the person or team occupying it.

**When it applies**

Create a Team with a stable identity, purpose, scope, owner route, lifecycle state, and challenge route. Add Persons through explicit Team Membership records. Attach Team Roles and Responsibilities through separately owned assignments so that membership alone never implies a role, responsibility, or permission. Preserve membership history rather than rewriting the current member list as if earlier participation never existed.

**Record formats**

[Role · v1](type-cal-artifact-type-role-v1.md#type-cal-artifact-type-role-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A role describes a position and its expectations before saying who holds it.

## Exact governing statement

Role is the normalized definition identified by semantic.role, owned within scope.people-teams, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D69 without silently merging it with another target.

Target-specific normative meaning:

A Role is a reusable, scope-bounded position describing expected responsibilities and eligible authority relationships independently of any Person, Team Membership, or current assignment.

Bound source-semantic basis:

A Team is a durable, owner-qualified collective identity through which Persons coordinate toward one declared purpose and scope. Its identity, lifecycle, membership, roles, responsibilities, and authority relationships are explicit and remain separate.

A Team is not merely the current set of its members. Membership changes do not silently create a different Team while its identity, purpose, scope, and owner boundary remain stable. An active Team has at least one current Person membership. A proposed Team may exist before its first membership so its purpose and owner can be reviewed without inventing members.

````
```text
Team(t) => CollectiveIdentity(t)
purpose(t) != empty
owner_route(t) != empty

active(t) => exists p, m:
  Person(p)
  and TeamMembership(m)
  and binds(m, p, t)
  and current(m)

members(t, time_1) != members(t, time_2) =/=> t_at_time_1 != t_at_time_2
holds(team_or_person, role) =/=> authorized_for(team_or_person, action)
owns_responsibility(team_or_person, r) =/=> authority_grant(r)
```

Here `t` is the Team identity, `p` is a Person, and `m` is an independently
lifecycle-managed membership relation. Team membership, role assignment,
responsibility ownership, and authority are related but non-equivalent facts.
````

- A Team is not a Product, Project, Goal, organization, company, department, mailing list, chat channel, access group, permission group, role, owner route, authority envelope, workflow, or an unqualified collection of accounts. This definition does not create employment, reporting lines, permissions, organizational authority, or an implementation. A passing Team validator does not prove that the Team exists outside the modeled context.
- This target remains distinct from the sibling targets semantic.role-assignment, semantic.team, semantic.team-membership reconstructed from CAV2-D69; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/role/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.role@1.0.0-candidate.1

**Content fingerprint · SHA-256**

d9315a8d2aea99af0933a9dc80dc09c418dcbc5ed2a334f246ebfdbfebf3db2b

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Create a Team with a stable identity, purpose, scope, owner route, lifecycle\nstate, and challenge route. Add Persons through explicit Team Membership\nrecords. Attach Team Roles and Responsibilities through separately owned\nassignments so that membership alone never implies a role, responsibility, or\npermission. Preserve membership history rather than rewriting the current\nmember list as if earlier participation never existed.",
  "authority_scope_ref": "scope.people-teams",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
