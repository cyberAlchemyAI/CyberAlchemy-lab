"""Pure path preparation candidate verification, no Lab runtime or mutation."""
import cProfile,hashlib,importlib.abc,importlib.util,json,os,re,stat,sys,time,uuid
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
SELECTION_SHA='7fb19388d18d539a98690a821a07d9cb9a0b35313295f893251242651b5c6c0b'

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
    with (HERE/'benchmark-events.jsonl').open('a') as f:f.write(json.dumps(value,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
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

def main():
    import tempfile
    candidate=selected_helper(selection['candidate_helper_binding']);caller=selected_helper(selection['caller_contract_binding']);pin=selection['candidate_helper_binding']['sha256']
    contract=caller.select(candidate,expected_path=ROOT/selection['candidate_helper_binding']['path'],expected_sha256=pin)
    need(len(contract)==5);caller.check(contract,candidate);before=fd_count()
    with tempfile.TemporaryDirectory(prefix='own-fivefield-compatibility-',dir=HERE) as folder:
        root=Path(folder);data=b'own ordinary selected helper compatibility\n';(root/'file').write_bytes(data)
        row={'path':'file','sha256':sha(data)};need(candidate.capture_one(root,row,code_sha256=pin)==data)
        need(candidate.verify_all(root,[row],code_sha256=pin)==1);need(not candidate._ACTIVE.value)
        caller.check(contract,candidate)
    need(before==fd_count());caller.check(contract,candidate)
    value={'schema_version':'lab-T03-helper-only-original-companion-compatibility/v1-candidate','authority_effect':'none','result':'PASS-exact-new-helper-with-unchanged4222-fivefield-companion','candidate_helper_binding':selection['candidate_helper_binding'],'unchanged_caller_binding':selection['caller_contract_binding'],'descriptor_delta':0,'original_callbacks_clocks_codeobjects_or_globals_mutated':False,'Lab_native_Source_reader_mapper_Context_Service_Session_or_lease_constructed':False,'task_complete':False}
    save('helper-only-compatibility-result.json',value);print(json.dumps({'result':value['result'],'descriptor_delta':0}))
if __name__=='__main__':main()
