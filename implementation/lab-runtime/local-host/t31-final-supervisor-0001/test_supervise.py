"""Original 28 transition closure cannot silently drop or duplicate a route."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('t31_final_supervisor',HERE/'supervise.py')
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)


def binding(path):
    return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


class All28PlanTests(unittest.TestCase):
    def make_plan(self,folder):
        inventory=json.loads(S.INVENTORY.read_bytes())
        refs=[row['transition_ref'] for row in inventory['rows']]
        control=folder/'control.json'
        control.write_text(json.dumps({'result':'PASS-actual-known-rule-refusal-and-candidate-detect-binding',
            'api_source_sha256':'a'*64,'api_profile_sha256':'b'*64}))
        config=folder/'stages.json'
        config.write_text(json.dumps({'schema_version':'lab-actual-retained-workflow-run/v1',
            'stages':[{'transition_ref':ref} for ref in refs]}))
        plan={'schema_version':'lab-t31-final-native-supervision/v1','mode':'transitions',
              'installed_repository':'/unused/selected','source_sha256':'a'*64,
              'profile_sha256':'b'*64,'authority_effect':'none',
              'inventory_binding':binding(S.INVENTORY),'control_result_binding':binding(control),
              'steps':[{'name':'all-28','config_binding':binding(config),
                        'expected_transitions':refs}]}
        return plan

    def test_exact_original_28_selected_once(self):
        with tempfile.TemporaryDirectory() as dirname:
            with patch.object(S,'selected',return_value=(None,None)):
                plan=self.make_plan(Path(dirname))
                self.assertIs(S.validate(plan),plan)

    def test_missing_or_duplicate_transition_refused(self):
        with tempfile.TemporaryDirectory() as dirname:
            with patch.object(S,'selected',return_value=(None,None)):
                plan=self.make_plan(Path(dirname))
                plan['steps'][0]['expected_transitions']=plan['steps'][0]['expected_transitions'][:-1]
                with self.assertRaisesRegex(ValueError,'exact config transitions'):
                    S.validate(plan)
                plan=self.make_plan(Path(dirname))
                plan['steps'].append(plan['steps'][0].copy())
                plan['steps'][1]['name']='duplicate'
                with self.assertRaisesRegex(ValueError,'every original transition once'):
                    S.validate(plan)

    def test_phase_can_add_only_fresh_inventory_routes(self):
        with tempfile.TemporaryDirectory() as dirname:
            folder=Path(dirname)
            with patch.object(S,'selected',return_value=(None,None)):
                plan=self.make_plan(folder)
                refs=plan['steps'][0]['expected_transitions']
                config=folder/'stages.json'
                config.write_text(json.dumps({'schema_version':'lab-actual-retained-workflow-run/v1',
                    'stages':[{'transition_ref':ref} for ref in refs[:2]]}))
                plan['steps'][0]['config_binding']=binding(config)
                plan['steps'][0]['expected_transitions']=refs[:2]
                plan['mode']='phase';plan['prior_result_binding']=None
                self.assertIs(S.validate(plan),plan)
                phase=folder/'phase';phase.mkdir();child=phase/'01-first';child.mkdir()
                child_result=child/'RESULT.json'
                child_result.write_text(json.dumps({'result':'PASS','source_sha256':'a'*64,
                    'profile_sha256':'b'*64,'actual_public_transition_commits':2,
                    'cases':[{'transition_ref':ref,'result':'PASS',
                              'actual_native_common_dispatcher':True,'exact_retry_read_only':True}
                             for ref in refs[:2]]}))
                terminal=phase/'01-TERMINAL.json'
                terminal.write_text(json.dumps({'result':'PASS','result_binding':binding(child_result)}))
                prior=phase/'RESULT.json'
                prior.write_text(json.dumps({'schema_version':'lab-t31-final-native-supervision-result/v1',
                    'mode':'phase','result':'PASS-phase','source_sha256':'a'*64,
                    'profile_sha256':'b'*64,'inventory_binding':plan['inventory_binding'],
                    'control_result_binding':plan['control_result_binding'],
                    'prior_result_binding':None,'actual_transition_count':2,
                    'completed_transition_refs':refs[:2],
                    'stage_evidence':[{'terminal_binding':binding(terminal),
                        'child_result_binding':binding(child_result),
                        'expected_transitions':refs[:2]}]}))
                plan['prior_result_binding']=binding(prior)
                config.write_text(json.dumps({'schema_version':'lab-actual-retained-workflow-run/v1',
                    'stages':[{'transition_ref':refs[2]}]}))
                plan['steps'][0]['config_binding']=binding(config)
                plan['steps'][0]['expected_transitions']=[refs[2]]
                self.assertIs(S.validate(plan),plan)
                config.write_text(json.dumps({'schema_version':'lab-actual-retained-workflow-run/v1',
                    'stages':[{'transition_ref':ref} for ref in refs[:2]]}))
                plan['steps'][0]['config_binding']=binding(config)
                plan['steps'][0]['expected_transitions']=refs[:2]
                with self.assertRaisesRegex(ValueError,'exact next'):
                    S.validate(plan)
                plan['prior_result_binding']=None
                config.write_text(json.dumps({'schema_version':'lab-actual-retained-workflow-run/v1',
                    'stages':[{'transition_ref':refs[9]}]}))
                plan['steps'][0]['config_binding']=binding(config)
                plan['steps'][0]['expected_transitions']=[refs[9]]
                with self.assertRaisesRegex(ValueError,'exact next'):
                    S.validate(plan)


if __name__=='__main__':unittest.main()
