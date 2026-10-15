"""Exact material closure and actual selected local publisher/adoption preparation."""
import copy
from jsonschema import Draft202012Validator,FormatChecker
from .host import *
CEILING='Isolated independently scoped operator-owned candidate evidence only. No human approval, R08 outcome, repository admission, activation, operational usefulness, release or completed Work.'
def protocol(host,name,value):return host.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:'+name+':v1-candidate',value)
def record(host,b,kind,version='v1'):
 raw=host.material(b);v=parse(raw);schema=ROOT/f'authority/artifact-types/{kind}/{version}/schema.json'
 need(v['kind']==kind and v['authority_effect']=='none' and Draft202012Validator(parse(schema.read_bytes()),format_checker=FormatChecker()).is_valid(v),'invalid-contract','Exact selected artifact body does not conform to its original carrier schema.')
 return v,raw

def recognition(host,selection):
 owner_keys={};required=selection['required_members']
 for item in selection['recognized_owners']:
  need(set(item)=={'principal_ref','role_ref','principal_binding','role_binding','assignment_binding','recognition_binding','public_key_hex','not_before','expires_at'},'unauthorized','Closed independent owner recognition required.')
  principal,_=record(host,item['principal_binding'],'principal');role,_=record(host,item['role_binding'],'role');assignment,_=record(host,item['assignment_binding'],'role-assignment')
  need(principal['node_id']==item['principal_ref'] and principal['payload']['status']=='active' and role['node_id']==item['role_ref'] and role['lifecycle_state']=='active','unauthorized','Selected owner Principal or Role is inactive or differs.')
  need(assignment['assignment_state']=='active' and assignment['role_ref']==role['node_id'] and assignment['assignee_ref']==principal['payload']['stable_subject_ref'] and assignment['scope_ref']==host.policy['scope_refs'][0],'unauthorized','Actual selected owner/Role assignment differs.')
  need(instant(assignment['period']['start'])<=now() and (assignment['period']['end'] is None or now()<instant(assignment['period']['end'])),'expired-authority','Actual selected owner Role assignment expired.')
  expected={'schema_version':'lab-owned-governance-owner-recognition/v1-candidate','principal_binding':item['principal_binding'],'role_binding':item['role_binding'],'assignment_binding':item['assignment_binding'],'public_key_hex':item['public_key_hex'],'scope_ref':host.policy['scope_refs'][0],'authority_effect':'none','claim_ceiling':CEILING}
  need(host.document(item['recognition_binding'])==expected,'unauthorized','Independent owner recognition original differs.')
  pair=(item['principal_ref'],item['role_ref']);need(pair not in owner_keys,'unauthorized','Duplicate independently selected owner key.')
  owner_keys[pair]={k:item[k] for k in ('public_key_hex','recognition_binding','not_before','expires_at')}
 need(set(owner_keys)=={(m['owner_principal_ref'],m['owner_role_ref']) for m in required},'unauthorized','Selected owner keys do not cover the exact required roster.')
 return owner_keys

