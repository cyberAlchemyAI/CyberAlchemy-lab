# Craft article review — v0.14

This pass covers positioning, argument progression, technical fidelity of the explanations, problem–solution connections, agentic engineering realism, example continuity, maintainability, accessibility, repetition and voice. Claim boundaries and research quality were excluded at the user's request. Existing source material and status qualifications were retained.

The modeling → failure causes → solutions structure and the full worked example are retained. This record identifies the passages changed and the editorial reason.

## 1 — Explain the model as a design reference

**Before:** A software model makes the system's meanings and responsibilities explicit: which concepts exist, what behavior they have, which states matter and how responsibilities connect. These choices guide implementation and provide a shared reference for later changes.

**Revision:** A software model makes the system's meanings and responsibilities explicit: which concepts exist, what behavior they have, which states matter and how responsibilities connect. For example, it can distinguish deciding whether a request is acceptable from changing state to fulfill that request. Those responsibilities can use the same information while having different consequences.

**Reason:** Ground modeling in responsibilities before introducing compiler terminology.

## 1 — Connect the two business examples

**Before:** ## 2. Why design breaks down during implementation

**Revision:** These examples show two jobs a model performs. It gives business states a precise meaning, and it states how responsibilities may interact. Together, those choices shape when the software may act and where the behavior belongs.

**Reason:** End the modeling section with a synthesis that leads into the failure causes.

## 2 — Name the assumption failure

**Before:** These examples expose different design obligations: which component may access another, what state a business process is in, and what that state permits. When those obligations change without being made explicit, the consequences can appear as ordinary bugs: an order is fulfilled too early, a retry repeats an effect, or a change in one component breaks behavior elsewhere. The visible failure may be a wrong result or a failing test. Understanding it requires tracing the assumptions, responsibilities and dependencies behind that symptom.

**Revision:** The difficulty appears when an assumption is preserved in conversation but lost during implementation, or when code changes an obligation without making that change explicit. An order is fulfilled too early. A retry repeats an effect. A change in one component breaks behavior elsewhere.

**Reason:** Explain the failure mechanism instead of repeating the examples summary.

## 2 — Separate handoff loss from incomplete execution

**Before:** ### Context loss and incomplete work

**Revision:** ### Design context is lost between sessions

**Reason:** Give context loss its own cause heading.

## 2 — Introduce omissions as a separate cause

**Before:** An agent can also understand the requirement and still leave the work incomplete.

**Revision:** ### Required work never reaches the finished result

**Reason:** Distinguish understanding a requirement from completing its implementation.

## 2 — Make omission observable

**Before:** A required action can be present in the context without receiving enough attention to reach the finished result. The code that exists may look coherent; the missing piece becomes visible only when someone checks the full requirement or exercises the neglected path.

**Revision:** Mentioning a required action in the task does not ensure that it reaches the finished result. The code that exists may look coherent; the missing piece becomes visible only when someone compares the result with the full requirement or exercises the neglected path.

**Reason:** Center the observable missing work and make the review action concrete.

## 2 — Separate local repair from accumulated debt

**Before:** ### Local fixes and accumulating design debt

**Revision:** ### A local repair changes the intended behavior

**Reason:** Explain the local repair mechanism without using guard before its definition.

## 2 — Give architectural brittleness its own heading

**Before:** Another failure mode is **brittleness through accumulated design shortcuts**.

**Revision:** ### Shortcuts accumulate into architectural brittleness

**Reason:** Preserve the depth while separating an accumulating failure from a single repair.

## 2 — Make the debt argument concrete and balanced

**Before:** This creates technical debt: future changes require more coordination, investigation and repair because earlier design decisions made the structure harder to change. A capacity rule copied into several callers must be updated in several places. A function combining decision, persistence and retry behavior becomes difficult to modify without affecting all three. Over time, a routine feature can require extensive reconstruction of the system, and repeated regressions can make further development impractical without redesign.

**Revision:** This creates technical debt: future changes require more coordination, investigation and repair because earlier design decisions made the structure harder to change. A capacity rule copied into several callers must be updated in several places. A function combining decision, persistence and retry behavior becomes difficult to modify without affecting all three.

**Reason:** Show the accumulating cost while preserving room for coherent simple solutions.

