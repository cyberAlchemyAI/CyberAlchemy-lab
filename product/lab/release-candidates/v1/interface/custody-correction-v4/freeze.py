"""Author complete source pins before any candidate runtime effect."""
import ast,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];OLD=HERE.parent/'custody-correction-v1'
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def put(p,value):p.open('x').write(json.dumps(value,indent=2,sort_keys=True)+'\n')
def main():
    assert not (HERE/'source-manifest.json').exists()
    # Host paths are the only changes to all original runtime/custody assertions.
    original=ROOT/'implementation/lab-runtime/v2/tests/test_runtime.py';raw=original.read_text()
    replacements=[('sys.path.insert(0, str(Path(__file__).resolve().parents[1]))','sys.path.insert(0, '+repr(str(HERE/'runtime'))+')'),
        ('PACKAGE = Path(__file__).resolve().parents[1]','PACKAGE = Path('+repr(str(HERE/'runtime'))+')'),
        ('REPO = PACKAGE.parents[2]','REPO = Path('+repr(str(ROOT))+')'),
        ('PACKAGE.parent / "v1"','Path('+repr(str(ROOT/'implementation/lab-runtime/v1'))+')'),
        ('PACKAGE.parent / "v1/profile.json"','Path('+repr(str(ROOT/'implementation/lab-runtime/v1/profile.json'))+')'),
        ('str(PACKAGE / "lab.py"),','str(PACKAGE / "lab.py"), "--repo", str(REPO),')]
    edits=[]
    for before,after in replacements:
        count=raw.count(before);assert count>=1;raw=raw.replace(before,after);edits.append({'before':before,'after':after,'occurrences':count})
    assert sum(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(ast.parse(raw)))==38
    (HERE/'regression-sources/test_runtime.py').open('x').write(raw)
    original_custody=HERE.parent/'runtime-byte-custody-v3/runtime/tests/test_custody.py'
    raw_custody=original_custody.read_text();before='PACKAGE=Path(__file__).resolve().parents[1];REPO=PACKAGE.parents[6]'
    after='PACKAGE=Path('+repr(str(HERE/'runtime'))+');REPO=Path('+repr(str(ROOT))+')'
    assert raw_custody.count(before)==1;raw_custody=raw_custody.replace(before,after)
    assert sum(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(ast.parse(raw_custody)))==28
    (HERE/'regression-sources/test_custody.py').open('x').write(raw_custody)
    put(HERE/'regression-sources/adaptation.json',{'authority_effect':'none','original_runtime':bind(original),
        'original_custody':bind(original_custody),'runtime_edits':edits,'custody_edits':[{'before':before,'after':after,'occurrences':1}],
        'original_assertions_changed':False,'runtime_cases':38,'custody_cases':28})
    for p in HERE.rglob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
    parent=json.loads((OLD/'source-manifest.json').read_bytes())
    for row in parent['files']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
    runtime=HERE/'runtime';files=[bind(p) for p in sorted(runtime.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
    changed=[]
    for row in files:
        p=ROOT/row['path'];old=OLD/'runtime'/p.relative_to(runtime)
        if not old.exists() or sha(old)!=row['sha256']:changed.append({'candidate_binding':row,'parent_binding':bind(old) if old.exists() else None})
    manifest={'schema_version':'lab-R03-correction-engine-manifest/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
        'engine_id':'lab-operator-reference-correction/v1-candidate','parent_binding':bind(OLD/'engine-manifest.json'),
        'files':files,'changed_files':changed,'profile_binding':bind(runtime/'profile.json'),
        'mapping_binding':json.loads((OLD/'engine-manifest.json').read_bytes())['mapping_binding'],
        'correction_profile_binding':json.loads((OLD/'engine-manifest.json').read_bytes())['correction_profile_binding']}
    put(HERE/'engine-manifest.json',manifest)
    put(HERE/'pins.json',{'manifest_sha256':sha(HERE/'engine-manifest.json'),'engine_id':manifest['engine_id'],
        'mapping_sha256':manifest['mapping_binding']['sha256'],'profile_sha256':manifest['profile_binding']['sha256'],
        'correction_profile_sha256':manifest['correction_profile_binding']['sha256']})
    inputs={r['path']:r for r in parent['files']}
    failed=HERE.parent/'custody-correction-v2'
    for row in json.loads((failed/'source-manifest.json').read_bytes())['files']:inputs[row['path']]=row
    previous=HERE.parent/'custody-correction-v3'
    for row in json.loads((previous/'source-manifest.json').read_bytes())['files']:inputs[row['path']]=row
    for p in [previous/'source-manifest.json',*sorted((previous/'receipts/0001').rglob('*')),
        *previous.glob('*-000*.log'),RUN/'context-R03-custody-correction-0005.json',RUN/'custody-correction-terminal-v3-0001.json',failed/'source-manifest.json',failed/'receipts/0001/guards.json',failed/'receipts/0001/schemas.json',failed/'guards-0001.log',failed/'schemas-0001.log',
        RUN/'context-R03-custody-correction-0003.json',RUN/'custody-prototype-terminal-0001.json',OLD/'source-manifest.json',OLD/'receipts/0001/guards.json',OLD/'receipts/0001/journey.json',
        RUN/'context-R03-custody-correction-0002.json',RUN/'R03-CUSTODY-SCHEMA-BINDING-0001.md']:
        if p.is_file():inputs[bind(p)['path']]=bind(p)
    for p in sorted(HERE.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:inputs[bind(p)['path']]=bind(p)
    put(HERE/'source-manifest.json',{'schema_version':'lab-custody-correction-source/v2-candidate',
        'authority_effect':'none','actual_owner_outcome':None,'frozen_before_runtime_effects':True,
        'parent_source_binding':bind(OLD/'source-manifest.json'),'engine_manifest_binding':bind(HERE/'engine-manifest.json'),
        'files':sorted(inputs.values(),key=lambda r:r['path']),
        'claim_ceiling':'Exact schema and retained correction candidate. Full public API and original plan remain open.'})
    print(json.dumps({'source':bind(HERE/'source-manifest.json'),'files':len(inputs),'runtime_files':len(files),'deltas':len(changed)}))
if __name__=='__main__':main()
