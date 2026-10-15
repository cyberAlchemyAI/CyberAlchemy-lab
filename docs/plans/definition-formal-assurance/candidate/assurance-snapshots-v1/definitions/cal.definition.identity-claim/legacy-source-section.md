## CAV2-D68: Person

Status: active
Term: person
Aliases: human individual
Promoted: 2026-08-31 by explicit owner direction to make Person a first-class CyberAlchemy v2 concept; definition authority only

### Normative Definition

A Person is one human individual whose identity may be referenced by
CyberAlchemy products, Projects, Contexts, Teams, responsibilities, decisions,
and evidence without reducing that human to an account, role, permission,
session, or machine-readable record.

Person identity remains distinct from every participation relationship. A
Person may join or leave Teams, hold different roles, own different work, use
multiple accounts, or have no digital account while remaining the same Person.
Any stored record is a bounded reference or projection of the Person, not the
Person itself. CyberAlchemy must minimize personal data and must not infer
private attributes merely because a Person is referenced.

### Formal Interpretation

```text
Person(p) => HumanIndividual(p)

represents(account, p) =/=> account = p
holds(p, role) =/=> p = role
member_of(p, team) requires exists membership
owns(p, artifact_or_decision) =/=> authorized_for(p, action)
observed(record_about_p) =/=> record_about_p = p

change(team_memberships(p), roles(p), accounts(p))
  =/=> successor_person_identity_required
```

Here `p` is a human individual. `represents`, `holds`, `member_of`, and `owns`
are relationships whose records and lifecycle remain independently owned. The
non-implications prevent identity, participation, ownership, and authority from
collapsing into one another.

### Operational Interpretation

Use Person when CyberAlchemy must refer to the same human across a Product,
Project, Goal, Context, Team, decision, or handoff. Keep accounts, interface
identities, memberships, roles, responsibilities, owner routes, and authority
grants as separate records linked to the Person reference. Collect only the
minimum attributes required by the named use and preserve the applicable
privacy, correction, challenge, and retirement routes.

### Plain-Language Intuition

A Person is the human, not their login, job title, permission, or database row.

### Domain-Context Voice

Inside CyberAlchemy v2, a Person may be a Human Participant, Work Owner,
reviewer, researcher, or member of one or more Teams. Those are ways the Person
participates. They do not replace the Person's identity and do not silently
grant authority. The People and Teams product owns the first business model
that connects these meanings while keeping sensitive personal data outside the
initial ontology.

### Boundary

A Person is not a user account, authentication subject, credential, contact,
employee record, customer record, legal identity assertion, profile, role,
permission, authority envelope, owner route, agent, model, session, or Team.
This definition does not establish identity verification, employment status,
consent, access rights, organizational hierarchy, or a right to process
personal data. A reference to a Person creates no authority effect.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [../../people-and-teams/README.md](../../people-and-teams/README.md)
- [../../people-and-teams/definitions.json](../../people-and-teams/definitions.json)
- [../../people-and-teams/nodes.json](../../people-and-teams/nodes.json)
