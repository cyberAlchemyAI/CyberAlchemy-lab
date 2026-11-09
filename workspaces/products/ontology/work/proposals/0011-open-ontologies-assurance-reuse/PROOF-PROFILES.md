# Proof profiles and what acceptance means

## A check is about an exact statement

Keep four independent questions visible: was the backend evidence accepted;
does the export preserve the selected Lab formal meaning; does that formal
meaning faithfully represent the source definition; and does the result meet
the required obligation? Approval and real-world truth remain separate.

The [profile catalog](PROFILES.json) describes proposed routes. None is currently
registered. There is no implicit profile or fallback to an easier checker.

Pinned source anchors:
[input fragment and file formats](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/lean/Fol/Syntax.lean),
[checker and soundness theorems](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/lean/Fol/Check.lean),
and [existing concrete witness pattern](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/lean/Fol/Witness.lean).

## The first definition profile

DA-FOL-ENC1 and DA-FOL-KERNEL1 accept one explicitly selected nonempty sort,
constants, unary/binary predicates, equality, closed formulas and complete finite
models. Supported connectives are not/and/or/implies/iff and forall/exists.
Zero-arity and higher-arity predicates, positive-arity functions, extra sorts,
unbound variables, missing interpretations, and temporal/normative/recursive
extensions are refused. A lost construct is never silently ignored.

This deliberately matches the copied Fol checker. Our existing richer Python
evaluator remains available under its own profile. A future richer lowering
needs its own proof; these initial profiles do not downgrade a requested theory
to fit the backend.

### Translation algorithm

1. Reuse exact Lab source/IR and required-set validation. Select T, required
   populations I, and the exact query Q without adding Q as an assumption.
2. Check the entire signature and every formula against the profile. Require
   closed formulas and a positive concrete carrier size.
3. Allocate injective symbols from canonical source-qualified identities. Use
   disjoint predicate/constant namespaces and reversible UTF-8 hex encoding;
   do not identify symbols by display names or hash alone.
4. Assign fresh natural-number binders with an explicit lexical environment.
   Preserve shadowing and reject capture. Lower iff to two implications,
   empty conjunction to true and empty disjunction to false.
5. Map constants and each complete unary/binary table to the source model's
   carrier indices. Preserve explicit false entries. Reject omitted or duplicate
   table entries, out-of-range indices and accidental carrier/symbol-map
   collisions. Distinct constants may denote the same element; do not add a
   unique-name assumption.
6. Emit problem/model TSV in the copied ABI and an independent source-to-target
   map. Its FNV identifier is only a format identifier. Bind raw source, export,
   labels, roles, required-set and mapping bytes with SHA-256 externally.
7. Independently decode the exported problem/model and compare them with the
   selected source IR/model. A matching hash of the emitter's own output is
   not sufficient to establish meaning preservation.

The explicit source logic and target Fol semantics must have a bridge with the
shape `sourceSatisfies M phi iff FolHolds (encodeModel M) (lower phi)` for every
supported well-typed closed formula. Model identity, required populations,
constant interpretation, equality and symbol injectivity are part of it.
The source-side denotation must be stated independently of the exporter.

The general bridge and its actual source/proof/import bindings are required
before a result is called kernel-checked **about Lab IR**. Earlier runs can be
reported as checks of an encoded candidate only. A bridge theorem about a
formal IR does not prove that a JSON parser or an informal definition is correct.

### Native acceptance and fresh Lean proof are different

DA-FOL-ENC1 runs the unchanged `oo-folmodel PROBLEM.tsv MODEL.tsv` executable.
That is acceptance by a compiled evaluator whose correctness was proved once.
It depends on the parser, compiler/runtime and host. It is not a fresh kernel
proof for the Lab request and cannot satisfy a kernel-replay requirement.

DA-FOL-KERNEL1 adds a proof builder. It emits concrete constructor data for
the selected theory, model and query outside the vendor tree. The pattern
already exists in upstream `lean/Fol/Witness.lean`:

```lean
-- Shape only: generated files contain concrete data, not these ellipses.
def theory : List Fol.Form := ...
def model : Fol.FinModel (n + 1) := ...
theorem checked : Fol.check model theory = true := by decide
theorem model_exists : Fol.Satisfiable theory :=
  Fol.satisfiable_of_check checked
```

The generator supplies a concrete positive numeral and complete model tables.
It also proves the appropriate symbol-coverage/closedness facts and binds exact
table identity. `Fol.covers` checks formula symbol coverage; by itself it does
not show that emitted tables equal the source witness.

