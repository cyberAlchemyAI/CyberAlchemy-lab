<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Person

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.person`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.people-teams`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Person is the normalized definition identified by semantic.person, owned within scope.people-teams, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D68 without silently merging it with another target.

Target-specific normative meaning:

A Person is one human individual whose identity remains distinct from accounts, references, claims, roles, memberships, permissions, sessions, and machine-readable records associated with that individual.

Bound source-semantic basis:

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

```text
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
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.person | Stable normalized identity for Person. |
| CAV2-D68 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- A Person is not a user account, authentication subject, credential, contact,
employee record, customer record, legal identity assertion, profile, role,
permission, authority envelope, owner route, agent, model, session, or Team.
This definition does not establish identity verification, employment status,
consent, access rights, organizational hierarchy, or a right to process
personal data. A reference to a Person creates no authority effect.
- This target remains distinct from the sibling targets semantic.identity-claim, semantic.person-reference reconstructed from CAV2-D68; shared source lineage does not merge their identities or validation purposes.

### Testable conditions

- The candidate identity remains cal.definition.person.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

A person is the human being, not their account, role, or database record.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Person is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

Inside CyberAlchemy v2, a Person may be a Human Participant, Work Owner,
reviewer, researcher, or member of one or more Teams. Those are ways the Person
participates. They do not replace the Person's identity and do not silently
grant authority. The People and Teams product owns the first business model
that connects these meanings while keeping sensitive personal data outside the
initial ontology.

### Examples

- Resolve semantic.person by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Person.

## Applicability

Use Person when CyberAlchemy must refer to the same human across a Product,
Project, Goal, Context, Team, decision, or handoff. Keep accounts, interface
identities, memberships, roles, responsibilities, owner routes, and authority
grants as separate records linked to the Person reference. Collect only the
minimum attributes required by the named use and preserve the applicable
privacy, correction, challenge, and retirement routes.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- A Person is not a user account, authentication subject, credential, contact,
employee record, customer record, legal identity assertion, profile, role,
permission, authority envelope, owner route, agent, model, session, or Team.
This definition does not establish identity verification, employment status,
consent, access rights, organizational hierarchy, or a right to process
personal data. A reference to a Person creates no authority effect.
- This target remains distinct from the sibling targets semantic.identity-claim, semantic.person-reference reconstructed from CAV2-D68; shared source lineage does not merge their identities or validation purposes.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D68 | ## CAV2-D68: Person | `4d23e94e91ce2c4d626536b760e8b0cf71174f3b48196585e363d066e543f9b3` | `candidate-unadmitted` |

## Primary consumers

None declared.

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.person@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.person | cyberalchemy-v2:CAV2-D68 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-person/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
