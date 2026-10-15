Constitution has a reproducible partial formalization of its genus, declared tuple, qualified adoption, scoped application, rule modes and separation from eight other roles. The checks expose several unresolved source-to-model and source-to-carrier mappings. No Constitution instance has been adopted, activated or granted authority by this work. Source-owner acceptance and a whole-definition proof remain pending.

This review explains the candidate's formal aspects and the evidence supporting each. Its review disposition is agent self-review, not an independent or source-owner verdict. The episode remains active: 38 of 183 current definition identities have partial interpretation drafts; 145 have no draft. There are 189 admitted source versions, zero source-owner-accepted whole translations and zero whole-definition proofs. The next definition priority is Contestability Policy. See [episode status](episode-status.json), [current inventory](current-inventory.json) and [receipt](receipt.json).

**Source identity, admission and currentness.** The primary source is exactly `cal.definition.constitution@1.0.0-candidate.1`, with SHA-256 `ed01aeb7e83336774412a31bb3798fb3650377874e135e84036771af9ecf434b`. It is a normalized Definition artifact admitted by `CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION`. Its historical internal candidate wording remains visible; that wording and the current registry admission are different observations. Admission of the source does not accept this interpretation.

The recorded source-use admission `CAL-SOURCE-FULL-DEFINITION-QUEUE-047` selects only `## CAV2-D58: Constitution` for this exact Definition version. The selected local Definitions file matches the full-file hash recorded at admission. The bound extractor selects a 4,419-byte D58 section with SHA-256 `19b1102f8a412f59fe7ec9e30ac474898ba662d117495f02e7b7a2110096a135`. Two independent executions of the bound pure Markdown generator produce the same 8,078-byte projection, hash `e00ac96bc2e85aceec48ff70896754ed0fef5401e133bf193228c7f96dc2210c`. Sixteen source checks pass. The declared producer path is absent, and repository identity/currentness at that producer is unauthenticated. These are exact selected-byte and recorded-admission checks, not authenticated live producer verification. See [source evidence](source-checks.json), [selected section](legacy-source-section.md) and [render](source-render-1.md).

**Definition forms and full clause accounting.** The source inventory contains 22 nonempty string units in its voices, boundaries, scope and claim ceiling. All characters in those units are accounted for across 38 spans: nine encoded, nine explanatory and 20 deferred. Complete accounting means that no inventoried source text was silently discarded. It does not mean that all text was translated into logic. Plain-language, domain-context and notation material stays explanatory; unresolved operational boundaries and source-precedence questions stay deferred.

The nine encoded spans consist of one genus-differentia span, six axiomatic-implicit spans and two spans with both axiomatic-implicit and operational forms. All nine carry the definition role. The prose declaration and printed tuple repeat one formal statement; the two source boundary passages repeat role noncollapse. Consequently the nine source spans contain seven distinct formal statements. The adoption/necessary-application span conjoins two primitive formulas, so the implementation contains eight primitive formulas. Counting spans, distinct statements and primitive formulas separately prevents duplicated source wording from inflating logical coverage. See [correspondence](correspondence.json), [accounting check](correspondence-check.json), [clause analysis](clause-analysis.json) and [denominators](denominator.json).

**Types, symbols and identity.** The interpretation uses many-sorted first-order logic with equality. Its 75 declarations are five nonempty sorts, 26 constants, three total functions, 31 unary predicates and ten relations. The sorts are `Entity`, `Token`, `Field`, `SubjectKind` and `ValidationMode`. Every symbol is qualified by the exact source version and this candidate's scope; identical names in another interpretation do not automatically share meaning.

`fieldValue : Entity × Field → Token` supplies abstract field values. `validationModeValue : Entity → ValidationMode` supplies a rule's mode. `actualSubjectKindValue : Entity → SubjectKind` is available for countermodel questions but is not linked to scope or selector matching by the encoded source theory. Totality means every correctly typed argument tuple has exactly one result. It does not authenticate a referenced owner, create a real record or identify a Constitution by its field values.

