"""Read-only and inert fake tests; never dispatch Docker or read protected body."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

import release


class ReleaseTests(unittest.TestCase):
    def test_exact_reviewed_bytes_and_preflight(self):
        checked = release.checked_bytes()
        self.assertEqual(set(checked), set(release.BOUND_NAMES))
        self.assertEqual(hashlib.sha256(checked['controller.py']).hexdigest(),
                         'ced9998c5c6464d156075e3344219672d16a8d4ad7a20da4bf9d0205b2408072')
        self.assertEqual(release.preflight()['effect'], 'NOT_RUN')
        self.assertFalse(os.path.lexists(release.ATTEMPT))

    def test_exact_checked_code_executes_without_second_source_read(self):
        checked = release.checked_bytes()
        previous = {name: sys.modules.get(name) for name in release.MODULE_NAMES}
        with mock.patch.object(release, 'checked_bytes', return_value=checked), \
             mock.patch.object(Path, 'read_bytes',
                               side_effect=AssertionError('second path read')):
            with release.reviewed_controller() as controller:
                self.assertEqual(controller.HERE, release.CONTROLLER)
                self.assertIs(controller.EFFECT_ENABLED, False)
                self.assertEqual(controller.ENTRYPOINT_SHA,
                                 hashlib.sha256(checked['mapper_once.py']).hexdigest())
                for name in release.MODULE_NAMES:
                    self.assertTrue(Path(sys.modules[name].__file__).is_relative_to(
                        release.CONTROLLER))
        for name in release.MODULE_NAMES:
            self.assertIs(sys.modules.get(name), previous[name])

    def test_freeze_and_review_pin_mismatch_refuse(self):
        with mock.patch.object(release, 'CONTROLLER_FREEZE_SHA', '0' * 64):
            with self.assertRaises(release.Refused):
                release.checked_bytes()
        with mock.patch.object(release, 'CONTROLLER_REVIEW_SHA', '0' * 64):
            with self.assertRaises(release.Refused):
                release.checked_bytes()
        self.assertFalse(os.path.lexists(release.ATTEMPT))

    def test_release_effect_switch_is_scoped_to_single_fake_call(self):
        class FakeController:
            EFFECT_ENABLED = False
            calls = 0
            def preflight(self):
                return {'effect': 'NOT_RUN', 'attempt': str(release.ATTEMPT),
                        'no_retry': True}
            def execute(self):
                self.calls += 1
                self.assertion = self.EFFECT_ENABLED
                return {'overall': 'OBSERVED_DOCKER_ONLY', 'synthetic': True}
        fake = FakeController()
        @contextmanager
        def selected():
            yield fake
        with mock.patch.object(release, 'reviewed_controller', selected):
            result = release.execute_reviewed_one_shot()
        self.assertEqual(result['overall'], 'OBSERVED_DOCKER_ONLY')
        self.assertTrue(fake.assertion)
        self.assertFalse(fake.EFFECT_ENABLED)
        self.assertEqual(fake.calls, 1)
        self.assertFalse(os.path.lexists(release.ATTEMPT))

    def test_bad_fake_preflight_refuses_before_effect(self):
        class FakeController:
            EFFECT_ENABLED = False
            def preflight(self):
                return {'effect': 'NOT_RUN', 'attempt': str(release.ATTEMPT),
                        'no_retry': False}
            def execute(self):
                raise AssertionError('fake effect reached')
        fake = FakeController()
        @contextmanager
        def selected():
            yield fake
        with mock.patch.object(release, 'reviewed_controller', selected):
            with self.assertRaisesRegex(release.Refused, 'PREFLIGHT_DRIFT'):
                release.execute_reviewed_one_shot()
        self.assertFalse(fake.EFFECT_ENABLED)

    def test_release_effect_disabled_flag_refuses_before_load(self):
        with mock.patch.object(release, 'EFFECT_ENABLED', False), \
             mock.patch.object(release, 'reviewed_controller',
                               side_effect=AssertionError('loaded')):
            with self.assertRaisesRegex(release.Refused, 'EFFECT_DISABLED'):
                release.execute_reviewed_one_shot()


if __name__ == '__main__':
    unittest.main()
