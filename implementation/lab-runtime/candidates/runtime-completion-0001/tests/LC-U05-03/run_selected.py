"""External complete pre/post binding guard; import no candidate before it."""
import argparse, hashlib, json, os, runpy, stat, sys
from pathlib import Path
R=Path('/home/vlad_/projects/CyberAlchemy-lab')
S=R/'implementation/lab-runtime/candidates/runtime-completion-0001'
T=S/'tests/LC-U05-03'
E=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U05-03'
def checked(path, expected):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as f:
        a=os.fstat(f.fileno())
        if not stat.S_ISREG(a.st_mode) or a.st_size>64*1024*1024: raise ValueError('selected input type')
        raw=f.read(64*1024*1024+1); b=os.fstat(f.fileno())
        if (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns) or hashlib.sha256(raw).hexdigest()!=expected: raise ValueError('selected input drift')
        return raw
def pairs(rows):
    value={}
    for k,v in rows:
        if k in value: raise ValueError('duplicate key')
        value[k]=v
    return value
def guard(path, expected):
    value=json.loads(checked(path,expected),object_pairs_hook=pairs)
    if set(value)!={'schema_version','files','owned_source_paths','authority_effect'} or value['schema_version']!='lab-u0503-selected-inputs/v1' or value['authority_effect']!='none' or not value['files']: raise ValueError('manifest')
    seen=set()
    for row in value['files']:
        if set(row)!={'kind','root_id','relative_path','sha256','size_bytes'} or row['kind']!='execution' or row['root_id'] not in ('repository','system'): raise ValueError('binding')
        rel=row['relative_path']
        if any(p in ('','.','..') for p in rel.split('/')) or '\\' in rel or '\0' in rel: raise ValueError('locator')
        key=row['root_id'],rel
        if key in seen: raise ValueError('duplicate binding')
        seen.add(key); p=(R if row['root_id']=='repository' else Path('/'))/rel
        if len(checked(p,row['sha256']))!=row['size_bytes']: raise ValueError('input size')
    actual=[str((S/'bootstrap'/n).relative_to(R)) for n in ('protected.py','environment.py')]
    for parent,dirs,files in os.walk(T,followlinks=False):
        for name in dirs+files:
            if (Path(parent)/name).is_symlink(): raise ValueError('source alias')
        actual += [str((Path(parent)/n).relative_to(R)) for n in files]
    if sorted(actual)!=value['owned_source_paths'] or any(('repository',x) not in seen for x in actual): raise ValueError('owned source inventory')
    return len(seen)
def main():
    p=argparse.ArgumentParser(); p.add_argument('--manifest',required=True,type=Path);p.add_argument('--manifest-sha',required=True)
    p.add_argument('--script',required=True,choices=('test_startup.py','test_inputs.py','test_host.py','test_original_contract.py','test_teardown.py','test_endpoint.py','test_endpoint_cold.py','test_composition.py','test_policy_compat.py','check_cleanup.py','actual_oracle.py'))
    a=p.parse_args();guard(a.manifest,a.manifest_sha)
    sys.path.insert(0,str(T));sys.argv=[str(T/a.script),'--temp-root',str(E)]
    try:runpy.run_path(sys.argv[0],run_name='__main__')
    finally:guard(a.manifest,a.manifest_sha)
if __name__=='__main__':main()
