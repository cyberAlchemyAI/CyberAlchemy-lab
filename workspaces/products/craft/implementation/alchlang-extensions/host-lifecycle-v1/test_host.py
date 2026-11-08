"""Bounded private-host storage observation contract; real host controls are integration tested."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from lifecycle import delivery_snapshot
import test_lifecycle

class Observation(test_lifecycle.Summary):
    def test_locked_storage_is_unavailable(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'db'
            with sqlite3.connect(path) as db:
                db.executescript('CREATE TABLE outbox(status);CREATE TABLE dead_letters(id);')
                db.execute('BEGIN EXCLUSIVE')
                self.assertFalse(delivery_snapshot(path)['available'])
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'db';target.write_text('fixture');link=Path(d)/'link';link.symlink_to(target)
            self.assertEqual(delivery_snapshot(link)['reason'],'UNSAFE_STORAGE')

if __name__=='__main__':unittest.main(verbosity=2)
