#!/usr/bin/env python3
"""Full C09 controller: bounded owned processes, exact case evidence and joined examples."""
import argparse,json,os,platform,signal,subprocess,sys,tempfile,threading,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from inventory_manifest import *

parser=argparse.ArgumentParser();parser.add_argument('selection');parser.add_argument('--selection-sha256',required=True);parser.add_argument('--native-executable',required=True);args=parser.parse_args()
selection_path=Path(args.selection).resolve()
if sha(read(selection_path))!=args.selection_sha256:raise ValueError('independent selection pin mismatch')
selection=load(selection_path);manifest_path=ROOT/selection['manifest_path'];manifest=validate_manifest(manifest_path,selection['manifest_sha256'])
if sha(read(args.native_executable))!=manifest['native_executable_sha256']:raise ValueError('native build differs from frozen candidate')
for row in selection['regression_inventory']:
    if sha(read(ROOT/row['path']))!=row['sha256']:raise ValueError('frozen test inventory bytes changed')
    actual=load(ROOT/row['path'])
    if actual['test_ids']!=row['test_ids'] or actual['count']!=row['count']:raise ValueError('frozen test inventory differs')
inventories={r['group']:r for r in selection['regression_inventory']}
if set(inventories)!={g['id'] for g in groups()} or sum(r['count'] for r in inventories.values())!=selection['total_cases']:raise ValueError('incomplete regression selection')
directory=PACKAGE/'receipts/C09';directory.mkdir(parents=True,exist_ok=True);index=1
while (directory/f'{index:04d}').exists():index+=1
run=directory/f'{index:04d}';run.mkdir();started=time.perf_counter();mutex=threading.Lock();active={};results=[]
env={**os.environ,'LAB_C08_NATIVE_EXECUTABLE':str(Path(args.native_executable).resolve()),'LAB_C08_GENERATOR_MANIFEST':'implementation/lab-context/candidates/v1/packages/0004/generator-manifest.json','C09_MANIFEST_PATH':str(manifest_path),'C09_MANIFEST_SHA256':selection['manifest_sha256']}
mutable=ROOT/'implementation/lab-context/candidates/v1/native_reader.py';original_mutable=read(mutable)


def execute(group,root,case=None):
    label=group['id'] if case is None else group['id']+'-'+case.rsplit('.',1)[-1]
    folder=run/label;folder.mkdir();fixtures=root/label;fixtures.mkdir()
    output=folder/'result.json';command=[sys.executable,str(PACKAGE/'worker.py'),group['id'],str(output)]
    if case is not None:command += ['--case',case]
    environment={**env,'C09_FIXTURE_ROOT':str(fixtures),'S01_FIXTURE_ROOT':str(fixtures)}
    begin=time.perf_counter();timeout=False
    process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=environment,start_new_session=True)
    with mutex:
        active[label]={'pid':process.pid,'group':group['id'],'case':case,'started':time.time(),'output':output.relative_to(ROOT).as_posix()}
        (run/'live-processes.json').write_text(json.dumps(active,indent=2,sort_keys=True)+'\n')
    try:stdout,stderr=process.communicate(timeout=420 if case is not None else group['budget_seconds'])
    except subprocess.TimeoutExpired:
        timeout=True;os.killpg(process.pid,signal.SIGKILL);stdout,stderr=process.communicate()
    with mutex:
        active.pop(label,None);(run/'live-processes.json').write_text(json.dumps(active,indent=2,sort_keys=True)+'\n')
    log=folder/'terminal.log';log.write_text(stdout+stderr)
    expected=[case] if case else inventories[group['id']]['test_ids']
    data=load(output) if output.exists() else {'tests':0,'successful':False,'checks':[],'errors':1,'failures':0,'observations':{}}
    checks=data['checks'];complete=len(checks)==len(expected) and {r['test'] for r in checks}==set(expected)
    success=not timeout and process.returncode==0 and data['successful'] and complete and all(r['result']=='PASS' for r in checks)
    # Retain every declared case, including cases never reached after a timeout/setup error.
    seen={r['test'] for r in checks};accounted=checks+[{'test':t,'result':'NOT-RUN','reason':'worker timed out or terminated before this case'} for t in expected if t not in seen]
    summary={'group':group['id'],'case':case,'result':'PASS' if success else 'FLAG','returncode':process.returncode,'timed_out':timeout,'budget_seconds':420 if case else group['budget_seconds'],'duration_seconds':time.perf_counter()-begin,'checks':accounted,'files':[{'path':log.relative_to(ROOT).as_posix(),'sha256':sha(read(log))}],'observations':data.get('observations',{})}
    if output.exists():summary['files'].append({'path':output.relative_to(ROOT).as_posix(),'sha256':sha(read(output))})
    summary_path=folder/'summary.json';summary_path.write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    with mutex:
        results.append({'path':summary_path.relative_to(ROOT).as_posix(),'sha256':sha(read(summary_path)),'group':group['id'],'case':case,'result':summary['result']})
        (run/'progress.json').write_text(json.dumps({'result':'RUNNING','completed_workers':len(results),'declared_cases':selection['total_cases'],'elapsed_seconds':time.perf_counter()-started,'results':results},indent=2,sort_keys=True)+'\n')
        print(json.dumps({'group':group['id'],'case':case,'result':summary['result'],'cases':len(expected),'duration_seconds':summary['duration_seconds']}),flush=True)
    return summary


