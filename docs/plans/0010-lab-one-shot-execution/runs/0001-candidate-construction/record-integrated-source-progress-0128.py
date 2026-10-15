"""Retain successful full lifecycle, actual construction failures and schema repair."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v86'


def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def main():
    parent=API/'receipts/R03-0127.json';value=load(parent);rows={row['path']:row for row in value['files']}
    actual=RUN/'API85-machine-lifecycle-full-0001.json';terminal=RUN/'API85-machine-lifecycle-full-terminal-0001.json'
    a,t=load(actual),load(terminal)
    assert a['result']=='PASS' and a['actual_cases']==20 and a['failures']==a['errors']==0
    assert t['actual_exit_code']==0 and a['source_guarded_exit_completed']
    assert not a['clock_replaced'] and not a['source_callbacks_replaced'] and not a['time_bounds_extended']
    audit=RUN/'typed-schema-registry-audit-0128.json';repair=RUN/'typed-schema-successor-qualification-0128.json'
    assert len(load(audit)['rejected_declared_tuples'])==8 and load(repair)['result']=='PASS'
    assert load(repair)['actual_schema_cases']==550 and load(repair)['exact_pair_and_qualifier_contract_checks']==41
    paths=[parent,actual,terminal,audit,repair,Path(__file__).resolve(),RUN/'qualify-integrated-source-0007.py']
    for version in (6,7):
        folder=BASE/('current-participation-v'+str(version))
        paths.extend(path for path in folder.rglob('*') if path.is_file() and '__pycache__' not in path.parts)
        paths.extend([RUN/('run-current-participation-build-000'+str(version)+'.py'),
                      RUN/('current-participation-build-terminal-000'+str(version)+'.json'),
                      RUN/('current-participation-build-000'+str(version)+'.log')])
        assert load(RUN/('current-participation-build-terminal-000'+str(version)+'.json'))['actual_exit_code']==1
    for folder in ('current-source-adapter-v5','current-source-adapter-v6','challenge-resolution-v2','typed-relation-schema-v4'):
        paths.extend(path for path in (BASE/folder).rglob('*') if path.is_file() and '__pycache__' not in path.parts)
    for row in [*a['files'],*load(repair)['files'],*[bind(path) for path in paths]]:
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    value.update(files=[rows[key] for key in sorted(rows)],historical_progress_binding=bind(parent),
        historical_API85_full_lifecycle_binding=bind(actual),historical_API85_actual_terminal_binding=bind(terminal),
        historical_API85_Machine_lifecycle_qualified=True,historical_API85_actual_lifecycle_cases=20,
        same_predecessor_live_jobs=[],typed_registry_schema_audit_binding=bind(audit),
        rejected_declared_typed_schema_pairs=8,typed_schema_successor_source_binding=bind(BASE/'typed-relation-schema-v4/source-manifest.json'),
        typed_schema_successor_qualification_binding=bind(repair),typed_schema_successor_shape_cases=550,
        typed_schema_successor_native_registration_qualified=False,
        integrated_source_actual_failures=[{'version':version,'terminal_binding':bind(RUN/('current-participation-build-terminal-000'+str(version)+'.json')),
            'failure_binding':bind(BASE/('current-participation-v'+str(version))/'packages/0001/failure.json')} for version in (6,7)],
        integrated_source_qualified=False,current_Machine_qualified=False,whole_API_qualified=False,
        task_complete=False,goal_complete=False,actual_owner_outcome=None,
        remaining_obligations=[
            'Register exact candidate Typed Relation/v4 in a fresh owned source through the original descriptor slot, stage owned immutable representation successors and preserve original/foreign source bodies. Native current-carrier and historical compatibility require actual validation.',
            'Complete the distinct integrated source construction; preserve failed Source6/7 snapshots and fixed period. Current Policy/v2 and all550declared endpoint pairs must be represented without weakening the validator or introducing new semantic pairs.',
            'Freeze/qualify the integrated source adapter and public successor with the exact selected gate as an immutable object, preserving the acyclic workspace binding and source/gate/transport/journal checks.',
            *value['remaining_obligations'][2:]],
        change='Actual API85 original20Machine/termination selection completed PASS exit0, including real expiry and disposal. No transfer to currentAPI86. Actual integrated Source6 failed at historicalPolicy/v1; preserved successorSource7 uses currentPolicy/v2 and failed at an already declared authority-boundary/decision-scope tuple rejected by TypedRelation/v3. Complete550tuple schema audit found8representation gaps. Frozen candidateTypedRelation/v4 adds exactlythose8schema branches:550actualshape cases,41exact pair/qualifier checks and3negative cases passed. Native registration, integrated source, public resolution and learning context remain unqualified.',
        claim_ceiling='Historical exactAPI85 full20lifecycle plus complete550synthetic schema representation cases only; no integrated native source, currentAPI86Machine, positivepublicresolution, canonicaladmission or completeLab.')
    output=API/'receipts/R03-0128.json'
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','progress_binding':bind(output),'bound_files':len(rows),'historical_API85_cases':20,
                      'typed_shape_cases':550,'typed_schema_gaps_repaired_as_candidates':8,'whole_API_qualified':False}),flush=True)


if __name__=='__main__':main()
