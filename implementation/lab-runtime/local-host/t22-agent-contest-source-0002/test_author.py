"""Fast causal checks before consuming a fresh native instance name."""
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('t22_contest_author', HERE / 'author.py')
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)

class ContestAuthorTests(unittest.TestCase):
    def test_distinct_contract_and_source_count(self):
        predecessor = A.selected_predecessor()
        template = A.FIXTURE / 'instances/legacy-local-947e6c2a5b3d10f8/source'
        records = A.rewrite_records((template / 'records.py').read_bytes(), predecessor)
        build = A.rewrite_build((template / 'build.py').read_bytes())
        self.assertIn(b"'challenge-contract': contract", records)
        self.assertIn(b"eligible_challenger_kinds=['agent-instance']", records)
        self.assertIn(b"challengeable_subject_kinds=['work']", records)
        self.assertIn(b"required_evidence_kinds=['source', 'validation-receipt']", records)
        self.assertNotIn(b"required_evidence_kinds=['source', 'validation-receipt', 'decision']", records)
        self.assertIn(b"len(items)==22", build)
        self.assertIn(b"'authored_current_artifacts':12", build)

    def test_changed_template_refused(self):
        predecessor = A.selected_predecessor()
        template = A.FIXTURE / 'instances/legacy-local-947e6c2a5b3d10f8/source/records.py'
        changed = template.read_bytes().replace(b'Read current scoped Project State', b'Different Work')
        with self.assertRaisesRegex(ValueError, 'anchor differs'):
            A.rewrite_records(changed, predecessor)

    def test_changed_source_count_refused(self):
        template = A.FIXTURE / 'instances/legacy-local-947e6c2a5b3d10f8/source/build.py'
        changed = template.read_bytes().replace(b'len(items)==21', b'len(items)==20')
        with self.assertRaisesRegex(ValueError, 'count anchor differs'):
            A.rewrite_build(changed)

    def test_contract_eligibility_negative(self):
        sample = json.loads(A.safe_read(A.ROOT / A.FOUNDATION, A.INPUTS[A.FOUNDATION]))
        sample.update(node_id='challenge-contract:completion-legacy-local-abc-agent-contest', scope_ref='project:one')
        sample['payload'].update(challengeable_subject_kinds=['work'], eligible_challenger_kinds=['agent-instance'],
                                 required_evidence_kinds=['source', 'validation-receipt'])
        sample['lifecycle_state'] = 'candidate'
        self.assertEqual(A.check_contract(sample, 'project:one', 'completion-legacy-local-abc')['kind'], 'challenge-contract')
        sample['payload']['eligible_challenger_kinds'] = ['principal']
        with self.assertRaisesRegex(ValueError, 'eligibility differs'):
            A.check_contract(sample, 'project:one', 'completion-legacy-local-abc')
        sample['payload'].update(eligible_challenger_kinds=['agent-instance'],
                                 required_evidence_kinds=['source', 'validation-receipt', 'decision'])
        with self.assertRaisesRegex(ValueError, 'pre-decision evidence boundary differs'):
            A.check_contract(sample, 'project:one', 'completion-legacy-local-abc')

    def test_changed_pinned_source_refused(self):
        with self.assertRaisesRegex(ValueError, 'selected input changed'):
            A.safe_read(A.ROOT / A.FOUNDATION, '0' * 64)

    def test_stage_cold_verify_when_present(self):
        if not (HERE / 'STAGE-0001.json').exists():
            self.skipTest('native family not staged yet')
        result = A.verify()
        self.assertFalse(result['source_built'])
        self.assertIsNone(result['contest_outcome'])

    def test_signed_source_contract_and_work_join(self):
        if not (HERE / 'STAGE-0001.json').exists():
            self.skipTest('native family not staged yet')
        receipt = A.verify()
        family = A.ROOT / receipt['family']
        if not (family / 'source-result.json').exists():
            self.skipTest('signed source not built yet')
        result = json.loads((family / 'source-result.json').read_bytes())
        cold = json.loads((family / 'cold-result.json').read_bytes())
        self.assertEqual(cold['result'], 'PASS-native-cold')
        self.assertEqual(cold['independent_cold_replays'], 2)
        self.assertEqual(result['source_binding'], cold['source_binding'])
        rows = json.loads((family / 'source/packages/0001/record-index.json').read_bytes())
        self.assertEqual(len(rows), 22)
        by_kind = {kind: [row for row in rows if row['kind'] == kind]
                   for kind in ('work', 'challenge-contract')}
        self.assertEqual(len(by_kind['work']), len(by_kind['challenge-contract']))
        self.assertEqual(len(by_kind['work']), 1)
        def body(row):
            pin = row['original_binding']
            return json.loads(A.safe_read(A.ROOT / pin['path'], pin['sha256']))
        work = body(by_kind['work'][0])
        contract = body(by_kind['challenge-contract'][0])
        prefix = 'completion-' + receipt['instance']
        A.check_contract(contract, work['scope_ref'], prefix)
        self.assertEqual(work['node_id'], 'work:' + prefix)
        self.assertIn(A.selected_predecessor().API30_REF, work['evidence_refs'])
        self.assertIn(A.SESSION, contract['evidence_refs'])
        self.assertEqual(contract['payload']['policy_ref'], 'protocol:' + prefix + '-policy/v1')

if __name__ == '__main__': unittest.main()
