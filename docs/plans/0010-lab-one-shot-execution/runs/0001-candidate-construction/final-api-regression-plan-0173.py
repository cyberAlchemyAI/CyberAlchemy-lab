"""Freeze explicit final API methods in whole-class worker buckets; no test run."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True

RUN=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_cal_final_api_methods_0173',RUN/'final-api-regression-map-0173.py');M=importlib.util.module_from_spec(spec);sys.modules[spec.name]=M;spec.loader.exec_module(M)

def pinned(directory,source,profile):
 directory=M.path(directory)
 M.require(M.binding(directory/'source-manifest.json')['sha256']==source,'explicit API source pin differs')
 M.require(M.binding(directory/'contract-profile.json')['sha256']==profile,'explicit API profile pin differs')
 return directory

def main():
 p=argparse.ArgumentParser();p.add_argument('--api-directory',required=True);p.add_argument('--source',required=True);p.add_argument('--profile',required=True)
 p.add_argument('--original-api-directory',required=True);p.add_argument('--original-source',required=True);p.add_argument('--original-profile',required=True)
 p.add_argument('--original-plan',required=True);p.add_argument('--original-plan-sha256',required=True);p.add_argument('--workers',type=int,default=4);p.add_argument('--output',required=True);a=p.parse_args()
 M.require(1<=a.workers<=32,'bounded explicit worker count required')
 api=pinned(a.api_directory,a.source,a.profile);original=pinned(a.original_api_directory,a.original_source,a.original_profile)
 old_plan_path=M.path(a.original_plan);M.require(M.binding(old_plan_path)['sha256']==a.original_plan_sha256,'original worker plan pin differs');old_plan=json.loads(old_plan_path.read_bytes())
 before=M.discover(original);current=M.discover(api);comparison=M.compare(before,current)
 M.require(len(before['methods'])==323 and set(before['methods'])==set(old_plan['all_declared_methods']),'exact original323 method inventory required')
 M.require(comparison['acceptable'],'undeclared inherited method/fixture change or unexpected new method')
 # These classes must run alone: Sessions retains original timers, and the
 # install/release tests deliberately corrupt selected source bytes briefly.
 sequential_names=('run_session_checks.py:Sessions','test_installation_release.py:InstallationReleaseAPI')
 sequential={k:current['classes'][k]['methods'] for k in sequential_names if k in current['classes']}
 workers={str(i):[] for i in range(a.workers)};loads={k:0 for k in workers};owners={k:'sequential:'+k for k in sequential}
 groups=[(k,v) for k,v in current['classes'].items() if k not in sequential]
 for name,row in sorted(groups,key=lambda item:(-len(item[1]['methods']),item[0])):
  worker=min(workers,key=lambda key:(loads[key],int(key)));workers[worker].extend(row['methods']);loads[worker]+=len(row['methods']);owners[name]='worker:'+worker
 workers={k:sorted(v) for k,v in workers.items() if v}
 all_methods=[*sum(sequential.values(),[]),*sum(workers.values(),[])]
 M.require(len(all_methods)==len(set(all_methods))==len(current['methods']) and set(all_methods)==set(current['methods']),'exact class bucket partition required')
 tools=[RUN/n for n in ('final-api-regression-0173.py','final-api-regression-plan-0173.py','final-api-regression-map-0173.py')]
 value={'schema_version':'lab-final-api-regression-plan/v1-candidate','api_directory':api.relative_to(M.ROOT).as_posix(),'source_sha256':a.source,'profile_sha256':a.profile,'original_api_directory':original.relative_to(M.ROOT).as_posix(),'original_source_sha256':a.original_source,'original_profile_sha256':a.original_profile,'original_plan_binding':M.binding(old_plan_path),'all_declared_methods':sorted(current['methods']),'original_declared_methods':sorted(before['methods']),'added_installation_release_methods':comparison['added_installation_release_methods'],'method_ast_comparison':comparison,'method_inventory':current,'original_method_inventory':before,'workers':workers,'sequential_classes':sequential,'class_bucket_owners':owners,'schedule':'Run each sequential class with no other final worker active; then run whole-class worker buckets with explicit host-selected concurrency. Do not overlap deliberate source tamper cases with any other qualification. Real fixture clocks and callbacks remain unchanged.','tools_bindings':[M.binding(x) for x in tools],'test_execution_performed':False,'method_or_fixture_monkeypatches':False,'original_clocks_or_callbacks_changed':False,'authority_effect':'none','actual_owner_outcome':None,'goal_complete':False,'whole_API_qualified':False,'claim_ceiling':'Frozen execution plan only. Retains original323 declarations and enumerates new installation/release declarations; no test outcome, human response, canonical admission or final Lab qualification.'}
 out=M.path(a.output);M.require(out.parent==RUN and out.name.startswith('final-api-regression-'),'owned new frozen plan path required')
 with out.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'plan_binding':M.binding(out),'original_methods':323,'added_methods':len(comparison['added_installation_release_methods']),'actual_declared_methods':len(current['methods']),'test_execution_performed':False}))
 return 0
if __name__=='__main__':raise SystemExit(main())
