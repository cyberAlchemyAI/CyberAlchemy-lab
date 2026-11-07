"""Synthetic/local qualification only. Test gates never install real permissions."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
REPO = PACKAGE.parents[2]
sys.path.insert(0, str(PACKAGE))
from define_runtime.capture import snapshot
from define_runtime.contracts import check
from define_runtime.custody import Custody
from define_runtime.exact import Refusal, binding, decode, encode, pointer, read, sha, write_package
from define_runtime.example import incident_request
from define_runtime.package import export, inspect_local, manifest_for, validate_manifest, verify_package
from define_runtime.prepare import local_ref, prepare
from define_runtime.host import NativeHost
from define_runtime.materialize import materialize, leaves
from define_runtime.observe import observe
from define_runtime.resolve import RecordResolver


class SyntheticGate:
    """Unit-test permission oracle; unavailable from the production CLI."""
    def __init__(self):self.enabled = True;self.calls = []
    def permit(self, operation, scope, subject):
        self.calls.append((operation, scope, subject))
        if not self.enabled:raise Refusal("authority-unavailable", "Synthetic test refusal", 3)
        return {"principal_ref": "synthetic-test-only", "policy_observation_binding": {"sha256": "a" * 64}}


class Runtime(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="define-v2-qualification-")
        self.addCleanup(self.tmp.cleanup);self.root = Path(self.tmp.name)
        self.request = incident_request(REPO)
        self.capture, self.buffers = snapshot(self.request, REPO, permit_retention=True)
        self.inputs = self.root / "inputs";self.inputs.mkdir()
        self.install_buffers()

    def install_buffers(self):
        for path, raw in self.buffers.items():
            p = self.inputs / path;p.parent.mkdir(parents=True, exist_ok=True);p.write_bytes(raw)

    def prepared(self, request=None, capture=None):
        return prepare(encode(request or self.request), encode(capture or self.capture), self.inputs)

    def package(self):
        pack, _, members = self.prepared();destination = self.root / "package"
        export(destination, pack, members)
        return destination, pack, members

    def custody(self):
        root = self.root / "retained";root.mkdir(mode=0o700)
        gate = SyntheticGate()
        return Custody(root, "unit-test-store", "scope:synthetic-only", gate), gate

    def assert_refused(self, callable_, code=None):
        with self.assertRaises(Refusal) as caught:callable_()
        if code:self.assertEqual(caught.exception.code, code)

    def test_closed_pack_and_embedded_application(self):
        pack, report, _ = self.prepared()
        check(pack, "pack")
        self.assertEqual([h["disposition"] for h in pack["handling"]], ["reuse", "propose", "specialize"])
        self.assertTrue(report["application_checks"][0]["fully_bound"])
        self.assertEqual(pack["assessments"][0]["reported_result"], "FAIL")
        self.assertEqual(report["assessment_execution_count"], 0)
        self.assertEqual(pack["readiness"]["prepare-owner-review"]["outcome"], "blocked")

    def test_deterministic_same_original_buffers(self):
        a = self.prepared();b = self.prepared()
        self.assertEqual(a, b)

    def test_strict_json_boundaries(self):
        for raw in [b'{"x":1,"x":2}', b'"\\ud800"', b'"\\u0000"', b'\xff', b'NaN', b'1.0', str(2**53).encode(), b'[' * 66 + b'0' + b']' * 66]:
            with self.subTest(raw=raw[:40]):self.assert_refused(lambda: decode(raw))

    def test_original_uint64_not_rounded(self):
        raw = b'{"integer":18446744073709551615}'
        value = decode(raw, source=True)
        self.assertEqual(value["integer"], 2**64 - 1)
        self.assert_refused(lambda: encode(value), "unsupported-number")

    def test_rfc6901_is_exact(self):
        self.assertEqual(pointer({"a/b": {"~": ["ok"]}}, "/a~1b/~0/0"), "ok")
        for selector in ["/x/01", "/x/-1", "/~9"]:
            self.assert_refused(lambda: pointer({"x": [1, 2]}, selector))

    def test_unknown_and_duplicate_handling_refuse(self):
        for mutation in ["extra", "duplicate", "missing"]:
            r = copy.deepcopy(self.request)
            if mutation == "extra":r["handling"][0]["payload"]["tolerance"] = 1
            elif mutation == "duplicate":r["handling"].append(r["handling"][0])
            else:r["handling"].pop()
            with self.subTest(mutation=mutation):self.assert_refused(lambda: self.prepared(r))

    def test_open_is_honest_inspectable_output(self):
        r = copy.deepcopy(self.request)
        r["required_concepts"].append({"concept_id": "exclusive-scope", "question": "Which exclusions apply?", "scope": "Incident"})
        r["handling"].append({"concept_id": "exclusive-scope", "disposition": "open", "payload": {"question": "Which exclusions apply?", "reason": "Not selected", "affected_use": "apply-parameters", "owner_route": None, "continuation": "Ask the actual incident owner."}})
        pack, _, _ = self.prepared(r)
        self.assertEqual(pack["readiness"]["inspect-preparation"]["outcome"], "ready")
        self.assertEqual(pack["readiness"]["apply-parameters"]["outcome"], "blocked")

    def test_meaning_change_is_local(self):
        r = copy.deepcopy(self.request)
        old = r["handling"][1]["payload"]["working_meaning"]
        meaning = copy.deepcopy(old);meaning["meaning_id"] = "working:changed-criterion";meaning["statement"] += " With a declared new exclusion."
        r["required_concepts"].append({"concept_id": "changed-criterion", "question": "Change meaning?", "scope": "Local proposal"})
        r["handling"].append({"concept_id": "changed-criterion", "disposition": "specialize", "payload": {"mode": "meaning-change", "parent_ref": local_ref(r["request_id"], 1, "working-meaning", 0, old), "working_meaning": meaning, "delta": "New exclusion", "identity_intention": "successor", "applicability": "Candidate comparison only"}})
        pack, _, _ = self.prepared(r)
        self.assertEqual(len(pack["working_meanings"]), 2)
        self.assertEqual(pack["materialization_selection"], [])

    def test_source_digest_mismatch_refuses(self):
        p = self.inputs / self.request["source_bindings"][0]["path"];p.write_bytes(p.read_bytes() + b" ")
        self.assert_refused(self.prepared, "binding-mismatch")

    def test_supplement_cannot_inherit_admission(self):
        c = copy.deepcopy(self.capture)
        next(r for r in c["input_rows"] if r["input_id"] == "authority")["population"] = "local-supplement"
        self.assert_refused(lambda: self.prepared(capture=c), "standing-laundering")

    def test_historical_registry_meaning_refuses(self):
        c = copy.deepcopy(self.capture);next(r for r in c["input_rows"] if r["input_id"] == "authority")["standing_observation"]["status"] = "historical"
        self.assert_refused(lambda: self.prepared(capture=c), "reuse-not-admitted-current")

    def test_reference_identity_and_selector_mismatch_refuse(self):
        for field, value in [("entry_id", "other"), ("selector", "/working_meanings/1"), ("sha256", "f" * 64), ("pack_revision", 2)]:
            r = copy.deepcopy(self.request);r["applications"][0]["meaning_ref"][field] = value
            with self.subTest(field=field):self.assert_refused(lambda: self.prepared(r))

    def test_parameters_are_declared_and_typed(self):
        for name, value in [("tolerance", 1), ("A", 42), ("F", {"arbitrary": True})]:
            r = copy.deepcopy(self.request);r["applications"][0]["bindings"][name] = value
            with self.subTest(name=name):self.assert_refused(lambda: self.prepared(r))

    def test_missing_binding_requires_explicit_gap(self):
        r = copy.deepcopy(self.request);a = r["applications"][0];del a["bindings"]["A"];a["value_provenance"] = [o for o in a["value_provenance"] if o["parameter"] != "A"]
        self.assert_refused(lambda: self.prepared(r), "unreported-binding-gap")
        a["binding_gaps"].append({"gap_id": "parameter:A", "reason": "Account unknown", "affected_use": "apply-parameters", "continuation": "Resolve exact account"})
        # Updating the application also requires updating the exact assessment reference.
        r["assessments"][0]["application_ref"] = local_ref(r["request_id"], 1, "application", 0, a)
        pack, report, _ = self.prepared(r)
        self.assertFalse(report["application_checks"][0]["fully_bound"])
        self.assertEqual(pack["readiness"]["apply-parameters"]["outcome"], "blocked")

    def test_value_provenance_is_not_free_text(self):
        r = copy.deepcopy(self.request);r["applications"][0]["value_provenance"][0]["sha256"] = "0" * 64
        self.assert_refused(lambda: self.prepared(r), "value-provenance-mismatch")

    def test_assessment_cannot_promote_execution(self):
        for key, value in [("validation_posture", "binding-verified-within-scope"), ("producer", {"identity": "invented", "execution_posture": "verified-external", "execution_receipt": None})]:
            r = copy.deepcopy(self.request);r["assessments"][0][key] = value
            with self.subTest(key=key):self.assert_refused(lambda: self.prepared(r))

    def test_imported_pass_fail_unevaluable_remain_reports(self):
        for result in ["PASS", "FAIL", "NOT_EVALUABLE"]:
            r = copy.deepcopy(self.request);a = r["assessments"][0];a["reported_result"] = result
            if result == "NOT_EVALUABLE":a["unevaluable_reason"] = "Missing source"
            pack, report, _ = self.prepared(r)
            self.assertEqual(pack["assessments"][0]["reported_result"], result)
            self.assertEqual(report["assessment_execution_count"], 0)

    def test_new_revision_needs_lineage(self):
        r = copy.deepcopy(self.request);r["request_revision"] = 2
        self.assert_refused(lambda: self.prepared(r))

    def test_live_claim_cannot_be_manufactured(self):
        c = copy.deepcopy(self.capture);c["mode"] = "live-host"
        self.assert_refused(lambda: self.prepared(capture=c), "live-capture-requires-host")

    def test_export_and_cold_local_reconstruction(self):
        destination, pack, _ = self.package();raw, manifest, required, buffers = inspect_local(destination)
        restored = self.root / "restored";write_package(restored, {**buffers, "manifest.json": raw})
        self.assertEqual((restored / "pack.json").read_bytes(), (destination / "pack.json").read_bytes())
        self.assertEqual(decode(buffers["pack.json"])["assessments"][0]["reported_result"], "FAIL")
        self.assertEqual(manifest["package_id"], pack["pack_id"])

    def test_output_no_replace_and_symlink(self):
        for kind in ["directory", "file", "symlink"]:
            destination = self.root / kind
            if kind == "directory":destination.mkdir()
            elif kind == "file":destination.write_text("keep")
            else:destination.symlink_to(self.inputs, target_is_directory=True)
            with self.subTest(kind=kind):self.assert_refused(lambda: write_package(destination, {"x.json": b"{}"}))

    def test_symlink_source_refuses(self):
        p = self.root / "source-link";p.symlink_to(self.inputs / self.request["source_bindings"][0]["path"])
        self.assert_refused(lambda: read(p), "source-unavailable")

    def test_required_members_cannot_be_downgraded(self):
        _, pack, members = self.package();m = manifest_for(pack, members)
        missing = next(i for i, r in m["members"].items() if r["path"].startswith("inputs/"))
        m["members"][missing]["required"] = False;m["required_roots"].remove(missing)
        self.assert_refused(lambda: verify_package(encode(m), lambda _, row: members[row["path"]]), "reconstruction-incomplete")

    def test_member_paths_and_dependencies_are_closed(self):
        pack, _, members = self.prepared()
        for path in ["../escape", "/tmp/escape", "a\\b", "a//b", "CON", "a."]:
            m = manifest_for(pack, members);next(iter(m["members"].values()))["path"] = path
            with self.subTest(path=path):self.assert_refused(lambda: validate_manifest(encode(m)))
        m = manifest_for(pack, members);next(iter(m["members"].values()))["dependencies"] = ["missing"]
        self.assert_refused(lambda: validate_manifest(encode(m)), "invalid-dependency")

    def test_finite_member_cycles_terminate(self):
        pack, _, members = self.prepared();m = manifest_for(pack, members);ids = list(m["members"])
        m["members"][ids[0]]["dependencies"] = [ids[1]];m["members"][ids[1]]["dependencies"] = [ids[0]]
        self.assertEqual(len(validate_manifest(encode(m))[1]), len(ids))

    def test_privacy_refuses_without_changing_bytes(self):
        pack, _, members = self.prepared();members["secret.json"] = b'{"private_key":"synthetic-sensitive-marker"}'
        self.assert_refused(lambda: export(self.root / "bad", pack, members), "private-material")
        self.assertFalse((self.root / "bad").exists())

    def test_custody_round_trip_in_fresh_instance(self):
        _, pack, members = self.package();store, gate = self.custody();raw = encode(manifest_for(pack, members))
        result = store.retain(raw, members, "request-1")
        fresh = Custody(store.root, store.store_id, store.scope, SyntheticGate())
        restored = self.root / "cold-restored"
        observation = fresh.reconstruct(result["locator"], result["receipt_ref"], destination=restored)
        self.assertEqual((restored / "pack.json").read_bytes(), members["pack.json"])
        self.assertIn("Session memory is not retained or restored.", observation["limitations"])
        self.assertEqual(decode((restored / "pack.json").read_bytes())["assessments"][0]["reported_result"], "FAIL")

    def test_custody_idempotency_and_conflict(self):
        _, pack, members = self.package();store, _ = self.custody();raw = encode(manifest_for(pack, members))
        first = store.retain(raw, members, "same")
        self.assertEqual(first, store.retain(raw, members, "same"))
        m = manifest_for(pack, members);m["limitations"].append("different exact root")
        self.assert_refused(lambda: store.retain(encode(m), members, "same"), "idempotency-conflict")

    def test_retained_corruption_never_returns_complete(self):
        _, pack, members = self.package();store, _ = self.custody();raw = encode(manifest_for(pack, members))
        result = store.retain(raw, members, "r")
        store.object_path(sha(members["pack.json"])).write_bytes(b"corrupt")
        self.assert_refused(lambda: store.reconstruct(result["locator"], result["receipt_ref"]), "reconstruction-incomplete")

    def test_retained_receipt_pin_is_required(self):
        _, pack, members = self.package();store, _ = self.custody();raw = encode(manifest_for(pack, members))
        result = store.retain(raw, members, "r")
        self.assert_refused(lambda: store.reconstruct(result["locator"], result["receipt_ref"][:-64] + "f" * 64), "receipt-digest-mismatch")

    def test_revoked_gate_refuses_retained_bytes(self):
        _, pack, members = self.package();store, gate = self.custody();raw = encode(manifest_for(pack, members));result = store.retain(raw, members, "r")
        gate.enabled = False
        self.assert_refused(lambda: store.reconstruct(result["locator"], result["receipt_ref"]), "authority-unavailable")

    def test_retention_rights_must_be_explicit(self):
        capture = copy.deepcopy(self.capture);capture["input_rows"][0]["retention_posture"] = "unresolved"
        pack, _, members = self.prepared(capture=capture);store, _ = self.custody()
        self.assert_refused(lambda: store.retain(encode(manifest_for(pack, members)), members, "r"), "retention-rights-unresolved")

    def test_noncanonical_uri_and_store_mismatch(self):
        store, _ = self.custody()
        for uri in ["file:///tmp/x", "lab-retained://unit-test-store/sha256/" + "A" * 64, "lab-retained://unit-test-store/sha256/" + "a" * 64 + "#/members/%2e%2e"]:
            self.assert_refused(lambda: store.reconstruct(uri, "retention-receipt:unit-test-store:" + "a" * 64 + ":sha256:" + "b" * 64))

    def test_missing_real_host_never_falls_back(self):
        self.assert_refused(lambda: NativeHost(None), "host-selection-required")
        p = self.root / "selection.json";p.write_bytes(b'{}');p.chmod(0o600)
        self.assert_refused(lambda: NativeHost(p), "invalid-fields")

    def test_caller_selection_cannot_install_its_own_host(self):
        b = binding(b"unqualified", "host.py")
        fields = {k: b for k in ["host_binding", "extension_binding", "protocol_binding", "source_profile_binding", "dependency_selection_binding", "source_selection_contract_binding"]}
        selection = {"schema_version": "cal.define.lab-adapter-selection/v1", "selection_id": "fake-caller-choice", "revision": 1, **fields,
                     "schema_bindings": [], "operation_mapping": {}, "credential_locators": [], "authority_posture": "native-current-verifier-required", "limits": {}, "authority_effect": "none"}
        p = self.root / "fake-selection.json";p.write_bytes(encode(selection));p.chmod(0o600)
        self.assert_refused(lambda: NativeHost(p), "host-successor-unqualified")

    def test_later_observation_preserves_pack(self):
        directory, _, _ = self.package();before = (directory / "pack.json").read_bytes()
        observed = observe(directory, "inspect-preparation", "another-reader", REPO, self.root / "observation")
        self.assertEqual(observed["outcome"], "ready")
        changed = observe(directory, "governing-application", "another-reader", REPO, self.root / "changed-use")
        self.assertEqual(changed["outcome"], "blocked")
        self.assertEqual((directory / "pack.json").read_bytes(), before)

    def test_complete_materialization_and_field_lineage(self):
        r, c = copy.deepcopy(self.request), copy.deepcopy(self.capture)
        meaning = r["handling"][1]["payload"]["working_meaning"]
        body = decode(read(REPO / "authority/artifact-types/definition/v2/fixtures/valid/definition.json"))
        body["voices"]["scientific_formal"]["normative_statement"] = meaning["statement"]
        body["voices"]["scientific_formal"]["notation"] = [{"symbol": p["name"], "meaning": p["interpretation"]} for p in meaning["parameters"]]
        body["boundaries"], body["scope"]["applicability"] = meaning["boundaries"], meaning["scope"]
        body["schema_digest"] = sha(read(REPO / "authority/artifact-types/definition/v2/schema.json"))
        body["source_direction"]["generator_sha256"] = sha(read(REPO / "authority/artifact-types/definition/v2/generator.py"))
        def add(path, raw):
            b = binding(raw, path);r["source_bindings"].append(b)
            row = copy.deepcopy(next(row for row in c["input_rows"] if row["population"] == "local-supplement"))
            row["input_id"], row["binding"] = path, b;c["input_rows"].append(row)
            p = self.inputs / path;p.write_bytes(raw)
            return b
        body_binding = add("candidate-definition.json", encode(body))
        lineage = {"schema_version": "cal.define.field-lineage/v1", "authored_by": "synthetic-test-author", "fields": [{"target_selector": path, "source_binding": body_binding, "source_selector": path} for path in leaves(body)], "claim_ceiling": "Authored fixture attribution only; no independent fidelity review.", "authority_effect": "none"}
        lineage_binding = add("candidate-lineage.json", encode(lineage))
        r["materialization_selection"] = [{"meaning_ref": r["applications"][0]["meaning_ref"], "purpose": "Candidate materialization test", "authority_scope": body["scope"]["authority_scope_ref"], "owner_route": "example:unqualified-owner-route", "identity_intention": "new-identity", "parent_ref": None, "definition_binding": body_binding, "field_lineage_binding": lineage_binding}]
        pack, _, members = self.prepared(r, c);directory = self.root / "materialization-pack";export(directory, pack, members)
        report = materialize(directory, self.root / "definitions")
        self.assertEqual(len(report["definitions"]), 1)
        self.assertTrue((self.root / "definitions/definitions/000/DEFINITION.md").is_file())
        self.assertIsNone(report["actual_owner_outcome"])
        # Corrupting the selected source after export cannot replace its frozen bytes.
        (self.inputs / "candidate-definition.json").write_bytes(b"{}")
        materialize(directory, self.root / "definitions-again")

    def test_retained_store_symlink_refuses_foreign_write(self):
        _, pack, members = self.package();store, _ = self.custody();foreign = self.root / "foreign";foreign.mkdir()
        (store.root / "objects").symlink_to(foreign, target_is_directory=True)
        self.assert_refused(lambda: store.retain(encode(manifest_for(pack, members)), members, "r"))
        self.assertEqual(list(foreign.iterdir()), [])

    def test_permission_rechecked_before_receipt_commit(self):
        _, pack, members = self.package();store, gate = self.custody()
        original = store.install
        def interrupt(path, raw):
            original(path, raw)
            if path.parent.name != "journal":gate.enabled = False
        store.install = interrupt
        self.assert_refused(lambda: store.retain(encode(manifest_for(pack, members)), members, "r"), "authority-unavailable")
        self.assertEqual(list((store.root / "packages").glob("*/complete.json")), [])

    def test_exact_work_source_reconstruction_and_candidate_ceiling(self):
        _, pack, members = self.package();store, gate = self.custody()
        receipt = store.retain(encode(manifest_for(pack, members)), members, "r")
        work = decode(read(REPO / "authority/artifact-types/work/v1/fixtures/valid/record.json"))
        source = decode(read(REPO / "authority/artifact-types/source/v1/fixtures/valid/record.json"))
        work["scope_ref"] = source["scope_ref"] = store.scope
        source["payload"].update(locator=receipt["locator"], content_digest=receipt["content_digest"], provenance_refs=[receipt["receipt_ref"]])
        source_ref = source["node_id"] + "@exact-1";work_ref = work["node_id"] + "@exact-1"
        work["payload"]["output_refs"] = [source_ref]
        records = {}
        for ref, body in [(source_ref, source), (work_ref, work)]:
            raw = encode(body)
            records[ref] = {"header": {"scope_ref": store.scope, "identity_ref": body["node_id"], "version_ref": ref, "carrier_ref": "cal.artifact-type." + body["kind"] + "/v1", "byte_sha256": sha(raw)}, "record": body, "raw": raw, "effective_state": "candidate"}
        from jsonschema import Draft202012Validator
        def validate(body, carrier):
            schema = decode(read(REPO / f'authority/artifact-types/{body["kind"]}/v1/schema.json'))
            self.assertTrue(Draft202012Validator(schema).is_valid(body))
        resolver = RecordResolver(records.__getitem__, validate, lambda: "cut-1", gate, store)
        self.assert_refused(lambda: resolver.reconstruct_work(work_ref, "cut-1"), "unselected-record-standing")
        result = resolver.reconstruct_work(work_ref, "cut-1", candidate_inspection=True)
        self.assertEqual(len(result["packages"]), 1)
        self.assertFalse(result["governing_standing_changed"])
        records[source_ref]["record"]["payload"]["content_digest"] = "sha256:" + "f" * 64
        self.assert_refused(lambda: resolver.reconstruct_work(work_ref, "cut-1", candidate_inspection=True), "exact-record-mismatch")

    def test_cli_exit_codes_and_fresh_process_reconstruction(self):
        destination, _, _ = self.package()
        def call(*args):return subprocess.run([sys.executable, "-I", "-B", str(PACKAGE / "define.py"), *map(str, args)], capture_output=True)
        self.assertEqual(call("inspect-package", destination).returncode, 0)
        restored = self.root / "cli-restored"
        self.assertEqual(call("reconstruct-local", destination, "--output", restored).returncode, 0)
        self.assertEqual(call("reconstruct-local", destination, "--output", restored).returncode, 3)
        self.assertEqual(call("compile", destination).returncode, 4)
        self.assertEqual(call("inspect-package", self.root / "missing").returncode, 3)

    def test_bootstrap_refuses_unselected_import_and_ignores_bytecode(self):
        copied_repo = self.root / "copied-repository"
        manifest = decode(read(PACKAGE / "runtime-manifest.json"))
        for row in manifest["files"]:
            destination = copied_repo / row["path"];destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(read(REPO / row["path"]))
        copied_package = copied_repo / "implementation/define-cli/v2"
        (copied_package / "runtime-manifest.json").write_bytes(read(PACKAGE / "runtime-manifest.json"))
        shadow = copied_package / "jsonschema.py";shadow.write_text("raise RuntimeError('UNSELECTED IMPORT EXECUTED')\n")
        command = [sys.executable, "-I", "-B", str(copied_package / "define.py"), "doctor"]
        blocked = subprocess.run(command, capture_output=True)
        self.assertEqual(blocked.returncode, 3)
        self.assertNotIn(b"UNSELECTED IMPORT EXECUTED", blocked.stderr)
        shadow.unlink()
        from importlib.util import cache_from_source
        from importlib._bootstrap_external import _code_to_timestamp_pyc
        source = copied_package / "define_runtime/exact.py";st = source.stat()
        cache = Path(cache_from_source(str(source)));cache.parent.mkdir(exist_ok=True)
        cache.write_bytes(_code_to_timestamp_pyc(compile("raise RuntimeError('UNSELECTED BYTECODE EXECUTED')", str(source), "exec"), int(st.st_mtime), st.st_size))
        good = subprocess.run(command, capture_output=True)
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)


if __name__ == "__main__":unittest.main()
