"""Selected stdlib ctypes initialization only; no Lab/source/native dispatch."""
import fcntl, hashlib, importlib, json, os, stat, sys
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
BASE=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
LIB=BASE/'lib/abi/libffi.so.8'
SELECTION=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'

def need(ok,why):
    if not ok:raise ValueError(why)

def snapshots(label):
    rows=[]
    for name in os.listdir('/proc/self/fd'):
        try:
            fd=int(name);s=os.fstat(fd);target=os.readlink('/proc/self/fd/'+name)
            rows.append({'fd':fd,'device':s.st_dev,'inode':s.st_ino,'mode':s.st_mode,
                         'is_selected_libffi':target==str(LIB),'access_mode':fcntl.fcntl(fd,fcntl.F_GETFL)&os.O_ACCMODE,
                         'close_on_exec':bool(fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC)})
        except OSError:continue
    return {'phase':label,'fds':sorted(rows,key=lambda r:r['fd'])}

def main():
    need(Path(sys.executable)==BASE/'bin/python'and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,'selected isolated0004 Python required')
    need('ctypes'not in sys.modules,'fresh ctypes initialization required')
    raw=SELECTION.read_bytes();need(hashlib.sha256(raw).hexdigest()=='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835','independent base selection differs')
    row=next(r for r in json.loads(raw)['inputs']if r['destination']=='lib/abi/libffi.so.8')
    need(hashlib.sha256(LIB.read_bytes()).hexdigest()==row['sha256'],'selected library bytes differ')
    before=LIB.stat();need(before.st_uid==os.getuid()and stat.S_IMODE(before.st_mode)==0o644,'selected library ownership/mode differs')
    observations=[snapshots('before-ctypes-import')]
    ctypes=importlib.import_module('ctypes');observations.append(snapshots('after-ctypes-import'))
    for _ in range(20):need(importlib.import_module('ctypes')is ctypes,'stdlib module identity changed')
    observations.append(snapshots('after20-repeated-ctypes-imports'))
    import gc
    gc.collect();observations.append(snapshots('after-garbage-collection'))
    need(hashlib.sha256(LIB.read_bytes()).hexdigest()==row['sha256'],'selected library changed')
    value={'authority_effect':'none','observations':observations,'selected_library_binding':{'path':str(LIB),'sha256':row['sha256']},
           'Lab_API_native_Source_or_catalog_calls':0,'original_callbacks_or_clocks_changed':False,
           'claim_ceiling':'Only selected CPython ctypes initialization/repeated-import descriptor behavior; original native attempt descriptor cause and future operation resource stability require separate correspondence.'}
    fd=os.open(HERE/'result.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w')as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    return 0

if __name__=='__main__':raise SystemExit(main())
