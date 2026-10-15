#!/usr/bin/env python3
"""Separate source-comparison coverage; every earlier failure remains locked."""
import argparse,json
from ac_runtime import read,sha,require
from ac_post_invalid_complete_runtime_v15 import Runtime as PreviousRuntime
from ac_future_budget import FutureBudgetMixin
from ac_coverage_runtime_v10 import CoverageRuntime as OriginalLiteralRuntime
from ac_outer_review_runtime_v14 import replace_outer,REVIEW

class Runtime(PreviousRuntime):
    def source_completion_plan(self):return read(self.p('coverage/source-completion/PLAN.v16.json'))
    def coverage_plan(self):return super().coverage_plan()+self.source_completion_plan()
    def integrity(self):
        super().integrity()
        for path,digest in read(self.p('coverage/source-completion/FREEZE.v16.json'))['sources'].items():
            require(sha(path)==digest,'Source comparison source drift '+path)
        return True
    def literal(self,j,v):
        if j['job_id'] in {q['job_id'] for q in self.source_completion_plan()} and j['role']=='review':
            return replace_outer(OriginalLiteralRuntime.literal(self,j,v),REVIEW)
        return super().literal(j,v)
    def payload(self,j):
        v=super().payload(j)
        if j['job_id'] in {q['job_id'] for q in self.source_completion_plan()}:
            v['source_comparison_context']=read(self.p('coverage/source-completion/GAP.v16.json'))
        return v
    def start(self,jid):
        require(jid in {j['job_id'] for j in self.source_completion_plan()},'Source completion IDs only')
        previous=PreviousRuntime(self.root)
        require(all(previous.state(j['job_id'])['terminal'] for j in previous.plan()),'All actual earlier admitted phases must close first')
        require(read(self.p('coverage/source-completion/ADMISSION.v16.json'))['admit'] is True,'Actual-evidence source-comparison admission required')
        require(read(self.p('receipts/POST-INVALID-CLOSURE.v13.json'))['all_five_terminal'] is True,'Actual five-role root closure required')
        out=FutureBudgetMixin.admit_later(self,jid)
        out['task_name']='acsource_'+str([j['job_id'] for j in self.source_completion_plan()].index(jid))
        return out
    def source_completion_status(self):
        ss={j['job_id']:self.state(j['job_id']) for j in self.source_completion_plan()}
        return {'counts':{k:sum(s['disposition']==k for s in ss.values()) for k in ['pending','admitted','spawned','finished','failed','gated']},'valid_finished':sum(s['valid'] for s in ss.values()),'terminal':all(s['terminal'] for s in ss.values()),'budget':self.budget(),'ready':{k:[j for j in v if j in ss] for k,v in self.ready().items()}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['status','verify','start','spawned','finish','failed','gate','reserve-overhead','record-overhead'])
    for n in ['job','handle','witness-file','invocation-id','purpose','evidence']:ap.add_argument('--'+n)
    ap.add_argument('--outcome',choices=['spawn','error'],default='spawn');a=ap.parse_args();r=Runtime()
    if a.command=='status':v=r.source_completion_status()
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
