# Implementation detail and algorithm contracts

Candidate design only. The functions and commands described here are future implementation, not currently available APIs. Exact planned files, unit ownership and validation phases are in [swu-manifest.json](swu-manifest.json). Task pages supplement these algorithms with concrete criteria and controls.

## A01–A03: decode, capture and currentness

Inputs: exact UTF-8 bytes, closed input schema, allowed repository root, selected registry version mapping, and expected input references. Output: either a typed source snapshot or a typed failed/unresolved receipt.

```text
decode(bytes, schema):
  reject invalid UTF-8 / duplicate object keys / illegal numeric values
  parse JSON without implicit defaults
  validate closed shape, required fields, types, unique identities
  reject extra fields and external schema retrieval
  return typed input OR malformed(path, diagnostic)

capture(registry_ref):
  read registry bytes -> r0 and digest0
  for each exact current identity -> version_ref:
    resolve exactly one entry with that identity and version
    reject missing/duplicate entry or non-admitted effective selection
    normalize relative path; reject traversal/symlink escape outside allowed root
    read source bytes once, compute SHA-256
    compare expected digest, source ID and source version
    bind source clauses, schema identity and exact admission-reference metadata
  record all historical entries separately
  reread registry and every captured file before publish
  if any bytes changed: stale attempt, publish no success
  publish complete absent candidate snapshot or failure receipt
```

Hash equality is a binding check, not proof of cryptographic collision resistance, source truth or actual authorization. Filesystem path confinement, JSON decoder, SHA-256 library and trusted selected registry remain audited assumptions. Source labels saying “candidate” do not override the selected effective admission entry. Missing inputs yield missing/unknown; digest/version changes yield stale; neither is a semantic counterexample.

## A04–A06: correspondence and obligation generation

Inputs: current Definition/v1 source, full normative clause map, explicit signature, carrier alignments, reviewed relation classes, declared assumptions and population policy. Outputs: source-bound interpretation and the complete required statement manifest.

Each normative clause has a stable selector and excerpt digest. Its disposition is encoded, externally assumed, explanatory with rationale, deferred or unresolved. Required source meaning cannot be silently dropped. Scientific-formal, plain-language and domain-example voices remain distinct; explain source precedence rather than concatenating them into axioms.

```text
requirements(interpretations, sealed_relation_policy, change):
  require all compared carriers aligned explicitly
  require complete clause and dependency declarations
  include source-fidelity, typing, closure and currentness obligations
  T := all included definitions + assumptions + couplings + invariants
  I := conjunction of declared required model-population obligations
  include SAT(T) and SAT(T AND I)
  for every relevant reviewed neighbour relation:
    alias: include exact A <-> B obligation; no unequal-extension query
    subtype: include inclusion and A inhabitant; properness only if declared
    overlap: include intersection and declared directed difference(s)
    disjoint: include exclusion plus both required inhabitants
    independent axes: include each forbidden-implication countermodel
                      plus move-frame and allowed-coupling checks
    unresolved: emit unresolved required relation, not success
  for each source/interpretation/coupling/profile change:
    include affected closure + combined snapshot regression
    add exact compatibility/conservativity claim only if explicitly requested
  seal sorted IDs, actual statements, prerequisites, strengths and digest
```

The requirement generator owns the required set. A supplied result list is compared to that set and cannot self-certify completeness. All-model distinction is a separate proposition; generating an existential permissible distinction does not satisfy it. Expected source meaning, theorem text and evidence statement must agree byte-for-byte or through an explicitly validated canonical normalization.

## A07–A10: successor pilot semantics

The v1 pilot stays immutable. The v2 candidate must represent independent dimensions:

- Whether an owner-qualified scoped grant/right is active.
- Whether an Authority Claim record asserts such a right, with complete fields.
- Whether a responsibility exists; obligation does not automatically grant permission.
- Whether provenance is recorded, empty under a selected meaning, incomplete with owned residue, or unknown.
- A governance move over one exact subject, with actual before/after records and active grants.

The candidate can distinguish an ungrounded claim from granted authority. A template of a possible grant confers no right. Unknown lineage is not a negative assertion about historical origin. Grant legitimacy remains an external premise unless a separately translated authorization theory establishes it.

