"""Real synthetic subprocess tests. Commands cannot invoke Docker or private inputs."""
import os
import subprocess
import sys
import unittest
from unittest import mock
import release as R

SCRIPTS = {
    'both_bound': "import os;os.write(1,b'a'*65536);os.write(2,b'b'*65536)",
    'stdout_overflow': "import os;os.write(1,b'a'*262144);os.write(2,b'b'*262144)",
    'stderr_overflow': "import os;os.write(2,b'b'*262144);os.write(1,b'a'*262144)",
    'timeout': "import time;time.sleep(5)",
    'nonzero': "import os,sys;os.write(1,b'ok');os.write(2,b'err');sys.exit(7)",
}

class CaptureTests(unittest.TestCase):
    def run_case(self, key, timeout=2):
        observed=[]
        def synthetic_spawn(_argv, **kwargs):
            proc=subprocess.Popen([sys.executable,'-I','-B','-c',SCRIPTS[key]],**kwargs)
            observed.append(proc)
            return proc
        try:
            result=R.bounded_capture([R.DOCKER,'synthetic-no-docker-execution'],
                                     timeout=timeout,spawn=synthetic_spawn,env={})
            return result
        finally:
            self.assertEqual(len(observed),1)
            self.assertIsNotNone(observed[0].poll())
            self.assertTrue(observed[0].stdout.closed)
            self.assertTrue(observed[0].stderr.closed)

    def test_dual_stream_at_exact_inflight_bound(self):
        result=self.run_case('both_bound')
        self.assertEqual(result.returncode,0)
        self.assertEqual((len(result.stdout),len(result.stderr)),(65536,65536))

    def test_stdout_and_stderr_overflow_refuse_then_reap(self):
        for key in ('stdout_overflow','stderr_overflow'):
            with self.subTest(key=key),self.assertRaisesRegex(R.Refused,'DOCKER_STREAM_BOUND'):
                self.run_case(key)

    def test_timeout_refuses_then_reaps(self):
        with self.assertRaisesRegex(R.Refused,'DOCKER_CAPTURE_TIMEOUT'):
            self.run_case('timeout',timeout=0.1)

    def test_returncode_and_streams_are_exact(self):
        result=self.run_case('nonzero')
        self.assertEqual((result.returncode,result.stdout,result.stderr),(7,b'ok',b'err'))

    def test_docker_frontend_routes_only_to_bounded_capture(self):
        expected=subprocess.CompletedProcess([R.DOCKER,'ps'],0,b'',b'')
        with mock.patch.object(R,'bounded_capture',return_value=expected) as bounded:
            self.assertIs(R.docker_call([R.DOCKER,'ps']),expected)
            bounded.assert_called_once_with([R.DOCKER,'ps'],timeout=10,env=R.DOCKER_ENV)
        with self.assertRaisesRegex(R.Refused,'DOCKER_CALL_SCOPE'):
            R.docker_call([sys.executable,'-c','pass'])

class AttachedCaptureTests(unittest.TestCase):
    def test_attached_path_has_bounded_reader_and_no_communicate(self):
        import inspect
        body=inspect.getsource(R.run_once)
        self.assertIn('attached_thread.start()',body)
        self.assertIn('drain_streams(process,deadline)',body)
        self.assertNotIn('.communicate(',body)
