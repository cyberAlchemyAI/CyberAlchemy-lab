"""Synthetic-only I11 checks. No scored outputs, old events, or disk fixtures written."""
import copy
import hashlib
import io
import json
from pathlib import Path
import unittest
from contextlib import ExitStack
from unittest.mock import patch

import composition_i11_runtime_v2 as r


class MemoryPath:
    """Only test-owned bytes. No temporary files or actual runtime events."""
    def __init__(self, value, files):
        self.name = str(value.name if isinstance(value, MemoryPath) else value)
        self.files = files

    def __str__(self):
        return self.name

    def __truediv__(self, other):
        return MemoryPath(self.name.rstrip("/") + "/" + str(other), self.files)

    @property
    def parent(self):
        return MemoryPath(self.name.rsplit("/", 1)[0], self.files)

    @property
    def parts(self):
        return Path(self.name).parts

    def is_absolute(self):
        return Path(self.name).is_absolute()

    def resolve(self):
        return self

    def mkdir(self, **kwargs):
        return None

    def exists(self):
        return self.name in self.files

    def read_bytes(self):
        if not self.exists():
            raise FileNotFoundError(self.name)
        return self.files[self.name]

    def read_text(self, **kwargs):
        return self.read_bytes().decode(errors=kwargs.get("errors", "strict"))

    def open(self, mode):
        if mode != "xb":
            raise ValueError("test permits exclusive binary writes only")
        if self.exists():
            raise FileExistsError(self.name)
        self.files[self.name] = b""
        target = self
        class Writer(io.BytesIO):
            def close(self):
                target.files[target.name] = self.getvalue()
                super().close()
        return Writer()


def review_template(packet, reviewer):
    """Typed synthetic placeholders; never native experimental judgment."""
    body = {"reviewer_id": reviewer, "columns": copy.deepcopy(packet["contract"]["columns"]),
            "limits": "SYNTHETIC STRUCTURAL TEMPLATE ONLY; no semantic assessment or native credit."}
    for table, obligations in packet["expected_matrix"].items():
        rows = []
        for ob in obligations:
            values = {}
            for field in body["columns"][table]:
                if field in ob["identity"]:
                    value = ob["identity"][field]
                elif field in ob["fixed_values"]:
                    value = ob["fixed_values"][field]
                elif field == "evidence":
                    value = "Synthetic template placeholder; no observed semantic validity."
                elif ob["null_semantics"]:
                    value = None
                elif field in r.v.BOOLS:
                    value = False
                elif field in ("usefulness", "observability"):
                    value = 0
                elif field == "relation":
                    value = "uncertain"
                elif field in r.v.ENUMS:
                    value = r.v.ENUMS[field][0]
                else:
                    raise AssertionError(field)
                values[field] = value
            rows.append([values[f] for f in body["columns"][table]])
        body[table] = rows
    return body


def native_pair(packet):
    reviews = [review_template(packet, key) for key in packet["review_job_ids"]]
    starts, terminals = [], []
    for i, body in enumerate(reviews):
        handle, call = "SYNTHETIC-AGENT-" + str(i), "SYNTHETIC-CALL-" + str(i)
        starts.append({"host_spawn_observed": True, "fresh_context": True, "turn": 1,
                       "agent_handle": handle, "native_call_id": call})
        terminals.append({"terminal_observed": True, "terminal_witness": "parent_received_NATIVE_FINAL_ANSWER",
                          "agent_handle": handle, "native_call_id": call, "validation": {"valid": True}})
    return reviews, terminals, starts


