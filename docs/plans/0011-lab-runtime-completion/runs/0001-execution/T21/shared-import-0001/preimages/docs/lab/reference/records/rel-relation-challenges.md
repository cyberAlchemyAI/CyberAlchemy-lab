[Documentation home](../../README.md)

# challenges

<a id="rel-relation-challenges"></a>

[Reference catalog](../relation-kinds.md#catalog-relations) / Exact record

# challenges

The question this connection answers

Which exact governed subject revision does this Challenge Event challenge?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **challenges** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** challenge_contract_ref, challenge_mode, challenged_version_ref

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** suspension, reversal, contradiction-proof, authority

## Read one permitted pattern

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [agent-action](endpoint-agent-action.md#endpoint-agent-action)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| challenge-event | agent-action |
| challenge-event | agent-assignment |
| challenge-event | agent-capability |
| challenge-event | agent-instance |
| challenge-event | agent-profile |
| challenge-event | agent-reflection |
| challenge-event | agent-session |
| challenge-event | artifact-type |
| challenge-event | artifact-type-request |
| challenge-event | authority-claim |
| challenge-event | bounded-context |
| challenge-event | canonical-package-manifest |
| challenge-event | capability-instance |
| challenge-event | capability-realization-binding |
| challenge-event | challenge-contract |
| challenge-event | challenge-event |
| challenge-event | classification-assignment |
| challenge-event | classification-scheme |
| challenge-event | classification-value |
| challenge-event | communication-preference |
| challenge-event | constitution |
| challenge-event | context |
| challenge-event | context-lineage-record |
| challenge-event | context-map |
| challenge-event | context-migration-manifest |
| challenge-event | context-profile |
| challenge-event | context-request |
| challenge-event | context-view |
| challenge-event | contract |
| challenge-event | decision |
| challenge-event | decision-scope |
| challenge-event | definition |
| challenge-event | delegation |
| challenge-event | drift-assessment |
| challenge-event | effect |
| challenge-event | evaluation |
| challenge-event | evidence-set |
| challenge-event | experiment-design |
| challenge-event | experiment-run |
| challenge-event | failure-assessment |
| challenge-event | failure-control-binding |
| challenge-event | failure-mode |
| challenge-event | failure-occurrence |
| challenge-event | feedback-record |
| challenge-event | finding |
| challenge-event | generated-output |
| challenge-event | goal |
| challenge-event | governance-event-history |
| challenge-event | governed-model |
| challenge-event | hypothesis |
| challenge-event | identity-claim |
| challenge-event | implementation |
| challenge-event | improvement-signal |
| challenge-event | improvement-target |
| challenge-event | incident |
| challenge-event | intent-resolution |
| challenge-event | lesson-application |
| challenge-event | lesson-outcome-assessment |
| challenge-event | measurement-method |
| challenge-event | measurement-result |
| challenge-event | method |
| challenge-event | model-instance-binding |
| challenge-event | observation |
| challenge-event | ontology |
| challenge-event | ontology-cut |
| challenge-event | ontology-edge |
| challenge-event | ontology-manifest |
| challenge-event | ontology-node |
| challenge-event | ontology-package |
| challenge-event | ontology-view |
| challenge-event | operational-lesson |
| challenge-event | operational-observation |
| challenge-event | person |
| challenge-event | person-reference |
| challenge-event | policy |
| challenge-event | preference-application-assessment |
| challenge-event | principal |
| challenge-event | principal-reference |
| challenge-event | product |
| challenge-event | product-capability |
| challenge-event | product-thesis |
| challenge-event | project |
| challenge-event | project-state |
| challenge-event | relation-kind |
| challenge-event | research-inquiry |
| challenge-event | research-run |
| challenge-event | responsibility |
| challenge-event | review |
| challenge-event | role |
| challenge-event | role-assignment |
| challenge-event | schema |
| challenge-event | semantic-event-history |
| challenge-event | source |
| challenge-event | team |
| challenge-event | team-membership |
| challenge-event | tool |
| challenge-event | typed-relation |
| challenge-event | ubiquitous-language |
| challenge-event | work |
| challenge-event | work-outcome-assessment |

### Exact meaning axis, effect and qualifier contract

relation.challenges

**Meaning axis:** `axis.contestability-target` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "challenge_contract_ref": {
      "minLength": 1,
      "type": "string"
    },
    "challenge_mode": {
      "minLength": 1,
      "type": "string"
    },
    "challenged_version_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "challenge_contract_ref",
    "challenge_mode",
    "challenged_version_ref"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/challenges.json)

### Contract content fingerprint

8425ae79bfbf45b7e8733cccfea2256ccaa79637323d23f979f692540897cec0

SHA-256 identifies the captured contents, not truth or permission.

[Return to this catalog](../relation-kinds.md#catalog-relations)