For a countermodel to Q, emit T and I plus `not Q` and apply the copied
`Fol.not_entails_of_check`. For consistency or joint inhabitation, prove model
existence for T or T and I as required. A positive query true in one witness is
only a statement about that witness; it does not establish Q in every model.
Prove that the same concrete M satisfies T, I and Q, using `check_iff`/`eval_iff`
or the exact combined witness. The example `model_exists` alone only proves
consistency and cannot fill that positive-query obligation.

Compile the concrete proof and replay it in a fresh pinned Lean environment.
Inspect the actual proposition, data, dependencies and axiom closure against
an independently assembled expected challenge. Merely finding a theorem name
or successful compiler exit is insufficient. Fixed generated tactics use
kernel computation (`by decide`), not `native_decide`, `sorry`, arbitrary user
tactics, imports, options or Lean source.

The copied Fol.Check theorem footprint is `[propext, Quot.sound]`. Pin the
actual bridge/leaf footprint too; any additional axiom needs its own profile
decision. Retain source and compiled import closures. A proof timeout is
incomplete; it must not fall back to native acceptance with the stronger label.

### Minimum strength is not just a label

A kernel proof of model existence still cannot discharge a required universal
property or general conservativity theorem. Match the exact proposition and
its quantifier/scope, not an ordinal ranking of the words “witness” and “proof.”
Every required population must hold in the same selected model. A satisfying
model or an empty bounded search cannot establish unbounded nonexistence.

## Agent views: CTX-HORN1

Export one captured ontology view with exact meaning/review references and its
task goals. First support ground, explicitly typed triples with stable named
identities. Refuse blank nodes, undeclared relation mappings, implicit n-ary
reification, unknown-value encodings and unbound qualifiers in this profile.

Keep full source G, smaller view P, rules R and goals Q distinct. Confirm that
P is a subset of G and that both runs use R and complete within bounds.
Use the copied `preserve` workflow and independently replay each selected
certificate. Bind certificate kind to checker ABI: mixed built-in certificates
use `oo-cert`, supplied Horn tables use `oo-horn check` with the exact table.
Their verdicts retain the difference between built-in semantic rules and
assumed supplied rules. An explicit checker path must match that kind.
Report preserved, lost-by-view, unsupported-in-source, invalid
comparison or incomplete. No source support is not a proof of falsity.

The bridge must state which Lab claims a triple represents. A mapping of
relation identities, types, qualifiers or protected authority roots is explicit;
generic RDF/OWL rules cannot create a Lab admission or operational permission.
This is a task-view workflow, not a replacement for existing typed-closure and
fresh-head extension theorems.

## Change reports: RDF-CHANGE-RL1

Reuse the copied planner's structural/logical/consequence reports and
closure-difference engine. Each report binds exact before/after datasets and
one rule profile. The unchanged batch `plan` interface takes a complete target,
uses replacement mode and fixes `owl-rl`, a 10,000 scan limit and a 1,000,000
render limit. Normalize additive input to G union delta and bind that full
target. Refuse requests for options this ABI cannot honor. These fixed caps
must appear in the effective profile and completion accounting.
The initial conservativity question accepts additive
extensions. Removals/replacements, incomplete scans or unknown reasoning remain
explicitly undecided for that question; structural findings can still be shown.

An empty difference means no new consequences under that completed rule table.
It does not establish general model conservativity or harmless business change.
The Lab's existing current-head and owner approval gates continue to govern
any later application. No upstream apply/rollback operation is exposed.

## Later profiles

FOL-REFUTE1 reuses supported resolution/LRAT/DL certificate routes. It must bind
the exact source theory, its checked encoding/clause set, and the negated target
where relevant. A valid proof of a caller-supplied weaker clause set is not a
proof of the selected Lab obligation. Unsupported proof steps remain refusals.

SHACL-CORE1 checks supported shapes on an already selected static export. It
does not forward conflicting temporal flags to the verified backend. Parse and
shape-compilation correctness remain separate from its evaluator theorem.

DA-FOL-RICH2 requires a separate bridge or reviewed checker extension for many
sorts, total functions, higher arities and complete model encodings. Sort
relativization must retain required nonempty domains; reified tuples need exact
membership and interpretation rules. Copy existing Fol code first and isolate
any extensions. No generic richness or compatibility is claimed by this design.

Isabelle/Rocq routes apply to their Horn formats. They do not automatically
cross-check generic finite-model proofs or all existing relational Lean proofs.
