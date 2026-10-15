#!/usr/bin/env python3
"""Author the no-effect detailed candidate plan from exact current sources.

The procedural DAG is not the semantic dependency graph. Family membership is
an editorial work partition. Unknown semantic edges remain a planned closure
obligation, never inferred from labels. This is not an Invoke producer receipt.
"""
from __future__ import annotations
import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[4]
IMPL = "craft/formalization/candidates/definition-assurance-v1"
DATA = "docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1"
PRODUCTS = {
 "A01": [IMPL + "/contracts.py", IMPL + "/schemas/input-envelope.json"],
 "A02": [IMPL + "/resolver.py", DATA + "/current-snapshot.json"],
 "A03": [DATA + "/source-and-formalization-coverage.json"],
 "A04": [IMPL + "/schemas/interpretation.json"],
 "A05": [IMPL + "/relation-policy.py", IMPL + "/profiles/relation-and-population-policy.json"],
 "A06": [IMPL + "/obligations.py", IMPL + "/profiles/obligation-rules.json"],
 "A07": [DATA + "/pilot-v2/interpretation.json"], "A08": [IMPL + "/pilot-v2.py"],
 "A09": [DATA + "/pilot-v2/evidence.json"], "A10": [DATA + "/pilot-v2/fidelity-review.json"],
 "C01": [IMPL + "/ir.py"], "C02": [IMPL + "/semantics.py"], "C03": [IMPL + "/dependencies.py"],
 "P01": [IMPL + "/profiles/selection.json", DATA + "/tooling-assessment.json"],
 "P02": [IMPL + "/providers/finite.py"], "P03": [IMPL + "/providers/smt.py"],
 "P04": [IMPL + "/proofs/evaluator-and-obligation-coverage/"],
 "P05": [IMPL + "/providers/selected-temporal-or-recursive/"],
 "E01": [IMPL + "/schemas/evidence.json"], "E02": [IMPL + "/bundles.py"],
 "E03": [IMPL + "/verifier.py"], "E04": [IMPL + "/tests/hostile-cases.json"],
 "I01": [IMPL + "/invalidation.py"], "I02": [IMPL + "/diff.py"],
 "I03": [IMPL + "/regression.py"], "I04": [IMPL + "/cli.py", IMPL + "/reports.py"],
 "I05": [DATA + "/workflow-rehearsal/"], "G01": [DATA + "/gates/l1.json"],
 "S01": [DATA + "/semantic-dependency-closure.json"], "S02": [DATA + "/neighbour-and-alignment-matrix.json"],
 "G02": [DATA + "/gates/l2.json"], "Z01": [DATA + "/whole-theory.json"],
 "Z02": [DATA + "/whole-theory-sat-and-inhabitation.json"], "Z03": [DATA + "/source-linked-diagnostics.json"],
 "Z04": [DATA + "/universal-obligation-and-assumption-audit.json"],
 "Z05": [DATA + "/whole-snapshot-regression.json"], "Z06": [DATA + "/independent-replay.json"],
 "Z07": [DATA + "/final-coverage-and-gaps.json"], "H01": [DATA + "/owner-review-package/"],
 "H02": [DATA + "/owner-dispositions.json"], "H03": [DATA + "/selected-owner-handoff.json"],
 "H04": [DATA + "/project-closeout.json"],
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


# Exact term sets map all identities with that term into an editorial family.
# Identical terms still produce distinct per-definition units.
GROUPS = [
 ("F01", "Meaning and logical foundations", "Definition|Semantic Primitive|Schema|Axiom|Invariant|Hypothesis|Premise|Governed Model", "Distinguish normative predicates, assumptions and explanatory prose; do not assume the target theorem."),
 ("F02", "Authority, policy and governance", "Authority|Authority Claim|Authority Boundary|Authority Model|Authority Promotion|Authority Surface|Responsibility|Constitution|Policy|Contract|Contestability Policy|Gate|Governance-Axis Independence Invariant|Root-Axis Independence Invariant|Parent-Instance Authority Separation Invariant|Closed Authority-Kind Invariant|Challenge Contract|Challenge Event|Exact Publication Authorization Invariant|Effect", "Claim without a grant; responsibility without permission; wrong scope; explicit coupling; unauthorized move."),
 ("F03", "Lineage, evidence and assessment", "Provenance|Source|Traceability|Evidence|Evidence Set|Review|Evaluation|Validation|Validation Receipt|Conformance|Finding|Measurement Method|Measurement Result|Claim-Support Compatibility Invariant|Interface Claim-Support Compatibility Invariant|Drift Assessment", "Recorded versus unknown provenance; empty trail policy; stale support; evidence without conformance or admission."),
 ("F04", "Artifacts, representations and packages", "Artifact|Artifact Lifetime|Artifact Surface Classification|Artifact Type|Artifact Type Registry|Artifact Type Request|Artifact Type Resolution|Identity Carrier|Semantic Epoch|Representation Revision|Canonical Representation Invariant|Four-Facet Artifact Invariant|Canonical Package Home|Canonical Package Manifest|Derived Refresh|Generated Output|Projection Specification|Schema Evolution Invariant|Withdrawal Record", "Semantic successor versus representation revision; ambiguous resolution; generated view versus source authority; unique surface assignment."),
 ("F05", "Identity, participants and classification", "Actor|Person|Person Reference|Principal|Principal Reference|Team|Team Membership|Role|Role Assignment|Identity Claim|Identity Relation|Identity Lineage|Classification|Classification Assignment|Classification Axis|Classification Scheme|Classification Value|Classification Orthogonality Invariant", "Reference versus referent; membership without role or rights; classification without identity equivalence; legitimate subtype overlap."),
 ("F06", "Contexts and ontology", "Context|Context Profile|Context Request|Context View|Context Lineage Record|Context Migration Manifest|Context Map|Bounded Context|Ubiquitous Language|Ontology|Ontology Node|Ontology Edge|Ontology Cut|Ontology View|Ontology Manifest|Model Instance Binding|Semantic Event History|Governance Event History", "Context-local meaning; ontology navigation without promotion; stale cuts and views; explicit model-instance bindings."),
 ("F07", "Typed relations and coupling", "Typed Relation|Relation Kind|Typed Connection Extension Rule|Typed Coupling Invariant|Constraint-Cycle Safety Invariant", "Ordered pairs and qualifiers; distinct semantic questions; prohibited constraining cycles; declared coupling without automatic authorization."),
 ("F08", "Products and coordination", "Craft Method|Method|Goal|Project|Product|Product Capability|Product Thesis|Capability Instance|Capability Realization Binding|Coordination Context|Intent|Intent Resolution|Work|Work Outcome Assessment|Implementation|Project State|Project Governance Event History|Project Semantic Event History|Work-State Continuity Capability", "Method specialization; goal evidence versus achievement decision; Product versus Project; capability versus realization; state versus projection."),
 ("F09", "Construction, residue and experience", "CyberAlchemy Construction Method|Discipline|Experience Evidence Formation Method|Residue|Residue Escalation Method|Residue Measurement|Prototype-First DomainSpec Construction Invariant|Bounded Self-Application Invariant|Govern UX/UI Knowledge", "Prototype before implementation; explicit residue owner and stop; experience without authority; bounded self-application."),
 ("F10", "Decisions, workflows and preferences", "Workflow|Decision|Decision Scope|Decision Bundle|Decision Checkpoint|Decision Request Set|Workflow Decision Profile|User Decision Preference|Admission Transaction|Communication Preference|Preference Application Assessment", "Lab/Craft homonyms; checkpoint without authority; preference cannot widen scope; decision versus executed transaction."),
 ("F11", "Agents, sessions and tools", "Agent|Agent Action|Agent Assignment|Agent Capability|Agent Instance|Agent Profile|Agent Reflection|Agent Session|Delegation|Tool|Session Memory", "Agent subtype of Actor; ability without permission; attempted versus completed action; immutable session attribution; memory without canonical state."),
 ("F12", "Research and operational learning", "Research Inquiry|Research Run|Experiment Design|Experiment Run|Observation|Operational Observation|Operational Learning Cycle|Operational Lesson|Lesson Application|Lesson Outcome Assessment|Feedback Record|Improvement Signal|Improvement Target", "Observation versus interpretation; lesson candidate versus accepted rule; finding versus evidence; predicted versus observed improvement."),
 ("F13", "Failure and incident semantics", "Failure|Failure Assessment|Failure Control Binding|Failure Mode|Failure Occurrence|Incident", "Failure class versus occurrence; incident versus diagnosis; control coverage without prevention proof; required hypothetical populations."),
 ("F14", "Repository, migration and history", "Append-Only Event Ledger|Ledger|CyberAlchemy Repository Identity|Repository Migration Manifest|Source-Ledgered Consolidation|Stable Repository|Stable Repository Stewardship", "Exact migration accounting; permanent lineage; historical versus current state; replay without self-admission."),
]


# ID, layer, D-stage, dependencies, title, ordered implementation rules,
# required acceptance evidence, risk class. These are planned, not executed.
CORE = [
 ("A01","L1","D3",[],"Strict candidate input contracts", "Specify closed interpretation, source, relation, assumption, population and result schemas; reject duplicate JSON keys and unknown fields; route malformed inputs to typed outcomes before semantic evaluation.", "Delete each required key; supply extra fields, duplicate identities and wrong types; all return typed unresolved/malformed records, never a raw traceback or silent pass.","medium"),
 ("A02","L1","D3",["A01"],"Exact source resolver and immutable capture", "Resolve current_lookup to unique exact entries; read and hash bytes once inside an allowed root; bind admission decision references; verify source ID/version; recheck the registry before publication.", "All 183 sources verified; stale hash, replaced lookup, missing file, duplicate version and capture race fail; preserve historical records and all input bytes.","medium"),
 ("A03","L1","D0",["A02"],"Complete source and formalization assessment", "Inventory every selected definition and historical predecessor; distinguish prose, exact bindings and replayed proofs; inspect indirect source mappings as explicit leads; emit one total current queue.", "Exactly 183 current rows and 189 admitted version entries; zero silent omissions; no textual mention counted as proof; source drift gets an explicit status.","medium"),
 ("A04","L1","D1",["A01","A03"],"Interpretation and clause-correspondence contract", "Define typed signatures and canonical statements; map every normative clause, boundary and example to encoded, premise, explanatory, deferred or unresolved; declare explicit semantic dependencies and source precedence.", "Owner sees realistic instance and counterexample; no inherited scaffold paragraph becomes an axiom by default; missing clauses/dependencies cannot count as complete.","high"),
 ("A05","L1","D1",["A04"],"Relation semantics and population policy", "Specify aliases, subtype inclusion/properness, overlap, disjointness and named forbidden inferences; distinguish non-entailment from all-model distinction; assign required or explicitly exempt population obligations per carrier.", "Positive alias, proper subtype and explicit coupling controls pass; false alias, collapsed distinction, empty required population and unaligned carriers remain failed/unresolved.","high"),
 ("A06","L1","D1",["A05"],"Required obligation denominator", "Derive requirements from reviewed relation policy, signature and change class; generate a manifest with exact statements, strength and prerequisites; input submitters cannot shrink the denominator.", "Omitted, substituted or weakened required obligation is rejected; all negative controls are checked against the independently required statement set.","high"),
 ("A07","L1","D2",["A04","A05"],"Pilot semantic successor specification", "Separate owner grants, claims and rights/responsibilities; define empty/unknown/incomplete provenance; bind each move to exact subject before/after states and active grants; document the candidate admission-use coupling.", "Source-backed interpretation alternatives and realistic examples; ungranted claim and unknown origin expressible; move/record mismatch and unrecorded grant changes rejected.","high"),
 ("A08","L1","D2",["A07","A06"],"Isolated successor pilot", "Author v2 candidate in a new absent directory; implement independent record and transition predicates against sealed signatures; retain v1 intact; keep counterexample queries out of the theory.", "Same positive distinction and authorized overlap; additionally claim-without-grant, unrelated subject move and incomplete claim variants are exercised.","high"),
 ("A09","L1","D2",["A08"],"Successor pilot replay and controls", "Run actual satisfiability, inhabitation and distinction queries; independently replay models and all finite configurations; record trust assumptions and exact budgets.", "Collapse, contradiction, vacuity, missing dependency, missing translation, malformed input, stale source, unsupported profile and real cancellation/timeout receive their exact outcomes.","medium"),
 ("A10","L1","D1",["A09"],"Pilot correspondence review", "Present exact candidate clauses, omissions, examples, witnesses and assumptions to semantic owner; record fidelity decisions separately from semantic admission; rejected clauses route to a new candidate iteration.", "Actual attributable owner fidelity review for exact bytes, or explicit pending state; no simulated approval and no canonical source mutation.","human"),
 ("C01","L1","D3",["A04","A05"],"Typed canonical theory IR", "Define closed sorts, variables, predicates, relation applications, equality, Boolean connectives and supported quantifiers; namespace by exact definition/scope; explicit shared-carrier alignment; unsupported constructs stay visible.", "Malformed and ill-sorted statements rejected; equal labels do not merge identities; distinct nominal types do not prove non-collapse; serialize deterministically.","high"),
 ("C02","L1","D3",["C01","A02","A06"],"Independent denotation and evaluator", "Define model satisfaction independently from Boolean acceptance; evaluate each supported AST node under an explicit environment and domain; separate T from queried obligations and populations.", "Hand-derived models, empty domains, alias/subtype/overlap controls and parser correspondence checked; no StaticConforms := checker=true as semantic specification.","high"),
 ("C03","L1","D3",["A04","A02"],"Dependency graph and SCC compiler", "Consume only author-declared uses_definition edges; resolve all transitive refs; compute strongly connected components; retain edge basis; condense to an execution order without erasing normative cycle restrictions.", "Two-node mutual definition SCC accepted for joint analysis; a prohibited constraining cycle separately rejected; unbound edge remains unresolved; reverse closure includes all affected nodes.","high"),
 ("P01","L1","D3",["C01","A05"],"Provider capability and evidence thresholds", "Assess logic requirements before availability; inventory exact installed builds; choose finite/SMT/proof routes and minimum strengths by obligation; isolate any later installs; seal budgets and candidate profile policy.", "No provider selected by labels alone; missing runtime, unsupported logic and weaker-than-required evidence block that obligation; no install is performed by this planning task.","medium"),
 ("P02","L1","D3",["C02","P01"],"Generic finite model provider", "Enumerate the exact finite interpretation rather than the two fixed pilot IDs; stream a first witness and counters; record domain and exhaustion completeness; enforce cancellation and resource limits.", "Two independently derived theories replay; bounded no-witness never claims unbounded separation/consistency; resource exhaustion is unknown; memory bounded by profile.","high"),
 ("P03","L2","D4",["P01","C02"],"Selected SMT provider projection", "If sealed profiles require SMT, lower the supported IR fragment with explicit sort/cardinality rules and preservation map; bind native formula/build/flags; normalize sat, unsat and unknown; otherwise record exact non-applicability.", "Witness replay for sat; exact solver-result ceiling for unsat; unsupported quantifiers and timeout unresolved; nominal sort partition cannot supply a distinction.","conditional"),
 ("P04","L2","D4",["P01","C02","A06"],"Mechanized correctness and universal route", "When mechanized claims are required, select pinned proof runtime; prove evaluator-to-independent-denotation correctness and supported obligation-generation coverage; audit axioms and reject assumed conclusion/sorry; otherwise retain trusted-checker ceiling explicitly.", "Generic theorem over arbitrary supported finite inputs, not one fixture; exact statement/dependencies/toolchain checked; model existence and required inhabitation remain separate obligations.","conditional"),
 ("P05","L2","D4",["P01","C02"],"Selected temporal or recursive profile extension", "If actual clause coverage requires transition or fixed-point semantics outside existing profiles, select one bounded temporal/recursive adapter or a mechanized encoding; define preservation to canonical IR and explicit bounds; otherwise bind non-applicability. Never choose an engine from a lifecycle/research label.", "Atomic transaction/replay and recursive lineage obligations retain their actual semantics; bounded trace absence is not universal liveness; projections cannot be independently SAT-joined as one model without compatibility proof.","conditional"),
 ("E01","L1","D3",["A01","A06"],"Exact evidence bundle contract", "Bind sources, interpretation, dependencies, required statements, profile, tool versions, assumptions, native inputs/results and review statuses; keep execution/currentness/fidelity/verdict/strength/readiness separate.", "Unknown, unsupported, stale and missing evidence cannot aggregate to ready; actual result data and all required statements are present; schema-only validation never labeled proof.","medium"),
 ("E02","L1","D3",["A03","E01"],"Immutable candidate bundle publisher", "Capture a closed manifest; write a private absent staging directory; publish create-only without overwriting competing paths; verify final source currentness; preserve attempts and old evidence.", "Interrupted and colliding publication preserves inputs and existing output; modified evidence/version does not reuse an old bundle identity; no frozen registry/schema edits.","medium"),
 ("E03","L1","D3",["P02","E02"],"Independent evidence verifier", "Resolve the required set independently from submitted result list; rehash all inputs and current bindings; check model witnesses against independent denotation; distinguish checker trust from mechanized proof; reject incomplete submissions.", "Omit a statement, change a witness, substitute a dependency or provider build; all rejected; historical proof remains historical rather than deleted.","high"),
 ("E04","L1","D3",["E03","A09"],"Adversarial control suite", "Build exact-cause fixtures across schemas, semantics, alias/subtype policy, witness verification, scope, source races and budgets; keep control mutations in copied candidate inputs.", "All declared controls fail/pass for named causes; no malformed input escape; never alter canonical inputs to make a control pass.","medium"),
 ("I01","L1","D3",["C03","E02","E03"],"Transitive invalidation", "Compare source and semantic dependency fingerprints; traverse reverse edges including SCCs; invalidate source/interpretation/assumption/coupling/profile/tool/statement changes; separate semantic and representation deltas.", "Changed leaf invalidates all dependants; deleted/new definition changes the global denominator; unchanged cache entry rehashed, not trusted as authority.","high"),
 ("I02","L1","D3",["I01","A06"],"Addition and revision obligation generation", "Compute exact baseline/proposal diff; classify source, representation, meaning, premise and coupling changes; regenerate affected requirements; preservation/conservativity claims are explicit extra obligations.", "Mislabelled change cannot reduce checks; source-only relabel does not create identity equivalence; obsolete requirements cannot silently disappear.","high"),
 ("I03","L1","D3",["I02","P02"],"Whole selected-snapshot regression", "Compile all included interpretations, axioms and couplings together; check T and T plus required populations before distinctions; recheck affected neighbours; full selected theory required despite local cache reuse.", "Three constraints pairwise satisfiable but jointly contradictory fail; local distinction successes never substitute for full satisfiability and inhabitation.","high"),
 ("I04","L1","D3",["I03","E04"],"Read-only candidate CLI and coverage report", "Expose capture/check/verify/diff/report commands with JSON and human views; declared absent outputs only; report exact whole-definition and projection coverage, remaining premises, failures and next unit.", "An unreviewed or missing translation visibly prevents semantic readiness; output inventory matches manifest; commands do not touch admissions or live registry.","medium"),
 ("I05","L1","D3",["I04","A10"],"Addition/revision workflow rehearsal", "Run one addition, one semantic revision and one representation revision through copied baseline inputs; show revised meanings and realistic examples; preserve source owners and exact review distinctions.", "Currentness and failure routes visible end to end; no live admission integration; effects require future exact owner decisions.","medium"),
 ("G01","L1","D3",["I05"],"L1 candidate workflow exit", "Join the successor-pilot correspondence, required controls, reproducible evidence and selected-snapshot regression receipts; review layer exit evidence.", "First repeatable selected-scope workflow credible; no all-definition coverage claim; no skipped required obligation or owner review.","gate"),
 ("S01","L2","D4",[],"Full semantic dependency declaration closure", "After all source-bound drafts, review every declared uses_definition edge and unresolved reference; seal SCCs, shared signatures, foundational premises and provisional family interfaces; regenerate SCC execution slices before running an incomplete closure.", "All 183 identities accounted; each dependency resolves or is explicit unresolved; no edge inferred from a term/primary_consumer_ref; cycles analyzed jointly.","high"),
 ("S02","L2","D4",["S01","A05","A06"],"Neighbour, alias and carrier-alignment matrix", "Consider all 16,653 unordered current-identity pairs for relevance; record comparable relation, directional strength or exact scoped non-comparability reason; seal shared carrier maps, explicit couplings and neighbour obligations.", "All pair decisions covered without blind inequalities; Lab/Craft homonyms analyzed; subtype overlap and aliases retained; unresolved alignment prevents comparison readiness.","high"),
 ("G02","L2","D4",[],"All-current translation and evidence accounting", "Join every family closure; independently compare source denominator, clause mappings, required obligations, evidence, reviews and residual assumptions; disposition every unsupported item without marking it satisfied.", "183 current identities each have complete required records or explicit unresolved disposition; administrative accounting does not imply 183 proved meanings.","gate"),
 ("Z01","L3","D5",["G02","S02","P01"],"One combined canonical theory", "Merge exact symbols and dependencies using reviewed carrier alignments; expand definitions or include explicit axioms; all cross-family couplings included; preserve scope distinctions and normalized source traceability.", "No omitted axiom/predicate/constraint/bridge; no nominal disjointness inserted to pass; one exact theory digest and complete statement denominator.","high"),
 ("Z02","L3","D5",["Z01","P02","P03"],"Joint satisfiability and required inhabitation", "Run one supported full-theory model check with every required population in the same model; audit assumptions; independently verify witness; if any construct is unsupported, declare full result unresolved.", "A full model plus inhabitants for all declared required carriers, or exact unsat/unknown/unsupported outcome; pairwise or partial-profile passes insufficient.","high"),
 ("Z03","L3","D5",["Z02","E03"],"Contradiction and vacuity diagnosis", "Map cores/counterexamples to source clauses and assumptions; use bounded minimization only as diagnostic; create semantic patch proposals and new iterations rather than weaken constraints silently.", "Known triple contradiction and empty-population controls pinpoint sources; exact incompatibility explanation; unsat core not claimed minimal without checking.","high"),
 ("Z04","L3","D5",["Z01","P04"],"Required universal obligations and assumption audit", "Discharge only explicitly demanded universal distinction/preservation/checker propositions; audit actual kernel dependencies and assumptions; a theorem under assumptions does not establish those assumptions satisfiable.", "Exact statements and generic proof evidence for required supported claims; absent/timeout/unsupported proofs remain visible and non-pass.","high"),
 ("Z05","L3","D5",["Z02","Z04","I04"],"Full-snapshot change regression", "Apply copied addition/revision/coupling/alias diffs across families; re-evaluate exact full theory and all required populations; compare old and new meanings, requirements and currentness.", "Cross-family collapse/contradiction rejected; legitimate alias and subtype extension retained; selected-data compatibility not called model conservativity.","high"),
 ("Z06","L3","D5",["Z03","Z05","E04"],"Clean independent replay", "On a clean candidate output tree, resolve exact source inputs, replay the complete statement set and verify witnesses/proofs without accepting provider summaries; recheck all current source bindings before closeout.", "Complete evidence inventory reproduced/verified at declared strength; no stale source or missing dependency; replay preserves historical results and unrelated work.","high"),
 ("Z07","L3","D5",["Z06"],"Final coverage and limitation ledger", "Produce separate source/translation/fidelity/evidence/strength/currentness dimensions for every definition and full snapshot; assign owner routes to all unresolved outcomes and epistemic assumptions.", "No umbrella all-definition consistency statement unless whole included semantics actually checked; dispositions distinguish incomplete assurance from administrative closeout.","medium"),
 ("H01","L3","D6",["Z07"],"Exact owner review package", "Assemble revised interpretations and realistic examples for all exact subjects; show contrasts, sources, evidence ceilings, unresolved outcomes and proposed effects; stage any selected application artifacts before the owner decision.", "Concrete inspectable package, exact digests and scope; semantic revision proposals separate from fidelity reviews; no implicit authority effect.","human"),
 ("H02","L3","D6",["H01"],"Owner semantic disposition", "Record actual owner choices over exact interpretations and any separately requested semantic-source changes; partial or rejected results remain visible; no actual admission action in the planning scope.", "Attributable exact dispositions, or explicit pending state; owner silence is not approval; unchecked concepts not called proved.","human"),
 ("H03","L3","D6",["H02"],"Selected admission-owner handoff", "If the owner explicitly selects admission effects, recheck currentness and deliver the exact staged candidate to the admitted workflow owner; live application requires its own explicit authorized scope and effects.", "No effect beyond selected decisions; no implementation coupling into another active project by default; deferred/no-admission branch valid and recorded.","protected-conditional"),
 ("H04","L3","D6",["H03"],"Project closeout and continuation", "Write project-owned delivery status reflecting actual achieved coverage, pending obligations and any separate effect receipts; preserve original pilot/planning snapshots and point to the next actual unit.", "Completion wording obeys evidence limits; no incomplete translation/theory called complete; local candidate status synchronization only unless later exact admission authorized.","medium"),
]


def main():
    registry = json.loads((LAB / "authority/definitions/registry.json").read_text())
    entries = {e["definition_id"] + "@" + e["version"]: e for e in registry["entries"]}
    rows = []
    for identity, version in sorted(registry["current_lookup"].items()):
        entry = entries[version]
        path = LAB / entry["path"]
        source = json.loads(path.read_text())
        assert digest(path) == entry["sha256"]
        rows.append({"definition_id": identity, "version_ref": version, "term": entry["term"],
                     "source_path": entry["path"], "source_sha256": entry["sha256"],
                     "scope_ref": source["scope"]["authority_scope_ref"], "source_aliases": source["aliases"],
                     "normative_selectors": ["/voices/scientific_formal/normative_statement", "/voices/scientific_formal/formal_expression", "/boundaries", "/scope"],
                     "family_basis": "Editorial partition after reading the full current normative voice and boundaries; not a semantic dependency/equivalence assertion.",
                     "source_fidelity": "not-reviewed", "formalization": "partial-pilot" if identity in {"cal.definition.authority", "cal.definition.provenance", "cal.definition.governance-axis-independence-invariant"} else "missing-translation",
                     "semantic_dependencies": "must-be-explicitly-declared-and-reviewed; not inferred here"})
    families = []
    assigned = set()
    for fid, title, terms, controls in GROUPS:
        members = [r for r in rows if r["term"] in terms.split("|")]
        for row in members:
            assert row["definition_id"] not in assigned, row["definition_id"]
            assigned.add(row["definition_id"])
            row["family_id"] = fid
        families.append({"id": fid, "name": title, "members": [r["definition_id"] for r in members], "controls": controls,
                         "semantic_predecessors": "unresolved until explicit closure S01; editorial family numbers are not dependencies"})
    assert assigned == set(registry["current_lookup"]), set(registry["current_lookup"]) - assigned
    tasks, units = [], []
    for ident, layer, stage, deps, title, rules, acceptance, risk in CORE:
        tasks.append({"id": ident, "title": title, "layer": layer, "stage": stage, "depends_on": deps.copy(),
                      "status": "planned", "owner": "role:definition-owner" if risk == "human" else "role:formal-assurance-implementer",
                      "risk": risk, "implementation_rules": rules, "acceptance": acceptance,
                      "condition": "Selected evidence-strength policy requires this provider; otherwise exact not-applicable receipt required." if risk == "conditional" else ("Later owner explicitly selects exact admission effects; otherwise no-effect disposition." if risk == "protected-conditional" else None),
                      "swu_ids": [ident + ".1"], "estimated_effort": "high" if risk in {"high","human"} else "medium"})
        units.append({"id": ident + ".1", "parent_task": ident, "kind": "owner-review" if risk == "human" else "implementation",
                      "purpose": title, "inputs": deps.copy(), "outputs": [*PRODUCTS[ident], f"{DATA}/units/{ident}/receipt.json", *([] if risk in {"human", "protected-conditional"} else [f"{IMPL}/tests/test_{ident}.py"])],
                      "write_scope": [*PRODUCTS[ident], f"{DATA}/units/{ident}/", *([] if risk in {"human", "protected-conditional"} else [f"{IMPL}/tests/test_{ident}.py"])],
                      "ordered_rules": rules, "edge_cases": acceptance, "failure_behavior": "Emit failed or explicit unresolved outcome; preserve inputs and last successful bundle. No silently skipped obligation.",
                      "validation": {"phase": "post-produce", "command": None if risk in {"human", "protected-conditional"} else f"python3 -m unittest discover -s {IMPL}/tests -p test_{ident}.py",
                                     "reviewable_check": acceptance, "runner_state": "Declared same-unit post-produce test output; no dependency on the later I04 CLI."},
                      "closeout": "Bind actual inputs/outputs/provider and criterion results; append project-local status; preserve prior candidate evidence."})
    core_by_id = {t["id"]: t for t in tasks}
    stage_rules = {
      "T": ("Translate", "Author one exact source-bound interpretation, complete clause map, typed signature, assumptions, explicit dependencies, required/exempt populations, intuition and realistic example/counterexample.", "Every normative clause accounted; missing translation or dependency explicit; no semantics from labels."),
      "O": ("Generate obligations", "Derive one definition's complete requirements using the sealed neighbour/class/alignment matrix and canonical theory IR; bind exact prerequisite clauses and strength.", "No missing/weak/substituted required obligation; alias/subtype/coupling controls match reviewed class; unaligned carriers unresolved."),
      "E": ("Run candidate evidence", "Compile the exact selected SCC/dependency theory; run satisfiability and joint inhabitation before distinction queries; replay models/proofs under selected profile; include cross-family premises and status.", "All required statements get actual results or explicit unresolved outcomes; witnesses satisfy the entire included closure; bounds and assumptions stated."),
      "R": ("Owner fidelity review", "Show exact source clauses, candidate interpretation, dependency assumptions, realistic examples and actual evidence; obtain attributable owner correspondence decision or retain pending status.", "Actual reviewed-byte fidelity disposition; no canonical meaning/admission mutation; neighbouring scopes and aliases remain explicit."),
    }
    all_r = []
    for family in families:
        fid = family["id"]
        members = [r for r in rows if r["family_id"] == fid]
        for phase, (verb, rules, accept) in stage_rules.items():
            tid = fid + "-" + phase
            dependencies = {"T": ["A04", "C01", "E02"], "O": [fid + "-T", "S02", "A06"],
                            "E": [fid + "-O", "G01", "P02", "P03", "P04", "P05"], "R": [fid + "-E"]}[phase]
            ids = []
            for row in members:
                uid = fid + "-" + phase + "." + row["definition_id"]
                ids.append(uid)
                units.append({"id": uid, "parent_task": tid, "kind": "owner-review" if phase == "R" else "definition-" + phase,
                              "definition_id": row["definition_id"], "version_ref": row["version_ref"],
                              "purpose": verb + ": " + row["term"], "inputs": [row["source_path"], row["source_sha256"], *dependencies],
                              "outputs": [f"{DATA}/definitions/{row['definition_id']}/{phase.lower()}.json"],
                              "write_scope": [f"{DATA}/definitions/{row['definition_id']}/"], "ordered_rules": rules,
                              "edge_cases": family["controls"], "failure_behavior": "Record unresolved/failed/pending without claiming fidelity, proof or admission. A new candidate iteration is a new DAG, not a cycle in this one.",
                              "validation": {"phase": "post-produce", "command": None if phase == "R" else (f"python3 {IMPL}/contracts.py validate --kind {'interpretation' if phase == 'T' else 'obligation-manifest'} --input {DATA}/definitions/{row['definition_id']}/{phase.lower()}.json" if phase in {"T", "O"} else f"python3 {IMPL}/cli.py verify-definition --definition {row['definition_id']} --phase {phase} --snapshot {DATA}/current-snapshot.json"),
                                             "reviewable_check": accept, "runner_state": "future implementation; review commands do not simulate owner decisions"},
                              "closeout": "Bind source version, selected interpretation/dependencies, complete required statements, actual outputs and statuses; update the project-owned coverage row."})
            tasks.append({"id": tid, "title": verb + " family " + family["name"], "layer": "L2", "stage": "D4",
                          "depends_on": dependencies, "status": "planned", "owner": "role:definition-owner" if phase == "R" else "role:formal-assurance-implementer",
                          "risk": "human" if phase == "R" else "high", "implementation_rules": rules, "acceptance": accept,
                          "condition": None, "swu_ids": ids, "estimated_effort": f"{len(members)} per-definition units; complexity varies by source"})
            if phase == "R":
                all_r.append(tid)
        closure = fid + "-J"
        tasks.append({"id": closure, "title": "Joint closure and review join: " + family["name"], "layer": "L2", "stage": "D4",
                      "depends_on": [], "status": "planned", "owner": "role:formal-assurance-reviewer", "risk": "high",
                      "implementation_rules": "Resolve the sealed actual dependency SCCs, compile the whole included closure with explicit reviewed cross-family symbols, and join every required result and fidelity status. Family alone is never assumed dependency-closed.",
                      "acceptance": "Required dependency reviews available; one scoped satisfiable inhabited closure or explicit unresolved outcome; no unreviewed dependency silently accepted.",
                      "condition": None, "swu_ids": [closure + ".1"], "estimated_effort": "high"})
        units.append({"id": closure + ".1", "parent_task": closure, "kind": "family-closure", "purpose": "Verify " + fid + " selected joint dependency theory",
                      "inputs": [fid + "-E", fid + "-R", "S01"], "outputs": [f"{DATA}/families/{fid}/closure-receipt.json"],
                      "write_scope": [f"{DATA}/families/{fid}/"], "ordered_rules": tasks[-1]["implementation_rules"],
                      "edge_cases": family["controls"], "failure_behavior": "Missing cross-family closure or unsupported logic remains unresolved; no local-family success substituted for whole theory.",
                      "validation": {"phase": "post-produce", "command": f"python3 {IMPL}/cli.py verify-family --family {fid} --snapshot {DATA}/current-snapshot.json", "reviewable_check": tasks[-1]["acceptance"], "runner_state": "future implementation"},
                      "closeout": "Bind all included dependency interpretations, fidelity records and required statement outcomes."})
    for task in tasks:
        if task["id"].endswith("-J"):
            task["depends_on"] = all_r.copy()
    # Conservative broad review barrier prevents inventing cross-family edges.
    # S01 may derive a narrower successor execution DAG from explicit SCCs.
    core_by_id["S01"]["depends_on"] = [f["id"] + "-T" for f in families] + ["C03", "A06"]
    core_by_id["G02"]["depends_on"] = [f["id"] + "-J" for f in families] + ["G01", "S02"]
    # Every unit captures the actual normalized task prerequisites, including
    # broad closure barriers assigned above. Future outputs are explicit creates.
    by_task = {t["id"]: t for t in tasks}
    for u in units:
        parent = by_task[u["parent_task"]]
        u["depends_on_tasks"] = parent["depends_on"].copy()
        u["execution_condition"] = parent["condition"]
        u["target_dispositions"] = [{"path": p, "disposition": "create", "activation_condition": parent["condition"] if parent["risk"] == "conditional" and p in PRODUCTS.get(parent["id"], []) else None} for p in u["outputs"]]
        u["pre_execution_check"] = "Rehash declared source and upstream receipts; verify exact source/currentness, semantic closure and absent outputs. Future outputs need not exist before creation."
    dag = {"schema_version": "definition-assurance-detailed-dag/v1-candidate", "authority_effect": "none",
           "status": "authored-candidate; implementation and semantic acceptance not executed", "requested_on": "2026-10-07",
           "objective": "All current and future definitions receive source-faithful formal interpretations, declared semantic non-collapse checks, exact evidence and one combined satisfiable inhabited theory at stated strengths.",
           "existing_evidence": "../d0-d2-v1/REPORT.md; historical inputs preserved; no per-definition completion inferred",
           "layers": ["L0 finite feasibility evidence delivered", "L1 faithful repeatable selected-scope workflow", "L2 all-current translation, review and checked coverage", "L3 combined theory, full regression and owner disposition"],
           "task_graph_meaning": "Edges are procedural prerequisites, not Lab Relation Kinds or inferred semantic dependencies.",
           "semantic_dependency_policy": "Explicit uses_definition declarations; SCCs jointly analyzed; prohibited normative value cycles remain separate obligations. Unknown semantic edges never count as complete.",
           "current_identity_count": len(rows), "admitted_version_count": len(entries), "task_count": len(tasks), "swu_count": len(units),
           "source_registry_sha256": digest(LAB / "authority/definitions/registry.json"), "definition_queue": rows,
           "families": families, "tasks": tasks,
           "iteration_policy": "Corrections produce a new version/attempt graph and invalidate affected evidence. Do not add backward edges or silently weaken the fixed DAG.",
           "execution_policy": {"designation": "candidate-future-execution", "current_request": "analysis-and-planning-only",
                                "implementation_readiness": "not-run", "semantic_admission": "not-authorized-by-this-planning-request",
                                "parallelism": "Independent branches may be scheduled; no subagents spawned or authorized by this plan.",
                                "write_scopes": [IMPL, DATA], "protected_inputs": ["authority/definitions/registry.json", "authority/admissions/", "all frozen source Definitions and schemas", "historical Lean snapshots", "unrelated projects and dirty work"]},
           "completion": "Complete structural accounting is distinct from formal assurance. Global consistency claimed only for a faithfully translated complete included theory with satisfiability and all required inhabitation; unresolved semantics or weaker evidence remain explicit."}
    dump("dag.json", dag)
    dump("swu-manifest.json", {"schema_version": "definition-assurance-swu-manifest/v1-candidate", "authority_effect": "none", "units": units})
    sources = ["authority/definitions/registry.json", "docs/plans/definition-formal-assurance/PROJECT.md", "docs/plans/definition-formal-assurance/project-plan.json", "docs/plans/definition-formal-assurance/source-baseline.json",
               "coordination/projects/definition-formal-assurance/v1/project.json", "docs/plans/definition-formal-assurance/candidate/d0-d2-v1/REPORT.md", "docs/plans/definition-formal-assurance/candidate/d0-d2-v1/checker.py",
               "docs/plans/definition-formal-assurance/candidate/d0-d2-v1/interpretation.json", "docs/plans/definition-formal-assurance/candidate/d0-d2-v1/verify_evidence.py", "docs/plans/definition-formal-assurance/candidate/d0-d2-v1/evidence.json",
               "craft/formalization/formalization-package.json", "craft/formalization/profiles/formal-language-profiles.json", "craft/formalization/schemas/formal-claim-definition-binding.schema.json", "craft/formalization/schemas/neutral-obligation-set.schema.json",
               "craft/formalization/schemas/provider-evidence-binding.schema.json", "craft/formalization/DomainSpecMetaTypeKernel.lean", "craft/impl/cli/lean/DomainSpecCheckedInterchangeDecoder.lean",
               "docs/plans/relational-theorem-checker/ANALYSIS.md", "docs/plans/relational-theorem-checker/layers/L0-working-proof.md", "docs/plans/relational-theorem-checker/layers/L2-model-evolution.md",
               "implementation/lab-runtime/v2/lab_runtime/sources.py", "authority/artifact-types/definition/v1/schema.json"]
    dump("source-baseline.json", {"schema_version": "definition-assurance-plan-sources/v1-candidate", "authority_effect": "none", "sources": [{"path": p, "sha256": digest(LAB / p)} for p in sources], "definitions": rows})
    byid = {t["id"]: t for t in tasks}
    remaining = set(byid)
    levels = []
    done = set()
    while remaining:
        frontier = sorted(i for i in remaining if set(byid[i]["depends_on"]) <= done)
        assert frontier, "Cyclic or unbound DAG"
        levels.append(frontier)
        done.update(frontier)
        remaining -= set(frontier)
    dump("topological-frontiers.json", {"authority_effect": "none", "frontiers": levels, "first_frontier": levels[0], "note": "These are logical frontiers, not estimates or permission to execute. Conditional provider nodes require explicit disposition receipts."})
    # Normalize SWU prerequisites to task gates plus source inputs, never rewrite
    # a SWU as an unbounded family task. One source revision per per-definition unit.
    tasks_root = HERE / "tasks"
    tasks_root.mkdir(exist_ok=True)
    for t in tasks:
        content = f"# {t['id']}: {t['title']}\n\nStatus: planned candidate. Layer: {t['layer']}. Project stage: {t['stage']}. Authority effect: none.\n\n## Inputs and dependencies\n\n" + ", ".join(t["depends_on"]) + "\n\n## Implementation detail\n\n" + t["implementation_rules"] + "\n\n## Acceptance and edge cases\n\n" + t["acceptance"] + "\n\n## Scope and verification\n\nEach listed SWU has exact inputs, outputs, candidate write scope, failure behavior and post-produce validation in [the shared manifest](../swu-manifest.json). Future validation commands are not claimed installed. Source bytes and historical artifacts are read-only.\n\n## Smallest working units\n\n" + "\n".join("- `" + uid + "`" for uid in t["swu_ids"]) + "\n"
        if t["condition"]:
            content += "\n## Conditional route\n\n" + t["condition"] + " No required semantic obligation is waived by provider non-applicability.\n"
        (tasks_root / (t["id"] + ".md")).write_text(content)
    # Full task graph is a deterministic human view of JSON, not a second source.
    mermaid = ["# Detailed execution DAG", "", "Candidate prerequisites; no authority effect. [dag.json](dag.json) owns graph meaning. Semantic SCCs are a separate planned output.", "", "```mermaid", "flowchart TD"]
    for t in tasks:
        mermaid.append(f'  {t["id"].replace("-", "_")}["{t["id"]}: {t["title"]}"]')
    for t in tasks:
        for dep in t["depends_on"]:
            mermaid.append(f'  {dep.replace("-", "_")} --> {t["id"].replace("-", "_")}')
    mermaid.extend(["```", "", "## Logical frontiers", "", "Frontiers describe permitted ordering only; conditional nodes need explicit disposition, owner nodes need actual reviews, and retries create a successor attempt.", ""])
    for index, frontier in enumerate(levels):
        mermaid.append(f"- W{index:02}: " + ", ".join(frontier))
    (HERE / "DAG.md").write_text("\n".join(mermaid) + "\n")
    family_md = ["# Full definition queue", "", "Every current identity appears once. Families are editorial work partitions; semantic dependencies and same-name equivalences are unresolved until explicit declaration and review.", ""]
    for f in families:
        family_md.extend(["## " + f["id"] + ": " + f["name"], "", f"{len(f['members'])} identities. Controls: {f['controls']}", "", "| Exact identity | Term | Version | Source |", "| --- | --- | --- | --- |"])
        for r in rows:
            if r["family_id"] == f["id"]:
                family_md.append(f"| `{r['definition_id']}` | {r['term']} | `{r['version_ref']}` | [source](../../../../../{r['source_path']}) |")
        family_md.append("")
    (HERE / "DEFINITION-QUEUE.md").write_text("\n".join(family_md))
    print(json.dumps({"tasks": len(tasks), "swus": len(units), "families": len(families), "definitions": len(rows), "frontiers": len(levels)}))


if __name__ == "__main__":
    main()