## 3 — Connect each solution mechanism to a failure

**Before:** The solution section described model roles and then repeated the division of responsibility in prose.

**Revision:** “The work is divided across design, construction and observation” now introduces a table linking each responsibility to the failure it helps address.

**Reason:** Replace repeated product summaries with an explicit mechanism map, define contract and profile, and establish the walkthrough.

## 4 — Make the capacity request tangible

**Before:** Consider an agent asked to implement a capacity decision for a compute service. The business wants some capacity to remain after a request of that size. The decision must reject requests that would consume all available capacity, and it must leave state unchanged.

**Revision:** Consider an agent asked to implement a capacity decision for a compute service. A caller supplies a request identifier, the number of units requested and the number available. The business wants some capacity to remain after a request of that size. The decision must reject requests that would consume all available capacity, and it must leave state unchanged.

**Reason:** Introduce a concrete input before the formal definition and carry its fields into the model.

## 4 — Explain snapshot and decision meaning

**Before:** We also need to define what the decision means. Acceptance means that the request satisfies this condition in the supplied snapshot. It does not mean that capacity has been reserved or a job has started.

**Revision:** A **snapshot** is the supplied record of the request and capacity quantities used for this decision. Acceptance means that the request satisfies the condition in that record. It does not mean that capacity has been reserved or a job has started.

**Reason:** Define snapshot at first use in the surrounding explanation and preserve the meaning of acceptance.

## 5 — Explain role formation in familiar language

**Before:** Each concept occupies a defined role, called a **meta-type**. The role states what kind of responsibility the concept has and which formation conditions it must satisfy. An Entity needs a declared identity. A Rule needs an evaluable condition. An Operation needs an explicit account of its behavior.

**Revision:** Each concept occupies a defined role, called a **meta-type**. The role states what responsibility the concept has and what must be declared for that role to be valid. An Entity needs an identity. A Rule needs a condition that can be evaluated. An Operation needs an explicit account of its behavior.

**Reason:** Explain typed and formation concepts with checks the example can show.

## 5 — Make the closed result set explicit

**Before:** | Capacity decision | Enum | Define the closed alternatives: Accept and Reject. |

**Revision:** | Capacity decision | Enum | Define the complete set of result alternatives: Accept and Reject. |

**Reason:** Explain closed alternatives without requiring prior Enum vocabulary.

## 5 — Connect the fields to the concrete request

**Before:** The snapshot declares a request identifier and two unsigned integer quantities. The model marks the request identifier as its identity; that responsibility is not inferred from a field's name.

**Revision:** The snapshot declares a request identifier and two unsigned integer quantities—whole numbers that cannot be negative. In request `R-104`, these quantities are 4 requested units and 5 available units. The model marks the request identifier as its identity; that responsibility is not inferred from a field's name.

**Reason:** Connect the formal field types and identity to the request introduced in section 4.

## 5 — Explain reads, writes, effects and guard

**Before:** The Operation declares its input, output, governing Rule, reads, writes and effects. A readable summary is:

**Revision:** The Operation declares its input, output, governing Rule, reads, writes and effects. **Reads** name the information it uses; **writes** name the state it changes; **external effects** describe interactions beyond that state boundary. The governing Rule acts as a **guard**: its result determines which declared outcome the Operation returns.

**Reason:** Define the behavioral vocabulary before the model summary.

## 5 — Distinguish rejection from an exception

**Before:** The failure path is part of the design before code is constructed. The agent declares Reject as the guard-failure result, and the supported translation produces that branch alongside Accept. Similarly, empty write and effect sets make the absence of reservation explicit. A reviewer can compare these declarations with the requirement and notice a missing responsibility before relying on the implementation.

**Revision:** The guard-failure path is part of the design before code is constructed. Here, failure means that the capacity condition is false; the result is the normal Reject alternative. The agent declares that result, and the supported translation produces its branch alongside Accept.

**Reason:** Clarify the example’s failure semantics and give the reviewer concrete obligations.

## 6 — Separate model references from relationships

**Before:** The first identifies the Rule that gates the Operation. The second identifies the Entity the Operation reads. Its input and output types are separate contract references, each with their own checks.

