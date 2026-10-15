"""Own input/clone races plus exact unprofiled retained source-table comparison."""
import ast,hashlib,importlib.abc,importlib.util,json,os,sys,tempfile,time,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6];HERE=Path(__file__).resolve().parent
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/pure-source-capture-0001'
SOURCE=ROOT/'product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances/diagnostic-0004/source'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load_capture(path,pin,name):
    raw=path.read_bytes();assert sha(raw)==pin
    class Loader(importlib.abc.SourceLoader):
        selected_source_sha256=pin
        def get_filename(self,name):return str(path)
        def get_data(self,filename):assert filename==str(path);return raw
        def get_code(self,name):return compile(raw,str(path),'exec',dont_inherit=True)
    spec=importlib.util.spec_from_file_location(name,path,loader=Loader());module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def put(p,raw):
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as s:s.write(raw)
def fixture():
    root=Path(tempfile.mkdtemp(prefix='cal-T03-source-batch-'));os.chmod(root,0o700);(root/'nested').mkdir(mode=0o700)
    rows=[]
    for name in ['one','two']:
        p=root/'nested'/name;put(p,b'owned inert file '+name.encode());rows.append({'path':'nested/'+name,'sha256':sha(p.read_bytes())})
    return root,rows

def monitor(target,ordinal,mutation,operation):
    seen=0;performed=False;mid=4
    def observer(code,offset):
        nonlocal seen,performed
        if code is target:
            seen+=1
            if seen==ordinal:mutation();performed=True
    sys.monitoring.use_tool_id(mid,'T03 real owned mutation observer');sys.monitoring.register_callback(mid,sys.monitoring.events.PY_START,observer);sys.monitoring.set_local_events(mid,target,sys.monitoring.events.PY_START)
    try:operation()
    finally:
        sys.monitoring.set_local_events(mid,target,0);sys.monitoring.register_callback(mid,sys.monitoring.events.PY_START,None);sys.monitoring.free_tool_id(mid)
        assert performed,'production checkpoint not reached'

