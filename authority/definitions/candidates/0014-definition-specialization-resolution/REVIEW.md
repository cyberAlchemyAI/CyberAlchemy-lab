# Step 3 — Definition specialization and identity resolution

- Status: `candidate-owner-review-open`
- Authority effect: `none`

## Positive Definitions

| New Definition | Replaces borrowed primary meaning | Resolution | Example |
| --- | --- | --- | --- |
| `cal.definition.context-profile@1.0.0-candidate.1` | `cal.definition.context@1.0.0-candidate.1` | Broad meaning remains `retained-as-semantic-dependency` | profile:product-project-context/v1 permits exactly one Product anchor, an optional Project anchor, explicit source digests, a 24-hour freshness ceiling, and successor-only revision. |
| `cal.definition.capability-realization-binding@1.0.0-candidate.1` | `cal.definition.product-capability@1.0.0-candidate.1` | Broad meaning remains `retained-as-endpoint-semantic-dependency` | binding:typed-meaning-runtime/v3 associates capability:typed-meaning@v2 with implementation:ontology-runtime@2.1, records candidate adoption, and projects a read-only realizes relation. |
| `cal.definition.measurement-method@1.0.0-candidate.1` | `cal.definition.residue-measurement@1.0.0-candidate.1` | Broad meaning remains `retained-only-when-method-measures-residue` | method:residue-entropy/v2 defines how to calculate entropy over a typed residue register, including sampling window, formula, implementation digest, calibration fixture, and uncertainty rule. |
| `cal.definition.measurement-result@1.0.0-candidate.1` | `cal.definition.residue-measurement@1.0.0-candidate.1` | Broad meaning remains `retained-only-when-result-measures-residue` | result:residue-entropy:run-44 records 0.37 bits for experiment-run:44 using method:residue-entropy/v2, its raw register digest, computation receipt, and ±0.02 uncertainty. |
| `cal.definition.model-instance-binding@1.0.0-candidate.1` | `cal.definition.parent-instance-authority-separation-invariant@1.0.0-candidate.1` | Broad meaning remains `retained-as-governing-invariant` | binding:agent-profile-instance-22 binds profile:definition-curator@v3 to a local instance, inherits stop and evidence rules, permits only budget overrides, and leaves admission authority prohibited. |
| `cal.definition.ledger@1.0.0-candidate.1` | Generic Ledger was unresolved | Positive Definition | ledger:ontology-semantic-events declares append-only complete-state events ordered by cursor, while ledger:artifact-inventory permits owner-reviewed corrective successor entries; both specialize the generic Ledger contract differently. |
| `cal.definition.withdrawal-record@1.0.0-candidate.1` | Migration-only withdrawal semantics | Positive Definition | withdrawal:CAV2-D70 permanently reserves CAV2-D70, binds its last known digest and owner decision, and routes consumers to a named successor only when that successor is independently admitted. |

## Workflow overlaps

| Generic | Craft meaning | Decision |
| --- | --- | --- |
| `cal.definition.decision-checkpoint@1.0.0-candidate.1` | `craft.definition.decision-checkpoint@1.0.0-candidate.1` | Craft specializes generic; neither identity supersedes the other. |
| `cal.definition.user-decision-preference@1.0.0-candidate.1` | `craft.definition.user-decision-preference@1.0.0-candidate.1` | Craft specializes generic; neither identity supersedes the other. |
| `cal.definition.workflow-decision-profile@1.0.0-candidate.1` | `craft.definition.workflow-decision-profile@1.0.0-candidate.1` | Craft specializes generic; neither identity supersedes the other. |

## Project Identity

`cal.artifact-type.project-identity/v1` remains v1. Its identity and non-collapse contract already separate Project from Product, Goal, Method, Context, and directory placement. Artifact Type admission, effective-state resolution, external relations, and representative instances remain later gates.

## Real-like combined example

A Context Profile defines reusable anchor and freshness rules but is not a Context. A Context created under it has its own purpose and source selection. A Measurement Method defines the residue-entropy procedure; a Measurement Result records one execution and does not become a Finding. A Capability Realization Binding canonically associates one Product Capability revision with one Implementation revision without merging them. A Model Instance Binding preserves parent and instance authority lanes. Both a corrective inventory Ledger and an append-only event Ledger satisfy the generic Ledger contract using different correction policies. A Withdrawal Record permanently reserves a retired identifier. Craft workflow records use the specialized `craft.*` meanings while non-Craft workflows use the generic `cal.*` meanings. Project Identity remains v1 because its meaning has not changed.

## Decision boundary

This candidate resolves Step 3 semantic identity and specialization choices only. It does not admit the seven Definitions, rebind or admit Artifact Types, activate workflow consumers, admit Project Identity, create a Ledger carrier, withdraw any identifier, or authorize runtime behavior.
