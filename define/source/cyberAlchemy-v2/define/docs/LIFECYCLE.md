# Define Lifecycles

Status: perennial candidate. No authority effect.
Owners: CyberAlchemy v2 product owner and CyberAlchemy v2 Define runtime owner.

In plain terms: this is a long-lived proposal. It grants no permission to act.
The product owner controls the proposed capability meaning. The runtime owner
controls the software contract.

## Purpose

A **lifecycle** is an ordered set of states. It shows where something is now,
what may happen next, who decides, and what each state proves.

Define has two separate lifecycles:

1. the lifecycle of the Define package and its documents; and
2. the lifecycle of one saved Define session.

Keeping them separate matters. A completed session does not approve the package,
promote a definition, or accept a runtime.

## Handled Definition Record Lifecycle

A handled-definition record belongs to one explicit concept, context, and
intended use. It begins as one of four dispositions: reuse, specialize, propose,
or open. A later material change creates a successor record; it does not rewrite
the earlier source state. At most one record for the same concept and context is
current.

Reuse must retain the exact canonical source state. Specialize and propose remain
candidates with all required definition voices and boundaries. Open retains the
question, affected use, stop decision, and next action without inventing a
normative definition. Supersession, validation, or registry presence does not
promote a record or implement persistence.

## Product Asset Lifecycle

The **product asset** is this Define package: its documents, machine-readable
records, schema, validator, and receipts.

In this lifecycle:

- **promoted** means formally accepted into the canonical definition store;
- **runtime adopted** means the runtime owner accepted one exact software
  contract; and
- **runtime rebound** means current capability records identify the standalone
  Define runtime without implying conformance or adoption.

It moves through these states:

    source evidence pinned
      -> candidate package authored
      -> candidate package validated
      -> product owner reviewed
      -> definitions promoted by a separate decision
      -> runtime adopted by a separate decision
      -> runtime rebound to exact candidate bytes

| State | Concrete result | Owner | What is still not proved |
| --- | --- | --- | --- |
| Source evidence pinned | Exact source files, versions, and text locations are recorded. | Define package author | The product meaning is correct. |
| Candidate package authored | A private proposal exists as a complete file set. | CyberAlchemy v2 product owner | The proposal is canonical or implemented. |
| Candidate package validated | Required files, fields, links, and current sources pass their checks. | Independent package validator | The proposal is correct, valuable, or approved. |
| Product owner reviewed | The product owner accepts one exact proposal for further review. | CyberAlchemy v2 product owner | Definitions are canonical or implementation may start. |
| Definitions promoted | Exact definition candidates enter the canonical definition store. | Definitions Governance owner | A runtime is accepted. |
| Runtime rebound | Current capability records identify one exact standalone runtime. | Define capability owner | Behavioral conformance or adoption is proved. |
| Runtime adopted | One exact runtime contract is accepted. | Define runtime owner | Anything is published, released, or deployed. |

The current package state is **candidate package validated**. Its PASS receipt
says the files are complete, connected, structurally valid, and current against
their recorded sources. Candidate means the package has not crossed the later
owner review and promotion steps; it does not mean the package lacks evidence.

## Define Session Lifecycle

A **Define Session** is the saved record for one goal. It keeps the goal, intent,
context, concepts, questions, answers, sources, owners, and handling choices
together. Those handling choices are called dispositions: reuse, specialize,
propose, or open.

The proposed session states are:

    created
      -> goal, intent, and context recorded
      -> sources and required concepts found
      -> questions opened, answered, deferred, or routed
      -> one disposition recorded for each concept
      -> Definition Pack checked
      -> pack handed to the named person, team, or tool
      -> session refreshed or closed

Creating a session only gives it an ID. It does not show that any concept is
correct or accepted.

The CyberAlchemy runtime does not implement this full lifecycle yet.

## Stop Conditions

Define stops and asks for an owner decision when:

- the goal, intent, or context is disputed;
- two owners give incompatible meanings for the same context;
- a proposed disposition would overwrite canonical meaning;
- a question would change product meaning, who may decide, or what effect is
  allowed;
- the next action would pass the recorded permission limit; or
- required evidence cannot be found and the next use cannot accept that gap.

Stopping is not failure. The session keeps the question, reason, owner, and next
step visible.

## Example

Example only: this does not define “customer,” appoint a real billing-domain
owner, or authorize implementation.

One refund session may move through these states:

    created
      -> goal recorded: “customer can request a refund”
      -> intent recorded: “reduce support work safely”
      -> context recorded: “online-shop refund eligibility”
      -> “customer” found to be unclear
      -> question routed to a suggested billing-domain owner
      -> gift-recipient refund remains open
      -> pack checked and sent to product and engineering

This may close one Define session. It does not make “customer” a canonical
CyberAlchemy definition. Definitions Governance must decide that separately.

## Claim Ceiling

These lifecycle descriptions do not prove an implemented state machine, saved
runtime state, CLI and chat synchronization, definition promotion, runtime
adoption, or any external package migration.
