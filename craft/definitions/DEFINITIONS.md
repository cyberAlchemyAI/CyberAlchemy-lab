<!-- MINT-ACT OUTPUT (L1) for domainspec-v2. Cast from templates/definitions.md. INTERNAL/private.
     INHERITS the three-voice card FORMAT. SKELETON: seeds 2 cards; the owner authors the rest via the
     definitions lifecycle. Obs-B: an Evidence cav2/v1 citation is provenance, never a resolution path. -->

# DomainSpec v2 Local Definition Cards

Status: active
Promotion scope: local-domainspec-v2-only
Canonical source: yes

Local definitions for this repository. They do not define the implementation contract, governance
weight, launch readiness, or external policy. Each card keeps three voices (Formal / Plain-language /
Domain-context).

> **Citation vs authority (Obs-B).** A card's `Evidence:` MAY cite a harvested v1/cav2 snapshot —
> that is provenance, not a resolution path. The normative meaning is owned **here**; removing the
> framework attachment does not change it. A `Source kind:` of method-authority points at **this
> repo's own constitution**, never at v1 or cav2.

## domainspec-v2-D1. Drift

Source kind: operator-reading; local-inference

Evidence: [impl/spec/DRIFT-CONVERGENCE.md](../impl/spec/DRIFT-CONVERGENCE.md)

Formal voice:

```text
drift =
  measurable divergence between intended DomainSpec behavior and observed system reality
  across surfaces { semantic, contract, runtime, governance, coordination }
convergence =
  evidence-backed sustained reduction of critical drift over time
```

Plain-language voice: drift is the problem signal — the spec and reality have pulled apart;
convergence is the trend of pulling them back, with receipts.

Domain-context voice: the subject of **drift governance**; measured across the 5 surfaces, acted on
(not defined) by Saturn.

Use carefully: drift is a *signal*, not a correction; one signal is not (non-)convergence.

Misuse warning: do not conflate drift (the divergence) with Saturn (the loop that acts on it), or
detecting drift with converging.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a claimed drift not
measurable across the 5 surfaces" → challenges the term; owner route = definitions-governance; gate = owner
decision; blocking question = "measurable divergence across {semantic, contract, runtime, governance,
coordination}?"; residue → definitions/reviews/.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
the 5-surface measurement is realized (BLK-DSV2-DRIFT-ENGINE) + no open contradiction; gate =
definitions-governance owner gate; status = active.

Promotion boundary: local-only (grounds drift-governance; not an external policy term)

## domainspec-v2-D2. Validation governance ⟵ *domain-originated*

Source kind: local-inference  *(may cite v1 precedent in Evidence — citation only)*

Evidence: [authority/AUTHORITY-MODEL.md](../authority/AUTHORITY-MODEL.md),
[impl/spec/TEST-PIPELINE.md](../impl/spec/TEST-PIPELINE.md)

Formal voice:

```text
validation governance =
  the authority over BUILD-TIME FIDELITY of a typed spec:
    which obligations it must derive into (TEST-PIPELINE -> engine derive)
    AND what counts as pass/fail (engine lint; audit-alignment)
  resolving to THIS repo's authority/, never to a framework
```

Plain-language voice: the authority that says "for this typed spec, these checks must hold, and here
is what passing means" — exercised by the engine `derive`/`lint`, `generate-tests`, `audit-alignment`.

Domain-context voice: one of v2's three domain-originated governances (owner route
`validation-governance`); the methods are the already-built tools, the governance is the authority
over them.

Use carefully: build-time fidelity is necessary, not sufficient — it is not runtime conformance.

Misuse warning: do not treat a passing derived test as correctness, and do not collapse it into
cav2's `gate` / SMT meta-validation (that is meta-validation of governance rules; this is object
validation of specs/impls).

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "treating build-time
fidelity as runtime correctness, or collapsing it into cav2's gate / SMT meta-validation" → challenges the
term; owner route = definitions-governance; gate = owner decision; blocking question = "is this object-level
validation of a typed spec, resolving to THIS repo's authority?"; residue → definitions/reviews/.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner ratifies the
kind (done 2026-06-29) + the L2 attestation seal (BLK-DSV2-L2-ATTESTATION); gate = definitions-governance
owner gate; status = active (RATIFIED; L2 seal pending).

Promotion boundary: RATIFIED kind (owner, 2026-06-29); L2 attestation seal pending

## domainspec-v2-D3. Edge-Law Admissibility ⟵ *build-from-owned (CAV2-D22/D29/D16)*

Source kind: local-inference  *(cites cav2 CAV2-D22/D29/D16 in Evidence — citation only)*

Evidence: [development/reformulate-batch1/DESIGN.md](../development/reformulate-batch1/DESIGN.md) (R3),
[research/2026-07-01-composability-edges-taxonomy-synthesis.md](../research/2026-07-01-composability-edges-taxonomy-synthesis.md);
provenance: cav2 CAV2-D22 (orthogonal classification), CAV2-D29 (axis orthogonality), CAV2-D16 (typed coupling)

Formal voice:

```text
edge-law admissibility =
  an edge TYPE is admissible IFF it composes into different code
  (adds a non-redundant distinction over the axes
   {concept-type, relation-kind, composition-shape, feature-boundary})
corollary =
  widen a SOURCE endpoint (same target, same semantics) = clean
  change the TARGET type = overload -> reject
```

Plain-language voice: an edge deserves its own name only if it makes the code compose differently; else
widen an existing edge or add a flag. Widening *who* uses an edge is fine; changing *what it points at* is not.

Domain-context voice: governs R3 (RELATIONSHIPS reformulation). Rulings: keep `enforces`≠`applies`; collapse
`enforces`/`enforces-cross`; reject the former `queries` label for Calc→Policy; and widen
`applies`→Policy→{Op,Calc}. The 2026-08-23 owner decision supersedes the earlier broad
`queries`→Behavioral→Entity ruling with `reads`→{Query,Operation}→Entity: the edge names an Entity-data
dependency, while Calculation remains a pure function over explicit inputs. See DEC-DSV2-EDGE-ADMISSIBILITY
and the BMC-REL-001 decision record.

Use carefully: this is classification/governance orthogonality (CAV2-D22/D29), NOT Lean/Hilbert projector
orthogonality (excluded from cav2 authority).

Misuse warning: do not overload an edge's target type to reuse a name; do not conflate with the
linear-algebra orthogonality.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "an edge type that does
NOT compose into different code yet claims its own type (or a target-type overload)" → challenges the term;
owner route = definitions-governance; gate = owner decision (cites CAV2-D22/D29/D16); blocking question =
"does the edge add a non-redundant distinction over {concept-type, relation-kind, composition-shape,
feature-boundary}?"; residue → definitions/reviews/.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
the R3 rulings applied to RELATIONSHIPS.md + no open contradiction; gate = definitions-governance owner gate;
status = active.

Promotion boundary: local-only (governs the v2 edge-law; cites cav2, transfers no cav2 authority)

## domainspec-v2-D4. Executable Typed Graph

Source kind: local-inference; synthesis

Evidence: [research/2026-07-01-composability-edges-taxonomy-synthesis.md](../research/2026-07-01-composability-edges-taxonomy-synthesis.md)

Formal voice:

```text
executable typed graph =
  the spec surface as ONE graph:
    nodes   = TAXONOMY meta-types (each -> one code pattern)
    edges   = RELATIONSHIPS typed edge-law
    realize = composability (how connected patterns reference each other in code)
  governed on 3 axes: layering (structure) / validation (derivation) / drift (alignment)
```

Plain-language voice: the spec is a typed graph you can build code from — the things (nodes), how they
connect (edges), and how each connection turns into code (composability).

Domain-context voice: thesis of the composability/edges/taxonomy synthesis; the substrate the spec-ontology
toy tested (verdict SURVIVED-narrow). Two enforcement arms: engine derivation (validation) + code-tag
composability (drift).

Use carefully: "executable" = derivable/checkable, not that the spec runs.

Misuse warning: do not collapse the three axes; engine derivation (moat) ≠ the composability check.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "collapsing the three
axes, or equating engine derivation with the composability check" → challenges the term; owner route =
definitions-governance; gate = owner decision; blocking question = "are nodes / edges / composability + the
three axes all distinct here?"; residue → definitions/reviews/.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
the composability/edges/taxonomy synthesis evidence holds + no open contradiction; gate =
definitions-governance owner gate; status = active.

Promotion boundary: local-only

## domainspec-v2-D5. Two-Plane Boundary

Source kind: local-inference (resolves the spec-as-ontology research)

Evidence: [research/2026-07-01-spec-as-ontology/findings.md](../research/2026-07-01-spec-as-ontology/findings.md)

Formal voice:

```text
two-plane boundary =
  ontology framing governs the AUTHORING plane (writing/editing/organizing the spec)
  derivation governs the CONTRACT plane (the crisp, total, engine-facing spec)
  authority flows contract -> authoring, never reverse
```

Plain-language voice: use ontology tooling while you write the spec, but the strict engine-facing spec stays
the source of truth — help flows one way only.

Domain-context voice: interim stance while DEC-DSV2-LANE-ZA (fuse vs generate) is deferred to an agent-cost
experiment.

Use carefully: authoring-plane metadata (confidence/premises) is non-authoritative over the crisp docs until
an owner route ratifies a consumer.

Misuse warning: do not let authoring-plane ontology labels leak into the engine-facing contract docs.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "authoring-plane labels
leaking into the engine-facing contract, or authority flowing authoring → contract" → challenges the term;
owner route = definitions-governance; gate = owner decision; blocking question = "does authority flow
contract → authoring only?"; residue → definitions/reviews/.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
DEC-DSV2-LANE-ZA resolved (or the interim two-plane stance holds) + no open contradiction; gate =
definitions-governance owner gate; status = active (interim).

Promotion boundary: local-only

## domainspec-v2-D6. meta-type

Source kind: method-vocabulary; local-inference

Evidence: [meta-types/meta-types.yml](./meta-types/meta-types.yml) (machine authority) ·
[meta-types/meta-types.md](./meta-types/meta-types.md) (three-voice human companion)

Formal voice:

```text
meta-type =
  one retained label in the 24-member staged DS-D1 node alphabet.
  every concept declares exactly one meta-type; it fixes the concept's well-formedness
  criterion, its edge participation, and the code pattern it maps to.
```

Plain-language voice: one of the 24 staged concept labels a DomainSpec aspect file may be built from — the
node alphabet, like parts of speech for a domain spec. Only the 13 backend types are active today; the nine UI
candidates and two deferred UI labels are not active types.

Domain-context voice: the node vocabulary the content validator checks against. The active backend set is
`DS-D1.1..9` plus `DS-D1.11..14`; `DS-D1.10 Saga` is superseded and never reused; `DS-D1.15..23` are UI
candidates; `DS-D1.24` and `.25` are deferred merge/split candidates.

Use carefully: a meta-type is a **node kind**; the relationships between them are **edge verbs** (`DS-D2`), a
separate vocabulary.

Misuse warning: do not conflate a meta-type (the kind) with a **concept** (an instance of a kind) or with a
**category** (the grouping of kinds).

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a concept that fits no
meta-type, needs two, or two meta-types that reduce to one — neither composes into different code from the
other" → challenges the staged-set closure and irredundancy; owner route = definitions-governance; gate = owner
decision; blocking questions = (1) "does every supported concept map to exactly one active type?" (2) "does each active type
compose into different code, or do two collapse into one node?" — the non-collapse challenge (the node-side
mirror of the D3 edge-law) is checked by `impl/tools/validate-meta-types-noncollapse.ts`: a separating structural
witness OR an authority-resolved separating edge witness, with an owner-enumerated exception lane for the
formal_return_type sort (Rule/Policy/Calculation); residue → `definitions/reviews/`. Third challenge staged
2026-07-08 (candidate); see `definitions/reviews/2026-07-08-d6-node-noncollapse.md`.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
the selected profile's type set is exercised on ≥1 real aspect + no open contradiction; gate = definitions-governance owner
gate; status on confirm = candidate → active.

Promotion boundary: local method vocabulary (DomainSpec v2); names the node alphabet, not an external policy term.

## domainspec-v2-D7. category

Source kind: method-vocabulary; local-inference

Evidence: [meta-types/meta-types.yml](./meta-types/meta-types.yml) · [meta-types/](./meta-types/meta-types.md)

Formal voice:

```text
category =
  the top-level grouping of meta-types: Structural | Behavioral | Connective | Lifecycle | UI.
  each meta-type belongs to exactly one category; categories mirror the meta-types/<category>/ layout.
```

Plain-language voice: the family a meta-type belongs to, grouped by what it does: structural (things),
behavioral (actions), connective (bridges), lifecycle (evolution), UI.

Domain-context voice: organizes the 24 staged labels and the active backend schema folders
(`impl/spec/meta-types/<category>/`); the authoring walkthrough proceeds category by category.

Use carefully: a category groups **kinds** (meta-types), not concepts.

Misuse warning: don't conflate a category (Structural) with a meta-type (Entity) or a concept
(PaymentTransaction).

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a meta-type that fits
no category, or two" → challenges the five-family closure; owner route = definitions-governance; gate = owner
decision; blocking question = "does each meta-type belong to exactly one family?"; residue → `definitions/reviews/`.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
all staged labels assigned to exactly one category + no open contradiction; gate = definitions-governance owner
gate; status on confirm = candidate → active.

Promotion boundary: local method vocabulary (DomainSpec v2).

## domainspec-v2-D8. formal criterion

Source kind: method-vocabulary; local-inference

