---
node_type: decision
is_session: false
status: pass
boundary: INTERNAL — DomainSpec v2 minted-project factory authority
created: 2026-07-14
timestamp: 2026-07-15T00:08:38Z
decision_id: DEC-DSV2-MINTED-PROJECT-NODE-PACKAGE
target_scope: PLAN-B1 / PLAN-B2 / PLAN-B3
source: operator choices in decision-gate, 2026-07-14
---

# Decision: Minted-Project Node Package

## Consequential work

The minted-project implementation plan could not bind write scopes or authorize a
Task Session while the factory authority homes, first supported profile, and
concrete-fixture dispositions were unresolved. This record binds those owner
choices without promoting the Refine toy package or mutating the factory.

The consumer-side default remains `specs/<feature>/feature.json` plus
`specs/<feature>/nodes/*.json`. Those project-local sources own concrete domain
meaning. DomainSpec owns reusable factory form and conformance only.

## Decision 1: factory authority homes

### Considered options

1. Split authority across the existing definitions, implementation-spec,
   tooling, and derivation-engine fixture surfaces.
2. Place contracts, profiles, runtime, templates, and conformance in one
   `impl/minted-project/` package.
3. Make the minted-project capability internal to the test-derivation engine.

### Selected option

**Option 1 — owner-split existing surfaces.**

### Authority binding

| Factory concern | Authoritative home | Authority role |
| --- | --- | --- |
| Supported-profile declaration | `projects/domainspec-v2/definitions/minted-project/` | DomainSpec v2 definitions authority; the first machine registry is `supported-profiles.yml` |
| Project, feature, node, and connection source schemas | `projects/domainspec-v2/impl/spec/minted-project/` | machine contract authority |
| Normalized graph, source-manifest, Markdown-view, and build-receipt contracts | `projects/domainspec-v2/impl/spec/minted-project/` | generated-view contract authority |
| Resolver/compiler behavioral contract | `projects/domainspec-v2/impl/spec/minted-project/` | compiler contract authority |
| Resolver, compiler, validator, generators, minter, and project template | `projects/domainspec-v2/impl/tools/minted-project/` | executable tooling owner |
| Canonical conformance fixtures and evidence | `projects/domainspec-v2/impl/test-derivation-engine/__fixtures__/minted-project/` | conformance witness owner |

Per-file module names below these homes are reversible implementation details.
Changing a concern's authoritative home is not reversible implementation detail
and requires a new owner decision.

### Rationale and consequence

This split keeps vocabulary/profile admission, machine contracts, executable
machinery, and evidence distinct while using existing DomainSpec ownership
surfaces. It costs some navigation, so the refreshed plan must add one index or
manifest linking these homes. No factory template may contain concrete consumer
feature semantics, and generated projections remain read-only outputs.

## Decision 2: first supported profile and admission posture

### Considered options

1. Admit `feature-with-independent-node-files` as an experimental profile after
   its complete validation surface passes.
2. Bind the same profile to the next DomainSpec release immediately.
3. Begin with an existing derivation-engine vertical slice.
4. Begin with cross-feature edges.

### Selected option

**Option 1 — independent node files as an experimental profile.**

### Admission binding

- Profile ID: `feature-with-independent-node-files`.
- Machine source: `projects/domainspec-v2/definitions/minted-project/supported-profiles.yml`.
- Owner: DomainSpec v2 definitions authority.
- Initial status: `experimental`; it is not release admission.
- Effective condition: the source schemas, compiler, validator, deterministic
  projections, positive fixtures, and negative controls all pass, and the
  evaluated registry digest is recorded in the resulting evidence receipt.
- Kind admission: a kind must be enumerated by the selected profile; existence
  in another registry does not imply support.
- Relationship admission: a relationship must be enumerated by the profile and
  active in its owning relationship registry.
- Failure separation: unsupported profile, unsupported kind, invalid shape, and
  non-active relationship state must remain distinguishable validation results.
  Exact error-code spelling is a reversible contract detail within the selected
  machine-contract home.
- Release admission: deferred to a separate owner-bound promotion decision after
  the experimental evidence exists.

### Rationale and consequence

This is the only profile directly supported by the completed toy experiment. It
lets the compiler become executable without converting kind existence or shape
evidence into a release promise. Cross-feature completeness and an independent
edge lifecycle remain outside this profile.

## Decision 3: toy-game evidence disposition

### Considered options

1. Keep the Refine package as immutable development evidence and normalize a
   canonical fixture only during implementation.
2. Promote the Refine package directly into canonical conformance fixtures.
3. Use the Refine package only as the minter's example project.
4. Immediately create separate conformance and example derivatives.

