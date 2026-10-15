"""Write the detailed candidate review from observed test and worked-case receipts."""
import json
import build_worked as b

def main():
 summary=json.loads((b.UNIT/'worked-summary.json').read_bytes());test=json.loads((b.UNIT/'attempt-001/result.json').read_bytes());cases=summary['cases'];negative=cases['counterfactual']['failed_or_unresolved_queries'];rows='\n'.join('| '+name+' | '+str(row['selected_query_count'])+' | '+str(row['independently_checked_models'])+' | '+row['status']+' |' for name in ['unchanged','counterfactual','retirement'] for row in [cases[name]])
 text=f'''# I03: whole selected-theory regression and review

Candidate unit I03.1 checks the entire selected formal theory before evaluating individual distinctions. Its acceptance is limited to exact finite regression, independently checked supplied models, retained obligation denominators, and explicit coverage gaps. It does not accept source meanings, discharge revision theorems, or complete the formalization episode.

The selected suite executed 29 hostile and semantic controls in {test['elapsed_seconds']} seconds, with no skipped or failed tests. Three worked cases use the existing seven-source governance projection, current source snapshot, actual I02 revision requirements, six carrier alignments, and a two-element Record carrier. The source registry still contains 183 current definitions and 189 admitted source versions; admission records provenance rather than truth or translation fidelity.

## 1. Definitions and the object being checked

A definition's admitted source, candidate interpretation, typed signature, selected statements, model, and evidence result are separate objects. Exact SourceRef fields retain definition ID, version, repository path and byte hash. An interpretation is required for every source in the selected theory, exactly once. Source admission does not turn an interpretation into an accepted meaning. Omitting one selected interpretation, duplicating a reference, or borrowing another source's predicate fails preparation.

The seven worked interpretations are partial unary projections associated with Authority, Authority Claim, Responsibility, Provenance, the governance axis independence invariant, Authority Boundary, and Authority Surface. Each whole normative source clause remains deferred. A model of these projections is not a model of the entire source definitions. Primitive, explicit, axiomatic, inductive and operational definition forms need their own interpretations and obligation choices; the runner does not infer a logical axiom merely from an artifact's name or kind.

## 2. Types, signatures and nominal identity

Source-qualified symbols preserve identity through composition. Sorts, predicates, relations, constants and supported total functions remain statically typed. Local spellings alone cannot identify symbols across sources. Carrier sharing requires the explicit selected alignment; predicate identity remains source-specific. The signature map binds every theory declaration to the composed interpretation and checks endpoint ownership.

Every selected theory formula, assumption, query and required population is type-checked after composition. Cardinalities must name exactly the composed sorts, use integer values from 1 through 3, and reject booleans, absent sorts and extra sorts. The worked carrier has cardinality 2. This is a selected finite domain, not an assertion that the domain of governance records contains only two real objects.

## 3. Logical roles determine what may be assumed

The joint theory T includes all selected theory statements, selected formal premise statements, encoded interpretation clauses marked definition, selected axiom, selected premise or constraint, and explicitly selected interpretation assumptions. The runner compiles these together before any consistency result. A false encoded definition clause therefore defeats a theory even when a separately supplied theory statement list is empty.

Proof obligations, derived claims, hypotheses and observation/measurement clauses are retained as additional claim queries rather than silently assumed. A clause mixing premise and claim roles is rejected as ambiguous. Unselected assumptions remain explicitly accounted for but contribute no premise. Deferred or unclassified clauses remain coverage gaps. The candidate implementation offers no temporal, modal, deontic, inductive or partial-function semantics beyond the existing static profile; those aspects require their own explicit formal contracts.

## 4. Joint consistency precedes local conclusions

The first query seeks a supplied model of the full T. The control theory contains P∨Q, ¬P∨Q, and ¬Q. Every pair has a real provider witness that the separate E03 denotation checker accepts. All three together produce the provider's bounded-no-theory-model result. The explanatory logical reason is that ¬Q makes the first clause require P and the second require ¬P. This explanation is not recorded as a mechanically checked theorem.

A passed local constraint or cached pairwise result cannot replace the whole check. The regression selection has no field authorizing cache-based omission. The triple control blocks the subsequent joint-population query and retains its unresolved result row. The report does not promote provider enumeration into an independently checked, unbounded inconsistency proof.

## 5. Required populations must coexist

The second prerequisite seeks one model satisfying T and every required population I together. Population statements regenerated by A06 enter this set, as do additional required populations declared inside included interpretations. An unresolved interpretation population policy fails preparation. One failed extra population cannot disappear merely because an external population list lacks it.

The joint-population control uses two predicates for which each required inhabitant exists separately. Its constraints allow all objects to be P or all objects to be Q, while prohibiting any object from being both. Separate provider witnesses are independently checked, but the combined required populations have no admissible model at the selected cardinality. All subsequent population and relation queries remain blocked with their IDs present. Consistency alone therefore does not permit vacuous distinctions.

## 6. Relations and evidence strength

After both prerequisites have independently checked witnesses, every regenerated population and relation query is evaluated against the same full T and I. An existential intersection or directed difference needs a concrete model witness. A universal claim is searched for a counterexample; finding no finite counterexample does not meet a mechanized-theorem requirement.

The alias controls exercise both outcomes. An actual counterexample is independently checked and defeats the requested alias. A constrained finite model search reporting no counterexample leaves universal evidence pending. The runner does not reinterpret a successful existential witness as equivalence, disjointness, conservativity, source identity, or an all-model theorem.

## 7. Independent model verification

Every supplied witness or countermodel is checked using E03's separate denotation implementation, not the provider's truth evaluator. The check verifies model structure and typing, exact finite cardinalities, full T, relevant I, selected query truth or falsity, model digest, native input bindings, provider/runtime bindings and policy bindings. Regression also checks the native snapshot digest against the prepared source snapshot.

Hostile controls reject rehashed false population models, substituted snapshot hashes, forged rehashed interpretation IR, wrong nominal sources and stale revision requirements. Structural validation, a reported witness label, and a hash-consistent payload each remain insufficient by themselves. A model accepted by the separate evaluator supplies conditional finite semantic evidence, not source fidelity or a kernel proof.

## 8. Revision and affected neighbours

I02 requirements are regenerated before the run and compared with the exact selected result. A caller cannot remove an inconvenient obligation from the stored result. The effective proposal theory retains actual derived change policy rather than trusting a declared representation-only label. The counterfactual adds Traceable⇒Position while preserving the request for a Traceable object outside Position; its request is therefore tested with the new constraint included.

All seven affected current sources in this worked counterfactual occur in the same fresh composed theory. Reports distinguish affected sources included in regression from affected neighbours outside the selection, which remain unresolved. No unsigned dependency edge or absent interpretation is invented to make semantic closure appear complete. Revision preservation and conservativity descriptors remain separate pending theorem obligations; this unit does not prove them.

## 9. Observed worked results

| Case | Selected queries | Independently checked model witnesses | Selected result |
|---|---:|---:|---|
{rows}

The counterfactual's failed or incomplete rows are recorded exactly as: `{json.dumps(negative,sort_keys=True)}`. Their provider absence/execution outcomes are kept with their strengths and limitations; they are not silently turned into checked theorems. The retirement case checks the regenerated smaller current query set while I02's removed-target and retirement-review obligations remain pending. Removing a request does not retrospectively establish the removed relation.

## 10. Abstract projection versus the record world

Generic finite predicate tables can satisfy the selected unary projection without corresponding to any record produced by the restricted A07/A08 world constructor. I03 consequently proves no converse lowering or representation theorem. Earlier A09 checks of concrete world configurations have a different denotation surface and remain separately bound evidence. Combining their names or result counts would not establish equivalence between model classes.

The worked formal premise list adds no formulas beyond the exact projection T. Source-level hypothetical conditions, inherited tuple interpretations, lineage assumptions, grant/claim distinctions and duty interpretation choices remain bound to earlier candidate contracts and pending owner findings. Their absence from the extra formula list does not discharge them.

## 11. Completeness and coverage

The exact logical query denominator is retained through success, failure, resource limits and blocked prerequisites. The current cases contain 11, 11 and 9 queries respectively. Additional encoded claim clauses and required interpretation populations would extend the denominator. On output-size exhaustion, all query IDs remain, while model support is cleared. On malformed or changed selected inputs, the entire result becomes unresolved and previously checked models are not retained as current evidence.

The global source denominator is 183. This selected logical theory has seven partial interpretations and 176 missing current interpretations. Seven whole normative clauses are deferred; source-owner fidelity, semantic dependency closure, full translations and whole-definition proofs remain pending. A selection requesting all-current-required returns all-current-regression-unresolved when current interpretations are missing, even if its selected finite checks succeed.

## 12. Freshness, resource limits and preservation

The selected profile is compared with the current provider policy, and the selected toolchain bindings must match the actual build and runtime. Budgets can tighten that policy. Cancellation, timeouts and interpretation/evaluation/output limits are execution outcomes with no logical absence conclusion. A report of bounded enumeration is retained as a provider report; generic exhaustive absence is not independently verified by E03.

Closing checks re-read selected inputs, current source bindings, regression and supporting engine bytes, and provider/runtime bindings. Races affecting inputs, a source file, an active engine or the selection file clear model support. All 201 source/registry/provenance files and all 587 prior sealed candidate files are rehashed again during fresh verification and closeout. Candidate creation preserves previous successes and unrelated workspace changes.

## 13. Review disposition and remaining work

This is a candidate agent self-review of I03 implementation and exact selected evidence. It is not an independent human review or a source-owner acceptance. The accepted claim is that the runner enforces whole selected T and joint I before local checks, independently verifies supplied models, preserves denominators and exposes scope/strength/fidelity gaps.

The formalization episode remains active. No current definition has an owner-accepted whole translation or whole-definition proof. I04 can expose this candidate workflow through a CLI, but broader formalization still requires authored interpretations, justified semantic couplings, owner review, specialized logic profiles where needed, universal proof evidence and a final review covering the entire 183-definition scope.
'''
 with (b.UNIT/'REVIEW.md').open('x') as stream:stream.write(text)
 print(json.dumps({'review_words':len(text.split()),'authority_effect':'none','semantic_ready':False},sort_keys=True))
if __name__=='__main__':main()