def main():
    selected=json.loads((RUN/'development-selection.json').read_bytes());pin=selected['capture']['sha256'];K=load_capture(HERE/'capture.py',pin,'_T03_selected_capture');cases=[];roots=[]
    def refused(label,operation):
        descriptors=len(os.listdir('/proc/self/fd'))
        try:operation()
        except (ValueError,OSError):pass
        else:raise AssertionError(label+' accepted')
        assert len(os.listdir('/proc/self/fd'))==descriptors and not getattr(K._ACTIVE,'value',False),'failed batch retained descriptors/registry'
        cases.append({'case':label,'result':'PASS-refused'})
    root,rows=fixture();roots.append(str(root));assert K.verify_all(root,rows,code_sha256=pin)==2 and K.capture_one(root,rows[0],code_sha256=pin)==(root/rows[0]['path']).read_bytes();cases.append({'case':'same independently selected bytes and complete row count','result':'PASS'})
    for mode in ['leaf','parent','late-leaf']:
        root,rows=fixture();roots.append(str(root))
        def mutation():
            path=root/rows[0]['path'] if mode!='parent' else root/'nested';held=path.with_name(path.name+'-retained');path.rename(held)
            if mode=='parent':path.mkdir(mode=0o700)
            else:put(path,held.read_bytes())
        target=K.Batch.read.__code__ if mode!='late-leaf' else K.Batch.check.__code__;ordinal=2
        refused('actual same-byte '+mode+' replacement inside full batch',lambda:monitor(target,ordinal,mutation,lambda:K.verify_all(root,rows,code_sha256=pin)))
    root,rows=fixture();roots.append(str(root));path=root/rows[0]['path'];path.rename(path.with_name('retained'));path.symlink_to(path.with_name('retained'));refused('leaf symlink never followed',lambda:K.verify_all(root,rows,code_sha256=pin))
    root,rows=fixture();roots.append(str(root));os.mkfifo(root/'nested/pipe',0o600);refused('special file is refused without blocking',lambda:K.capture_one(root,{'path':'nested/pipe','sha256':'0'*64},code_sha256=pin))
    root,rows=fixture();roots.append(str(root));refused('wrong digest',lambda:K.verify_all(root,[rows[0]|{'sha256':'0'*64}],code_sha256=pin));refused('wrong independent kernel pin',lambda:K.verify_all(root,rows,code_sha256='0'*64));refused('duplicate row',lambda:K.verify_all(root,rows+[rows[0]],code_sha256=pin));refused('conflicting duplicate row',lambda:K.verify_all(root,rows+[rows[0]|{'sha256':'0'*64}],code_sha256=pin))
    for name in ['../escape','./nested/one','nested//one','/external/unselected','nested\\one']:
        refused('noncanonical/unselected path '+name,lambda name=name:K.capture_one(root,{'path':name,'sha256':rows[0]['sha256']},code_sha256=pin))
    refused('absolute relative-path alias',lambda:K.verify_all(root,[rows[0],{'path':str(root/rows[0]['path']),'sha256':rows[0]['sha256']}],code_sha256=pin,selected_external=[{'path':str(root/rows[0]['path']),'sha256':rows[0]['sha256']}]))
    def nested():
        with K.scope(root,pin):K.verify_all(root,rows,code_sha256=pin)
    refused('nested scope',nested)
    def thrown():
        with K.scope(root,pin):raise ValueError('owned intentional exception')
    refused('exception closes scope and descriptors',thrown)
    # Test the actual staged outer entry identity guard as bounded excerpts.
    # These functions keep their true staged co_filename; this is not a loaded
    # Source-family producer or an asserted Context/permission execution.
    staged=RUN/'postimages/source/base.py';tree=ast.parse(staged.read_text());names={'original','verify_inputs','_capture_identity'};selected_nodes=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names]
    namespace={'ROOT':root,'SOURCE_CAPTURE':K,'_CAPTURE_MODULE':K,'_CAPTURE_PIN':pin,'_CAPTURE_ENTRIES':(K.capture_one,K.verify_all,K.kernel_guard,K.need),'require':lambda value,msg:None if value else (_ for _ in ()).throw(ValueError(msg))}
    exec(compile(ast.Module(body=selected_nodes,type_ignores=[]),str(staged),'exec'),namespace)
    for field in ['capture_one','verify_all','kernel_guard','need']:
        original=getattr(K,field);called=[]
        setattr(K,field,lambda *a,**kw:called.append(True))
        try:refused('outer staged entry refuses '+field+' substitution before replacement executes',lambda:namespace['verify_inputs'](rows));assert not called
        finally:setattr(K,field,original)
    original=namespace['SOURCE_CAPTURE'];namespace['SOURCE_CAPTURE']=types.SimpleNamespace()
    try:refused('outer staged entry refuses entire module replacement',lambda:namespace['verify_inputs'](rows))
    finally:namespace['SOURCE_CAPTURE']=original
    for field in ['read','check','close']:
        original=getattr(K.Batch,field);called=[]
        def mutation():setattr(K.Batch,field,lambda *a,**kw:called.append(True))
        try:refused('saved original batch guards/cleanup reject '+field+' substitution',lambda:monitor(K.Batch.read.__code__,2,mutation,lambda:namespace['verify_inputs'](rows)));assert not called
        finally:setattr(K.Batch,field,original)
    original=K.need
    try:refused('need substitution cannot suppress direct kernel rejection',lambda:monitor(K.Batch.read.__code__,2,lambda:setattr(K,'need',lambda *a:None),lambda:namespace['verify_inputs'](rows)))
    finally:K.need=original
    clone_root=Path(tempfile.mkdtemp(prefix='cal-T03-owned-kernel-'));roots.append(str(clone_root));clone=clone_root/'capture.py';put(clone,(HERE/'capture.py').read_bytes());owned=load_capture(clone,pin,'_T03_owned_clone')
    refused('physical owned kernel mutation after source read is rejected',lambda:monitor(owned.Batch.read.__code__,2,lambda:clone.write_bytes(clone.read_bytes()+b'\n# owned changed code\n'),lambda:owned.verify_all(root,rows,code_sha256=pin)))
    # Actual original full fresh verifier: unchanged code, no Source class,
    # nonce, permission or lease constructor. Complete selected table retained.
    package_name='_T03_original_Source_guard';spec=importlib.util.spec_from_file_location(package_name,SOURCE/'__init__.py',submodule_search_locations=[str(SOURCE)]);package=importlib.util.module_from_spec(spec);sys.modules[package_name]=package;spec.loader.exec_module(package);B=__import__(package_name+'.base',fromlist=['verify_source']);source_raw=(SOURCE/'source-manifest.json').read_bytes();source_pin=sha(source_raw);source_manifest=json.loads(source_raw);timings=[]
    for iteration in range(3):
        start=time.monotonic();B.verify_source(source_pin);old=time.monotonic()-start
        start=time.monotonic();count=K.verify_all(ROOT,source_manifest['files'],code_sha256=pin);new=time.monotonic()-start
        assert count==len(source_manifest['files'])==1263
        timings.append({'iteration':iteration+1,'original_full_guard_seconds':old,'new_complete_file_table_seconds':new,'rows_read_hashed':count,'profiled':False})
    assert (SOURCE/'source-manifest.json').read_bytes()==source_raw and sha((HERE/'capture.py').read_bytes())==pin
    cases.append({'case':'three actual unchanged complete Source verifier and fresh successor1263-row table runs, no lease constructed','result':'PASS'})
    result={'schema_version':'lab-T03-pure-source-capture-evidence/v1-candidate','result':'PASS','cases':cases,'owned_roots':roots,'actual_source_manifest_sha256':source_pin,'actual_original_guard_code_sha256':sha((SOURCE/'base.py').read_bytes()),'capture_code_sha256':pin,'unprofiled_sequential_timings':timings,'timing_scope':'Full old Source guard includes metadata/environment; new helper timings cover same full1263 row byte table only. Does not prove whole-path timing or lease margin. Parent may concurrently operate other runtime.','original_API_or_Source_callbacks_monkeypatched':False,'new_kernel_only_deliberately_mutated':True,'staged_outer_identity_excerpt_only':True,'actual_Source8_family_successor_constructed':False,'actual_complete_Session_sequence':False,'permission_or_period_cached':False,'authority_effect':'none','task_complete':False}
    out=RUN/'evidence.json';put(out,json.dumps(result,indent=2,sort_keys=True).encode()+b'\n');print(json.dumps({'result':'PASS','cases':len(cases),'timings':timings,'report':str(out)}),flush=True)
if __name__=='__main__':main()
