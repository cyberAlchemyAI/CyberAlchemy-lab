"""Synthetic loaded-object/code joins. Never import or invoke original producers."""
import ast
import hashlib
import json
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
SOURCE = ROOT / "implementation/lab-runtime/candidates/runtime-completion-0001/workflow/factory_v1.py"
REGISTRY = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v30/workflow_output_registry.py"
REGISTRY_SHA = "8e3a35b1c1d06d4b9d8e343ecc4e4dcee2267f0c695d37c2a4cdd3542673c763"
MODULE = None  # The selected driver injects an exact-byte compiled module.


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


class Fixture:
    def __init__(self, kind="function", optimize=0):
        self.kind = kind
        self.registry = REGISTRY.read_bytes()
        if sha(self.registry) != REGISTRY_SHA:
            raise RuntimeError("REGISTRY_DRIFT")
        self.path = "implementation/lab-workflows/candidates/v1/workflows/engineering.py"
        self.ref = "transition:engineering:designed"
        self.code = {
            "function": b"calls=[]\ndef produce():\n calls.append('called')\n return 17\n",
            "method": b"calls=[]\nclass Worker:\n def produce(self):\n  calls.append('called')\n  return 17\n",
            "classmethod": b"calls=[]\nclass Worker:\n @classmethod\n def produce(cls):\n  calls.append('called')\n  return 17\n",
        }[kind]
        self.module = types.ModuleType("selected_owned_fixture")
        self.module.__file__ = str(ROOT / self.path)
        # Only these fixed inert definitions execute in tests; never the producer.
        exec(compile(self.code, self.module.__file__, "exec", dont_inherit=True,
                     optimize=optimize), self.module.__dict__)
        if kind == "function":
            self.fn, self.instance, entry = self.module.produce, None, "produce"
        elif kind == "method":
            self.instance = self.module.Worker()
            self.fn, entry = self.instance.produce, "Worker.produce"
        else:
            self.instance = self.module.Worker
            self.fn, entry = self.module.Worker.produce, "Worker.produce"
        self.binding = {"path": self.path, "sha256": sha(self.code)}
        self.selection = {"schema_version": "lab-inert-callable-selection/v1",
                          "source_cut": "fixture-cut", "transition_ref": self.ref,
                          "producer_binding": self.binding, "entrypoint": entry,
                          "callable_kind": kind, "compile_optimize": optimize}
        self.inventory = {"schema_version": "lab-inert-producer-source-subset/v1",
                          "source_cut": "fixture-cut", "files": [self.binding]}
        self.expected_selection = sha(raw(self.selection))
        self.expected_inventory = sha(raw(self.inventory))

    def verify(self, **overrides):
        args = dict(expected_selection_sha256=self.expected_selection,
                    source_inventory_raw=raw(self.inventory),
                    expected_inventory_sha256=self.expected_inventory,
                    registry_source_raw=self.registry,
                    expected_registry_source_sha256=REGISTRY_SHA, source_raw=self.code,
                    expected_source_cut="fixture-cut", repository_root=str(ROOT),
                    module=self.module, callable_object=self.fn, expected_instance=self.instance)
        args.update(overrides)
        return MODULE.verify_callable(raw(self.selection), **args)

    def repin(self):
        self.expected_selection = sha(raw(self.selection))
        self.expected_inventory = sha(raw(self.inventory))


