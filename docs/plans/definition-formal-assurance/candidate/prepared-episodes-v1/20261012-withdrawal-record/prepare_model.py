"""Prepare exact Withdrawal Record optional-field,recovery and history finite controls."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;dest=p/'prepared'
s='''"""Supplied Withdrawal Record declaration models; no real identifier transitions."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
def getfn(m,n,*args):return next(x['value'] for x in m['functions'][n] if x['args']==list(args))
def refresh(m):
 for fields,carrier in b.GROUPS:
  for n in fields:m['predicates'][n+'BindingDeclared']=[[x['args'][0],x['value']] for x in m['functions'][n]]
def base_model():
 ds={'WithdrawalRecordReference':['r'+str(i) for i in range(6)]+['rOutside'],'IdentifierReference':['id'+str(i) for i in range(8)]+['idOutside'],'SubjectReference':['p'+str(i) for i in range(6)]+['pOutside'],'DigestReference':['dig0','dig1','dig2','digOutside'],'PostureReference':['post0','post1','postOutside'],'ReasonReference':['reason'+str(i) for i in range(6)]+['reasonOutside'],'TimeReference':['time'+str(i) for i in range(6)]+['timeOutside'],'DecisionReference':['d'+str(i) for i in range(6)]+['dOutside'],'OwnerReference':['owner0','owner1','ownerOutside'],'EvidenceReference':['ev0','ev1','evOutside'],'ChallengeReference':['route0','route1','routeOutside'],'SuccessorReference':['s0','s1','s2','sOutside'],'AdmissionStateReference':['state0','state1','stateOutside'],'RecoveryRuleReference':['q0','q1','qOutside'],'HistoricalResolutionReference':['h'+str(i) for i in range(6)]+['hOutside'],'Token':['empty','reference','other']}
 def suffix(x):return 'Outside' if x.endswith('Outside') else x[-1]
 def digest(x):return {'0':'dig0','2':'dig1','4':'dig2'}.get(suffix(x),'digOutside')
 maps={'recordIdentifier':lambda x:'id'+suffix(x),'recordSubject':lambda x:'p'+suffix(x),'recordPosture':lambda x:'postOutside' if x.endswith('Outside') else 'post1' if x=='r2' else 'post0','recordReason':lambda x:'reason'+suffix(x),'recordEffectiveTime':lambda x:'time'+suffix(x),'recordOwnerDecision':lambda x:'d'+suffix(x),'recordEvidence':lambda x:'evOutside' if x.endswith('Outside') else 'ev1' if x in ['r3','r4','r5'] else 'ev0','recordChallenge':lambda x:'routeOutside' if x.endswith('Outside') else 'route1' if x in ['r3','r4','r5'] else 'route0','recordHistoryResolution':lambda x:'h'+suffix(x),'recordDigest':digest,'recordSuccessor':lambda x:{'r0':'s0','r2':'s1','r4':'s2'}.get(x,'sOutside'),'recordRecoveryRule':lambda x:{'r3':'q0','r4':'q1'}.get(x,'qOutside'),'subjectIdentifier':lambda x:'id'+suffix(x),'subjectLastKnownDigest':digest,'decisionOwner':lambda x:'ownerOutside' if x.endswith('Outside') else 'owner1' if x in ['d3','d4','d5'] else 'owner0','successorIdentity':lambda x:{'s0':'id6','s1':'id7','s2':'id5','sOutside':'idOutside'}[x],'successorAdmissionState':lambda x:'stateOutside' if x.endswith('Outside') else 'state1' if x=='s1' else 'state0','historyRecord':lambda x:'r'+suffix(x),'historyIdentifier':lambda x:'id'+suffix(x),'historyPosture':lambda x:'postOutside' if x.endswith('Outside') else 'post1' if x=='h2' else 'post0'}
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['WithdrawalRecordReference','Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in ['RecordApplicable','RecordInScopeDeclared','RecordPermanentDeclared','RecordGovernedDeclared','RecordBoundedDeclared','RecordGovernanceLineageDeclared']:preds[n]=[['r'+str(i)] for i in range(6)]
 preds.update(RecordRetiredIdentifierDeclared=[['r0'],['r2'],['r3'],['r5']],RecordRejectedIdentifierDeclared=[['r1'],['r2'],['r4']],RecordDigestAvailableDeclared=[['r0'],['r2'],['r4']],SubjectDigestAvailableDeclared=[['p0'],['p2'],['p4']],RecordEffectiveDeclared=[['r0'],['r1'],['r3']],RecordIdentifierReuseRejectedDeclared=[['r0'],['r1'],['r3']],RecordIdentifierReservedDeclared=[['r0'],['r1'],['r2'],['r5']],RecordExplicitRecoverySelectedDeclared=[['r3'],['r4']],RecordReservationExceptionDeclared=[['r3'],['r4']],RecordSuccessorClaimedDeclared=[['r0'],['r2'],['r4']],SubjectInactiveDeclared=[['p1'],['p2'],['p4']],RecordActualAuthority=[['r1']])
 preds['DecisionRecordedDeclared']=[['d'+str(i)] for i in range(6)]
 for n in ['SuccessorRecordedDeclared','SuccessorIndependentlyResolvedDeclared','SuccessorOwnIdentityPreservedDeclared','SuccessorOwnAdmissionStatePreservedDeclared']:preds[n]=[['s0'],['s1'],['s2']]
 for n in ['HistoryRecordedDeclared','HistoryWithoutLoadingSubjectDeclared']:preds[n]=[['h'+str(i)] for i in range(6)]
 preds['HistoryResolvableDeclared']=[['h1'],['h2'],['h4']]
 for n in ['RecoveryRuleRecordedDeclared','RecoveryRuleExplicitDeclared','RecoveryRuleHigherOrderDeclared','RecoveryRulePermitsRestorationDeclared']:preds[n]=[['q0'],['q1']]
 preds['RecoveryRuleAppliesToIdentifierDeclared']=[['q0','id3'],['q1','id4']]
 m={'domains':ds,'constants':{'EMPTY':'empty'},'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('exact-reservation-optional-digest-successor-recovery-and-history-records')
 add('no-selected-records',lambda m:m['predicates'].update(RecordApplicable=[],RecordInScopeDeclared=[]),I=False)
 add('only-first-record-selected',lambda m:m['predicates'].update(RecordApplicable=[['r0']],RecordInScopeDeclared=[['r0']]),I=False)
 add('no-independent-authority',lambda m:m['predicates'].update(RecordActualAuthority=[]),I=False)
 add('all-actual-outcomes-independently-supplied',lambda m:[m['predicates'].update({'RecordActual'+n:[['r'+str(i)] for i in range(6)]}) for n in b.ACTUAL],I=False)
 for n in b.ACTUAL:add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['RecordActual'+n].append(['r0']))
 for n in b.EXCLUDED:
  add('selected-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['r0']),T=False,I=None)
  add('outside-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['rOutside']))
 add('unused-unavailable-digest-handle-empty',lambda m:setfn(m,b.HANDLES['DigestReference'],'digOutside','empty'))
 add('unused-successor-handle-empty',lambda m:setfn(m,b.HANDLES['SuccessorReference'],'sOutside','empty'))
 add('unused-recovery-handle-empty',lambda m:setfn(m,b.HANDLES['RecoveryRuleReference'],'qOutside','empty'))
 add('unavailable-digest-binding-absent-allowed',lambda m:m['predicates'].update(recordDigestBindingDeclared=[x for x in m['predicates']['recordDigestBindingDeclared'] if x[0]!='r1']))
 add('unclaimed-successor-binding-absent-allowed',lambda m:m['predicates'].update(recordSuccessorBindingDeclared=[x for x in m['predicates']['recordSuccessorBindingDeclared'] if x[0]!='r1']))
 add('unused-recovery-binding-absent-allowed',lambda m:m['predicates'].update(recordRecoveryRuleBindingDeclared=[x for x in m['predicates']['recordRecoveryRuleBindingDeclared'] if x[0]!='r0']))
 add('same-successor-identity-label-not-automatically-merge',lambda m:change(m,'successorIdentity','s0','id0'))
 add('active-subject-history-availability-not-forced',lambda m:m['predicates']['HistoryResolvableDeclared'].append(['h0']))
 add('inactive-record-reuse-rejection-independent',lambda m:m['predicates']['RecordIdentifierReuseRejectedDeclared'].append(['r5']))
 add('retired-and-rejected-inclusive',lambda m:m['predicates']['RecordRejectedIdentifierDeclared'].append(['r0']))
 add('governed-missing',lambda m:m['predicates']['RecordGovernedDeclared'].remove(['r0']),T=False,I=None)
 add('bounded-missing',lambda m:m['predicates']['RecordBoundedDeclared'].remove(['r0']),T=False,I=None)
 add('permanent-missing',lambda m:m['predicates']['RecordPermanentDeclared'].remove(['r0']),T=False,I=None)
 add('governance-lineage-missing',lambda m:m['predicates']['RecordGovernanceLineageDeclared'].remove(['r0']),T=False,I=None)
 add('no-retired-or-rejected-identifier',lambda m:m['predicates']['RecordRetiredIdentifierDeclared'].remove(['r0']),T=False,I=None)
 add('scope-selected-without-source-scope',lambda m:m['predicates']['RecordInScopeDeclared'].remove(['r0']),T=False,I=None)
 add('subject-identifier-mismatch',lambda m:change(m,'subjectIdentifier','p0','id1'),T=False,I=None)
 add('available-digest-subject-flag-missing',lambda m:m['predicates']['SubjectDigestAvailableDeclared'].remove(['p0']),T=False,I=None)
 add('record-digest-availability-missing',lambda m:m['predicates']['RecordDigestAvailableDeclared'].remove(['r0']),T=False,I=None)
 add('available-digest-subject-mismatch',lambda m:change(m,'recordDigest','r0','dig1'),T=False,I=None)
 add('no-recovery-but-identifier-not-reserved',lambda m:m['predicates']['RecordIdentifierReservedDeclared'].remove(['r0']),T=False,I=None)
 add('reservation-exception-without-explicit-recovery',lambda m:m['predicates']['RecordReservationExceptionDeclared'].append(['r0']),T=False,I=None)
 add('explicit-recovery-without-reservation-exception',lambda m:m['predicates']['RecordReservationExceptionDeclared'].remove(['r3']),T=False,I=None)
 add('effective-record-reuse-not-rejected',lambda m:m['predicates']['RecordIdentifierReuseRejectedDeclared'].remove(['r0']),T=False,I=None)
 add('effective-recovery-still-needs-reuse-rejection',lambda m:m['predicates']['RecordIdentifierReuseRejectedDeclared'].remove(['r3']),T=False,I=None)
 for n,arg in [('DecisionRecordedDeclared','d0'),('SuccessorRecordedDeclared','s0'),('SuccessorIndependentlyResolvedDeclared','s0'),('SuccessorOwnIdentityPreservedDeclared','s0'),('SuccessorOwnAdmissionStatePreservedDeclared','s0'),('HistoryRecordedDeclared','h0'),('HistoryWithoutLoadingSubjectDeclared','h0'),('HistoryResolvableDeclared','h1'),('RecoveryRuleRecordedDeclared','q0'),('RecoveryRuleExplicitDeclared','q0'),('RecoveryRuleHigherOrderDeclared','q0'),('RecoveryRulePermitsRestorationDeclared','q0')]:add('missing-selected-posture-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 add('recovery-not-applicable-to-record-identifier',lambda m:m['predicates']['RecoveryRuleAppliesToIdentifierDeclared'].remove(['q0','id3']),T=False,I=None)
 for n,value in [('historyRecord','r1'),('historyIdentifier','id1'),('historyPosture','post1')]:add('history-inexact-'+n,lambda m,n=n,value=value:change(m,n,'h0',value),T=False,I=None)
 targets={id(b.RECORD_FIELDS):'r0',id(b.DIGEST_FIELDS):'r0',id(b.SUCCESSOR_FIELDS):'r0',id(b.RECOVERY_FIELDS):'r3',id(b.SUBJECT_FIELDS):'p0',id(b.SUBJECT_DIGEST_FIELDS):'p0',id(b.DECISION_FIELDS):'d0',id(b.SUCCESSOR_RECORD_FIELDS):'s0',id(b.HISTORY_FIELDS):'h0'}
 for fields,carrier in b.GROUPS:
  arg=targets[id(fields)]
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   alt=next(x for x in base_model()['domains'][sort] if x!=getfn(base_model(),n,arg));add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   value=getfn(base_model(),n,arg);declared='RecordApplicable' if sort=='WithdrawalRecordReference' else sort+'Declared';add('undeclared-selected-target-'+n,lambda m,declared=declared,value=value:m['predicates'][declared].remove([value]),T=False,I=None)
 selected={'WithdrawalRecordReference':'r0','IdentifierReference':'id0','SubjectReference':'p0','DigestReference':'dig0','PostureReference':'post0','ReasonReference':'reason0','TimeReference':'time0','DecisionReference':'d0','OwnerReference':'owner0','EvidenceReference':'ev0','ChallengeReference':'route0','SuccessorReference':'s0','AdmissionStateReference':'state0','RecoveryRuleReference':'q0','HistoricalResolutionReference':'h0'}
 for sort,n in b.HANDLES.items():add('empty-selected-handle-'+sort,lambda m,n=n,value=selected[sort]:setfn(m,n,value,'empty'),T=False,I=None)
 add('malformed-empty-domain',lambda m:m['domains'].update(WithdrawalRecordReference=[]),error='empty-or-malformed-domain')
 add('malformed-missing-domain',lambda m:m['domains'].pop('IdentifierReference'),error='model-signature-denominator-mismatch')
 add('malformed-missing-function',lambda m:m['functions'].pop('recordIdentifier'),error='model-signature-denominator-mismatch')
 add('malformed-partial-function',lambda m:m['functions']['recordIdentifier'].pop(),error='nontotal-function')
 add('malformed-function-range',lambda m:setfn(m,'recordIdentifier','r0','foreign'),error='ill-sorted-function-result')
 add('malformed-function-argument',lambda m:m['functions']['recordIdentifier'][0].update(args=['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-range',lambda m:m['predicates']['RecordApplicable'].append(['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-arity',lambda m:m['predicates']['RecoveryRuleAppliesToIdentifierDeclared'].append(['q0']),error='ill-sorted-model-tuple')
 return rows
def qualify(model,ids):return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}
'''
old=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.semantic-epoch/verify_candidate.py').read_text();tail=old[old.index('def verify(write=False):'):].replace('cal.definition.schema-evolution-invariant/','cal.definition.semantic-epoch/').replace('SemanticEpoch','WithdrawalRecord').replace('Exact immutable owner-selected epoch genus,owner/material assessment,predecessor/successor/selection/delta/lineage and representation exclusions checked on supplied models;actual materiality,owner selection,lineage,storage,authority and whole proof remain pending.','Exact permanent governance/lineage record,reservation,conditional digest,optional independent successor,explicit higher-order recovery and historical resolution declarations checked on supplied models;actual withdrawal,identity,hashes,owner authorization,retention,lookup,restoration,effects and whole proof remain pending.')
s+=tail;ast.parse(s)
with (dest/'verify_candidate.py').open('x') as f:f.write(s)
print('Prepared Withdrawal Record supplied finite models and independent hostile controls.')
