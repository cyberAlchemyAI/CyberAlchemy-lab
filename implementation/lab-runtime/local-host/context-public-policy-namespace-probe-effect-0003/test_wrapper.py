"""Effect-denying causal checks of the review-gated outer one-shot wrapper."""
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock
import wrapper as W

class WrapperTests(unittest.TestCase):
    def test_exact_pins_selected_disabled_modules_and_freshness(self):
        selected,release,observer,source,freeze_sha=W.basis()
        self.assertEqual(W.sha(source),W.SOURCE_SHA)
        self.assertFalse(selected.EFFECT_ENABLED)
        self.assertFalse(release.EFFECT_ENABLED)
        self.assertFalse(observer.EFFECT_ENABLED)
        self.assertEqual(selected.NAME,W.NAME)
        self.assertEqual(selected.ATTEMPT,W.RELEASE_ATTEMPT)
        self.assertEqual(selected.OBSERVATION,W.INNER_OBSERVATION)
        self.assertEqual(freeze_sha,W.sha(W.SELF_FREEZE.read_bytes()))
        self.assertFalse(W.RELEASE_ATTEMPT.exists())
        self.assertFalse(W.INNER_OBSERVATION.exists())
        self.assertFalse(W.OUTER_OBSERVATION.exists())

    def test_own_review_missing_or_bad_cannot_enable(self):
        freeze_sha=W.sha(W.SELF_FREEZE.read_bytes())
        with self.assertRaises(W.Refused): W.own_static_review('bad',freeze_sha)
        with self.assertRaises((FileNotFoundError,W.Refused)):
            W.own_static_review('0'*64,freeze_sha)
        with tempfile.TemporaryDirectory(prefix='future-review-fixture-',dir=W.HERE) as root:
            path=Path(root)/'review.json'
            review={'schema':'context-public-policy-probe-effect-one-shot-independent-static-review/v1',
                'verdict':'PASS_BOUNDED_PUBLIC_ONLY_ONE_SHOT_STATIC',
                'candidate_freeze_sha256':freeze_sha,'findings':[],
                'docker_effect':'UNRUN',
                'same_uid_ceiling':'TRUSTED_SAME_UID_NOT_HOSTILE_SWAP_PROOF'}
            path.write_bytes(W.wire(review))
            with mock.patch.object(W,'FUTURE_REVIEW',path):
                self.assertEqual(W.own_static_review(W.sha(path.read_bytes()),freeze_sha),
                                 W.sha(path.read_bytes()))
                for change in ({'verdict':'HOLD'},
                               {'candidate_freeze_sha256':'0'*64},
                               {'findings':[{'id':'R01'}]}):
                    path.write_bytes(W.wire(dict(review,**change)))
                    with self.assertRaises(W.Refused):
                        W.own_static_review(W.sha(path.read_bytes()),freeze_sha)

    def test_self_or_review_pin_drift_refuses(self):
        with mock.patch.object(W,'RELEASE_REVIEW_SHA','0'*64):
            with self.assertRaises(W.Refused): W.basis()
        with mock.patch.object(W,'SOURCE_SHA','0'*64):
            with self.assertRaises(W.Refused): W.basis()
        own=json.loads(W.SELF_FREEZE.read_bytes())
        own['members']['wrapper.py']='0'*64
        with tempfile.TemporaryDirectory(prefix='self-freeze-fixture-',dir=W.HERE) as root:
            path=Path(root)/'freeze.json'
            path.write_bytes(W.wire(own))
            with mock.patch.object(W,'SELF_FREEZE',path):
                with self.assertRaises(W.Refused): W.basis()

    def test_read_only_same_state_preflight(self):
        old=os.umask(0o077)
        try: result=W.preflight()
        finally: os.umask(old)
        self.assertEqual(result['effect'],'NOT_RUN')
        self.assertEqual(result['status'],'AWAITING_OWN_INDEPENDENT_STATIC_REVIEW')
        self.assertEqual(result['name'],W.NAME)
        self.assertTrue(result['host']['name_absent'])
        self.assertTrue(result['host']['attempt_absent'])
        self.assertEqual(len(result['mounts']),6)
        self.assertTrue(all(row['read_only'] for row in result['mounts']))
        self.assertFalse(W.OUTER_OBSERVATION.exists())

    def test_checked_source_bootstrap_and_no_second_loader(self):
        source=W.checked_bytes(W.SOURCE/'wrapper.py',W.SOURCE_SHA)
        argv=W.child_argv(source,'a'*32)
        self.assertEqual(argv[:5],[W.PYTHON,'-I','-B','-S','-c'])
        self.assertIn(W.SOURCE_SHA,argv[-1])
        self.assertIn('OUTER_MARKER',argv[-1])
        self.assertIn('module.EFFECT_ENABLED=True',argv[-1])
        self.assertLess(len(argv[-1].encode()),65536)
        with self.assertRaisesRegex(W.Refused,'CHILD_SELECTION'):
            W.child_argv(source+b'x','a'*32)
        with mock.patch.object(Path,'read_bytes',side_effect=AssertionError('second path load')):
            self.assertEqual(W.sha(W.basis()[3]),W.SOURCE_SHA)

    def test_outer_join_strict_os_and_inner_record(self):
        summary={'overall':'PASS_BOUNDED_PUBLIC_NAMESPACE_PROBE_ONLY',
                 'container_name_absent':True,'container_cid_absent':True,
                 'retry_allowed':False}
        stdout=W.wire(summary)
        inner=W.wire({'schema':'context-public-only-probe-observer-record/v1',
                      'status':'PROVISIONAL_MATCH','candidate':summary,
                      'retry_allowed':False})
        self.assertEqual(W.outer_join(0,stdout,b'',inner)['status'],
                         'PROVISIONAL_EXTERNAL_EFFECT_REVIEW_REQUIRED')
        for args in ((1,stdout,b'',inner),(0,stdout,b'x',inner),
                     (0,b'non-json',b'',inner),
                     (0,stdout,b'',W.wire({'schema':'wrong','status':'PROVISIONAL_MATCH',
                                           'candidate':summary,'retry_allowed':False}))):
            with self.assertRaises((W.Refused,ValueError,KeyError)):
                W.outer_join(*args)

    def test_postclaim_spawn_failure_retains_unknown_no_retry(self):
        writes=[]
        class FakeAttempt:
            claimed=False
            def __init__(self,path): self.path=path
            def claim(self): self.claimed=True
            def write(self,name,raw): writes.append((name,raw))
            def close(self): pass
        source=W.checked_bytes(W.SOURCE/'wrapper.py',W.SOURCE_SHA)
        selected=types.SimpleNamespace(DOCKER_ENV={'PATH':'/usr/bin:/bin','HOME':'/home/vlad_'})
        release=types.SimpleNamespace(Attempt=FakeAttempt,wire=W.wire)
        observer=types.SimpleNamespace(CaptureUnknown=type('CaptureUnknown',(Exception,),{}))
        with mock.patch.object(W,'basis',return_value=(selected,release,observer,source,'0'*64)),\
             mock.patch.object(W,'own_static_review',return_value='0'*64),\
             mock.patch.object(W,'preflight',return_value={}),\
             mock.patch.object(W.os,'urandom',return_value=b'0'*16),\
             mock.patch.object(W.subprocess,'Popen',side_effect=OSError('synthetic spawn')):
            with self.assertRaisesRegex(W.Refused,'OUTER_UNKNOWN_PRESERVE_NO_RETRY'):
                W.observe_one_shot('0'*64)
        self.assertEqual([name for name,_ in writes],
                         ['intent.json','stdout','stderr','observation.json'])
        record=json.loads(writes[-1][1])
        self.assertEqual(record['status'],'UNKNOWN_PRESERVE_NO_RETRY')
        self.assertFalse(record['retry_allowed'])
        self.assertFalse(W.OUTER_OBSERVATION.exists())

if __name__=='__main__': unittest.main(verbosity=2)
