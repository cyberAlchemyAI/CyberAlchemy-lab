"""Hypothetical current-member/owner profiles, Team frames and actual carrier observations."""
import copy,json,types
from datetime import datetime
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def baseline():
 root=b.ROOT/'authority/artifact-types';rec=json.loads((root/'team/v1/fixtures/valid/record.json').read_bytes());m=json.loads((root/'team-membership/v1/fixtures/valid/record.json').read_bytes())
 return {'record':rec,'Team_entity':'Team:hyp1','carrier_entity':'Record:Team:hyp1','owner_qualification':{'team_ref':rec['node_id'],'scope_ref':rec['scope_ref'],'owner_route':rec['owner_route'],'justification_marker':'hypothetical-owner-qualification:1'},'membership_resolution':{m['node_id']:{'record':m,'membership_entity':'Membership:hyp1','Person_entity':'Human:hyp1','reference_resolution_marker':'hypothetical-Person-reference-resolution:1'}},'query_time':'2026-10-06T00:00:00Z','reference_only_conclusions':[],'independent_outcomes':[],'owner_policy_reviewed':False,'actual_collective_Human_and_owner_verified':False}
def stamp(value):return datetime.strptime(value,'%Y-%m-%dT%H:%M:%SZ')
def errors(p):
 es=[];rec=p['record'];resolved=[];now=None
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected profile')
 ck(rec['status']=='candidate-unadmitted' and rec['authority_effect']=='none','candidate posture/non-effect retained')
 ck(p['Team_entity']!=p['carrier_entity'],'hypothetical collective entity distinct from machine carrier')
 ck(all(isinstance(rec[k],str) and bool(rec[k].strip()) for k in ['node_id','name','purpose','scope_ref','identity_boundary','owner_ref','owner_route','challenge_route']),'explicit nonempty selected metadata; values not authenticated')
 q=p['owner_qualification'];ck(q['team_ref']==rec['node_id'] and q['scope_ref']==rec['scope_ref'] and q['owner_route']==rec['owner_route'] and bool(q['justification_marker']),'exact hypothetical owner qualification, scope and route')
 ck(rec['lifecycle_state'] in ['proposed','active','suspended','retired','superseded'],'selected Team lifecycle vocabulary')
 ck(rec['node_id'] not in rec['successor_refs'],'selected stronger policy rejects self-successor')
 if rec['lifecycle_state']=='superseded':ck(bool(rec['successor_refs']),'selected stronger superseded-Team policy requires explicit successor')
 try:now=stamp(p['query_time'])
 except (ValueError,TypeError):es.append('invalid selected UTC query calendar')
 for token in rec['membership_refs']:
  row=p['membership_resolution'].get(token)
  if row is None:resolved.append({'token':token,'status':'unresolved-record','current_under_hypothesis':None});continue
  m=row['record'];status='resolved-hypothetical-record';within=current=None;issues=[]
  if m['node_id']!=token:issues.append('resolved-node-token-mismatch')
  if m['team_ref']!=rec['node_id']:issues.append('different-Team')
  if m['scope_ref']!=rec['scope_ref']:issues.append('different-selected-scope')
  if not row['reference_resolution_marker'] or not row['Person_entity']:issues.append('unresolved-Person-denotation')
  if row['membership_entity'] in [p['Team_entity'],row['Person_entity']] or row['Person_entity']==p['Team_entity']:issues.append('collapsed-membership-or-Person-entity')
  start=end=None;end_known=m['period']['end'] is None
  try:start=stamp(m['period']['start'])
  except (ValueError,TypeError):issues.append('invalid-start-calendar')
  if m['period']['end'] is not None:
   try:end=stamp(m['period']['end']);end_known=True
   except (ValueError,TypeError):issues.append('invalid-end-calendar')
  if start is not None and end is not None and end<=start:issues.append('nonordered-selected-period')
  if start is not None and now is not None and end_known:within=start<=now and (end is None or now<end)
  if not issues and within is not None:current=m['membership_state']=='active' and within
  if issues:status='unresolved-or-invalid-selected-binding'
  resolved.append({'token':token,'status':status,'issues':issues,'within_selected_half_open_effective_period':within,'current_under_hypothesis':current,'Person_entity':row['Person_entity'],'actual_currentness_or_Human_verified':False})
 current=[x for x in resolved if x['current_under_hypothesis'] is True]
 if rec['lifecycle_state']=='active':ck(bool(current),'active Team needs at least one exact resolved hypothetical current membership/Person')
 ck(not p['reference_only_conclusions'],'Team/membership/owner labels alone no selected world conclusion')
 ck(set(p['independent_outcomes'])<=set(b.OUTCOMES),'independent world outcomes separate')
 ck(p['owner_policy_reviewed'] is False and p['actual_collective_Human_and_owner_verified'] is False,'hypothetical profile never creates owner or actual entity verification')
 return es,{'listed_refs':len(rec['membership_refs']),'current_hypothetical_witnesses':len(current),'resolved_rows':resolved,'actual_currentness_verified':False,'complete_actual_membership_catalog_verified':False,'period_policy':'hypothetical-effective-period-half-open-UTC; source time-bound interpretation remains unreviewed'}
