<!-- Generated from proposal.json by tooling/generators/craft_transplant.py. Do not edit. -->

# Source-preserving Craft transplant architecture

- Proposal: `CAL-PROP-0005`
- Status: `candidate`
- Decision posture: `owner-directed-construction-revision`
- Authority effect: `none`

## Objective

Move the current DomainSpec v2 implementation home into CyberAlchemy Lab as the Craft workspace by copying its existing version-controlled product files before renaming or rebinding them, rather than rebuilding its semantics or runtime from prototype witnesses.

## Architecture

- `craft/` — source-preserving Craft product workspace. A renamed Product workspace, not a DDD Bounded Context and not an authority effect.
- `authority/` — CyberAlchemy Lab shared authority and artifact mechanics. Does not silently supersede authority records copied under craft/.
- `product/` — Lab Product identities, capabilities, and construction candidates. References the Craft workspace without duplicating its implementation.
- `contexts/` — Explicit DDD Bounded Context identities and maps. Craft, Product, Governance, and directories are not contexts by implication.
- `evidence/migrations/domainspec-v2-to-craft/` — copy manifest, validation, exclusions, and rollback evidence. Evidence does not admit copied bytes or activate the workspace.

### Craft workspace

- `craft/.craft/`
- `craft/architecture/`
- `craft/authority/`
- `craft/capabilities/`
- `craft/definitions/`
- `craft/discovery/`
- `craft/formalization/`
- `craft/impl/`
- `craft/ontology/`
- `craft/research/`
- `craft/<root product and runtime files>`

**Identity.** The destination directory is named craft, while copied file bytes and stable DS-* identifiers remain unchanged during the transplant. Active-name rewrites and path rebinding are a later, independently validated successor task.

**Cohesion.** Preserve the existing relative tree so internal links, packages, fixtures, and implementation boundaries remain inspectable as one system; do not scatter copied files across Lab authority, product, context, implementation, or evidence planes before dependency-aware rebinding.

**Contexts.** The craft/ workspace does not establish a Bounded Context. Context membership remains an explicit typed relation owned under contexts/.

## Copy contract

- Source: `/home/vrondelli/projects/domainspec-core/projects/domainspec-v2`
- Destination: `/home/vrondelli/projects/CyberAlchemy-lab/craft`
- Selection: git-tracked files outside projects/domainspec-v2/development/
- Mapping: strip projects/domainspec-v2/ and preserve every remaining relative path beneath craft/
- Bytes: source and destination SHA-256 must match for every copied file
- Modes: preserve source file permission bits
- Collisions: refuse an existing destination file with different bytes

Excluded:

- `projects/domainspec-v2/development/**`
- `untracked files`
- `ignored dependencies and caches`
- `implementation/domainspec/** frozen v1 evidence`
- `CyberAlchemy-lab P0-P2 prototype files`

## Construction effect

- Current frontier: Copy and verify the current DomainSpec v2 product workspace as a candidate Craft transplant.
- Superseded strategy: Do not continue CML10-P3 as a reimplementation or replacement compiler path.
- Preserved evidence: P0-P2 remain historical prototype evidence with unchanged bytes.
- Next frontier: Inventory active-name and path bindings inside the copied workspace, then perform dependency-aware DomainSpec-to-Craft renaming without semantic reconstruction.

## Rollback

- Before admission: Remove only craft/, this proposal package, the transplant tool/validator, and evidence/migrations/domainspec-v2-to-craft/.
- Source effect: `none`
- Legacy v1 effect: `none`

## Claim ceiling

This candidate architecture and byte-preserving copy do not admit, activate, approve, publish, release, or deploy Craft. They do not prove that copied DomainSpec names or paths are already correctly rebound for the active Craft identity.