**Revision:** The first identifies the Rule that gates the Operation. The second identifies the Entity the Operation reads. The input and output declarations separately refer to the snapshot and decision types. Naming a type in a contract and declaring a relationship in the graph each contribute their own checks.

**Reason:** Make the distinction between input/output references and typed relationships easier to follow.

## 6 — Define architectural boundary in the example

**Before:** This is already an architectural boundary: the decision can be examined independently of a database connection, job scheduler or delivery mechanism. Adding one of those responsibilities changes the design and needs an explicit contract.

**Revision:** This establishes a boundary around one responsibility. A caller provides the record, the decision evaluates it, and the caller receives Accept or Reject. The decision can be examined independently of a database connection, job scheduler or delivery mechanism. Adding one of those responsibilities changes the design and needs an explicit contract.

**Reason:** Show what crosses the boundary and what stays inside it.

## 6 — Connect architectural composition to code choices

**Before:** The domain model does not choose every architectural detail automatically. We must also select a profile and implementation forms. Together, they specify applicable structure, permitted dependencies and how the modeled concepts are represented. A relationship can have valid endpoint roles yet be forbidden across a particular feature or layer boundary.

**Revision:** The domain model does not choose every architectural detail automatically. We must also select an architecture profile and implementation forms. Together, they specify how responsibilities are organized, which dependencies are permitted and how the concepts are represented in code.

**Reason:** Explain composition through responsibilities and boundaries before introducing extension rules.

## 7 — Explain realization as a construction selection

**Before:** Craft calls a selected implementation form a **realization**. It connects a supported role to an exact representation under a language and architecture profile.

**Revision:** Craft calls a selected implementation form a **realization**. It specifies how a supported role is represented under a language and architecture profile. For the capacity Operation, that selection determines the source-code form that implements its typed contract.

**Reason:** Connect the new term immediately to the ongoing example.

## 7 — Explain the code-to-model bindings

**Before:** The compilation approach resolves these choices, checks the model and translates supported concepts into source-code artifacts.

**Revision:** The compiler resolves these choices, checks the model and translates supported concepts into source-code artifacts. A source-code artifact is a produced file or other recorded output. Bindings record the model and implementation selections associated with that output, allowing later inspection to trace it back to the design.

**Reason:** Explain artifact and binding in plain language before the compilation diagram.

## 7 — Make source-code compilation clear

**Before:** The compiler constructs the Rule and its use together. The comparison, guard call, Accept branch and Reject branch follow from the selected contracts. Once those obligations are declared, constructing them follows explicit translation rules; the agent need not remember to handwrite each piece separately.

**Revision:** Craft's compilation produces source code in the selected language. In this example, the strict comparison becomes the body of `within_capacity`, and the Operation becomes a function that calls it and returns one of the two declared alternatives.

**Reason:** Clarify the output and connect each function to its modeled responsibility.

## 8 — Follow the order of construction and evaluation

**Before:** “Before construction” → “During execution” → “After construction.”

**Revision:** “Check the model” → “Check the artifacts” → “Examine behavior” → “Account for completion.”

**Reason:** Present model validation, artifact inspection, behavior and completion in order while retaining the existing detailed explanations and qualifications.

## 9 — Separate a meaning change from a new responsibility

**Before:** Suppose the business later permits requests that consume all available capacity.

**Revision:** The original decision now gives us a reference for two different kinds of change: revising what acceptance means and adding behavior after acceptance.

**Reason:** Introduce the two kinds of evolution before their consequences.

## 9 — Identify the new responsibility

**Before:** A different request—“reserve capacity when the decision succeeds”—has wider consequences.

**Revision:** ### Add a state-changing responsibility

**Reason:** Give the reservation extension a separate place in the argument.

## 9 — Demonstrate why the snapshot decision is not a reservation

**Before:** This is how a model guides evolution. It exposes which meaning changed, which responsibility was added, which declared dependencies follow and which evidence needs refreshing.

**Revision:** The distinction matters under concurrency. Two requests can each ask for 4 units while using snapshots that show 5 available. Each satisfies the original comparison, but reserving both would require 8 units. The reservation design needs to specify how the capacity check and state change remain consistent when requests overlap.

**Reason:** Use the existing quantities to explain the additional consistency responsibility concretely.

## 9 — Give identity and repeated effects their own transition

