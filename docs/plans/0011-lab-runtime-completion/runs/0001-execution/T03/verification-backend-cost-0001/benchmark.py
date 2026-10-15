"""Normal streamed SHA256/backend and defensive-helper measurement only."""
import cProfile,hashlib,importlib.abc,importlib.util,json,os,re,stat,sys,time,uuid
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
SELECTION_SHA='b53ed97be85dca24dad1b0feccdf91cc7b4790eb482d429817514ee53e29c5fa'

def need(value):
    if not value:raise ValueError('selected technical benchmark input differs')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def stamp(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def directory(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid)
def exact(path,pin):
    """Capture the independently pinned bootstrap before executing its bytes."""
    handles=[];links=[]
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);handles.append(parent)
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent);handles.append(child)
            links.append((parent,part,child,directory(os.fstat(child))));parent=child
        fd=os.open(path.name,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW,dir_fd=parent);handles.append(fd);before=os.fstat(fd)
        need(stat.S_ISREG(before.st_mode));parts=[]
        while chunk:=os.read(fd,1024*1024):parts.append(chunk)
        raw=b''.join(parts)
        need(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False)))
        for parent,part,held,expected in links:need(directory(os.stat(part,dir_fd=parent,follow_symlinks=False))==directory(os.fstat(held))==expected)
        need(sha(raw)==pin);return raw
    finally:
        for fd in reversed(handles):os.close(fd)

selection=json.loads(exact(HERE/'input-selection.json',SELECTION_SHA))
helper=selection['helper_binding'];kernel=ROOT/helper['path'];PIN=helper['sha256'];code=exact(kernel,PIN)
class CapturedLoader(importlib.abc.SourceLoader):
    selected_source_sha256=PIN
    def get_filename(self,name):return str(kernel)
    def get_data(self,path):need(path==str(kernel));return code
    def get_code(self,name):return compile(code,str(kernel),'exec',dont_inherit=True)
name='_cal_T03_normal_verification_cost_'+uuid.uuid4().hex
spec=importlib.util.spec_from_file_location(name,kernel,loader=CapturedLoader());K=importlib.util.module_from_spec(spec);sys.modules[name]=K;spec.loader.exec_module(K)

def closed_inputs():
    need(sha(exact(HERE/'input-selection.json',SELECTION_SHA))==SELECTION_SHA)
    manifest=selection['source_manifest_binding']
    raw=K.capture_one(ROOT,manifest,code_sha256=PIN)
    rows=json.loads(raw)['files'];need(rows==selection['source_rows'] and len(rows)==1310)
    for r in selection['source_metadata']:
        p=ROOT/r['path'];s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_size==r['size_bytes'] and stat.S_IMODE(s.st_mode)==r['mode'])
    return rows

def dependency_guard():
    binding=selection['dependency_selection_binding'];raw=K.capture_one(ROOT,binding,code_sha256=PIN);deps=json.loads(raw)
    expected={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':0o755 if r['kind'] in {'interpreter','native-executable'} else 0o644} for r in deps['inputs']}
    expected.update(deps['wheel_members']);expected['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755;need(len(expected)==1010)
    install=ROOT/selection['installation_path'];need(install.stat().st_uid==os.getuid() and stat.S_IMODE(install.stat().st_mode)==0o700)
    installed=[]
    for name,row in expected.items():
        p=install/name;s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==row['mode'] and s.st_size==row['size_bytes'])
        installed.append({'path':str(p.relative_to(ROOT)),'sha256':row['sha256']})
    actual=set()
    for current,dirs,files in os.walk(install,followlinks=False):
        for name in dirs+files:need(not (Path(current)/name).is_symlink())
        actual.update(str((Path(current)/name).relative_to(install)) for name in files)
    need(actual==set(expected)|{'installation.json'})
    count=K.verify_all(ROOT,installed,code_sha256=PIN);need(count==1010)
    return {'fresh_installed_file_rows':count,'selection_sha256':binding['sha256'],'installed_bytes':sum(r['size_bytes'] for r in expected.values())}

def save(name,value):
    p=HERE/name
    with p.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}

def event(value):
    value={'observed_at':datetime.now(timezone.utc).isoformat(),**value}
    with (HERE/'events.jsonl').open('a') as f:f.write(json.dumps(value,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value,sort_keys=True),flush=True)

def fd_count():return len(list(Path('/proc/self/fd').iterdir()))

