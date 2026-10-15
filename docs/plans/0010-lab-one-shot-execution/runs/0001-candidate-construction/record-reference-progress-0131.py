"""Record scoped actual resolution evidence; retain all remaining plan obligations."""
import base64
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v91'
def load(path):return json.loads(path.read_bytes())
def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    parent=BASE/'api-v87/receipts/R03-0130.json';value=load(parent);rows={r['path']:r for r in value['files']}
    public=RUN/'API91-integrated-resolution-0002.json';p=load(public)
    selection=RUN/'reference-goal-selection-qualification-0131.json';s=load(selection)
    controls=RUN/'API91-integrated-controls-0001.json';control=load(controls)
    primitives=RUN/'resolution-primitives-qualification-0131.json';primitive=load(primitives)
    assert control['result']=='PASS' and control['actual_cases']==4 and len(control['checks'])==7
    assert primitive['result']=='PASS' and primitive['actual_original_methods']==15 and primitive['failures']==primitive['errors']==0
    assert p['result']=='PASS' and len(p['checks'])==6 and p['actual_cases']==1 and p['fixture_removed'] and p['source_guarded_exit_completed']
    assert s['result']=='PASS' and s['actual_checks']==37 and s['source_guarded_exit_completed']
    reports=[];role_checks=[]
    for item in p['validation_evidence_originals']:
        raw=base64.b64decode(item['base64_original_bytes'],validate=True)
        assert hashlib.sha256(raw).hexdigest()==item['binding']['sha256'];record=json.loads(raw)
        if record.get('schema_version')=='lab-validation-report/v1-candidate':reports.append(record)
        if record.get('details',{}).get('schema_version')=='lab-exact-resolution-reference-check/v1-candidate':role_checks.append(record['details'])
    assert len(reports)==3 and all(r['result']=='pass' and not r['gaps'] for r in reports)
    assert len(role_checks)==4 and any(r['posture']=='historical' for report in reports for r in report['reference_checks'])
    assert any(r['posture']=='excluded' and r['requested_ref']=='protocol:R03-fresh-context-delivery' for report in reports for r in report['reference_checks'])
    assert all(not r['actual_output_asserted'] and not r['work_satisfaction_asserted'] and not r['current_authority_asserted'] for r in role_checks)
    local=[parent,public,selection,Path(__file__).resolve(),RUN/'qualify-API90-integrated-resolution-0001.py',RUN/'API91-integrated-resolution-0001.json',RUN/'qualify-API91-integrated-resolution-0001.py',RUN/'qualify-API91-integrated-resolution-0002.py',controls,primitives,RUN/'qualify-API91-integrated-controls-0001.py',RUN/'qualify-resolution-primitives-0131.py',RUN/'REFERENCE-CLOSURE-REVIEW-0131.md',RUN/'public-resolution-helper-observation-0131.json',
        RUN/'qualify-reference-selection-0131.py',RUN/'qualify-reference-goal-selection-0131.py',RUN/'reference-successor-static-review-0131.json',RUN/'reference-goal-scope-diagnosis-0131.json',RUN/'typed-relation-v4-public-header-gap-0131.json',RUN/'API90-integrated-resolution-0001.json',RUN/'reference-selection-qualification-0131.json',
        RUN/'freeze-reference-successors-0131.py',RUN/'freeze-reference-provenance-successor-0131.py',
        RUN/'freeze-reference-project-scope-successor-0131.py',RUN/'freeze-reference-goal-scope-successor-0131.py',API/'source-manifest.json',API/'contract-profile.json']
    source=load(API/'source-manifest.json')
    for row in [*source['files'],*p['files'],*s['files'],*control['files'],*primitive['files'],*[bind(path) for path in local]]:
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    remaining=[
        'Qualify current API91 negative public cases for changed source/policy, schema/signature/core failures, deadlines and alternate actual callbacks; scoped positive episode plus37selection checks does not transfer inherited qualification.',
        'Declare exact versioned public protocol carrier closure for candidate TypedRelation/v4; the preserved shared common/v1 artifact_ref currently excludes it. Then qualify query/inspection against selected source; no wildcard carrier admission.',
        'Qualify inherited323API methods and Reader7 original adapter behavior against their independently selected current fixtures. Retain all original assertions, failure receipts and explicit fixture scope.',
        'Close mapped ontology and exact operational lesson applicability, produce a new actual Agent Context, then perform a later controlled lesson application with outcomes/counterevidence. Prior repair is not causal application evidence.',
        'Implement all10original missing operations: checkpoint.resolve,admission.apply,action.evaluate,action.dispatch,action.reconcile,workflow.transition,ontology.project,installation.execute,capability.adoption.prepare,release.prepare.',
        'Complete R03,R05,R06,R07,S02 original construction and acceptance criteria before sole actual R08 owner response; retain separately authorized A01-A04 operational effects.']
    value.update(files=[rows[k] for k in sorted(rows)],historical_progress_binding=bind(parent),
        source_binding=bind(API/'source-manifest.json'),profile_binding=bind(API/'contract-profile.json'),
        integrated_public_resolution_qualified=True,integrated_public_resolution_qualification_binding=bind(public),
        exact_reference_selection_qualification_binding=bind(selection),actual_reference_selection_checks=37,actual_public_control_cases=4,actual_resolution_primitive_methods=15,
        public_control_qualification_binding=bind(controls),resolution_primitive_qualification_binding=bind(primitives),
        actual_resolution_validation_reports=3,actual_resolution_typed_role_checks=4,
        actual_resolution_evidence_originals=len(p['validation_evidence_originals']),same_live_jobs=[],
        original_API_test_methods_retained=323,unchanged_method_ASTs=323,explicit_fixture_input_corrections=[],
        current_Machine_qualified=False,whole_API_qualified=False,task_complete=False,goal_complete=False,
        remaining_obligations=remaining,
        change='API91 actual controlled public challenge resolution returned exact signed semantic/governance candidate effects. Three native semantic reports passed, with explicit expected protocol declaration and historical exact challenged revision. Exact journal retry, pure-scope dispatch/write refusals, original source preservation and owned cleanup passed.37independent reference selection/contract checks,4actualpublicrefusalcases and15originalprimitive methods passed. All323inherited methods unchanged; no full API, new AgentContext, canonical admission or completedLab.',
        claim_ceiling='One actual controlled current-source public resolution episode with retained original validation evidence and37contract/control checks only; full inherited/negative/API/learning/AgentContext and completeLab remain unqualified.')
    output=API/'receipts/R03-0131.json';output.parent.mkdir(mode=0o700,exist_ok=True)
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','progress_binding':bind(output),'bound_files':len(rows),'validation_reports':3,
        'typed_role_checks':4,'actual_positive_public_cases':1,'whole_API_qualified':False}))

if __name__=='__main__':main()