**Before:** Retries are another everyday example.

**Revision:** ### Preserve identity and behavior across attempts

**Reason:** Guide the reader from state ownership to retry behavior without an abrupt topic change.

## 10 — Apply the earlier mechanisms instead of explaining them again

**Before:** Three subsections separately reintroduced requirements, construction and observation.

**Revision:** “Trace the missing work” applies those mechanisms together to the unfinished helper, before handing the work to the next session.

**Reason:** Keep the partial-work scenario and all its mechanisms while consolidating repeated model/compiler/verification introductions.

## 10 — Keep the narrative chronological

**Before:** ### Keep successive changes from accumulating design debt

**Revision:** ### Leave an accurate handoff

**Reason:** First leave a record of the unfinished initial decision, then extend the service through later requests.

## 10 — Connect successive requests to the original boundary

**Before:** Now extend the capacity service over several requests. The following is a design sketch of possible evolution; reservation and retry behavior are additional responsibilities beyond the compiled decision shown earlier.

**Revision:** Once the decision's responsibilities are explicit, consider a sequence of requests to extend the service. Each request adds something the earlier design must now accommodate. The following is a design sketch of possible evolution; reservation and retry behavior are additional responsibilities beyond the compiled decision shown earlier.

**Reason:** Show why the next feature tests earlier architectural choices.

## 10 — Clarify how the next agent inherits the debt

**Before:** Each patch could satisfy a narrow example. Together, they make changes increasingly expensive: the next agent must find every copied rule, infer which flags matter and determine where an effect has already happened. New fixes can then add another branch or copy, continuing the cycle.

**Revision:** Each patch could satisfy a narrow example. Together, they make changes increasingly expensive: the next agent must find every copied rule, infer which flags matter and determine where an effect has already happened. Changing the acceptance boundary now requires coordinating several implementations instead of revising one declared responsibility. New fixes can then add another branch or copy, continuing the cycle.

**Reason:** Connect debt directly to the cost of the next named requirement.

## 10 — Give reservation, entry points and retries concrete ownership

**Before:** - **Decision:** keep the existing snapshot-based decision explicit, including its strict Rule and absence of writes or effects.
- **Reservation:** give the state change an owning Operation, declared reads and writes, guard, failure continuation and a consistency contract appropriate to shared capacity.
- **Entry points:** connect each modeled entry point to the intended responsibility. Review external callers for bypasses or copied rules.
- **Orchestration and retries:** declare which Operations are coordinated, what identifies a repeated request and which effects may repeat. Workflow orchestration and Operation-owned state changes retain separate contracts.

**Revision:** - **Decision:** keep the existing snapshot-based decision explicit, including its strict Rule and absence of writes or effects. Its result retains the meaning established earlier.
- **Reservation:** give the capacity mutation an owning Operation. Declare its reads, writes, guard, failure continuation and consistency contract for shared capacity.
- **Entry points:** connect the modeled API and worker paths to their intended responsibilities. Review external callers for bypasses or copied rules.
- **Orchestration and retries:** state which Operations are coordinated, what identifies a repeated request and which effects may repeat. Workflow orchestration and Operation-owned state changes retain separate contracts.

**Reason:** Tie each design response to a concrete step in the accumulating-debt example.

## 10 — Distinguish a copied expression from a modeled Rule

**Before:** A copied Rule in an unmodeled worker is outside that artifact comparison,

**Revision:** A copied comparison in a handwritten worker outside the model is outside that artifact comparison,

**Reason:** Preserve the distinction between a typed Rule concept and code that repeats its predicate.

## 10 — Connect the summary back to the causes section

**Before:** ### What this changes for agentic engineering

**Revision:** ### Return to the failure causes

**Reason:** Use the summary as a synthesis of the argument instead of restarting the product explanation.

## 10 — Explain durable project context and ontology views

**Before:** Within the Lab, the machine agent is ephemeral. Its session can have short-term memory. Durable design knowledge belongs to project state, with context and ontology views exposing the relevant sources and relationships. The compiler's inputs, completed work, observed results and remaining obligations belong in that durable state, so a later agent can continue from an explicit account of the project.