def selected_helper(binding):
    path=ROOT/binding['path'];raw=exact(path,binding['sha256'])
    class Loader(importlib.abc.SourceLoader):
        selected_source_sha256=binding['sha256']
        def get_filename(self,name):return str(path)
        def get_data(self,filename):need(filename==str(path));return raw
        def get_code(self,name):return compile(raw,str(path),'exec',dont_inherit=True)
    name='_cal_T03_backend_cost_defensive_'+uuid.uuid4().hex
    spec=importlib.util.spec_from_file_location(name,path,loader=Loader());m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def stream_rows(rows,factory,finish):
    """Owned comparison path: same fresh anchored file reads for every backend."""
    verified=0;total=0
    with K.scope(ROOT,PIN) as batch:
        for row in rows:
            parts,digest=K.selected(str(ROOT),row,());parent=batch.entries[1](batch,parts[:-1]);name=parts[-1]
            fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
            try:
                before=os.fstat(fd);attached=os.stat(name,dir_fd=parent,follow_symlinks=False)
                need(stat.S_ISREG(before.st_mode) and stamp(before)==stamp(attached));h=factory();size=0
                while chunk:=os.read(fd,1024*1024):size+=len(chunk);need(size<=before.st_size);h.update(chunk)
                attached=os.stat(name,dir_fd=parent,follow_symlinks=False)
                need(size==before.st_size and stamp(before)==stamp(os.fstat(fd))==stamp(attached))
                need(finish(h)==digest);batch.leaves.append((parent,name,K.stamp(before)));verified+=1;total+=size
            finally:os.close(fd)
    need(verified==1310 and total==selection['source_input_bytes']);return verified,total

def backend_info():
    out={'hashlib_sha256_callable_module':hashlib.sha256.__module__,'hashlib_sha256_callable_name':hashlib.sha256.__name__}
    for label,factory in [('hashlib.sha256',lambda:hashlib.sha256()),('hashlib.new-sha256',lambda:hashlib.new('sha256'))]:
        obj=factory();out[label]={'object_type_module':type(obj).__module__,'object_type_name':type(obj).__name__,'name':obj.name,'digest_size':obj.digest_size,'block_size':obj.block_size}
    try:
        import _hashlib
        out['_hashlib']={'available':True,'path':getattr(_hashlib,'__file__',None),'openssl_sha256_present':hasattr(_hashlib,'openssl_sha256')}
    except ImportError as error:out['_hashlib']={'available':False,'exception_class':type(error).__name__}
    try:
        import ssl
        out['selected_ssl_OpenSSL']={'available':True,'version':ssl.OPENSSL_VERSION,'version_info':ssl.OPENSSL_VERSION_INFO,'path':ssl.__file__}
    except ImportError as error:out['selected_ssl_OpenSSL']={'available':False,'exception_class':type(error).__name__}
    crypto=None
    try:
        import cryptography
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends.openssl.backend import backend
        obj=hashes.Hash(hashes.SHA256());out['cryptography']={'available':True,'version':cryptography.__version__,'package_path':cryptography.__file__,'hash_type_module':type(obj).__module__,'hash_type_name':type(obj).__name__,'OpenSSL_version':backend.openssl_version_text()}
        crypto=(lambda:hashes.Hash(hashes.SHA256()),lambda h:h.finalize().hex())
    except ImportError as error:out['cryptography']={'available':False,'exception_class':type(error).__name__}
    return out,crypto

