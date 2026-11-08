# Define integration work map: gaps and risks

Status: static audit and proposed amendments. No implementation, tests or admission performed.

## Assessment

The map has 67 work items, resolves its named dependencies and has no task cycles. Its recorded source bindings still match the inspected repository. **Acyclic does not mean executable or safe to admit.** The audit found 12 unresolved obligations: **3 critical, 7 high and 2 medium**. Critical here means the affected authorization/application claim must not be made until its design is closed; it does not mean a live compromise was found.

This is an author self-audit using repository code and plan evidence. Failure scenarios are proposed verification cases, not reproduced failures.

## Priority summary

| ID | Priority | Gap or risk | Must resolve before |
| --- | --- | --- | --- |
| [R01](#r01) | high | The proposed formal meaning needs an unambiguous interpretation | semantic promotion readiness and exact Definition owner decision |
| [R02](#r02) | critical | Key possession is not yet bound to the semantic principal | semantic authorization or repository application; read-only candidate work can proceed |
| [R03](#r03) | critical | Source parsing can use different bytes from the recorded digest | using successor source capture as authorization evidence |
| [R04](#r04) | critical | Repository publication has no chosen coherent commit boundary | the first repository admission transaction |
| [R05](#r05) | high | The future source epoch depends on records not yet created | freezing the adoption manifest and authorizing epoch advancement |
| [R06](#r06) | high | Cross-runtime parsing and hash rules remain unspecified | signed successor protocol interchange |
| [R07](#r07) | high | Verification can precede a required binding and late documentation | Product review and final adoption decisions |
| [R08](#r08) | high | A completed decision task does not mean its outcome permits continuation | automated continuation or authorized application |
| [R09](#r09) | high | Legacy compile and durable-session consumers need explicit adapters | changing pack/readiness/session protocols |
| [R10](#r10) | high | Semantic revision impact is not closed over declared consumers | a foundational Definition successor or any semantic revision admission |
| [R11](#r11) | medium | Pack and assurance work has no declared resource bounds | declaring production-like bounded operation or scaling beyond current fixtures |
| [R12](#r12) | medium | The first useful preview is tied to the entire authority implementation | starting broad implementation scheduling; does not block draft review |

## Findings

<a id="r01"></a>
### R01 — The proposed formal meaning needs an unambiguous interpretation

**Priority:** high. **Affected work:** G01.02, G01.05, G03.02.

The Pack formula omits grouping around quantified clauses and the reference-resolution disjunction. ValidationScopeDeclared(V) can be read as part of only the DeclaredGap branch. ExactlyOne(delta(c) in D) has no specified typed interpretation. Existing language checks accept supplied distinction rationales and reject normalized textual collisions; they are not semantic equivalence or full-consistency proofs.

**Risk:** A structurally valid Definition could receive conflicting formal interpretations or a stronger non-collapse claim than its evidence supports.

**Recommended amendment:**

- Group every quantified clause; declare delta:C->D and matching payloads explicitly, with validation scope outside the disjunction.
- Bind each required predicate/signature to an operational or selected formal interpretation.
- Declare the assurance claim class and coverage: structural, finite interpreted model, owner fidelity review, or stronger supported proof. Do not rename a lexical/rationale check as formal non-collapse.

**Evidence:**

- [define/proposals/0002-semantic-foundation-and-integration-plan/definitions/definition-pack/definition.json](../0002-semantic-foundation-and-integration-plan/definitions/definition-pack/definition.json) — /voices/scientific_formal/formal_expression.
- [implementation/define-cli/v1/src/language-quality.mjs](../../../implementation/define-cli/v1/src/language-quality.mjs) — evaluateNonCollapse, lines 71-110.

**Future verification:**

- Counterexamples: all references resolved with validation scope absent; unresolved reference without a declared gap; two differently worded statements with the same meaning.
- Check interpretation against all three voices and declared neighboring/current definitions; record unsupported source clauses.

<a id="r02"></a>
### R02 — Key possession is not yet bound to the semantic principal

**Priority:** critical. **Affected work:** G07.01, G07.02, G07.07, G07.08.

A local store accepts an explicit owner_ref and public key; signature verification proves that configured key signed the local envelope. The work map requests role/principal/assignment evidence but does not specify who establishes the trusted key-to-principal binding. Durable actor access and user confirmation are caller declarations.

**Risk:** A matching owner label and valid local signature could be mistaken for an actual semantic-owner determination when new authorization code is added.

**Recommended amendment:**

- Select an explicit trust root: the existing exact human owner-decision route, or a separately admitted principal/key enrollment or delegation binding.
- Keep operator key, semantic principal, owner role, assignment and decision source independently represented.
- Treat actor_ref, allowed_effects and user_confirmed as declarations unless their authentication basis is established. Do not create an authentication service merely to fill these fields.

**Evidence:**

- [implementation/lab-runtime/v2/lab_runtime/store.py](../../../implementation/lab-runtime/v2/lab_runtime/store.py) — Store.initialize, lines 76-94; verify_approval, lines 42-51.
- [implementation/define-cli/v1/src/durable-session-runtime.mjs](../../../implementation/define-cli/v1/src/durable-session-runtime.mjs) — authorize(command), lines 75-80.

**Future verification:**

- A valid local key with a copied definition-owner label is rejected for semantic promotion.
- Unbound, rotated or revoked keys cannot make new effects; historical approved effects retain their exact recorded basis.

<a id="r03"></a>
### R03 — Source parsing can use different bytes from the recorded digest

**Priority:** critical. **Affected work:** G01.01, G07.02, G09.02.

Capture.read hashes f.read_bytes(), then JSON loading reopens the path. Final freshness checks current bytes, but the parsed document was not necessarily parsed from the hashed byte buffer. A transient A -> B -> A change can evade a later A-byte comparison.

**Risk:** The successor may bind a source digest to document content it did not actually hash. This is a static race possibility, not a reproduced exploit or claim about current admitted data.

**Recommended amendment:**

- Strictly decode/parse the exact byte buffer that was hashed; reject duplicate keys and nonfinite values from that buffer.
- Read immutable selected epoch material or pin one snapshot/descriptor for the capture.
- Carry parsed-content and file-byte identity consistently through source/reference validation.

**Evidence:**

- [implementation/lab-runtime/v2/lab_runtime/sources.py](../../../implementation/lab-runtime/v2/lab_runtime/sources.py) — Capture.read, lines 82-92; final freshness in capture, lines 294-301.
- [implementation/lab-runtime/v2/lab_runtime/common.py](../../../implementation/lab-runtime/v2/lab_runtime/common.py) — load(path), lines 31-42.

**Future verification:**

- Planned controlled writer-interleaving case checks that parsed content always corresponds to the captured digest.
- Persistent and transient source changes must cause a clean retry/failure or remain outside the pinned immutable snapshot.

<a id="r04"></a>
### R04 — Repository publication has no chosen coherent commit boundary

**Priority:** critical. **Affected work:** G08.06, G09.02, G09.05, G10.06.

The local runtime stages a transaction then atomically advances one HEAD. The plan extends this to repository registry, index, drift, profiles, current lookup and Project State, but does not choose how readers observe those multiple files as one committed epoch. A store lock does not lock arbitrary repository edits.

**Risk:** Readers may see mixed epochs or fail during cutover; crash recovery could leave authorized records and current lookup inconsistent. Rechecking sources immediately before commit does not prevent a later external write.

**Recommended amendment:**

- Choose a concrete repository publication protocol: immutable epoch directory plus one accepted selection pointer, or another explicit staged/CAS protocol with a recoverable single visibility boundary.
- Specify lock/CAS coverage, immutable preimages, reader snapshot selection and external-edit detection.
- Keep schema/code/profile selection compatible throughout publication; do not describe independent per-file replacement as whole-repository atomicity.

**Evidence:**

- [implementation/lab-runtime/v2/lab_runtime/store.py](../../../implementation/lab-runtime/v2/lab_runtime/store.py) — Store.apply, lines 221-254.
- [implementation/lab-runtime/v2/lab_runtime/common.py](../../../implementation/lab-runtime/v2/lab_runtime/common.py) — atomic(path,data).
- [define/proposals/0003-integration-work-map/steps/g08.md](../0003-integration-work-map/steps/g08.md) — G08.06.

**Future verification:**

- Planned reader-during-cutover, competing writer, stale preimage and crash-at-each-publication-step cases.
- After recovery, readers see a complete old or complete new selected epoch, or an explicit unavailable state; no mixed state is labeled current.

<a id="r05"></a>
### R05 — The future source epoch depends on records not yet created

**Priority:** high. **Affected work:** G01.06, G08.03, G09.02, G10.05.

G09.02 prepares an exact successor reader/profile before the later decision. That epoch includes post-approval authorization, history and state material. Actual signature/timestamp-dependent bytes do not exist during early preparation. The task graph is acyclic, but these content dependencies are not specified.

**Risk:** A prospective profile may contain unresolved hashes, use fixture hashes as real outcomes, or require its own future authorization digest. No actual digest cycle is asserted; the design must rule one out.

**Recommended amendment:**

- Separate the manifest of immutable reviewed inputs from declared generated consequences and observed application receipts.
- Authorize exact inputs, selected effects, deterministic generator/version and preconditions; identify legitimately post-decision fields explicitly.
- Describe when final source-profile/selection bytes are materialized and how their authority derives, without a self-referential digest or second implicit approval.

**Evidence:**

- [define/proposals/0003-integration-work-map/work-items.json](../0003-integration-work-map/work-items.json) — G09.02 precedes G10.05.
- [implementation/lab-runtime/v2/lab_runtime/sources.py](../../../implementation/lab-runtime/v2/lab_runtime/sources.py) — capture: exact bundle/state/authorization selections.
- [implementation/lab-runtime/v2/lab_runtime/operations.py](../../../implementation/lab-runtime/v2/lab_runtime/operations.py) — consequences: authorization_sha256, governance records and history.

**Future verification:**

- Fixture-dependent, predicted and observed digests cannot be substituted for each other.
- A content-dependency graph distinguishes reviewed inputs, decision evidence and generated outputs; no output must hash itself.

<a id="r06"></a>
### R06 — Cross-runtime parsing and hash rules remain unspecified

**Priority:** high. **Affected work:** G04.01, G04.02, G07.07, G08.02.

Node uses JSON.stringify of sorted-key objects; Python uses json.dumps with its own number formatting and strict persisted-file loading. The CLI reads JSON with JSON.parse, which does not retain duplicate key occurrences. Current authority signatures are Python-owned; the proposed cross-runtime evidence/core protocol has no explicit serialization ownership.

**Risk:** The same conceptual record can have different semantic digests, and duplicate-key input can be interpreted differently from the text a reviewer saw. This is a protocol risk, not a reproduced failure of current string-only context epochs.

**Recommended amendment:**

- Choose one normative serialization/digest owner, or a fully specified shared serialization with numeric/string restrictions.
- Distinguish raw-file hashes from normalized record digests and signature bytes.
- Require strict duplicate-key rejection at external boundaries before JSON.parse discards duplicates; define allowed number precision and normalization explicitly.

**Evidence:**

- [implementation/define-cli/v1/src/canonical.mjs](../../../implementation/define-cli/v1/src/canonical.mjs) — canonicalJson/digest, lines 3-17.
- [implementation/lab-runtime/v2/lab_runtime/common.py](../../../implementation/lab-runtime/v2/lab_runtime/common.py) — encoded/digest/load, lines 19-42.
- [implementation/define-cli/v1/src/lab-cli.mjs](../../../implementation/define-cli/v1/src/lab-cli.mjs) — JSON.parse proposal input, line 67.

**Future verification:**

- Planned cross-runtime cases: 1 versus 1.0, exponent forms, negative zero, unsafe integers, Unicode and numeric-looking keys.
- Duplicate keys and unsupported nonfinite/precision values fail before review; source text and normalized content remain traceable.

<a id="r07"></a>
### R07 — Verification can precede a required binding and late documentation

**Priority:** high. **Affected work:** G02.05, G05.06, G10.01, G10.02, G10.04, G10.05.

The exact CLI realization binding G02.05 is not a dependency or ancestor of the verification matrix or frozen prototype verification. Documentation is prepared after prototype verification, and there is no explicit check of the final documentation/adoption closure.

**Risk:** Tests can be recorded for a candidate that lacks its claimed realization binding; late docs may describe unverified commands or mismatched scope.

**Recommended amendment:**

- Add G02.05 as a dependency of G10.01.
- Add a final documentation/adoption-closure check after G10.04 and before G10.05.
- Bind every verification result to its input manifest; a later code, contract or behavior change reopens the relevant verification and invalidates affected decisions.

**Evidence:**

- [define/proposals/0003-integration-work-map/work-items.json](../0003-integration-work-map/work-items.json) — G10.01/G10.02 do not depend on G02.05; G10.04 follows G10.02.

**Future verification:**

- Prototype verification cannot be ready while the realization binding is pending.
- Exact documented CLI commands, relative links and stated behavior are checked on final selected bytes.

<a id="r08"></a>
### R08 — A completed decision task does not mean its outcome permits continuation

**Priority:** high. **Affected work:** G10.03, G10.05, G10.06, G06.05.

The DAG describes prerequisites and pending statuses, but no transition predicates. G10.03 finishes when any owner outcome is recorded, including rejection. The work map calls for rebuilding closure after partial selections but does not define explicit revise/defer/reject branches or approval invalidation after changed bytes.

**Risk:** An executor could treat recorded rejection as a satisfied prerequisite, or reuse old evidence after a revision. There is no such executor behavior claimed today.

**Recommended amendment:**

- Add explicit guards for qualifying Product approval and each independent owner effect.
- Define revise -> new candidate epoch -> impacted verification -> new decision; defer/reject stop only the dependent branch.
- Compute accepted-subset dependency closure and require an exact newly reviewable bundle when target membership or bytes change.

**Evidence:**

- [define/proposals/0003-integration-work-map/work-items.json](../0003-integration-work-map/work-items.json) — G10.03 completion includes approve/revise/defer/reject; G10.05 depends on task completion.

**Future verification:**

- Rejected/deferred Product or semantic outcomes never reach their dependent apply effect.
- Partial selection preserves unselected targets; changed-byte requests cannot reuse an old decision/core/bundle.

<a id="r09"></a>
### R09 — Legacy compile and durable-session consumers need explicit adapters

**Priority:** high. **Affected work:** G04.01, G04.03, G04.05, G05.01, G10.01.

The active pack validator accepts only the legacy pack discriminator. Alch handoff requires no open questions and lowers every disposition. Session/store discriminators remain v1. The map proposes versioning and partial/use-specific readiness, but does not enumerate these consumers as a concrete compatibility matrix.

**Risk:** A new pack may validate for preparation yet be rejected or misinterpreted by compile/resume. Relaxing a global ready flag could accidentally allow unsupported compile input.

**Recommended amendment:**

- Choose an explicit supported route for every consumer: legacy preservation, versioned adapter, or visible unsupported result.
- Retain compile-specific readiness unless an exact selected subset and compiler contract support it.
- Specify identity/revision/lineage across conversions and saved session resume; do not coerce a new schema label to an old one.

**Evidence:**

- [implementation/define-cli/v1/src/session-runtime.mjs](../../../implementation/define-cli/v1/src/session-runtime.mjs) — validateDefinitionPack, lines 83-110.
- [implementation/define-cli/v1/src/alch-handoff.mjs](../../../implementation/define-cli/v1/src/alch-handoff.mjs) — evaluateDefinitionPackAlchHandoff, lines 84-105; renderDefinitionPackAlch.
- [implementation/define-cli/v1/src/durable-session-runtime.mjs](../../../implementation/define-cli/v1/src/durable-session-runtime.mjs) — session/store/command v1 discriminators.

**Future verification:**

- Planned old/new pack x prepare/compile/resume compatibility cases.
- Open questions may be reviewable while unsupported compilation remains blocked; numeric/boolean Calculation regressions still run on the selected compiler.

<a id="r10"></a>
### R10 — Semantic revision impact is not closed over declared consumers

**Priority:** high. **Affected work:** G01.05, G03.04, G06.03, G07.05, G09.04.

The map compares selected semantic neighbors and requests affected consumers, but does not construct the dependency inventory for a foundational Definition revision or other changed meanings. Existing runtime validation focuses on target records, active typed relations and carrier Definition references; narrative and application consumers are not all covered.

**Risk:** A meaning can be revised while current profiles, carriers, policies, other Definitions or docs retain an incompatible exact meaning. Two terms can remain semantically redundant despite different wording.

**Recommended amendment:**

- Build an exact declared consumer/dependency impact manifest across current Definitions, carriers, profiles, policies, mappings, sessions and documentation.
- For every affected reference select preserve-historical, proven-compatible, update, deprecate, block or explicitly deferred residue with owner.
- Declare the scope of consistency/non-collapse assurance; current-source coverage and known interpretation gaps must remain visible rather than promising whole-repository proof.

**Evidence:**

- [define/proposals/0003-integration-work-map/work-items.json](../0003-integration-work-map/work-items.json) — G01.05/G03.04/G06.03.
- [implementation/lab-runtime/v2/lab_runtime/operations.py](../../../implementation/lab-runtime/v2/lab_runtime/operations.py) — post-staging validation of active relations/carrier Definition references, lines 200-217.
- [authority/definitions/registry.json](../../../authority/definitions/registry.json) — current_lookup and entries.

**Future verification:**

- An incompatible declared dependent blocks current promotion/adoption until repaired or explicitly governed.
- A preserved historical binding stays exact; it is not silently rewritten to the new current version.

<a id="r11"></a>
### R11 — Pack and assurance work has no declared resource bounds

**Priority:** medium. **Affected work:** G04.01, G04.05, G05.05, G10.01.

Chat limits some arrays and context has an inline budget, but the new scripted pack/supplement/reference graph and semantic impact work have no selected limits. Pair checking grows with the number of terms; recursive references and saved session history add separate costs.

**Risk:** Large input may consume excessive memory or time, or be truncated in a way that hides incomplete semantic coverage.

**Recommended amendment:**

- Declare file/output bytes, concept count, reference depth, pair-check budget, history size and timeout limits for the intended release.
- Use explicit batches and residue/continuation records when the full declared set exceeds a bound.
- Never report full required-concept coverage after silent truncation.

**Evidence:**

- [implementation/define-cli/v1/src/language-quality.mjs](../../../implementation/define-cli/v1/src/language-quality.mjs) — expectedPairs/evaluateNonCollapse.
- [implementation/define-cli/v1/schemas/define-conversation-turn.schema.json](../../../implementation/define-cli/v1/schemas/define-conversation-turn.schema.json) — chat language arrays maxItems=24.
- [implementation/define-cli/v1/src/lab-cli.mjs](../../../implementation/define-cli/v1/src/lab-cli.mjs) — script/proposal file reads.
- [define/proposals/0003-integration-work-map/steps/g04.md](../0003-integration-work-map/steps/g04.md) — new closed pack and supplemental contracts.

**Future verification:**

- Boundary and over-limit inputs produce clear bounded outcomes.
- Batch recomposition preserves full declared required-set identity and unresolved residue.

<a id="r12"></a>
### R12 — The first useful preview is tied to the entire authority implementation

**Priority:** medium. **Affected work:** G05.03, G05.06, G07.08, G08.06, G09.06.

The full candidate freeze waits for independent governance records, transaction compatibility and refreshed views. The map lacks a separate bounded frozen preview milestone, although complete non-mutating candidate preparation could be reviewed earlier.

**Risk:** Sixty-seven items can become a single large change before users inspect real output, increasing feedback cost and the risk of unnecessary generic runtime work.

**Recommended amendment:**

- Declare three delivery milestones: read-only preparation preview; guarded exact review; authorized application with epoch/view refresh.
- Freeze each candidate surface separately with exact limitations; keep the single final admission scope reviewable if that remains the selected interaction model.
- Constrain the first writer/adapter to this Definition integration and defer general admission-platform work unless a concrete target requires it.

**Evidence:**

- [define/proposals/0003-integration-work-map/work-items.json](../0003-integration-work-map/work-items.json) — G05.06 freeze depends on governance, transaction and context completion.

**Future verification:**

- The preview can be demonstrated without signing, stores, repository mutation or new authority.
- Every milestone has a bounded accepted/deferred scope; partial delivery is never reported as full integration.

## Example of the largest authority risk

An operator provisions a local key and calls itself `role:definition-owner`. A valid signature proves that this configured key signed the local proposal. It does not prove that the human owning the Definition authorized that key or selected this semantic effect. The new integration must resolve that distinction through exact human decision evidence or an admitted principal/key binding before it can promote a Definition.

## What the audit does not add

The findings do not establish a need for more root Definitions. First tighten the two drafts and reuse the existing Authority Boundary, Role Assignment, Principal/Decision, Source, Schema Evolution and Admission Transaction meanings. Principal/key enrollment, interpretation, publication and compatibility rules can be expressed as bounded contracts and exact owner decisions. A new subsystem or Artifact Type needs its own demonstrated consumer requirement.

## Recommended amendments and order

1. Fix the Pack expression and selected assurance interpretation; prepare the declared semantic-consumer impact map.
2. Select semantic-owner trust evidence, exact-byte source parsing and canonical digest ownership.
3. Specify the publication boundary and the distinction between reviewed inputs, decision evidence and generated epoch outputs.
4. Repair verification dependencies, outcome guards and legacy consumer compatibility.
5. Add bounded preview/review/application milestones and input budgets.

The [machine-readable amendment proposal](proposed-plan-amendments.json) adds 12 obligations to the original 67 and previews an acyclic 79-item graph. It **does not modify** the existing work map. These obligations may be merged into its existing tasks when their contracts and finish criteria are made explicit; 79 items is not a required implementation size.

## Existing risks already mapped

The audit does not count the known v1/v2 profile mismatch, nested scope checks, independent owner boundaries, specialized Method Binding carrier, missing Definition challenge subject or old source epoch as newly discovered gaps. Those remain open tasks in 0003. This audit narrows their required mechanisms and exposes missing dependency/acceptance details.

## Claim limits

Planning checks verify source hashes, relative links and the proposed dependency graph. No runtime tests, race simulation, key enrollment, live-store changes, code fixes, full-definition formal assurance or admission were performed. See [findings.json](findings.json), [source-selection.json](source-selection.json) and [planning-checks.json](planning-checks.json).