class FactoryTests(unittest.TestCase):
    def test_function_method_classmethod_code_match_without_invocation(self):
        for kind in ("function", "method", "classmethod"):
            f = Fixture(kind)
            result = f.verify()
            self.assertEqual(result["observation"], "selected-code-match")
            self.assertEqual(result["producer_invocations"], 0)
            self.assertEqual(result["authority_effect"], "none")
            self.assertFalse(result["actual_instance_custody_verified"])
            self.assertEqual(f.module.calls, [])

    def test_all_compile_optimization_profiles(self):
        for optimize in (0, 1, 2):
            f = Fixture(optimize=optimize)
            self.assertEqual(f.verify()["producer_invocations"], 0)

    def test_selection_inventory_and_registry_byte_drift(self):
        for which in ("selection", "inventory", "registry"):
            f = Fixture()
            if which == "selection":
                f.selection["entrypoint"] = "other"
            elif which == "inventory":
                f.inventory["source_cut"] = "other"
            else:
                f.registry += b"\n"
            with self.assertRaisesRegex(MODULE.BindingRefusal, "SELECTED_DRIFT"):
                f.verify()

    def test_source_bytes_must_match_selected_binding(self):
        f = Fixture()
        with self.assertRaisesRegex(MODULE.BindingRefusal, "SELECTED_DRIFT"):
            f.verify(source_raw=f.code + b"\n")

    def test_coherent_wrong_cut_and_missing_membership_refuse(self):
        f = Fixture()
        f.selection["source_cut"] = "other"
        f.repin()
        with self.assertRaisesRegex(MODULE.BindingRefusal, "SELECTION_CONTEXT"):
            f.verify()
        f = Fixture()
        f.inventory["files"] = [{"path": "fixture/other.py", "sha256": sha(f.code)}]
        f.repin()
        with self.assertRaisesRegex(MODULE.BindingRefusal, "SOURCE_MEMBERSHIP"):
            f.verify()

    def test_duplicate_source_path_refuses(self):
        f = Fixture()
        f.inventory["files"].append(dict(f.binding))
        f.repin()
        with self.assertRaisesRegex(MODULE.BindingRefusal, "INVENTORY_DUPLICATE"):
            f.verify()

    def test_coherent_wrong_family_origin_refuses(self):
        f = Fixture()
        f.selection["transition_ref"] = "transition:research:designed"
        f.repin()
        with self.assertRaisesRegex(MODULE.BindingRefusal, "PRODUCER_ORIGIN"):
            f.verify()

    def test_forged_filename_and_module_registration_refuse(self):
        f = Fixture()
        f.fn.__code__ = f.fn.__code__.replace(co_filename="/fixture/forged.py")
        with self.assertRaisesRegex(MODULE.BindingRefusal, "CALLABLE_ORIGIN"):
            f.verify()
        f = Fixture()
        f.module.produce = lambda: None
        with self.assertRaisesRegex(MODULE.BindingRefusal, "FUNCTION_REGISTRATION"):
            f.verify()

    def test_same_filename_modified_executable_code_refuses(self):
        f = Fixture()
        other = compile(f.code.replace(b"return 17", b"return 18"),
                        f.module.__file__, "exec", dont_inherit=True)
        code = next(c for c in other.co_consts if type(c) is types.CodeType)
        f.fn.__code__ = code
        with self.assertRaisesRegex(MODULE.BindingRefusal, "CODE_MISMATCH"):
            f.verify()

    def test_lookalike_module_globals_refuse(self):
        f = Fixture()
        other = types.ModuleType(f.module.__name__)
        other.__file__ = f.module.__file__
        other.produce = f.fn
        with self.assertRaisesRegex(MODULE.BindingRefusal, "CALLABLE_ORIGIN"):
            f.verify(module=other)

    def test_wrong_exact_instance_and_subclass_refuse(self):
        f = Fixture("method")
        with self.assertRaisesRegex(MODULE.BindingRefusal, "INSTANCE_REGISTRATION"):
            f.verify(expected_instance=f.module.Worker())
        class Other(f.module.Worker):
            pass
        instance = Other()
        with self.assertRaisesRegex(MODULE.BindingRefusal, "INSTANCE_REGISTRATION"):
            f.verify(callable_object=instance.produce, expected_instance=instance)

    def test_module_and_callable_marker_hooks_never_run(self):
        calls = []
        class Marker:
            def __eq__(self, other):
                calls.append("eq")
                return True
            def __call__(self):
                calls.append("call")
        f = Fixture()
        f.module.__file__ = Marker()
        with self.assertRaisesRegex(MODULE.BindingRefusal, "MODULE_ORIGIN"):
            f.verify()
        f = Fixture()
        f.fn.__module__ = Marker()
        with self.assertRaisesRegex(MODULE.BindingRefusal, "CALLABLE_ORIGIN"):
            f.verify()
        f = Fixture()
        with self.assertRaisesRegex(MODULE.BindingRefusal, "CALLABLE_TYPE"):
            f.verify(callable_object=Marker())
        self.assertEqual(calls, [])

    def test_code_constant_comparison_cannot_run_marker_hook(self):
        calls = []
        class Marker:
            def __eq__(self, other):
                calls.append("eq")
                return True
        f = Fixture()
        self.assertTrue(any(type(x) is str for x in f.fn.__code__.co_consts))
        f.fn.__code__ = f.fn.__code__.replace(
            co_consts=tuple(Marker() if type(x) is str else x for x in f.fn.__code__.co_consts))
        with self.assertRaisesRegex(MODULE.BindingRefusal, "CODE_CONSTANT"):
            f.verify()
        self.assertEqual(calls, [])

    def test_no_module_import_or_callable_execution_for_bad_source(self):
        f = Fixture()
        f.code = b"raise RuntimeError('must never execute')\ndef produce():\n return 17\n"
        f.binding["sha256"] = sha(f.code)
        f.repin()
        with self.assertRaisesRegex(MODULE.BindingRefusal, "CODE_MISMATCH"):
            f.verify()
        self.assertEqual(f.module.calls, [])

    def test_registry_alternative_origin_table_is_selected_not_executed(self):
        f = Fixture()
        tables = MODULE.registry_origins(f.registry, REGISTRY_SHA)
        self.assertEqual(len(tables["REGISTRY"]), 28)
        self.assertIn("challenge-handling", tables["IMPLEMENTATION_ORIGINS"])
        self.assertEqual(len(tables["STAGED_PRODUCER_ORIGINS"]), 7)

    def test_family_alternative_and_staged_code_origin_positives(self):
        for path in (
            "product/lab/release-candidates/v1/interface/challenge-resolution-v6/preparation.py",
            "product/lab/release-candidates/v1/interface/api-integration-v23/workflow_stage_producers.py",
        ):
            f = Fixture()
            f.selection["transition_ref"] = "transition:challenge-handling:eligible"
            f.binding["path"] = path
            f.module.__file__ = str(ROOT / path)
            f.fn.__code__ = f.fn.__code__.replace(co_filename=f.module.__file__)
            f.repin()
            self.assertEqual(f.verify()["producer_invocations"], 0)
            self.assertEqual(f.module.calls, [])

    def test_property_registration_is_never_evaluated(self):
        f = Fixture("method")
        calls = []
        def getter(instance):
            calls.append("property")
            return f.fn
        f.module.Worker.produce = property(getter)
        with self.assertRaisesRegex(MODULE.BindingRefusal, "INSTANCE_REGISTRATION"):
            f.verify()
        self.assertEqual(calls, [])

    def test_bounded_nonplain_raw_and_depth_refuse(self):
        f = Fixture()
        with self.assertRaisesRegex(MODULE.BindingRefusal, "SELECTED_BYTES"):
            f.verify(source_raw=object())
        nested = None
        for _ in range(20):
            nested = [nested]
        data = raw(nested)
        with self.assertRaisesRegex(MODULE.BindingRefusal, "DOCUMENT_DATA"):
            MODULE.document(data, sha(data))
