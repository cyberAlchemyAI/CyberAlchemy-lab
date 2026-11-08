"""The candidate smoke must not accept an exit-zero fixture with no PASS result."""

import sys
import unittest

import run_docker


class DockerSmokeAcceptance(unittest.TestCase):
    def test_exit_zero_without_selected_result_is_not_a_journey(self):
        args = [sys.executable, "-B", "-c", 'print("local Work journey: PASS")']
        observed = run_docker.command(args, expected_stdout=b"local Work journey: PASS")
        missing = run_docker.command(args, expected_stdout=b"local Work journey: FAIL")
        self.assertEqual((observed["exit_code"], missing["exit_code"]), (0, 0))
        self.assertTrue(observed["expected_stdout_seen"])
        self.assertFalse(missing["expected_stdout_seen"])


if __name__ == "__main__":
    unittest.main()
