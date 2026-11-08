# Worked examples

Design examples only. The selected source specimen remains an executed local synthetic fixture, not a production incident or admitted shared criterion. The exact original example remains in the [reviewed Pack](../../development/m1-preparation-preview/v1/reviews/consolidated-model/v2/incident-pack.json).

## 1. Investigate INC-1042 without creating a shared Definition

**Intent:** investigate reported missing export identifiers. **Goal:** make the required meanings and evidence boundaries explicit for the investigator and reviewer.

| Declared concept | Handling | Why |
| --- | --- | --- |
| Incident | Reuse exact current admitted Incident meaning | Accountability/investigation context; no closure effect |
| Investigation Work | Reuse exact current Work meaning with task context | Task ID is context metadata; do not invent a Work parameter contract |
| Export identifier completeness | Propose embedded working meaning | No applicable admitted criterion selected in this example |
| Account exclusivity | Open | The completeness criterion does not establish that extra/foreign records are absent |

Working meaning:

> For fixed source snapshot S, account A, filters F and saved extraction E, identifier completeness holds when every identifier required by S/A/F appears in E.

It declares parameters S/A/F/E. The selected exclusions retain field accuracy, duplicate multiplicity, extra/foreign IDs, live-source consistency, root cause, repair permission and incident closure as separate questions.

### Pack contents

```text
pack:INC-1042-investigation @ revision1
  working_meanings[0]
    working:export-identifier-completeness @ revision1
    standing: working-proposal
    parameters: S:string, A:string, F:object, E:string; all required

  applications[0]
    application:INC-1042-coverage @ revision1
    meaning: exact working meaning above
    bindings: S=S-1042, A=Northstar, F={status:active}, E=E-1042
    provenance: exact saved snapshot and extraction selectors/digests

  assessments[0] (only if supplied by a separate recorded producer)
    subject: exact application revision1 and its input digests
    method/evidence/execution: exact captured synthetic fixture receipt
    reported: required12,000; present11,800; missing200; FAIL
    validation posture: verified only within the recorded synthetic scope

  gaps
    account exclusivity unresolved; blocks full export conformance/closure

  materialization_selection: []
```

**Visible result:** one Pack and generated reading view, ready for bounded meaning/evidence inspection. No new standalone Definition, incident closure, owner assignment or permission to extract/repair is inferred. The empty materialization array is a normal successful outcome.

Define does not execute the displayed assessment. It imports the producer's already recorded exact result and verifies its bindings/limits. If only the numbers and `FAIL` are supplied, execution/profile evidence remains unverified; the Pack cannot claim a completed governed Evaluation.

## 2. Retry without rewriting the original failure

A separate Work/producer generates saved extraction `E-1042-retry`. Define receives that exact evidence and the new assessment record.

```text
Pack revision2 (predecessor revision1)
  retained original application1 + assessment1: missing200 → FAIL
  application revision2: same working meaning, E=E-1042-retry
  assessment revision2: required12,000; present12,000; missing0 → PASS
  exclusivity question: still open
  materialization_selection: []
```

Changing the extraction/input epoch changes the application revision. The meaning remains exact and unchanged. A genuinely established empty required population would satisfy this presence criterion; an unknown population is an applicability/evidence gap, never an assumed empty set. Range/identifier correctness belongs to the separate fixture Method evidence and its controls.

## 3. Select the criterion for reusable materialization

The human explicitly selects the exact local meaning for a declared shared scope and purpose, with an owner route and a proposed new identity or exact successor choice.

The materializer then prepares a full Definition/v2:

- Stable proposed identity/version and explicitly declared authority scope.
- Normative scientific/formal statement, notation, applicability and exclusions.
- Non-normative plain-language and domain-context voices.
- Exact source/selector/standing, consumers, drift route, evidence and residue.
- Field lineage and generated `DEFINITION.md` under the exact selected generator.
- Required interpretation/non-collapse/consistency/consumer/profile evidence or explicit blockers.

Task values `Northstar`, `S-1042` and `E-1042` stay in the Pack's application. They do not become the shared criterion's general parameter values. A missing source, owner, full voice or semantic evidence does not get fabricated to make the candidate appear admission-ready.

The review adapter prepares the exact target and separate applicable owner requests through existing Lab change/review interfaces. The candidate remains unadmitted until actual qualified owner effects and application occur.

## 4. Later apply an admitted version

Only after the separate actual admission exists, a subsequent task can choose `reuse` or `specialize/application` under that exact admitted criterion and its qualified parameter contract. It binds its own account/filter/snapshot/extraction in its own Pack. No shared Definition copy is created for that task.

If the next task needs a tolerance of100missing records, that is a changed criterion unless the selected meaning already declares such a parameter. Adding `tolerance:100` to an undeclared contract is rejected. The user must prepare an explicit meaning-change proposal/successor through its own route.

## 5. Durable project knowledge and the next agent

The human may select the Pack as a retained Work result. The host retains exact package bytes and prepares existing Source/Evidence Set/Work records with their separate scopes and permissions. This records where the task knowledge/evidence lives; it does not admit the local criterion or turn its assessment into a universal fact.

The old Session closes and short memory expires. A new authorized Session reconstructs the selected Work and exact retained Pack from Project State and Context/Ontology Views. A missing retained body or stale source context becomes a visible gap. There is no hidden persistent machine-agent memory.

## 6. Same mechanism beyond the incident

For a sales qualification task, the Pack binds values to an already selected qualification meaning and retains a separately produced assessment. If the task introduces a different definition of a qualified lead, it records a working meaning rather than hiding the change as parameter values. The same Pack/materialization/owner boundaries apply; this design adds no domain-specific execution engine.