def review_closure(host,selection,current):
 need(set(selection)=={'review_package_binding','proposal_binding','target_package_binding','runtime_approval_binding','required_members','recognized_owners','channel_key'},'unauthorized','Closed independent review selection required.')
 review=host.document(selection['review_package_binding']);need(protocol(host,'review-package',review) and review['base_cut']==current,'stale-cut','Exact materialized review cut differs.')
 manifest=host.document(review['manifest_binding']);need(manifest['schema_version']=='lab-exact-review-materialization/v1-candidate' and manifest['base_cut']==current and manifest['proposal_binding']==selection['proposal_binding'],'invalid-contract','Actual reviewed material manifest/cut/proposal differs.')
 need(manifest['all_targets_materialized'] is True and manifest['atomicity_requirement']=='all-or-nothing' and manifest['human_checkpoint_count']==1 and manifest['actual_owner_outcome'] is None and manifest['runtime_activations']==0 and manifest['external_effect_refs']==[] and manifest['repository_admissions_applied']==0,'gate-required','Review scope is not an exact pending candidate package.')
 public=host.document(selection['proposal_binding']);need(protocol(host,'change-proposal',public) and public['base_cut']==current and public['scope_ref']==host.policy['scope_refs'][0],'invalid-contract','Actual original change proposal/cut/scope differs.')
 need(public['source_profile_binding']==binding((NATIVE/'profile.json').relative_to(ROOT).as_posix(),(NATIVE/'profile.json').read_bytes()),'integrity-failed','Exact proposal native profile differs.')
 host.material(public['workspace_binding'])
 native=host.document(selection['target_package_binding']);need(native['schema_version']==U.PROPOSAL_VERSION,'closure-missing','Native publication requires retained original target bytes.')
 need(public['connection_proposals']==[],'closure-missing','This independently selected native publication route requires relation targets in its complete immutable target package; additional connection proposals are not silently applied.')
 actual=host.store.review(native);cores=actual['decision_cores'];need(len(cores)==len(public['targets'])==len(manifest['targets'])==len(review['ordered_core_bindings']),'closure-missing','Independent target/core coverage differs.')
 data=host.snapshot();S.verify_approval(host.document(selection['runtime_approval_binding']),native,cores,data['config'])
 checkpoint=next((r for r in manifest['generated_carriers'] if r['artifact']==review['checkpoint']),None)
 bundle=next((r for r in manifest['generated_carriers'] if r['artifact']==review['decision_bundle']),None)
 need(checkpoint is not None and bundle is not None,'closure-missing','Actual generated checkpoint or bundle originals are absent.')
 cb,craw=record(host,checkpoint['object_binding'],'decision-checkpoint');bb,braw=record(host,bundle['object_binding'],'decision-bundle')
 for ref,body,raw in ((review['checkpoint'],cb,craw),(review['decision_bundle'],bb,braw)):
  need(ref['identity_ref']==body['node_id'] and ref['byte_sha256']==sha(raw) and ref['scope_ref']==body['scope_ref']==public['scope_ref'],'integrity-failed','Exact generated carrier header/body differs.')
 profile_rows=[r for r in host.policy['materials'] if r['ref']==review['workflow_decision_profile']['version_ref']]
 need(len(profile_rows)==1,'closure-missing','Materialized workflow decision profile is absent.')
 profile,praw=record(host,{k:profile_rows[0][k] for k in ('ref','sha256')},'workflow-decision-profile')
 need(sha(praw)==review['workflow_decision_profile']['byte_sha256'] and profile['node_id']==review['workflow_decision_profile']['identity_ref'],'integrity-failed','Exact selected workflow profile header differs.')
 q=profile['payload'];need(q['decision_mode']=='single' and q['exact_target_required'] is True and q['default_checkpoint_kind']=='final-review' and 'final-review' in q['allowed_checkpoint_kinds'],'gate-required','Actual workflow profile does not select one exact final review.')
 need(cb['owner_ref']==bb['owner_ref'] and cb['payload']['workflow_profile_ref']==review['workflow_decision_profile']['version_ref'] and cb['payload']['decision_bundle_ref']==bb['node_id'] and bb['payload']['checkpoint_ref']==cb['node_id'],'closure-missing','Profile/checkpoint/bundle closure differs.')
 ordered=bb['payload']['ordered_decisions'];need(len(ordered)==len(cores) and bb['payload']['bundle_digest']==sha(encoded(ordered)) and bb['payload']['all_targets_materialized'] is True and bb['payload']['atomicity_requirement']=='all-or-nothing','integrity-failed','Exact materialized bundle/order/digest differs.')
 need(manifest['ordered_core_bindings']==review['ordered_core_bindings'] and manifest['example_bindings']==review['example_bindings'],'closure-missing','Manifest core/example selection differs.')
 unique=[]
 for member in selection['required_members']:
  if member['core_binding'] not in unique:unique.append(member['core_binding'])
 need(unique==review['ordered_core_bindings'],'unauthorized','Independent required roster core order differs.')
 for i,(core,nt,t,mt,decision) in enumerate(zip(cores,native['targets'],public['targets'],manifest['targets'],ordered)):
  core_binding=review['ordered_core_bindings'][i];need(host.document(core_binding)==core,'integrity-failed','Independently recomputed stable Decision core differs.')
  raw=U.decode_content(nt['content']) if nt['operation']!='withdraw' else None
  need(t['artifact']['version_ref']==nt['version_ref'] and t['artifact']['carrier_ref']==nt['carrier_ref'] and t['operation']==nt['operation'] and t['decision_core_binding']==core_binding and mt['target']==t and mt['core_binding']==core_binding,'closure-missing','Public/native target/core/materialization differs.')
  need(t['artifact']['scope_ref']==public['scope_ref'],'unauthorized','Reviewed target namespace differs.')
  if nt['operation']=='admit':need(t['predecessor'] is None,'invalid-contract','Admission target names a predecessor.')
  else:
   prior=data['projection']['subjects'].get(nt['predecessor_ref']);need(prior is not None and t['predecessor']['version_ref']==nt['predecessor_ref'] and t['predecessor']['identity_ref']==prior['identity'] and t['predecessor']['byte_sha256']==prior['source']['sha256'],'closure-missing','Exact reviewed predecessor differs from native current preimage.')
  if raw is not None:
   need(host.material({'ref':t['content']['content_ref'],'sha256':t['content']['byte_sha256']})==raw and t['artifact']['byte_sha256']==sha(raw) and t['content']['size_bytes']==len(raw) and t['artifact']['identity_ref']==nt['record']['node_id'],'integrity-failed','Reviewed original target bytes/header differ.')
   host.material(t['candidate_binding']);need(mt['original_content_binding']=={'ref':t['content']['content_ref'],'sha256':sha(raw)},'closure-missing','Materialized target original binding differs.')
  need(decision['decision_ref']==core['decision_ref'] and decision['decision_core_sha256']==core_binding['sha256'] and decision['target_refs']==[nt['version_ref']] and decision['target_digests']==[{'target_ref':nt['version_ref'],'sha256':t['artifact']['byte_sha256']}] and decision['scope_ref']==public['scope_ref'] and decision['selected_outcome'] is None,'closure-missing','Actual bundle member/core/target closure differs.')
  members=[m for m in selection['required_members'] if m['core_binding']==core_binding];need(members and decision['owner_ref']==members[0]['owner_principal_ref'],'unauthorized','Bundle owner voice differs from independent roster.')
  for member in members:need(host.document(member['effect_binding'])==t,'unauthorized','Signed exact effect selection differs from materialized target.')
 for b in public['schema_bindings']+public['evidence_bindings']+review['validation_bindings']+review['example_bindings']+review['operational_instruction_bindings']:host.material(b)
 for b in review['validation_bindings']:
  report=host.document(b);need(protocol(host,'validation-report',report) and report['result']=='pass' and report['source_cut']==current and report['subject_binding']==selection['proposal_binding'],'gate-required','Exact reviewed validation report did not pass.')
 owners=recognition(host,selection)
 need(bb['owner_ref'] in {principal for principal,role in owners},'unauthorized','Materialized bundle accountable owner is not in the independently recognized required owner roster.')
 approval=host.document(selection['runtime_approval_binding']);signers=[o for o in selection['recognized_owners'] if o['role_ref']==data['config']['owner_ref'] and o['public_key_hex']==data['config']['public_key']]
 need(len(signers)==1 and instant(signers[0]['not_before'])<=instant(approval['approved_at'])<=now() and instant(approval['approved_at'])<instant(signers[0]['expires_at']),'unauthorized','Native runtime approval signer/time differs from independently recognized current owner.')
 responses=manifest['ordered_required_owner_responses'];need(len(responses)==len(selection['required_members']),'unauthorized','Materialized required owner response coverage differs.')
 for response,member in zip(responses,selection['required_members']):
  need(response['core_binding']==member['core_binding'] and response['owner_role_ref']==member['owner_role_ref'] and response['owner_principal']['identity_ref']==member['owner_principal_ref'] and response['selected_outcome'] is None,'unauthorized','Materialized required owner order differs.')
 return review,manifest,public,native,owners

