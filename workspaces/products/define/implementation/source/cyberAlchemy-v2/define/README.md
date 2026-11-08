# CyberAlchemy v2 Define

Status: private candidate package. No authority effect.

In plain terms: this is a private proposal under review. These files grant no
permission to change, publish, execute, or deploy anything.

## Start with a real problem

A team wants to add refunds to an online shop. Before it starts, the team notices
that the word “customer” is unclear. It could mean the buyer, the account owner,
or the person who received the product.

The same problem can appear after work has started. A developer, designer, or
reviewer may discover that two parts of the project use “customer” differently.

Define handles this problem. It helps people and tools identify and clarify the
important terms, where they apply, who owns them, where current information came
from, and what is still unanswered. This can happen before work starts or while
it continues.

Example only: this refund scenario does not define “customer” or authorize
implementation.

## What Define records

Define keeps these concrete items together:

| Item | What it means |
| --- | --- |
| Goal | The specific result wanted, including its limits. |
| Intent | The original reason for the goal. |
| Context | Where the work applies: for example, one product, feature, domain, user group, or time period. |
| Concept | An important term or idea that the work depends on. |
| Source | The exact document, record, or system where information came from. |
| Evidence | Information used to support a statement or decision. |
| Owner | The person or role allowed to decide one exact matter. |
| Open question | Something important that is still unknown, unclear, or disputed. |

For every required concept, Define records one handling choice. The package calls
this choice a **disposition**:

- reuse: an existing owned definition fits this context;
- specialize: an existing definition fits after its context is narrowed;
- propose: a new candidate definition is needed; or
- open: the answer is not ready and the question remains visible.

## What Define produces

Define produces a checked bundle containing the goal, intent, context, concepts,
sources, evidence, owners, dispositions, and open questions. This bundle is
called a **Definition Pack**.

The named person, team, or tool that uses the pack is its **consumer**. The
consumer decides whether the pack is useful input for one stated use. The pack
does not choose the consumer's product, design, or technical solution.

## Handled-definitions registry

[handled-definitions.json](handled-definitions.json) is a separate candidate
registry for semantic handling records created by Define in a bounded context.
Each future record must carry exactly one disposition—reuse, specialize,
propose, or open—together with its sources, decision owner, consumers, and
challenge or refresh route. The registry is initially empty; this slice does
not invent a domain definition merely to demonstrate storage.

This registry is not [definitions.json](definitions.json). The latter describes
the vocabulary used by the Define package itself. Neither registry is the
canonical definition store, and neither may promote a definition by insertion.

## Construction handoff registry

[construction-handoffs.json](construction-handoffs.json) is the Define-owned
boundary between validated business meaning and an exact DomainSpec project,
profile, language, and source set. It does not own the complete
`ConstructionBinding`; that record is owned by its Project in
[the Goals package](../goals/bindings/construction-bindings.json).

The handoff registry is empty and blocked. The current DomainSpec compilation
check is not evaluable, so existing local node and relation files are not
treated as compiler output or as a generated system ontology.

## When Define is used

Define is not only an upfront stage.

- Before work starts, it can expose unclear concepts and missing context.
- While work continues, it can answer new questions or record them as open.
- After evidence or context changes, it can refresh an existing Definition Pack.

Define is also not mandatory before every design or implementation task. Use it
when unclear or unstable concepts would cause guessing, rework, or an ownership
conflict.

## Read the documents

1. [docs/PRODUCT.md](docs/PRODUCT.md) — what Define should do, why it matters,
   and how it fits inside CyberAlchemy.
2. [docs/DEFINE.md](docs/DEFINE.md) — the capability, its inputs, work, result,
   boundaries, and owners.
3. [docs/LIFECYCLE.md](docs/LIFECYCLE.md) — the states of the Define package and
   one Define session.
4. [docs/AUTHORITY.md](docs/AUTHORITY.md) — who may decide what and when a
   separate decision is required.
5. [docs/DEFINITION-PACK.md](docs/DEFINITION-PACK.md) — the output fields and
   checks.
6. [docs/INTERACTION.md](docs/INTERACTION.md) — how one saved session appears in
   the CLI and chat.

[documents.json](documents.json) records each document's ID, owner, intended
type, expected lifetime, authority state, required headings, and current blocker.

## Module and CyberAlchemy link

[module.json](module.json) records that Define is a private part of
CyberAlchemy. It links Define to the wider
[CyberAlchemy Product Thesis](../product/PRODUCT-THESIS.md) and candidate
[CyberAlchemy product ontology](../ontology/product/README.md). It also lists
the business, system, and bridge models that belong to Define.

CyberAlchemy owns the wider product promise. Define explains one part of that
promise: how people and machines make important meaning clear before work moves
on. The link does not let Define change CyberAlchemy, and it does not make Define
the whole product or give anyone permission to act.

