"""The pre-close emitter must bind the actual alias-loaded installed host."""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch


HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('t31_installed_first_emitter',HERE/'native_first_emitter.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)


class AliasHostTests(unittest.TestCase):
    def test_actual_alias_service_and_modules_selected(self):
        api=Path('/selected/repository/product/lab/release-candidates/v1/interface/api-next')
        alias='_t03_installed_alias_test'
        package=ModuleType(alias);package.__file__=str(api/'__init__.py')
        modules={alias:package}
        for name in ('protocol','guard','service','auth','current_legacy_context_sessions','artifact_model'):
            module=ModuleType(alias+'.'+name);module.__file__=str(api/(name+'.py'))
            modules[alias+'.'+name]=module
        Service=type('Service',(),{'__module__':alias+'.service'})
        modules[alias+'.service'].Service=Service
        originals={key:sys.modules.get(key) for key in modules}
        try:
            sys.modules.update(modules)
            selected,actual=E.host_package(Service(),api)
            self.assertEqual(selected,alias)
            self.assertIs(actual['service'],modules[alias+'.service'])
            modules[alias+'.artifact_model'].__file__='/foreign/artifact_model.py'
            with self.assertRaisesRegex(ValueError,'module origin differs'):
                E.host_package(Service(),api)
        finally:
            for key,prior in originals.items():
                if prior is None:sys.modules.pop(key,None)
                else:sys.modules[key]=prior

    def test_installed_root_carrier_catalog_when_selected(self):
        import os
        root=os.environ.get('CAL_INSTALLED_REPOSITORY')
        if not root:self.skipTest('installed root not selected')
        carrier=E.carrier_validator(Path(root))
        self.assertEqual(type(carrier).__name__,'OriginalCarriers')

    def test_same_root_different_api_directory_refused(self):
        import hashlib
        root=Path('/selected/repository')
        api=root/'product/lab/release-candidates/v1/interface/api-foreign'
        provider=ModuleType('cal_installed_runtime_selection_v1')
        provider.root=lambda:root
        provider.require_runtime_ready=lambda:None
        provider.guard=lambda:None
        source={'path':'product/lab/release-candidates/v1/interface/api-selected/source-manifest.json',
                'sha256':'a'*64}
        profile={'path':'product/lab/release-candidates/v1/interface/api-selected/contract-profile.json',
                 'sha256':'b'*64}
        provider.binding=lambda slot:source if slot=='api.source' else profile
        digest=hashlib.sha256((HERE/'native_first_emitter.py').read_bytes()).hexdigest()
        with patch.dict(sys.modules,{'cal_installed_runtime_selection_v1':provider}),\
             patch.object(Path,'is_dir',return_value=True):
            with self.assertRaisesRegex(ValueError,'another installed API Source/profile'):
                E.NativeFirstEmitter(api_directory=api,source_sha256='a'*64,
                    profile_sha256='b'*64,control_path='/tmp/fixture-grant',
                    control_sha256='c'*64,adapter_sha256=digest)


if __name__=='__main__':unittest.main()
