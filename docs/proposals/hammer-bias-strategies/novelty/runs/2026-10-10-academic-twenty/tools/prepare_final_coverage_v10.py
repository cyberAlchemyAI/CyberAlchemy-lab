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
    from ac_review4_coverage import jobs as review4_jobs, HELPER_SOURCES
    review4 = review4_jobs(r)
    new_controls += review4
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
    require(read(r.p('receipts/future-coverage-design.final.json'))['observation'] == 'actual_FINAL', 'Actual unscored coverage design FINAL required')
    projected = len(r.invocations()) + len(plan) + 1 + 14 + 1 + 2
    require(projected <= 300, 'Coverage plus coordinators, grammar and audits exceed ceiling')
    save(r.p('coverage/PLAN.v10.json'), plan)
    save(r.p('coverage/GAP-ADMISSION.v10.json'), {
        'utc': now(), 'status': 'prospective separate coverage, no native call',
        'evidence': evidence, 'new_roles': [j['job_id'] for j in new_controls],
        'original_first_reviews': [j['job_id'] for j in original if j['role'] == 'review'],
        'original_reviews_preserved': True,
        'prospective_native_total_including_grammar_and_audits': projected,
        'ceiling': 300})
    contract = (
        '# Separate ordinary, arrangement and missing-control coverage, version10\n\n'
        'Version10 adds six fresh AC07 OLD/BREADTH roles and one later '
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
        'CONTRACT.v6.md for provenance; PLAN.v10.json alone defines the '
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
    contract = ('# Separately admitted comparison coverage, version10\n\n'
        + f'PLAN.v10.json defines {len(plan)} new scheduled dispositions, including ten independent later reviews. '
        + 'Original197 dispositions, all first bytes, original reviewer judgments and unrun versions2–6 remain unchanged. '
        + 'This separate phase includes ordinary baselines, prospectively matched-count arrangement conditions, missing control endpoints, the twelve REVIEW3 fidelity roles, and the newly declared REVIEW4/5 comparisons. '
        + 'Read GAP-ADMISSION.v10.json, ADDITIONAL-GAPS.v5.json and REVIEW4-COVERAGE-DESIGN.v1.md for exact scope. '
        + 'New roles can reuse unchanged valid upstream handoffs only when their plan explicitly declares this. Such later endpoints are not full reruns or retroactive repairs. '
        + 'The original packet cap clarification has two preserved phases (61 closed roles and132 then-unadmitted roles). Later builder/transfer cap1 agrees with the existing strict role requirement.\n\n'
        + 'All inherited first-save, actual FINAL, word/reference, sidecar, source exposure and two-worker requirements apply. Root owns this prospective protocol. '
        + 'BUDGET-AMENDMENT.v1.json authorizes a300 cumulative call ceiling for the later phase; the original root-authored260 bound and original plan remain historical. '
        + f'The present projection is{projected} actual/admitted calls including the conditional14-role grammar phase, both later coordinators and two completion auditors. '
        + 'No user-imposed token/call budget was supplied. The native goal is unbudgeted; changing this root plan completes the already-authorized comparison scope. '
        + 'Every failed native tool attempt counts, including the two root capacity errors and this unscored design role. The errors arose while all four concurrent slots were occupied and establish no permanent resource exhaustion.\n\n'
        + 'Application, feasible outcome, final addition, full-upstream novelty, burden and learning are distinct. Honest no-tension outcomes and supported applicability refusals remain visible; no case is fabricated to force a positive application judgment. '
        + 'Later reviewer packets contain admission-bound literal case/method/role envelopes, actual FINALs, banks/cards/feedback and prospective holdout provenance. These witnesses attest recorded workflow, not hidden reads or platform-authenticated history. '
        + 'The paired AC04 study fixes three proposal constructions and six search slots per arm. AC16 later older practice uses the same curriculum opportunities and a declared earlier retained procedure; no fresh role has trained weights. '
        + 'AC17 later attack precedes new fresh heldout applications, while the original omitted attack stays omitted. Heldout repeats use the same frozen cases with fresh actors and are not new unseen cases for root. '
        + 'AC20 later routes reuse the unchanged valid pre-assistance implementation and a separately admitted service precursor, followed by actual shared/distinct/union routes. Original failed/gated chains and unavailable source-diversity comparisons remain unchanged.\n')
    save(r.p('coverage/CONTRACT.v10.md'), contract.encode())
    prompt = (f"Execute only the{len(plan)} separately admitted dispositions in coverage/PLAN.v10.json. Read coverage/CONTRACT.v10.md, GAP-ADMISSION.v10.json, ADDITIONAL-GAPS.v5.json, REVIEW4-COVERAGE-DESIGN.v1.md and BUDGET-AMENDMENT.v1.json. Use python3 tools/ac_coverage_runtime_v10.py ready/start/spawned/finish/gate/status/verify from this run directory. The start command creates an exclusive prompt and pre-call reservation; actually call collaboration.spawn_agent with fork_turns none using its returned task_name/message. Register only the literal actual returned handle; record actual call errors with failed and a literal witness. At most two scored children live under root plus coordinator. Do not call any helper agent. Wait for actual FINAL; write its exact text, observed actual handle and observation actual_FINAL in an exclusive receipts/jobs/<ID>.coordinator-witness.json, then finish through the adapter. Its first-byte locks and supplementary post-attack adjacent model trials are required. Read output keys and honest invalid dispositions, never repair/retry or overwrite first bytes. Original197 is closed and immutable. No changes to cases, method, role schema, dependencies, score, cap, budget or scope are authorized. Preserve all failed/gated originals and first reviewer disagreement. Do not admit grammar jobs or completion auditors. Run until all75 planned dispositions are terminal, observing actual native FINALs. Verify source/first-byte/admission/ledger locks, then save exclusive receipts/COORDINATOR-CLOSURE.v10.json with exact status, verify, actual native invocation counts, failures/gates, limitations and updated ledger scope. Return an actual FINAL explaining closure and any unavailable comparison. Communicate meaningful actual progress to root; no model-call simulation or unsupported completion. Read the script CLI if witness flags need clarification.")
    prompt = prompt.replace('all75', 'all'+str(len(plan)))
    save(r.p('coverage/COORDINATOR-PROMPT.v10.txt'), prompt.encode())
    adapter = r.p('tools/ac_coverage_runtime_v6.py').read_text()
    adapter = adapter.replace('from ac_coverage_runtime_v5 import',
                              'from ac_coverage_runtime_v6 import')
    adapter = adapter.replace('PLAN.v6', 'PLAN.v10').replace('FREEZE.v6', 'FREEZE.v10')
    adapter = adapter.replace('coverage v6 source drift', 'coverage v10 source drift')
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
    adapter = adapter.replace('class CoverageRuntime(PriorCoverageRuntime):',
        'from ac_future_budget import FutureBudgetMixin\nclass CoverageRuntime(FutureBudgetMixin, PriorCoverageRuntime):')
    adapter = adapter.replace('    def coverage_plan(self):',
        "    def start(self, jid):\n        require(jid in {j['job_id'] for j in self.coverage_plan()}, 'Later coverage IDs only')\n        return self.admit_later(jid)\n    def coverage_plan(self):",1)
    adapter = adapter.replace('        v = CapRuntime.payload(self, j) if',
        '        from ac_review4_coverage import base_job, payload as add_payload\n        base = base_job(j)\n        v = CapRuntime.payload(self, base) if',1)
    adapter = adapter.replace("else super().payload(j)\n", "else super().payload(base)\n        v = add_payload(self, j, v)\n        v['job'] = j\n",1)
    adapter = adapter.replace('        validate_trial(j, v)\n',
        '        validate_trial(j, v)\n        from ac_review4_coverage import validate as extra_validate\n        extra_validate(self, j, v)\n',1)
    adapter = adapter.replace("        if j['role'] == 'review':\n            bank =", "        if j['role'] == 'review':\n            freeze = read(self.p('preparation/FREEZE.v1.json'))\n            v['prospective_holdout_provenance'] = {'partition': read(self.p('preparation/HOLDOUT-PARTITIONS.v1.json')), 'freeze_utc': freeze['utc'], 'frozen_case_hashes': {p: h for p, h in freeze['sources'].items() if '/inputs/cases/' in p}, 'case_author_actual_FINAL': read(self.p('receipts/case_design.final.json')), 'scope': 'Recorded prospective freeze before native practice; root access declared, no hidden-read attestation.'}\n            v['actual_beneficiary_provenance'] = read(self.p('coverage/ACTUAL-BENEFICIARY-PROVENANCE.v1.json'))\n            bank =",1)
    save(r.p('tools/ac_coverage_runtime_v10.py'), adapter.encode())
    save(r.p('coverage/ADDITIONAL-GAPS.v5.json'), {
        'utc': now(), 'status': 'prospective separate coverage; no native scored call',
        'earlier_gap_inventory': 'coverage/ADDITIONAL-GAPS.v4.json',
        'actual_review_evidence': {n: {'raw_sha256': sha(r.p('raw/'+n+'.json')), 'native_FINAL_sha256': sha(r.p('receipts/jobs/'+n+'.native-final.json')), 'state': r.state(n)} for n in ['REVIEW-4-1','REVIEW-4-2','REVIEW-5-1','REVIEW-5-2']},
        'declared_extra_roles': [j['job_id'] for j in review4],
        'immutable_original_ac20_service_state': r.state('AC20-PRE-service'),
        'original_all197_terminal': True, 'first_grades_preserved': True,
        'prospective_native_total': projected, 'later_cumulative_ceiling': 300})
    goal = read(r.p('receipts/GOAL-SCOPE-BUDGET-OBSERVATION.v1.json'))
    require(goal['observation'] == 'actual_get_goal_tool_result', 'Actual native goal observation required')
    require(goal['result']['remainingTokens'] is None, 'Unexpected explicit native token budget')
    save(r.p('coverage/BUDGET-AMENDMENT.v1.json'), {
        'utc': now(), 'authority': 'root-authored prospective protocol',
        'original_root_protocol_ceiling': 260, 'later_cumulative_ceiling': 300,
        'reason': 'Actual first independent reviews identified missing method/control clauses and AC20 failed precursor; separately admitted coverage and audits complete the already-authorized scope.',
        'goal_observation_path': 'receipts/GOAL-SCOPE-BUDGET-OBSERVATION.v1.json',
        'goal_observation_sha256': sha(r.p('receipts/GOAL-SCOPE-BUDGET-OBSERVATION.v1.json')),
        'prospective_total_with_grammar_and_two_audits': projected,
        'existing_actual_call_count': len(r.invocations()),
        'original_plan_contract_outputs_and_reviews_unchanged': True})
    paths = ['coverage/PLAN.v10.json' , 'coverage/GAP-ADMISSION.v10.json', 'coverage/ADDITIONAL-GAPS.v4.json',
             'coverage/CONTRACT.v10.md', 'coverage/COORDINATOR-PROMPT.v10.txt',
             'tools/ac_coverage_runtime_v10.py', 'tools/prepare_final_coverage_v10.py',
             'tools/ac_fidelity_coverage.py', 'tools/ac_review4_coverage.py', 'tools/ac_future_budget.py', 'coverage/REVIEW4-COVERAGE-DESIGN.v1.md', 'coverage/ADDITIONAL-GAPS.v5.json', 'coverage/BUDGET-AMENDMENT.v1.json', 'coverage/ACTUAL-BENEFICIARY-PROVENANCE.v1.json', 'receipts/future-coverage-design.final.json', 'receipts/GOAL-SCOPE-BUDGET-OBSERVATION.v1.json'] + list(HELPER_SOURCES)
    save(r.p('coverage/FREEZE.v10.json'), {
        'utc': now(), 'sources': {str(r.p(p)): sha(r.p(p)) for p in paths},
        'prospective_jobs': len(plan), 'native_calls_at_preparation': 0})
    # This remains conditional preparation. Admission needs actual review
    # evidence and closure of the separately executed control coverage.
    for name in ['PLAN', 'CONTRACT', 'COORDINATOR-PROMPT']:
        suffix = {'PLAN': 'json', 'CONTRACT': 'md', 'COORDINATOR-PROMPT': 'txt'}[name]
        text = r.p('coverage/grammar/' + name + '.v8.' + suffix).read_text()
        if name == 'CONTRACT':
            text = text.split('## Version4')[0]
            text += ('## Current conditional version11\n\n'
                     'PLAN.v11.json, tools/ac_grammar_runtime_v11.py and '
                     'ADMISSION.v11.json alone authorize this conditional '
                     '14-role coverage. Prior drafts remain preserved and '
                     'unrun. The adapter imports final dynamic-count coverage v10; '
                     'grammar cases, roles and condition instructions are '
                     'unchanged from v8. Builder packet cap1 matches the '
                     'existing strict bound. Original197 packet-clarity '
                     'phases and all original unknown/invalid dispositions '
                     'remain separately visible.\n')
        elif name == 'COORDINATOR-PROMPT':
            text = text.splitlines()[0]
        text = text.replace('v8', 'v11').replace('Version8', 'Version11')
        text = text.replace('coverage/PLAN.v6', 'coverage/PLAN.v10')
        text = text.replace('coverage/CONTRACT.v6', 'coverage/CONTRACT.v10')
        text = text.replace('ac_coverage_runtime_v6', 'ac_coverage_runtime_v10')
        save(r.p('coverage/grammar/' + name + '.v11.' + suffix), text.encode())
    grammar = r.p('tools/ac_grammar_runtime_v8.py').read_text()
    grammar = grammar.replace('v8', 'v11').replace('Version8', 'Version11')
    grammar = grammar.replace('ac_coverage_runtime_v6', 'ac_coverage_runtime_v10')
    grammar = grammar.replace('from ac_runtime import Runtime\n        out=Runtime.start(self,jid)', 'from ac_future_budget import FutureBudgetMixin\n        out=FutureBudgetMixin.admit_later(self,jid)')
    save(r.p('tools/ac_grammar_runtime_v11.py'), grammar.encode())
    gpaths = ['coverage/grammar/PLAN.v11.json', 'coverage/grammar/CONTRACT.v11.md',
              'coverage/grammar/COORDINATOR-PROMPT.v11.txt',
              'coverage/grammar/inputs/JG.json', 'tools/ac_grammar_runtime_v11.py']
    save(r.p('coverage/grammar/FREEZE.v11.json'), {
        'utc': now(), 'sources': {str(r.p(p)): sha(r.p(p)) for p in gpaths},
        'prospective_jobs': 14, 'native_calls_at_preparation': 0,
        'status': 'conditional not admitted'})
    from ac_coverage_runtime_v10 import CoverageRuntime
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
    save(r.p('coverage/PREFLIGHT.v10.json'), {
        'utc': now(), 'status': 'pass', 'checks': checks,
        'scope': 'Root pure preparation checks; no native output or preflight call',
        'native_calls': 0})
    print(json.dumps({'prepared': True, 'jobs': len(plan), 'projected_calls': projected}))


if __name__ == '__main__':
    main()
