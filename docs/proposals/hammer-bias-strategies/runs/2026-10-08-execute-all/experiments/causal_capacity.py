#!/usr/bin/env python3
"""Execute capacity interventions in an explicitly stipulated two-stage toy model."""
import json
from pathlib import Path
p=Path(__file__).resolve().parent
rows=[]
for summary in (3,6,12):
 for approval in (4,8,16):
  base=min(10,summary,approval)
  outcomes={
   'baseline':base,
   'double_summary':min(10,summary*2,approval),
   'add_four_approval_slots':min(10,summary,approval+4),
   'both':min(10,summary*2,approval+4)}
  rows.append({'summary_capacity':summary,'approval_capacity':approval,'arrivals':10,'outcomes':outcomes,'marginal_summary':outcomes['double_summary']-base,'marginal_approval':outcomes['add_four_approval_slots']-base,'discriminating_observation':'Separate stage service capacities and waiting, rather than aggregate end-to-end delay.'})
report={'kind':'executed-controlled-capacity-interventions','model':'completed = min(arrivals, summary_capacity, approval_capacity)','evaluated_conditions':len(rows)*4,'baseline_conditions':len(rows),'nonbaseline_interventions':len(rows)*3,'rows':rows,'observations':{'summary_only_advantage_cases':sum(x['marginal_summary']>x['marginal_approval'] for x in rows),'approval_only_advantage_cases':sum(x['marginal_approval']>x['marginal_summary'] for x in rows),'equal_marginal_cases':sum(x['marginal_approval']==x['marginal_summary'] for x in rows)},'hypotheses':{'universal_summary_improvement':'refuted inside this model by cases with an approval bottleneck','universal_approval_improvement':'refuted inside this model by cases with a summary bottleneck','cause_conditioned_choice':'supported as a decision rule within the stipulated model; not inferred as a production result'},'scope_limit':'The causal graph and capacities are stipulated; this is a transparent controlled model, not evidence that any real review process follows it. No intervention on a live process occurred.'}
(p/'causal-capacity-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report['observations']))
