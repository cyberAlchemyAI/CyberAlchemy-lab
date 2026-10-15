<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Team Membership

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.team-membership`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.people-teams`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Team Membership is the normalized definition identified by semantic.team-membership, owned within scope.people-teams, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D69 without silently merging it with another target.

Target-specific normative meaning:

A Team Membership is a time-bounded, attributable relation connecting one Person to one Team with an explicit lifecycle state; it does not by itself assign a Role, Responsibility, or Authority.

Bound source-semantic basis:

A Team is a durable, owner-qualified collective identity through which Persons
coordinate toward one declared purpose and scope. Its identity, lifecycle,
membership, roles, responsibilities, and authority relationships are explicit
and remain separate.

A Team is not merely the current set of its members. Membership changes do not
silently create a different Team while its identity, purpose, scope, and owner
boundary remain stable. An active Team has at least one current Person
membership. A proposed Team may exist before its first membership so its
purpose and owner can be reviewed without inventing members.

```text
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
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.team-membership | Stable normalized identity for Team Membership. |
| CAV2-D69 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- A Team is not a Product, Project, Goal, organization, company, department,
mailing list, chat channel, access group, permission group, role, owner route,
authority envelope, workflow, or an unqualified collection of accounts. This
definition does not create employment, reporting lines, permissions,
organizational authority, or an implementation. A passing Team validator does
not prove that the Team exists outside the modeled context.
- This target remains distinct from the sibling targets semantic.role, semantic.role-assignment, semantic.team reconstructed from CAV2-D69; shared source lineage does not merge their identities or validation purposes.

### Testable conditions

- The candidate identity remains cal.definition.team-membership.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

Membership records that a person belongs to a team for a period, without assuming what job or power they have.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Team Membership is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

Inside CyberAlchemy v2, a Team can coordinate Projects, Goals, definitions,
research, reviews, or product responsibilities. A Team may be named as an owner
route only when the corresponding ownership record says so. Team membership
alone does not make every member an owner or decision authority. The People and
Teams product owns the first candidate business ontology for these relations.

### Examples

- Resolve semantic.team-membership by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Team Membership.

## Applicability

Create a Team with a stable identity, purpose, scope, owner route, lifecycle
state, and challenge route. Add Persons through explicit Team Membership
records. Attach Team Roles and Responsibilities through separately owned
assignments so that membership alone never implies a role, responsibility, or
permission. Preserve membership history rather than rewriting the current
member list as if earlier participation never existed.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- A Team is not a Product, Project, Goal, organization, company, department,
mailing list, chat channel, access group, permission group, role, owner route,
authority envelope, workflow, or an unqualified collection of accounts. This
definition does not create employment, reporting lines, permissions,
organizational authority, or an implementation. A passing Team validator does
not prove that the Team exists outside the modeled context.
- This target remains distinct from the sibling targets semantic.role, semantic.role-assignment, semantic.team reconstructed from CAV2-D69; shared source lineage does not merge their identities or validation purposes.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D69 | ## CAV2-D69: Team | `96ef06b646205295cd9110341831d4297ebe9e3856fc91972045ca76dc25adf9` | `candidate-unadmitted` |

## Primary consumers

None declared.

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.team-membership@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.team-membership | cyberalchemy-v2:CAV2-D69 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-team-membership/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
