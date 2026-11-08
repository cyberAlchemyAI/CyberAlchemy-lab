"""Effect-free admission tests; all selections and host snapshots are synthetic."""
import importlib.util
from pathlib import Path
import os
import tempfile
import unittest


SOURCE = Path(__file__).with_name("host_admission_preflight_v2.py")
spec = importlib.util.spec_from_file_location("host_admission_preflight_v2", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.host = {"broker_uid": 1000, "self_cgroup": "0::/init.scope", "cgroup2_root_mounted": True,
                     "root_uid": 0, "root_mode": 0o555, "root_writable_by_current_uid": False,
                     "controllers": ["cpu", "memory", "pids"], "nss_observed_account_uids": [1000]}
        self.selection = {"broker_uid": 1000, "worker_uid": 1001,
                          "scope_cgroup": "/user.slice/user-1000.slice/user@1000.service/app.slice/test.scope",
                          "administrator_binding": "a" * 64}

    def test_no_selection_blocks(self):
        result = module.assess(self.host)
        self.assertEqual(result["result"], "BLOCKED")
        self.assertIn("NO_INDEPENDENT_HOST_SELECTION", result["reasons"])
        self.assertFalse(result["host_qualified"])

    def test_plausible_selection_never_qualifies(self):
        self.host["nss_observed_account_uids"].append(1001)
        result = module.assess(self.host, self.selection)
        self.assertEqual(result["result"], "SELECTION_SHAPE_ONLY")
        self.assertFalse(result["host_qualified"])

    def test_nonexistent_worker_account_blocks(self):
        self.assertIn("WORKER_ACCOUNT_NOT_OBSERVED", module.assess(self.host, self.selection)["reasons"])

    def test_same_uid_refuses(self):
        self.selection["worker_uid"] = 1000
        self.assertIn("NO_SEPARATE_WORKER_UID", module.assess(self.host, self.selection)["reasons"])

    def test_wrong_broker_and_bad_scope_refuse(self):
        self.selection["broker_uid"] = 0
        self.selection["scope_cgroup"] = "/user.slice/../init.scope"
        reasons = module.assess(self.host, self.selection)["reasons"]
        self.assertIn("BROKER_UID_MISMATCH", reasons)
        self.assertIn("SCOPE_NOT_NOMINATED", reasons)

    def test_double_slash_and_non_scope_refuse(self):
        self.selection["scope_cgroup"] = "/user.slice//test.scope"
        self.assertIn("SCOPE_NOT_NOMINATED", module.assess(self.host, self.selection)["reasons"])

    def test_nul_and_overlong_scope_refuse(self):
        self.selection["scope_cgroup"] = "/user.slice/test\0.scope"
        self.assertIn("SCOPE_NOT_NOMINATED", module.assess(self.host, self.selection)["reasons"])
        self.selection["scope_cgroup"] = "/user.slice/" + "a" * 4096 + ".scope"
        self.assertIn("SCOPE_NOT_NOMINATED", module.assess(self.host, self.selection)["reasons"])
        self.selection["scope_cgroup"] = "/user.slice/test.service"
        self.assertIn("SCOPE_NOT_NOMINATED", module.assess(self.host, self.selection)["reasons"])
        self.selection["scope_cgroup"] = "/user.slice/é.scope"
        self.assertIn("SCOPE_NOT_NOMINATED", module.assess(self.host, self.selection)["reasons"])

    def test_missing_controller_and_non_v2_refuse(self):
        self.host["controllers"] = ["cpu", "pids"]
        self.host["cgroup2_root_mounted"] = False
        reasons = module.assess(self.host, self.selection)["reasons"]
        self.assertIn("REQUIRED_CONTROLLERS_NOT_OBSERVED", reasons)
        self.assertIn("CGROUP2_ROOT_NOT_OBSERVED", reasons)

    def test_extra_selection_fields_refuse(self):
        self.selection["unreviewed"] = "value"
        self.assertIn("SELECTION_SHAPE", module.assess(self.host, self.selection)["reasons"])

    def test_selection_reader_refuses_oversize_before_read(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "selection.json"
            path.write_bytes(b"x" * 8192)
            original_read = module.os.read
            calls = []
            def observed_read(fd, count):
                calls.append(count)
                return original_read(fd, count)
            module.os.read = observed_read
            try:
                with self.assertRaisesRegex(ValueError, "SELECTION_TOO_LARGE"):
                    module.read_selected_file(str(path))
            finally:
                module.os.read = original_read
            self.assertEqual(calls, [])

    def test_selection_reader_refuses_symlink_and_fifo_promptly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            regular = root / "selection.json"
            regular.write_bytes(b"{}")
            symlink = root / "link.json"
            symlink.symlink_to(regular)
            with self.assertRaisesRegex(ValueError, "SELECTION_NOT_REGULAR"):
                module.read_selected_file(str(symlink))
            fifo = root / "pipe.json"
            os.mkfifo(fifo)
            with self.assertRaisesRegex(ValueError, "SELECTION_NOT_REGULAR"):
                module.read_selected_file(str(fifo))
            parent_link = root / "parent-link"
            parent_link.symlink_to(root, target_is_directory=True)
            with self.assertRaises(OSError):
                module.read_selected_file(str(parent_link / "selection.json"))

    def test_selection_reader_exact_bytes_and_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "selection.json"
            path.write_bytes(b'{"broker_uid":1000}')
            self.assertEqual(module.read_selected_file(str(path)), b'{"broker_uid":1000}')
            with self.assertRaisesRegex(ValueError, "SELECTION_DUPLICATE_KEY"):
                module.parse_selection(b'{"worker_uid":1000,"worker_uid":1001}')


if __name__ == "__main__":
    unittest.main()
