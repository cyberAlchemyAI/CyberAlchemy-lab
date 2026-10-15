"""Stage a distinct successor; preserve the actual frozen API13 and failures."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api-integration-v13'
NEW=BASE/'api-integration-v14'
SOURCE='213ebd20742b8f7c8af0aa6614b71f735d574e89d22c92c094c3657c0d189322'
PROFILE='73d832dcec7776f6a8a3064ac9c11a60ba086c6802bb81c159058dcea9d692b2'

def main():
    assert not NEW.exists()
    assert hashlib.sha256((OLD/'contract-profile.json').read_bytes()).hexdigest()==PROFILE
    spec=importlib.util.spec_from_file_location('_cal_API14_parent_guard',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    guard.verify(SOURCE)
    shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('receipts','__pycache__'))
    for name in ('source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json'):
        (NEW/name).unlink()
    path=NEW/'auth.py'
    original=path.read_text()
    old="        profile=source.source_selection(self.policy['source_name'])['engine_pins']['profile_sha256']"
    assert original.count(old)==1
    replacement="""        selected_source=source.source_selection(self.policy['source_name'])
        if self.policy['source_name'] in source.HISTORY_NAMES:
            profile=selected_source['profile_binding']['sha256']
        else:
            profile=selected_source['engine_pins']['profile_sha256']"""
    path.write_text(original.replace(old,replacement))
    for path in NEW.glob('*.py'):
        ast.parse(path.read_text())
    guard.verify(SOURCE)
    print(json.dumps({'result':'STAGED_UNQUALIFIED','actual_history_profile_selected_before_generic_engine_lookup':True,
                      'predecessor_unchanged':True,'authority_effect':'none','task_complete':False}),flush=True)

if __name__=='__main__':
    main()
