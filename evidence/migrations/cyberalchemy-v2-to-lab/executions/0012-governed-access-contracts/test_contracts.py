import copy
import unittest
from jsonschema import ValidationError
from contracts import contracts,check,check_request_bundle,check_response_bundle,digest_record

def example(schema):
    if 'const' in schema:return schema['const']
    if 'enum' in schema:return schema['enum'][0]
    typ=schema.get('type')
    if typ=='object':return {k:example(v) for k,v in schema['properties'].items()}
    if typ=='array':return [example(schema['items'])] if schema.get('minItems',0) else []
    if typ=='boolean':return False
    if typ=='integer':return 10
    return '1'*64 if schema.get('pattern')=='^[0-9a-f]{64}$' else 'declared'
def fixture(ident):
    d=example(contracts()[ident][2])
    if 'issued_at' in d:d['expires_at']=20
    if ident.endswith('CUSTOMER-ARTIFACT-CUSTODY'):d['terms_accepted']=True
    if ident.endswith('ONTOLOGY-READ-ONLY'):d['read_only']=True
    return d

def bundle():
    prefix='CA2-CAP-CONTRACT-'
    r,e,t,a,p=[fixture(prefix+k) for k in ['AGENT-INSTANTIATION-REQUEST','KEP-SERVICE-REQUEST-ENVELOPE','CLI-ACCESS-ENTITLEMENT','WORKSPACE-AUTHORIZATION','TYPED-INTENT-PROJECT']]
    e['payload_sha256']=a['request_sha256']=digest_record(r);t['expires_at']=a['expires_at']=20;p['validation_passed']=True
    return r,e,t,a,p
class ContractTests(unittest.TestCase):pass
for ident in contracts():
    def test(self,ident=ident):
        good=fixture(ident);self.assertFalse(check(ident,good)['action_authorized'])
        for bad in [{**good,'authority_effect':'grant'},{**good,'undeclared_field':'x'},{k:v for k,v in good.items() if k!='action_authorized'}]:
            with self.assertRaises((ValueError,ValidationError)):check(ident,bad)
    setattr(ContractTests,'test_'+ident.lower().replace('-','_'),test)
class BehavioralTests(unittest.TestCase):
    def test_consistent_bundle_is_not_authorization(self):self.assertFalse(check_request_bundle(*bundle(),'declared',11)['action_authorized'])
    def test_request_mismatch(self):
        b=bundle();b[0]['node_id']='other'
        with self.assertRaises(ValueError):check_request_bundle(*b,'declared',11)
    def test_caller_mismatch(self):
        b=bundle();b[2]['caller_ref']='other'
        with self.assertRaises(ValueError):check_request_bundle(*b,'declared',11)
    def test_scope_and_expiry(self):
        for scope,now in [('other',11),('declared',20),('declared',9)]:
            with self.assertRaises(ValueError):check_request_bundle(*bundle(),scope,now)
    def test_path_escape(self):
        ident='CA2-CAP-POLICY-CREATE-ONLY-CONTAINED-TARGET'
        for path in ['../escape','/absolute','a/../b','a\\b','a//b','C:drive']:
            with self.assertRaises(ValueError):check(ident,{**fixture(ident),'target_relative':path})
    def test_policy_rejections(self):
        mutations={'AGENT-REQUEST-NON-AUTHORITY':{'authority_inferred':True},'CREATE-ONLY-CONTAINED-TARGET':{'target_exists':True},'CUSTOMER-ARTIFACT-CUSTODY':{'terms_accepted':False},'VALIDATION-NON-AUTHORITY':{'authority_inferred':True},'ONTOLOGY-READ-ONLY':{'operation':'mutate'},'EXTERNAL-EFFECT-NON-INHERITANCE':{'external_effect_requested':True}}
        for name,change in mutations.items():
            ident='CA2-CAP-POLICY-'+name
            with self.assertRaises(ValueError):check(ident,{**fixture(ident),**change})
    def test_response_chain(self):
        r,e,*_=bundle();prefix='CA2-CAP-CONTRACT-';out=fixture(prefix+'KEP-SERVICE-RESPONSE-ENVELOPE');art=fixture(prefix+'GOVERNED-SYSTEM-ARTIFACT');rec=fixture(prefix+'EVIDENCE-RECEIPT')
        out['request_sha256']=rec['request_sha256']=digest_record(r);out['receipt_sha256']=digest_record(rec)
        self.assertFalse(check_response_bundle(r,e,out,art,rec)['action_authorized'])
        out['correlation_id']='other'
        with self.assertRaises(ValueError):check_response_bundle(r,e,out,art,rec)
    def test_failure_cannot_contain_artifacts(self):
        ident='CA2-CAP-CONTRACT-KEP-SERVICE-FAILURE-ENVELOPE'
        with self.assertRaises(ValidationError):check(ident,{**fixture(ident),'artifacts':['claimed-output']})
if __name__=='__main__':unittest.main()
