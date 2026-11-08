"""Pure candidate-plan checks. Never executes Bubblewrap or native code."""
from pathlib import Path
import unittest

from t35_external_v1.phase_scoped_v2 import native_seal_smoke_0001 as smoke


class NativeSealSmokePlan(unittest.TestCase):
    def test_selected_leaves_and_empty_input_are_exact(self):
        self.assertEqual(len(smoke.static_preflight()), 5)
        self.assertEqual(smoke.SYNTHETIC_INPUT,
                         b'{"semantic":[],"governance":[]}\n')
        self.assertEqual(len(smoke.SYNTHETIC_INPUT), smoke.MAX_INPUT_BYTES)

    def test_rendered_sandbox_has_only_readonly_selected_mounts(self):
        scratch = Path('/tmp/lc-u02-05-native-seal-test')
        argv = smoke.render_argv(scratch)
        self.assertEqual(argv.count('--ro-bind'), 5)
        self.assertNotIn('--bind', argv)
        self.assertNotIn('/home/vlad_', argv)
        self.assertNotIn('/var/lib/cyberalchemy-lab', argv)
        self.assertEqual(argv[-7:], [
            '/work/abi/ld-linux-x86-64.so.2', '--inhibit-cache',
            '--library-path', '/work/abi', '/work/native',
            'seal-fixture', '/work/input/events.json'])
        with self.assertRaises(ValueError):
            smoke.render_argv(Path('/home/vlad_/protected'))

    def test_observation_cannot_promote_forced_or_unknown_cleanup(self):
        ok = dict(returncode=0, stdout=smoke.EXPECTED_STDOUT, stderr=b'',
                  child_closed=True, forced_cleanup=False)
        self.assertTrue(smoke.check_observation(**ok))
        self.assertFalse(smoke.check_observation(**(ok | {'child_closed': False})))
        self.assertFalse(smoke.check_observation(**(ok | {'forced_cleanup': True})))
        self.assertFalse(smoke.check_observation(**(ok | {'stdout': b'wrong'})))
        self.assertFalse(smoke.check_observation(**(ok | {'stderr': b'error'})))


if __name__ == '__main__':
    unittest.main()