try:
    with tempfile.TemporaryDirectory(prefix='lab-C09-owned-fixtures-') as temp:
        root=Path(temp)
        # Context mutates one owned candidate source for its invalidation guard.
        # It runs alone, then all consumers use the restored exact package.
        execute(next(g for g in groups() if g['id']=='context'),root)
        remaining=[g for g in groups() if g['id'] not in ['context','frozen-v2-regression']]
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(execute,g,root) for g in remaining]
            for future in as_completed(futures):future.result()
        legacy=next(g for g in groups() if g['id']=='frozen-v2-regression')
        with ThreadPoolExecutor(max_workers=legacy['case_workers']) as pool:
            futures=[pool.submit(execute,legacy,root,t) for t in inventories[legacy['id']]['test_ids']]
            for future in as_completed(futures):future.result()
finally:
    # The known source-mutation guard restores bytes in its normal finally block.
    # If its process was killed, restore only that exact known mutation.
    current=read(mutable)
    source_repair=None
    if current==original_mutable+b'\n':
        mutable.write_bytes(original_mutable);source_repair='known verification newline mutation restored after terminal worker'

currentness_error=None
try:validate_manifest(manifest_path,selection['manifest_sha256'])
except Exception as error:currentness_error=str(error)
summaries=[load(ROOT/r['path']) for r in results]
actual_checks=[c for s in summaries for c in s['checks']]
expected_ids=[t for r in inventories.values() for t in r['test_ids']]
inventory_complete=len(actual_checks)==len(expected_ids) and len({c['test'] for c in actual_checks})==len(expected_ids) and {c['test'] for c in actual_checks}==set(expected_ids)
observations={}
for summary in summaries:
    if summary['case'] is None:observations.update(summary['observations'])
required_observations={'transition','publication','bootstrap','context_packs','joined','publication_invalidation','replay_timings'}
observation_complete=required_observations<=set(observations)
passed=inventory_complete and observation_complete and currentness_error is None and all(r['result']=='PASS' for r in results) and all(c['result']=='PASS' for c in actual_checks)
example=run/'observed-predecision-example.json';example.write_text(json.dumps({'authority_effect':'none','fixture_only':True,'actual_owner_outcome':None,'real_work_satisfaction_claimed':False,'observations':observations,'scope':'Actual isolated joins and component regression; no real Work or human pilot, no power-loss proof.'},indent=2,sort_keys=True)+'\n')
files=[{'path':manifest_path.relative_to(ROOT).as_posix(),'sha256':selection['manifest_sha256']},{'path':selection_path.relative_to(ROOT).as_posix(),'sha256':args.selection_sha256},{'path':example.relative_to(ROOT).as_posix(),'sha256':sha(read(example))}]+manifest['files']+[{'path':r['path'],'sha256':r['sha256']} for r in results]
for s in summaries:files+=s['files']
files+=[{'path':r['path'],'sha256':r['sha256']} for r in inventories.values()]
performance=load(ROOT/'implementation/lab-runtime/candidates/repeatable-operation/receipts/C03-acceptance-0001.json')
receipt={'schema_version':'lab-C09-complete-integration-check/v1-candidate','task':'C09','authority_effect':'none','result':'PASS' if passed else 'FLAG','task_complete':passed,'cases':len(expected_ids),'passed_cases':sum(c['result']=='PASS' for c in actual_checks),'inventory_complete':inventory_complete,'observations_complete':observation_complete,'duration_seconds':time.perf_counter()-started,'candidate_manifest_sha256':selection['manifest_sha256'],'currentness_error':currentness_error,'source_repair':source_repair,'files':list({r['path']:r for r in files}.values()),'source_bindings':load(ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/context-C09.json')['source_bindings'],'environment':{'python':sys.version,'platform':platform.platform()},'performance_posture':performance['performance_result'],'retained_performance_limits':performance['limitations'],'selected_replay_acceleration':'measured-no-op; no cache','actual_owner_outcome':None,'repository_admissions_applied':0,'real_work_satisfaction_claimed':False,'human_pilot_observations':0,'runtime_activations':0,'external_effects':0,'scope':'Complete declared successor regression plus actual source/catalog/reconstruction/native-context join and publication-driven Session invalidation in isolated stores.','remaining_obligations':[] if passed else ['All exact declared cases, joined observations and source currentness must pass before C09 completion.'],'claim_ceiling':'Candidate conformance and controlled process-interruption recovery; no actual canonical admission, completed real Work, general API authority, broader native profiles, Product SLA or power-loss durability.'}
path=run/'receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':receipt['result'],'cases':receipt['cases'],'passed_cases':receipt['passed_cases'],'duration_seconds':receipt['duration_seconds'],'receipt':path.relative_to(ROOT).as_posix(),'currentness_error':currentness_error}),flush=True)
sys.exit(0 if passed else 1)
