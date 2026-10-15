"""Run each full original method in a separately guarded owned process."""
import argparse,ast,hashlib,json,subprocess,sys,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(m):
    for row in m['files']:
        if sha(ROOT/row['path'])!=row['sha256']:raise RuntimeError('changed source '+row['path'])
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-sha256',required=True);ap.add_argument('--workers',type=int,default=6);args=ap.parse_args()
    if not 1<=args.workers<=8 or sha(HERE/'source-manifest.json')!=args.source_sha256:raise RuntimeError('source/worker guard mismatch')
    m=json.loads((HERE/'source-manifest.json').read_bytes());verify(m)
    destination=HERE/'receipts/0001';destination.mkdir(parents=True,exist_ok=False)
    ids=[]
    for module,cls in [('test_runtime','RuntimeTests'),('test_custody','CustodyTests')]:
        tree=ast.parse((HERE/'runtime/tests'/f'{module}.py').read_text());definition=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
        ids += [f'{module}.{cls}.{n.name}' for n in definition.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    if len(ids)!=len(set(ids)):raise RuntimeError('duplicate methods')
    started=time.monotonic()
    def run_case(item):
        index,test_id=item;name=f'{index:03d}.json';log=destination/f'{index:03d}.log'
        argv=[sys.executable,str(HERE/'run_checks.py'),'--source-sha256',args.source_sha256,'--case-id',test_id,'--out','receipts/0001/'+name]
        with log.open('xb') as output:
            result=subprocess.run(argv,stdout=output,stderr=subprocess.STDOUT)
        path=destination/name;report=json.loads(path.read_bytes()) if path.exists() else None
        good=result.returncode==0 and report is not None and report['result']=='PASS' and report['tests_run']==1 and report['checks']==[{'test':test_id,'result':'PASS'}]
        return {'test':test_id,'result':'PASS' if good else 'FAIL','exit_code':result.returncode,'command':argv,'report_binding':binding(path) if report else None,'log_binding':binding(log)}
    cases=[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(run_case,item) for item in enumerate(ids)]
        for future in as_completed(futures):
            case=future.result();cases.append(case);print(json.dumps({'terminal_cases':len(cases),'total':len(ids),'test':case['test'],'result':case['result']}),flush=True)
    verify(m);cases.sort(key=lambda row:row['test']);observations=[];roots=[]
    for case in cases:
        if case['report_binding']:
            report=json.loads((ROOT/case['report_binding']['path']).read_bytes());observations+=report['observations'];roots+=report['owned_roots']
    good=all(c['result']=='PASS' for c in cases) and len(cases)==len(ids) and all(r['removed'] and not Path(r['path']).exists() for r in roots)
    report={'schema_version':'lab-original-byte-custody-full-suite/v1-candidate','result':'PASS' if good else 'FAIL',
        'source_manifest_binding':binding(HERE/'source-manifest.json'),'test_methods':len(cases),
        'original_runtime_methods':sum(c['test'].startswith('test_runtime.') for c in cases),'custody_methods':sum(c['test'].startswith('test_custody.') for c in cases),
        'actual_case_processes':len(cases),'workers':args.workers,'all_children_terminal':True,'cases':cases,'observations':observations,'owned_roots':roots,
        'all_owned_roots_removed':all(r['removed'] and not Path(r['path']).exists() for r in roots),'sources_unchanged':True,
        'authority_effect':'none','actual_owner_outcome':None,'private_keys_exported':False,'private_memory_exported':False,
        'task_complete':False,'goal_complete':False,'elapsed_seconds':round(time.monotonic()-started,3),
        'claim_ceiling':'Full original runtime assertions and explicit original-JSON storage primitive evidence; public API integration and complete original task criteria remain pending.'}
    path=destination/'result.json';path.open('x').write(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':report['result'],'methods':len(cases),'result_binding':binding(path)}),flush=True)
    raise SystemExit(0 if good else 1)
if __name__=='__main__':main()
