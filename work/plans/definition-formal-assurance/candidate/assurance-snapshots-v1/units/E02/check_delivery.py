"""Read-only byte/source integrity and historical controlled-package replay."""
import base64
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7]
BASE=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'
UNIT=Path(__file__).resolve().parent
sys.path[:0]=[str(IMPL),str(BASE/'units/E01')]
import bundles as b
import evidence_contract as e


def verify_file(row):
    if hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Stale bound file: '+row['path'])


def main():
    counts={}
    for path in [BASE/'units/P02/delivery-manifest.json',UNIT/'delivery-manifest.json']:
        rows=json.loads(path.read_text())['files']
        if len({row['path'] for row in rows})!=len(rows):raise ValueError('Duplicate manifest path')
        for row in rows:verify_file(row)
        counts[str(path.relative_to(ROOT))]=len(rows)
    for unit in ['E01','E02']:
        receipt=json.loads((BASE/f'units/{unit}/receipt.json').read_text())
        for row in receipt['inputs']+receipt['outputs']:verify_file(row)
        if receipt['authority_effect']!='none' or receipt['goal_status']!='active':raise ValueError('Incorrect receipt authority/completion boundary')
    example=json.loads((BASE/'units/E01/pending-evidence-example.json').read_text());captured={row['path']:base64.b64decode(row['content_base64'],validate=True) for row in example['captured_artifacts']};report=e.check(example['bundle'],example['expected_required_set'],captured=captured)
    if not e.r.same_json(report,example['actual_check']) or report['semantic_ready']:raise ValueError('E01 example check mismatch')
    cases=json.loads((UNIT/'worked-publications.json').read_text());replays=0;attempts=0
    for case in cases['records']:
        actual=case['actual']
        if actual['status']=='published-candidate':
            report=b.inspect(ROOT,actual['bundle_ref'],case['expected_required_set'],expected_contract=b.checked_contract())
            stored=next(row['actual'] for row in cases['relocated_capture_replays'] if row['case_id']==case['case_id'])
            if not b.r.same_json(report,stored) or report['source_currentness']!='historical-capture-only':raise ValueError('Historical package replay mismatch')
            replays+=1
        if actual.get('preserved_attempt_ref'):
            if not (ROOT/actual['preserved_attempt_ref']).is_dir():raise ValueError('Missing preserved attempt')
            attempts+=1
        if case.get('preserved_empty_target_ref'):
            path=ROOT/case['preserved_empty_target_ref']
            if not path.is_dir() or list(path.iterdir()):raise ValueError('Empty collision target changed')
    if replays!=2 or attempts!=3:raise ValueError('Controlled-publication denominator mismatch')
    snapshot=json.loads((BASE/'current-snapshot.json').read_text());source=b.r.verify(snapshot,ROOT)
    print(json.dumps({'result':'PASS','delivery_manifests':counts,'source_capture':source,'new_tests':46,'historical_controlled_packages':replays,'preserved_attempts':attempts,'authority_effect':'none','goal_status':'active','full_project_completion':'not-established'},indent=2,sort_keys=True))


if __name__=='__main__':main()
