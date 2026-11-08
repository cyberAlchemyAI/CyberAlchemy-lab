"""Read-only stage integrity, source/currentness and complete-witness checks."""
import json
import hashlib
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'
BASE=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
UNIT=Path(__file__).resolve().parent
sys.path[:0]=[str(IMPL/'providers'),str(IMPL)]
import finite as f


def verify_file(row):
    path=Path(row['path']);path=path if path.is_absolute() else ROOT/path
    if f.file_digest(path)!=row['sha256']:raise ValueError('Stale bound file: '+row['path'])


def main():
    counts={}
    for path in [BASE/'units/P01/delivery-manifest.json',UNIT/'delivery-manifest.json']:
        manifest=json.loads(path.read_text());rows=manifest['files']
        if len({row['path'] for row in rows})!=len(rows):raise ValueError('Duplicate manifest path')
        for row in rows:verify_file(row)
        counts[str(path.relative_to(ROOT))]=len(rows)
    receipt=json.loads((UNIT/'receipt.json').read_text())
    for row in receipt['inputs']+receipt['outputs']:verify_file(row)
    if receipt['test_count']!=33 or receipt['goal_status']!='active' or receipt['authority_effect']!='none':raise ValueError('Incorrect unit receipt boundary')
    cases=json.loads((UNIT/'worked-theories.json').read_text())['records'];replays=0
    for case in cases:
        result=case['actual']
        if result['semantic_ready'] is not False or result['unbounded_conclusion'] is not None:raise ValueError('Overstated native result')
        for row in result['implementation_bindings']:verify_file(row)
        if result['witness'] is not None:
            actual=f.replay(case['subject'],result,case['theory'],case['populations'],case['query'],case['cardinalities'],expected_mode=case['mode'])
            if not f.r.same_json(actual,case['witness_replay']):raise ValueError('Witness replay mismatch')
            replays+=1
        if result['status'] in {'resource-limit','timeout','cancelled','provider-error','unsupported','malformed','unresolved-input-or-binding'} and (result['evidence_strength']!='none' or result['exhaustion_complete']):raise ValueError('Execution state promoted to logical evidence')
    if len(cases)!=7 or replays!=3 or cases[-1]['tracemalloc_peak_bytes']>=8_000_000:raise ValueError('Incorrect worked-control denominator')
    snapshot=json.loads((BASE/'current-snapshot.json').read_text());capture=f.r.verify(snapshot,ROOT)
    runtime=f.current_bindings()
    print(json.dumps({'result':'PASS','delivery_manifests':counts,'source_capture':capture,'tests':33,'worked_cases':7,'witness_replays':replays,'runtime_and_implementation_bindings':len(runtime),'goal_status':'active','full_project_completion':'not-established','authority_effect':'none'},indent=2,sort_keys=True))


if __name__=='__main__':main()
