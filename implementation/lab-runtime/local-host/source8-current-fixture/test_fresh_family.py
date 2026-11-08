import datetime as dt
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cal_fresh_family_under_test", HERE / "fresh_family.py")
fresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fresh)


class CurrentSignedFamily(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cal-source8-current-")
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.now = dt.datetime.now(dt.timezone.utc)
        self.run = "0123456789abcdef"

    def test_construct_and_select_cold(self):
        old = fresh.retained_period()
        created = fresh.create(self.home, run_id=self.run, now=self.now)
        self.assertEqual(fresh.select(self.home, self.run, now=self.now), created)
        self.assertEqual(fresh.retained_period(), old)
        self.assertEqual(fresh.module().checked_time(created["expires_at"]) -
                         fresh.module().checked_time(created["not_before"]), dt.timedelta(hours=24))
        self.assertEqual(created["authority_effect"], "none")
        self.assertEqual({p.name for p in (self.home / self.run / "family/protected").iterdir()},
                         {"source-key.bin", "context-key.bin", "source-archive.json"})

    def test_consumed_name_and_expiry_refused(self):
        fresh.create(self.home, run_id=self.run, now=self.now)
        with self.assertRaisesRegex(ValueError, "CONSUMED_INSTANCE_REFUSED"):
            fresh.create(self.home, run_id=self.run, now=self.now)
        with self.assertRaisesRegex(ValueError, "SOURCE_PERIOD_REFUSED"):
            fresh.select(self.home, self.run, now=self.now + dt.timedelta(hours=24))

    def test_backdated_and_future_construction_refused(self):
        for instant in (self.now - dt.timedelta(minutes=1), self.now + dt.timedelta(minutes=1)):
            with self.subTest(instant=instant):
                with self.assertRaisesRegex(ValueError, "ACTUAL_CLOCK_REQUIRED"):
                    fresh.create(self.home, run_id=self.run, now=instant)
                self.assertFalse((self.home / self.run).exists())

    def test_reader_and_session_budgets(self):
        fresh.create(self.home, run_id=self.run, now=self.now)
        public = self.home / self.run / "family/public"
        reader = json.loads((public / "reader.json").read_bytes())
        context = json.loads((public / "context.json").read_bytes())
        terminal = json.loads((public / "terminal.json").read_bytes())
        clock = fresh.module().checked_time
        self.assertEqual(clock(reader["expires_at"]) - self.now, dt.timedelta(minutes=30))
        self.assertEqual(clock(context["expires_at"]) - self.now, dt.timedelta(minutes=20))
        self.assertEqual(clock(terminal["effective_deadline"]) - self.now,
                         dt.timedelta(seconds=900))
        self.assertEqual(context["max_session_seconds"], 900)

    def test_repository_home_refused_before_private_key(self):
        with self.assertRaisesRegex(ValueError, "HOME_INSIDE_REPOSITORY_REFUSED"):
            fresh.create(HERE, run_id=self.run, now=self.now)
        with self.assertRaisesRegex(ValueError, "HOME_INSIDE_REPOSITORY_REFUSED"):
            fresh.select(HERE, self.run, now=self.now)
        self.assertFalse((HERE / self.run).exists())

    def test_world_readable_home_refused_before_private_key(self):
        self.home.chmod(0o755)
        with self.assertRaisesRegex(ValueError, "PRIVATE_HOME_REQUIRED"):
            fresh.create(self.home, run_id=self.run, now=self.now)
        with self.assertRaisesRegex(ValueError, "PRIVATE_HOME_REQUIRED"):
            fresh.select(self.home, self.run, now=self.now)
        self.assertFalse((self.home / self.run).exists())

    def test_cli_construct_then_select(self):
        created = subprocess.run([sys.executable, "-I", "-B", str(HERE / "fresh_family.py"),
                                  str(self.home), "--create"], capture_output=True, text=True,
                                 check=True)
        value = json.loads(created.stdout)
        self.assertEqual(value["status"], "PASS_LOCAL_SYNTHETIC")
        selected = subprocess.run([sys.executable, "-I", "-B", str(HERE / "fresh_family.py"),
                                   str(self.home), "--select", value["run_id"]],
                                  capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(selected.stdout), value)


class ConstructorAndSelectionRefusals(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cal-source8-refusal-")
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.now = dt.datetime.now(dt.timezone.utc)
        self.run = "fedcba9876543210"
        fresh.create(self.home, run_id=self.run, now=self.now)

    def test_wrong_constructor_and_run_refused(self):
        path = self.home / self.run / "selection.json"
        original = path.read_bytes()
        selected = json.loads(original)
        selected["kind"] = "legacy-custody-constructor"
        path.write_bytes(fresh.module().canonical(selected))
        with self.assertRaisesRegex(ValueError, "WRONG_CONSTRUCTOR_REFUSED"):
            fresh.select(self.home, self.run, now=self.now)
        path.write_bytes(original)
        with self.assertRaisesRegex(ValueError, "INSTANCE_ORIGIN_REFUSED"):
            fresh.select(self.home, "0123456789abcdef", now=self.now)

    def test_signed_family_tamper_refused(self):
        source = self.home / self.run / "family/public/source.json"
        source.write_bytes(source.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "PUBLIC_LEAF_CHANGED"):
            fresh.select(self.home, self.run, now=self.now)

    def test_old_period_substitution_refused(self):
        path = self.home / self.run / "selection.json"
        selected = json.loads(path.read_bytes())
        selected["old_period_bindings"][0]["sha256"] = "0" * 64
        path.write_bytes(fresh.module().canonical(selected))
        with self.assertRaisesRegex(ValueError, "OLD_PERIOD_CHANGED"):
            fresh.select(self.home, self.run, now=self.now)


if __name__ == "__main__":
    unittest.main()
