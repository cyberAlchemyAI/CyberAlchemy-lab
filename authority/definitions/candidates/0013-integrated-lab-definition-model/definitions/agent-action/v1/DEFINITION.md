<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Agent Action

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.agent-action`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:agent-action-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Agent Action is an immutable attributable record of one proposed, attempted, completed, rejected, or failed operation by an Agent Instance within one Session. The Action record does not prove that its claimed output, delivery, or external effect occurred.

```text
Action(x,i,s) => Active(i,s) and within(time(x),s) and InputsBound(x) and AuthorityEvidence(x); ClaimedEffect(x,e) =/=> ObservedEffect(e).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Agent Action Definition. |

### Boundary conditions

- Every Agent Action is attributed to one exact Agent Instance inside one exact active Session.
- Proposed, attempted, completed, rejected, failed, delivered, and effect-observed are distinct postures.
- An Action binds exact inputs, outputs, Tools, Methods, Implementations, Policies, authority evidence, approvals, receipts, and residue as applicable.
- An Action record proves attribution and recorded posture only; delivery, external effect, acceptance, correctness, and authority effect require separate evidence or Decisions.
- Corrections create successor records or linked assessments; they do not erase the original Action.

### Testable conditions

- Action time falls within the bound Session and Instance lifetimes.
- Every governed operation cites applicable Assignment and authority evidence.
- Completion is not accepted as delivery or observed effect without a separate receipt or observation.
- Every output retains provenance to the Action and exact Tool or Implementation versions.
- Failed or indeterminate effects preserve residue and do not silently retry.

## Plain-language voice

An Agent Action is an immutable attributable record of one proposed, attempted, completed, rejected, or failed operation by an Agent Instance within one Session. Every Agent Action is attributed to one exact Agent Instance inside one exact active Session.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Agent Action supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- action:materialize-step2 records the files written, tool invocation, exact inputs, receipt, and remaining residue.

## Applicability

An Agent Action is an immutable attributable record of one proposed, attempted, completed, rejected, or failed operation by an Agent Instance within one Session.

### Exclusions

- Every Agent Action is attributed to one exact Agent Instance inside one exact active Session.
- Proposed, attempted, completed, rejected, failed, delivered, and effect-observed are distinct postures.
- An Action binds exact inputs, outputs, Tools, Methods, Implementations, Policies, authority evidence, approvals, receipts, and residue as applicable.
- An Action record proves attribution and recorded posture only; delivery, external effect, acceptance, correctness, and authority effect require separate evidence or Decisions.
- Corrections create successor records or linked assessments; they do not erase the original Action.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- Every Agent Action is attributed to one exact Agent Instance inside one exact active Session.
- Proposed, attempted, completed, rejected, failed, delivered, and effect-observed are distinct postures.
- An Action binds exact inputs, outputs, Tools, Methods, Implementations, Policies, authority evidence, approvals, receipts, and residue as applicable.
- An Action record proves attribution and recorded posture only; delivery, external effect, acceptance, correctness, and authority effect require separate evidence or Decisions.
- Corrections create successor records or linked assessments; they do not erase the original Action.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.actor-model-review@2026-10-05 | whole-file | `cc2fec4a1f9bd7a4796d6735866b16736087e125dcaf23d7fa6abed33862ee42` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.agent-action@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0013-integrated-lab-definition-model/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- .arcanum/ontology-vault/2026-10-05-actor-agent-model-review.md
- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md
- .arcanum/ontology-vault/2026-10-06-lab-semantic-gap-audit.md

## Residue

- Definition-owner review and exact admission remain required.
- Artifact Type carrier, relation, qualifier, ontology, runtime, and consumer decisions remain separate.

## Claim ceiling

This candidate defines Agent Action for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
