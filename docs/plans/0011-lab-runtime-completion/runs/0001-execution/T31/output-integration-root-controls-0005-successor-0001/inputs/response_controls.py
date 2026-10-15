"""Authored inert signature/domain checks, no actual role/producer permission."""
import base64,copy,hashlib,importlib.util,json,sys,types
from pathlib import Path
HERE=Path(__file__).absolute().parent;POST=HERE/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'
def main():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
    pkg='_T31_v5_OWNED_INERT_response';parent=types.ModuleType(pkg);parent.__path__=[str(HERE/'pure')];sys.modules[pkg]=parent
    def load(leaf,path):
        spec=importlib.util.spec_from_file_location(pkg+'.'+leaf,path);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
    P=load('protocol',HERE/'pure/protocol.py');load('workflow_output_contracts',POST/'workflow_output_contracts.py');R=load('workflow_response_contract',POST/'workflow_response_contract.py')
    key=Ed25519PrivateKey.generate();public=base64.b64encode(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode();raw=b'{"OWNED-INERT-actual-input":true}\n'
    fields={'schema_version':'lab-authenticated-challenge-response-input/v1-candidate','policy_binding':{'ref':'OWNED-INERT:policy','sha256':'1'*64},'response_sha256':hashlib.sha256(raw).hexdigest(),'run_binding':{'ref':'OWNED-INERT:run','sha256':'2'*64},'work_ref':'OWNED-INERT:work@1','source_cut':{'OWNED-INERT':True},'eligible_invocation_ref':'OWNED-INERT:eligible'}
    selected={k:fields[k]for k in ('policy_binding','run_binding','work_ref','source_cut','eligible_invocation_ref')};signed=dict(fields,signature_base64=base64.b64encode(key.sign(P.compact(fields))).decode());encoded=P.compact(signed)
    assert R.authenticate_response(raw,encoded,public_key=public,**selected)[0]==json.loads(raw);checks=['owned inert signed response bytes join exact preselected phase input domain']
    for field in selected:
        changed=copy.deepcopy(selected);changed[field]={'OWNED-INERT:other':True}if type(selected[field])is dict else 'OWNED-INERT:other'
        try:R.authenticate_response(raw,encoded,public_key=public,**changed)
        except ValueError:checks.append('authenticated response rejects different '+field)
        else:raise AssertionError(field)
    for body,proof in [(raw+b' ',encoded),(raw,P.compact(dict(signed,signature_base64=base64.b64encode(b'0'*64).decode())))]:
        try:R.authenticate_response(body,proof,public_key=public,**selected)
        except Exception:checks.append('changed exact input/signature refuses before producer')
        else:raise AssertionError('changed response accepted')
    # Exact original gate signer recognition: a valid unrelated-key signature
    # still cannot represent this current Principal.
    from datetime import datetime,timedelta,timezone
    principal={'kind':'principal','node_id':'OWNED-INERT:principal','scope_ref':'OWNED-INERT:scope','payload':{'status':'active','stable_subject_ref':'ed25519-public-key-sha256:'+hashlib.sha256(base64.b64decode(public)).hexdigest(),'recognition_boundary_refs':['OWNED-INERT:boundary@1']}}
    assert R.recognize_signer(public,principal,principal['node_id'],principal['scope_ref'])
    unrelated=Ed25519PrivateKey.generate();other_public=base64.b64encode(unrelated.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode();other_signed=P.compact(dict(fields,signature_base64=base64.b64encode(unrelated.sign(P.compact(fields))).decode()))
    R.authenticate_response(raw,other_signed,public_key=other_public,**selected)
    try:R.recognize_signer(other_public,principal,principal['node_id'],principal['scope_ref'])
    except ValueError:checks.append('valid signature under unrelated policy key is not recognized by actual current Principal')
    else:raise AssertionError('unrelated signer recognized')
    def header(ref):return {'scope_ref':'OWNED-INERT:scope','identity_ref':ref,'version_ref':ref+'@1','carrier_ref':'OWNED-INERT:carrier','byte_sha256':'a'*64}
    actual_now=datetime.now(timezone.utc);start=(actual_now-timedelta(minutes=1)).isoformat();end=(actual_now+timedelta(minutes=1)).isoformat();parse_time=lambda v:datetime.fromisoformat(v)
    selection={k:header('OWNED-INERT:'+k)for k in ('principal','role_assignment','role','authority_boundary','assignee','challenge_contract','subject')}
    selection['principal']=header('OWNED-INERT:principal');selection['authority_boundary']=header('OWNED-INERT:boundary');selection['person_reference']=selection['assignee']
    selection.update(schema_version='lab-private-original-response-authority/v1-candidate',assignee_kind='person-reference',owner_route='OWNED-INERT:owner-route',scope_ref='OWNED-INERT:scope',source_cut={'OWNED-INERT':True},work_ref='OWNED-INERT:work@1',run_binding={'ref':'OWNED-INERT:run','sha256':'b'*64},response_effect_ref='OWNED-INERT:respond',role_function_ref='OWNED-INERT:response-function',boundary_period_ref='OWNED-INERT:period',boundary_not_before=start,boundary_expires_at=end,principal_assignee_correspondence='person-reference-stable-subject/v1-candidate',team_membership=None,assignee_use_ref='OWNED-INERT:response-use',permitted_phase_effects=['capture-one-authenticated-responded-candidate'],authority_effect='none',actual_owner_outcome=None)
    grant={k:copy.deepcopy(selection[k])for k in ('owner_route','scope_ref','source_cut','work_ref','run_binding','role_assignment','challenge_contract','subject')};grant.update(owner_principal=selection['principal'],role_ref=selection['role']['version_ref'],expires_at=end)
    role={'node_id':selection['role']['identity_ref'],'scope_ref':selection['scope_ref'],'lifecycle_state':'active','authority_boundary':selection['authority_boundary']['version_ref'],'functions':[selection['role_function_ref']]}
    assignment={'node_id':selection['role_assignment']['identity_ref'],'scope_ref':selection['scope_ref'],'assignment_state':'active','assignee_kind':'person-reference','assignee_ref':selection['assignee']['version_ref'],'role_ref':grant['role_ref']}
    boundary={'node_id':selection['authority_boundary']['identity_ref'],'scope_ref':selection['scope_ref'],'lifecycle_state':'active','payload':{'owner_role_ref':grant['role_ref'],'accountable_principal_ref':principal['node_id'],'authority_scope_ref':selection['scope_ref'],'allowed_effect_kinds':[selection['response_effect_ref']],'excluded_effect_kinds':[],'revocation_state':'not-revoked','effective_period':selection['boundary_period_ref']}}
    assignee={'kind':'person-reference','node_id':selection['assignee']['identity_ref'],'scope_ref':selection['scope_ref'],'lifecycle_state':'active','reference_value':principal['payload']['stable_subject_ref'],'permitted_uses':[selection['assignee_use_ref']],'prohibited_uses':[]}
    contract={'node_id':selection['challenge_contract']['identity_ref'],'scope_ref':selection['scope_ref'],'payload':{'owner_route':selection['owner_route']}}
    bodies={'principal':principal,'assignment':assignment,'role':role,'boundary':boundary,'assignee':assignee,'person':assignee,'membership':None,'contract':contract}
    R.response_authority(selection,grant,**bodies,now=actual_now,instant=parse_time);checks.append('explicit private response interpretation joins original Role Assignment Boundary Principal assignee Contract and actual period metadata')
    for field,changed in [('role',dict(role,node_id='OWNED-INERT:unrelated-role')),('contract',dict(contract,payload={'owner_route':'OWNED-INERT:unrelated-route'})),('boundary',dict(boundary,payload=dict(boundary['payload'],accountable_principal_ref='OWNED-INERT:other-principal'))),('person',dict(assignee,reference_value='OWNED-INERT:other-subject'))]:
        altered=dict(bodies);altered[field]=changed
        try:R.response_authority(selection,grant,**altered,now=actual_now,instant=parse_time)
        except ValueError:checks.append('response authority refuses unrelated '+field+' correspondence before output')
        else:raise AssertionError(field)
    team_selection=copy.deepcopy(selection);team_selection.update(assignee=header('OWNED-INERT:team'),assignee_kind='team',team_membership=header('OWNED-INERT:membership'))
    team={'kind':'team','node_id':team_selection['assignee']['identity_ref'],'scope_ref':selection['scope_ref'],'lifecycle_state':'active'}
    membership={'node_id':team_selection['team_membership']['identity_ref'],'scope_ref':selection['scope_ref'],'membership_state':'active','person_reference_ref':selection['person_reference']['version_ref'],'team_ref':team_selection['assignee']['version_ref'],'period':{'start':start,'end':end}}
    team_assignment=dict(assignment,assignee_kind='team',assignee_ref=team_selection['assignee']['version_ref']);team_bodies=dict(bodies,assignment=team_assignment,assignee=team,membership=membership)
    R.response_authority(team_selection,grant,**team_bodies,now=actual_now,instant=parse_time);checks.append('actual original TeamMembership correspondence metadata joins person team principal and real period')
    for key,value in [('team_ref','OWNED-INERT:foreign-team'),('person_reference_ref','OWNED-INERT:foreign-person'),('membership_state','inactive'),('period',{'start':start,'end':start})]:
        altered=dict(team_bodies,membership=dict(membership,**{key:value}))
        try:R.response_authority(team_selection,grant,**altered,now=actual_now,instant=parse_time)
        except ValueError:checks.append('team authority refuses foreign/inactive/stale '+key)
        else:raise AssertionError(key)
    for key,value in [('allowed_effect_kinds',[]),('excluded_effect_kinds',[selection['response_effect_ref']]),('revocation_state','revoked')]:
        altered=dict(bodies,boundary=dict(boundary,payload=dict(boundary['payload'],**{key:value})))
        try:R.response_authority(selection,grant,**altered,now=actual_now,instant=parse_time)
        except ValueError:checks.append('actual AuthorityBoundary refuses denied/revoked '+key)
        else:raise AssertionError(key)
    return checks
