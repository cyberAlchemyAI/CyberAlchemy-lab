[Documentation home](../../README.md)

# Person

<a id="def-cal-definition-person"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Person

A human being, separately identified from accounts, roles and records describing them.

**When it applies**

Use Person when CyberAlchemy must refer to the same human across a Product, Project, Goal, Context, Team, decision, or handoff. Keep accounts, interface identities, memberships, roles, responsibilities, owner routes, and authority grants as separate records linked to the Person reference. Collect only the minimum attributes required by the named use and preserve the applicable privacy, correction, challenge, and retirement routes.

**Record formats**

[Person · v1](type-cal-artifact-type-person-v1.md#type-cal-artifact-type-person-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A person is the human being, not their account, role, or database record.

## Exact governing statement

Person is the normalized definition identified by semantic.person, owned within scope.people-teams, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D68 without silently merging it with another target.

Target-specific normative meaning:

A Person is one human individual whose identity remains distinct from accounts, references, claims, roles, memberships, permissions, sessions, and machine-readable records associated with that individual.

Bound source-semantic basis:

A Person is one human individual whose identity may be referenced by CyberAlchemy products, Projects, Contexts, Teams, responsibilities, decisions, and evidence without reducing that human to an account, role, permission, session, or machine-readable record.

Person identity remains distinct from every participation relationship. A Person may join or leave Teams, hold different roles, own different work, use multiple accounts, or have no digital account while remaining the same Person. Any stored record is a bounded reference or projection of the Person, not the Person itself. CyberAlchemy must minimize personal data and must not infer private attributes merely because a Person is referenced.

````
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
````

- A Person is not a user account, authentication subject, credential, contact, employee record, customer record, legal identity assertion, profile, role, permission, authority envelope, owner route, agent, model, session, or Team. This definition does not establish identity verification, employment status, consent, access rights, organizational hierarchy, or a right to process personal data. A reference to a Person creates no authority effect.
- This target remains distinct from the sibling targets semantic.identity-claim, semantic.person-reference reconstructed from CAV2-D68; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/person/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.person@1.0.0-candidate.1

**Content fingerprint · SHA-256**

670c5a04cd9ff403190c868281073a9c21d86b33a6009c3940b1309997c952db

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use Person when CyberAlchemy must refer to the same human across a Product,\nProject, Goal, Context, Team, decision, or handoff. Keep accounts, interface\nidentities, memberships, roles, responsibilities, owner routes, and authority\ngrants as separate records linked to the Person reference. Collect only the\nminimum attributes required by the named use and preserve the applicable\nprivacy, correction, challenge, and retirement routes.",
  "authority_scope_ref": "scope.people-teams",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
