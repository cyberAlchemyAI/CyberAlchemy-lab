"""Closed source bindings and exact environment preflight."""
import hashlib,importlib.metadata,importlib.util,json,os,platform,sys
from datetime import datetime, timezone, timedelta
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[8]
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
    _capture_identity()
    raw=_CAPTURE_ENTRIES[0](ROOT,row,code_sha256=_CAPTURE_PIN)
    _capture_identity();return raw
def verify_source(pin):
    raw=original({'path':(HERE/'source-manifest.json').relative_to(ROOT).as_posix(),'sha256':pin})
    m=parse(raw);require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'source cannot grant authority')
    require(m['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'selected source environment differs')
    verify_inputs(m['files'])
    return m
def emit(path,value,*,raw=None):
    path=Path(path);require(path.is_relative_to(HERE/'packages') or path.is_relative_to(HERE/'receipts'),'outside source output boundary')
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(encoded(value) if raw is None else raw)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

# Separately selected successor helper: actual filename, captured code, no old-origin alias.
_CAPTURE_PIN='9de43edbdc7025a3fb17b35432a6f393a9856b02839b66470c2f4a2007e67211'
_CAPTURE_PATH=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/integrity-hardening-0002/capture.py'
_CALLER_PATH=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/integrity-hardening-0002/caller_contract.py'
_CALLER_PIN='4222b3ac165fa5ee8a9bed801290ffe42f63e69002ced521d4ac7e9e84bb7135'
def _load_selected_capture(selected_path,selected_pin,leaf):
    import importlib.abc,stat
    handles=[];links=[];fd=None
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);handles.append(parent)
        for name in selected_path.parts[1:-1]:
            child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child);s=os.fstat(child);links.append((parent,name,child,(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid)));parent=child
        fd=os.open(selected_path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent);before=os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_size<=1048576,'selected capture helper not bounded regular code')
        chunks=[];size=0
        while True:
            chunk=os.read(fd,1048577-size)
            if not chunk:break
            size+=len(chunk);require(size<=1048576,'capture helper grew');chunks.append(chunk)
        raw=b''.join(chunks);after=os.fstat(fd);attached=os.stat(selected_path.name,dir_fd=parent,follow_symlinks=False)
        signature=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        require(sha(raw)==selected_pin and len(raw)==before.st_size and signature(before)==signature(after)==signature(attached),'selected capture helper changed')
        for p,name,held,identity in links:
            a=os.stat(name,dir_fd=p,follow_symlinks=False);s=os.fstat(held);require((a.st_dev,a.st_ino,a.st_mode,a.st_uid,a.st_gid)==(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid)==identity,'capture helper ancestor changed')
    finally:
        if fd is not None:os.close(fd)
        for handle in reversed(handles):os.close(handle)
    class CaptureLoader(importlib.abc.SourceLoader):
        selected_source_sha256=selected_pin
        def get_filename(self,name):return str(selected_path)
        def get_data(self,path):require(path==str(selected_path),'unselected capture helper filename');return raw
        def get_code(self,name):return compile(raw,str(selected_path),'exec',dont_inherit=True)
    name='_cal_source_input_capture_v2_successor_'+leaf+'_'+__name__.replace('.','_')
    require(name not in sys.modules,'capture helper namespace already registered')
    spec=importlib.util.spec_from_file_location(name,selected_path,loader=CaptureLoader());m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def _load_capture():
    return _load_selected_capture(_CAPTURE_PATH,_CAPTURE_PIN,'kernel')
SOURCE_CAPTURE=_load_capture()
_CAPTURE_MODULE=SOURCE_CAPTURE
_CAPTURE_ENTRIES=(SOURCE_CAPTURE.capture_one,SOURCE_CAPTURE.verify_all,SOURCE_CAPTURE.kernel_guard,SOURCE_CAPTURE.need)
CAPTURE_CALLER=_load_selected_capture(_CALLER_PATH,_CALLER_PIN,'caller')
_CAPTURE_CALLER_MODULE=CAPTURE_CALLER
_CAPTURE_CALLER_ENTRIES=(CAPTURE_CALLER.select,CAPTURE_CALLER.check)
_CAPTURE_CALLER_STATE=tuple((fn,fn.__code__,fn.__globals__,fn.__defaults__,fn.__kwdefaults__,
    tuple(sorted((fn.__kwdefaults__ or {}).items())),fn.__closure__,
    tuple(cell.cell_contents for cell in (fn.__closure__ or ()))) for fn in _CAPTURE_CALLER_ENTRIES)
_CAPTURE_CALLER_GLOBALS=tuple(CAPTURE_CALLER.__dict__.items())
_CAPTURE_CONTRACT=_CAPTURE_CALLER_ENTRIES[0](SOURCE_CAPTURE,expected_path=_CAPTURE_PATH,expected_sha256=_CAPTURE_PIN)

def _capture_identity():
    require(SOURCE_CAPTURE is _CAPTURE_MODULE and (SOURCE_CAPTURE.capture_one,SOURCE_CAPTURE.verify_all,SOURCE_CAPTURE.kernel_guard,SOURCE_CAPTURE.need)==_CAPTURE_ENTRIES,'selected source capture module or entry callbacks changed')
    require(CAPTURE_CALLER is _CAPTURE_CALLER_MODULE and (CAPTURE_CALLER.select,CAPTURE_CALLER.check)==_CAPTURE_CALLER_ENTRIES,'independently captured caller changed')
    namespace=CAPTURE_CALLER.__dict__
    require(set(namespace)=={name for name,value in _CAPTURE_CALLER_GLOBALS}
        and all(namespace[name] is value for name,value in _CAPTURE_CALLER_GLOBALS),'captured caller global bindings changed')
    for fn,code,globals_selected,defaults,kwdefaults,kwitems,closure,cells in _CAPTURE_CALLER_STATE:
        require(fn.__code__ is code and fn.__globals__ is globals_selected
            and fn.__defaults__ is defaults and fn.__kwdefaults__ is kwdefaults
            and tuple(sorted((fn.__kwdefaults__ or {}).items()))==kwitems and fn.__closure__ is closure
            and all(cell.cell_contents is selected for cell,selected in zip(fn.__closure__ or (),cells)),
            'captured caller code or context changed')
    _CAPTURE_CALLER_ENTRIES[1](_CAPTURE_CONTRACT,SOURCE_CAPTURE)
def verify_inputs(rows,*,selected_external=()):
    _capture_identity()
    count=_CAPTURE_ENTRIES[1](ROOT,rows,code_sha256=_CAPTURE_PIN,selected_external=selected_external)
    _capture_identity();return count

loader=module('_cal_completion_diagnostic_0004_engine_0208',(ROOT/'product/lab/release-candidates/v1/interface')/'custody-correction-v4/loader.py')
original_bridge=module('_cal_completion_diagnostic_0004_bridge_0208',(ROOT/'product/lab/release-candidates/v1/interface')/'custody-correction-v4/reader_adapter.py')
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
