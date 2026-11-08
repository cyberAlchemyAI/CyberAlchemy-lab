"""Independent public-only static replay of the frozen observer wrapper."""
from __future__ import annotations

import builtins
import hashlib
from pathlib import Path
import sys
import unittest
from unittest import mock

LOCAL = Path(__file__).resolve().parents[1]
WRAPPER = LOCAL / 'mapper-successor-docker-observer-effect-0001'
sys.path.insert(0, str(WRAPPER))
import wrapper as W


class IndependentChecks(unittest.TestCase):
    def test_exact_captured_observer_buffer_executes_once(self):
        target = W.PREVIOUS / 'observer.py'
        expected = W.checked_bytes(target, W.OBSERVER_SHA)
        observed_reads = []
        observed_compiles = []
        original_read = W.checked_bytes
        original_compile = builtins.compile

        def counted_read(path, *args, **kwargs):
            if Path(path) == target:
                observed_reads.append(1)
            return original_read(path, *args, **kwargs)

        def counted_compile(source, filename, mode, *args, **kwargs):
            if filename == str(target):
                observed_compiles.append(source)
            return original_compile(source, filename, mode, *args, **kwargs)

        with mock.patch.object(W, 'checked_bytes', side_effect=counted_read), \
             mock.patch.object(builtins, 'compile', side_effect=counted_compile):
            selected = W.load_reviewed_observer()
        self.assertEqual(len(observed_reads), 1)
        self.assertEqual(observed_compiles, [expected])
        self.assertFalse(selected.EFFECT_ENABLED)
        self.assertEqual(selected._run_once.__module__, selected.__name__)
        self.assertEqual(hashlib.sha256(expected).hexdigest(), W.OBSERVER_SHA)

    def test_exact_unrun_attempts_and_one_shot_command(self):
        selected = W.load_reviewed_observer()
        self.assertFalse(W.OBSERVATION.exists())
        self.assertFalse(W.ATTEMPT.exists())
        self.assertEqual(selected.COMMAND,
            ['/usr/bin/python3', '-B', str(selected.RELEASE),
             '--execute-reviewed-one-shot'])
        self.assertEqual(W.preflight()['effect'], 'NOT_RUN')
        self.assertFalse(W.OBSERVATION.exists())
        self.assertFalse(W.ATTEMPT.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
