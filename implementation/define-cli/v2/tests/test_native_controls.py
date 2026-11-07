"""Real native helper correspondence in a synthetic isolated branch, not owner authority."""
import copy
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
REPO = PACKAGE.parents[2]
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(REPO / "implementation/lab-runtime/v2"))
from define_runtime.exact import Refusal, binding, decode, encode, read, sha
from define_runtime.review import native_controls, stage_review, ReviewJournal
from lab_runtime import common, operations
from lab_runtime.cli import example
from lab_runtime.store import Store


class NativeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="define-native-core-qualification-")
        cls.root = Path(cls.temporary.name)
        cls.store = Store(cls.root / "branch", REPO)
        # Public test data only; no private key, owner outcome or application is generated.
        cls.store.initialize(common.load(REPO / "implementation/lab-runtime/v2/profile.json"), "define-core-fixture", "role:synthetic-fixture", "0" * 64)
        cls.data = cls.store.replay(require_current=True)
        cls.proposal = example(cls.store, "define-native-core")

    @classmethod
    def tearDownClass(cls):cls.temporary.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=self.root);self.addCleanup(self.tmp.cleanup);self.inputs = Path(self.tmp.name)
        def add(path, raw):
            (self.inputs / path).write_bytes(raw)
            return binding(raw, path)
        t = self.proposal["targets"][0];raw = common.encoded(t["record"])
        support = add("support.json", b'{}\n')
        profile = add("profile.json", read(REPO / "implementation/lab-runtime/v2/profile.json"))
        self.cut = {"commit_sha256": self.data["head"]["transaction_digest"], "source_profile_sha256": profile["sha256"]}
        self.cohort = {"schema_version": "cal.define.review-cohort/v1", "cohort_id": "cohort:synthetic-native", "revision": 1,
                       "source_cut": self.cut, "source_profile_binding": profile,
                       "native_mechanics_bindings": [add(Path(m.__file__).name, read(m.__file__)) for m in [common, operations]],
                       "scope_ref": self.data["config"]["scope_ref"], "ordered_targets": [{"target_id": "work", "category": t["category"], "operation": t["operation"],
                           "artifact_header": {"scope_ref": self.data["config"]["scope_ref"], "identity_ref": t["record"]["node_id"], "version_ref": t["version_ref"], "carrier_ref": t["carrier_ref"], "byte_sha256": sha(raw)},
                           "predecessor_ref": None, "content_binding": add("work.json", raw), "candidate_contract_binding": support,
                           "decision_ref": t["decision_ref"], "native_contract": None, "requested_effect": "candidate-inspection", "dependency_refs": []}],
                       "schema_bindings": [], "evidence_bindings": [], "owner_route_selections": ["example:synthetic-route"],
                       "examples_binding": support, "consequences_recipe_binding": support, "privacy_review_binding": support, "authority_effect": "none"}
        self.view = SimpleNamespace(data=self.data, handle=SimpleNamespace(common=common, operations=operations), selected={"name": "legacy"})

    def test_native_core_semantics_and_file_bytes_are_distinct(self):
        before = common.digest(self.data["projection"])
        result = native_controls(self.view, self.cohort, self.inputs, self.cut)
        actual = self.store.review(self.proposal)
        self.assertEqual(result["cores"], actual["decision_cores"])
        self.assertEqual(result["inputs"]["inputs/001-core.json"], common.encoded(actual["decision_cores"][0]))
        self.assertNotEqual(sha(result["inputs"]["inputs/001-core.json"]), result["cores"][0]["target_digest"])
        self.assertEqual(before, common.digest(self.data["projection"]))

    def test_stale_cut_unselected_mechanics_and_identity_refuse(self):
        for mutation in ["cut", "mechanics", "identity", "body"]:
            c = copy.deepcopy(self.cohort)
            if mutation == "cut":c["source_cut"] = {**self.cut, "commit_sha256": "f" * 64}
            elif mutation == "mechanics":c["native_mechanics_bindings"] = []
            elif mutation == "identity":c["ordered_targets"][0]["artifact_header"]["identity_ref"] = "work:other"
            else:c["ordered_targets"][0]["artifact_header"]["byte_sha256"] = "f" * 64
            with self.subTest(mutation=mutation), self.assertRaises(Refusal):native_controls(self.view, c, self.inputs, self.cut)

    def test_workspace_inputs_publish_without_owner_outcome(self):
        class Gate:
            def permit(_, *args):return {"principal_ref": "example:fixture-principal"}
            def call(_, operation, payload):
                return {"routing": {"fixture": True}, "policy_selection_binding": {"sha256": "a" * 64}, "verified_owner_route_selections": self.cohort["owner_route_selections"], "authority_effect": "none"}
        schema = decode(read(REPO / "product/lab/release-candidates/v1/interface/api-integration-v17/workspace.schema.json"))
        destination = self.inputs / "workspace"
        result = stage_review(self.view, Gate(), encode(self.cohort), self.inputs, destination, schema, lambda: self.cut)
        self.assertFalse(result["current_owner_authority_verified"])
        self.assertIsNone(result["actual_owner_outcome"])
        self.assertTrue((destination / "objects").is_dir())
        self.assertTrue((destination / "journal").is_dir())
        self.assertEqual(self.store.replay()["head"]["transaction_digest"], self.data["head"]["transaction_digest"])

    def test_outer_journal_idempotency_conflict_and_inspection(self):
        class Gate:
            def permit(_, *args):return {"principal_ref": "example:fixture-principal"}
            def call(_, operation, payload):return {"routing": {"fixture": True}, "policy_selection_binding": {"sha256": "a" * 64}, "verified_owner_route_selections": self.cohort["owner_route_selections"], "authority_effect": "none"}
        root = self.inputs / "operations";root.mkdir(mode=0o700)
        journal = ReviewJournal(root, Gate(), self.cohort["scope_ref"]);self.addCleanup(journal.close)
        schema = decode(read(REPO / "product/lab/release-candidates/v1/interface/api-integration-v17/workspace.schema.json"))
        first = journal.stage("key-1", self.view, encode(self.cohort), self.inputs, schema, lambda: self.cut)
        self.assertEqual(first, journal.stage("key-1", self.view, encode(self.cohort), self.inputs, schema, lambda: self.cut))
        changed = copy.deepcopy(self.cohort);changed["revision"] = 2
        with self.assertRaises(Refusal):journal.stage("key-1", self.view, encode(changed), self.inputs, schema, lambda: self.cut)
        operation = next((root / "operations").iterdir()).name
        observation = journal.inspect(operation)
        self.assertEqual(observation["native_governing_outcome"], "not-established-by-local-journal")
        self.assertEqual(observation["posture"], "candidate-inputs-staged")


if __name__ == "__main__":unittest.main()
