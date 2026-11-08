"""Small causal origin/archive cases; no full-table regeneration per mutation."""
import t08_prerequisite
from bootstrap import E
import argparse,copy,io,json,stat,struct,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from lab_contracts.codec import sha,Refusal
from dependency_graph.reader import RoleReader
from environment.origins import OriginSelection,verify_selected_origins,wheel_inventory
from test_reader import Fixture

def archive(rows):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w') as z:
        for name,raw,mode in rows:
            info=zipfile.ZipInfo(name);info.external_attr=mode<<16;z.writestr(info,raw)
    return stream.getvalue()

class WheelTests(unittest.TestCase):
    def reject(self,raw):
        with self.assertRaisesRegex(Refusal,'^WHEEL_ORIGIN_REFUSED$'):wheel_inventory(raw)
    def test_exact_original_member_bytes_and_modes(self):
        self.assertEqual(wheel_inventory(archive([('pkg/a.py',b'payload',stat.S_IFREG|0o755)])),
            {'deps/pkg/a.py':{'sha256':sha(b'payload'),'size_bytes':7,'mode':0o644}})
    def test_traversal_absolute_backslash_dot_and_empty_component_refuse(self):
        for name in ('../a','/a','pkg/../a','pkg/./a','pkg//a','pkg\\a'):
            with self.subTest(name=name):self.reject(archive([(name,b'x',stat.S_IFREG|0o644)]))
    def test_symlink_device_and_fifo_members_refuse(self):
        for mode in (stat.S_IFLNK,stat.S_IFIFO,stat.S_IFCHR):self.reject(archive([('a',b'x',mode|0o600)]))
    def test_hook_and_data_install_alternatives_refuse(self):
        for name in ('a.pth','x.data/a.py','.data/a.py'):self.reject(archive([(name,b'x',stat.S_IFREG|0o644)]))
    def test_duplicate_member_identity_refuses(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',UserWarning);raw=archive([('a',b'x',0),('a',b'y',0)])
        self.reject(raw)
    def test_nul_truncation_does_not_rebind_member(self):
        raw=archive([('abc',b'x',0)]).replace(b'abc',b'a\0c');self.reject(raw)
    def test_declared_expansion_bound_checked_before_decompression(self):
        raw=bytearray(archive([('a',b'x',0)]));central=raw.index(b'PK\x01\x02')
        struct.pack_into('<I',raw,central+24,32*1024*1024+1);self.reject(bytes(raw))
    def test_corrupt_archive_refuses_without_extraction(self):self.reject(b'not a zip file')

OWNED=[]
class OriginTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='owned-small-origin-',dir=E);self.root=Path(self.temp.name);OWNED.append(self.root)
        self.f=Fixture(self.root);self.f.policy['files'][2]['kind']='host-dependency'
        self.f.policy_binding=self.f.write('policy-new.json',self.f.policy,'execution')
        self.reader=self.f.role();b=self.f.public
        self.selection=OriginSelection(self.f.source,self.f.profile,self.f.cut,[{'destination':'data','file_id':'schema','binding':copy.deepcopy(b)}])
        self.requirements={'inputs':[{'kind':'stdlib','destination':'data','sha256':b['sha256'],'size_bytes':b['size_bytes'],'mode':0o644}],
            'wheel_members':{},'elf_graph':{}}
    def tearDown(self):self.temp.cleanup()
    def test_complete_origin_positive_and_no_runtime_claim(self):
        value=verify_selected_origins(self.reader,self.requirements,self.selection)
        self.assertEqual(value['members'],1);self.assertFalse(value['runtime_abi_verified']);self.assertEqual(self.f.calls,0)
    def test_body_changes_after_first_read_are_detected_before_success(self):
        original=RoleReader.read;calls=[]
        def changed(reader,file_id,*a,**k):
            raw=original(reader,file_id,*a,**k)
            if file_id=='schema' and not calls:
                calls.append(file_id);(self.root/'schema.json').write_bytes(b'changed')
            return raw
        with patch.object(RoleReader,'read',changed),self.assertRaises(Refusal):verify_selected_origins(self.reader,self.requirements,self.selection)
        self.assertEqual(calls,['schema'])
    def test_changed_selection_during_read_refuses(self):
        original=RoleReader.read
        def changed(reader,file_id,*a,**k):
            raw=original(reader,file_id,*a,**k);self.selection.members[0]['destination']='other';return raw
        with patch.object(RoleReader,'read',changed),self.assertRaises(Refusal):verify_selected_origins(self.reader,self.requirements,self.selection)
    def test_missing_origin_fails_before_any_member_call(self):
        self.selection.members.clear()
        with patch.object(RoleReader,'read',side_effect=AssertionError('member read occurred')) as read,self.assertRaises(Refusal):
            verify_selected_origins(self.reader,self.requirements,self.selection)
        read.assert_not_called()
    def test_unknown_elf_declaration_is_not_omitted(self):
        self.requirements['elf_graph']={'data':{'needed':[],'interpreter':None}}
        with self.assertRaises(Refusal):verify_selected_origins(self.reader,self.requirements,self.selection)
    def test_archive_member_not_selected_refuses(self):
        self.requirements['wheel_members']={'deps/absent':{'sha256':'0'*64,'size_bytes':0,'mode':0o644}}
        with self.assertRaises(Refusal):verify_selected_origins(self.reader,self.requirements,self.selection)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);a=p.parse_args()
    if a.temp_root!=E or not E.is_dir():raise ValueError('owned root')
    suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in (WheelTests,OriginTests))
    result=unittest.TextTestRunner(verbosity=2).run(suite);t08_prerequisite.guard()
    clean=not any(p.exists() for p in OWNED)
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if result.wasSuccessful() and clean else 'FAIL',
        'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean' if clean else 'retained-owned'}))
    raise SystemExit(0 if result.wasSuccessful() and clean else 1)
