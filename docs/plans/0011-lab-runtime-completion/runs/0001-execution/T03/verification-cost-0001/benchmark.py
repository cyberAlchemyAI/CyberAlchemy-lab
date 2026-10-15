"""Normal pure Source-table verification costs; no Lab constructors or effects."""
import cProfile,hashlib,importlib.abc,importlib.util,json,os,re,stat,sys,time,uuid
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
SELECTION_SHA='196b11535490a97fd1cb61814c80e1ffe27528cfb53cddd175d0b159a9515cd2'

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

def main():
    failure=None;observations=[];dependency_entry=None;dependency_exit=None;source_entry=None;source_exit=None
    original_callbacks=K._CALLBACKS;fds_before=fd_count()
    save('started.json',{'actual_pid':os.getpid(),'UTC':datetime.now(timezone.utc).isoformat(),'selection_sha256':SELECTION_SHA,'benchmark_sha256':sha(Path(__file__).read_bytes()),'interpreter':sys.executable,'authority_effect':'none'})
    try:
        dependency_entry=dependency_guard();rows=closed_inputs();source_entry=K.verify_all(ROOT,rows,code_sha256=PIN)
        event({'event':'full-dependency-and-source-entry-PASS','dependency_rows':1010,'source_rows':source_entry})
        for i,scenario in enumerate(selection['scenarios']):
            rows=closed_inputs();profile=cProfile.Profile() if scenario['profiling'] else None
            event({'event':'scenario-start','index':i,**scenario,'source_rows':len(rows)})
            before=fd_count();start=time.monotonic();cpu=time.thread_time()
            if profile is not None:profile.enable()
            try:
                if scenario['mode']=='verify_all':verified=K.verify_all(ROOT,rows,code_sha256=PIN)
                else:
                    verified=0
                    for row in rows:
                        body=K.capture_one(ROOT,row,code_sha256=PIN);verified+=1;del body
            finally:
                if profile is not None:profile.disable()
            elapsed=time.monotonic()-start;thread_cpu=time.thread_time()-cpu;after=fd_count();need(verified==1310 and before==after and K._CALLBACKS==original_callbacks and not K._ACTIVE.value)
            profile_rows=[]
            if profile is not None:
                for e in profile.getstats():
                    if hasattr(e.code,'co_filename') and e.code.co_filename==str(kernel):
                        profile_rows.append({'path':helper['path'],'function':e.code.co_name,'line':e.code.co_firstlineno,'calls':e.callcount,'recursive_calls':e.reccallcount,'inclusive_seconds':e.totaltime,'exclusive_seconds':e.inlinetime})
            observation={'index':i,**scenario,'fresh_rows_read_and_hashed':verified,'source_input_bytes':selection['source_input_bytes'],'wall_seconds':elapsed,'current_thread_CPU_seconds':thread_cpu,'file_descriptors_before_after':[before,after],'helper_callbacks_unchanged':True,'thread_local_batch_scope_closed':True,'profile_rows':sorted(profile_rows,key=lambda r:(r['line'],r['function']))}
            observations.append(observation);event({'event':'scenario-terminal',**{k:v for k,v in observation.items() if k!='profile_rows'}})
    except BaseException as error:
        failure={'exception_class':type(error).__name__,'frames':[]};tb=error.__traceback__
        while tb:
            path=Path(tb.tb_frame.f_code.co_filename)
            if path.is_relative_to(ROOT):failure['frames'].append({'path':str(path.relative_to(ROOT)),'function':tb.tb_frame.f_code.co_name,'line':tb.tb_lineno})
            tb=tb.tb_next
        event({'event':'refusal','failure':failure,'messages_args_private_bytes_recorded':False})
    finally:
        try:rows=closed_inputs();source_exit=K.verify_all(ROOT,rows,code_sha256=PIN);dependency_exit=dependency_guard()
        except BaseException as error:failure=failure or {'exception_class':type(error).__name__,'phase':'exit-guard'}
    passed=failure is None and len(observations)==5 and source_entry==source_exit==1310 and dependency_entry and dependency_exit and fd_count()==fds_before
    report={'schema_version':'lab-T03-normal-pure-verification-cost-results/v1-candidate','result':'PASS-scoped-pure-cost-measurement' if passed else 'REFUSED','failure':failure,'input_selection_sha256':SELECTION_SHA,'helper_binding':helper,'source_manifest_binding':selection['source_manifest_binding'],'observations':observations,'source_entry_exit_rows':[source_entry,source_exit],'dependency_entry':dependency_entry,'dependency_exit':dependency_exit,'file_descriptors_entry_exit':[fds_before,fd_count()],'original_callbacks_clocks_verifier_order_or_row_hashes_changed':False,'raw_input_bodies_exported':False,'source_or_native_reader_Service_Agent_Session_lease_constructors_executed':False,'authority_effect':'none','task_complete':False,'whole_API_qualified':False,'Session_speedup_or_empirical_margin_established':False,'cost_limits':['cProfile overhead declared per scenario; profile duration is not uninstrumented duration.','Small single-process sample; OS page cache and scheduler load are uncontrolled.','Batch and rowwise variants exercise original helper functions without caching bytes or trust across invocations.','Pure technical file hashing proves no actor, permission, native-history admission or provenance authority.']}
    binding=save('results.json',report);event({'event':'actual-result','result':report['result'],'result_binding':binding});return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
