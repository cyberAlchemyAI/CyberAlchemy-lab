from .legacy_fixture_selection import *
"""Actual policy and source-identity checks for Session termination.

The fixtures own their policy files and replay views. Repository source bytes,
callbacks, clocks and captured original grants are never replaced.
"""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

from . import auth as A
from . import example_fixture as F
from .protocol import Schemas, source

PROFILE = None


class TerminationBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = Schemas(PROFILE)
        cls.manager = source.replay_source(PUBLIC_SOURCE_NAME)
        cls.view = cls.manager.__enter__()
        cls.addClassCleanup(cls.manager.__exit__, None, None, None)
        cls.materials, cls.metadata, cls.target = F.materials_for(cls.view)
        cls.events = []

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='cal-R03-termination-boundary-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.root.chmod(0o700)
        from .legacy_context_sessions import R
        self.key, self.path, self.pin = F.provision(
            self.root, PUBLIC_SOURCE_NAME, self.materials, self.metadata,
            principal=R.PRINCIPAL)
        self.channel = A.ReaderChannel(self.path, self.pin, self.schemas)
        self.channel.authenticate(F.proof(self.key, self.channel.challenge))
        self.addCleanup(self.channel.close)
        self.original_basis = copy.deepcopy(self.channel.termination_basis)
        self.assertIsNotNone(self.original_basis)

    def test_01_real_termination_rereads_policy_without_reselecting_source(self):
        counts = {'policy_reads': 0, 'source_selections': 0}

        def observe(frame, event, argument):
            if event != 'call':
                return
            if frame.f_code.co_filename == str(Path(A.__file__)) and frame.f_code.co_name == 'policy_guard':
                counts['policy_reads'] += 1
            if frame.f_code.co_filename == str(Path(A.HERE / 'source_bridge.py')) and frame.f_code.co_name in ('source_selection', 'custody_delivery'):
                counts['source_selections'] += 1

        self.assertIsNone(sys.getprofile())
        try:
            sys.setprofile(observe)
            result = self.channel.termination_guard()
        finally:
            sys.setprofile(None)
        self.assertEqual(result, self.channel.context)
        self.assertEqual(counts, {'policy_reads': 1, 'source_selections': 0})
        self.assertEqual(self.channel.termination_basis, self.original_basis)
        self.events.append({'case': 'actual-policy-read', 'observed': counts})

    def test_02_owned_Project_State_drift_does_not_prevent_termination(self):
        original = self.view.data['config']['scope_ref']
        try:
            self.view.data['config']['scope_ref'] = 'project:owned-termination-drift'
            with self.assertRaises(ValueError):
                self.view.custody_signed_sources.guard()
            self.assertEqual(self.channel.termination_guard(), self.channel.context)
        finally:
            self.view.data['config']['scope_ref'] = original
        self.view.custody_signed_sources.guard()
        self.events.append({'case': 'owned-Project-State-drift', 'source_guard_refused': True,
                            'termination_policy_guard_passed': True})

    def test_03_real_policy_revocation_still_refuses_termination(self):
        original = self.path.read_bytes()
        try:
            self.path.write_bytes(original + b' ')
            with self.assertRaisesRegex(ValueError, 'revoked or changed'):
                self.channel.termination_guard()
        finally:
            self.path.write_bytes(original)
        self.assertEqual(self.channel.termination_basis, self.original_basis)
        self.channel.termination_guard()

    def test_04_actual_policy_mode_drift_still_refuses_termination(self):
        try:
            self.path.chmod(0o400)
            with self.assertRaisesRegex(ValueError, 'owner/mode differ'):
                self.channel.termination_guard()
        finally:
            self.path.chmod(0o600)
        self.channel.termination_guard()

    def test_05_captured_identity_drift_cannot_substitute_original_period(self):
        try:
            self.channel.termination_basis['period_binding']['sha256'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'exact current termination period or Principal differs'):
                self.channel.termination_guard()
        finally:
            self.channel.termination_basis = copy.deepcopy(self.original_basis)
        self.channel.termination_guard()

    def test_06_source_identity_is_not_Agent_authentication_or_extended_permission(self):
        selected = self.original_basis['period_binding']
        raw = (A.ROOT / selected['ref']).read_bytes()
        self.assertEqual(source.sha(raw), selected['sha256'])
        period = source.parse(raw)
        self.assertEqual(period['not_before'], EXPECTED_NOT_BEFORE)
        self.assertEqual(period['expires_at'], EXPECTED_EXPIRES_AT)
        self.assertEqual(period['principal_ref'], EXPECTED_PRINCIPAL)
        self.assertTrue(verify_retained_original_period_chain(source))
        self.assertLessEqual(A.instant(self.channel.policy['expires_at']), A.instant(period['expires_at']))
        self.assertEqual(self.channel.policy['session_control']['max_session_seconds'], 900)
        self.assertEqual(self.channel.context['role_assignment_bindings'], [])
        for field in ('agent_instance_ref', 'assignment_ref', 'session_ref'):
            self.assertIsNone(self.channel.context[field])
        self.assertEqual(self.channel.termination_guard(), self.channel.context)

