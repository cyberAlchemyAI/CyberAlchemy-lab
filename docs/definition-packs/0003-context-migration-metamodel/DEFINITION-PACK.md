<!-- GENERATED FILE: edit canonical JSON and run render.py. -->

# Context Migration Metamodel Definition Pack

> Generated from `definition-pack.json`, `handled-definitions.json`, and `definition-drift-audit.json`; this Markdown is not canonical.

- Pack: `DEFINE-PACK-CAL-CONTEXT-MIGRATION-METAMODEL-003`
- Status: `candidate-authored-pending-source-admission-and-owner-review`
- Authority effect: `none`
- Promotion ready: `false`

## Goal

Establish the smallest non-collapsing vocabulary needed to represent and migrate Coordination Contexts, DDD Bounded Contexts, their languages and maps, and owner-local capability instances into CyberAlchemy Lab.

## Intent

Make context migration explicit, directional, source-bound, and recursively governable before creating contexts/ or relocating ontology-lifecycle/.

## Dispositions

- Reuse: `0`
- Specialize: `2`
- Revise: `1`
- Propose: `4`
- Open: `0`

| ID | Term | Disposition | Plain-language voice |
|---|---|---|---|
| `cal.coordination-context` | Coordination Context | `specialize` | The durable frame that says what a piece of work is about, why information is needed, and who will use it. |
| `cal.bounded-context` | Bounded Context | `propose` | A named boundary within which words and domain rules have one deliberately consistent meaning. |
| `cal.ubiquitous-language` | Ubiquitous Language | `revise` | The shared vocabulary used to discuss and build one bounded part of the domain. |
| `cal.context-map` | Context Map | `propose` | The explicit map showing how bounded contexts depend on or translate for one another and who owns each side. |
| `cal.capability-instance` | Capability Instance | `specialize` | A locally owned realization of a reusable capability, connected to its blueprint without becoming the blueprint. |
| `cal.context-migration-manifest` | Context Migration Manifest | `propose` | The exact, reviewable plan for what context material might move, where it would go, what would change, and how to stop or reverse safely. |
| `cal.context-lineage-record` | Context Lineage Record | `propose` | The durable record explaining how an old context identity relates to its successors and which meanings stayed the same or changed. |

## Candidate definitions

### Coordination Context (`cal.coordination-context`)

Disposition: `specialize`  
Owner: `future:coordination-context-owner`  
Status: `candidate-unadmitted`

**Scientific/formal voice:** A Coordination Context is a durable, identity-bearing, owner-qualified frame that binds one Product, an optional Project, an optional Goal, a stable purpose, intended consumers and uses, subject scope, source policies, and zero or more references to independently owned Bounded Contexts. A material change to Product, Project, Goal, or purpose requires a successor identity.

**Formal model:** `CoordinationContext = (id, product_ref, project_ref?, goal_ref?, purpose, consumer_refs, intended_uses, subject_scope, source_policy_refs, bounded_context_refs, owner_ref, lifecycle, revision_history, challenge_route); |product_ref|=1; |project_ref|<=1; |goal_ref|<=1; material_anchor_change => successor_required.`

**Operational interpretation:** Use a Coordination Context to frame why selected information is needed and by whom. Resolve changing source selections into separate views rather than mutating the context identity.

**Plain-language voice:** The durable frame that says what a piece of work is about, why information is needed, and who will use it.

**CyberAlchemy Lab context:** In CyberAlchemy Lab, Coordination Context records belong under coordination/contexts and may reference Governance or Ontology Lifecycle bounded contexts without becoming either one.

**Boundary:** A Coordination Context is not a DDD Bounded Context, Product, Project, Goal, session, prompt, source selection, resolved view, authority envelope, decision, or execution permission.

Promotion blockers:

- CAV2-D66 selector admission for this exact specialization is absent.
- The Coordination Context owner role and artifact type are not admitted.

### Bounded Context (`cal.bounded-context`)

Disposition: `propose`  
Owner: `future:bounded-context-owner`  
Status: `candidate-unadmitted`

**Scientific/formal voice:** A Bounded Context is a versioned, owner-scoped semantic boundary inside which one declared domain model and one Ubiquitous Language are intended to remain internally consistent for an explicit scope and set of exclusions. Its relationships to other Bounded Contexts exist only through separately owned directional Context Maps and contracts.

