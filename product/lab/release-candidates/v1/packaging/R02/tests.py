"""Adversarial installation, scoped export and recovery guards in owned fixtures."""
from common import *
from installer import *
from tempfile import TemporaryDirectory
import copy, unittest
PACKAGE=None;PIN=None
class Guards(unittest.TestCase):
 def setUp(self):self.t=TemporaryDirectory(prefix='cal-R02-negative-');self.root=Path(self.t.name);self.scope=OwnedScope(str(self.root))
 def tearDown(self):self.t.cleanup()
 def test_wrong_pin(self):
  with self.assertRaises(ValueError):package_bytes(PACKAGE,'0'*64)
 def test_environment(self):
  v=environment();v['sqlite_version']='unselected'
  with self.assertRaises(ValueError):environment_guard(v)
 def test_existing_foreign_directory(self):
  dest=self.root/'old';dest.mkdir();(dest/'history').write_bytes(b'retain')
  with self.assertRaises(ValueError):install(PACKAGE,PIN,dest,self.scope)
  self.assertEqual(read(dest/'history'),b'retain')
 def test_existing_empty_directory(self):
  dest=self.root/'empty';dest.mkdir()
  with self.assertRaises(ValueError):install(PACKAGE,PIN,dest,self.scope)
  self.assertTrue(dest.is_dir());self.assertEqual(list(dest.iterdir()),[])
 def test_symlink_destination(self):
  (self.root/'foreign').mkdir();(self.root/'link').symlink_to(self.root/'foreign',target_is_directory=True)
  with self.assertRaises(ValueError):install(PACKAGE,PIN,self.root/'link',self.scope)
 def test_escaped_destination(self):
  with self.assertRaises(ValueError):self.scope.destination(self.root/'nested/escape')
 def test_incomplete_install_stage_retained(self):
  stage=self.root/('.dest.install-'+PIN);stage.mkdir();(stage/'residue').write_bytes(b'retain')
  with self.assertRaises(ValueError):install(PACKAGE,PIN,self.root/'dest',self.scope)
  self.assertEqual(read(stage/'residue'),b'retain');self.assertFalse((self.root/'dest').exists())
 def test_private_key_payload(self):
  with self.assertRaises(ValueError):export_files({'record.json':b'{"private_key":"private"}'},self.root/'export',self.scope)
  self.assertFalse((self.root/'export').exists())
 def test_private_pem_text(self):
  with self.assertRaises(ValueError):privacy(b'-----BEGIN PRIVATE KEY-----\nnot-public\n-----END PRIVATE KEY-----')
 def test_session_memory_payload(self):
  for name in ('short_memory','session_memory'):
   with self.assertRaises(ValueError):privacy(encoded({name:'private'}))
 def test_encoded_private_payload(self):
  with self.assertRaises(ValueError):privacy(encoded({'byte_contents':{'record.json':base64.b64encode(b'{"short_memory":"private"}').decode()}}))
 def test_schema_is_not_memory(self):
  privacy(encoded({'$schema':'https://json-schema.org/draft/2020-12/schema','type':'object','properties':{'short_memory':{'type':'string'}}}),source=True)
  with self.assertRaises(ValueError):privacy(encoded({'$schema':'https://json-schema.org/draft/2020-12/schema','short_memory':'private'}),source=True)
 def test_export_private_path(self):
  for name in ('.env','.local/file','key.pem','record.key','../escape','/absolute','a/../b','a\\b'):
   with self.assertRaises(ValueError):export_files({name:b'{}'},self.root/'export',self.scope)
 def test_export_existing_file(self):
  dest=self.root/'export';dest.write_bytes(b'retain')
  with self.assertRaises(ValueError):export_files({'record.json':b'{}'},dest,self.scope)
  self.assertEqual(read(dest),b'retain')
 def test_recovery_wrong_pin(self):
  emit(self.root/'snapshot',snapshot({'record.json':b'{}'}))
  with self.assertRaises(ValueError):restore(self.root/'snapshot','0'*64,self.root/'restored',self.scope)
 def test_recovery_no_overwrite(self):
  emit(self.root/'snapshot',snapshot({'record.json':b'{}'}));dest=self.root/'restored';dest.mkdir();(dest/'history').write_bytes(b'retain')
  with self.assertRaises(ValueError):restore(self.root/'snapshot',sha(read(self.root/'snapshot')),dest,self.scope)
  self.assertEqual(read(dest/'history'),b'retain')
 def test_incomplete_recovery_retained(self):
  emit(self.root/'snapshot',snapshot({'record.json':b'{}'}));pin=sha(read(self.root/'snapshot'));stage=self.root/('.restored.recover-'+pin);stage.mkdir();(stage/'residue').write_bytes(b'retain')
  with self.assertRaises(ValueError):restore(self.root/'snapshot',pin,self.root/'restored',self.scope)
  self.assertEqual(read(stage/'residue'),b'retain')
 def test_duplicate_json(self):
  with self.assertRaises(ValueError):parse(b'{"x":1,"x":2}')
 def test_snapshot_byte_digest(self):
  v=snapshot({'record.json':b'{}'});v['sha256s']['record.json']='0'*64
  with self.assertRaises(ValueError):payload(encoded(v))
 def test_snapshot_closed_envelope(self):
  v=snapshot({'record.json':b'{}'});v['owner_approved']=True
  with self.assertRaises(ValueError):payload(encoded(v))
 def test_archive_private_content(self):
  emit(self.root/'snapshot',snapshot({'record.json':b'{"short_memory":"private"}'}))
  with self.assertRaises(ValueError):restore(self.root/'snapshot',sha(read(self.root/'snapshot')),self.root/'restored',self.scope)
 def test_archive_symlink_source(self):
  emit(self.root/'real',snapshot({'record.json':b'{}'}));(self.root/'link').symlink_to(self.root/'real')
  with self.assertRaises(ValueError):restore(self.root/'link',sha(read(self.root/'real')),self.root/'restored',self.scope)
 def test_recovery_idempotent_exact(self):
  emit(self.root/'snapshot',snapshot({'record.json':b'{}'}));pin=sha(read(self.root/'snapshot'));restore(self.root/'snapshot',pin,self.root/'restored',self.scope)
  self.assertTrue(restore(self.root/'snapshot',pin,self.root/'restored',self.scope)['idempotent'])
 def test_unselected_dependency_file(self):
  _,files=package_bytes(PACKAGE,PIN);dest=self.root/'install';write_files(dest,files);(dest/'deps/unselected.py').write_bytes(b'bad')
  with self.assertRaises(ValueError):verify_install(dest,PACKAGE,PIN)
 def test_installed_bytes_changed(self):
  _,files=package_bytes(PACKAGE,PIN);dest=self.root/'install';write_files(dest,files);p=dest/'deps/jsonschema/__init__.py';p.write_bytes(read(p)+b'\n')
  with self.assertRaises(ValueError):verify_install(dest,PACKAGE,PIN)

def run(package,pin):
 global PACKAGE,PIN
 PACKAGE=package;PIN=pin;result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Guards));need(result.wasSuccessful(),'R02 negative suite failed');return result.testsRun
