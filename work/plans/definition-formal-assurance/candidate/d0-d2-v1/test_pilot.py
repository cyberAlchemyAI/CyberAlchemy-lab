#!/usr/bin/env python3
"""Semantic failure controls and witness replay, not implementation mirrors."""
import copy
import json
import unittest
from pathlib import Path

import checker
import replay
import verify_evidence

HERE = Path(__file__).resolve().parent


class PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = checker.load(HERE / "interpretation.json")
        cls.bundle = checker.bundle()
        cls.cases = {c["case"]: c for c in cls.bundle["cases"]}

    def test_positive_is_inhabited_combined_theory(self):
        result = self.cases["positive"]["result"]
        self.assertEqual(result["searched"], 192)
        self.assertEqual(result["outcome"], "satisfied")
        witness = next(q["witness"] for q in result["obligations"] if q["obligation_id"] == "provenance-without-authority")
        p, a = replay.facts(witness)
        self.assertTrue(p - a)
        self.assertTrue(p & a)
        self.assertFalse(any(g["object"] in p - a for g in witness["root_grants"]))
        self.assertTrue(replay.verify(witness, self.spec, "required-inhabitation"))

    def test_replay_every_emitted_witness_and_all_configurations(self):
        checks = 0
        for case in self.bundle["cases"]:
            spec = case["input"]
            if case["result"]["execution"] != "completed":
                continue
            for q in case["result"]["obligations"]:
                if q["witness"]:
                    self.assertTrue(replay.verify(q["witness"], spec, q["obligation_id"]))
                    checks += 1
            # Independent evaluation compares all cases, including excluded models.
            for model in checker.models(spec):
                for q in checker.OBLIGATIONS:
                    self.assertEqual(checker.theory_holds(model, spec) and checker.query_holds(model, q), replay.verify(model, spec, q))
                    checks += 1
        self.assertGreater(checks, 3000)

    def test_collapse_fails_only_distinction(self):
        result = self.cases["collapse"]["result"]
        self.assertEqual({q["obligation_id"]: q["outcome"] for q in result["obligations"]},
                         {"combined-satisfiability": "satisfied", "required-inhabitation": "satisfied",
                          "provenance-without-authority": "violated", "permitted-overlap": "satisfied"})

    def test_contradiction_cannot_prove_distinction(self):
        result = self.cases["contradiction"]["result"]
        self.assertEqual(result["obligations"][0]["outcome"], "violated")
        self.assertTrue(all(q["outcome"] == "not-run" for q in result["obligations"][1:]))

    def test_vacuity_is_satisfiable_but_uninhabited(self):
        result = self.cases["vacuity"]["result"]
        self.assertEqual(result["obligations"][0]["outcome"], "satisfied")
        self.assertEqual(result["obligations"][1]["outcome"], "violated")
        self.assertTrue(all(q["outcome"] == "not-run" for q in result["obligations"][2:]))

    def test_missing_dependency_translation_stale_unsupported_timeout(self):
        for name, outcome in [("missing-dependency", "unknown"), ("missing-translation", "unknown"),
                              ("stale", "stale"), ("unsupported", "unsupported"), ("timeout", "unknown")]:
            result = self.cases[name]["result"]
            self.assertEqual(result["outcome"], outcome)
            self.assertEqual(result["readiness"], "unresolved")
            self.assertEqual(result["searched"], 0)

    def test_omitted_requirements_do_not_self_approve(self):
        spec = copy.deepcopy(self.spec)
        spec["required_obligations"] = spec["required_obligations"][:-1]
        self.assertEqual(checker.run(spec)["reason"], "missing-or-substituted-obligation")
        spec = copy.deepcopy(self.spec)
        identity = spec["required_dependencies"].pop()
        del spec["dependencies"][identity]
        self.assertEqual(checker.run(spec)["reason"], "missing-dependency")

    def test_axis_silent_change_rejected_declared_coupling_allowed(self):
        self.assertEqual([replay.frame(m) for m in self.spec["moves"]], [True, False, True])
        self.assertEqual([checker.valid_move(m) for m in self.spec["moves"]], [True, False, True])

    def test_records_need_semantics_beyond_distinct_labels(self):
        record = checker.subject("artifact:local-rule", "complete", True)
        self.assertTrue(checker.authority_holds(record, self.spec["root_grants"]))
        self.assertFalse(checker.authority_holds(record, []))
        for field in ("scope", "object", "basis", "challenge_route"):
            bad = copy.deepcopy(record)
            bad["authority_claim"][field] = "scope:unapproved" if field == "scope" else ""
            self.assertFalse(checker.authority_holds(bad, self.spec["root_grants"]))
        self.assertTrue(checker.provenance_holds(checker.subject("x", "routed-gap", False)))
        self.assertFalse(checker.provenance_holds(checker.subject("x", "unrouted-gap", False)))
        bad = checker.subject("x", "complete", False)
        bad["provenance_path"][0]["relation"] = ""
        self.assertFalse(checker.provenance_holds(bad))

    def test_submitted_witness_cannot_substitute_roots_or_omit_objects(self):
        witness = copy.deepcopy(self.cases["positive"]["result"]["obligations"][1]["witness"])
        self.assertTrue(replay.verify(witness, self.spec, "required-inhabitation"))
        witness["root_grants"] = []
        self.assertFalse(replay.verify(witness, self.spec, "required-inhabitation"))
        witness = copy.deepcopy(self.cases["positive"]["result"]["obligations"][1]["witness"])
        witness["records"].pop()
        self.assertFalse(replay.verify(witness, self.spec, "required-inhabitation"))

    def test_evidence_omission_tampering_and_old_checker_are_rejected(self):
        self.assertGreater(verify_evidence.verify(self.bundle), 0)
        mutations = []
        missing = copy.deepcopy(self.bundle)
        missing["cases"].pop()
        mutations.append(missing)
        omitted = copy.deepcopy(self.bundle)
        omitted["cases"][0]["result"]["obligations"].pop()
        mutations.append(omitted)
        tampered = copy.deepcopy(self.bundle)
        tampered["cases"][0]["result"]["obligations"][0]["witness"]["records"].pop()
        mutations.append(tampered)
        old = copy.deepcopy(self.bundle)
        old["provider"]["checker_sha256"] = "0" * 64
        mutations.append(old)
        for evidence in mutations:
            with self.assertRaises((ValueError, verify_evidence.jsonschema.ValidationError)):
                verify_evidence.verify(evidence)


if __name__ == "__main__":
    unittest.main(verbosity=2)
