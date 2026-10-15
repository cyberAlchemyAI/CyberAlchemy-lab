"""External manifest pins and frozen regression/source closure cannot be replaced."""
import copy,json,os,sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

PACKAGE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PACKAGE))
from inventory_manifest import *


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory(prefix='lab-c09-manifest-negative-');self.addCleanup(self.temp.cleanup)
        self.path=Path(os.environ['C09_MANIFEST_PATH']);self.pin=os.environ['C09_MANIFEST_SHA256'];self.original=load(self.path)
    def staged(self,value):
        p=Path(self.temp.name)/'manifest.json';p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n');return p,sha(p.read_bytes())
    def test_frozen_manifest_is_current(self):self.assertEqual(validate_manifest(self.path,self.pin),self.original)
    def test_revised_manifest_cannot_reuse_old_pin(self):
        changed=copy.deepcopy(self.original);changed['files'][0]['sha256']='0'*64;p,pin=self.staged(changed)
        with self.assertRaisesRegex(ValueError,'independent candidate manifest pin'):validate_manifest(p,self.pin)
    def test_resealed_false_source_hash_rejected(self):
        changed=copy.deepcopy(self.original);changed['files'][0]['sha256']='0'*64;p,pin=self.staged(changed)
        with self.assertRaisesRegex(ValueError,'candidate bytes changed'):validate_manifest(p,pin)
    def test_removed_regression_group_rejected(self):
        changed=copy.deepcopy(self.original);changed['groups'].pop();p,pin=self.staged(changed)
        with self.assertRaisesRegex(ValueError,'regression group inventory changed'):validate_manifest(p,pin)
    def test_removed_or_duplicate_source_binding_rejected(self):
        for duplicate in [False,True]:
            changed=copy.deepcopy(self.original)
            if duplicate:changed['files'].append(changed['files'][0])
            else:changed['files'].pop()
            p,pin=self.staged(changed)
            with self.assertRaisesRegex(ValueError,'candidate file closure changed'):validate_manifest(p,pin)
    def test_manifest_cannot_fabricate_owner_outcome(self):
        changed=copy.deepcopy(self.original);changed['actual_owner_outcome']='admitted';p,pin=self.staged(changed)
        with self.assertRaisesRegex(ValueError,'owner authority'):validate_manifest(p,pin)