def verify_checkpoint(host,message,current,*,accountable_caller_required=True):
 selected=host.policy['review_selection'];need(selected is not None and message['review_package_binding']==selected['review_package_binding'],'unauthorized','Checkpoint selects another privately provisioned review.')
 review,manifest,public,native,owners=review_closure(host,selected,current)
 if accountable_caller_required:
  bundle_row=next(r for r in manifest['generated_carriers'] if r['artifact']==review['decision_bundle']);bundle=host.document(bundle_row['object_binding'])
  need(host.policy['principal_ref']==bundle['owner_ref'],'unauthorized','Actual authenticated checkpoint caller differs from the materialized accountable bundle owner.')
 need(message['checkpoint_binding']==next(r['object_binding'] for r in manifest['generated_carriers'] if r['artifact']==review['checkpoint']),'integrity-failed','Checkpoint original binding differs from materialized carrier.')
 materials={r['ref']:host.material({'ref':r['ref'],'sha256':r['sha256']}) for r in host.policy['materials']}
 for b in [message['review_package_binding'],message['checkpoint_binding'],message['channel_verification_binding'],*[o['authorization_evidence_binding'] for o in message['ordered_outcomes']]]:materials[b['ref']]=host.material(b)
 return K.verify(message,materials=materials,required_members=selected['required_members'],owner_keys=owners,channel_key=selected['channel_key'],current_cut=current,now=now(),validate=lambda n,v:protocol(host,n,v))

