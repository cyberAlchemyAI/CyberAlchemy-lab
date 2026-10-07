<!-- GENERATED FILE: run build.py to refresh. -->

# Materialized Artifact Type candidates

These 26 packages start from the Artifact Type contracts selected by migration decision `CAL-REMAINING-83-CONTRACT-ADMISSION-0052`. Their Definition dependencies are rebound to the admitted Definition registry, and authorized owner-review refinements are identified explicitly. The packages remain candidates and have no consumer activation.

| # | Migration target | Artifact Type | Name | Domain family | Admitted Definition binding | Package | Status |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `type.intent` | `cal.artifact-type.intent/v1` | Intent | `coordination` | `cal.definition.intent@1.0.0-candidate.1` | `authority/artifact-types/intent/v1` | `candidate-refined` |
| 2 | `type.product` | `cal.artifact-type.product/v1` | Product | `product` | `cal.definition.product@1.0.0-candidate.1` | `authority/artifact-types/product/v1` | `candidate-materialized` |
| 3 | `type.product-thesis` | `cal.artifact-type.product-thesis/v1` | Product Thesis | `product` | `cal.definition.product-thesis@1.0.0-candidate.1` | `authority/artifact-types/product-thesis/v1` | `candidate-refined` |
| 4 | `type.product-capability` | `cal.artifact-type.product-capability/v1` | Product Capability | `product` | `cal.definition.product-capability@1.0.0-candidate.1` | `authority/artifact-types/product-capability/v1` | `candidate-refined` |
| 5 | `type.capability-realization-binding` | `cal.artifact-type.capability-realization-binding/v1` | Capability Realization Binding | `binding` | `cal.definition.product-capability@1.0.0-candidate.1` | `authority/artifact-types/capability-realization-binding/v1` | `candidate-refined` |
| 6 | `type.project` | `cal.artifact-type.project/v1` | Project | `coordination` | `CAV2-D60@1.0.0-candidate.1` | `authority/artifact-types/project/v1` | `candidate-materialized` |
| 7 | `type.research-inquiry` | `cal.artifact-type.research-inquiry/v1` | Research Inquiry | `knowledge-development` | `cal.definition.research-inquiry@1.0.0-candidate.1` | `authority/artifact-types/research-inquiry/v1` | `candidate-refined` |
| 8 | `type.research-run` | `cal.artifact-type.research-run/v1` | Research Run | `knowledge-development` | `cal.definition.research-run@1.0.0-candidate.1` | `authority/artifact-types/research-run/v1` | `candidate-refined` |
| 9 | `type.finding` | `cal.artifact-type.finding/v1` | Finding | `knowledge-development` | `cal.definition.finding@1.0.0-candidate.1` | `authority/artifact-types/finding/v1` | `candidate-refined` |
| 10 | `type.experiment-design` | `cal.artifact-type.experiment-design/v1` | Experiment Design | `knowledge-development` | `cal.definition.experiment-design@1.0.0-candidate.1` | `authority/artifact-types/experiment-design/v1` | `candidate-refined` |
| 11 | `type.experiment-run` | `cal.artifact-type.experiment-run/v1` | Experiment Run | `knowledge-development` | `cal.definition.experiment-run@1.0.0-candidate.1` | `authority/artifact-types/experiment-run/v1` | `candidate-refined` |
| 12 | `type.observation` | `cal.artifact-type.observation/v1` | Observation | `knowledge-development` | `cal.definition.observation@1.0.0-candidate.1` | `authority/artifact-types/observation/v1` | `candidate-refined` |
| 13 | `type.measurement-method` | `cal.artifact-type.measurement-method/v1` | Measurement Method | `knowledge-development` | `cal.definition.residue-measurement@1.0.0-candidate.1` | `authority/artifact-types/measurement-method/v1` | `candidate-refined` |
| 14 | `type.measurement-result` | `cal.artifact-type.measurement-result/v1` | Measurement Result | `knowledge-development` | `cal.definition.residue-measurement@1.0.0-candidate.1` | `authority/artifact-types/measurement-result/v1` | `candidate-refined` |
| 15 | `type.ontology` | `cal.artifact-type.ontology/v1` | Ontology | `semantic-model` | `cal.definition.ontology@1.0.0-candidate.1` | `authority/artifact-types/ontology/v1` | `candidate-refined` |
| 16 | `type.context` | `cal.artifact-type.context/v1` | Context | `context` | `cal.definition.context@1.0.0-candidate.1` | `authority/artifact-types/context/v1` | `candidate-refined` |
| 17 | `type.context-profile` | `cal.artifact-type.context-profile/v1` | Context Profile | `context` | `cal.definition.context@1.0.0-candidate.1` | `authority/artifact-types/context-profile/v1` | `candidate-refined` |
| 18 | `type.context-request` | `cal.artifact-type.context-request/v1` | Context Request | `context` | `cal.definition.context-request@1.0.0-candidate.1` | `authority/artifact-types/context-request/v1` | `candidate-refined` |
| 19 | `type.context-view` | `cal.artifact-type.context-view/v1` | Context View | `context` | `cal.definition.context-view@1.0.0-candidate.1` | `authority/artifact-types/context-view/v1` | `candidate-refined` |
| 20 | `type.model-instance-binding` | `cal.artifact-type.model-instance-binding/v1` | Model Instance Binding | `binding` | `cal.definition.parent-instance-authority-separation-invariant@1.0.0-candidate.1` | `authority/artifact-types/model-instance-binding/v1` | `candidate-refined` |
| 21 | `type.person-reference` | `cal.artifact-type.person-reference/v1` | Person Reference | `people-teams` | `cal.definition.person-reference@1.0.0-candidate.1` | `authority/artifact-types/person-reference/v1` | `candidate-refined` |
| 22 | `type.identity-claim` | `cal.artifact-type.identity-claim/v1` | Identity Claim | `people-teams` | `cal.definition.identity-claim@1.0.0-candidate.1` | `authority/artifact-types/identity-claim/v1` | `candidate-refined` |
| 23 | `type.team` | `cal.artifact-type.team/v1` | Team | `people-teams` | `cal.definition.team@1.0.0-candidate.1` | `authority/artifact-types/team/v1` | `candidate-refined` |
| 24 | `type.team-membership` | `cal.artifact-type.team-membership/v1` | Team Membership | `people-teams` | `cal.definition.team-membership@1.0.0-candidate.1` | `authority/artifact-types/team-membership/v1` | `candidate-refined` |
| 25 | `type.role` | `cal.artifact-type.role/v1` | Role | `people-teams` | `cal.definition.role@1.0.0-candidate.1` | `authority/artifact-types/role/v1` | `candidate-refined` |
| 26 | `type.role-assignment` | `cal.artifact-type.role-assignment/v1` | Role Assignment | `people-teams` | `cal.definition.role-assignment@1.0.0-candidate.1` | `authority/artifact-types/role-assignment/v1` | `candidate-refined` |

## Status boundary

Materialization proves that each selected migration contract now has a stable candidate package with a closed schema, generated projections, fixtures, exact admitted Definition bindings, and a passing validation receipt. Artifact Type admission, real instances, consumer integration, and activation require separate decisions.