Evidence: [meta-types/](./meta-types/meta-types.md) (each card's Formal voice) ·
[impl/spec/meta-types/](../impl/spec/meta-types/) (the `.schema.yml` criteria)

Formal voice:

```text
formal criterion =
  a decidable predicate over a concept's structure: concept C is a well-formed T iff criterion_T(C).
  authored in <type>.schema.yml (structural rule kinds); checkable WITHOUT running the engine.
```

Plain-language voice: the machine-checkable rule per meta-type (in its `.schema.yml`) — the exact structural
conditions a concept must meet to count as that type.

Domain-context voice: the checkable core of each DS-D1 card; the content validator applies it. Distinct from
TAXONOMY's descriptive prose (which says what a type is *like*, not *exactly when* a concept qualifies).

Use carefully: a formal criterion checks **shape**, not meaning; a check that needs the engine to decide is a
boundary flag, not a criterion.

Misuse warning: do not equate the formal criterion (public shape check) with the engine's δ-derivation
(private — the moat).

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a criterion decidable
only by running derivation" → challenges its public-checkability; owner route = definitions-governance; gate =
owner decision; blocking question = "can it be checked structurally, without the engine?"; residue → `definitions/reviews/`.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
the criterion runs in the validator (pos/neg fixtures discriminate) + no open contradiction; gate =
definitions-governance owner gate; status on confirm = candidate → active.

Promotion boundary: local method vocabulary (DomainSpec v2); a public shape check, never the engine
δ-derivation (moat).

## domainspec-v2-D9. edge-participation signature

Source kind: method-vocabulary; local-inference  *(method term that cites domain authority `DS-D8`)*

Evidence: [relationships.yml](./relationships/relationships.yml) ·
[relationships.md](./relationships/relationships.md) · [meta-types/](./meta-types/meta-types.md)
(each card's edge-participation slice)

Formal voice:

```text
edge-participation signature (DS-D8) =
  the method term for asking whether a meta-type may participate
  as source or target of a declared relationship.
  It is realized by DS-D8, the domain relationship-signature authority.
```

Plain-language voice: the who-may-connect-to-whom rule — for each edge verb, the allowed source and target
meta-types; a declared edge with wrong endpoints is rejected.

Domain-context voice: the DS-D8 slice each meta-type card lists (SOURCE of / TARGET of) is now loaded from
root `definitions/relationships/relationships.yml`. Current authority has 31 active signatures; generated
views such as `owned-by` are navigation only. Distinct from the relationship verb vocabulary (`DS-D2`).

Use carefully: the signature types the **endpoints**; *which* edges earn a type is edge-law admissibility
(`domainspec-v2-D3`), a separate question.

Misuse warning: do not conflate the signature (endpoint typing) with the edge **verb** (`DS-D2`, the
relationship name) or with **admissibility** (`domainspec-v2-D3`).

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a declared edge whose
endpoints violate the signature yet is claimed valid" → challenges the signature; owner route =
definitions-governance; gate = owner decision; blocking question = "do both endpoints' meta-types match the
verb's signature?"; residue → `definitions/reviews/`.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
DS-D8 authority lands in `definitions/relationships/relationships.yml` + the validator checks endpoints + no
open contradiction; gate = definitions-governance owner gate; status on confirm = active.

Promotion boundary: local method vocabulary (DomainSpec v2); it names the participation-check method and
does not redefine DS-D8.

## domainspec-v2-D10. content validator

Source kind: method-vocabulary; local-inference

Evidence: [impl/tools/validate-content.ts](../impl/tools/validate-content.ts) · [impl/spec/meta-types/](../impl/spec/meta-types/)

Formal voice:

```text
content validator =
  validate-content(aspect_file): for each concept C with declared type T, run criterion_T(C);
  for each declared edge E(a --verb--> b), check the DS-D8 signature against type(a), type(b).
  returns { valid, violations[] }. a build-time fidelity check; no δ-rule import.
```

Plain-language voice: a linter for the spec's content — not just that types are declared, but that each
concept is well-formed and each edge is admissible.

Domain-context voice: the validation-governance method (`impl/tools/validate-content.ts`); extends
`validate-relationships` with per-type content checks; distinct from `engine lint` and engine `derive`.

Use carefully: it checks build-time **shape** fidelity, not runtime correctness.

Misuse warning: do not collapse it into the engine (`derive` / δ-rules) — it is the public contract, kept
consistent with the engine but not importing its algorithm.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a validity claim that
requires running derivation" → challenges its public-check boundary; owner route = definitions-governance;
gate = owner decision; blocking question = "does it decide validity by structure, without the engine?";
residue → `definitions/reviews/`.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
validate-content runs on a real feature (a seeded violation flips it) + wired into `npm run validate` + no
open contradiction; gate = definitions-governance owner gate; status on confirm = candidate → active.

Promotion boundary: local method vocabulary (DomainSpec v2); a public validation-governance method, never the
engine δ-derivation (moat).

## domainspec-v2-D11. instance

Source kind: method-vocabulary; local-inference

Evidence: [impl/tools/instances.ts](../impl/tools/instances.ts) · [meta-types/meta-types.yml](./meta-types/meta-types.yml) (the machine registry pattern)

Formal voice:

```text
instance =
  a concept normalized to structured YAML conforming to its meta-type schema (<concept>.instance.yml):
    a declared meta_type + fields / values / attributes as data.
  the machine-readable form; validated against the SAME criterion as the authored markdown.
```

Plain-language voice: the machine-readable twin of an authored concept — the same concept expressed as data
(fields, attributes) a tool can consume, not prose.

Domain-context voice: the MT-INST surface (`impl/tools/instances.ts generate`, DEF-D3 = source B); generated
example instances live under `impl/spec/__generated__/` (gitignored).

Use carefully: an instance is a machine **form** of a concept, not a new concept; it conforms to — does not
redefine — its meta-type schema.

Misuse warning: do not confuse an instance (data conforming to a schema) with the **schema** itself (the
criterion) or with the concept's markdown card.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "an instance that claims
conformance but violates its schema criterion" → challenges the instance; owner route = definitions-governance;
gate = owner decision; blocking question = "does the instance satisfy its meta-type criterion?"; residue →
`definitions/reviews/`.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
generated instances validate round-trip (ok passes, mutated rejected) + no open contradiction; gate =
definitions-governance owner gate; status on confirm = candidate → active.

Promotion boundary: local method vocabulary (DomainSpec v2); a public shape artifact, never the engine
δ-derivation (moat).

## domainspec-v2-D12. instance validator

Source kind: method-vocabulary; local-inference

Evidence: [impl/tools/instances.ts](../impl/tools/instances.ts) · [impl/tools/tests/instances.test.ts](../impl/tools/tests/instances.test.ts)

Formal voice:

```text
instance validator =
  instances validate: for each <concept>.instance.yml, load its meta-type schema and apply the same
  criterion rules to the instance's structured data (fields / values / attributes).
  returns pass | violations. shape only; no δ-rule import.
```

Plain-language voice: the `instances validate` mode — load each `<concept>.instance.yml`, apply its schema
criterion, accept conforming / reject malformed.

Domain-context voice: `impl/tools/instances.ts` (validate mode); the machine-side counterpart of the content
validator; proven by `tools/tests/instances.test.ts` (generate → validate; mutated → reject).

Use carefully: it checks the generated instance's **shape** against the schema, not meaning.

Misuse warning: do not conflate it with the content validator (markdown) or the engine (`derive`) — it is the
instance-side public shape check.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "an instance passing the
validator but violating the schema criterion" → challenges the validator; owner route = definitions-governance;
gate = owner decision; blocking question = "does it apply the same criterion the schema declares?"; residue →
`definitions/reviews/`.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
the round-trip test is green (generate → validate passes; mutated → rejected) + no open contradiction; gate =
definitions-governance owner gate; status on confirm = candidate → active.

Promotion boundary: local method vocabulary (DomainSpec v2); a public shape check, never the engine
δ-derivation (moat).

## domainspec-v2-D13. aspect file

Source kind: method-vocabulary; local-inference

Evidence: [impl/spec/features/sample/SPEC.md](../impl/spec/features/sample/SPEC.md) · [impl/spec/__fixtures__/mt/](../impl/spec/__fixtures__/mt/) (minimal aspect files)

Formal voice:

```text
aspect file =
  a markdown spec document for a feature: a Concept Registry (concept -> meta-type) + per-concept tables
  (fields / attributes) + declared edges. the human-authored unit the content validator reads.
```

Plain-language voice: a spec doc that declares concepts and their meta-types + fields/edges — the
human-authored source the content validator checks.

Domain-context voice: e.g. `impl/spec/features/<feature>/SPEC.md`; the `__fixtures__/mt/*.md` are minimal
aspect files; its granularity is the content validator's input.

Use carefully: "aspect" = a facet of a feature's spec; the validator's input granularity is the aspect file.

Misuse warning: do not confuse the aspect file (human markdown) with an **instance** (machine YAML) — both
are validated, but they are different forms.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a spec doc with concepts
but no registry/tables the validator can read" → challenges the aspect-file shape; owner route =
definitions-governance; gate = owner decision; blocking question = "does it carry a Concept Registry +
per-concept tables?"; residue → `definitions/reviews/`.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
a real feature aspect file validates + no open contradiction; gate = definitions-governance owner gate;
status on confirm = candidate → active.

Promotion boundary: local method vocabulary (DomainSpec v2).

## domainspec-v2-D14. Concept Registry

Source kind: method-vocabulary; local-inference

Evidence: [impl/tools/validate-content.ts](../impl/tools/validate-content.ts) (reads it first) · [impl/spec/__fixtures__/mt/](../impl/spec/__fixtures__/mt/)

Formal voice:

```text
Concept Registry =
  a table in an aspect file: Concept | Type (a meta-type), optionally an ID.
  it declares each concept's meta-type; the content validator reads it to dispatch the right criterion.
```

Plain-language voice: the concept-to-meta-type map for a feature — it says "PaymentTransaction is an Entity,"
so the validator knows to run the Entity criterion.

Domain-context voice: the first thing the content validator parses; definitions-governance (M2-C1) aggregates
per-feature registries into the non-authoritative project-level
[CONCEPT-REGISTRY.json](./CONCEPT-REGISTRY.json) read model.

Use carefully: the registry declares the **type**; the concept's structure (fields / attributes) is in its
own table below.

Misuse warning: a concept absent from the registry is untyped — the validator can't check it; do not rely on
headings alone.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a concept used but not
registered with a meta-type" → challenges the registry's completeness; owner route = definitions-governance;
gate = owner decision; blocking question = "is every concept declared with a meta-type here?"; residue →
`definitions/reviews/`.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
a real aspect file's registry drives validation + no open contradiction; gate = definitions-governance owner
gate; status on confirm = candidate → active.

Promotion boundary: local method vocabulary (DomainSpec v2).

## domainspec-v2-D15. declared-attributes convention

Source kind: method-vocabulary; local-inference (owner decision 2026-07-02)

Evidence: [meta-types/](./meta-types/meta-types.md) (behavioral/connective/lifecycle cards) · [impl/spec/meta-types/](../impl/spec/meta-types/) (the `attribute-*` rule kinds)

Formal voice:

```text
declared-attributes convention =
  behavioral / connective / lifecycle concepts declare their discriminators in an Attribute | Value table;
  the validator reads the declared value (attribute-equals / attribute-present) instead of parsing the
  Formal cell. shape-only; keeps the semantic parse behind the engine moat.
```

Plain-language voice: declare-don't-infer — instead of the validator guessing a concept's kind from its body,
the concept states its discriminating attributes (`state_change`, `formal_return_type`, `scope`, …) in a table.

Domain-context voice: the owner decision (2026-07-02) powering the MT2/MT3 discriminators (`state_change`,
`formal_return_type`, `scope`, `temporal`, `direction`, `interface_kind`, `has_transitions`).

Use carefully: it trades some rigor (author self-declaration) for moat-safety — a declared value is checked,
not proven.

Misuse warning: do not infer the discriminator by parsing the Formal cell — that crosses into the engine moat
(a DEFINE-FALSIFIED boundary).

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a discriminator
decidable only by parsing the body, not declarable" → challenges the convention's coverage; owner route =
definitions-governance; gate = owner decision; blocking question = "can the discriminator be a declared value,
or does it need a semantic parse?"; residue → `definitions/reviews/`.

Confirm contract (promotion — build-from-owned on the cav2 promotion gate): promotes when = owner approves +
the declared attributes discriminate all behavioral/connective/lifecycle pairs (tests green) + no open
contradiction; gate = definitions-governance owner gate; status on confirm = candidate → active.

Promotion boundary: local method vocabulary (DomainSpec v2); declared-value checks, never the engine semantic
parse (moat).

## domainspec-v2-D16. Layering governance

Source kind: local-inference (domain-originated; RATIFIED kind)

Evidence: [authority/AUTHORITY-MODEL.md](../authority/AUTHORITY-MODEL.md),
[authority/constitutions/domainspec-v2-CONSTITUTION.md](../authority/constitutions/domainspec-v2-CONSTITUTION.md),
[development/reformulate-batch1/implementation-layering.md](../development/reformulate-batch1/implementation-layering.md),
[domainspec-v2-D3](#domainspec-v2-d3), [DS-D8](#ds-d8)

Formal voice:

```text
layering governance =
  the domain-local authority over structural fidelity:
    each concept's architectural layer assignment
    AND the layer-law / Edge-Law admissibility of typed dependencies.

layer-admissible relation =
  a relation admitted by active DS-D8 relationship signature authority
  AND not forbidden by the C6 layer-law / adapter-line boundary.

forbidden edge =
  unconstructible, not merely flagged after construction.
```

Plain-language voice: layering governance decides what may be connected, before any validator reports
whether a specific document obeys that structure.

Domain-context voice: one of v2's three ratified domain-originated governances. It owns the law side of the
layering -> validation -> drift chain: layer membership, C6, and Edge-Law admissibility. Validation tools
exercise this law, but do not own it.

Use carefully: a layer assignment is evidence for structure, not itself a dependency-law verdict. DS-D8
identifies active relationship signatures; layering governance decides whether the structural dependency is
admissible under the layer-law and adapter-line boundary.

Misuse warning: do not approve a cross-layer edge the law forbids, treat a forbidden edge as a warning, or
collapse the layering law into the validation check that detects violations.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a relation is treated as
constructible while C6, the adapter-line boundary, or active DS-D8 authority forbids it" -> challenges the
term; owner route = definitions-governance; gate = owner decision; blocking question = "is the structure
layer-admissible, and is the validator checking rather than owning the law?"; residue -> `definitions/reviews/`.

Confirm contract (promotion -- build-from-owned on the cav2 promotion gate): promotes when = owner ratifies
the kind (done 2026-06-29) + the L2 attestation seal (BLK-DSV2-L2-ATTESTATION) + no open contradiction; gate =
definitions-governance owner gate; status = active (RATIFIED; L2 seal pending).

Promotion boundary: RATIFIED local DomainSpec v2 governance kind; authority over structural fidelity only.
It does not amend cav2's closed governance enumeration, external policy, or the implementation contract.

## domainspec-v2-D17. Drift governance

Source kind: local-inference (domain-originated; RATIFIED kind)

Evidence: [authority/AUTHORITY-MODEL.md](../authority/AUTHORITY-MODEL.md),
[authority/constitutions/domainspec-v2-CONSTITUTION.md](../authority/constitutions/domainspec-v2-CONSTITUTION.md),
[impl/spec/DRIFT-CONVERGENCE.md](../impl/spec/DRIFT-CONVERGENCE.md),
[domainspec-v2-D1](#domainspec-v2-d1)

Formal voice:

```text
drift governance =
  the domain-local authority over temporal fidelity / convergence:
    whether measurable drift across
    {semantic, contract, runtime, governance, coordination}
    is being reduced over time with evidence.

convergence verdict =
  an evidence-backed trend over a stream of drift signals,
  never one passing check or one observed signal.

write-authority proviso =
  no modeling surface may write directly to a node's promotion-status.
```

Plain-language voice: drift governance decides whether the spec and reality are getting closer over time,
using evidence across the drift surfaces instead of one red/green signal.

Domain-context voice: one of v2's three ratified domain-originated governances. It owns the drift/convergence
ledger and temporal-fidelity verdicts. `DRIFT-CONVERGENCE.md` is the operational reference; Saturn is the
actuator that acts on drift signals, not the authority that defines drift governance.

Use carefully: drift is the divergence signal (`domainspec-v2-D1`); drift governance is the authority for
trend judgement; Saturn is the corrective loop. Keep those three roles separate.

Misuse warning: do not declare convergence from a single passing check, let a modeling surface write
promotion status, or conflate the Saturn control loop with the governance kind.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a convergence claim is
made from one signal, or a drift/control surface writes promotion-status directly" -> challenges the term;
owner route = definitions-governance; gate = owner decision; blocking question = "is there evidence-backed
reduction of drift over time across the relevant surfaces without violating write authority?"; residue ->
`definitions/reviews/`.

Confirm contract (promotion -- build-from-owned on the cav2 promotion gate): promotes when = owner ratifies
the kind (done 2026-06-29) + the L2 attestation seal (BLK-DSV2-L2-ATTESTATION) + no open contradiction; gate =
definitions-governance owner gate; status = active (RATIFIED; L2 seal pending).

Promotion boundary: RATIFIED local DomainSpec v2 governance kind; authority over temporal fidelity and
convergence only. It does not write promotion status, define Saturn, or transfer authority to external policy.

## domainspec-v2-D18. relationship non-collapse test

Source kind: method-vocabulary; local-inference; build-from-owned

Evidence: [domainspec-v2-D3](#domainspec-v2-d3) ·
[relationships.yml](./relationships/relationships.yml) · [relationships.md](./relationships/relationships.md) ·
[development/r3-research/ds-d1-metatype-category-boundary/findings.md](../development/r3-research/ds-d1-metatype-category-boundary/findings.md)

Formal voice:

```text
relationship non-collapse test =
  DomainSpec v2's DS-D2/DS-D8-local import of the CAV2 non-collapse discipline
  through domainspec-v2-D3 edge-law admissibility.

relationship_non_collapse_properties =
  {
    reject/allow decision,
    derivation consequence,
    projection consequence,
    composition path consequence,
    owner route consequence,
    generated artifact consequence
  }

  a candidate relationship is eligible for authored DS-D2/DS-D8 authority
  only if removing that relationship would change at least one member of
  relationship_non_collapse_properties.

otherwise =
  keep the candidate as prose, display notation, generated view,
  attribute/scope metadata, reading aid, or deferred design pressure.
```

Plain-language voice: an edge deserves its own relationship name only if taking the edge away changes one of
the named properties. If nothing changes except wording, it collapses into an existing edge, metadata, a
generated view, or explanation.

Domain-context voice: this is the R3/DS-D8 promotion filter and the local use of the CAV2 non-collapse test.
It explains why `owned-by` is generated view only, `enforces-cross` collapsed into `enforces` plus scope
metadata, `depends-on` remains deferred, and `owns` / `belongs-to` stay distinct because they change
validation, projection, and owner-routing behavior.

Use carefully: the test decides whether a relationship should be first-class. It does not by itself prove
that every endpoint signature, validator rule, or category law has been implemented.

Misuse warning: do not promote a relationship because the phrase is intuitive, repeated in docs, easy to draw
as `Source --[verb]--> Target`, or useful as reverse navigation. Do not cite an unnamed "consequence"; cite at
least one tracked property card.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a relationship remains
first-class after removal changes none of the tracked non-collapse properties" -> challenges the term; owner
route = definitions-governance; gate = owner decision; blocking question = "which tracked property changes if
this relationship is removed?"; residue ->
`definitions/reviews/`.

Confirm contract: active after owner-approved R3A root relationship authority and endpoint validation; future
candidate relationships must cite at least one changed non-collapse property before promotion. Gate =
definitions-governance owner gate.

Promotion boundary: local DomainSpec v2 method vocabulary; governs relationship promotion, not DS-D1
meta-type formation and not full category-law authority.

## domainspec-v2-D20. reject/allow decision

Source kind: method-vocabulary; local-inference

Evidence: [domainspec-v2-D18](#domainspec-v2-d18) · [DS-D8](#ds-d8) ·
[validate-relationships.ts](../impl/tools/validate-relationships.ts)

Formal voice:

```text
reject/allow decision =
  an explicit validator or owner-gate outcome where a candidate relationship changes
  whether a declared edge, endpoint pairing, fixture, or relationship label is accepted
  or rejected.
```

Plain-language voice: the edge matters if it changes a red/green decision: this relationship row is allowed,
that one is rejected.

Domain-context voice: DS-D8 endpoint validation is the primary current witness. For example,
`Operation --[emits]--> Event` is rejected while `Entity --[emits]--> Event` is allowed. A new edge can claim
this property only when the validator or owner gate would make a different allow/reject decision.

Use carefully: a human preference is not a reject/allow decision unless it is tied to a named gate, validator,
fixture, or owner review outcome.

Misuse warning: do not count "clearer wording" as a reject/allow change.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a relationship claims a
reject/allow property with no validator, fixture, or owner-gate decision that changes" -> challenges the term;
owner route = definitions-governance; gate = owner decision; blocking question = "which decision flips when
this relationship is removed?"; residue -> `definitions/reviews/`.

Confirm contract: active when a relationship proposal cites the changed validator/fixture/owner-gate result.
Gate = definitions-governance owner gate.

Promotion boundary: local method vocabulary; one property for D18, not a standalone relationship authority.

## domainspec-v2-D21. derivation consequence

Source kind: method-vocabulary; local-inference

Evidence: [domainspec-v2-D18](#domainspec-v2-d18) · [domainspec-v2-D2](#domainspec-v2-d2) ·
[impl/spec/TEST-PIPELINE.md](../impl/spec/TEST-PIPELINE.md)

Formal voice:

```text
derivation consequence =
  a change in which build-time obligations, tests, generated checks, or validation duties
  are derived from a spec because the relationship exists.
```

Plain-language voice: the edge matters if it causes different checks or obligations to be produced.

Domain-context voice: DomainSpec keeps the public derivation contract separate from private engine
delta-rules. A relationship may pass this property when it changes the public obligation set, but it must not
require importing private derivation logic into DS-D8.

Use carefully: derivation consequence is about the public contract and observable obligations, not private
engine internals.

Misuse warning: do not claim derivation consequence merely because implementation code happens to read the
edge; the derived obligation must be named.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a relationship claims a
derivation property but no derived obligation changes" -> challenges the term; owner route =
definitions-governance; gate = owner decision; blocking question = "which obligation, test, or check changes
if this relationship is removed?"; residue -> `definitions/reviews/`.

Confirm contract: active when a relationship proposal cites the changed public obligation or test surface.
Gate = definitions-governance owner gate.

Promotion boundary: local method vocabulary; does not expose private derivation delta-rules.

## domainspec-v2-D22. projection consequence

Source kind: method-vocabulary; local-inference

Evidence: [domainspec-v2-D18](#domainspec-v2-d18) ·
[relationships.md](./relationships/relationships.md) ·
[minted-project graph schema](../impl/spec/minted-project/graph.schema.json)

Formal voice:

```text
projection consequence =
  a change in a non-authoritative view, read model, markdown companion,
  implementation-facing projection, or navigation surface that is generated from
  or constrained by canonical relationship authority.
```

Plain-language voice: the edge matters if it changes a view people or tools rely on, while the root authority
still remains elsewhere.

Domain-context voice: minted-project graph views and display notation are projections. `owned-by` is also a
projection consequence of `owns`, but because it is generated reverse navigation it is not an authored
canonical edge.

Use carefully: projection consequence can justify a generated view, but not automatically a first-class
authored relationship.

Misuse warning: do not treat a projection as the source of truth.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a relationship claims a
projection property but no governed view/read model changes" -> challenges the term; owner route =
definitions-governance; gate = owner decision; blocking question = "which projection changes, and is it
authoritative or generated?"; residue -> `definitions/reviews/`.

Confirm contract: active when a relationship proposal cites the changed projection and its authority boundary.
Gate = definitions-governance owner gate.

Promotion boundary: local method vocabulary; projections remain subordinate to root relationship authority.

## domainspec-v2-D23. composition path consequence

Source kind: method-vocabulary; local-inference; build-from-owned

Evidence: [domainspec-v2-D3](#domainspec-v2-d3) · [domainspec-v2-D18](#domainspec-v2-d18) ·
[relationships.yml](./relationships/relationships.yml)

Formal voice:

```text
composition path consequence =
  a change in how typed concepts compose across relationship authority:
    allowed source/target path,
    relationship chain,
    feature-boundary crossing,
    ordered operation path,
    or code-pattern connection.
```

Plain-language voice: the edge matters if it creates a different path through the typed graph or a different
way code/spec pieces connect.

Domain-context voice: this is the closest D18 property to the original CAV2 non-collapse idea in D3:
an edge earns its own type when it composes differently. `enforces-cross` failed because scope metadata kept
the same composition path; `owns` and `belongs-to` survive because they support different Entity-to-Entity
paths.

Use carefully: composition path consequence is not full category-law composition. It is finite DS-D8 path
behavior inside the typed composable graph fragment.

Misuse warning: do not claim this property from visual graph layout alone.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a relationship claims a
composition path property but collapses into the same typed path as an existing edge plus metadata" ->
challenges the term; owner route = definitions-governance; gate = owner decision; blocking question = "which
typed composition path changes?"; residue -> `definitions/reviews/`.

Confirm contract: active when a relationship proposal cites the changed typed path or code-pattern connection.
Gate = definitions-governance owner gate.

Promotion boundary: local method vocabulary; finite DS-D8 composition only, not full category law.

## domainspec-v2-D24. owner route consequence

Source kind: method-vocabulary; local-inference

Evidence: [domainspec-v2-D18](#domainspec-v2-d18) ·
[authority/AUTHORITY-MODEL.md](../authority/AUTHORITY-MODEL.md) ·
[relationships.yml](./relationships/relationships.yml)

Formal voice:

```text
owner route consequence =
  a change in which governance owner, approval path, review gate, or remediation
  route is responsible because the relationship exists.
```

Plain-language voice: the edge matters if it sends the problem to a different owner.

Domain-context voice: DS-D1 formation, DS-D2 labels, DS-D8 signatures, validators, and implementation
projections have different owners. A new relationship can claim this property only when removal changes the
owner route, not merely because someone wants review.

Use carefully: owner route consequence is about authority routing, not who happened to edit the file.

Misuse warning: do not use this property to bypass the root definitions owner.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a relationship claims an
owner-route property but the same owner and gate would handle the case without it" -> challenges the term;
owner route = definitions-governance; gate = owner decision; blocking question = "which owner route changes?";
residue -> `definitions/reviews/`.

Confirm contract: active when a relationship proposal cites the changed owner/gate/remediation route. Gate =
definitions-governance owner gate.

Promotion boundary: local method vocabulary; does not transfer authority between owners.

## domainspec-v2-D25. generated artifact consequence

Source kind: method-vocabulary; local-inference

Evidence: [domainspec-v2-D18](#domainspec-v2-d18) ·
[relationships.yml](./relationships/relationships.yml) · [domainspec-v2-D11](#domainspec-v2-d11)

Formal voice:

```text
generated artifact consequence =
  a change in a generated file, generated view, generated instance, fixture,
  test artifact, or machine-readable output caused by the relationship's presence.
```

Plain-language voice: the edge matters if generation produces something different.

Domain-context voice: generated reverse navigation such as `owned-by`, generated instances, fixtures, and
test artifacts can all witness this property. The property may justify generation without promoting the
generated thing as an authored canonical relationship.

Use carefully: generated artifact consequence must name the generated artifact and the source authority it is
derived from.

Misuse warning: do not treat generated output as canonical source just because it changed.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a relationship claims a
generated artifact property but no generated artifact changes or provenance is named" -> challenges the term;
owner route = definitions-governance; gate = owner decision; blocking question = "which generated artifact
changes, and what source produced it?"; residue -> `definitions/reviews/`.

Confirm contract: active when a relationship proposal cites the changed generated artifact and its provenance.
Gate = definitions-governance owner gate.

Promotion boundary: local method vocabulary; generation evidence is not canonical promotion.

## domainspec-v2-D19. typed composable graph fragment

Source kind: method-vocabulary; local-inference

Evidence: [relationships.yml](./relationships/relationships.yml) ·
[relationships.md](./relationships/relationships.md) · [domainspec-v2-D4](#domainspec-v2-d4) ·
[DS-D8](#ds-d8)

Formal voice:

```text
typed composable graph fragment =
  a finite directed graph surface where:
    nodes are typed by DS-D1 meta-types,
    edges are typed by active DS-D2 relationship verbs,
    endpoint admissibility is checked by DS-D8 signatures,
    composition is limited to declared finite obligations in root relationship authority.

fragment boundary =
  this does not claim full category law:
    no general identity,
    no general closure under composition,
    no associativity proof,
    no path-equation proof,
    no functorial preservation proof,
  unless a later owner route turns those into finite validator obligations.
```

Plain-language voice: DomainSpec has a typed graph that can compose enough to validate and generate useful
structure, but it is not yet claiming the full mathematical package of category laws.

Domain-context voice: R3A relationship authority uses this phrase for the current DS-D8 state: 31 active
relationship signatures with typed endpoints, generated/deferred/deprecated edge policies, and validators
that reject noncanonical or unconstructible edges. Category laws remain a separate future formalization route.

Use carefully: use this phrase when describing the current deployed relationship model. Use "category" only
for the broader future formalization once identity, closure, associativity, path laws, and preservation checks
are finite validator obligations.

Misuse warning: do not infer full category-theory authority from the word "composable"; current composition
is finite and signature-bound, not general.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a relationship path is
claimed category-law valid without finite identity/composition/closure/associativity/path obligations" ->
challenges the term; owner route = definitions-governance; gate = owner decision; blocking question = "is
this claim inside the finite DS-D8 fragment or does it require full category laws?"; residue ->
`definitions/reviews/`.

Confirm contract: active with R3A DS-D8 root relationship authority; promote to fuller category-law language
only through a separate owner route with finite validator obligations. Gate = definitions-governance owner gate.

Promotion boundary: local DomainSpec v2 method vocabulary; names the current deployed graph authority without
promoting full category law.

## DS-D1 — Meta-Type System

The **DomainSpec domain-vocabulary** scheme (`DS-D*`) — the node/edge alphabet — is maintained **separately**
from this file's governance/method scheme (`domainspec-v2-D*`), and linked here:

- **meta-type** = one of the 24 staged DomainSpec node labels; maturity determines whether it may be used as active authority.
- Human cards (per type, 3-voice): [meta-types/meta-types.md](./meta-types/meta-types.md)
- Machine view (registry): [meta-types/meta-types.yml](./meta-types/meta-types.yml)
- Criterion (per type, machine-checkable): `impl/spec/meta-types/<category>/<type>.schema.yml`

Status: `DS-D1.1..9` plus `DS-D1.11..14` are 13 active backend types; `DS-D1.10 Saga` is superseded and its
ID is not reused; `DS-D1.15..23` are nine UI candidates; `DS-D1.24 Adapter` is a deferred merge-candidate and
`DS-D1.25 State Indicator` is a deferred split-candidate. Relationship verbs (`DS-D2`) and
relationship signatures (`DS-D8`) are active from R3A root authority.

## DS-D2 — Relationship Verb Set

Source kind: domain-vocabulary; active (R3A)

Evidence: [relationships.yml](./relationships/relationships.yml) (machine authority) ·
[relationships.md](./relationships/relationships.md) (human companion) ·
[relationship-signatures.ts](../impl/tools/lib/relationship-signatures.ts) (implementation consumer)

Formal voice:

```text
DS-D2 relationship verb =
  a canonical authored relationship label admitted by the active
  signatures in definitions/relationships/relationships.yml.

canonical authored verb =
  present in at least one active relationship signature
  AND not listed only as generated_view, deprecated, or deferred.
```

Plain-language voice: DS-D2 is the approved vocabulary for arrows in a DomainSpec graph: names like
`enforces`, `reads`, `owns`, and `orchestrates`. If a label is only generated (`owned-by`), deprecated
(`enforces-cross`, `queries`), or deferred (`depends-on`), authors do not use it as a canonical edge.

Domain-context voice: feature specs use DS-D2 labels in Concept Graph tables. The validator reads the root
relationship authority, not the implementation projection, and rejects noncanonical labels before any endpoint
meaning is considered.

Use carefully: DS-D2 names the relationship label. DS-D8 types that label's allowed endpoints.

Misuse warning: do not treat a display notation such as `Operation --[emits]--> Event` as authoritative if it
is not backed by an active root signature. `owned-by` is a generated view for navigation, not an authored
relationship.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a relationship label is
authored as canonical while root authority lists it only as generated, deprecated, or deferred" -> challenges
DS-D2; owner route = definitions-governance; gate = owner decision; blocking question = "is this label backed
by an active root signature?"; residue -> `definitions/reviews/`.

Confirm contract: active after owner-approved R3A root authority, `validate:rels` endpoint validation, and no
open contradiction. Gate = definitions-governance owner gate.

Promotion boundary: local DomainSpec v2 domain vocabulary; source of truth is root `definitions/relationships/`.

## DS-D8 — Relationship Signature Authority

Source kind: domain-vocabulary; active (R3A)

Evidence: [relationships.yml](./relationships/relationships.yml) (machine authority) ·
[relationships.md](./relationships/relationships.md) (human companion) ·
[validate-relationships.ts](../impl/tools/validate-relationships.ts) (endpoint validator) ·
[relationship-signatures.ts](../impl/tools/lib/relationship-signatures.ts) (shared loader/checker)

Formal voice:

```text
DS-D8 relationship signature =
  an active tuple in definitions/relationships/relationships.yml:
    (verb, source_type(s), target_type(s), scope, multiplicity, lifecycle status,
     optional generated relationship projection).

edge admissibility check =
  a declared edge a --[verb]--> b is constructible iff:
    verb resolves to an active DS-D2 label
    AND type(a) is in the signature source set
    AND type(b) is in the signature target set.
    AND the edge's same-feature or cross-feature location is admitted by scope
    AND the declared multiplicity bounds hold.
```

Plain-language voice: DS-D8 is the typed contract behind every allowed relationship. It says not only that
`enforces` is a valid word, but that only a Rule may enforce an Operation.

Domain-context voice: R3A currently defines 31 active signatures. `creates` is the same-feature,
partial-one-to-one `Operation -> Entity` signature. The edge is canonical; `creation_targets` is generated
from its outgoing target rather than authored independently.
The legacy `ui` and `ui-backend` scope tokens are same-feature graph lanes; only
an explicit `cross-feature` token admits a Cross-Feature Dependency.
`enforces` admits both same-feature and cross-feature placement while retaining one
Rule-to-Operation semantic verb; `enforces-cross` remains a rejected deprecated alias.
`orchestrates` has one Workflow signature
covering same-feature and cross-feature scope; `owned-by` is generated navigation; `depends-on`, Operation-returned Value Object, and the
Event payload/publisher split stay deferred until new evidence proves distinct behavior.

Use carefully: DS-D8 is endpoint authority, not a full category-law proof system. Category laws remain a
separate future formalization route. Current wording is
`typed composable graph fragment` (`domainspec-v2-D19`), and new or disputed relationships must pass the
relationship non-collapse test (`domainspec-v2-D18`).

Misuse warning: do not count generated/deprecated/deferred entries as active signatures, and do not use schema
`edge_participation` slices as independent authority; they are evidence checked against DS-D8.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a declared relationship
passes while its endpoint meta-types do not match any active root signature" -> challenges DS-D8; owner route =
definitions-governance; gate = owner decision; blocking question = "which active signature permits this
source/target pair?"; residue -> `definitions/reviews/`.

Confirm contract: active after owner-approved R3A root authority, schema participation consistency, endpoint,
multiplicity, and projection-authorship fixtures, `validate:rels`, `validate:content`, and no open contradiction.
Gate = definitions-governance owner gate.

Promotion boundary: local DomainSpec v2 domain vocabulary; implementation surfaces may project DS-D8 but must
not redefine it.

## domainspec-v2-D26. relationship source-effect binding

Status: superseded by [`domainspec-v2-D27`](#domainspec-v2-d27); stable ID retained for history.

Source kind: method-vocabulary; historical local-inference

Evidence: [DEC-DSV2-OPERATION-CREATES-ENTITY](../authority/decisions/2026-07-22-operation-creates-entity.md) ·
[DEC-DSV2-CANONICAL-CREATION-RESPONSIBILITY](../authority/decisions/2026-07-22-canonical-creation-responsibility.md)

Formal voice (historical, non-authoritative): the former `creates` contract required independently authored
`creation_targets` and `creates` edges to satisfy a biconditional. That contract is no longer active.

Plain-language voice: DomainSpec used to require authors to state the same creation fact twice and then check
that the two statements agreed.

Domain-context voice: the edge is now the sole authored creation fact. Generated views may still expose
`creation_targets`, but source specifications and minted node sources may not author it.

Supersession reason: equality checking made duplication consistent but did not make the two representations
orthogonal. D27 replaces that dual-authoring contract with canonical responsibility and generated projection.

## domainspec-v2-D27. Canonical Single Responsibility Principle

Status: active

Source kind: method-vocabulary; local-inference (build-from-owned: software-engineering Single Responsibility
Principle, CAV2-D16 typed coupling, CAV2-D22 orthogonal classification, and CAV2-D29 axis orthogonality)

Evidence: [DS-D8](#ds-d8) · [domainspec-v2-D18](#domainspec-v2-d18) ·
[DEC-DSV2-CANONICAL-CREATION-RESPONSIBILITY](../authority/decisions/2026-07-22-canonical-creation-responsibility.md) ·
[relationships.yml](./relationships/relationships.yml)

Formal voice:

```text
Let B be one authority boundary.
Let C_B be its canonical model elements and R_B its admitted semantic responsibilities.
Let owns_B(c, r) mean that element c canonically owns responsibility r.
Let authored_B(p) be the canonical authored representations of proposition p.

Canonical Single Responsibility(B) iff:
  for every c in C_B: c has exactly one primary semantic responsibility;
  for every r in R_B: exactly one c in C_B owns r;
  for every canonical proposition p: |authored_B(p)| = 1;
  every equivalent non-canonical representation of p is a generated projection
  with provenance back to authored_B(p).

creates is a partial injection from Operation concepts to Entity concepts:
  creates subset_of Operation x Entity
  for every Operation O: |{E | creates(O, E)}| <= 1
  for every Entity E:    |{O | creates(O, E)}| <= 1

creation_targets(O) = sorted({E | creates(O, E)})  [generated, never authored]
```

`B` is the authority boundary in which ownership is evaluated. A *primary semantic responsibility* is the
element's governing reason to exist in the model, not every consequence it participates in. A *canonical
proposition* is one semantic fact admitted as authority. The `creates` inequalities define partial
one-to-one participation (`0..1` on both sides), not a total bijection.

Plain-language voice: one element owns one primary responsibility; one responsibility has one canonical
owner; one fact is authored once. Other useful representations are generated from that fact.

Domain-context voice: an Operation may still emit an Event, be enforced by a Rule, query an Entity, and
participate in a Workflow while owning one cohesive operational responsibility. A Workflow owns coordination,
not the business responsibilities of the Operations it orchestrates. Legitimate independently meaningful
relationships such as `enforces` may remain many-to-many; cardinality is constrained only when responsibility
ownership requires it.

Conformance scope: D27 is active as a model-admission principle. The current machine-executable application is
`creates`; DomainSpec does not yet claim that every existing concept and relationship has a machine-readable
responsibility owner. Each additional application needs its own finite owner, authorship, consequence, and
validation evidence before claiming conformance.

### Application: canonical creation responsibility

Canonical example:

```text
CreatePlayer --[creates]--> Player
```

The edge is the sole authored creation proposition. Generated views may show:

```text
CreatePlayer.creation_targets = [Player]
```

Other concepts may relate to the same Entity without competing for its creation responsibility:

```text
FindPlayer   --[reads]--> Player
UpdatePlayer --[reads]--> Player
Team         --[owns]-----> Player
```

The following graphs are rejected:

```text
CreatePlayer   --[creates]--> Player
RegisterPlayer --[creates]--> Player   # two canonical owners for one creation responsibility
```

```text
CreatePlayer --[creates]--> Player
CreatePlayer --[creates]--> Team       # one Operation mixes two creation responsibilities
```

Runtime multiplicity remains separate:

```text
one CreatePlayer Operation concept
  -> many executions
  -> many distinct Player runtime instances
```

Use carefully: classical software-engineering SRP supplies the cohesion intuition, but it does not by itself
prove graph cardinality or single authorship. Those additional constraints are the DomainSpec specialization
recorded here and must be backed by explicit authority and validators.

Misuse warning: do not count fields, methods, edges, or statements and call the result a responsibility count.
Do not collapse orchestration, enforcement, querying, event production, and creation merely because they
interact. The test is semantic ownership and independent operational consequence.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "two canonical elements
own the same semantic responsibility, one element owns unrelated primary responsibilities, or one proposition
is authored in equivalent forms" -> challenges D27; owner route = definitions-governance; gate = owner
decision; blocking question = "what is the one canonical owner and authored representation of this semantic
responsibility?"; residue -> `definitions/reviews/`.

Confirm contract: active for `creates` after owner selection of edge-canonical authorship, rejection of plural
source and target degree, generated `creation_targets`, synchronized DS-D8 authority, and passing positive and
negative Markdown/compiler fixtures. Gate = definitions-governance owner gate.

Promotion boundary: DomainSpec-local modeling and validation principle. It builds from CAV2 invariants without
creating a new CyberAlchemy v2 primitive or claiming that every independently meaningful relationship must be
one-to-one.

## domainspec-v2-D29. Ownership Dimension Registry

Status: active

Source kind: domain-vocabulary; owner-selected D06 projection dependency

Evidence: [DS-D8](#ds-d8) · [domainspec-v2-D27](#domainspec-v2-d27) ·
[ownership-dimensions.json](./ownership-dimensions/ownership-dimensions.json) ·
[BMC-REL-D06 P01 decision](../development/relationship-constraint-decisions/BMC-REL-001/sidecars/BMC-REL-D06-PROJECTION/decisions/BMC-REL-D06-PROJECTION-DECISIONS.md#p01--ownership-dimension-vocabulary)

Formal voice:

```text
Let OwnershipDimensionId be the exact finite active_ids set in
definitions/ownership-dimensions/ownership-dimensions.json.

Initially:
  OwnershipDimensionId = {
    lifecycle,
    custody,
    write-responsibility
  }.

An ownership-dimension reference is admitted iff it is one exact active stable
ID in that registry. The active IDs are pairwise non-overlapping semantic axes.
If a proposed classification is unknown, free-text, aliased, or ambiguous across
more than one active axis, validation fails closed rather than inferring an ID.

For every admitted dimension d, target Entity t, and owner Entities o1 and o2:
  owns_d(o1, t) and owns_d(o2, t) implies o1 = o2.

No existence condition follows: an Entity need not have an owner in any
dimension. Adding, revising, deprecating, or removing a registry entry requires
a fresh Definitions Governance owner decision and a new exact registry digest.
```

The registry order is serialization only and carries no precedence. It contains stable IDs only; this
definition card owns their meanings.

Plain-language voice: DomainSpec recognizes three current kinds of direct Entity ownership. Lifecycle,
custody, and write responsibility are separate questions, so different Entities may own different kinds for
the same target. Within one kind, two competing direct owners are not admitted. Unknown or ambiguous kinds are
rejected instead of guessed, and the registry cannot grow through ordinary authoring.

Domain-context voice: the canonical `owns` relationship remains one `Entity -> Entity` verb and `owned-by`
remains generated reverse navigation. A later typed representation may bind an `owns` fact to one registry ID,
but this card does not choose that representation. The compatibility token `one_to_many`, endpoint types,
feature scope, runtime writers, Operations, permissions, and calls do not supply a dimension.

### Active ownership dimensions

#### `lifecycle`

Formal voice: responsibility for the target Entity's admission as an identity-bearing domain concept,
continuity rules, lifecycle-transition policy, and retirement. It does not by itself grant custody or authority
for every business-state write.

Plain-language voice: the lifecycle owner decides when the Entity exists as a governed identity and how its
lifecycle may begin, continue, and end.

Domain-context voice: on `Entity --[owns]--> Entity`, `lifecycle` classifies responsibility for the target's
identity-bearing lifecycle without changing the canonical verb or generated inverse.

#### `custody`

Formal voice: responsibility for stewardship, possession, placement, or operational keeping of the target
Entity without necessarily controlling its lifecycle or all business-state mutation.

Plain-language voice: the custodian looks after or holds the Entity even when another owner governs its
lifecycle or writes its state.

Domain-context voice: on `Entity --[owns]--> Entity`, `custody` permits a distinct custodian without competing
with an owner on another admitted dimension.

#### `write-responsibility`

Formal voice: responsibility and authority for changing the target Entity's business state under its admitted
invariants. It does not by itself determine lifecycle admission, retirement, or custody.

Plain-language voice: the write-responsibility owner is accountable for authorized changes to the Entity's
business state.

Domain-context voice: on `Entity --[owns]--> Entity`, `write-responsibility` classifies direct semantic
responsibility for Entity-state mutation; runtime writers, Operations, permissions, and calls do not become
canonical `owns` edges merely by performing or permitting a write.

Validation implications: require one exact active ID for any dimension-bearing ownership fact; reject unknown,
free-text, duplicate, aliased, deprecated, or ambiguously overlapping IDs; reject two distinct direct owners for
the same target and dimension; permit distinct owners for distinct dimensions; do not infer mandatory ownership,
numeric bounds, self-edge policy, cycle policy, transitivity, closure, inverse authorship, serialization, or
runtime cardinality. These implications remain non-executable until a separately selected typed representation
and validator bind this registry.

Use carefully: the registry admits semantic responsibility axes, not organizational titles, permissions,
runtime actors, storage locations, or arbitrary tags. A new word in prose is not a registry entry.

Misuse warning: do not silently map synonyms to an active ID, classify one fact under several IDs, or treat the
three initial entries as exhaustive forever. Evolution is possible only through a fresh owner decision.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "an ownership fact uses an
unknown, ambiguous, or multiply classified dimension, or two direct owners claim the same target and admitted
dimension" -> challenges the term; owner route = definitions-governance; gate = owner decision; blocking
question = "which exact active ownership-dimension ID and registry digest govern this fact?"; residue ->
`definitions/reviews/`.

Confirm contract: active from the exact D06 P01 owner selection and this synchronized three-voice card, index,
and machine-readable registry. Packet representation and executable validation require the separate P02 owner
decision. Gate = definitions-governance owner gate.

Promotion boundary: local DomainSpec v2 ownership-dimension vocabulary only. It does not change DS-D8 endpoint
authority, the `owns` signature, generated `owned-by`, D27 beyond the selected D06 application, implementation,
publication, release, deployment, or production state.

## domainspec-v2-D30. Membership Kind Registry

Status: active

Source kind: domain-vocabulary; D07 P01 contents owner-selected registry

Evidence: [DS-D8 canonical `belongs-to`](#ds-d8--relationship-signature-authority) ·
[D18 relationship contracts](#domainspec-v2-d18-relationship-non-collapse-test) ·
[`BMC-REL-D07-P01-CONTENTS-A-MINIMAL-TWO-KIND` selection](../development/relationship-constraint-decisions/BMC-REL-001/sidecars/BMC-REL-D07-PROJECTION/receipts/BMC-REL-D07-P01-CONTENTS-SELECTION-RECEIPT.json) ·
[`membership-kinds.json`](./membership-kinds/membership-kinds.json)

Formal voice:

Let `K_active` be the exact finite set of active IDs in the digest-bound
`definitions/membership-kinds/membership-kinds.json`. Initially:

```text
K_active = { classification, home-assignment }.
```

A future kind-bearing canonical `belongs-to` fact is admitted only when it references one exact active ID. A
fact whose intended meaning fits zero active meanings is unknown; a fact that fits more than one is ambiguous.
Both fail closed. Free text, aliases, implicit synonym mapping, deprecated IDs, duplicate IDs, and multi-kind
classification of one fact are invalid. The active meanings are pairwise non-overlapping:

- `classification` answers “what classifier or category is applied to the source?”
- `home-assignment` answers “what explicit home or placement context is assigned to the source?”

For each Entity `e`, kind `k` in `K_active`, and parent Entities `p1`, `p2`:

```text
belongs_to_k(e, p1) and belongs_to_k(e, p2) implies p1 = p2.
```

There is no existence condition. Different parents under distinct active kinds are permitted but not required.
The generic prose word `membership` and the unselected `collection-membership` design label are not active IDs.

Plain-language voice: a `belongs-to` fact may say either what category the source is classified under or which
explicit home it is assigned to. The author must choose one exact active meaning, and the fact is rejected if
neither or both meanings fit. Nothing is required to belong anywhere, and different meanings may point to
different parents.

DomainSpec-context voice: this registry refines the canonical Entity-to-Entity `belongs-to` vocabulary without
changing its endpoints or turning compatibility label `many_to_one` into numeric authority. It remains
independent from canonical `owns` and the D29 ownership-dimension registry. It does not decide packet
representation or executable validation.

### `classification`

Formal voice: `classification(e, p)` means the parent Entity `p` functions as the conceptual classifier or
category under which source Entity `e` is classified. It asserts neither membership in `p` as a collection nor
assignment of `p` as `e`'s governing home or placement.

Plain-language voice: `e` is treated as an example or member of the kind represented by `p`; this says what
category `e` is classified under, not where it is housed or which collection it joins.

DomainSpec-context voice: on canonical `Entity --[belongs-to]--> Entity`, `classification` may classify a source
under a target Entity without changing endpoint types or the canonical verb. `Copy --[belongs-to]--> Title` is a
hypothetical explanatory fit only when Title actually classifies Copy; the existing example alone does not
prove the kind binding.

### `home-assignment`

Formal voice: `home-assignment(e, p)` means parent Entity `p` is the explicitly designated organizational,
operational, or placement context to which source Entity `e` is assigned as its home for the modeled purpose.
It asserts neither that `p` classifies `e` nor that `e` merely participates in `p` as a collection.

Plain-language voice: `p` is the place or governing context where `e` belongs for this assignment, rather than
a category describing `e` or a group that simply includes it.

DomainSpec-context voice: on canonical `belongs-to`, `home-assignment` may express an Entity's assigned home
while remaining distinct from `owns`. `Copy --[belongs-to]--> Branch` is a hypothetical explanatory fit only
when Branch is the modeled home; the existing example alone does not prove the kind binding.

Validation implications: bind every registry-bearing check to the exact registry digest; require one exact
active ID for each future kind-bearing fact; reject unknown, free-text, aliased, deprecated, duplicated,
multi-classified, or ambiguously overlapping IDs; reject two distinct direct parents for the same source Entity
and kind; permit different parents for distinct kinds without requiring any membership; reject ownership IDs
and any treatment of `belongs-to` as `owns^-1`. These implications remain non-executable until a separately
selected P02 representation and validator bind this registry.

Use carefully: a new prose term is not a registry entry. Owner-gated add, revise, deprecate, or remove operations
require a fresh Definitions Governance decision, synchronized card, index and registry bytes, a new digest, and
downstream drift review.

Misuse warning: do not map a generic “membership” catchall, `collection-membership`, `other`, aliases, ownership
dimensions, or ambiguous meanings to an active ID. Do not infer numeric bounds, self-edge policy, cycle policy,
transitivity, closure, duplicate-edge policy, inverse authorship, serialization, runtime behavior, or mandatory
membership.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a `belongs-to` fact uses an
unknown, ambiguous, aliased, inactive, or multiply classified membership kind, or two distinct direct parents
claim the same source and active kind" -> challenges the term; owner route = definitions-governance; gate = owner
decision; blocking question = "which exact active membership-kind ID and registry digest govern this fact?";
residue -> `definitions/reviews/`.

Confirm contract: active only after exact owner acceptance and atomic synchronization of this three-voice card,
the D30 index row, and the machine-readable registry. P02 typed representation and executable validation require
a separate owner decision. Gate = definitions-governance owner gate.

Promotion boundary: local DomainSpec v2 membership-kind vocabulary only. It does not change DS-D8 endpoint
authority, the canonical `belongs-to` signature, `owns`, D29, packet/schema/validator authority, implementation,
publication, release, deployment, or production state.

## domainspec-v2-D28. DomainSpec obligation lifecycle

Status: active

Source kind: local-inference; owner-ratified lifecycle vocabulary

Evidence: [GATE-05 separate owner-local lifecycles](../../../research/2026-08-20-domainspec-v2-cav2-proof-obligation-substrate/development/refinement-runs/20260821T145409Z-proof-substrate-next-steps/stages/10-gate-01-top03-refresh/apply-corrected/owner-decisions/GATE-05-DECISION.md) ·
[TOP-03 DomainSpec v2 adoption acceptance](../authority/decisions/2026-08-22-top03-shared-syntax-adoption-acceptance.md)

Formal voice:

```text
Let o = (owner_namespace, obligation_id, version, digest) identify one exact
DomainSpec obligation version.

LifecycleState = {open, discharged, killed}
LifecycleEvent = {opened, discharged, reopened, killed}

state_o([]) = undefined

fold(undefined, opened)      = open
fold(open, discharged)       = discharged
fold(discharged, reopened)   = open
fold(open, killed)           = killed

Every other event/state pair is invalid.

current_state(o) = fold(events_o ordered by their owner-admitted sequence)

Only the DomainSpec lifecycle owner may admit a LifecycleEvent for o.
Evidence, validation, generation, projection, evaluation, or CAV2 promotion
may inform that owner decision but cannot append the event themselves.
```

The event and state tokens are closed members of this one lifecycle definition; they are not independent
definition cards. `killed` is terminal for the exact obligation version `o`. A materially changed proposition
requires an owner-governed new identity or version and a new `opened` event rather than another transition on
the killed version.

Plain-language voice: an obligation begins open. Its owner may accept enough evidence and discharge it, reopen
it when more work is needed, or kill it when that exact obligation no longer applies. Tests and proofs provide
evidence; they never press those lifecycle buttons themselves.

Domain-context voice: DomainSpec v2 proof and validation surfaces may record Lean, Cedar, Datalog, evaluator,
mutation, or runtime results against an exact obligation. A generated catalogue or human page derives the
current lifecycle state from the append-only owner events and displays the owning decision. It may not emit a
transition or turn a passing result into a discharge.

Currentness is a separate axis. When a source, predicate, binding, runtime, policy, or other exact input changes,
an earlier discharge remains a valid historical owner event but becomes non-current for the changed binding.
That change does not rewrite the earlier event and does not automatically emit `reopened`.

Decision dispositions are also separate. `refuse` and `defer` record what the owner decided about the current
request; neither changes the prior lifecycle state. `resolved` may appear in ordinary explanation, but it is not
a machine lifecycle state because it would collapse `discharged` and `killed`.

Use carefully: always qualify the state with the exact obligation identity and version. The word `killed` in
mutation testing means that a negative variant was detected; it is not the `killed` lifecycle state of an
obligation.

Misuse warning: do not infer a transition from a schema pass, proof checker, Lean theorem, Cedar or Datalog
result, mutation kill, evaluator receipt, generated page, publication, or CAV2 promotion. Do not reopen an
obligation merely because one of its bindings became non-current.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a non-owner surface
performs a transition, an invalid event/state pair is accepted, currentness is collapsed into lifecycle, or a
mutation kill is treated as an obligation kill" -> challenges the term; owner route = definitions-governance
plus the DomainSpec lifecycle owner; gate = owner decision; blocking question = "which exact owner-admitted
event over which exact obligation version produced this state?"; residue -> `definitions/reviews/`.

Confirm contract: active from the accepted GATE-05 owner decision and this synchronized three-voice card. A
future schema, reducer, validator, catalogue, or generated page may claim conformance only after positive and
negative fixtures enforce the closed transitions, owner-only event admission, append-only history, separate
currentness, and non-transitioning `refuse`/`defer` dispositions. Gate = definitions-governance owner gate.

Promotion boundary: local DomainSpec v2 obligation semantics and lifecycle only. It does not define or change
CAV2 promotion, domain adoption, proof truth, publication authorization, or another domain's lifecycle.

## domainspec-v2-D31. Meta-Type Realization

Status: active

Source kind: method-vocabulary; owner-admitted implementation binding

Evidence: [current implementation state](./meta-types/current-implementation.md) ·
[machine-readable state](./meta-types/current-implementation.json) ·
[immutable baseline manifest](../development/meta-type-instantiation-cli/CANONICAL-IMPLEMENTED-BASELINE.v6.json)

Formal voice:

```text
Realization = (
  meta_type_id,
  language,
  source_ref + source_sha256,
  provider_ref + provider_sha256,
  binding_ref + binding_sha256
)

A realization is current iff that exact tuple occurs once in the current
canonical implemented meta-type baseline. Its identity is byte-bound; path or
label equality without digest equality is insufficient.
```

Plain-language voice: a realization is the exact selected implementation recipe for one DomainSpec meta-type
in one language. It names the implementation, its provider, and the binding that joins them, including their
digests.

Domain-context voice: the current baseline contains one TypeScript, one Python, and one Rust realization for
each of the 13 active backend meta-types. A realization is neither the semantic meta-type itself nor a domain
instance created from it.

Use carefully: qualify every realization by baseline ID and digest. A later byte-compatible-looking file is
not the same realization unless its exact binding is admitted in a new baseline.

Misuse warning: do not infer realization admission from an old form queue, provider/profile gate, example
candidate, filename, or passing test that is outside the current baseline manifest.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a claimed realization is
missing, duplicated, uses an unknown language, or disagrees with a selected source/provider/binding digest" ->
challenges the term; owner route = implementation-conformance profile owner plus definitions-governance; gate
= exact baseline comparison; blocking question = "which exact baseline row and digests identify this
realization?"; residue -> `definitions/reviews/`.

Confirm contract: active from the owner-admitted current implementation state, the immutable baseline, and
schema/validator PASS over all 39 rows. Gate = definitions-governance owner gate.

Promotion boundary: project-local realization identity only. It grants no generated-target conformance,
publication, release, deployment, or production authority.

## domainspec-v2-D32. Canonical Implemented Meta-Type Baseline

Status: active

Source kind: project-local implementation authority

Evidence: [current implementation state](./meta-types/current-implementation.md) ·
[owner definitions-first decision](../development/meta-type-instantiation-cli/OWNER-CANONICAL-DOCS-AND-BASELINE-V2-DECISION.json) ·
[baseline validator](../development/meta-type-instantiation-cli/validate-baseline.mjs)

Formal voice:

```text
Baseline = (
  baseline_id,
  baseline_digest,
  owner_decision_ref + sha256,
  exact_inventory,
  backend_meta_type_set,
  realization_rows,
  UI_supporting_state,
  relationship_authority_denominator
)

The baseline is immutable. Changing any frozen byte requires a new baseline ID,
inventory, digest, owner binding, and validation result. The current baseline is
resolved through definitions/meta-types/current-implementation.json.
```

Plain-language voice: this is the sealed, versioned snapshot of the implementations DomainSpec has selected
as its starting point. It answers “what exactly do we mean by implemented today?” without relying on scattered
historical decisions.

Domain-context voice: the current baseline admits 13 backend meta-types and 39 realization rows across
TypeScript, Python, and Rust. It preserves the 11 UI states as supporting context, the 31-row DS-D8
relationship denominator, and the complete D36-D44 compensation definition epoch. Baselines `@1` through
`@5` are historical; the current state points to `@6`.

Use carefully: distinguish baseline admission from DS-D1 semantic maturity and from conformance of a generated
consumer project. These three axes can change independently.

Misuse warning: do not regenerate a frozen manifest in place, stretch an earlier digest over changed bytes, or
turn historical form/provider/profile gates into current baseline authority.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "the current pointer,
inventory, decision, denominators, realization rows, or digest disagree" -> challenges the term; owner route =
definitions-governance plus implementation-conformance profile owner; gate = new immutable baseline; blocking
question = "which exact manifest and owner decision define the claimed current baseline?"; residue ->
`definitions/reviews/`.

Confirm contract: active when the current-state schema and validator, baseline validator, ontology projection,
index, and drift audit agree on one exact baseline identity and digest. Gate = definitions-governance owner
gate.

Promotion boundary: project-local current implementation authority only. It does not prove that a target was
instantiated, conformant, published, released, deployed, or production-ready.

## domainspec-v2-D33. Meta-Type Instantiation

Status: active

Source kind: method-vocabulary; deterministic generation contract

Evidence: [WP-MTCLI-001](../development/meta-type-instantiation-cli/WORK-PACK.md) ·
[implementation plan](../development/meta-type-instantiation-cli/IMPLEMENTATION-PLAN.md) ·
[current implementation state](./meta-types/current-implementation.md)

Formal voice:

```text
instantiate(node, selected_realization, target_root) =
  validate typed input and exact baseline binding
  -> derive a deterministic contained artifact plan
  -> validate collisions, paths, and declared effects
  -> publish the complete plan atomically or publish nothing
  -> emit a baseline-bound receipt
  -> reread and observe the target outputs
```

Plain-language voice: instantiation turns a typed DomainSpec concept into the exact selected implementation in
another project, with predictable files and an auditable result.

Domain-context voice: the private CLI selects one D31 realization by meta-type and language, generates only
inside the declared target root, and binds its output receipt to the current D32 baseline. Its closed decoder,
planner, guarded atomic writer, receipt, reread observer, and clean-package replay are implemented and admitted
in baseline `domainspec-meta-types-current-implemented@3`.

Use carefully: generation must preserve DomainSpec meaning and the selected realization. It may format or
place code, but it may not invent a different architecture form.

Misuse warning: copying templates, creating some files, or obtaining a successful process exit is not
instantiation unless the input, selection, mutation, receipt, and reread contracts all hold.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "generation is
nondeterministic, escapes the target, mutates partially, or is not bound to one selected realization" ->
challenges the term; owner route = meta-type instantiation CLI owner; gate = executable positive and hostile
fixtures; blocking question = "what exact input and baseline row deterministically produced these outputs?";
residue -> `definitions/reviews/`.

Confirm contract: active and implemented for the private CLI after the decoder, planner, guarded atomic writer,
receipt, reread observers, hostile fixtures, and deterministic clean-package replay passed. Gate =
implementation-conformance profile owner.

Promotion boundary: generation contract only. It does not authorize publication, release, deployment,
production changes, or implicit successor execution.

## domainspec-v2-D34. Target Implementation Conformance

Status: active

Source kind: method-vocabulary; observed-versus-selected predicate

Evidence: [implementation-conformance ontology](../development/implementation-conformance/ontology-experiment/ontology.json) ·
[current implementation state](./meta-types/current-implementation.md) ·
[DS-D8 relationship authority](#ds-d8--relationship-signature-authority)

Formal voice:

```text
conforms(target, selection, baseline) = PASS iff
  selection occurs exactly once in baseline.realization_rows
  and target inventory equals the declared artifact plan
  and every selected structural, semantic, relationship, effect, continuation,
      and digest obligation is observed and satisfied.

Missing, unknown, unsupported, stale, or undeclared observations cannot become PASS.
```

Plain-language voice: conformance proves that the target project implements the exact version and language
form DomainSpec selected, not merely something with a similar name or shape.

Domain-context voice: for an Operation, observation includes declared read, write, and effect sets; guard
execution before mutation; atomic state-and-outbox behavior; explicit failure continuation; rejection of
undeclared reads, writes, or effects; and the typed Rule, Event, and Workflow relationships governed by DS-D8.

Use carefully: report unsupported observations as `not_evaluable` with their blockers. Conformance is always
bound to one target snapshot and one exact baseline.

Misuse warning: do not infer semantic or behavioral conformance from generated file presence, compilation,
unit-test PASS, one profile, or a historical candidate admission.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "an expected output or
obligation is absent, drifted, undeclared, unobservable, or matched against another baseline" -> challenges the
term; owner route = implementation-conformance profile owner; gate = fail-closed target observers; blocking
question = "which observations prove equality to the exact selected realization?"; residue ->
`definitions/reviews/`.

Confirm contract: active and implemented for the admitted static generated-target observation boundary after
the observer registry and positive/hostile fixtures passed across TypeScript, Python, and Rust artifacts. Runtime
behavior outside an admitted provider remains unsupported. Gate = implementation-conformance profile owner.

Promotion boundary: target-local evidence only. A conformance PASS does not grant publication, release,
deployment, production, or broader architecture acceptance authority.

## domainspec-v2-D35. Baseline-Bound Instantiation Receipt

Status: active

Source kind: evidence-vocabulary; deterministic generation receipt

Evidence: [WP-MTCLI-001](../development/meta-type-instantiation-cli/WORK-PACK.md) ·
[meta-type instantiation](#domainspec-v2-d33) · [target implementation conformance](#domainspec-v2-d34)

Formal voice:

```text
InstantiationReceipt = (
  baseline_id + baseline_digest,
  input_identity + input_digest,
  selected_realization_refs + digests,
  artifact_plan,
  output_paths + output_digests,
  mutation_outcome,
  reread_observations,
  conformance_outcome
)
```

Plain-language voice: the receipt is the generated implementation's tamper-evident birth certificate. It says
what was selected, what was written, what was observed afterward, and whether the result matched.

Domain-context voice: the current private `instantiate`, `lint`, and `receipt` CLI surfaces agree on this same
binding. The receipt schema and producer are implemented, target bytes are reread, and clean-package replay
checks deterministic package identity.

Use carefully: a receipt reports one completed attempt. It cannot repair missing observations or substitute a
new baseline for the one actually used.

Misuse warning: do not treat a plan, log, process exit, or receipt with unbound paths/digests as this receipt.
Do not let receipt production mask partial mutation or a failed reread.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "receipt identity,
selection, outputs, observations, or target bytes disagree" -> challenges the term; owner route = meta-type
instantiation CLI owner; gate = receipt schema plus hostile replay; blocking question = "can every claimed
output be recomputed from this exact input and baseline binding?"; residue -> `definitions/reviews/`.

Confirm contract: active and implemented after the receipt schema, producer, verifier, target reread, tamper
fixtures, and two-run clean-package replay passed. Gate = implementation-conformance profile owner.

Promotion boundary: evidence for one bounded instantiation only. It grants no publication, release,
deployment, production, or external-effect authority.

## domainspec-v2-D36. Workflow Compensation

Status: active

Source kind: method-vocabulary; owner-admitted forward-recovery model

Evidence: [durable compensation concept model](../development/durable-compensation-concepts/README.md) ·
[canonical runtime contract](../impl/architecture-conformance/targets/typescript/workflow-compensation-v1.md) ·
[reference implementation](../impl/architecture-conformance/targets/typescript/workflow-compensation-v1.ts) ·
[current implementation state](./meta-types/current-implementation.md)

Formal voice:

```text
WorkflowCompensation = (
  immutable D37 RecoveryIntent,
  frozen recovery plan,
  exact recovery Operations,
  external execution through D38..D44
)

workflow_evaluation_result in {not-required, recovery-required}

For one failed Workflow execution w:
  not-required => no RecoveryIntent exists
  recovery-required => exactly one RecoveryIntent exists
  targets(w) is a subset of the Operations orchestrated by that Workflow
  plan(w) is a topological ordering of targets(w)

Ordering precedence:
  explicit Operation dependency edges first;
  otherwise reverse completed-step order;
  reverse completed-step order is also the deterministic tie-breaker.

Workflow evaluation may emit intent and plan but never invokes recovery Operations.
Before the first invocation, the external executor resolves every planned Operation
to one exact binding or rejects the complete plan without mutation.
```

Semantic recovery state is owned by D37, durable coordination state by D38, individual execution outcomes by
D39, replay protection by D40, exclusive worker authority by D41 and D42, retry scheduling by D43, and the
whole recovery's final result by D44. Every recovery target remains an ordinary Operation and retains its
declared reads, writes, effects, guard-before-mutation ordering, atomic state-and-outbox boundary, Events, and
explicit failure continuation. Compensation adds no DS-D1 meta-type and no DS-D2/DS-D8 relationship verb.

Plain-language voice: Workflow Compensation is forward recovery after part of a Workflow completed. The
Workflow records what happened and requests a frozen recovery plan; durable machinery can safely resume that
same plan after retries, crashes, or worker replacement without silently choosing a different action.

Domain-context voice: DomainSpec binds forward and recovery steps through the existing
`Workflow --[orchestrates]--> Operation` relationship. The current three-profile reference implementation
realizes intent planning, exact-binding preflight, external invocation, and deterministic replay keys. Durable
dispatch, claiming, lease renewal, persisted retry scheduling, and restart recovery remain unimplemented and
are recorded separately from the admitted semantics.

Use carefully: a D39 failed or unknown attempt is not the D44 outcome of the whole recovery. Retry preserves
the D37 intent, frozen plan, exact Operation occurrence, durable progress, and D40 invocation identity.

Misuse warning: do not model compensation as a new meta-type, invent a `compensates` edge, execute recovery
inside Workflow evaluation, collapse Claim into Lease or Replay Identity, or infer durable implementation from
canonical semantics.

Challenge contract (CAV2-D40, protocol-only): modes = contradiction / scope; edge = "a Workflow invokes
recovery directly, a target is not one of its orchestrated Operations, binding preflight occurs after mutation,
retry changes semantic identity, or an attempt result is treated as terminal recovery state" -> challenges the
term; owner route = definitions-governance plus the implementation-conformance profile owner; gate = owner
decision plus positive and hostile profile fixtures; blocking question = "which exact intent, plan occurrence,
Operation binding, attempt, claim, lease, and replay identity realize this recovery?"; residue ->
`definitions/reviews/`.

Confirm contract: active by direct owner admission and synchronized D36-D44 definition and ontology
validation. Current implementation coverage remains separately bounded by
`definitions/meta-types/current-implementation.json`. Gate = definitions-governance owner gate.

Promotion boundary: project-local durable Workflow recovery semantics. It grants no claim that durable
dispatch is implemented and no publication, release, deployment, production, or external-effect authority.

## domainspec-v2-D37. Recovery Intent

Status: active

Source kind: method-vocabulary; owner-admitted durable-recovery identity

Evidence: [durable compensation concept model](../development/durable-compensation-concepts/README.md) ·
[Workflow Compensation](#domainspec-v2-d36)

Formal voice:

```text
RecoveryIntent = (
  intent_id,
  workflow_execution_id,
  failure_occurrence_id,
  failed_step_id,
  completed_step_journal_digest,
  plan_digest
)

semantic_status in {required, satisfied, unresolved}

required   iff execution or an authorized retry remains possible
satisfied  iff D44 disposition = completed
unresolved iff D44 disposition in {exhausted, escalated}
```

There is at most one intent for one immutable Workflow failure occurrence. Its identity and plan digest never
change after creation. `not-required` is a D36 evaluation result and means no intent exists.

Plain-language voice: the intent is the stable statement that one particular Workflow failure still needs one
particular recovery plan. It is the recovery's identity, not a queue message or a worker attempt.

Domain-context voice: DomainSpec derives the intent from the completed-step journal and the exact
`Workflow --[orchestrates]--> Operation` plan. Retries, claims, leases, workers, and restarts preserve it.

Use carefully: `required` may coexist with a failed or unknown D39 attempt while retry remains possible.

Misuse warning: do not create a new intent for retry or infer semantic completion from worker or lease state.

Challenge contract: a mutable plan digest, duplicate intent for one failure occurrence, or attempt state used
as semantic state challenges the term; owner route = definitions-governance; residue -> `definitions/reviews/`.

Confirm contract: active by direct owner admission and synchronized definition/ontology validation.

Promotion boundary: semantic recovery identity only; it is not execution or implementation evidence.

## domainspec-v2-D38. Durable Compensation Dispatch

Status: active

Source kind: method-vocabulary; owner-admitted durable coordination aggregate

Evidence: [durable compensation concept model](../development/durable-compensation-concepts/README.md) ·
[Recovery Intent](#domainspec-v2-d37)

Formal voice:

```text
DurableCompensationDispatch = (
  dispatch_id,
  intent_id,
  frozen_plan_digest,
  durable_progress_journal,
  dispatch_state,
  version
)

dispatch_state in {ready, leased, executing, retry-scheduled, terminal}

ready -> leased -> executing -> terminal
leased -> ready
executing -> ready | retry-scheduled
retry-scheduled -> ready
```

Every transition compares against the current version and is recorded atomically with its dispatch outbox
record. The intent, frozen plan, completed progress, exact Operation binding, and D40 identity survive worker
loss and restart. A terminal dispatch has no implicit successor.

Plain-language voice: the dispatch is the durable recovery record. It remembers what must run, what already
finished, and where execution can safely resume.

Domain-context voice: DomainSpec binds one D37 intent to the D36 plan. The dispatcher coordinates existing
Operations but never replans, substitutes an Operation, or absorbs its business effects.

Use carefully: dispatch state answers where durable coordination is, not whether recovery is semantically
satisfied or whether one invocation succeeded.

Misuse warning: do not infer a durable dispatcher implementation from this active semantic contract.

Challenge contract: non-atomic transition/outbox recording, mutable plan identity, lost completed progress,
or a successor from terminal challenges the term; owner route = definitions-governance plus runtime owner.

Confirm contract: active as canonical semantics; implementation remains explicit residue until executable
durability evidence exists.

Promotion boundary: durable coordination semantics only; no implementation, deployment, or production claim.

## domainspec-v2-D39. Compensation Execution Attempt

Status: active

Source kind: method-vocabulary; owner-admitted execution-episode identity

Evidence: [durable compensation concept model](../development/durable-compensation-concepts/README.md) ·
[Durable Compensation Dispatch](#domainspec-v2-d38)

Formal voice:

```text
CompensationExecutionAttempt = (
  attempt_id,
  dispatch_id,
  plan_occurrence_id,
  attempt_number,
  claim_id,
  lease_id,
  fencing_token,
  started_at,
  finished_at?,
  outcome
)

outcome in {succeeded, failed, unknown}
```

One attempt is one bounded executor episode for one planned Operation occurrence. Starting execution after a
retry or takeover creates a new attempt. Claim acquisition and lease grant or renewal alone do not.

Plain-language voice: an attempt is one try. Losing the worker can make the result unknown, which is different
from proving that the Operation failed.

Domain-context voice: every DomainSpec attempt retains the exact Operation occurrence and evidence references;
an unknown result can be replayed only with D40's unchanged invocation identity.

Use carefully: attempt identity changes per execution episode; semantic recovery identity does not.

Misuse warning: do not turn a failed or unknown attempt directly into a terminal recovery disposition.

Challenge contract: reused attempt identity, missing authority binding, or loss treated as proven failure
challenges the term; owner route = definitions-governance plus runtime owner.

Confirm contract: active as canonical semantics; durable attempt recording remains implementation residue.

Promotion boundary: one execution episode only; not the whole recovery outcome.

## domainspec-v2-D40. Compensation Invocation Identity

Status: active

Source kind: method-vocabulary; owner-admitted replay-protection identity

Evidence: [durable compensation concept model](../development/durable-compensation-concepts/README.md) ·
[canonical runtime contract](../impl/architecture-conformance/targets/typescript/workflow-compensation-v1.md)

Formal voice:

```text
invocation_identity = H(intent_id, plan_digest, operation_id, plan_occurrence_id)

For attempts a and b over the same plan occurrence:
  invocation_identity(a) = invocation_identity(b)
  attempt_id(a) != attempt_id(b)

semantic_application_count(invocation_identity) <= 1
```

The identity excludes worker, process, attempt, claim, lease, and scheduling values. The exact recovery
Operation or its bound adapter must durably recognize an already-applied identity and return its recorded
result without repeating the business effect.

Plain-language voice: every retry is a new try at the same recovery action, so it gets a new attempt identity
but reuses the same business-safe replay key.

Domain-context voice: DomainSpec refines D36's deterministic idempotency key into a stable identity for each
planned Operation occurrence. The same Operation appearing twice in one plan receives two occurrence keys.

Use carefully: the guarantee is at-least-once invocation with at-most-once semantic application, not universal
exactly-once delivery.

Misuse warning: do not rotate the key on retry or use a Claim or Lease as business-effect replay protection.

Challenge contract: a retry-specific key or repeated semantic application for one identity challenges the
term; owner route = definitions-governance plus the Operation binding owner.

Confirm contract: active by direct owner admission; current deterministic key evidence is bounded by the
reference runtime, and durable adapter coverage remains independently observable.

Promotion boundary: replay identity and semantic deduplication contract only.

## domainspec-v2-D41. Compensation Claim

Status: active

Source kind: method-vocabulary; owner-admitted exclusive advancement authority

Evidence: [durable compensation concept model](../development/durable-compensation-concepts/README.md) ·
[Durable Compensation Dispatch](#domainspec-v2-d38)

Formal voice:

```text
CompensationClaim = (
  claim_id,
  dispatch_id,
  claimant_id,
  acquired_at,
  acquired_dispatch_version,
  fencing_token,
  claim_state
)

claim_state in {current, released, superseded}

current(claim) iff
  claim.claim_state = current
  and claim.fencing_token = greatest_committed_fencing_token(claim.dispatch_id)

may_advance(claim, now) iff current(claim) and exists active D42 lease at now
```

Acquisition is compare-and-set against `acquired_dispatch_version` and atomically creates a fencing token
greater than every prior committed token for the dispatch. Takeover creates a new Claim and supersedes every
earlier claimant.

Plain-language voice: the Claim identifies which worker is currently allowed to move one recovery record
forward. Its fence stops an older worker from committing after takeover.

Domain-context voice: DomainSpec uses the Claim to serialize D38 coordination only. D40 protects business
effects, and each Operation retains its own effect authority.

Use carefully: advancing a dispatch requires both the current Claim and an active D42 Lease.

Misuse warning: do not collapse the Claim into its Lease, Replay Identity, attempt, or domain ownership.

Challenge contract: two current claims, non-monotonic fencing, or stale-worker advancement challenges the
term; owner route = definitions-governance plus runtime owner.

Confirm contract: active as canonical semantics; claim-store implementation remains residue.

Promotion boundary: exclusive dispatch advancement authority only; not Operation or business authority.

## domainspec-v2-D42. Compensation Claim Lease

Status: active

Source kind: method-vocabulary; owner-admitted bounded claim validity

Evidence: [durable compensation concept model](../development/durable-compensation-concepts/README.md) ·
[Compensation Claim](#domainspec-v2-d41)

Formal voice:

```text
CompensationClaimLease = (
  lease_id,
  claim_id,
  lease_generation,
  valid_from,
  expires_at,
  renewed_from_lease_id?
)

active(lease, now) iff
  valid_from <= now < expires_at
  and lease.lease_generation = greatest_committed_generation(lease.claim_id)
  and current(claim(lease.claim_id))
```

Renewal creates a newer Lease generation for the same Claim and preserves its fencing token. Expiry before
execution creates no attempt. Expiry after execution begins makes that attempt unknown; takeover creates a new
D41 Claim before any successor attempt.

Plain-language voice: the Lease is the Claim's deadline. If a worker stops renewing it, another worker can
eventually take over instead of leaving recovery stuck forever.

Domain-context voice: DomainSpec uses the Lease for crash-recovery liveness while the Claim and fence preserve
exclusive advancement safety.

Use carefully: Claim and Lease lifecycles are independent of retry; authority loss may occur without retry.

Misuse warning: do not treat Lease renewal as retry or a Lease as business-effect replay protection.

Challenge contract: unbounded validity, renewal changing Claim or fence, or advancement after expiry
challenges the term; owner route = definitions-governance plus runtime owner.

Confirm contract: active as canonical semantics; clock, duration, cadence, and storage remain architecture
choices and implementation residue.

Promotion boundary: time-bounded Claim validity only.

## domainspec-v2-D43. Compensation Retry

Status: active

Source kind: method-vocabulary; owner-admitted successor-attempt scheduling

Evidence: [durable compensation concept model](../development/durable-compensation-concepts/README.md) ·
[Compensation Execution Attempt](#domainspec-v2-d39)

Formal voice:

```text
CompensationRetry = (
  dispatch_id,
  predecessor_attempt_id,
  successor_attempt_number,
  not_before,
  remaining_budget,
  selected_policy_ref
)

retry preserves:
  intent_id, dispatch_id, plan_digest, durable progress, Operation binding,
  plan occurrence, invocation identity

retry changes:
  attempt_id, scheduling metadata

retry may change after authority loss or takeover:
  claim_id, lease_id, fencing_token
```

Retry exists only when the failed Operation's explicit continuation, or an explicitly selected policy allowed
by that binding, selects retry. Limits and backoff are bounded and persisted before eligibility.

Plain-language voice: retry means “try the same declared recovery action again later,” not “choose a new plan.”

Domain-context voice: the DomainSpec dispatcher enacts the Operation-owned continuation. It cannot invent retry
policy, reset completed progress, or convert escalation into retry.

Use carefully: Claim acquisition and Lease renewal are not Retry; scheduling is not execution.

Misuse warning: do not retry with a new D40 identity, substitute an Operation, or retry after terminal state.

Challenge contract: unbounded retry, replanning, or continuation bypass challenges the term; owner route =
definitions-governance plus the Operation binding owner.

Confirm contract: active as canonical semantics; durable scheduling remains implementation residue.

Promotion boundary: authorized successor-attempt scheduling only.

## domainspec-v2-D44. Compensation Terminal Disposition

Status: active

Source kind: method-vocabulary; owner-admitted terminal recovery result

Evidence: [durable compensation concept model](../development/durable-compensation-concepts/README.md) ·
[Durable Compensation Dispatch](#domainspec-v2-d38)

Formal voice:

```text
CompensationTerminalDisposition = (
  dispatch_id,
  disposition,
  final_attempt_id?,
  cause,
  evidence_refs,
  recorded_at
)

disposition in {completed, exhausted, escalated}
```

`completed` requires durable success evidence for every plan occurrence. `exhausted` requires an explicit
terminal-failure continuation or consumed retry budget. `escalated` requires the Operation-owned escalation
route. A terminal dispatch has no implicit successor.

Plain-language voice: Terminal Disposition is the durable final answer for the whole recovery, not the result
of one attempt.

Domain-context voice: DomainSpec records the final attempt and evidence without turning that record into
permission for another Workflow or Operation.

Use carefully: only `completed` makes D37 satisfied; `exhausted` and `escalated` make it unresolved.

Misuse warning: do not treat a failed attempt, exhausted retry budget, or escalation receipt as permission for
implicit successor work.

Challenge contract: terminal state without its required evidence or any implicit successor transition
challenges the term; owner route = definitions-governance plus runtime owner.

Confirm contract: active as canonical semantics; durable terminal recording remains implementation residue.

Promotion boundary: terminal recovery meaning only; no publication, deployment, or successor authority.

## domainspec-v2-D45. Concern-Specific Dependency Contract

Status: active

Source kind: method-vocabulary; owner-admitted implementation-boundary model

Evidence: [Operation, Workflow, and Infrastructure-Binding Pattern Research](../development/research/2026-08-20-operation-workflow-infrastructure-binding-patterns/TOWER.md) ·
[System Integration Contract Layer Revision 2](../development/refinement-runs/20260813T153029Z-system-integration-contract-layer-revision-2/RESULT.md) ·
[Infrastructure-Binding Architecture Admission](../development/meta-type-instantiation-cli/OWNER-INFRASTRUCTURE-BINDING-ARCHITECTURE-ADMISSION.json) ·
[Durable Recovery Architecture](../architecture/durable-recovery/README.md)

Research provenance: the Tower supplies the responsibility-specific seam and non-collapse model; Revision 2
confirms the separate system-integration ownership plane; the owner admission makes that model canonical.
Neither research artifact selects a provider or implementation profile.

Formal voice:

```text
ConcernSpecificDependencyContract = (
  contract_id,
  concern,
  consumer_roles,
  operation_signatures,
  failure_surface,
  implementation_profile_ref
)

requires:
  one named concern per contract
  provider mechanics absent from consumer-owned signatures
  concrete realization supplied at a composition boundary
```

A dependency contract is named for the responsibility it exposes, such as a Recovery Repository, Recovery
Unit of Work, Clock, Scheduler, Wakeup capability, or Operation Binding Resolver. DomainSpec does not require
one universal code-level `Port` abstraction, DI container, decorator system, or service locator. A DomainSpec
Interface remains a DS-D1 logical boundary and is not implied merely because code consumes a dependency.

Plain-language voice: name the seam after the job it performs. A store contract, clock, and message sender
have different responsibilities and should not be hidden behind one generic dependency shape.

Domain-context voice: the durable-recovery runtime consumes a Recovery Coordination Repository, a local
Recovery Unit of Work, a Clock, a Wakeup capability, and exact Operation bindings. A TypeScript profile may
express these as structural types supplied through higher-order-function construction; another profile may
choose another language form without changing the concern.

Use carefully: this term governs responsibility and dependency direction, not suffixes, files, framework
choice, or provider technology.

Misuse warning: do not turn every dependency into a DomainSpec Interface or infrastructure-binding record.
Pure helpers and local capabilities may need only an exact implementation binding.

Challenge contract: a generic contract that erases concern-specific failure or evidence obligations, or a
consumer importing concrete provider mechanics, challenges the term; owner route = implementation-profile
owner plus definitions-governance.

Confirm contract: active as the canonical code-seam model; language-specific shapes remain profile-owned.

Promotion boundary: dependency responsibility and direction only; no provider or runtime guarantee.

## domainspec-v2-D46. Persistence Binding

Status: active

Source kind: method-vocabulary; owner-admitted infrastructure-binding record

Evidence: [Operation, Workflow, and Infrastructure-Binding Pattern Research](../development/research/2026-08-20-operation-workflow-infrastructure-binding-patterns/TOWER.md) ·
[System Integration Contract Layer Revision 2](../development/refinement-runs/20260813T153029Z-system-integration-contract-layer-revision-2/RESULT.md) ·
[Infrastructure-Binding Architecture Admission](../development/meta-type-instantiation-cli/OWNER-INFRASTRUCTURE-BINDING-ARCHITECTURE-ADMISSION.json) ·
[Durable Recovery Architecture](../architecture/durable-recovery/README.md)

Research provenance: the Tower separates a Repository contract from persistence metadata; Revision 2
introduces the candidate `PersistenceBinding` record and ownership split; the owner admission accepts the
distinction while leaving the adapter and provider open.

Formal voice:

```text
PersistenceBinding = (
  binding_id,
  logical_subject_refs,
  dependency_contract_ref,
  adapter_ref,
  resource_ref,
  implementation_profile_ref,
  logical_physical_mapping_ref,
  evidence_boundary
)
```

The binding connects exact logical persistence roles and one D45 contract to one selected physical
realization and its evidence boundary. `interface_ref` is optional and is present only when an actual DS-D1
Interface owns the logical boundary; Entity, Operation, Query, Workflow-runtime, or other exact subject refs
may bind persistence without inventing an Interface. Database, ORM, schema, migration, connection, locking,
and provider configuration remain implementation-profile or adapter concerns.

Plain-language voice: a Persistence Binding says which repository-shaped contract uses which concrete store
realization, and exactly how far the evidence for that choice reaches.

Domain-context voice: DomainSpec durable recovery binds the Recovery Coordination Repository to the selected
coordination-store adapter. The binding may prove exact reads and writes for that adapter, but it does not by
itself prove atomicity, retry safety, delivery, or production durability.

Use carefully: keep the code contract, metadata binding, concrete adapter, runtime observation, and owner
decision as separate records.

Misuse warning: a Repository shape is not a Persistence Binding, and a passing schema or fixture is not proof
that a database committed or recovered state.

Challenge contract: an unbound adapter, ambiguous logical-to-physical mapping, missing evidence boundary, or
provider detail smuggled into portable semantics challenges the term; owner route = system-integration owner
plus implementation-profile owner.

Confirm contract: active as canonical infrastructure-binding semantics; provider implementation remains
separate evidence.

Promotion boundary: persistence realization identity and bounded evidence only.

## domainspec-v2-D47. Transaction Guarantee Binding

Status: active

Source kind: method-vocabulary; owner-admitted local-atomicity binding

Evidence: [Operation, Workflow, and Infrastructure-Binding Pattern Research](../development/research/2026-08-20-operation-workflow-infrastructure-binding-patterns/TOWER.md) ·
[System Integration Contract Layer Revision 2](../development/refinement-runs/20260813T153029Z-system-integration-contract-layer-revision-2/RESULT.md) ·
[Infrastructure-Binding Architecture Admission](../development/meta-type-instantiation-cli/OWNER-INFRASTRUCTURE-BINDING-ARCHITECTURE-ADMISSION.json) ·
[Durable Recovery Architecture](../architecture/durable-recovery/README.md)

Research provenance: the Tower supplies the local-Unit-of-Work and non-Workflow-wide-transaction boundary;
Revision 2 introduces the candidate `TransactionGuaranteeBinding` record; the owner admission accepts only
the portable distinction, not any database guarantee.

Formal voice:

```text
TransactionGuaranteeBinding = (
  binding_id,
  unit_of_work_contract_ref,
  participant_refs,
  atomicity_scope,
  selected_guarantees,
  implementation_profile_ref,
  failure_outcome_binding_ref,
  evidence_boundary
)
```

The binding declares one exact local commit boundary and its participants. It applies only when atomicity or
another named transaction guarantee is claimed. It requires D48 typed failure outcomes and provider-specific
commit, rollback, conflict, partial-commit, and restoration observations. It never creates one transaction
over a multi-step Workflow or across independent resources.

Plain-language voice: a Transaction Guarantee Binding states exactly which writes must succeed or fail
together in one selected local transaction.

Domain-context voice: a durable-recovery coordination transition and its dispatch-outbox record share one
Recovery Unit of Work. Each recovery Operation separately owns its business-state-and-outbox transaction;
the coordinator never combines the two boundaries into a distributed transaction.

Use carefully: declare only guarantees the selected adapter and evidence can observe. Isolation, durability,
or rollback restoration must not be inferred from the word transaction.

Misuse warning: do not describe Workflow compensation as database rollback or claim Workflow-wide atomicity.

Challenge contract: unresolved participants, a missing D48 reference, partial-commit ambiguity, or a claim
beyond the selected local resource challenges the term; owner route = transaction binding owner plus the
Operation or durable-runtime owner.

Confirm contract: active as canonical local-transaction binding semantics; exact provider guarantees remain
profile-bound.

Promotion boundary: one declared local transaction boundary only.

## domainspec-v2-D48. Failure Outcome Binding

Status: active

Source kind: method-vocabulary; owner-admitted integration-failure classification

Evidence: [Operation, Workflow, and Infrastructure-Binding Pattern Research](../development/research/2026-08-20-operation-workflow-infrastructure-binding-patterns/TOWER.md) ·
[System Integration Contract Layer Revision 2](../development/refinement-runs/20260813T153029Z-system-integration-contract-layer-revision-2/RESULT.md) ·
[Infrastructure-Binding Architecture Admission](../development/meta-type-instantiation-cli/OWNER-INFRASTRUCTURE-BINDING-ARCHITECTURE-ADMISSION.json) ·
[Durable Recovery Architecture](../architecture/durable-recovery/README.md)

Research provenance: the Tower requires failure evidence to remain distinct from continuation authority;
Revision 2 introduces the candidate `FailureOutcomeBinding` record; the owner admission preserves
`retryable`, `non-retryable`, and `unknown` without turning classification into Retry selection.

Formal voice:

```text
FailureOutcomeBinding = (
  binding_id,
  concern_ref,
  provider_outcome_ref,
  outcome_class,
  evidence_refs,
  continuation_owner_ref
)

outcome_class in {retryable, non-retryable, unknown}
```

The binding classifies one provider or integration failure without selecting the continuation that consumes
it. `unknown` is required when evidence cannot distinguish application, rollback, commit, delivery, or other
relevant outcomes. Retry is permitted only through a separately declared continuation and stable semantic
identity; the binding cannot make an unsafe operation retryable.

Plain-language voice: a Failure Outcome Binding translates a concrete failure into a typed result while
preserving uncertainty instead of guessing what happened.

Domain-context voice: durable recovery maps store conflicts, rollback failures, authority loss, and unknown
Operation outcomes into explicit continuations. A D39 failed or unknown attempt remains distinct from the D44
terminal result of the whole recovery.

Use carefully: preserve the provider observation separately from the classification and the later retry,
escalation, or terminal decision.

Misuse warning: do not turn every failure into retry, collapse `unknown` into failed, or treat classification
as proof that state was restored.

Challenge contract: missing raw evidence, provider-authored continuation authority, or classification that
hides an unknown commit or business-effect outcome challenges the term; owner route = failure-outcome owner
plus continuation owner.

Confirm contract: active as canonical failure-classification semantics; retry mechanics and budgets remain
separately owned.

Promotion boundary: typed failure meaning only; no implicit continuation.

## domainspec-v2-D49. Durable Workflow Runtime Binding

Status: active

Source kind: method-vocabulary; owner-admitted durable-profile composition binding

Evidence: [Operation, Workflow, and Infrastructure-Binding Pattern Research](../development/research/2026-08-20-operation-workflow-infrastructure-binding-patterns/TOWER.md) ·
[System Integration Contract Layer Revision 2](../development/refinement-runs/20260813T153029Z-system-integration-contract-layer-revision-2/RESULT.md) ·
[Infrastructure-Binding Architecture Admission](../development/meta-type-instantiation-cli/OWNER-INFRASTRUCTURE-BINDING-ARCHITECTURE-ADMISSION.json) ·
[Durable Recovery Architecture](../architecture/durable-recovery/ARCHITECTURE.md)

Research provenance: the Tower supplies the durable-only composition spine; Revision 2 confirms the sibling
system-integration ownership plane and evidence join; the owner admission accepts the binding concept without
selecting its runtime, database, queue, or provider composition.

Formal voice:

```text
DurableWorkflowRuntimeBinding = (
  binding_id,
  workflow_profile_ref,
  persistence_binding_refs,
  transaction_guarantee_binding_refs,
  failure_outcome_binding_refs,
  scheduler_contract_ref,
  clock_contract_ref,
  wakeup_contract_ref?,
  replay_contract_ref,
  version_compatibility_ref,
  evidence_boundary
)
```

The binding is required only when a selected Workflow profile claims durable progress across process loss or
restart. It composes concern-specific contracts and bindings; it does not replace D46 persistence records or
turn runtime-provider behavior into portable Workflow meaning. A synchronous in-process Workflow profile does
not inherit checkpoint, lease, timer, replay, or version-compatibility obligations merely because the durable
profile has them.

Plain-language voice: a Durable Workflow Runtime Binding is the manifest that names everything a restart-safe
Workflow runtime depends on and the evidence required for that exact combination.

Domain-context voice: DomainSpec durable recovery uses this binding to connect Recovery Intent coordination,
the Recovery Repository and Unit of Work, Claim and Lease timing, retry scheduling, wakeups, restart
reconciliation, and Operation-owned replay safety without selecting a database or queue in the ontology.

Use carefully: bind one exact profile and provider composition. Persistence, scheduling, delivery, replay,
and version evidence retain their own scopes and owners.

Misuse warning: do not apply this binding to every Workflow, use it as a generic service container, or infer
that one passing provider proves every durable runtime.

Challenge contract: missing concern bindings, ambiguous synchronous/durable applicability, replay identity
drift, or absent restart/version evidence challenges the term; owner route = Workflow profile owner plus
system-integration owner.

Confirm contract: active as canonical durable-profile composition semantics; provider selection and runtime
proof remain implementation work.

Promotion boundary: exact durable-runtime composition and evidence boundary only.

<!-- SKELETON note: D1-D2 mint-seeded; D3-D5 consolidated 2026-07-01 into this canonical home (was the
     separate governance surface DSV2-D1/2/3, now removed). Companions backfilled 2026-07-01 to the current
     mint baseline: DEFINITIONS-INDEX + DEFINITION-DRIFT-AUDIT + DEFINITION-LOCALIZATION-ROUTE + reviews/.
     Governance-kind cards for layering-governance and drift-governance were added 2026-07-02 as D16/D17.
     DS-D1 meta-type system lives in meta-types/ (human meta-types.md + machine meta-types.yml), linked above. -->
