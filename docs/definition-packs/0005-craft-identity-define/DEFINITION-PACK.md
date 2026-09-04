<!-- GENERATED FILE: edit definition-pack.json or handled-definitions.json and run render.py. -->

# CML-07 Craft Identity Define Pack

> Generated from machine-canonical Define records. Candidate only; authority effect is none.

- Pack: `DEFINE-PACK-CAL-CRAFT-IDENTITY-CML07-001`
- Route: `CA2-ROUTE-DEFINE`
- Producer: `cav2.define@0.6.0-candidate`
- Status: `candidate-authored`
- Consumer: `CML07-S1-CORRECTED-DEFINITION-CANDIDATE-AUTHOR`

## Goal

Resolve the six semantic concepts required by CML-07 before identity Artifact Type construction.

## Intent

Migrate the Craft identity chain into CyberAlchemy Lab while keeping Product, Project, Method, Goal, relation, ownership, context, and authority orthogonal and using CyberAlchemy-v2 Define as the semantic authoring capability.

## Context

The bounded semantic input needed to represent the renamed Craft Product lineage through separate Product, Project, Method, Goal, and relation carriers before S2 schema construction.

Context sufficiency: `sufficient-for-candidate-definition`.

## Concept dispositions

| Concept | Term | Disposition | Decision owner |
| --- | --- | --- | --- |
| `cal.definition.product` | Product | `propose` | `role:definition-owner` |
| `CAV2-D32` | Method | `reuse` | `role:definition-owner` |
| `CAV2-D20` | Craft Method | `reuse` | `role:definition-owner` |
| `CAV2-D59` | Goal | `reuse` | `role:definition-owner` |
| `CAV2-D60` | Project | `reuse` | `role:definition-owner` |
| `cal.definition.identity-relation` | Identity Relation | `propose` | `role:definition-owner` |

## Resolved definitions

### Product (`cal.definition.product`)

- Disposition: `propose`
- Decision owner: `role:definition-owner`
- Context: The Product identity needed by CML-07 to preserve Craft as the same Product lineage renamed from DomainSpec v2 while keeping Project, Method, Goal, Feature, Capability, Bounded Context, and realization separate.
- Intended use: Candidate semantic input for a Lab Product Definition and later Product Identity Artifact Type.

#### Normative result

A Product is a durable identity-bearing boundary for a coherent purpose and promise of value. Projects may coordinate it, Methods may be embodied by it, and Features, Capabilities, contexts, and realizations may relate to it, but none becomes the Product or acquires its authority through that relation.

#### Formal result

```text
Product(p) = (identity, purpose, value_promise, lineage, owner_route); related(p,x) does not imply p = x or authority(p) = authority(x).
```

#### Plain-language result

A Product is the enduring thing that promises value. Projects organize work around it and methods help build it, but neither is the Product.

#### Domain-context result

Craft is the current name of the same Product lineage formerly called DomainSpec v2. Product placement does not create a Craft root Bounded Context.

#### Boundary

Product is not Project, Method, Goal, Product Feature, Product Capability, Bounded Context, repository, directory, or implementation.

Candidate posture: `candidate`; canonical target: `unassigned`.

### Method (`CAV2-D32`)

- Disposition: `reuse`
- Decision owner: `role:definition-owner`
- Context: Generic Method meaning required to type Craft Method as a separate specialization in CML-07.
- Intended use: Exact reuse binding for the successor Lab Method Definition record.

#### Exact reused canonical definition

- Source definition: `CAV2-D32`
- Source: `domainspec-core:cyberAlchemy-v2/authority/definitions/DEFINITIONS.md`
- Selector: `lines:2114-2180`
- Selected digest: `28608be42869eaf5183bd5b4154d9bded38f1a17ad35c11072b9a49f1e4dc348`
- Source owner: `CyberAlchemy v2 definitions-governance owner`

