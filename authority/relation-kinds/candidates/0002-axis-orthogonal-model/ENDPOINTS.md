<!-- GENERATED FILE: canonical data is model.json and endpoint-inventory.json. -->

# Relation endpoint inventory

This surface separates relation grammar from Artifact Type lifecycle. `A` means an admitted-current carrier exists, `C` means a materialized candidate carrier exists, and `R` means the relation model references the concept but no canonical root Artifact Type carrier exists.

**Closed endpoint model:** 50 named endpoint kinds and 147 exact ordered pairs = 13 admitted-current + 15 candidate-materialized + 22 referenced without a canonical carrier. Wildcards: 0.

## Complete declared connection matrix

| # | Semantic axis | Directed relation | Declared ordered endpoint pairs |
| ---: | --- | --- | --- |
| 1 | `axis.membership` | `relation.member-of` | `product-capability` [A] → `product` [A]<br>`product-thesis` [A] → `product` [A]<br>`context` [C] → `product` [A]<br>`research-inquiry` [A] → `project` [A]<br>`research-run` [A] → `project` [A]<br>`experiment-design` [C] → `project` [A]<br>`experiment-run` [C] → `project` [A]<br>`goal` [A] → `project` [A]<br>`work` [R] → `project` [A]<br>`evidence-set` [R] → `project` [A]<br>`capability-realization-binding` [A] → `project` [A]<br>`context` [C] → `project` [A]<br>`ontology-node` [R] → `ontology` [C]<br>`typed-relation` [R] → `ontology` [C]<br>`product` [A] → `product` [A]<br>`responsibility` [R] → `role` [C]<br>`person-reference` [C] → `team` [C] |
| 2 | `axis.contribution` | `relation.contributes-to` | `project` [A] → `product` [A]<br>`project` [A] → `goal` [A]<br>`research-inquiry` [A] → `goal` [A]<br>`research-run` [A] → `goal` [A]<br>`experiment-design` [C] → `goal` [A]<br>`experiment-run` [C] → `goal` [A] |
| 3 | `axis.method-dependency` | `relation.uses-method` | `research-run` [A] → `method` [A]<br>`experiment-run` [C] → `method` [A]<br>`measurement-result` [C] → `method` [A]<br>`observation` [C] → `method` [A]<br>`project` [A] → `method` [A]<br>`product` [A] → `method` [A] |
| 4 | `axis.evaluation` | `relation.evaluates` | `evaluation` [R] → `product-thesis` [A]<br>`evaluation` [R] → `product-capability` [A]<br>`evaluation` [R] → `capability-realization-binding` [A]<br>`experiment-design` [C] → `product` [A]<br>`experiment-design` [C] → `product-capability` [A]<br>`experiment-design` [C] → `capability-realization-binding` [A]<br>`experiment-design` [C] → `product-thesis` [A]<br>`experiment-run` [C] → `product` [A]<br>`experiment-run` [C] → `product-capability` [A]<br>`experiment-run` [C] → `capability-realization-binding` [A]<br>`experiment-run` [C] → `product-thesis` [A] |
| 5 | `axis.realization` | `relation.realizes` | `implementation` [R] → `product-capability` [A]<br>`experiment-run` [C] → `experiment-design` [C] |
| 6 | `axis.inquiry-engagement` | `relation.engages-inquiry` | `research-run` [A] → `research-inquiry` [A]<br>`experiment-design` [C] → `research-inquiry` [A]<br>`experiment-run` [C] → `research-inquiry` [A]<br>`finding` [C] → `research-inquiry` [A] |
| 7 | `axis.origin-lineage` | `relation.originates-from` | `definition` [A] → `source` [R]<br>`artifact-type` [A] → `source` [R]<br>`relation-kind` [R] → `source` [R]<br>`finding` [C] → `source` [R] |
| 8 | `axis.derivation` | `relation.derives-from` | `observation` [C] → `experiment-run` [C]<br>`observation` [C] → `research-run` [A]<br>`measurement-result` [C] → `experiment-run` [C]<br>`measurement-result` [C] → `research-run` [A]<br>`evidence-set` [R] → `experiment-run` [C]<br>`evidence-set` [R] → `research-run` [A]<br>`finding` [C] → `research-run` [A]<br>`finding` [C] → `evidence-set` [R]<br>`context-view` [C] → `context` [C]<br>`product-capability` [A] → `product-thesis` [A]<br>`generated-output` [R] → `source` [R] |
| 9 | `axis.evidence-polarity` | `relation.evidence-bears-on` | `evidence-set` [R] → `finding` [C]<br>`evidence-set` [R] → `identity-claim` [C]<br>`evidence-set` [R] → `authority-claim` [R]<br>`evidence-set` [R] → `hypothesis` [R]<br>`observation` [C] → `finding` [C]<br>`observation` [C] → `identity-claim` [C]<br>`observation` [C] → `authority-claim` [R]<br>`observation` [C] → `hypothesis` [R]<br>`measurement-result` [C] → `finding` [C]<br>`measurement-result` [C] → `identity-claim` [C]<br>`measurement-result` [C] → `authority-claim` [R]<br>`measurement-result` [C] → `hypothesis` [R] |
| 10 | `axis.governance-applicability` | `relation.governed-by` | `context` [C] → `policy` [R]<br>`ontology` [C] → `policy` [R]<br>`artifact-type` [A] → `constitution` [R]<br>`definition` [A] → `constitution` [R]<br>`relation-kind` [R] → `constitution` [R] |
| 11 | `axis.decision-effect` | `relation.declares-effect-on` | `decision` [R] → `definition` [A]<br>`decision` [R] → `artifact-type` [A]<br>`decision` [R] → `relation-kind` [R]<br>`decision` [R] → `product-capability` [A]<br>`decision` [R] → `capability-realization-binding` [A]<br>`decision` [R] → `governed-model` [R]<br>`decision` [R] → `effect` [R] |
| 12 | `axis.classification` | `relation.instance-of` | `implementation` [R] → `product-capability` [A]<br>`implementation` [R] → `governed-model` [R]<br>`product-capability` [A] → `product` [A]<br>`capability-instance` [A] → `product-capability` [A]<br>`capability-instance` [A] → `governed-model` [R] |
| 13 | `axis.implementation-binding` | `relation.binds-implementation` | `implementation` [R] → `ontology` [C]<br>`implementation` [R] → `schema` [R] |
| 14 | `axis.conformance` | `relation.conforms-to` | `context` [C] → `context-profile` [C]<br>`capability-instance` [A] → `governed-model` [R]<br>`capability-instance` [A] → `contract` [R] |
| 15 | `axis.contract-inheritance` | `relation.inherits-contract` | `capability-instance` [A] → `contract` [R] |
| 16 | `axis.context-framing` | `relation.frames` | `context` [C] → `bounded-context` [A]<br>`context` [C] → `product` [A]<br>`context` [C] → `project` [A]<br>`context` [C] → `goal` [A]<br>`context` [C] → `review` [R] |
| 17 | `axis.context-resolution-request` | `relation.requests-resolution-of` | `context-request` [C] → `context` [C] |
| 18 | `axis.request-fulfillment` | `relation.fulfills-request` | `context-view` [C] → `context-request` [C] |
| 19 | `axis.lifecycle-succession` | `relation.successor-of` | `definition` [A] → `definition` [A]<br>`artifact-type` [A] → `artifact-type` [A]<br>`relation-kind` [R] → `relation-kind` [R]<br>`bounded-context` [A] → `bounded-context` [A]<br>`context` [C] → `context` [C]<br>`context-profile` [C] → `context-profile` [C]<br>`context-request` [C] → `context-request` [C]<br>`context-view` [C] → `context-view` [C]<br>`product` [A] → `product` [A]<br>`product-thesis` [A] → `product-thesis` [A]<br>`product-capability` [A] → `product-capability` [A]<br>`capability-realization-binding` [A] → `capability-realization-binding` [A]<br>`project` [A] → `project` [A]<br>`research-inquiry` [A] → `research-inquiry` [A]<br>`research-run` [A] → `research-run` [A]<br>`experiment-design` [C] → `experiment-design` [C]<br>`experiment-run` [C] → `experiment-run` [C]<br>`observation` [C] → `observation` [C]<br>`measurement-result` [C] → `measurement-result` [C]<br>`finding` [C] → `finding` [C]<br>`ontology` [C] → `ontology` [C]<br>`person-reference` [C] → `person-reference` [C]<br>`identity-claim` [C] → `identity-claim` [C]<br>`team` [C] → `team` [C]<br>`role` [C] → `role` [C]<br>`role-assignment` [C] → `role-assignment` [C]<br>`capability-instance` [A] → `capability-instance` [A]<br>`governed-model` [R] → `governed-model` [R]<br>`contract` [R] → `contract` [R]<br>`schema` [R] → `schema` [R]<br>`policy` [R] → `policy` [R]<br>`constitution` [R] → `constitution` [R]<br>`method` [A] → `method` [A]<br>`goal` [A] → `goal` [A] |
| 20 | `axis.assignment` | `relation.assigned-to` | `person-reference` [C] → `role` [C]<br>`person-reference` [C] → `responsibility` [R]<br>`team` [C] → `role` [C]<br>`team` [C] → `responsibility` [R] |
| 21 | `axis.identity-assertion` | `relation.asserts-identity-of` | `person-reference` [C] → `person` [R]<br>`person-reference` [C] → `person-reference` [C]<br>`identity-claim` [C] → `person-reference` [C] |
| 22 | `axis.authority-scope` | `relation.scopes-authority-over` | `authority-claim` [R] → `role-assignment` [C]<br>`authority-claim` [R] → `decision-scope` [R] |
| 23 | `axis.semantic-contract` | `relation.carries-definition` | `artifact-type` [A] → `definition` [A] |

