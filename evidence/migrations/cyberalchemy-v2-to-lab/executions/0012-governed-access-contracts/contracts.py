"""Proposed candidate contracts. Checks never grant authorization or execute effects."""
import json
from pathlib import PurePosixPath
from jsonschema import Draft202012Validator
T={'type':'string','pattern':r'\S'}
H={'type':'string','pattern':'^[0-9a-f]{64}$'}
BOOL={'type':'boolean'}
TIME={'type':'integer','minimum':0}
TEXTS={'type':'array','items':T,'uniqueItems':True}
LANG={'enum':['typescript','python','rust']}
def fields(**kwargs):return kwargs
def schema(props):
    props={'authority_effect':{'const':'none'},'action_authorized':{'const':False},**props}
    return {'$schema':'https://json-schema.org/draft/2020-12/schema','type':'object','required':sorted(props),'additionalProperties':False,'properties':props}
# Explicit identity mappings. These elaborate source concepts, not equivalent identities.
DEFINITIONS={
'KEP-SERVICE-REQUEST-ENVELOPE':('CAA-CONTRACT-KEP-SERVICE-REQUEST-ENVELOPE', fields(version={'const':1},correlation_id=T,idempotency_key=T,caller_ref=T,payload_contract_ref={'const':'CA2-CAP-CONTRACT-AGENT-INSTANTIATION-REQUEST'},payload_sha256=H,issued_at=TIME,expires_at=TIME)),
'AGENT-INSTANTIATION-REQUEST':('CAA-CONTRACT-AGENT-INSTANTIATION-REQUEST',fields(caller_ref=T,project_ref=T,project_sha256=H,node_id=T,meta_type_ref=T,generator_sha256=H,language=LANG,target_relative=T,entitlement_ref=T,authorization_ref=T)),
'CLI-ACCESS-ENTITLEMENT':('CAA-ENTITLEMENT-CLI-ACCESS',fields(entitlement_ref=T,caller_ref=T,scope_ref=T,operations={'type':'array','minItems':1,'items':{'enum':['instantiate','inspect']},'uniqueItems':True},expires_at=TIME,evidence_sha256=H)),
'WORKSPACE-AUTHORIZATION':('CAA-DECISION-WORKSPACE-AUTHORIZATION',fields(authorization_ref=T,decision_ref=T,caller_ref=T,request_sha256=H,project_sha256=H,node_id=T,language=LANG,workspace_root=T,target_relative=T,expires_at=TIME)),
'TYPED-INTENT-PROJECT':('CAA-CONTRACT-TYPED-INTENT-PROJECT',fields(project_ref=T,project_sha256=H,node_ids={'type':'array','minItems':1,'items':T,'uniqueItems':True},validation_receipt_sha256=H,validation_passed=BOOL)),
'KEP-SERVICE-RESPONSE-ENVELOPE':('CAA-CONTRACT-KEP-SERVICE-RESPONSE-ENVELOPE',fields(version={'const':1},correlation_id=T,request_sha256=H,artifact_sha256=H,receipt_sha256=H,omissions=TEXTS)),
'KEP-SERVICE-FAILURE-ENVELOPE':('CAA-CONTRACT-KEP-SERVICE-FAILURE-ENVELOPE',fields(version={'const':1},correlation_id=T,request_sha256=H,code={'enum':['invalid-input','scope-mismatch','expired','target-exists','unsupported-realization']},retryable=BOOL,artifacts={'type':'array','maxItems':0})),
'GOVERNED-SYSTEM-ARTIFACT':('CAA-ARTIFACT-GOVERNED-SYSTEM',fields(target_relative=T,artifact_sha256=H,project_sha256=H,generator_sha256=H,language=LANG)),
'ONTOLOGY-READ-MODEL':('CAA-READMODEL-ONTOLOGY',fields(registry_sha256=H,selector=T,projection_sha256=H,read_only={'const':True},omissions=TEXTS)),
'EVIDENCE-RECEIPT':('CAA-RECEIPT-SYSTEM-BUILDING',fields(request_sha256=H,artifact_sha256=H,generator_sha256=H,target_relative=T,result={'enum':['created','rejected']},runtime_admitted={'const':False})),
}
POLICIES={
'AGENT-REQUEST-NON-AUTHORITY':('CAA-POLICY-AGENT-REQUEST-NON-AUTHORITY',fields(request_present=BOOL,authority_inferred=BOOL)),
'CREATE-ONLY-CONTAINED-TARGET':('CAA-BOUNDARY-CREATE-ONLY-TARGET',fields(target_relative=T,target_exists=BOOL,symlink_components=BOOL)),
'CUSTOMER-ARTIFACT-CUSTODY':('CAA-POLICY-CUSTOMER-ARTIFACT-CUSTODY',fields(customer_ref=T,destination_owner_ref=T,custody_terms_sha256=H,terms_accepted=BOOL)),
'VALIDATION-NON-AUTHORITY':('CAA-POLICY-VALIDATION-NON-AUTHORITY',fields(validation_passed=BOOL,authority_inferred=BOOL)),
'ONTOLOGY-READ-ONLY':('CAA-POLICY-ONTOLOGY-READ-ONLY',fields(operation={'enum':['inspect','mutate','promote']},read_only=BOOL)),
'EXTERNAL-EFFECT-NON-INHERITANCE':('CAA-POLICY-EFFECT-NON-INHERITANCE',fields(external_effect_requested=BOOL,inherited_authority=BOOL)),
}
def contracts():
    return {**{'CA2-CAP-CONTRACT-'+k:('contract',v[0],schema(v[1])) for k,v in DEFINITIONS.items()},**{'CA2-CAP-POLICY-'+k:('policy',v[0],schema(v[1])) for k,v in POLICIES.items()}}
