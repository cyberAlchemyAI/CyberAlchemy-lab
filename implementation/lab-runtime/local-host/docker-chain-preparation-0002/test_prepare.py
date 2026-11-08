"""Causal positive and refusal tests for the effect-disabled selection."""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("docker_chain_prepare_0001", HERE / "prepare.py")
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class PreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selection = prepare.load_closed((HERE / "selection.json").read_bytes())

    def test_exact_27_role_projection_and_inverse_diff(self):
        got = prepare.prepare(copy.deepcopy(self.selection))
        frozen = prepare.load_closed((HERE / "proposed-selection.json").read_bytes())
        self.assertEqual(got, frozen)
        self.assertEqual(len(got["roles"]), 27)
        self.assertEqual({role: sum(row["role"] == role for row in got["roles"])
                          for role in ("source", "reader", "mapped", "context")},
                         {"source": 5, "reader": 7, "mapped": 4, "context": 11})
        self.assertTrue(all(row["preimage"]["sha256"] ==
                            row["inverse_diff"]["inverse_recovered_sha256"]
                            for row in got["roles"]))
        self.assertEqual(got["effect"], "NOT_RUN")
        self.assertFalse(got["feasibility"]["container_ready"])

    def rejects(self, mutate):
        candidate = copy.deepcopy(self.selection)
        mutate(candidate)
        with self.assertRaises(ValueError):
            prepare.prepare(candidate)

    def test_preimage_substitution_refused(self):
        self.rejects(lambda s: s["preimages"][0].update(sha256="0" * 64))

    def test_extra_projection_change_refused(self):
        self.rejects(lambda s: s["expected_projections"][0].update(sha256="0" * 64))

    def test_inverse_patch_mutation_refused(self):
        original = b"alpha\nbeta\n"
        projected = b"alpha\ngamma\n"
        proof = prepare.inverse_diff(original, projected)
        self.assertEqual(prepare.apply_inverse(projected, proof["patch"]), original)
        proof["patch"][1]["old_base64"] = "ZGVsdGEK"
        with self.assertRaises(ValueError):
            prepare.apply_inverse(projected, proof["patch"])

    def test_constructor_substitution_refused(self):
        self.rejects(lambda s: s["inputs"]["constructor"].update(sha256="0" * 64))

    def test_coherent_t35_wrong_file_substitutions_refused(self):
        # Each replacement is a real file with its *correct* SHA, reproducing
        # all four false-provenance cases from independent review DCP-R01.
        bindings = self.selection["inputs"]
        replacements = {
            "constructor": bindings["path_contract"],
            "phase_rebind": bindings["path_contract"],
            "hardener": bindings["path_contract"],
            "path_contract": bindings["compose"],
        }
        for key, replacement in replacements.items():
            with self.subTest(key=key):
                self.rejects(lambda s, k=key, row=replacement: s["inputs"].__setitem__(k, copy.deepcopy(row)))

    def test_source_engine_pin_substitution_refused(self):
        self.rejects(lambda s: s["inputs"]["source_dependencies"]["custody_pins"].update(sha256="0" * 64))

    def test_historical_authorization_cannot_be_fresh_grant(self):
        self.rejects(lambda s: s["episode_proposal"].update(authorization_state="GRANTED"))
        self.rejects(lambda s: s["episode_proposal"].update(scope_ref="scope:historical"))

    def test_historical_period_and_identity_refused(self):
        self.rejects(lambda s: s["episode_proposal"].update(not_before="2026-10-13T00:00:00+00:00",
                                                             expires_at="2026-10-14T00:00:00+00:00"))
        self.rejects(lambda s: s["episode_proposal"].update(principal_ref="principal:R03-legacy-session-fixture-0257"))

    def test_pin_cycle_or_reader_package_refused(self):
        self.rejects(lambda s: s["pin_order"].reverse())
        self.rejects(lambda s: s["pin_order"].insert(3, "reader_package"))

    def test_future_package_digest_refused(self):
        self.rejects(lambda s: s["future_pins"].update(source_package="0" * 64))

    def test_false_container_readiness_refused(self):
        self.rejects(lambda s: s["feasibility"].update(container_ready=True))
        self.rejects(lambda s: s["feasibility"]["blockers"].pop())
        self.rejects(lambda s: s["feasibility"].update(fd_limit_verified=True))
        self.rejects(lambda s: s["feasibility"].update(scratch_capacity_verified=True))
        self.rejects(lambda s: s["feasibility"].update(bubblewrap_available_in_image=True))
        self.rejects(lambda s: s["feasibility"]["native"].update(machine="aarch64"))

    def test_duplicate_json_key_refused(self):
        with self.assertRaises(ValueError):
            prepare.load_closed(b'{"schema_version": 1, "schema_version": 2}')

    def test_native_pin_and_mode(self):
        self.assertEqual(self.selection["inputs"]["native"]["sha256"], prepare.role_stage.NATIVE_SHA)
        self.assertTrue(prepare.checked_bytes(self.selection["inputs"]["native"], executable=True).startswith(b"\x7fELF"))
        self.rejects(lambda s: s["inputs"]["native"].update(sha256="0" * 64))

    def test_original_family_write_path_refused(self):
        self.rejects(lambda s: s["layout"].update(family="/var/lib/cyberalchemy-lab/source8-v1/instances/" +
                                                                s["layout"]["instance"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