The constants name 15 fields, six subject kinds, four modes and an `EMPTY` Token. The theory does not add a unique-names axiom. Different constant names may denote the same value unless explicitly distinguished. Supplied positive models expose aliasing of field values, subject-kind constants and mode constants. A positive model also contains distinct Constitutions with identical field values. No implicit extensional identity rule is introduced. See [interpretation](t.json), [typed IR](static-ir.json) and [model controls](model-controls.json).

**Genus and differentiae.** For every entity `c`, the candidate states:

```text
Constitution(c) ↔
  OwnerScopedAuthorityArtifact(c) ∧ SelectorBound(c) ∧
  ComposableArtifact(c) ∧ TurnsAxiomsInvariantsIntoRulesPolicies(c) ∧
  NamedGovernedSubjectKinds(c)
```

This represents the source's genus and qualifying properties as an equivalence. Removing any qualifying property from a supplied Constitution violates the theory; giving all properties without the Constitution predicate also violates it. These predicates are candidate denotations, not verified real-world properties. Source-owner review must accept the equivalence and its denotation. Raw field completeness alone does not satisfy the genus.

**Declared tuple and structured data.** A Constitution must declare a non-`EMPTY` abstract value for each of the following fields:

```text
id, version, scope, subject_kinds, selectors, rules, policies,
precedence, composition, owner_route, authority_level,
validation_bindings, downstream_effect, challenge_route,
retirement_or_split_rule
```

Both source declaration passages use this same candidate constraint. Non-`EMPTY` Tokens are weaker than structured lists, resolved references, valid version identities, a qualified owner route or an executable precedence policy. The theory also permits extra declared fields; requiring these 15 fields does not impose a closed record schema. Missing-field and empty-value controls cover each of the 15 required fields independently.

**Subject-kind vocabulary.** Declared subject kinds for a Constitution must fall among artifact, task/workflow, repository-owned agent action, system operation/state transition, validation surface and authority movement. This is a guarded restriction on `DeclaredSubjectKind`, not a global restriction on every entity or kind. It does not establish that all six denotations differ or that each category is populated.

A supplied model satisfies the theory while a subject of an undeclared kind applies through independently supplied scope/selector relations. This exposes the missing accepted map from actual subject kind to declared kinds and selector semantics. The six conceptual source categories also differ from the current global Relation Kind endpoint vocabulary. No conversion between those axes is assumed.

**Exact owner adoption and application logic.** The candidate expands the adoption marker into a qualified relation:

```text
ExactAdoption(c) := ∃d.
  DecisionRole(d) ∧ OwnerAuthorizedAdoption(d,c) ∧
  OwnerAdoptsExact(d,c,fieldValue(c,F_version),fieldValue(c,F_scope))

Constitution(c) → (VersionExactOwnerAdoption(c) ↔ ExactAdoption(c))
```

The prose says that application requires exact owner adoption, scope membership and matching selectors. The printed expression further gives a biconditional:

```text
Constitution(c) →
  (Applies(c,s) ↔ Promoted(c) ∧ VersionExactOwnerAdoption(c) ∧
                  InScope(c,s) ∧ SelectorMatches(c,s))
```

Both the prose's necessary condition and the printed biconditional are retained, with source precedence unresolved. The biconditional asserts sufficiency within this candidate theory as well as necessity. Omitting the application relation when all four conditions hold therefore violates the theory. Merely copying an owner-adoption record does not establish qualification: a Decision role, authorization marker and exact version/scope values must also match. Another version or scope cannot substitute in the supplied controls.

The owner-route field is still an opaque Token; it is not connected to an authenticated owner/principal denotation. Promotion, authorization, scope membership and selector matching are supplied predicates, not actual service outcomes. Coherent revocation and unpromotion models cease to apply, but those finite examples do not establish a universal temporal revocation mechanism.

