"""Causal checks for the d95 diagnostic Lesson margin selection."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t03_d95_margin_under_test', HERE / 'margin.py')
margin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(margin)


def fixtures():
    source = {'source_binding': {'ref': 'source', 'sha256': 'a' * 64},
              'package_binding': {'ref': 'package', 'sha256': 'b' * 64},
              'period_binding': {'ref': 'period', 'sha256': 'c' * 64},
              'context_source_binding': {'ref': 'context', 'sha256': 'd' * 64}}
    parent = {'source_name': margin.CURRENT_SOURCE_NAME, 'principal_ref': 'principal:Vlad',
              'scope_refs': ['project:lab'], 'authority_effect': 'none',
              'actual_owner_outcome': None,
              'session_control': {'period_binding': source['period_binding']}}
    attachment = {'session_ref': 'session:one', 'agent_instance_ref': 'agent:one'}
    common = {k: parent[k] for k in ('source_name', 'principal_ref', 'scope_refs',
                                    'authority_effect', 'actual_owner_outcome')}
    app = {**common, 'schema_version': 'lab-local-lesson-application-policy/v2-candidate',
           'source8_control': {**source, 'application_journal_scope': None},
           'session_control': {'period_binding': source['period_binding']},
           'allowed_operations': ['lesson.apply'],
           'application_control': {'method_binding': margin.method_binding(margin.APPLICATION_METHOD),
                                   'runtime_identities': dict(attachment)}}
    assessment = {**common, 'schema_version': 'lab-local-lesson-assessment-policy/v1-candidate',
                  'source8_control': {**source, 'application_journal_scope': {
                      'root': '/tmp/private', 'workspace_binding': {'ref': 'workspace:one', 'sha256': 'e' * 64},
                      'manifest_sha256': 'f' * 64}},
                  'session_control': None, 'allowed_operations': ['lesson.assess'],
                  'assessment_control': {'method_binding': margin.method_binding(margin.ASSESSMENT_METHOD)}}
    return source, parent, attachment, app, assessment


class MarginScopeTest(unittest.TestCase):
    def test_exact_application_and_assessment(self):
        source, parent, attachment, app, assessment = fixtures()
        self.assertEqual(margin.check_operator_scope(app, parent, attachment, source), 'application')
        self.assertEqual(margin.check_operator_scope(assessment, parent, attachment, source), 'assessment')

    def test_foreign_family_refused(self):
        source, parent, attachment, app, _ = fixtures()
        app['source_name'] = 'completion-current-participation:foreign'
        with self.assertRaisesRegex(ValueError, 'Source8 family'):
            margin.check_operator_scope(app, parent, attachment, source)

    def test_changed_signed_period_refused(self):
        source, parent, attachment, app, _ = fixtures()
        app['source8_control']['period_binding'] = {'ref': 'period', 'sha256': '0' * 64}
        with self.assertRaisesRegex(ValueError, 'signed Source8'):
            margin.check_operator_scope(app, parent, attachment, source)

    def test_wrong_application_method_refused(self):
        source, parent, attachment, app, _ = fixtures()
        app['application_control']['method_binding']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'application operator method'):
            margin.check_operator_scope(app, parent, attachment, source)

    def test_wrong_session_identity_refused(self):
        source, parent, attachment, app, _ = fixtures()
        app['application_control']['runtime_identities']['session_ref'] = 'session:other'
        with self.assertRaisesRegex(ValueError, 'Session identity'):
            margin.check_operator_scope(app, parent, attachment, source)

    def test_unscoped_assessment_journal_refused(self):
        source, parent, attachment, _, assessment = fixtures()
        assessment['source8_control']['application_journal_scope'] = None
        with self.assertRaisesRegex(ValueError, 'journal scope'):
            margin.check_operator_scope(assessment, parent, attachment, source)

    def test_wrong_assessment_method_refused(self):
        source, parent, attachment, _, assessment = fixtures()
        assessment['assessment_control']['method_binding']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'assessment operator method'):
            margin.check_operator_scope(assessment, parent, attachment, source)

    def test_extra_source8_control_refused(self):
        source, parent, attachment, app, _ = fixtures()
        app['source8_control']['unselected'] = True
        with self.assertRaisesRegex(ValueError, 'signed Source8'):
            margin.check_operator_scope(app, parent, attachment, source)

    def test_added_authority_effect_refused(self):
        source, parent, attachment, app, _ = fixtures()
        app['authority_effect'] = 'admit'
        with self.assertRaisesRegex(ValueError, 'effect differs'):
            margin.check_operator_scope(app, parent, attachment, source)

    def test_foreign_api_package_refused_before_private_config(self):
        name = '_cal_foreign_t03_margin_test'
        module = types.ModuleType(name)
        module.__file__ = str(HERE / 'test_margin.py')
        sys.modules[name] = module
        try:
            with self.assertRaisesRegex(ValueError, 'package origin differs'):
                margin.verify_selection(name)
        finally:
            del sys.modules[name]


if __name__ == '__main__':
    unittest.main()
