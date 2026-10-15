"""Record actual CPU measurement and exact known-outcome scope successor."""
import hashlib,json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v47'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
 parent=BASE/'api-v46/receipts/R03-0082.json';old=load(parent);assert old['result']=='PASS' and not old['task_complete']
 assert bind(API/'source-manifest.json')['sha256']=='666fcd2bc4f0e77b257a26915d26aab8083a8ac6c252dd9bc0f259a7ede80c62'
 assert bind(API/'contract-profile.json')['sha256']=='754aee27b34b334f67e4143dd9ab7826dcab7047ba40a2cb68461d2da457aa13'
 measurement=load(RUN/'API45-failure12-cpu-measurement-0001.json');assert measurement['result']=='MEASURED' and measurement['actual_case_result']=='FAIL' and measurement['actual_tests']==1 and measurement['errors']==0
 assert load(RUN/'API45-failure12-cpu-measurement-terminal-0001.json')['actual_exit_code']==0
 assert load(RUN/'API47-freeze-terminal-0001.json')['actual_exit_code']==0
 static=load(RUN/'API47-known-outcome-static-0001.json');assert static['result']=='PASS' and static['unchanged_original_test_methods']==293 and static['known_outcome_groups']==2 and static['original_predicate_ASTs_unchanged']
 rows={r['path']:r for r in old['files']}
 for r in load(API/'source-manifest.json')['files']:rows[r['path']]=r
 extras=[parent,API/'source-manifest.json',API/'contract-profile.json',RUN/'API45-failure12-cpu-measurement-0001.json',RUN/'API45-failure12-cpu-measurement-terminal-0001.json',RUN/'API45-failure12-cpu-measurement-0001.log',RUN/'API45-known-outcome-source-cost-finding-0001.json',RUN/'API47-freeze-terminal-0001.json',RUN/'API47-freeze-0001.log',RUN/'context-R03-known-outcome-read-scope-API-0047.json',RUN/'API47-known-outcome-static-0001.json',RUN/'freeze-R03-known-outcome-read-scope-API-0047-0001.py',RUN/'run-API47-full-failure-after-core-schema-0001.py',Path(__file__).resolve()]
 for p in extras:
  r=bind(p);rows[r['path']]=r
 for r in rows.values():assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
 remaining=list(old['remaining_obligations']);remaining[1]='Verify frozen API47 read-scope grouping with the full original failure18 and every other current runtime suite. Keep original900-second bound, real clocks, every source/policy predicate and effect boundary.'
 remaining[2]='Finish SAME37740 original API46 cases14/15, retain actual verdict and cleanup evidence; SAME21283 waits for its terminal then runs complete API47 original failure18. Do not restart either on observation timeout.'
 v={**old,'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),'parent_progress_binding':bind(parent),'files':[rows[k] for k in sorted(rows)],'change':'Unchanged original API45 case12 CPU measurement completed:1 retained assertion failure0 errors; repeated original reads/source verification measured. Frozen API47 groups only existing pure known-failure predicate sequences through original read scope; all293 methods/34 schemas and original predicate ASTs retained. API46 original core/schema check continues; full API47 failure18 is serialized after it.',
 'completed_CPU_measurement_binding':bind(RUN/'API45-failure12-cpu-measurement-0001.json'),'completed_CPU_measurement_terminal_binding':bind(RUN/'API45-failure12-cpu-measurement-terminal-0001.json'),'source_cost_finding_binding':bind(RUN/'API45-known-outcome-source-cost-finding-0001.json'),'known_outcome_read_scope_static_binding':bind(RUN/'API47-known-outcome-static-0001.json'),'original_known_outcome_predicate_ASTs_unchanged':True,'durable_finish_and_delivery_outside_read_scope':True,'current_full_suites':['API46 original core/schema cases14/15 on37740','API47 full original failure18 serial driver on21283'],'current_full_public_suite_verdict':None,'API47_runtime_verification_result_established':False,'API46_successor_runtime_verification_executed':True,'successor_original_case_result_established':False,'full_original_failure_successor_driver_binding':bind(RUN/'run-API47-full-failure-after-core-schema-0001.py'),'normal_runtime_qualified':False,'remaining_obligations':remaining,'claim_ceiling':'Exact scoped candidate progress. CPU diagnostic reproduces an original assertion failure and measures overlapping verification cost. API47 static predicate/test retention passes; actual successor deadline and full public runtime qualifications remain unproven. No public typed handler, actual grant, genuine participant evidence, owner outcome or admission.'}
 path=API/'receipts/R03-0083.json';put(path,v)
 print(json.dumps({'result':'PASS','progress_binding':bind(path),'bound_files':len(rows),'normal_runtime_qualified':False,'task_complete':False}),flush=True)
if __name__=='__main__':main()
