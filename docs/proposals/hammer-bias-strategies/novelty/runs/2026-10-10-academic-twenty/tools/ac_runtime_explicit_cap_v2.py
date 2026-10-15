#!/usr/bin/env python3
"""Prospective packet clarity amendment; frozen original sources stay intact."""
import argparse,json
from ac_runtime import Runtime as OriginalRuntime,read,sha,require
class Runtime(OriginalRuntime):
    def integrity(self):
        super().integrity()
        for path,digest in read(self.p('preparation/CAP-CLARIFICATION-FREEZE.v2.json'))['sources'].items():
            require(sha(path)==digest,'Prospective cap clarity source drift '+path)
        return True
    def payload(self,j):
        v=super().payload(j)
        if j['role'] in ['builder','transfer']:v['candidate_cap']=1
        return v
    def start(self,jid):
        require(jid in read(self.p('preparation/CAP-CLARIFICATION-BOUNDARY.v2.json'))['still_unadmitted_job_ids'],'Cap amendment cannot replace an already admitted packet')
        return super().start(jid)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['ready','status','verify','start','spawned','finish','failed','gate','reserve-overhead','record-overhead'])
    for n in ['job','handle','witness-file','invocation-id','purpose','evidence']:ap.add_argument('--'+n)
    ap.add_argument('--outcome',choices=['spawn','error'],default='spawn');a=ap.parse_args();r=Runtime()
    if a.command in ['ready','status','verify']:v=getattr(r,a.command)()
    elif a.command=='start':v=r.start(a.job)
    elif a.command=='spawned':v=r.spawned(a.job,a.handle)
    elif a.command=='finish':v=r.finish(a.job,read(a.witness_file))
    elif a.command=='failed':v=r.failed(a.job,read(a.witness_file))
    elif a.command=='gate':v=r.gate(a.job)
    elif a.command=='reserve-overhead':v=r.reserve_overhead(a.invocation_id,a.purpose)
    else:v=r.record_overhead(a.invocation_id,a.handle,a.purpose,a.evidence,a.outcome)
    print(json.dumps(v,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
