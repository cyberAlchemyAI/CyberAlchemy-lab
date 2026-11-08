"""Pure authenticated response-input proof; no producer/API effect or grant."""
import base64
from .workflow_output_contracts import need,closed,parse,sha
from .protocol import compact

def authenticate_response(response_raw,signature_raw,*,public_key,policy_binding,run_binding,work_ref,source_cut,eligible_invocation_ref):
    proof=parse(signature_raw)
    closed(proof,('schema_version','policy_binding','response_sha256','run_binding','work_ref','source_cut','eligible_invocation_ref','signature_base64'))
    need(proof['schema_version']=='lab-authenticated-challenge-response-input/v1-candidate' and proof['policy_binding']==policy_binding and proof['response_sha256']==sha(response_raw) and proof['run_binding']==run_binding and proof['work_ref']==work_ref and proof['source_cut']==source_cut and proof['eligible_invocation_ref']==eligible_invocation_ref,'actual response signature input lineage differs')
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    payload={k:v for k,v in proof.items() if k!='signature_base64'}
    Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key,validate=True)).verify(base64.b64decode(proof['signature_base64'],validate=True),compact(payload))
    return parse(response_raw),proof


def recognize_signer(public_key,principal,principal_ref,scope_ref):
    """Exact original v6 gate signer/current Principal condition, no delegation."""
    import hashlib
    public=base64.b64decode(public_key,validate=True)
    need(len(public)==32 and principal['kind']=='principal' and principal['node_id']==principal_ref
         and principal['scope_ref']==scope_ref and principal['payload']['status']=='active'
         and principal['payload']['stable_subject_ref']=='ed25519-public-key-sha256:'+hashlib.sha256(public).hexdigest(),
         'selected response signer not recognized by exact current Principal')
    return public


def response_authority(selection,grant,*,principal,assignment,role,boundary,assignee,person,membership,contract,now,instant):
    """A selected private phase interpretation needs every actual original join.

    These source records are necessary evidence. They do not themselves create
    permission: the independently selected private authority contract and fresh
    phase permission remain mandatory. No role is inferred from a route string.
    """
    fields=('schema_version','principal','role_assignment','role','authority_boundary','assignee','assignee_kind',
            'challenge_contract','subject','owner_route','scope_ref','source_cut','work_ref','run_binding',
            'response_effect_ref','role_function_ref','boundary_period_ref','boundary_not_before','boundary_expires_at','principal_assignee_correspondence','person_reference','team_membership','assignee_use_ref',
            'permitted_phase_effects','authority_effect','actual_owner_outcome')
    closed(selection,fields);p=selection
    need(p['schema_version']=='lab-private-original-response-authority/v1-candidate' and p['authority_effect']=='none'
         and p['actual_owner_outcome']is None and p['permitted_phase_effects']==['capture-one-authenticated-responded-candidate'],
         'explicit independently selected response authority contract required')
    for field,key in [('principal','owner_principal'),('role_assignment','role_assignment'),('challenge_contract','challenge_contract'),
                      ('subject','subject'),('owner_route','owner_route'),('scope_ref','scope_ref'),('source_cut','source_cut'),
                      ('work_ref','work_ref'),('run_binding','run_binding')]:
        need(p[field]==grant[key],'response authority differs from exact phase: '+field)
    for name,body in [('principal',principal),('role_assignment',assignment),('role',role),('authority_boundary',boundary),('assignee',assignee),('challenge_contract',contract)]:
        need(body['node_id']==p[name]['identity_ref'] and body['scope_ref']==p[name]['scope_ref'],'original authority header/body identity differs: '+name)
    scope=grant['scope_ref'];owner=principal['node_id'];role_refs=(role['node_id'],p['role']['version_ref']);boundary_refs=(boundary['node_id'],p['authority_boundary']['version_ref'])
    need(principal['payload']['status']=='active' and assignment['assignment_state']=='active'
         and role['lifecycle_state']=='active' and boundary['lifecycle_state']=='active'
         and assignee['lifecycle_state']=='active','actual response authority records inactive')
    need(assignment['assignee_kind']==p['assignee_kind']==assignee['kind'] and p['assignee_kind']in('person-reference','team')
         and assignment['assignee_ref']in(assignee['node_id'],p['assignee']['version_ref']),
         'original RoleAssignment assignee correspondence differs')
    need(p['principal_assignee_correspondence']=='person-reference-stable-subject/v1-candidate' and person['kind']=='person-reference'
         and person['node_id']==p['person_reference']['identity_ref'] and person['scope_ref']==scope
         and person['lifecycle_state']=='active' and person['reference_value']==principal['payload']['stable_subject_ref']
         and p['assignee_use_ref']in person['permitted_uses'] and p['assignee_use_ref']not in person['prohibited_uses'],
         'current Source does not recognize exact Principal/assignee subject and permitted use')
    if p['assignee_kind']=='person-reference':
        need(p['assignee']==p['person_reference'] and p['team_membership']is None and membership is None,'direct assignee correspondence differs')
    else:
        need(type(membership)is dict and p['team_membership']is not None and membership['node_id']==p['team_membership']['identity_ref']
             and membership['scope_ref']==scope and membership['membership_state']=='active'
             and membership['person_reference_ref']in(person['node_id'],p['person_reference']['version_ref'])
             and membership['team_ref']in(assignee['node_id'],p['assignee']['version_ref'])
             and instant(membership['period']['start'])<=now and(membership['period']['end']is None or now<instant(membership['period']['end'])),
             'actual original team membership/period does not recognize this Principal')
    need(assignment['role_ref']==grant['role_ref'] and assignment['role_ref']in role_refs
         and role['authority_boundary']in boundary_refs and boundary['payload']['owner_role_ref']in role_refs,
         'actual selected Role/RoleAssignment/AuthorityBoundary join differs')
    need(boundary['payload']['accountable_principal_ref']in(owner,p['principal']['version_ref'])
         and any(ref in principal['payload']['recognition_boundary_refs']for ref in boundary_refs),
         'current Principal does not recognize this actual authority boundary')
    need(all(body['scope_ref']==scope for body in (principal,assignment,role,boundary,assignee,contract))
         and boundary['payload']['authority_scope_ref']==scope and contract['payload']['owner_route']==p['owner_route'],
         'actual original response authority scope/Contract route differs')
    need(p['role_function_ref']in role['functions'] and p['response_effect_ref']in boundary['payload']['allowed_effect_kinds']
         and p['response_effect_ref']not in boundary['payload']['excluded_effect_kinds']
         and boundary['payload']['revocation_state']=='not-revoked',
         'selected actual Role/boundary denies response effect or is revoked')
    need(boundary['payload']['effective_period']==p['boundary_period_ref']
         and instant(p['boundary_not_before'])<=now<instant(p['boundary_expires_at'])<=instant(grant['expires_at']),
         'independently interpreted original response boundary period absent/expired')
    return p
