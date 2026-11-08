"""Pure verification from independently selected original bytes; no effect grant.

Every trust/selection binding is supplied by the trusted coordinator, separately
from ingress. This unit ships only a technical-fixture enrollment. Actual G07
host/role/currentness and replay custody are deliberately unavailable.
"""
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft202012Validator
from .contracts import *

class Capture:
    def __init__(self,reader):self.reader=reader;self.originals={};self.total=0
    def raw(self,b):
        binding(b);key=canonical(b)
        if key not in self.originals:
            need(len(self.originals)<1024 and self.total+b['size_bytes']<=256*LIMIT,'CAPTURE_BOUND')
            raw=self.reader.read(b,max_bytes=MEMBER_LIMIT);self.total+=len(raw);self.originals[key]=(b,raw)
        return self.originals[key][1]
    def finish(self):
        for b,raw in self.originals.values():
            need(self.reader.read(b,max_bytes=MEMBER_LIMIT)==raw,'ORIGINAL_CHANGED_DURING_VERIFY')
    def load(self,b):
        binding(b);need(b['size_bytes']<=LIMIT,'CONTROL_ENVELOPE_BOUND')
        return parse(self.raw(b),max_bytes=LIMIT)


def signed(capture,b,issuer):
    e=capture.load(b);envelope(e)
    need(e['issuer_ref']==issuer['issuer_ref'],'ISSUER_NOT_ENROLLED')
    try:Ed25519PublicKey.from_public_bytes(hexbytes(issuer['public_key'],32)).verify(hexbytes(e['signature'],64),signing(e))
    except (InvalidSignature,ValueError):raise Refusal('SIGNATURE_INVALID') from None
    return e['payload']


def native(capture,b,schema_binding):
    value=capture.load(b);schema=capture.load(schema_binding)
    # These exact original schemas are standalone. Remote/ref resolution is not
    # an allowed fallback; changes require a separately reviewed adapter.
    def no_ref(v):
        if isinstance(v,dict):
            need('$ref' not in v and '$dynamicRef' not in v,'NATIVE_SCHEMA_REFERENCE')
            for x in v.values():no_ref(x)
        elif isinstance(v,list):
            for x in v:no_ref(x)
    no_ref(schema)
    need(Draft202012Validator(schema).is_valid(value),'NATIVE_SCHEMA')
    return value


