import bootstrap
from bootstrap import E
import argparse,json,marshal,os,struct,tempfile,unittest,importlib.util,uuid,sys
from pathlib import Path
from lab_contracts.codec import sha,Refusal
from lab_selectors.authority import bounded_transport
from lab_packaging.installer import Parent,install
from lab_packaging.probe import cold_probe,python_command
from fixtures import full_payload,anchor,terminal

OWNED=[]
class ColdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.payload=full_payload();cls.pin=sha(cls.payload.verify())
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='owned-cold-',dir=E);self.root=Path(self.temp.name);OWNED.append(self.root)
        self.parent=Parent(anchor(self.root));self.tree,self.expected=install(self.payload,self.pin,self.parent,'installed','stage')
    def tearDown(self):self.tree.close();self.parent.close();self.temp.cleanup()
    def test_actual_cold_origins_sqlite_extensions_native_and_cache_guard(self):
        result=cold_probe(self.tree,self.expected);self.assertEqual(result['result'],'PASS')
        self.assertGreater(len(result['observation']['mapped_origins']),20);self.assertGreater(len(result['observation']['module_origins']),50)
        self.assertFalse(result['native_semantic_qualified']);self.assertFalse(result['protected_startup_qualified'])
        result['payload_manifest_sha256']=self.pin
        raw=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode();path=E/('cold-observation-'+str(uuid.uuid4())+'.json')
        with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        print('cold observation '+path.name+' sha256 '+sha(raw),file=sys.stderr)
    def test_duplicate_fresh_install_has_identical_payload_bytes(self):
        second,expected=install(self.payload,self.pin,self.parent,'second','stage-two')
        try:
            self.assertEqual(expected,self.expected);self.assertEqual((self.tree.path/'payload-manifest.json').read_bytes(),(second.path/'payload-manifest.json').read_bytes())
            self.assertNotEqual(second.ids[''],self.tree.ids['']);second.verify(expected)
        finally:second.cleanup()
    def test_missing_dependency_refuses_before_executable_dispatch(self):
        (self.tree.path/'lib/abi/libsqlite3.so.0').unlink()
        with self.assertRaises(Refusal):cold_probe(self.tree,self.expected)
    def test_wrong_origin_same_name_refuses_before_executable_dispatch(self):
        p=self.tree.path/'lib/abi/libsqlite3.so.0';p.write_bytes(b'wrong origin same name')
        with self.assertRaises(Refusal):cold_probe(self.tree,self.expected)
    def test_actual_isolated_command_ignores_poisoned_incidental_pyc(self):
        # This is a separately owned import fixture, not an exported payload.
        fixture=self.root/'pyc-fixture';fixture.mkdir();source=fixture/'cache_target.py';source.write_text("value = 'selected-source'\n")
        code=compile("value = 'POISONED_BYTECODE'\n",str(source),'exec')
        # Unchecked-hash pyc ignores source hash: without explicit prefix this
        # would execute the poison despite -B. Keep poison solely in own tree.
        # cache_from_source honors this author's sentinel prefix, so use exact
        # conventional adjacent cache location for the installed -I interpreter.
        adjacent=fixture/'__pycache__'/('cache_target.'+__import__('sys').implementation.cache_tag+'.pyc')
        adjacent.parent.mkdir(exist_ok=True)
        adjacent.write_bytes(importlib.util.MAGIC_NUMBER+struct.pack('<I',1)+b'12345678'+marshal.dumps(code))
        code="import sys;sys.path.insert(0,sys.argv[1]);import cache_target;print(cache_target.value)"
        out=bounded_transport(python_command(self.tree,code,[fixture]),{'LC_ALL':'C'},str(self.root),b'',10000,4096)
        self.assertEqual(out,b'selected-source\n')
        control=python_command(self.tree,code,[fixture]);index=next(i for i,v in enumerate(control) if v.startswith('pycache_prefix='))
        del control[index-1:index+1]
        out=bounded_transport(control,{'LC_ALL':'C'},str(self.root),b'',10000,4096)
        self.assertEqual(out,b'POISONED_BYTECODE\n');self.tree.verify(self.expected)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);a=p.parse_args()
    if a.temp_root!=E:raise ValueError('owned root')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ColdTests));raise SystemExit(terminal(result,OWNED))
