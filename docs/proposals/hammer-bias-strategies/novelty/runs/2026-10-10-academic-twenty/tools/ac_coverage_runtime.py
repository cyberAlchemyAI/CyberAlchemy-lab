#!/usr/bin/env python3
"""Separate first-save control coverage; imports the immutable primary adapter.

No model calls. Original failed controls and first reviews remain unchanged.
"""
import argparse, json
from ac_runtime import Runtime, ROOT, read, sha, require

class CoverageRuntime(Runtime):
    def original_plan(self):
        return read(self.p('preparation/PLAN.v1.json'))
    def coverage_plan(self):
        return read(self.p('coverage/PLAN.v2.json'))
    def plan(self):
        return self.original_plan()+self.coverage_plan()
    def integrity(self):
        super().integrity()
        for path,digest in read(self.p('coverage/FREEZE.v2.json'))['sources'].items():
            require(sha(path)==digest,'Separate coverage protocol drift '+path)
        return True
    def start(self,jid):
        require(jid in {j['job_id'] for j in self.coverage_plan()},'Coverage adapter admits coverage jobs only')
        require(all(self.state(j['job_id'])['terminal'] for j in self.original_plan()),'Original plan must close before separate coverage starts')
        out=super().start(jid)
        out['task_name']='accov_'+str([j['job_id'] for j in self.coverage_plan()].index(jid))
        return out
    def coverage_status(self):
        states={j['job_id']:self.state(j['job_id']) for j in self.coverage_plan()}
        return {'coverage_counts':{k:sum(s['disposition']==k for s in states.values()) for k in ['pending','admitted','spawned','finished','failed','gated']},'coverage_valid_finished':sum(s['disposition']=='finished' and s['valid'] for s in states.values()),'coverage_live':[j for j,s in states.items() if s['disposition'] in ['admitted','spawned']],'coverage_terminal':all(s['terminal'] for s in states.values()),'budget':self.budget(),'ready':{k:[j for j in v if j in states] for k,v in self.ready().items()}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('command',choices=['ready','status','verify','start','spawned','finish','failed','gate','reserve-overhead','record-overhead'])
    for name in ['job','handle','witness-file','invocation-id','purpose','evidence']:ap.add_argument('--'+name)
    ap.add_argument('--outcome',choices=['spawn','error'],default='spawn')
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
