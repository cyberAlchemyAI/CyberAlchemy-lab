[Documentation home](../../README.md)

# Identity Claim

<a id="def-cal-definition-identity-claim"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Identity Claim

# Identity Claim

States that a reference belongs to a person and the basis for believing it. Establishing identity does not grant a role or permission.

**When it applies**

Use Person when CyberAlchemy must refer to the same human across a Product, Project, Goal, Context, Team, decision, or handoff. Keep accounts, interface identities, memberships, roles, responsibilities, owner routes, and authority grants as separate records linked to the Person reference. Collect only the minimum attributes required by the named use and preserve the applicable privacy, correction, challenge, and retirement routes.

**Record formats**

[Identity claim · v1](type-cal-artifact-type-identity-claim-v1.md#type-cal-artifact-type-identity-claim-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-identity-claim-section-2"></a>

## Source explanatory wording

It says that a reference belongs to a person and states why that should be believed; it does not grant that person any role or permission.

<a id="def-cal-definition-identity-claim-section-3"></a>

## Exact governing statement

Identity Claim is the normalized definition identified by semantic.identity-claim, owned within scope.people-teams, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D68 without silently merging it with another target.

Target-specific normative meaning:

An Identity Claim is an attributable, challengeable assertion that a Person Reference denotes a particular Person under a declared evidence and assurance policy; the claim does not establish private attributes, roles, membership, or authority.

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
- This target remains distinct from the sibling targets semantic.person, semantic.person-reference reconstructed from CAV2-D68; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/5de86228d02b-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.identity-claim@1.0.0-candidate.1

**Content fingerprint · SHA-256**

5de86228d02bc0167b55d275dc519b9a4fc1bc2bee4f1a881d651f511892c6b1

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
