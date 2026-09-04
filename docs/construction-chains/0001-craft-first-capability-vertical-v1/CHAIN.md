<!-- GENERATED FILE: edit chain.json and run build.py. -->

# Craft First Product Capability Vertical

> Candidate construction chain; no admission, implementation, migration, or runtime authority.

- Chain: `CAL-CML08-12-CRAFT-FIRST-CAPABILITY-VERTICAL-0001`
- Status: `candidate-authored-dependencies-open`
- Predecessor: `CAL-DECISION-0031-CML07-CRAFT-IDENTITY-V1`
- Interaction mode: `single` at `CML12-FINAL-EXACT-BYTE-DECISION-CHECKPOINT`

## Outcome

Carry the admitted CML-07 Craft identity foundation through one exact Product Capability vertical to candidate runtime and consumer migration evidence without collapsing Product Feature, Product Capability, Capability Instance, Bounded Context, specification, implementation, or conformance identities.

## Why the chain starts with semantic closure

- **CML08-GAP-SEMANTICS** — The corresponding Artifact Types and D65 successor claims cannot yet be admitted or evaluated.
- **CML08-GAP-PRODUCT-CAPABILITY-TYPE** — The System Construction Product Feature and the migration proposal's first vertical cannot be silently treated as an adopted Product Capability.
- **CML08-GAP-VERTICAL-SELECTION** — No source migration or implementation slice is selected.

## Sequence

### CML08-S0-CLOSE-VERTICAL-SEMANTICS-TYPES-AND-OWNERS

After this stage, we know whether every identity and evidence carrier needed by the first vertical has canonical meaning, a closed machine contract, and a separately scoped owner.

Included:

- author the missing canonical Definitions listed in CML08-GAP-SEMANTICS
- author Artifact Type/v2 registrations with semantic_definition_refs for each new canonical carrier
- author Product Capability adoption, business-ontology, specification, compiler-output, platform-profile, implementation-binding, and conformance owner assignments
- author negative fixtures for Product Feature/Product Capability, Product Capability/Capability Instance, Bounded Context/directory, and validation/conformance collapse

Outputs:

- `authority/definitions/candidates/<next>-craft-first-vertical-semantic-closure/`
- `authority/artifact-types/<new-first-vertical-types>/`
- `authority/owners/foundation-01/v1/candidates/<next>-craft-first-vertical/`
- `tests/fixtures/cml08-semantic-non-collapse/`

Exit evidence:

- all new Artifact Types bind admitted-or-final-bundle-targeted semantic Definitions
- all owner roles have non-overlapping scopes
- all human projections reproduce from canonical machine records
- hostile collapse fixtures fail for the intended reason

Effect ceiling: Makes exact vertical selection candidate-authorable only; no semantic or type admission occurs.

### CML08-S1-SELECT-FIRST-CAPABILITY-CONTEXT-AND-INSTANCE

After this stage, we know whether one exact Product Capability vertical can be selected without inferring capability identity from the System Construction Product Feature or context identity from a directory.

Included:

- one Product Capability candidate with a stable identity and version
- one explicit Product Feature to Product Capability relation or explicit no-relation posture
- one Capability Instance envelope
- one Bounded Context/v2 candidate or explicit no-context posture
- one exact dependency-closed source selector set
- one recursion stop, recomposition route, terminal handoff, and rollback boundary

Outputs:

- `product/capabilities/<selected-capability-id>/v1/capability.json`
- `product/capabilities/<selected-capability-id>/v1/CAPABILITY.md`
- `contexts/<selected-context-id>/v1/context.json-or-no-context.json`
- `<resolved-instance-root>/envelope.json`
- `evidence/migrations/domainspec-v2-to-craft/manifests/<selected-instance-id>-selection.json`

Exit evidence:

- all identities and versions are explicit and distinct
- the source selector closure is exact and digest-bound
- the no-context posture is explicit if no DDD semantic boundary is justified
- directory placement supplies no classification or authority

Effect ceiling: Makes candidate Product Capability and business-ontology authoring evaluable only.

### CML09-S2-AUTHOR-CAPABILITY-AND-BUSINESS-ONTOLOGY

After this stage, we know whether the selected Product Capability promise and only its required business meaning close against exact canonical Definitions and context ownership.

Included:

- Product Capability contract and outcome obligations
- capability-local business ontology closure
- typed Context Map relations only where multiple Bounded Contexts exist
- Capability Instance parent and inherited-contract bindings
- source admission candidates for every imported semantic byte

Outputs:

- `product/capabilities/<selected-capability-id>/v1/business-ontology/`
- `contexts/<selected-context-id>/v1/maps/-or-explicit-none`
- `<resolved-instance-root>/construction/capability-binding.json`
- `authority/decisions/source-admission/<selected-instance-id>-semantics/v1/admissions.json`

Exit evidence:

- business ontology contains no unselected source concept
- all concepts resolve to canonical Definitions or explicit context-local language terms
- Context Map relations are owned by maps and not back-repeated on context endpoints
- Capability Instance authority remains distinct from parent capability adoption

Effect ceiling: Makes authored specification candidate construction evaluable only.

### CML10-S3-AUTHOR-SPECIFICATION-COMPILE-GRAPH-AND-SYSTEM-ONTOLOGY

After this stage, we know whether one exact authored specification deterministically compiles into the graph and system ontology required by the selected capability instance.

Included:

- Craft-authored canonical specification source under the Capability Instance
- exact compiler identity and profile
- deterministic compiled graph
- system ontology derived from the graph
- two-run byte-identity and source-to-output trace receipts

