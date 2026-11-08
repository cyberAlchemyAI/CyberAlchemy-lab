"""Closed bounded C07 envelopes. No payload can supply its own issuer trust."""
import re
from datetime import datetime, timezone
from lab_contracts.codec import canonical, parse, need, closed, sha, Refusal
from lab_contracts.validation import validate

LIMIT=1024*1024
MEMBER_LIMIT=64*LIMIT
OUTCOMES={'approve','reject','revise','defer','stop'}
VERSION='lab-owner-envelope/v2'

def text(v):
    need(type(v) is str and 0<len(v)<=4096 and v.strip()==v and '\x00' not in v,'TEXT')
    return v

def integer(v):
    need(type(v) is int and 0<=v<=2**63-1,'TIME_INTEGER');return v

def fields(v,name,keys):
    closed(v,['schema_version',*keys]);need(v['schema_version']==name,'SCHEMA_VERSION')

def items(v,maximum=128,empty=False):
    need(type(v) is list and (empty or len(v)>0) and len(v)<=maximum,'ARRAY_BOUND')
    need(len({canonical(x) for x in v})==len(v),'DUPLICATE_ITEM');return v

def strings(v,empty=False):
    for x in items(v,empty=empty):text(x)
    return v

def binding(v):
    validate('ByteBinding',v)
    need(v['kind']!='protected-input','PROTECTED_PROVIDER_REQUIRED')
    need(v['size_bytes']<=MEMBER_LIMIT,'MEMBER_BOUND')
    return v

def bindings(v,empty=False):
    for b in items(v,empty=empty):binding(b)
    return v

def hexbytes(v,n):
    need(type(v) is str and re.fullmatch('[0-9a-f]{'+str(n*2)+'}',v) is not None,'HEX_ENCODING')
    return bytes.fromhex(v)

def period(v):
    closed(v,['start','end']);integer(v['start']);integer(v['end']);need(v['start']<v['end'],'PERIOD');return v

def active(v,t):period(v);need(v['start']<=t<v['end'],'PERIOD_INACTIVE')

def timestamp(v):
    need(type(v) is str and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',v) is not None,'NATIVE_TIMESTAMP')
    try:return int(datetime.strptime(v,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp())
    except ValueError:raise Refusal('NATIVE_TIMESTAMP') from None

def owner(v):
    closed(v,['owner_id','principal_ref','assignee_ref','role_ref','boundary_ref','scope_ref','target_refs'])
    for k in v:
        if k=='target_refs':strings(v[k])
        else:text(v[k])

def review(v):
    fields(v,'lab-owner-review-core/v2',['review_id','source_binding','profile_binding','environment_binding','base_binding',
      'targets','owner_matrix','material_bindings','evidence_bindings','artifact_meaning','limitations','required_permission_kinds'])
    text(v['review_id']);text(v['artifact_meaning']);strings(v['limitations'],empty=True)
    strings(v['required_permission_kinds'],empty=True);need(set(v['required_permission_kinds'])<={'operator','release'},'REQUIRED_PERMISSION_KIND')
    for k in ['source_binding','profile_binding','environment_binding','base_binding']:binding(v[k])
    bindings(v['material_bindings']);bindings(v['evidence_bindings'],empty=True)
    refs=[]
    for row in items(v['targets']):
        closed(row,['target_ref','member_binding','effect_kinds']);text(row['target_ref']);binding(row['member_binding']);strings(row['effect_kinds']);refs.append(row['target_ref'])
    need(len(set(refs))==len(refs),'DUPLICATE_TARGET')
    principals=[];coverage=set()
    for row in items(v['owner_matrix'],64):
        owner(row);principals.append(row['owner_id']);need(set(row['target_refs'])<=set(refs),'OWNER_UNKNOWN_TARGET');coverage.update(row['target_refs'])
    need(len(set(principals))==len(principals) and coverage==set(refs),'OWNER_COVERAGE')

def envelope(v):
    fields(v,VERSION,['issuer_ref','algorithm','payload','signature'])
    text(v['issuer_ref']);need(v['algorithm']=='Ed25519-lowerhex-canonical-v2','ALGORITHM');hexbytes(v['signature'],64)
    need(type(v['payload']) is dict,'PAYLOAD')

def signing(v):
    return canonical({k:v[k] for k in ['schema_version','issuer_ref','algorithm','payload']})

def enrollment(v):
    fields(v,'lab-owner-enrollment/v2',['usage','issuers','host_mechanism','role_registry','registry_cursor','max_age_seconds','native_schemas','replay_root'])
    need(v['usage']=='technical-fixture','ACTUAL_G07_PROVIDER_REQUIRED')
    closed(v['issuers'],['review','host','role','effect'])
    for issuer in v['issuers'].values():closed(issuer,['issuer_ref','public_key']);text(issuer['issuer_ref']);hexbytes(issuer['public_key'],32)
    need(v['issuers']['host']['issuer_ref']!=v['issuers']['role']['issuer_ref'] and v['issuers']['host']['public_key']!=v['issuers']['role']['public_key'],'ISSUER_DUTY_SEPARATION')
    for k in ['host_mechanism','role_registry','registry_cursor']:text(v[k])
    integer(v['max_age_seconds']);need(0<v['max_age_seconds']<=86400,'FRESHNESS_BOUND')
    closed(v['native_schemas'],['assignment','role','boundary'])
    for b in v['native_schemas'].values():binding(b)
    closed(v['replay_root'],['root_id','path','identity']);text(v['replay_root']['root_id']);text(v['replay_root']['path'])
    closed(v['replay_root']['identity'],['device','inode','uid','gid','mode'])
    for x in v['replay_root']['identity'].values():integer(x)
    need(v['replay_root']['identity']['mode']==448,'REPLAY_PRIVATE_MODE')

def selection(v):
    fields(v,'lab-owner-selection/v2',['operation_id','review_binding','review_core','owner_inputs','effect_authorization_binding','operator_permission_bindings','disposition_profile'])
    text(v['operation_id']);binding(v['review_binding']);review(v['review_core'])
    text(v['disposition_profile']);need(v['disposition_profile'] in {'c07-v1','t26-original-v1'},'DISPOSITION_PROFILE')
    for row in items(v['owner_inputs'],64):
        closed(row,['owner_id','principal_ref','presentation_binding','role_attestation_binding','disposition_binding'])
        text(row['principal_ref']);text(row['owner_id'])
        for k in ['presentation_binding','role_attestation_binding','disposition_binding']:binding(row[k])
    need(len({x['owner_id'] for x in v['owner_inputs']})==len(v['owner_inputs']),'DUPLICATE_OWNER_INPUT')
    if v['effect_authorization_binding'] is not None:binding(v['effect_authorization_binding'])
    bindings(v['operator_permission_bindings'],empty=True)
