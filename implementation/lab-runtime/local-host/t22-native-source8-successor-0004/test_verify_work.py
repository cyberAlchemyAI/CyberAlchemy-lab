"""Causal counterexamples to the signed T22 Work selection."""
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('t22_built_work_verify', HERE / 'verify_work.py')
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def inputs():
    return [json.loads(V.read(path, pin)) for path, pin in
            ((V.WORK, V.WORK_SHA), (V.SOURCE, V.SOURCE_SHA), (V.PACKAGE, V.PACKAGE_SHA),
             (V.INDEX, V.INDEX_SHA), (V.STAGE, V.STAGE_SHA))]


class BuiltWorkTests(unittest.TestCase):
    def test_exact_selected_work(self):
        self.assertEqual(V.verify()['status'], 'PASS-exact-built-Work')

    def test_changed_work_input_ref_refused(self):
        values = inputs()
        values[0]['payload']['input_refs'].append('sha256:' + '0' * 64 + ':' + V.STATE)
        with self.assertRaisesRegex(ValueError, 'exact input refs differ'):
            V.validate(*values)

    def test_changed_work_statement_digest_refused(self):
        values = inputs()
        values[0]['payload']['work_statement'] = values[0]['payload']['work_statement'].replace(V.INPUTS[V.STATE], '0' * 64)
        with self.assertRaisesRegex(ValueError, 'selected byte tokens differ'):
            V.validate(*values)

    def test_historical_evidence_substitution_refused(self):
        values = inputs()
        values[0]['evidence_refs'][1] = 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        with self.assertRaisesRegex(ValueError, 'Work evidence differs'):
            V.validate(*values)

    def test_manifest_lineage_substitution_refused(self):
        values = inputs()
        for row in values[1]['files']:
            if row['path'] == V.STATE:
                row['sha256'] = '0' * 64
                break
        with self.assertRaisesRegex(ValueError, 'episode input missing'):
            V.validate(*values)

    def test_changed_selected_bytes_refused(self):
        with self.assertRaisesRegex(ValueError, 'selected bytes changed'):
            V.read(V.WORK, '0' * 64)

    def test_changed_signed_context_use_refused(self):
        package = json.loads(V.read(V.PACKAGE, V.PACKAGE_SHA))
        coordination = json.loads(V.read(V.COORDINATION, V.COORDINATION_SHA))
        context = json.loads(V.read(V.CONTEXT, V.CONTEXT_SHA))
        policy = json.loads(V.read(V.POLICY, V.POLICY_SHA))
        context['intended_uses'] = ['Read a different project']
        with self.assertRaisesRegex(ValueError, 'intended use differs'):
            V.validate_context_alignment(coordination, context, policy, package)

    def test_changed_signed_context_purpose_refused(self):
        package = json.loads(V.read(V.PACKAGE, V.PACKAGE_SHA))
        coordination = json.loads(V.read(V.COORDINATION, V.COORDINATION_SHA))
        context = json.loads(V.read(V.CONTEXT, V.CONTEXT_SHA))
        policy = json.loads(V.read(V.POLICY, V.POLICY_SHA))
        context['purpose'] = 'Generic context only'
        with self.assertRaisesRegex(ValueError, 'purpose differs'):
            V.validate_context_alignment(coordination, context, policy, package)


if __name__ == '__main__': unittest.main()
