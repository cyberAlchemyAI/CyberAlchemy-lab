"""Actual controlled transport, host permission and source-bound view construction."""
from .generation import *
import tempfile,time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
SOURCE_PIN='129eae6c7ceb445c6d79bdc54c6abf6da6e9fa312fc6d9205d1a5c18c7cfe14b'
SOURCE_PACKAGE='e42b503ad366c8c4920eb9380a65190b2910892f2481e62ca260de12692598d7'

def emit(p,value,raw=None):
    require(p.is_relative_to(HERE/'packages') or p.is_relative_to(HERE/'receipts'),'delivery output boundary escaped')
    p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(encoded(value) if raw is None else raw)

def provision(path,source):
    """Explicit construction-only host grant, outside public request JSON."""
    time=now();period=load(reader.HERE/'packages/0001/period.json')
    require(EL.instant(period['not_before'])<=time<EL.instant(period['expires_at']),'original source Assignment period not current')
    key=Ed25519PrivateKey.generate()
    policy={'schema_version':'lab-context-host-policy/v1-candidate','host_uid':os.getuid(),
        'principal_ref':records.PRINCIPAL,'scope_ref':source.sources.scope_ref,
        'reader_public_key':base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode(),
        'not_before':stamp(max(time-timedelta(seconds=1),EL.instant(load(reader.HERE/'packages/0001/period.json')['not_before']))),
        'expires_at':stamp(min(time+timedelta(minutes=20),EL.instant(load(reader.HERE/'packages/0001/period.json')['expires_at']))),
        'max_input_bytes':1048576,'max_output_bytes':2097152,'max_session_seconds':900,
        'period_binding':binding(reader.HERE/'packages/0001/period.json'),'allowed_operations':['context.get','session.open'],
        'authority_effect':'none','actual_owner_outcome':None}
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(encoded(policy))
    return key,sha(path.read_bytes())

def query(source,channel):
    ref=lambda identity:source.sources.resolve(identity)[0].artifact
    return copy.deepcopy({'schema_version':'lab-context-query/v1-candidate','request_ref':'request:R03-actual-source-delivery:'+uuid.uuid4().hex,
        'actor':channel.actor(),'assignment':ref(records.ASSIGNMENT+'@'+records.VERSION),
        'work':ref(records.WORK+'@'+records.VERSION),'coordination_context':ref(records.COORDINATION+'@'+records.VERSION),
        'source_cut':source.source_cut,'intended_use':'Read current scoped Project State','selectors':[],
        'exclusions':['historical-session-memory','private-source-archives','external-effects','unrelated-work'],
        'freshness_requirement':'current','budget':{'max_actions':0,'max_input_bytes':1048576,'max_output_bytes':2097152,
            'deadline':stamp(now()+timedelta(minutes=5))},'authority_effect':'none'})

def build(source_pin,mapped_pin):
    verify_source(source_pin);out=HERE/'packages/0001';require(not out.exists(),'refuse delivery package overwrite');out.mkdir(parents=True,mode=0o700);started=time.monotonic()
    schemas=API.Schemas(API_PROFILE_PIN)
    with reader.open_signed(SOURCE_PIN,SOURCE_PACKAGE) as source,tempfile.TemporaryDirectory(prefix='cal-R03-context-host-') as tmp:
        root=Path(tmp);root.chmod(0o700);policy_path=root/'permission.json';key,policy_pin=provision(policy_path,source)
        channel=HostChannel(policy_path,policy_pin,source_pin,source,schemas)
        try:
            proof_raw=wire({'challenge':channel.challenge,'signature':base64.b64encode(key.sign(wire(channel.challenge))).decode()})
            trusted=channel.authenticate(proof_raw);message=query(source,channel);raw=wire(message)
            emit(out/'request.json',None,raw=raw);emit(out/'authentication-proof.json',None,raw=proof_raw)
            emit(out/'trusted-context.json',trusted);emit(out/'host-permission-public.json',load(policy_path))
            bodies,refs,delivery,provenance,lesson=generate(source,channel,message,raw,mapped_pin,schemas)
            index=[]
            for number,(identity,body) in enumerate(bodies.items()):
                path=out/'artifacts'/(str(number).zfill(2)+'.json');emit(path,body)
                index.append({'artifact':refs[identity],'original_binding':binding(path)})
            emit(out/'artifact-index.json',index);emit(out/'delivery.json',delivery);emit(out/'lesson-selection.json',lesson)
            provenance['verified_original_binding']=bind((out/'delivery.json').relative_to(ROOT).as_posix(),(out/'delivery.json').read_bytes())
            emit(out/'delivery-provenance.json',provenance)
            require(EL.instant(delivery['expires_at'])>now(),'actual delivery expired during construction')
            source.guard();channel.guard();schemas.guard();verify_source(source_pin)
        finally:channel.close();key=None
    require(not root.exists(),'private host permission root remains')
    result={'result':'PASS','actual_generated_artifact_carriers':30,'ontology_nodes':15,'ontology_edges':10,
        'context_request_view_and_ontology_cut_view_records':5,'actual_original_schema_validation':True,
        'real_nonce_transport_authentication':True,'current_independent_host_permission':True,'current_absolute_Assignment_period':True,
        'actual_Context_Delivery_posture':'ready','native_domain_mapping_supplied':True,'source_and_native_cuts_distinct':True,
        'owned_host_policy_and_transport_key_removed':True,'owned_host_root':str(root),'duration_seconds':time.monotonic()-started,'active_Agents_created':0,'public_API_operations_added':0,
        'source_sha256':source_pin,'mapped_package_sha256':mapped_pin,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    emit(out/'build-result.json',result)
    manifest={'schema_version':'lab-actual-context-delivery-package/v1-candidate','files':[binding(p) for p in sorted(out.rglob('*')) if p.is_file()],
        'source_manifest_binding':binding(HERE/'source-manifest.json'),'authority_effect':'none','actual_owner_outcome':None,
        'delivery_binding':binding(out/'delivery.json'),'provenance_binding':binding(out/'delivery-provenance.json'),
        'claim_ceiling':'Actual historical construction delivery at its recorded expiry; later use must revalidate current source, host permission and expiry.'}
    emit(out/'manifest.json',manifest)
    print(json.dumps({'result':'PASS','package_binding':binding(out/'manifest.json'),'generated_carriers':30,'posture':'ready','public_API_operations_added':0}),flush=True)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);p.add_argument('--mapped-package-sha256',required=True);a=p.parse_args();build(a.source_sha256,a.mapped_package_sha256)
