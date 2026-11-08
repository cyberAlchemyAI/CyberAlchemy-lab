import unittest

from src.body_war_canary_recovery import advance_effect, classify_recovery, make_recovery_ledger


class RecoveryTests(unittest.TestCase):
    def test_ledger_precedes_effects_and_advances_sequentially(self):
        ledger = make_recovery_ledger("run-1", "orodi-bw-run-1", "runs/run-1", "a" * 64)
        self.assertTrue(ledger["written_before_first_effect"])
        self.assertEqual(advance_effect(ledger, "images-prepared")["effect_epoch"], 1)
        with self.assertRaisesRegex(ValueError, "NON_SEQUENTIAL"):
            advance_effect(ledger, "candidate-exposed")

    def test_recovery_targets_only_exact_known_resources(self):
        ledger = make_recovery_ledger("run-1", "orodi-bw-run-1", "runs/run-1", "a" * 64)
        self.assertEqual(classify_recovery(ledger, {"stable", "gateway"}, set()), "cleanup-required")
        self.assertEqual(classify_recovery(ledger, set(), set()), "recovered")
        self.assertEqual(classify_recovery(ledger, {"stable"}, {"similar-name"}), "blocked-unknown-effect")


if __name__ == "__main__": unittest.main()
