"""The installed consumer retains the exact original observation checks."""
import ast
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ORIGINAL = ROOT / 'implementation/lab-runtime/local-host/t31-durable-output-0001/observed_replay.py'
RETAINED = ROOT / 'implementation/lab-runtime/local-host/t31-workflow-stream-0002/run-0001'


def selected(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ObservedConsumer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path[:0] = [str(HERE), str(ORIGINAL.parent)]
        cls.old = selected(ORIGINAL, '_t21_original_observed_replay')
        cls.new = selected(HERE / 'observed_consumer.py', '_t21_selected_observed_consumer')

    def test_exact_selected_consumer_function_and_input_pins(self):
        def function(path):
            return next(node for node in ast.parse(path.read_text()).body
                        if isinstance(node, ast.FunctionDef) and node.name == 'consume_observed')
        self.assertEqual(ast.dump(function(ORIGINAL)), ast.dump(function(HERE / 'observed_consumer.py')))
        self.assertEqual(self.old.EXTRA_INPUTS, self.new.EXTRA_INPUTS)

    def test_both_actual_retained_kinds_have_the_same_bounded_observation(self):
        result = json.loads((RETAINED / 'RESULT.json').read_bytes())
        for kind in ('engineering', 'research'):
            row = next(row for row in result['new_output_transitions']
                       if row['transition_ref'].split(':')[1] == kind)
            originals = [(header, (RETAINED / path).read_bytes())
                         for header, path in zip(row['output_artifact_refs'], row['output_original_paths'], strict=True)]
            with self.subTest(kind=kind):
                self.assertEqual(self.old.consume_observed(kind, originals, RETAINED),
                                 self.new.consume_observed(kind, originals, RETAINED))

    def test_one_changed_original_refuses(self):
        result = json.loads((RETAINED / 'RESULT.json').read_bytes())
        row = next(row for row in result['new_output_transitions']
                   if row['transition_ref'].split(':')[1] == 'engineering')
        originals = [(header, (RETAINED / path).read_bytes())
                     for header, path in zip(row['output_artifact_refs'], row['output_original_paths'], strict=True)]
        index = next(i for i, (header, _) in enumerate(originals)
                     if header['carrier_ref'] == 'cal.artifact-type.generated-output/v2')
        body = json.loads(originals[index][1])
        body['payload']['output_digest'] = 'sha256:' + '0' * 64
        originals[index] = (originals[index][0], json.dumps(body).encode())
        with self.assertRaisesRegex(ValueError, 'consumed source body differs'):
            self.new.consume_observed('engineering', originals, RETAINED)


if __name__ == '__main__':
    unittest.main()
