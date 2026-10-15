#!/usr/bin/env python3
"""Prospective literal clarification only; all existing packets stay frozen."""
import argparse, json
from ac_runtime import read, sha, require
from ac_coverage_runtime_v10 import CoverageRuntime as PreviousRuntime


class CoverageRuntime(PreviousRuntime):
    def integrity(self):
        super().integrity()
        for path, digest in read(self.p('coverage/REVIEW-SCHEMA-FREEZE.v12.json'))['sources'].items():
            require(sha(path) == digest, 'Review clarification source drift ' + path)
        return True

    def literal(self, j, v):
        original = super().literal(j, v)
        boundary = read(self.p('coverage/REVIEW-SCHEMA-BOUNDARY.v12.json'))
        if j['job_id'] not in boundary['still_unadmitted_review_ids']:
            return original
        require(j['role'] == 'review', 'Clarification applies only to review roles')
        old = 'All schema keys required, irrelevant selection/method_card/revision use empty defaults.'
        new = ('Emit exactly the six top-level keys in payload.schema: job_id, strategy_id, '
               'arm, case_id, disagreements_preserved, strategy_reviews. No other top-level '
               'keys are allowed. The general empty selection/method_card/revision defaults '
               'apply to other roles only. Keep inspection evidence and coverage limitations '
               'inside the existing strategy_reviews fields; do not add an audit object.')
        require(original.count(old) == 1, 'Expected unchanged common literal')
        require(set(v['schema']) == {'job_id', 'strategy_id', 'arm', 'case_id',
                                    'disagreements_preserved', 'strategy_reviews'},
                'Review schema must remain the original six-key contract')
        return original.replace(old, new)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('command', choices=['ready','status','verify','start','spawned',
        'finish','failed','gate','reserve-overhead','record-overhead'])
    for name in ['job','handle','witness-file','invocation-id','purpose','evidence']:
        ap.add_argument('--' + name)
    ap.add_argument('--outcome', choices=['spawn','error'], default='spawn')
    a = ap.parse_args(); r = CoverageRuntime()
    if a.command == 'status': v = r.coverage_status()
    elif a.command in ['ready','verify']: v = getattr(r, a.command)()
    elif a.command == 'start': v = r.start(a.job)
    elif a.command == 'spawned': v = r.spawned(a.job, a.handle)
    elif a.command == 'finish': v = r.finish(a.job, read(a.witness_file))
    elif a.command == 'failed': v = r.failed(a.job, read(a.witness_file))
    elif a.command == 'gate': v = r.gate(a.job)
    elif a.command == 'reserve-overhead': v = r.reserve_overhead(a.invocation_id,a.purpose)
    else: v = r.record_overhead(a.invocation_id,a.handle,a.purpose,a.evidence,a.outcome)
    print(json.dumps(v, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