**Revision:** Within the Lab, the machine agent is ephemeral. Its session can have short-term memory. Durable design knowledge belongs to project state. Context views expose information relevant to the task; ontology views expose the concepts and relationships recorded in that state. The compiler's inputs, completed work, observed results and remaining obligations belong in that durable state, so a later agent can continue from an explicit account of the project.

**Reason:** Explain the two views and connect session continuity to persistent project records.

## 11 — Explain implementation conformance

**Before:** CyberAlchemy Lab organizes knowledge and work. Craft contributes a specialized model for software design, architectural composition, code compilation and implementation conformance.

**Revision:** CyberAlchemy Lab organizes knowledge and work. Craft contributes a specialized model for software design, architectural composition, code compilation and implementation conformance—the comparison of an observed implementation with its selected design.

**Reason:** Introduce the Lab through the artifacts the reader has already encountered.

## 11 — Explain the connection between the two models

**Before:** The Lab and Craft retain distinct contracts. A business definition can inform a software Rule through an explicit binding. A Lab artifact relationship and a Craft software relationship each keep their own endpoint and scope constraints. Ontology views make these connections navigable through their underlying records.

**Revision:** The Lab and Craft retain distinct contracts. An explicit binding can connect the business definition of “within capacity” to the software Rule that expresses its predicate. The Rule's `enforces` connection to Decide capacity belongs to Craft's software model. Connections among the Lab's definition, work and evidence records belong to the Lab artifact model.

**Reason:** Use the same definition and Operation to explain the difference between software and Lab artifact relationships.

## 11 — Keep lifecycle attached to the relevant subject

**Before:** The three axes also make an agent's handoff interpretable. Authority identifies the selected definition the agent was working under. Provenance connects the code and evaluation results to their exact inputs. Lifecycle records whether a proposal, artifact or work item has reached the applicable state through its required transitions.

**Revision:** The three axes also make an agent's handoff interpretable. Authority identifies the selected definition the agent was working under. Provenance connects the code and evaluation results to their exact inputs. Lifecycle records whether a proposal, artifact or work item has reached the applicable state through its required transitions.

**Reason:** Distinguish governance and execution lifecycle without introducing new status vocabulary.

## Final reading — Explain predicate at its first use

**Before:** A readable summary is:

**Revision:** The Rule's **predicate** is the condition evaluated as true or false. Here it is the strict comparison of requested and available units.

A readable summary is:

**Reason:** Explain the formal term immediately before the model summary.

## Final reading — Consolidate the repeated boundary explanation

**Before:** For this example, the design keeps the decision self-contained. Its declared dependencies are the snapshot, Rule and result type. Its behavior has no state-writing or external-effect responsibility. A caller supplies the snapshot and receives a decision.

This establishes a boundary around one responsibility. A caller provides the record, the decision evaluates it, and the caller receives Accept or Reject. The decision can be examined independently of a database connection, job scheduler or delivery mechanism. Adding one of those responsibilities changes the design and needs an explicit contract.

**Revision:** For this example, the design keeps the decision self-contained. Its declared dependencies are the snapshot, Rule and result type. Its behavior has no state-writing or external-effect responsibility.

This establishes a boundary around one responsibility. A caller provides the record, the decision evaluates it, and the caller receives Accept or Reject. The decision can be examined independently of a database connection, job scheduler or delivery mechanism. Adding one of those responsibilities changes the design and needs an explicit contract.

**Reason:** Retain the dependencies and boundary while describing the caller interaction once.

## Final reading — Explain endpoint constraints in context

**Before:** A new relationship kind needs a declared meaning, endpoint constraints and an explicit extension route before it can participate in that composition.

**Revision:** A new relationship kind needs a declared meaning, constraints on the roles at each end—its endpoint constraints—and an explicit extension route before it can participate in that composition.

**Reason:** Keep the technical term and explain what it governs.

## Final reading — Improve the completion transition

**Before:** Nor does having a check establish that an agent ran it.

**Revision:** The existence of a check does not establish that an agent ran it.

**Reason:** Make the sentence stand on its own after the new subsection heading.

## Final reading — Connect the Lab explanation to the walkthrough

**Before:** The capacity example has produced several different subjects:

**Revision:** The capacity example connects several different subjects:

**Reason:** Describe the relationship among subjects in the article directly.
