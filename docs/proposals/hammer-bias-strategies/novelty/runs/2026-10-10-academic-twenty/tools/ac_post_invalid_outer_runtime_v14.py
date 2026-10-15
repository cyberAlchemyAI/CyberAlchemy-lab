#!/usr/bin/env python3
import json,argparse
from ac_runtime import read
from ac_post_invalid_runtime_v13 import Runtime as PreviousPost
from ac_grammar_outer_runtime_v14 import GrammarRuntime
from ac_outer_review_runtime_v14 import replace_outer
from ac_coverage_runtime_v10 import CoverageRuntime as OriginalLiteralRuntime

class Runtime(PreviousPost,GrammarRuntime):
    def literal(self,j,v):
        if j['job_id'] not in {q['job_id'] for q in self.post_invalid_plan()}:
            return super().literal(j,v)
        original=OriginalLiteralRuntime.literal(self,j,v)
        if j['role']=='review':
            clarity=('Emit exactly the six top-level keys in payload.schema: job_id, '
                     'strategy_id, arm, case_id, disagreements_preserved, strategy_reviews. '
                     'No extra default, inspection or audit objects. Copy all four identity '
                     'values from payload.job. Put inspection evidence in the existing review '
                     'row fields. Preserve earlier invalid rows as unadmitted observations.')
        else:
            clarity=('Emit exactly all top-level keys in payload.schema, including job_id. '
                     'Copy job_id, strategy_id, arm and case_id from payload.job. Irrelevant '
                     'selection/method_card/revision use empty defaults. Check the complete '
                     'key set before the one exclusive first save; no output repair or retry.')
        return ('This bounded role is self-contained: all required task facts and procedures '
                'are in this packet and its explicitly allowed review sources. Workspace '
                'memories and unrelated history are irrelevant; read this packet first.\n'
                +replace_outer(original,clarity))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['status','verify','start','spawned','finish','failed','gate','reserve-overhead','record-overhead'])
    for n in ['job','handle','witness-file','invocation-id','purpose','evidence']:ap.add_argument('--'+n)
    ap.add_argument('--outcome',choices=['spawn','error'],default='spawn');a=ap.parse_args();r=Runtime()
    if a.command=='status':v=r.post_invalid_status()
    elif a.command=='verify':v=r.verify()
    elif a.command=='start':v=r.start(a.job)
    elif a.command=='spawned':v=r.spawned(a.job,a.handle)
    elif a.command=='finish':v=r.finish(a.job,read(a.witness_file))
    elif a.command=='failed':v=r.failed(a.job,read(a.witness_file))
    elif a.command=='gate':v=r.gate(a.job)
    elif a.command=='reserve-overhead':v=r.reserve_overhead(a.invocation_id,a.purpose)
    else:v=r.record_overhead(a.invocation_id,a.handle,a.purpose,a.evidence,a.outcome)
    print(json.dumps(v,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
