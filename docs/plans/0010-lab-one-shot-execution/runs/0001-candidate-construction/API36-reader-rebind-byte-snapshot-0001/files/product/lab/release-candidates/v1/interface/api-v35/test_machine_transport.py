"""Real public Session fixtures and host-bound Machine transport; no fake clock."""
import base64
import copy
import time
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from . import machine_transport as MT
from . import auth as A
from . import example_fixture as F
from . import artifact_model as M
from .protocol import compact, binding, source
from .handlers import cut
from .test_custody_sessions import Sessions
from .custody_context_sessions import D


class MachineTransport(unittest.TestCase):
    """Reuse original fixture helpers without inheriting its test methods."""
    @classmethod
    def setUpClass(cls):
        Sessions.setUpClass.__func__(cls)
        cls.machine_events=[]

    invoke=Sessions.invoke
    success=Sessions.success
    fresh_delivery=Sessions.fresh_delivery
    opening=Sessions.opening
    opening_success=Sessions.opening_success
    inspection=Sessions.inspection
    closing=Sessions.closing
    tearDown=Sessions.tearDown

    def setUp(self):
        Sessions.setUp(self)
        self.opened_result,self.opening_call=self.opening_success()
        self.resource=self.service.sessions.live[self.opened_result['session_ref']]
        path=MT.HERE/'source-manifest.json'
        self.selection={'path':str(path.relative_to(MT.ROOT)),'sha256':source.sha(path.read_bytes())}
        self.peer=MT.select(self.service,self.opened_result['session_ref'],self.selection)
        self.addCleanup(self.peer.close)

    def authenticated(self):
        raw=self.peer.proof()
        context=self.peer.authenticate(raw)
        self.assertEqual(context['agent_instance_ref'],self.resource.agent['node_id'])
        self.assertEqual(context['session_ref'],self.resource.session['node_id'])
        self.assertEqual(context['assignment_ref'],self.opened_result['assignment']['version_ref'])
        self.assertEqual(context['principal_ref'],self.channel.context['principal_ref'])
        self.assertEqual(context['role_assignment_bindings'],[])
        self.assertEqual(context['limits']['max_actions'],0)
        self.assertLessEqual(A.instant(context['expires_at']),self.resource.expires)
        self.assertLessEqual(A.instant(context['expires_at']),A.instant(self.channel.context['expires_at']))
        self.assertNotEqual(context['connection_ref'],self.channel.connection)
        return context,raw

    def machine_call(self,request):
        raw=compact(request);reply=self.peer.call(raw)
        from .fixture_observation import record
        record(self.id(),self.peer.service,raw,reply)
        self.machine_events.append({'operation':request['operation'],'request_sha256':source.sha(raw),'reply':copy.deepcopy(reply)})
        self.assertTrue(self.schemas.valid('api-reply',reply),reply)
        self.assertEqual(reply['request_binding']['sha256'],source.sha(raw))
        self.assertEqual(reply['trusted_context_binding'],binding(self.peer.context['context_ref'],compact(self.peer.context)))
        return reply

    def test_01_actual_identity_signature_and_shared_custody(self):
        context,raw=self.authenticated()
        value=self.peer.P.frame_parse(raw)
        self.peer.public_key.verify(base64.b64decode(value['signature'],validate=True),compact(value['challenge']))
        self.assertIs(self.peer.service.sessions.parent,self.service.sessions)
        self.assertIs(self.service.sessions.live[context['session_ref']],self.resource)
        self.assertFalse(hasattr(self.peer.service.sessions,'lease'))

    def test_02_all_seven_public_read_operations_with_actual_Actor(self):
        context,_=self.authenticated();current=cut(self.view)
        for op in ('lab.status','catalog.get','artifact.query'):
            self.assertEqual(self.machine_call(F.call(context,op,current))['kind'],'result')
        subject=next(s for s in self.view.subjects.values() if s['identity']==self.peer.resource.agent['payload']['profile_ref'].split('@')[0])
        self.assertEqual(self.machine_call(F.call(context,'artifact.inspect',current,artifact=M.artifact_ref(self.view,subject),include=['body','contract','gaps']))['kind'],'result')
        message=D.query(self.view.custody_signed_sources,self.peer.service.sessions.bridge)
        message['budget'].update(max_input_bytes=65536,max_output_bytes=1048576)
        request=F.call(context,'lab.status',current);request.update(operation='context.get',message=message)
        self.assertEqual(self.machine_call(request)['kind'],'result')
        request=self.inspection(context['session_ref'])
        request['message']['actor']={k:context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
        request['message']['actor']['role_assignment_refs']=[]
        self.assertEqual(self.machine_call(request)['kind'],'result')
        self.assertEqual(self.machine_call(F.call(context,'operation.inspect',None,lookup={'operation':'session.open','idempotency_key':self.opening_call['idempotency_key']}))['kind'],'result')
        self.assertEqual({row['operation'] for row in self.machine_events},set(MT.READ_OPERATIONS))

    def test_03_signed_proof_replay_refused(self):
        _,raw=self.authenticated()
        with self.assertRaises(ValueError):self.peer.authenticate(raw)
        self.assertTrue(self.peer.closed);self.assertIsNone(self.peer._private_key)

    def test_04_other_key_refused_and_credential_disposed(self):
        raw=F.proof(Ed25519PrivateKey.generate(),self.peer.challenge)
        with self.assertRaises(Exception):self.peer.authenticate(raw)
        self.assertTrue(self.peer.closed);self.assertIsNone(self.peer._private_key)

    def test_05_another_connection_nonce_refused(self):
        challenge=copy.deepcopy(self.peer.challenge);challenge['connection_ref']='connection:foreign'
        raw=F.proof(Ed25519PrivateKey.generate(),challenge)
        with self.assertRaises(ValueError):self.peer.authenticate(raw)
        self.assertTrue(self.peer.closed)

    def test_06_public_Actor_spoof_does_not_change_trusted_identity(self):
        context,_=self.authenticated();request=F.call(context,'lab.status',cut(self.view))
        request['message']['actor']['principal_ref']='principal:claimed-owner'
        reply=self.machine_call(request)
        self.assertEqual(reply['kind'],'error');self.assertEqual(reply['message']['code'],'unauthorized')
        self.assertEqual(self.peer.guard(),context)

    def test_07_real_effect_request_refused_before_journal_claim(self):
        context,_=self.authenticated();request=copy.deepcopy(self.opening_call)
        request['call_id']='call:Machine:forbidden-effect'
        request['message']['actor']={k:context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
        request['message']['actor']['role_assignment_refs']=[]
        before={str(p.relative_to(self.service.vault.root)):source.sha(p.read_bytes()) for p in self.service.vault.root.rglob('*') if p.is_file()}
        reply=self.peer.call(compact(request))
        self.assertEqual(reply['schema_version'],'lab-api-transport-error/v1-candidate')
        self.assertEqual(reply['code'],'unsupported-operation')
        self.assertEqual(before,{str(p.relative_to(self.service.vault.root)):source.sha(p.read_bytes()) for p in self.service.vault.root.rglob('*') if p.is_file()})

    def test_08_second_peer_cannot_restore_same_resource(self):
        self.peer.close()
        with self.assertRaises(ValueError):MT.select(self.service,self.opened_result['session_ref'],self.selection)
        self.assertFalse(self.resource.closed)

    def test_09_durable_metadata_cannot_supply_missing_live_resource(self):
        sid=self.opened_result['session_ref'];original=self.service.sessions.live.pop(sid)
        try:
            with self.assertRaises(ValueError):MT.select(self.service,sid,self.selection)
        finally:self.service.sessions.live[sid]=original

    def test_10_real_policy_revocation_invalidates_credential(self):
        self.authenticated();original=self.policy.read_bytes()
        with self.policy.open('ab') as stream:stream.write(b'\n')
        try:
            with self.assertRaises(ValueError):self.peer.guard()
            self.assertTrue(self.peer.closed);self.assertIsNone(self.peer._private_key)
        finally:self.policy.write_bytes(original)

    def test_11_real_public_termination_zeroes_RAM_and_disposes_credential(self):
        self.authenticated();note=b'Machine Session short memory';self.peer.note(note)
        retained=self.resource.memory[0]
        self.assertTrue(self.success(self.closing(self.opened_result))['discarded_memory'])
        self.assertTrue(self.resource.closed);self.assertTrue(self.peer.closed)
        self.assertIsNone(self.peer._private_key);self.assertIsNone(self.peer.context)
        self.assertEqual(bytes(retained),b'\0'*len(note));self.assertEqual(self.resource.memory,[])
        for path in self.root.rglob('*'):
            if path.is_file():self.assertNotIn(note,path.read_bytes())
        with self.assertRaises(ValueError):self.peer.proof()

    def test_12_peer_close_keeps_parent_Session_owned_and_live(self):
        self.authenticated();self.peer.service.close()
        self.assertTrue(self.peer.closed);self.assertIsNone(self.peer._private_key)
        self.assertFalse(self.service.sessions.closed);self.assertIs(self.service.sessions.live[self.opened_result['session_ref']],self.resource)
        self.resource.guard();self.assertFalse(self.resource.closed)

    def test_13_real_original_expiry_closes_transport_without_renewal(self):
        self.authenticated();expires=self.resource.expires
        period_path=D.reader.HERE/'packages/0001/period.json'
        original_period=period_path.read_bytes()
        while A.now()<expires:time.sleep(max(0,min(1,(expires-A.now()).total_seconds())))
        with self.assertRaises(Exception):self.peer.guard()
        self.assertTrue(self.peer.closed);self.assertIsNone(self.peer._private_key)
        self.assertEqual(self.resource.expires,expires);self.assertEqual(period_path.read_bytes(),original_period)

    def test_14_closed_proof_shape_refuses_caller_authority_fields(self):
        value=self.peer.P.frame_parse(self.peer.proof());value['role_assignment_refs']=['owner:claimed']
        with self.assertRaises(ValueError):self.peer.authenticate(compact(value))
        self.assertTrue(self.peer.closed);self.assertIsNone(self.peer._private_key)
