# CyberAlchemy v2 Define System Runtime Ontology

Status: private candidate; not implemented; authority effect none.

This durable package models the proposed CyberAlchemy v2 Define session runtime
using the current DomainSpec v2 `complete-backend-criteria@2` candidate profile.
Its stable ontology identity is `cav2.define.system-runtime.v1`, its only branch
is `system`, and its owner route is the CyberAlchemy v2 Define runtime owner.

The machine source is the package-local DomainSpec project under
[`domainspec-project/`](domainspec-project/). [`NODES.json`](NODES.json) and
[`RELATIONS.json`](RELATIONS.json) are checked indexes of that per-node source;
they do not own a second graph. [`VIEWS.json`](VIEWS.json) defines the six
Design navigation views over that graph. The bounded discovery architecture is
under [`design/`](design/); it is not a governed Design bundle. This
README is derived navigation.

## Runtime model

The graph distinguishes:

- identity-bearing `DefineSession`, `DefineQuestion`, `DefineAnswer`, and
  `DefinitionPack` entities plus provenance-bearing context candidates and
  sufficiency evaluations;
- session-scope and authority-envelope value objects plus explicit question
  states;
- CLI and chat interfaces over one shared session;
- create, resolve context, evaluate sufficiency, request more context, open,
  record, defer, resume, validate, and export operations;
- inspect-session, current-question, and open-gaps queries;
- same-session/question, answer-authority, silence-is-not-answer, and
  exact-disposition rules;
- failure-recovery and authority-ceiling policies;
- one Define session workflow, lifecycle state machine, lifecycle events, and
  CLI/chat mappings.

The current expansion adds technology-neutral runtime contracts for:

- exact session revisions, schema versions, actor access context, and
  compare-and-commit persistence;
- one shared transport port and one repository port without choosing their
  protocol or backend;
- explicit saved and rejected outcomes, retry idempotency, conflict detection,
  and last-confirmed-state recovery;
- access/privacy, retention, telemetry, proportional governance,
  accessibility, and SLO policies without inventing owner-controlled values;
- a persistence mapping that must preserve session meaning and authority; and
- an explicit private Arcanum substrate boundary without authorizing public
  migration; and
- a private semantic-evaluator port that treats the existing Agent Reasoning
  Engine witness as bounded feasibility evidence, not a completed Define
  adapter or authority source.

Only active signatures in the exact DomainSpec relationship registry are used.
The source-owned connections are validated against endpoint kinds as well as
the exact registry digest.

## Lifecycle and interaction

```text
create session -> explicit context + references
       -> current-window candidates when needed
       -> saved-session candidates when still needed
       -> evaluate: sufficient | insufficient | indeterminate
       -> insufficient/indeterminate: request more context
       -> sufficient: open question -> record answer | defer question
       ^                                  |
       +----------- resume --------------+
                         -> compare revision -> save confirmed state
                         -> validate pack -> export pack
```

Each lifecycle-changing operation produces a past-fact event, and those events
transition the proposed session state machine. CLI and chat expose behavior over
the same session identities. A state-changing result is complete only after its
revision and digest are confirmed. Silence is not an answer; validation does
not approve content; export preserves open gaps and authority effect none.

## Discovery Design boundary

The design subpackage contains 42 typed design records, 38 relationships, six
views, ten owner-routed gaps, and twelve unexecuted witness contracts. It reuses
the DomainSpec architecture ontology experiment, BTE Design, BTE Design input
selection, and Define CLI model as evidence-only precedents. Normal Invoke
Design W1-W3 activation is not claimed because no exact owner-approved input
boundary and no admitted Define v3 result were supplied.

## DomainSpec v2 boundary

The project binds `complete-backend-criteria@2`, the exact current kind and
relationship registry digests, the formation projection digest, and the
current implementation snapshot. That profile is `candidate` with
`release_admission: not-granted`. The current minted-project compiler/minter
does not establish a full v2 conformance path, so compilation is
`not_evaluable`; validation must report `FLAG`, never `PASS`, while this remains
true. No DomainSpec source or runtime is changed here.

## Parent Define package boundary

The parent Define bridge declares `system-ontology/` as an independently
owned nested child package. Its profile, validator, receipt history, ontology
identity, root node, owner, visibility, and authority ceiling are explicit
parent bindings; its material bytes remain outside the parent material digest.
Nested-package admission does not establish implementation, compiler
conformance, parent PASS, release admission, or any other authority.

The package-local `domainspec-project/project.json` remains a DomainSpec
minted-project manifest, not a `CAV2-D60` Project. The CAV2 Project package now
defines a separate recursive-instance binding registry, but no Define Project
or binding is registered there. `RES-CAV2-DEFINE-SYS-005` preserves the missing
Project identity, exact parent version and contract, owner-qualified authority
claims, and adoption decision.

## Validate

From the repository root:

```sh
python3 cyberAlchemy-v2/define/system-ontology/scripts/validate.py
```

The dependency-free command is check-only. It validates the closed child
inventory, JSON records, exact source currency, DomainSpec source and formation
shapes, kind and relationship signatures, endpoint and six-view closure,
one-to-one index agreement, the deterministic discovery Design subpackage,
residue, receipt currency, and claim ceilings. Receipts are append-only and
must be materialized separately.

## Claim ceiling

A structurally clean run supports only a private, source-current candidate
model and discovery architecture. It does not establish implemented
persistence, CLI/chat synchronization, security, accessibility, recovery,
numeric SLOs, witness execution, governed Design, runtime conformance,
profile or release admission, parent package PASS, canonical definitions,
execution, publication, release, deployment, or an external effect.
