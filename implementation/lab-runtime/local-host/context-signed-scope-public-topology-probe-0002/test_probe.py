"""Inert public topology projection and child-shape tests only."""
import errno
import os
from pathlib import Path
import stat
import tempfile
import types
import unittest
from unittest import mock

import child
import probe

class ProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(
            prefix='fixture-signed-scope-topology-',dir=probe.FAMILY)
        cls.root=Path(cls.tmp.name)
        cls.stage=cls.root/'stage'
        cls.claim=cls.root/'attempt.claim'
        cls.stage.mkdir(mode=0o700)
        for path,raw in ((cls.stage/'.public-topology-only',probe.STAGE_MARKER),
                         (cls.claim,probe.CLAIM_MARKER)):
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            try:os.write(fd,raw)
            finally:os.close(fd)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_exact_three_bind_projection_and_no_private_source(self):
        row=probe.projection(self.stage,self.claim,'a'*32)
        self.assertFalse(row['effect_enabled'])
        self.assertFalse(row['docker_invoked'])
        self.assertEqual(row['basis']['portable_review'],
                         'PASS_BOUNDED_INERT_BUNDLE_CORRECTION')
        argv=row['create_argv']
        self.assertEqual(argv.count('--mount'),3)
        mounts=[argv[i+1] for i,value in enumerate(argv) if value=='--mount']
        self.assertEqual(mounts,[
            f'type=bind,src={self.stage},dst={probe.STAGE_TARGET},readonly',
            f'type=bind,src={probe.BUNDLE},dst=/bundle,readonly',
            f'type=bind,src={self.claim},dst=/control/attempt.claim,readonly'])
        self.assertNotIn(f'src={probe.STAGE_TARGET},',str(mounts))
        self.assertEqual(row['private_archive'],'ABSENT')
        for flag,value in (('--network','none'),('--cap-drop','ALL'),
                           ('--user','1000:1000'),
                           ('--security-opt','no-new-privileges')):
            self.assertEqual(argv[argv.index(flag)+1],value)
        self.assertIn('--read-only',argv)
        self.assertEqual(argv.count('--tmpfs'),2)
        self.assertEqual(argv[-7:-2],[probe.IMAGE,'python','-I','-B','-c'])
        self.assertEqual(probe.sha(argv[-2].encode()),probe.CHILD_SHA)

    def test_extra_stage_content_and_nonfixture_source_refuse(self):
        extra=self.stage/'branch.snapshot'
        try:
            extra.write_bytes(b'synthetic forbidden extra')
            with self.assertRaisesRegex(probe.Refused,'SYNTHETIC_STAGE_EXACT_ONLY'):
                probe.projection(self.stage,self.claim,'a'*32)
        finally:extra.unlink()
        with self.assertRaisesRegex(probe.Refused,'PUBLIC_FIXTURE_PATHS'):
            probe.projection(probe.STAGE_TARGET,self.claim,'a'*32)

    def test_marker_and_child_pin_drift_refuse(self):
        with mock.patch.object(probe,'CHILD_SHA','0'*64):
            with self.assertRaisesRegex(probe.Refused,'PIN_DRIFT'):
                probe.projection(self.stage,self.claim,'a'*32)
        with mock.patch.object(probe,'PLAN_REVIEW_SHA','0'*64):
            with self.assertRaisesRegex(probe.Refused,'PIN_DRIFT'):
                probe.basis()
        with mock.patch.object(probe,'PREDECESSOR_REVIEW_SHA','0'*64):
            with self.assertRaisesRegex(probe.Refused,'PIN_DRIFT'):
                probe.basis()
        with mock.patch.object(probe,'PORTABLE_SHA','0'*64):
            with self.assertRaisesRegex(probe.Refused,'PIN_DRIFT'):
                probe.basis()
        old=self.claim.read_bytes()
        try:
            self.claim.write_bytes(b'forged public marker')
            with self.assertRaisesRegex(probe.Refused,'PIN_DRIFT'):
                probe.fixture(self.stage,self.claim)
        finally:self.claim.write_bytes(old)

    def test_child_mountinfo_exact_ro_and_no_nested(self):
        def mount(target,options='ro'):
            return f'1 0 0:1 / {target} {options} - ext4 /dev/x {options}\n'.encode()
        good=b''.join(mount(target) for target in child.TARGETS)
        self.assertEqual(child.mountinfo_ro(good),child.sha(good))
        for bad in (good+mount(child.TARGETS[0]+'/nested'),
                    good+mount(child.TARGETS[1]),
                    good.replace(mount(child.TARGETS[0]),mount(child.TARGETS[0],'rw'))):
            with self.assertRaisesRegex(RuntimeError,
                'NESTED_MOUNT_UNDER_PROBE_TARGET|THREE_VFS_READ_ONLY_BINDS'):
                child.mountinfo_ro(bad)

    def test_mountinfo_fragmented_read_rejects_nested_tail(self):
        def mount(target,options='ro'):
            return f'1 0 0:1 / {target} {options} - ext4 /dev/x {options}\n'.encode()
        clean=b''.join(mount(target) for target in child.TARGETS)
        nested=mount(child.TARGETS[0]+'/hidden')
        self.assertEqual(child.mountinfo_ro(clean),child.sha(clean))
        chunks=iter((clean,nested,b''))
        closed=[]
        raw=child.read_bounded('/synthetic/mountinfo',128*1024,
                               read_fn=lambda _fd,_size:next(chunks),
                               open_fn=lambda *_args:7,
                               close_fn=lambda fd:closed.append(fd),
                               clock_fn=lambda:0.0)
        self.assertEqual(raw,clean+nested)
        self.assertEqual(closed,[7])
        with self.assertRaisesRegex(RuntimeError,'NESTED_MOUNT_UNDER_PROBE_TARGET'):
            child.mountinfo_ro(raw)

    def test_mountinfo_reader_limits_refuse_without_prefix_acceptance(self):
        closed=[]
        with self.assertRaisesRegex(RuntimeError,'PUBLIC_READ_INCOMPLETE'):
            child.read_bounded('/synthetic',128*1024,
                               read_fn=lambda _fd,_size:b'x',
                               open_fn=lambda *_args:8,
                               close_fn=lambda fd:closed.append(fd),
                               clock_fn=lambda:0.0,max_calls=2)
        self.assertEqual(closed,[8])
        ticks=iter((0.0,0.0,3.0))
        with self.assertRaisesRegex(RuntimeError,'PUBLIC_READ_INCOMPLETE'):
            child.read_bounded('/synthetic',128*1024,
                               read_fn=lambda _fd,_size:b'x',
                               open_fn=lambda *_args:9,
                               close_fn=lambda fd:closed.append(fd),
                               clock_fn=lambda:next(ticks))
        self.assertEqual(closed[-1],9)
        chunks=iter((b'abcd',b'e'))
        with self.assertRaisesRegex(RuntimeError,'PUBLIC_READ_BOUND'):
            child.read_bounded('/synthetic',4,
                               read_fn=lambda _fd,_size:next(chunks),
                               open_fn=lambda *_args:10,
                               close_fn=lambda fd:closed.append(fd),
                               clock_fn=lambda:0.0)
        self.assertEqual(closed[-1],10)

    def test_child_erofs_requires_errno_30_and_no_sentinel(self):
        def denied(code):
            def run(*_args,**_kwargs):raise OSError(code,'synthetic')
            return run
        self.assertEqual(child.erofs_create('/synthetic',denied(errno.EROFS),lambda _:False),
                         errno.EROFS)
        for code in (errno.EACCES,errno.EPERM):
            with self.assertRaisesRegex(RuntimeError,'EROFS_CREATE'):
                child.erofs_create('/synthetic',denied(code),lambda _:False)
            with self.assertRaisesRegex(RuntimeError,'EROFS_CLAIM'):
                child.erofs_claim_write(denied(code))
        with self.assertRaisesRegex(RuntimeError,'SENTINEL_PREEXISTS'):
            child.erofs_create('/synthetic',denied(errno.EROFS),lambda _:True)

    def test_child_claim_identity_and_marker(self):
        st=os.stat(self.claim)
        self.assertEqual(child.read_bounded(self.claim,1024),probe.CLAIM_MARKER)
        with self.assertRaisesRegex(RuntimeError,'PUBLIC_READ_BOUND'):
            child.read_bounded(self.claim,4)
        config={'claim_dev':st.st_dev,'claim_ino':st.st_ino,
                'claim_marker_sha256':probe.sha(probe.CLAIM_MARKER)}
        child.verify_claim(st,probe.CLAIM_MARKER,config)
        for forged in (config|{'claim_dev':True},
                       config|{'claim_ino':float(st.st_ino)},
                       config|{'claim_ino':st.st_ino+1}):
            with self.assertRaisesRegex(RuntimeError,'HELD_PUBLIC_CLAIM_IDENTITY'):
                child.verify_claim(st,probe.CLAIM_MARKER,forged)
        with self.assertRaisesRegex(RuntimeError,'HELD_PUBLIC_CLAIM_MARKER'):
            child.verify_claim(st,b'forged marker',config)

    def test_readonly_docker_preflight_strict_returns(self):
        image=types.SimpleNamespace(returncode=0,stdout=
             f'{probe.IMAGE} amd64 20001:20001 /attempt/root\n'.encode(),stderr=b'')
        absent=types.SimpleNamespace(returncode=1,stdout=b'\n',stderr=
             ('Error response from daemon: No such container: '+probe.NAME+'\n').encode())
        def runner(argv,**_kwargs):
            return absent if argv[1:3]==['container','inspect'] else image
        self.assertTrue(probe.readonly_docker_preflight(runner)['name_absent'])
        for value in (False,0.0):
            image.returncode=value
            with self.assertRaisesRegex(probe.Refused,'DOCKER_IMAGE_PREFLIGHT'):
                probe.readonly_docker_preflight(runner)
        image.returncode=0
        for value in (True,1.0):
            absent.returncode=value
            with self.assertRaisesRegex(probe.Refused,'DOCKER_NAME_PREFLIGHT'):
                probe.readonly_docker_preflight(runner)

    def test_effect_unconditionally_refused(self):
        with self.assertRaisesRegex(probe.Refused,'EFFECT_DISABLED'):
            probe.dispatch()

if __name__=='__main__':unittest.main()
