"""Focused, cheap checks of the T22 Work authoring boundary."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('t22_native_author', HERE / 'author.py')
AUTHOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUTHOR)
OLD_RECORDS = (AUTHOR.FIXTURE / 'instances/legacy-local-947e6c2a5b3d10f8/source/records.py')


class AuthorTests(unittest.TestCase):
    def test_exact_template_rewrite(self):
        raw = AUTHOR.rewrite_records(OLD_RECORDS.read_bytes())
        self.assertIn(b'R03 episode 0005', raw)
        self.assertIn(AUTHOR.INPUTS[next(iter(AUTHOR.INPUTS))].encode(), raw)
        self.assertIn(AUTHOR.INPUTS['authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/project-state.json'].encode(), raw)
        self.assertIn(AUTHOR.EVIDENCE.encode(), raw)
        self.assertIn(('sha256:' + AUTHOR.INPUTS[AUTHOR.API30_REF] + ':' + AUTHOR.API30_REF).encode(), raw)
        self.assertIn(('sha256:' + AUTHOR.INPUTS[AUTHOR.STATE_REF] + ':' + AUTHOR.STATE_REF).encode(), raw)
        self.assertIn(("work['evidence_refs'] = " + repr([AUTHOR.API30_REF, AUTHOR.STATE_REF, AUTHOR.EVIDENCE])).encode(), raw)
        self.assertNotIn(b"work['evidence_refs'] = [EVIDENCE", raw)
        self.assertIn(b"input_refs=[INTENT + '@' + VERSION]", raw)
        self.assertNotIn(b"input_refs=[INTENT + '@' + VERSION, 'sha256:", raw)
        self.assertNotIn(b'work_statement=\'Generate current bounded views', raw)

    def test_changed_template_refused(self):
        changed = OLD_RECORDS.read_bytes().replace(b'Read current scoped Project State', b'Different Work')
        with self.assertRaisesRegex(ValueError, 'anchor differs'):
            AUTHOR.rewrite_records(changed)

    def test_changed_pinned_input_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.json'
            path.write_bytes(b'original')
            with self.assertRaisesRegex(ValueError, 'selected input changed'):
                AUTHOR.safe_read(path, AUTHOR.sha(b'changed'))

    def test_staged_receipt_cold_verify(self):
        result = AUTHOR.verify()
        self.assertEqual(result['status'], 'STAGED')
        self.assertEqual(result['authority_effect'], 'none')
        self.assertFalse(result['source_built'])

    def test_native_intended_use_contract_remains_aligned(self):
        result = AUTHOR.verify()
        family = AUTHOR.ROOT / result['family']
        records = (family / 'source/records.py').read_text()
        mapping = json.loads((family / 'mapped/policy.json').read_bytes())
        query = (family / 'context/build.py').read_text()
        intended = mapping['intended_use_binding']['original_Coordination_Context_value']
        self.assertEqual(intended, 'Read current scoped Project State')
        self.assertIn('intended_uses=' + repr([intended]), records)
        self.assertIn("'intended_use':" + repr(intended), query)


if __name__ == '__main__':
    unittest.main()
