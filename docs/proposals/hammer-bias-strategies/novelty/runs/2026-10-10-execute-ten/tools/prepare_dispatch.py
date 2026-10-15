import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
F=R.parents[1]/'future-preparation/2026-10-09'
d=json.loads((F/'future-pilot.dispatch.json').read_text())
d['dispatch_id']='novelty-ten-native-comparison-2026-10-10'
d['status']='research_runtime_route';d['execution_status']='prospective_unscored'
d['intent']={'raw':'Execute all ten newly prepared novelty strategies with the retained four-case comparison pilot.','objective':'184 prospective scored fresh native calls, all ten strategies, four pilot cells and ordinary/generic controls, dual independent raw assessments.','target_artifact':str(R/'reports/RESULTS.md')}
for s in d['steps']:
 s['stop_conditions']=['No scored retry or frozen protocol mutation; invalid sources gate dependents, but case assessment accepts failure packets.','Never drop untouched confirmation cases because of development negatives.','Structural route pass is not novelty or canonical capability efficacy.']
 s['inputs']=[{'kind':'intent' if s['step_id']=='freeze' else 'receipt','ref':str(R/('SCOPE.json' if s['step_id']=='freeze' else 'receipts/events.jsonl'))}]
 s['outputs']=[{'kind':'receipt','ref':str(R/'receipts'/f"{s['step_id']}.json")}]
 if 'evidence_artifact' in s:s['evidence_artifact']=str(R/'reports'/f"{s['step_id']}-evidence.json")
 for t in s.get('techniques',[]):
  t['source_ref']=str(R/'CONTRACT.md');t['validation_note']='Controlled research adapter: guard tests, immutable sources, actual native start and FINAL receipts, full exact assessment pair coverage, independent prelaunch and final audit. No canonical capability-bound admission claimed.'
 if 'capability_metadata' in s:s['capability_metadata']['status']='Source of technique inspiration only; this study is an explicit controlled adapter, not whole canonical skill efficacy or capability-bound runtime admission.'
d['steps'][2]['name']='Run fourteen three-stage conditions in all four case blocks'
d['steps'][2]['condition_ids']=['A','B','C','D','O','G','S01','S02','S03','S04','S07','S08','S09','S10']
d['subagent_strategy']={'status':'required','binding_mode':'descriptive','trigger':'Independent concern and raw proposal generation, staged fresh handoffs, two independent blinded whole-case reviews.','explanation':'Actual native collaboration workers run the controlled study; the descriptive route does not claim canonical capability-bound admission.','context':'User explicitly requested Robot Talks and execute all strategies; scope is frozen ten plus original four-case pilot.','roles':[{'role_id':rid,'purpose':purpose,'owns':owns,'applies_to_steps':steps} for rid,purpose,owns,steps in [('concern-inverter','Challenge causal return path','Own assigned concern artifact',['concerns']),('dependency-attacker','Break dependency and preserve outcome','Own assigned concern artifact',['concerns']),('condition-stage1','Assigned process mutation or control','Own assigned stage1 artifact',['branches']),('distill-adapter','Source-bound summary and residue','Own assigned stage2 artifact',['branches']),('fresh-builder','Construct at most two feasible separating probe cards','Own assigned raw builder artifact',['branches']),('raw-assessor','Independent methodblind complete case assessment','Own assigned whole-case review',['assess','confirm'])]],'parallelism':'mixed','join_policy':'all','authorization':'approved','permission_prompt':'Already authorized by explicit user Robot Talks request and execute-all goal; no additional approval pending.','receipt_requirements':['dispatch_id','step_id','capability_ref','status','artifacts','validation','observer_status','blockers','residue','handoff_note','agent_id','role_id','spawn_status','join_status','close_status','reroute','case_sha256','prompt_sha256','output_sha256','terminal_witness']}
d['observability']['trace_events']+=['independent_prelaunch','capacity_observed','dependent_gate','raw_assessment_pair_coverage','immutable_integrity_recheck']
d['observability']['signal_grouping']='job_id,case_id,condition_id,stage_id,event_kind'
d['promotion_guardrails']=['Actual native receipts establish attempted process execution only. Modeljudged archive-relative probe newness remains distinct from global originality, observed physical or human benefit, full canonical skill efficacy and equal compute.']
d['subagent_strategy']['context']=[d['subagent_strategy']['context']]
p=R/'runtime.dispatch.json'
with p.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
print(p)
