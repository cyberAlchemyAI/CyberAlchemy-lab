"""Stage a distinct successor; preserve the actual frozen API14 and failures."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api-integration-v14'
NEW=BASE/'api-integration-v15'
SOURCE='aea84d1d97c2780e8fb172b6dd4d8807f2e89892a02f0fe0e5daab97b3f0c240'
PROFILE='327d3c480168b0008597969e31e11e73f429370a226bd16370245e82ef78fb16'

def main():
    assert not NEW.exists()
    assert hashlib.sha256((OLD/'contract-profile.json').read_bytes()).hexdigest()==PROFILE
    spec=importlib.util.spec_from_file_location('_cal_API15_parent_guard',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    guard.verify(SOURCE)
    shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('receipts','__pycache__'))
    for name in ('source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json'):
        (NEW/name).unlink()
    for path in NEW.glob('*.py'):
        ast.parse(path.read_text())
    guard.verify(SOURCE)
    print(json.dumps({'result':'STAGED_UNQUALIFIED','preparation_only':True,
                      'predecessor_unchanged':True,'authority_effect':'none','task_complete':False}),flush=True)

if __name__=='__main__':
    main()
