# Ontology Lifecycle State Vocabulary

Decision: `CAL-GONLIFE-0007`

Question: `GON-OQ-001`

Selected option: `GONLIFE-1`

Status: `selected`

Decision source: explicit user selection

Decision time: `2026-09-01T16:16:19Z`

## Decision

`OntologyLifecycleState` is a closed vocabulary with exactly three values:

| Value | Meaning | Active cut | Terminal |
| --- | --- | --- | --- |
| `active` | The subject exists for ontology use at the selected cursor. | included | no |
| `retired` | The subject remains historically addressable but is unavailable for current use. | excluded | no |
| `removed` | The subject is a terminal semantic tombstone. Its canonical event history remains preserved. | excluded | yes |

`created` is an event transition, not a persistent lifecycle value. The first
accepted semantic event creates the subject and produces complete `active`
state.

`absent` is a lookup or projection result before a first subject event or when
no identity resolves. It is not stored in a subject event payload.

## Transition law

```text
absent --create--> active
active --retire--> retired
retired --reactivate--> active
active --remove--> removed
retired --remove--> removed
removed --X--> no successor under the same identity
```

A concept that must become usable after terminal removal requires a new subject
identity and explicit provenance linking it to the removed subject.

## Relation integrity

An active relation can appear in an active ontology cut only when both endpoint
nodes are `active` in that same cut.

If an endpoint becomes `retired` or `removed`, the relation cannot remain
active. Its own lifecycle event must retire or remove it, or projection must
return typed integrity residue and fail closed.

## Forbidden collapses

Lifecycle remains independent from:

- workflow or review status;
- candidate or maturity status;
- promotion verdict;
- projection state;
- evidence confidence;
- commitment confidence;
- authority kind or posture.

None of those axes changes lifecycle implicitly. An allowed semantic lifecycle
event must record the transition.

`removed` does not mean filesystem deletion or erasure of canonical events.

## Exact binding

This decision binds Decision Gate request digest
`91343bafe3c0e5d44eb989e84bc7a0a952b8d90cde0d080c8fe4e1b348caf904`
and the `GONDEF-1` definition epoch:

- `definition-pack.json`:
  `9128208f453869ccb96c381d09a8df0cdd3274a5c039751a9519ac0746af825d`
- `handled-definitions.json` selector `CAL-GON-D019`:
  `c740dc445effa1188f29883abddfcd79a6087de98f60e086738279f243b614aa`
- `schema-semantics.json`:
  `50dd47269e75c09f391272c368e3e2fceb7aa12a3aebf65b3106f3f5fea2d052`

## Effect and remaining boundary

Resolved:

- `GON-OQ-001`;
- selection of the closed ontology lifecycle vocabulary.

Still blocked:

- executable schemas and the 12 required negative fixtures;
- `G-W1 PASS`.

This decision does not modify the selected Definition Pack, authorize schema
implementation, admit DomainSpec output, establish runtime conformance, or
authorize publication, release, deployment, migration, or external effects.