**Formal model:** `BoundedContext = (id, version, domain_model_ref, ubiquitous_language_ref, scope, exclusions, semantic_owner_ref, contract_refs, context_map_refs, lifecycle, evidence_refs, challenge_route); unique(id,version); every cross_context_dependency => exists exact directional ContextMap.`

**Operational interpretation:** Create a Bounded Context only after naming its model, language, owner, scope, exclusions, and cross-context dependencies. Reject context identity inferred from a package name or directory.

**Plain-language voice:** A named boundary within which words and domain rules have one deliberately consistent meaning.

**CyberAlchemy Lab context:** CyberAlchemy Lab treats Governance and Ontology Lifecycle as distinct bounded-context candidates because authority decisions and ontology event history have related but non-identical models and owners.

**Boundary:** A Bounded Context is not a folder, module, package, Product, capability, Coordination Context, Project, Goal, team, deployment unit, database, or authority grant.

Promotion blockers:

- No admitted Lab source provides a canonical Bounded Context meaning.
- The proposed meaning requires definition-owner and bounded-context-owner review.

### Ubiquitous Language (`cal.ubiquitous-language`)

Disposition: `revise`  
Owner: `future:bounded-context-language-owner`  
Status: `candidate-unadmitted`

**Scientific/formal voice:** A Ubiquitous Language is the owner-governed set of expressions, concepts, relations, interpretation rules, usage surfaces, ambiguities, and revision routes used to express one Bounded Context's model. Each load-bearing expression resolves to one current concept disposition within that context or remains explicitly unresolved.

**Formal model:** `UbiquitousLanguage = (id, bounded_context_ref, concept_refs, expression_bindings, relation_bindings, interpretation_rules, usage_surfaces, owner_refs, ambiguity_records, revision_state); each current binding belongs_to(bounded_context_ref); shared_spelling =/=> shared_meaning.`

**Operational interpretation:** Use the same owned expressions across relevant conversation, model, specification, implementation, and evidence surfaces inside the context; record ambiguities and bridges instead of forcing equivalence.

**Plain-language voice:** The shared vocabulary used to discuss and build one bounded part of the domain.

**CyberAlchemy Lab context:** Governance and Ontology Lifecycle must each own their language. Terms such as decision, event, lifecycle, and state cross the boundary only through explicit mappings.

**Boundary:** A Ubiquitous Language is not a repository-wide dictionary, canonical definition registry, glossary file, ontology, programming language, maintenance discipline, or proof that every participant understands the same thing.

Promotion blockers:

- The source Language and Ubiquitous Language meanings are package-local candidates.
- No external DDD source has been admitted for the established term.

### Context Map (`cal.context-map`)

Disposition: `propose`  
Owner: `future:context-map-owner`  
Status: `candidate-unadmitted`

**Scientific/formal voice:** A Context Map is a versioned, owner-approved set of typed directional relationships between exact Bounded Context versions. Each relationship declares upstream and downstream roles, integration or translation contracts, information and authority limits, owners, evidence, drift handling, and change coordination.

**Formal model:** `ContextMap = (id, version, context_refs, relationships, owner_refs, lifecycle, evidence_refs, drift_route); Relationship = (source_context_version, target_context_version, direction, relationship_kind, contract_refs, translation_refs, information_boundary, authority_boundary, owners); directory_or_import_proximity =/=> relationship.`

**Operational interpretation:** Use a Context Map before one context consumes another context's language, model, events, or contracts. Fail closed when direction, version, contract, or ownership is missing.

**Plain-language voice:** The explicit map showing how bounded contexts depend on or translate for one another and who owns each side.

**CyberAlchemy Lab context:** The first Lab map will connect Ontology Lifecycle downstream to Governance upstream while leaving the exact DDD relationship pattern for a separate owner decision.

**Boundary:** A Context Map is not a directory tree, dependency scan, import graph, ontology relation set, runtime topology, authority transfer, or evidence that two contexts agree.

Promotion blockers:

- The exact Governance to Ontology Lifecycle relationship pattern remains unresolved.
- Context-map owner roles and artifact type are not admitted.

### Capability Instance (`cal.capability-instance`)

Disposition: `specialize`  
Owner: `future:capability-instance-owner`  
Status: `candidate-unadmitted`

**Scientific/formal voice:** A Capability Instance is an owner-local, version-exact realization or specialization of one Product Capability inside an explicitly declared coordination and semantic context. It binds separate parent and instance authority lanes, inherited contract, extension scope, adoption decision, D65 construction stages, conformance evidence, lifecycle, drift and recomposition routes, recursion budget or stop, and terminal handoff.

