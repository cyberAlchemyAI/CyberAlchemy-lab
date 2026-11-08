"""Only synthetic disposable attempts; the selected 1,570-row effect stays off."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import uuid
from unittest import mock

import stage_writer as W


class StageWriterTests(unittest.TestCase):
    def fixture(self):
        source = Path(tempfile.mkdtemp(prefix='source-fixture-', dir=W.HERE))
        (source/'x').mkdir(mode=0o755)
        (source/'x'/'one.txt').write_bytes(b'fixture one\n')
        (source/'x'/'one.txt').chmod(0o644)
        attempt = W.HERE / ('fixture-'+uuid.uuid4().hex)
        row = {'path':'x/one.txt','sha256':hashlib.sha256(b'fixture one\n').hexdigest(),
               'mode':'0644','source':'fixture','source_path':source/'x'/'one.txt',
               'source_mode':0o644}
        self.addCleanup(lambda: shutil.rmtree(source))
        self.addCleanup(lambda: shutil.rmtree(attempt) if attempt.exists() else None)
        return source,attempt,[row],{'x':0o755}

    def test_actual_selection_read_only_and_effect_refusal(self):
        import sys
        sys.path.insert(0, '/usr/lib/python3/dist-packages')
        selected = W.preflight()
        self.assertEqual(selected['rows'],1570)
        self.assertEqual(selected['directories'],1021)
        self.assertEqual(selected['auth'],'UNMINTED_UNSELECTED')
        self.assertEqual(selected['selection_reads']['mapped_package_buffers'],55)
        self.assertFalse(W.ATTEMPT.exists())
        with self.assertRaisesRegex(W.Refused,'STAGE_EFFECT_DISABLED'):
            W.run_effect()
        with self.assertRaisesRegex(W.Refused,'STAGE_EFFECT_DISABLED'):
            W.stage_once(W.ATTEMPT,[{'path':'fixture','sha256':'0'*64}],{},'0'*64)
        for fn in (W.issue_authority,W.create_private_key_or_policy,W.jit_or_docker):
            with self.assertRaises(W.Refused):fn()

    def test_fixture_exact_copy_and_mode_under_umask_0077(self):
        _source,attempt,rows,dirs = self.fixture()
        previous = os.umask(0o077)
        try:
            result = W.stage_once(attempt,rows,dirs,'a'*64,fixture=True)
        finally:
            os.umask(previous)
        self.assertEqual(result,{'files':1,'directories':1})
        self.assertEqual((attempt/'root/x/one.txt').read_bytes(),b'fixture one\n')
        self.assertEqual((attempt/'root/x').stat().st_mode & 0o777,0o755)
        self.assertEqual((attempt/'root/x/one.txt').stat().st_mode & 0o777,0o644)
        self.assertFalse(json.loads((attempt/'consumed.json').read_bytes())['retry_allowed'])
        self.assertEqual(json.loads((attempt/'stage.provisional.json').read_bytes())['status'],
                         'OBSERVED_STAGE_ONLY_PENDING_EXTERNAL_OS_REVIEW')
        with self.assertRaises(W.Unknown):
            W.stage_once(attempt,rows,dirs,'a'*64,fixture=True)

    def test_fault_after_marker_consumes_and_never_retries(self):
        _source,attempt,rows,dirs = self.fixture()
        def fault(point,*_):
            if point == 'after_marker': raise OSError('fixture interruption')
        with self.assertRaises(W.Unknown) as raised:
            W.stage_once(attempt,rows,dirs,'b'*64,fixture=True,fault=fault)
        self.assertTrue(raised.exception.claimed)
        self.assertFalse(raised.exception.retry_allowed)
        self.assertTrue((attempt/'root').is_dir())
        self.assertTrue((attempt/'consumed.json').is_file())
        self.assertFalse((attempt/'root/x').exists())
        with self.assertRaises(W.Unknown):
            W.stage_once(attempt,rows,dirs,'b'*64,fixture=True)

    def test_postclaim_premarker_mode_fault_is_consumed(self):
        _source,attempt,rows,dirs = self.fixture()
        real_fchmod = os.fchmod
        def fault(fd,mode):
            if os.readlink(f'/proc/self/fd/{fd}') == str(attempt):
                raise OSError('fixture post-mkdir fchmod')
            return real_fchmod(fd,mode)
        with mock.patch.object(W.os,'fchmod',side_effect=fault):
            with self.assertRaises(W.Unknown) as raised:
                W.stage_once(attempt,rows,dirs,'h'*64,fixture=True)
        self.assertTrue(raised.exception.claimed)
        self.assertFalse(raised.exception.retry_allowed)
        self.assertTrue(attempt.is_dir())
        self.assertFalse((attempt/'consumed.json').exists())
        with self.assertRaises(W.Unknown):
            W.stage_once(attempt,rows,dirs,'h'*64,fixture=True)

    def test_partial_row_fault_keeps_owned_evidence(self):
        _source,attempt,rows,dirs = self.fixture()
        def fault(point,*_):
            if point == 'after_row': raise OSError('fixture postcopy')
        with self.assertRaises(W.Unknown):
            W.stage_once(attempt,rows,dirs,'c'*64,fixture=True,fault=fault)
        self.assertEqual((attempt/'root/x/one.txt').read_bytes(),b'fixture one\n')
        self.assertTrue((attempt/'consumed.json').exists())
        self.assertFalse((attempt/'stage.provisional.json').exists())

    def test_changed_source_refuses_and_preserves_partial(self):
        source,attempt,rows,dirs = self.fixture()
        (source/'x/one.txt').write_bytes(b'changed\n')
        with self.assertRaises(W.Unknown):
            W.stage_once(attempt,rows,dirs,'d'*64,fixture=True)
        self.assertTrue((attempt/'consumed.json').exists())
        self.assertFalse((attempt/'stage.provisional.json').exists())

    def test_postcopy_source_change_refuses_before_provisional(self):
        source,attempt,rows,dirs = self.fixture()
        def fault(point,*_):
            if point == 'after_row':
                (source/'x/one.txt').write_bytes(b'late changed\n')
        with self.assertRaises(W.Unknown):
            W.stage_once(attempt,rows,dirs,'g'*64,fixture=True,fault=fault)
        self.assertEqual((attempt/'root/x/one.txt').read_bytes(),b'fixture one\n')
        self.assertTrue((attempt/'consumed.json').exists())
        self.assertFalse((attempt/'stage.provisional.json').exists())

    def test_replaced_root_refuses_without_foreign_write(self):
        source,attempt,rows,dirs = self.fixture()
        foreign = source/'foreign'
        foreign.mkdir(mode=0o700)
        def fault(point,*_):
            if point == 'after_marker':
                (attempt/'root').rename(attempt/'retained-root')
                (attempt/'root').symlink_to(foreign, target_is_directory=True)
        with self.assertRaises(W.Unknown):
            W.stage_once(attempt,rows,dirs,'e'*64,fixture=True,fault=fault)
        self.assertEqual(list(foreign.iterdir()),[])
        self.assertTrue((attempt/'retained-root').is_dir())
        self.assertFalse((attempt/'stage.provisional.json').exists())

    def test_real_root_swap_before_copy_never_writes_replacement(self):
        _source,attempt,rows,dirs = self.fixture()
        def fault(point,*_):
            if point == 'before_row':
                (attempt/'root').rename(attempt/'retained-root')
                (attempt/'root').mkdir(mode=0o700)
        with self.assertRaises(W.Unknown) as raised:
            W.stage_once(attempt,rows,dirs,'i'*64,fixture=True,fault=fault)
        self.assertTrue(raised.exception.claimed)
        self.assertFalse((attempt/'root/x/one.txt').exists())
        self.assertFalse((attempt/'stage.provisional.json').exists())
        self.assertTrue((attempt/'retained-root/x').is_dir())

    def test_real_root_swap_inside_copy_targets_retained_inode(self):
        _source,attempt,rows,dirs = self.fixture()
        real_open = W.os.open
        swapped = False
        def interposed(name, flags, *args, **kwargs):
            nonlocal swapped
            if name == 'one.txt' and flags & W.os.O_EXCL and not swapped:
                swapped = True
                (attempt/'root').rename(attempt/'retained-root')
                (attempt/'root').mkdir(mode=0o700)
            return real_open(name, flags, *args, **kwargs)
        with mock.patch.object(W.os,'open',side_effect=interposed):
            with self.assertRaises(W.Unknown) as raised:
                W.stage_once(attempt,rows,dirs,'k'*64,fixture=True)
        self.assertTrue(swapped)
        self.assertTrue(raised.exception.claimed)
        self.assertFalse((attempt/'root/x/one.txt').exists())
        self.assertEqual((attempt/'retained-root/x/one.txt').read_bytes(),b'fixture one\n')
        self.assertFalse((attempt/'stage.provisional.json').exists())

    def test_attempt_real_directory_swap_after_claim_refuses_foreign(self):
        _source,attempt,rows,dirs = self.fixture()
        retained = attempt.with_name(attempt.name+'-retained')
        self.addCleanup(lambda: shutil.rmtree(retained) if retained.exists() else None)
        def fault(point,*_):
            if point == 'after_attempt_mkdir':
                attempt.rename(retained)
                attempt.mkdir(mode=0o700)
        with self.assertRaises(W.Unknown) as raised:
            W.stage_once(attempt,rows,dirs,'j'*64,fixture=True,fault=fault)
        self.assertTrue(raised.exception.claimed)
        self.assertFalse((attempt/'consumed.json').exists())
        self.assertFalse((attempt/'root').exists())
        self.assertTrue(retained.is_dir())
        self.assertFalse((retained/'stage.provisional.json').exists())

    def test_fixture_cannot_open_protected_archive(self):
        _source,attempt,rows,dirs = self.fixture()
        rows[0]['path'] = 'product/branch.snapshot'
        with self.assertRaisesRegex(W.Refused,'FIXTURE_SCOPE'):
            W.stage_once(attempt,rows,dirs,'f'*64,fixture=True)
        self.assertFalse(attempt.exists())


if __name__ == '__main__':
    unittest.main()
