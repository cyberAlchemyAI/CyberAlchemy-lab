"""Externally anchored source closure before/after a closed inert test command."""
import bootstrap
from bootstrap import R,S,E,checked
import argparse,json,os,runpy,sys
from pathlib import Path
from lab_contracts.codec import parse

SCRIPTS=frozenset(('test_reader.py','test_semantic.py','test_full_inventory.py','test_requirements.py',
    'test_elf.py','test_original_elf.py','test_origins.py','test_composite.py','test_input_guard.py',
    'build_materialization_map.py','check_cleanup.py'))
SCOPES=(S/'dependency_graph',S/'environment',S/'tests/LC-U05-01')

def guard_snapshot(manifest,expected_sha,*,repository=R,scopes=SCOPES):
    raw=checked(manifest,expected_sha);value=parse(raw,64*1024*1024)
    if set(value)!={'schema_version','files','owned_source_paths','authority_effect'} or value['schema_version']!='lab-u0501-selected-inputs/v1' or value['authority_effect']!='none':raise ValueError('selected manifest')
    if type(value['files'])is not list or not value['files'] or type(value['owned_source_paths'])is not list:raise ValueError('selected inventory')
    seen=set()
    for b in value['files']:
        if set(b)!={'kind','root_id','relative_path','sha256','size_bytes'} or b['root_id'] not in ('repository','system'):raise ValueError('selected binding')
        if b['kind']!='execution' or type(b['size_bytes'])is not int or not 0<=b['size_bytes']<=64*1024*1024 or type(b['sha256'])is not str or len(b['sha256'])!=64 or any(c not in '0123456789abcdef' for c in b['sha256']):raise ValueError('selected binding domain')
        rel=b['relative_path'];parts=rel.split('/')
        if not rel or rel.startswith('/') or any(x in ('','.','..') for x in parts) or '\\' in rel or '\0' in rel:raise ValueError('selected relative path')
        key=(b['root_id'],rel)
        if key in seen:raise ValueError('duplicate selected input')
        seen.add(key);path=(repository if b['root_id']=='repository' else Path('/'))/rel
        if len(checked(path,b['sha256']))!=b['size_bytes']:raise ValueError('selected size drift')
    actual=[]
    for scope in scopes:
        if scope.is_symlink() or not scope.is_dir():raise ValueError('source scope changed')
        for parent,dirs,files in os.walk(scope,followlinks=False):
            for name in dirs:
                if (Path(parent)/name).is_symlink():raise ValueError('unselected source directory alias')
            for name in files:
                path=Path(parent)/name
                if path.is_symlink():raise ValueError('unselected source alias')
                rel=str(path.relative_to(repository));actual.append(rel)
                if ('repository',rel) not in seen:raise ValueError('unselected source bytes')
    if sorted(actual)!=value['owned_source_paths']:raise ValueError('source inventory changed')
    return raw

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--manifest-sha',required=True);p.add_argument('--script',choices=sorted(SCRIPTS),required=True);a=p.parse_args()
    if a.manifest.parent!=E or not a.manifest.name.startswith('input-manifest-'):raise ValueError('selected manifest locator')
    def guard():
        guard_snapshot(a.manifest,a.manifest_sha)
    guard();sys.argv=[str(S/'tests/LC-U05-01'/a.script)]+(['--verify'] if a.script=='build_materialization_map.py' else ['--temp-root',str(E)])
    code=0
    try:runpy.run_path(sys.argv[0],run_name='__main__')
    except SystemExit as result:
        if type(result.code)is not int:raise ValueError('closed test exit')
        code=result.code
    finally:guard()
    raise SystemExit(code)

if __name__=='__main__':main()
