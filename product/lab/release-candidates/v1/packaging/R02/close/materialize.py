"""Bind cold audit and planned operations postimage without canonical admission."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=BASE.parents[5]
sys.path.insert(0,str(BASE/'successors/0001'))
from common import *
def run(core_pin,audit_pin,recipe_pin):
 need(sha(read(Path(__file__)))==recipe_pin,'independent materializer pin differs')
 core=BASE/'successors/0003/receipts/0001.json';audit=BASE/'audit/0001/result.json'
 need(sha(read(core))==core_pin and sha(read(audit))==audit_pin,'independent core/audit pin differs');v=load(core);a=load(audit)
 need(v['result']=='PASS' and v['task_complete'] and all(v['checks'].values()) and a['result']=='PASS' and a['receipt_sha256']==core_pin,'full terminal and independent audit required')
 for b in v['files']:need(sha(read(ROOT/b['path']))==b['sha256'],'core source changed: '+b['path'])
 path=HERE/'postimages/product/lab/release-candidates/v1/OPERATIONS.md';path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb') as f:f.write(read(BASE/'successors/0001/OPERATIONS.md'));f.flush();os.fsync(f.fileno())
 extras=[*(BASE/'attempts').glob('*/terminal.json'),core,audit,BASE/'audit/0001/verify.py',Path(__file__),path]
 files={b['path']:b['sha256'] for b in v['files']}
 for p in extras:files[p.relative_to(ROOT).as_posix()]=sha(read(p))
 v['files']=[{'path':n,'sha256':h} for n,h in sorted(files.items())];v['core_receipt_binding']={'path':core.relative_to(ROOT).as_posix(),'sha256':core_pin};v['audit_binding']={'path':audit.relative_to(ROOT).as_posix(),'sha256':audit_pin};v['planned_operations_postimage']={'target_path':'product/lab/release-candidates/v1/OPERATIONS.md','candidate_path':path.relative_to(ROOT).as_posix(),'sha256':sha(read(path)),'admitted':False};v['checks']['independent_cold_receipt_payload_privacy_audit']=True;v['checks']['original_operations_postimage_materialized']=True;v['counts']['integration_acceptance']=len(v['checks']);v['selected_package']='packages/0003';v['historical_failures_preserved']=True
 v['final_assembly_obligations'].append('R05 integration must exercise the selected jsonschema 4.23.0/dependency environment; earlier global-environment receipts remain historical evidence.')
 emit(HERE/'receipts/0001.json',v);print(json.dumps({'result':'PASS','checks':v['counts'],'files':len(files),'receipt_sha256':sha(read(HERE/'receipts/0001.json'))}))
if __name__=='__main__':run(*sys.argv[1:])
