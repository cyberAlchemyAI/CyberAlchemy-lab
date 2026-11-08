# DomainSpec Formalization

Status: **contracts-authored candidate package; stable compiler projection implemented separately**

The Stable 1.0 CLI now compiles the complete project graph, emits DS-D8
obligation applicability/predicate/witness data, generates a graph-bound Lean
proof unit, and certifies it through an independent Lean JSON decoder. That
implementation lives in `../impl/cli` and does not implement or adopt the
broader wizard, TDE, provider, or EVF lifecycle described by this package.

This package defines how DomainSpec can turn business meaning into bounded,
checkable evidence without letting a formal tool silently change the meaning.

The intended path is:

```text
business meaning
  -> explicit definition-binding graph
  -> formal signature + canonical proposition / FormalClaim
  -> optional external evaluation context + InterpretationModel
  -> capability assessment and route admission
  -> preservation-backed projection
  -> execution route: TDE neutral obligations -> native source -> provider evidence
     or theorem route: Lean binding -> EVF theorem request -> theorem evidence
  -> EVF evidence join
```

The package manifest, ontology, working method, artifact contracts, candidate
profile registry, and Define wizard question flow now exist. The wizard CLI,
projection adapter, native-source generator, TDE integration, provider
execution, and EVF execution are not implemented. Auth Foundation now contains
the first definition-bound FormalClaim draft and derived consumer envelope.

## Canonical package artifacts

- [`formalization-package.json`](formalization-package.json) — package identity,
  exact sources, ownership boundaries, artifacts, and claim ceiling.
- [`ontology/formalization.ontology.json`](ontology/formalization.ontology.json)
  — business/system bridge ontology for the formalization path.
- [`definitions/formalization-definitions.json`](definitions/formalization-definitions.json),
  [`definitions/formalization-definitions-index.json`](definitions/formalization-definitions-index.json),
  and [`definitions/formalization-definition-drift-audit.json`](/home/vlad_/projects/cyberAlchemy-v2/craft/projects/domainspec-v2/formalization/definitions/formalization-definition-drift-audit.json)
  — 26 package-local critical terms, their deterministic index, and the
  current drift/repair boundary. These candidates reference, but do not
  redefine, Arcanum or CyberAlchemy-v2 authority.
- [`method/formalization-method.json`](method/formalization-method.json) —
  owners, artifacts, visible session states, working stages, outcome meanings,
  change rules, and progressive implementation layers.
- [`schemas/formalization-package.schema.json`](schemas/formalization-package.schema.json)
  — package input contract.
- [`schemas/formalization-ontology.schema.json`](schemas/formalization-ontology.schema.json)
  — ontology input contract.
- [`schemas/formalization-method.schema.json`](schemas/formalization-method.schema.json)
  — working-method input contract for agents and tools.
- [`contracts/formalization-contract-set.json`](contracts/formalization-contract-set.json)
  — all artifact contracts, owners, consumers, compatibility edges, and typed
  outcomes in one machine-readable registry.
- [`profiles/formal-language-profiles.json`](profiles/formal-language-profiles.json)
  — candidate semantic roles and result ceilings for Lean/DTT, FOL, SMT,
  TLA/TLC, Alloy, and Souffle.
- [`authoring/define-wizard.json`](authoring/define-wizard.json) — candidate S0
  through S3 questions and shared CLI/chat session behavior.
- [`schemas/`](/home/vlad_/projects/cyberAlchemy-v2/craft/projects/domainspec-v2/formalization/schemas) — per-artifact input schemas for BusinessMeaning,
  explicit FormalClaim definition binding, FormalClaim v4, a derived consumer
  definition-complete envelope, separate optional EvaluationContext and
  InterpretationModel, capability assessment, neutral
  obligations, projections, preservation, native source, provider evidence,
  EVF joins, authoring sessions, wizard flow, and case packages.
- [`fixtures/contract-fixtures.json`](fixtures/contract-fixtures.json) —
  synthetic positive, exact-cause negative, stale, unknown, duplicate,
  malformed, timeout, and claim-ceiling schema cases.
- [`docs/WORKING-METHOD.md`](docs/WORKING-METHOD.md),
  [`docs/FORMALCLAIM-AND-PROFILES.md`](docs/FORMALCLAIM-AND-PROFILES.md),
  [`docs/UNDERSTANDING-PROJECTION.md`](docs/UNDERSTANDING-PROJECTION.md),
  [`docs/TDE-EVF-INTEGRATION.md`](docs/TDE-EVF-INTEGRATION.md), and
  [`docs/DEFINE-WIZARD.md`](docs/DEFINE-WIZARD.md) — derived human views.
- [`schemas/formal-claim-understanding-projection.schema.json`](schemas/formal-claim-understanding-projection.schema.json)
  — candidate contract for clause- and expression-bound understanding nodes,
  linked definition identities, and a serial human-reading projection. It is
  explanatory only and is not yet emitted by the stable compiler.
- [`validate.mjs`](validate.mjs) — deterministic package, schema-instance,
  source-currentness, graph-closure, and boundary validation.
- [`receipts/`](/home/vlad_/projects/cyberAlchemy-v2/craft/projects/domainspec-v2/formalization/receipts) — append-only validation and review history.

JSON and JSON Schema are canonical. Markdown is human navigation only.

## Opt-in v4 proposition formation

