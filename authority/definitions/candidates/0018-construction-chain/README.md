# Definitions-to-generation construction contract candidate

**Current review:** [review outcome](review/STATUS.md). Semantic review and source/CLI checks are complete; final owner/publication and correct host-scope gates remain blocked. Do not implement yet.


This package completes the current semantic coverage and contract/design artifacts before runtime implementation. It follows:

**Definitions → typed artifacts → business/domain ontology → business-system bridge → system-design ontology → AlchLang → generation.**

## Start here

- [Coverage matrix](COVERAGE.md) and [machine matrix](COVERAGE.json): 16 workflow obligations and their explicit missing implementation joins.
- [Candidate index](INDEX.json): two new scoped Definitions, with generated human projections.
- [Chain contract](contracts/chain.json), [six handoff contracts](contracts/handoffs/), [format schemas](contracts/formats.schema.json), [scope binding](contracts/scope-binding.json), [review](contracts/review.json), [evolution](contracts/evolution.json), [language projection](contracts/language-projection.json) and [generation gate](contracts/generation-gate.json).
- [System contracts](SYSTEM-CONTRACTS.json) and [alignment decisions](ALIGNMENTS.json) own the proposed technical specifications. The [three ontology models](models/) project their exact subjects; they are not a second writable authority for those sources.
- [Four ontology profiles](profiles/): business, bridge, authored system-design and generated-implementation. All specialize the existing Ontology meaning.
- [Actual Define result](define-process/RESULT.json) and [current frozen Packs](define-process/CURRENT-PACKS.zip).
- [Validation receipt](RECEIPT.json) and [review checklist](REVIEW.md).

## Meaning and authority

44 existing meanings are reused unchanged: 41 current admitted definitions and three preexisting candidate meanings (Lab Workspace, Definition Pack and CyberAlchemy Define). Their distinct standing remains explicit. Only Construction Chain Contract and Construction Stage Handoff are new Definition/v2 candidates. No duplicate global Ontology, Schema, Artifact, Work or Record meaning was created. Record denotes the existing artifact-instance route.

Formats are candidate profile/design contracts, not newly registered native Artifact Types. GovernedModel is the semantic base for process/model specifications; the specialized graph files do not pretend to be native GovernedModel envelopes. Actual native records must use their exact selected current carriers and any required independently reviewed mapping. No canonical registry, live ontology history, owner assignment or operational permission is created.

The pre-AlchLang system model is authored system design. A generated implementation/provenance graph is downstream evidence checked against it. Exact source subjects, ontology representations, local edges, global Typed Relations, semantic acceptance, approval and observed effects stay separate. Evidence confidence and commitment confidence are independent fields.

Generation entry requires the complete current source/mapping/profile chain. Output manifests and independent conformance results are completion requirements, not circular prerequisites for starting generation. Required gaps block a claim of conformant generation; a residue entry is not a waiver. Iteration uses explicit successor revisions and transitive invalidation, not hidden rewrites. Existing code is mapped as existing support, never presented as historically generated from these new designs.

## Define process and reuse

The existing CLI limits a Pack to 24 concepts. The latest review family contains 24 foundation and 22 workflow concepts: 41 admitted reuses and five exact candidate proposals. Three proposals reuse preexisting candidate bodies unchanged; two are the new chain/handoff meanings. No duplicate global meanings were created.

Both current Packs passed actual `define lab prepare`, standalone inspection and exact reconstruction. The workflow Pack materialized all five complete Definitions and passed actual `define lab review`. Freshly extracted archive copies passed inspection, and altered original bytes were refused. The [result](define-process/RESULT.json) preserves exact commands, reports and scope limits. Only this latest family and its native review/mapping/proposal are archived.

The signed local context binds all 41 admitted source meanings to the observed source-current native selection. It does not authenticate an external issuer or override the standalone Pack's frozen readiness. Those readiness gaps remain visible. Native structural review grants no semantic acceptance or permission.

The native proposal was rejected for this workflow because its historical migration Project, fixed Goal and User Journey wording misattribute the work. Authorization and application were not invoked; native HEAD stayed at sequence zero. The unused operator was revoked. See [review outcome](review/STATUS.md) for the exact remaining owner, publication, host-scope and later construction-compatibility gates.

## Implementation boundary

No new AlchLang behavior, native adapter, runtime gate or production workflow is implemented here. All existing runtime/Product source bytes and the canonical Definition registry remain unchanged. Next implementation must consume these reviewed exact inputs, preserve scoped authority and provide positive/causal-negative behavior evidence for each matrix obligation.
