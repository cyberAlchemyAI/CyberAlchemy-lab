"""Fake-daemon fault tests plus one read-only live Docker absence check."""
from __future__ import annotations

import copy
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

import controller as c


class FakeDocker:
    CID = "a" * 64

    def __init__(self, mode: str, family: Path):
        self.mode = mode
        self.family = family
        self.info = None
        self.calls = []

    def inspected(self, name):
        self.calls.append(("inspect", name))
        return copy.deepcopy(self.info)

    def cli(self, argv, *, seconds=12.0):
        self.calls.append(tuple(argv[:3]))
        action = argv[1]
        if action == "create":
            if self.mode == "create_lost":
                return subprocess.CompletedProcess(argv, 1, b"", b"lost create response")
            label = argv[argv.index("--label") + 1].split("=", 1)[1]
            self.info = {"Id": self.CID, "Name": "/" + c.NAME, "Image": c.IMAGE,
                         "Config": {"Image": c.IMAGE,
                                    "Labels": {"cal.source.attempt": label}},
                         "State": {"Running": False, "Status": "created", "ExitCode": 0}}
            return subprocess.CompletedProcess(argv, 0, (self.CID + "\n").encode(), b"")
        if action == "stop":
            if self.mode == "stop_timeout":
                raise subprocess.TimeoutExpired(argv, seconds)
            if self.mode == "cleanup_lost":
                return subprocess.CompletedProcess(argv, 1, b"", b"daemon unavailable")
            self.info["State"]["Running"] = False
            self.info["State"]["ExitCode"] = 137
            return subprocess.CompletedProcess(argv, 0, (self.CID + "\n").encode(), b"")
        if action == "kill":
            if self.mode == "cleanup_lost":
                return subprocess.CompletedProcess(argv, 1, b"", b"daemon unavailable")
            self.info["State"]["Running"] = False
            self.info["State"]["ExitCode"] = 137
            return subprocess.CompletedProcess(argv, 0, (self.CID + "\n").encode(), b"")
        if action == "wait":
            if self.mode == "late_stop_wait":
                c.STOP_REQUESTED = True
            code = 0 if self.mode in ("success", "stream_overflow", "unexpected_extra",
                                      "late_stop_wait", "rm_crash") else 137
            return subprocess.CompletedProcess(argv, 0, (str(code) + "\n").encode(), b"")
        if action == "rm":
            if self.mode == "rm_crash":
                raise OSError("fake controller crash immediately before Docker rm")
            self.info = None
            return subprocess.CompletedProcess(argv, 0, (self.CID + "\n").encode(), b"")
        raise AssertionError(argv)

    def capture(self, cid, stdout, stderr):
        self.calls.append(("start", cid))
        if self.mode == "never_started":
            raise TimeoutError("fake Docker start response lost before launch")
        self.info["State"]["Running"] = True
        self.info["State"]["Status"] = "running"
        if self.mode == "client_lost":
            raise TimeoutError("fake Docker client died while daemon continued")
        if self.mode == "cleanup_lost":
            raise TimeoutError("fake Docker client died while daemon continued")
        if self.mode == "stop_timeout":
            raise TimeoutError("fake Docker client died while daemon continued")
        if self.mode == "deadline":
            return None, True
        package = self.family / "packages/0001"
        package.mkdir()
        member = package / "build-result.json"
        member.write_text('{"result":"PASS"}\n')
        manifest = {"files": [{"path":
                    "product/lab/release-candidates/v1/interface/docker-source-20261020-0001/packages/0001/build-result.json",
                    "sha256": c.sha(member.read_bytes())}]}
        (package / "manifest.json").write_bytes(c.json_bytes(manifest))
        if self.mode == "unexpected_extra":
            (self.family.parents[4] / "unexpected.txt").write_text("extra")
        source = {"result": "PASS", "cold_replay": "PASS",
                  "signed_transactions": 2, "authored_records": 11,
                  "authored_typed_relations": 10,
                  "source_manifest_sha256": "b" * 64,
                  "package_manifest_sha256": c.sha((package / "manifest.json").read_bytes()),
                  "authority_effect": "none", "actual_owner_outcome": None}
        stdout.write_bytes(c.json_bytes(source))
        self.info["State"]["Running"] = False
        self.info["State"]["Status"] = "exited"
        self.info["State"]["ExitCode"] = 0
        if self.mode == "stream_overflow":
            return 0, True
        return 0, False


