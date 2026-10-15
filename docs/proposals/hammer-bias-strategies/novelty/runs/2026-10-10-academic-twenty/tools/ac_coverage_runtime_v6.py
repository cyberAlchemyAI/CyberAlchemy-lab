#!/usr/bin/env python3
"""Separate ordinary/arrangement coverage; original protocols and grades retained."""
import argparse, hashlib, json
from ac_runtime import read, sha, require, encoded, words
from ac_coverage_runtime_v5 import CoverageRuntime as PriorCoverageRuntime
from ac_coverage_runtime_v3 import CoverageRuntime as CapRuntime

class CoverageRuntime(PriorCoverageRuntime):
    def coverage_plan(self):
        return read(self.p('coverage/PLAN.v6.json'))
    def integrity(self):
        super().integrity()
        for path, digest in read(self.p('coverage/FREEZE.v6.json'))['sources'].items():
            require(sha(path) == digest, 'Separate coverage v6 source drift ' + path)
        return True
    def payload(self, j):
        v = CapRuntime.payload(self, j) if j['role'] == 'review' else super().payload(j)
        if j.get('arrangement_coverage'):
            v['comparison_resource_contract'] = {
                'search_slots': 6,
                'proposal_candidate_count': 3,
                'final_builder_candidate_cap': 1,
                'condition': j['arm'],
                'meaning': 'New prospectively matched generation counts; post-original coverage, not an original regrade or equal hidden compute.'}
        if j['role'] == 'review':
            bank = read(self.p('inputs/analogues.json'))
            v['source_exposure_audit'] = {
                'bank_literal': bank,
                'bank_sha256_canonical': hashlib.sha256(encoded(bank)).hexdigest(),
                'scope': 'Actual recorded assigned packets; not independent attestation of unobserved reads.',
                'roles': {}}
            for d in j['dependencies']:
                p = self.p('prompts/' + d + '.payload.json')
                if not p.exists():
                    continue
                q = read(p)
                a = read(self.p('receipts/jobs/' + d + '.admitted.json'))
                v['source_exposure_audit']['roles'][d] = {
                    'actual_payload_sha256': sha(p),
                    'matches_admission_digest': sha(p) == a['payload_sha256'],
                    'common_analog_bank_delivered': 'common_analog_source_bank' in q,
                    'common_analog_bank_sha256_canonical': hashlib.sha256(encoded(q['common_analog_source_bank'])).hexdigest() if 'common_analog_source_bank' in q else None,
                    'candidate_cap': q['candidate_cap'],
                    'assigned_instructions': q['job'].get('instructions', ''),
                    'comparison_resource_contract': q.get('comparison_resource_contract'),
                    'method_id': q['job']['method_id']}
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
