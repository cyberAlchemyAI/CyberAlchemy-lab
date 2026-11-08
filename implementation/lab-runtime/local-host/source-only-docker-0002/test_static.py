"""Effect-disabled checks for the exact public Source development cut."""
from __future__ import annotations

import copy
import datetime as dt
import json
import unittest

import prepare_public as preparation
import source_once
import stage_public


class PublicCutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads((preparation.HERE / "public-cut.json").read_bytes())
        cls.episode = json.loads((preparation.HERE / "generated" / preparation.NEW_FAMILY /
                                  "episode-contract.json").read_bytes())

    def test_exact_constructed_cut_and_generated_bytes(self):
        plan, generated = preparation.construct()
        self.assertEqual(plan, self.plan)
        self.assertEqual(len(plan["public_inputs"]), 933)
        self.assertEqual(len(generated), 8)
        for name, raw in generated.items():
            self.assertEqual(raw, (preparation.HERE / "generated" / name).read_bytes())
        self.assertEqual({row["path"] for row in plan["public_inputs"]},
                         {row["path"] for row in plan["public_provenance"]})

    def test_private_archives_refused_before_read(self):
        for path in preparation.EXCLUDED:
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "private or unknown"):
                preparation.public_bytes(path, None)

    def test_original_role_preimages_and_new_identity(self):
        for name, original_sha in preparation.OLD_ROLE_SHA.items():
            raw = preparation.public_bytes(preparation.OLD_FAMILY + "/" + name, original_sha)
            projected = preparation.project_role(name, raw)
            self.assertNotIn(preparation.OLD_ID.encode(), projected)
            self.assertNotIn(preparation.OLD_AUTH.encode(), projected)
            with self.subTest(role=name), self.assertRaisesRegex(ValueError, "exact Source role preimage"):
                preparation.project_role(name, raw + b"\n")

    def test_current_development_episode_and_causal_rejections(self):
        inside = dt.datetime(2026, 10, 20, 9, tzinfo=dt.timezone.utc)
        source_once.current(self.episode, now=inside, plan=self.plan)
        for change in (
            {"principal_ref": "principal:R03-legacy-session-fixture-0257"},
            {"authorization_binding": {"path": "other", "sha256": "0" * 64}},
            {"authority_effect": "canonical"},
            {"max_session_seconds": 901},
        ):
            variant = copy.deepcopy(self.episode)
            variant.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                source_once.current(variant, now=inside, plan=self.plan)
        for outside in (dt.datetime(2026, 10, 20, 8, 19, tzinfo=dt.timezone.utc),
                        dt.datetime(2026, 10, 21, 8, 20, tzinfo=dt.timezone.utc)):
            with self.subTest(outside=outside), self.assertRaises(ValueError):
                source_once.current(self.episode, now=outside, plan=self.plan)

    def test_existing_stage_refused(self):
        with self.assertRaisesRegex(ValueError, "fresh exact"):
            stage_public.stage(preparation.HERE)


if __name__ == "__main__":
    unittest.main()