**Selection, loading and promotion.** Candidate, selected and context-loaded labels do not independently entail application. Separate countermodels establish these nonentailments outside the primary theory. They are not prohibitions against application: a Constitution carrying one of those labels can also apply when separately promoted, adopted and matched. Definition-term promotion is distinct from promotion/adoption of a Constitution instance. The required populations include a term-promoted but unpromoted instance.

**Rule modes and actual validation.** Every rule associated with a Constitution must have the `Rule` role and one of deterministic, review, hybrid or none-yet as its mode value. Removing the role or supplying an unlisted mode violates the guarded constraint. Unrelated entities remain outside that guard.

A none-yet rule may belong to an applicable Constitution without an active validation binding. A mode label does not execute a validator, produce evidence or establish proof. Deterministic and review modes also need accepted bindings, procedures and completion evidence before any real validation claim can follow. Four named mode constants are not independently proven four distinct denotations. The finite profile checker adds an explicit hypothesis that a none-yet binding is disabled; that additional hypothesis is not silently imported into the primary theory.

**Role separation and grounding.** A Constitution cannot simultaneously bear the candidate roles Axiom, Invariant, Discipline, Decision, Validator, Gate, Evidence or Proof. Each collapse has a negative model control. This is local role separation; it does not reconstruct a shared ontology or authenticate all real-world classifications. Axioms and invariants ground rules, disciplines can steward or propose practices, Decisions can adopt, validators can check and evidence can support. Those relations and action permissions require accepted cross-definition maps; the Constitution is not given their authority merely by mentioning them.

**Precedence, composition, effect and retirement.** The tuple declares these fields without implementing their semantics. The source's discussion of system, developer, host and external-owner boundaries remains explanatory/deferred. No global hierarchy, composition algorithm, amendment route, split policy or history semantics has been proven. Application may coexist with no actual subject effect. Independently supplied actual-authority, admission, truth, proof, owner-acceptance, runtime, external-effect, universal-enforcement and higher-precedence-override predicates do not turn those outcomes into theorems. Their model/query results are about candidate entailment only.

**Nonvacuity and unresolved populations.** Eleven required existential populations make the interpretation's intended examples explicit: a Constitution; raw declared fields without one; distinct same-valued Constitutions; exact applicable adoption; selected/loaded candidate without application; raw adoption without authorization; scope without selector match; applicable none-yet rule without active binding; application without actual effect; selected named subject kinds; and term promotion without instance promotion. Forty other population obligations remain unresolved, with no fabricated exemptions or owner review references.

Theory satisfaction `T` and required-population satisfaction `I` are checked independently. A universal rule is not justified by finding one convenient witness; an existential witness does not repair a universal violation. Required populations are authored proof obligations, not observed populations of actual operating systems.

**Finite semantic evidence.** There are 98 controls: 91 well-formed supplied models, of which 31 satisfy the theory and 60 violate it as expected, plus seven malformed models rejected for totality, sort, arity, duplicate tuple or domain faults. The models preserve the original finite evaluator limits; no budget increase or denominator reduction was used to obtain a pass. Twenty-one queries remain explicitly outside `T`, each with a retained finite countermodel, digest, false target and true witness condition. These are counterexamples to selected entailment claims, not a mechanized whole-definition proof. Each supplied model is independently evaluated; there is no claim that separate models share one real-world denotation. See [model evidence](model-controls.json), [query policy](query-policy.json) and [model checker](verify_candidate.py).

**Stronger application hypotheses and finite histories.** The separate profile checker tests 61 hypothetical contexts, rejecting 17, and 19 history frames, rejecting 13. A qualified context carries 17 matching axes: Constitution, version, scope, subject, subject kind, selector, owner, owner route, authority level, precedence, composition, rule, mode, validation binding, downstream effect, challenge route and retirement rule. Eleven support axes cover genus/tuple mapping, exact identity, scope/selector/kind mapping, owner authentication, adoption, promotion, precedence/composition, mode/binding, effects, retirement and source fidelity.

