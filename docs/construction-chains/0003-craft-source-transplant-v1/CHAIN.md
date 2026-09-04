<!-- Generated from chain.json by tooling/generators/craft_transplant.py. Do not edit. -->

# Craft Source-Preserving Transplant and Rebinding Chain

- Chain: `CAL-CML10R-CRAFT-SOURCE-TRANSPLANT-0003`
- Status: `candidate-runnable-frontier`
- Authority effect: `none`
- Current frontier: `CML10R-T1-INVENTORY-ACTIVE-NAME-AND-PATH-BINDINGS`

## Objective

Copy the current DomainSpec v2 product workspace into CyberAlchemy Lab as Craft, then rename and rebind the copied system dependency-aware without reconstructing its definitions, compiler, runtime, or evidence machinery.

## Construction rule

Transplant first, rebind second, validate third. Existing source bytes are evidence and implementation material; copied placement grants no admission or authority.

## Stages

### 1. `CML10R-T0-COPY-SOURCE-WORKSPACE`

- Lane: `product-construction`
- State: `tested-candidate`
- Depends on: none
- Objective: Copy every selected version-controlled DomainSpec v2 product file outside development history into craft/ with relative paths, bytes, and modes preserved.
- Exit evidence: The independent transplant validator reports PASS for exact source selection, bytes, modes, destination closure, exclusions, and zero authority.
- Authority effect: `none`

### 2. `CML10R-T1-INVENTORY-ACTIVE-NAME-AND-PATH-BINDINGS`

- Lane: `product-construction`
- State: `runnable`
- Depends on: CML10R-T0-COPY-SOURCE-WORKSPACE
- Objective: Inventory every active DomainSpec product name, package ID, command, path, import, generated target, profile, and user-facing label inside craft/ and classify legacy-only occurrences separately.
- Exit evidence: Every occurrence has a typed classification, owner, destination form, dependency order, and validation consumer; no replacement is performed in this stage.
- Authority effect: `none`

### 3. `CML10R-T2-RENAME-AND-REBIND-COPIED-WORKSPACE`

- Lane: `product-construction`
- State: `waiting`
- Depends on: CML10R-T1-INVENTORY-ACTIVE-NAME-AND-PATH-BINDINGS
- Objective: Apply the inventory as an exact dependency-ordered rename and rebinding manifest inside craft/, preserving DS-* semantic IDs and explicit historical provenance.
- Exit evidence: No active package, command, compiler, profile, or user-facing current-name field retains DomainSpec except typed legacy/provenance fields, and every changed consumer resolves.
- Authority effect: `none`

### 4. `CML10R-T3-PROFILE-AND-RESTORE-TOOLCHAINS`

- Lane: `operational-support`
- State: `waiting`
- Depends on: CML10R-T2-RENAME-AND-REBIND-COPIED-WORKSPACE
- Objective: Bind the copied workspace to its exact Node, pnpm, TypeScript, Python, Rust, Lean, container, filesystem, and network profiles; install or restore only missing dependencies under separately bounded platform effects.
- Exit evidence: Every required tool and dependency resolves from an exact profile and lock; unavailable optional lanes remain typed residue rather than hidden PASS.
- Authority effect: `none`

### 5. `CML10R-T4-VALIDATE-CRAFT-WORKSPACE`

- Lane: `product-construction`
- State: `waiting`
- Depends on: CML10R-T2-RENAME-AND-REBIND-COPIED-WORKSPACE, CML10R-T3-PROFILE-AND-RESTORE-TOOLCHAINS
- Objective: Run the copied system's existing checks plus hostile rename, stale-path, source-drift, generated-view, rollback, and two-run determinism tests from final Craft paths.
- Exit evidence: All acceptance-critical selected-workspace checks pass from final paths and no unresolved residue is inflated into PASS.
- Authority effect: `none`

### 6. `CML10R-T5-INTEGRATE-LAB-PLANES`

- Lane: `product-construction`
- State: `waiting`
- Depends on: CML10R-T4-VALIDATE-CRAFT-WORKSPACE
- Objective: Bind the validated Craft workspace to Lab Product, authority, capability, context, platform, and evidence records through references and explicit maps without duplicating its implementation or inferring a Bounded Context from placement.
- Exit evidence: All cross-plane identities and references close while the Craft implementation has exactly one active home.
- Authority effect: `none`

### 7. `CML10R-T6-COLLECT-CURRENT-PRODUCT-TEST-EVIDENCE`

- Lane: `product-construction`
- State: `waiting`
- Depends on: CML10R-T5-INTEGRATE-LAB-PLANES
- Objective: Freeze one exact testable Craft candidate and collect complete current product-test evidence over its copied, rebound, and integrated bytes.
- Exit evidence: One immutable candidate and its complete current tests are identified; approval is eligible only when every required result is PASS.
- Authority effect: `none`

### 8. `CML10R-T7-PRODUCT-APPROVAL-CHECKPOINT`

- Lane: `human-decision`
- State: `waiting`
- Depends on: CML10R-T6-COLLECT-CURRENT-PRODUCT-TEST-EVIDENCE
- Objective: Present the exact tested Craft candidate once for approve, revise, reject, defer, or stop.
- Exit evidence: The decision binds the exact candidate and current product-test evidence and has product-approval-only effect.
- Authority effect: `product-approval-only-if-approved`

## Approval boundary

- Mode: `single-final-product-boundary`
- Workflow: `source-preserving-product-migration`
- Eligible after: `CML10R-T6-COLLECT-CURRENT-PRODUCT-TEST-EVIDENCE`
- Decision stage: `CML10R-T7-PRODUCT-APPROVAL-CHECKPOINT`
- Approved effect: `product-approval-only`
- Operational authority: `separate-later-route`

## Work plan

- Product-construction frontier: `CML10R-T1-INVENTORY-ACTIVE-NAME-AND-PATH-BINDINGS`
- Causal construction blockers: `0`
- Operational support remains separately owned and cannot hide runnable product work.

## Claim ceiling

This chain makes the source-preserving migration route explicit. It does not admit copied bytes, complete active-name rebinding, prove runtime conformance, approve the Product, activate consumers, delete legacy sources, commit, publish, release, or deploy.