def checkpoint_result(host,message,inner,current):
 observed=verify_checkpoint(host,message,current);ob=host.object(encoded(observed));authorized=observed['all_required_members_authorized']
 result={'schema_version':'lab-validation-report/v1-candidate','report_ref':'report:owned-checkpoint:'+sha(inner),'subject_binding':host.object(inner),'source_cut':current,'validator_binding':binding((HERE/'governance.py').relative_to(ROOT).as_posix(),(HERE/'governance.py').read_bytes()),'checks':[{'check_ref':'check:exact-recognized-channel-members','obligation_ref':'O-AUTHORITY','result':'pass','evidence_bindings':[ob,*observed['evidence_bindings']],'claim_ceiling':CEILING}],'reference_checks':[],'gaps':[],'result':'pass','claim_ceiling':CEILING+' All required exact effects authorized: '+str(authorized)+'. A valid rejection or deferral is a recorded outcome.','authority_effect':'none'}
 host.object(encoded(result));return result

def admission_preflight(host,message,current,key):
 need(message['authority_scope']=='operator-local','gate-required','Repository admission requires actual final R08 and is unavailable in this isolated publisher.')
 need(message['expected_cut']==current and message['idempotency_key']==key,'stale-cut','Exact native preimage or nested command key differs.')
 s=host.policy['review_selection'];need(s is not None and all(message[k]==s[k] for k in ('proposal_binding','target_package_binding','review_package_binding')),'unauthorized','Admission package differs from independent private selection.')
 resolution=host.document(message['resolution_binding']);need(protocol(host,'checkpoint-resolution',resolution),'invalid-contract','Original selected resolution schema differs.')
 observed=verify_checkpoint(host,resolution,current,accountable_caller_required=False);need(observed['all_required_members_authorized'],'gate-required','Every exact required member must actually authorize its selected local effect.')
 # Admission consumes a resolution actually recorded by this authenticated host.
 matched=False
 for path in (host.root/'operations').iterdir():
  if path.name.endswith('.governance-staging'):continue
  row=parse(private(path))
  if row['operation']=='checkpoint.resolve' and row.get('result') is not None and row['message_binding']==message['resolution_binding']:matched=True
 need(matched,'gate-required','Exact verified resolution has not been durably recorded by this selected host.')
 return host.document(s['target_package_binding']),host.document(s['runtime_approval_binding'])