class I11PureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schedule, cls.reviews = r.schedules()
        cls.case = r.read(r.R / "cases/H-P.json")
        cls.prompt = (r.R / "prompts/composition-i11-draft-v2/I11-000-S1.txt").read_bytes()
        cls.fixture = r.read(r.R / "fixtures/composition-i11-maximal-inputs.v2.json")
        cls.saved_fixture = r.read(r.R / "fixtures/composition-i11-maximal-raw.v2.json")
        cls.contract = r.read(r.R / "generation-review-contract.v2.json")
        cls.criteria = r.read(r.R / "criteria-generation.v2.json")
        cls.archives = r.read(r.R / "archives/case-archives.json")
        cls.case = r.read(r.R / "cases/H-P.json")
        cls.inputs = (cls.fixture["schedule"], cls.fixture["reviews"], cls.contract, cls.criteria, cls.archives)

    def sample(self, arm="000", stage=3):
        jobs = self.fixture["schedule"]["jobs"]
        job = next(j for j in jobs if j["arm"] == arm and j["stage"] == stage)
        body = copy.deepcopy(self.fixture["artifacts"][job["job_id"]])
        priors = {k: copy.deepcopy(self.fixture["artifacts"][k]) for k in job["depends_on"]}
        return job, body, priors

    def build(self, artifacts=None, dispositions=None):
        return r.build_raw_case("H-P", artifacts if artifacts is not None else self.fixture["artifacts"],
            dispositions if dispositions is not None else self.fixture["dispositions"], inputs=self.inputs)

    def test_exact_schedule_all_roles_and_no_D(self):
        self.assertEqual(len(self.schedule["jobs"]), 162)
        self.assertEqual(len(self.reviews["jobs"]), 12)
        self.assertEqual({j["role"] for j in self.schedule["jobs"]}, {"raw"})
        self.assertEqual([self.schedule["jobs"][0]["job_id"], self.schedule["jobs"][-1]["job_id"]], ["G0401", "G0562"])
        for mutate in (lambda s: s["jobs"].pop(), lambda s: s["jobs"][2]["input_refs"].pop(),
                       lambda s: s["jobs"][0].update(role="D"), lambda s: s["jobs"][0].update(stage=True)):
            changed = copy.deepcopy(self.schedule)
            mutate(changed)
            with self.assertRaises(ValueError):
                r.validate_schedule(changed, self.reviews)

    def test_exact_raw_review_schedule(self):
        changed = copy.deepcopy(self.reviews)
        changed["jobs"][0]["depends_on"].pop()
        with self.assertRaises(ValueError):
            r.validate_schedule(self.schedule, changed)
        changed = copy.deepcopy(self.reviews)
        changed["jobs"][0]["review_phase"] = "post"
        with self.assertRaises(ValueError):
            r.validate_schedule(self.schedule, changed)

    def test_every_stage_and_construction_fixture_valid(self):
        for job in self.fixture["schedule"]["jobs"]:
            prior = {k: self.fixture["artifacts"][k] for k in job["depends_on"]}
            result = r.validate_generation(job, self.fixture["artifacts"][job["job_id"]], self.case, prior)
            self.assertTrue(result["valid"], result["errors"])

    def test_stage_three_must_cover_both_earlier_stages(self):
        job, body, prior = self.sample()
        body["lineage"] = [row for row in body["lineage"] if not row["source_id"].startswith(job["depends_on"][0] + ":")]
        self.assertFalse(r.validate_generation(job, body, self.case, prior)["valid"])
        prior.pop(job["depends_on"][0])
        self.assertFalse(r.validate_generation(job, body, self.case, prior)["valid"])

    def test_duplicate_and_unknown_lineage_or_current_ids(self):
        for mutate in (lambda b: b["lineage"].append(copy.deepcopy(b["lineage"][0])),
                       lambda b: b["lineage"][0].update(source_id="G9999:R1"),
                       lambda b: b["openings"][1].update(id="R1"),
                       lambda b: b["openings"][0].update(id="R3"),
                       lambda b: b["lineage"][0].update(target_ids=["R3"]),
                       lambda b: b["lineage"][0].update(disposition="parked", target_ids=["R1"])):
            job, body, prior = self.sample()
            mutate(body)
            self.assertFalse(r.validate_generation(job, body, self.case, prior)["valid"])

    def test_source_refs_bare_unknown_duplicate_and_malformed(self):
        for refs in (["R1"], ["resources[999]"], ["valued_outcome", "valued_outcome"], [["R1"]], [], "valued_outcome"):
            job, body, prior = self.sample()
            body["openings"][0]["source_refs"] = refs
            self.assertFalse(r.validate_generation(job, body, self.case, prior)["valid"])

    def test_typed_fields_and_exact_shape(self):
        for mutate in (lambda b: b.update(case_id=1), lambda b: b.update(role="D"),
                       lambda b: b.update(assessment=[]), lambda b: b.update(proposals=[]),
                       lambda b: b["openings"][0].update(prediction=4),
                       lambda b: b["openings"][0].update(fit=True),
                       lambda b: b["lineage"][0].update(target_ids=[{}])):
            job, body, prior = self.sample()
            mutate(body)
            self.assertFalse(r.validate_generation(job, body, self.case, prior)["valid"])

    def test_construction_attack_cap_and_links(self):
        for mutate in (lambda b: b.pop("attacks"), lambda b: b["attacks"].append(copy.deepcopy(b["attacks"][0])),
                       lambda b: b["attacks"][0].update(attack_id="A3"),
                       lambda b: b["attacks"][0].update(source_refs=["R1"]),
                       lambda b: b["attacks"][0].update(source_refs=["valued_outcome"]),
                       lambda b: b["attacks"][0].update(linked_opening_ids=[]),
                       lambda b: b["attacks"][0].update(disposition="critique"),
                       lambda b: b["attacks"][0].update(disposition="no_branch", linked_opening_ids=["R1"])):
            job, body, prior = self.sample("010", 2)
            mutate(body)
            self.assertFalse(r.validate_generation(job, body, self.case, prior)["valid"])
        job, body, prior = self.sample("010", 2)
        body["attacks"][0].update(disposition="no_branch", linked_opening_ids=[])
        self.assertTrue(r.validate_generation(job, body, self.case, prior)["valid"])

    def test_no_opening_remains_valid_and_all_prior_parked(self):
        job, body, prior = self.sample()
        body["openings"] = []
        for row in body["lineage"]:
            row.update(disposition="parked", target_ids=[])
        self.assertTrue(r.validate_generation(job, body, self.case, prior)["valid"])
        artifacts = copy.deepcopy(self.fixture["artifacts"])
        artifacts[job["job_id"]] = body
        packet, _ = self.build(artifacts)
        self.assertEqual(packet["matrix_counts"]["raw_rows"], 52)
        self.assertEqual(packet["matrix_counts"]["unit_rows"], 27)
        uid = r.b.opaque("U", job["job_id"])
        ob = next(o for o in packet["expected_matrix"]["unit_rows"] if o["identity"]["unit_id"] == uid)
        self.assertFalse(ob["null_semantics"])
        self.assertNotIn("no_opening_reason_supported", ob["fixed_values"])

    def test_strict_unique_JSON_keys_and_non_JSON_numbers(self):
        for text in ('{"x":1,"x":2}', '{"nested":{"x":1,"x":2}}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                r.json_text(text)
        self.assertEqual(r.json_text('{"nested":{"x":1}}'), {"nested": {"x": 1}})

    def test_frozen_builder_full_1790_and_1431_conservation(self):
        packet, admin = self.build()
        self.assertEqual(packet, self.saved_fixture)
        self.assertEqual(packet["matrix_counts"], r.MAX_COUNTS)
        self.assertEqual(packet["expected_total_rows"], 1790)
        self.assertEqual(len(packet["units"]), 27)
        self.assertEqual(packet["unresolved_references"], [])
        paths = {x["path"]: x["sha256"] for x in admin["input_bindings"]}
        self.assertEqual(paths[r.SCHEDULE], r.sha(r.R / r.SCHEDULE))
        self.assertEqual(paths[r.REVIEWS], r.sha(r.R / r.REVIEWS))
        self.assertNotIn("generation-schedule.v2.json", paths)
        self.assertNotIn("generation-review-schedule.v2.json", paths)

    def test_builder_never_reads_old_schedules_or_changes_globals(self):
        originals = (r.b.read, r.b.Path, r.b.build_packet, r.raw.base, r.g.read, r.g.jobs)
        original_read = Path.read_text
        original_bytes = Path.read_bytes
        def safe_read(path, *args, **kwargs):
            self.assertNotIn(str(path), {str(r.R / "generation-schedule.v2.json"), str(r.R / "generation-review-schedule.v2.json")})
            return original_read(path, *args, **kwargs)
        def safe_bytes(path, *args, **kwargs):
            self.assertNotIn(str(path), {str(r.R / "generation-schedule.v2.json"), str(r.R / "generation-review-schedule.v2.json")})
            return original_bytes(path, *args, **kwargs)
        with patch.object(Path, "read_text", safe_read), patch.object(Path, "read_bytes", safe_bytes):
            self.build()
        self.assertEqual(originals, (r.b.read, r.b.Path, r.b.build_packet, r.raw.base, r.g.read, r.g.jobs))

    def test_missing_invalid_skipped_packet_dispositions_and_nulls(self):
        artifacts, dispositions = copy.deepcopy(self.fixture["artifacts"]), copy.deepcopy(self.fixture["dispositions"])
        jobs = self.fixture["schedule"]["jobs"]
        for j, execution in zip(jobs[:3], ("invalid", "missing", "skipped")):
            dispositions[j["job_id"]] = {"execution": execution, "cause": "Synthetic terminal failure/skip."}
            if execution != "invalid":
                artifacts.pop(j["job_id"])
        packet, _ = self.build(artifacts, dispositions)
        self.assertEqual(len(packet["units"]), 27)
        self.assertEqual(packet["matrix_counts"]["unit_rows"], 27)
        self.assertTrue(any(ob["null_semantics"] for ob in packet["expected_matrix"]["raw_rows"]))
        review = review_template(packet, packet["review_job_ids"][0])
        self.assertTrue(r.rv.validate_review(packet, review)["valid"])
        dispositions.pop(jobs[0]["job_id"])
        with self.assertRaises(ValueError):
            self.build(artifacts, dispositions)

    def test_review_full_coverage_and_identity_gates(self):
        packet, _ = self.build()
        body = review_template(packet, packet["review_job_ids"][0])
        self.assertTrue(r.rv.validate_review(packet, body)["valid"])
        for mutate in (lambda b: b["candidate_pairs"].pop(), lambda b: b["raw_rows"].append(copy.deepcopy(b["raw_rows"][0])),
                       lambda b: b.update(reviewer_id="old-reviewer"), lambda b: b["raw_rows"][0].__setitem__(2, True)):
            bad = copy.deepcopy(body)
            mutate(bad)
            self.assertFalse(r.rv.validate_review(packet, bad)["valid"])

    def test_lock_fresh_native_witness_and_distinct_handles(self):
        packet, _ = self.build()
        bodies, witnesses, starts = native_pair(packet)
        report = r.reconcile_raw(packet, bodies, witnesses, starts)
        self.assertTrue(report["independent_review_complete"])
        self.assertEqual(len(report["rows"]), 1790)
        for mutate in (lambda w, s: w[1].update(agent_handle=w[0]["agent_handle"]),
                       lambda w, s: w[0].update(terminal_observed=False),
                       lambda w, s: s[0].update(fresh_context=False),
                       lambda w, s: w[0].update(terminal_witness="inferred_from_file"),
                       lambda w, s: s[1].update(native_call_id=s[0]["native_call_id"])):
            w, s = copy.deepcopy(witnesses), copy.deepcopy(starts)
            mutate(w, s)
            with self.assertRaises(ValueError):
                r.reconcile_raw(packet, bodies, w, s)

    def test_failed_review_lock_all_semantics_null(self):
        packet, _ = self.build()
        bodies, witnesses, starts = native_pair(packet)
        witnesses[0]["validation"]["valid"] = False
        bodies[0] = None
        report = r.reconcile_raw(packet, bodies, witnesses, starts)
        self.assertFalse(report["independent_review_complete"])
        self.assertEqual(len(report["rows"]), 1790)
        for row in report["rows"]:
            for field, status in row["field_status"].items():
                self.assertEqual(status, "unobservable")
                self.assertIsNone(row["values"][field])

    def test_family_and_scalar_disagreements_remain_null(self):
        packet, _ = self.build()
        bodies, witnesses, starts = native_pair(packet)
        columns = packet["contract"]["columns"]["raw_rows"]
        bodies[1]["raw_rows"][0][columns.index("novelty")] = "equivalent"
        bodies[1]["raw_rows"][0][columns.index("usefulness")] = 1
        report = r.reconcile_raw(packet, bodies, witnesses, starts)
        row = next(x for x in report["rows"] if x["table"] == "raw_rows")
        self.assertIsNone(row["values"]["novelty"])
        self.assertIsNone(row["values"]["usefulness"])
        self.assertEqual(row["field_status"]["novelty"], "family_unresolved")
        self.assertEqual(row["field_status"]["usefulness"], "scalar_unresolved")
        self.assertEqual(len(report["family_disagreements"]), 1)
        self.assertEqual(len(report["disputes"]), 1)
        self.assertEqual(report["scalar_adjudication"], "unused_unless_separately_admitted")

    def test_state_coverage_preserves_missing_skipped_empty_null(self):
        jobs = {k: {} for k in ("a", "b", "c", "d")}
        log = []
        for key, state in (("a", "valid"), ("b", "invalid"), ("c", "missing")):
            for kind in ("job_prepared", "native_spawn", "native_terminal_join"):
                log.append({"runtime_version": r.VERSION, "job_id": key, "event_kind": kind,
                    "terminal_observed": True, "terminal_witness": "parent_received_NATIVE_FINAL_ANSWER", "execution": state})
        log.append({"runtime_version": r.VERSION, "job_id": "d", "event_kind": "dependency_disposition"})
        out = r.coverage(jobs, log, {"a": {"openings": []}}, {"rows": [{"values": {"x": None}, "field_status": {"x": "unobservable"}}]})
        self.assertEqual([out[x] for x in ("planned", "actual_native_starts", "valid", "invalid", "missing", "skipped", "empty_valid", "null_semantic_fields")], [4, 3, 1, 1, 1, 1, 1, 1])
        with self.assertRaises(ValueError):
            r.state_from_events(jobs, [*log, log[-2]])

    def test_native_start_and_FINAL_never_inferred_from_file(self):
        prepared = {"prompt_sha256": "p", "source_freeze_sha256": "f", "output_ref": "synthetic.json"}
        start = {"agent_handle": "native-1", "native_call_id": "call-1"}
        witness = {"native_start_observed": True, "fresh_context": True, "turn": 1, "job_id": "j",
                   **start, "prompt_sha256": "p", "source_freeze_sha256": "f"}
        r.start_valid("j", "native-1", witness, prepared, [])
        with self.assertRaises(ValueError):
            r.start_valid("j", "native-1", {}, prepared, [])
        final = {"native_final_observed": True, "terminal_witness": "parent_received_NATIVE_FINAL_ANSWER",
                 "job_id": "j", **start, "prompt_sha256": "p", "source_freeze_sha256": "f",
                 "output_ref": "synthetic.json", "output_sha256": None}
        r.final_valid("j", "native-1", final, prepared, start, None)
        for field in ("native_final_observed", "prompt_sha256", "source_freeze_sha256", "output_ref", "output_sha256", "native_call_id"):
            wrong = dict(final)
            wrong[field] = "drift"
            with self.assertRaises(ValueError):
                r.final_valid("j", "native-1", wrong, prepared, start, None)


class I11MemoryOnlyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schedule, cls.reviews = r.schedules()
        cls.case = r.read(r.R / "cases/H-P.json")
        cls.prompt = (r.R / "prompts/composition-i11-draft-v2/I11-000-S1.txt").read_bytes()
        cls.portfolio = r.read(r.R / "inputs/plan/portfolio.json")
        cls.packet = r.read(r.R / "fixtures/composition-i11-maximal-raw.v2.json")
        cls.review_prompt = (r.R / r.REVIEW_PROMPT).read_bytes()

    def setUp(self):
        self.files, self.log = {}, []
        self.root = MemoryPath(str(r.R), self.files)
        self.path_patch = patch.object(r, "Path", lambda value: value if isinstance(value, MemoryPath) else MemoryPath(value, self.files))
        self.path_patch.start()
        self.addCleanup(self.path_patch.stop)

    def put(self, path, value):
        self.files[str(self.root / path)] = value if isinstance(value, bytes) else (json.dumps(value) + "\n").encode()

    def test_first_save_is_exclusive(self):
        target = self.root / "new.json"
        r.save_new(target, {"first": True})
        initial = target.read_bytes()
        with self.assertRaises(FileExistsError):
            r.save_new(target, {"first": False})
        self.assertEqual(target.read_bytes(), initial)

    def test_source_binding_hash_drift_and_duplicates_rejected(self):
        self.put("source.json", {"first": True})
        bound = r.bindings(["source.json"], self.root)
        r.bindings_valid(bound, self.root)
        with self.assertRaises(ValueError):
            r.bindings_valid(bound + bound, self.root)
        self.put("source.json", {"first": False})
        with self.assertRaises(ValueError):
            r.bindings_valid(bound, self.root)

    def admission(self):
        # A wholly synthetic prospective receipt graph, never saved on disk.
        schedule = self.schedule
        reviews = self.reviews
        self.put(r.PACK, {"source_bindings": []})
        self.put(r.SCHEDULE, schedule)
        self.put(r.REVIEWS, reviews)
        self.put(r.BUDGET, {"scored_retries": 0, "review_saved_word_soft_limit": 30000, "preparation_native_call_maximum": 6})
        for path in r.source_paths(self.root):
            if not (self.root / path).exists():
                self.put(path, {"synthetic": True})
        self.put("synthetic-capacity-prompt.txt", b"SYNTHETIC CAPACITY PROMPT")
        capacity_bindings = r.bindings([r.CAPACITY, "synthetic-capacity-prompt.txt"], self.root)
        self.put(r.PACK, {"source_bindings": r.bindings([r.SCHEDULE, r.REVIEWS, r.BUDGET], self.root)})
        digest = r.sha(self.root / r.CAPACITY)
        self.put(r.CAPACITY_VALIDATION, {"classification": "pass", "source_bindings": capacity_bindings,
            "native_fixture_structural_validation": {"valid": True, "output_sha256": digest}, "expected_rows": 1790,
            "actual_native_starts": 1, "actual_native_terminal_joins": 1, "saved_word_soft_limit": 30000})
        independent_bindings = r.bindings(r.source_paths(self.root, False, capacity_bindings), self.root)
        self.put(r.INDEPENDENT, {"classification": "independent_prelaunch_pass", "independent_native_final_observed": True,
            "independent_agent_handle": "SYNTHETIC-INDEPENDENT", "source_bindings": independent_bindings})
        self.put(r.FREEZE, {"files": r.bindings(r.source_paths(self.root, True, capacity_bindings), self.root)})
        self.put(r.ADMISSION, {"status": "pass", "freeze_sha256": r.sha(self.root / r.FREEZE),
            "independent_prelaunch_sha256": r.sha(self.root / r.INDEPENDENT),
            "capacity_validation_sha256": r.sha(self.root / r.CAPACITY_VALIDATION)})
        log = [{"job_id": "CAP-I11-MAXIMAL-RAW", "event_kind": "native_spawn", "agent_handle": "SYNTHETIC-CAPACITY",
                "host_spawn_observed": True, "fresh_context": True},
               {"job_id": "CAP-I11-MAXIMAL-RAW", "event_kind": "preparation_terminal_join", "agent_handle": "SYNTHETIC-CAPACITY",
                "terminal_observed": True, "terminal_witness": "parent_received_NATIVE_FINAL_ANSWER", "output_ref": r.CAPACITY,
                "validation": {"output_sha256": digest}}]
        self.put("receipts/events.jsonl", ("\n".join(json.dumps(e) for e in log) + "\n").encode())

    def test_prospective_exact_admission_and_missing_new_gate_rejected(self):
        self.admission()
        self.assertIn("freeze_sha256", r.ready(self.root))
        self.files.pop(str(self.root / r.ADMISSION))
        with self.assertRaises(FileNotFoundError):
            r.ready(self.root)

    def test_missing_freeze_independent_pass_and_capacity_FINAL_rejected(self):
        self.admission()
        freeze = self.files.pop(str(self.root / r.FREEZE))
        with self.assertRaises(FileNotFoundError):
            r.ready(self.root)
        self.files[str(self.root / r.FREEZE)] = freeze
        self.put("receipts/events.jsonl", b"")
        with self.assertRaisesRegex(ValueError, "actual fresh maximal capacity"):
            r.ready(self.root)
        self.admission()
        body = r.read(self.root / r.INDEPENDENT)
        body["classification"] = "preparation_only"
        self.put(r.INDEPENDENT, body)
        self.put(r.FREEZE, {"files": r.bindings(r.source_paths(self.root, True, r.read(self.root / r.CAPACITY_VALIDATION)["source_bindings"]), self.root)})
        with self.assertRaisesRegex(ValueError, "separate independent"):
            r.ready(self.root)

    def test_exact_freeze_source_coverage_and_drift(self):
        self.admission()
        self.put(r.CODE, {"changed": True})
        with self.assertRaisesRegex(ValueError, "source hash drift"):
            r.ready(self.root)
        self.admission()
        manifest = r.read(self.root / r.FREEZE)
        manifest["files"].pop()
        self.put(r.FREEZE, manifest)
        with self.assertRaisesRegex(ValueError, "exact new I11 source freeze"):
            r.ready(self.root)

    def test_dependency_invalid_missing_skipped_skip_only_the_dependent_cell(self):
        schedule = self.schedule
        jobs = {j["job_id"]: j for j in schedule["jobs"]}
        def synthetic_emit(body):
            receipt = {**body, "runtime_version": r.VERSION, "source_freeze_sha256": "SYNTHETIC"}
            self.log.append(receipt)
            return receipt
        for failure in ("invalid", "missing", "skipped"):
            self.log = []
            if failure == "skipped":
                self.log.append({"runtime_version": r.VERSION, "job_id": "G0401", "event_kind": "dependency_disposition"})
            else:
                for kind in ("job_prepared", "native_spawn", "native_terminal_join"):
                    self.log.append({"runtime_version": r.VERSION, "job_id": "G0401", "event_kind": kind,
                        "execution": failure, "terminal_observed": True, "terminal_witness": "parent_received_NATIVE_FINAL_ANSWER"})
            with patch.object(r, "ready", return_value={"freeze_sha256": "SYNTHETIC"}), patch.object(r, "events", side_effect=lambda: self.log), \
                 patch.object(r, "all_jobs", return_value=jobs), patch.object(r, "emit", side_effect=synthetic_emit), patch.object(r, "R", self.root):
                receipt = r.generation_prepare("G0402")
                self.assertEqual(receipt["status"], "skipped")
                self.assertEqual(r.status(self.log)["G0404"], "pending")
                r.generation_prepare("G0403")
                self.assertEqual(r.status(self.log)["G0403"], "skipped")

    def test_prepared_source_and_prompt_drift_rejected(self):
        self.put("source.json", {"x": 1})
        self.put("prompt.txt", b"SYNTHETIC PROMPT")
        prepared = {"source_freeze_sha256": "f", "input_bindings": r.bindings(["source.json"], self.root),
                    "prompt_ref": "prompt.txt", "prompt_sha256": r.sha(self.root / "prompt.txt")}
        with patch.object(r, "R", self.root), patch.object(r, "ready", return_value={"freeze_sha256": "f"}):
            r.verify_prepared(prepared)
            self.put("prompt.txt", b"DRIFT")
            with self.assertRaisesRegex(ValueError, "prepared prompt drift"):
                r.verify_prepared(prepared)
        with patch.object(r, "R", self.root), patch.object(r, "ready", return_value={"freeze_sha256": "other"}):
            with self.assertRaisesRegex(ValueError, "prepared freeze drift"):
                r.verify_prepared(prepared)

    def test_in_memory_generation_lifecycle_missing_invalid_and_first_save(self):
        jobs = {j["job_id"]: j for j in self.schedule["jobs"]}
        self.put(r.SCHEDULE, self.schedule)
        self.put(r.REVIEWS, self.reviews)
        self.put(r.BUDGET, {"synthetic": True})
        self.put("cases/H-P.json", self.case)
        for j in self.schedule["jobs"]:
            self.put(j["prompt_ref"], self.prompt)
        def synthetic_emit(body):
            receipt = {**body, "runtime_version": r.VERSION, "source_freeze_sha256": "SYNTHETIC"}
            self.log.append(receipt)
            return receipt
        def witness(key, handle, prepared, final=False):
            result = {"job_id": key, "agent_handle": handle, "native_call_id": "CALL-" + handle,
                      "prompt_sha256": prepared["prompt_sha256"], "source_freeze_sha256": "SYNTHETIC"}
            if final:
                path = self.root / prepared["output_ref"]
                result.update(native_final_observed=True, terminal_witness="parent_received_NATIVE_FINAL_ANSWER",
                              output_ref=prepared["output_ref"], output_sha256=r.sha(path) if path.exists() else None)
            else:
                result.update(native_start_observed=True, fresh_context=True, turn=1)
            return result
        with ExitStack() as stack:
            stack.enter_context(patch.object(r, "R", self.root))
            stack.enter_context(patch.object(r, "ready", return_value={"freeze_sha256": "SYNTHETIC"}))
            stack.enter_context(patch.object(r, "events", side_effect=lambda: self.log))
            stack.enter_context(patch.object(r, "all_jobs", return_value=jobs))
            stack.enter_context(patch.object(r, "emit", side_effect=synthetic_emit))
            first = r.generation_prepare("G0401")
            with self.assertRaises(ValueError):
                r.spawn("G0401", "NATIVE-1", {})
            r.spawn("G0401", "NATIVE-1", witness("G0401", "NATIVE-1", first))
            body = {"case_id": "H-P", "role": "raw", "openings": [], "lineage": [], "assessment": "Synthetic honest no-opening."}
            self.put(first["output_ref"], body)
            with self.assertRaises(ValueError):
                r.join("G0401", "NATIVE-1", {})
            terminal = r.join("G0401", "NATIVE-1", witness("G0401", "NATIVE-1", first, True))
            self.assertEqual(terminal["execution"], "valid")
            second = r.generation_prepare("G0402")
            r.spawn("G0402", "NATIVE-2", witness("G0402", "NATIVE-2", second))
            terminal = r.join("G0402", "NATIVE-2", witness("G0402", "NATIVE-2", second, True))
            self.assertEqual(terminal["execution"], "missing")
            self.assertEqual(r.generation_prepare("G0403")["status"], "skipped")
            fourth = r.generation_prepare("G0404")
            r.spawn("G0404", "NATIVE-4", witness("G0404", "NATIVE-4", fourth))
            self.put(fourth["output_ref"], b'{"case_id":"H-P","case_id":"H-P"}')
            terminal = r.join("G0404", "NATIVE-4", witness("G0404", "NATIVE-4", fourth, True))
            self.assertEqual(terminal["execution"], "invalid")
            with self.assertRaises(ValueError):
                r.generation_prepare("G0404")
            self.put(jobs["G0407"]["output_ref"], body)
            with self.assertRaisesRegex(ValueError, "first substantive"):
                r.generation_prepare("G0407")

    def test_original_pilot_nonadvancement_disposes_confirmation_explicitly(self):
        jobs = {j["job_id"]: j for j in self.schedule["jobs"]}
        self.put("inputs/plan/portfolio.json", self.portfolio)
        policy = next(x for x in self.portfolio["studies"] if x["id"] == "I11")
        locks = [r.packet_ref(case, "lock") for case in r.CASES[:2]]
        for path in locks:
            self.put(path, {"independent_review_complete": False})
        gate = {"status": "stop", "confirmation_allowed": False, "decision_status": "no_advantage",
                "reason": "Synthetic original-policy nonadvancement; not a semantic finding.",
                "policy_source_sha256": r.sha(self.root / "inputs/plan/portfolio.json"),
                "failure_or_elimination": policy["failure_or_elimination"],
                "pilot_lock_bindings": r.bindings(locks, self.root)}
        self.put("receipts/gates/I11-pilot-lock.json", gate)
        with patch.object(r, "R", self.root), patch.object(r, "ready", return_value={}), \
             patch.object(r, "all_jobs", return_value=jobs), patch.object(r, "events", return_value=[]), \
             patch.object(r, "bound_case", return_value=({"independent_review_complete": False}, {"independent_review_complete": False})), \
             patch.object(r, "emit", side_effect=lambda body: body):
            result = r.generation_prepare("G0455")
            self.assertEqual(result["status"], "skipped")
            self.assertEqual(result["cause"], "original_I11_pilot_policy_prevents_confirmation")
            gate.update(status="pass", confirmation_allowed=True, decision_status="advance_screen")
            self.put("receipts/gates/I11-pilot-lock.json", gate)
            with self.assertRaisesRegex(ValueError, "complete observed dual pilot"):
                r.generation_prepare("G0455")

    def test_in_memory_opaque_dual_review_lifecycle_and_lock(self):
        jobs = {j["job_id"]: j for j in [*self.schedule["jobs"], *self.reviews["jobs"]]}
        self.put(r.BUDGET, {"synthetic": True})
        self.put(r.REVIEW_PROMPT, self.review_prompt)
        self.put(r.packet_ref("H-P", "packet"), self.packet)
        self.put(r.packet_ref("H-P", "map"), {"input_bindings": r.bindings([r.BUDGET], self.root)})
        selected = [j for j in self.schedule["jobs"] if j["case_id"] == "H-P"]
        for j in selected:
            for kind in ("job_prepared", "native_spawn", "native_terminal_join"):
                self.log.append({"runtime_version": r.VERSION, "job_id": j["job_id"], "event_kind": kind,
                    "execution": "valid", "terminal_observed": True, "terminal_witness": "parent_received_NATIVE_FINAL_ANSWER"})
        def synthetic_emit(body):
            receipt = {**body, "runtime_version": r.VERSION, "source_freeze_sha256": "SYNTHETIC"}
            self.log.append(receipt)
            return receipt
        with ExitStack() as stack:
            stack.enter_context(patch.object(r, "R", self.root))
            stack.enter_context(patch.object(r, "ready", return_value={"freeze_sha256": "SYNTHETIC"}))
            stack.enter_context(patch.object(r, "events", side_effect=lambda: self.log))
            stack.enter_context(patch.object(r, "all_jobs", return_value=jobs))
            stack.enter_context(patch.object(r, "emit", side_effect=synthetic_emit))
            stack.enter_context(patch.object(r, "bound_case", return_value=(self.packet, {})))
            stack.enter_context(patch.object(r, "case_payload", return_value=({}, {j["job_id"]: {"execution": "valid"} for j in selected}, [])))
            for n in (1, 2):
                key = f"RF-R-I11-H-P-{n}"
                prepared = r.review_prepare(key)
                text = (self.root / prepared["prompt_ref"]).read_text()
                self.assertIn("Max30000 saved words soft", text)
                self.assertNotIn("Max6000", text)
                self.assertNotIn("composition-i11-maps", text)
                self.assertNotIn("RF-R-I11-", text)
                handle = f"SYNTHETIC-REVIEW-{n}"
                start = {"job_id": key, "agent_handle": handle, "native_call_id": f"CALL-{n}",
                    "native_start_observed": True, "fresh_context": True, "turn": 1,
                    "prompt_sha256": prepared["prompt_sha256"], "source_freeze_sha256": "SYNTHETIC"}
                r.spawn(key, handle, start)
                body = review_template(self.packet, prepared["assigned_reviewer_id"])
                self.put(prepared["opaque_output_ref"], body)
                final = {**start, "native_final_observed": True, "terminal_witness": "parent_received_NATIVE_FINAL_ANSWER",
                    "output_ref": prepared["opaque_output_ref"], "output_sha256": r.sha(self.root / prepared["opaque_output_ref"])}
                terminal = r.join(key, handle, final)
                self.assertEqual(terminal["execution"], "valid")
                self.assertEqual(terminal["native_final_witness"], final)
                self.assertEqual((self.root / prepared["output_ref"]).read_bytes(), (self.root / prepared["opaque_output_ref"]).read_bytes())
            result = r.lock("H-P")
            report = r.read(self.root / result["output_ref"])
            self.assertTrue(report["independent_review_complete"])
            self.assertEqual(len(report["rows"]), 1790)
            with self.assertRaises(FileExistsError):
                r.lock("H-P")


if __name__ == "__main__":
    unittest.main(verbosity=2)
