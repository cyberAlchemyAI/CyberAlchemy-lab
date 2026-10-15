import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('integrity', Path(__file__).with_name('integrity.py'))
integrity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integrity)


class IntegrityTests(unittest.TestCase):
    def test_changed_or_missing_criteria_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'schedule.json').write_text('{}')
            (root / 'criteria.json').write_text('{"version":1}')
            manifest = {'hashes': {'criteria.json': integrity.digest(root / 'criteria.json')},
                        'schedule_sha256': integrity.digest(root / 'schedule.json'), 'frozen_at_utc': 'test'}
            (root / 'freeze-manifest.json').write_text(json.dumps(manifest))
            self.assertTrue(integrity.verify(root)['valid'])
            (root / 'criteria.json').write_text('{"version":2}')
            self.assertFalse(integrity.verify(root)['valid'])
            (root / 'criteria.json').unlink()
            self.assertFalse(integrity.verify(root)['valid'])

    def test_scored_spawn_prohibits_prospective_freeze(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'receipts').mkdir()
            (root / 'receipts/events.jsonl').write_text(json.dumps({'event': 'spawn', 'stage': 'main'}) + '\n')
            with self.assertRaisesRegex(ValueError, 'already spawned'):
                integrity.freeze(root)


if __name__ == '__main__':
    unittest.main()
