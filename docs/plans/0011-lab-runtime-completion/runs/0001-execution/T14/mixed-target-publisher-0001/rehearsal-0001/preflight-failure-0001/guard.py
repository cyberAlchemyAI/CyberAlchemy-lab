"""Selected rehearsal-only full table guard; no production callbacks changed."""
import hashlib,json,os,stat
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
MF=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T14/mixed-target-publisher-0001/source-manifest.json'
MFPIN='9161e89f0d622fbe4c6f8d95fbf1e7c412cd07318fb817444c777cbcf2fdb6b6'
DEP=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
DEPPIN='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
I=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
SELF_SELECTION=None;SELF_PIN=None;LAST=None

def sha(raw):return hashlib.sha256(raw).hexdigest()
def stamp(st):return (st.st_dev,st.st_ino,st.st_uid,st.st_mode,st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
def capture(path,pin,mode=None,size=None):
    if type(pin) is not str or len(pin)!=64:raise ValueError('independent digest required')
    path=Path(path);fds=[];links=[]
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);fds.append(parent)
        for name in path.parts[1:-1]:
            fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);fds.append(fd)
            links.append((parent,name,fd,(os.fstat(fd).st_dev,os.fstat(fd).st_ino)));parent=fd
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);fds.append(fd);before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):raise ValueError('selected file type')
        if mode is not None and stat.S_IMODE(before.st_mode)!=mode:raise ValueError('selected mode')
        if size is not None and before.st_size!=size:raise ValueError('selected size')
        chunks=[]
        while True:
            piece=os.read(fd,1024*1024)
            if not piece:break
            chunks.append(piece)
        raw=b''.join(chunks)
        if stamp(before)!=stamp(os.fstat(fd)) or stamp(before)!=stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False)):raise ValueError('selected leaf changed')
        for p,n,h,identity in links:
            s=os.stat(n,dir_fd=p,follow_symlinks=False)
            if (s.st_dev,s.st_ino)!=identity or not stat.S_ISDIR(s.st_mode):raise ValueError('selected parent changed')
        if sha(raw)!=pin:raise ValueError('selected digest')
        return raw
    finally:
        for fd in reversed(fds):os.close(fd)

def verify():
    global LAST
    source=json.loads(capture(MF,MFPIN));software={}
    for row in source['files']:software[row['path']]=capture(ROOT/row['path'],row['sha256'],size=row['size_bytes'])
    dependency=json.loads(capture(DEP,DEPPIN));rows={r['destination']:r for r in dependency['inputs']};rows.update(dependency['wheel_members'])
    for path,row in rows.items():capture(I/path,row['sha256'],mode=row['mode'],size=row['size_bytes'])
    own=json.loads(capture(SELF_SELECTION,SELF_PIN))
    for row in own['files']:capture(row['path'],row['sha256'],size=row['size_bytes'])
    LAST={'source_rows':len(source['files']),'installed_dependency_rows':len(rows),'rehearsal_code_rows':len(own['files']),
          'source_manifest_sha256':MFPIN,'dependency_selection_sha256':DEPPIN,'rehearsal_selection_sha256':SELF_PIN}
    return software
