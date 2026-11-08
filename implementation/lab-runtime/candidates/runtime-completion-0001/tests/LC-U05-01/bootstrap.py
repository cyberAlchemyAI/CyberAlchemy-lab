"""Guard selected accepted dependencies before importing any candidate package."""
import hashlib, json, os, stat, sys
from pathlib import Path
R = Path('/home/vlad_/projects/CyberAlchemy-lab')
S = R/'implementation/lab-runtime/candidates/runtime-completion-0001'
E = R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U05-01'
OLD = E.parent/'LC-U01-02'
PREFIX = OLD/'python-bytecode-cache-disabled-0002'
DEP = R/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps'

def checked(path, expected=None):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > 64*1024*1024:
            raise ValueError('input type/bound')
        raw = stream.read(64*1024*1024+1)
        after = os.fstat(stream.fileno())
        fields = lambda s: (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        if fields(before) != fields(after): raise ValueError('input changed')
        if expected is not None and hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('selected digest')
        return raw

checked(PREFIX, 'a5712f1655f68e6f8fe7cacbfb454dc0be0cd1ad8f22f1788fbad7b8adafae29')
if os.environ.get('PYTHONPYCACHEPREFIX') != str(PREFIX) or not sys.flags.no_site or not sys.dont_write_bytecode:
    raise ValueError('guarded Python required')
PREVIOUS = json.loads(checked(OLD/'coordinator-dispatch-0002.json',
    '478e5ab1966aabe8c758121d51543b8366d8eb38558da54b9c3405fda2346864'))
IMPORT_BINDINGS = []
for b in PREVIOUS['source_bindings']:
    if b['root_id'] == 'repository':
        p = R/b['relative_path']
        if any(p.is_relative_to(base) for base in (S/'contracts',S/'selectors',DEP)):
            checked(p,b['sha256']);IMPORT_BINDINGS.append(b)
sys.path[:0] = [str(S),str(S/'contracts'),str(S/'selectors'),str(DEP)]