### Selected option

**Option 1 — development witness now; normalize during implementation.**

### Rationale and consequence

The current Refine run remains a development-scoped validation witness and is
not canonical factory authority. A minimal generic derivative may enter the
canonical conformance home only after the selected profile's contracts and
validation conditions exist. This prevents exploratory layout choices from
becoming normative merely because they were useful evidence.

## Decision 4: existing concrete feature-pack disposition

### Considered options

1. Separate misplaced feature specifications from intentional engine fixtures.
2. Keep every current concrete pack as a validation witness in place.
3. Retire the concrete packs and replace them with generic fixtures.
4. Run a new per-pack audit before assigning any disposition.

### Selected option

**Option 1 — boundary-clean split.**

### Disposition binding

| Existing artifact | Disposition | Owner and effective condition |
| --- | --- | --- |
| `projects/domainspec-v2/impl/spec/features/sample/` | `migrate-to-consumer-example` | DomainSpec v2 plan owner; move only after the minter defines a valid consumer-example destination |
| `projects/domainspec-v2/impl/spec/features/financial-settlement/` | `migrate-to-consumer-example` | DomainSpec v2 plan owner; move only after the minter defines a valid consumer-example destination |
| `projects/domainspec-v2/impl/spec/features/agent-execution-orchestrator/` | `migrate-to-consumer-example` | DomainSpec v2 plan owner; move only after the minter defines a valid consumer-example destination |
| `projects/domainspec-v2/impl/test-derivation-engine/__fixtures__/financial-settlement/` | `validation-witness` | test-derivation-engine conformance owner; remains non-authoritative domain evidence |
| `projects/domainspec-v2/impl/test-derivation-engine/__fixtures__/agent-execution-orchestrator/` | `validation-witness` | test-derivation-engine conformance owner; remains non-authoritative domain evidence |
| `projects/domainspec-v2/development/refinement-runs/20260714-minted-project-node-package-toy-game/` | `validation-witness` (development-scoped) | Refine evidence owner; immutable and not canonical conformance input |

`migrate-to-consumer-example` is a classification and future effective
condition, not authorization to move or delete files in this gate. Until a
destination and migration task are approved, the source rows remain in place
but must not be cited as minted-project authority.

### Rationale and consequence

Concrete domains may be retained when they are clearly test evidence, but they
must not occupy a factory contract surface in a way that implies DomainSpec owns
their meaning. This split preserves useful real-world validation while making
the eventual consumer boundary explicit.

## Assumptions recorded

- Directory-level authority homes are binding; individual filenames other than
  the profile registry remain reversible details for Invoke Plan to specify.
- The profile registry uses YAML because the existing DomainSpec definitions
  registries are YAML-backed; changing serialization within the same authority
  home requires contract migration but not a new authority-home decision.
- Generated `graph.json`, `source-manifest.json`, Markdown, and build receipts
  are never hand-authored authority.
- The refreshed plan must preserve separate checks for kind existence, schema
  shape, experimental profile support, relationship activation, and release
  admission.

## Deferred decisions

- Exact consumer-example repository or package destination for the three
  `migrate-to-consumer-example` rows.
- Release promotion of `feature-with-independent-node-files`.
- Cross-feature edge completeness and independent-edge lifecycle ownership.
- Website and interactive mental-map implementation.

None of these decisions blocks refreshing the current factory plan or selecting
its first bounded implementation SWU afterward.

## Remaining blockers

None for Invoke Refresh/Plan. This decision does not itself authorize Task
Session execution: the blocked plan must first be refreshed with these bindings,
its dispatch revalidated, and one SWU explicitly selected.

## Validation and next route

- Decision Gate: **PASS** — four blocker decisions resolved by the operator.
- Consequential implementation mutation: not performed.
- Authority or fixture migration: not performed.
- Next: run Invoke Refresh/Plan against the S09 plan and work-pack, bind these
  paths and dispositions, validate the refreshed dispatch, and present the first
  bounded SWU for Task Session selection.

## Source evidence

- `projects/domainspec-v2/development/refinement-runs/20260714-minted-project-node-package-toy-game/stages/S10-final-synthesis/DECISION-GATE-HANDOFF.md`
- `projects/domainspec-v2/development/refinement-runs/20260714-minted-project-node-package-toy-game/stages/S08-distill-repair/selected-design.json`
- `projects/domainspec-v2/development/refinement-runs/20260714-minted-project-node-package-toy-game/stages/S09-invoke-plan/PLAN.md`
- Operator selections in the 2026-07-14 `decision-gate` conversation.
