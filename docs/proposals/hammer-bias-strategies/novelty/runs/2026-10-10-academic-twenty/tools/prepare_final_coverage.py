#!/usr/bin/env python3
"""Prepare separate coverage only after primary closure; no native model calls.

Preserves every original first output, score and unrun draft. The known missing
AC07 controls receive new three-stage chains, followed by the already planned
fresh reviews. Additional gaps require explicit root adjudication, never an
automatic zero-effect inference or repair of an original output.
"""
import copy
import json
from ac_runtime import Runtime, read, save, sha, require, now


def main():
    r = Runtime()
    original = r.plan()
    require(all(r.state(j['job_id'])['terminal'] for j in original),
            'All original dispositions must close before final coverage preparation')
    require(read(r.p('receipts/coordinator.final.json'))['observation'] == 'actual_FINAL',
            'Actual primary coordinator FINAL witness required')
    require(not any(r.p('receipts/jobs/' + j['job_id'] + '.admitted.json').exists()
                    for j in read(r.p('coverage/PLAN.v6.json'))),
            'Prepared v6 coverage must still be unrun')
    old = read(r.p('coverage/PLAN.v6.json'))
    new_controls = []
    evidence = []
    for arm in ['OLD', 'BREADTH']:
        invalid = 'AC07-' + arm + '-J0-builder'
        require(r.state(invalid)['terminal'] and not r.state(invalid)['valid'],
                'Recorded original control gap required: ' + invalid)
        evidence.append({'job_id': invalid, 'actual_state': r.state(invalid),
                         'raw_path': 'raw/' + invalid + '.json',
                         'raw_sha256': sha(r.p('raw/' + invalid + '.json'))})
        for stage in ['proposal', 'critique', 'builder']:
            source = r.job('AC07-' + arm + '-J0-' + stage)
            job = copy.deepcopy(source)
            job['job_id'] = 'COV-' + source['job_id']
            job['dependencies'] = ['COV-' + d for d in source['dependencies']]
            job['additional_control_coverage'] = True
            job['instructions'] = (
                'Fresh separately admitted AC07 ' + arm + ' control after the '
                'invalid original builder. Original outputs and unavailable '
                'comparisons remain unchanged. Use the same case, method and '
                'six-slot condition as the recorded original control. '
                'This is a new first save and a later comparison, never a retry '
                'or regrade of the first study. ' + source.get('instructions', ''))
            new_controls.append(job)
    none_source = r.job('AC09-NONE-builder')
    require(r.state(none_source['job_id'])['terminal'] and
            not r.state(none_source['job_id'])['valid'],
            'Actual original AC09 NONE missing-output failure required')
    require(not r.p('raw/' + none_source['job_id'] + '.json').exists(),
            'Preserve original missing output')
    require(all(r.state(d)['valid'] for d in none_source['dependencies']),
            'Original NONE critique must remain valid')
    none_job = copy.deepcopy(none_source)
    none_job['job_id'] = 'COV-' + none_source['job_id']
    none_job['additional_control_coverage'] = True
    none_job['instructions'] = (
        'Separately admitted later NONE builder using the unchanged valid '
        'original AC09-NONE-critique handoff. Preserve the original missing '
        'builder output, invalid disposition and unavailable first comparison. '
        'The actual initial NONE first/second/critique pool remains original '
        'control evidence. Use the available python3 command for an exclusive '
        'first save. ' + none_source.get('instructions', ''))
    new_controls.append(none_job)
    evidence.append({
        'job_id': none_source['job_id'], 'actual_state': r.state(none_source['job_id']),
        'raw_exists': False,
        'native_FINAL_path': 'receipts/jobs/' + none_source['job_id'] + '.native-final.json',
        'native_FINAL_sha256': sha(r.p('receipts/jobs/' + none_source['job_id'] + '.native-final.json')),
        'later_role': none_job['job_id'],
        'unchanged_valid_original_dependencies': none_job['dependencies']})
    from ac_fidelity_coverage import jobs as fidelity_jobs
    fidelity = fidelity_jobs(r)
    new_controls += fidelity
    plan = [j for j in old if j['role'] != 'review'] + new_controls
    for source in [j for j in old if j['role'] == 'review']:
        job = copy.deepcopy(source)
        relevant = [j['job_id'] for j in new_controls
                    if j['strategy_id'] in job['review_strategies']]
        job['dependencies'] += relevant
        job['instructions'] += (
            ' The separately admitted COV-AC07-OLD and COV-AC07-BREADTH '
            'chains, where assigned, supply fresh control coverage. Keep the '
            'original invalid builders and their unavailable contrasts visible. '
            'COV-AC09-NONE-builder supplies only a later endpoint from the '
            'unchanged original valid NONE critique; the original missing '
            'output remains invalid and unavailable. '
            'Additional fidelity roles provide accurate AC09 before/revised '
            'preservation and actual independent ROOT:S03 investigators, '
            'unchanged-core ordinary AC10 work, strict same-parent and '
            'actual-account boundary checks, and an actual post-attack '
            'shared-construction adjacent trial. Inspect their stated scope '
            'and actual supplementary model replays separately from the '
            'original observations. Never convert a source-backed refusal '
            'or an unavailable contrast into zero effect. '
            'Assess later comparisons separately against unchanged treatment '
            'and DEPTH stages; never repair original first grades. All original '
            'packets before the prospective cap clarification remain unchanged; '
            'future builder fields match the existing strict bound of one. '
            'Inspect assigned input manifests for the two original packet '
            'clarity phases; compliance changes are not creativity or learning.')
        plan.append(job)
    ids = [j['job_id'] for j in original + plan]
    require(len(ids) == len(set(ids)), 'Duplicate cumulative job ID')
    require(all(set(j['dependencies']) <= set(ids) for j in plan),
            'Unknown cumulative dependency')
    projected = len(r.invocations()) + len(plan) + 1 + 14 + 1 + 2
    require(projected <= 260, 'Coverage plus coordinators, grammar and audits exceed ceiling')
    save(r.p('coverage/PLAN.v7.json'), plan)
    save(r.p('coverage/GAP-ADMISSION.v7.json'), {
        'utc': now(), 'status': 'prospective separate coverage, no native call',
        'evidence': evidence, 'new_roles': [j['job_id'] for j in new_controls],
        'original_first_reviews': [j['job_id'] for j in original if j['role'] == 'review'],
        'original_reviews_preserved': True,
        'prospective_native_total_including_grammar_and_audits': projected,
        'ceiling': 260})
    contract = (
        '# Separate ordinary, arrangement and missing-control coverage, version7\n\n'
        'Version7 adds six fresh AC07 OLD/BREADTH roles and one later '
        'AC09 NONE builder and twelve requirement-level fidelity roles to '
        'the unrun v6 package, for41 dispositions: '
        'six ordinary, six matched-count AC04, six AC07 controls, one '
        'AC09 endpoint, twelve fidelity roles and ten independent reviews. '
        'The latter add one shared-candidate post-attack adjacent builder, '
        'two accurate before/revised preservation stages, four actual '
        'independent ROOT:S03 stages, three ordinary unchanged-core stages '
        'and two bounded source-account/parent-link investigations. Their '
        'scope is operation/comparison coverage, not a regrade or a new '
        'equal-compute effect estimate. Original control '
        'builders remain invalid. Cases, actual source-bank exposure, '
        'methods, six-slot conditions and inherited word/search caps match '
        'their original controls. Explicit builder packet cap1 matches the '
        'already-existing strict role requirement. This supplies later '
        'comparison coverage rather than altering any original first bytes '
        'or dispositions. Original197 packet clarity has two disclosed '
        'phases under preparation/CAP-CLARIFICATION-AMENDMENT.v2.md; '
        'the first61 completed roles and four gates are preserved, while '
        '132 then-unadmitted packets receive the prospective clarification. '
        'Both original and amendment freezes remain binding.\n\n'
        'All inherited v6 first-save, actual native FINAL, word/reference, '
        'sidecar-order, exposure and two-worker requirements apply. The '
        'earlier unrun versions remain preserved as preparation. Read '
        'CONTRACT.v6.md for provenance; PLAN.v7.json alone defines the '
        '41 new scheduled dispositions. The native-call ceiling is260 '
        'including failed calls, both later coordinators and two required '
        'completion auditors. No native coverage call precedes primary '
        'closure or this freeze. Later reviews preserve all first grades, '
        'inspect every required control and expose missingness rather than '
        'zero effects. Both ordinary arms receive common source facts; '
        'paired AC04 proposals each prescribe3 initial constructions and '
        '6 search slots, without an equal hidden-compute claim. Later '
        'reviewers receive admission-bound actual role envelopes and '
        'deduplicated literal case/method packs as well as source-bank '
        'manifests; this addresses first-review uncertainty about absent '
        'W0 source facts and assigned resumption allowances. A changed '
        'number of outputs is distinct from a changed assigned allowance. '
        'First reviewer doubts remain immutable.\n')
    save(r.p('coverage/CONTRACT.v7.md'), contract.encode())
    prompt = r.p('coverage/COORDINATOR-PROMPT.v6.txt').read_text().splitlines()[0]
    prompt = prompt.replace('v6', 'v7').replace('twenty-two', 'forty-one').replace('all22', 'all41')
    prompt += ('\nFinal version7 includes41 actual roles; PLAN.v7.json is authoritative. '
               'Its extra six AC07 OLD/BREADTH roles are separately admitted '
               'controls, not original retries. Preserve original cap failures '
               'and the original missing AC09 NONE builder. Its one later '
               'builder uses the unchanged valid original critique. '
               'Twelve additional fidelity roles address actual first REVIEW3 '
               'clauses. The adapter itself performs and locks three '
               'deterministic adjacent-setting replays after the one actual '
               'post-attack native builder FINAL. These are pure-model '
               'executions, not three extra native calls or physical trials. '
               'Do not bypass that adapter finish/verify. Boundary roles '
               'must never invent a defective incumbent or unsupported '
               'parent-preserving link. '
               'and all original reviewer grades. Read GAP-ADMISSION.v7.json '
               'and the primary CAP-CLARIFICATION-AMENDMENT.v2.md.\n')
    save(r.p('coverage/COORDINATOR-PROMPT.v7.txt'), prompt.encode())
    adapter = r.p('tools/ac_coverage_runtime_v6.py').read_text()
    adapter = adapter.replace('from ac_coverage_runtime_v5 import',
                              'from ac_coverage_runtime_v6 import')
    adapter = adapter.replace('PLAN.v6', 'PLAN.v7').replace('FREEZE.v6', 'FREEZE.v7')
    adapter = adapter.replace('coverage v6 source drift', 'coverage v7 source drift')
    adapter = adapter.replace('    def payload(self, j):\n',
                              '    def finish(self, jid, witness):\n'
                              '        from ac_fidelity_coverage import finish_trial\n'
                              '        out = super().finish(jid, witness)\n'
                              '        finish_trial(self, self.job(jid))\n'
                              '        return out\n'
                              '    def verify(self):\n'
                              '        from ac_fidelity_coverage import verify_trials\n'
                              '        out = super().verify()\n'
                              '        verify_trials(self)\n'
                              "        out['supplementary_adjacent_trial_integrity'] = 'pass'\n"
                              '        return out\n'
                              '    def payload(self, j):\n', 1)
    adapter = adapter.replace("        if j.get('arrangement_coverage'):\n",
                              "        if j.get('post_attack_adjacent_trial'):\n"
                              '            from ac_fidelity_coverage import trial_contract\n'
                              "            v['post_attack_adjacent_trial_contract'] = trial_contract(self, j)\n"
                              "        if j.get('arrangement_coverage'):\n", 1)
    adapter = adapter.replace('        super().validate(j, v)\n',
                              '        super().validate(j, v)\n'
                              '        from ac_fidelity_coverage import validate_trial\n'
                              '        validate_trial(j, v)\n', 1)
    adapter = adapter.replace('        return v\n    def literal',
                              "        if j['role'] == 'review':\n"
                              "            for d, record in v['actual_chains'].items():\n"
                              "                trial = self.p('replays/' + d + '.adjacent-settings.json')\n"
                              "                if trial.exists():\n"
                              "                    record['post_attack_adjacent_trials'] = read(trial)\n"
                              "                    record['post_attack_adjacent_trial_sha256'] = sha(trial)\n"
                              '        return v\n    def literal', 1)
    adapter = adapter.replace('        super().integrity()\n',
                              '        super().integrity()\n'
                              '        from ac_runtime_explicit_cap_v2 import Runtime as ExplicitCapRuntime\n'
                              '        ExplicitCapRuntime(self.root).integrity()\n', 1)
    adapter = adapter.replace("            for d in j['dependencies']:\n",
                              "            v['source_exposure_audit']['case_packs'] = {}\n"
                              "            v['source_exposure_audit']['method_packs'] = {}\n"
                              "            for d in j['dependencies']:\n", 1)
    adapter = adapter.replace('                q = read(p)\n',
                              '                q = read(p)\n'
                              "                case_digest = hashlib.sha256(encoded(q['case'])).hexdigest()\n"
                              "                method_digest = hashlib.sha256(encoded(q['method'])).hexdigest()\n"
                              "                v['source_exposure_audit']['case_packs'][case_digest] = q['case']\n"
                              "                v['source_exposure_audit']['method_packs'][method_digest] = q['method']\n", 1)
    adapter = adapter.replace("                    'candidate_cap': q['candidate_cap'],\n",
                              "                    'candidate_cap': q['candidate_cap'],\n"
                              "                    'word_cap': q['word_cap'],\n"
                              "                    'delivered_case_digest': case_digest,\n"
                              "                    'delivered_method_digest': method_digest,\n"
                              "                    'literal_role_envelope': self.p('prompts/' + d + '.txt').read_text().split('\\nPAYLOAD_JSON\\n', 1)[0],\n"
                              "                    'literal_prompt_matches_admission': sha(self.p('prompts/' + d + '.txt')) == a['prompt_sha256'],\n"
                              "                    'registered_spawn_observation': read(self.p('receipts/jobs/' + d + '.spawned.json')) if self.p('receipts/jobs/' + d + '.spawned.json').exists() else None,\n"
                              "                    'native_FINAL_observation': read(self.p('receipts/jobs/' + d + '.native-final.json')) if self.p('receipts/jobs/' + d + '.native-final.json').exists() else None,\n"
                              "                    'fixed_search_budget': q.get('fixed_search_budget'),\n"
                              "                    'context_manifest': q.get('context_manifest'),\n"
                              "                    'allowed_source_refs': q['allowed_source_refs'],\n"
                              "                    'allowed_input_job_refs': q['allowed_input_job_refs'],\n"
                              "                    'essential_summary_literal': q.get('essential_summary'),\n"
                              "                    'additional_delivered_packs': {key: q[key] for key in ['routed_sources', 'source_exposure_manifest', 'examples', 'retrieved_card', 'external_state', 'practice_feedback', 'actual_feedback', 'matched_failure_feedback', 'received_criticism', 'criticism_sha256', 'received_opening', 'verified_core', 'actual_beneficiary', 'fixed_pool_sha256'] if key in q},\n"
                              "                    'essential_summary_sha256': hashlib.sha256(q['essential_summary'].encode()).hexdigest() if 'essential_summary' in q else None,\n"
                              "                    'frame_failure_sha256': hashlib.sha256(encoded(q['actual_common_frame_failure'])).hexdigest() if 'actual_common_frame_failure' in q else None,\n", 1)
    save(r.p('tools/ac_coverage_runtime_v7.py'), adapter.encode())
    paths = ['coverage/PLAN.v7.json', 'coverage/GAP-ADMISSION.v7.json', 'coverage/ADDITIONAL-GAPS.v4.json',
             'coverage/CONTRACT.v7.md', 'coverage/COORDINATOR-PROMPT.v7.txt',
             'tools/ac_coverage_runtime_v7.py', 'tools/prepare_final_coverage.py',
             'tools/ac_fidelity_coverage.py']
    save(r.p('coverage/FREEZE.v7.json'), {
        'utc': now(), 'sources': {str(r.p(p)): sha(r.p(p)) for p in paths},
        'prospective_jobs': len(plan), 'native_calls_at_preparation': 0})
    # This remains conditional preparation. Admission needs actual review
    # evidence and closure of the separately executed control coverage.
    for name in ['PLAN', 'CONTRACT', 'COORDINATOR-PROMPT']:
        suffix = {'PLAN': 'json', 'CONTRACT': 'md', 'COORDINATOR-PROMPT': 'txt'}[name]
        text = r.p('coverage/grammar/' + name + '.v8.' + suffix).read_text()
        if name == 'CONTRACT':
            text = text.split('## Version4')[0]
            text += ('## Current conditional version9\n\n'
                     'PLAN.v9.json, tools/ac_grammar_runtime_v9.py and '
                     'ADMISSION.v9.json alone authorize this conditional '
                     '14-role coverage. Prior drafts remain preserved and '
                     'unrun. The adapter imports final41-role coverage v7; '
                     'grammar cases, roles and condition instructions are '
                     'unchanged from v8. Builder packet cap1 matches the '
                     'existing strict bound. Original197 packet-clarity '
                     'phases and all original unknown/invalid dispositions '
                     'remain separately visible.\n')
        elif name == 'COORDINATOR-PROMPT':
            text = text.splitlines()[0]
        text = text.replace('v8', 'v9').replace('Version8', 'Version9')
        text = text.replace('coverage/PLAN.v6', 'coverage/PLAN.v7')
        text = text.replace('coverage/CONTRACT.v6', 'coverage/CONTRACT.v7')
        text = text.replace('ac_coverage_runtime_v6', 'ac_coverage_runtime_v7')
        save(r.p('coverage/grammar/' + name + '.v9.' + suffix), text.encode())
    grammar = r.p('tools/ac_grammar_runtime_v8.py').read_text()
    grammar = grammar.replace('v8', 'v9').replace('Version8', 'Version9')
    grammar = grammar.replace('ac_coverage_runtime_v6', 'ac_coverage_runtime_v7')
    save(r.p('tools/ac_grammar_runtime_v9.py'), grammar.encode())
    gpaths = ['coverage/grammar/PLAN.v9.json', 'coverage/grammar/CONTRACT.v9.md',
              'coverage/grammar/COORDINATOR-PROMPT.v9.txt',
              'coverage/grammar/inputs/JG.json', 'tools/ac_grammar_runtime_v9.py']
    save(r.p('coverage/grammar/FREEZE.v9.json'), {
        'utc': now(), 'sources': {str(r.p(p)): sha(r.p(p)) for p in gpaths},
        'prospective_jobs': 14, 'native_calls_at_preparation': 0,
        'status': 'conditional not admitted'})
    from ac_coverage_runtime_v7 import CoverageRuntime
    c = CoverageRuntime()
    c.integrity()
    checks = ['Unique cumulative IDs and valid dependency graph',
              'Original actual coordinator FINAL and all197 terminal',
              'Native budget reserves coverage, grammar and both audits',
              'Original and all inherited/new coverage freezes intact']
    for job in [j for j in new_controls if j['job_id'].startswith('COV-AC07')]:
        if job['role'] == 'proposal':
            delivered = c.payload(job)
            source = r.payload(r.job(job['job_id'].removeprefix('COV-')))
            for key in ['case', 'method', 'fixed_search_budget',
                        'common_analog_source_bank', 'allowed_source_refs', 'candidate_cap']:
                require(delivered[key] == source[key], 'Fresh control input mismatch: ' + key)
            checks.append(job['job_id'] + ': original facts/method/conditions/exposure match')
    delivered = c.payload(none_job)
    source = read(r.p('prompts/AC09-NONE-builder.payload.json'))
    for key in ['case', 'method', 'allowed_source_refs', 'allowed_input_job_refs',
                'candidate_cap', 'word_cap', 'received_handoffs']:
        require(delivered[key] == source[key],
                'Later NONE builder must preserve actual original assigned input: ' + key)
    checks.append('Later AC09 NONE endpoint receives identical actual original case/method/refs/caps/selected handoff')
    for job in [j for j in plan if j['role'] == 'review']:
        require(set(c.payload(job)['actual_chains']) == set(job['dependencies']),
                'Review delivery does not contain every assigned dependency')
    checks.append('All10 later review payloads include their actual current dependency states; new coverage states remain pending')
    save(r.p('coverage/PREFLIGHT.v7.json'), {
        'utc': now(), 'status': 'pass', 'checks': checks,
        'scope': 'Root pure preparation checks; no native output or preflight call',
        'native_calls': 0})
    print(json.dumps({'prepared': True, 'jobs': len(plan), 'projected_calls': projected}))


if __name__ == '__main__':
    main()
