"""Bind the pure checkpoint candidate and exact original schema/native inputs."""
import ast
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
RULES=ROOT/'product/lab/release-candidates/v1/interface/checkpoint-resolution-rules-v2'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    files=sorted(p for p in RULES.iterdir() if p.is_file())
    for p in files:
        if p.suffix=='.py':ast.parse(p.read_bytes())
    own=[bind(p) for p in files]+[bind(Path(__file__).resolve()),bind(RUN/'author-checkpoint-resolution-rules-0002.py')]
    inputs=[]
    for folder in ('docs/proposals/0007-lab-integrated-schema-package/schemas','docs/proposals/0006-lab-artifact-storage/schemas'):
        inputs.extend(bind(p) for p in sorted((ROOT/folder).glob('*.json')))
    for kind in ('decision-checkpoint','decision-bundle'):
        inputs.extend(bind(ROOT/f'authority/artifact-types/{kind}/v1/{name}') for name in ('schema.json','fixtures/valid/record.json'))
    inputs.append(bind(ROOT/'authority/artifact-types/work/v1/fixtures/valid/record.json'))
    inputs.extend(bind(ROOT/p) for p in ('product/lab/release-candidates/v1/interface/checkpoint-resolution-rules-v1/source-manifest.json','product/lab/release-candidates/v1/interface/checkpoint-resolution-rules-v1/receipts/checks-0001.json','product/lab/release-candidates/v1/interface/checkpoint-resolution-rules-v1/receipts/actual-0001.log'))
    native=ROOT/'product/lab/release-candidates/v1/interface/custody-correction-v4/runtime'
    inputs.extend(bind(native/p) for p in ('lab_runtime/__init__.py','lab_runtime/common.py','lab_runtime/custody.py','schemas/artifact-content-entry.schema.json'))
    value={'schema_version':'lab-checkpoint-pure-rule-source/v1-candidate','files':own,'input_bindings':inputs,
        'source_sha256':hashlib.sha256(json.dumps(own+inputs,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),
        'authority_effect':'none','actual_owner_outcome':None,'actual_runtime_qualified':False,'task_complete':False,'goal_complete':False}
    p=RULES/'source-manifest.json'
    with p.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':'FROZEN','source_sha256':value['source_sha256'],'source_manifest_binding':bind(p),
        'original_schema_native_input_count':len(inputs),'actual_runtime_qualified':False}),flush=True)
if __name__=='__main__':main()
