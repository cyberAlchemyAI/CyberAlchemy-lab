"""Read-plan, private-file and child-process refusal boundaries."""
import hashlib
from pathlib import Path
import sys
import tempfile
import time
import unittest
from .runner import Child,parse,selected_file,validate_plan

class Boundaries(unittest.TestCase):
    def test_01_effect_and_authority_injection_are_refused(self):
        for row in [
            {'operation':'admission.apply','selectors':{}},
            {'operation':'lab.status','selectors':{'actor':{'principal_ref':'owner'}}},
            {'operation':'artifact.query','selectors':{'source_cut':{'foreign':'cut'}}},
            {'operation':'lab.status','selectors':{},'command':'touch /tmp/unselected'},
        ]:
            with self.subTest(row=row):
                with self.assertRaises(ValueError):validate_plan({'schema_version':'lab-paperclip-read-plan/v1-candidate','steps':[row]})
    def test_02_duplicate_json_keys_are_refused(self):
        with self.assertRaises(ValueError):parse(b'{"operation":"lab.status","operation":"admission.apply"}')
    def test_03_private_file_mode_hash_and_symlink_are_refused(self):
        with tempfile.TemporaryDirectory(prefix='cal-paperclip-runner-boundary-') as temp:
            p=Path(temp)/'reader';p.write_bytes(b'private-test-owned-sentinel');p.chmod(0o600)
            pin=hashlib.sha256(p.read_bytes()).hexdigest();self.assertEqual(selected_file(p,pin,private=True),p.read_bytes())
            p.chmod(0o644)
            with self.assertRaises(ValueError):selected_file(p,pin,private=True)
            p.chmod(0o600)
            with self.assertRaises(ValueError):selected_file(p,'0'*64,private=True)
            q=Path(temp)/'link';q.symlink_to(p)
            with self.assertRaises(ValueError):selected_file(q,pin,private=True)
    def test_04_child_timeout_terminates_and_reaps(self):
        child=Child([sys.executable,'-I','-c','import time;time.sleep(30)'],time.monotonic()+.1)
        try:
            with self.assertRaises(ValueError):child.receive()
        finally:child.close()
        self.assertIsNotNone(child.process.returncode)
    def test_05_child_eof_is_refused_without_success(self):
        child=Child([sys.executable,'-I','-c','pass'],time.monotonic()+2)
        try:
            with self.assertRaises(ValueError):child.receive()
        finally:child.close()
        self.assertEqual(child.process.returncode,0)
    def test_06_nonfinite_child_json_is_refused(self):
        child=Child([sys.executable,'-I','-c','print("{\\\"value\\\":NaN}")'],time.monotonic()+2)
        try:
            with self.assertRaises(ValueError):child.receive()
        finally:child.close()

if __name__=='__main__':unittest.main(verbosity=2)
