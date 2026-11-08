"""Execute exact current-permission helper and actual auth borrowed expression.

These are bounded component tests. Live Reader/Source/wire qualification is
reported separately; no component stub is used by the installed runtime.
"""
import ast,copy,hashlib,json,os,re,stat,tempfile,unittest
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone,timedelta
from types import SimpleNamespace,ModuleType
API=Path(__file__).resolve().parents[4]/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001'
METADATA_POST=Path(__file__).resolve().parent/'metadata-reader-origin-successor-0001/current_metadata_permission.py'
def need(value,reason):
 if not value:raise ValueError(reason)
def selected_function(path,name,namespace):
 node=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name)
 exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),namespace);return namespace[name]
class CurrentMetadata(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='cal-metadata-permission-');self.root=Path(self.temp.name);self.period=self.root/'family/source/period.json';self.period.parent.mkdir(parents=True);self.now=datetime.now(timezone.utc);self.body={'principal_ref':'principal:original-agent','not_before':(self.now-timedelta(minutes=1)).isoformat(),'expires_at':(self.now+timedelta(minutes=20)).isoformat()};self.period.write_text(json.dumps(self.body));self.row={'path':str(self.period.relative_to(self.root)),'sha256':hashlib.sha256(self.period.read_bytes()).hexdigest()}
  self.slots={'family.period':self.row,'family.context_source':{'path':'family/context/source-manifest.json','sha256':'c'*64},'family.reader_source':{'path':'family/reader/source-manifest.json','sha256':'r'*64},'family.source':{'path':'family/source/source-manifest.json','sha256':'s'*64}}
  self.portable=SimpleNamespace(ROOT=self.root,guard=lambda:None,binding=lambda key:copy.deepcopy(self.slots[key]),value=lambda key:'current-fixture')
  source=SimpleNamespace(require=need,parse=json.loads)
  capture=selected_function(API/'guard.py','_capture_exact',{'os':os,'stat':stat,'hashlib':hashlib,'Path':Path,'PurePosixPath':PurePosixPath,'re':re})
  self.validate=selected_function(METADATA_POST,'validate',{'PORTABLE':self.portable,'_capture_exact':capture,'source':source,'Path':Path,'ModuleType':ModuleType})
  self.channel=SimpleNamespace(current_metadata_basis=None)
  self.producer=ModuleType('selected_actual_context');self.producer.__file__=str(self.root/'family/context/build.py');self.producer.HERE=self.root/'family/context';self.producer.reader=SimpleNamespace(HERE=self.root/'family/source',adapter=SimpleNamespace(HERE=self.root/'family/reader'));self.producer.records=SimpleNamespace(PRINCIPAL='principal:original-agent')
  self.policy={'source_name':'current-fixture','principal_ref':'principal:independent-metadata','expires_at':(self.now+timedelta(minutes=5)).isoformat()}
  calls=[n for n in ast.walk(ast.parse((API/'auth.py').read_text())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='current_metadata_permission'];self.assertEqual(len(calls),1);self.producer_argument=compile(ast.Expression(body=calls[0].args[2]),str(API/'auth.py'),'eval')
 def tearDown(self):self.temp.cleanup()
 def run_guard(self,check_source=True,producer='selected',clock=None):
  return self.validate(self.channel,self.policy,self.producer if producer=='selected' else producer,check_source,clock or(lambda:self.now),lambda s:datetime.fromisoformat(s))
 def test_original_true_and_false_boundaries(self):
  self.assertEqual(self.run_guard(),'principal:original-agent');self.assertEqual(self.run_guard(False,producer=None),'principal:original-agent')
 def test_actual_auth_borrowed_producer_expression(self):
  producer=eval(self.producer_argument,{}, {'borrowed':SimpleNamespace(producer=self.producer),'selected_delivery':None});self.assertIs(producer,self.producer);self.assertEqual(self.run_guard(producer=producer),'principal:original-agent')
 def test_actual_auth_direct_producer_expression(self):
  producer=eval(self.producer_argument,{}, {'borrowed':None,'selected_delivery':self.producer});self.assertIs(producer,self.producer);self.run_guard(producer=producer)
 def test_false_never_requires_or_uses_producer(self):
  self.run_guard();poison=SimpleNamespace()
  self.assertEqual(self.run_guard(False,producer=poison),'principal:original-agent')
 def test_wrong_producer_refuses(self):
  bad=ModuleType('wrong_context');bad.__dict__.update(self.producer.__dict__);bad.HERE=self.root/'foreign/context'
  with self.assertRaisesRegex(ValueError,'producer'):self.run_guard(producer=bad)
 def test_same_path_foreign_object_refuses(self):
  bad=SimpleNamespace(**{k:v for k,v in vars(self.producer).items() if not k.startswith('__')});bad.__file__=self.producer.__file__
  with self.assertRaisesRegex(ValueError,'producer'):self.run_guard(producer=bad)
 def test_wrong_module_origin_refuses(self):
  self.producer.__file__=str(self.root/'foreign/build.py')
  with self.assertRaisesRegex(ValueError,'producer'):self.run_guard()
 def test_wrong_source_origin_refuses(self):
  self.producer.reader.HERE=self.root/'foreign/source'
  with self.assertRaisesRegex(ValueError,'producer'):self.run_guard()
 def test_wrong_reader_adapter_origin_refuses(self):
  self.producer.reader.adapter.HERE=self.root/'foreign/reader'
  with self.assertRaisesRegex(ValueError,'producer'):self.run_guard()
 def test_original_principal_cannot_be_metadata(self):
  self.policy['principal_ref']='principal:original-agent'
  with self.assertRaisesRegex(ValueError,'cannot borrow'):self.run_guard()
 def test_original_principal_mismatch_refuses(self):
  self.producer.records.PRINCIPAL='principal:wrong'
  with self.assertRaisesRegex(ValueError,'producer'):self.run_guard()
 def test_changed_period_refuses_before_refreshing_basis(self):
  self.run_guard();before=copy.deepcopy(self.channel.current_metadata_basis);self.period.write_bytes(self.period.read_bytes()+b' ')
  with self.assertRaisesRegex(ValueError,'SHA|digest|capture|bytes'):self.run_guard(False,producer=None)
  self.assertEqual(self.channel.current_metadata_basis,before)
 def test_missing_retained_basis_refuses(self):
  with self.assertRaisesRegex(ValueError,'retained'):self.run_guard(False,producer=None)
 def test_changed_retained_basis_refuses(self):
  self.run_guard();self.channel.current_metadata_basis['principal_ref']='principal:forged'
  with self.assertRaisesRegex(ValueError,'retained'):self.run_guard(False,producer=None)
 def test_expired_or_overlong_grant_refuses(self):
  self.run_guard()
  with self.assertRaisesRegex(ValueError,'period'):self.run_guard(False,producer=None,clock=lambda:self.now+timedelta(minutes=6))
  self.policy['expires_at']=(self.now+timedelta(minutes=21)).isoformat()
  with self.assertRaisesRegex(ValueError,'period'):self.run_guard()
if __name__=='__main__':unittest.main()