def safe_relative(path):
    p=PurePosixPath(path)
    if p.is_absolute() or '\\' in path or ':' in path or '\x00' in path or any(x in ['', '.', '..'] for x in path.split('/')):raise ValueError('Target must be a normalized contained relative path')
def check(ident,data):
    Draft202012Validator(contracts()[ident][2]).validate(data)
    if 'target_relative' in data:safe_relative(data['target_relative'])
    if 'issued_at' in data and data['issued_at']>=data['expires_at']:raise ValueError('Invalid freshness interval')
    if ident.startswith('CA2-CAP-POLICY-'):
        k=ident.removeprefix('CA2-CAP-POLICY-')
        passed={
            'AGENT-REQUEST-NON-AUTHORITY':not data.get('authority_inferred',False),
            'CREATE-ONLY-CONTAINED-TARGET':not(data.get('target_exists',False) or data.get('symlink_components',False)),
            'CUSTOMER-ARTIFACT-CUSTODY':data.get('terms_accepted',False) and data.get('customer_ref')==data.get('destination_owner_ref'),
            'VALIDATION-NON-AUTHORITY':not data.get('authority_inferred',False),
            'ONTOLOGY-READ-ONLY':data.get('operation')=='inspect' and data.get('read_only',False),
            'EXTERNAL-EFFECT-NON-INHERITANCE':not(data.get('external_effect_requested',False) or data.get('inherited_authority',False)),
        }[k]
        if not passed:raise ValueError('Candidate policy rejected input: '+k)
    return {'result':'consistent-candidate','action_authorized':False}
def digest_record(record):
    import hashlib
    return hashlib.sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def check_request_bundle(request,envelope,entitlement,authorization,project,scope,now):
    for k,v in [('AGENT-INSTANTIATION-REQUEST',request),('KEP-SERVICE-REQUEST-ENVELOPE',envelope),('CLI-ACCESS-ENTITLEMENT',entitlement),('WORKSPACE-AUTHORIZATION',authorization),('TYPED-INTENT-PROJECT',project)]:check('CA2-CAP-CONTRACT-'+k,v)
    digest=digest_record(request)
    if envelope['payload_sha256']!=digest or authorization['request_sha256']!=digest:raise ValueError('Request digest mismatch')
    if len({x['caller_ref'] for x in [request,envelope,entitlement,authorization]})!=1:raise ValueError('Caller mismatch')
    for key in ['project_sha256','node_id','language','target_relative']:
        if request[key]!=authorization[key]:raise ValueError('Authorization scope mismatch: '+key)
    if request['entitlement_ref']!=entitlement['entitlement_ref'] or request['authorization_ref']!=authorization['authorization_ref']:raise ValueError('Decision reference mismatch')
    if entitlement['scope_ref']!=scope or 'instantiate' not in entitlement['operations']:raise ValueError('Entitlement scope mismatch')
    if not envelope['issued_at']<=now<min(envelope['expires_at'],entitlement['expires_at'],authorization['expires_at']):raise ValueError('Expired or future request')
    if request['project_sha256']!=project['project_sha256'] or request['project_ref']!=project['project_ref'] or request['node_id'] not in project['node_ids'] or not project['validation_passed']:raise ValueError('Project validation mismatch')
    return {'result':'consistent-candidate','action_authorized':False,'limitations':['Caller and approval claims are supplied assertions; not authenticated.','Filesystem containment, atomic writes and signature verification require a real adapter.']}
def check_response_bundle(request,envelope,response,artifact,receipt):
    for k,v in [('AGENT-INSTANTIATION-REQUEST',request),('KEP-SERVICE-REQUEST-ENVELOPE',envelope),('KEP-SERVICE-RESPONSE-ENVELOPE',response),('GOVERNED-SYSTEM-ARTIFACT',artifact),('EVIDENCE-RECEIPT',receipt)]:check('CA2-CAP-CONTRACT-'+k,v)
    if response['correlation_id']!=envelope['correlation_id']:raise ValueError('Response correlation mismatch')
    digest=digest_record(request)
    if any(x!=digest for x in [envelope['payload_sha256'],response['request_sha256'],receipt['request_sha256']]):raise ValueError('Response request mismatch')
    if response['receipt_sha256']!=digest_record(receipt) or response['artifact_sha256']!=artifact['artifact_sha256'] or receipt['artifact_sha256']!=artifact['artifact_sha256']:raise ValueError('Response artifact or receipt mismatch')
    for key in ['project_sha256','generator_sha256','target_relative','language']:
        if artifact[key]!=request[key]:raise ValueError('Artifact provenance mismatch')
    if receipt['generator_sha256']!=request['generator_sha256'] or receipt['target_relative']!=request['target_relative'] or receipt['result']!='created':raise ValueError('Receipt result mismatch')
    return {'result':'consistent-candidate','action_authorized':False}
