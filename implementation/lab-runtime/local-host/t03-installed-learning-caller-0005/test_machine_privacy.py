"""Actual public transport builder and causal privacy witness validation."""
import ast,hashlib,importlib.util,json,unittest
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('_machine_privacy',HERE/'machine_privacy.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
compact=lambda value:json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def original_transport():
 path=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001/service.py'
 tree=ast.parse(path.read_bytes());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='transport')
 scope={'source':SimpleNamespace(sha=lambda raw:hashlib.sha256(raw).hexdigest())}
 exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),scope);return scope['transport']
class Resource:
 def __init__(self):self.memory=[]
 def note(self,value):self.memory.append(bytearray(value))
class Tests(unittest.TestCase):
 def service(self,reply):
  schemas=SimpleNamespace(valid=lambda key,v:(key=='transport-error' and v.get('schema_version')=='lab-api-transport-error/v1-candidate') or (key=='api-reply' and v.get('kind') in ('error','result')),protocol_valid=lambda *_:True,profile_binding={'ref':'actualprofile','sha256':'a'*64},operations={'session.inspect':{'result_schema':{'resource_uri':'result'},'error_schema':{'resource_uri':'error'}}})
  return SimpleNamespace(schemas=schemas,vault=SimpleNamespace(root=Path('/tmp/fixture')),call=lambda raw:reply)
 def test_actual_malformed_transport_builder_is_accepted_without_fabricated_kind(self):
  raw=b'{not-json';reply=original_transport()('malformed-json',raw);w=M.Witness(Resource());w.invoke(self.service(reply),raw,compact,'malformed','transport-error',expected_code='malformed-json')
  self.assertEqual(w.replies[0]['kind'],'transport-error');self.assertIsNone(reply.get('kind'));self.assertTrue(w.replies[0]['actual_schema_and_request_binding_valid'])
 def test_wrong_transport_cause_binding_or_effect_uncertainty_refuses(self):
  raw=b'{not-json';good=original_transport()('malformed-json',raw)
  for delta in ({'code':'unauthenticated-channel'},{'request_byte_sha256':'0'*64},{'effect_may_have_started':True},{'kind':'error'}):
   with self.subTest(delta=delta),self.assertRaisesRegex(ValueError,'malformed transport'):
    M.Witness(Resource()).invoke(self.service({**good,**delta}),raw,compact,'malformed','transport-error',expected_code='malformed-json')
 def test_valid_domain_refusal_requires_exact_causal_code_and_request_binding(self):
  raw=compact({'operation':'session.inspect'});service=self.service(None)
  good={'kind':'error','schema_version':'reply','message':{'code':'unauthorized'},'request_binding':{'sha256':hashlib.sha256(raw).hexdigest()},'contract_profile_binding':service.schemas.profile_binding}
  M.Witness(Resource()).invoke(self.service(good),raw,compact,'foreign','error',expected_code='unauthorized')
  for delta in ({'message':{'code':'invalid-contract'}},{'request_binding':{'sha256':'0'*64}}):
   with self.subTest(delta=delta),self.assertRaises(ValueError):M.Witness(Resource()).invoke(self.service({**good,**delta}),raw,compact,'foreign','error',expected_code='unauthorized')
 def test_private_ram_in_transport_is_refused_before_posture_acceptance(self):
  raw=b'{not-json';w=M.Witness(Resource());reply={**original_transport()('malformed-json',raw),'unexpected_note':w.sentinel.decode()}
  with self.assertRaisesRegex(ValueError,'private Machine RAM'):w.invoke(self.service(reply),raw,compact,'malformed','transport-error',expected_code='malformed-json')
if __name__=='__main__':unittest.main()
