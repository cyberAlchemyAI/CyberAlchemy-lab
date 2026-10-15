[Documentation home](../../README.md)

# successor-of

<a id="rel-relation-successor-of"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / successor-of

# successor-of

The question this connection answers

Which predecessor does this successor continue or replace?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **successor-of** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** succession_effect

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** automatic-supersession, identity-equality, authority-transfer

<a id="rel-relation-successor-of-section-1"></a>

## Read one permitted pattern

[agent-action](endpoint-agent-action.md#endpoint-agent-action) **successor-of**Required: succession_effect [agent-action](endpoint-agent-action.md#endpoint-agent-action)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-action | agent-action |
| agent-assignment | agent-assignment |
| agent-capability | agent-capability |
| agent-instance | agent-instance |
| agent-profile | agent-profile |
| agent-reflection | agent-reflection |
| agent-session | agent-session |
| artifact-type | artifact-type |
| artifact-type-request | artifact-type-request |
| authority-claim | authority-claim |
| bounded-context | bounded-context |
| canonical-package-manifest | canonical-package-manifest |
| capability-instance | capability-instance |
| capability-realization-binding | capability-realization-binding |
| challenge-contract | challenge-contract |
| challenge-event | challenge-event |
| classification-assignment | classification-assignment |
| classification-scheme | classification-scheme |
| classification-value | classification-value |
| communication-preference | communication-preference |
| constitution | constitution |
| context | context |
| context-lineage-record | context-lineage-record |
| context-map | context-map |
| context-migration-manifest | context-migration-manifest |
| context-profile | context-profile |
| context-request | context-request |
| context-view | context-view |
| contract | contract |
| decision | decision |
| decision-scope | decision-scope |
| definition | definition |
| delegation | delegation |
| drift-assessment | drift-assessment |
| effect | effect |
| evaluation | evaluation |
| evidence-set | evidence-set |
| experiment-design | experiment-design |
| experiment-run | experiment-run |
| failure-assessment | failure-assessment |
| failure-control-binding | failure-control-binding |
| failure-mode | failure-mode |
| failure-occurrence | failure-occurrence |
| feedback-record | feedback-record |
| finding | finding |
| generated-output | generated-output |
| goal | goal |
| governance-event-history | governance-event-history |
| governed-model | governed-model |
| hypothesis | hypothesis |
| identity-claim | identity-claim |
| implementation | implementation |
| improvement-signal | improvement-signal |
| improvement-target | improvement-target |
| incident | incident |
| intent-resolution | intent-resolution |
| lesson-application | lesson-application |
| lesson-outcome-assessment | lesson-outcome-assessment |
| measurement-method | measurement-method |
| measurement-result | measurement-result |
| method | method |
| model-instance-binding | model-instance-binding |
| observation | observation |
| ontology | ontology |
| ontology-cut | ontology-cut |
| ontology-edge | ontology-edge |
| ontology-manifest | ontology-manifest |
| ontology-node | ontology-node |
| ontology-package | ontology-package |
| ontology-view | ontology-view |
| operational-lesson | operational-lesson |
| operational-observation | operational-observation |
| person | person |
| person-reference | person-reference |
| policy | policy |
| preference-application-assessment | preference-application-assessment |
| principal | principal |
| principal-reference | principal-reference |
| product | product |
| product-capability | product-capability |
| product-thesis | product-thesis |
| project | project |
| project-state | project-state |
| relation-kind | relation-kind |
| research-inquiry | research-inquiry |
| research-run | research-run |
| responsibility | responsibility |
| review | review |
| role | role |
| role-assignment | role-assignment |
| schema | schema |
| semantic-event-history | semantic-event-history |
| source | source |
| team | team |
| team-membership | team-membership |
| tool | tool |
| typed-relation | typed-relation |
| ubiquitous-language | ubiquitous-language |
| work | work |
| work-outcome-assessment | work-outcome-assessment |

### Exact meaning axis, effect and qualifier contract

relation.successor-of

**Meaning axis:** `axis.lifecycle-succession` — the distinct semantic question this rule owns.

Records succession; replacement occurs only when succession_effect is supersedes.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "succession_effect": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "succession_effect"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/successor-of.json)

### Contract content fingerprint

7bfc432c8be8d1cd981dc0a05e83bd6bbf6db6ede758abcb8872eaa4d7fbe60b

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
