"""Unfrozen authoring run, with no public or current-host qualification."""
import importlib.util
from pathlib import Path
import sys
import unittest

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
HERE = ROOT / 'product/lab/release-candidates/v1/interface/typed-extension-preparation-v7'
name = '_cal_typed_prospective_authoring_v7'
spec = importlib.util.spec_from_file_location(name, HERE / '__init__.py', submodule_search_locations=[str(HERE)])
package = importlib.util.module_from_spec(spec); sys.modules[name] = package; spec.loader.exec_module(package)
module = __import__(name + '.test_prospective', fromlist=['ProspectiveTests'])
suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.ProspectiveTests)
assert suite.countTestCases() == 20
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() and result.testsRun == 20 else 1)