These support values are labelled hypotheses. They do not authenticate a person, adopted instance or validation result. The stronger profile additionally checks a higher-precedence block and exact adoption context. Missing support, mismatched axes and attempted actual-world claims are rejected. Select/load/render/mode-declaration frames preserve identity/version/scope/tuple/history; application and retirement frames require their stated hypotheses. Finite frames prove no universal temporal property and perform no runtime transition. See [profile and carrier evidence](authority-profile-checks.json).

**Documentary schema and historical candidate instance.** The selected D58 documentary schema row lists the 15 tuple fields. A tracked documentary row does not activate a machine validator. The separately selected Stable Repository Constitution remains historical candidate context: 17 numbered rule headings, eight review modes and nine hybrid modes, with no explicit exact instance-version header recorded. The selected rule IDs are C1–C15, C17 and C18; no broader inference about the absent heading is made. Its rules and embedded runtime instructions are not imported or executed. No complete instance-schema validation, owner adoption or rule validation is claimed. See [schema row](legacy-schema-row-context.md), [candidate instance context](legacy-candidate-constitution-context.md) and [historical Model context](legacy-model-context.md).

**Dedicated current carrier and unresolved mapping.** The current `cal.artifact-type.constitution/v1` is directly bound to the exact admitted Definition source. That binding is stronger evidence of intended association than a name resemblance; it still does not establish semantic fidelity. Its required payload has `governed_scope_ref`, `rule_refs`, `invariant_refs` and `amendment_policy_ref`. Rule and invariant arrays require nonempty unique items. Other root fields provide record identity, owner and challenge references.

| Source tuple field | Possible current record locator | Mapping status |
| --- | --- | --- |
| id | node_id | Unaccepted identity map |
| scope | payload.governed_scope_ref | Unaccepted scope map |
| rules | payload.rule_refs | Unaccepted rule-reference map |
| owner_route | owner_ref | Unaccepted owner-route/reference map |
| challenge_route | challenge_route | Unaccepted route map |
| version, subject_kinds, selectors, policies, precedence, composition, authority_level, validation_bindings, downstream_effect, retirement_or_split_rule | No direct named locator among the selected record fields | Unresolved |

The selected fixture's root scope and governed scope have different literals. No accepted equivalence is supplied. It has no exact instance-version field. An amendment-policy reference cannot silently stand for all policies, and `authority_effect: none` cannot silently implement the source's downstream-effect field. Thirteen dedicated schema probes reject eight malformed/extra-field variants while accepting five unresolved-reference or missing-adoption variants. Schema acceptance therefore does not resolve the owner, scope, rule, invariant or policy, or establish application.

Across seven related carriers, 29 hostile fixtures are rejected. Twenty related probes accept five unresolved-reference shapes; 20 lifecycle probes accept all selected labels without proving posture grants. Five pure endpoint generators and associated schema/root bytes are checked for selected deterministic projections. Declared receipt-writing validators are not executed. The admitted historical generic Definition v1 source fails the current generic Definition v2 schema at four bindings: artifact type reference, schema reference, schema version and generator reference. The source is not migrated or its admission invalidated to conceal that mismatch. The wrapper type, generic Definition classification, authority-kind labels and Constitution instance kind remain separate axes.

**Relation role and endpoint consistency.** The embedded Constitution carrier's independent enum fields accept all 16 combinations tested over its two relation kinds, two directions and four counterpart kinds, although only five combinations are declared carrier roles. Eleven accepted combinations therefore fall outside its own role declarations. This is a shape-versus-role closure gap, not proof that actual relations exist.

The current Relation Kind catalog has six Constitution endpoint roles. Five match carrier declarations; the sixth is incoming `relation.challenges` from a Challenge Event. The carrier rejects that embedded record, while the generic current Typed Relation v3 schema accepts the corresponding global relation shape with unresolved references and qualifiers. The two actual schema observations are retained together. No challenge has actually been qualified or created.

