#!/usr/bin/env python3
"""Prospective literal handoff study from actual closed sources; zero model calls."""
import copy, hashlib, json
from ac_runtime import ROOT, read, save, sha, require, now, encoded, words
from ac_source_completion_runtime_v17 import Runtime as PreviousRuntime
from ac_provenance_fidelity_runtime_v18 import Runtime

def main():
    prev = PreviousRuntime()
    verification = prev.verify()
    require(verification['status'] == 'pass' and all(prev.state(j['job_id'])['terminal'] for j in prev.plan()), 'Earlier actual phases must be closed and intact')
    r = Runtime()
    prefix = 'coverage/provenance-fidelity/'
    pools = ['AC20-PRE-implementation', 'COV-AC20-PRE-service']
    routes = {
        'SHARED': ['COV-SOURCE-LATER-SHARED-route0', 'COV-SOURCE-LATER-SHARED-route1'],
        'DISTINCT': ['COV-SOURCE-LATER-DISTINCT-route0', 'COV-SOURCE-LATER-DISTINCT-route1'],
        'UNION': ['COV-AC20-UNION-route0', 'COV-AC20-UNION-route1']}
    sources = []
    capsule_counts = {}
    case = read(r.p('inputs/cases/J0.json'))
    for arm, ids in routes.items():
        capsule = {'case_sha256_canonical_encoded': hashlib.sha256(encoded(case)).hexdigest(), 'pools': [], 'source_routes': []}
        for jid in pools + ids:
            require(prev.state(jid)['valid'], 'Actual valid precursor required: ' + jid)
            raw_path = r.p('raw/' + jid + '.json'); body = read(raw_path)
            capsule['pools'].append({'job_id': jid, 'raw_sha256': sha(raw_path), 'candidates': body['candidates'], 'source_limits': body['limits'], 'handoff_residue': body['handoff'].get('residue')})
            sources.append(raw_path)
        for jid in ids:
            path = r.p('prompts/' + jid + '.payload.json'); packet = read(path)
            banks = []
            for key, bank in packet['routed_sources'].items():
                original = bank['original_path']; sources.append(original)
                banks.append({'selector_key': key, 'source_id': bank['id'], 'original_path': original, 'original_selector': bank['original_selector'], 'original_file_sha256': sha(original), 'body_sha256_canonical_encoded': hashlib.sha256(encoded(bank['body'])).hexdigest()})
            capsule['source_routes'].append({'job_id': jid, 'payload_sha256': sha(path), 'source_banks': banks, 'source_exposure_manifest': packet['source_exposure_manifest'], 'forwarded_source_provenance': packet['forwarded_source_provenance']})
            sources.append(path)
        require(sum(len(p['candidates']) for p in capsule['pools']) == 12, 'Four actual three-candidate pools required')
        save(r.p(prefix + 'capsules/' + arm + '.json'), capsule)
        capsule_counts[arm] = words(capsule)
    cap = 10000
    require(max(capsule_counts.values()) + 3500 < cap, 'Literal capsule and bounded construction must fit')
    plan = []
    literal = (' Separate prospective provenance transmission study. Preserve earlier incomplete handoffs and first grades unchanged. '
               'Inside the existing handoff.summary string encode a JSON object with EXACTLY capsule, construction, audit, limits. '
               'capsule is the complete required literal object, copied without altering ANY value; construction and audit are nonempty strings, limits is a nonempty list. '
               'Use Python to parse the payload and preserve the literal capsule instead of manually retyping arrays. '
               'All12 precursor candidates, source selectors/hashes, limits and route identities must survive. '
               'The larger10000-word cap supports transmission only, not matched efficacy or compute. Six search slots, no new source bank, unchanged J0 facts. '
               'Allowed useful source-bound refusals and known constructions need no novelty claim. No earlier incomplete exchange/builder output is supplied. '
               'Exactly13 top-level schema keys; no extra pools/provenance fields. Candidate cap3 exchange,1 builder. One exclusive first save, no retry or correction.')
    for arm, ids in routes.items():
        template_arm = arm if arm != 'UNION' else 'SHARED'
        for role in ['exchange', 'builder']:
            template = prev.job('COV-SOURCE-LATER-' + template_arm + '-' + role)
            j = copy.deepcopy(template)
            j.update(job_id='COV-PROVENANCE-' + arm + '-' + role, arm=arm,
                     provenance_fidelity_coverage=True, source_completion_coverage=False,
                     word_cap=cap, instructions=literal)
            j['dependencies'] = pools + ids if role == 'exchange' else ['COV-PROVENANCE-' + arm + '-exchange']
            j['instructions'] += (' Read required_transmission_capsule from this exchange payload; it is a frozen literal preservation target, not a proposed answer.' if role == 'exchange' else
                ' Receive only this exchange selected summary and common J0 facts. Parse capsule from received_handoffs; do not read expected capsule files or upstream raw/payload files. Retain it exactly in your selected summary while producing your own bounded reconstruction/audit. No independent source exposure is implied by hashes.')
            plan.append(j)
    extra = [j['job_id'] for j in plan]
    for n in [1, 2]:
        j = copy.deepcopy(prev.job('COV-REVIEW-5-SOURCE-POST-' + str(n)))
        j.update(job_id='COV-REVIEW-5-PROVENANCE-' + str(n), provenance_fidelity_coverage=True, source_completion_coverage=False)
        j['dependencies'] += extra
        j['instructions'] += (' Separately assess six new provenance exchange/builder roles against immutable incomplete selected summaries. '
            'Check all12 arrays, identity-qualified precursor nodes, selectors/body/file hashes, unknowns and actual builder summary-only received payload. '
            'Literal transmission is a different operation from discovering an unknown mechanism. Construction/source pools and J0 facts are unchanged. '
            'All6 roles have larger10000-word transport caps; original/source comparisons retain their caps and grades. '
            'Assess whether full AC20 agent handoff procedure is now actually executed, without converting it into source-diversity benefit. '
            'Preserve AC17–19 earlier semantic limitations and actual disputes; source-bound absence of required object is not an invented positive result.')
        plan.append(j)
    save(r.p(prefix + 'PLAN.v18.json'), plan)
    observation = r.p('receipts/HANDOFF-GOAL-SCOPE-OBSERVATION.v1.json')
    goal = read(observation)['actual_result']['goal']
    require(goal['status'] == 'active' and 'tokenBudget' not in goal, 'Actual active unbudgeted goal observation required')
    save(r.p('coverage/BUDGET-AMENDMENT.v2.json'), {'utc': now(), 'authority': 'root-authored prospective protocol', 'original_root_protocol_ceiling': 260, 'previous_later_cumulative_ceiling': 300, 'later_cumulative_ceiling': 310, 'existing_actual_call_count': len(prev.invocations()), 'prospective_total_with_eight_roles_and_two_audits': len(prev.invocations()) + 10, 'goal_observation_path': str(observation), 'goal_observation_sha256': sha(observation), 'reason': 'Actual independent source reviews identified missing full precursor arrays/provenance in selected summaries of all three source arms; separately admitted six transmission/construction roles and two reviews complete handoff coverage.', 'previous_budgets_plans_first_outputs_reviews_unchanged': True})
    gap = {'utc': now(), 'observation': 'actual_source_review_gap_not_positive_novelty_requirement', 'evidence': ['raw/COV-REVIEW-5-SOURCE-POST-1.json', 'raw/COV-REVIEW-5-SOURCE-POST-2.json'], 'roles': 8, 'word_cap_all_exchange_builder': cap, 'capsule_normalized_words': capsule_counts, 'preservation_target': 'All12 full candidate objects from four actual pools, literal unknown/limits, actual source allocation/file/selector/body hashes and route identities', 'scope': 'Prospective summary transmission; precursor/route stages reused, no new full search experiment or field data', 'prior_first_results_unchanged': True}
    save(r.p(prefix + 'GAP.v18.json'), gap)
    contract = '# Provenance fidelity coverage v18\n\nEight fresh native roles: SHARED/DISTINCT/UNION exchange and summary-only builder, then two independent reviews. All12 candidate objects and source allocation provenance must survive inside the existing selected summary. Original incomplete handoffs, invalids and independent grades remain immutable. Root freezes a literal preservation capsule; only exchanges receive the target, while builders receive only the actual exchange summary and common J0 facts. This tests explicit transmission and external artifact retention, not spontaneous discovery, human retention, independent empirical datasets, equal compute or creative benefit. Six search slots and original schema/candidate bounds remain; all six exchanges/builders have an explicitly larger10000-word transmission cap. The separately declared root-owned later ceiling310 prospectively follows immutable260 and300 ceilings; actual native goal is unbudgeted.\n'
    save(r.p(prefix + 'CONTRACT.v18.md'), contract.encode())
    probes = []
    for j in plan[:6]:
        capsule = read(r.p(prefix + 'capsules/' + j['arm'] + '.json'))
        summary = {'capsule': capsule, 'construction': 'Pure fixture only', 'audit': 'Pure fixture only', 'limits': ['Unrun native role']}
        text = json.dumps(summary)
        v = {'handoff': {'summary': text}}
        r.validate_summary(j, v, text if j['role'] == 'builder' else None)
        bad = copy.deepcopy(v); s = json.loads(bad['handoff']['summary']); s['capsule']['pools'][0]['candidates'] = []; bad['handoff']['summary'] = json.dumps(s)
        rejected = False
        try: r.validate_summary(j, bad, text if j['role'] == 'builder' else None)
        except Exception: rejected = True
        require(rejected, 'Missing literal candidate array must be rejected')
        if j['role'] == 'builder':
            try: r.validate_summary(j, v, bad['handoff']['summary'])
            except Exception: pass
            else: raise ValueError('Actually received capsule mismatch must reject')
        probes.append({'job_id': j['job_id'], 'literal_capsule_pass': True, 'array_loss_rejected': True, 'normalized_summary_words': words(v)})
    b = r.budget(); require(b['prospective_total'] == 301 and b['prospective_total'] <= b['ceiling'], 'Actual301 projection required')
    save(r.p(prefix + 'PREFLIGHT.v18.json'), {'status': 'pass', 'utc': now(), 'model_calls': 0, 'literal_probes': probes, 'previous_verification': verification, 'budget': b, 'prior_admitted_role_count': len(prev.plan()), 'planned_new_roles': 8, 'no_new_native_admission': True})
    sources += [r.p(prefix + x) for x in ['PLAN.v18.json','GAP.v18.json','CONTRACT.v18.md','PREFLIGHT.v18.json']]
    sources += list(r.p(prefix + 'capsules').glob('*.json'))
    sources += [r.p('coverage/BUDGET-AMENDMENT.v2.json'), observation, r.p('tools/ac_provenance_fidelity_runtime_v18.py'), r.p('tools/prepare_ac_provenance_v18.py')]
    save(r.p(prefix + 'FREEZE.v18.json'), {'utc': now(), 'sources': {str(p): sha(p) for p in dict.fromkeys(sources)}, 'native_execution_unrun_at_freeze': True, 'earlier_sources_bound_by_inherited_freezes': True})
    r.integrity()
    save(r.p(prefix + 'ADMISSION.v18.json'), {'utc': now(), 'admit': True, 'observation': 'actual_closed_source_evidence_and_root_pure_preflight', 'previous_source_closure_path': 'receipts/SOURCE-COMPLETION-CLOSURE.v17.json', 'previous_source_closure_sha256': sha(r.p('receipts/SOURCE-COMPLETION-CLOSURE.v17.json')), 'previous_all_admitted_terminal': True, 'previous_integrity': verification, 'preflight_sha256': sha(r.p(prefix + 'PREFLIGHT.v18.json')), 'freeze_sha256': sha(r.p(prefix + 'FREEZE.v18.json')), 'budget': b, 'calls_before_admission': len(prev.invocations())})
    print(json.dumps({'admitted': True, 'new_roles': 8, 'capsule_words': capsule_counts, 'cap': cap, 'budget': b}))

if __name__ == '__main__': main()
