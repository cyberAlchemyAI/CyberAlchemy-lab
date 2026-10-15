"""Bounded pure own-code qualification, not an API/Source/dependency guard."""
import hashlib,json,os,stat,sys,time,types,uuid
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).resolve().parent
def _capture_helper(path,expected):
    fds=[];links=[]
    def stamp(st):return (st.st_dev,st.st_ino,st.st_uid,st.st_mode,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
    def directory(st):return (st.st_dev,st.st_ino,st.st_uid,st.st_mode)
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);fds.append(parent)
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
            links.append((parent,part,directory(os.fstat(child))));fds.append(child);parent=child
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent);fds.append(fd);before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size>1024*1024:raise ValueError('bounded regular bootstrap helper required')
        raw=b''
        while True:
            block=os.read(fd,1024*1024+1-len(raw))
            if not block:break
            raw+=block
            if len(raw)>1024*1024:raise ValueError('bootstrap helper too large')
        if stamp(before)!=stamp(os.fstat(fd)) or stamp(before)!=stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False)):raise ValueError('bootstrap helper detached')
        if any(directory(os.stat(name,dir_fd=parent,follow_symlinks=False))!=selected for parent,name,selected in links):raise ValueError('bootstrap ancestor detached')
        if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('independent bootstrap helper hash differs')
        return raw
    finally:
        for fd in reversed(fds):os.close(fd)


_CAPTURE_PIN='979c76d1f974430044b7c266b09482a256bde8d03bac081c876728a2be49285c'

def run(expected_manifest):
    C=types.ModuleType('_cal_T35_pure_capture_'+uuid.uuid4().hex);C.__file__=str(HERE/'capture.py');sys.modules[C.__name__]=C
    exec(compile(_capture_helper(HERE/'capture.py',_CAPTURE_PIN),C.__file__,'exec'),C.__dict__)
    manifest=json.loads(C.read(HERE/'source-manifest.json',expected_manifest));rows={r['path']:r for r in manifest['files']}
    labels=['observe.py','phase_controls.py','driver.py','capture.py','positive_lifecycle.py','security_lifecycle.py',
            'preimage/driver.py','preimage/capture.py','preimage/positive_lifecycle.py','preimage/security_lifecycle.py']
    captured={}
    for label in labels:
        path=HERE/label;row=rows[str(path.relative_to(ROOT))];raw=C.read(path,row['sha256']);C.require(len(raw)==row['size_bytes'],'pure input size')
        captured[label]=raw
    name='_cal_T35_phase_controls_'+uuid.uuid4().hex;module=C.module(name,HERE/'phase_controls.py',captured['phase_controls.py'])
    start=time.monotonic();result=module.check(captured)
    for label in labels:
        path=HERE/label;row=rows[str(path.relative_to(ROOT))];C.require(C.read(path,row['sha256'])==captured[label],'pure own input changed')
    C.read(HERE/'source-manifest.json',expected_manifest)
    return {'schema_version':'lab-T35-phase-only-pure-qualification/v1-candidate','result':'PASS-pure-component-only','pid':os.getpid(),
        'source_manifest_sha256':expected_manifest,'selected_interpreter':sys.executable,'direct_pure_input_rows':len(labels),
        'coverage':'Exact captured ten pure-control inputs entry/exit only; full inherited component, installed dependency and actual API Source guards not executed.',
        'elapsed_seconds':time.monotonic()-start,'pure_controls':result,'actual_Lab_native_or_lease':False,
        'actual_runtime_calibration':False,'authority_effect':'none','task_complete':False}

if __name__=='__main__':print(json.dumps(run(sys.argv[1]),sort_keys=True))