def controls():
 rows=[]
 def add(id,change,bad=False,current=1):
  p=baseline();change(p);es,detail=errors(p)
  if bool(es)!=bad or detail['current_hypothetical_witnesses']!=current:raise ValueError('Unexpected Team profile '+id+' '+str((es,detail)))
  if id=='invalid-nonnull-end-is-unknown-not-open' and detail['resolved_rows'][0]['within_selected_half_open_effective_period'] is not None:raise ValueError('Invalid end became open/false interval')
  rows.append({'case_id':id,'profile':p,'errors':es,'membership_check':detail,'expected_rejection':bad,'owner_policy_reviewed':False,'actual_collective_Human_owner_denotation_established':False,'actual_runtime_execution':False})
 add('active-Team-one-hypothetical-resolved-current-witness',lambda p:None)
 def extra(p,state='inactive'):
  token='Membership:hyp2';r=copy.deepcopy(next(iter(p['membership_resolution'].values())));r['record'].update(node_id=token,membership_state=state);r['membership_entity']='Membership:hyp2';p['record']['membership_refs'].append(token);p['membership_resolution'][token]=r
 add('one-current-plus-one-inactive-ref-permitted',extra)
 add('one-current-plus-one-unresolved-ref-permitted-not-whole-catalog-closure',lambda p:p['record']['membership_refs'].append('absent:Membership'))
 add('two-current-witnesses-permitted',lambda p:extra(p,'active'),current=2)
 add('proposed-Team-with-no-members-permitted',lambda p:p['record'].update(lifecycle_state='proposed',membership_refs=[]),current=0)
 add('retired-Team-with-no-members-permitted',lambda p:p['record'].update(lifecycle_state='retired',membership_refs=[]),current=0)
 add('independent-world-facts-allowed',lambda p:p.update(independent_outcomes=b.OUTCOMES))
 add('display-name-change-preserves-selected-boundary',lambda p:p['record'].update(name='Other functional label'))
 add('active-Team-empty-ref-list',lambda p:p['record'].update(membership_refs=[]),True,0)
 add('active-Team-only-unresolved-token',lambda p:p['record'].update(membership_refs=['absent:Membership']),True,0)
 def member(p):return next(iter(p['membership_resolution'].values()))
 add('active-Team-before-membership-start',lambda p:p.update(query_time='2026-10-04T00:00:00Z'),True,0)
 add('active-Team-after-membership-end',lambda p:member(p)['record']['period'].update(end='2026-10-05T12:00:00Z'),True,0)
 add('active-Team-half-open-exact-end',lambda p:member(p)['record']['period'].update(end=p['query_time']),True,0)
 for state in ['proposed','inactive','revoked']:add('active-Team-only-'+state+'-membership',lambda p,state=state:member(p)['record'].update(membership_state=state),True,0)
 add('resolved-membership-wrong-Team',lambda p:member(p)['record'].update(team_ref='other:Team'),True,0)
 add('resolved-membership-wrong-selected-scope',lambda p:member(p)['record'].update(scope_ref='other:Scope'),True,0)
 add('resolved-record-token-mismatch',lambda p:member(p)['record'].update(node_id='other:Membership'),True,0)
 add('unresolved-Person-denotation-marker',lambda p:member(p).update(reference_resolution_marker=''),True,0)
 add('membership-entity-collapsed-with-Team',lambda p:member(p).update(membership_entity=p['Team_entity']),True,0)
 add('Person-entity-collapsed-with-Team',lambda p:member(p).update(Person_entity=p['Team_entity']),True,0)
 add('invalid-start-calendar',lambda p:member(p)['record']['period'].update(start='2026-99-99T00:00:00Z'),True,0)
 add('invalid-nonnull-end-is-unknown-not-open',lambda p:member(p)['record']['period'].update(end='2026-99-99T00:00:00Z'),True,0)
 add('invalid-query-calendar',lambda p:p.update(query_time='2026-99-99T00:00:00Z'),True,0)
 add('Team-collapsed-with-machine-carrier',lambda p:p.update(carrier_entity=p['Team_entity']),True)
 for key in ['purpose','scope_ref','owner_route','identity_boundary','challenge_route']:add('empty-'+key,lambda p,key=key:p['record'].__setitem__(key,' '),True,current=0 if key=='scope_ref' else 1)
 add('owner-qualification-wrong-Team',lambda p:p['owner_qualification'].update(team_ref='other'),True)
 add('owner-qualification-wrong-scope',lambda p:p['owner_qualification'].update(scope_ref='other'),True)
 add('owner-qualification-wrong-route',lambda p:p['owner_qualification'].update(owner_route='other'),True)
 add('owner-qualification-marker-missing',lambda p:p['owner_qualification'].update(justification_marker=''),True)
 add('self-successor-not-selected-policy',lambda p:p['record']['successor_refs'].append(p['record']['node_id']),True)
 add('superseded-without-successor-not-selected-policy',lambda p:p['record'].update(lifecycle_state='superseded'),True)
 for n in b.OUTCOMES:add('Team-alone-not-'+n,lambda p,n=n:p.update(reference_only_conclusions=[n]),True)
 add('authority-effect-not-Team-metadata',lambda p:p['record'].update(authority_effect='grant'),True)
 add('owner-review-not-invented',lambda p:p.update(owner_policy_reviewed=True),True)
 add('actual-collective-owner-Human-verification-not-invented',lambda p:p.update(actual_collective_Human_and_owner_verified=True),True)
 return rows
