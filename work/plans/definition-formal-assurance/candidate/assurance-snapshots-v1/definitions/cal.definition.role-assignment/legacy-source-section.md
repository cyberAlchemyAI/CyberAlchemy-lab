## CAV2-D69: Team

Status: active
Term: team
Aliases: purpose-bound team
Promoted: 2026-08-31 by explicit owner direction to make Team a first-class CyberAlchemy v2 concept; definition authority only

### Normative Definition

A Team is a durable, owner-qualified collective identity through which Persons
coordinate toward one declared purpose and scope. Its identity, lifecycle,
membership, roles, responsibilities, and authority relationships are explicit
and remain separate.

A Team is not merely the current set of its members. Membership changes do not
silently create a different Team while its identity, purpose, scope, and owner
boundary remain stable. An active Team has at least one current Person
membership. A proposed Team may exist before its first membership so its
purpose and owner can be reviewed without inventing members.

### Formal Interpretation

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

### Operational Interpretation

Create a Team with a stable identity, purpose, scope, owner route, lifecycle
state, and challenge route. Add Persons through explicit Team Membership
records. Attach Team Roles and Responsibilities through separately owned
assignments so that membership alone never implies a role, responsibility, or
permission. Preserve membership history rather than rewriting the current
member list as if earlier participation never existed.

### Plain-Language Intuition

A Team is a named group working toward a purpose. The group stays recognizable
even when its members change.

### Domain-Context Voice

Inside CyberAlchemy v2, a Team can coordinate Projects, Goals, definitions,
research, reviews, or product responsibilities. A Team may be named as an owner
route only when the corresponding ownership record says so. Team membership
alone does not make every member an owner or decision authority. The People and
Teams product owns the first candidate business ontology for these relations.

### Boundary

A Team is not a Product, Project, Goal, organization, company, department,
mailing list, chat channel, access group, permission group, role, owner route,
authority envelope, workflow, or an unqualified collection of accounts. This
definition does not create employment, reporting lines, permissions,
organizational authority, or an implementation. A passing Team validator does
not prove that the Team exists outside the modeled context.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [../../people-and-teams/README.md](../../people-and-teams/README.md)
- [../../people-and-teams/definitions.json](../../people-and-teams/definitions.json)
- [../../people-and-teams/nodes.json](../../people-and-teams/nodes.json)
