"""Same-function code mutation only in a fresh isolated exact captured module."""
import argparse,hashlib,importlib.abc,importlib.util,json,os,stat,sys,tempfile
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).parent
ORIGINAL=ROOT/'product/lab/release-candidates/v1/interface/source-input-capture-v1-completion-0001/capture.py'
PIN='748a605d1ed0a6ac68de2fd87c407c49a9723e60bd3941c9f8498e702729ea3c'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def capture(path,pin):
    fds=[];links=[]
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);fds.append(parent)
        for name in path.parts[1:-1]:
            fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent);fds.append(fd);v=os.fstat(fd)
            links.append((parent,name,fd,(v.st_dev,v.st_ino)));parent=fd
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent);fds.append(fd);before=os.fstat(fd)
        assert stat.S_ISREG(before.st_mode) and before.st_size<1048576
        raw=b''
        while part:=os.read(fd,1048576):raw+=part;assert len(raw)<=before.st_size
        fields=lambda v:(v.st_dev,v.st_ino,v.st_mode,v.st_uid,v.st_size,v.st_mtime_ns,v.st_ctime_ns)
        assert fields(before)==fields(os.fstat(fd))==fields(os.stat(path.name,dir_fd=parent,follow_symlinks=False))
        for p,n,h,expected in links:
            v=os.stat(n,dir_fd=p,follow_symlinks=False);assert stat.S_ISDIR(v.st_mode) and (v.st_dev,v.st_ino)==expected
        assert sha(raw)==pin;return raw
    finally:
        for fd in reversed(fds):os.close(fd)
def load(path,pin,name):
    raw=capture(path,pin)
    class Loader(importlib.abc.SourceLoader):
        selected_source_sha256=pin
        def get_filename(self,name):return str(path)
        def get_data(self,filename):assert filename==str(path);return raw
        def get_code(self,name):return compile(raw,str(path),'exec',dont_inherit=True)
    spec=importlib.util.spec_from_file_location(name,path,loader=Loader());module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
def inert_read(self,parts,digest,retain=True):return b'UNVERIFIED-INERT-MARKER' if retain else None
parser=argparse.ArgumentParser();parser.add_argument('--probe-sha256',required=True);args=parser.parse_args();assert sha(Path(__file__).read_bytes())==args.probe_sha256
K=load(ORIGINAL,PIN,'_T03_isolated_original_integrity_probe')
root=Path(tempfile.mkdtemp(prefix='cal-T03-kernel-integrity-'));root.chmod(0o700)
fd=os.open(root/'inert.bin',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.write(fd,b'actual independently pinned inert data');os.close(fd)
row={'path':'inert.bin','sha256':sha((root/'inert.bin').read_bytes())};bad={**row,'sha256':'0'*64}
def refused():
    try:K.capture_one(root,bad,code_sha256=PIN)
    except ValueError:return True
    raise AssertionError('baseline invalid digest accepted')
baseline=K.capture_one(root,row,code_sha256=PIN);assert baseline==(root/'inert.bin').read_bytes();assert refused()
fds=len(os.listdir('/proc/self/fd'));method=K.Batch.read;code=method.__code__
try:
    method.__code__=inert_read.__code__
    assert K.Batch.read is method and K._CALLBACKS[3] is method
    K.kernel_guard(PIN)
    observed=K.capture_one(root,bad,code_sha256=PIN)
    assert observed==b'UNVERIFIED-INERT-MARKER' and observed!=baseline
    result={'same_function_object_preserved':True,'same_callback_tuple_equality_preserved':True,'kernel_guard_accepted_modified_code':True,'capture_one_returned_inert_marker_against_invalid_file_digest':True,'selected_file_was_not_read_or_hashed_by_mutated_read':True}
finally:method.__code__=code
assert K.capture_one(root,row,code_sha256=PIN)==baseline and refused()
assert len(os.listdir('/proc/self/fd'))==fds and not getattr(K._ACTIVE,'value',False)
assert capture(ORIGINAL,PIN)==ORIGINAL.read_bytes() and sha(Path(__file__).read_bytes())==args.probe_sha256
out={'schema_version':'lab-T03-same-function-code-counterexample/v1-candidate','result':'REPRODUCED','original_kernel_sha256':PIN,'actual_selected_installation':'runtime-dependencies-v2-completion-0001/installations/0004','baseline_exact_capture_passed':True,'baseline_and_restored_invalid_digest_refused':True,'isolated_mutation':result,'mutated_method_code_restored':True,'descriptor_delta':0,'owned_root_retained':True,'owned_root_locator_sha256':sha(str(root).encode()),'original_production_software_or_process_changed':False,'Lab_lease_native_or_private_keys':False,'concurrent_load':'Root positive learning session 81567 was ongoing; no performance inference.','authority_effect':'none','task_complete':False}
with (HERE/'counterexample.json').open('x') as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'result':out['result'],'counterexample_sha256':sha((HERE/'counterexample.json').read_bytes()),'descriptor_delta':0}))
