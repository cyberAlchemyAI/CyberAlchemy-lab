"""Actual Session/report learning custody; preserve the authored fixture Lesson.

The private host selects normalized real API archives and exact first/later
receipts. Session identity is read from the actual formal body, never a hash.
"""
import copy
from datetime import datetime
import importlib
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator
import retained as R
ROOT=Path(__file__).resolve().parents[4]
def enc(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def original(binding,*,path_key=False):
    keys={'path','sha256'}if path_key else {'ref','sha256'};R.need(type(binding)is dict and set(binding)==keys,'closed actual learning original binding required')
    raw=R.read(Path(binding['path'if path_key else'ref']));R.need(R.sha(raw)==binding['sha256'],'actual learning original differs');return raw

def produce(*,records,observations,controls):
    R.need(type(controls)is dict and set(controls)=={'first_binding','later_binding','files'},'closed first/later actual learning selection required')
    files=controls['files'];R.need(type(files)is dict and set(files)=={'lesson','report','counterevidence','application','assessment','events'},'exact original learning evidence file closure required')
    first_raw=original(controls['first_binding']);later_raw=original(controls['later_binding']);first,later=(json.loads(raw)for raw in(first_raw,later_raw))
    R.need(first['result']=='PASS-local-current-one-Lesson-selection-and-close'and later['result']=='PASS-local-current-Lesson-later-application-independent-assessment'
           and all(first[k]is True for k in('selection_registry_erased','explicitly_closed','memory_erased','closed_refused'))
           and first['fixture_only']is True and later['fixture_only']is True and first['authority_effect']==later['authority_effect']=='none',
           'actual first/later terminal Session evidence did not pass')
    R.need(later['first_session_receipt']=={'path':controls['first_binding']['ref'],'sha256':R.sha(first_raw)},'later use selects another first Session receipt')
    selected=sys.modules.get('cal_installed_runtime_selection_v1');R.need(selected is not None and selected.root()==ROOT,'actual selected-root learning consumer required');selected.guard()
    for receipt in(first,later):
        R.need(receipt['api_source_binding']==selected.binding('api.source')and receipt['profile_binding']==selected.binding('api.profile')
               and receipt['family_source_binding']==selected.binding('family.source'),'actual Session selected software/family differs')
    formal=[]
    for receipt in(first,later):
        raw=original(receipt['formal_session_binding'],path_key=True);value=json.loads(raw);sid=value['session_ref'];body=value['formal_session_body'];memory=body['payload']['session_memory']
        R.need(type(sid)is str and sid and body['node_id']==sid and R.sha(sid.encode())==receipt['session_ref_sha256']
               and value['source_cut']==receipt['source_cut']and value['api_source_binding']==receipt['api_source_binding']
               and value['family_source_binding']==receipt['family_source_binding']and value['short_memory_exported']is False
               and set(memory)=={'selected_input_refs','working_record_refs','unresolved_questions','expires_with_session'}
               and memory['working_record_refs']==[]and memory['unresolved_questions']==[]and memory['expires_with_session']is True,
               'actual formal Session identity/refs-only memory differs')
        Draft202012Validator(json.loads((ROOT/'authority/artifact-types/agent-session/v1/schema.json').read_bytes())).validate(body);formal.append(value)
    R.need(formal[0]['session_ref']!=formal[1]['session_ref']and first['source_cut']==later['source_cut'],'later use must be a genuinely distinct actual Session on this Source')
    raw_files={name:original(binding)for name,binding in files.items()};lesson,report,counter,application,assessment=(json.loads(raw_files[k])for k in('lesson','report','counterevidence','application','assessment'))
    work=later['actual_later_work'];cut=later['source_cut']
    R.need(work['parent_session_closed']is True and work['independent_assessment_after_parent_close']is True and work['fixture_only']is True
           and work['actual_owner_outcome']is None and work['authority_effect']=='none'
           and R.sha(raw_files['report'])==work['inspection_output_sha256']and R.sha(raw_files['counterevidence'])==work['counterevidence_sha256']
           and R.sha(raw_files['assessment'])==work['assessment_candidate_sha256'],'actual independent post-close learning work/original hashes differ')
    R.need(report['schema_version']=='lab-T03-live-Lesson-inspection-output/v1-candidate'and report['source_cut']==counter['source_cut']==cut
           and counter['result']=='observed-selection-does-not-establish-state-correctness'
           and report['fixture_only']is True and report['authority_effect']==counter['authority_effect']=='none'
           and len(report['observed_discrepancies'])==work['actual_discrepancy_count'],'actual report/counterevidence selection differs')
    lesson_h=report['lesson'];R.need(set(lesson_h)==R.FIELDS and lesson_h['byte_sha256']==R.sha(raw_files['lesson'])and lesson_h['identity_ref']==lesson['node_id']
           and lesson['payload']['status']=='fixture-reviewed-for-runtime-test'and R.sha(lesson_h['version_ref'].encode())==first['lesson_version_ref_sha256']==later['lesson_version_ref_sha256'],
           'actual authored source Lesson identity/provenance differs')
    api=ROOT/selected.current().package['entrypoint']['api_directory'];portable=importlib.import_module(api.name+'.runtime_selection');P=importlib.import_module(api.name+'.protocol')
    index=json.loads(P.source.original(portable.binding('family.record_index')));lesson_rows=[row for row in index if row['version_ref']==lesson_h['version_ref']]
    R.need(len(lesson_rows)==1 and lesson_rows[0]['original_binding']['sha256']==R.sha(raw_files['lesson'])
           and P.source.original(lesson_rows[0]['original_binding'])==raw_files['lesson'],'authored Lesson is not the exact current selected signed family original')
    work_rows=[row for row in index if row['kind']=='work'];R.need(len(work_rows)==1,'one exact current Work required');wr=work_rows[0];work_raw=P.source.original(wr['original_binding']);work_body=json.loads(work_raw)
    scope=work_body['scope_ref'];work_ref=wr['version_ref']
    selected_observations={};actual_headers={}
    for operation,body,name in [('lesson.apply',application,'application'),('lesson.assess',assessment,'assessment')]:
        matching=[o for o in observations if o['actual_reply']['operation']==operation and o['actual_reply']['kind']=='result'
                  and o['original_source_cut']==cut and R.sha(enc(o['actual_reply']['message']))==work['application_reply_sha256'if name=='application'else'assessment_reply_sha256']]
        R.need(len(matching)==1,'one exact actual learning API producer required: '+operation);observed=matching[0]
        returned=[(h,raw)for h,raw in observed['outputs']if raw==raw_files[name]and h['identity_ref']==body['node_id']]
        R.need(len(returned)==1 and returned[0][0]['version_ref']in records and records[returned[0][0]['version_ref']]==returned[0],
               'actual returned application/assessment candidate original differs')
        selected_observations[operation]=observed;actual_headers[name]=returned[0][0]
    R.need(application['payload']['session_ref']==formal[1]['session_ref']and application['payload']['lesson_revision_ref']==lesson_h['version_ref']
           and assessment['payload']['lesson_application_ref']==actual_headers['application']['version_ref']and assessment['payload']['disposition']=='recorded-outcome-only'
           and assessment['owner_ref']=='principal:T03-independent-assessor'and assessment['payload']['causal_claim_ceiling']=='Exact recorded application outcome only; no general or causal effectiveness inferred.'
           and lesson_h['scope_ref']==application['scope_ref']==assessment['scope_ref']==report['project_ref']==scope,
           'actual Session/Lesson/application/independent assessment semantic chain differs')
    events=[json.loads(line)for line in raw_files['events'].splitlines()if line];inspected=[e for e in events if e.get('phase')=='lesson-influenced-inspection'and e.get('state')=='passed']
    closed=[e for e in events if e.get('phase')=='parent.close-before-assessment'and e.get('state')=='passed'];assessed=[e for e in events if e.get('phase')=='lesson.assess'and e.get('state')=='passed']
    R.need(len(inspected)==len(closed)==len(assessed)==1 and datetime.fromisoformat(inspected[0]['at_utc'])<=datetime.fromisoformat(closed[0]['at_utc'])<datetime.fromisoformat(assessed[0]['at_utc']),
           'actual inspection/parent-close/independent assessment event order differs')
    seed=R.sha(enc({'later':controls['later_binding'],'report':files['report'],'assessment':actual_headers['assessment']}));ids={k:k+':actual-local-learning:'+seed for k in('operational-observation','work-outcome-assessment','improvement-signal')};refs={k:v+'@candidate.1'for k,v in ids.items()};outputs=[]
    for kind in ids:
        folder=ROOT/'authority/artifact-types'/kind/'v1';body=json.loads((folder/'fixtures/valid/record.json').read_bytes());body.update(node_id=ids[kind],owner_ref=assessment['owner_ref'],scope_ref=scope,lifecycle_state='candidate',successor_refs=[],evidence_refs=[controls['later_binding']['ref'],files['report']['ref'],files['counterevidence']['ref']],
            claim_ceiling='Actual bounded fixture Session/report/application/independent-assessment custody only. No novel human-reviewed Lesson, broad effectiveness, Source admission or original Work completion.')
        if kind=='operational-observation':
            body['payload'].update(project_ref=scope,action_ref=actual_headers['application']['version_ref'],method_ref=report['producer_binding']['path'],observed_at=inspected[0]['at_utc'],datum='Actual later Session consumed a source-pinned report with '+str(work['actual_discrepancy_count'])+' selection discrepancies.',evidence_refs=[files['report']['ref'],files['counterevidence']['ref']],interpretation_posture='recorded-bounded-source-selection-only')
            body['relation_refs']=[{'relation_kind_ref':'relation.evidence-bears-on','direction':'source','counterpart_kind':'work-outcome-assessment','counterpart_ref':refs['work-outcome-assessment']}]
        elif kind=='work-outcome-assessment':
            body['payload'].update(subject_ref=work_ref,expected_result_ref='protocol:bounded-source-pinned-report-and-fresh-Session-consumption',observed_result_ref=files['report']['ref'],disposition='bounded-observation-recorded-only',evidence_refs=[files['report']['ref'],files['counterevidence']['ref']],gap_refs=['gap:original-Work-completion-not-assessed','gap:source-selection-is-not-state-correctness'])
            body['relation_refs']=[{'relation_kind_ref':'relation.evaluates','direction':'source','counterpart_kind':'work','counterpart_ref':work_ref}]
        else:
            body['payload'].update(source_refs=[actual_headers['assessment']['version_ref'],refs['operational-observation']],signal_statement='Review the exact observed source-selection discrepancies; '+str(work['actual_discrepancy_count'])+' were recorded. This does not establish broad Lesson effectiveness.',observed_window=inspected[0]['at_utc']+'/'+assessed[0]['at_utc'],improvement_target_ref='none',routing_owner_ref=assessment['owner_ref'],evidence_posture='bounded-candidate-observation-only',deduplication_key='actual-source-selection:'+report['selection_sha256'])
            body['relation_refs']=[{'relation_kind_ref':'relation.derives-from','direction':'source','counterpart_kind':'operational-observation','counterpart_ref':refs['operational-observation']}]
        Draft202012Validator(json.loads((folder/'schema.json').read_bytes())).validate(body);raw=enc(body);outputs.append(({'scope_ref':scope,'identity_ref':ids[kind],'version_ref':refs[kind],'carrier_ref':'cal.artifact-type.'+kind+'/v1','byte_sha256':R.sha(raw)},raw))
    outputs.append((copy.deepcopy(lesson_h),raw_files['lesson']));selected.guard()
    return {'records':outputs,'consumed_input_refs':[actual_headers[k]['version_ref']for k in('application','assessment')],
            'consumed_observation_refs':[selected_observations[op]['observation_binding']['ref']for op in('lesson.apply','lesson.assess')],
            'receipt':{'schema_version':'lab-actual-local-learning-workflow-production/v1','first_binding':controls['first_binding'],'later_binding':controls['later_binding'],'original_file_bindings':files,
                       'actual_later_session_ref':formal[1]['session_ref'],'formal_session_binding':later['formal_session_binding'],'authored_fixture_Lesson_preserved':lesson_h,
                       'actual_application':actual_headers['application'],'actual_independent_assessment':actual_headers['assessment'],'new_human_reviewed_Lesson_created':False,
                       'general_or_causal_effectiveness_inferred':False,'actual_owner_outcome':None,'authority_effect':'none'}}
