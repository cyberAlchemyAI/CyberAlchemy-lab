#!/usr/bin/env python3
import argparse,json
from ac_runtime import read,require,sha
from ac_outer_review_runtime_v14 import CoverageRuntime as PreviousRuntime,replace_outer

class CoverageRuntime(PreviousRuntime):
    def integrity(self):
        super().integrity()
        for path,digest in read(self.p('coverage/COMPLETE-KEYS-FREEZE.v15.json'))['sources'].items():
            require(sha(path)==digest,'Complete key clarity source drift '+path)
        return True
    def literal(self,j,v):
        original=super().literal(j,v)
        if j['job_id'] not in read(self.p('coverage/COMPLETE-KEYS-BOUNDARY.v15.json'))['future_nonreview_ids']:
            return original
        require(j['role']!='review','Nonreview-only key clarity')
        clarity=('Emit exactly these13 top-level keys from payload.schema: job_id, strategy_id, '
                 'arm, case_id, operation_trace, candidates, attack, handoff, budget_used, limits, '
                 'selection, method_card, revision. Copy all four identity values from payload.job. '
                 'Do not add top-level pools, source/exposure/provenance graphs or inspection objects. '
                 'Record all required source and precursor details inside existing operation_trace '
                 'result text or handoff summary/residue. Irrelevant selection/method_card/revision '
                 'use the existing empty defaults. Check the entire key set before the one exclusive '
                 'first save; no output repair or retry.')
        require(len(v['schema'])==13,'Unchanged13-key nonreview schema required')
        return replace_outer(original,clarity)

def main():
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