After building the local AlchLang core (`npm run build` in
`language/capabilities/alchlang/plans/general-compiler-v1/implementation`), run
`node craft/projects/domainspec-v2/formalization/validate-claim-formation.mjs`
from the checkout root with one JSON request on stdin:

```json
{"schema_version":"domainspec-v2.formal-claim-formation-request/v1-candidate","root_directory":"/absolute/evidence/root","claim_ref":{"path":"claim.json","sha256":"<64 lowercase hex digits>","size_bytes":123,"current":true},"selected_profile":"fol-core/1-candidate"}
```

The command first validates the exact claim bytes against the full v4 JSON
Schema, then runs the selected AlchLang proposition checker. It emits one JSON
result: `checked` (exit 0), `rejected` (exit 2), or `unsupported` (exit 3).
The result binds the claim, schema and local checker entry bytes (not the
checker's transitive module graph), but it is
**formation-only**: it does not validate accepted meaning, definition closure,
interpretation, admission, TDE, provider execution, EVF, or runtime behavior.
The historical Auth v4 `text/vnd.domainspec.fol-core` source is unsupported,
not an accepted positive case. This opt-in command is separate from the
whole-package `validate.mjs` and does not alter its current provenance blockers.

The definition registry is the candidate authority for package-local term
bodies. The ontology projects those terms into graph nodes; schemas constrain
agent inputs; the index provides lookup. Neither the ontology label, the
index, nor a copied consumer envelope may silently become definition authority.

## Ownership boundary

- Domain projects own their business meaning and specific FormalClaims.
- This package owns the reusable ontology and candidate authoring, profile,
  projection, preservation, native-source, and bridge contracts.
- Define owns the interactive authoring experience and produces JSON source
  payloads; wizard state is not business acceptance or formal proof.
- Validation governance owns capability classification and admission policy.
- TDE owns neutral obligation and case derivation.
- Formal providers own bounded checks of selected projections and exact
  provider-runtime bindings.
- EVF owns actual provider selection, theorem requests, and the exact evidence
  join. TDE may only emit provider-routing candidates.

A provider result does not become business authority merely because the
provider can check one projection.

## How we work with the module

The normal working sequence is:

1. Scope one business question and name its owner and claim ceiling.
2. Record BusinessMeaning in normal domain language with examples and
   counterexamples, then attach stable definitions whose formal voice is
   normative and whose plain-language and domain-context voices are
   explanatory. Each definition points to the business facts it explains. An
   accepted successor explicitly changes its supersession effect and accepts
   every inline definition; a draft cannot claim accepted supersession.
3. Declare the claim's definition dependencies as explicit `uses_definition`
   graph edges, including every transitive dependency. Do not infer edges from
   names.
4. Bind one formal signature and CanonicalProposition into a schema-valid
   FormalClaim source. InterpretationModel is not a claim field.
5. If evaluation needs an InterpretationModel, bind it later as an external
   evaluation context.
6. Let validation governance classify the exact claim and admit one bounded
   route.
7. Create a preservation-backed projection for that route before executable
   TDE derivation.
8. Let TDE derive neutral cases only for an admitted executable projection, or
   bind the selected EVF theorem/solver/model route request.
9. Run one bounded provider check over exact inputs and environment.
10. Let EVF join current evidence to the exact claim and selected route subject
   — an execution obligation or theorem request — then state only the bounded
   conclusion. `PASS_BOUNDED` requires every bound reference to be current and
   the case package to point to that exact EVF join.

When something changes, restart at the earliest meaning-bearing artifact that
changed. A business definition, definition graph, formal signature, assumption,
proposition, or ceiling change creates a new FormalClaim identity. An
InterpretationModel change creates a new evaluation-context identity, not a new
FormalClaim. Adding another provider for the same meaning creates a new
projection and evidence, not a second business truth.

The method grows in five layers:

- **L0:** manually author one Auth Foundation rule through a reviewed
  FormalClaim source; no provider or proof claim.
- **L1:** complete one bounded TDE → provider → EVF evidence vertical.
- **L2:** make authoring interactive, visible, resumable, and deterministic in
  Define CLI and chat.
- **L3:** add multiple providers and harden unsupported, indeterminate, stale,
  missing, and failed outcomes.
- **L4:** prove the package can be reused by a second domain without inheriting
  Auth-specific meaning.

## Legacy imported evidence

[`DomainSpecEdgeSignature.lean`](DomainSpecEdgeSignature.lean) remains an exact
imported Lean snapshot. It is useful evidence that an edge-signature rule can
be stated and checked in Lean, but it is not this package's authority, current
relationship source, runtime, or proof of the new formalization model.

Its known drift is preserved intentionally:

- the snapshot has an older meta-type and edge vocabulary;
- `enforcesCross` is stale;
- current `owns`, `belongs-to`, and `creates` relations are absent;
- `applies` and `reads` differ from current relationship authority;
- its `associates` extension is not a current root signature.

Do not hand-edit the Lean snapshot to hide this drift. A later, separately
selected derivation design may generate formal provider sources from current
authority.

## Next boundary

Independently review the Auth Foundation v4 FormalClaim draft, its explicit
definition closure, and its deterministic consumer envelope. FormalClaim
admission remains a separate owner decision. Current TDE intake still requires
an exact `FormalClaimSourcePayload/v2` projection; v4 is not adopted. Do not
derive obligations or execute providers in L0.