def admission_result(host,message,inner,native,approval):
 host.guard();need(host.cut()==message['expected_cut'],'stale-cut','Native head changed before selected publication.')
 try:
  observed=host.store.apply(native,approval)
  data=host.snapshot();transaction=data['transactions'][-1]
  need(transaction['digest']==observed['transaction_digest'],'indeterminate','Native commit observation differs.')
  for target in native['targets']:
   if target['operation']!='withdraw':need(U.original_bytes(host.store,target['version_ref'],transaction['digest'])==U.decode_content(target['content']),'indeterminate','Committed original byte readback differs.')
  commit=host.object(encoded(transaction));post=host.cut(data)
  return {'schema_version':'lab-commit-receipt/v1-candidate','request_binding':binding(message['request_ref'],inner),'commit_binding':commit,'post_cut':post,'posture':'committed','output_bindings':[commit],'projection_posture':'pending','file_generation_posture':'not-selected','recovery_required':False,'gaps':[],'claim_ceiling':CEILING+' Actual exact signed candidate native transaction and target-byte readback observed.','authority_effect':'none'}
 except Exception as error:
  # The durable key is already pending: no exception can invite redispatch.
  raise Refusal('indeterminate','Selected native publication may have started; inspect the durable key and signed store without redispatch.') from error

def capability_preflight(host,channel,message,current):
 selected=host.policy['capability_selection'];need(selected is not None,'unauthorized','Independent capability selection unavailable.')
 need(message['source_cut']==current and all(message[k]==selected[k] for k in ('capability','binding','realization_refs','conformance_bindings','observation_contract_bindings','operational_scope_ref','authority_basis')),'unauthorized','Capability/realization/evidence/scope selection differs from independent host policy.')
 basis=selected['authority_basis'];need(basis['authority_scope']=='operator-local' and basis['owner_principal_ref']==channel.actor()['principal_ref'] and basis['scope_refs']==[message['operational_scope_ref']] and now()<instant(basis['expires_at'])<=instant(host.policy['expires_at']),'expired-authority','Independently scoped adoption preparation permission differs or expired.')
 for b in basis['evidence_bindings']+basis['policy_bindings']:host.material(b)
 def selected_record(header,kind,version='v1'):
  b={'ref':header['version_ref'],'sha256':header['byte_sha256']};body,raw=record(host,b,kind,version)
  need(body['node_id']==header['identity_ref'] and body['scope_ref']==header['scope_ref'] and header['carrier_ref']=='cal.artifact-type.'+kind+'/'+version,'integrity-failed','Exact selected capability header/body/carrier differs.');return body,raw
 capability,_=selected_record(message['capability'],'product-capability');realization,old=selected_record(message['binding'],'capability-realization-binding','v2')
 need(realization['capability_ref']==capability['node_id'] and realization['capability_version_ref']==message['capability']['version_ref'] and realization['binding_state']=='candidate' and realization['adoption_decision_ref'] is None,'closure-missing','Actual candidate realization binding does not bind this exact capability version.')
 implementations=[]
 for h in message['realization_refs']:
  impl,raw=selected_record(h,'implementation');need(capability['node_id'] in impl['payload']['realizes_capability_refs'],'closure-missing','Implementation does not realize selected capability.')
  need(any(r['realization_kind']=='implementation' and r['realization_ref']==h['version_ref'] for r in realization['realization_refs']),'closure-missing','Nonempty exact implementation realization binding is missing.');implementations.append(h)
 need(len(implementations)==len(realization['realization_refs']) and implementations,'closure-missing','Complete nonempty implementation binding coverage required.')
 for b in message['conformance_bindings']:
  report=host.document(b);need(protocol(host,'validation-report',report) and report['result']=='pass' and report['source_cut']==current and report['subject_binding']=={'ref':message['binding']['version_ref'],'sha256':sha(old)},'gate-required','Exact realization conformance evidence is missing, stale or failed.')
  need(any(c['check_ref']=='check:capability-implementation-original-schema' and c['result']=='pass' for c in report['checks']),'gate-required','Selected conformance does not cover exact implementation schemas.')
 for b in message['observation_contract_bindings']:
  contract=host.document(b);need(set(contract)=={'schema_version','capability','binding','implementations','operational_scope_ref','source_cut','usefulness_claimed','activation_allowed','authority_effect'} and contract['schema_version']=='lab-owned-capability-observation-contract/v1-candidate' and contract['capability']==message['capability'] and contract['binding']==message['binding'] and contract['implementations']==implementations and contract['operational_scope_ref']==message['operational_scope_ref'] and contract['source_cut']==current and contract['usefulness_claimed'] is False and contract['activation_allowed'] is False and contract['authority_effect']=='none','closure-missing','Actual observation contract does not bind exact capability/implementations/scope/cut.')
 return realization,old,implementations

