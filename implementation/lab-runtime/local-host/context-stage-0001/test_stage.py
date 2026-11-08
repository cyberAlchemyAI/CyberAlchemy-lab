"""Causal tests use public metadata and disposable fake file bytes only."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import stage as S
import roles as R
import construct as C

class StageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selection,cls.projected,cls.proof,cls.binding=C.construct()

    def test_closed_family_inventory_and_protected_metadata_only(self):
        inventory=S.verify_inventory()
        self.assertEqual(len(inventory['reader_stage_public']),985)
        self.assertEqual(len(inventory['mapper_source_files']),5)
        self.assertEqual(len(inventory['mapper_package_members']),54)
        self.assertEqual(inventory['selected_family_total_files'],1046)
        self.assertEqual(inventory['reader_stage_protected_binding']['body'],'UNOPENED_UNCOPIED')

    def test_future_stage_selection_exact_partition(self):
        value=self.selection
        self.assertEqual(len(value['existing_family_public']),1045)
        self.assertEqual(len(value['exact_public_checkout_additions']),512)
        self.assertEqual(len(value['projected_api_additions']),5)
        self.assertEqual(len(value['projected_context_additions']),7)
        self.assertEqual(value['future_root_file_count_if_protected_copied_under_separate_effect'],1570)
        self.assertEqual(value['container_native_path'],'/attempt/input/lab-context-native-reader')
        self.assertEqual(value['native_sha256'],C.NATIVE_SHA)

    def test_generated_roles_and_selection_equal_pure_projection(self):
        self.assertEqual((S.HERE/'selection.json').read_bytes(),C.encoded(self.selection))
        self.assertEqual((S.HERE/'role-projection-proof.json').read_bytes(),C.encoded(self.proof))
        for name,raw in self.projected.items():
            self.assertEqual((S.HERE/'generated/context'/name).read_bytes(),raw)
        for row in self.selection['projected_api_additions']:
            name=Path(row['path']).name
            self.assertEqual(S.sha((S.HERE/'generated/api-v25'/name).read_bytes()),row['sha256'])
        self.assertEqual((S.HERE/'generated/context/implementation-binding.json').read_bytes(),self.binding)

    def test_context_role_paths_pins_auth_policy_guards_and_effect_refusal(self):
        base=self.projected['base.py']
        control=self.projected['control.py']
        self.assertIn(b"HERE.parent / 'docker-mapped-20261020-0001'",base)
        self.assertIn(b"MAPPED_PIN = '"+R.MAPPER_SHA.encode()+b"'",base)
        self.assertIn(b"API_PROFILE_PIN = '"+R.API_PROFILE_SHA.encode()+b"'",base)
        self.assertIn(b"AUTH = ROOT / 'authorization/context-development.json'",control)
        self.assertIn(b'def read_auth_bytes(',control)
        self.assertIn(b'def read_policy_bytes(',control)
        self.assertNotIn(b'AUTH.read_bytes()',control)
        self.assertNotIn(b'self.path.read_bytes()',control)
        self.assertEqual(self.proof['dummy_authorization_sha256'],'a'*64)
        self.assertEqual(self.proof['dummy_policy_sha256'],'b'*64)
        for fn in (C.final_context_manifest,C.launch,R.final_context_manifest,R.launch):
            with self.assertRaises(S.Refused):fn()

    def test_archive_body_never_entered_held_reader(self):
        original=S.held_read;opened=[]
        def watched(root,name,pin,*args,**kwargs):
            opened.append(str(name))
            return original(root,name,pin,*args,**kwargs)
        with mock.patch.object(S,'held_read',side_effect=watched):
            S.verify_inventory()
        self.assertNotIn(S.ARCHIVE,opened)

    def test_wrong_mapper_leaf_hash_refused(self):
        original=S.held_read
        def wrong(root,name,pin,*args,**kwargs):
            if str(name).endswith('/semantic/00000001.json'):
                return original(root,name,'0'*64,*args,**kwargs)
            return original(root,name,pin,*args,**kwargs)
        with mock.patch.object(S,'held_read',side_effect=wrong):
            with self.assertRaisesRegex(S.Refused,'digest differs'):
                S.verify_inventory()

    def fixture(self,content=b'fixture bytes'):
        temp=tempfile.TemporaryDirectory(prefix='cal-context-stage-fake-')
        root=Path(temp.name);src=root/'src';dst=root/'dst'
        (src/'nested').mkdir(parents=True);(dst/'nested').mkdir(parents=True)
        (src/'nested/file').write_bytes(content)
        row={'path':'nested/file','sha256':S.sha(content),'mode':'0600'}
        return temp,src,dst,row

    def test_fake_held_copy_and_no_replace(self):
        temp,src,dst,row=self.fixture()
        with temp:
            self.assertEqual(S.copy_fake_public(src,dst,row),len(b'fixture bytes'))
            self.assertEqual((dst/'nested/file').read_bytes(),b'fixture bytes')
            with self.assertRaises(FileExistsError):S.copy_fake_public(src,dst,row)
            self.assertEqual((dst/'nested/file').read_bytes(),b'fixture bytes')

    def test_fake_copy_hash_failure_cleans_owned_leaf(self):
        temp,src,dst,row=self.fixture()
        with temp:
            row['sha256']='0'*64
            with self.assertRaisesRegex(S.Refused,'copy source changed'):
                S.copy_fake_public(src,dst,row)
            self.assertFalse((dst/'nested/file').exists())

    def test_fake_symlink_and_fifo_refuse_without_copy(self):
        temp,src,dst,row=self.fixture()
        with temp:
            (src/'nested/file').unlink()
            (src/'nested/file').symlink_to('/etc/hosts')
            with self.assertRaises(OSError):S.copy_fake_public(src,dst,row)
            self.assertFalse((dst/'nested/file').exists())
            (src/'nested/file').unlink()
            os.mkfifo(src/'nested/file')
            with self.assertRaisesRegex(S.Refused,'bounded regular'):
                S.copy_fake_public(src,dst,row)
            self.assertFalse((dst/'nested/file').exists())

    def test_protected_path_and_real_root_forbidden_to_fake_copy(self):
        temp,src,dst,row=self.fixture()
        with temp:
            row['path']=S.ARCHIVE
            with self.assertRaisesRegex(S.Refused,'protected archive copy'):
                S.copy_fake_public(src,dst,row)
            row['path']='nested/file'
            with self.assertRaisesRegex(S.Refused,'fake-only copy root'):
                S.copy_fake_public(S.ROOT,dst,row)

if __name__=='__main__':unittest.main()
