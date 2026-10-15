"""Run all114 predecessor checks plus12 explicit public representation cases."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    path = HERE / 'source-manifest.json'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == args.source_sha256
    source = json.loads(path.read_bytes())
    for row in source['files']:
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    name = '_cal_typed_extension_wire_checks_v9'
    spec = importlib.util.spec_from_file_location(name, HERE / '__init__.py',
                                                submodule_search_locations=[str(HERE)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    wire = __import__(name + '.test_wire', fromlist=['WireTests'])
    source_selection = __import__(name + '.test_source_selection', fromlist=['SourceSelectionTests'])
    postimage = __import__(name + '.test_postimage', fromlist=['PostimageTests'])
    prospective = __import__(name + '.test_prospective', fromlist=['ProspectiveTests'])
    catalog_binding = __import__(name + '.test_catalog_binding', fromlist=['CatalogBindingTests'])
    predecessor_binding = __import__(name + '.test_predecessor_binding', fromlist=['PredecessorBindingTests'])
    import test_extensions
    import test_bound_extensions
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(cls)
                               for cls in [test_extensions.ExtensionTests,
                                           test_bound_extensions.BoundExtensionTests, wire.WireTests,
                                           source_selection.SourceSelectionTests, postimage.PostimageTests,
                                           prospective.ProspectiveTests, catalog_binding.CatalogBindingTests, predecessor_binding.PredecessorBindingTests]])
    assert suite.countTestCases() == 126
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    for row in source['files']:
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    value = {'schema_version': 'lab-typed-extension-wire-checks/v1-candidate',
             'result': 'PASS' if result.wasSuccessful() and result.testsRun == 126 else 'FAIL',
             'actual_tests': result.testsRun, 'original_C14_cases': 29, 'new_wire_cases': 18, 'new_actual_catalog_selection_cases': 17,
             'new_original_engine_postimage_cases': 14, 'new_prospective_endpoint_cases': 20, 'new_current_catalog_binding_cases': 16, 'new_public_predecessor_representation_cases': 12,
             'failures': len(result.failures), 'errors': len(result.errors),
             'source_sha256': args.source_sha256, 'python': platform.python_version(),
             'actual_public_calls': 0, 'new_host_or_signer_fixtures': 0,
             'whole_API_qualified': False, 'public_handler_qualified': False,
             'actual_owner_outcome': None, 'authority_effect': 'none',
             'claim_ceiling': 'All114 predecessor cases and12 explicit public representation cases over hypothetical D75 copies; independently pinned catalog and runtime envelopes remain distinct. No current host, Actor, owner, public dispatcher or admission qualification.'}
    receipts = HERE / 'receipts'
    receipts.mkdir(exist_ok=True)
    with (receipts / 'checks-0001.json').open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps(value), flush=True)
    raise SystemExit(0 if value['result'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
