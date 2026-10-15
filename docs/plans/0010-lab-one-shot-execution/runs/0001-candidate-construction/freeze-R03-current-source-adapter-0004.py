"""Freeze actual source/adapter dependencies after a successful owned producer."""
import ast,hashlib,importlib.metadata,json,platform
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
HERE=ROOT/'product/lab/release-candidates/v1/interface/current-source-adapter-v4'
PRODUCER=HERE.parent/'current-participation-v5'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    assert not (HERE/'source-manifest.json').exists()
    terminal=RUN/'current-participation-build-terminal-0005.json';t=json.loads(terminal.read_bytes())
    assert t['actual_exit_code']==0 and t['result']=='PASS'
    outcome=json.loads((PRODUCER/'packages/0001/build-result.json').read_bytes())
    assert outcome['result']=='PASS' and outcome['owned_store_and_key_removed'] and not Path(outcome['owned_root']).exists()
    rows={}
    def add(row):
        assert rows.get(row['path'],row)==row and bind(ROOT/row['path'])==row,row['path']
        rows[row['path']]=row
    for row in json.loads((PRODUCER/'source-manifest.json').read_bytes())['files']:add(row)
    for row in json.loads((PRODUCER/'packages/0001/manifest.json').read_bytes())['files']:add(row)
    for p in [PRODUCER/'source-manifest.json',PRODUCER/'packages/0001/manifest.json',terminal,Path(__file__).resolve(),*HERE.iterdir()]:
        if p.is_file():
            if p.suffix=='.py':ast.parse(p.read_bytes())
            add(bind(p))
    value={'schema_version':'lab-current-source-adapter/v4-candidate','files':[rows[k] for k in sorted(rows)],'producer_source_binding':bind(PRODUCER/'source-manifest.json'),'producer_package_binding':bind(PRODUCER/'packages/0001/manifest.json'),'producer_terminal_binding':bind(terminal),'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'original17method_ASTs_retained':True,'new_methods':3,'expected_tests':20,'authority_effect':'none','actual_owner_outcome':None,'current_Agent_qualified':False}
    p=HERE/'source-manifest.json'
    with p.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(p),'files':len(rows),'expected_tests':20}),flush=True)
if __name__=='__main__':main()