The broader selected `relation.governed-by` comparison also retains 29 current Kind pairs versus 23 current Typed Relation schema pairs, with six policy-target pairs missing from the latter. Successor-of has 100 pairs on both selected surfaces. Thirty concrete pair probes accept 24 and reject six. Matching pair counts do not establish semantic adoption or valid succession. The three kinds that can currently be governed by a Constitution on that relation are artifact-type, definition and relation-kind; those are not identified with the source's six conceptual governed-subject categories. The selected catalog checks report no missing axiom/invariant/rule semantic kinds, without making a universal repository claim.

**Dependency closure and the execution DAG.** Constitution declares 36 independently reviewable semantic uses and ten separately qualified comparison sources. Their packets are not assembled into the primary theory, and no meaning alignment is presumed from namespace compatibility. The current declared graph contains 93 nodes, 686 edges and 55 missing or quarantined counterpart interpretations. Its 38-member component contains 429 internal edges and has unresolved cycle classification. That semantic graph is not an acyclic execution plan; no least fixed point, recursive semantics or shared-model consistency is assumed. See [dependencies](dependency-graph.json) and [comparison selection](comparison-selection.json).

The existing foundations-first plan remains the detailed execution DAG: 121 tasks, 511 prerequisite edges, 797 small work units and 36 frontiers. Definition forms, type/logic foundations and per-definition translations remain ahead of downstream implementation. The first frontier sequence is M01 → {M02, M03} → M04 → M05 → M06 → M07 → M08 → M09. This work executes only `F02-T.cal.definition.constitution`, whose actual prerequisite receipts A04, C01 and E02 pass their bounded software/source-capture criteria. Their success does not substitute for source-owner meaning approval. Family completion still needs every required translation and its review obligations. The former I04 report retains its exact eight-draft selection; this unit's 38-draft inventory is a distinct current report.

**Failure retention, reproducibility and preservation.** The first carrier-profile attempt exited with code 1 because it expected the five carrier roles to equal six current Kind roles. Its checker, stdout, stderr and hashes are retained in [attempt 001](attempts/001-carrier-current-kind-role-subset/attempt.json). Recovery changed the observation to an explicit subset and retained the paired embedded/global challenge checks. Neither the primary interpretation nor canonical contracts changed.

The first final-audit execution also exited with code 1 before creating seal outputs. Its assertion expected the selected semantic-kind absence result as a list; the actual report groups empty lists under axiom, invariant and rule. [Attempt 002](attempts/002-final-audit-catalog-absence-container/attempt.json) retains the failed finalizer, its exact terminal error-line excerpt and the primary-theory digest. The assertion now checks that grouped result. The source, interpretation, profile evidence and six replay results remain unchanged. The retained terminal text is an excerpt, not a complete stdout/stderr transcript.

Six fresh read-only commands check the interpretation contract, finite models, source, profile/carriers, dependencies and current inventory. Their actual argv, exits and output files are retained in [fresh results](fresh-command-results.json). The final seal and read-only delivery audit require all six to exit zero with empty stderr and matching current reports. They recheck 201 captured source files, all 3,270 predecessor candidate files, selected external bytes and input/runtime bindings. The manifest includes the archived failed attempt and all new evidence, excluding Python caches and its own self-reference. See [delivery manifest](delivery-manifest.json) and [coverage row](coverage-row.json).

At this boundary, the whole episode has 871 source units and 1,176 accounted spans: 273 encoded, 317 explanatory and 586 deferred, with 326 required and 991 unresolved population obligations. These totals measure candidate coverage, not accepted formalization. Continuing with Contestability Policy preserves the user's definitions/types/logic priority while source-precedence, carrier fidelity, authenticated adoption and shared meaning decisions remain explicitly open.
