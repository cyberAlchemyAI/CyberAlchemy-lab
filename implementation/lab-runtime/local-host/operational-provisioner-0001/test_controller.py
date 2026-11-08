import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from datetime import datetime, timedelta, timezone

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("operational_provisioner", HERE / "controller.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def write(path, raw, mode=0o600):
    with open(path, "xb") as handle:
        handle.write(raw)
    os.chmod(path, mode)
    return module.digest(raw)


class ProvisionerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cal-operational-provisioner-test-", dir="/tmp")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.custody = self.root / "custody"
        self.custody.mkdir(mode=0o700)
        self.rollback = self.root / "retained-old-store"
        self.rollback.mkdir(mode=0o700)
        self.engine = self.root / "engine.py"
        self.profile = self.root / "profile.json"
        self.base_head = self.root / "HEAD.json"
        self.key = self.custody / "operator.pem"
        self.policy = self.custody / "reader-policy.json"
        key_sha256 = write(self.key, b"test-only-key")
        expiry = (datetime.now(timezone.utc) + timedelta(minutes=20)).isoformat()
        self.policy_value = {"host_uid": os.getuid(), "principal_ref": "role:local-operator",
                             "source_name": "source8-session-participation",
                             "scope_refs": ["scope:lab-runtime-local:test-store"],
                             "expires_at": expiry, "revoked": False,
                             "authority_effect": "none"}
        self.plan = {"schema_version": module.VERSION, "store_id": "test-store",
                     "operator_ref": "role:local-operator",
                     "scope_ref": "scope:lab-runtime-local:test-store", "owner_uid": os.getuid(),
                     "engine_path": str(self.engine), "engine_sha256": write(self.engine, b"engine-v1"),
                     "profile_path": str(self.profile), "profile_sha256": write(self.profile, b"profile-v1"),
                     "base_head_path": str(self.base_head), "base_head_sha256": write(self.base_head, b"head-v1"),
                     "store_path": str(self.root / "owned-store"),
                     "rollback_path": str(self.rollback), "private_key_path": str(self.key),
                     "private_key_sha256": key_sha256,
                     "custody_policy_path": str(self.policy),
                     "custody_policy_sha256": write(self.policy, json.dumps(self.policy_value).encode()),
                     "channel_root_path": str(self.root / "per-run-channels"),
                     "source_name": "source8-session-participation",
                     "source_expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()}
        self.plan_path = self.root / "plan.json"
        self.save_plan()

    def save_plan(self):
        self.plan_path.write_text(json.dumps(self.plan))
        self.plan_path.chmod(0o600)

    def policy_change(self, **updates):
        self.policy_value.update(updates)
        self.policy.write_text(json.dumps(self.policy_value))
        self.plan["custody_policy_sha256"] = module.digest(self.policy.read_bytes())
        self.save_plan()

    def test_two_fresh_runs_and_restart(self):
        ctrl = module.Controller.initialize(str(self.plan_path))
        first = ctrl.stage()
        self.assertEqual(first["generation"], 1)
        self.assertEqual(stat.S_IMODE(Path(first["policy_path"]).stat().st_mode), 0o600)
        self.assertEqual(Path(first["policy_path"]).read_bytes(), self.policy.read_bytes())
        restarted = module.Controller(str(self.plan_path))
        self.assertEqual(restarted.restart()["status"], "fresh-channel-required")
        self.assertFalse(Path(first["policy_path"]).exists())
        second = restarted.stage()
        self.assertEqual(second["generation"], 2)
        self.assertNotEqual(second["policy_path"], first["policy_path"])
        self.assertEqual(restarted.rollback()["status"], "inactive")
        self.assertFalse(Path(second["policy_path"]).exists())
        self.assertTrue(Path(self.plan["store_path"]).exists())
        self.assertTrue(self.rollback.exists())

    def test_changed_engine_or_policy_refused_without_channel_mutation(self):
        ctrl = module.Controller.initialize(str(self.plan_path))
        active = ctrl.stage()
        self.engine.write_bytes(b"changed")
        self.assertEqual(ctrl.restart()["status"], "fresh-channel-required")
        self.assertFalse(Path(active["policy_path"]).exists())
        self.engine.write_bytes(b"engine-v1")
        active = ctrl.stage()
        self.policy.write_bytes(b"changed")
        with self.assertRaisesRegex(module.Refused, "PIN_CHANGED"):
            ctrl.stage()
        self.assertFalse(Path(active["policy_path"]).exists())

    def test_revocation_and_period_refused_before_setup(self):
        self.policy_change(revoked=True)
        with self.assertRaisesRegex(module.Refused, "POLICY_SCOPE_OR_PERIOD_REFUSED"):
            module.Controller.initialize(str(self.plan_path))
        self.assertFalse(Path(self.plan["store_path"]).exists())
        self.policy_change(revoked=False,
                           expires_at=(datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat())
        with self.assertRaisesRegex(module.Refused, "POLICY_SCOPE_OR_PERIOD_REFUSED"):
            module.Controller.initialize(str(self.plan_path))

    def test_preimage_and_unknown_channel_preserved(self):
        ctrl = module.Controller.initialize(str(self.plan_path))
        active = ctrl.stage()
        Path(active["policy_path"]).write_bytes(b"alien")
        with self.assertRaisesRegex(module.Refused, "PIN_CHANGED"):
            ctrl.rollback()
        self.assertEqual(Path(active["policy_path"]).read_bytes(), b"alien")
        self.assertTrue(self.rollback.exists())

    def test_pending_empty_directory_reconciled(self):
        ctrl = module.Controller.initialize(str(self.plan_path))
        pending_id = "run-" + "a" * 32
        ctrl.state["pending"] = {"run_id": pending_id, "policy_sha256": self.plan["custody_policy_sha256"],
                                 "operation_id": "op:pending-a", "request_sha256": "1" * 64}
        ctrl._save()
        uncertain = Path(self.plan["channel_root_path"]) / pending_id
        uncertain.mkdir(mode=0o700)
        self.assertEqual(module.Controller(str(self.plan_path)).restart()["status"], "fresh-channel-required")
        self.assertFalse(uncertain.exists())
        self.assertIsNone(module.Controller(str(self.plan_path)).state["pending"])

    def test_pending_foreign_bytes_preserved(self):
        ctrl = module.Controller.initialize(str(self.plan_path))
        pending_id = "run-" + "d" * 32
        ctrl.state["pending"] = {"run_id": pending_id,
                                 "policy_sha256": self.plan["custody_policy_sha256"],
                                 "operation_id": "op:foreign", "request_sha256": "4" * 64}
        ctrl._save()
        uncertain = Path(self.plan["channel_root_path"]) / pending_id
        uncertain.mkdir(mode=0o700)
        foreign = uncertain / "policy.json"
        foreign.write_bytes(b"changed-policy")
        foreign.chmod(0o600)
        with self.assertRaisesRegex(module.Refused, "UNCERTAIN_CHANNEL_RETAINED"):
            module.Controller(str(self.plan_path)).rollback()
        self.assertEqual(foreign.read_bytes(), b"changed-policy")
        self.assertEqual(module.Controller(str(self.plan_path)).state["pending"]["run_id"], pending_id)

    def test_pending_exact_policy_reconciled_but_extra_file_refused(self):
        ctrl = module.Controller.initialize(str(self.plan_path))
        pending_id = "run-" + "e" * 32
        ctrl.state["pending"] = {"run_id": pending_id,
                                 "policy_sha256": self.plan["custody_policy_sha256"],
                                 "operation_id": "op:exact-pending", "request_sha256": "5" * 64}
        ctrl._save()
        directory = Path(self.plan["channel_root_path"]) / pending_id
        directory.mkdir(mode=0o700)
        exact = directory / "policy.json"
        exact.write_bytes(self.policy.read_bytes())
        exact.chmod(0o600)
        extra = directory / "foreign.txt"
        extra.write_bytes(b"preserve")
        with self.assertRaisesRegex(module.Refused, "UNCERTAIN_CHANNEL_RETAINED"):
            module.Controller(str(self.plan_path)).restart()
        self.assertEqual(extra.read_bytes(), b"preserve")
        self.assertTrue(exact.exists())
        extra.unlink()
        self.assertEqual(module.Controller(str(self.plan_path)).restart()["status"], "fresh-channel-required")
        self.assertFalse(directory.exists())
        self.assertIsNone(module.Controller(str(self.plan_path)).state["pending"])

    def test_abrupt_after_mkdir_fresh_process_retry_and_rollback(self):
        module.Controller.initialize(str(self.plan_path))
        sentinel = self.rollback / "unrelated.txt"
        sentinel.write_bytes(b"keep-this")
        code = """
import importlib.util, os, sys
from pathlib import Path
module_path, plan_path = sys.argv[1:]
spec = importlib.util.spec_from_file_location('crash_provisioner', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
real_mkdir = os.mkdir
def crash_after_mkdir(path, mode=0o777, *args, **kwargs):
    result = real_mkdir(path, mode, *args, **kwargs)
    if Path(path).name.startswith('run-'):
        os._exit(73)
    return result
module.os.mkdir = crash_after_mkdir
module.Controller(plan_path).stage('op:abrupt', 'session:abrupt')
"""
        interrupted = subprocess.run(
            [sys.executable, "-B", "-c", code, str(HERE / "controller.py"), str(self.plan_path)],
            check=False, capture_output=True, text=True)
        self.assertEqual(interrupted.returncode, 73, interrupted.stderr)
        before = module.Controller(str(self.plan_path)).state
        pending_id = before["pending"]["run_id"]
        old = Path(self.plan["channel_root_path"]) / pending_id
        self.assertTrue(old.is_dir())
        self.assertEqual(os.listdir(old), [])
        retried = subprocess.run(
            [sys.executable, "-B", str(HERE / "controller.py"), "--plan", str(self.plan_path),
             "--operation-id", "op:abrupt", "--intent", "session:abrupt", "stage"],
            check=False, capture_output=True, text=True)
        self.assertEqual(retried.returncode, 0, retried.stderr + retried.stdout)
        staged = json.loads(retried.stdout)
        self.assertEqual(staged["generation"], 1)
        self.assertNotEqual(staged["run_id"], pending_id)
        self.assertFalse(old.exists())
        self.assertTrue(Path(staged["policy_path"]).is_file())
        rolled = subprocess.run(
            [sys.executable, "-B", str(HERE / "controller.py"), "--plan", str(self.plan_path),
             "rollback"], check=False, capture_output=True, text=True)
        self.assertEqual(rolled.returncode, 0, rolled.stderr + rolled.stdout)
        self.assertEqual(sentinel.read_bytes(), b"keep-this")
        self.assertTrue(Path(self.plan["store_path"]).is_dir())
        self.assertFalse(Path(staged["policy_path"]).exists())

    def test_dangling_pending_symlink_preserves_intent(self):
        ctrl = module.Controller.initialize(str(self.plan_path))
        pending_id = "run-" + "b" * 32
        ctrl.state["pending"] = {"run_id": pending_id,
                                 "policy_sha256": self.plan["custody_policy_sha256"],
                                 "operation_id": "op:pending-b", "request_sha256": "2" * 64}
        ctrl._save()
        uncertain = Path(self.plan["channel_root_path"]) / pending_id
        uncertain.symlink_to(self.root / "missing-target")
        with self.assertRaisesRegex(module.Refused, "UNCERTAIN_CHANNEL_RETAINED"):
            module.Controller(str(self.plan_path)).restart()
        self.assertEqual(module.Controller(str(self.plan_path)).state["pending"]["run_id"], pending_id)
        self.assertTrue(uncertain.is_symlink())

    def test_malformed_expiry_has_controlled_cli_refusal(self):
        for which in ("plan", "policy"):
            with self.subTest(which=which):
                if which == "plan":
                    self.plan["source_expires_at"] = 123
                    self.save_plan()
                else:
                    self.plan["source_expires_at"] = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
                    self.policy_change(expires_at=123)
                completed = subprocess.run(
                    [sys.executable, "-B", str(HERE / "controller.py"),
                     "--plan", str(self.plan_path), "initialize"],
                    check=False, capture_output=True, text=True)
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(json.loads(completed.stdout)["reason"], "INVALID_EXPIRY")
                self.assertEqual(completed.stderr, "")

    def test_corrupt_run_id_refused_before_path_use(self):
        ctrl = module.Controller.initialize(str(self.plan_path))
        ctrl.state["pending"] = {"run_id": "../../retained-old-store",
                                 "policy_sha256": self.plan["custody_policy_sha256"],
                                 "operation_id": "op:corrupt", "request_sha256": "3" * 64}
        ctrl._save()
        with self.assertRaisesRegex(module.Refused, "STATE_RUN_REFUSED"):
            module.Controller(str(self.plan_path))
        self.assertTrue(self.rollback.exists())

    def test_symlink_and_wrong_permissions_refused(self):
        symlink = self.root / "linked-key"
        symlink.symlink_to(self.key)
        self.plan["private_key_path"] = str(symlink)
        self.save_plan()
        with self.assertRaisesRegex(module.Refused, "SYMLINK_PATH_REFUSED"):
            module.Controller.initialize(str(self.plan_path))
        self.plan["private_key_path"] = str(self.key)
        self.save_plan()
        self.key.chmod(0o644)
        with self.assertRaisesRegex(module.Refused, "KEY_CUSTODY_REFUSED"):
            module.Controller.initialize(str(self.plan_path))

    def test_scope_or_existing_store_refused(self):
        self.plan["scope_ref"] = "scope:other"
        self.save_plan()
        with self.assertRaisesRegex(module.Refused, "POLICY_SCOPE_OR_PERIOD_REFUSED"):
            module.Controller.initialize(str(self.plan_path))
        self.plan["scope_ref"] = "scope:lab-runtime-local:test-store"
        self.save_plan()
        module.Controller.initialize(str(self.plan_path))
        with self.assertRaisesRegex(module.Refused, "OUTPUT_ALREADY_EXISTS"):
            module.Controller.initialize(str(self.plan_path))

    def test_concurrent_controller_refused(self):
        first = module.Controller.initialize(str(self.plan_path))
        second = module.Controller(str(self.plan_path))
        with first._locked():
            with self.assertRaisesRegex(module.Refused, "STORE_BUSY"):
                second.stage()
        staged = second.stage()
        self.assertEqual(staged["generation"], 1)

    def test_revocation_still_allows_channel_invalidation(self):
        ctrl = module.Controller.initialize(str(self.plan_path))
        active = ctrl.stage()
        self.policy.write_text(json.dumps({**self.policy_value, "revoked": True}))
        fresh = module.Controller(str(self.plan_path))
        self.assertEqual(fresh.restart()["status"], "fresh-channel-required")
        self.assertFalse(Path(active["policy_path"]).exists())
        with self.assertRaisesRegex(module.Refused, "PIN_CHANGED"):
            fresh.stage()

    def test_plan_mode_key_parent_and_key_pin(self):
        self.plan_path.chmod(0o644)
        with self.assertRaisesRegex(module.Refused, "PLAN_MODE_REFUSED"):
            module.Controller.initialize(str(self.plan_path))
        self.plan_path.chmod(0o600)
        self.custody.chmod(0o755)
        with self.assertRaisesRegex(module.Refused, "DIRECTORY_IDENTITY_REFUSED"):
            module.Controller.initialize(str(self.plan_path))
        self.custody.chmod(0o700)
        self.key.write_bytes(b"changed-key")
        with self.assertRaisesRegex(module.Refused, "PIN_CHANGED"):
            module.Controller.initialize(str(self.plan_path))
        self.assertFalse(Path(self.plan["store_path"]).exists())

    def test_full_write_handles_short_writes_and_zero_refusal(self):
        real_write = os.write
        calls = []

        def short_write(fd, raw):
            calls.append(len(raw))
            return real_write(fd, raw[:1])

        with mock.patch.object(module.os, "write", side_effect=short_write):
            ctrl = module.Controller.initialize(str(self.plan_path))
            staged = ctrl.stage()
        self.assertGreater(len(calls), 10)
        self.assertEqual(Path(staged["policy_path"]).read_bytes(), self.policy.read_bytes())
        with mock.patch.object(module.os, "write", return_value=0):
            with self.assertRaisesRegex(module.Refused, "SHORT_WRITE_REFUSED"):
                module._write_all(1, b"x")

    def test_full_read_handles_short_reads(self):
        real_read = os.read
        calls = []

        def short_read(fd, count):
            calls.append(count)
            return real_read(fd, min(count, 2))

        with mock.patch.object(module.os, "read", side_effect=short_read):
            self.assertEqual(module._read_owned(self.engine, self.plan["engine_sha256"]), b"engine-v1")
        self.assertGreater(len(calls), 2)

    def test_exact_retry_conflict_and_retired_operation(self):
        ctrl = module.Controller.initialize(str(self.plan_path))
        first = ctrl.stage("op:inspection-1", "session:inspection-1")
        replay = module.Controller(str(self.plan_path)).stage("op:inspection-1", "session:inspection-1")
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["policy_path"], first["policy_path"])
        self.assertEqual(replay["generation"], first["generation"])
        with self.assertRaisesRegex(module.Refused, "OPERATION_CONFLICT"):
            ctrl.stage("op:inspection-1", "session:different")
        self.assertTrue(Path(first["policy_path"]).exists())
        second = ctrl.stage("op:inspection-2", "session:inspection-2")
        self.assertEqual(second["generation"], 2)
        self.assertFalse(Path(first["policy_path"]).exists())
        with self.assertRaisesRegex(module.Refused, "OPERATION_RETIRED"):
            ctrl.stage("op:inspection-1", "session:inspection-1")
        self.assertTrue(Path(second["policy_path"]).exists())
        ctrl.rollback()
        with self.assertRaisesRegex(module.Refused, "OPERATION_RETIRED"):
            module.Controller(str(self.plan_path)).stage("op:inspection-2", "session:inspection-2")

    def test_pending_empty_retry_keeps_request_binding(self):
        ctrl = module.Controller.initialize(str(self.plan_path))
        request = module.digest(json.dumps({"plan_sha256": ctrl.plan_sha256,
            "policy_sha256": self.plan["custody_policy_sha256"],
            "intent": "session:original"}, sort_keys=True,
            separators=(",", ":")).encode())
        ctrl.state["pending"] = {"run_id": "run-" + "c" * 32,
                                 "policy_sha256": self.plan["custody_policy_sha256"],
                                 "operation_id": "op:interrupted", "request_sha256": request}
        ctrl._save()
        with self.assertRaisesRegex(module.Refused, "OPERATION_CONFLICT"):
            module.Controller(str(self.plan_path)).stage("op:interrupted", "session:changed")
        self.assertIsNotNone(module.Controller(str(self.plan_path)).state["pending"])
        staged = module.Controller(str(self.plan_path)).stage("op:interrupted", "session:original")
        self.assertEqual(staged["generation"], 1)
        self.assertIsNone(module.Controller(str(self.plan_path)).state["pending"])

    def test_two_independently_owned_store_rehearsals(self):
        other_temp = tempfile.TemporaryDirectory(prefix="cal-operational-provisioner-second-", dir="/tmp")
        self.addCleanup(other_temp.cleanup)
        other = Path(other_temp.name)
        other_custody = other / "custody"
        other_custody.mkdir(mode=0o700)
        other_rollback = other / "retained"
        other_rollback.mkdir(mode=0o700)
        second_policy = {**self.policy_value,
                         "principal_ref": "role:second-operator",
                         "scope_refs": ["scope:lab-runtime-local:second-store"]}
        second = dict(self.plan)
        second.update(store_id="second-store", operator_ref="role:second-operator",
                      scope_ref="scope:lab-runtime-local:second-store",
                      store_path=str(other / "store"), rollback_path=str(other_rollback),
                      channel_root_path=str(other / "channels"),
                      private_key_path=str(other_custody / "key.pem"),
                      private_key_sha256=write(other_custody / "key.pem", b"second-test-only-key"),
                      custody_policy_path=str(other_custody / "policy.json"),
                      custody_policy_sha256=write(other_custody / "policy.json", json.dumps(second_policy).encode()))
        for name in ("engine", "profile", "base_head"):
            source = Path(self.plan[name + "_path"])
            target = other / source.name
            second[name + "_sha256"] = write(target, source.read_bytes())
            second[name + "_path"] = str(target)
        second_path = other / "plan.json"
        write(second_path, json.dumps(second).encode())
        for plan_path, operation_id in ((self.plan_path, "op:first-store"),
                                        (second_path, "op:second-store")):
            def cli(action):
                result = subprocess.run(
                    [sys.executable, "-B", str(HERE / "controller.py"), "--plan",
                     str(plan_path), "--operation-id", operation_id, action],
                    check=False, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                return json.loads(result.stdout)
            cli("initialize")
            staged = cli("stage")
            replay = cli("stage")
            self.assertTrue(replay["replayed"])
            self.assertEqual(replay["policy_path"], staged["policy_path"])
            cli("restart")
            self.assertFalse(Path(staged["policy_path"]).exists())
            cli("rollback")
        self.assertNotEqual(self.plan["operator_ref"], second["operator_ref"])
        self.assertNotEqual(self.plan["private_key_sha256"], second["private_key_sha256"])
        self.assertNotEqual(self.plan["store_path"], second["store_path"])

    def test_active_unlink_crash_recovery_preserves_foreign_bytes(self):
        ctrl = module.Controller.initialize(str(self.plan_path))
        first = ctrl.stage()
        policy = Path(first["policy_path"])
        run_dir = policy.parent
        policy.unlink()  # Simulated crash after unlink, before rmdir/state write.
        self.assertEqual(module.Controller(str(self.plan_path)).restart()["status"], "fresh-channel-required")
        self.assertFalse(run_dir.exists())
        second = ctrl.stage()
        run_dir = Path(second["policy_path"]).parent
        Path(second["policy_path"]).unlink()
        alien = run_dir / "foreign.txt"
        alien.write_bytes(b"retained")
        with self.assertRaisesRegex(module.Refused, "CHANNEL_PREIMAGE_REFUSED"):
            module.Controller(str(self.plan_path)).restart()
        self.assertEqual(alien.read_bytes(), b"retained")
        self.assertIsNotNone(module.Controller(str(self.plan_path)).state["active"])

    def test_active_rmdir_crash_recovery(self):
        ctrl = module.Controller.initialize(str(self.plan_path))
        active = ctrl.stage()
        run_dir = Path(active["policy_path"]).parent
        Path(active["policy_path"]).unlink()
        run_dir.rmdir()  # Simulated crash before state write.
        self.assertEqual(module.Controller(str(self.plan_path)).restart()["status"], "fresh-channel-required")
        self.assertIsNone(module.Controller(str(self.plan_path)).state["active"])

    def test_real_api16_reader_channel_from_staged_policy(self):
        import importlib.util
        from importlib import import_module

        base = module.ROOT / "product/lab/release-candidates/v1/interface/api-integration-v16"
        name = "_cal_t34_api16_integration"
        if name not in sys.modules:
            selected = importlib.util.spec_from_file_location(
                name, base / "__init__.py", submodule_search_locations=[str(base)])
            package = importlib.util.module_from_spec(selected)
            sys.modules[name] = package
            selected.loader.exec_module(package)
        fixtures = import_module(name + ".fixtures")
        auth = import_module(name + ".auth")
        protocol = import_module(name + ".protocol")
        api_root = self.root / "api-owned"
        api_root.mkdir(mode=0o700)
        signer, key_path, pin = None, None, None
        signer, policy_path, pin = fixtures.provision(api_root, "engineering")
        key_path = api_root / "reader.pem"
        policy_value = json.loads(policy_path.read_bytes())
        self.plan.update(
            operator_ref=policy_value["principal_ref"],
            scope_ref=policy_value["scope_refs"][0],
            source_name="engineering",
            source_expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            private_key_path=str(key_path),
            private_key_sha256=module.digest(key_path.read_bytes()),
            custody_policy_path=str(policy_path),
            custody_policy_sha256=pin)
        self.save_plan()
        ctrl = module.Controller.initialize(str(self.plan_path))
        staged = ctrl.stage()
        channel = auth.ReaderChannel(staged["policy_path"], staged["policy_sha256"], protocol.Schemas())
        channel.authenticate(fixtures.proof(signer, channel.challenge))
        self.assertEqual(channel.context["principal_ref"], policy_value["principal_ref"])
        self.assertEqual(channel.policy["scope_refs"], policy_value["scope_refs"])
        ctrl.rollback()


if __name__ == "__main__":
    unittest.main()
