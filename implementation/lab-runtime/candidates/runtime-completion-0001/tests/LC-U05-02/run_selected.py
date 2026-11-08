"""Guard every selected byte before importing candidate test code."""
import argparse,hashlib,json,os,runpy,stat,sys
from pathlib import Path
R=Path('/home/vlad_/projects/CyberAlchemy-lab')
S=R/'implementation/lab-runtime/candidates/runtime-completion-0001'
E=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U05-02'
def checked(path,digest):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as f:
        a=os.fstat(f.fileno())
        if not stat.S_ISREG(a.st_mode) or a.st_size>64*1024*1024:raise ValueError('input type/bound')
        raw=f.read(64*1024*1024+1);b=os.fstat(f.fileno())
        if (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns) or hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('input drift')
        return raw
def pairs(rows):
    result={}
    for k,v in rows:
        if k in result:raise ValueError('duplicate JSON field')
        result[k]=v
    return result
def guard(path,digest):
    value=json.loads(checked(path,digest),object_pairs_hook=pairs)
    if set(value)!={'schema_version','files','owned_source_paths','authority_effect'} or value['schema_version']!='lab-u0502-selected-inputs/v1' or value['authority_effect']!='none' or not value['files']:raise ValueError('manifest')
    seen=set()
    for b in value['files']:
        if set(b)!={'kind','root_id','relative_path','sha256','size_bytes'} or b['kind']!='execution' or b['root_id'] not in ('repository','system'):raise ValueError('binding')
        rel=b['relative_path'];parts=rel.split('/')
        if any(p in ('','.','..') for p in parts) or '\\' in rel or '\0' in rel:raise ValueError('path')
        key=(b['root_id'],rel)
        if key in seen:raise ValueError('duplicate binding')
        seen.add(key)
        p=(R if b['root_id']=='repository' else Path('/'))/rel
        if len(checked(p,b['sha256']))!=b['size_bytes']:raise ValueError('input size')
    actual=[]
    for scope in (S/'packaging',S/'tests/LC-U05-02'):
        for parent,dirs,files in os.walk(scope,followlinks=False):
            for name in dirs+files:
                p=Path(parent)/name
                if p.is_symlink():raise ValueError('source alias')
            for name in files:
                rel=str((Path(parent)/name).relative_to(R));actual.append(rel)
                if ('repository',rel) not in seen:raise ValueError('unselected source')
    if sorted(actual)!=value['owned_source_paths']:raise ValueError('source inventory')
def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--manifest-sha',required=True)
    p.add_argument('--script',choices=['test_installer.py','test_closure.py','test_cold.py','check_cleanup.py'],required=True);a=p.parse_args()
    guard(a.manifest,a.manifest_sha);sys.path.insert(0,str(S/'tests/LC-U05-02'))
    sys.argv=[str(S/'tests/LC-U05-02'/a.script),'--temp-root',str(E)]
    try:runpy.run_path(sys.argv[0],run_name='__main__')
    finally:guard(a.manifest,a.manifest_sha)
if __name__=='__main__':main()
