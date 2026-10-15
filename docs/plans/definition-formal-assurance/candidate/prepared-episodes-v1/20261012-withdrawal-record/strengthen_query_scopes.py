"""Retain successful broad countermodels; test actual outcomes under relevant source guards."""
from pathlib import Path
import json,hashlib,shutil,ast,sys
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.withdrawal-record');a=u/'attempts/001-successful-before-source-conditioned-queries';a.mkdir(parents=True)
names=['build_candidate.py','query-policy.json','source-query-obligation.json','model-controls.json','model-command-result.json','model-stdout.txt','model-stderr.txt'];refs=[]
for n in names:
 shutil.copyfile(u/n,a/n);refs.append({'path':str(a/n),'sha256':hashlib.sha256((a/n).read_bytes()).hexdigest()})
with (a/'stage.json').open('x') as f:json.dump({'status':'retained-successful-prior-query-stage','producer_exit_code':json.loads((a/'model-command-result.json').read_text())['exit_code'],'files':refs,'change':'Outcome non-entailment targets/witnesses are now conditioned on source-relevant declared availability,successor,recovery,effectiveness or subject inactivity','primary_theory_changed':False,'scope_or_population_denominator_changed':False,'source_fidelity':'pending','semantic_ready':False},f,indent=2);f.write('\n')
q=u/'build_candidate.py';s=q.read_text();i=s.index(" queries=[");j=s.index(";put('query-policy.json'",i)
replacement=""" queries=[]
 for n in ACTUAL:
  condition=None;scope_label='all-selected-records'
  if n in ['DigestAvailability','DigestFidelity']:condition=pred('RecordDigestAvailableDeclared',R);scope_label='declared-digest-available'
  elif n in ['SuccessorExistence','SuccessorResolution','SuccessorIdentity','SuccessorAdmission']:condition=pred('RecordSuccessorClaimedDeclared',R);scope_label='claimed-successor'
  elif n in ['RecoveryRuleAuthority','Restoration']:condition=pred('RecordExplicitRecoverySelectedDeclared',R);scope_label='explicit-higher-order-recovery-selected'
  elif n=='NoIdentifierReuse':condition=pred('RecordEffectiveDeclared',R);scope_label='declared-effective-record'
  elif n=='HistoricalAvailability':condition=pred('SubjectInactiveDeclared',SUBJECT);scope_label='declared-inactive-subject'
  selected_scope=APP if condition is None else both(APP,condition)
  queries.append({'query_id':'Record-not-Actual'+n,'target':allof([('WithdrawalRecordReference','r')],implies(selected_scope,pred('RecordActual'+n,R))),'witness_condition':exists([('WithdrawalRecordReference','r')],both(selected_scope,neg(pred('RecordActual'+n,R)))),'source_condition':scope_label,'selected_in_T':False,'source_fidelity':'pending'})"""
s=s[:i]+replacement+s[j:];ast.parse(s);q.write_text(s)
sys.path.insert(0,str(u));import build_candidate as b
queries=[]
for n in b.ACTUAL:
 condition=None;label='all-selected-records'
 if n in ['DigestAvailability','DigestFidelity']:condition=b.pred('RecordDigestAvailableDeclared',b.R);label='declared-digest-available'
 elif n in ['SuccessorExistence','SuccessorResolution','SuccessorIdentity','SuccessorAdmission']:condition=b.pred('RecordSuccessorClaimedDeclared',b.R);label='claimed-successor'
 elif n in ['RecoveryRuleAuthority','Restoration']:condition=b.pred('RecordExplicitRecoverySelectedDeclared',b.R);label='explicit-higher-order-recovery-selected'
 elif n=='NoIdentifierReuse':condition=b.pred('RecordEffectiveDeclared',b.R);label='declared-effective-record'
 elif n=='HistoricalAvailability':condition=b.pred('SubjectInactiveDeclared',b.SUBJECT);label='declared-inactive-subject'
 scope=b.APP if condition is None else b.both(b.APP,condition);queries.append({'query_id':'Record-not-Actual'+n,'target':b.allof([('WithdrawalRecordReference','r')],b.implies(scope,b.pred('RecordActual'+n,b.R))),'witness_condition':b.exists([('WithdrawalRecordReference','r')],b.both(scope,b.neg(b.pred('RecordActual'+n,b.R)))),'source_condition':label,'selected_in_T':False,'source_fidelity':'pending'})
policy={'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False}
with (u/'query-policy.json').open('w') as f:json.dump(policy,f,sort_keys=True,separators=(',',':'));f.write('\n')
for n in ['model-controls.json','model-command-result.json','model-stdout.txt','model-stderr.txt']:(u/n).unlink()
with (u/'query-scope-refinement.json').open('x') as f:json.dump({'retained_successful_stage_ref':{'path':str(a/'stage.json'),'sha256':hashlib.sha256((a/'stage.json').read_bytes()).hexdigest()},'primary_theory_changed':False,'source_units_changed':False,'required_populations_changed':False,'query_count':34,'source_conditioned_queries':sum(x['source_condition']!='all-selected-records' for x in queries),'reason':'Counterexamples must exhibit the relevant claimed/available/effective/recovery/inactive source condition,not only an unrelated record.'},f,indent=2);f.write('\n')
print('Retained successful broad queries; strengthened ten targets and witnesses under exact source-relevant conditions; T and I unchanged.')
