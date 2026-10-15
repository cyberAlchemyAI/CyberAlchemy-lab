# Define Authority And Governance

Status: perennial candidate. No authority effect.
Owner: CyberAlchemy v2 product owner.

In plain terms: this is a long-lived proposal. It grants no role or permission.

## Purpose

Some actions only collect or explain information. Other actions make a result
official, allow implementation, change public files, or create a real-world
effect.

**Authority** is the allowed responsibility to make one exact decision count for
one stated scope and effect.

**Governance** is the set of rules, checks, and owner decisions that keeps those
limits visible.

Routine checks should run without stopping the person. A person should be asked
when an action would change accepted meaning, executable work, public files, or
an external system.

## Authority Rules

The checked Define output bundle is called a Definition Pack.

1. Evidence may support a decision. It cannot make the decision.
2. A generated document may name an owner. It cannot appoint one.
3. A validation PASS may show that listed checks passed. It cannot approve the
   content.
4. Writing, reviewing, participating, or having access does not automatically
   give decision authority.
5. The owner responsible for the smallest relevant scope decides an action with
   real consequences.
6. A Definition Pack has authority effect none unless a separate owner decision
   grants one exact effect.
7. Registry insertion, lookup, or validation does not promote a definition or
   appoint its meaning owner.

## Owners And Decision Rights

Before the ownership table:

- a **definition candidate** is a proposed meaning under review;
- a **canonical definition** is formally accepted into
  cyberAlchemy-v2/authority/definitions/DEFINITIONS.md;
- a **runtime** is the software that would save, resume, check, and hand off a
  Define Session; and
- a **migration** is a controlled change from one owned public surface to
  another.

| Matter | Owner | May decide | May not decide through this role alone |
| --- | --- | --- | --- |
| Goal and intent | Goal owner | The wanted result, its limits, its original reason, and acceptable clarification. | Project-wide definitions or another owner's source. |
| Meaning inside an existing source | Source owner | What a term means inside that source's stated context. | Whether another team must use it. |
| Candidate Define product meaning | CyberAlchemy v2 product owner | The proposed capability, boundaries, and desired outcomes. | Canonical definition promotion or runtime acceptance. |
| Handled-definitions registry asset | CyberAlchemy v2 product owner | The candidate registry purpose, scope, and inclusion in Define. | Meaning inside a record, schema conformance, canonical promotion, or runtime persistence. |
| Handled-definition record schema | CyberAlchemy v2 Definitions Governance owner | The required record voices, disposition variants, source links, drift checks, and authority ceiling. | Meaning inside a source, contextual fitness, runtime persistence, or consumer acceptance. |
| Meaning in one handled record | Named source or decision owner | The exact meaning or open status for the stated context. | Canonical promotion, unrelated contexts, or downstream execution. |
| Definition candidate | Definitions Governance owner | Promote, revise, reject, or leave it open. | Runtime adoption or execution. |
| Define runtime | CyberAlchemy v2 Define runtime owner | Accept one exact implementation contract. | Change product meaning or external package ownership. |
| Use of a Definition Pack | Owner of the next use | Accept the pack as input for one stated use. | Promote definitions or act beyond the recorded permission limit. |
| External package migration | External package lifecycle owner plus CyberAlchemy v2 product owner | Choose exact compatibility or retirement targets. | Publish private text or change unlisted external files. |

## Minimum Governance

Define may perform the following routine actions because they do not change
accepted meaning or authority and do not create public, executable, or external
effects:

- read and compare sources;
- draft explanations;
- link evidence;
- record questions;
- route a question to a known owner; and
- run structural checks.

A separate owner decision is required to:

- change the goal, intent, or context;
- choose between conflicting owned meanings;
- promote or demote a definition;
- accept a runtime contract;
- accept a downstream use with real consequences;
- cross the public/private boundary;
- remove or deprecate an external package surface; or
- publish, release, deploy, or change an external system.

This split is called **proportionate governance**: software handles routine
checks; people decide actions with real consequences.

## Definition Pack Authority Envelope

A Definition Pack carries a short permission record. This record is called its
**authority envelope**.

The envelope states:

- who owns the goal and intent;
- who will use the pack;
- who owns each reused source;
- who must decide proposed or open meanings;
- what the pack was checked against;
- which uses are allowed;
- which actions are blocked; and
- how to challenge or refresh the pack.

The default authority effect is none. The pack cannot give itself permission.

## Challenge And Correction

A person or owner may challenge:

- a definition;
- its context or scope;
- a disposition;
- a source or evidence link;
- a relationship;
- an answer; or
- an authority claim.

The session records the challenge and routes it to the responsible owner. Until
it is resolved, the affected concept stays open or is limited to a clearly
stated use.

## Example

Example only: this does not define “customer” or authorize implementation.

For a refund feature:

- the billing source owner may explain what “customer” means in the billing
  source;
- the product owner may decide whether that meaning fits the refund context;
- Definitions Governance may decide whether a project-wide definition becomes
  canonical; and
- the engineering owner may later accept an implementation plan.

These are separate decisions. A passing Definition Pack does not grant
permission to build or deploy the refund feature.

## Claim Ceiling

This document explains candidate ownership and decision limits. It grants no
role, permission, promotion, admission, execution, publication, release,
deployment, or migration authority.
