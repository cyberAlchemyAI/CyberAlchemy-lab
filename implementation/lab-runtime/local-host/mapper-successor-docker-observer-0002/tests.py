"""Causal public-fixture tests; never dispatch the reviewed Mapper release."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import unittest

import observer as o


def terminal():
    return {'schema_version':'lab-mapper-docker-one-shot-evidence/v2',
            'name':o.NAME,'phase':'TERMINAL','overall':'PASS',
            'cleanup':'PASS','container_absent':True,'create_attempted':True,
            'client_exit':0,'daemon_exit':0,'daemon_exit_consistent':True,
            'container_id':'e'*64}


def final():
    return {'schema':'lab-mapper-successor-docker-final/v1',
            'overall':'OBSERVED_DOCKER_ONLY','attempt':str(o.ATTEMPT),
            'stage_effect_review_sha256':o.STAGE_REVIEW_SHA,'no_retry':True,
            'authority_effect':'none','actual_owner_outcome':None,
            'original_task_acceptance':False,
            'requires_external_exit_zero_and_independent_effect_review':True,
            'terminal_sha256':o.sha((json.dumps(terminal(),sort_keys=True)+'\n').encode()),
            'output':{'schema':'lab-mapper-successor-output-verification/v1',
                      'result':'PASS_CANDIDATE_OUTPUT_ONLY',
                      'manifest_sha256':'d'*64,'files':55,
                      'semantic_leaves':25,'governance_leaves':25,
                      'exact_governance_joins':25,'authority_effect':'none',
                      'actual_owner_outcome':None,'task_complete':False}}


def selected():
    return {'effect':'NOT_RUN','release':{
        'freeze_sha256':o.FREEZE_SHA,'review_sha256':o.REVIEW_SHA,
        'release_sha256':o.RELEASE_SHA},'preflight_stdout_sha256':'b'*64}


class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=o.HERE)
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name)
        os.chmod(self.parent,0o700)
        self.root = self.parent/'observation'
        self.process = None

    def run_fixture(self,stdout,stderr=b'',exit_code=0,delay=0,preflight=selected,
                    final_raw=None,terminal_raw=None,limit=None,interrupt=False):
        if final_raw is None: final_raw = o.wire(final())
        if terminal_raw is None:
            terminal_raw = (json.dumps(terminal(),sort_keys=True)+'\n').encode()
        source = ('import sys,time; time.sleep(%r); '
                  'sys.stdout.buffer.write(bytes.fromhex(%r)); '
                  'sys.stderr.buffer.write(bytes.fromhex(%r)); '
                  'sys.exit(%r)') % (delay,stdout.hex(),stderr.hex(),exit_code)
        def spawn(argv,**kwargs):
            self.assertEqual(argv,o.COMMAND)
            self.assertTrue(kwargs['start_new_session'])
            self.process = subprocess.Popen([sys.executable,'-c',source],**kwargs)
            if interrupt:
                timer = threading.Timer(.04,lambda: os.kill(os.getpid(),signal.SIGINT))
                timer.start()
                self.addCleanup(timer.join)
            return self.process
        if limit is not None:
            original = o.capture_process
            def capture(*args,**kwargs): return original(*args,limit=limit,**kwargs)
            o.capture_process = capture
            self.addCleanup(setattr,o,'capture_process',original)
        try:
            return o._run_once(observation=self.root,preflight_fn=preflight,
                               spawn=spawn,final_reader=lambda:final_raw,
                               terminal_reader=lambda:terminal_raw)
        finally:
            if self.process is not None:
                self.assertIsNotNone(self.process.poll(),'child must be reaped')

    def record(self):
        selected = self.root/'observation.json'
        if not selected.exists(): selected = self.root/'capture.json'
        return json.loads(selected.read_bytes())

    def test_real_process_success_raw_join_and_no_retry(self):
        raw = (json.dumps(final(),sort_keys=True)+'\n').encode()
        result = self.run_fixture(raw)
        self.assertEqual(result['status'],'PROVISIONAL_OS_ZERO_FINAL_JOIN')
        self.assertEqual((self.root/'stdout').read_bytes(),raw)
        self.assertEqual((self.root/'stderr').read_bytes(),b'')
        self.assertEqual(self.record()['status'],'PROVISIONAL_OS_ZERO_FINAL_JOIN')
        self.assertEqual((self.root.stat().st_mode & 0o777),0o700)
        for name in ('consumed.json','intent.json','stdout','stderr','capture.json',
                     'observation.json'):
            self.assertEqual(((self.root/name).stat().st_mode & 0o777),0o600)
        with self.assertRaises(o.Refused):
            self.run_fixture(raw)

    def test_nonzero_exit_preserves_exact_raw_streams(self):
        with self.assertRaises(o.Refused):
            self.run_fixture(b'public-out\n',b'public-error\n',23)
        record = self.record()
        self.assertEqual(record['status'],'UNKNOWN_PRESERVE_NO_RETRY')
        self.assertEqual(record['capture']['exit_code'],23)
        self.assertEqual((self.root/'stdout').read_bytes(),b'public-out\n')
        self.assertEqual((self.root/'stderr').read_bytes(),b'public-error\n')

    def test_late_stderr_after_stdout_is_unknown(self):
        raw = (json.dumps(final(),sort_keys=True)+'\n').encode()
        with self.assertRaises(o.Refused): self.run_fixture(raw,b'late\n')
        self.assertEqual(self.record()['capture']['counts'][1],5)
        self.assertEqual(self.record()['status'],'UNKNOWN_PRESERVE_NO_RETRY')

    def test_final_join_mismatch_is_unknown(self):
        raw = (json.dumps(final(),sort_keys=True)+'\n').encode()
        changed = final(); changed['terminal_sha256'] = 'c'*64
        with self.assertRaises(o.Refused): self.run_fixture(raw,final_raw=o.wire(changed))
        self.assertEqual(self.record()['status'],'UNKNOWN_PRESERVE_NO_RETRY')

    def test_terminal_absence_mismatch_is_unknown(self):
        raw = (json.dumps(final(),sort_keys=True)+'\n').encode()
        changed = terminal(); changed['container_absent'] = False
        with self.assertRaises(o.Refused):
            self.run_fixture(raw,terminal_raw=(json.dumps(changed,sort_keys=True)+'\n').encode())
        self.assertEqual(self.record()['status'],'UNKNOWN_PRESERVE_NO_RETRY')

    def test_postclose_publication_failure_keeps_consumed_pending(self):
        raw = (json.dumps(final(),sort_keys=True)+'\n').encode()
        original = o.postclose_write
        def fail(*_args): raise OSError('fixture postclose failure')
        o.postclose_write = fail
        self.addCleanup(setattr,o,'postclose_write',original)
        with self.assertRaises(OSError): self.run_fixture(raw)
        self.assertTrue((self.root/'consumed.json').is_file())
        self.assertFalse((self.root/'observation.json').exists())
        self.assertEqual(self.record()['status'],'REAPED_PENDING_POSTCLOSE')

    def test_r01_partial_stream_setup_closes_returned_stdout(self):
        raw = (json.dumps(final(),sort_keys=True)+'\n').encode()
        original = o.Observation.create_stream
        owned = []
        def fail_stderr(instance,name):
            if name == 'stderr': raise OSError('fixture stderr setup')
            fd = original(instance,name)
            owned.append(fd)
            return fd
        o.Observation.create_stream = fail_stderr
        self.addCleanup(setattr,o.Observation,'create_stream',original)
        with self.assertRaises(o.Refused): self.run_fixture(raw)
        self.assertEqual(len(owned),1)
        with self.assertRaises(OSError): os.fstat(owned[0])
        self.assertIsNone(self.process)
        self.assertEqual(self.record()['status'],'UNKNOWN_PRESERVE_NO_RETRY')

    def test_r01_local_create_stream_chmod_failure_closes_open_fd(self):
        observation = o.Observation(self.root)
        observation.claim()
        opened = []
        real_open,real_fchmod = os.open,os.fchmod
        def tracking_open(path,*args,**kwargs):
            fd = real_open(path,*args,**kwargs)
            if path == 'stdout': opened.append(fd)
            return fd
        def failing_chmod(*_args): raise OSError('fixture fchmod')
        os.open,os.fchmod = tracking_open,failing_chmod
        try:
            with self.assertRaises(OSError): observation.create_stream('stdout')
        finally:
            os.open,os.fchmod = real_open,real_fchmod
            observation.close()
        self.assertEqual(len(opened),1)
        with self.assertRaises(OSError): os.fstat(opened[0])

    def test_r02_close_then_raise_never_retries_reused_number(self):
        first = os.open(self.parent/'first',os.O_RDWR|os.O_CREAT|os.O_EXCL,0o600)
        second = os.open(self.parent/'second',os.O_RDWR|os.O_CREAT|os.O_EXCL,0o600)
        ledger = [first,second]
        real_close = os.close
        foreign = []
        def reused_close(fd):
            if fd == first and not foreign:
                real_close(fd)
                foreign.append(os.open(self.parent/'foreign',
                                       os.O_RDWR|os.O_CREAT|os.O_EXCL,0o600))
                raise OSError('fixture close after release')
            return real_close(fd)
        os.close = reused_close
        try:
            with self.assertRaises(OSError): o.close_streams(ledger)
        finally:
            os.close = real_close
        self.assertEqual(ledger,[])
        self.assertEqual(foreign,[first])
        os.write(foreign[0],b'foreign remains owned')
        self.assertEqual(os.fstat(foreign[0]).st_size,21)
        real_close(foreign[0])
        with self.assertRaises(OSError): os.fstat(second)

    def test_r03_postclose_and_read_teardown_closes_all_after_error(self):
        observation = o.Observation(self.root)
        observation.claim()
        identity = observation.identity
        observation.close()
        real_open,real_close = os.open,os.close
        tracked = []
        fired = []
        def tracking_open(*args,**kwargs):
            fd = real_open(*args,**kwargs)
            tracked.append(fd)
            return fd
        def close_then_raise(fd):
            real_close(fd)
            if not fired:
                fired.append(fd)
                raise OSError('fixture first close after release')
        os.open,os.close = tracking_open,close_then_raise
        try:
            with self.assertRaises(OSError):
                o.postclose_write(self.root,identity,'observation.json',b'{}\n')
        finally:
            os.open,os.close = real_open,real_close
        self.assertTrue(fired)
        for fd in tracked:
            with self.assertRaises(OSError): os.fstat(fd)
        fixture = self.parent/'read-fixture'
        fixture.write_bytes(b'public')
        tracked.clear(); fired.clear()
        os.open,os.close = tracking_open,close_then_raise
        try:
            with self.assertRaises(OSError): o.read_regular(fixture)
        finally:
            os.open,os.close = real_open,real_close
        self.assertTrue(fired)
        for fd in tracked:
            with self.assertRaises(OSError): os.fstat(fd)

    def test_capture_overflow_drains_child_and_retains_prefix(self):
        with self.assertRaises(o.Refused): self.run_fixture(b'abcdef',limit=3)
        self.assertEqual((self.root/'stdout').read_bytes(),b'abc')
        self.assertEqual(self.record()['capture']['counts'][0],6)
        self.assertTrue(self.record()['capture']['overflow'])

    def test_interruption_keeps_child_until_reaped_and_is_unknown(self):
        raw = (json.dumps(final(),sort_keys=True)+'\n').encode()
        with self.assertRaises(o.Refused): self.run_fixture(raw,delay=.2,interrupt=True)
        capture = self.record()['capture']
        self.assertEqual(capture['exit_code'],0)
        self.assertEqual(capture['signals'],[signal.SIGINT])
        self.assertTrue(capture['child_preserved_after_signal'])
        self.assertEqual(self.record()['status'],'UNKNOWN_PRESERVE_NO_RETRY')

    def test_same_state_refusal_has_no_claim_or_spawn(self):
        bad = selected(); bad['release']['freeze_sha256'] = '0'*64
        with self.assertRaises(o.Refused):
            self.run_fixture(b'',preflight=lambda:bad)
        self.assertFalse(self.root.exists())
        self.assertIsNone(self.process)

    def test_cli_effect_is_disabled(self):
        result = subprocess.run([sys.executable,'-B',str(o.HERE/'observer.py'),
                                 '--execute-reviewed-one-shot'],capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(self.root.exists())


if __name__ == '__main__': unittest.main(verbosity=2)