def verify_owner(c,inputs,owner_row,review,review_binding,trust,operation,now):
    need(inputs['owner_id']==owner_row['owner_id'] and inputs['principal_ref']==owner_row['principal_ref'],'OWNER_INPUT_IDENTITY')
    host=trust['issuers']['host'];role_issuer=trust['issuers']['role']
    presentation=signed(c,inputs['presentation_binding'],host)
    fields(presentation,'lab-owner-presentation/v2',['mechanism_ref','principal_ref','session_id','event_id','nonce','review_binding','material_bindings','presented_at'])
    for k in ['mechanism_ref','principal_ref','session_id','event_id','nonce']:text(presentation[k])
    integer(presentation['presented_at']);bindings(presentation['material_bindings'])
    need(presentation['mechanism_ref']==trust['host_mechanism'] and presentation['principal_ref']==owner_row['principal_ref'],'PRESENTATION_IDENTITY')
    need(presentation['review_binding']==review_binding and presentation['material_bindings']==review['material_bindings'],'PRESENTED_BYTES')
    role=signed(c,inputs['role_attestation_binding'],role_issuer)
    fields(role,'lab-owner-role-attestation/v2',['registry_ref','registry_cursor','principal_ref','assignee_ref','role_ref','boundary_ref','scope_ref',
        'assignment_binding','role_binding','boundary_binding','correspondence_binding','revocation_binding','period','boundary_period_text','effective_period_resolution','effect_kinds'])
    for k in ['registry_ref','registry_cursor','principal_ref','assignee_ref','role_ref','boundary_ref','scope_ref','boundary_period_text']:text(role[k])
    strings(role['effect_kinds']);active(role['period'],now)
    need(role['registry_ref']==trust['role_registry'] and role['registry_cursor']==trust['registry_cursor'],'ROLE_REGISTRY_CURRENTNESS')
    for k in ['principal_ref','assignee_ref','role_ref','boundary_ref','scope_ref']:need(role[k]==owner_row[k],'ROLE_OWNER_JOIN')
    assignment=native(c,role['assignment_binding'],trust['native_schemas']['assignment'])
    original_role=native(c,role['role_binding'],trust['native_schemas']['role'])
    boundary=native(c,role['boundary_binding'],trust['native_schemas']['boundary'])
    correspondence=c.load(role['correspondence_binding'])
    fields(correspondence,'lab-principal-assignee-resolution/v2',['registry_ref','registry_cursor','principal_ref','assignee_ref','assignee_kind','basis_bindings','period'])
    for k in ['registry_ref','registry_cursor','principal_ref','assignee_ref']:need(correspondence[k]==role[k],'PRINCIPAL_ASSIGNEE_JOIN')
    need(correspondence['assignee_kind']==assignment['assignee_kind'],'ASSIGNEE_KIND')
    bindings(correspondence['basis_bindings']);active(correspondence['period'],now)
    for b in correspondence['basis_bindings']:c.raw(b)
    need(assignment['assignee_ref']==role['assignee_ref'] and assignment['role_ref']==original_role['node_id']==role['role_ref'] and
         original_role['authority_boundary']==boundary['node_id']==role['boundary_ref'],'ORIGINAL_ROLE_JOIN')
    need(assignment['assignment_state']=='active' and original_role['lifecycle_state']=='active' and boundary['lifecycle_state']=='active','ORIGINAL_ROLE_STATE')
    need(assignment['scope_ref']==original_role['scope_ref']==boundary['scope_ref']==role['scope_ref'],'ORIGINAL_SCOPE')
    start=timestamp(assignment['period']['start'])
    end=assignment['period']['end']
    need(start<=role['period']['start'] and (end is None or role['period']['end']<=timestamp(end)),'ASSIGNMENT_PERIOD')
    payload=boundary['payload']
    need(payload['accountable_principal_ref']==role['principal_ref'] and payload['owner_role_ref']==role['role_ref'] and payload['authority_scope_ref']==role['scope_ref'],'BOUNDARY_JOIN')
    need(payload['revocation_state']=='not-revoked','BOUNDARY_REVOKED')
    needed=set(e for row in review['targets'] if row['target_ref'] in owner_row['target_refs'] for e in row['effect_kinds'])
    need(needed<=set(role['effect_kinds'])<=set(payload['allowed_effect_kinds']) and not needed.intersection(payload['excluded_effect_kinds']),'EFFECT_BOUNDARY')
    need(role['boundary_period_text']==payload['effective_period'],'NATIVE_PERIOD_TEXT')
    resolution=role['effective_period_resolution']
    closed(resolution,['kind','period','review_core_sha256'])
    active(resolution['period'],now)
    need(resolution['period']['start']<=role['period']['start']<role['period']['end']<=resolution['period']['end'],'BOUNDARY_PERIOD')
    if resolution['kind']=='exact-review':
        need(resolution['review_core_sha256']==sha(canonical(review)) and payload['effective_period']=='exact-review:'+resolution['review_core_sha256'],'EXACT_REVIEW_PERIOD')
    else:
        need(resolution['kind']=='authoritative-period-resolution' and resolution['review_core_sha256'] is None,'PERIOD_RESOLUTION')
        # Meaning of the original opaque period is attested by the separately
        # enrolled role authority. It is never inferred from key possession.
    revocation=c.load(role['revocation_binding'])
    fields(revocation,'lab-owner-current-revocation/v2',['registry_ref','registry_cursor','assignment_ref','role_ref','boundary_ref','state','checked_at','valid_until','basis_bindings'])
    need(revocation['registry_ref']==role['registry_ref'] and revocation['registry_cursor']==role['registry_cursor'] and revocation['assignment_ref']==assignment['node_id'] and revocation['role_ref']==role['role_ref'] and revocation['boundary_ref']==role['boundary_ref'],'REVOCATION_JOIN')
    need(revocation['state']=='not-revoked','REVOKED');integer(revocation['checked_at']);integer(revocation['valid_until'])
    need(revocation['checked_at']<=now<revocation['valid_until'] and now-revocation['checked_at']<=trust['max_age_seconds'],'REVOCATION_STALE')
    bindings(revocation['basis_bindings'])
    for b in revocation['basis_bindings']:c.raw(b)
    disposition=signed(c,inputs['disposition_binding'],host)
    fields(disposition,'lab-owner-disposition/v2',['mechanism_ref','principal_ref','session_id','event_id','presentation_binding','role_attestation_binding','review_binding','material_bindings','target_refs','scope_ref','outcome','message_binding','recorded_at','operation_id'])
    for k in ['mechanism_ref','principal_ref','session_id','event_id','scope_ref','outcome','operation_id']:text(disposition[k])
    need(disposition['mechanism_ref']==trust['host_mechanism'] and disposition['principal_ref']==owner_row['principal_ref'] and disposition['session_id']==presentation['session_id'],'DISPOSITION_IDENTITY')
    need(disposition['presentation_binding']==inputs['presentation_binding'] and disposition['role_attestation_binding']==inputs['role_attestation_binding'] and disposition['review_binding']==review_binding and disposition['material_bindings']==review['material_bindings'],'DISPOSITION_DISPLAY_CHAIN')
    need(disposition['target_refs']==owner_row['target_refs'] and disposition['scope_ref']==owner_row['scope_ref'] and disposition['operation_id']==operation,'DISPOSITION_SCOPE')
    need(disposition['outcome'] in OUTCOMES,'DISPOSITION_OUTCOME');c.raw(disposition['message_binding']);integer(disposition['recorded_at'])
    shown=presentation['presented_at'];spoken=disposition['recorded_at']
    need(shown<=spoken<=now and now-shown<=trust['max_age_seconds'],'PRESENTATION_STALE')
    for t in [shown,spoken]:
        active(role['period'],t);active(correspondence['period'],t);active(resolution['period'],t)
    return {'owner_id':owner_row['owner_id'],'principal_ref':owner_row['principal_ref'],'outcome':disposition['outcome'],
            'disposition_binding':inputs['disposition_binding'],'host_event':{'host_issuer':host['issuer_ref'],'mechanism_ref':trust['host_mechanism'],'event_id':disposition['event_id']},
            'presentation_event':{'host_issuer':host['issuer_ref'],'mechanism_ref':trust['host_mechanism'],'event_id':presentation['event_id'],'nonce':presentation['nonce']},
            'target_refs':owner_row['target_refs']}


