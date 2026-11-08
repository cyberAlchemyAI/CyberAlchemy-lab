"""Inert Docker projection and synthetic observer tests only."""
import datetime as dt
import json
import os
from pathlib import Path
import unittest
from unittest import mock

import observer
import plan

NOW=dt.datetime(2026,10,20,18,30,tzinfo=dt.timezone.utc)

class PlanTests(unittest.TestCase):
    def test_reviewed_public_basis_and_current_period(self):
        basis=plan.pinned_basis(NOW)
        self.assertEqual(basis['loader_review_sha256'],plan.LOADER_REVIEW_SHA)
        self.assertEqual(basis['controller_review_sha256'],plan.CONTROLLER_REVIEW_SHA)
        self.assertEqual(basis['portable_freeze_sha256'],plan.PORTABLE_FREEZE_SHA)
        self.assertEqual(basis['predecessor_hold_review_sha256'],plan.PREDECESSOR_REVIEW_SHA)
        self.assertEqual(basis['effect'],'NOT_RUN')
        self.assertFalse(os.path.lexists(plan.CLAIM))

    def test_expiry_or_review_drift_refuses(self):
        with self.assertRaisesRegex(plan.Refused,'SELECTED_SOURCE_PERIOD_OR_ENVIRONMENT'):
            plan.pinned_basis(dt.datetime(2026,10,21,15,tzinfo=dt.timezone.utc))
        with mock.patch.object(plan,'CONTROLLER_REVIEW_SHA','0'*64):
            with self.assertRaisesRegex(plan.Refused,'PIN_DRIFT'):
                plan.pinned_basis(NOW)
        with mock.patch.object(plan,'PORTABLE_FREEZE_SHA','0'*64):
            with self.assertRaisesRegex(plan.Refused,'PIN_DRIFT'):
                plan.pinned_basis(NOW)

    def test_exclusive_claim_precondition(self):
        original=plan.os.path.lexists
        def present(path):
            return path==plan.CLAIM or original(path)
        with mock.patch.object(plan.os.path,'lexists',side_effect=present):
            with self.assertRaisesRegex(plan.Refused,'ATTEMPT_ALREADY_CONSUMED'):
                plan.pinned_basis(NOW)

    def test_projected_create_has_only_three_ro_binds_and_required_limits(self):
        row=plan.plan(NOW,'a'*32)
        self.assertFalse(row['effect_enabled'])
        self.assertFalse(row['docker_invoked'])
        argv=row['create_argv']
        self.assertEqual(argv.count('--mount'),3)
        mounts=[argv[i+1] for i,value in enumerate(argv) if value=='--mount']
        self.assertEqual(mounts,[
            f'type=bind,src={plan.STAGE},dst={plan.STAGE},readonly',
            f'type=bind,src={plan.BUNDLE},dst=/bundle,readonly',
            f'type=bind,src={plan.CLAIM},dst=/control/attempt.claim,readonly'])
        for flag,value in [('--network','none'),('--cap-drop','ALL'),
                           ('--user','1000:1000'),('--security-opt','no-new-privileges')]:
            self.assertEqual(argv[argv.index(flag)+1],value)
        self.assertIn('--read-only',argv)
        self.assertEqual(argv.count('--tmpfs'),2)
        self.assertEqual(argv[-6:],[plan.IMAGE,'python','-I','-B','-c',
                                    'raise SystemExit("EFFECT_DISABLED_NO_REVIEWED_SIGNED_OPEN_CHILD")'])
        self.assertIn('portable_bundle_independent_review',
                      row['unresolved'])

    def test_token_drift_and_all_effects_refuse(self):
        with self.assertRaisesRegex(plan.Refused,'ONE_SHOT_LABEL_SHAPE'):
            plan.projected_create_argv('../wrong')
        for fn in (plan.execute,plan.create_claim,observer.dispatch,
                   observer.publish_attestation):
            with self.assertRaisesRegex(Exception,'EFFECT_DISABLED'):
                fn()

    def test_readonly_image_observation_and_wrong_image_refusal(self):
        class Result:
            returncode=0
            stderr=b''
            stdout=f'{plan.IMAGE} amd64 20001:20001 /attempt/root\n'.encode()
        class Absent:
            returncode=1
            stdout=b'\n'
            stderr=('Error response from daemon: No such container: '+plan.NAME+'\n').encode()
        def runner(argv,**_kwargs):
            return Absent() if argv[1:3]==['container','inspect'] else Result()
        self.assertEqual(plan.docker_readonly_observation(runner)['image_id'],
                         plan.IMAGE)
        Result.stdout=b'sha256:wrong amd64 20001:20001 /attempt/root\n'
        with self.assertRaisesRegex(plan.Refused,'DOCKER_IMAGE_ID_OR_CONFIG'):
            plan.docker_readonly_observation(runner)
        Result.stdout=f'{plan.IMAGE} amd64 20001:20001 /attempt/root\n'.encode()
        Absent.stderr=b'other absence failure'
        with self.assertRaisesRegex(plan.Refused,'DOCKER_NAME_ABSENCE'):
            plan.docker_readonly_observation(runner)

    def test_docker_returncode_bool_and_float_aliases_refuse(self):
        class Result:
            returncode=0
            stderr=b''
            stdout=f'{plan.IMAGE} amd64 20001:20001 /attempt/root\n'.encode()
        class Absent:
            returncode=1
            stdout=b'\n'
            stderr=('Error response from daemon: No such container: '+plan.NAME+'\n').encode()
        def runner(argv,**_kwargs):
            return Absent() if argv[1:3]==['container','inspect'] else Result()
        for invalid in (False,0.0):
            Result.returncode=invalid
            with self.assertRaisesRegex(plan.Refused,'DOCKER_IMAGE_ID_OR_CONFIG'):
                plan.docker_readonly_observation(runner)
        Result.returncode=0
        for invalid in (True,1.0):
            Absent.returncode=invalid
            with self.assertRaisesRegex(plan.Refused,'DOCKER_NAME_ABSENCE'):
                plan.docker_readonly_observation(runner)

    def test_synthetic_observer_binding_and_negative_external_cases(self):
        basis=plan.pinned_basis(NOW)
        claim='f'*64
        identity={'dev':1,'ino':2}
        row={'schema':'context-signed-scope-child-attestation/v1',
             'status':'PROVISIONAL_EXTERNAL_OBSERVER_ONLY',
             'scope_ref':basis['scope_expected'],
             'source_manifest_sha256':basis['source_manifest_sha256'],
             'reader_manifest_sha256':basis['reader_manifest_sha256'],
             'reader_code_sha256':basis['reader_code_sha256'],
             'loader_freeze_sha256':basis['loader_freeze_sha256'],
             'controller_freeze_sha256':basis['controller_freeze_sha256'],
             'source_period_sha256':basis['source_period_sha256'],
             'opened_at':'2026-10-20T18:30:00+00:00',
             'closed_at':'2026-10-20T18:31:00+00:00',
             'claim_marker_sha256':claim,'claim_dev':1,'claim_ino':2,
             'first_guard':True,'final_guard':True,
             'reader_guard':True,'close_ok':True,'authority_effect':'none',
             'actual_owner_outcome':None,'retry_allowed':False}
        raw=(json.dumps(row,sort_keys=True,separators=(',',':'))+'\n').encode()
        terminal={'cid':'a'*64,'exit_code':0,'oom_killed':False}
        result=observer.validate_fixture_envelope(basis,claim,identity,raw,b'',0,terminal,True)
        self.assertEqual(result['status'],'SYNTHETIC_ENVELOPE_VALID_NO_EFFECT_CLAIM')
        for changes in ({'scope_ref':'forged'},{'private_body':'oops'},
                        {'close_ok':False},{'claim_ino':3}):
            forged=(json.dumps(row|changes)+'\n').encode()
            with self.assertRaisesRegex(observer.Refused,'SIGNED_SCOPE_ATTESTATION_BINDING'):
                observer.validate_fixture_envelope(basis,claim,identity,forged,b'',0,terminal,True)
        for changes in ({'closed_at':'2026-10-21T15:00:00+00:00'},
                        {'closed_at':'2026-10-20T18:46:00+00:00'}):
            forged=(json.dumps(row|changes)+'\n').encode()
            with self.assertRaisesRegex(observer.Refused,'SIGNED_SCOPE_PERIOD_OR_DURATION'):
                observer.validate_fixture_envelope(basis,claim,identity,forged,b'',0,terminal,True)
        with self.assertRaisesRegex(observer.Refused,'EXTERNAL_PROCESS_OR_STREAMS'):
            observer.validate_fixture_envelope(basis,claim,identity,raw,b'error',0,terminal,True)
        with self.assertRaisesRegex(observer.Refused,'DOCKER_TERMINAL_OR_ABSENCE'):
            observer.validate_fixture_envelope(basis,claim,identity,raw,b'',0,terminal,False)

    def test_synthetic_scalar_aliases_refuse(self):
        basis=plan.pinned_basis(NOW)
        claim='f'*64
        identity={'dev':1,'ino':2}
        row={'schema':'context-signed-scope-child-attestation/v1',
             'status':'PROVISIONAL_EXTERNAL_OBSERVER_ONLY',
             'scope_ref':basis['scope_expected'],
             'source_manifest_sha256':basis['source_manifest_sha256'],
             'reader_manifest_sha256':basis['reader_manifest_sha256'],
             'reader_code_sha256':basis['reader_code_sha256'],
             'loader_freeze_sha256':basis['loader_freeze_sha256'],
             'controller_freeze_sha256':basis['controller_freeze_sha256'],
             'source_period_sha256':basis['source_period_sha256'],
             'opened_at':'2026-10-20T18:30:00+00:00',
             'closed_at':'2026-10-20T18:31:00+00:00',
             'claim_marker_sha256':claim,'claim_dev':1,'claim_ino':2,
             'first_guard':True,'final_guard':True,'reader_guard':True,
             'close_ok':True,'authority_effect':'none',
             'actual_owner_outcome':None,'retry_allowed':False}
        def raw(value):return (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
        terminal={'cid':'a'*64,'exit_code':0,'oom_killed':False}
        for invalid in (False,0.0):
            with self.assertRaisesRegex(observer.Refused,'EXTERNAL_PROCESS_OR_STREAMS'):
                observer.validate_fixture_envelope(basis,claim,identity,raw(row),b'',invalid,terminal,True)
            with self.assertRaisesRegex(observer.Refused,'DOCKER_TERMINAL_OR_ABSENCE'):
                observer.validate_fixture_envelope(basis,claim,identity,raw(row),b'',0,terminal|{'exit_code':invalid},True)
        for field,invalid in (('claim_dev',True),('claim_dev',1.0),
                              ('claim_ino',2.0)):
            with self.assertRaisesRegex(observer.Refused,'SIGNED_SCOPE_ATTESTATION_BINDING'):
                observer.validate_fixture_envelope(basis,claim,identity,
                    raw(row|{field:invalid}),b'',0,terminal,True)

if __name__=='__main__':unittest.main()
