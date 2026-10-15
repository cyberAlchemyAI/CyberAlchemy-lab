## CAV2-D40: Challenge Contract

Status: active
Term: challenge contract
Aliases: challenge_contract, challenge response contract, contestability contract, contradiction review contract

### Normative Definition

A challenge contract is the explicit review surface attached to a
CyberAlchemy v2 node, candidate, claim, or authority artifact that states how
the object may be challenged, contradicted, validated, blocked, or routed for
owner review without silently changing its meaning or confidence.

A challenge contract must declare the valid challenge response, admissible
challenge modes, contradiction and validation links when present, owner route,
resolution gate, blocking questions, and challenge residue route. It does not
contain the object's own confidence or residue and does not introduce a third
confidence axis. Object confidence remains a sibling posture using the
`evidence_confidence` and `commitment_confidence` split governed by `CAV2-D23`.

### Formal Interpretation

An admissible challenge contract has at least:

```text
ChallengeContract =
  (challenge_response, valid_challenge_modes, contradiction_edges,
   validation_edges, owner_route, resolution_gate, blocking_questions,
   challenge_residue_route)
```

where `challenge_residue_route` says where unresolved challenge residue is
handled. The object's own confidence and residue are not part of the challenge
contract. When an object records confidence, active CyberAlchemy v2 uses
`evidence_confidence` for evidence support and `commitment_confidence` for
commitment posture.

### Operational Interpretation

Use challenge contract when a candidate ontology node, projection, definition
proposal, constitution proposal, research claim, or authority artifact needs to
say what kind of objection is valid and what happens next. A contradiction
edge may block promotion; a validation edge may increase evidence support; a
blocking question may defer the node; and unresolved challenge residue must
remain attached until an owner route closes, waives, or demotes it.

### Plain-Language Intuition

It is the object's "how to disagree with me correctly" field.

### Domain-Context Voice

In CyberAlchemy v2, challenge contract belongs on the ontology candidate node
shape before candidate concepts become load-bearing. It lets the project reuse
challenge responses, `contradicts` and `validates` edges, owner routes, gates,
and residue routing while node confidence remains outside the contract as
`evidence_confidence` and `commitment_confidence`. It is the schema-level answer
to the question: if this node is challenged, who reviews it, with which
evidence, and where does the challenge residue go?

### Boundary

Challenge contract is not a verdict, not a confidence score, not proof of
truth, not a promotion decision, and not an ontology-owned override of the
relevant owner route. It names the challenge path; owner routes and gates still
decide movement.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [../../ontology/NODE-MODEL.md](../../ontology/NODE-MODEL.md)
- [../../ontology/PACKAGE-MODEL.md](../../ontology/PACKAGE-MODEL.md)
- [../../ontology/LIFECYCLE-MODEL.md](../../ontology/LIFECYCLE-MODEL.md)
- [../imports/house_project/docs/vault/ontology-conventions.md](../imports/house_project/docs/vault/ontology-conventions.md)
- [../imports/house_project/docs/vault/premise/ontology-premises.md](../imports/house_project/docs/vault/premise/ontology-premises.md)