> ## CAV2-D32: Method
>
> Status: active
> Term: method
> Aliases: governed method, method primitive, repeatable governance method
> Ancestral provenance (non-normative): generic descendant of the CyberAlchemy Method ([`arcanum/framework/CYBERALCHEMY-METHOD.md`](../../../arcanum/framework/CYBERALCHEMY-METHOD.md), 5 anchors). Evidence posture — not deployed. See [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md) § Ancestral Lineage Reconciliation.
>
> ### Normative Definition
>
> A method is a governed repeatable way to transform intent, source evidence,
> state, or residue into artifacts and continued work under declared roles,
> actions or phases, gates, validation conditions, residue handling, provenance,
> and recomposition or evolution rules.
>
> A method may be instantiated by a narrower named method, such as `CAV2-D17`
> reflection tower method, `CAV2-D20` Craft method, or `CAV2-D21` four-facet
> action method. The generic term names the umbrella role; each concrete method
> must still declare its own scope, inputs, outputs, gates, and boundaries.
>
> ### Formal Interpretation
>
> For a method `M`, an admissible CyberAlchemy v2 method record has at least:
>
> ```text
> M = (scope, inputs, actions, roles, gates, outputs, evidence,
>      residue_rule, validation_rule, recomposition_rule, boundary)
> ```
>
> The method is repeatable when another execution can identify which fields are
> being reused, which are being specialized, and which residue remains open.
>
> ### Operational Interpretation
>
> Use this term when deciding whether a repeated CyberAlchemy move is merely a
> task habit, an implementation pipeline, a technique, a lifecycle label, or a
> governed method. A method can use engines, pipelines, checklists, ledgers,
> schemas, agents, or workflows, but it is not identical to any one of them
> unless the concrete definition says so.
>
> ### Plain-Language Intuition
>
> A method is the repeatable way the project turns intent and evidence into work
> that can be checked, carried forward, and improved.
>
> ### Domain-Context Voice
>
> In CyberAlchemy v2, method is the umbrella term that lets the project compare
> the CyberAlchemy Method source material, Craft method, reflection tower method,
> four-facet action method, promotion routes, and later runtime workflows without
> collapsing them into one pipeline. This is why `method` belongs in the
> primordial basis: lower towers can build their own methods, but their method
> claims must remain explicit and reviewable.
>
> ### Boundary
>
> Method is not a single technique, not a one-off task, not a mere checklist, not
> an engine, not a pipeline, not a lifecycle state, and not authority by itself.
> Authority comes from the owner surface and gate that admit a method into a
> particular use.
>
> ### Primary Consumers
>
> - [source-clusters/primordial.md](source-clusters/primordial.md)
> - [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
> - [../../CRAFT.md](../../CRAFT.md)
> - [../../../arcanum/framework/CYBERALCHEMY-METHOD.md](../../../arcanum/framework/CYBERALCHEMY-METHOD.md)

### Craft Method (`CAV2-D20`)

- Disposition: `reuse`
- Decision owner: `role:definition-owner`
- Context: The governed recursive system-building Method embodied by the Craft Product and used by the Craft Project without identity collapse.
- Intended use: Exact reuse binding for the successor Lab Craft Method Definition record and later Method Binding contract.

#### Exact reused canonical definition

- Source definition: `CAV2-D20`
- Source: `domainspec-core:cyberAlchemy-v2/authority/definitions/DEFINITIONS.md`
- Selector: `lines:1014-1185`
- Selected digest: `ce8dd8633ff5df8fc76b71cf544327209f34a875ed9f93e262469f7c98d8b640`
- Source owner: `CyberAlchemy v2 definitions-governance owner`

> ## CAV2-D20: Craft Method
>
> Status: active
> Term: Craft method
> Aliases: CyberAlchemy building method, governed system-building method, recursive residue-carrying building method, Craft recursive method
>
> ### Normative Definition
>
> Craft method is CyberAlchemy's governed recursive system-building method. It
> turns owner-controlled Product intent into an evidence-bounded working system by
> preserving one explicit chain through context, definitions, product and business
> meaning, system specification, exact realization selection, deterministic
> construction, independent conformance, bounded operation, recovery, evolution,
> and owner continuation.
>
> The method uses a source-of-truth ledger to preserve state across that chain. It
> records contexts, candidate definitions, blockers, enablers, decisions, gaps,
> artifacts, next moves, validation evidence, residue, and recomposition
> obligations. Ledgering is the method's continuity mechanism; it is not the whole
> method.
>
> In CyberAlchemy v2, Craft method is valid only when it preserves these
> boundaries:
>
> - a Product and its Product Thesis own product purpose and value propositions
> - a Project coordinates the goals, owners, evidence, decisions, and work used to
>   develop or evolve the Product
> - Product Features and Product Capabilities remain distinct from the Product,
>   Project, Method, and their realizations
> - canonical definitions, product and business ontology, DomainSpec source,
>   generated system ontology, realization selection, construction, conformance,
>   runtime evidence, and owner decisions remain separately identifiable
> - every implementation-bearing construction follows the exact
>   `CAV2-D65` DomainSpec-governed construction chain or carries typed residue for
>   the missing prerequisite
> - `.craft/ledger.yml` or an equivalent declared ledger is the source of truth
>   for Craft state
> - `CRAFT.md`, `.craft/index.json`, projections, and status output are derived
>   views
> - residue is typed and carried forward instead of hidden
> - schema-level and instance-level validation are not collapsed
> - child contexts recompose into their parent through evidence
> - closure happens by owner decision, gate, or accepted residue, not by a claim
>   of total final completion
> - Craft state can carry local candidate definitions and receipts but cannot
>   make terms canonical without definitions-governance
>
> ### Formal Interpretation
>
> For a bounded Product and Project scope `S`, the Craft method has the minimum
> governed shape:
>
> ```text
> M_Craft(S) =
>   (context, product_intent, domain_meaning, system_specification,
>    realization_selection, construction, conformance, operation,
>    recovery_and_evolution, owner_continuation, ledger_state)
>
> L_S = (C, B, E, D, G, A, N, R)
> ```
>
> where:
>
> - `context` resolves the Product, Project, Goal, participants, consumers, and
>   source policies relevant to the bounded work
> - `product_intent` carries the Product Thesis plus selected Product Feature or
>   Product Capability obligations
> - `domain_meaning` carries canonical definitions and product/business ontology
> - `system_specification` carries DomainSpec and generated system-ontology state
> - `realization_selection` identifies exact architecture and language-profile
>   realizations
> - `construction` materializes the selected contained target deterministically
> - `conformance` independently evaluates declared static and relational
>   obligations
> - `operation` supplies bounded runtime evidence without becoming authority
> - `recovery_and_evolution` preserves compensation, recovery, migration,
>   rollback, compatibility, and successor-state obligations
> - `owner_continuation` routes an evidenced next state to its explicit owner
> - `C` is the set of contexts or child contexts
> - `B` is blockers
> - `E` is enablers or available evidence
> - `D` is decisions
> - `G` is gaps or unresolved obligations
> - `A` is artifacts and source references
> - `N` is next moves or route obligations
> - `R` is typed residue plus recomposition evidence
>
> A Craft step is admissible when it preserves typed identity and source
> authority, records the operation that changed state, keeps generated views
> derivative, validates every reachable declared consumer, and either repairs,
> types, routes, accepts, or defers residue with an owner. Construction does not
> establish conformance; conformance does not establish runtime truth; evidence
> does not establish owner adoption or permission.
>
> Formal-foundations evidence supports this shape by treating residue as typed and
> composable, by separating schema-fidelity from instance-fidelity, by showing
> that reflection towers assemble without finite total closure, and by justifying
> stop criteria based on decision and residue plateau rather than completion. This
> is support evidence for the method; it does not prove that an LLM-centered Craft
> run achieved a clean functor, kernel, or zero-residue translation.
>
> ### Operational Interpretation
>
> Use Craft method whenever CyberAlchemy builds or materially evolves a Product,
> Product Feature, Product Capability, system, or implementation-bearing
> capability. Begin from the Product and Project context, define the meaning,
> model the product and business obligations, author or update the DomainSpec
> source, select exact realizations, construct the target, independently check it,
> observe bounded runtime behavior, preserve recovery and evolution obligations,
> and route the evidenced state to its owner.
>
> The same method provides durable work memory across sessions, definition towers,
> authority imports, constitution towers, research packets, promotion queues, and
> nested project spaces. A human or agent should be able to continue without
> guessing what is blocked, what is merely candidate, what has evidence, what was
> constructed, and what must recompose upward.
>
> ### Plain-Language Intuition
>
> Craft method is how CyberAlchemy builds a system without losing why it should
> exist: define the meaning, choose exactly how it will be built, build it, check
> it independently, observe it, and carry every leftover problem to the next
> owner instead of pretending the work is finished.
>
> ### Domain-Context Voice
>
> Inside CyberAlchemy v2, the Craft Product embodies this method and the Craft
> Project coordinates its development and evolution. Product Features are shaped
> inside the Craft Product context; Product Capabilities state stable outcomes;
> DomainSpec expresses system intent; architecture and language profiles select
> exact realizations; construction and conformance provide separate evidence; and
> the Craft ledger preserves continuity and residue across the whole path.
>
> The method connects `CAV2-D12` Craft execution surface, `CAV2-D17` reflection
> tower method, `CAV2-D18` residue, and `CAV2-D65` DomainSpec-governed
> construction invariant. The execution surface is where Craft state lives; the
> method is the broader discipline for carrying meaning, realization,
> construction, evidence, recovery, residue, and recomposition through recursive
> system work.
>
> The public Arcanum `craft` capability is one narrower repository-ledger
> realization used by this private method. It does not own the private Craft
> Product, Project, Product Thesis, Product Features, or method semantics.
>
> ### Boundary
>
> Craft method is not the Craft Product, Craft Project, a Product Feature, Product
> Capability, Product Thesis, DomainSpec model, architecture pattern, generator,
> runtime, public Arcanum capability, `.craft` state, generic task runner, or
> replacement for task-session. It is not a source of canonical definitions and
> does not authorize implementation or prove that a translation, construction,
> conformance assessment, operation, recovery, or migration is complete.
>
> It may use formal foundations as support evidence, but it must preserve their
> honesty boundary: formal cousins describe the structure Craft operates inside;
> they do not certify that a particular Craft run achieved the clean formal case.
>
> Craft method also does not promote `ledger` as a cross-method primitive by
> itself. Ledger remains separately flagged for review until recursivity, relation
> inheritance, and local Craft ledger conformance are settled.
>
> ### Primary Consumers
>
> - [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
> - [source-clusters/primordial.md](source-clusters/primordial.md)
> - [../../CRAFT.md](../../CRAFT.md)
> - [../../.craft/ledger.yml](../../.craft/ledger.yml)
> - [../../product/craft/README.md](../../product/craft/README.md)
> - [../../goals/projects/craft/README.md](../../goals/projects/craft/README.md)
> - [../../../arcanum/arcana/craft/SKILL.md](../../../arcanum/arcana/craft/SKILL.md)
> - [../../../arcanum/development/craft/CRAFT-FORMAL-FOUNDATIONS.md](../../../arcanum/development/craft/CRAFT-FORMAL-FOUNDATIONS.md)

### Goal (`CAV2-D59`)

- Disposition: `reuse`
- Decision owner: `role:definition-owner`
- Context: Goal meaning required to represent one Project-owned desired outcome without treating activity, validation, or agent claims as achievement.
- Intended use: Exact reuse binding for the successor Lab Goal Definition record and later Goal carrier contract.

#### Exact reused canonical definition

- Source definition: `CAV2-D59`
- Source: `domainspec-core:cyberAlchemy-v2/authority/definitions/DEFINITIONS.md`
- Selector: `lines:4443-4521`
- Selected digest: `f9589997351dcd40f5c37f970568aab3a09345c1b8ab6331860d5533d2c7a674`
- Source owner: `CyberAlchemy v2 definitions-governance owner`

> ## CAV2-D59: Goal
>
> Status: active
> Term: goal
> Aliases: governed goal, project goal, outcome goal
> Promoted: 2026-08-29 by owner-requested product-foundation modeling; definition authority only
>
> ### Normative Definition
>
> A goal is a durable, attributable statement of a desired future outcome for one
> project. It says what should become true, why that outcome matters, what is in
> and out of scope, who owns the goal, how success will be judged, which evidence
> is required, how it connects to a product thesis or other purpose, and how it
> can be revised, challenged, achieved, abandoned, or superseded.
>
> A goal may stay active without a deadline. It becomes achieved only when its
> declared success conditions have adequate evidence and the goal owner records
> the lifecycle change. Activity, progress, a passing sub-check, or an agent claim
> does not achieve it automatically.
>
> ### Formal Interpretation
>
> ```text
> Goal =
>   (id, project_ref, outcome, rationale, thesis_refs, scope, exclusions,
>    owner_route, success_conditions, evidence_requirements, evidence_refs,
>    lifecycle_state, target_horizon?, revision_history, challenge_route)
>
> lifecycle_state in { draft, active, achieved, abandoned, superseded }
>
> achieved(Goal) only if
>   all_required_success_conditions_have_adequate_evidence
>   and owner_records_achievement
> ```
>
> ### Schema
>
> Schema handle: `CAV2-D59-SCHEMA` — tracked in
> [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
> The machine-checkable candidate instance contract is owned by
> [../../goals/schemas/goal-package.schema.json](../../goals/schemas/goal-package.schema.json).
>
> ### Operational Interpretation
>
> Use a goal when a project needs to preserve an eventual result across sessions,
> plans, tasks, experiments, and implementation changes. Let plans choose a path
> and tasks perform bounded work, but keep checking both against the goal's result
> and success evidence.
>
> ### Plain-Language Intuition
>
> A goal says which future result the project is trying to reach and what evidence
> will let us honestly say it was reached.
>
> ### Domain-Context Voice
>
> In CyberAlchemy v2, a goal connects product meaning to project work. For
> example, the PythonConstraint goal connects the CyberAlchemy product thesis to a
> bounded CyberAlchemy-v2 and DomainSpec-v2 experiment. Its plans and runs may
> change, but the desired result, owner, evidence requirements, and current
> achievement claim remain visible.
>
> ### Boundary
>
> A goal is not intent (`CAV2-D39`), a project (`CAV2-D60`), a plan, a task, a
> work pack, evidence, a deadline, or authority to execute. Intent can orient work
> before its final result is clear. A goal states the result clearly enough to be
> tested. A plan chooses how to pursue it. Evidence supports an achievement
> decision. The goal itself grants no implementation, publication, deployment, or
> external-effect authority.
>
> ### Primary Consumers
>
> - [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
> - [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
> - [../../goals/README.md](../../goals/README.md)
> - [../../goals/GOAL-DOCUMENT-TYPE.md](../../goals/GOAL-DOCUMENT-TYPE.md)
> - [../../product/PRODUCT-THESIS.md](../../product/PRODUCT-THESIS.md)

### Project (`CAV2-D60`)

- Disposition: `reuse`
- Decision owner: `role:definition-owner`
- Context: Project meaning required to represent the durable Craft coordination boundary separately from Product, Method, Goal, repository, and authority.
- Intended use: Exact reuse binding for the successor Lab Project Definition record and later Project Identity contract.

#### Exact reused canonical definition

- Source definition: `CAV2-D60`
- Source: `domainspec-core:cyberAlchemy-v2/authority/definitions/DEFINITIONS.md`
- Selector: `lines:4522-4602`
- Selected digest: `3dc9faeecf91410b8b6a00aa8fd847d474031bd207e91743e72507dee6c526db`
- Source owner: `CyberAlchemy v2 definitions-governance owner`

> ## CAV2-D60: Project
>
> Status: active
> Term: project
> Aliases: governed project, project identity, work project
> Promoted: 2026-08-29 by owner-requested product-foundation modeling; definition authority only
>
> ### Normative Definition
>
> A project is a durable, identity-bearing coordination boundary that groups
> related goals, owners, evidence, decisions, artifacts, work, and lifecycle state
> toward a declared purpose.
>
> A project must name its purpose, scope, exclusions, owners, current Goal references,
> evidence index, lifecycle state, purpose or product-thesis connections,
> instance-binding references, and challenge route. Its identity remains stable
> when a plan, task, folder, tool, or implementation changes.
>
> ### Formal Interpretation
>
> ```text
> Project =
>   (id, name, purpose, scope, exclusions, owner_routes, goal_refs,
>    research_refs, experiment_refs, evidence_index, thesis_refs,
>    instance_binding_refs, lifecycle_state, challenge_route)
>
> lifecycle_state in { proposed, active, completed, cancelled, superseded }
> |goal_refs| >= 1
> proposed(Project) => exists g in goal_refs: lifecycle(g) in { draft, active }
> active(Project) => exists g in goal_refs: lifecycle(g) = active
> ```
>
> ### Schema
>
> Schema handle: `CAV2-D60-SCHEMA` — tracked in
> [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
> The machine-checkable candidate project record is owned by
> [../../goals/schemas/goal-package.schema.json](../../goals/schemas/goal-package.schema.json).
> Its v2 shape adds `instance_binding_refs`; the referenced records are owned by
> the Project binding registry rather than embedded as untyped Project metadata.
>
> ### Operational Interpretation
>
> Use a project to keep several sessions and kinds of work connected to the same
> purpose. A project can have several goals, and each goal in the current contract
> belongs to exactly one project. A proposed Project may begin with a draft Goal;
> an active Project must retain at least one active Goal. Project evidence may come from many spaces, but
> it stays indexed under the project identity. When the Project coordinates a
> locally owned instance of a parent model, `instance_binding_refs` names the
> exact `CAV2-D64-SCHEMA` records that preserve that relationship. An empty list
> means that the Project currently asserts no recursive instance binding.
>
> ### Plain-Language Intuition
>
> A project is the named piece of work that keeps its goals, owners, evidence, and
> history together even when the files and plans move.
>
> ### Domain-Context Voice
>
> In CyberAlchemy v2, the PythonConstraint experiment is a project shared by the
> CyberAlchemy-v2 product lane and the DomainSpec-v2 implementation/research lane.
> It may use `product/`, `goals/`, `projects/domainspec-v2/`, validation, and
> temporary runtime spaces without becoming identical to any one of those places.
>
> ### Boundary
>
> A project is not a project space (`CAV2-D15`), goal (`CAV2-D59`), product,
> repository, plan, work pack, session, team, or authority envelope. A project
> space is a place where work lives; a project is the identity and coordination
> boundary of the work. Creating a project does not authorize its goals or tasks.
> Project membership, a folder named `project`, or a DomainSpec minted-project
> manifest does not create a `CAV2-D60` Project or a recursive instance binding.
>
> ### Primary Consumers
>
> - [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
> - [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
> - [../../goals/README.md](../../goals/README.md)
> - [../../goals/GOAL-DOCUMENT-TYPE.md](../../goals/GOAL-DOCUMENT-TYPE.md)
> - [../../goals/bindings/recursive-instance-bindings.json](../../goals/bindings/recursive-instance-bindings.json)

### Identity Relation (`cal.definition.identity-relation`)

- Disposition: `propose`
- Decision owner: `role:definition-owner`
- Context: The explicit typed connection needed to represent dependent classifications without redundant canonical labels, endpoint collapse, directory inference, or authority transfer.
- Intended use: Candidate semantic input for a Lab Identity Relation Definition and later Identity Graph contract.

#### Normative result

An Identity Relation is a separately governed typed edge with a stable relation identity, kind, source endpoint, target endpoint, owner, evidence, and lifecycle. It preserves endpoint identities and authority; dependent classifications use explicit relations rather than silently inferred or redundant canonical labels.

#### Formal result

```text
R = (relation_id, kind, from_ref, to_ref, owner_ref, evidence_refs, lifecycle); R(a,b) does not imply a = b or authority(a) = authority(b).
```

#### Plain-language result

An Identity Relation says exactly how two separate things are connected without turning them into the same thing or transferring authority.

#### Domain-context result

The Craft graph uses explicit coordinated_by, embodies_method, uses_method, and pursues_goal relations. Convenience labels derived from them are generated projections, not new canonical axes.

#### Boundary

Identity Relation is not an endpoint, identity equality, authority transfer, inferred context membership, directory dependency, or canonical convenience label.

Candidate posture: `candidate`; canonical target: `unassigned`.

## Explicit relations

- `CAV2-D20` — `specializes` → `CAV2-D32`
- `cal.definition.product` — `coordinated_by` → `CAV2-D60`
- `cal.definition.product` — `embodies_method` → `CAV2-D20`
- `CAV2-D60` — `uses_method` → `CAV2-D20`
- `CAV2-D60` — `pursues_goal` → `CAV2-D59`
- `cal.definition.identity-relation` — `governs_explicit_connection_between` → `cal.definition.product`

## Open questions and stops

### CML07-DEFINE-OPEN-001

Should the Product and Identity Relation proposals become Lab canonical definitions at the final CML-07 boundary?

- Construction stop: `true`
- Next action: Derive exact Lab Definition candidates and include them in the final CML-07 decision set.

### CML07-DEFINE-OPEN-002

Should the four reused CAV2 definitions be represented as exact imports rather than rewritten semantic successors?

- Construction stop: `true`
- Next action: Under CA2-ROUTE-DEFINITIONS, bind exact source meaning and treat Lab-specific wording as nonnormative domain context.

### CML07-DEFINE-OPEN-003

May S2 begin before source admissions, owner bindings, and successor Definition records are bound into one final decision set?

- Construction stop: `true`
- Next action: Author only non-effectful successor candidates with explicit dependency residue; make no evaluable or admitted S2 claim before the final boundary.

## Allowed uses

- Review or challenge the six dispositions and relationships.
- Use as exact semantic input to a successor Lab Definition candidate under CA2-ROUTE-DEFINITIONS.
- Carry unresolved admission and ownership dependencies to the final CML-07 boundary.

## Blocked actions

- Treat candidate 0006 as correctly Define-routed or canonical.
- Promote either proposal or silently revise any reused CAV2 meaning.
- Claim CML07-S2 evaluable, construct identity carriers, implement, publish, release, or deploy.

## Claim ceiling

A structurally validated Define candidate for the six CML-07 concepts. It does not accept the pack, admit sources or owners, promote definitions, make S2 evaluable, construct carriers, implement, publish, release, or deploy.
