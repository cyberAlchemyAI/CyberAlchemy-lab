"""Stage a separately owned signed source producer with exact Intent Resolution."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'current-participation-v8';NEW=BASE/'current-participation-v9'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    assert not NEW.exists()
    shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('packages','receipts','__pycache__','source-manifest.json','freeze.py'))
    p=NEW/'base.py';s=p.read_text().replace('_0008','_0009');p.write_text(s)
    p=NEW/'build.py';s=p.read_text().replace('R03-current-participation-0008','R03-current-participation-0009').replace('cal-R03-integrated-source-0008-','cal-R03-workflow-source-0009-')
    marker="            emit(out/'record-index.json',current[:len(fresh)]);emit(out/'integrated-record-index.json',all_rows)"
    block="""            # This is an isolated development interpretation, whose exact
            # local native approval is retained. It is not a human owner outcome
            # or a canonical interpretation/admission of the original Intent.
            version='intent-resolution:R03-workflow-source-0009@1.0.0-candidate.1'
            decision_ref='decision:Source9:isolated-workflow-interpretation'
            resolution=load(ROOT/'authority/artifact-types/intent-resolution/v1/fixtures/valid/record.json')
            resolution.update(node_id=version.split('@')[0],owner_ref=records.PRINCIPAL,
                scope_ref=data['config']['scope_ref'],name='Isolated workflow source-inspection interpretation',
                challenge_route='protocol:R03-owned-workflow-source-review',lifecycle_state='candidate',
                claim_ceiling='Isolated candidate interpretation and native approval only; no human owner outcome, completed Work or canonical admission.',
                evidence_refs=['protocol:R03-Source9-intent-resolution-approval'],relation_refs=[],successor_refs=[])
            resolution['payload'].update(intent_ref=records.INTENT,owner_decision_ref=decision_ref,
                selected_subject_refs=[records.WORK],satisfaction_test_refs=['check:actual-exact-source-inspection'],excluded_subject_refs=[])
            target={'category':'artifact-instance','operation':'admit','version_ref':version,
                'carrier_ref':'cal.artifact-type.intent-resolution/v1','record':resolution,
                'predecessor_ref':None,'decision_ref':decision_ref,'contract':None}
            original_resolution=authored_bytes(resolution)
            emit(out/'workflow-intent-resolution.json',None,raw=original_resolution)
            data=commit('workflow-intent-resolution',[target],{version:original_resolution})
            current.append({**all_rows[-1],'original_binding':binding(out/'workflow-intent-resolution.json'),'encoding':handle.custody.ENCODING})
            emit(out/'record-index.json',current[:len(fresh)]);emit(out/'integrated-record-index.json',all_rows)
"""
    assert s.count(marker)==1;s=s.replace(marker,block.rstrip())
    s=s.replace("'expected_original_targets':105","'expected_original_targets':106")
    p.write_text(s)
    context=RUN/'context-R03-workflow-source-0134.json'
    value={'schema_version':'lab-bounded-context/v1-candidate','task':'R03 workflow.transition current-source prerequisite',
        'source_bindings':[bind(p) for p in [RUN/'authorization.json',OLD/'source-manifest.json',OLD/'packages/0001/manifest.json',BASE/'workflow-transition-v1/kernel.py',ROOT/'authority/artifact-types/intent-resolution/v1/schema.json',Path(__file__).resolve()]],
        'finding':'Actual Source8 has current Intent, Work, Coordination Context and Workflow Decision Profile, but no current Intent Resolution. The transition kernel requires an exact eligible resolution; a schema-valid synthetic header cannot fill it.',
        'construction':'New owned source imports the predecessor-selected original bytes and appends one exact isolated Intent Resolution under actual test-owned native approval. No parent bytes or periods are renewed.',
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
    with context.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    parent=json.loads((OLD/'source-manifest.json').read_bytes());rows={r['path']:r for r in parent['files']}
    for p in [OLD/'source-manifest.json',OLD/'packages/0001/manifest.json',context,Path(__file__).resolve(),ROOT/'authority/artifact-types/intent-resolution/v1/fixtures/valid/record.json']:
        rows[str(p.relative_to(ROOT))]=bind(p)
    for p in sorted(NEW.glob('*')):
        if p.is_file():
            if p.suffix=='.py':ast.parse(p.read_text())
            rows[str(p.relative_to(ROOT))]=bind(p)
    value={**parent,'schema_version':'lab-current-participation-source/v9-candidate','files':[rows[k] for k in sorted(rows)],
        'parent_source_binding':bind(OLD/'source-manifest.json'),'parent_package_binding':bind(OLD/'packages/0001/manifest.json'),
        'workflow_context_binding':bind(context),'expected_original_targets':106,'expected_signed_transactions':6,
        'public_workflow_transition_qualified':False,'new_Agent_period_selected':False,
        'claim_ceiling':'Frozen owned source producer for one isolated Intent Resolution; original signed production/replay/public workflow qualification required. No human owner decision, canonical admission or original period extension.'}
    with (NEW/'source-manifest.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(NEW/'source-manifest.json')}),flush=True)
if __name__=='__main__':main()
