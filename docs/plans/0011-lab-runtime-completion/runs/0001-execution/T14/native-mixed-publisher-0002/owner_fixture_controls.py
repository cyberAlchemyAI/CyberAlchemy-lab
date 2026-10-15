"""Synthetic T33 historical-verifier controls; no genuine human/owner outcome."""
from dataclasses import replace
from datetime import datetime,timedelta,timezone
from hashlib import sha256
import copy,importlib.util,sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from .owner_history import verify_committed_response

def main(original_path,original_sha256,read):
    raw=read(original_path);assert sha256(raw).hexdigest()==original_sha256
    name='_T14_EXACT_T33_FOR_OWNED_FIXTURES';spec=importlib.util.spec_from_file_location(name,original_path);O=importlib.util.module_from_spec(spec);sys.modules[name]=O
    try:
        exec(compile(raw,str(original_path),'exec'),O.__dict__)
        checks=[]
        def fixture(when):
            host=Ed25519PrivateKey.generate();registry=Ed25519PrivateKey.generate()
            pub=lambda key:key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex()
            stamp=lambda value:value.strftime('%Y-%m-%dT%H:%M:%SZ')
            trust=O.TrustContext('fixture:T14:host',pub(host),'fixture:T14:registry',pub(registry),'fixture:T14:mechanism','fixture:T14:registry','technical-fixture')
            authority={'principal_ref':'fixture:T14:owner','scope_ref':'fixture:T14:scope','expires_at':stamp(when+timedelta(hours=1)),'owner_roles':{'artifact-instance':'fixture:T14:role'}}
            core={'owner_ref':'fixture:T14:role','target_ref':'fixture:T14:target/v1','target_sha256':'a'*64,'decision_ref':'fixture:T14:decision'}
            review={'authority':authority,'authority_sha256':O.digest(authority),'targets':[{'category':'artifact-instance','version_ref':'fixture:T14:target/v1'}],
                'independent_cores':[core],'core_sha256s':[O.legacy_core_digest(core)],'bundle_id':'fixture-t14','bundle_path':'fixture:T14:admission','authority_effect':'none'}
            def sign(payload,kind):
                issuer=trust.role_issuer if kind=='role'else trust.host_issuer;key=registry if kind=='role'else host
                value={'issuer_ref':issuer,'payload':payload};return {**value,'signature':key.sign(O.encoded(value)).hex()}
            evidence=[{'ref':'fixture:T14:source','sha256':'b'*64}]
            role={'schema_version':'lab-governing-owner-evidence/v1-candidate','registry_ref':trust.governing_registry_ref,'registry_cursor':'fixture:T14:cursor',
                'principal_ref':authority['principal_ref'],'scope_ref':authority['scope_ref'],'governing_roles':authority['owner_roles'],'authority_sha256':O.digest(authority),
                'source_evidence':evidence,'valid_from':stamp(when-timedelta(minutes=10)),'valid_until':stamp(when+timedelta(hours=1)),
                'resolution':'independently-resolved-current-governing-authority','permitted_effect':'one-exact-immutable-repository-bundle'}
            response={'schema_version':O.VERSION,'authority_proof':sign(role,'role')}
            shown={'schema_version':'lab-host-review-presentation/v1-candidate','mechanism_ref':trust.mechanism_ref,'presentation_id':'fixture:T14:presentation','conversation_id':'fixture:T14:conversation',
                'principal_ref':authority['principal_ref'],'review_sha256':O.digest(review),'authority_sha256':O.digest(authority),'bundle_id':review['bundle_id'],'bundle_path':review['bundle_path'],
                'decision_core_sha256s':review['core_sha256s'],'displayed_material_sha256':'c'*64,'presented_at':stamp(when-timedelta(minutes=2))}
            response['presentation']=sign(shown,'host');content='OWNED SYNTHETIC CONTROL ONLY; no real owner.'
            message={'schema_version':'lab-host-owner-message/v1-candidate','mechanism_ref':trust.mechanism_ref,'message_id':'fixture:T14:message','conversation_id':shown['conversation_id'],
                'principal_ref':authority['principal_ref'],'interaction_kind':'human-explicit-review-disposition','content':content,'content_sha256':sha256(content.encode()).hexdigest(),
                'presentation_sha256':O.digest(response['presentation']),'review_sha256':O.digest(review),'authority_proof_sha256':O.digest(response['authority_proof']),
                'selected_outcome':O.ADMIT,'recorded_at':stamp(when-timedelta(minutes=1))}
            response['message']=sign(message,'host')
            selected=O.Selection(O.digest(review),O.digest(response['authority_proof']),O.digest(response['presentation']),O.digest(response['message']),role['registry_cursor'],authority['principal_ref'],authority['scope_ref'],'c'*64,O.digest(evidence))
            return response,review,selected,trust,stamp(when)
        args=fixture(datetime.now(timezone.utc).replace(microsecond=0));response,review,selected,trust,when=args
        actual=O.verify(response,review,selected,trust);history=verify_committed_response(response,review,selected,trust,ingress=O,publication_time=when)
        assert actual==history and history['usage']=='technical-fixture';checks.append('actual original current verification equals explicit historical fixture verification')
        def denies(name,call):
            try:call()
            except O.Refusal:checks.append(name);return
            raise AssertionError(name)
        denies('technical fixture still cannot authorize new publication',lambda:O.verify_for_publication(response,review,selected,trust))
        for field,bad in [('review_sha256','d'*64),('displayed_material_sha256','d'*64),('registry_cursor','fixture:T14:wrong')]:
            altered=replace(selected,**{field:bad});denies('historical exact independent binding refuses '+field,lambda altered=altered:verify_committed_response(response,review,altered,trust,ingress=O,publication_time=when))
        bad=copy.deepcopy(response);bad['message']['signature']='0'*128;badselect=replace(selected,message_sha256=O.digest(bad['message']))
        denies('historical signature remains actually verified',lambda:verify_committed_response(bad,review,badselect,trust,ingress=O,publication_time=when))
        denies('historical time outside original role interval refuses',lambda:verify_committed_response(response,review,selected,trust,ingress=O,publication_time='2000-01-01T00:00:00Z'))
        old=fixture(datetime.now(timezone.utc).replace(microsecond=0)-timedelta(hours=3));r,v,s,t,w=old
        denies('original real wall clock continues refusing expired fixture',lambda:O.verify(r,v,s,t))
        assert verify_committed_response(r,v,s,t,ingress=O,publication_time=w)['usage']=='technical-fixture';checks.append('historical signed fixture cold evidence survives expiry without original clock/callback patch')
        assert read(original_path)==raw
        return {'result':'PASS-owned-synthetic-owner-controls-only','checks':checks,'count':len(checks),'original_current_clock_unchanged':True,'actual_owner_outcome':None,'actual_native_calls':0,'authority_effect':'none'}
    finally:sys.modules.pop(name,None)
