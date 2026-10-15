from __future__ import annotations

import copy
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_runtime.cli import example
from lab_runtime.common import RuntimeFault, atomic, byte_digest, digest, encoded, load, pointer, sealed
from lab_runtime.graph import build, query
from lab_runtime.session import Session
from lab_runtime.sources import capture, freshness, resolve, validate_schema
from lab_runtime.store import Store, keygen

PACKAGE = Path(__file__).resolve().parents[1]
REPO = PACKAGE.parents[6]


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory(prefix="cal-lab-runtime-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.key = self.root / "owner.pem"
        self.pub = self.root / "owner.pub"
        keygen(self.key, self.pub)
        self.store = Store(self.root / "store", REPO)
        self.store.initialize(load(PACKAGE / "profile.json"), "test-branch", "role:repository-owner", self.pub.read_text().strip())

    def proposal(self, name="work-one"):
        return example(self.store, name)

    def commit(self, proposal):
        return self.store.apply(proposal, self.store.authorize(proposal, self.key))

    def test_real_d75_baseline_and_catalog(self):
        data = self.store.replay(require_current=True)
        self.assertEqual(data["projection"]["state"]["payload"]["cursor"], "decision:0075")
        self.assertEqual([len(h["payload"]["events"]) for h in data["projection"]["histories"].values()], [5, 5])
        values = list(data["projection"]["subjects"].values())
        self.assertEqual(sum(v["category"] == "definition" for v in values), 189)
        self.assertEqual(sum(v["category"] == "definition" and v["effective_state"] == "admitted-current" for v in values), 183)
        self.assertEqual(len(data["projection"]["contracts"]), 143)
        self.assertEqual(sum(c["lifecycle_state"] == "admitted-current" for c in data["projection"]["contracts"].values()), 121)
        self.assertEqual(len(data["projection"]["relation_contracts"]), 41)

    def test_d75_overlays_exact_carriers_and_six_global_edges(self):
        data = self.store.replay(require_current=True)
        source = data["baseline"]
        base = "authority/admissions/lab-operational-runtime/v1/"
        versions = []
        for name in ("artifact-instance-admission.json", "typed-relation-admission.json"):
            overlay = source["documents"][base + name]
            for item in overlay["entries"]:
                entry = source["subjects"][item["version_ref"]]
                self.assertEqual(entry["source"], {"path": item["admitted_instance_path"], "sha256": item["sha256"]})
                self.assertEqual(entry["effective_state"], "admitted-current")
                contract = source["contracts"][item["carrier_type_ref"]]
                validate_schema(entry["record"], contract["schema_path"], contract.get("schema_selector"), source["documents"])
                if name == "typed-relation-admission.json":
                    versions.append(item["version_ref"])
        edges = build(data)["edges"]
        projected = [e for e in edges if e.get("relation_subject") in versions]
        self.assertEqual(len(projected), 6)
        self.assertEqual({e["predicate"] for e in projected}, {"relation.member-of", "relation.successor-of", "relation.materializes-consequence"})
        self.assertEqual(len([e for e in projected if e["predicate"] == "relation.materializes-consequence"]), 4)

    def test_d75_preserves_historical_versions_and_distinct_package_label(self):
        data = self.store.replay()
        subjects = data["projection"]["subjects"]
        for ref in ("project-state:cyberalchemy-v2-to-lab-migration:decision-0074@decision-0074",
                    "project-semantic-event-history:cyberalchemy-v2-to-lab-migration@decision-0074",
                    "project-governance-event-history:cyberalchemy-v2-to-lab-migration@decision-0074"):
            self.assertEqual(subjects[ref]["effective_state"], "admitted-historical")
        current_states = [v for v in subjects.values() if v["kind"] == "project-state" and v["effective_state"] == "admitted-current"]
        self.assertEqual(len(current_states), 1)
        self.assertEqual(current_states[0]["version_ref"], "project-state:cyberalchemy-v2-to-lab-migration:decision-0075@decision-0075")
        impl = resolve(subjects, "implementation:cyberalchemy-lab:operational-runtime:v1")
        self.assertEqual(impl["effective_state"], "admitted-current")
        self.assertEqual(impl["record"]["lifecycle_state"], "candidate")
        with self.assertRaises(RuntimeFault):
            resolve(subjects, "implementation:cyberalchemy-lab:operational-runtime:v1@v1")
        bridges = [e for e in build(data)["edges"] if e["predicate"] == "implemented-by" and
                   "implementation/lab-runtime/v1/lab.py" in e["target"]]
        self.assertEqual(len(bridges), 1)
        self.assertEqual(bridges[0]["source"], impl["version_ref"])
        self.assertFalse(any(v["identity"] == "implementation:cyberalchemy-lab:operational-runtime:v2" for v in subjects.values()))

    def test_v1_store_readable_but_blocks_successor_writes_and_context(self):
        legacy = self.root / "legacy"
        code = "import sys;sys.path.insert(0,sys.argv[1]);from lab_runtime.store import Store;from lab_runtime.common import load,encoded;from lab_runtime.cli import example;from pathlib import Path;s=Store(sys.argv[2],Path(sys.argv[3]));s.initialize(load(Path(sys.argv[1])/'profile.json'),'legacy','role:repository-owner',Path(sys.argv[4]).read_text().strip());print(encoded(example(s,'legacy-work')).decode())"
        run = subprocess.run([sys.executable, "-c", code, str(REPO / "implementation/lab-runtime/v1"), str(legacy), str(REPO), str(self.pub)], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        proposal = json.loads(run.stdout)
        old = Store(legacy, REPO)
        status = old.status()
        self.assertEqual(status["repository_admission_as_of"], "decision:0074")
        self.assertIn("runtime-source-profile-successor-required", status["freshness"]["changed"])
        self.assertEqual(query(old.replay(), "Lifecycle")["connections"], [])
        for operation in (lambda: old.review(proposal), lambda: old.authorize(proposal, self.key),
                          lambda: old.apply(proposal, {}), lambda: Session(old, "product:cyberalchemy-lab")):
            with self.assertRaisesRegex(RuntimeFault, "stale repository sources"):
                operation()
        self.assertEqual(old.status()["sequence"], 0)

    def test_successor_profile_required_for_initialization(self):
        legacy_profile = load(REPO / "implementation/lab-runtime/v1/profile.json")
        with self.assertRaisesRegex(RuntimeFault, "exact source profile"):
            Store(self.root / "wrong-profile", REPO).initialize(legacy_profile, "wrong", "role:repository-owner", self.pub.read_text().strip())
        self.assertFalse((self.root / "wrong-profile").exists())

    def test_current_lookup_must_match_immutable_selection(self):
        from unittest.mock import patch
        from lab_runtime.sources import Capture
        profile = load(PACKAGE / "profile.json")
        lookup_path = profile["current_selection"]["lookup"]["path"]
        original = Capture.read
        def changed_lookup(cap, path, expected=None):
            value = original(cap, path, expected)
            if path == lookup_path:
                value = copy.deepcopy(value)
                value["current_project_state"]["sha256"] = "0" * 64
            return value
        with patch.object(Capture, "read", changed_lookup):
            with self.assertRaisesRegex(RuntimeFault, "lookup differs"):
                capture(REPO, profile)
        from lab_runtime.sources import under
        original_under = under
        changed_file = self.root / "current.json"
        value = load(REPO / lookup_path)
        value["decision_ref"] = "unrecorded-decision"
        atomic(changed_file, encoded(value))
        def redirected(root, path):
            return changed_file if path == lookup_path else original_under(root, path)
        with patch("lab_runtime.sources.under", redirected):
            self.assertIn(lookup_path, self.store.status()["freshness"]["changed"])
            with self.assertRaises(RuntimeFault):
                self.store.review(self.proposal())

    def test_snapshot_is_deterministic(self):
        a = self.store.replay()["baseline"]
        b = capture(REPO, load(PACKAGE / "profile.json"))
        self.assertEqual(a, b)

    def test_source_candidate_fields_do_not_override_admission(self):
        data = self.store.replay()
        value = resolve(data["projection"]["subjects"], "product-capability:cyberalchemy-lab:governed-knowledge-lifecycle")
        self.assertEqual(value["effective_state"], "admitted-current")
        self.assertEqual(value["record"]["status"], "candidate-unadmitted")
        self.assertEqual(value["record"]["lifecycle_posture"]["status"], "draft")
        self.assertEqual(value["record"]["realization_binding_refs"], [])
        closed = resolve(data["projection"]["subjects"], "agent-session:first-governed-agent-episode:2026-10-06")
        self.assertEqual(closed["operational_disposition"], "closed-at-owner-review-boundary")
        self.assertFalse(closed["session_memory_retained"])

    def test_three_lenses_and_unresolved_versions(self):
        data = self.store.replay()
        for lens in ["Authority", "Provenance", "Lifecycle"]:
            q = query(data, lens)
            self.assertTrue(q["nodes"])
            self.assertEqual(q["authority_effect"], "none")
            self.assertFalse(q["replay_source"])
        g = build(data)
        finding = next(d for d in g["diagnostics"] if "state-successor" in d["subject"])
        self.assertTrue(finding["excluded_from_confirmed_paths"])
        self.assertIn("candidate.1", finding["reason"])
        self.assertTrue(any(e["predicate"] == "relation.materializes-consequence" for e in g["edges"]))
        self.assertTrue(any(e["predicate"] == "transition-from" for e in g["edges"]))
        self.assertTrue(any(e["predicate"] == "implemented-by" for e in g["edges"]))

    def test_traversal_limits_and_actual_direction(self):
        data = self.store.replay()
        cap = "product-capability:cyberalchemy-lab:governed-knowledge-lifecycle"
        q = query(data, cap, direction="outgoing", depth=1, predicates=["relation.derives-from"])
        self.assertEqual(len(q["connections"]), 1)
        self.assertEqual(q["connections"][0]["predicate"], "relation.derives-from")
        limited = query(data, "Lifecycle", max_nodes=1, max_edges=1)
        self.assertEqual(len(limited["nodes"]), 1)
        self.assertTrue(limited["coverage"]["truncated"])
        with self.assertRaises(RuntimeFault):
            query(data, depth=-1)

    def test_atomic_consequences_and_fresh_process_replay(self):
        p = self.proposal()
        result = self.commit(p)
        self.assertEqual(result["receipt"]["semantic_cursor"], 6)
        self.assertEqual(result["receipt"]["governance_cursor"], 6)
        self.assertEqual(len(result["receipt"]["outputs"]), 16)
        tx = self.store.replay()["transactions"][-1]
        self.assertEqual(len(tx["consequences"]["admission_transaction"]["payload"]["deterministic_consequences"]), 4)
        self.assertEqual(len(tx["consequences"]["governance_records"]), 5)
        self.assertEqual(len(tx["consequences"]["typed_relations"]), 6)
        subjects = self.store.replay()["projection"]["subjects"]
        for entry in subjects.values():
            if entry["source"].get("store_id"):
                record = pointer(load(self.store.path / entry["source"]["path"]), entry["source"]["selector"])
                self.assertEqual(byte_digest(encoded(record)), entry["source"]["sha256"])
        process = subprocess.run([sys.executable, str(PACKAGE / "lab.py"), "--store", str(self.store.path), "verify"], capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)["head"], result["transaction_digest"])

    def test_idempotency_and_conflicting_reuse(self):
        p = self.proposal()
        approval = self.store.authorize(p, self.key)
        one = self.store.apply(p, approval)
        two = self.store.apply(p, approval)
        self.assertTrue(two["idempotent"])
        self.assertEqual(one["transaction_digest"], two["transaction_digest"])
        p["targets"][0]["record"]["name"] = "different bytes"
        with self.assertRaises(RuntimeFault):
            self.store.apply(p, approval)
        self.assertEqual(self.store.status()["sequence"], 1)

    def test_revision_and_withdrawal_keep_old_bytes(self):
        p = self.proposal()
        self.commit(p)
        original = copy.deepcopy(p["targets"][0]["record"])
        revision = self.proposal("revision")
        target = copy.deepcopy(p["targets"][0])
        target.update(operation="revise", predecessor_ref=target["version_ref"], decision_ref="decision:local:revision")
        target["version_ref"] = target["record"]["node_id"] + "@candidate.2"
        target["record"]["name"] = "Revised local work"
        revision["targets"] = [target]
        self.commit(revision)
        subjects = self.store.replay()["projection"]["subjects"]
        old = subjects[p["targets"][0]["version_ref"]]
        self.assertEqual(old["record"], original)
        self.assertEqual(old["effective_state"], "local-admitted-historical")
        withdraw = self.proposal("withdraw")
        target.update(operation="withdraw", predecessor_ref=target["version_ref"], record=None, decision_ref="decision:local:withdraw")
        withdraw["targets"] = [target]
        self.commit(withdraw)
        entry = self.store.replay()["projection"]["subjects"][target["version_ref"]]
        self.assertEqual(entry["effective_state"], "local-withdrawn")
        self.assertEqual(self.store.status()["sequence"], 3)

    def test_multi_target_review_one_atomic_checkpoint(self):
        p, other = self.proposal("one"), self.proposal("two")
        p["targets"].append(other["targets"][0])
        self.assertEqual(len(self.store.review(p)["decision_cores"]), 2)
        result = self.commit(p)
        self.assertEqual(result["receipt"]["semantic_cursor"], 6)
        self.assertEqual(len(result["receipt"]["decision_core_digests"]), 2)

    def test_stale_head_and_tampered_approval(self):
        p, other = self.proposal("one"), self.proposal("two")
        approval = self.store.authorize(p, self.key)
        forged = copy.deepcopy(approval)
        forged["owner_ref"] = "role:attacker"
        with self.assertRaises(RuntimeFault):
            self.store.apply(p, forged)
        forged = copy.deepcopy(approval)
        forged["signature"] = "00" * 64
        with self.assertRaises(RuntimeFault):
            self.store.apply(p, forged)
        self.commit(other)
        with self.assertRaises(RuntimeFault):
            self.store.apply(p, approval)

    def test_target_drift_after_approval(self):
        p = self.proposal()
        approval = self.store.authorize(p, self.key)
        p["targets"][0]["record"]["name"] = "changed after review"
        with self.assertRaises(RuntimeFault):
            self.store.apply(p, approval)
        self.assertEqual(self.store.status()["sequence"], 0)

    def test_scope_policy_and_malformed_record_rejected_without_write(self):
        original = self.store.status()["head"]
        for mutation in [lambda p: p.update(scope_ref="scope:other"), lambda p: p.update(policy_ref="policy:other"),
                         lambda p: p.update(unrecognized=True), lambda p: p["targets"][0]["record"].update(scope_ref="scope:other"),
                         lambda p: p["targets"][0]["record"].update(implicit_admission=True),
                         lambda p: p["targets"][0].update(carrier_ref="cal.artifact-type.work/v999")]:
            p = self.proposal()
            mutation(p)
            with self.assertRaises(RuntimeFault):
                self.store.review(p)
        self.assertEqual(self.store.status()["head"], original)

    def test_definition_admission_uses_current_carrier(self):
        data = self.store.replay()
        record = load(REPO / "authority/artifact-types/definition/v2/fixtures/valid/definition.json")
        record.update(definition_id="cal.definition.local-runtime-example", version="1.0.0-candidate.1", term="Local runtime example")
        record["index_entry"]["entry_id"] = record["definition_id"]
        p = self.proposal("definition")
        p["targets"] = [{"category": "definition", "operation": "admit", "version_ref": record["definition_id"] + "@" + record["version"],
                         "record": record, "carrier_ref": "cal.artifact-type.definition/v2", "predecessor_ref": None,
                         "decision_ref": "decision:local:definition", "contract": None}]
        self.commit(p)
        self.assertEqual(resolve(self.store.replay()["projection"]["subjects"], record["definition_id"])["effective_state"], "local-admitted-current")

    def test_new_artifact_type_and_instance(self):
        data = self.store.replay()
        work = data["projection"]["contracts"]["cal.artifact-type.work/v1"]
        record = {"artifact_type_ref": "cal.artifact-type.local-work/v1", "semantic_kind": "work", "semantic_definition_refs": work["semantic_definition_refs"],
                  "schema_path": "runtime/schemas/local-work-v1.json", "schema_selector": None, "distinct_validation_purpose": "Validate a local Work record under this explicitly registered schema package."}
        schema = copy.deepcopy(data["projection"]["documents"][work["schema_path"]])
        schema_path = "runtime/schemas/local-work-v1.json"
        schema_sha = byte_digest(encoded(schema))
        record["schema_sha256"] = schema_sha
        p = self.proposal("type")
        instance = p["targets"][0]
        instance["carrier_ref"] = record["artifact_type_ref"]
        instance["decision_ref"] = "decision:local:type-instance"
        p["schemas"][schema_path] = schema
        p["targets"] = [{"category": "artifact-type", "operation": "admit", "version_ref": record["artifact_type_ref"],
                         "record": record, "carrier_ref": "cal.artifact-type.artifact-type/v3", "predecessor_ref": None,
                         "decision_ref": "decision:local:type", "contract": {"semantic_kind": "work", "schema_path": schema_path,
                         "schema_sha256": schema_sha, "schema_selector": None, "instance_discriminator": work["instance_discriminator"],
                         "identity_field": "node_id", "allowed_relation_kinds": work["artifact"]["allowed_relation_kinds"], "relation_roles": work["artifact"]["relation_roles"]}}, instance]
        self.commit(p)
        self.assertIn(record["artifact_type_ref"], self.store.replay()["projection"]["contracts"])

    def relation_proposal(self):
        p = self.proposal("relation")
        data = self.store.replay()
        source = resolve(data["projection"]["subjects"], "product-capability:cyberalchemy-lab:governed-knowledge-lifecycle")
        target = resolve(data["projection"]["subjects"], "product-thesis:cyberalchemy-lab-governed-work")
        record = copy.deepcopy(data["projection"]["documents"]["authority/admissions/governance-transaction-surface/v1/instances/typed-relations/materializes-project-state.json"])
        record.update(node_id="typed-relation:local:lineage", scope_ref=p["scope_ref"])
        record["payload"].update(relation_kind_ref="relation.derives-from", source={"kind": source["kind"], "ref": source["identity"], "version_ref": source["version_ref"]},
                                  target={"kind": target["kind"], "ref": target["identity"], "version_ref": target["version_ref"]},
                                  qualifiers={"derivation_role": "thesis-outcome-realization"})
        p["targets"] = [{"category": "typed-relation", "operation": "admit", "version_ref": record["node_id"] + "@local.1",
                         "record": record, "carrier_ref": "cal.artifact-type.typed-relation/v3", "predecessor_ref": None,
                         "decision_ref": "decision:local:relation", "contract": None}]
        return p

    def test_typed_relation_admission_and_closed_qualifiers(self):
        p = self.relation_proposal()
        for mutation in [lambda r: r["payload"]["target"].update(kind="project"),
                         lambda r: r["payload"]["target"].update(version_ref="unresolved@candidate.1"),
                         lambda r: r["payload"]["qualifiers"].update(extra="semantic-collapse")]:
            bad = copy.deepcopy(p)
            mutation(bad["targets"][0]["record"])
            with self.assertRaises(RuntimeFault):
                self.store.review(bad)
        self.commit(p)

    def test_relation_kind_revision_and_endpoint_extension_gate(self):
        data = self.store.replay()
        prior = next(v for v in data["projection"]["subjects"].values() if v["category"] == "relation-kind" and v["identity"] == "relation.derives-from")
        record = copy.deepcopy(prior["record"])
        p = self.proposal("kind")
        record["scope_ref"] = p["scope_ref"]
        p["targets"] = [{"category": "relation-kind", "operation": "revise", "version_ref": record["node_id"] + "@local.2",
                         "record": record, "carrier_ref": "cal.artifact-type.relation-kind/v2", "predecessor_ref": prior["version_ref"],
                         "decision_ref": "decision:local:kind", "contract": None}]
        bad = copy.deepcopy(p)
        bad["targets"][0]["record"]["payload"]["allowed_endpoint_pairs"].append({"source_kind": "unknown", "target_kind": "project"})
        with self.assertRaises(RuntimeFault):
            self.store.review(bad)
        self.commit(p)

    def test_declared_relation_extension_with_carrier_successors_and_instance(self):
        data = self.store.replay()
        p, other = self.proposal("extension"), self.proposal("extension-two")
        first, second = p["targets"][0], other["targets"][0]
        new_relation = "relation.local-work-lineage"
        prior_kind = next(v for v in data["projection"]["subjects"].values() if v["identity"] == "relation.derives-from")
        kind = copy.deepcopy(prior_kind["record"])
        kind.update(node_id=new_relation, name="Local Work lineage", scope_ref=p["scope_ref"])
        kind["payload"].update(relation_kind_id=new_relation, axis_id="axis.local-work-lineage", predicate="local-work-lineage",
                               source_kinds=["work"], target_kinds=["work"], allowed_endpoint_pairs=[{"source_kind": "work", "target_kind": "work"}],
                               unique_question="Which local Work record is the declared lineage source of another local Work record?", absorbed_relation_kinds=[new_relation])
        targets = []
        for semantic_kind, old_ref, new_ref, schema_version in [("work", "cal.artifact-type.work/v1", "cal.artifact-type.work/v2", "cyberalchemy-lab-work/v2"),
                                                               ("typed-relation", "cal.artifact-type.typed-relation/v3", "cal.artifact-type.typed-relation/v4", "cyberalchemy-lab-typed-relation/v4")]:
            old = data["projection"]["contracts"][old_ref]
            schema = copy.deepcopy(data["projection"]["documents"][old["schema_path"]])
            schema["properties"]["schema_version"]["const"] = schema_version
            if semantic_kind == "typed-relation":
                schema["properties"]["payload"]["properties"]["relation_kind_ref"]["enum"].append(new_relation)
            name = "runtime/schemas/" + semantic_kind + "-extension.json"
            p["schemas"][name] = schema
            sha = byte_digest(encoded(schema))
            desc = {"artifact_type_ref": new_ref, "semantic_kind": semantic_kind, "semantic_definition_refs": old["semantic_definition_refs"],
                    "schema_path": name, "schema_selector": None, "schema_sha256": sha, "distinct_validation_purpose": "Explicit local schema successor for the declared endpoint extension."}
            roles = copy.deepcopy(old["artifact"].get("relation_roles", []))
            allowed = list(old["artifact"].get("allowed_relation_kinds", []))
            if semantic_kind == "work":
                roles += [{"direction": d, "relation_kind_ref": new_relation, "counterpart_kinds": ["work"]} for d in ["source", "target"]]
                allowed.append(new_relation)
            targets.append({"category": "artifact-type", "operation": "revise", "version_ref": new_ref, "predecessor_ref": old_ref, "record": desc,
                            "carrier_ref": "cal.artifact-type.artifact-type/v3", "decision_ref": "decision:local:extend-" + semantic_kind,
                            "contract": {"semantic_kind": semantic_kind, "schema_path": name, "schema_selector": None, "schema_sha256": sha,
                                         "instance_discriminator": {"path": "/schema_version", "value": schema_version}, "identity_field": "node_id",
                                         "allowed_relation_kinds": allowed, "relation_roles": roles}})
        for target in [first, second]:
            target["record"]["schema_version"] = "cyberalchemy-lab-work/v2"
            target["carrier_ref"] = "cal.artifact-type.work/v2"
        relation = copy.deepcopy(self.relation_proposal()["targets"][0])
        relation.update(carrier_ref="cal.artifact-type.typed-relation/v4", decision_ref="decision:local:extended-connection")
        relation["record"].update(schema_version="cyberalchemy-lab-typed-relation/v4", node_id="typed-relation:local:work-lineage")
        relation["version_ref"] = relation["record"]["node_id"] + "@local.1"
        relation["record"]["payload"].update(relation_kind_ref=new_relation,
            source={"kind": "work", "ref": first["record"]["node_id"], "version_ref": first["version_ref"]},
            target={"kind": "work", "ref": second["record"]["node_id"], "version_ref": second["version_ref"]})
        targets += [{"category": "relation-kind", "operation": "admit", "version_ref": new_relation + "@local.1", "predecessor_ref": None,
                     "record": kind, "carrier_ref": "cal.artifact-type.relation-kind/v2", "decision_ref": "decision:local:extended-kind", "contract": None}, first, second, relation]
        p["targets"] = targets
        self.commit(p)
        graph = build(self.store.replay())
        self.assertTrue(any(e["predicate"] == new_relation for e in graph["edges"]))

    def test_axis_collapse_and_recorded_decision_reuse_rejected(self):
        p = self.proposal()
        p["targets"][0]["decision_ref"] = "CAL-DECISION-0071-CYBERALCHEMY-LAB-OPERATIONAL-FOUNDATION-ADMISSION"
        with self.assertRaises(RuntimeFault):
            self.store.review(p)
        data = self.store.replay()
        prior = next(v for v in data["projection"]["subjects"].values() if v["identity"] == "relation.derives-from")
        record = copy.deepcopy(prior["record"])
        record.update(node_id="relation.duplicate-lineage", scope_ref=p["scope_ref"])
        record["payload"]["relation_kind_id"] = record["node_id"]
        p["targets"] = [{"category": "relation-kind", "operation": "admit", "version_ref": record["node_id"] + "@local.1", "predecessor_ref": None,
                         "record": record, "carrier_ref": "cal.artifact-type.relation-kind/v2", "decision_ref": "decision:local:duplicate-kind", "contract": None}]
        with self.assertRaisesRegex(RuntimeFault, "collapses an existing typed axis"):
            self.store.review(p)

    def test_no_remote_schema_resolution(self):
        with self.assertRaises(RuntimeFault):
            validate_schema({}, "runtime/schemas/unsafe.json", None, {"runtime/schemas/unsafe.json": {"$ref": "https://attacker.invalid/schema"}})

    def test_source_drift_blocks_writes_and_reports_stale_reads(self):
        p = self.proposal()
        approval = self.store.authorize(p, self.key)
        shadow = self.root / "shadow"
        shadow.mkdir()
        # An unavailable source root is stale; no change to real admitted files.
        self.store.repo = shadow
        self.assertEqual(self.store.status()["freshness"]["status"], "stale")
        result = query(self.store.replay(), "Lifecycle")
        self.assertEqual(result["connections"], [])
        self.assertEqual(result["result_status"], "partial")
        with self.assertRaises(RuntimeFault):
            self.store.apply(p, approval)
        self.assertEqual(self.store.status()["sequence"], 0)

    def test_new_repository_admission_epoch_invalidates_frozen_baseline(self):
        data = self.store.replay()
        from unittest.mock import patch
        changed = copy.deepcopy(data["baseline"]["epoch_inventory"])
        changed["admission_bundles"].append("authority/admissions/later-epoch/v1/bundle.json")
        with patch("lab_runtime.sources.epoch_inventory", return_value=changed):
            self.assertEqual(self.store.status()["freshness"]["status"], "stale")
            with self.assertRaises(RuntimeFault):
                self.store.review(self.proposal())

    def test_baseline_and_transaction_tamper_detection(self):
        p = self.proposal()
        self.commit(p)
        path = self.store.path / "transactions/0000000001.json"
        tx = load(path)
        tx["consequences"]["receipt"]["semantic_cursor"] = 999
        atomic(path, encoded(sealed({k: v for k, v in tx.items() if k != "digest"})))
        with self.assertRaises(RuntimeFault):
            self.store.replay()

    def test_writer_lock_is_exclusive(self):
        with self.store.lock():
            process = subprocess.run([sys.executable, "-c", "import sys;sys.path.insert(0,sys.argv[1]);from lab_runtime.store import Store;from pathlib import Path;s=Store(sys.argv[2],Path(sys.argv[3]));s.recover(s.status()['head'])", str(PACKAGE), str(self.store.path), str(REPO)], capture_output=True, text=True)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("another writer", process.stderr)

    def crash_probe(self, stage):
        p = self.proposal()
        a = self.store.authorize(p, self.key)
        proposal_file, approval_file = self.root / "proposal.json", self.root / "approval.json"
        atomic(proposal_file, encoded(p))
        atomic(approval_file, encoded(a))
        code = "import sys;sys.path.insert(0,sys.argv[1]);from lab_runtime.store import Store;from lab_runtime.common import load;from pathlib import Path;Store(sys.argv[2],Path(sys.argv[3])).apply(load(sys.argv[4]),load(sys.argv[5]),crash_at=sys.argv[6])"
        run = subprocess.run([sys.executable, "-c", code, str(PACKAGE), str(self.store.path), str(REPO), str(proposal_file), str(approval_file), stage], capture_output=True, text=True)
        self.assertEqual(run.returncode, 86, run.stderr)
        state = self.store.status()
        self.assertTrue(state["recovery_required"])
        self.assertEqual(state["sequence"], 1 if stage == "after-head" else 0)
        with self.assertRaises(RuntimeFault):
            self.store.recover("wrong-head")
        self.store.recover(state["head"])
        self.assertFalse(self.store.status()["recovery_required"])
        result = self.store.apply(p, a)
        self.assertEqual(result["idempotent"], stage == "after-head")
        self.assertEqual(self.store.status()["sequence"], 1)

    def test_crash_after_pending(self):
        self.crash_probe("after-pending")

    def test_crash_before_head(self):
        self.crash_probe("before-head")

    def test_crash_after_head(self):
        self.crash_probe("after-head")

    def test_ephemeral_memory_expiry_and_candidate_views(self):
        now = [1791395000.0]
        s = Session(self.store, "product:cyberalchemy-lab", ttl=10, clock=lambda: now[0])
        context = s.context()
        self.assertEqual(context["agent_session"]["payload"]["authority_envelope_ref"].split(":")[0], "runtime-context-read-only")
        self.assertTrue(context["ontology_nodes"])
        self.assertFalse(context["ontology_view"]["payload"]["replay_source"])
        before = self.store.status()["head"]
        s.note("Temporary investigation scratch")
        self.assertEqual(len(s.memory), 1)
        now[0] += 11
        with self.assertRaises(RuntimeFault):
            s.context()
        self.assertTrue(s.closed)
        self.assertEqual(s.memory, [])
        self.assertEqual(self.store.status()["head"], before)

    def test_new_head_invalidates_session_and_new_session_reconstructs(self):
        s = Session(self.store, "product:cyberalchemy-lab")
        self.commit(self.proposal())
        with self.assertRaises(RuntimeFault):
            s.context()
        s.close()
        next_session = Session(self.store, "product:cyberalchemy-lab")
        self.assertEqual(next_session.context()["project_state"]["node_id"], "project-state:test-branch:1")
        self.assertEqual(next_session.memory, [])
        next_session.close()

    def test_private_key_boundary_and_wrong_operator(self):
        keygen(self.root / "other.pem", self.root / "other.pub")
        with self.assertRaises(RuntimeFault):
            self.store.authorize(self.proposal(), self.root / "other.pem")
        self.key.chmod(0o644)
        with self.assertRaises(RuntimeFault):
            self.store.authorize(self.proposal(), self.key)

    def test_duplicate_json_keys_rejected(self):
        f = self.root / "duplicate.json"
        f.write_text('{"proposal_id":"one","proposal_id":"two"}')
        with self.assertRaises(RuntimeFault):
            load(f)

    def test_configuration_head_and_baseline_integrity(self):
        head_path = self.store.path / "HEAD.json"
        head = load(head_path)
        head["sequence"] = -1
        atomic(head_path, encoded(sealed({k: v for k, v in head.items() if k != "digest"})))
        with self.assertRaises(RuntimeFault):
            self.store.replay()

    def test_declared_grant_limits_and_unknown_recovery_material(self):
        config = load(self.store.path / "config.json")
        limited = Store(self.root / "limited", REPO)
        limited.initialize(load(PACKAGE / "profile.json"), "limited", "role:local-owner", config["public_key"], allowed_categories=["artifact-instance"], allowed_effects=["admit"])
        proposal = example(limited, "work")
        proposal["targets"][0]["category"] = "typed-relation"
        with self.assertRaises(RuntimeFault):
            limited.review(proposal)
        unknown = self.store.path / "transactions/0000000003.json"
        unknown.write_text('{}')
        with self.assertRaisesRegex(RuntimeFault, "unknown future transaction"):
            self.store.recover(self.store.status()["head"])
        self.assertTrue(unknown.exists())

    def test_rebuild_is_disposable_and_deterministic(self):
        one, two = self.root / "graph-one.json", self.root / "graph-two.json"
        head = self.store.status()["head"]
        for out in [one, two]:
            run = subprocess.run([sys.executable, str(PACKAGE / "lab.py"), "--store", str(self.store.path), "rebuild", "--out", str(out)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(one.read_bytes(), two.read_bytes())
        self.assertEqual(self.store.status()["head"], head)


if __name__ == "__main__":
    unittest.main()
