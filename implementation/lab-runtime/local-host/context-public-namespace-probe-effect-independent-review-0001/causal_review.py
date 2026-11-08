"""Independent inert tests of the frozen public probe effect wrapper."""
from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest import mock

BASE = Path(__file__).resolve().parents[1]
EFFECT = BASE / 'context-public-namespace-probe-effect-0001'
sys.path.insert(0, str(EFFECT))
import wrapper as W


class CapturedObserverImportReview(unittest.TestCase):
    def test_observer_initialization_executes_unchecked_loader(self):
        observed = []
        class UncheckedLoader:
            def create_module(self, spec):
                return None
            def exec_module(self, module):
                # No file is mutated. This stands in for a changed release.py
                # reached by the observer's second path-based module load.
                observed.append(module.__name__)
                module.unchecked_top_level_executed = True
                module.preflight = lambda **_kwargs: None
                module.check_file = lambda *_args: None
                module.docker_call = lambda *_args: None
        def injected_spec(name, path):
            observed.append(str(path))
            return importlib.machinery.ModuleSpec(name, UncheckedLoader())
        with mock.patch.object(importlib.util, 'spec_from_file_location',
                               side_effect=injected_spec):
            release, observer = W.basis()
        self.assertIs(observer.R, release)
        self.assertEqual(observed[0], str(W.PREVIOUS / 'release.py'))
        self.assertEqual(observed[1], 'context_public_probe_release_inert')
        self.assertTrue(release.EFFECT_ENABLED is False)


if __name__ == '__main__':
    unittest.main()
