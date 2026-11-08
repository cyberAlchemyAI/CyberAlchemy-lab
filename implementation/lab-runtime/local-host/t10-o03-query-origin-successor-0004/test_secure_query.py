from pathlib import Path
import sys
import types
import unittest

import secure_query
import verify


class SecureOrigin(unittest.TestCase):
    def test_nested_scope_path_is_restored_on_success_and_exception(self):
        before = list(sys.path)
        coupling = str(secure_query.ROOT / 'product/lab/release-candidates/v1/interface/coupling')
        with secure_query.selected_modules():
            self.assertEqual(sys.path.count(coupling), before.count(coupling) + 1)
        self.assertEqual(sys.path, before)
        with self.assertRaisesRegex(ValueError, 'test failure'):
            with secure_query.selected_modules():
                raise ValueError('test failure')
        self.assertEqual(sys.path, before)

    def test_ambient_matching_file_impostors_do_not_execute(self):
        previous = {name: sys.modules.get(name) for name in secure_query.NAMES}
        called = []
        fake = types.ModuleType('common')
        fake.__file__ = str(secure_query.OLD / 'query-successor/common.py')
        def bad(*args, **kwargs):
            called.append(True)
            raise AssertionError('ambient impostor executed')
        fake.sha = bad
        sys.modules['common'] = fake
        fake_query = types.ModuleType('query_run')
        fake_query.__file__ = str(secure_query.OLD / 'query_run.py')
        sys.modules['query_run'] = fake_query
        fake_scope = types.ModuleType('scope')
        fake_scope.__file__ = str(secure_query.OLD / 'query-successor/scope.py')
        sys.modules['scope'] = fake_scope
        try:
            with secure_query.selected_modules() as (runner, modules):
                self.assertIsNot(modules['common'], fake)
                self.assertIsNot(runner, fake_query)
                self.assertIsNot(modules['scope'], fake_scope)
                self.assertEqual(modules['common'].sha(b'a'), secure_query.sha(b'a'))
            self.assertFalse(called)
            self.assertIs(sys.modules['common'], fake)
        finally:
            for name, module in previous.items():
                if module is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = module

    def test_wrong_pinned_code_digest_refuses(self):
        with self.assertRaisesRegex(ValueError, 'selected executable bytes changed'):
            secure_query.read_exact(secure_query.OLD / 'query-successor/common.py', '0' * 64)

    def test_unselected_loader_refuses(self):
        with secure_query.selected_modules() as (_, modules):
            with self.assertRaisesRegex(ValueError, 'unselected query loader origin'):
                modules['common'].module('unexpected', secure_query.LOADER)

    def test_scope_restriction(self):
        with self.assertRaisesRegex(ValueError, 'unselected secure query scope'):
            secure_query.execute('O05-source-interpretation')

    def test_cold_join_of_actual_current_and_historical_answers(self):
        result = verify.verify()
        self.assertEqual(set(result['scopes']), {'current-specialist-owner', 'historical-d73-slice'})
        self.assertFalse(result['o05_source_scope_selected'])

    def test_changed_secure_result_pin_refuses(self):
        original = verify.CASES['current-specialist-owner']
        try:
            verify.CASES['current-specialist-owner'] = (original[0], '0' * 64, original[2], original[3])
            with self.assertRaisesRegex(ValueError, 'retained secure query result changed'):
                verify.verify()
        finally:
            verify.CASES['current-specialist-owner'] = original

    def test_changed_original_receipt_pin_refuses(self):
        original = verify.CASES['historical-d73-slice']
        try:
            verify.CASES['historical-d73-slice'] = (original[0], original[1], original[2], '0' * 64)
            with self.assertRaisesRegex(ValueError, 'frozen query receipt changed'):
                verify.verify()
        finally:
            verify.CASES['historical-d73-slice'] = original


if __name__ == '__main__':
    unittest.main()
