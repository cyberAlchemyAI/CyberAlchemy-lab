"""Freeze actual Reader7/Source8 dependencies without transferring test proof."""
import ast
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
HERE=ROOT/'product/lab/release-candidates/v1/interface/current-source-adapter-v7'
PRODUCER=HERE.parent/'current-participation-v8'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    assert not (HERE/'source-manifest.json').exists()
    terminal=RUN/'current-participation-build-terminal-0008.json';t=json.loads(terminal.read_bytes())
    assert t['actual_exit_code']==0 and t['result']=='PASS'
    outcome=json.loads((PRODUCER/'packages/0001/build-result.json').read_bytes())
    assert outcome['result']=='PASS' and outcome['actual_original_targets']==105 and outcome['signed_transactions']==5
    assert outcome['owned_store_and_key_removed'] and not Path(outcome['owned_root']).exists()
    rows={}
    def add(row):
        assert rows.get(row['path'],row)==row and bind(ROOT/row['path'])==row,row['path'];rows[row['path']]=row
    for name in ('source-manifest.json','packages/0001/manifest.json'):
        for row in json.loads((PRODUCER/name).read_bytes())['files']:add(row)
        add(bind(PRODUCER/name))
    for path in (terminal,Path(__file__).resolve(),*HERE.iterdir()):
        if path.is_file():
            if path.suffix=='.py':ast.parse(path.read_text())
            add(bind(path))
    value={'schema_version':'lab-current-source-adapter/v7-candidate','files':[rows[key] for key in sorted(rows)],
        'producer_source_binding':bind(PRODUCER/'source-manifest.json'),'producer_package_binding':bind(PRODUCER/'packages/0001/manifest.json'),
        'producer_terminal_binding':bind(terminal),'environment':{'python':platform.python_version(),
            'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},
        'authority_effect':'none','actual_owner_outcome':None,'source_adapter_qualified':False,
        'original_adapter_cases_requalified':False,'current_Agent_qualified':False,
        'claim_ceiling':'Exact frozen Reader7 selecting actual Source8; inherited adapter behavior, new current carriers and public source integration remain subject to actual qualification.'}
    with (HERE/'source-manifest.json').open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(HERE/'source-manifest.json'),'bound_files':len(rows),'source_adapter_qualified':False}),flush=True)


if __name__=='__main__':main()
