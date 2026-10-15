"""Record the human's batch-review instruction, without accepting any meaning.

Archives exact pre-change workflow bytes. Proof reports and earlier assessments
remain immutable. Idempotent reruns retain the original archive.
"""
from pathlib import Path
import hashlib
import importlib.util
import json

HERE=Path(__file__).resolve().parent
N01=HERE.parent
SUCCESSOR=N01.parents[1]
ROOT=SUCCESSOR.parents[5]
ANSWER='do all definitions and we change or approve at the end'

def read(path):return json.loads(path.read_text())
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n')
def binding(path):return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def run():
    if (HERE/'review-manifest.json').exists():
        assert read(HERE/'review-manifest.json')['actual_batch_response'] is None, 'Preserve actual assessment; create a new workflow revision.'
    existing_seq=read(N01/'sequential-review.json')
    assert not any(u.get('batch_actual_assessment') for u in existing_seq['units']), 'Preserve actual batch assessments.'
    before=HERE/'history/pre-batch-workflow.json'
    if not before.exists():
        files=[N01/'sequential-review.json',N01/'decision-gate.json',N01/'formal-preparation-index.json',N01/'check_current_review.py',N01/'review-state-validation.json',SUCCESSOR/'execution/plan.json']
        snapshots=[]
        for source in files:
            saved=HERE/'history'/source.name
            saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(source.read_bytes())
            snapshots.append({'original_path':str(source.relative_to(ROOT)),'original_sha256':binding(source)['sha256'],'snapshot':binding(saved)})
        write(before,{'schema':'relational.pre-batch-workflow-snapshot/v1','status':'historical-only','snapshots':snapshots,'authority_effect':'none'})
    procedural={'source':'direct-human-user-message','answer':ANSWER,'interpretation':'Prepare the complete definition set before requesting consolidated changes or approval. This is procedural authorization, not semantic acceptance, proof validity or inherited discharge.','supersedes_prior_sequential_procedure':True,'scope':'all 41 candidate definitions and their shared proposed choices'}
    write(HERE/'procedural-response.json',procedural)
    manifest={'schema':'relational.consolidated-definition-review-manifest/v1','revision':read(HERE/'index.json')['revision'],
      'status':'ready-for-human-review','definition_index':binding(HERE/'index.json'),'review_packet':binding(HERE/'REVIEW.md'),
      'foundations':binding(HERE/'FOUNDATIONS.md'),'schema':binding(HERE/'definition.schema.json'),'audit_driver':binding(HERE/'verify_batch.py'),
      'response_template':binding(HERE/'review-response-template.json'),'actual_batch_response':None,'new_assessments':0,'inherited_discharges':0,'authority_effect':'none'}
    write(HERE/'review-manifest.json',manifest)
    helper=HERE/'audit_registered_K04.py'
    previous=N01/'registration/K04-2026-10-11/audit_registered.py'
    text=previous.read_text().replace("assert current['status']=='awaiting-actual-meaning-assessment'", "assert current['status'] in {'awaiting-actual-meaning-assessment','ready-for-consolidated-review'}")
    helper.write_text(text)
    package={'revision':manifest['revision'],'definition_count':41,'new_theorem_declarations':0,'inherited_discharges':0,
      'definition_index':binding(HERE/'index.json'),'review_manifest':binding(HERE/'review-manifest.json'),
      'audit_driver':binding(HERE/'verify_batch.py'),'authority_effect':'none'}
    index=read(N01/'formal-preparation-index.json')
    index['candidate_definition_batches']=[package]
    index['pending_review_audit_driver']=binding(helper)
    write(N01/'formal-preparation-index.json',index)
    seq=read(N01/'sequential-review.json')
    if 'historical_sequential_procedural_response' not in seq:
        seq['historical_sequential_procedural_response']=seq['procedural_response']
    seq['procedural_response']=procedural
    seq['review_mode']='consolidated-at-end'
    seq['status']='batch-definitions-ready-for-consolidated-review'
    seq['current_unit']='ALL41'
    seq['batch_definition_revision']=manifest['revision']
    seq['batch_definition_count']=41
    seq['batch_review_manifest']=binding(HERE/'review-manifest.json')
    for unit in seq['units']:
        if unit['actual_assessment'] is None:
            unit['status']='ready-for-consolidated-review'
        proposed=next(r for r in read(HERE/'index.json')['units'] if r['unit']==unit['unit'])
        unit['batch_definition']=proposed['definition']
        unit['batch_explanation']=proposed['explanation']
        unit['batch_actual_assessment']=None
        if unit.get('assessment_request'):
            unit['prior_sequential_request_active']=False
    write(N01/'sequential-review.json',seq)
    request={'schema':'relational.consolidated-definition-assessment-request/v1','unit':'ALL41','revision':manifest['revision'],
      'status':'ready-at-end-of-definition-preparation','review_manifest':binding(HERE/'review-manifest.json'),
      'question':'After reviewing the complete proposal, identify Kxx/Dxx/Exx revisions or approve explicitly selected meanings and shared choices. This assesses intended semantics only; theorem validity, discharges and operational readiness remain separate.',
      'actual_response':None,'procedural_response':binding(HERE/'procedural-response.json'),'new_assessments':0,'inherited_discharges':0,'authority_effect':'none'}
    write(N01/'ALL41-assessment-request.json',request)
    gate=read(N01/'decision-gate.json')
    if 'historical_sequential_decision_question' not in gate:
        gate['historical_sequential_decision_question']=gate['decision_question']
        gate['historical_sequential_recommendation']=gate['recommended']
        gate['historical_sequential_options']=gate['options']
    gate.update({'status':'complete-definition-batch-ready-for-consolidated-review','review_mode':'consolidated-at-end','current_unit':'ALL41',
      'procedural_response':procedural,'decision_question':request['question'],
      'options':[{'id':'revise-selected','label':'Identify changes to Kxx, Dxx or Exx meanings'},{'id':'accept-selected','label':'Approve expressly selected meanings and choices in the exact batch revision'},{'id':'accept-batch','label':'Approve all 41 proposed meanings and expressly selected shared policies/extension bridges'}],
      'recommended':'Review the complete set, then request changes or explicitly scope approval.',
      'actual_response':None,'selected_option':None,'active_assessment_request':binding(N01/'ALL41-assessment-request.json'),
      'batch_review_manifest':binding(HERE/'review-manifest.json'),
      'consequential_work_held':['N01 acceptance without required exact semantic/proof evidence','N02 inherited discharges without exact accepted meaning and complete proof evidence','N03 contract freeze without agreed exact successor definitions'],
      'independent_work_allowed':['Prepare/revise all 41 candidate definitions without serial approvals','Candidate formal-model and source-adapter preparation for any relation','Coverage, source, branch and binding validation without accepting or discharging inherited IDs'],
      'blocker_audit':{'prior_K04_serial_question_superseded_procedurally':True,'batch_preparation_blocked':False,'blocked_threshold_met':False}})
    write(N01/'decision-gate.json',gate)
    plan=read(SUCCESSOR/'execution/plan.json');progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    progress.update({'current_review':'ALL41','review_mode':'consolidated-at-end','prepared_batch_definition_count':41,
      'batch_review_manifest':binding(HERE/'review-manifest.json'),'batch_definition_index':binding(HERE/'index.json'),
      'sequential_review':binding(N01/'sequential-review.json'),'formal_preparation_index':binding(N01/'formal-preparation-index.json'),
      'pending_review_audit_driver':binding(helper),
      'definition_review_scheduling':'All candidate definitions prepared before consolidated human assessment; no serial K04 gate blocks preparation.'})
    write(SUCCESSOR/'execution/plan.json',plan)
    driver=N01/'check_current_review.py'
    text=driver.read_text()
    anchor="    declarations = []\n"
    insertion="""    definition_batch_counts = None
    if index.get('candidate_definition_batches'):
        import importlib.util
        assert len(index['candidate_definition_batches']) == 1
        package = index['candidate_definition_batches'][0]
        audit_path = ROOT / package['audit_driver']['path']
        spec = importlib.util.spec_from_file_location('current_definition_batch_audit', audit_path)
        batch_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(batch_module)
        definition_batch_counts = batch_module.audit(ROOT, package, check, enforce_workflow=True)
        assert progress['prepared_batch_definition_count'] == definition_batch_counts['definition_count'] == 41
        assert definition_batch_counts['new_theorem_declarations'] == definition_batch_counts['inherited_discharges'] == 0
    declarations = []
"""
    if 'definition_batch_counts = None' not in text:
        assert text.count(anchor)==1
        text=text.replace(anchor,insertion)
        report_anchor="        'candidate_fragment_theorems': len(declarations),\n"
        assert text.count(report_anchor)==1
        text=text.replace(report_anchor,"        'review_mode': seq.get('review_mode', 'sequential'),\n        'candidate_definition_batch': definition_batch_counts,\n"+report_anchor)
        driver.write_text(text)
    write(HERE/'workflow-registration.json',{'schema':'relational.batch-review-workflow-registration/v1','result':'complete-candidate-batch-registered-without-semantic-acceptance',
      'procedural_response':binding(HERE/'procedural-response.json'),'definition_manifest':binding(HERE/'review-manifest.json'),
      'historical_workflow':binding(before),'current_state':{'plan':binding(SUCCESSOR/'execution/plan.json'),'review_state':binding(N01/'sequential-review.json'),'decision_gate':binding(N01/'decision-gate.json'),'formal_index':binding(N01/'formal-preparation-index.json'),'main_driver':binding(driver)},
      'preserved_K04_audit_driver':binding(previous),'batch_K04_audit_driver':binding(helper),'definition_count':41,
      'actual_scoped_assessments_retained':4,'new_semantic_assessments':0,'candidate_fragment_theorems_retained':2036,'new_theorem_declarations':0,'inherited_discharges':0,'N01_accepted':False,'authority_effect':'none'})
    print(json.dumps({'review_mode':'consolidated-at-end','definitions':41,'new_assessments':0,'inherited_discharges':0}))

if __name__=='__main__':run()
