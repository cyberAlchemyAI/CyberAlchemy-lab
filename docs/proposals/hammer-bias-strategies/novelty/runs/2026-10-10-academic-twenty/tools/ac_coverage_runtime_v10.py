#!/usr/bin/env python3
"""Separate ordinary/arrangement coverage; original protocols and grades retained."""
import argparse, hashlib, json
from ac_runtime import read, sha, require, encoded, words
from ac_coverage_runtime_v6 import CoverageRuntime as PriorCoverageRuntime
from ac_coverage_runtime_v3 import CoverageRuntime as CapRuntime

from ac_future_budget import FutureBudgetMixin
class CoverageRuntime(FutureBudgetMixin, PriorCoverageRuntime):
    def start(self, jid):
        require(jid in {j['job_id'] for j in self.coverage_plan()}, 'Later coverage IDs only')
        return self.admit_later(jid)
    def coverage_plan(self):
        return read(self.p('coverage/PLAN.v10.json'))
    def integrity(self):
        super().integrity()
        from ac_runtime_explicit_cap_v2 import Runtime as ExplicitCapRuntime
        ExplicitCapRuntime(self.root).integrity()
        for path, digest in read(self.p('coverage/FREEZE.v10.json'))['sources'].items():
            require(sha(path) == digest, 'Separate coverage v10 source drift ' + path)
        return True
    def finish(self, jid, witness):
        from ac_fidelity_coverage import finish_trial
        out = super().finish(jid, witness)
        finish_trial(self, self.job(jid))
        return out
    def verify(self):
        from ac_fidelity_coverage import verify_trials
        out = super().verify()
        verify_trials(self)
        out['supplementary_adjacent_trial_integrity'] = 'pass'
        return out
    def payload(self, j):
        from ac_review4_coverage import base_job, payload as add_payload
        base = base_job(j)
        v = CapRuntime.payload(self, base) if j['role'] == 'review' else super().payload(base)
        v = add_payload(self, j, v)
        v['job'] = j
        if j.get('post_attack_adjacent_trial'):
            from ac_fidelity_coverage import trial_contract
            v['post_attack_adjacent_trial_contract'] = trial_contract(self, j)
        if j.get('arrangement_coverage'):
            v['comparison_resource_contract'] = {
                'search_slots': 6,
                'proposal_candidate_count': 3,
                'final_builder_candidate_cap': 1,
                'condition': j['arm'],
                'meaning': 'New prospectively matched generation counts; post-original coverage, not an original regrade or equal hidden compute.'}
        if j['role'] == 'review':
            freeze = read(self.p('preparation/FREEZE.v1.json'))
            v['prospective_holdout_provenance'] = {'partition': read(self.p('preparation/HOLDOUT-PARTITIONS.v1.json')), 'freeze_utc': freeze['utc'], 'frozen_case_hashes': {p: h for p, h in freeze['sources'].items() if '/inputs/cases/' in p}, 'case_author_actual_FINAL': read(self.p('receipts/case_design.final.json')), 'scope': 'Recorded prospective freeze before native practice; root access declared, no hidden-read attestation.'}
            v['actual_beneficiary_provenance'] = read(self.p('coverage/ACTUAL-BENEFICIARY-PROVENANCE.v1.json'))
            bank = read(self.p('inputs/analogues.json'))
            v['source_exposure_audit'] = {
                'bank_literal': bank,
                'bank_sha256_canonical': hashlib.sha256(encoded(bank)).hexdigest(),
                'scope': 'Actual recorded assigned packets; not independent attestation of unobserved reads.',
                'roles': {}}
            v['source_exposure_audit']['case_packs'] = {}
            v['source_exposure_audit']['method_packs'] = {}
            for d in j['dependencies']:
                p = self.p('prompts/' + d + '.payload.json')
                if not p.exists():
                    continue
                q = read(p)
                case_digest = hashlib.sha256(encoded(q['case'])).hexdigest()
                method_digest = hashlib.sha256(encoded(q['method'])).hexdigest()
                v['source_exposure_audit']['case_packs'][case_digest] = q['case']
                v['source_exposure_audit']['method_packs'][method_digest] = q['method']
                a = read(self.p('receipts/jobs/' + d + '.admitted.json'))
                v['source_exposure_audit']['roles'][d] = {
                    'actual_payload_sha256': sha(p),
                    'matches_admission_digest': sha(p) == a['payload_sha256'],
                    'common_analog_bank_delivered': 'common_analog_source_bank' in q,
                    'common_analog_bank_sha256_canonical': hashlib.sha256(encoded(q['common_analog_source_bank'])).hexdigest() if 'common_analog_source_bank' in q else None,
                    'candidate_cap': q['candidate_cap'],
                    'word_cap': q['word_cap'],
                    'delivered_case_digest': case_digest,
                    'delivered_method_digest': method_digest,
                    'literal_role_envelope': self.p('prompts/' + d + '.txt').read_text().split('\nPAYLOAD_JSON\n', 1)[0],
                    'literal_prompt_matches_admission': sha(self.p('prompts/' + d + '.txt')) == a['prompt_sha256'],
                    'registered_spawn_observation': read(self.p('receipts/jobs/' + d + '.spawned.json')) if self.p('receipts/jobs/' + d + '.spawned.json').exists() else None,
                    'native_FINAL_observation': read(self.p('receipts/jobs/' + d + '.native-final.json')) if self.p('receipts/jobs/' + d + '.native-final.json').exists() else None,
                    'fixed_search_budget': q.get('fixed_search_budget'),
                    'context_manifest': q.get('context_manifest'),
                    'allowed_source_refs': q['allowed_source_refs'],
                    'allowed_input_job_refs': q['allowed_input_job_refs'],
                    'essential_summary_literal': q.get('essential_summary'),
                    'additional_delivered_packs': {key: q[key] for key in ['routed_sources', 'source_exposure_manifest', 'examples', 'retrieved_card', 'external_state', 'practice_feedback', 'actual_feedback', 'matched_failure_feedback', 'received_criticism', 'criticism_sha256', 'received_opening', 'verified_core', 'actual_beneficiary', 'fixed_pool_sha256'] if key in q},
                    'essential_summary_sha256': hashlib.sha256(q['essential_summary'].encode()).hexdigest() if 'essential_summary' in q else None,
                    'frame_failure_sha256': hashlib.sha256(encoded(q['actual_common_frame_failure'])).hexdigest() if 'actual_common_frame_failure' in q else None,
                    'assigned_instructions': q['job'].get('instructions', ''),
                    'comparison_resource_contract': q.get('comparison_resource_contract'),
                    'method_id': q['job']['method_id']}
        if j['role'] == 'review':
            for d, record in v['actual_chains'].items():
                trial = self.p('replays/' + d + '.adjacent-settings.json')
                if trial.exists():
                    record['post_attack_adjacent_trials'] = read(trial)
                    record['post_attack_adjacent_trial_sha256'] = sha(trial)
        return v
    def literal(self, j, v):
        s = super().literal(j, v)
        if j.get('arrangement_coverage') and j['arm'] == 'FUNCTION':
            s = s.replace('For AC04 create-exclusive sidecar raw/' + j['job_id'] + '.arrangements.json before any function interpretation, then interpret, swap local assembly/interpretation concerns once and record rejected arrangement;',
                'For this AC04 FUNCTION control, state the required function first, then generate exactly three source-supported constructions; do not use an arrangement-first sidecar or role swap;')
            s = s.replace('AC04 reconstruct/swap once if not already recorded; preserve arrangement sidecar provenance.',
                'AC04 FUNCTION preserves function-first provenance and all received constructions; no arrangement-first role swap.')
        return s
    def validate(self, j, v):
        super().validate(j, v)
        from ac_fidelity_coverage import validate_trial
        validate_trial(j, v)
        from ac_review4_coverage import validate as extra_validate
        extra_validate(self, j, v)
        if not j.get('arrangement_coverage'):
            return
        if j['role'] == 'proposal':
            require(len(v['candidates']) == 3, 'Separate AC04 prospectively fixed generation count is three')
            if j['arm'] == 'T':
                side = self.p('raw/' + j['job_id'] + '.arrangements.json')
                require(side.exists(), 'Separate AC04 arrangement sidecar missing')
                require(words(read(side)) <= 400 and words(v) + words(read(side)) <= j['word_cap'], 'Separate AC04 combined output cap')
                require(side.stat().st_mtime_ns <= self.p('raw/' + j['job_id'] + '.json').stat().st_mtime_ns, 'Separate AC04 sidecar save order')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('command', choices=['ready','status','verify','start','spawned','finish','failed','gate','reserve-overhead','record-overhead'])
    for n in ['job','handle','witness-file','invocation-id','purpose','evidence']: ap.add_argument('--'+n)
    ap.add_argument('--outcome', choices=['spawn','error'], default='spawn')
    a=ap.parse_args();r=CoverageRuntime()
    if a.command=='status':v=r.coverage_status()
    elif a.command in ['ready','verify']:v=getattr(r,a.command)()
    elif a.command=='start':v=r.start(a.job)
    elif a.command=='spawned':v=r.spawned(a.job,a.handle)
    elif a.command=='finish':v=r.finish(a.job,read(a.witness_file))
    elif a.command=='failed':v=r.failed(a.job,read(a.witness_file))
    elif a.command=='gate':v=r.gate(a.job)
    elif a.command=='reserve-overhead':v=r.reserve_overhead(a.invocation_id,a.purpose)
    else:v=r.record_overhead(a.invocation_id,a.handle,a.purpose,a.evidence,a.outcome)
    print(json.dumps(v,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