```text
move_valid(subject, before, after, intended, recorded):
  require exact subject identity/version and record-posture correspondence
  delta := actual changed normative components(before, after)
  require delta subset intended union explicitly_recorded_changes
  require recorded_changes subset delta
  require any authority delta has a separately justified matching root/basis
  require all included provenance and record invariants before/after
  return only the selected predicate result, not real admission permission
```

Controls: claim without a grant; grant for another scope/object; responsibility without permission; no-op move; silently changed status; explicit legitimate coupling; posture/record mismatch; unrecorded grant delta; and unknown/empty/incomplete lineage. Owner fidelity review decides which candidate interpretation preserves the actual source. Candidate coding and tests do not change canonical meaning.

## C01–C03: typed semantics, closure and cycles

The smallest IR supports explicit sort declarations, typed variables/constants, predicate applications, equality, Boolean connectives and selected quantifiers over named domains. No automatic global name unification or nominal type partition is allowed. Every later operator has a separate supported-fragment declaration, denotation and projection contract.

Define satisfaction `M, env |= phi` independently from executable `evaluate(phi, M, env)`. For each AST form, record the mathematical rule and executable lowering. Malformed variables, mismatched arity, unknown sorts and unsupported operators fail before evaluating an obligation. Unsupported logic is not false.

```text
closure(explicit_edges, selected_sources):
  resolve each exact dependency endpoint and interpretation binding
  traverse uses_definition edges to a fixed point
  preserve edge source selector and meaning-bearing basis
  if unresolved dependency exists: incomplete closure
  compute strongly_connected_components(explicit_edges)
  for each SCC: prepare one joint signature and theory unit
  condense SCC graph and topologically order resulting units
  separately evaluate any source invariant forbidding constraining cycles
```

The SCC algorithm can use Tarjan/Kosaraju with `O(V+E)` graph processing; this is a proposed implementation complexity, not a measured performance result. Raw semantic recursion is not automatically a prohibited value cycle. Conversely, condensing a prohibited cycle does not make it permissible. Names, aliases, citations and consumer lists are not edge declarations.

## P01–P05: provider capability and evidence

Inputs: actual statements, supported fragments, minimum strengths, runtime inventory and budgets. Output: one exact selected route per obligation, or explicit unsupported/missing route.

The finite provider enumerates only the declared domain and interpretation assignments. Stream the first verified witness; retain counters and search completeness rather than every full model in memory. Define enumeration completeness against the declared profile. Resource limits yield unknown/timeout, not exhaustive absence.

An SMT projection records sort/cardinality mapping, every axiom/query, normalization, native formula digest and solver build/options. A `sat` model must be checked against the canonical interpretation. An `unsat` result retains solver-result strength unless separately accepted proof evidence establishes more. Unknown/unsupported is not a counterexample. Quantifier and dynamic fragments are selected explicitly.

A mechanized route checks the exact submitted statement and dependency/axiom inventory; reject admitted target assumptions, `sorry`-based proofs or missing proof dependencies. Generic evaluator correctness must quantify over arbitrary supported inputs and prove executable success implies independently defined satisfaction. A theorem about one demonstration record is insufficient. Required obligation-generator coverage is a distinct statement.

A temporal/fixed-point projection retains the actual source rule, frame/state semantics and bounded/unbounded distinction. If provider projections differ, a whole-theory result needs a common interpretation or verified shared-symbol compatibility. Independently satisfiable projections cannot simply be joined as one model.

Conditional nodes P03–P05 need exact activation or non-applicability receipts. Non-applicability refers to a provider route, never to dropping a required meaning or strength. Profile selection remains unresolved where actual requirements cannot be supported.

## E01–E04: evidence verification and publishing

```text
verify_evidence(required_manifest, supplied_bundle):
  validate closed shape and unique IDs
  rehash exact source/interpretation/dependency/profile/provider bindings
  compare submitted obligations with the complete required denominator
  require identical actual statements, directions, prerequisites and strengths
  replay each model against independent canonical satisfaction and inhabitants
  verify each required proof under exact toolchain and axiom policy
  verify exhaustion/saturation certificate only at its supported strength
  return dimensioned actual verdicts; aggregate only afterwards
```

