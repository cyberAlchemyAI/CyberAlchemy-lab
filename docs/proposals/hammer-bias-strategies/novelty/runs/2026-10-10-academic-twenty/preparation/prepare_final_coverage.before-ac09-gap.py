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
        'Version7 adds six fresh AC07 OLD/BREADTH roles to the unrun v6 '
        'package, for28 dispositions: six ordinary, six matched-count AC04, '
        'six AC07 controls and ten independent reviews. Original control '
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
        '28 new scheduled dispositions. The native-call ceiling is260 '
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
    prompt = prompt.replace('v6', 'v7').replace('twenty-two', 'twenty-eight').replace('all22', 'all28')
    prompt += ('\nFinal version7 includes28 actual roles; PLAN.v7.json is authoritative. '
               'Its extra six AC07 OLD/BREADTH roles are separately admitted '
               'controls, not original retries. Preserve original cap failures '
               'and all original reviewer grades. Read GAP-ADMISSION.v7.json '
               'and the primary CAP-CLARIFICATION-AMENDMENT.v2.md.\n')
    save(r.p('coverage/COORDINATOR-PROMPT.v7.txt'), prompt.encode())
    adapter = r.p('tools/ac_coverage_runtime_v6.py').read_text()
    adapter = adapter.replace('from ac_coverage_runtime_v5 import',
                              'from ac_coverage_runtime_v6 import')
    adapter = adapter.replace('PLAN.v6', 'PLAN.v7').replace('FREEZE.v6', 'FREEZE.v7')
    adapter = adapter.replace('coverage v6 source drift', 'coverage v7 source drift')
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
    paths = ['coverage/PLAN.v7.json', 'coverage/GAP-ADMISSION.v7.json', 'coverage/ADDITIONAL-GAPS.v2.json',
             'coverage/CONTRACT.v7.md', 'coverage/COORDINATOR-PROMPT.v7.txt',
             'tools/ac_coverage_runtime_v7.py', 'tools/prepare_final_coverage.py']
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
                     'unrun. The adapter imports final28-role coverage v7; '
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
    for job in new_controls:
        if job['role'] == 'proposal':
            delivered = c.payload(job)
            source = r.payload(r.job(job['job_id'].removeprefix('COV-')))
            for key in ['case', 'method', 'fixed_search_budget',
                        'common_analog_source_bank', 'allowed_source_refs', 'candidate_cap']:
                require(delivered[key] == source[key], 'Fresh control input mismatch: ' + key)
            checks.append(job['job_id'] + ': original facts/method/conditions/exposure match')
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
