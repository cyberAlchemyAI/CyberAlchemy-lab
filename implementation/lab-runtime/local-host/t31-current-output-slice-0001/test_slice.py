"""Focused producer/consumer and retained-claim causal negatives."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')


def load(name):
    spec = importlib.util.spec_from_file_location('t31_test_' + name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


producer = load('producer')
consumer = load('consumer')
verifier = load('verify')


class View:
    subjects = {'one': {'effective_state': 'admitted-current', 'version_ref': 'one@1'},
                'old': {'effective_state': 'historical', 'version_ref': 'old@1'}}


class SliceTests(unittest.TestCase):
    def setUp(self):
        self.view = View()
        self.cut = {'store_ref': 'signed-fixture', 'commit_sequence': 1}
        self.binding = {'ref': 'source:fixture', 'sha256': 'a' * 64}
        self.work = {'version_ref': 'work:fixture@1'}
        self.scope = 'project:cyberalchemy-v2-to-lab-migration'
        self.report, self.body, self.header = producer.produce(self.view, self.cut,
            self.work, self.binding, self.scope)

    def test_output_schema_and_later_consumer(self):
        schema = json.loads((ROOT / 'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/generated-output/v2/schema.json').read_bytes())
        Draft202012Validator(schema).validate(json.loads(self.body))
        result = consumer.consume(self.view, self.cut, self.binding, self.work,
                                  self.report, self.body, self.header)
        self.assertEqual(result['current_subject_count'], 1)
        self.assertEqual(result['output_body_sha256'], self.header['byte_sha256'])

    def test_later_consumer_refuses_report_body_and_source_changes(self):
        for kwargs in ({'report_raw': self.report + b' '},
                       {'body_raw': self.body + b' '},
                       {'source_binding': {'ref': 'source:other', 'sha256': 'b' * 64}}):
            args = {'view': self.view, 'cut': self.cut, 'source_binding': self.binding,
                    'work': self.work, 'report_raw': self.report,
                    'body_raw': self.body, 'header': self.header}
            args.update(kwargs)
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                consumer.consume(**args)

    def test_retained_receipt_and_false_original_credit(self):
        self.assertEqual(verifier.verify()['result'], 'PASS')
        receipt = json.loads((HERE / 'RUN-0001.json').read_bytes())
        receipt['observed']['original_w08_transitions_observed'] = 1
        with tempfile.TemporaryDirectory(prefix='t31-slice-check-') as tmp:
            path = Path(tmp) / 'changed.json'
            path.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, 'claim differs'):
                verifier.verify(path)


if __name__ == '__main__':
    unittest.main()
