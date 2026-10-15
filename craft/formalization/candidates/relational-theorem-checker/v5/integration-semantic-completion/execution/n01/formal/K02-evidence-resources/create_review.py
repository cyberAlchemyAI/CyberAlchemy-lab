"""Derive the review and component map from verified current proof/import evidence."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9];H=HERE.parents[3]
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def run():
    proof=json.loads((HERE/'verification.json').read_text());audit=json.loads((HERE/'import-resolution-audit.json').read_text())
    assert proof['result']=='candidate-fragment-pass' and audit['verification']==bind(HERE/'verification.json')
    prefix='RelationalSuccessor.CandidateEvidenceResources.'
    groups=[('combined resource budget',['combined_budget_exact','authority_counts_toward_budget','authority_bytes_are_charged','dishonest_declared_count_does_not_reduce_budget']),('numeric arithmetic-input boundary',['parts_work_exact','token_work_exact','decimal_power_exponents_bounded','first_unsupported_none_exact','first_unsupported_is_actual_token']),('every nested numeric token',['number_tokens_exact','number_tokens_values_exact','number_tokens_entries_exact','numeric_tree_tokens_exact','numeric_tree_none_exact','numeric_tree_refusal_has_actual_occurrence']),('capture preflight and exact source ordinal',['preflight_ready_exact','preflight_invalid_envelope_exact','preflight_digest_verified_never_refused','preflight_numeric_refusal_actual_cause','all_preflight_exact','first_source_refusal_retains_capture','first_source_refusal_exact_position','digest_reason_exact','preflight_digest_refusal_exact','preflight_scalar_refusal_exact']),('guarded evidence data and independent stage causes',['authority_none_exact','data_prepared_exact','data_outcome_has_independent_cause','bounded_prepared_exact','bounded_budget_refusal_exact','bounded_success_retains_original_inputs','bounded_success_still_requires_authentic_boundary','data_outcome_meaning_exact','bounded_outcome_has_independent_cause']),('truthful local diagnostic fields',['diagnostic_source_position_has_checked_prefix','diagnostic_numeric_token_has_original_occurrence','diagnostic_data_only_after_complete_preflight'])]
    rows=[]
    for name,names in groups:
        targets=[prefix+n for n in names];assert set(targets)<=set(proof['new_declarations'])
        rows.append({'component':name,'theorem_targets':targets,'status':'candidate-component-proved','inherited_discharges':0})
    definition=H/'definitions/K02-addresses-intent.json'
    inherited=json.loads(definition.read_text())['pending_ids']
    matrix={'task':'N01','unit':'K02-evidence-resources','verification':bind(HERE/'verification.json'),'rows':rows,'original_K02_definition':bind(definition),'original_K02_ids':inherited,'all_original_K02_ids_still_pending':True,'inherited_discharges':0,'whole_source_refinement':False,'complete_theory_countermodels':False,'mandatory_independent_checking':False,'authority_effect':'none'}
    (HERE/'refinement-matrix.json').write_text(json.dumps(matrix,indent=2)+'\n')
    seconds=round(sum(r['seconds'] for r in proof['records']),3);maximum=max(r['seconds'] for r in proof['records']);inspections=sum(r['inspected_declarations'] for r in proof['records'])
    text=f'''# Guarded evidence preparation: what changed and what remains

The new candidate entrypoint checks one combined original-byte/count budget and
numeric work limits before interpreting typed profile or authority fields. This
closes two concrete component gaps: the authority capture previously did not count
in the catalog's aggregate/count budget, and a short token such as
`1e1000000000` could request an enormous decimal power in the exact Nat decoder.

## Formal meaning comes first

Success means all three independently specified conditions hold:

```text
BoundedPreparedMeaning(stage)
  = CombinedBudgetMeaning(authority + declarations + selections)
  AND AllPreflightMeaning(every original capture)
  AND PreparedEvidenceMeaning(exact profile and authority stage)
```

`bounded_prepared_exact` proves the guarded implementation returns that exact stage
if and only if this meaning holds. The final conjunct is the previous evidence
meaning; the new guard does not replace or weaken its source/evidence joins. All
original envelopes are retained. Ownership still requires an actual independently
established authentic snapshot; the data preparation cannot manufacture it.

## Execution layers

| Layer | What it establishes | What it does not establish |
|---|---|---|
| Combined budget | Actual bytes, count and per-capture lengths include authority and every declaration/selection | A measured memory or elapsed-time ceiling |
| Lexical numeric guard | Token/mantissa/exponent-digit/magnitude bounds constrain every decimal-power exponent used by the current Nat evaluator | Integrality, authentic meaning or successful typed decoding |
| Scalar-tree traversal | Nested arrays, unused fields and duplicate object entries retain their numeric tokens | Shape/schema acceptance of those entries |
| Capture preflight | Envelope, exact digest/profile, supported scalar document and numeric eligibility all pass | Typed profile or authority preparation |
| Typed data preparation | Exact selected profile data, authority data and their evidence joins hold | Authentic ownership/root/provider evidence |
| Local diagnostic | First failed capture, original envelope and actual numeric token; or exact failed data stage | An invented field path, blame or authority conclusion |

Authority is source index 0, followed by declaration inputs and then selection
inputs in their original order. `first_source_refusal_exact_position` proves the
reported position by decomposing the original list into an accepted prefix, the
actual failed capture and its suffix. The scalar and digest refusal theorems also
retain their independent missing meanings. Every typed-data outcome is equivalent
to its independently defined data-stage meaning.

## Worked cases

| Input/change | Result | Cause |
|---|---|---|
| Original captured authority, declaration and selection | `data.prepared` | Bounded prepared-data meaning holds; authenticity remains separate |
| Count limit two for these three captures | `resource.combined-budget-exceeded` | Authority counts as an input |
| Total byte limit covering only declaration + selection | `resource.combined-budget-exceeded` | Authority bytes are charged too |
| Claimed authority byte length changed to zero | `source.invalid-envelope` | Original bytes remain charged; claimed length is inconsistent |
| Huge exponent inside nested/unused/duplicate entries | `resource.numeric-work-unsupported` | Actual retained token fails configured work limits before typed arithmetic |
| Invalid syntax or an unpaired surrogate string | `source.unsupported-scalar-document` | No supported scalar-document meaning exists |
| Changed requested trust root | `data.authority-preparation-refused` | Prepared profile exists; no matching authority data exists |
| Missing source review in an otherwise prepared snapshot | `data.evidence-join-refused` | Data stages exist; their source-evidence joins fail |
| Broken declaration/selection envelope | Source indices 1/2 respectively | Authority and every earlier capture passed |

`42.0`, `4.2e1`, `4.2E+1` and `-0` remain numerically supported within the configured
work bounds. The fractional token `0.5` can be resource-eligible while the Nat
adapter rejects it. The exact nonintegral token
`123.000000000000000000000001` likewise passes this resource guard but is refused
by the Nat adapter. Resource eligibility never substitutes for mathematical type
checking or rounds the original lexeme.

## Verification

All {len(proof['records'])} fresh isolated pinned Lean invocations and matching-phase
import-resolution pairs pass: {proof['new_general_declarations']} general declarations
and {proof['new_worked_control_declarations']} closed controls, {inspections}
dependency-inclusive axiom inspections. All {proof['runtime_composed_cases']} runtime
comparisons pass in each phase. The inherited six original byte fixtures are
checked against their actual bytes and literal captures. A separate configuration
schema audit passes 25 decoded-value shape checks; it is not raw decoder equivalence.

Compilation/elaboration/evaluation totals {seconds} seconds, maximum single
invocation {maximum} seconds. These observations are not operational measurements.
Same-kernel replay is not the mandatory independent proof checker. Permitted
standard axioms are only propext, Quot.sound and Classical.choice; no sorry/admit,
native_decide or custom axioms are used in new sources.

## Remaining gaps and limits

- Legacy unguarded APIs remain callable. Intended consumers must be forced through
  the guarded boundary before its protection can be relied on operationally.
- Preflight and legacy preparation repeat hashing and scalar parsing. A reuse
  implementation must first preserve the exact original-byte and prepared meanings.
- Limits are explicit configuration. Excessively permissive configuration can still
  admit expensive work. Recursion/depth, arrays, memory and end-to-end time need the
  composed N14 measurement and a reviewed supported resource policy.
- Budget and scalar refusals group several causes. Typed-data diagnostics identify
  the stage, not one field. Further precision needs independently defined causes
  and proofs; the current API states this limit explicitly.
- The actual authoritative snapshot provider, complete Schema/review interpretation,
  remaining source policies, whole K02/all-kind refinement, full-theory/effect
  closure and mandatory independent checking remain required.
- These 55 declarations discharge none of the original semantic IDs. All 263 remain
  pending; the original 90 discharges retain scope. K04 and D01-D08 remain pending.
  Only N00 is accepted (1/20). All 41 kinds, 550 pairs, seven extensions and the final
  new actual bounded-use assessment retain their original completion criteria.

See NEXT-IMPLEMENTATION.md for the formalization-first continuation order. The
complete plan remains active and incomplete; no deployment or promotion occurred.
'''
    (HERE/'MODEL-REVIEW.md').write_text(text)
    print('Review and exact component refinement map created.')
if __name__=='__main__':run()
