"""No-Docker causal tests for the one-shot public probe effect wrapper."""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import tempfile
import types
import unittest
from unittest import mock

import wrapper as W


class EffectWrapperTests(unittest.TestCase):
    def test_second_path_loader_never_executes_sentinel(self):
        import importlib.util
        sentinel = []
        class HostileLoader:
            def create_module(self, spec): return None
            def exec_module(self, module):
                sentinel.append('UNVERIFIED_TOP_LEVEL')
                raise AssertionError('unchecked pathname executed')
        def replacement(name, path, **kwargs):
            return importlib.util.spec_from_loader(name, HostileLoader())
        with mock.patch.object(importlib.util, 'spec_from_file_location',
                               side_effect=replacement) as loader:
            release, observer = W.basis()
        self.assertEqual(sentinel, [])
        loader.assert_not_called()
        self.assertIs(observer.R, release)
        defaults = observer.run_observer.__kwdefaults__
        self.assertIs(defaults['preflight'], release.preflight)
        self.assertIs(defaults['read_file'], release.check_file)

    def test_observer_projection_exact_inverse_and_drift(self):
        raw = W.read_file(W.PREVIOUS/'observer.py', W.PREVIOUS_MEMBERS['observer.py'])
        projected = W.observer_projection(raw)
        self.assertEqual(projected.replace(W.OBSERVER_IMPORT_POSTIMAGE,
                         W.OBSERVER_IMPORT_PREIMAGE, 1), raw)
        for altered in (raw+b'\n', raw.replace(b'SPEC.loader.exec_module(R)', b'pass')):
            with self.assertRaisesRegex(W.Refused, 'OBSERVER_PREIMAGE_PIN'):
                W.observer_projection(altered)

    def test_exact_reviewed_selection_and_self_freeze(self):
        release,observer = W.basis()
        self.assertFalse(release.EFFECT_ENABLED)
        self.assertFalse(observer.EFFECT_ENABLED)
        self.assertIs(observer.R,release)
        self.assertEqual(release.NAME,'cal-context-public-only-probe-20261020-0003')
        self.assertEqual(release.PINS[release.CHILD],W.PREVIOUS_MEMBERS['probe_child.py'])
        self.assertEqual(W.sha(W.read_file(W.PREVIOUS_FREEZE)),W.PREVIOUS_FREEZE_SHA)
        self.assertEqual(W.sha(W.read_file(W.PREVIOUS_REVIEW)),W.PREVIOUS_REVIEW_SHA)
        self.assertEqual(W.sha(W.read_file(W.BOOTSTRAP_WRAPPER_REVIEW)),
                         W.BOOTSTRAP_WRAPPER_REVIEW_SHA)

    def test_restrictive_umask_live_readonly_preflight_fresh_identity(self):
        previous = os.umask(0o077)
        try:
            selected = W.preflight()
        finally:
            os.umask(previous)
        self.assertEqual(selected['effect'],'NOT_RUN')
        self.assertEqual(selected['docker_name'],
                         'cal-context-public-only-probe-20261020-0003')
        self.assertTrue(selected['host']['name_absent'])
        self.assertTrue(selected['host']['attempt_absent'])
        self.assertTrue(selected['observer_attempt'].endswith('-0003'))

    def test_pin_and_self_binding_drift_refuse(self):
        with mock.patch.object(W,'PREVIOUS_REVIEW_SHA','0'*64):
            with self.assertRaises(W.Refused): W.basis()
        frozen = json.loads(W.FREEZE.read_bytes())
        frozen['bindings']['wrapper.py'] = '0'*64
        with tempfile.TemporaryDirectory(prefix='effect-freeze-fixture-',dir=W.HERE) as base:
            path = Path(base)/'freeze.json'
            path.write_text(json.dumps(frozen))
            with mock.patch.object(W,'FREEZE',path):
                with self.assertRaises(W.Refused): W.basis()

    def test_preflight_observer_claim_and_host_fail_closed(self):
        r = types.SimpleNamespace(NAME='probe-name',ATTEMPT=Path('/fixture/attempt'),
            preflight=lambda **_: {'effect_enabled':False,'host':{
                'name_absent':True,'attempt_absent':True},'name':'probe-name'},
            open_chain=lambda _p:[os.open(W.HERE,os.O_RDONLY|os.O_DIRECTORY)],
            close_all=lambda fds:[os.close(fd) for fd in fds])
        with tempfile.TemporaryDirectory(prefix='effect-preflight-fixture-',dir=W.HERE) as base:
            # The selected parent itself must be owner-0700.
            observation = Path(base)/'observation'
            o = types.SimpleNamespace(OBSERVATION=observation)
            with mock.patch.object(W,'basis',return_value=(r,o)),\
                 mock.patch.object(W,'PYTHON','/usr/bin/python3.14'):
                # Held ancestry from the fake release reports HERE (0755), so refuse.
                with self.assertRaisesRegex(W.Refused,'OBSERVER_PARENT_CUSTODY'):
                    W.preflight()
            def held(_path):
                return [os.open(base,os.O_RDONLY|os.O_DIRECTORY)]
            r.open_chain = held
            with mock.patch.object(W,'basis',return_value=(r,o)):
                self.assertEqual(W.preflight()['status'],
                                 'READY_FOR_INDEPENDENT_EFFECT_REVIEW')
                observation.mkdir()
                with self.assertRaisesRegex(W.Refused,'PRE_DISPATCH_SCOPE_OCCUPIED'):
                    W.preflight()
            self.assertEqual(stat.S_IMODE(Path(base).stat().st_mode),0o700)

    def test_spawn_exact_parent_handoff_and_sanitized_env(self):
        captured = []
        def fake_spawn(argv,**kwargs):
            captured.append((argv,kwargs))
            return 'fake-process'
        argv = [W.PYTHON,'-I','-B','-S',str(W.SELF),'--execute-reviewed-one-shot']
        self.assertEqual(W.observer_spawn(argv,token='a'*32,parent_pid=os.getpid(),
            spawn=fake_spawn,start_new_session=True,close_fds=True),'fake-process')
        env = captured[0][1]['env']
        self.assertEqual(env['PATH'],'/usr/bin:/bin')
        self.assertEqual(env['HOME'],'/home/vlad_')
        self.assertEqual(env['CAL_PUBLIC_PROBE_PARENT_PID'],str(os.getpid()))
        self.assertEqual(env['CAL_PUBLIC_PROBE_PARENT_TOKEN'],'a'*32)
        self.assertNotIn('DOCKER_HOST',env)
        for altered in (argv[:-1]+['--preflight'],argv[:-1]+['--observe-reviewed-one-shot']):
            with self.assertRaises(W.Refused):
                W.observer_spawn(altered,token='a'*32,parent_pid=os.getpid(),
                                 spawn=fake_spawn,start_new_session=True,close_fds=True)
        with self.assertRaises(W.Refused):
            W.observer_spawn(argv,token='short',parent_pid=os.getpid(),
                             spawn=fake_spawn,start_new_session=True,close_fds=True)
        with self.assertRaises(W.Refused):
            W.observer_spawn(argv,token='a'*32,parent_pid=os.getpid()+1,
                             spawn=fake_spawn,start_new_session=True,close_fds=True)

    def test_child_requires_matching_observer_claim(self):
        with tempfile.TemporaryDirectory(prefix='effect-child-fixture-',dir=W.HERE) as base:
            path = Path(base)/'observation'
            path.mkdir()
            marker = path/'consumed.json'
            name = 'probe-name'
            value = {'schema':'context-public-only-probe-consumed/v1',
                     'status':'CONSUMED_UNKNOWN_UNTIL_EXTERNAL_REVIEW',
                     'name':name,'attempt':str(path),'retry_allowed':False}
            marker.write_text(json.dumps(value))
            marker.chmod(0o600)
            r = types.SimpleNamespace(NAME=name)
            o = types.SimpleNamespace(OBSERVATION=path)
            env = {'CAL_PUBLIC_PROBE_PARENT_PID':'1234',
                   'CAL_PUBLIC_PROBE_PARENT_TOKEN':'b'*32}
            self.assertEqual(W.child_handoff(r,o,env,1234),'b'*32)
            with self.assertRaisesRegex(W.Refused,'CHILD_REQUIRES_EXTERNAL_OBSERVER_PARENT'):
                W.child_handoff(r,o,env,1235)
            marker.chmod(0o644)
            with self.assertRaisesRegex(W.Refused,'PIN_SHAPE'):
                W.child_handoff(r,o,env,1234)

    def test_release_and_observer_effect_paths_simulated_only(self):
        flags = []
        def release_run():
            flags.append(r.EFFECT_ENABLED)
            return {'status':'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED'}
        r = types.SimpleNamespace(EFFECT_ENABLED=False,
            preflight=lambda **kw: flags.append(kw['host']),run_once=release_run)
        def observe_run(**kwargs):
            flags.append((o.EFFECT_ENABLED,r.EFFECT_ENABLED,
                          kwargs['preflight'] is r.preflight,
                          kwargs['read_file'] is r.check_file,
                          kwargs['docker_call'] is r.docker_call,
                          kwargs['observation_path'] == o.OBSERVATION))
            return {'overall':'PASS_BOUNDED_PUBLIC_NAMESPACE_PROBE_ONLY'}
        r.check_file = lambda *args:None
        r.docker_call = lambda *args:None
        o = types.SimpleNamespace(EFFECT_ENABLED=False,RELEASE=None,R=None,
            OBSERVATION=Path('/fixture/observer'),run_observer=observe_run)
        with mock.patch.object(W,'basis',return_value=(r,o)),\
             mock.patch.object(W,'child_handoff',return_value='token'):
            self.assertEqual(W.release_one_shot()['status'],
                             'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED')
            self.assertFalse(r.EFFECT_ENABLED)
        with mock.patch.object(W,'basis',return_value=(r,o)),\
             mock.patch.object(W,'preflight',return_value={}),\
             mock.patch.object(W.os,'urandom',return_value=b'0'*16):
            self.assertEqual(W.observe_one_shot()['overall'],
                             'PASS_BOUNDED_PUBLIC_NAMESPACE_PROBE_ONLY')
            self.assertFalse(r.EFFECT_ENABLED)
            self.assertFalse(o.EFFECT_ENABLED)
            self.assertEqual(o.RELEASE,W.SELF)
            self.assertIs(o.R,r)
        self.assertEqual(flags,[True,True,(True,True,True,True,True,True)])


if __name__ == '__main__': unittest.main()
