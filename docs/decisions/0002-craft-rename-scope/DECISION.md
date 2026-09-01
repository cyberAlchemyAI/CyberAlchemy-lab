<!-- Generated from decision.json. Do not edit this projection directly. -->

# Decision 0002: Craft rename scope for the DomainSpec v2 lineage

- Decision ID: `CAL-DECISION-0002`
- Status: **owner-selected**
- Date: 2026-08-31
- Decision owner: CyberAlchemy Lab repository owner
- Selected option: `RN-2` — Active Craft naming with stable legacy IDs
- Authority effect: **none**
- Canonical source: `decision.json`

## Question

How broadly should the selected DomainSpec v2 to Craft rename apply while migrating the same Product lineage into CyberAlchemy Lab?

## Considered options

### RN-1 — Product rename only

- Kind: `action`
- Disposition: **not-selected**
- Effect: Rename the Product, Project, and Method while retaining DomainSpec as the active language, compiler, package, path, and identifier name.
- Risk: Leaves two active names and weakens the intended Craft product boundary.

### RN-2 — Active Craft naming with stable legacy IDs

- Kind: `action`
- Disposition: **selected**
- Effect: Use Craft or neutral specification terminology on active paths, packages, tools, CLI surfaces, profiles, and prose while preserving legacy semantic IDs during the first stable migration and binding them through explicit lineage maps.
- Risk: Requires disciplined alias and lineage handling until a separately selected identifier policy retires or retains the legacy IDs.

### RN-3 — Complete namespace rekey

- Kind: `action`
- Disposition: **not-selected**
- Effect: Mint new Craft identifiers and rename every active semantic, schema, package, CLI, and path identity.
- Risk: Creates the largest reference and semantic-identity migration surface.

### RN-D — Defer

- Kind: `defer`
- Disposition: **not-selected**
- Effect: Retain the earlier Product-lineage naming decision without beginning Lab migration planning.
- Risk: Leaves active migration terminology unresolved.

### RN-S — Stop

- Kind: `stop`
- Disposition: **not-selected**
- Effect: Stop the DomainSpec v2 to Craft migration direction.
- Risk: Abandons the selected Craft Product-lineage direction.

## Decision

Select `RN-2` — **Active Craft naming with stable legacy IDs**.

Lineage posture: `same-product-renamed`.

### Active naming policy

- Use Craft for the current Product, Project, Method, packages, tools, CLI surfaces, profiles, and other user-visible active identities.
- Use neutral specification terminology for the authored-source and compiled-system layer when repeating Craft would obscure the layer's role.
- Do not introduce new active domainspec-named paths or package identities in CyberAlchemy Lab.
- Treat DomainSpec v2 as the former Product name and external migration-source label.

### Identifier policy

- Preserve stable legacy semantic IDs such as DS-* during the first stable migration when changing them would break lineage or reference closure.
- Every preserved legacy ID must carry an explicit former-name or lineage mapping to its active Craft meaning.
- A preserved ID is not permission to keep an active DomainSpec path, package name, CLI name, or display label.
- Minting replacement CRAFT-* semantic IDs requires a separate owner decision with exact bidirectional mappings and consumer-closure evidence.

### Historical policy

- Do not rewrite historical DomainSpec v2 evidence, receipts, decisions, source paths, or immutable digests.
- Retain unselected source material in domainspec-core as external legacy evidence.
- Import only exact dependency-closed bytes selected through CyberAlchemy Lab source admission.

## Rationale

- The selection makes Craft the coherent active product name without pretending historical identifiers and evidence can be safely rewritten.
- Stable semantic IDs preserve same-lineage continuity and reduce reference breakage during the first vertical.
- Neutral specification terminology keeps the construction layer intelligible without retaining DomainSpec as a second active Product name.
- Explicit lineage maps make temporary old-name identifiers visible and challengeable rather than hiding them behind aliases.

## Bound evidence

- `domainspec-core:cyberAlchemy-v2/goals/projects/craft/CRAFT-IDENTITY-DECISION.json` — SHA-256 `1f2d01026865e031adba063de0dc1dfa081c49a931223aa4bc9f726d3397bceb` — lineage-and-former-name-evidence-only
- `domainspec-core:cyberAlchemy-v2/development/domainspec-v2/migration/mig-b/map/CRAFT-MIGRATION-ORDER.json` — SHA-256 `7b690fd8ede305449ec63334d3155c34fcdf5bc7da582eeeb4f0ba84de0b9ac2` — migration-planning-precedent-only
- `CyberAlchemy-lab:docs/proposals/0001-context-artifact-architecture/proposal.json` — SHA-256 `7ee7288a8e376c2634230be0e123fdb65c858369495a7f21283c77f7124e31b2` — draft-architecture-input-only
- `CyberAlchemy-lab:docs/proposals/0002-platform-environment-architecture/proposal.json` — SHA-256 `4d0fd148adb999871c7e10994b3c32514ba6c273f46fe0d66013031a804d7a24` — draft-platform-input-only

## Downstream required changes

1. Revise the context and artifact architecture draft to replace active domainspec/ paths with specification/ and add explicit Product plus Project/Goal coordination surfaces.
2. Revise the platform environment architecture draft to replace domainspec-compiler with craft-compiler and use Craft or neutral specification profile names.
3. Author a Lab-bound migration proposal that preserves MIG-B's selective, definitions-first dependency order but targets the selected Lab architecture.
4. Create an exact old-to-current lineage map for preserved DS-* identifiers before admitting the first definition slice.
5. Re-freeze the legacy source epoch because prior source-bound Craft package digests have drifted and the destination repository changed.

## Remaining blockers

- The two Lab architecture proposals are drafts and have not been selected.
- No admitted Lab owner-decision artifact type, schema, projection generator, validator, or source-admission mechanism exists.
- The exact first Craft capability and bounded context are not selected.
- The exact legacy definition closure and lineage-map schema are not yet bound to a fresh source epoch.
- The CyberAlchemy governance enforcement runtime is not admitted.

## Explicitly blocked effects

- architecture selection
- definition or ontology admission
- semantic identifier replacement
- source copying or path rewriting
- consumer rebinding
- authority transfer
- implementation
- publication
- release
- deployment
- v1.0.0 claim

## Claim ceiling

This record binds the repository owner's RN-2 migration-scope selection as non-effectful decision evidence. It does not select the Lab architecture, admit an artifact type or source, change canonical definitions, rename or copy files, replace DS-* identifiers, migrate consumers or authority, implement a runtime, publish, release, deploy, or establish v1.0.0.
