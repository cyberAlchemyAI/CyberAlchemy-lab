"""Pinned predecessor imports; outer selected runner pins this new unit first."""
import hashlib,json,os,stat,sys
from pathlib import Path
R=Path('/home/vlad_/projects/CyberAlchemy-lab')
S=R/'implementation/lab-runtime/candidates/runtime-completion-0001'
E=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U05-02'
PREV=E.parent/'LC-U05-01';OLD=E.parent/'LC-U01-02'
PREFIX=OLD/'python-bytecode-cache-disabled-0002'
DEP=R/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps'
def checked(path,expected=None):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as f:
        a=os.fstat(f.fileno())
        if not stat.S_ISREG(a.st_mode) or a.st_size>64*1024*1024:raise ValueError('selected regular bounded input')
        raw=f.read(64*1024*1024+1);b=os.fstat(f.fileno())
        key=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
        if key(a)!=key(b) or (expected and hashlib.sha256(raw).hexdigest()!=expected):raise ValueError('selected input drift')
        return raw
checked(PREFIX,'a5712f1655f68e6f8fe7cacbfb454dc0be0cd1ad8f22f1788fbad7b8adafae29')
if os.environ.get('PYTHONPYCACHEPREFIX')!=str(PREFIX) or not sys.flags.no_site or not sys.dont_write_bytecode:raise ValueError('Python guard')
checked(PREV/'coordinator-acceptance-0001.json','e0ec7282aebaa548c7b041fa2090a6c066cdc19c403afe64730a9574e72437b6')
POST=json.loads(checked(PREV/'implementation-postimage-0001.json','b782d11f709a1b2c7fa25c044efd36e8ef60bdee6e69d1a91005a65200a8caba'))
for b in POST['files']:
    if len(checked(R/b['path'],b['sha256']))!=b['size_bytes']:raise ValueError('accepted predecessor drift')
IMPORT=json.loads(checked(OLD/'coordinator-dispatch-0002.json','478e5ab1966aabe8c758121d51543b8366d8eb38558da54b9c3405fda2346864'))
for b in IMPORT['source_bindings']:
    if b['root_id']=='repository' and any((R/b['relative_path']).is_relative_to(p) for p in (S/'contracts',S/'selectors',DEP)):
        checked(R/b['relative_path'],b['sha256'])
sys.path[:0]=[str(S/'packaging'),str(S),str(S/'contracts'),str(S/'selectors'),str(DEP)]
