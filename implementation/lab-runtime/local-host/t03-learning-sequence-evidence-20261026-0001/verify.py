"""Cold correspondence check over three actual native learning run receipts.

This never opens a Session, revives a permission, or substitutes execution.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

def need(value,message):
 if not value:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def checked_bytes(path):
 path=Path(path);need(not path.is_symlink() and not any(p.is_symlink() for p in path.parents),'linked evidence locator')
 return path.read_bytes()
def read(path):
 raw=checked_bytes(path);return json.loads(raw),raw

def consumed_names(rows):
 expected={'later-inspection-output.json','later-assessment-candidate.json','later-assessment-result.json','later-inspection-counterevidence.json'}
 names=[row['name'] for row in rows]
 need(len(names)==len(set(names))==len(expected) and set(names)==expected,
      'later consumer did not consume the exact four distinct assessed originals')
 return names

def verify(first_path,later_path,consumer_path):
 first,fr=read(first_path);later,lr=read(later_path);consumer,cr=read(consumer_path)
 need(first['result']=='PASS-local-current-one-Lesson-selection-and-close','first Session did not pass')
 need(later['result']=='PASS-local-current-Lesson-later-application-independent-assessment','later application/assessment did not pass')
 need(consumer['result']=='PASS-local-assessed-result-later-Session-consumption-and-close','independent later consumer did not pass')
 for key in ('api_source_binding','profile_binding','family_source_binding','source_cut'):
  need(first[key]==later[key]==consumer[key],'three actual runs did not use one selected cut: '+key)
 need(later['first_session_receipt']['sha256']==sha(fr) and consumer['earlier_learning_receipt']['sha256']==sha(lr),'actual receipt chain differs')
 formals=[]
 for receipt,path in ((first,first_path),(later,later_path),(consumer,consumer_path)):
  binding=receipt['formal_session_binding'];body,raw=read(binding['path']);need(sha(raw)==binding['sha256'],'actual formal Session original differs')
  need(sha(body['session_ref'].encode())==receipt['session_ref_sha256'] and body['source_cut']==receipt['source_cut'],'actual formal Session/cut differs')
  need(body['formal_session_body']['kind']=='agent-session' and body['formal_session_body']['node_id']==body['session_ref'],'formal body is not the actual native Session identity')
  memory=body['formal_session_body']['payload']['session_memory']
  need(set(memory)=={'selected_input_refs','working_record_refs','unresolved_questions','expires_with_session'} and memory['working_record_refs']==memory['unresolved_questions']==[],'formal capture contains working notes')
  need(body['short_memory_exported'] is False,'formal capture claims private memory export');formals.append(body)
 need(len({f['session_ref'] for f in formals})==3,'the later tasks did not use distinct real Sessions')
 need(first['selection_registry_erased'] and first['explicitly_closed'] and first['memory_erased'] and first['closed_refused'],'first disposal evidence incomplete')
 need(consumer['selection_registry_erased'] and consumer['explicitly_closed'] and consumer['memory_erased'] and consumer['closed_refused'],'consumer disposal evidence incomplete')
 base=Path(later_path).parent;work=later['actual_later_work']
 originals={}
 for name,key in [('application-candidate-original.json',None),('later-application-result.json','application_reply_sha256'),('later-assessment-candidate.json','assessment_candidate_sha256'),('later-assessment-result.json','assessment_reply_sha256'),('later-inspection-output.json','inspection_output_sha256'),('later-inspection-counterevidence.json','counterevidence_sha256')]:
  value,raw=read(base/name)
  if key:need(sha(raw)==work[key],'actual later output binding differs: '+name)
  originals[name]=(value,raw)
 app,app_raw=originals['application-candidate-original.json'];proposal,_=originals['later-application-result.json']
 headers=[t['artifact'] for t in proposal['targets'] if t['artifact']['carrier_ref']=='cal.artifact-type.lesson-application/v1']
 need(len(headers)==1 and headers[0]['byte_sha256']==sha(app_raw) and headers[0]['identity_ref']==app['node_id'],'actual application target/original differs')
 need(app['payload']['session_ref']==formals[1]['session_ref'] and sha(app['payload']['lesson_revision_ref'].encode())==first['lesson_version_ref_sha256']==later['lesson_version_ref_sha256'],'application lost the actual earlier Lesson/later Session')
 assessment,_=originals['later-assessment-candidate.json']
 need(assessment['payload']['lesson_application_ref']==headers[0]['version_ref'] and assessment['owner_ref']!=app['owner_ref'],'assessment lost exact application or independent assessor')
 ceiling='Exact recorded application outcome only; no general or causal effectiveness inferred.'
 need(assessment['payload']['disposition']=='recorded-outcome-only' and assessment['payload']['causal_claim_ceiling']==assessment['claim_ceiling']==ceiling and bool(assessment['payload']['counterevidence_refs']),'recorded outcome was upgraded or counterevidence lost')
 need(work['parent_session_closed'] and work['independent_assessment_after_parent_close'],'assessment borrowed a live parent')
 events=[json.loads(line) for line in checked_bytes(base/'events.jsonl').decode().splitlines()]
 closed=[e for e in events if e.get('phase')=='parent.close-before-assessment' and e.get('state')=='passed']
 assessed=[e for e in events if e.get('phase')=='lesson.assess' and e.get('state')=='starting']
 need(len(closed)==len(assessed)==1 and closed[0]['at_utc']<assessed[0]['at_utc'],'actual parent close did not precede assessment')
 consumed_names(consumer['consumed_inputs'])
 need(consumer['lesson_version_ref_sha256']==first['lesson_version_ref_sha256']==later['lesson_version_ref_sha256'],'later consumer selected a different Lesson')
 for row in consumer['consumed_inputs']:
  raw=originals[row['name']][1]
  need(row['sha256']==sha(raw) and row['size_bytes']==len(raw) and row['actual_private_input_read_and_native_note'] is True,'later real result consumption differs')
 need(len(consumer['consumed_inputs'])==4 and consumer['assessed_result_later_consumed'],'later result consumption incomplete')
 privacy=consumer['Machine_privacy_result']
 need(privacy['result']=='PASS-actual-Machine-Session-private-memory-boundaries' and privacy['held_note_zeroed'] and privacy['memory_erased'] and privacy['selection_registry_erased'] and privacy['private_vault_write_refused'] and privacy['checked']['wire_replies']>=4 and privacy['checked']['durable_files']>0,'actual Machine privacy/disposal evidence incomplete')
 observed=set(first['common_dispatch_operation_pairs'])|set(later['common_dispatch_operation_pairs'])|set(consumer['common_dispatch_operation_pairs'])
 required={'context.get','session.open','session.inspect','session.close','lesson.select','lesson.apply','lesson.assess'}
 need(required<=observed,'seven actual common lifecycle operation pairs incomplete')
 negatives=later['permission_negatives']
 need(negatives['changed_to_revoked_selected_grant_refused'] and negatives['actual_clock_expired_grant_refused'] and negatives['whole_Vault_unchanged'] and negatives['closed_parent_not_resurrected'],'actual permission negatives incomplete')
 return {'schema_version':'lab-cold-actual-three-Session-learning-correspondence/v1','result':'PASS-cold-original-learning-sequence-correspondence','api_source_binding':first['api_source_binding'],'profile_binding':first['profile_binding'],'family_source_binding':first['family_source_binding'],'actual_distinct_Sessions':3,'actual_operation_pairs':sorted(required),'actual_receipt_sha256':[sha(fr),sha(lr),sha(cr)],'actual_application_original_sha256':sha(app_raw),'actual_parent_disposal_before_independent_assessment':True,'actual_assessed_result_later_consumed':True,'actual_Machine_privacy':privacy,'canonical_admissions':0,'authority_effect':'none'}

if __name__=='__main__':
 p=argparse.ArgumentParser()
 for key in ('first','later','consumer','output'):p.add_argument('--'+key,required=True)
 a=p.parse_args();result=verify(a.first,a.later,a.consumer);raw=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode()
 fd=os.open(a.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(raw)
 print(json.dumps({'result':result['result'],'sha256':sha(raw)}))
