"""Exact current Source Work/private resolution and cold original closure."""
import copy
from contextlib import nullcontext
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT/'implementation/lab-runtime/local-host/t31-retained-api-0001'))
from test_frame import Frame

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE/filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

B = load('t31_native_intent_bundle_test', 'intent_bundle.py')
C = load('t31_native_intent_config_test', 'prepare_intent_config.py')
CUT = {'store_ref':'retained-fixture-component-only'}
PRINCIPAL = 'principal:synthetic-private-coordinator'
RUN = 'workflow-run:current-intent-framing-test'
SOURCE = {'path':'product/lab/release-candidates/v1/interface/api-test/source-manifest.json','sha256':'a'*64}
PROFILE = {'path':'product/lab/release-candidates/v1/interface/api-test/contract-profile.json','sha256':'b'*64}


class NativeIntentFraming(unittest.TestCase):
    def inputs(self):
        frame = Frame(); frame.setUp()
        return frame.inputs

    def test_private_resolution_selects_unchanged_source_work(self):
        inputs = self.inputs(); before = copy.deepcopy(inputs)
        result = B.derive(inputs, CUT, PRINCIPAL, RUN)
        self.assertEqual(inputs, before)
        ir = result['intent_resolution']; work = result['current_source_work']
        body = json.loads(result['records'][ir['version_ref']][1])
        self.assertIn(work['version_ref'], body['payload']['selected_subject_refs'])
        self.assertEqual(result['transitions'][B.ROUTES[1]], [work])
        self.assertEqual(result['records'][work['version_ref']][1], inputs['work'][1])

    def test_changed_work_and_foreign_goal_edge_refused(self):
        inputs = self.inputs(); h, raw = inputs['work']; inputs['work'] = (h, raw+b' ')
        with self.assertRaisesRegex(ValueError, 'original/header'):
            B.derive(inputs, CUT, PRINCIPAL, RUN)
        inputs = self.inputs(); h, raw = inputs['goal_project']; body = json.loads(raw)
        body['payload']['target']['version_ref'] = 'project:foreign@1'
        raw = B.encoded(body); h = copy.deepcopy(h); h['byte_sha256'] = B.sha(raw)
        inputs['goal_project'] = (h, raw)
        with self.assertRaisesRegex(ValueError, 'Goal/Project'):
            B.derive(inputs, CUT, PRINCIPAL, RUN)
        inputs = self.inputs(); h, raw = inputs['work']; h = copy.deepcopy(h)
        h['carrier_ref'] = 'cal.artifact-type.goal/v1'; inputs['work'] = (h, raw)
        with self.assertRaisesRegex(ValueError, 'work original/header'):
            B.derive(inputs, CUT, PRINCIPAL, RUN)

    def test_current_source_inputs_read_edge_original_without_projection_record(self):
        inputs = self.inputs()
        subjects = {}
        for kind, (header, raw) in inputs.items():
            subjects[kind] = {'identity': header['identity_ref'],
                              'carrier_ref': header['carrier_ref'],
                              'effective_state': 'admitted-current',
                              'header': header, 'raw': raw}
        view = SimpleNamespace(subjects=subjects,
            custody_signed_sources=SimpleNamespace(
                sources=SimpleNamespace(scope_ref=inputs['project'][0]['identity_ref'])))
        model = SimpleNamespace(model_read_batch=lambda _: nullcontext(),
                                artifact_ref=lambda _, subject: subject['header'],
                                record_bytes=lambda _, subject: (subject['raw'],))
        delivery = SimpleNamespace(records=SimpleNamespace(
            INTENT=inputs['intent'][0]['identity_ref'],
            WORK=inputs['work'][0]['identity_ref'],
            GOAL=inputs['goal'][0]['identity_ref'],
            COORDINATION=inputs['coordination'][0]['identity_ref']))
        self.assertEqual(B.current_inputs(view, model, delivery), inputs)

    def test_private_bundle_cold_readback_and_mutation_refusal(self):
        inputs = self.inputs(); derived = B.derive(inputs, CUT, PRINCIPAL, RUN)
        with tempfile.TemporaryDirectory() as dirname:
            output = Path(dirname)/'bundle'
            selection = B.persist(output, inputs, derived, SOURCE, PROFILE, CUT, PRINCIPAL, RUN)
            cold = SimpleNamespace(guard=lambda: True)
            with patch.object(B, 'selected_runtime', return_value=(cold, None, SOURCE, PROFILE)):
                read = B.consume({key: selection[key] for key in ('kind','manifest_path','manifest_sha256')})
                self.assertEqual(read['records'][derived['current_source_work']['version_ref']][1], inputs['work'][1])
                self.assertEqual(read['transitions'], derived['transitions'])
                work_path = output/'input-work.json'; work_path.write_bytes(work_path.read_bytes()+b' ')
                with self.assertRaisesRegex(ValueError, 'retained signed Source original'):
                    B.consume({key: selection[key] for key in ('kind','manifest_path','manifest_sha256')})

    def test_two_stage_config_uses_same_native_identity_and_source(self):
        inputs = self.inputs(); derived = B.derive(inputs, CUT, PRINCIPAL, RUN)
        bundle = {'run_ref':RUN,'principal_ref':PRINCIPAL,'source_cut':CUT,
                  'source_binding':SOURCE,'profile_binding':PROFILE,
                  'source_inputs':inputs,
                  'input_refs':{inputs[k][0]['carrier_ref']:inputs[k][0]['version_ref']
                                for k in ('intent','goal','coordination')},
                  'transitions':derived['transitions'],
                  'intent_resolution':derived['intent_resolution'],
                  'current_source_work':derived['current_source_work']}
        native = {'identity':{'principal_ref':PRINCIPAL,'run_ref':RUN},
                  'source_cut':CUT,'source_binding':SOURCE,'profile_binding':PROFILE,
                  'coordination_inputs':{('coordination-context' if k == 'coordination' else k):v
                                         for k,v in inputs.items() if k in ('intent','work','goal','coordination')}}
        fake_bundle = SimpleNamespace(consume=lambda selected: bundle, ROUTES=B.ROUTES)
        fake_native = SimpleNamespace(consume=lambda selected: native)
        def choose(name, path):
            return fake_bundle if 'intent_bundle' in str(path) else fake_native
        with tempfile.TemporaryDirectory() as dirname, patch.object(C, 'module', side_effect=choose):
            target = Path(dirname)/'intent-config.json'
            C.prepare({'kind':'intent-framing'}, {'terminal_result':'first'}, target)
            config = json.loads(target.read_bytes())
            self.assertEqual([row['transition_ref'] for row in config['stages']], list(B.ROUTES))
            self.assertEqual(config['stages'][1]['input_refs']['cal.artifact-type.intent-resolution/v1'],
                             derived['intent_resolution']['version_ref'])
            self.assertEqual(config['stages'][1]['output_refs'], [derived['current_source_work']['version_ref']])
            native['coordination_inputs']['work'] = (inputs['work'][0], inputs['work'][1] + b' ')
            with self.assertRaisesRegex(ValueError, 'Source original differs'):
                C.prepare({'kind':'intent-framing'}, {'terminal_result':'first'}, Path(dirname)/'foreign-work.json')
            native['coordination_inputs']['work'] = inputs['work']
            native['source_cut'] = {'store_ref':'foreign'}
            with self.assertRaisesRegex(ValueError, 'lineage differ'):
                C.prepare({'kind':'intent-framing'}, {'terminal_result':'first'}, Path(dirname)/'foreign.json')


if __name__ == '__main__':
    unittest.main()