Do not overwrite existing evidence. Build into an absent private staging path and publish with create-only semantics. Check collisions at the actual publication boundary, not with a check-then-overwriting rename. On interruption, preserve old success and new failure-attempt evidence. No cleanup or deletion of historical evidence is implied by this design.

The trusted boundary includes parsing/hashing, semantic translator, requirements policy, provider lowerings, actual runtimes and verifier unless separately mechanized. Two independently handwritten evaluators are useful error detection, not a proof that both preserve prose meaning. Authentication of real roots and evidence truth remain separate from formal tuple matching.

## I01–I05: invalidation, extension impact and regression

```text
invalidate(base, proposal):
  diff exact source/version, clause, signature, statement and premise bindings
  include changed carrier alignments, couplings, bounds, profile and toolchain
  changed := all meaning/evidence-relevant subjects and requirement generators
  affected := changed union reverse_dependency_closure(changed)
  expand affected to whole SCCs and relevant neighbour obligations
  if selected source set changed: invalidate full snapshot denominator
  retain old evidence as historical; prohibit reuse as current
  regenerate affected required statements
  compile and check full selected theory T and T AND I
  recheck actual source currentness at publication/closeout
```

Cache entries are scoped optimization, never authority. A representation-only diff still needs exact correspondence/preservation evidence; a semantic revision requires revised obligations. Selected-data compatibility, invariant preservation and model conservativity are separate properties. The CLI is read-only with respect to canonical sources and generates candidate artifacts only.

## S01–S02 and F01–F14: full queue execution

Each current definition has exactly four units: T, O, E and R. Their input binds the actual version, source path and SHA-256; no convenient substitute Lifecycle definition is introduced. A family closure unit J consumes reviewed actual dependency closures, not merely editorial family members.

All draft T units precede S01, which seals actual semantic dependencies. S02 accounts for the complete 16,653-pair relevance/alignment denominator. Candidate evidence can run after selected-scope infrastructure passes G01 and conditional provider routes have dispositions. Actual owner reviews follow evidence so reviewers can inspect concrete witnesses and limitations. The conservative plan waits for all reviews before family J readiness; a later SCC-derived plan can narrow this barrier without guessing today.

If a clause requires symbols from an unresolved external theory, its check remains unresolved. Do not substitute untyped opaque values and call the whole meaning complete. Rejected fidelity reviews create a new candidate interpretation and an affected-closure retry, not an approval default.

## Z01–Z07: complete theory and diagnostics

```text
T_full := union of every included reviewed current interpretation,
          all shared alignments, declared axioms, couplings and invariants
I_full := conjunction of all required population obligations
require supported faithful composition of all included constructs
check SAT(T_full)
check SAT(T_full AND I_full) in one combined model
check all required distinction/inclusion/forbidden-inference statements
check separately required universal properties at declared proof strength
independently replay full evidence and recheck source currentness
```

A combined-model witness must interpret every included symbol. Pairwise checks and separate family models are insufficient. An unsat core helps diagnosis but is not claimed minimal unless its minimality is checked. Source-clause contradictions route to exact patch proposals; they are not automatically “fixed” by weakening an axiom.

Known hostile controls include `p`, `q`, `not(p and q)` for pairwise-versus-joint inconsistency; an empty required population under an otherwise satisfiable theory; an omitted cross-family coupling; a stale dependency review; and a projection retaining the theory digest while altering a meaning-bearing mapping.

## H01–H04: owner review, effects and closeout

Produce the complete concrete review package before requesting an owner decision. It includes exact source-to-interpretation correspondence, realistic examples, evidence ceilings, remaining assumptions and any proposed effects. Fidelity review accepts correspondence; semantic-source revision admission is a different effect. Owner silence is neither.

This planning request authorizes no actual semantic admission. H03 is a conditional handoff to the admitted workflow owner after later explicit exact effect selection and fresh currentness checks. It performs no default edit to the registry or other active implementation project. A no-admission decision remains a valid no-effect branch.

Closeout reports what actually passed, what remains unreviewed/unsupported/stale, and whether the complete theory was checked. Administrative disposition of an unresolved item does not relabel it proved. Candidate-only status synchronization preserves all original pilot and planning evidence.
