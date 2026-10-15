"""Record actual signed Source8 and Reader7 without closing their pending suites."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v86';SOURCE=BASE/'current-participation-v8'


def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def main():
    parent=API/'receipts/R03-0128.json';value=load(parent);rows={row['path']:row for row in value['files']}
    terminal=RUN/'current-participation-build-terminal-0008.json';result=SOURCE/'packages/0001/build-result.json'
    t,r=load(terminal),load(result)
    assert t['actual_exit_code']==0 and r['result']=='PASS' and r['signed_transactions']==5 and r['actual_original_targets']==105
    assert r['owned_store_and_key_removed'] and not Path(r['owned_root']).exists()
    assert r['owned_representation_successors']==31 and r['type_registration_targets']==32 and r['preserved_foreign_sources']==10
    reader=RUN/'integrated-reader-qualification-0007.json';a=load(reader)
    assert a['result']=='PASS' and a['actual_cases']==1 and a['source_guarded_exit_completed']
    assert a['observed']['included_current_records']==283 and a['observed']['accounted_subjects']==870
    paths=[parent,terminal,result,reader,Path(__file__).resolve(),RUN/'run-current-participation-build-0008.py',
        RUN/'current-participation-build-0008.log',RUN/'qualify-integrated-source-0008.py',
        RUN/'integrated-source-selection-0008.json',RUN/'qualify-R03-integrated-reader-0007.py',
        RUN/'native-registration-observation-0129-0001.json',RUN/'freeze-R03-current-source-adapter-0007.py']
    for folder in ('current-participation-v8','current-source-adapter-v7','typed-relation-registration-v2'):
        paths.extend(path for path in (BASE/folder).rglob('*') if path.is_file() and '__pycache__' not in path.parts)
    for row in [*a['files'],*[bind(path) for path in paths]]:
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    value.update(files=[rows[key] for key in sorted(rows)],historical_progress_binding=bind(parent),
        integrated_source_build_terminal_binding=bind(terminal),integrated_source_build_result_binding=bind(result),
        integrated_source_source_binding=bind(SOURCE/'source-manifest.json'),
        integrated_source_package_binding=bind(SOURCE/'packages/0001/manifest.json'),
        integrated_source_signed_transactions=5,integrated_source_original_targets=105,
        typed_schema_successor_native_signed_registration=True,owned_typed_representation_successors=31,preserved_foreign_sources=10,
        integrated_reader_source_binding=bind(BASE/'current-source-adapter-v7/source-manifest.json'),
        integrated_reader_construction_binding=bind(reader),integrated_reader_actual_catalog_cases=1,
        integrated_reader_included_current_records=283,integrated_reader_accounted_subjects=870,
        integrated_source_qualified=False,integrated_reader_original_cases_requalified=False,
        same_live_jobs=[{'tool_session_id':57233,'pid':377850,'purpose':'Source8 actual23case cold/native/gate qualification',
            'selection_binding':bind(RUN/'integrated-source-selection-0008.json')}],
        current_Machine_qualified=False,whole_API_qualified=False,task_complete=False,goal_complete=False,
        remaining_obligations=[
            'Observe the same Source8 actual23case cold/native/gate suite57233 through actual terminal; all105original body retrieval, actual tamper/refusal, compatibility, independent gate/response and cleanup cases remain required.',
            'Qualify inherited Reader behavior and scope/invalidation cases against exact Reader7/Source8; one catalog construction case does not close the adapter.',
            'Integrate the exact new source and gate-object method into a frozen public successor with original transport/authentication, native candidate validation, journal/retry/deadline and source/policy exit checks. Preserve Source5 Machine paths and qualify changed public behavior independently.',
            *value['remaining_obligations'][3:]],
        change='Source8 actual producer PASS exit0:5signed development transactions,105original targets,32native type-registration/compatibility cores,31owned representation successors,10foreign source records preserved and owned signer/store removed. OriginalSource5 and all7learning originals remain in history. Exact prospective semantic/governance cores and an independent newly generated gate signature were constructed without circular workspace identity or exported keys. Reader7 actual catalog construction PASS:1case,283current records,870subjects accounted. Full23cold/native/gate suite57233continues; public resolution and learning context remain unqualified.',
        claim_ceiling='Actual Source8 signed construction and one Reader7 catalog case only; fullcold/native/gate, inherited adapter, public transport/journal, mapped context and learning application/outcome remain required. No canonical admission or completeLab.')
    output=API/'receipts/R03-0129.json'
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','progress_binding':bind(output),'bound_files':len(rows),
                      'signed_transactions':5,'original_targets':105,'reader_current_records':283,'same_live_job':57233}),flush=True)


if __name__=='__main__':main()
