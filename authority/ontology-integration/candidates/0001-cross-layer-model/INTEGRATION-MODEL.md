<!-- GENERATED FILE: canonical data is integration-model.json. -->

# Step 7 — Ontology cross-layer integration model

- Layers: `8`
- Cross-layer mappings: `7`
- Non-collapse cases: `12`
- Gaps: `10`
- Proposed Artifact Type actions: `7`
- Authority effect: `none`

## Integrated flow

```text
admitted Definition
  -> admitted Artifact Type carrier
  -> admitted artifact instance
  -> optional Ontology Node representation

admitted Relation Kind
  -> admitted global Typed Relation
  -> optional digest-bound Ontology Edge projection

Ontology Node / Ontology Edge semantic events
  + exact governance-event joins
  -> consistent Ontology Cut
  -> purpose-bounded Ontology View
  -> optional Context View for an Agent Session
```

## Non-collapse rules

- **Artifact Type / artifact instance** — Contract versus governed occurrence.
- **artifact instance / Ontology Node** — Represented subject versus ontology-scoped representation.
- **Typed Relation / Ontology Edge** — Global connection versus ontology-scoped projected or local connection.
- **Relation Kind / DomainSpec relationship signature** — Global semantic connection contract versus modeling-language structural signature.
- **Ontology / Ontology Manifest** — Governed meaning layer versus stable configuration and identity record.
- **Ontology Node / Governed Ontology Node View** — Ontology subject versus calculated consumer read model.
- **Ontology Cut / Ontology View** — Complete consistent state at a cursor versus purpose-bounded selection for a consumer.
- **Ontology View / Context View** — Ontology-specific projection versus broader task-ready context projection that may cite several sources.
- **Semantic Event History / Governance Event History** — Meaning-bearing history versus governance observation history joined to exact semantic epochs.
- **ontology lifecycle / governance status** — Subject availability versus independent admission, maturity, confidence, challenge, or authority posture.
- **canonical event history / projection** — Replay authority versus discardable calculated output.
- **local relation type / global Relation Kind** — Ontology or modeling namespace meaning versus globally admitted connection vocabulary.

## Carrier actions

- `supersede-before-admission` `cal.artifact-type.ontology-node/v2` bound to `cal.definition.ontology-node@1.0.0-candidate.1`
- `materialize-new` `cal.artifact-type.ontology-edge/v1` bound to `cal.definition.ontology-edge@1.0.0-candidate.1`
- `materialize-new` `cal.artifact-type.ontology-manifest/v1` bound to `cal.definition.ontology-manifest@1.0.0-candidate.1`
- `materialize-new` `cal.artifact-type.ontology-cut/v1` bound to `cal.definition.ontology-cut@1.0.0-candidate.1`
- `materialize-new` `cal.artifact-type.ontology-view/v1` bound to `cal.definition.ontology-view@1.0.0-candidate.1`
- `materialize-new` `cal.artifact-type.semantic-event-history/v1` bound to `cal.definition.semantic-event-history@1.0.0-candidate.1`
- `materialize-new` `cal.artifact-type.governance-event-history/v1` bound to `cal.definition.governance-event-history@1.0.0-candidate.1`

## Gaps

### ONT-GAP-001 — Ontology Node/v1

The candidate carrier lacks represented subject kind/ref/version/digest, closed semantic and governance facet separation, event epoch bindings, branch/profile, use obligations, and forbidden-collapse fields required by its admitted Definition and selected architecture.

Recommendation: Materialize Ontology Node/v2 and supersede v1 before Artifact Type admission.

### ONT-GAP-002 — Ontology Edge

The Definition is admitted but no Artifact Type carrier exists.

Recommendation: Materialize Ontology Edge/v1 with projected-global and ontology-local modes, exact endpoints, independent identity/lifecycle, and no authority transfer.

### ONT-GAP-003 — Ontology Manifest

The Definition is admitted but no Artifact Type carrier exists; Ontology/v1 is the meaning-layer aggregate and cannot substitute for its stable configuration record.

Recommendation: Materialize Ontology Manifest/v1.

### ONT-GAP-004 — Ontology Cut

The Definition is admitted but no Artifact Type carrier exists.

Recommendation: Materialize Ontology Cut/v1 as a rebuildable exact-cursor calculated record that is forbidden as replay input.

### ONT-GAP-005 — Ontology View

The Definition is admitted but no Artifact Type carrier exists.

Recommendation: Materialize Ontology View/v1 with consumer, selector, exact cut, event-set digest, freshness, expiry, exclusions, and claim ceiling.

### ONT-GAP-006 — Semantic Event History

The Definition is admitted but no Artifact Type carrier exists.

Recommendation: Materialize Semantic Event History/v1 as an append-only subject-history manifest bound to exact event records and cursors.

### ONT-GAP-007 — Governance Event History

The Definition is admitted but no Artifact Type carrier exists.

Recommendation: Materialize Governance Event History/v1 with exact semantic epoch joins and upstream Governance evidence bindings.

### ONT-GAP-008 — relation namespaces

The 23 global Relation Kinds, 24 business-ontology relationships, and 28 DomainSpec signatures have no explicit namespace and bridge registry; `derives-from` collides textually.

Recommendation: Create an explicit relation namespace and bridge registry; preserve unmapped local terms.

### ONT-GAP-009 — selected architecture posture

Immutable proposal bytes and several consumers still say unselected or draft although CAL-GONA-0005 selected the exact digest.

Recommendation: Create a current effective-state overlay/index; do not rewrite historical proposal bytes.

### ONT-GAP-010 — local governed-node definition pack

The selected local pack uses OntologyRelation while the admitted integrated model uses Ontology Edge for the same scoped first-class concept.

Recommendation: Declare OntologyRelation as the Ontology Lifecycle bounded-context term mapped to global Ontology Edge; preserve local aliases and source definitions without duplicate global identity.

## Runtime boundary

Exact adopted Rust library plus one authorized and successfully materialized local CLI instance. No daemon, persistent active service, repository enforcement, general legacy migration, cutover, publication, deployment, or external effect is established.

## Claim ceiling

This candidate maps selected and admitted evidence, identifies integration gaps, and proposes seven Artifact Type actions. It does not amend a selected convention, rewrite historical bytes, admit a carrier or instance, add a relation endpoint pair, migrate an ontology, or activate a runtime.
