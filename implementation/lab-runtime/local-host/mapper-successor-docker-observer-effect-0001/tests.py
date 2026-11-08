"""Inert one-shot wrapper tests; never dispatch the Mapper release."""
import os
from pathlib import Path
import tempfile
import unittest

import wrapper as w


class FakeObserver:
    RELEASE_SHA = 'cf85a26da6166e96855050ae0f511d22ff260ce4f807b9c67a077391b01bf927'
    def __init__(self):
        self.preflight_calls = 0
        self.dispatch_calls = 0
    def preflight(self):
        self.preflight_calls += 1
        return {'effect':'NOT_RUN','observation':str(w.OBSERVATION),
                'release':{'freeze_sha256':w.RELEASE_FREEZE_SHA,
                           'review_sha256':w.RELEASE_REVIEW_SHA,
                           'release_sha256':self.RELEASE_SHA},
                'preflight_stdout':b'public metadata only'}
    def _run_once(self,*,preflight_fn):
        self.dispatch_calls += 1
        if preflight_fn != self.preflight: raise AssertionError('wrong source binding')
        preflight_fn()
        return {'status':'PROVISIONAL_OS_ZERO_FINAL_JOIN','no_retry':True,
                'independent_effect_review':'PENDING'}


class WrapperTests(unittest.TestCase):
    def test_pinned_source_loads_once_in_memory_with_disabled_predecessor(self):
        selected = w.load_reviewed_observer()
        self.assertFalse(selected.EFFECT_ENABLED)
        self.assertEqual(selected.OBSERVATION,w.OBSERVATION)
        self.assertEqual(selected.ATTEMPT,w.ATTEMPT)
        self.assertEqual(selected.NAME,w.NAME)
        self.assertEqual(selected.COMMAND,
            ['/usr/bin/python3','-B',str(selected.RELEASE),'--execute-reviewed-one-shot'])

    def test_preflight_strips_raw_child_metadata(self):
        fake = FakeObserver()
        result = w.preflight(loader=lambda:fake)
        self.assertEqual(fake.preflight_calls,1)
        self.assertNotIn('preflight_stdout',result)

    def test_dispatch_one_loader_one_selected_preflight_one_effect_call(self):
        fake = FakeObserver()
        loads = []
        def loader(): loads.append(1); return fake
        result = w.dispatch(loader=loader)
        self.assertEqual(result['status'],'PROVISIONAL_OS_ZERO_FINAL_JOIN')
        self.assertEqual((len(loads),fake.preflight_calls,fake.dispatch_calls),(1,1,1))

    def test_dispatch_disabled_gate_blocks_loader(self):
        before = w.EFFECT_ENABLED
        w.EFFECT_ENABLED = False
        self.addCleanup(setattr,w,'EFFECT_ENABLED',before)
        with self.assertRaises(w.Refused):
            w.dispatch(loader=lambda: (_ for _ in ()).throw(AssertionError('loaded')))

    def test_nonprovisional_child_result_is_refused(self):
        fake = FakeObserver()
        def not_ready(*,preflight_fn):
            preflight_fn()
            return {'status':'UNKNOWN_PRESERVE_NO_RETRY','no_retry':True,
                    'independent_effect_review':'PENDING'}
        fake._run_once = not_ready
        with self.assertRaises(w.Refused): w.dispatch(loader=lambda:fake)

    def test_wrong_digest_refuses_nofollow_file(self):
        with tempfile.TemporaryDirectory(dir=w.HERE) as directory:
            path = Path(directory)/'public'
            path.write_bytes(b'public fixture')
            with self.assertRaises(w.Refused):
                w.checked_bytes(path,'0'*64)


if __name__ == '__main__': unittest.main(verbosity=2)