def frames():
 rows=[]
 def baseline_frame():
  rec=baseline()['record'];z=copy.deepcopy(rec);z['membership_refs']=['Membership:hyp-successor']
  return {'operation':'change-members','before':rec,'after':z,'before_Team_entity':'Team:hyp1','after_Team_entity':'Team:hyp1','before_current_People':['Human:hyp1'],'after_current_People':['Human:hyp2'],'old_record_retained':True,'membership_decision_marker':'Decision:hyp-membership','separate_assignment_decision_marker':None,'before_authority':[],'after_authority':[],'separate_authority_decision_marker':None,'successor':None,'succession_effect':None}
 def check(f):
  es=[];a=f['before'];z=f['after']
  if f['operation'] not in ['change-members','change-label','retire','supersede']:es.append('operation outside selected Team frame')
  for key in ['node_id','purpose','scope_ref','owner_route','owner_ref','identity_boundary']:
   if a[key]!=z[key]:es.append('selected stable-boundary Team frame preserves '+key)
  if f['before_Team_entity']!=f['after_Team_entity']:es.append('selected continuing Team Entity unchanged')
  if not f['old_record_retained']:es.append('prior Team/member projection retained')
  if f['operation']=='change-members' and not f['membership_decision_marker']:es.append('hypothetical independently governed membership change marker required')
  if (a['role_assignment_refs']!=z['role_assignment_refs'] or a['responsibility_refs']!=z['responsibility_refs']) and f['separate_assignment_decision_marker'] is None:es.append('membership change alone does not alter independent assignments')
  if f['before_authority']!=f['after_authority'] and f['separate_authority_decision_marker'] is None:es.append('Team/member metadata alone does not change independent authority')
  if f['operation']=='change-label' and (a['membership_refs']!=z['membership_refs'] or a['lifecycle_state']!=z['lifecycle_state']):es.append('selected label edit preserves members and lifecycle')
  if f['operation']=='retire' and z['lifecycle_state']!='retired':es.append('retirement exact state')
  if f['operation']=='supersede':
   s=f['successor']
   if z['lifecycle_state']!='superseded' or s is None or s['node_id']==a['node_id'] or s['node_id'] not in z['successor_refs'] or f['succession_effect']!='supersedes':es.append('explicit fresh successor and replacement effect required by selected stronger policy')
  return es
 def add(id,change,bad=False):
  f=baseline_frame();change(f);es=check(f)
  if bool(es)!=bad:raise ValueError('Unexpected Team frame '+id+' '+str(es))
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'owner_policy_reviewed':False,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 add('actual-hypothetical-Person-set-changes-same-Team-boundary',lambda f:None)
 add('fresh-membership-record-same-Person-set-also-preserves-Team',lambda f:f.update(after_current_People=f['before_current_People']))
 add('separate-assignment-decision-can-coexist',lambda f:f['after']['role_assignment_refs'].append('Assignment:hyp2') or f.update(separate_assignment_decision_marker='Decision:hyp-assignment'))
 add('separate-authority-decision-can-coexist',lambda f:f.update(after_authority=['Permission:hyp'],separate_authority_decision_marker='Decision:hyp-authority'))
 add('retirement-does-not-automatically-revoke-independent-authority',lambda f:f.update(operation='retire') or f['after'].update(lifecycle_state='retired'))
 add('functional-label-edit-same-boundary-and-members',lambda f:f.update(operation='change-label') or f['after'].update(name='Other functional label',membership_refs=f['before']['membership_refs']))
 def successor(f):f.update(operation='supersede',successor={**copy.deepcopy(f['before']),'node_id':'Team:hyp-successor'},succession_effect='supersedes');f['after'].update(lifecycle_state='superseded',successor_refs=['Team:hyp-successor'])
 add('explicit-fresh-successor-replacement-not-identity-equality',successor)
 for key in ['node_id','purpose','scope_ref','owner_route','owner_ref','identity_boundary']:add('membership-step-changes-'+key,lambda f,key=key:f['after'].__setitem__(key,'other'),True)
 add('membership-step-changes-Team-Entity',lambda f:f.update(after_Team_entity='other'),True)
 add('prior-history-discarded',lambda f:f.update(old_record_retained=False),True)
 add('membership-change-marker-missing',lambda f:f.update(membership_decision_marker=''),True)
 add('membership-alone-adds-role-assignment',lambda f:f['after']['role_assignment_refs'].append('Assignment:hyp2'),True)
 add('membership-alone-adds-responsibility',lambda f:f['after']['responsibility_refs'].append('Responsibility:hyp2'),True)
 add('membership-alone-grants-authority',lambda f:f.update(after_authority=['Permission:hyp']),True)
 add('membership-alone-revokes-authority',lambda f:f.update(before_authority=['Permission:hyp']),True)
 add('label-edit-changes-members',lambda f:f.update(operation='change-label'),True)
 add('retirement-wrong-state',lambda f:f.update(operation='retire'),True)
 add('superseded-without-successor',lambda f:f.update(operation='supersede') or f['after'].update(lifecycle_state='superseded'),True)
 add('succession-without-replacement-effect',lambda f:successor(f) or f.update(succession_effect='continues'),True)
 add('succession-self-reference',lambda f:successor(f) or f['successor'].update(node_id=f['before']['node_id']),True)
 add('unselected-operation',lambda f:f.update(operation='grant-authority'),True)
 return rows
