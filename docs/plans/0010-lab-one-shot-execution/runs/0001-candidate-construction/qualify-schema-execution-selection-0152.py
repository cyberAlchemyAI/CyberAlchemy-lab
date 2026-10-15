"""Real schema construction, fresh byte drift refusals and same-object timings."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time
import traceback

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
API=BASE/'api-integration-v7';OLD=BASE/'api-integration-v6'
SOURCE='c373b7b65c381b97f3016192d74a21b6d13463ef8f6fdbd0938c1260dd828707'
PROFILE='442a6da153a65d481820d4ce83748e1aed57729ec3cead5d6b55f78c31dd7f7e'
FORK=BASE/'schema-execution-owned-fixture-0152'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(p):return json.loads(p.read_bytes())
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def package(name,path):
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return __import__(name+'.protocol',fromlist=['Schemas'])
def main():
    output=RUN/'Schema-execution-qualification-0152.json';assert not output.exists() and not FORK.exists()
    checks=[];observations=[];failure=None;exit_error=None
    try:
        P=package('_cal_schema_execution_actual_0152',API)
        G=__import__('_cal_schema_execution_actual_0152.guard',fromlist=['verify']);G.verify(SOURCE)
        schemas=P.Schemas(PROFILE)
        checks.append({'check':'actual-independent-profile-and-original-URI-registry-construction','result':'PASS'})
        B=package('_cal_schema_execution_baseline_0152',OLD)
        for name,callback in [('full-history-baseline',lambda:B.Schemas.guard(schemas)),('selected-execution',schemas.guard),('full-history-baseline',lambda:B.Schemas.guard(schemas)),('selected-execution',schemas.guard)]:
            started=time.monotonic();callback();observations.append({'method':name,'seconds':time.monotonic()-started})
        checks.append({'check':'both-real-guards-over-same-exact-Schemas-object-profile-and-files','result':'PASS'})
        # An explicitly owned unfrozen fork keeps byte-mutation tests out of all
        # frozen sources and concurrently running qualification histories.
        shutil.copytree(API,FORK,ignore=shutil.ignore_patterns('source-manifest.json','receipts','__pycache__'))
        selection=load(FORK/'SCHEMA-EXECUTION-DEPENDENCIES.json')
        oldprefix=API.relative_to(ROOT).as_posix()+'/';newprefix=FORK.relative_to(ROOT).as_posix()+'/'
        def moved(row):
            if row['path'].startswith(oldprefix):return bind(ROOT/(newprefix+row['path'][len(oldprefix):]))
            return row
        selection['files']=[moved(row) for row in selection['files']]
        selection['selection_reasons']={newprefix+k[len(oldprefix):] if k.startswith(oldprefix) else k:v for k,v in selection['selection_reasons'].items()}
        selection['files'].sort(key=lambda row:row['path'])
        write(FORK/'SCHEMA-EXECUTION-DEPENDENCIES.json',selection)
        profile=load(FORK/'contract-profile.json');rows={row['path']:row for row in profile['files']}
        for row in selection['files']:rows[row['path']]=row
        profile['schema_execution_dependency_binding']=bind(FORK/'SCHEMA-EXECUTION-DEPENDENCIES.json')
        rows[profile['schema_execution_dependency_binding']['path']]=profile['schema_execution_dependency_binding']
        profile['files']=[rows[k] for k in sorted(rows)]
        write(FORK/'contract-profile.json',profile)
        Q=package('_cal_schema_execution_owned_fork_0152',FORK)
        probe=Q.Schemas(bind(FORK/'contract-profile.json')['sha256'])
        for name in ('service.py','authentication.schema.json'):
            path=FORK/name;before=path.read_bytes();path.write_bytes(before+b'\n')
            try:
                try:probe.guard()
                except (ValueError,AssertionError):pass
                else:raise AssertionError('actual selected drift was accepted: '+name)
            finally:path.write_bytes(before)
            probe.guard();checks.append({'check':'fresh-selected-byte-drift-refused:'+name,'result':'PASS'})
        # Fresh independently bound malformed selection cannot omit required
        # execution files even when its enclosing profile hash is coherent.
        omitted=next(row for row in selection['files'] if row['path']==str((FORK/'service.py').relative_to(ROOT)))
        selection['files'].remove(omitted);selection['selection_reasons'].pop(omitted['path'])
        write(FORK/'SCHEMA-EXECUTION-DEPENDENCIES.json',selection)
        profile['schema_execution_dependency_binding']=bind(FORK/'SCHEMA-EXECUTION-DEPENDENCIES.json')
        for row in profile['files']:
            if row['path']==profile['schema_execution_dependency_binding']['path']:row.update(profile['schema_execution_dependency_binding'])
        write(FORK/'contract-profile.json',profile)
        try:Q.Schemas(bind(FORK/'contract-profile.json')['sha256'])
        except (ValueError,AssertionError) as error:
            assert 'mandatory schema execution input omitted' in str(error),str(error)
        else:raise AssertionError('required runtime file omission accepted')
        checks.append({'check':'coherent-profile-cannot-omit-required-runtime-input','result':'PASS'})
    except BaseException:failure=traceback.format_exc()
    finally:
        if FORK.exists():shutil.rmtree(FORK)
        try:
            if 'G' in locals():G.verify(SOURCE)
            else:raise AssertionError('entry source guard unavailable')
        except BaseException:exit_error=traceback.format_exc()
    value={'schema_version':'lab-real-schema-execution-qualification/v1-candidate','result':'PASS' if failure is None and exit_error is None else 'FAIL',
        'checks':checks,'observations':observations,'failure':failure,'source_guarded_exit_completed':exit_error is None,'exit_guard_error':exit_error,
        'owned_fixture_removed':not FORK.exists(),'files':[bind(p) for p in [API/'source-manifest.json',API/'contract-profile.json',API/'SCHEMA-EXECUTION-DEPENDENCIES.json',Path(__file__).resolve()]],
        'original_sources_callbacks_clocks_and_permissions_changed':False,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False,
        'claim_ceiling':'Schema execution selection, actual code/schema drift refusal and sampled guard timings only. No public Session performance, full API or pilot qualification.'}
    with output.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':value['result'],'checks':len(checks),'report':bind(output)}),flush=True)
    return 0 if value['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
