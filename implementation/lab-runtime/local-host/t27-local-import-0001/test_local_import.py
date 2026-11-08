import os
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from local_import import ImportError, LocalImporter, digest

sys.path.insert(0, str(Path(__file__).parents[1] / "t26-local-decision-state-0001"))
from decision_state import DecisionState, Event, Target


BODY = b'{"bundle":"local-fixture","members":["a"]}\n'


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.importer = LocalImporter(self.root)
        self.before = self.importer.read_head()[1]

    def test_positive_idempotence_and_wrong_head(self):
        first = self.importer.import_bundle(body=BODY, selected_digest=digest(BODY),
                                            expected_head_digest=self.before,
                                            approved=lambda _: True)
        self.assertEqual(first["sequence"], 1)
        self.assertFalse(first["idempotent"])
        again = self.importer.import_bundle(body=BODY, selected_digest=digest(BODY),
                                            expected_head_digest=self.before,
                                            approved=lambda _: True)
        self.assertTrue(again["idempotent"])
        self.assertEqual(again["head_digest"], first["head_digest"])
        with self.assertRaisesRegex(ImportError, "wrong HEAD"):
            self.importer.import_bundle(body=b"other", selected_digest=digest(b"other"),
                                        expected_head_digest=self.before,
                                        approved=lambda _: True)

    def test_altered_body_and_unapproved_refuse_without_effect(self):
        for body, selected, approved in ((BODY + b"x", digest(BODY), lambda _: True),
                                         (BODY, digest(BODY), lambda _: False)):
            with self.assertRaises(ImportError):
                self.importer.import_bundle(body=body, selected_digest=selected,
                                            expected_head_digest=self.before,
                                            approved=approved)
        self.assertEqual(self.importer.read_head()[1], self.before)
        self.assertEqual(list(self.importer.bundles.iterdir()), [])

    def test_crash_after_stage_then_fresh_process_retry_preserves_foreign(self):
        foreign = self.root / "foreign.txt"
        foreign.write_bytes(b"foreign")
        code = (
            "from pathlib import Path\n"
            "from local_import import LocalImporter,digest\n"
            "import os,sys\n"
            "root=Path(sys.argv[1]);body=bytes.fromhex(sys.argv[2]);before=sys.argv[3]\n"
            "LocalImporter(root).import_bundle(body=body,selected_digest=digest(body),"
            "expected_head_digest=before,approved=lambda _:True,after_stage=lambda:os._exit(49))\n"
        )
        result = subprocess.run([sys.executable, "-c", code, str(self.root), BODY.hex(), self.before],
                                env={**os.environ, "PYTHONPATH": str(Path(__file__).parent)},
                                check=False)
        self.assertEqual(result.returncode, 49)
        self.assertEqual(self.importer.read_head()[1], self.before)
        self.assertEqual(foreign.read_bytes(), b"foreign")
        resume_code = (
            "from pathlib import Path\n"
            "from local_import import LocalImporter,digest\n"
            "import json,sys\n"
            "body=bytes.fromhex(sys.argv[2])\n"
            "result=LocalImporter(Path(sys.argv[1])).import_bundle(body=body,"
            "selected_digest=digest(body),expected_head_digest=sys.argv[3],"
            "approved=lambda _:True)\n"
            "print(json.dumps(result))\n"
        )
        resumed_process = subprocess.run(
            [sys.executable, "-c", resume_code, str(self.root), BODY.hex(), self.before],
            env={**os.environ, "PYTHONPATH": str(Path(__file__).parent)},
            capture_output=True, text=True, check=True)
        resumed = json.loads(resumed_process.stdout)
        self.assertEqual(resumed["sequence"], 1)
        self.assertEqual(foreign.read_bytes(), b"foreign")
        self.assertEqual((self.importer.bundles / f"{digest(BODY)}.bin").read_bytes(), BODY)

    def test_symlink_head_refuses(self):
        self.importer.head.unlink()
        self.importer.head.symlink_to("foreign.txt")
        with self.assertRaises(ImportError):
            LocalImporter(self.root).read_head()

    def test_t26_exact_local_bundle_decision_controls_import(self):
        selected = Target.from_bytes(member="whole-bundle", scope="local-import",
                                     base_digest=self.before, bundle_digest=digest(BODY),
                                     body=BODY)
        state = DecisionState()
        with self.assertRaisesRegex(ImportError, "not approved"):
            self.importer.import_decided_bundle(target=selected, decision_state=state,
                                                body=BODY, expected_head_digest=self.before)
        state.apply(Event("local-choice", selected, "approve"), body=BODY)
        result = self.importer.import_decided_bundle(target=selected, decision_state=state,
                                                     body=BODY, expected_head_digest=self.before)
        self.assertEqual(result["sequence"], 1)
        changed_scope = Target.from_bytes(member="whole-bundle", scope="release",
                                          base_digest=self.before, bundle_digest=digest(BODY),
                                          body=BODY)
        with self.assertRaisesRegex(ImportError, "whole local-import"):
            self.importer.import_decided_bundle(target=changed_scope, decision_state=state,
                                                body=BODY, expected_head_digest=self.before)
        changed_base = Target.from_bytes(member="whole-bundle", scope="local-import",
                                         base_digest=digest(b"other head"),
                                         bundle_digest=digest(BODY), body=BODY)
        with self.assertRaisesRegex(ImportError, "whole local-import"):
            self.importer.import_decided_bundle(target=changed_base, decision_state=state,
                                                body=BODY, expected_head_digest=self.before)

    def test_committed_bundle_tamper_refuses_cold_read(self):
        self.importer.import_bundle(body=BODY, selected_digest=digest(BODY),
                                    expected_head_digest=self.before, approved=lambda _: True)
        (self.importer.bundles / f"{digest(BODY)}.bin").write_bytes(b"changed")
        with self.assertRaisesRegex(ImportError, "committed bundle bytes changed"):
            LocalImporter(self.root).read_head()

    def test_root_swap_cannot_write_foreign_head(self):
        selected = self.root / "selected"
        foreign = self.root / "foreign"
        selected.mkdir(mode=0o700)
        foreign.mkdir(mode=0o700)
        owned = LocalImporter(selected)
        other = LocalImporter(foreign)
        before = owned.read_head()[1]
        detached = self.root / "detached"
        selected.rename(detached)
        selected.symlink_to(foreign, target_is_directory=True)
        with self.assertRaisesRegex(ImportError, "selected import root was replaced"):
            owned.import_bundle(body=BODY, selected_digest=digest(BODY),
                                expected_head_digest=before, approved=lambda _: True)
        self.assertEqual(other.read_head()[1], before)
        self.assertEqual(digest((detached / "HEAD.json").read_bytes()), before)
        self.assertEqual(list((foreign / "bundles").iterdir()), [])

    def test_root_swap_after_stage_refuses_before_head_publication(self):
        selected = self.root / "selected"
        foreign = self.root / "foreign"
        selected.mkdir(mode=0o700)
        foreign.mkdir(mode=0o700)
        owned = LocalImporter(selected)
        other = LocalImporter(foreign)
        before = owned.read_head()[1]
        detached = self.root / "detached"

        def swap():
            selected.rename(detached)
            selected.symlink_to(foreign, target_is_directory=True)

        with self.assertRaisesRegex(ImportError, "selected import root was replaced"):
            owned.import_bundle(body=BODY, selected_digest=digest(BODY),
                                expected_head_digest=before,
                                approved=lambda _: True, after_stage=swap)
        self.assertEqual(other.read_head()[1], before)
        self.assertEqual(digest((detached / "HEAD.json").read_bytes()), before)
        self.assertEqual(list((foreign / "bundles").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
