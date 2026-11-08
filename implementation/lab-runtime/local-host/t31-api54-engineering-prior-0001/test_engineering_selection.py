import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v54-t31-engineering-prior-0001'
spec = importlib.util.spec_from_file_location('_t31_api54_engineering_test', PACKAGE / '__init__.py',
                                              submodule_search_locations=[str(PACKAGE)])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
P = __import__(spec.name + '.workflow_producer_outputs', fromlist=['selected_workflow_instance'])
R = __import__(spec.name + '.workflow_output_registry', fromlist=['selected_transition'])


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def witness():
    registry = R.selected_transition('transition:engineering:designed')
    binding = registry['definition_binding']
    public_raw = (ROOT / binding['path']).read_bytes()
    assert hashlib.sha256(public_raw).hexdigest() == binding['sha256']
    executable = json.loads(public_raw)
    executable['decision_profile'] = {
        'scope_ref': 'project:cyberalchemy-v2-to-lab-migration',
        'identity_ref': 'workflow-decision-profile:local',
        'version_ref': 'workflow-decision-profile:local@1',
        'carrier_ref': 'cal.artifact-type.workflow-decision-profile/v1',
        'byte_sha256': 'a' * 64}
    private_raw = compact(executable)
    private_binding = {'ref': 'private:engineering-instance',
                       'sha256': hashlib.sha256(private_raw).hexdigest()}

    class Vault:
        def material(self, actual):
            if actual != private_binding: raise ValueError('wrong private binding')
            return private_raw
    class Host: vault = Vault()
    class Factory:
        source_rows = {(binding['path'], binding['sha256'])}
        plan = {'scope_ref': executable['decision_profile']['scope_ref']}
        def read_public(self, actual):
            if actual != binding: raise ValueError('wrong public binding')
            return public_raw
    return Host(), Factory(), registry, private_binding, executable


class EngineeringSelectionTests(unittest.TestCase):
    def test_exact_original_inputs_profile_only(self):
        host, factory, registry, binding, executable = witness()
        self.assertEqual(P.selected_workflow_instance(host, factory,
            'transition:engineering:designed', binding, registry), executable)
        self.assertEqual(P.selected_workflow_instance(host, factory,
            'transition:engineering:implemented', binding, registry), executable)

    def test_input_substitution_is_refused(self):
        host, factory, registry, binding, executable = witness()
        changed = copy.deepcopy(executable)
        changed['transitions'][0]['input_carriers'] = ['cal.artifact-type.work/v1']
        body = compact(changed)
        class Authorization:
            def material(self, selected): return body
        with self.assertRaises(ValueError):
            P.selected_workflow_instance(host, factory,
                'transition:engineering:designed',
                {'ref': binding['ref'], 'sha256': hashlib.sha256(body).hexdigest()},
                registry, authorization=Authorization())


if __name__ == '__main__': unittest.main()
