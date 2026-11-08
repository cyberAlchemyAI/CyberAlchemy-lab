# Experience design package

Status: candidate design for an invited mixed-developer pilot. This package is a review surface, not a deployed product, approved brand, observed analytics stream or accessibility certification.

| Artifact | Role |
| --- | --- |
| [Research and evidence](RESEARCH.md) | Primary-source design constraints and testable claims. |
| [Brand identity](BRAND.md) and [design system handoff](SYSTEM.md) | Voice, visual direction, token usage and component behavior. |
| [Role journeys](FLOWS.md) | Participant, reviewer, researcher and support transitions and recovery. |
| [Source register](source.json) and [55 records](index.json) | One brand identity, one design system, four role flows, twelve screens, ten components and 27 event specifications. Each row has a source-bound candidate carrier instance. |
| [Tokens](tokens.json) | Candidate DTCG-style visual tokens. |
| [Measurement plan](MEASUREMENT-PLAN.md) | Event-to-metric and research boundary, missingness and privacy controls. |
| [Validation contract](VALIDATION.md) | Browser fixtures and human-study residue before release. |
| [Prototype](prototype.html) | Illustrative participant view for design review, with no capture or telemetry. |

The six meanings live in [definitions.json](../model/definitions.json) and individual [Definition/v1 candidates](../model/definition-records/index.json). The six candidate Artifact Type Requests live under [carriers](../model/carriers/README.md). The Lab [Experiment Design/v1](../model/lab-records/experiment-design-e08.json) remains the study carrier; a future event occurrence belongs to the operational event ledger, not to an Event Specification record.

## Decision and version route

1. Product and research owners review promise, claims, vocabulary and comprehension tasks. A name or logo requires separate selection and rights review.
2. UX and accessibility reviewers review screen/component states against the relevant policies and failure protocol. The timer, recording, blur and upload states are especially consequential.
3. Privacy/security owners approve event purposes, fields, retention, vendors and permissions before any emitter or third-party analytics is enabled. Optional research reuse is separately gated.
4. Register E08 targets, tasks, denominators, sample and variant assignment before users see a variant. Use synthetic fixtures to test browser behavior, then permissioned user research to test comprehension, burden and trust.
5. Version the exact changed record, token source, screen and event schema together. Preserve previous versions and report deviations. No design record itself can authorize participant collection or hiring use.

## Main relationship rules

- `Brand Identity → Design System → UI Component → Interface Screen → Experience Flow` describes expression and interaction. It does not make a visual style an assessment method.
- `Interface Screen → Analytics Event Specification → Session Event occurrence → Product Success Metric` keeps an intended event, a logged occurrence and a derived aggregate separate.
- Every participant screen links to purpose, access and recovery rules where relevant. Staff screens additionally use role-specific permissions. Event collection follows the policy decision, not the presence of an event specification.
- [Participant Metrics](../software/PARTICIPANT-METRICS.md) govern personal feedback. [Product Success Metrics](../model/PRODUCT-SUCCESS-METRICS.md) govern aggregate product questions. Neither is inferred from a page view alone.
