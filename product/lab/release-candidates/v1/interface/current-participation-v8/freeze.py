"""Freeze the new owned producer before exact signed development effects."""
import ast
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
OLD=HERE.parent/'current-participation-v5';ADAPTER=HERE.parent/'current-source-adapter-v7'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    assert not (HERE/'source-manifest.json').exists() and not (HERE/'packages').exists()
    rows={}
    def add(row):
        assert rows.get(row['path'],row)==row and bind(ROOT/row['path'])==row,row['path'];rows[row['path']]=row
    old=json.loads((OLD/'source-manifest.json').read_bytes());package=json.loads((OLD/'packages/0001/manifest.json').read_bytes())
    for row in old['files']+package['files']:add(row)
    for path in [OLD/'source-manifest.json',OLD/'packages/0001/manifest.json',
                 RUN/'authorization.json',RUN/'Machine-policy-custody-lesson-0001/index.json',
                 RUN/'API85-machine-lifecycle-full-0001.json',RUN/'API85-machine-lifecycle-full-terminal-0001.json']:
        add(bind(path))
    learning=json.loads((RUN/'Machine-policy-custody-lesson-0001/index.json').read_bytes())
    for row in learning['files']:add(row)
    previous_failed=HERE.parent/'current-participation-v7'
    add(bind(previous_failed/'source-manifest.json'))
    add(bind(RUN/'current-participation-build-terminal-0007.json'))
    for path in previous_failed.glob('packages/0001/**/*'):
        if path.is_file():add(bind(path))
    kinds=['principal','principal-reference','policy','challenge-contract','evidence-set','challenge-event','decision','effect','decision-scope','authority-boundary']
    for kind in kinds:
        version='v2' if kind in ('policy','decision','decision-scope') else 'v1'
        folder=ROOT/'authority/artifact-types'
        if version=='v2':folder=folder/'candidates/0013-governance-transaction-surface/impacted-carrier-successors'
        add(bind(folder/kind/version/'fixtures/valid/record.json'))
    for folder in (HERE,ADAPTER,HERE.parent/'challenge-resolution-v2',HERE.parent/'typed-relation-registration-v2',HERE.parent/'typed-relation-schema-v4'):
        for path in sorted(folder.glob('*')):
            if path.is_file():
                if path.suffix=='.py':ast.parse(path.read_text())
                add(bind(path))
    episode=json.loads((HERE/'episode-contract.json').read_bytes())
    prior=json.loads((OLD/'episode-contract.json').read_bytes())
    assert all(episode[key]!=prior[key] for key in ('principal_ref','assignment_version_ref','period_ref'))
    value={'schema_version':'lab-current-participation-source/v8-candidate','files':[rows[key] for key in sorted(rows)],
        'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},
        'failed_construction_predecessor_binding':bind(previous_failed/'source-manifest.json'),'previous_candidate_source_binding':bind(OLD/'source-manifest.json'),'previous_candidate_package_binding':bind(OLD/'packages/0001/manifest.json'),
        'fixed_new_episode_binding':bind(HERE/'episode-contract.json'),'implementation_code_binding':bind(ADAPTER/'reader.py'),
        'implementation_entrypoint_ref':ADAPTER.relative_to(ROOT).as_posix()+'/reader.py#SelectedReader.open_signed',
        'preserved_original_targets':30,'fresh_participation_targets':21,'contest_targets':22,
        'expected_original_targets':105,'expected_signed_transactions':5,'expected_type_registration_targets':32,
        'exact_gate_method_binding':bind(HERE.parent/'challenge-resolution-v2/gate.py'),
        'resolution_object_selection_method_binding':bind(HERE.parent/'challenge-resolution-v2/preparation.py'),
        'source5_renewed':False,'private_keys_exported':False,'current_Agent_qualified':False,
        'public_API_resolution_qualified':False,'learning_context_qualified':False,
        'authority_effect':'none','actual_owner_outcome':None,
        'claim_ceiling':'Frozen producer and exact distinct Source6 construction contract only; actual signed production, cold replay, Reader5 and public/learning qualification remain required.'}
    with (HERE/'source-manifest.json').open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(HERE/'source-manifest.json'),'files':len(rows),
                      'expected_original_targets':105,'expected_signed_transactions':5,'expected_type_registration_targets':32}),flush=True)


if __name__=='__main__':main()
