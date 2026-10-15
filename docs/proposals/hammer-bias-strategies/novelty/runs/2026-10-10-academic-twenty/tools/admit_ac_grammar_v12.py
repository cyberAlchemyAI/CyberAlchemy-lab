#!/usr/bin/env python3
"""Conditional admission only after actual prior closure and source-bound gap.

This performs no native call and never changes an original score or packet.
"""
import json
from ac_runtime import read, save, sha, require, now
from ac_complete_keys_runtime_v15 import CoverageRuntime


def main():
    r = CoverageRuntime()
    require(all(r.state(j['job_id'])['terminal'] for j in r.plan()),
            'Original197 and later75 must actually close first')
    for path in ['receipts/coordinator.final.json',
                 'receipts/coverage-coordinator.final.json']:
        require(read(r.p(path))['observation'] == 'actual_FINAL',
                'Actual coordinator FINAL witness required: ' + path)
    require(r.verify()['status'] == 'pass', 'All existing source/first-lock checks')
    observations = []
    evidence = ['receipts/COORDINATOR-CLOSURE.v10.json',
                'receipts/coverage-coordinator.final.json']
    for jid in ['REVIEW-1-1','REVIEW-1-2']:
        require(r.state(jid)['valid'], 'Valid original review required')
        row = next(x for x in read(r.p('raw/' + jid + '.json'))['strategy_reviews']
                   if x['strategy_id'] == 'AC03')
        require(row['application'] == 'unknown',
                'Original AC03 uncertainty must actually be present')
        observations.append({'job_id':jid,'valid':True,'actual_assessment':row})
        evidence += ['raw/' + jid + '.json','receipts/jobs/' + jid + '.finished.json']
    clarification = read(r.p('coverage/grammar/BUDGET-CLARIFICATION-FREEZE.v12.json'))
    for path, digest in clarification['sources'].items():
        require(sha(path) == digest, 'Conditional budget clarity source drift')
    require(r.budget()['prospective_total'] <= r.budget()['ceiling'],
            'Conditional roles/coordinator/auditors must fit cumulative budget')
    evidence += ['coverage/grammar/BUDGET-CLARIFICATION.v12.md',
                 'coverage/grammar/BUDGET-CLARIFICATION-FREEZE.v12.json',
                 'coverage/REVIEW-SCHEMA-AMENDMENT.v12.md',
                 'coverage/REVIEW-SCHEMA-FREEZE.v12.json']
    evidence += ['coverage/OUTER-LITERAL-AMENDMENT.v14.md','coverage/OUTER-LITERAL-FREEZE.v14.json']
    decision = {
        'utc':now(),'admit':True,
        'authority':'root-authored separately conditional execution protocol',
        'actual_evidence_paths':[str(r.p(p)) for p in evidence],
        'actual_evidence_sha256':{str(r.p(p)):sha(r.p(p)) for p in evidence},
        'valid_original_review_observations':observations,
        'reason':'Both valid actual original AC03 reviews leave the old-rule exclusion unconfirmed. Later COV-REVIEW-1 draws are invalid and do not supply admitted grades. After original197 and later75 actual closure, execute the already-prepared explicit JG grammar to cover that operative boundary; preserve all original scores, invalids and missingness.',
        'scheduled_grammar_dispositions':14,
        'plan_path':str(r.p('coverage/grammar/PLAN.v11.json')),
        'plan_sha256':sha(r.p('coverage/grammar/PLAN.v11.json')),
        'case_sha256':sha(r.p('coverage/grammar/inputs/JG.json')),
        'runtime':'tools/ac_grammar_complete_runtime_v15.py',
        'budget_before_admission':r.budget(),
        'binding_budget_reference':'coverage/BUDGET-AMENDMENT.v1.json: later cumulative300; originalroot260 preserved. BUDGET-CLARIFICATION.v12.md supersedes only stale260 references in inherited grammar preparation texts.',
        'scope_limits':['Explicit source-backed grammar application coverage, not original-case regrade or efficacy','No changed hard mechanics, new physical facts, field originality, human learning or weight updates','Two invalid later review rows remain unadmitted; fresh grammar reviewers use unchanged six-key schema with prospective clarity']}
    save(r.p('coverage/grammar/ADMISSION.v11.json'),decision)
    from ac_grammar_complete_runtime_v15 import GrammarRuntime
    gr=GrammarRuntime();gr.integrity()
    print(json.dumps({'admitted_grammar':14,'budget':gr.budget()},ensure_ascii=False))


if __name__ == '__main__': main()
