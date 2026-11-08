"""Independent public-fixture checks for frozen Context stage writer 0002."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
import uuid
from unittest import mock

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent/'context-successor-public-stage-writer-0002'
FREEZE_SHA = '8a49c612931a277485ce3a17fc5c89ac81020c2aa9e556ca46ba65e21c73c742'
sha = lambda b: hashlib.sha256(b).hexdigest()

def check_freeze():
    raw = (CANDIDATE/'freeze.json').read_bytes()
    if sha(raw) != FREEZE_SHA:
        raise RuntimeError('FREEZE_DRIFT')
    selected = json.loads(raw)
    for name, expected in selected['members'].items():
        if sha((CANDIDATE/name).read_bytes()) != expected:
            raise RuntimeError('MEMBER_DRIFT:'+name)
    return selected

check_freeze()
sys.path.insert(0, '/usr/lib/python3/dist-packages')
opened = set()
def audit(event, args):
    if event == 'open' and args:
        path = str(args[0])
        if path.endswith('branch.snapshot'):
            raise RuntimeError('PRIVATE_ARCHIVE_BODY_FORBIDDEN')
        if '/mapper-attempt/root/' in path and '/packages/0001/' in path:
            opened.add(path)
    if event.startswith(('subprocess.', 'socket.')) or event in ('os.system','os.fork','os.exec'):
        raise RuntimeError('EFFECT_FORBIDDEN')
sys.addaudithook(audit)

W = types.ModuleType('checked_stage_writer_0002')
W.__file__ = str(CANDIDATE/'stage_writer.py')
exec(compile((CANDIDATE/'stage_writer.py').read_bytes(), W.__file__, 'exec'), W.__dict__)
# Only the explicit fixture gate is moved; all production input/attempt pins stay exact.
W.HERE = HERE
W.__file__ = str(HERE/'stage_writer.py')

class ReviewerTests(unittest.TestCase):
    def fixture(self):
        source = Path(tempfile.mkdtemp(prefix='reviewer-source-', dir=HERE))
        (source/'one').write_bytes(b'public fixture\n')
        (source/'one').chmod(0o644)
        foreign = source/'foreign'
        foreign.mkdir(mode=0o700)
        (foreign/'x').mkdir(mode=0o755)
        attempt = HERE/('fixture-'+uuid.uuid4().hex)
        retained = HERE/('retained-'+uuid.uuid4().hex)
        for path in (source,attempt,retained):
            self.addCleanup(lambda path=path: shutil.rmtree(path) if path.exists() else None)
        row = {'path':'x/one','sha256':sha(b'public fixture\n'),
               'mode':'0644','source_path':source/'one','source_mode':0o644}
        return source,foreign,attempt,retained,[row],{'x':0o755}

    def test_R02_attempt_replaced_after_mkdir_remains_unknown(self):
        _,foreign,attempt,retained,rows,dirs = self.fixture()
        original_inode = []
        def fault(point,*_):
            if point == 'after_attempt_mkdir':
                original_inode.append(attempt.stat().st_ino)
                attempt.rename(retained)
                attempt.mkdir(mode=0o700)
        with self.assertRaises(W.Unknown) as caught:
            W.stage_once(attempt,rows,dirs,'1'*64,fixture=True,fault=fault)
        self.assertTrue(caught.exception.claimed)
        self.assertFalse(caught.exception.retry_allowed)
        self.assertEqual(retained.stat().st_ino,original_inode[0])
        self.assertEqual(list(attempt.iterdir()),[])
        self.assertEqual(list(retained.iterdir()),[])
        self.assertFalse((attempt/'stage.provisional.json').exists())
        self.assertEqual(list((foreign/'x').iterdir()),[])

    def test_R01_real_root_swap_before_copy_rejects_foreign(self):
        _,foreign,attempt,retained,rows,dirs = self.fixture()
        original_root = []
        def fault(point,*_):
            if point == 'before_row':
                original_root.append((attempt/'root').stat().st_ino)
                (attempt/'root').rename(retained)
                foreign.rename(attempt/'root')
        with self.assertRaises(W.Unknown) as caught:
            W.stage_once(attempt,rows,dirs,'2'*64,fixture=True,fault=fault)
        self.assertTrue(caught.exception.claimed)
        self.assertEqual(retained.stat().st_ino,original_root[0])
        self.assertEqual(list((attempt/'root/x').iterdir()),[])
        self.assertFalse((retained/'x/one').exists())
        self.assertTrue((attempt/'consumed.json').is_file())
        self.assertFalse((attempt/'stage.provisional.json').exists())

    def test_R01_swap_inside_target_open_writes_only_original_fd(self):
        _,foreign,attempt,retained,rows,dirs = self.fixture()
        original_open = W.os.open
        swapped = False
        target_parent_inode = []
        def open_interposed(name, flags, *args, **kwargs):
            nonlocal swapped
            if name == 'one' and flags & os.O_EXCL and not swapped:
                swapped = True
                target_parent_inode.append(os.fstat(kwargs['dir_fd']).st_ino)
                (attempt/'root').rename(retained)
                foreign.rename(attempt/'root')
            return original_open(name, flags, *args, **kwargs)
        with mock.patch.object(W.os,'open',side_effect=open_interposed):
            with self.assertRaises(W.Unknown) as caught:
                W.stage_once(attempt,rows,dirs,'3'*64,fixture=True)
        self.assertTrue(swapped)
        self.assertTrue(caught.exception.claimed)
        self.assertEqual(target_parent_inode,[ (retained/'x').stat().st_ino ])
        self.assertEqual((retained/'x/one').read_bytes(),b'public fixture\n')
        self.assertEqual(list((attempt/'root/x').iterdir()),[])
        self.assertFalse((attempt/'stage.provisional.json').exists())

    def test_marker_precedes_content_and_claim_identity_survives_success(self):
        _,_,attempt,_,rows,dirs = self.fixture()
        seen=[]
        def fault(point,*_):
            if point == 'after_marker':
                seen.append((attempt.stat().st_ino,(attempt/'root').stat().st_ino))
                self.assertTrue((attempt/'consumed.json').is_file())
                self.assertEqual(list((attempt/'root').iterdir()),[])
        result=W.stage_once(attempt,rows,dirs,'4'*64,fixture=True,fault=fault)
        self.assertEqual(result,{'files':1,'directories':1})
        self.assertEqual(seen,[(attempt.stat().st_ino,(attempt/'root').stat().st_ino)])
        self.assertEqual((attempt/'root/x/one').read_bytes(),b'public fixture\n')
        self.assertEqual(json.loads((attempt/'stage.provisional.json').read_bytes())['status'],
                         'OBSERVED_STAGE_ONLY_PENDING_EXTERNAL_OS_REVIEW')

result=unittest.TextTestRunner(verbosity=2).run(
    unittest.defaultTestLoader.loadTestsFromTestCase(ReviewerTests))
preflight=W.preflight()
check_freeze()
print(json.dumps({'tests':result.testsRun,'passed':result.wasSuccessful(),
                  'read_only_preflight':preflight,
                  'mapped_package_open_paths_count':len(opened),
                  'actual_attempt_absent':not W.ATTEMPT.exists(),
                  'protected_archive_body':'UNOPENED','stage_effect':'UNRUN'},
                 sort_keys=True))
raise SystemExit(0 if result.wasSuccessful() else 1)
