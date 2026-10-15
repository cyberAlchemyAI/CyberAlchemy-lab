"""Prepare closed independently pinned diagnostic inputs; never start runtime."""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def exact(row):
    assert type(row) is dict and set(row)=={'path','sha256'}
    assert type(row['path']) is str and type(row['sha256']) is str and re.fullmatch('[a-f0-9]{64}',row['sha256'])
    p=Path(row['path']);assert not p.is_absolute() and p.as_posix()==row['path'] and '..' not in p.parts and '\\' not in row['path'] and '\0' not in row['path'] and row['path']!='.'
    path=ROOT/p;assert path.is_file() and not path.is_symlink() and not any(x.is_symlink() for x in path.parents)
    raw=path.read_bytes();assert sha(raw)==row['sha256'];return raw
def row(path,pin):
    x={'path':str(path.relative_to(ROOT)),'sha256':pin};exact(x);return x
parser=argparse.ArgumentParser();parser.add_argument('--runtime-selection',required=True);parser.add_argument('--runtime-selection-sha256',required=True)
args=parser.parse_args();runtime_binding={'path':args.runtime_selection,'sha256':args.runtime_selection_sha256};runtime=json.loads(exact(runtime_binding))
assert runtime['schema_version']=='lab-current-session-runtime-selection/v1-candidate' and runtime['instance']=='optimized-0002'
assert runtime['authority_effect']=='none' and runtime['actual_owner_outcome'] is None and runtime['shared_API_qualified'] is False
for key in ['source_binding','source_package_binding','reader_binding','mapper_binding','mapper_package_binding','context_source_binding','context_package_binding','implementation_binding','period_binding']:exact(runtime[key])
source2=json.loads((RUN/'T07/api17-task-local-capture-0003/preimage/source-manifest.json').read_bytes())
source2_rows={x['path']:x for x in source2['files']}
def predecessor(path):return row(path,source2_rows[str(path.relative_to(ROOT))]['sha256'])
driver_manifest=RUN/'T35/full-learning-driver-0001/source-manifest-0003.json'
driver_raw=driver_manifest.read_bytes();assert sha(driver_raw)=='dbccd24d4b621f6f3c4495f686ea42120be36baa81a65a08f73574f5b75c0ed9'
driver_rows={x['path']:x for x in json.loads(driver_raw)['files']}
def driver(path):return row(path,driver_rows[str(path.relative_to(ROOT))]['sha256'])
context_root=str(Path(runtime['context_source_binding']['path']).parent)
selection={'schema_version':'lab-full-learning-input-selection/v1-candidate','authority_effect':'none',
    'api_path':str(API.relative_to(ROOT)),'source_name':runtime['public_source_name'],
    'factory_module':'source_bridge','factory_name':'current_session_fixture_delivery','producer_root':context_root,
    'source_pin':runtime['source_binding']['sha256'],'source_package_pin':runtime['source_package_binding']['sha256'],
    'runtime_selection_binding':runtime_binding,'period_binding':runtime['period_binding'],
    'provider_binding':predecessor(API.parent/'source8-session-runtime-v1-action-0148/provider.py'),
    'caller_boundary_binding':row(RUN/'T04/revision-0002/caller_adapter.py','b2b171a48754ffcff9cda8dbac889b06bd0b2e0d32d3c75ad49c4d63aeaab7f8'),
    'api_bootstrap_bindings':[predecessor(API/'__init__.py'),row(API/'guard.py','65ba71adb3b885f6fedc268be29f982f1f03139265f00a7e9ed08ff19b6adeb3')],
    'application_method_binding':predecessor(API.parent/'lesson-application-v4-completion-0001/preparation.py'),
    'assessment_method_binding':predecessor(API.parent/'lesson-assessment-v2-action-0148/preparation.py'),
    'lifecycle_bindings':{k:driver(RUN/'T35/full-learning-driver-0001'/filename) for k,filename in [('positive','positive_lifecycle.py'),('security','security_lifecycle.py')]}}
out=RUN/'T35/full-learning-inputs-0001';assert not out.exists();out.mkdir()
path=out/'selection.json'
with path.open('x') as f:json.dump(selection,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'status':'PREPARED-diagnostic-inputs-only','selection_binding':{'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())},'runtime_started':False,'task_complete':False,'authority_effect':'none'}))
