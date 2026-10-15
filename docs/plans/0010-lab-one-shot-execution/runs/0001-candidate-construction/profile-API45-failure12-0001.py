"""Measure one original owned-fixture case without replacing callbacks or clocks.

CPU profiling changes execution cost; this diagnostic does not qualify normal
900-second delivery. Only function counters/times are saved, never frame locals,
Session memory, key values or public request bodies.
"""
import ast,cProfile,hashlib,importlib.util,json,pstats,sys,time,unittest
from pathlib import Path
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v45'
SOURCE='8931c159d933d0144791542d0357bdf8ba532a3b12bd68f35ab3d5a347a0624d'
PROFILE='81fd3ed4feb462b23888dfe0edc98787cb18e24c2b7342e23dc230c6b2c54b31'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 name='_cal_api45_failure12_cpu_diagnostic'
 spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
 package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
 guard=__import__(name+'.guard',fromlist=['verify']);manifest=guard.verify(SOURCE)
 assert manifest['freeze_precedes_new_owned_fixture_effects']
 assert bind(API/'contract-profile.json')['sha256']==PROFILE
 module=__import__(name+'.test_failure_api',fromlist=['FailureAPI']);module.SOURCE=SOURCE;module.PROFILE=PROFILE
 method='test_12_full_postimage_annotation_conflict_is_recorded'
 node=next(n for n in ast.walk(ast.parse((API/'test_failure_api.py').read_bytes())) if isinstance(n,ast.FunctionDef) and n.name==method)
 method_sha=hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()
 profiler=cProfile.Profile(timer=time.process_time)
 wall=time.monotonic();cpu=time.process_time()
 profiler.enable()
 try:result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([module.FailureAPI(method)]))
 finally:profiler.disable()
 elapsed_wall=time.monotonic()-wall;elapsed_cpu=time.process_time()-cpu
 guard.verify(SOURCE);assert bind(API/'contract-profile.json')['sha256']==PROFILE
 stats=pstats.Stats(profiler)
 rows=[]
 for (filename,line,function),(primitive,total,self_cpu,cumulative,callers) in stats.stats.items():
  p=Path(filename)
  if not p.is_absolute() or not p.is_relative_to(ROOT):continue
  rows.append({'code_path':p.relative_to(ROOT).as_posix(),'line':line,'function':function,'primitive_calls':primitive,'total_calls':total,'self_cpu_seconds':self_cpu,'cumulative_cpu_seconds':cumulative})
 rows.sort(key=lambda r:r['cumulative_cpu_seconds'],reverse=True)
 value={'schema_version':'lab-original-case-cpu-measurement/v1-candidate','result':'MEASURED',
        'actual_case_result':'PASS' if result.wasSuccessful() else 'FAIL','actual_tests':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),'expected_tests':1,
        'wall_seconds':elapsed_wall,'process_cpu_seconds':elapsed_cpu,'cpu_timer':'time.process_time',
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'original_test_source_binding':bind(API/'test_failure_api.py'),'original_test_method_AST_sha256':method_sha,
        'measurement_runner_binding':bind(Path(__file__).resolve()),'highest_cumulative_repository_functions':rows[:40],
        'original_callbacks_and_real_host_clocks_unchanged':True,'original_900_second_bound_unchanged':True,
        'frame_locals_or_key_values_inspected':False,'Session_RAM_inspected':False,
        'profiling_overhead_affects_wall_delivery':True,'normal_runtime_qualified':False,
        'actual_owner_outcome':None,'authority_effect':'none','task_complete':False,
        'claim_ceiling':'CPU counters/times for one unchanged original case and its owned fixture, including setup/cleanup. Profiling overhead and scheduling prevent normal deadline qualification or inferred phase causality without further analysis.'}
 with (RUN/'API45-failure12-cpu-measurement-0001.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'result':'MEASURED','actual_case_result':value['actual_case_result'],'wall_seconds':elapsed_wall,'process_cpu_seconds':elapsed_cpu,'normal_runtime_qualified':False}),flush=True)
if __name__=='__main__':main()
