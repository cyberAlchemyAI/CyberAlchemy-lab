import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def loaded(name, path, *, package=False):
    spec = importlib.util.spec_from_file_location(
        name, path, submodule_search_locations=[str(path.parent)] if package else None)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


observer = loaded('_cal_t35_recut_observer_test', HERE / 'observe.py')
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v33-t35-current-reader-0001'
loaded('_cal_t35_recut_api_test', API / '__init__.py', package=True)
service_module = __import__('_cal_t35_recut_api_test.service', fromlist=['Service'])


class ObserverRecutTests(unittest.TestCase):
    def test_actual_service_code_and_changed_code(self):
        selection = observer.verify_boundary_selection(
            HERE / 'selected-boundaries.json',
            '903956f1cdd1bc4825a83d1ecdc63870c4966202fc14192a1c97c44708adff75', ROOT)
        callback = service_module.Service.call
        observer.verify_selection(selection['Service.call'], callback, callback, 'callback')
        original = callback.__code__
        try:
            callback.__code__ = original.replace(co_consts=original.co_consts + ('changed',))
            with self.assertRaisesRegex(observer.BoundaryRefusal, 'BOUNDARY_CALLBACK_CODE_REFUSED'):
                observer.verify_selection(selection['Service.call'], callback, callback, 'callback')
        finally:
            callback.__code__ = original
        observer.verify_selection(selection['Service.call'], callback, callback, 'callback')

    def test_changed_release_pin_and_source_refuse(self):
        with self.assertRaisesRegex(observer.BoundaryRefusal, 'BOUNDARY_RELEASE_PIN_REFUSED'):
            observer.verify_boundary_selection(HERE / 'selected-boundaries.json', '0' * 64, ROOT)
        from unittest.mock import patch
        with patch.object(observer, 'API_SOURCE_SHA256', '0' * 64):
            with self.assertRaisesRegex(observer.BoundaryRefusal, 'BOUNDARY_SELECTION_CONTRACT_REFUSED'):
                observer.verify_boundary_selection(
                    HERE / 'selected-boundaries.json',
                    '903956f1cdd1bc4825a83d1ecdc63870c4966202fc14192a1c97c44708adff75', ROOT)


if __name__ == '__main__':
    unittest.main()
