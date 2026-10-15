#!/usr/bin/env python3
"""Version11 grammar coverage with explicit strict builder caps; prior unrun versions preserved."""
import argparse,json
from ac_runtime import read,sha,require
from ac_coverage_runtime_v10 import CoverageRuntime

class GrammarRuntime(CoverageRuntime):
    def grammar_plan(self):return read(self.p('coverage/grammar/PLAN.v11.json'))
    def plan(self):return super().plan()+self.grammar_plan()
    def integrity(self):
        super().integrity()
        for path,digest in read(self.p('coverage/grammar/FREEZE.v11.json'))['sources'].items():
            require(sha(path)==digest,'Conditional grammar source drift '+path)
        return True
    def effective_case(self,j):
        if j['case_id']=='JG':return read(self.p('coverage/grammar/inputs/JG.json'))
        return super().effective_case(j)
    def start(self,jid):
        require(jid in {j['job_id'] for j in self.grammar_plan()},'Grammar adapter admits grammar coverage only')
        require(all(self.state(j['job_id'])['terminal'] for j in self.original_plan()+self.coverage_plan()),'Primary and later ordinary coverage must close first')
        decision=read(self.p('coverage/grammar/ADMISSION.v11.json'))
        require(decision['admit'] is True and decision.get('actual_evidence_paths'),'Actual later review/audit must justify separate grammar coverage')
        # Base admission preserves the complete cumulative budget and worker cap.
        from ac_future_budget import FutureBudgetMixin
        out=FutureBudgetMixin.admit_later(self,jid)
        out['task_name']='acgrammar_'+str([j['job_id'] for j in self.grammar_plan()].index(jid))
        return out
    def grammar_status(self):
        ss={j['job_id']:self.state(j['job_id']) for j in self.grammar_plan()}
        return {'grammar_counts':{k:sum(s['disposition']==k for s in ss.values()) for k in ['pending','admitted','spawned','finished','failed','gated']},'grammar_valid_finished':sum(s['disposition']=='finished' and s['valid'] for s in ss.values()),'grammar_terminal':all(s['terminal'] for s in ss.values()),'budget':self.budget(),'ready':{k:[j for j in v if j in ss] for k,v in self.ready().items()}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['status','verify','start','spawned','finish','failed','gate','reserve-overhead','record-overhead'])
    for name in ['job','handle','witness-file','invocation-id','purpose','evidence']:ap.add_argument('--'+name)
    ap.add_argument('--outcome',choices=['spawn','error'],default='spawn');a=ap.parse_args();r=GrammarRuntime()
    if a.command=='status':v=r.grammar_status()
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