## Named endpoint carriers

| Endpoint kind | State | Canonical carrier | Source in relations | Target in relations | Note |
| --- | --- | --- | --- | --- | --- |
| `artifact-type` | `admitted-current` | `cal.artifact-type.artifact-type/v2`<br>`authority/artifact-types/artifact-type/v2/artifact.json` | `relation.carries-definition`, `relation.governed-by`, `relation.originates-from`, `relation.successor-of` | `relation.declares-effect-on`, `relation.successor-of` |  |
| `authority-claim` | `referenced-no-canonical-carrier` | None yet | `relation.scopes-authority-over` | `relation.evidence-bears-on` |  |
| `bounded-context` | `admitted-current` | `cal.artifact-type.bounded-context/v2`<br>`authority/artifact-types/bounded-context/v2/artifact.json` | `relation.successor-of` | `relation.frames`, `relation.successor-of` |  |
| `capability-instance` | `admitted-current` | `cal.artifact-type.capability-instance/v1`<br>`authority/artifact-types/capability-instance/v1/artifact.json` | `relation.conforms-to`, `relation.inherits-contract`, `relation.instance-of`, `relation.successor-of` | `relation.successor-of` |  |
| `capability-realization-binding` | `admitted-current` | `cal.artifact-type.capability-realization-binding/v1`<br>`authority/artifact-types/capability-realization-binding/v1/artifact.json` | `relation.member-of`, `relation.successor-of` | `relation.declares-effect-on`, `relation.evaluates`, `relation.successor-of` |  |
| `constitution` | `referenced-no-canonical-carrier` | None yet | `relation.successor-of` | `relation.governed-by`, `relation.successor-of` |  |
| `context` | `candidate-materialized` | `cal.artifact-type.context/v1`<br>`authority/artifact-types/context/v1/artifact.json` | `relation.conforms-to`, `relation.frames`, `relation.governed-by`, `relation.member-of`, `relation.successor-of` | `relation.derives-from`, `relation.requests-resolution-of`, `relation.successor-of` |  |
| `context-profile` | `candidate-materialized` | `cal.artifact-type.context-profile/v1`<br>`authority/artifact-types/context-profile/v1/artifact.json` | `relation.successor-of` | `relation.conforms-to`, `relation.successor-of` |  |
| `context-request` | `candidate-materialized` | `cal.artifact-type.context-request/v1`<br>`authority/artifact-types/context-request/v1/artifact.json` | `relation.requests-resolution-of`, `relation.successor-of` | `relation.fulfills-request`, `relation.successor-of` |  |
| `context-view` | `candidate-materialized` | `cal.artifact-type.context-view/v1`<br>`authority/artifact-types/context-view/v1/artifact.json` | `relation.derives-from`, `relation.fulfills-request`, `relation.successor-of` | `relation.successor-of` |  |
| `contract` | `referenced-no-canonical-carrier` | None yet | `relation.successor-of` | `relation.conforms-to`, `relation.inherits-contract`, `relation.successor-of` |  |
| `decision` | `referenced-no-canonical-carrier` | None yet | `relation.declares-effect-on` | — | Decision documents exist, but no canonical root Decision Artifact Type package exists. |
| `decision-scope` | `referenced-no-canonical-carrier` | None yet | — | `relation.scopes-authority-over` |  |
| `definition` | `admitted-current` | `cal.artifact-type.definition/v1`<br>`authority/artifact-types/definition/v1/candidates/0002-post-foundation-01/artifact.json` | `relation.governed-by`, `relation.originates-from`, `relation.successor-of` | `relation.carries-definition`, `relation.declares-effect-on`, `relation.successor-of` |  |
| `effect` | `referenced-no-canonical-carrier` | None yet | — | `relation.declares-effect-on` |  |
| `evaluation` | `referenced-no-canonical-carrier` | None yet | `relation.evaluates` | — |  |
| `evidence-set` | `referenced-no-canonical-carrier` | None yet | `relation.derives-from`, `relation.evidence-bears-on`, `relation.member-of` | `relation.derives-from` |  |
| `experiment-design` | `candidate-materialized` | `cal.artifact-type.experiment-design/v1`<br>`authority/artifact-types/experiment-design/v1/artifact.json` | `relation.contributes-to`, `relation.engages-inquiry`, `relation.evaluates`, `relation.member-of`, `relation.successor-of` | `relation.realizes`, `relation.successor-of` |  |
| `experiment-run` | `candidate-materialized` | `cal.artifact-type.experiment-run/v1`<br>`authority/artifact-types/experiment-run/v1/artifact.json` | `relation.contributes-to`, `relation.engages-inquiry`, `relation.evaluates`, `relation.member-of`, `relation.realizes`, `relation.successor-of`, `relation.uses-method` | `relation.derives-from`, `relation.successor-of` |  |
| `finding` | `candidate-materialized` | `cal.artifact-type.finding/v1`<br>`authority/artifact-types/finding/v1/artifact.json` | `relation.derives-from`, `relation.engages-inquiry`, `relation.originates-from`, `relation.successor-of` | `relation.evidence-bears-on`, `relation.successor-of` |  |
| `generated-output` | `referenced-no-canonical-carrier` | None yet | `relation.derives-from` | — |  |
| `goal` | `admitted-current` | `cal.artifact-type.goal/v1`<br>`authority/artifact-types/goal/v1/artifact.json` | `relation.member-of`, `relation.successor-of` | `relation.contributes-to`, `relation.frames`, `relation.successor-of` |  |
| `governed-model` | `referenced-no-canonical-carrier` | None yet | `relation.successor-of` | `relation.conforms-to`, `relation.declares-effect-on`, `relation.instance-of`, `relation.successor-of` |  |
| `hypothesis` | `referenced-no-canonical-carrier` | None yet | — | `relation.evidence-bears-on` | Product Thesis can carry hypothesis propositions, but Hypothesis is not a standalone Artifact Type. |
| `identity-claim` | `candidate-materialized` | `cal.artifact-type.identity-claim/v1`<br>`authority/artifact-types/identity-claim/v1/artifact.json` | `relation.asserts-identity-of`, `relation.successor-of` | `relation.evidence-bears-on`, `relation.successor-of` |  |
| `implementation` | `referenced-no-canonical-carrier` | None yet | `relation.binds-implementation`, `relation.instance-of`, `relation.realizes` | — |  |
| `measurement-result` | `candidate-materialized` | `cal.artifact-type.measurement-result/v1`<br>`authority/artifact-types/measurement-result/v1/artifact.json` | `relation.derives-from`, `relation.evidence-bears-on`, `relation.successor-of`, `relation.uses-method` | `relation.successor-of` |  |
| `method` | `admitted-current` | `cal.artifact-type.method-binding/v1`<br>`authority/artifact-types/method-binding/v1/artifact.json` | `relation.successor-of` | `relation.successor-of`, `relation.uses-method` | The admitted carrier is Method Binding; the relation endpoint uses the normalized semantic kind method. |
| `observation` | `candidate-materialized` | `cal.artifact-type.observation/v1`<br>`authority/artifact-types/observation/v1/artifact.json` | `relation.derives-from`, `relation.evidence-bears-on`, `relation.successor-of`, `relation.uses-method` | `relation.successor-of` |  |
| `ontology` | `candidate-materialized` | `cal.artifact-type.ontology/v1`<br>`authority/artifact-types/ontology/v1/artifact.json` | `relation.governed-by`, `relation.successor-of` | `relation.binds-implementation`, `relation.member-of`, `relation.successor-of` |  |
| `ontology-node` | `referenced-no-canonical-carrier` | None yet | `relation.member-of` | — |  |
| `person` | `referenced-no-canonical-carrier` | None yet | — | `relation.asserts-identity-of` |  |
| `person-reference` | `candidate-materialized` | `cal.artifact-type.person-reference/v1`<br>`authority/artifact-types/person-reference/v1/artifact.json` | `relation.asserts-identity-of`, `relation.assigned-to`, `relation.member-of`, `relation.successor-of` | `relation.asserts-identity-of`, `relation.successor-of` |  |
| `policy` | `referenced-no-canonical-carrier` | None yet | `relation.successor-of` | `relation.governed-by`, `relation.successor-of` |  |
| `product` | `admitted-current` | `cal.artifact-type.product-identity/v2`<br>`authority/artifact-types/product-identity/v2/artifact.json` | `relation.member-of`, `relation.successor-of`, `relation.uses-method` | `relation.contributes-to`, `relation.evaluates`, `relation.frames`, `relation.instance-of`, `relation.member-of`, `relation.successor-of` | Product Identity/v2 is the current Product identity carrier. |
| `product-capability` | `admitted-current` | `cal.artifact-type.product-capability/v1`<br>`authority/artifact-types/product-capability/v1/artifact.json` | `relation.derives-from`, `relation.instance-of`, `relation.member-of`, `relation.successor-of` | `relation.declares-effect-on`, `relation.evaluates`, `relation.instance-of`, `relation.realizes`, `relation.successor-of` |  |
| `product-thesis` | `admitted-current` | `cal.artifact-type.product-thesis/v1`<br>`authority/artifact-types/product-thesis/v1/artifact.json` | `relation.member-of`, `relation.successor-of` | `relation.derives-from`, `relation.evaluates`, `relation.successor-of` |  |
| `project` | `admitted-current` | `cal.artifact-type.project-identity/v1`<br>`authority/artifact-types/project-identity/v1/artifact.json` | `relation.contributes-to`, `relation.successor-of`, `relation.uses-method` | `relation.frames`, `relation.member-of`, `relation.successor-of` | Project Identity/v1 is the current Project identity carrier. |
| `relation-kind` | `referenced-no-canonical-carrier` | None yet | `relation.governed-by`, `relation.originates-from`, `relation.successor-of` | `relation.declares-effect-on`, `relation.successor-of` | The Relation Kind catalog is candidate-only and no Relation Kind Artifact Type carrier exists. |
| `research-inquiry` | `admitted-current` | `cal.artifact-type.research-inquiry/v1`<br>`authority/artifact-types/research-inquiry/v1/artifact.json` | `relation.contributes-to`, `relation.member-of`, `relation.successor-of` | `relation.engages-inquiry`, `relation.successor-of` |  |
| `research-run` | `admitted-current` | `cal.artifact-type.research-run/v1`<br>`authority/artifact-types/research-run/v1/artifact.json` | `relation.contributes-to`, `relation.engages-inquiry`, `relation.member-of`, `relation.successor-of`, `relation.uses-method` | `relation.derives-from`, `relation.successor-of` |  |
| `responsibility` | `referenced-no-canonical-carrier` | None yet | `relation.member-of` | `relation.assigned-to` |  |
| `review` | `referenced-no-canonical-carrier` | None yet | — | `relation.frames` |  |
| `role` | `candidate-materialized` | `cal.artifact-type.role/v1`<br>`authority/artifact-types/role/v1/artifact.json` | `relation.successor-of` | `relation.assigned-to`, `relation.member-of`, `relation.successor-of` |  |
| `role-assignment` | `candidate-materialized` | `cal.artifact-type.role-assignment/v1`<br>`authority/artifact-types/role-assignment/v1/artifact.json` | `relation.successor-of` | `relation.scopes-authority-over`, `relation.successor-of` |  |
| `schema` | `referenced-no-canonical-carrier` | None yet | `relation.successor-of` | `relation.binds-implementation`, `relation.successor-of` | Schemas exist as governed files, but no canonical root Schema Artifact Type package exists. |
| `source` | `referenced-no-canonical-carrier` | None yet | — | `relation.derives-from`, `relation.originates-from` | Source records exist in governance surfaces, but no canonical root Source Artifact Type package exists. |
| `team` | `candidate-materialized` | `cal.artifact-type.team/v1`<br>`authority/artifact-types/team/v1/artifact.json` | `relation.assigned-to`, `relation.successor-of` | `relation.member-of`, `relation.successor-of` |  |
| `typed-relation` | `referenced-no-canonical-carrier` | None yet | `relation.member-of` | — | Typed relation instances are modeled by this candidate, but no standalone Typed Relation Artifact Type exists. |
| `work` | `referenced-no-canonical-carrier` | None yet | `relation.member-of` | — |  |

## Admitted carriers without a declared connection

| Endpoint kind | Carrier | Connection status |
| --- | --- | --- |
| `intent` | `cal.artifact-type.intent/v1` | No connection. Adding one requires an explicit pair declaration. |

## Extension rule

Definition dependency: `cal.definition.typed-connection-extension-rule@1.0.0-candidate.1` (`candidate-unadmitted`).

A new connection requires an explicit ordered source_kind -> target_kind pair in the owning Relation Kind plus owner review, evidence, and validation. Registering a new endpoint kind alone creates no connection.

## Claim ceiling

This inventory reports carrier availability and the closed endpoint universe named by the candidate relation model. It does not admit missing carriers, admit Relation Kinds, validate instances, or authorize undeclared connections.
