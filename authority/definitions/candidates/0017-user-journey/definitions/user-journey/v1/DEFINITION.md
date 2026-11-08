<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# User Journey

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.user-journey`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:lab-user-journey-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A User Journey is a contextual account of an actor pursuing a desired outcome through interactions with a Product, including relevant decisions, handoffs, and possible outcomes. The actor may be a person, an agent, or collaborating people and agents.

### Notation

No notation is required.

### Boundary conditions

- The primary actor, starting situation, desired outcome, and Product reference are explicit.
- Proposed interactions are distinguishable from observed execution.
- Alternative outcomes and relevant handoffs remain visible.

### Testable conditions

- The account identifies who is trying to achieve which outcome in which starting situation.
- The sequence relates interactions and decisions to the actor's outcome.
- Permission, semantic admission, and observed success are not inferred from the account.

## Plain-language voice

A journey explains what someone or an agent is trying to accomplish with a product, what they encounter, and where the interaction can lead.

## Domain-context voice

Workspace: `project:cyberalchemy-v2-to-lab-migration`

The Lab's proposed project-lifecycle journeys cover creation, resumed work, definition changes, team onboarding, agent delegation, and recovery. These are design proposals, not observed usability results.

### Examples

- A founder creates a project, accepts its founding declaration, and starts the first Work.
- An agent resumes selected Work using the project's pinned context and prepares a candidate.
- After an uncertain response, an operator inspects the original operation before retrying.

## Applicability

Product design accounts of a human, agent, or collaborating actors pursuing a desired outcome through a product.

### Exclusions

- An executable workflow or permission grant.
- A record proving that an interaction occurred.
- A Product identity, capability, implementation, or admission decision.

## Boundaries

- A journey describes pursuit of an outcome; an executable Workflow requires its own contract.
- An Agent appearing in a journey receives no permission from that inclusion.
- A proposed successful outcome is not evidence that the Product works.
- The journey does not merge Product, Project, Work, or actor identities.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.product@1.0.0-candidate.1 | whole-json | `19c6b3bdb5e4c8515837d40c2b0a98b0fecb6edc3698aab359fa2a0d64d9a1cd` | `admitted` |

## Primary consumers

- product:cyberalchemy-lab
- define:lab-integration-user-journey

## Lookup and drift

- Index: `authority/definitions/candidates/0017-user-journey/registry.json` / `cal.definition.user-journey`
- Drift owner: `role:definition-owner`
- Audit: `define/development/lab-integration/v1/REPORT.md`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- define/development/lab-integration/v1/CONTEXT.md

## Residue

- semantic-owner-review-required
- journey-format-review-required
- human-product-usefulness-evidence-not-collected
- canonical-definition-admission-not-performed

## Claim ceiling

Agent-assisted candidate authored for the requested Define/Lab integration test. Structural/native local-store checks do not supply canonical Lab admission, independent semantic-fidelity acceptance, or observed product usefulness.
