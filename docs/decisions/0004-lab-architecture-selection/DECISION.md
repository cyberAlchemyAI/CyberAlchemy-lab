<!-- Generated from decision.json. Do not edit this projection directly. -->

# CyberAlchemy Lab architecture selection

- Decision: `CAL-DECISION-0004-LAB-ARCHITECTURE-SELECTION`
- Status: `owner-selected`
- Decision posture: `selected`
- Authority effect: `architecture-planning-selection-only`
- Selected option: `CML00-ACCEPT`
- Selected at: `2026-09-01T01:09:20Z`

## Decision Gate result

- Result: `PASS`
- Phase: `CML-00-SELECT-LAB-ARCHITECTURE`
- Phase result: `complete-planning`
- Blocker decisions resolved: `1`
- Blocker decisions remaining: `0`
- Admissibility request: `admissibility-request.json` (`sha256:e680fae62b0142116624ee97eb9a4e999e7606f2a9f7cbc17086ac52ff35f056`)
- Request digest: `577a4d49217a591030de2de52ea540aa8633a7ab05aac19151b699be1ee658d7`
- Admissibility receipt: `admissibility-receipt.json` (`sha256:b5db0b2c99d1c72c9c8f9f707e7e940624850b1d73a518c0b9e3fd96a0b63f67`)

The exact architecture graph, candidate path model, owner-role separation contract, RN-2 naming policy, and LEANS-2 phase DAG are selected as the CyberAlchemy Lab planning baseline.

## Accepted candidate

- `docs/decisions/0004-lab-architecture-selection/candidate.json` (`sha256:4977c0225e68de5f7122cb5f05ff5e562d90f5a9908b687533aa96c69ba5a596`)

## Accepted architecture graph

- `CAL-PROP-0001` — `docs/proposals/0001-context-artifact-architecture/proposal.json` (`sha256:c4174297bfa71818012b77848a7cb8560b47d303b30f062144f2dc03c478932f`)
- `CAL-PROP-0002` — `docs/proposals/0002-platform-environment-architecture/proposal.json` (`sha256:cd1b51802aba4dba2c6cbd765f6a5dd000487919530e0fdaaf2b8ba81aa9485b`)
- `CAL-PROP-0003` — `docs/proposals/0003-craft-migration/proposal.json` (`sha256:22e9d945adee809190c0ae75a7e455110a45f857372ca529a6c8dbfb58220dfc`)

## Bound owner decisions

- `CAL-DECISION-0002:RN-2`
- `CAL-DECISION-0003-LEAN-SEQUENCING:LEANS-2`

## Rationale

Accept the RN-2-aligned context/artifact, platform/environment, and Craft migration architecture graph with LEANS-2 sequencing as one immutable planning baseline.

## Owner-role posture

The CAL-PROP-0001 owner-role registry is constituted as a separation-of-authorities contract. Binding accountable identities, scopes, and execution credentials remains a successor prerequisite and cannot collapse distinct decision or evidence roles.

## Non-effects

- The accepted proposal and candidate bytes remain immutable; their embedded draft and blocked posture records describe the pre-decision candidate epoch and are not rewritten.
- This decision does not admit an artifact type, external source, definition, invariant, FormalClaim, Lean result, runtime, implementation, construction binding, conformance result, or release baseline.
- This decision does not authorize CML-01, migration, implementation, installation, network access, filesystem scope beyond this decision pair, Git operations, publication, release, or deployment.
- The candidate CyberAlchemy governance runtime does not supply, expand, or enforce this owner decision.

## Successor blockers

- CML-01 requires a new exact owner-directed implementation authorization under an implementation route.
- Accountable identities and exact execution scopes must be bound to the selected owner roles before they exercise successor authority.
- Artifact mechanics, schemas, deterministic generators, source-admission records, validators, and negative witnesses remain unimplemented and unadmitted.

## Claim ceiling

Decision Gate PASS and CML-00 complete-planning apply only to the exact accepted architecture graph. They do not register admitted execution state, authorize CML-01, prove CAV2-D65 construction, establish conformance, publish, release, deploy, or establish the first stable version.

