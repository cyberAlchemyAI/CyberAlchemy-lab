[Documentation home](../README.md)

# Intent, product and project

<a id="purpose"></a>

04

<a id="purpose-title"></a>

## Connect the customer need to the work

 [Explore this in the system map ↑](system-map.md#system-map) 

<a id="docs-purpose-heading-2"></a>

### State the need before choosing the solution

Northstar needs a complete eligible export. An **Intent** records that problem, desired outcome or direction while the response is still being worked out. The missing-row report makes the need urgent. It has yet to establish which code change would satisfy it.

The owner chooses an export-repair project, beginning with investigation and using the accepted identifier-coverage criterion. An **Intent Resolution** records that response and its satisfaction test. We have a direction for the effort. Evidence will determine whether it succeeds.

<a id="docs-purpose-heading-3"></a>

### Keep the product and the repair effort identifiable

The customer platform is the **Product**, with a continuing promise of value for people managing and retrieving their data. The export-repair **Project** coordinates this particular effort through goals, work, decisions and evidence.

The **Incident** organizes the response to the reported failure, including accountability, communication, recovery and closure.

The platform continues beyond this repair effort. An investigation result can be saved while the incident response stays open. These are different responsibilities within the same situation, and the map shows where each record fits.

<a id="figure-purpose-to-implementation"></a>

<a id="incident-model-map-title"></a>

### One incident, different records doing different jobs

#### Intent

A declared problem or desired change, before its solution is settled.

**Restore a complete eligible export for Northstar**

#### Intent Resolution

The owner’s chosen response and satisfaction test.

**Choose an export-repair project and the accepted coverage criterion**

Value offered over time

1. #### Product

   

   The durable identity that owns a promise of value.

   **The customer platform**
2. #### Product Capability

   

   The outcome that one product must make possible.

   **Customers can obtain all required export identifiers**
3. #### Capability Realization Binding

   

   A governed association between exact capability and implementation versions.

   **The selected export-capability revision linked to service revision 7**
4. #### Implementation

   

   The technical realization to build, assess and operate.

   **Service 7 produced E12; revision 8 is a candidate change**

Work organized around the problem

1. #### Project

   

   The durable coordination identity for goals, work, decisions and evidence.

   **The Northstar export-repair effort**
2. #### Goal

   

   A desired outcome with success conditions and rules for recording achievement.

   **Required identifiers present in an assessed replacement export**
3. #### Work

   

   A bounded activity with inputs, constraints and an expected result.

   **Investigate the reported omission in E12**
4. #### Agent Assignment

   

   The binding that identifies the agent’s participation in this work.

   **Session 12 takes the investigation job, with separate delegation**

#### Incident · INC-0241

The incident coordinates the response: who is accountable, what gets communicated, how recovery is assessed and when closure is justified. Its response remains open. The repair project and investigation have their own states.

Read the two columns as responsibilities. Assignment names the job. Delegation supplies permission. The session brings that job together with selected views and temporary working memory.

Figure 03 The map pairs each general role with an illustrative record in the same incident. Reading order and grouping explain their roles; exact connections, permissions and state changes follow their own contracts.

<a id="docs-purpose-heading-4"></a>

### Connect the promised outcome to the software

Why should the platform be valuable, and to whom? The **Product Thesis** explains that. A **Product Capability** states the outcome the product needs to enable. Here, the export must contain every required identifier for the declared account, filters and snapshot.

The **Implementation** supplies a technical realization. Service revision 7 produced E12.

A **Capability Realization Binding** links an exact capability revision to exact implementation revisions, with roles and adoption posture. Revision 8 needs a successor binding revision if its selected endpoints or adoption posture change.

That link still leaves conformance, adoption, deployment and observed operation to their own records. The capability gives the repair a criterion; evidence has to show whether the service meets it.

<a id="docs-purpose-heading-5"></a>

### Turn the target into bounded work

The repair **Goal** is to assess a replacement export with all required identifiers present. A Goal records the desired outcome and the conditions for achievement. Its owner needs adequate evidence for every required success condition before recording achievement.

The omission in E12 is an investigation result. The repair goal is still ahead.

**Work** identifies a bounded effort, with its purpose, owner, participants, inputs, expected result and constraints. This Work item investigates the omission. It can produce an observation and candidate assessment while the project still needs a proven repair.

**Method** 2 supplies the identifier comparison. A **Workflow** describes ordered software Operations within or across Product Feature boundaries, with declared ownership scope. Evaluation can produce a recovery intent and plan; a separate executor invokes exact Operation bindings. Diagnosis, code changes and assessment take their own Work items and permissions.

Work · illustrative investigation record

<a id="incident-work-brief-title"></a>

#### Investigate the Northstar export omission

**Purpose**

Assess the report in INC-0241 and preserve what is established, uncertain and still to investigate.

**Owner and participant**

Customer-data service owner; the agent in session 12 has the investigation assignment.

**Inputs**

Snapshot S1, output E12 and saved run logs. The comparison uses account Northstar and filter `status = active`.

**Method**

Version 2 compares actual row identifiers under completeness definition 1.0.0.

**Expected result**

A recorded observation and evidence-bounded assessment, with a traceable proposal if a change is recommended.

**Limits and checkpoint**

The 30-minute delegation permits investigation and candidate proposals. View 3 has expired at the latest checkpoint, so work is paused pending usable information and current permission.

So far, the comparison establishes 200 missing required identifiers. We have not established the cause or recovery. Candidate revision 8 still needs assessment.

<a id="craft-in-the-lab"></a>

### Where Craft fits in this work

**Craft** is the software-design Product within the wider Lab. Its vocabulary, architecture constraints and supported construction tools can help a project working on another Product. In this case, the customer platform owns the export promise and the repair Project coordinates the effort. Craft is a possible tool for later software-change Work.

The current assignment is investigation. If the owner authorizes implementation work later, an agent could express the export criterion as a Craft **Rule**, declare retrieval responsibilities and connections, then select an architecture profile and supported implementation forms. Account, filters and snapshot stay explicit.

The code and checks would be outputs of that work. Replacement-export assessment, adoption, activation and closure would still follow their own routes. We are describing a possible next step, not an executed repair.

Craft separates several software jobs. A **Rule** evaluates a condition, a **Calculation** derives a value from supplied information, a **Query** retrieves information and an **Operation** owns a business state change.

In the capacity example, 4 requested slots against a snapshot of 5 available slots return Accept. Requests for 5 or 6 return Reject because the condition is strictly less than available capacity. Every classification leaves the snapshot at 5. Recorded local checks exercised these cases in memory and generated TypeScript, Python and Rust. A separate reservation Operation would check current capacity, reduce it to 1 and create the reservation. Rejection can leave state unchanged. Accepting repair evidence or authorizing deployment still belongs to the Lab owner’s decision route.

[Read how Craft fits into the Lab](../craft/model.md#governance), then follow its [capacity-decision example](../craft/model.md#definition). It takes a definition into a typed software model, with a separate criterion for acceptance.

### How the Lab selects relevant information

A **Coordination Context** records why information is needed and who will use it. It has exactly one product anchor, and optionally one project and one primary goal. Material changes to those anchors or purpose require a successor context identity.

The profile supplies reusable selection rules. A request states what the task needs, and a view contains the chosen information.

Meaning can differ across parts of a domain. Billing and customer-data management might use “active customer” under different rules. A **Bounded Context** establishes the local meaning. A **Context Map** records how the models relate without treating their terms as interchangeable.

A **Ledger** keeps an ordered collection under declared rules. An event history adds requirements for retaining prior entries and reconstructing state from them. Those extra requirements matter when we rely on the history to recover a project.

### Definitions and sources

[Product](../reference/records/def-cal-definition-product.md#def-cal-definition-product) · [Product Thesis](../reference/records/def-cal-definition-product-thesis.md#def-cal-definition-product-thesis) · [Product Capability](../reference/records/def-cal-definition-product-capability.md#def-cal-definition-product-capability) · [Capability Realization Binding](../reference/records/def-cal-definition-capability-realization-binding.md#def-cal-definition-capability-realization-binding) · [Project](../reference/records/def-cav2-d60.md#def-cav2-d60) · [Goal](../reference/records/def-cav2-d59.md#def-cav2-d59) · [Work](../reference/records/def-cal-definition-work.md#def-cal-definition-work) · [Coordination Context](../reference/records/def-cal-definition-coordination-context.md#def-cal-definition-coordination-context) · [Bounded Context](../reference/records/def-cal-definition-bounded-context.md#def-cal-definition-bounded-context) · [Ledger](../reference/records/def-cal-definition-ledger.md#def-cal-definition-ledger)

- [Complete CyberAlchemy Lab model](../../../authority/ontology-integration/candidates/0003-definition-complete-runtime-integration/MODEL.md)
- [Coordination Context v2 schema](../../../authority/artifact-types/coordination-context/v2/schema.json)
