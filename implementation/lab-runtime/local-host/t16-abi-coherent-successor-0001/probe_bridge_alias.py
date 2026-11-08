"""Diagnostic only: test whether current family can satisfy one old adapter AST.

The in-memory alias is intentionally not an API cut or T16 qualification.
"""
import importlib, importlib.util, json, sys, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
INSTALL=Path('/tmp/cal-T03-native-install-20261023/0001')
sys.path.insert(0,str(INSTALL/'deps'))
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v60-t16-abi423-0001'
NAME='_cal_t16_alias_diagnostic'
spec=importlib.util.spec_from_file_location(NAME,API/'__init__.py',submodule_search_locations=[str(API)])
package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
guard=importlib.import_module(NAME+'.guard')
guard.verify('8fa16946889b0bf9fdb83895d3162c9549bcc867f307729359220d8ecaecb184')
source=importlib.import_module(NAME+'.source_bridge')
source.custody_delivery=source.current_legacy_delivery
tests=importlib.import_module(NAME+'.test_metadata_scope')
tests.PROFILE='94427e61f76b5c8b26a4bae2036433863f7e8dccb49eaaaae668bf1a5f72c7c5'
case=tests.MetadataScopes('test_00_current_metadata_after_original_Assignment_expiry')
result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([case]))
print(json.dumps({'diagnostic_only':True,'aliases_original_custody_to_new_current_family':True,
                  'inherited_method':'MetadataScopes.test_00_current_metadata_after_original_Assignment_expiry',
                  'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
                  'success':result.wasSuccessful()},sort_keys=True))
if not result.wasSuccessful():raise SystemExit(1)
