[Documentation home](../../README.md)

# Work-State Continuity Capability

<a id="def-cal-definition-work-state-continuity-capability"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Work-State Continuity Capability

# Work-State Continuity Capability

Supports resuming work from saved state and records instead of relying on a participant’s recollection of the conversation.

**When it applies**

Use the Craft execution surface when continuing CyberAlchemy v2 work from structured state. The source of truth is `Craft ledger`; `CRAFT.md` and `Craft index` are derived navigation surfaces.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-work-state-continuity-capability-section-2"></a>

## Source explanatory wording

It lets work resume from recorded state instead of relying on somebody remembering the conversation.

<a id="def-cal-definition-work-state-continuity-capability-section-3"></a>

## Exact governing statement

Work-State Continuity Capability is the normalized product-capability identified by semantic.work-state-continuity-capability, owned within scope.product, and carried by type.product-capability. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D12, CAV2-D20 without silently merging it with another target.

Target-specific normative meaning:

Work-State Continuity Capability is the ability to preserve and reconstruct current work state across people, agents, sessions, interruptions, and child contexts from one declared ledger containing decisions, blockers, evidence, artifacts, residue, and next routes.

Bound source-semantic basis:

A Craft execution surface is the project-local Craft ledger, derived index, and linked human view used to record recursive work state, blockers, decisions, candidate definitions, gaps, artifacts, next moves, and recomposition evidence for a bounded project scope.

Craft method is CyberAlchemy's governed recursive system-building method. It turns owner-controlled Product intent into an evidence-bounded working system by preserving one explicit chain through context, definitions, product and business meaning, system specification, exact realization selection, deterministic construction, independent conformance, bounded operation, recovery, evolution, and owner continuation.

The method uses a source-of-truth ledger to preserve state across that chain. It records contexts, candidate definitions, blockers, enablers, decisions, gaps, artifacts, next moves, validation evidence, residue, and recomposition obligations. Ledgering is the method's continuity mechanism; it is not the whole method.

In CyberAlchemy v2, Craft method is valid only when it preserves these boundaries:

- a Product and its Product Thesis own product purpose and value propositions - a Project coordinates the goals, owners, evidence, decisions, and work used to develop or evolve the Product - Product Features and Product Capabilities remain distinct from the Product, Project, Method, and their realizations - canonical definitions, product and business ontology, DomainSpec source, generated system ontology, realization selection, construction, conformance, runtime evidence, and owner decisions remain separately identifiable - every implementation-bearing construction follows the exact `CAV2-D65` DomainSpec-governed construction chain or carries typed residue for the missing prerequisite - `Craft ledger` or an equivalent declared ledger is the source of truth for Craft state - `CRAFT.md`, `Craft index`, projections, and status output are derived views - residue is typed and carried forward instead of hidden - schema-level and instance-level validation are not collapsed - child contexts recompose into their parent through evidence - closure happens by owner decision, gate, or accepted residue, not by a claim of total final completion - Craft state can carry local candidate definitions and receipts but cannot make terms canonical without definitions-governance

````
For a bounded Product and Project scope `S`, the Craft method has the minimum
governed shape:

```text
M_Craft(S) =
  (context, product_intent, domain_meaning, system_specification,
   realization_selection, construction, conformance, operation,
   recovery_and_evolution, owner_continuation, ledger_state)

L_S = (C, B, E, D, G, A, N, R)
```

where:

- `context` resolves the Product, Project, Goal, participants, consumers, and
  source policies relevant to the bounded work
- `product_intent` carries the Product Thesis plus selected Product Feature or
  Product Capability obligations
- `domain_meaning` carries canonical definitions and product/business ontology
- `system_specification` carries DomainSpec and generated system-ontology state
- `realization_selection` identifies exact architecture and language-profile
  realizations
- `construction` materializes the selected contained target deterministically
- `conformance` independently evaluates declared static and relational
  obligations
- `operation` supplies bounded runtime evidence without becoming authority
- `recovery_and_evolution` preserves compensation, recovery, migration,
  rollback, compatibility, and successor-state obligations
- `owner_continuation` routes an evidenced next state to its explicit owner
- `C` is the set of contexts or child contexts
- `B` is blockers
- `E` is enablers or available evidence
- `D` is decisions
- `G` is gaps or unresolved obligations
- `A` is artifacts and source references
- `N` is next moves or route obligations
- `R` is typed residue plus recomposition evidence

A Craft step is admissible when it preserves typed identity and source
authority, records the operation that changed state, keeps generated views
derivative, validates every reachable declared consumer, and either repairs,
types, routes, accepts, or defers residue with an owner. Construction does not
establish conformance; conformance does not establish runtime truth; evidence
does not establish owner adoption or permission.

Formal-foundations evidence supports this shape by treating residue as typed and
composable, by separating schema-fidelity from instance-fidelity, by showing
that reflection towers assemble without finite total closure, and by justifying
stop criteria based on decision and residue plateau rather than completion. This
is support evidence for the method; it does not prove that an LLM-centered Craft
run achieved a clean functor, kernel, or zero-residue translation.
````

- Craft can carry local candidate definitions and receipts, but it does not make terms canonical and does not replace definitions-governance, constitution-governance, decision-gate, or task-session.
- Craft method is not the Craft Product, Craft Project, a Product Feature, Product Capability, Product Thesis, DomainSpec model, architecture pattern, generator, runtime, public Arcanum capability, `.craft` state, generic task runner, or replacement for task-session. It is not a source of canonical definitions and does not authorize implementation or prove that a translation, construction, conformance assessment, operation, recovery, or migration is complete. It may use formal foundations as support evidence, but it must preserve their honesty boundary: formal cousins describe the structure Craft operates inside; they do not certify that a particular Craft run achieved the clean formal case. Craft method also does not promote `ledger` as a cross-method primitive by itself. Ledger remains separately flagged for review until recursivity, relation inheritance, and local Craft ledger conformance are settled.
- This target remains distinct from the sibling targets semantic.cyberalchemy-construction-method, semantic.residue-escalation-method reconstructed from CAV2-D20; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/902aca01d397-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.work-state-continuity-capability@1.0.0-candidate.1

**Content fingerprint · SHA-256**

902aca01d397ab35c525aaa9c25f05b11dc92bde3ba9a5bc43cf71b264f44469

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use the Craft execution surface when continuing CyberAlchemy v2 work from\nstructured state. The source of truth is `Craft ledger`; `CRAFT.md` and\n`Craft index` are derived navigation surfaces.\n\nUse Craft method whenever CyberAlchemy builds or materially evolves a Product,\nProduct Feature, Product Capability, system, or implementation-bearing\ncapability. Begin from the Product and Project context, define the meaning,\nmodel the product and business obligations, author or update the DomainSpec\nsource, select exact realizations, construct the target, independently check it,\nobserve bounded runtime behavior, preserve recovery and evolution obligations,\nand route the evidenced state to its owner.\n\nThe same method provides durable work memory across sessions, definition towers,\nauthority imports, constitution towers, research packets, promotion queues, and\nnested project spaces. A human or agent should be able to continue without\nguessing what is blocked, what is merely candidate, what has evidence, what was\nconstructed, and what must recompose upward.",
  "authority_scope_ref": "scope.product",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
