"""Read-only sealed-unit integrity, independent replay and real-source checks."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7];UNIT=Path(__file__).resolve().parent
BASE=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(UNIT),str(IMPL)]
import run_cases
v=run_cases.v


def verify_file(row):
    if hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Stale bound file: '+row['path'])


def main():
    manifests={}
    for path in [BASE/'units/E02/delivery-manifest.json',UNIT/'delivery-manifest.json']:
        rows=json.loads(path.read_text())['files']
        if len({row['path'] for row in rows})!=len(rows):raise ValueError('Duplicate delivery identity')
        for row in rows:verify_file(row)
        manifests[str(path.relative_to(ROOT))]=len(rows)
    receipt=json.loads((UNIT/'receipt.json').read_text())
    for row in receipt['inputs']+receipt['outputs']:verify_file(row)
    if receipt['authority_effect']!='none' or receipt['goal_status']!='active' or receipt['unit_id']!='E03.1':raise ValueError('Receipt authority/goal mismatch')
    context=json.loads((UNIT/'context.json').read_text())
    for row in context['sources']:verify_file(row)
    cases=json.loads((UNIT/'worked-verifications.json').read_text())
    if cases['current_lab_definition_proofs']!=0 or len(cases['records'])!=3 or len(cases['replays'])!=3:raise ValueError('Worked case denominator mismatch')
    for row,expected in zip(cases['records'],cases['replays']):
        actual={'case_id':row['case_id'],**run_cases.replay(row)}
        if not v.r.same_json(actual,expected):raise ValueError('Independent replay mismatch')
    snapshot=json.loads((BASE/'current-snapshot.json').read_text());source=v.r.verify(snapshot,ROOT)
    print(json.dumps({'result':'PASS','authority_effect':'none','delivery_manifests':manifests,'source_capture':source,'tests':receipt['test_count'],'retained_cases':3,'independent_replays':3,'owner_accepted_whole_definition_translations':0,'whole_definition_proofs':0,'goal_status':'active','full_project_completion':'not-established'},indent=2,sort_keys=True))


if __name__=='__main__':main()
