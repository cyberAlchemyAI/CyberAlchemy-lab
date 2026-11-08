"""Verify actual fixture-root custody without constructing production services."""
import ast
from contextlib import contextmanager,redirect_stderr
import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
SOURCE=Path(__file__).resolve().parent.parent/'t31-public-owned-transition-0001/public_fixture.py'
tree=ast.parse(SOURCE.read_bytes());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='owned_fixture_root')
scope=dict(contextmanager=contextmanager,Path=Path,tempfile=tempfile,shutil=shutil,sys=sys)
exec(compile(ast.Module(body=[node],type_ignores=[]),str(SOURCE),'exec'),scope)
owned=scope['owned_fixture_root']
class Custody(unittest.TestCase):
 def test_success_removes_actual_root_in_both_modes(self):
  for keep in (False,True):
   with owned(keep) as root:(root/'original').write_bytes(b'actual controlled fixture')
   self.assertFalse(root.exists())
 def test_default_failure_keeps_existing_cleanup_contract(self):
  with self.assertRaisesRegex(ValueError,'primary fixture failure'):
   with owned() as root:raise ValueError('primary fixture failure')
  self.assertFalse(root.exists())
 def test_requested_failure_retains_original_inode_mode_and_bytes(self):
  stream=io.StringIO()
  with redirect_stderr(stream),self.assertRaisesRegex(ValueError,'primary fixture failure'):
   with owned(True) as root:
    original=root/'original';original.write_bytes(b'actual controlled fixture');identity=original.stat().st_ino
    raise ValueError('primary fixture failure')
  try:
   self.assertEqual(original.read_bytes(),b'actual controlled fixture');self.assertEqual(original.stat().st_ino,identity)
   self.assertEqual(root.stat().st_mode&0o777,0o700);self.assertIn(str(root),stream.getvalue())
  finally:shutil.rmtree(root)
if __name__=='__main__':unittest.main()
