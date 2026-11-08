import ast
import hashlib
import importlib.util
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from io import StringIO
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("api30_current_rebind", HERE / "prepare_successor.py")
rebind = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rebind)


class SuccessorPreparation(unittest.TestCase):
    def test_current_authority_and_installed_liblzma_rebind_is_exact(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "profile.json"
            path.write_bytes((rebind.OLD / "contract-profile.json").read_bytes())
            before = json.loads(path.read_text())
            selected = rebind.rebind_current_authority_and_retire_system_liblzma(path)
            after = json.loads(path.read_text())
            old_authority = {"path": rebind.AUTHORITY_CURRENT, "sha256": rebind.AUTHORITY_OLD_SHA}
            old_system = {"path": rebind.OLD_SYSTEM_LIBLZMA, "sha256": rebind.SELECTED_LIBLZMA_SHA}
            expected = list(before["files"])
            expected[expected.index(old_authority)] = selected["current_authority"]
            expected.remove(old_system)
            self.assertEqual(after["files"], expected)
            self.assertEqual(after["files"].count(selected["installed_liblzma"]), 1)
            self.assertEqual({k: v for k, v in after.items() if k != "files"},
                             {k: v for k, v in before.items() if k != "files"})
            with self.assertRaisesRegex(ValueError, "exact current authority or liblzma profile rows differ"):
                rebind.rebind_current_authority_and_retire_system_liblzma(path)
            path.write_text(json.dumps(before))
            original = rebind.digest
            with patch.object(rebind, "digest", side_effect=lambda p: "0" * 64 if p.name == "current.json" else original(p)):
                with self.assertRaisesRegex(ValueError, "current authority byte differs"):
                    rebind.rebind_current_authority_and_retire_system_liblzma(path)
            with patch.object(rebind, "digest", side_effect=lambda p: "0" * 64 if p.name == "liblzma.so.5" else original(p)):
                with self.assertRaisesRegex(ValueError, "selected installed liblzma byte differs"):
                    rebind.rebind_current_authority_and_retire_system_liblzma(path)

    def test_only_stale_duplicate_native_executable_row_is_retired(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "profile.json"
            path.write_bytes((rebind.OLD / "contract-profile.json").read_bytes())
            before = json.loads(path.read_text())["files"]
            stable = rebind.retire_ephemeral_native_executable_row(path)
            after = json.loads(path.read_text())["files"]
            stale = {"path": rebind.OLD_EPHEMERAL_NATIVE_EXE, "sha256": rebind.NATIVE_EXE_SHA}
            self.assertEqual(after, [row for row in before if row != stale])
            self.assertEqual(after.count(stable), 1)
            self.assertEqual(rebind.digest(rebind.ROOT / stable["path"]), stable["sha256"])
            with self.assertRaisesRegex(ValueError, "exact duplicate native executable profile rows differ"):
                rebind.retire_ephemeral_native_executable_row(path)

    def test_current_integration_member_dispatch_origin_is_exact(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "profile.json"
            path.write_bytes((rebind.OLD / "contract-profile.json").read_bytes())
            row = rebind.select_current_integration_members(path, rebind.OUTPUT)
            selected = json.loads(path.read_text())
            self.assertEqual(selected["integration_members_binding"], row)
            self.assertEqual([item for item in selected["files"] if item["path"] == row["path"]], [row])
            self.assertEqual(rebind.digest(rebind.OUTPUT / "integration-members.json"), row["sha256"])
            self.assertEqual(rebind.digest(rebind.ROOT / rebind.OLD_INTEGRATION_MEMBERS), row["sha256"])
            with self.assertRaisesRegex(ValueError, "inherited integration member origin differs"):
                rebind.select_current_integration_members(path, rebind.OUTPUT)

    def test_current_t06_operator_profile_additions_are_exact_and_drift_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "profile.json"
            path.write_bytes((rebind.OLD / "contract-profile.json").read_bytes())
            before = json.loads(path.read_text())
            additions = rebind.include_t06_operator_rows(path)
            after = json.loads(path.read_text())
            self.assertEqual(len(additions), 10)
            self.assertEqual(after["files"][:len(before["files"])], before["files"])
            self.assertEqual(len({row["path"] for row in after["files"]}), len(after["files"]))
            for row in additions:
                self.assertEqual(rebind.digest(rebind.ROOT / row["path"]), row["sha256"])
            path.write_text(json.dumps(before))
            original = rebind.digest
            with patch.object(rebind, "digest", side_effect=lambda p: "0" * 64 if p.name == "driver-selection.json" else original(p)):
                with self.assertRaisesRegex(ValueError, "reviewed T06 operator selection differs"):
                    rebind.include_t06_operator_rows(path)

    def test_both_context_handlers_and_source_selection_are_rebound(self):
        values = {
            "family_path": "implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-test",
            "context_path": "implementation/lab-runtime/local-host/source8-current-fixture/context-successors/legacy-local-test/context-successor-0001",
            "context_sha256": "1" * 64,
            "mapped_package_sha256": "2" * 64,
            "legacy_name": "completion-legacy:legacy-local-test",
            "current_name": "completion-current-participation:legacy-local-test",
            "store": "completion-legacy-local-test",
            "reader_sha256": "3" * 64,
            "not_before": "2026-10-22T00:00:00+00:00",
            "expires_at": "2026-10-23T00:00:00+00:00",
        }
        pairs = rebind.replacements(values)
        for filename in ("source_bridge.py", "current_legacy_context_sessions.py",
                         "current_context_sessions.py", "machine_auth_scope.py",
                         "legacy_fixture_selection.py"):
            old = (rebind.OLD / filename).read_text()
            new = old
            for before, after in pairs:
                new = new.replace(before, after)
            self.assertNotEqual(new, old, filename)
            self.assertTrue(values["family_path"] in new or values["context_sha256"] in new,
                            filename)
            self.assertNotIn(rebind.OLD_LEGACY, new, filename)
            self.assertNotIn(rebind.OLD_OPTIMIZED, new, filename)
        bridge = (rebind.OLD / "source_bridge.py").read_text()
        for before, after in pairs:
            bridge = bridge.replace(before, after)
        self.assertIn(values["context_path"], bridge)
        selection = (rebind.OLD / "legacy_fixture_selection.py").read_text()
        for before, after in pairs:
            selection = selection.replace(before, after)
        self.assertIn("2026-10-13T01:28:58.791379+00:00", selection)
        self.assertIn("verify_retained_original_period_chain", selection)

    def test_incomplete_family_does_not_create_output(self):
        existed = rebind.OUTPUT.exists()
        prior = rebind.digest(rebind.OUTPUT / "source-manifest.json") if existed else None
        with tempfile.TemporaryDirectory(dir=rebind.ROOT / "implementation/lab-runtime/local-host") as temp:
            family = Path(temp)
            with self.assertRaisesRegex(ValueError, "incomplete"):
                rebind.build(family)
            self.assertEqual(rebind.OUTPUT.exists(), existed)
            if existed:
                self.assertEqual(rebind.digest(rebind.OUTPUT / "source-manifest.json"), prior)

    def test_machine_helpers_route_exact_legacy_origins(self):
        original = (rebind.OLD / "machine_context_scope.py").read_text()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "machine_context_scope.py"
            path.write_text(original)
            rebind.route_legacy_machine_scope(path)
            changed = path.read_text()
            self.assertIn("if origin not in ('legacy_context_sessions.py','current_legacy_context_sessions.py'):", changed)
            self.assertIn("machine-context-scope-v4-api33-legacy-0001", changed)
            self.assertIn("machine-context-scope-v5-api33-current-legacy-0001", changed)
            self.assertIn("return _v3_generate", changed)
            self.assertIn('raise ValueError("unselected v3 Machine helper")', changed)
            self.assertNotIn("assert Path(selected.__file__)", changed)
            self.assertEqual(original.count("generate=selected.generate"), 1)

    def test_current_machine_origin_guard_is_exact(self):
        original = (rebind.OLD / "current_machine_context_scope.py").read_text()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "current_machine_context_scope.py"
            path.write_text(original)
            rebind.correct_current_machine_origin(path)
            changed = path.read_text()
            self.assertIn("Path(C.__file__).resolve()==HERE/'current_context_sessions.py'", changed)
            self.assertIn("not Path(C.__file__).is_symlink()", changed)
            self.assertNotIn(".parent.parent==HERE.parent", changed)

    def test_current_source8_test_grant_binds_selected_period(self):
        original = (rebind.OLD / "fixtures.py").read_text()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fixtures.py"
            path.write_text(original)
            rebind.enable_current_source8_test_grant(path)
            changed = path.read_text()
            self.assertIn("source.current_session_fixture_delivery() if source_name==source.CURRENT_SOURCE8_NAME", changed)
            self.assertIn("period=d.reader.HERE/'packages/0001/period.json'", changed)

    def test_schema_guard_keeps_historical_closure_and_checks_successor(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "protocol.py"
            path.write_bytes((rebind.OLD / "protocol.py").read_bytes())
            rebind.adapt_protocol_guard(path)
            changed = path.read_text()
            self.assertIn("historical=HERE.parent/'api-integration-v30'", changed)
            self.assertIn("verify_successor(receipt['successor_manifest_sha256'])", changed)
            self.assertNotIn("mandatory.update(str((HERE/name).relative_to(ROOT))", changed)

    def test_all_runtime_selectors_and_observation_fail_closed_under_optimization(self):
        with tempfile.TemporaryDirectory() as temp:
            for name in rebind.RUNTIME_SELECTOR_MODULES:
                path = Path(temp) / name
                path.write_bytes((rebind.OLD / name).read_bytes())
                rebind.harden_runtime_selector(path)
                self.assertNotIn("assert Path(selected.__file__)", path.read_text(), name)
                self.assertIn('raise ValueError("unselected runtime helper")', path.read_text(), name)
            for name, harden in (("legacy_fixture_selection.py", rebind.harden_retained_expiry_checks),
                                 ("fixture_observation.py", rebind.harden_fixture_observation)):
                path = Path(temp) / name
                path.write_bytes((rebind.OLD / name).read_bytes())
                harden(path)
                self.assertNotIn("assert ", path.read_text(), name)
                compile(path.read_bytes(), str(path), "exec", optimize=2)

    def test_closed_authentication_schema_selects_only_new_source_aliases(self):
        values = {"legacy_name": "completion-legacy:legacy-local-test",
                  "current_name": "completion-current-participation:legacy-local-test"}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "authentication.schema.json"
            path.write_bytes((rebind.OLD / path.name).read_bytes())
            rebind.select_current_authentication_schema(path, values)
            text = path.read_text()
            self.assertNotIn(rebind.OLD_LEGACY_NAME, text)
            self.assertNotIn(rebind.OLD_OPTIMIZED_NAME, text)
            self.assertIn(values["legacy_name"], text)
            self.assertIn(values["current_name"], text)
            self.assertIsInstance(json.loads(text), dict)

    def test_exact_native_role_exclusions_cover_canonical_sql_and_heads(self):
        values = rebind.family_values(rebind.FAMILY)
        self.assertEqual(len(rebind.EXPECTED_ROLE_EXCLUSIONS), 8)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            for name in ("artifact_model.py", "projection.py", "projection_refresh.py", "handlers.py", "guarded_reads.py"):
                (output / name).write_bytes((rebind.OLD / name).read_bytes())
            rebind.install_native_role_dispositions(output / "native_dispositions.py", values)
            rebind.apply_native_role_exclusions(output)
            helper = (output / "native_dispositions.py").read_text()
            self.assertIn(values["mapping_sha256"], helper)
            self.assertIn(values["mapped_package_sha256"], helper)
            self.assertIn("'retained-source-outside-declared-context-selection'", helper)
            self.assertIn("set(origin.subjects) == set(by_ref)", helper)
            for ref in rebind.EXPECTED_ROLE_EXCLUSIONS:
                self.assertIn(ref, helper)
            for name, count in (("artifact_model.py", 1), ("projection.py", 2),
                                ("handlers.py", 1)):
                body = (output / name).read_text()
                self.assertEqual(body.count("native.unrepresentable(view,"), count, name)
                compile(body, str(output / name), "exec", optimize=2)
            self.assertIn("native.excluded_subjects(view)", (output / "handlers.py").read_text())
            self.assertEqual((output / "guarded_reads.py").read_text().count("verify_end(view)"), 2)
            compile(helper, str(output / "native_dispositions.py"), "exec", optimize=2)

    def test_native_mapping_drift_fails_before_build(self):
        original = rebind.digest
        with patch.object(rebind, "digest", side_effect=lambda path: "0" * 64 if path.name == "mapping.json" else original(path)):
            with self.assertRaisesRegex(ValueError, "mapping bytes differ"):
                rebind.family_values(rebind.FAMILY)

    def test_current_profile_selects_exact_native_engine_only(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "source_bridge.py"
            path.write_bytes((rebind.OLD / path.name).read_bytes())
            rebind.select_native_engine_profile(path, {
                "engine_profile_path": "implementation/lab-runtime/local-host/source8-current-fixture/engine-v3/runtime/profile.json"})
            text = path.read_text()
            self.assertIn("if name==CURRENT_SOURCE8_NAME else HERE.parent/'custody-correction-v4/runtime/profile.json'", text)
            self.assertIn("if name==CURRENT_LEGACY_NAME else HERE.parent/'custody-correction-v4/runtime/profile.json'", text)
            tree = ast.parse(text)
            selected = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name in ("legacy_profile_binding", "source8_profile_binding")]
            self.assertEqual(len(selected), 2)
            selected_module = ast.Module(body=selected, type_ignores=[])
            ast.fix_missing_locations(selected_module)
            engine = rebind.ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/engine-v3/runtime/profile.json"
            historical = rebind.ROOT / "product/lab/release-candidates/v1/interface/custody-correction-v4/runtime/profile.json"
            sha = lambda raw: hashlib.sha256(raw).hexdigest()
            class Reader:
                selected_sha = "0" * 64
                def selection(self, *args):
                    return {"engine_pins": {"profile_sha256": self.selected_sha}}
            class Delivery:
                SOURCE_PIN = "source"
                SOURCE_PACKAGE = "package"
                reader = Reader()
            delivery = Delivery()
            def require(value, reason):
                if not value:
                    raise ValueError(reason)
            scope = {"HERE": rebind.OLD, "ROOT": rebind.ROOT, "sha": sha, "require": require,
                     "CURRENT_LEGACY_NAME": "current-legacy", "CURRENT_SOURCE8_NAME": "current-source8",
                     "legacy_delivery_for": lambda name: delivery,
                     "source8_delivery_for": lambda name: delivery}
            exec(compile(selected_module, str(path), "exec"), scope)
            for function_name, current_name in (("legacy_profile_binding", "current-legacy"),
                                                ("source8_profile_binding", "current-source8")):
                with self.assertRaisesRegex(ValueError, "profile differs"):
                    scope[function_name](current_name)
                delivery.reader.selected_sha = sha(engine.read_bytes())
                self.assertEqual(scope[function_name](current_name)["sha256"], delivery.reader.selected_sha)
                delivery.reader.selected_sha = sha(historical.read_bytes())
                self.assertEqual(scope[function_name]("historical")["sha256"], delivery.reader.selected_sha)
                delivery.reader.selected_sha = "0" * 64

    def test_foreign_runtime_helpers_refused_in_normal_and_optimized_python(self):
        selected = {
            "machine_context_scope": ("machine_context_scope_v3_api25_completion_0001", "generation"),
            "classification_preparation": ("classification_preparation_v9", "preparation"),
            "typed_preparation": ("typed_preparation_v4", "preparation"),
            "failure_preparation": ("failure_preparation_v5", "preparation"),
            "lesson_selection": ("lesson_host_v3", "host"),
            "current_lesson_selection": ("current_lesson_host_v1", "host"),
            "lesson_assessment": ("lesson_assessment_v1", "preparation"),
            "lesson_application": ("lesson_application_v1", "preparation"),
            "current_lesson_application": ("current_lesson_application_v1", "preparation"),
            "challenge_resolution": ("challenge_resolution_v6", "preparation"),
        }
        script = """import runpy,sys,types
from pathlib import Path
path=Path(sys.argv[1]);suffix=sys.argv[2];child=sys.argv[3]
name='_cal_'+path.parent.name.replace('-','_')+'_'+suffix
parent=types.ModuleType(name);parent.__path__=[];sys.modules[name]=parent
foreign=types.ModuleType(name+'.'+child);foreign.__file__='/tmp/unselected-runtime-helper.py'
sys.modules[name+'.'+child]=foreign
try:
    selected=runpy.run_path(str(path))
    if path.stem=='challenge_resolution':
        selected['implementation']({'schema_version':'lab-local-integrated-challenge-resolution-policy/v3-candidate'})
except ValueError as error:
    if 'unselected' in str(error):raise SystemExit(0)
    raise
raise SystemExit('foreign helper accepted')
"""
        with tempfile.TemporaryDirectory() as temp:
            api = Path(temp) / rebind.OUTPUT.name
            api.mkdir()
            for stem in selected:
                path = api / (stem + ".py")
                path.write_bytes((rebind.OLD / path.name).read_bytes())
                if stem == "machine_context_scope":
                    rebind.route_legacy_machine_scope(path)
                else:
                    rebind.harden_runtime_selector(path)
            for optimized in (False, True):
                for stem, (suffix, child) in selected.items():
                    args = [sys.executable, "-B", *(["-O"] if optimized else []),
                            "-c", script, str(api / (stem + ".py")), suffix, child]
                    result = subprocess.run(args, text=True, capture_output=True)
                    self.assertEqual(result.returncode, 0, (stem, optimized, result.stderr, result.stdout))

    def test_whole_runner_records_actual_case_timing_and_lease_expiries(self):
        import run_successor as runner
        class Dummy(unittest.TestCase):
            def test_observed(self):
                self.channel = SimpleNamespace(policy={"expires_at": "2026-10-22T22:00:00+00:00"},
                                               context={"expires_at": "2026-10-22T21:59:00+00:00"})
                self.delivery_result = {"expires_at": "2026-10-22T21:58:00+00:00"}
                self.opened_result = {"expires_at": "2026-10-22T21:57:00+00:00"}
        result = unittest.TextTestRunner(stream=StringIO(), resultclass=runner.SuccessResult).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Dummy))
        self.assertTrue(result.wasSuccessful())
        row = result.case_rows[next(iter(result.case_rows))]
        self.assertEqual(row["result"], "PASS")
        self.assertGreaterEqual(row["monotonic_elapsed_seconds"], 0)
        self.assertEqual(row["observed_lease_expiries"]["context_delivery"],
                         "2026-10-22T21:58:00+00:00")
        self.assertEqual(row["observed_lease_expiries"]["session"],
                         "2026-10-22T21:57:00+00:00")

    def test_local_guard_verifies_current_bytes_and_refuses_tamper(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            api = root / rebind.OUTPUT.name
            api.mkdir()
            guard_path = api / "guard.py"
            guard_path.write_bytes((rebind.OLD / "guard.py").read_bytes())
            rebind.install_local_guard(guard_path)
            (api / "payload.py").write_text("VALUE = 1\n")
            (api / "contract-profile.json").write_text("{}\n")
            helper_files = []
            for helper in rebind.MACHINE_HELPERS:
                directory = root / helper
                directory.mkdir()
                for name in ("__init__.py", "generation.py"):
                    selected = directory / name
                    selected.write_text("# exact helper\n")
                    helper_files.append(selected)
            family_source = root / "family-source.json"
            family_source_package = root / "family-source-package.json"
            family_reader = root / "family-reader.json"
            family_mapped = root / "family-mapped.json"
            family_mapping = root / "family-mapping.json"
            family_context = root / "family-context.json"
            family_context_package = root / "family-context-package.json"
            predecessor = root / "predecessor.json"
            engine_profile = root / "engine-profile.json"
            for selected in (family_source, family_source_package, family_reader, family_mapped, family_mapping,
                             family_context, family_context_package, predecessor, engine_profile):
                selected.write_text("{}\n")
            bind = lambda selected: {"path": selected.relative_to(root).as_posix(), "sha256": rebind.digest(selected)}
            manifest = {"schema_version": "lab-api30-current-source-successor/v1",
                        "environment": {"python": platform.python_version(),
                                        "jsonschema": importlib.metadata.version("jsonschema"),
                                        "cryptography": importlib.metadata.version("cryptography")},
                        "authority_effect": "none", "actual_owner_outcome": None,
                        "historical_input_accounting_qualified": False,
                        "claim_ceiling": "Local current bytes only.",
                        "files": [bind(selected) for selected in sorted([*api.iterdir(), *helper_files])],
                        "family_source_manifest_binding": bind(family_source),
                        "family_source_package_binding": bind(family_source_package),
                        "family_reader_manifest_binding": bind(family_reader),
                        "family_mapped_package_binding": bind(family_mapped),
                        "family_mapping_binding": bind(family_mapping),
                        "family_context_manifest_binding": bind(family_context),
                        "family_context_package_binding": bind(family_context_package),
                        "profile_binding": bind(api / "contract-profile.json"),
                        "engine_profile_binding": bind(engine_profile),
                        "predecessor_source_manifest_binding": bind(predecessor)}
            source_manifest = api / "source-manifest.json"
            source_manifest.write_text(json.dumps(manifest, sort_keys=True))
            module_spec = importlib.util.spec_from_file_location("test_api33_local_guard", guard_path)
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)
            module.ROOT = root
            module.verify(rebind.digest(source_manifest))
            (api / "payload.py").write_text("VALUE = 2\n")
            with self.assertRaises(ValueError):
                module.verify(rebind.digest(source_manifest))


if __name__ == "__main__":
    unittest.main()
