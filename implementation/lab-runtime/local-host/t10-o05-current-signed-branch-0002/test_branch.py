import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import branch


class SignedCurrentBranch(unittest.TestCase):
    def setUp(self):
        self.output = branch.HERE / 'run-0001'

    def clone(self):
        temp = tempfile.TemporaryDirectory(prefix='negative-', dir=branch.HERE)
        target = Path(temp.name) / 'run'
        shutil.copytree(self.output, target)
        self.addCleanup(temp.cleanup)
        return target

    def test_public_signed_branch_cold_replays_current(self):
        result = branch.replay(self.output)
        self.assertEqual(result['status'], 'PASS-LOCAL-SIGNED-BRANCH')
        self.assertEqual(result['head_sequence'], 1)

    def test_changed_signed_byte_refuses(self):
        target = self.clone()
        file = target / 'branch/transactions/0000000001.json'
        file.write_bytes(file.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'retained branch bytes changed'):
            branch.replay(target)

    def test_false_authority_claim_refuses(self):
        target = self.clone()
        receipt = target / 'RESULT.json'
        data = json.loads(receipt.read_bytes())
        data['authority_effect'] = 'repository-admission'
        receipt.write_bytes(branch.encoded(data))
        with self.assertRaisesRegex(ValueError, 'retained branch receipt differs'):
            branch.replay(target)

    def test_private_key_residue_refuses(self):
        target = self.clone()
        (target / 'owner.pem').write_text('not a real key')
        with self.assertRaisesRegex(ValueError, 'retained branch output closure differs'):
            branch.replay(target)

    def test_changed_public_branch_claim_refuses_even_with_rehashed_receipt(self):
        target = self.clone()
        file = target / 'branch/transactions/0000000001.json'
        transaction = json.loads(file.read_bytes())
        transaction['approval']['signature'] = '00' * 64
        transaction['digest'] = hashlib.sha256(json.dumps(
            {k: v for k, v in transaction.items() if k != 'digest'},
            sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
        file.write_bytes(branch.encoded(transaction))
        head_file = target / 'branch/HEAD.json'
        head = json.loads(head_file.read_bytes())
        head['transaction_digest'] = transaction['digest']
        head['digest'] = hashlib.sha256(json.dumps(
            {k: v for k, v in head.items() if k != 'digest'},
            sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
        head_file.write_bytes(branch.encoded(head))
        receipt = target / 'RESULT.json'
        data = json.loads(receipt.read_bytes())
        next(row for row in data['public_files'] if row['path'] == 'transactions/0000000001.json')['sha256'] = branch.sha(file.read_bytes())
        next(row for row in data['public_files'] if row['path'] == 'HEAD.json')['sha256'] = branch.sha(head_file.read_bytes())
        data['head_transaction_digest'] = transaction['digest']
        receipt.write_bytes(branch.encoded(data))
        with self.assertRaisesRegex(Exception, 'invalid owner approval signature'):
            branch.replay(target)

    def test_old_signed_o05_archive_is_historical_not_current(self):
        import importlib.util
        file = branch.ROOT / 'implementation/lab-runtime/local-host/t10-o03-o05-current-source-attempt-0001/compatibility.py'
        spec = importlib.util.spec_from_file_location('o05_original_compatibility', file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.attempt()
        self.assertEqual(result['historical_replay'], 'PASS')
        self.assertEqual(result['result'], 'REFUSED-ORIGINAL-ARCHIVE-AS-CURRENT')
        self.assertFalse(result['query_executed'])


if __name__ == '__main__':
    unittest.main()
