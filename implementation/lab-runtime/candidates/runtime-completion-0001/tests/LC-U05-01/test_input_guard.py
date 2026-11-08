"""Causal source-selection failures in exclusively owned miniature inventories."""
import bootstrap
from bootstrap import E
import argparse,copy,hashlib,json,os,tempfile,unittest
from pathlib import Path
from run_selected import guard_snapshot

OWNED=[]
class GuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='owned-input-guard-',dir=E)
        self.root=Path(self.tmp.name);OWNED.append(self.root)
        self.source=self.root/'source';self.source.mkdir();self.file=self.source/'a.py';self.file.write_bytes(b'x=1\n')
        self.value={'schema_version':'lab-u0501-selected-inputs/v1','authority_effect':'none',
            'owned_source_paths':['source/a.py'],'files':[{'kind':'execution','root_id':'repository','relative_path':'source/a.py',
            'sha256':hashlib.sha256(self.file.read_bytes()).hexdigest(),'size_bytes':4}]}
        self.manifest=self.root/'manifest.json';self.pin=self.save()
    def tearDown(self):self.tmp.cleanup()
    def save(self):
        raw=json.dumps(self.value).encode();self.manifest.write_bytes(raw);return hashlib.sha256(raw).hexdigest()
    def guard(self,pin=None):return guard_snapshot(self.manifest,pin or self.pin,repository=self.root,scopes=(self.source,))
    def test_exact_complete_inventory_passes(self):self.guard()
    def test_new_python_source_refuses(self):
        (self.source/'extra.py').write_bytes(b'bad')
        with self.assertRaises(ValueError):self.guard()
    def test_existing_source_changed_refuses(self):
        self.file.write_bytes(b'x=2\n')
        with self.assertRaises(ValueError):self.guard()
    def test_coherent_repinned_manifest_cannot_replace_external_pin(self):
        self.file.write_bytes(b'x=2\n');self.value['files'][0]['sha256']=hashlib.sha256(self.file.read_bytes()).hexdigest();self.save()
        with self.assertRaises(ValueError):self.guard()
    def test_omitted_binding_refuses_even_when_inventory_lists_file(self):
        self.value['files']=[];pin=self.save()
        with self.assertRaises(ValueError):self.guard(pin)
    def test_duplicate_binding_refuses(self):
        self.value['files'].append(copy.deepcopy(self.value['files'][0]));pin=self.save()
        with self.assertRaises(ValueError):self.guard(pin)
    def test_symlink_file_and_directory_refuse(self):
        self.file.unlink();self.file.symlink_to(self.manifest)
        with self.assertRaises((ValueError,OSError)):self.guard()
        self.file.unlink();self.file.write_bytes(b'x=1\n');(self.source/'alias').symlink_to(self.source,target_is_directory=True)
        with self.assertRaises(ValueError):self.guard()
    def test_fifo_refuses_without_waiting_for_writer(self):
        self.file.unlink();os.mkfifo(self.file)
        with self.assertRaises(ValueError):self.guard()
    def test_unknown_field_and_traversal_refuse(self):
        self.value['unknown']=True;pin=self.save()
        with self.assertRaises(ValueError):self.guard(pin)
        del self.value['unknown'];self.value['files'][0]['relative_path']='source/../source/a.py';pin=self.save()
        with self.assertRaises(ValueError):self.guard(pin)
    def test_duplicate_json_key_refuses(self):
        raw=self.manifest.read_bytes();raw=b'{"authority_effect":"none",'+raw[1:];self.manifest.write_bytes(raw)
        with self.assertRaises(ValueError):self.guard(hashlib.sha256(raw).hexdigest())
    def test_boolean_size_and_malformed_digest_refuse(self):
        self.value['files'][0]['size_bytes']=True;pin=self.save()
        with self.assertRaises(ValueError):self.guard(pin)
        self.value['files'][0]['size_bytes']=4;self.value['files'][0]['sha256']='A'*64;pin=self.save()
        with self.assertRaises(ValueError):self.guard(pin)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);a=p.parse_args()
    if a.temp_root!=E or not E.is_dir():raise ValueError('owned root')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(GuardTests))
    clean=not any(p.exists() for p in OWNED)
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if result.wasSuccessful() and clean else 'FAIL',
        'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean' if clean else 'retained-owned'}))
    raise SystemExit(0 if result.wasSuccessful() and clean else 1)
