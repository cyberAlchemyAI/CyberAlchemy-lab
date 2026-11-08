import bootstrap
from bootstrap import E
import argparse,copy,os,signal,tempfile,unittest
from pathlib import Path
from lab_contracts.codec import canonical,sha
from lab_packaging.installer import Parent,install,InstallFailure
from fixtures import tiny,anchor,terminal

OWNED=[]
class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='owned-installer-',dir=E);self.root=Path(self.temp.name);OWNED.append(self.root)
        self.p=Parent(anchor(self.root));self.payload=tiny();self.pin=sha(self.payload.verify())
    def tearDown(self):self.p.close();self.temp.cleanup()
    def install(self,**kwargs):return install(self.payload,self.pin,self.p,'installed','stage',**kwargs)
    def reject(self,**kwargs):
        with self.assertRaises(InstallFailure) as e:self.install(**kwargs)
        return e.exception
    def test_fresh_exact_inventory_modes_and_owned_cleanup(self):
        tree,expected=self.install();tree.verify(expected);self.assertEqual((tree.path/'bin/tool').stat().st_mode&0o777,0o755)
        tree.cleanup();self.assertEqual(list(self.root.iterdir()),[])
    def test_restrictive_umask_does_not_change_selected_modes(self):
        old=os.umask(0o777)
        try:tree,expected=self.install()
        finally:os.umask(old)
        tree.verify(expected);tree.cleanup()
    def test_existing_empty_directory_never_adopted(self):
        (self.root/'installed').mkdir();ino=(self.root/'installed').stat().st_ino;self.reject()
        self.assertEqual((self.root/'installed').stat().st_ino,ino);self.assertFalse((self.root/'stage').exists())
    def test_existing_equal_file_never_adopted(self):
        (self.root/'installed').write_bytes(b'fixture public bytes\n');self.reject();self.assertEqual((self.root/'installed').read_bytes(),b'fixture public bytes\n')
    def test_existing_stage_never_cleaned(self):
        (self.root/'stage').mkdir();(self.root/'stage/foreign').write_bytes(b'foreign');self.reject()
        self.assertEqual((self.root/'stage/foreign').read_bytes(),b'foreign')
    def test_symlink_target_refuses(self):
        (self.root/'foreign').mkdir();(self.root/'installed').symlink_to('foreign',target_is_directory=True);self.reject()
        self.assertTrue((self.root/'installed').is_symlink())
    def test_collision_during_rename_preserves_foreign(self):
        def hook(event,tree):
            if event=='before-publish':(self.root/'installed').mkdir();(self.root/'installed/foreign').write_bytes(b'foreign')
        e=self.reject(hook=hook);self.assertEqual(e.cleanup,'clean');self.assertFalse((self.root/'stage').exists())
        self.assertEqual((self.root/'installed/foreign').read_bytes(),b'foreign')
    def test_owned_partial_write_cleaned_at_each_boundary(self):
        for boundary in ('stage-durable','directory-fsync','file-create','file-write','file-fsync','name-fsync','before-publish'):
            def hook(event,tree):
                if event==boundary:raise OSError('inert injected failure')
            e=self.reject(hook=hook);self.assertEqual(e.cleanup,'clean');self.assertEqual(list(self.root.iterdir()),[])
    def test_uncertain_after_rename_preserves_complete_new_generation(self):
        def hook(event,tree):
            if event=='after-rename':raise OSError('inert directory fsync uncertainty')
        e=self.reject(hook=hook);self.assertEqual(e.cleanup,'retained-owned');self.assertTrue((self.root/'installed/bin/tool').is_file())
    def test_foreign_stage_extra_refuses_cleanup_without_deleting_own_files(self):
        def hook(event,tree):
            if event=='before-publish':(tree.path/'foreign').write_bytes(b'foreign');raise OSError('failure')
        e=self.reject(hook=hook);self.assertEqual(e.cleanup,'retained-owned')
        self.assertEqual((self.root/'stage/foreign').read_bytes(),b'foreign');self.assertTrue((self.root/'stage/bin/tool').exists())
    def test_stage_root_replacement_preserves_both_trees(self):
        def hook(event,tree):
            if event=='before-publish':os.rename(tree.path,self.root/'detached');tree.path.mkdir();(tree.path/'foreign').write_bytes(b'foreign')
        self.assertEqual(self.reject(hook=hook).cleanup,'retained-owned')
        self.assertTrue((self.root/'detached/bin/tool').exists());self.assertEqual((self.root/'stage/foreign').read_bytes(),b'foreign')
    def test_file_replacement_is_not_owned_even_if_equal(self):
        def hook(event,tree):
            if event=='before-publish':
                p=tree.path/'bin/tool';p.rename(tree.path/'old');p.write_bytes(b'fixture public bytes\n');p.chmod(0o755)
        self.assertEqual(self.reject(hook=hook).cleanup,'retained-owned');self.assertTrue((self.root/'stage/old').exists())
    def test_hardlink_alias_refuses_before_publication(self):
        def hook(event,tree):
            if event=='before-publish':os.link(tree.path/'bin/tool',self.root/'alias')
        self.assertEqual(self.reject(hook=hook).cleanup,'retained-owned');self.assertFalse((self.root/'installed').exists())
    def test_missing_parent_identity_refuses(self):
        a=anchor(self.root);a.expected['inode']+=1
        with self.assertRaises(Exception):Parent(a)
    def test_ancestor_symlink_refuses(self):
        (self.root/'alias').symlink_to(self.root,target_is_directory=True)
        a=anchor(self.root);from dataclasses import replace
        with self.assertRaises(Exception):Parent(replace(a,path=str(self.root/'alias')))
    def test_parent_detach_refuses_before_staging(self):
        sub=self.root/'parent';sub.mkdir();p=Parent(anchor(sub));sub.rename(self.root/'moved');sub.mkdir()
        try:
            with self.assertRaises(InstallFailure):install(self.payload,self.pin,p,'installed','stage')
        finally:p.close()
        self.assertEqual(list(sub.iterdir()),[])
    def test_wrong_manifest_pin_refuses_before_staging(self):
        self.pin='0'*64;self.reject();self.assertEqual(list(self.root.iterdir()),[])
    def test_changed_payload_refuses_before_staging(self):
        self.payload.files['bin/tool']=b'changed';self.reject();self.assertEqual(list(self.root.iterdir()),[])
    def test_source_drift_refuses_before_publish(self):
        calls=[]
        def recheck():
            calls.append(1)
            if len(calls)==2:raise ValueError('drift')
        self.payload._recheck=recheck;self.assertEqual(self.reject().cleanup,'clean');self.assertEqual(list(self.root.iterdir()),[])
    def test_incomplete_stage_identity_reports_unknown_and_retains(self):
        from unittest.mock import patch
        with patch('lab_packaging.installer._created_directory',side_effect=OSError('inert open failure')):
            self.assertEqual(self.reject().cleanup,'unknown')
        self.assertTrue((self.root/'stage').is_dir())
    def test_descriptor_reserve_refuses_before_staging(self):
        from unittest.mock import patch
        with patch('lab_packaging.installer.resource.getrlimit',return_value=(10,10)):self.reject()
        self.assertEqual(list(self.root.iterdir()),[])
    def test_held_file_descriptors_are_closed_after_cleanup(self):
        before=len(os.listdir('/proc/self/fd'));tree,expected=self.install()
        self.assertGreater(len(os.listdir('/proc/self/fd')),before);tree.cleanup()
        self.assertEqual(len(os.listdir('/proc/self/fd')),before)
    def test_existing_open_descriptors_count_toward_reserve(self):
        from unittest.mock import patch
        with patch('lab_packaging.installer.resource.getrlimit',return_value=(128,128)),patch('lab_packaging.installer.os.listdir',return_value=list(range(100))):
            self.reject()
        self.assertEqual(list(self.root.iterdir()),[])
    def test_unsafe_destination_refuses_before_staging(self):
        self.payload.files={'../escape':b'x'};self.reject();self.assertEqual(list(self.root.iterdir()),[])
    def test_subprocess_death_retains_stage_and_later_install_cannot_adopt(self):
        pid=os.fork()
        if pid==0:
            def hook(event,tree):
                if event=='file-fsync':os.kill(os.getpid(),signal.SIGKILL)
            self.install(hook=hook);os._exit(99)
        got,status=os.waitpid(pid,0);self.assertEqual(got,pid);self.assertTrue(os.WIFSIGNALED(status));self.assertEqual(os.WTERMSIG(status),signal.SIGKILL)
        self.assertTrue((self.root/'stage').is_dir());before=(self.root/'stage').stat().st_ino;self.reject();self.assertEqual((self.root/'stage').stat().st_ino,before)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);a=p.parse_args()
    if a.temp_root!=E:raise ValueError('owned root')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(InstallerTests));raise SystemExit(terminal(result,OWNED))
