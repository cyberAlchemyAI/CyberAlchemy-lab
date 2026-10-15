"""Freeze exact candidate source and original authority artifacts."""
import ast
import hashlib
import json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
OWN=ROOT/'product/lab/release-candidates/v1/interface/checkpoint-owner-verification-v1'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    files=sorted(p for p in OWN.iterdir() if p.is_file())
    for p in files:
        if p.suffix=='.py':ast.parse(p.read_bytes())
    own=[bind(p) for p in files]+[bind(Path(__file__).resolve())]
    inputs=[bind(ROOT/f'authority/artifact-types/{kind}/v1/{name}')
        for kind in ('principal','role-assignment','authority-claim','authority-boundary','decision-scope')
        for name in ('schema.json','fixtures/valid/record.json')]
    inputs.extend(bind(ROOT/p) for p in (
        'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json',
        'product/lab/release-candidates/v1/interface/api-v59/source-manifest.json',
        'product/lab/release-candidates/v1/interface/checkpoint-resolution-rules-v2/source-manifest.json',
        'product/lab/release-candidates/v1/interface/checkpoint-resolution-rules-v2/receipts/checks-0001.json',
        'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'))
    rows=own+inputs
    value={'schema_version':'lab-checkpoint-owner-verification-source/v1-candidate','files':own,'input_bindings':inputs,
        'source_sha256':hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),
        'actual_owner_outcome':None,'live_authority_verified':False,'public_checkpoint_handler_qualified':False,
        'authority_effect':'none','task_complete':False,'goal_complete':False}
    path=OWN/'source-manifest.json'
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'FROZEN','source_sha256':value['source_sha256'],'manifest_binding':bind(path)}),flush=True)
if __name__=='__main__':main()
