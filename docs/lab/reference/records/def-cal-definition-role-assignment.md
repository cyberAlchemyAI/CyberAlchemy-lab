[Documentation home](../../README.md)

# Role Assignment

<a id="def-cal-definition-role-assignment"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Role Assignment

# Role Assignment

Records who holds a role, within which scope and time interval. It does not silently add team membership or authority.

**When it applies**

Create a Team with a stable identity, purpose, scope, owner route, lifecycle state, and challenge route. Add Persons through explicit Team Membership records. Attach Team Roles and Responsibilities through separately owned assignments so that membership alone never implies a role, responsibility, or permission. Preserve membership history rather than rewriting the current member list as if earlier participation never existed.

**Record formats**

[Role assignment · v1](type-cal-artifact-type-role-assignment-v1.md#type-cal-artifact-type-role-assignment-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-role-assignment-section-2"></a>

## Source explanatory wording

It records who holds a role, where, and for how long, without silently making them a team member or granting extra authority.

<a id="def-cal-definition-role-assignment-section-3"></a>

## Exact governing statement

Role Assignment is the normalized definition identified by semantic.role-assignment, owned within scope.people-teams, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D69 without silently merging it with another target.

Target-specific normative meaning:

A Role Assignment is an owner-qualified, time-bounded relation that binds one Person or Team to one Role within an exact scope and lifecycle epoch; it does not create Team Membership or authority beyond separately admitted claims.

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
- This target remains distinct from the sibling targets semantic.role, semantic.team, semantic.team-membership reconstructed from CAV2-D69; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/role-assignment/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.role-assignment@1.0.0-candidate.1

**Content fingerprint · SHA-256**

c47f2da496cdff6fe04f0424012a8bebc8e4c01b4b855769c8974df980183be1

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

[Return to Definitions](../definitions.md#catalog-definitions)
