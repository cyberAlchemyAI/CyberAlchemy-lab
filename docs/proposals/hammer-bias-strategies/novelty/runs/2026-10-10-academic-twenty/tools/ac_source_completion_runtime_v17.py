#!/usr/bin/env python3
"""Prospective ten-role source comparison, superseding unadmitted v16 six."""
import json
from ac_runtime import read,sha,require
from ac_source_completion_runtime_v16 import Runtime as PreviousRuntime
from ac_post_invalid_complete_runtime_v15 import Runtime as PreviousClosedRuntime
from ac_coverage_runtime_v10 import CoverageRuntime as OriginalLiteralRuntime
from ac_outer_review_runtime_v14 import replace_outer
from ac_future_budget import FutureBudgetMixin

class Runtime(PreviousRuntime):
    def source_completion_plan(self):return read(self.p('coverage/source-completion/PLAN.v17.json'))
    def integrity(self):
        super().integrity()
        for path,digest in read(self.p('coverage/source-completion/FREEZE.v17.json'))['sources'].items():
            require(sha(path)==digest,'Ten-role source-comparison source drift '+path)
        return True
    def literal(self,j,v):
        if j['job_id'].startswith('COV-SOURCE-LATER-DISTINCT-'):
            clarity=('Emit exactly these13 top-level keys from payload.schema: job_id, strategy_id, '
                     'arm, case_id, operation_trace, candidates, attack, handoff, budget_used, limits, '
                     'selection, method_card, revision. Copy all four identity values from payload.job. '
                     'Do not add top-level pools, source/exposure/provenance graphs or inspection objects. '
                     'Record all required source and precursor details inside existing operation_trace '
                     'result text or handoff summary/residue. Irrelevant selection/method_card/revision '
                     'use the existing empty defaults. Check the entire key set before the one exclusive '
                     'first save; no output repair or retry.')
            require(len(v['schema'])==13,'Unchanged13-key schema required')
            return replace_outer(OriginalLiteralRuntime.literal(self,j,v),clarity)
        return super().literal(j,v)
    def start(self,jid):
        require(jid in {j['job_id'] for j in self.source_completion_plan()},'Source comparison IDs only')
        previous=PreviousClosedRuntime(self.root)
        require(all(previous.state(j['job_id'])['terminal'] for j in previous.plan()),'All actual previous phases must close')
        require(read(self.p('coverage/source-completion/ADMISSION.v17.json'))['admit'] is True,'Actual-evidence ten-role admission required')
        require(read(self.p('receipts/POST-INVALID-CLOSURE.v13.json'))['all_five_terminal'] is True,'Actual previous root closure required')
        out=FutureBudgetMixin.admit_later(self,jid)
        out['task_name']='acsource_'+str([j['job_id'] for j in self.source_completion_plan()].index(jid))
        return out

if __name__=='__main__':
    import ac_source_completion_runtime_v16 as cli
    cli.Runtime=Runtime
    cli.main()
