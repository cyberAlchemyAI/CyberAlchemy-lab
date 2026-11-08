# Craft Product Thesis

Status: **draft candidate**
Canonical kind: `CAV2-D63 Product Thesis`
Thesis ID: `CA2-PRODUCT-THESIS-CRAFT`
Product: `CA2-PRODUCT-CRAFT`
Coordinating Project: `CA2-PROJECT-CRAFT`
Building Method: `CAV2-D20`
Commitment state: **draft**
Authority effect: **none**

## Product Identity

Craft is the current name of the DomainSpec v2 Product lineage inside CyberAlchemy. It is not a separate successor
Product. The Craft Project coordinates its development and evolution, and the Craft Method defines how it builds
systems. Product, Project, and Method share the Craft name and purpose but remain separate kinds with separate
artifacts, lifecycles, and authority boundaries. Existing DomainSpec-v2 paths remain legacy provenance and
migration inputs until their bytes and authority bindings are deliberately moved.

## Parent Product Context

The broader CyberAlchemy Product Thesis frames Craft: humans and machines should build complex systems together
without losing owner control, meaning, evidence boundaries, or visible continuation. Craft specializes that
proposition around the act of turning Product intent into an evidence-bearing working system.

## Thesis

Craft helps an owner turn typed Product intent and domain meaning into a working system, compare independent
evidence with the expected behavior, and use the result to continue, repair, revise, or stop. It preserves the
selected realization, evidence, recovery obligations, and responsible owner as construction and evolution proceed.

```text
typed intent + meaning + expected behavior
                   |
                   v
selected realization -> deterministic construction -> independent evidence
          ^                                                   |
          |                                                   v
          +---- repair / revise <- compare with expectations -> continue / stop
                                         |
                                         v
                         retain evidence + recovery + owner handoff
```

The comparison can support an expectation, contradict it, or leave it unknown. Revising meaning belongs to its
owner; a failed check does not authorize changing the intended behavior. This is the draft product promise,
not evidence that the complete loop is implemented. The [construction feedback explanation](../docs/construction-feedback-loop.md)
develops the stages, a concrete example, and the checks that could challenge the promise.

## Problem

Product purpose, feature decisions, domain meaning, architecture, implementation, operation, and evidence are
fragmented across tools and handoffs. Teams repeatedly rediscover choices, generators silently pick implementation
details, static checks miss runtime truth, and later changes drift from the meaning that justified the system.

## Value Proposition

Craft helps an owner turn a Product Feature into a working, explainable system whose implementation traces to its
meaning, whose observed behavior can be compared with expectations, and whose changes retain evidence, recovery
obligations, and owner control.

## Value Mechanism

Craft creates value by embodying `CAV2-D20 Craft Method`: resolve the Product and Project context; define shared
meaning; model Product Features, Product Capabilities, and business obligations; express the system in DomainSpec;
select exact architecture and language-profile realizations; construct deterministically; validate independently;
observe bounded runtime truth; compare the evidence with declared expectations; use that assessment to continue,
repair, revise through the responsible owner, or stop; and retain evidence, recovery and evolution obligations,
residue, and successor state for explicit owners.

## Product, Project, Method, And Feature

- The **Product** owns this value proposition and supplies context for its Product Features.
- The **Project** coordinates the goals, owners, evidence, decisions, and work used to develop the Product.
- The **Method** owns the repeatable system-building discipline.
- A **Product Feature** is a candidate product-local unit shaped inside the Product context; it is not yet a
  canonical CyberAlchemy kind.
- A **Product Capability** is the admitted `CAV2-D67` stable outcome kind and must not be silently equated with a
  Product Feature.

## First-Order Principles

1. Product purpose and feature context precede construction.
2. Product, Project, Method, Feature, Capability, realization, and evidence remain distinct identities.
3. Owners retain authority over meaning and consequential adoption decisions.
4. Exact realization selection is explicit and machine-checkable.
5. Construction is deterministic and dependency-closed.
6. Conformance observation remains independent from construction.
7. Runtime evidence is bounded, attributable, and replay-safe where required.
8. Evidence never becomes authority by accumulation.
9. Recovery, compensation, rollback, migration, and safe evolution are product behavior.
10. Construction and validation machinery remain replaceable.

## Intended Outcomes

- **Continuity** — implementation obligations trace to Product and domain meaning.
- **Construction speed** — reusable exact realizations reduce recurring architecture work.
- **Conformance** — declared structural, relational, and runtime drift is detected.
- **Evolvability** — change and recovery preserve explicit contracts and residue.
- **Replaceability** — runtimes and generators can change without losing source meaning.
- **Human control** — owners can understand, challenge, accept, or reject consequential transitions.

## DomainSpec v2 Rename And Continuity

DomainSpec v2 is Craft's former name and the label retained by the current source and implementation paths. Its
meta-type, language-profile, construction, conformance, operation, workflow, recovery, and integration assets
belong to the same Product lineage. Migration must classify exact legacy assets as moved current capability,
archived provenance, separately owned dependency, or rejected residue. The naming decision does not itself move
files, change imports, redirect consumers, relocate authority, or delete legacy sources.

## Evidence Strategy

Test the thesis through exact preservation of selected working DomainSpec capabilities; one bounded Product
Feature constructed into a target system; deterministic replay and artifact identity; independent static and
runtime conformance; recovery, compensation, migration, and rollback evidence; and measured owner, builder,
operator, and reviewer burden.

One successful target cannot prove the thesis. Failure must distinguish a defective realization from
counterevidence against the Product or Method.

## Open Product Decisions

1. What is the first bounded user and Product Feature slice?
2. Should Product Feature become a canonical kind, and how does it relate to Product Capability?
3. Which DomainSpec-v2 assets move under Craft paths, remain archived provenance, stay separately owned, or are rejected?
4. Which ontology and architecture contracts are mandatory before construction begins?
5. What is the first runtime evidence boundary beyond static conformance?
6. What exact migration plan moves physical paths and authority bindings while preserving product-lineage continuity?
7. Is the shared Craft name sufficiently clear across Product, Project, Method, public capability, and ledger state?

## Revision Criteria

Revise the Product realization—and, when evidence is systemic, this thesis or the Method—when continuity costs
more than it saves, owners cannot distinguish source meaning from projections, exact realization prevents useful
adaptation without evidence benefit, construction cannot integrate with real projects, conformance duplicates
construction defects, runtime observations cannot stay bounded, safe evolution cannot be preserved, or a simpler
Product and Method preserve the same guarantees.

## Claim Ceiling

This package establishes the private Craft Product identity and starts its draft Product Thesis, linked to the
separate Craft Project and canonical Craft Method, and records DomainSpec v2 as its former name. It does not commit
the thesis, canonically define or admit a Product Feature, physically migrate or delete legacy DomainSpec-v2
paths, relocate authority, select architecture, implement a system, prove product value, publish, release, deploy,
or grant production authority.