class ControllerTests(unittest.TestCase):
    def setUp(self):
        c.STOP_REQUESTED = False
        self.addCleanup(lambda: setattr(c, "STOP_REQUESTED", False))
        self.temporary = tempfile.TemporaryDirectory(prefix="cal-fake-source-controller-")
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.base = root / "tool"
        self.base.mkdir()
        self.attempt = root / "attempt"
        self.root = self.attempt / "root"
        self.family = self.root / "product/lab/release-candidates/v1/interface/docker-source-20261020-0001"
        for name in ("packages", "receipts"):
            (self.family / name).mkdir(parents=True, mode=0o700)
        self.evidence = self.attempt / "evidence"
        self.evidence.mkdir(mode=0o700)
        self.plan = {"public_inputs": [], "generated_bindings": [],
                     "source_manifest": {"sha256": "b" * 64}}

    def execute_fake(self, mode):
        fake = FakeDocker(mode, self.family)
        with mock.patch.multiple(c, BASE=self.base, ATTEMPT=self.attempt, ROOT=self.root,
                                 FAMILY=self.family, EVIDENCE=self.evidence), \
             mock.patch.object(c, "frozen_inputs", return_value=self.plan), \
             mock.patch.object(c, "inspected", side_effect=fake.inspected), \
             mock.patch.object(c, "cli", side_effect=fake.cli), \
             mock.patch.object(c, "capture_start", side_effect=fake.capture):
            result = c.run()
        return fake, result

    def test_clean_owned_exit_and_no_replace_terminal(self):
        fake, result = self.execute_fake("success")
        self.assertEqual(result["overall"], "PASS")
        self.assertEqual(result["daemon_exit"], 0)
        self.assertIsNone(fake.info)
        self.assertEqual(json.loads((self.evidence / "source-once.terminal.json").read_bytes()), result)
        self.assertTrue((self.evidence / "source-attempt-consumed.json").is_file())
        self.assertTrue((self.evidence / "source-pre-removal.json").is_file())

    def test_selected_absence_diagnostics_are_anchored(self):
        name = c.NAME
        for stderr in (f"error: no such object: {name}\n".encode(),
                       f"Error: No Such Object: {name} \n".encode(),
                       f"error: no such container: {name}\n".encode()):
            with self.subTest(stderr=stderr), mock.patch.object(
                    c, "cli", return_value=subprocess.CompletedProcess([], 1, b"[]\n", stderr)):
                self.assertIsNone(c.inspected(name))

    def test_misleading_absence_substring_and_transport_are_ambiguous(self):
        name = c.NAME
        cases = (
            (1, b"[]\n", f"daemon unavailable; error: no such object: {name}\n".encode()),
            (1, b"[]\n", f"error: no such object: {name}-other\n".encode()),
            (1, b"[]\n", f"error: no such object: {name.upper()}\n".encode()),
            (1, b"[]\n", f"ERROR: NO SUCH OBJECT: {name.upper()}\n".encode()),
            (1, b"[]\n", f"error: no such object: {name.replace('cal', 'Cal', 1)}\n".encode()),
            (1, b"partial", f"error: no such object: {name}\n".encode()),
            (2, b"[]\n", f"error: no such object: {name}\n".encode()),
            (1, b"[]\n", b"Cannot connect to the Docker daemon\n"),
        )
        for code, stdout, stderr in cases:
            with self.subTest(stderr=stderr), mock.patch.object(
                    c, "cli", return_value=subprocess.CompletedProcess([], code, stdout, stderr)), \
                 self.assertRaisesRegex(ValueError, "ambiguous"):
                c.inspected(name)

    def test_live_selected_name_absent_read_only(self):
        # This is a Docker inspect only. It never creates/starts a container.
        self.assertIsNone(c.inspected(c.NAME))

    def test_lost_create_response_consumes_without_retry(self):
        fake, result = self.execute_fake("create_lost")
        self.assertEqual(result["overall"], "UNKNOWN")
        self.assertTrue(result["no_retry"])
        self.assertIsNone(fake.info)
        self.assertTrue((self.evidence / "source-attempt-consumed.json").is_file())
        with self.assertRaises(FileExistsError):
            c.exclusive(self.evidence / "source-attempt-consumed.json", b"again")

    def test_client_dies_daemon_continues_owned_cleanup(self):
        fake, result = self.execute_fake("client_lost")
        self.assertEqual(result["overall"], "UNKNOWN")
        self.assertEqual(result["daemon_exit"], 137)
        self.assertIsNone(fake.info)
        self.assertIn((c.DOCKER, "stop", "--time"), fake.calls)
        self.assertTrue(result["absent"])

    def test_lost_daemon_cleanup_retains_unknown(self):
        fake, result = self.execute_fake("cleanup_lost")
        self.assertEqual(result["overall"], "UNKNOWN")
        self.assertTrue(result["no_retry"])
        self.assertTrue(fake.info["State"]["Running"])
        self.assertIn("cleanup_error_class", result)

    def test_stop_timeout_reinspects_then_kills_only_owned_container(self):
        fake, result = self.execute_fake("stop_timeout")
        self.assertEqual(result["overall"], "UNKNOWN")
        self.assertTrue(result["forced_cleanup"])
        self.assertIsNone(fake.info)
        self.assertIn((c.DOCKER, "kill", FakeDocker.CID), fake.calls)

    def test_created_never_started_is_removed_without_wait(self):
        fake, result = self.execute_fake("never_started")
        self.assertEqual(result["overall"], "UNKNOWN")
        self.assertEqual(result["cleanup"], "removed_unstarted")
        self.assertIsNone(fake.info)
        self.assertNotIn((c.DOCKER, "wait", FakeDocker.CID), fake.calls)

    def test_deadline_stops_daemon_and_consumes_unknown(self):
        fake, result = self.execute_fake("deadline")
        self.assertEqual(result["overall"], "UNKNOWN")
        self.assertTrue(result["stream_or_deadline_failure"])
        self.assertTrue(result["forced_cleanup"])
        self.assertIsNone(fake.info)

    def test_stream_overflow_cannot_pass_even_with_exit_zero(self):
        fake, result = self.execute_fake("stream_overflow")
        self.assertEqual(result["overall"], "UNKNOWN")
        self.assertEqual(result["daemon_exit"], 0)
        self.assertTrue(result["stream_or_deadline_failure"])
        self.assertIsNone(fake.info)

    def test_extra_regular_file_outside_outputs_refuses_pass(self):
        fake, result = self.execute_fake("unexpected_extra")
        self.assertEqual(result["overall"], "UNKNOWN")
        self.assertIn("postclose_error_class", result)
        self.assertIsNone(fake.info)

    def test_late_stop_during_daemon_wait_refuses_pass(self):
        fake, result = self.execute_fake("late_stop_wait")
        self.assertEqual(result["daemon_exit"], 0)
        self.assertEqual(result["overall"], "UNKNOWN")
        self.assertTrue(result["no_retry"])
        self.assertIsNone(fake.info)

    def test_late_stop_during_postclose_refuses_pass(self):
        real_inventory = c.output_inventory
        def interrupted_inventory():
            value = real_inventory()
            c.STOP_REQUESTED = True
            return value
        with mock.patch.object(c, "output_inventory", side_effect=interrupted_inventory):
            fake, result = self.execute_fake("success")
        self.assertEqual(result["overall"], "UNKNOWN")
        self.assertIsNone(fake.info)

    def test_stop_immediately_before_terminal_commit_refuses_pass(self):
        real_mask = signal.pthread_sigmask
        def signal_at_commit(how, mask):
            if how == signal.SIG_BLOCK:
                c.STOP_REQUESTED = True
            return real_mask(how, mask)
        with mock.patch.object(c.signal, "pthread_sigmask", side_effect=signal_at_commit):
            fake, result = self.execute_fake("success")
        self.assertEqual(result["daemon_exit"], 0)
        self.assertEqual(result["overall"], "UNKNOWN")
        self.assertTrue(result["interrupted"])
        self.assertIsNone(fake.info)

    def test_pre_removal_receipt_survives_rm_crash(self):
        fake, result = self.execute_fake("rm_crash")
        self.assertEqual(result["overall"], "UNKNOWN")
        self.assertIsNotNone(fake.info)
        receipt = json.loads((self.evidence / "source-pre-removal.json").read_bytes())
        self.assertEqual(receipt["container"]["id"], FakeDocker.CID)
        self.assertEqual(receipt["daemon_wait_exit"], 0)
        fake.mode = "client_lost"
        with mock.patch.multiple(c, BASE=self.base, ATTEMPT=self.attempt, ROOT=self.root,
                                 FAMILY=self.family, EVIDENCE=self.evidence), \
             mock.patch.object(c, "inspected", side_effect=fake.inspected), \
             mock.patch.object(c, "cli", side_effect=fake.cli):
            recovered = c.recover_consumed()
        self.assertEqual(recovered["operation"], "UNKNOWN")
        self.assertEqual(recovered["prior_daemon_wait_exit"], 0)
        self.assertEqual(recovered["prior_pre_removal_sha256"],
                         c.sha((self.evidence / "source-pre-removal.json").read_bytes()))
        self.assertIsNone(fake.info)

    def test_receipt_write_failure_keeps_container_and_unknown(self):
        real_exclusive = c.exclusive
        def fail_receipt(path, raw):
            if path.name == "source-pre-removal.json":
                raise OSError("fake receipt storage failure")
            return real_exclusive(path, raw)
        with mock.patch.object(c, "exclusive", side_effect=fail_receipt):
            fake, result = self.execute_fake("success")
        self.assertEqual(result["overall"], "UNKNOWN")
        self.assertIsNotNone(fake.info)
        self.assertFalse(fake.info["State"]["Running"])
        self.assertFalse((self.evidence / "source-pre-removal.json").exists())

    def test_fifo_in_receipts_refused_without_opening_it(self):
        os.mkfifo(self.family / "receipts" / "unexpected.fifo")
        with mock.patch.object(c, "FAMILY", self.family), \
             self.assertRaisesRegex(ValueError, "nonregular output entry"):
            c.output_inventory()

    def test_fifo_outside_outputs_refused_by_staged_tree_inventory(self):
        os.mkfifo(self.root / "unexpected.fifo")
        with self.assertRaisesRegex(ValueError, "nonregular staged tree entry"):
            c.tree_names(self.root)

    def test_cleanup_only_recovery_never_restarts_source(self):
        fake, first = self.execute_fake("cleanup_lost")
        self.assertEqual(first["overall"], "UNKNOWN")
        fake.mode = "client_lost"
        fake.calls.clear()
        with mock.patch.multiple(c, BASE=self.base, ATTEMPT=self.attempt, ROOT=self.root,
                                 FAMILY=self.family, EVIDENCE=self.evidence), \
             mock.patch.object(c, "inspected", side_effect=fake.inspected), \
             mock.patch.object(c, "cli", side_effect=fake.cli):
            recovered = c.recover_consumed()
        self.assertTrue(recovered["absent"])
        self.assertEqual(recovered["operation"], "UNKNOWN")
        self.assertIsNone(fake.info)
        self.assertFalse(any(call[0] == "start" or call[:2] == (c.DOCKER, "create")
                             for call in fake.calls))

    def test_recovery_refuses_substituted_container_identity(self):
        fake, first = self.execute_fake("cleanup_lost")
        self.assertEqual(first["overall"], "UNKNOWN")
        fake.info["Config"]["Labels"]["cal.source.attempt"] = "wrong"
        fake.calls.clear()
        with mock.patch.multiple(c, BASE=self.base, ATTEMPT=self.attempt, ROOT=self.root,
                                 FAMILY=self.family, EVIDENCE=self.evidence), \
             mock.patch.object(c, "inspected", side_effect=fake.inspected), \
             mock.patch.object(c, "cli", side_effect=fake.cli):
            recovered = c.recover_consumed()
        self.assertIn("cleanup_error_class", recovered)
        self.assertTrue(fake.info["State"]["Running"])
        self.assertNotIn((c.DOCKER, "stop", "--time"), fake.calls)
        self.assertNotIn((c.DOCKER, "kill", FakeDocker.CID), fake.calls)

    def test_real_pipe_capture_bounds_without_docker(self):
        real_popen = subprocess.Popen
        def fake_popen(_argv, **kwargs):
            return real_popen([sys.executable, "-B", "-c",
                               "import sys; sys.stdout.write('x'*100); sys.stderr.write('y'*100)"],
                              **kwargs)
        out, err = self.evidence / "pipe.stdout", self.evidence / "pipe.stderr"
        out.write_bytes(b"")
        err.write_bytes(b"")
        with mock.patch.object(c.subprocess, "Popen", side_effect=fake_popen), \
             mock.patch.object(c, "MAX_STREAM", 16):
            code, overflow = c.capture_start(FakeDocker.CID, out, err)
        self.assertEqual(code, 0)
        self.assertTrue(overflow)
        self.assertEqual(len(out.read_bytes()), 16)
        self.assertEqual(len(err.read_bytes()), 16)

    def test_real_pipe_capture_deadline_without_docker(self):
        real_popen = subprocess.Popen
        def fake_popen(_argv, **kwargs):
            return real_popen([sys.executable, "-B", "-c",
                               "import time; time.sleep(1)"], **kwargs)
        out, err = self.evidence / "deadline.stdout", self.evidence / "deadline.stderr"
        out.write_bytes(b"")
        err.write_bytes(b"")
        with mock.patch.object(c.subprocess, "Popen", side_effect=fake_popen), \
             mock.patch.object(c, "DEADLINE", 0.05):
            code, timed_out = c.capture_start(FakeDocker.CID, out, err)
        self.assertIsNone(code)
        self.assertTrue(timed_out)

    def test_stop_request_shortens_real_pipe_capture(self):
        real_popen = subprocess.Popen
        def fake_popen(_argv, **kwargs):
            return real_popen([sys.executable, "-B", "-c",
                               "import time; time.sleep(1)"], **kwargs)
        out, err = self.evidence / "signal.stdout", self.evidence / "signal.stderr"
        out.write_bytes(b"")
        err.write_bytes(b"")
        timer = threading.Timer(0.05, lambda: setattr(c, "STOP_REQUESTED", True))
        timer.start()
        try:
            with mock.patch.object(c.subprocess, "Popen", side_effect=fake_popen):
                code, stopped = c.capture_start(FakeDocker.CID, out, err)
        finally:
            timer.join()
            c.STOP_REQUESTED = False
        self.assertIsNone(code)
        self.assertTrue(stopped)

    def test_selector_setup_failure_reaps_owned_client(self):
        real_popen = subprocess.Popen
        children = []
        def fake_popen(_argv, **kwargs):
            child = real_popen([sys.executable, "-B", "-c",
                                "import time; time.sleep(2)"], **kwargs)
            children.append(child)
            return child
        out, err = self.evidence / "setup.stdout", self.evidence / "setup.stderr"
        out.write_bytes(b"")
        err.write_bytes(b"")
        with mock.patch.object(c.subprocess, "Popen", side_effect=fake_popen), \
             mock.patch.object(c.selectors, "DefaultSelector", side_effect=OSError("selector setup lost")), \
             self.assertRaisesRegex(OSError, "selector setup lost"):
            c.capture_start(FakeDocker.CID, out, err)
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].poll())
        self.assertTrue(children[0].stdout.closed)
        self.assertTrue(children[0].stderr.closed)

    def test_log_open_failure_reaps_owned_client(self):
        real_popen = subprocess.Popen
        real_open = Path.open
        children = []
        def fake_popen(_argv, **kwargs):
            child = real_popen([sys.executable, "-B", "-c",
                                "import time; time.sleep(2)"], **kwargs)
            children.append(child)
            return child
        def fake_open(path, *args, **kwargs):
            if path.name == "logfail.stdout":
                raise OSError("log open lost")
            return real_open(path, *args, **kwargs)
        out, err = self.evidence / "logfail.stdout", self.evidence / "logfail.stderr"
        out.write_bytes(b"")
        err.write_bytes(b"")
        with mock.patch.object(c.subprocess, "Popen", side_effect=fake_popen), \
             mock.patch.object(Path, "open", fake_open), \
             self.assertRaisesRegex(OSError, "log open lost"):
            c.capture_start(FakeDocker.CID, out, err)
        self.assertIsNotNone(children[0].poll())
        self.assertTrue(children[0].stdout.closed)
        self.assertTrue(children[0].stderr.closed)

    def test_mid_drain_failure_reaps_owned_client(self):
        real_popen = subprocess.Popen
        children = []
        def fake_popen(_argv, **kwargs):
            child = real_popen([sys.executable, "-B", "-c",
                                "import sys,time; sys.stdout.write('data'); sys.stdout.flush(); time.sleep(2)"],
                               **kwargs)
            children.append(child)
            return child
        out, err = self.evidence / "drain.stdout", self.evidence / "drain.stderr"
        out.write_bytes(b"")
        err.write_bytes(b"")
        with mock.patch.object(c.subprocess, "Popen", side_effect=fake_popen), \
             mock.patch.object(c.os, "read", side_effect=OSError("drain lost")), \
             self.assertRaisesRegex(OSError, "drain lost"):
            c.capture_start(FakeDocker.CID, out, err)
        self.assertIsNotNone(children[0].poll())
        self.assertTrue(children[0].stdout.closed)
        self.assertTrue(children[0].stderr.closed)

    def test_cleanup_failure_preserves_primary_and_reports_uncertainty(self):
        class BrokenClient:
            def __init__(self):
                self.stdout = io.BytesIO()
                self.stderr = io.BytesIO()
            def poll(self):
                return None
            def terminate(self):
                raise OSError("owned client terminate lost")
        child = BrokenClient()
        out, err = self.evidence / "broken.stdout", self.evidence / "broken.stderr"
        with mock.patch.object(c.subprocess, "Popen", return_value=child), \
             mock.patch.object(c.selectors, "DefaultSelector", side_effect=OSError("selector primary lost")):
            with self.assertRaises(BaseExceptionGroup) as caught:
                c.capture_start(FakeDocker.CID, out, err)
        self.assertIn("selector primary lost", str(caught.exception.exceptions[0]))
        self.assertIn("owned client terminate lost", str(caught.exception.exceptions[1]))
        self.assertTrue(child.stdout.closed)
        self.assertTrue(child.stderr.closed)


if __name__ == "__main__":
    unittest.main()
