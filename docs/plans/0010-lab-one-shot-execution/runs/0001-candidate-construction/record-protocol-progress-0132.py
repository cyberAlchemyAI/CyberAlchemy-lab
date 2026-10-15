"""Record versioned protocol and full adapter evidence; retain live public cases."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v93'
def load(path):return json.loads(path.read_bytes())
def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    parent=BASE/'api-v91/receipts/R03-0131.json';value=load(parent);rows={r['path']:r for r in value['files']}
    resource=RUN/'source8-protocol2-resource-qualification-0132.json';r=load(resource)
    adapter=RUN/'reader7-original-suite-qualification-0132.json';a=load(adapter)
    assert r['result']=='PASS' and r['actual_checks']==113 and r['source_guarded_exit_completed']
    assert a['result']=='PASS' and a['actual_original_methods']==20 and a['errors']==a['failures']==0 and a['source_guarded_exit_completed']
    local=[parent,resource,adapter,RUN/'source8-resource-qualification-0132.json',
        RUN/'qualify-source8-resources-0132.py',RUN/'qualify-source8-protocol2-resources-0132.py',
        RUN/'qualify-reader7-original-suite-0132.py',RUN/'reader7-original-checks-rebased-0132.py',
        RUN/'qualify-API92-current-inspection-0001.py',RUN/'qualify-API93-current-inspection-0001.py',
        RUN/'signed-catalog-projection-static-gap-0132.json',RUN/'build-source8-protocol-0132.py',
        RUN/'freeze-source8-protocol-0132.py',RUN/'freeze-signed-catalog-projection-0132.py',
        API/'source-manifest.json',API/'contract-profile.json',Path(__file__).resolve()]
    source=load(API/'source-manifest.json')
    for row in [*source['files'],*r['files'],*a['files'],*[bind(p) for p in local]]:
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    remaining=[
        'Wait on exact live public processes:API92current inspection session17207/PID387586 and API93current inspection session37104/PID388070. Both are confirmed active. Preserve original reports and inspect final guarded results; observation silence is not completion and never justifies restarting.',
        'Qualify actual current canonical/SQLite query parity and source/policy/schema/callback/signature/core negatives;97versioned resources/113checks and adapter20methods do not qualify the public API.',
        'Requalify actual public challenge resolution against the new negotiated profile and all323inherited API methods. API91 scoped runtime qualification is not transferred to API93.',
        'Close lesson applicability and ontology mapping, produce a new actual Agent Context, then perform a later controlled lesson application with outcomes/counterevidence; prior repair is not causal application evidence.',
        'Implement all10original missing operations:checkpoint.resolve,admission.apply,action.evaluate,action.dispatch,action.reconcile,workflow.transition,ontology.project,installation.execute,capability.adoption.prepare,release.prepare.',
        'Complete original R03/R05/R06/R07/S02 acceptance before sole actual R08 owner response; preserve separately authorized A01-A04 effects.']
    value.update(files=[rows[k] for k in sorted(rows)],historical_progress_binding=bind(parent),
        source_binding=bind(API/'source-manifest.json'),profile_binding=bind(API/'contract-profile.json'),
        negotiated_protocol_profile_version=4,versioned_protocol_resource_count=97,actual_protocol_resource_checks=113,
        protocol_resource_qualification_binding=bind(resource),reader_original_suite_qualification_binding=bind(adapter),
        actual_reader_original_methods=20,reader_unchanged_method_ASTs=18,reader_explicit_fixture_scope_corrections=a['explicit_fixture_scope_corrections'],
        original_API_test_methods_retained=323,unchanged_method_ASTs=323,
        integrated_public_resolution_qualified=False,current_protocol_query_inspection_qualified=False,whole_API_qualified=False,
        same_live_jobs=[{'session_id':17207,'pid':387586,'scope':'API92 current instance/catalog/canonical/SQL inspection'},
                        {'session_id':37104,'pid':388070,'scope':'API93 signed-locator corrected current inspection'}],
        remaining_obligations=remaining,task_complete=False,goal_complete=False,
        change='API93frozen protocol profilev4 selects97independently versioned resources with exactly one new carrier TypedRelation/v4, closed native body schema and signed catalog declaration. Original resource IDs retain their meaning;113resource checks PASS. Original20Reader7behavior methods PASS with18unchangedASTs and2explicit current fixture scope changes retaining23noncanonical source assertions. Current public query/SQL cases remain active; no positive qualification or whole API transfer.',
        claim_ceiling='Versioned protocol/resource schema isolation and full20original adapter behavior only. Actual current public query/SQL and new-profile resolution/inherited API remain unqualified; completeLab and final owner outcome remain absent.')
    output=API/'receipts/R03-0132.json';output.parent.mkdir(mode=0o700,exist_ok=True)
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','progress_binding':bind(output),'bound_files':len(rows),'resource_checks':113,
        'adapter_methods':20,'public_query_qualified':False,'whole_API_qualified':False}))
if __name__=='__main__':main()