Outputs:

- `<resolved-instance-root>/specification/project.json`
- `<resolved-instance-root>/specification/authored/`
- `<resolved-instance-root>/specification/generated/graph.json`
- `<resolved-instance-root>/specification/generated/system-ontology.json`
- `evidence/conformance/<selected-instance-id>/construction-determinism/`

Exit evidence:

- all outputs trace to exact authored source and compiler profile digests
- two clean runs produce identical generated bytes
- generated records are never edited as canonical authored source
- the system ontology contains no requirement outside the selected capability and business ontology closure

Effect ceiling: Makes realization and exact implementation-binding candidates evaluable only.

### CML11-S4-AUTHOR-REALIZATIONS-PROFILES-AND-IMPLEMENTATION-BINDING

After this stage, we know whether every selected realization and exact implementation binding closes against the system ontology under pinned language, tool, runtime, filesystem, network, and environment profiles.

Included:

- only the TypeScript, Python, Rust, Lean, compiler, and runtime profiles required by the selected vertical
- content-addressed tool declarations and environment lock
- language-neutral realization contracts
- exact implementation binding from system-ontology obligations to final-path components
- offline warm-store and clean-store policy checks

Outputs:

- `platform/languages/<selected-language-id>/v1/`
- `platform/tools/<selected-tool-id>/v1/`
- `platform/profiles/<selected-profile-id>/v1/`
- `platform/runtimes/<selected-runtime-id>/v1/`
- `platform/locks/<selected-instance-id>.lock.json`
- `<resolved-instance-root>/implementation/binding.json`

Exit evidence:

- every system-ontology obligation has one exact binding or typed residue
- no mutable global tool or unpinned environment supplies conformance
- active paths and package identities use Craft or neutral names
- profile, installation, implementation, and conformance identities remain distinct

Effect ceiling: Makes bounded implementation, runtime, and consumer-migration validation candidate-authorable only.

### CML12-S5-MATERIALIZE-VALIDATE-AND-PACKAGE-FINAL-DECISIONS

After this stage, we know whether the exact final-path Craft vertical installs, builds, tests, runs, conforms within declared scopes, rolls back, and can be presented as one immutable Decision Request Set.

Included:

- dependency-closed implementation and Craft CLI at final Lab paths
- only explicitly selected consumer rebindings
- schema, identity-contract, construction, implementation, installation, and runtime conformance assessed as separate scopes
- collect-all non-effectful preacceptance evidence
- rollback rehearsal
- one closed digest-bound Decision Request Set at the configured final checkpoint

Outputs:

- `<resolved-instance-root>/implementation/`
- `<resolved-instance-root>/evidence/`
- `evidence/migrations/domainspec-v2-to-craft/manifests/<selected-instance-id>-migration.json`
- `evidence/migrations/domainspec-v2-to-craft/receipts/<selected-instance-id>/`
- `evidence/migrations/domainspec-v2-to-craft/rollback/<selected-instance-id>/`
- `docs/admission-bundles/<next>-craft-first-capability-vertical-v1/`

Exit evidence:

- all applicable checks are PASS and all dependent blocked checks remain explicitly NOT_EVALUABLE
- independent construction and conformance paths share no unreported decision logic
- two clean runs reproduce target bytes, manifests, projections, and conformance results
- rollback restores exact preimages without changing the legacy source repository
- every final request member binds an exact target digest, owner, effect, invalidation rule, and rollback boundary

Effect ceiling: Presents one final human interaction containing separately governed ordered requests; it performs no decision, admission, activation, publication, or deployment.

## One final interaction

All exact candidate bytes and collect-all receipts are authored before one human interaction. Each request retains its own owner, target, effect, and outcome. Ordered application follows the dependency graph and stops at the first failed effect.

- `CML12-DR-01-SEMANTICS-TYPES-OWNERS` — Admit exact semantic Definitions, Artifact Types, and owner-registry postimage in dependency order.
- `CML12-DR-02-VERTICAL-SELECTION` — Select exact capability, instance, context posture, source closure, recursion stop, and rollback boundary.
- `CML12-DR-03-CAPABILITY-ONTOLOGY-SPECIFICATION` — Admit the exact capability, business ontology, authored specification, compiled graph, and system ontology.
- `CML12-DR-04-BINDING-AND-SCOPED-CONFORMANCE` — Accept the exact implementation binding and only the named conformance scopes supported by current evidence.
- `CML12-DR-05-LOCAL-ACTIVATION-AND-CONSUMER-REBINDING` — Authorize only the manifest-bound local activation and selected consumer rebindings with the rehearsed rollback.

Excluded from that interaction:

- git commit or push
- publication or release
- deployment
- destructive source deletion
- credential or network effects

## Recommended next unit

`CML08-S0-SEMANTIC-CLOSURE-AUDIT-AND-AUTHORING` — Inventory exact CyberAlchemy-v2 meanings for the missing first-vertical terms, decide preserve/revise/split/reclassify/drop per term, then author only the dependency-closed Definition, Artifact Type, hostile-fixture, and owner candidates.

## Claim ceiling

This candidate authors the CML-08 through CML-12 dependency graph, five-layer implementation model, semantic gaps, exact output surfaces, validation obligations, and one final interaction shape only. It does not admit a Definition, Artifact Type, owner, Product Capability, Capability Instance, Bounded Context, ontology, specification, graph, implementation binding, conformance claim, runtime, migration, publication, deployment, or stable release.
