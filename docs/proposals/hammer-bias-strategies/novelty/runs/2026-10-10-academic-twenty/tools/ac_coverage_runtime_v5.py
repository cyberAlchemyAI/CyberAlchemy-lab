#!/usr/bin/env python3
"""Prospective role-stage clarification after unrun v4 pure preflight."""
from ac_coverage_runtime_v4 import CoverageRuntime as PriorCoverageRuntime
from ac_runtime import read,sha,require
class CoverageRuntime(PriorCoverageRuntime):
    def coverage_plan(self):return read(self.p('coverage/PLAN.v5.json'))
    def integrity(self):
        super().integrity()
        for path,digest in read(self.p('coverage/FREEZE.v5.json'))['sources'].items():
            require(sha(path)==digest,'Separate coverage v5 source drift '+path)
        return True

def main():
    import argparse,json
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['ready','status','verify','start','spawned','finish','failed','gate','reserve-overhead','record-overhead'])
    for n in ['job','handle','witness-file','invocation-id','purpose','evidence']:ap.add_argument('--'+n)
    ap.add_argument('--outcome',choices=['spawn','error'],default='spawn');a=ap.parse_args();r=CoverageRuntime()
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