def verify_fixture(reader,expected_enrollment,expected_selection,*,now):
    """Caller is the separately trusted fixture coordinator, never request data.

    Result is a reproducible fixture observation, never an execution permit.
    Reinvoke against fresh independently selected originals at every later
    verification boundary; earlier output cannot substitute for current checks.
    """
    integer(now);c=Capture(reader);trust=c.load(expected_enrollment);enrollment(trust)
    selected=c.load(expected_selection);selection(selected)
    core=signed(c,selected['review_binding'],trust['issuers']['review']);review(core)
    need(core==selected['review_core'],'CURRENT_REVIEW_SELECTION')
    for key in ['source_binding','profile_binding','environment_binding','base_binding']:c.raw(core[key])
    for b in core['material_bindings']+core['evidence_bindings']:c.raw(b)
    for row in core['targets']:c.raw(row['member_binding'])
    owners={r['owner_id']:r for r in selected['owner_inputs']}
    need(set(owners)=={r['owner_id'] for r in core['owner_matrix']},'OWNER_INPUT_COVERAGE')
    results=[verify_owner(c,owners[row['owner_id']],row,core,selected['review_binding'],trust,selected['operation_id'],now) for row in core['owner_matrix']]
    events=[canonical(r['host_event']) for r in results]+[canonical({k:r['presentation_event'][k] for k in ['host_issuer','mechanism_ref','event_id']}) for r in results]
    need(len(events)==len(set(events)),'DUPLICATE_HOST_EVENT')
    nonces=[canonical({k:r['presentation_event'][k] for k in ['host_issuer','mechanism_ref','nonce']}) for r in results]
    need(len(nonces)==len(set(nonces)),'DUPLICATE_PRESENTATION_NONCE')
    supported={'approve','reject','revise','defer'} if selected['disposition_profile']=='c07-v1' else {'approve','reject','defer','stop'}
    for row in results:
        row['profile_supported']=row['outcome'] in supported
        row['profile_status']='supported-observation' if row['profile_supported'] else 'unsupported-nonpositive-gated'
    effect_ok=False
    if selected['effect_authorization_binding'] is not None:
        effect=signed(c,selected['effect_authorization_binding'],trust['issuers']['effect'])
        fields(effect,'lab-owner-effect-authorization/v2',['operation_id','review_binding','target_bindings','positive_disposition_bindings','operator_permission_bindings','period'])
        active(effect['period'],now)
        need(effect['operation_id']==selected['operation_id'] and effect['review_binding']==selected['review_binding'] and effect['target_bindings']==core['targets'],'EFFECT_EXACT_TARGET')
        need(all(r['outcome']=='approve' for r in results),'POSITIVE_DISPOSITIONS_ABSENT')
        need(effect['positive_disposition_bindings']==[r['disposition_binding'] for r in results],'POSITIVE_DISPOSITION_COVERAGE')
        need(effect['operator_permission_bindings']==selected['operator_permission_bindings'],'OPERATOR_SELECTION')
        permission_kinds=[]
        for b in selected['operator_permission_bindings']:
            p=signed(c,b,trust['issuers']['effect'])
            fields(p,'lab-owner-operator-permission/v2',['operation_id','review_binding','target_bindings','period','permission_kind'])
            text(p['permission_kind']);need(p['permission_kind'] in {'operator','release'},'PERMISSION_KIND');active(p['period'],now);permission_kinds.append(p['permission_kind'])
            need(p['operation_id']==selected['operation_id'] and p['review_binding']==selected['review_binding'] and p['target_bindings']==core['targets'],'OPERATOR_SCOPE')
        need(len(permission_kinds)==len(set(permission_kinds)) and set(permission_kinds)==set(core['required_permission_kinds']),'REQUIRED_OPERATOR_PERMISSION')
        effect_ok=True
    else:need(not selected['operator_permission_bindings'],'UNUSED_OPERATOR_PERMISSION')
    result={'schema_version':'lab-owner-fixture-verification/v2','usage':'technical-fixture','authority_effect':'none','actual_effect_authorized':False,
            'operation_id':selected['operation_id'],'review_binding':selected['review_binding'],'selection_binding':expected_selection,'enrollment_binding':expected_enrollment,
            'observed_at':now,'disposition_profile':selected['disposition_profile'],'owner_results':results,'positive_effect_contract_verified':effect_ok,
            'original_bindings':[b for b,_ in c.originals.values()]}
    c.finish()
    return result


def verify_actual(*args,**kwargs):
    # A role/key/message flag cannot manufacture independently trusted actual
    # host functionality, current role interpretation or broker replay custody.
    raise Refusal('ACTUAL_G07_HOST_ROLE_REPLAY_PROVIDER_REQUIRED')