def capability_result(host,channel,message,inner,key,current):
 realization,old,implementations=capability_preflight(host,channel,message,current)
 basis=message['authority_basis']
 proposed=copy.deepcopy(realization);proposed['binding_version']='2.0.0-candidate.owned-'+sha(inner)[:16];proposed['conformance_refs']=[b['ref'] for b in message['conformance_bindings']];proposed['observation_refs']=[b['ref'] for b in message['observation_contract_bindings']]
 schema_path=ROOT/'authority/artifact-types/capability-realization-binding/v2/schema.json';schema_raw=schema_path.read_bytes();need(Draft202012Validator(parse(schema_raw),format_checker=FormatChecker()).is_valid(proposed),'invalid-contract','Exact prepared binding violates original artifact schema.')
 raw=encoded(proposed);body=host.object(raw);version=proposed['node_id']+'@'+proposed['binding_version'];header={'scope_ref':proposed['scope_ref'],'identity_ref':proposed['node_id'],'version_ref':version,'carrier_ref':message['binding']['carrier_ref'],'byte_sha256':sha(raw),'candidate_contract_binding':binding(schema_path.relative_to(ROOT).as_posix(),schema_raw)}
 core={'decision_ref':'decision:owned-capability:'+sha(inner),'category':'artifact-instance','operation':'revise','version_ref':version,'target_digest':C.digest(proposed)};cb=host.object(encoded(core));metadata=host.object(encoded({'schema_version':'lab-candidate-target-metadata/v1-candidate','category':'artifact-instance','decision_ref':core['decision_ref'],'contract':None}))
 declaration=host.object(encoded({'schema_version':'lab-owned-capability-adoption-declaration/v1-candidate','capability':message['capability'],'binding':header,'realization_refs':implementations,'operational_scope_ref':message['operational_scope_ref'],'authority_basis':basis,'conformance_bindings':message['conformance_bindings'],'observation_contract_bindings':message['observation_contract_bindings'],'posture':'candidate-prepared','actual_adoption':False,'usefulness_observed':False,'runtime_activations':0,'external_effect_refs':[],'authority_effect':'none','claim_ceiling':CEILING}))
 return {'schema_version':'lab-change-proposal/v1-candidate','proposal_ref':'proposal:owned-capability:'+sha(inner),'actor':channel.actor(),'scope_ref':host.policy['scope_refs'][0],'base_cut':current,'source_profile_binding':binding((NATIVE/'profile.json').relative_to(ROOT).as_posix(),(NATIVE/'profile.json').read_bytes()),'workspace_binding':binding('owned-governance-policy',private(host.policy_path)),'targets':[{'operation':'revise','artifact':header,'predecessor':message['binding'],'content':{'content_ref':body['ref'],'byte_sha256':sha(raw),'size_bytes':len(raw),'media_type':'application/json'},'candidate_binding':metadata,'requested_effect':'Candidate exact owner-local capability binding/adoption declaration; independent admission and operational action still required.','decision_core_binding':cb}],'schema_bindings':[binding(schema_path.relative_to(ROOT).as_posix(),schema_raw)],'connection_proposals':[],'evidence_bindings':[declaration,*message['conformance_bindings'],*message['observation_contract_bindings']],'idempotency_key':key,'challenge_route':realization['challenge_route'],'authority_effect':'none'}
