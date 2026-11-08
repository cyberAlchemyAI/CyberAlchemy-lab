"""Causal fake-file proof of no foreign unlink, one-close ownership, and durable name."""
import errno
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import copy_safe as C

class SafeCopyTests(unittest.TestCase):
    def fixture(self,body=b'fake public bytes'):
        temporary=tempfile.TemporaryDirectory(prefix='cal-context-stage-fake-')
        root=Path(temporary.name);source=root/'src';target=root/'dst'
        (source/'nested').mkdir(parents=True);(target/'nested').mkdir(parents=True)
        (source/'nested/file').write_bytes(body)
        return temporary,source,target,{'path':'nested/file','sha256':C.sha(body),'mode':'0600'}

    def test_reviewed_predecessor_unchanged(self):
        self.assertEqual(C.verify_predecessor()['stage_file_plan'],1570)

    def test_success_fsyncs_file_then_directory(self):
        temporary,source,target,row=self.fixture()
        with temporary:
            seen=[];real=C._fsync
            def observed(fd):
                seen.append(stat.S_IFMT(os.fstat(fd).st_mode));real(fd)
            with mock.patch.object(C,'_fsync',side_effect=observed):
                self.assertEqual(C.copy_fake_public(source,target,row),len(b'fake public bytes'))
            self.assertEqual(seen,[stat.S_IFREG,stat.S_IFDIR])
            self.assertEqual((target/'nested/file').read_bytes(),b'fake public bytes')
            self.assertEqual((target/'nested/file').stat().st_mode&0o777,0o600)

    def test_midwrite_foreign_replacement_is_never_unlinked(self):
        temporary,source,target,row=self.fixture()
        with temporary:
            real=C._write;swapped=False
            def replace(fd,chunk):
                nonlocal swapped
                if not swapped:
                    swapped=True
                    (target/'nested/file').rename(target/'nested/owned-renamed')
                    (target/'nested/file').write_bytes(b'foreign sentinel')
                return real(fd,chunk)
            with mock.patch.object(C,'_write',side_effect=replace):
                with self.assertRaises(C.CopyPoisoned) as caught:
                    C.copy_fake_public(source,target,row)
            self.assertFalse(caught.exception.retry_allowed)
            self.assertTrue(caught.exception.stage_poisoned)
            self.assertNotEqual(caught.exception.created_inode,caught.exception.final_name_identity)
            self.assertEqual((target/'nested/file').read_bytes(),b'foreign sentinel')
            self.assertEqual((target/'nested/owned-renamed').read_bytes(),b'fake public bytes')

    def test_rename_before_commit_refuses_and_preserves_owned_inode(self):
        temporary,source,target,row=self.fixture()
        with temporary:
            real=C._fsync;renamed=False
            def detach(fd):
                nonlocal renamed
                real(fd)
                if not renamed and stat.S_ISREG(os.fstat(fd).st_mode):
                    renamed=True
                    (target/'nested/file').rename(target/'nested/owned-renamed')
            with mock.patch.object(C,'_fsync',side_effect=detach):
                with self.assertRaises(C.CopyPoisoned) as caught:
                    C.copy_fake_public(source,target,row)
            self.assertIsNone(caught.exception.final_name_identity)
            self.assertFalse((target/'nested/file').exists())
            self.assertEqual((target/'nested/owned-renamed').read_bytes(),b'fake public bytes')

    def test_hash_failure_poisoned_partial_name_is_not_unlinked(self):
        temporary,source,target,row=self.fixture()
        with temporary:
            row['sha256']='0'*64
            with self.assertRaises(C.CopyPoisoned) as caught:
                C.copy_fake_public(source,target,row)
            self.assertIn('digest differs',str(caught.exception.primary_error))
            self.assertEqual((target/'nested/file').read_bytes(),b'fake public bytes')
            self.assertEqual(caught.exception.created_inode,caught.exception.final_name_identity)

    def test_close_before_release_attempted_once_all_other_fds_closed(self):
        temporary,source,target,row=self.fixture()
        with temporary:
            real=C._close_once;seen=[];leaked=[]
            def fault(fd):
                seen.append(fd)
                if not leaked:
                    leaked.append(fd)
                    raise OSError(errno.EIO,'injected close before release')
                real(fd)
            with mock.patch.object(C,'_close_once',side_effect=fault):
                with self.assertRaises(C.CopyPoisoned) as caught:
                    C.copy_fake_public(source,target,row)
            self.assertIsNone(caught.exception.primary_error)
            self.assertEqual(len(caught.exception.cleanup_errors),1)
            self.assertEqual(len(seen),len(set(seen)))
            self.assertGreater(len(seen),3)
            os.fstat(leaked[0])
            os.close(leaked[0])

    def test_close_after_release_does_not_close_reused_fd(self):
        temporary,source,target,row=self.fixture()
        with temporary:
            real=C._close_once;seen=[];reused=[]
            def fault(fd):
                seen.append(fd)
                if not reused:
                    real(fd)
                    new=os.open('/dev/null',os.O_RDONLY)
                    reused.append(new)
                    self.assertEqual(new,fd)
                    raise OSError(errno.EIO,'injected close after release')
                real(fd)
            with mock.patch.object(C,'_close_once',side_effect=fault):
                with self.assertRaises(C.CopyPoisoned) as caught:
                    C.copy_fake_public(source,target,row)
            self.assertEqual(len(caught.exception.cleanup_errors),1)
            self.assertEqual(len(seen),len(set(seen)))
            os.fstat(reused[0])
            os.close(reused[0])

    def test_first_middle_last_close_faults_attempt_every_owned_fd_once(self):
        temporary,source,target,row=self.fixture()
        with temporary:
            baseline=[];real=C._close_once
            def observed(fd):baseline.append(fd);real(fd)
            with mock.patch.object(C,'_close_once',side_effect=observed):
                C.copy_fake_public(source,target,row)
        total=len(baseline)
        self.assertGreater(total,8)
        for fault_at in (0,total//2,total-1):
            temporary,source,target,row=self.fixture()
            with temporary:
                seen=[];leaked=[]
                def fault(fd):
                    position=len(seen);seen.append(fd)
                    if position==fault_at:
                        leaked.append(fd)
                        raise OSError(errno.EIO,'ambiguous close before release')
                    real(fd)
                with mock.patch.object(C,'_close_once',side_effect=fault):
                    with self.assertRaises(C.CopyPoisoned) as caught:
                        C.copy_fake_public(source,target,row)
                self.assertEqual(len(seen),total)
                self.assertEqual(len(set(seen)),total)
                self.assertEqual(len(caught.exception.cleanup_errors),1)
                os.fstat(leaked[0]);os.close(leaked[0])

    def test_primary_error_and_secondary_close_fault_preserved(self):
        temporary,source,target,row=self.fixture()
        with temporary:
            real=C._close_once;first=True
            def failed_fsync(fd):raise OSError(errno.EIO,'primary fsync failed')
            def failed_close(fd):
                nonlocal first
                if first:
                    first=False;real(fd)
                    raise OSError(errno.EIO,'secondary close after release')
                real(fd)
            with mock.patch.object(C,'_fsync',side_effect=failed_fsync),\
                 mock.patch.object(C,'_close_once',side_effect=failed_close):
                with self.assertRaises(C.CopyPoisoned) as caught:
                    C.copy_fake_public(source,target,row)
            self.assertIn('primary fsync failed',str(caught.exception.primary_error))
            self.assertEqual(len(caught.exception.cleanup_errors),1)
            self.assertIn('secondary close after release',str(caught.exception.cleanup_errors[0][1]))
            self.assertTrue((target/'nested/file').exists())

    def test_collision_symlink_fifo_and_protected_refusal(self):
        temporary,source,target,row=self.fixture()
        with temporary:
            (target/'nested/file').write_bytes(b'existing')
            with self.assertRaises(C.CopyPoisoned) as caught:
                C.copy_fake_public(source,target,row)
            self.assertIsInstance(caught.exception.primary_error,FileExistsError)
            self.assertEqual((target/'nested/file').read_bytes(),b'existing')
            (target/'nested/file').unlink()
            (source/'nested/file').unlink()
            (source/'nested/file').symlink_to('/etc/hosts')
            with self.assertRaises(C.CopyPoisoned):C.copy_fake_public(source,target,row)
            self.assertFalse((target/'nested/file').exists())
            (source/'nested/file').unlink();os.mkfifo(source/'nested/file')
            with self.assertRaises(C.CopyPoisoned) as caught:
                C.copy_fake_public(source,target,row)
            self.assertIn('bounded one-link regular',str(caught.exception.primary_error))
            self.assertFalse((target/'nested/file').exists())
            row['path']=C.ARCHIVE
            with self.assertRaisesRegex(C.Refused,'protected archive body'):
                C.copy_fake_public(source,target,row)

    def test_real_root_cannot_enter_fake_copy(self):
        temporary,source,target,row=self.fixture()
        with temporary:
            with self.assertRaisesRegex(C.Refused,'disposable fake root'):
                C.copy_fake_public(C.REAL_SOURCE,target,row)

if __name__=='__main__':unittest.main()
