"""First-save unscored I11 schedule and maximal fixture; never admits launch."""
import copy
import json
from datetime import datetime, timezone
import generation_publication_v3 as pub
import generation_runtime_v2 as g
import generation_raw_first_runtime as f
import blind_generation_raw_first as packet

R = f.R


def save(path, body):
    target = R / path
    target.parent.mkdir(parents=True, exist_ok=True)
    pub.exclusive_text(target, body if isinstance(body, str) else json.dumps(body, indent=2) + '\n')


def prepare():
    cases = ['H-P', 'A-P', 'H-C1', 'H-C2', 'A-C1', 'A-C2']
    arms = ['000', '001', '010', '011', '100', '101', '110', '111', 'G']
    roles = f.read(R / 'prompts/composition-draft/roles.json')
    original = (R / 'prompts/generation-v2/I02-ordinary.txt').read_text()
    marker = 'Missing source cards are not silently invented.'
    assert marker in original
    common = original.split(marker, 1)[0] + marker + '\n'
    prompts, jobs, reviews, index = {}, [], [], 401
    for case in cases:
        for arm in arms:
            priors = []
            for stage in [1, 2, 3]:
                operation = ('generic' if arm == 'G' else
                             ['necessity', 'construction', 'conversion'][stage-1] if arm[stage-1] == '1' else 'ordinary')
                prompt = f'prompts/composition-i11-draft-v2/I11-{arm}-S{stage}.txt'
                text = common + roles[operation] + '\n'
                if stage > 1:
                    text += 'Read every supplied earlier same-cell raw stage; each qualified prior ID requires one explicit disposition. Final output remains raw generation; no compressor.\n'
                if operation == 'construction':
                    text += 'Return attacks max two A1/A2 with dependency, source_refs of assigned qualified prior IDs, linked_opening_ids, disposition replacement|removal|test|no_branch. Each non-no_branch has current R1/R2 targets; no_branch targets empty.\n'
                if prompt not in prompts:
                    save(prompt, text)
                    prompts[prompt] = g.sha(R / prompt)
                key = f'G{index:04d}'
                index += 1
                job = {'job_id': key, 'study_id': 'I11', 'case_id': case,
                       'phase': 'pilot' if case.endswith('-P') else 'confirmation', 'role': 'raw',
                       'arm': arm, 'stage': stage, 'operation': operation, 'prompt_ref': prompt,
                       'output_ref': f'outputs/composition/{key}.json',
                       'input_refs': [f'cases/{case}.json'] + [p['output_ref'] for p in priors],
                       'depends_on': [p['job_id'] for p in priors],
                       'requires_gates': ['I11-composition-native-admission'] + ([] if case.endswith('-P') else ['I11-pilot-lock']),
                       'maximum_current_openings': 2, 'soft_saved_word_limit': 420}
                jobs.append(job)
                priors.append(job)
        for n in [1, 2]:
            reviews.append({'job_id': f'RF-R-I11-{case}-{n}', 'study_id': 'I11', 'case_id': case,
                            'phase': 'pilot' if case.endswith('-P') else 'confirmation', 'review_phase': 'raw',
                            'depends_on': [j['job_id'] for j in jobs if j['case_id'] == case],
                            'output_ref': f'reviews/composition/RF-R-I11-{case}-{n}.json',
                            'soft_saved_word_limit': 30000})
    sp, rp = 'composition-i11-schedule.draft-v2.json', 'composition-i11-reviews.draft-v2.json'
    save(sp, {'classification': 'draft_unadmitted_no_scored_calls', 'jobs': jobs,
              'scope': 'All original six blocks, nine arms, three raw stages. All cross-stage pairs included. No compressor; confirmation conditional.'})
    save(rp, {'classification': 'draft_unadmitted', 'jobs': reviews})
    paths = ['inputs/plan/PLAN.md', 'inputs/plan/portfolio.json', 'criteria-generation.v2.json',
             'generation-review-contract.v2.json', sp, rp, *prompts]
    bindings = [{'path': p, 'sha256': g.sha(R / p)} for p in paths]
    bp = 'receipts/I11-composition-preparation-budget.v2.json'
    save(bp, {'classification': 'prospective_I11_preparation_not_scored_admission', 'study_id': 'I11',
              'time_utc': datetime.now(timezone.utc).isoformat(),
              'authority': 'Existing user goal run all strategies; PLAN selected ready-wave ceiling six preparation calls plus one completion audit. Separate I11 allocation, no transfer from unused raw-first or I10 calls.',
              'preparation_native_call_maximum': 6, 'completion_audit_native_call_maximum': 1,
              'experimental_pilot_base_and_maximum': [58, 60], 'experimental_confirmation_base_and_maximum': [116, 120],
              'review_saved_word_soft_limit': 30000,
              'why_word_rebudget': 'Full 1431 raw pairs instead of smaller unadmitted 567-pair draft. Native maximal complete capacity and independent runtime/source audit still required before scoring.',
              'scored_retries': 0, 'actual_new_scored_calls': 0, 'actual_new_preparation_calls': 0,
              'source_bindings': bindings})
    fixture_jobs = copy.deepcopy([j for j in jobs if j['case_id'] == 'H-P'])
    remap = {j['job_id']: f'G{9001+i:04d}' for i, j in enumerate(fixture_jobs)}
    output_map = {j['output_ref']: f'fixtures/composition-i11-source-capacity/{remap[j["job_id"]]}.json' for j in fixture_jobs}
    for job in fixture_jobs:
        job['job_id'] = remap[job['job_id']]
        job['depends_on'] = [remap[p] for p in job['depends_on']]
        job['output_ref'] = output_map[job['output_ref']]
        job['input_refs'] = [output_map.get(p, p) for p in job['input_refs']]
    bodies, dispositions = {}, {}
    for job in fixture_jobs:
        prior = [p + ':' + o['id'] for p in job['depends_on'] for o in bodies[p]['openings']]
        openings = [{'id': f'R{i}', 'kind': 'question', 'claim': f'Unscored capacity fixture question {i}.',
                     'delta': 'Fixture-only dependency replacement; no discovered strategy.',
                     'prediction': 'Both fixture variants predict the same stipulated observation.',
                     'probe': 'Unscored fixture only; no physical, data or human probe executed.',
                     'fit': 'uncertain', 'assumptions': ['Fixture has no measured feasibility or efficacy.'],
                     'source_refs': ['valued_outcome', *prior]} for i in [1, 2]]
        body = {'case_id': 'H-P', 'role': 'raw', 'openings': openings,
                'assessment': 'UNSCORED_CAPACITY_FIXTURE; structurally complete template only.',
                'lineage': [{'source_id': p, 'disposition': 'changed', 'target_ids': ['R1'],
                             'reason': 'Fixture-only complete lineage; no observed transformation.'} for p in prior]}
        if job['operation'] == 'construction':
            body['attacks'] = [{'attack_id': f'A{i}', 'dependency': 'Fixture-only prior dependency.',
                               'source_refs': [prior[i-1]], 'linked_opening_ids': ['R1'], 'disposition': 'test'} for i in [1, 2]]
        bodies[job['job_id']] = body
        dispositions[job['job_id']] = {'execution': 'valid', 'cause': 'Unscored synthetic maximal fixture; no native experimental execution.'}
    fs = {'jobs': fixture_jobs}
    fr = {'jobs': [{'job_id': f'RF-R-I11-H-P-{n}', 'study_id': 'I11', 'case_id': 'H-P'} for n in [1, 2]]}
    inputs = (fs, fr, f.read(R / 'generation-review-contract.v2.json'),
              f.read(R / 'criteria-generation.v2.json'), f.read(R / 'archives/case-archives.json'))
    body, admin = packet.build_raw('I11', 'H-P', bodies, dispositions, R, inputs)
    expected = {'raw_rows': 54, 'archive_pairs': 216, 'candidate_pairs': 1431, 'post_rows': 0,
                'retention_rows': 0, 'lineage_rows': 54, 'addition_rows': 0, 'attack_rows': 8,
                'contradiction_rows': 0, 'unit_rows': 27}
    assert body['matrix_counts'] == expected and body['expected_total_rows'] == 1790
    mp, ip = 'fixtures/composition-i11-maximal-raw.v2.json', 'fixtures/composition-i11-maximal-inputs.v2.json'
    save(mp, body)
    save(ip, {'classification': 'unscored_capacity_only', 'schedule': fs, 'reviews': fr,
              'artifacts': bodies, 'dispositions': dispositions, 'builder_input_bindings': admin['input_payload_bindings']})
    report = {'classification': 'draft_full_matrix_not_native_capacity_or_admission', 'schedule_roles': len(jobs),
              'phase_counts': {'pilot_generation': 54, 'pilot_reviews': 4, 'confirmation_generation': 108, 'confirmation_reviews': 8},
              'all_three_stages_raw': True, 'compression_roles': 0, 'full_maximal_matrix_counts': expected,
              'full_maximal_rows': 1790, 'prior_unadmitted_draft_rows': 926, 'broader_cross_stage_pairs_not_omitted': 864,
              'review_soft_saved_word_limit': 30000, 'native_maximal_capacity_check': 'not_started_required',
              'independent_runtime_audit': 'not_started_required', 'actual_scored_calls': 0, 'actual_preparation_calls': 0,
              'source_bindings': bindings + [{'path': p, 'sha256': g.sha(R / p)} for p in
                                           [bp, mp, ip, 'tools/prepare_i11_full_matrix_v2.py',
                                            'tools/blind_generation_v2.py', 'tools/blind_generation_raw_first.py']]}
    path = 'reports/I11-full-matrix-preparation.v2.json'
    save(path, report)
    return g.event({'event_kind': 'unscored_composition_preparation', 'study_id': 'I11',
                    'output_ref': path, 'output_sha256': g.sha(R / path), 'all_scheduled_generation_roles': len(jobs),
                    'maximal_case_rows': 1790, 'native_call_credit': 0, 'runtime_admitted': False})


if __name__ == '__main__':
    print(json.dumps(prepare()))
