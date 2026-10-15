"""Freeze all executable source and predecessor bindings before any effects."""
import ast,hashlib,importlib.metadata,json,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    assert not (HERE/'source-manifest.json').exists() and not (HERE/'packages').exists() and not (HERE/'receipts').exists()
    rows={}
    def add(row):
        assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
        p=ROOT/row['path'];assert p.is_file() and not p.is_symlink() and bind(p)==row,row['path']
    predecessors=[]
    for name in ['custody-correction-v4','session-participation-v2','operator-context-v6','session-authority-v1','session-authority-v2']:
        path=HERE.parent/name/'source-manifest.json';m=json.loads(path.read_bytes());add(bind(path));predecessors.append(bind(path))
        for row in m['files']:add(row)
    for p in (HERE.parent/'session-participation-v2/packages/0001').rglob('*'):
        if p.is_file():add(bind(p))
    context=RUN/'context-R03-custody-participation-0001.json';c=json.loads(context.read_bytes());assert c['strict_coverage']=='PASS'
    for row in c['source_bindings']:add({'path':row['path'],'sha256':row['sha256']})
    for p in [context,RUN/'CONTEXT-R03-custody-participation-0001.md']:add(bind(p))
    counts={}
    for p in HERE.glob('*.py'):
        tree=ast.parse(p.read_bytes(),filename=str(p));counts[p.name]=len([n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')])
    assert sum(counts.values())==144 and counts['test_original_branch.py']==22 and counts['test_raw_source.py']==32 and counts['test_eligibility.py']==74 and counts['test_revision_witness.py']==16
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:add(bind(p))
    manifest={'schema_version':'lab-original-participation-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),
        'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},
        'parent_source_bindings':predecessors,'context_binding':bind(context),'test_method_counts':counts,
        'frozen_before_owned_store_and_signer_effects':True,'authority_effect':'none','actual_owner_outcome':None,
        'claim_ceiling':'A new exact original-byte current domain source. Full 34 API and 46 task scope remains; no live permission, Agent, final owner or canonical outcome.'}
    with (HERE/'source-manifest.json').open('x') as f:f.write(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(HERE/'source-manifest.json'),'files':len(rows),'tests':144}))
if __name__=='__main__':main()
