#!/usr/bin/env python3
"""Separate source-bound endpoint/review coverage after actual earlier closure."""
import argparse,json
from ac_runtime import read,sha,require
from ac_grammar_review_schema_runtime_v12 import GrammarRuntime as PreviousRuntime
from ac_future_budget import FutureBudgetMixin


class Runtime(PreviousRuntime):
    def post_invalid_plan(self):
        return read(self.p('coverage/post-invalid/PLAN.v13.json'))

    def coverage_plan(self):
        return super().coverage_plan()+self.post_invalid_plan()

    def integrity(self):
        super().integrity()
        for path,digest in read(self.p('coverage/post-invalid/FREEZE.v13.json'))['sources'].items():
            require(sha(path)==digest,'Post-invalid coverage source drift '+path)
        return True

    def payload(self,j):
        v=super().payload(j)
        if j['job_id'] in {q['job_id'] for q in self.post_invalid_plan()}:
            v['post_invalid_coverage_context']=read(self.p('coverage/post-invalid/GAP.v13.json'))
        return v

    def literal(self,j,v):
        old=super().literal(j,v)
        if j['job_id'] not in {q['job_id'] for q in self.post_invalid_plan()}:
            return old
        common='All schema keys required, irrelevant selection/method_card/revision use empty defaults.'
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
        require(old.count(common)==1,'Unchanged inherited common literal expected')
        return ('This bounded role is self-contained: all required task facts and procedures '
                'are in this packet and its explicitly allowed review sources. Workspace '
                'memories and unrelated history are irrelevant; read this packet first.\n'
                +old.replace(common,clarity))

    def start(self,jid):
        require(jid in {j['job_id'] for j in self.post_invalid_plan()},'Post-invalid IDs only')
        previous=PreviousRuntime(self.root)
        require(all(previous.state(j['job_id'])['terminal'] for j in previous.plan()),
                'Original197, later75 and conditional grammar14 must close first')
        require(read(self.p('coverage/post-invalid/ADMISSION.v13.json'))['admit'] is True,
                'Actual-evidence post-invalid admission required')
        for p in ['receipts/coverage-coordinator.final.json','receipts/grammar-coordinator.final.json']:
            require(read(self.p(p))['observation']=='actual_FINAL','Actual prior coordinator FINAL required')
        out=FutureBudgetMixin.admit_later(self,jid)
        out['task_name']='acpost_'+str([j['job_id'] for j in self.post_invalid_plan()].index(jid))
        return out

    def post_invalid_status(self):
        ss={j['job_id']:self.state(j['job_id']) for j in self.post_invalid_plan()}
        return {'post_invalid_counts':{k:sum(s['disposition']==k for s in ss.values()) for k in ['pending','admitted','spawned','finished','failed','gated']},'valid_finished':sum(s['valid'] for s in ss.values()),'terminal':all(s['terminal'] for s in ss.values()),'budget':self.budget(),'ready':{k:[j for j in v if j in ss] for k,v in self.ready().items()}}


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