**Formal model:** `CapabilityInstance = (id, capability_version_ref, coordination_context_ref, bounded_context_refs, parent_authority_claim, instance_authority_claim, inherited_contract_ref, extension_scope, adoption_decision_ref, construction_binding_ref, conformance_refs, lifecycle, drift_route, recomposition_route, recursion_stop, terminal_handoff); instance =/=> parent; conformance =/=> authority.`

**Operational interpretation:** Instantiate a capability only after binding the exact parent version and local owner. Keep authored specification, generated projections, implementation, evidence, residue, and handoff inside the instance envelope.

**Plain-language voice:** A locally owned realization of a reusable capability, connected to its blueprint without becoming the blueprint.

**CyberAlchemy Lab context:** The existing ontology-lifecycle vertical may become a capability instance inside the new Ontology Lifecycle bounded context only after its exact parent capability and complete recursive and construction bindings are selected.

**Boundary:** A Capability Instance is not the Product Capability, Bounded Context, Coordination Context, Project, Goal, directory, implementation component, deployment, conformance result, or authority grant.

Promotion blockers:

- CAV2-D64 and CAV2-D67 selectors are not admitted for this specialization.
- The parent Product Capability for the current ontology-lifecycle vertical is not admitted.

### Context Migration Manifest (`cal.context-migration-manifest`)

Disposition: `propose`  
Owner: `future:migration-owner`  
Status: `candidate-unadmitted`

**Scientific/formal voice:** A Context Migration Manifest is an immutable candidate plan that binds exact source repository selectors and digests to explicit artifact dispositions, proposed destination identities and paths, dependency order, preimages, expected postimages, validation obligations, owner gates, rollback boundaries, exclusions, and unresolved residue for one bounded migration scope.

**Formal model:** `ContextMigrationManifest = (id, source_repository, source_selections, dispositions, destination_candidates, dependency_order, preimages, expected_postimages, validation_obligations, owner_gates, rollback_boundary, exclusions, residue, lifecycle); manifest_exists =/=> source_admitted or migration_authorized or migrated.`

**Operational interpretation:** Create one manifest per context migration epoch. Reject broad directory copies, inferred admissions, untracked splits, or destinations without identity and owner decisions.

**Plain-language voice:** The exact, reviewable plan for what context material might move, where it would go, what would change, and how to stop or reverse safely.

**CyberAlchemy Lab context:** The Ontology Lifecycle manifest will eventually select exact bytes from the current root vertical and external CyberAlchemy-v2 evidence, but this CTX-00 pack does not create that manifest or authorize relocation.

**Boundary:** A Context Migration Manifest is not source admission, execution authorization, a file-copy command, lineage proof, migration receipt, context admission, publication, or deployment.

Promotion blockers:

- The migration-owner role is not bound.
- No selected context postimages or rollback contract exists.

### Context Lineage Record (`cal.context-lineage-record`)

Disposition: `propose`  
Owner: `future:lineage-owner`  
Status: `candidate-unadmitted`

**Scientific/formal voice:** A Context Lineage Record is an immutable, owner-qualified statement relating exact predecessor and successor context identities through one typed lineage disposition, with source and destination versions, preserved and changed semantic scopes, decision evidence, effective boundary, challenges, and residue. It records identity history without inferring semantic equivalence or admission.

**Formal model:** `ContextLineageRecord = (id, predecessor_context_ref?, successor_context_refs, lineage_kind, source_version, destination_versions, preserved_scope, changed_scope, decision_ref, evidence_refs, effective_boundary, challenge_route, residue); lineage_kind in {preserved, successor, split, merged, superseded, withdrawn}; lineage =/=> equivalence or admission.`

**Operational interpretation:** Write a lineage record after context identity and migration decisions are known. Use it to preserve splits, successors, mergers, supersession, and withdrawal without rewriting predecessor history.

**Plain-language voice:** The durable record explaining how an old context identity relates to its successors and which meanings stayed the same or changed.

**CyberAlchemy Lab context:** Ontology Lifecycle will require lineage from the current unclassified vertical to its future bounded-context package; the record must say that directory continuity alone is not semantic identity continuity.

**Boundary:** A Context Lineage Record is not a migration manifest, source admission, context map, alias, redirect, Git rename, equivalence proof, promotion decision, or permission to delete the predecessor.

Promotion blockers:

- The lineage-owner role and lineage artifact type are not admitted.
- No predecessor and successor context artifacts exist for an exact lineage statement.

## Explicit relationships

