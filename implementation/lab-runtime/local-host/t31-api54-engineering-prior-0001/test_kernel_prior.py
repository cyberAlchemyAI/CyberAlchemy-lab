import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / 'product/lab/release-candidates/v1/interface/workflow-transition-v2-t31'
spec = importlib.util.spec_from_file_location('_t31_kernel_prior_test', PACKAGE / '__init__.py',
                                              submodule_search_locations=[str(PACKAGE)])
module = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = module
spec.loader.exec_module(module)
K = __import__(spec.name + '.kernel', fromlist=['plan'])
F = __import__(spec.name + '.fixtures', fromlist=['build'])


def witness():
    message, facts = F.build()
    definition = json.loads(facts['definition_raw'])
    run = json.loads(facts['run_raw'])
    transition = definition['transitions'][0]
    transition.update(transition_ref='transition:engineering:implemented',
                      from_state='designed', to_state='implemented',
                      input_carriers=['cal.artifact-type.work/v1',
                                      'cal.artifact-type.generated-output/v2'])
    definition.update(states=['prepared','designed','implemented','blocked','indeterminate'],
                      terminal_states=['implemented','blocked'])
    definition_binding = {'ref': message['definition_binding']['ref'],
                          'sha256': K.digest(definition)}
    run.update(state='designed', definition_binding=definition_binding)
    run_binding = {'ref': message['run_binding']['ref'], 'sha256': K.digest(run)}
    message.update(transition_ref=transition['transition_ref'], expected_state='designed',
                   definition_binding=definition_binding, run_binding=run_binding)
    header = {'scope_ref': facts['host_grant']['scope_ref'],
              'identity_ref': 'generated-output:local-design',
              'version_ref': 'generated-output:local-design@candidate.1',
              'carrier_ref': 'cal.artifact-type.generated-output/v2',
              'byte_sha256': 'c' * 64}
    message['input_artifacts'] = [run['work'], header]
    facts['selected_headers'][header['version_ref']] = {
        'artifact': copy.deepcopy(header), 'posture': 'produced-current',
        'semantic_kind': 'generated-output'}
    facts['host_grant'].update(run_binding=run_binding,
                               definition_binding=definition_binding,
                               permitted_transitions=[transition['transition_ref']])
    satisfaction = json.loads(facts['satisfaction_raw'])
    satisfaction['subject_binding'] = run_binding
    facts.update(definition_raw=K.encoded(definition), run_raw=K.encoded(run),
                 satisfaction_raw=K.encoded(satisfaction))
    message['satisfaction_report_binding'] = {
        'ref': message['satisfaction_report_binding']['ref'],
        'sha256': K.digest(satisfaction)}
    facts['host_grant']['satisfaction_report_binding'] = message['satisfaction_report_binding']
    return message, facts, header


class KernelPriorTests(unittest.TestCase):
    def test_engineering_implemented_allows_distinct_produced_posture(self):
        message, facts, _ = witness()
        self.assertEqual(K.plan(message, **facts)['event']['to_state'], 'implemented')

    def test_produced_posture_cannot_replace_source_work(self):
        message, facts, _ = witness()
        facts['selected_headers'][json.loads(facts['run_raw'])['work']['version_ref']]['posture'] = 'produced-current'
        with self.assertRaises(ValueError): K.plan(message, **facts)

    def test_produced_posture_cannot_enter_other_phase(self):
        message, facts, _ = witness()
        definition = json.loads(facts['definition_raw'])
        definition['transitions'][0]['transition_ref'] = 'transition:research:executed'
        facts['definition_raw'] = K.encoded(definition)
        message['definition_binding']['sha256'] = K.digest(definition)
        facts['host_grant']['definition_binding'] = message['definition_binding']
        run = json.loads(facts['run_raw'])
        run['definition_binding'] = message['definition_binding']
        facts['run_raw'] = K.encoded(run)
        message['run_binding']['sha256'] = K.digest(run)
        facts['host_grant']['run_binding'] = message['run_binding']
        satisfaction = json.loads(facts['satisfaction_raw'])
        satisfaction['subject_binding'] = message['run_binding']
        facts['satisfaction_raw'] = K.encoded(satisfaction)
        message['satisfaction_report_binding']['sha256'] = K.digest(satisfaction)
        facts['host_grant']['satisfaction_report_binding'] = message['satisfaction_report_binding']
        message['transition_ref'] = 'transition:research:executed'
        facts['host_grant']['permitted_transitions'] = ['transition:research:executed']
        with self.assertRaises(ValueError): K.plan(message, **facts)


if __name__ == '__main__': unittest.main()
