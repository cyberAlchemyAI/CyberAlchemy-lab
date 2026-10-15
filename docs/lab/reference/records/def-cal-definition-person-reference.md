[Documentation home](../../README.md)

# Person Reference

<a id="def-cal-definition-person-reference"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Person Reference

# Person Reference

The minimum record needed to identify a person for a stated purpose, without duplicating their full identity record.

**When it applies**

Use Person when CyberAlchemy must refer to the same human across a Product, Project, Goal, Context, Team, decision, or handoff. Keep accounts, interface identities, memberships, roles, responsibilities, owner routes, and authority grants as separate records linked to the Person reference. Collect only the minimum attributes required by the named use and preserve the applicable privacy, correction, challenge, and retirement routes.

**Record formats**

[Person reference · v1](type-cal-artifact-type-person-reference-v1.md#type-cal-artifact-type-person-reference-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-person-reference-section-2"></a>

## Source explanatory wording

It is the smallest record needed to point to a person for a specific purpose.

<a id="def-cal-definition-person-reference-section-3"></a>

## Exact governing statement

Person Reference is the normalized definition identified by semantic.person-reference, owned within scope.people-teams, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D68 without silently merging it with another target.

Target-specific normative meaning:

A Person Reference is a minimal, purpose-bounded identifier or record used to refer to a Person in a governed artifact while minimizing personal data; it is a projection and never the Person itself.

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
- This target remains distinct from the sibling targets semantic.identity-claim, semantic.person reconstructed from CAV2-D68; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/person-reference/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.person-reference@1.0.0-candidate.1

**Content fingerprint · SHA-256**

752acd8587d2e5ed97d84ee67223e2fe81c2b622c10064cd0a306a2d65c43668

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

[Return to Definitions](../definitions.md#catalog-definitions)
