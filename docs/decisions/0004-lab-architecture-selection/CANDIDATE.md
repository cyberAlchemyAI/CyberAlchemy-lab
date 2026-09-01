<!-- Generated from candidate.json. Do not edit this projection directly. -->

# CyberAlchemy Lab architecture selection

- Decision: `CAL-DECISION-0004-LAB-ARCHITECTURE-SELECTION`
- Status: `awaiting-owner-selection`
- Decision posture: `not-selected`
- Authority effect: `none`

## Exact architecture graph

- `CAL-PROP-0001` — `docs/proposals/0001-context-artifact-architecture/proposal.json` (`sha256:c4174297bfa71818012b77848a7cb8560b47d303b30f062144f2dc03c478932f`); context-artifact-owner-path-and-recursion-model
- `CAL-PROP-0002` — `docs/proposals/0002-platform-environment-architecture/proposal.json` (`sha256:cd1b51802aba4dba2c6cbd765f6a5dd000487919530e0fdaaf2b8ba81aa9485b`); language-tool-runtime-profile-environment-and-lock-model
- `CAL-PROP-0003` — `docs/proposals/0003-craft-migration/proposal.json` (`sha256:22e9d945adee809190c0ae75a7e455110a45f857372ca529a6c8dbfb58220dfc`); migration-boundaries-phase-dag-and-claim-ceiling

## Bound owner decisions

- `CAL-DECISION-0002:RN-2` — Active product and specification naming is Craft or neutral while stable DS identifiers remain lineage IDs.
- `CAL-DECISION-0003-LEAN-SEQUENCING:LEANS-2` (`sha256:91f4a2fb282ddc3649dda673e46dbb3cd52d8bd261944e17f2d87c90765b319d`) — Lean evidence is a parallel non-blocking branch after semantic snapshot acceptance.

## Selected architecture properties

- Machine records are canonical and checked-in human views are deterministic generated projections.
- Artifact semantics, authority, ownership, schema, lifecycle, context, capability, Product, Project, module, package, and directory are orthogonal axes.
- The full recursive envelope belongs to a capability instance; the whole repository form is not copied recursively.
- Product and Governance are not inferred to be DDD Bounded Contexts.
- Craft Product identity and Project coordination have separate carriers.
- Active capability-instance authored and compiled source lives under specification/, not domainspec/.
- Lean, Lake, craft-compiler, language, toolchain, runtime, environment, and lock declarations live in the platform plane; materialized local bytes live under ignored .cyberalchemy/ state.
- CML-05/CML-06 and CML-07 branch independently from accepted CML-04 semantics according to explicit depends_on edges.

## Owner-role posture

The role registry in CAL-PROP-0001 is selected as a separation-of-authorities contract; accountable identities may be bound later, and one person may hold multiple roles only without collapsing their distinct decisions or evidence.

## Selection options

- `CML00-ACCEPT` — Accept the exact architecture graph and allow CML-00 completion; CML-01 still requires a new routed execution authorization.
- `CML00-REVISE` — Return one or more exact proposal bytes for bounded revision; CML-00 remains blocked.
- `CML00-DEFER` — Keep the immutable candidate available but make no architecture selection.
- `CML00-STOP` — Stop this selection process without accepting architecture or authorizing a successor.

## Claim ceiling

This candidate presents exact architecture bytes for owner selection. Until CML00-ACCEPT is recorded, no architecture or path is accepted and CML-00 remains blocked. Selection would complete planning only and would not authorize CML-01, migration, implementation, installation, Git, publication, release, or deployment.

