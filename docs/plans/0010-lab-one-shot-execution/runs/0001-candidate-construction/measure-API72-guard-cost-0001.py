"""Measure one original full guard without a Session, trace or replaced callback."""
import cProfile, hashlib, importlib.util, json, pstats, time
from pathlib import Path
RUN=Path(__file__).resolve().parent; ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v72'
SOURCE='1e18a7d5a2c310ee200f3d4cf6c1f95cb50bb9fad6252028fdc5d29b5b684c24'
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    spec=importlib.util.spec_from_file_location('_cal_API72_guard_cost',API/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    profiler=cProfile.Profile();started=time.perf_counter()
    manifest=profiler.runcall(guard.verify,SOURCE)
    elapsed=time.perf_counter()-started
    calls=[]
    for (filename,line,function),(primitive,total,self_time,cumulative,_) in pstats.Stats(profiler).stats.items():
        path=Path(filename)
        if path.is_relative_to(ROOT):
            calls.append({'source':path.relative_to(ROOT).as_posix(),'line':line,'function':function,
                'primitive_calls':primitive,'total_calls':total,'self_seconds':self_time,'cumulative_seconds':cumulative})
    profile=json.loads((API/'contract-profile.json').read_bytes())
    closures=[]
    for name,rows in [('source',manifest['files']),('protocol-profile',profile['files'])]:
        closures.append({'selection':name,'selected_files':len(rows),
            'selected_bytes':sum((ROOT/row['path']).stat().st_size for row in rows)})
    value={'schema_version':'lab-original-guard-cost-measurement/v1-candidate','result':'PASS',
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'producer_binding':bind(Path(__file__).resolve()),'guard_binding':bind(API/'guard.py'),
        'wall_seconds':elapsed,'selected_closures':closures,'repository_function_measurements':calls,
        'actual_guard_invocations':1,'source_callbacks_replaced':False,'Session_created':False,
        'clock_replaced':False,'private_values_or_memory_exported':False,
        'Machine_expiry_cost_attribution_established':False,'historical_full_suite_cause_established':False,
        'claim_ceiling':'One actual original API72 full source verification and exact selection sizes only. No complete invocation or Machine cause attribution.',
        'authority_effect':'none','actual_owner_outcome':None,'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
    path=RUN/'API72-guard-cost-measurement-0001.json'
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','wall_seconds':elapsed,'closures':closures,'report_binding':bind(path)}),flush=True)
if __name__=='__main__':main()