def main():
    failure=None;observations=[];dependency_entry=None;dependency_exit=None;source_entry=None;source_exit=None;backends=None
    originals=K._CALLBACKS;fds_before=fd_count();defensive=None
    save('started.json',{'actual_pid':os.getpid(),'UTC':datetime.now(timezone.utc).isoformat(),'selection_sha256':SELECTION_SHA,'benchmark_sha256':sha(Path(__file__).read_bytes()),'interpreter':sys.executable,'authority_effect':'none'})
    try:
        dependency_entry=dependency_guard();rows=closed_inputs();source_entry=K.verify_all(ROOT,rows,code_sha256=PIN)
        sys.path.insert(0,str(ROOT/selection['installation_path']/'deps'))
        backends,crypto=backend_info();defensive=selected_helper(selection['defensive_helper_binding']);defensive_callbacks=defensive._CALLBACKS
        event({'event':'dependency-source-entry-and-backend-inspection-PASS','dependency_rows':1010,'source_rows':1310,'backends':backends})
        scenarios=[('hashlib.sha256',lambda rows:stream_rows(rows,lambda:hashlib.sha256(),lambda h:h.hexdigest())),('hashlib.new-sha256',lambda rows:stream_rows(rows,lambda:hashlib.new('sha256'),lambda h:h.hexdigest()))]
        if crypto is not None:scenarios.append(('cryptography.Hash-SHA256',lambda rows:stream_rows(rows,*crypto)))
        else:observations.append({'mode':'cryptography.Hash-SHA256','result':'ABSENT-no-installation-attempted'})
        scenarios.extend([('original-helper-full-table',lambda rows:(K.verify_all(ROOT,rows,code_sha256=PIN),selection['source_input_bytes'])),('defensive-helper-full-table',lambda rows:(defensive.verify_all(ROOT,rows,code_sha256=selection['defensive_helper_binding']['sha256']),selection['source_input_bytes']))])
        for label,callback in scenarios:
            rows=closed_inputs();before=fd_count();event({'event':'scenario-start','mode':label,'profiling':False})
            start=time.monotonic();cpu=time.thread_time();verified,size=callback(rows);elapsed=time.monotonic()-start;CPU=time.thread_time()-cpu;after=fd_count()
            need(verified==1310 and size==selection['source_input_bytes'] and before==after and K._CALLBACKS==originals and defensive._CALLBACKS==defensive_callbacks and not K._ACTIVE.value)
            if label=='defensive-helper-full-table':need(not defensive._ACTIVE.value)
            observation={'mode':label,'result':'PASS-fresh-full-table','fresh_rows_read_and_hashed':verified,'input_bytes':size,'wall_seconds':elapsed,'current_thread_CPU_seconds':CPU,'file_descriptors_before_after':[before,after],'profiling_or_monitoring_enabled':False,'original_helper_functions_primitives_or_clocks_replaced':False}
            observations.append(observation);event({'event':'scenario-terminal',**observation})
    except BaseException as error:
        failure={'exception_class':type(error).__name__,'frames':[]};tb=error.__traceback__
        while tb:
            path=Path(tb.tb_frame.f_code.co_filename)
            if path.is_relative_to(ROOT):failure['frames'].append({'path':str(path.relative_to(ROOT)),'function':tb.tb_frame.f_code.co_name,'line':tb.tb_lineno})
            tb=tb.tb_next
        event({'event':'refusal','failure':failure,'messages_args_raw_bodies_recorded':False})
    finally:
        try:rows=closed_inputs();source_exit=K.verify_all(ROOT,rows,code_sha256=PIN);dependency_exit=dependency_guard();exact(ROOT/selection['defensive_helper_binding']['path'],selection['defensive_helper_binding']['sha256'])
        except BaseException as error:failure=failure or {'exception_class':type(error).__name__,'phase':'exit-guard'}
    passed=failure is None and len(observations)==5 and source_entry==source_exit==1310 and dependency_entry and dependency_exit and fd_count()==fds_before
    report={'schema_version':'lab-T03-verification-backend-cost-results/v1-candidate','result':'PASS-scoped-backend-and-defensive-helper-costs' if passed else 'REFUSED','failure':failure,'input_selection_sha256':SELECTION_SHA,'original_helper_binding':selection['helper_binding'],'defensive_helper_binding':selection['defensive_helper_binding'],'source_manifest_binding':selection['source_manifest_binding'],'backends':backends,'observations':observations,'source_entry_exit_rows':[source_entry,source_exit],'dependency_entry':dependency_entry,'dependency_exit':dependency_exit,'file_descriptors_entry_exit':[fds_before,fd_count()],'production_backend_adopted_or_hash_functions_callbacks_clocks_replaced':False,'raw_input_bodies_exported':False,'Source_native_reader_Service_Agent_Session_grant_lease_executed':False,'authority_effect':'none','task_complete':False,'whole_API_qualified':False,'Session_speedup_or_empirical_margin_established':False,'limits':['Single samples under uncontrolled OS page cache/scheduling; normal fresh reads are not cold-cache claims.','Streamed backend paths use the same owned file read/attachment/hash checks, not a modified production helper.','Original and defensive helper runs preserve their own selected immutable callbacks and additional original integrity checks.','Hash backend and helper measurements are different paths; differences do not imply production integration equivalence or provenance/permission admission.']}
    binding=save('results.json',report);event({'event':'actual-result','result':report['result'],'result_binding':binding});return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())