- `cal.coordination-context` --`references`--> `cal.bounded-context`: A Coordination Context may reference independently owned bounded-context meanings without merging them.
- `cal.ubiquitous-language` --`applies-within`--> `cal.bounded-context`: One Ubiquitous Language is owned and interpreted within one exact bounded context.
- `cal.context-map` --`maps`--> `cal.bounded-context`: A Context Map declares directional relationships among exact bounded-context versions.
- `cal.capability-instance` --`owned-within`--> `cal.bounded-context`: A capability instance retains local meaning and lifecycle under an explicitly selected owner boundary.
- `cal.context-migration-manifest` --`plans-migration-of`--> `cal.bounded-context`: A migration manifest binds exact source selections to a proposed destination context without performing the migration.
- `cal.context-lineage-record` --`records-lineage-of`--> `cal.bounded-context`: A lineage record preserves predecessor and successor identity claims without inferring equivalence.

## Drift and blockers

- `CTX00-DRIFT-001` (blocking): Definition/v1 is admitted as an artifact type, but no canonical Definition term instance exists and the registry is empty. Remediation: Author and separately promote the Definition term before promoting CTX-00 terms.
- `CTX00-DRIFT-002` (blocking): CyberAlchemy-v2 Context and DDD Bounded Context are distinct, while an unqualified contexts/ path can make them appear equivalent. Remediation: Use Coordination Context for the CAV2-D66 specialization and reserve contexts/ for explicit Bounded Context packages.
- `CTX00-DRIFT-003` (blocking): Product and Governance labels occur as products, modules, ontologies, and candidate context evidence; labels and directories cannot establish bounded-context identity. Remediation: Require separate owner-selected context artifacts and retain Product, module, ontology, and context identities as independent axes.
- `CTX00-DRIFT-004` (blocking): The current ontology-lifecycle/ directory is a candidate capability vertical, while CAL-BC-ONTOLOGY-LIFECYCLE is only a selected bounded-context candidate. Remediation: Keep the directory in place until separate context identity, language, capability-instance, source-admission, lineage, and migration decisions exist.
- `CTX00-DRIFT-005` (blocking): Architecture, migration, Governance-context, Ontology-Lifecycle-context, language, context-map, and lineage owner roles are not bound in the admitted owner registry. Remediation: Bind accountable principals and non-collapsing scopes before owner-controlled admissions.
- `CTX00-DRIFT-006` (blocking): CAV2-D29, D64, D66, D67 and the Language, Governance-language, and Context package sources are current evidence but are not admitted for CTX-00 target uses. Remediation: Prepare exact selector-level source-admission candidates with one target use per source.
- `CTX00-DRIFT-007` (blocking): No admitted artifact types exist for the seven context-migration concepts or for Definition Pack. Remediation: After term review, author artifact-type candidates separately from semantic definitions.
- `CTX00-DRIFT-008` (blocking): Ontology Lifecycle is selected downstream of Governance meaning, but the exact DDD context-map relationship pattern and contract remain unresolved. Remediation: Select the exact upstream/downstream integration pattern only after both context candidates and owners exist.
- `CTX00-DRIFT-009` (blocking): Folder names, repeated labels, source package roles, and generated indexes could be mistaken for independent canonical classification axes. Remediation: Reject inferred fields, keep explicit typed relations, and treat indexes and convenience labels as generated projections.

## Promotion blockers

- The canonical Definition term has not been admitted as a Definition/v1 instance.
- External selectors CAV2-D29, CAV2-D64, CAV2-D66, CAV2-D67, Language concepts, Governance language, and Context package evidence are not admitted for CTX-00 uses.
- lab-architecture-owner, migration-owner, Governance context owner, and Ontology Lifecycle context owner are not bound in the admitted owner registry.
- The Definition Pack artifact type is candidate-unadmitted.
- No artifact-type candidates exist yet for the seven proposed context concepts.

## Successor gates

- `CTX-00-SOURCE-ADMISSION`
- `CTX-00-TERM-REVIEW`
- `CTX-00-DEFINITION-CANDIDATES`
- `CTX-00-ARTIFACT-TYPE-CANDIDATES`
- `CTX-00-OWNER-ADMISSION`

## Claim ceiling

This pack proposes seven non-collapsing context-migration meanings and records their sources, dispositions, relationships, and blockers. It does not make any term canonical, admit any external selector or artifact type, bind missing owners, create contexts/, relocate ontology-lifecycle/, authorize implementation, publish, deploy, or establish the first stable version.
