# Fresh Session participation and host permission preflight

Candidate component for R03. This does not implement or advertise a public API
handler, create a Machine Agent, or produce a permission token for later effects.
Each dispatch must recheck current source, host permission, expiry and budgets.

## Required sources and checks

ExactSources accepts host selected original bytes, artifact references, current
postures, carrier schemas and a current byte/cut guard. Public request metadata
cannot create source facts. Whole-file original hashes remain original hashes;
an embedded source needs an explicit encoding/provenance adapter before use.
Stable references resolve one current revision; ambiguous revisions fail.

SessionEligibility verifies authenticated Principal, Project, Assignment,
Profile, Work, Intent, one-Goal Coordination Context and selected Goal sources.
An Assignment may name the selected eligible Profile or an explicitly reserved
fresh instance. It cannot silently reuse an old instance or infer permission.
Periods resolve through the host's explicit registry with absolute start and
expiry. Owner, Project, Work, declared outputs, required inputs, consumer,
source Policy and stop conditions must agree.

The host separately supplies SessionPermission, verified current evidence,
allowed operations, period bindings, revocations, budgets, protocol references
and exact Implementation source/environment bindings. An admitted carrier,
Assignment, Profile, Agent Capability, view, message or preflight result grants
no permission. The current permission is copied before checks and rechecked
afterward; changes within a mutable period registry cannot bypass this comparison.

## Capability separation

Agent Capabilities must be explicitly declared by the selected Agent Profile
and bind the exact selected Implementation revision. Contract and failure
references resolve through typed domain records or explicit protocol bindings.
Protocol bindings retain their own reference class; they do not become governed
Schema, Contract, Policy, Failure Mode or registry artifacts.

Product Capability realization remains a separate axis. It never substitutes
for an Agent Capability or a Tool/action permission. The Implementation's selected
source/environment evidence is independently verified by the host guard. Merely
listing an entrypoint or conformance claim in a body cannot satisfy that check.

## Context and memory

Session creation requires exact previously delivered current Context/Ontology
Views for the same Assignment, Work, Coordination Context, principal, source cut,
and independently provisioned authority envelope. Actual view generation and
native domain mapping are integration obligations, not functions of this module.
The original API schemas and wire/currentness/JCS dispatcher remain mandatory.

Short memory belongs only to the live Session. A schema-valid Agent Session/v1
metadata record may contain an empty memory structure with expiry=true; nonempty
input, working-record or question memory is private and ineligible as context.
Expiration policy is not persisted memory content. This exemption applies to a
validated Session carrier at its exact payload path; schemas and arbitrary nested
objects do not obtain that exemption from names alone.

## Claim limits and next wiring

Construction tests use protected original source files, actual repository carrier
schemas and explicitly isolated candidate source selections. Their host Actor
and permission are construction fixtures. They do not establish authentication,
admission, active Agent creation, native view readiness, Tool execution, human
pilot success, conformance, or a complete public Session contract.

The remaining integration must deliver actual views from the same selected API
branch and native event cut, bind fresh Machine identity and classification,
create ephemeral resources through exact durable idempotency and operation
inspection, enforce budgets/deadlines around effects, and dispose memory even
after source invalidation. Close must retain unresolved actions and honest
uncertainty after a lost process.

This package, its protocol/period rules and evidence remain independent candidate
review members in S02/R08. No intermediate owner response or admission is required
for the authorized construction fixtures.
