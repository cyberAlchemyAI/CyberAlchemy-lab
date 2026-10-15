[Documentation home](../README.md)

# Operational learning

<a id="learning"></a>

07

<a id="learning-title"></a>

## Turn experience into a lesson you can examine

 [Explore this in the system map ↑](system-map.md#system-map) 

<a id="docs-learning-heading-2"></a>

### Keep the result and the hypothesis distinct

The investigation also gives us material for learning. An **Operational **Observation**** records missing identifiers, while an **Agent Reflection** proposes examining batch boundaries under the snapshot conditions. The omission is established. Its location and cause still need evidence. Research and Experiment Runs use the separate Observation record kind.

<a id="docs-learning-heading-3"></a>

### State when the advice applies

An **Operational Lesson** turns experience into candidate advice. It needs evidence, applicability, exclusions and a predicted benefit. It also needs a **falsifier**: an observable result that would contradict the prediction.

For the next learning example, consider a separate hypothetical export whose data changes between requests. An agent proposes checking adjacent batches. This candidate lesson explicitly excludes fixed snapshots such as S1.

Back in Northstar’s investigation, a later agent could record deliberate non-use. The candidate would stay in Project State, while the S1 investigation still needs a causal test and repair evidence. Saving advice grants neither policy standing nor permission.

<a id="figure-learning-loop"></a>

<a id="learning-record-title"></a>

### 01 Record what happened

 First episode

1. Work

   

   #### Investigate the reported omission

   

   Inspect Northstar’s saved export and source snapshot.
2. Operational Observation

   

   #### Required rows are missing

   

   Save the output and comparison evidence.
3. Reflection

   

   #### Inspect adjacent batches

   

   Record this interpretation for investigation.

<a id="learning-proposal-title"></a>

### 02 Propose a lesson

Operational Lesson · proposed

#### Compare adjacent batches

**Evidence**

Recorded failed run and row comparison.

**Applies when**

The dataset can change between successive batch requests.

**Exclusions**

Fixed-data exports with a different integrity contract, and failures unrelated to batch retrieval.

**Predicted benefit**

Detect missing rows before delivery.

**What would contradict it**

A later export passes this check but still delivers data with required rows missing.

<a id="learning-later-title"></a>

### 03 Examine later use

 Later episode

1. Lesson Application

   

   #### Record what was used

   

   Name the lesson version used in this run, or record why it was deliberately not used.
2. Lesson Outcome Assessment

   

   #### Compare prediction with result

   

   Did the check detect missing rows before delivery? Record the evidence and its limits.

The result may support or contradict the prediction, or leave it uncertain under these conditions.

Figure 07 Saving a lesson, showing it to an agent, using it and demonstrating benefit are separate facts. Changes to policies, profiles or code require their own authorization.

<a id="docs-learning-heading-4"></a>

### Separate the failure from its explanation

### Failure Mode · a possible pattern

For example, changing row order between requests could cause rows to be skipped.

### Failure Occurrence · one episode

This particular export has missing rows. Recording it does not yet establish the cause.

### Failure Assessment · the examination

Investigate the pattern, cause, impact and recovery, while recording what remains uncertain.

**Classification** organizes failures and lessons under a declared scheme, such as affected system part and observed impact. A category leaves cause to investigation. An **Incident** organizes a response when needed. A **Failure Control Binding** associates a measure with prevention, detection, containment, recovery or compensation.

<a id="docs-learning-heading-5"></a>

### Test the cause within the incident’s scope

A **Research Inquiry** might ask whether batch retrieval omits required identifiers even from a fixed snapshot. An **Experiment Design** could hold S1, Northstar and `status = active` fixed while varying batch boundaries, with declared comparisons, measurements and controls. An **Experiment Run** would record an execution.

The same run can evaluate a product or capability and address a research question, under its declared connections.

That work could assess revision 8 against the same completeness criterion. Its findings would stay within the tested conditions. Conformance, adoption, activation, recovery and closure then follow their own requirements. The project goal needs evidence and recorded achievement too.

**Why later use matters**A later agent can see a lesson without using it, or use it without demonstrating benefit. A Lesson Application records actual use or deliberate non-use. A Lesson Outcome Assessment compares the predicted benefit with the observed result.

### Definitions and sources

[Research Inquiry](../reference/records/def-cal-definition-research-inquiry.md#def-cal-definition-research-inquiry) · [Experiment Design](../reference/records/def-cal-definition-experiment-design.md#def-cal-definition-experiment-design) · [Experiment Run](../reference/records/def-cal-definition-experiment-run.md#def-cal-definition-experiment-run) · [Failure Mode](../reference/records/def-cal-definition-failure-mode.md#def-cal-definition-failure-mode) · [Failure Occurrence](../reference/records/def-cal-definition-failure-occurrence.md#def-cal-definition-failure-occurrence) · [Failure Assessment](../reference/records/def-cal-definition-failure-assessment.md#def-cal-definition-failure-assessment) · [Incident](../reference/records/def-cal-definition-incident.md#def-cal-definition-incident) · [Classification](../reference/records/def-cal-definition-classification.md#def-cal-definition-classification) · [Operational Learning Cycle](../reference/records/def-cal-definition-operational-learning-cycle.md#def-cal-definition-operational-learning-cycle)

- [Integrated Lab model record](../../../authority/ontology-integration/candidates/0003-definition-complete-runtime-integration/integrated-model.json)