## Ontology packages

Define now separates product meaning, proposed runtime structure, and their
alignment:

- [business-ontology/](business-ontology/) owns the private
  `business-domain` ontology: 9 product-meaning nodes and 8 business
  relations;
- [system-ontology/](system-ontology/) owns the private `system-runtime`
  ontology: 65 DomainSpec-typed nodes and 131 source-owned relations; and
- this parent package owns only the `business-system-bridge`: two bridge nodes,
  thirteen cross-package relations, an empty construction-handoff registry,
  and explicit evidence gaps.

Each child has its own profile, sources, schema bindings, validator, and
append-only receipt history. The parent excludes child material bytes from its
own digest while validating each declared child identity, current receipt, and
cross-package endpoint.

## Document status

These files are intended to be long-lived and kept up to date. CyberAlchemy calls
that **perennial**.

They are still **canonical-document candidates**. They are not admitted canonical
artifacts and they grant no decision rights.

Candidate does not mean unsupported. It means the material has not crossed the
separate owner-controlled promotion step.

CAV2-D51 says a canonical artifact must have:

1. a recognized artifact type; and
2. an owner-approved process that produced it.

The current type table does not approve a creation process for this exact Define
document set. Putting files in this folder cannot approve them.

## Evidence already used

This package is built from prior CyberAlchemy, Arcanum, and DomainSpec work. It
is not a definition written without evidence.

The current package records 25 exact sources. They include:

- 11 active CAV2 definitions for ontology, method, definition, authority,
  claim-to-proof limits, intent, promotion, canonical artifacts, durability,
  and schema;
- the CAV2 product thesis, product ontology, authority model, source rules, and
  package model;
- the standalone Define CLI contract, capability, compiled Alch runtime,
  implementation binding, and realization record; and
- the current Define system ontology, including its profile, nodes, and
  relations.

The package validator checks that those exact sources and selected text
locations still exist and that their recorded bytes have not changed.
Historical PASS receipts remain immutable history; they do not cover the
refactored bridge bytes or clear current source drift.

Together, this evidence supports the need for Define, its concepts, its method,
its authority limits, its output structure, and its relationship to existing
mechanics. It does not yet establish measured outcomes from people using the
finished CyberAlchemy Define product.

## Source order

If two files disagree, use this order and record the disagreement:

1. cyberAlchemy-v2/authority/definitions/DEFINITIONS.md owns formally accepted
   CyberAlchemy v2 terms.
2. [definitions.json](definitions.json) holds the four Define definition
   candidates. It does not allocate canonical CAV2-D* IDs.
3. [handled-definitions.json](handled-definitions.json) holds candidate
   context-bound handling records produced by Define; it is currently empty.
4. [module.json](module.json) locates Define inside CyberAlchemy;
   [business-ontology/](business-ontology/) owns product meaning,
   [system-ontology/](system-ontology/) owns the proposed runtime, and
   [construction-handoffs.json](construction-handoffs.json),
   [profile.json](profile.json), [nodes.json](nodes.json),
   [relations.json](relations.json), [views.json](views.json), and
   [migration/runtime-rebinding-v1.json](migration/runtime-rebinding-v1.json) hold their bridge and package
   lifecycle model.
5. The files under docs/ explain that model for people.
6. This README introduces and links the package.

A human-readable document cannot silently change a machine record. A changed
definition, relationship, owner, status, or permission limit must also change
the machine-readable source that owns it.

## Product and runtime boundary

CyberAlchemy v2 owns this proposal for what Define should do and why.

The standalone Define CLI supplies the candidate implementation: conversational
intake, durable shared sessions, Alch-authored semantic gates, Definition Pack
handoff, source-linked ontology, and Craft/DomainSpec compilation. CyberAlchemy
continues to own the product meaning and authority boundary.

[migration/runtime-rebinding-v1.json](migration/runtime-rebinding-v1.json)
records the exact candidate rebinding. Local implementation evidence does not
establish behavioral conformance, adoption, activation, or publication.

## Validate

From the repository root:

    python3 cyberAlchemy-v2/define/scripts/validate.py

The validator checks the parent file boundary, child identities and current
receipts, document headings, exact source versions, package vocabulary,
handled-definition registry separation, the empty blocked construction-handoff
registry and its Project ownership boundary, cross-package relationships,
open-gap references, permission limits, and historical parent receipt integrity.

## Claim ceiling

A PASS would say the parent bridge and both declared children are internally
coherent and still match their recorded sources. The current parent result
remains BLOCKED by upstream source currency and child receipt or validation
gates. Child PASS or FLAG results do not clear those blockers. No result here makes the documents
canonical, promotes a definition, proves the interactive runtime, removes
an external package, creates a ConstructionBinding, claims compiler output or a generated
system ontology, publishes, releases, deploys, or establishes measured product outcomes.
