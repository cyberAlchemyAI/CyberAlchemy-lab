"""Closed source bindings and exact environment preflight."""
import hashlib,importlib.metadata,importlib.util,json,os,platform,sys
from datetime import datetime, timezone, timedelta
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def parse(raw):
    def pairs(rows):
        v={}
        for k,x in rows:
            require(k not in v,'duplicate source JSON key');v[k]=x
        return v
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite source JSON')))
def load(path):return parse(Path(path).read_bytes())
def require(value,message):
    if not value:raise ValueError(message)
def binding(path):return {'path':Path(path).relative_to(ROOT).as_posix(),'sha256':sha(Path(path).read_bytes())}
def original(row):
    require(type(row) is dict and set(row)=={'path','sha256'},'closed source binding required')
    name=row['path'];p=PurePosixPath(name)
    require(type(name) is str and not p.is_absolute() and p.as_posix()==name and '..' not in p.parts and '\\' not in name,'unsafe source path')
    path=ROOT/name;require(path.is_file() and not path.is_symlink() and not any(q.is_symlink() for q in path.parents),'unsafe original source')
    raw=path.read_bytes();require(sha(raw)==row['sha256'],'selected source bytes changed '+name);return raw
def verify_source(pin):
    raw=(HERE/'source-manifest.json').read_bytes();require(sha(raw)==pin,'independent participation source pin differs')
    m=parse(raw);require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'source cannot grant authority')
    require(m['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'selected source environment differs')
    for row in m['files']:original(row)
    return m
def emit(path,value,*,raw=None):
    path=Path(path);require(path.is_relative_to(HERE/'packages') or path.is_relative_to(HERE/'receipts'),'outside source output boundary')
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(encoded(value) if raw is None else raw)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
loader=module('_cal_completion_optimized_0004_engine_0208',(ROOT/'product/lab/release-candidates/v1/interface')/'custody-correction-v4/loader.py')
original_bridge=module('_cal_completion_optimized_0004_bridge_0208',(ROOT/'product/lab/release-candidates/v1/interface')/'custody-correction-v4/reader_adapter.py')
def selected_pins():return loader.EnginePins(**load((ROOT/'product/lab/release-candidates/v1/interface')/'custody-correction-v4/pins.json'))
def episode():
    value=load(HERE/'episode-contract.json')
    require(value['authority_effect']=='none' and value['actual_owner_outcome'] is None and value['fixture_only'] is True,'fixture grants no human or original authority')
    start=datetime.fromisoformat(value['not_before']);end=datetime.fromisoformat(value['expires_at'])
    require(start.tzinfo is not None and end.tzinfo is not None and end-start==timedelta(hours=24),'independently fixed24h source period required')
    require(value['original_Source8_period_binding']==binding((ROOT/'product/lab/release-candidates/v1/interface')/'current-participation-v8/packages/0001/period.json'),'original period provenance differs')
    require(value['original_Assignment_renewed'] is False and value['original_signer_restored'] is False and value['Session_memory_rehydrated'] is False,'old authority or memory cannot be restored')
    require(value['principal_ref']==records_identity('PRINCIPAL') and value['assignment_version_ref']==records_identity('ASSIGNMENT')+'@'+records_identity('VERSION'),'independent current identities differ')
    return value
def records_identity(name):
    from . import records
    return getattr(records,name)
def cut(view):
    data=view.data
    return {'store_ref':data['config']['store_id'],'branch_ref':'branch:'+data['config']['store_id'],
        'commit_sequence':data['head']['sequence'],'commit_sha256':data['head']['transaction_digest'],
        'source_profile_sha256':view.handle.manifest['profile_binding']['sha256'],
        'streams':[{'stream_ref':name,'cursor':len(record['payload']['events']),
            'head_sha256':view.handle.common.digest(record)} for name,record in sorted(data['projection']['histories'].items())]}
