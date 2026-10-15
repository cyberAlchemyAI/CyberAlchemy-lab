"""Real signed source and live resources; no copied grants or fake Session facts."""
import copy
from contextlib import ExitStack
import importlib
import json
from pathlib import Path
import tempfile
import unittest

PACKAGE=None
PROFILE=None


class LessonChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert PACKAGE and PROFILE
        cls.P=importlib.import_module(PACKAGE+'.protocol')
        cls.F=importlib.import_module(PACKAGE+'.example_fixture')
        cls.S=importlib.import_module(PACKAGE+'.service')
        cls.MT=importlib.import_module(PACKAGE+'.machine_transport')
        cls.C=importlib.import_module(PACKAGE+'.custody_context_sessions')
        cls.original=importlib.import_module(PACKAGE+'.test_custody_sessions').Sessions
        cls.stack=ExitStack();cls.addClassCleanup(cls.stack.close)
        cls.view=cls.stack.enter_context(cls.P.source.replay_source('custody-participation'))
        cls.schemas=cls.P.Schemas(PROFILE)
        cls.materials,cls.metadata,cls.target=cls.F.materials_for(cls.view)
        cls.events=[]
        for name in ('invoke','success','fresh_delivery','opening','opening_success','inspection','closing'):
            setattr(cls,name,getattr(cls.original,name))

    def setUp(self):
        self.fixture_stack=ExitStack();self.addCleanup(self.fixture_stack.close)
        self.root=Path(self.fixture_stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-API52-owned-lesson-')))
        self.root.chmod(0o700)
        D=self.C.D;R=self.C.R;selected=self.view.custody_signed_sources
        exact=lambda ref:copy.deepcopy(selected.sources.resolve(ref+'@'+R.VERSION)[0].artifact)
        assignment,work,coord,profile=(exact(ref) for ref in (R.ASSIGNMENT,R.WORK,R.COORDINATION,R.PROFILE))
        current=self.S.cut(self.view)
        instruction={'schema_version':'lab-lesson-instruction-policy/v1-candidate','source_cut':current,
            'assignment':assignment,'work':work,'coordination_context':coord,'instruction_refs':['instruction:bounded-candidate-advice'],
            'tags':[],'veto_lesson_influence':False,'authority_effect':'none','actual_owner_outcome':None}
        instruction_raw=self.P.compact(instruction)
        source_path=self.view.data['projection']['contracts']['cal.artifact-type.work/v1']['schema_path']
        plan={'schema_version':'lab-lesson-host-plan/v1-candidate','source_cut':current,'assignment':assignment,'work':work,
            'coordination_context':coord,'profile':profile,'project_ref':selected.sources.scope_ref,
            'family':'family:bounded-signed-source-inspection','source_binding':{'ref':source_path,'sha256':self.view.data['baseline']['materials'][source_path]},
            'instruction_policy_binding':self.P.binding('candidate:lesson-instructions',instruction_raw),
            'domain_profile':{'supported_lesson_statuses':['candidate'],'supported_retention_policy_refs':['protocol:W06-retain-project-evidence-exclude-session-notes@1'],
                'reviewed_use_postures':[{'disposition':'reviewed-for-controlled-use','effective_state':'local-admitted-current','fixture_only':True}]},
            'lessons':[],'authority_effect':'none','actual_owner_outcome':None}
        materials={**self.materials,'candidate:lesson-instructions':instruction_raw,'candidate:lesson-host-plan':self.P.compact(plan)}
        projection=importlib.import_module(PACKAGE+'.projection_refresh').control(self.view)
        self.key,self.policy,self.policy_pin=self.F.provision(self.root,'custody-participation',materials,self.metadata,
                                                           principal=R.PRINCIPAL,projection_control=projection)
        # Finish provisioning before any authentication or live resource exists.
        # The original Assignment period remains byte-identical and clock-bound.
        policy=self.P.frame_parse(self.policy.read_bytes())
        policy.update(schema_version='lab-local-lesson-read-policy/v1-candidate',allowed_operations=list(self.P.LESSON_SUPPORTED),
            development_authorization_binding=self.P.binding(str(D.AUTH.relative_to(self.P.ROOT)),D.AUTH.read_bytes()),
            lesson_control={'plan_binding':self.P.binding('candidate:lesson-host-plan',materials['candidate:lesson-host-plan'])})
        self.policy.write_bytes(self.P.compact(policy));self.policy_pin=self.P.source.sha(self.policy.read_bytes())
        self.channel=importlib.import_module(PACKAGE+'.auth').ReaderChannel(self.policy,self.policy_pin,self.schemas)
        self.authenticated=self.channel.authenticate(self.F.proof(self.key,self.channel.challenge))
        self.service=self.S.Service(self.view,self.channel,self.schemas)
        self.fixture_stack.callback(self.service.close)
        self.delivery_result=None;self.opened=[]
        self.result,self.opening_call=self.opening_success()
        source_path=self.MT.HERE/'source-manifest.json'
        self.peer=self.MT.select(self.service,self.result['session_ref'],{'path':str(source_path.relative_to(self.MT.ROOT)),
                              'sha256':self.P.source.sha(source_path.read_bytes())})
        self.fixture_stack.callback(self.peer.close)
        self.peer_context=self.peer.authenticate(self.peer.proof())

    def request(self):
        message=self.C.D.query(self.view.custody_signed_sources,self.peer.service.sessions.bridge)
        message['budget'].update(max_actions=0,max_input_bytes=65536,max_output_bytes=1048576)
        request=self.F.call(self.peer_context,'lab.status',self.S.cut(self.view))
        request.update(operation='lesson.select',message=message)
        return request

    def machine_call(self,request):
        raw=self.P.compact(request);reply=self.peer.call(raw)
        self.events.append({'actual_machine_call':json.loads(raw),'request_sha256':self.P.source.sha(raw),'reply':copy.deepcopy(reply)})
        return reply

    def test_01_actual_empty_inventory_and_zero_action(self):
        resource=self.peer.resource;sentinel=b'API51-Session-only-short-memory';resource.note(sentinel);held=resource.memory[0]
        before=len(list((self.root/'workspace/journal').glob('*.allocated.json')))
        reply=self.machine_call(self.request())
        self.assertEqual(reply.get('kind'),'result',reply)
        self.assertEqual(reply['message']['schema_version'],'lab-lesson-selection/v1-candidate')
        self.assertEqual(reply['message']['items'],[])
        self.assertEqual(reply['message']['session_ref'],resource.session['node_id'])
        self.assertEqual(reply['message']['assignment'],self.result['assignment'])
        self.assertEqual(self.peer_context['limits']['max_actions'],0)
        self.assertEqual(before,len(list((self.root/'workspace/journal').glob('*.allocated.json'))))
        self.assertEqual(reply['handler_binding']['ref'],str((self.MT.HERE/'lesson_selection.py').relative_to(self.MT.ROOT)))
        for path in (self.root/'workspace').rglob('*'):
            if path.is_file():self.assertNotIn(sentinel,path.read_bytes())
        self.service.sessions.dispose_all()
        self.assertEqual(held,bytearray(len(sentinel)));self.assertTrue(self.peer.closed);self.assertIsNone(self.peer._private_key)

    def test_02_spoofed_Actor_and_foreign_Assignment_refused(self):
        request=self.request();request['message']['actor']['principal_ref']='principal:claimed-owner'
        reply=self.machine_call(request)
        self.assertEqual(reply.get('kind'),'error',reply);self.assertEqual(reply['message']['code'],'unauthorized')
        request=self.request();request['message']['assignment']['version_ref']='assignment:foreign@1'
        reply=self.machine_call(request)
        self.assertEqual(reply.get('kind'),'error',reply)
        self.assertEqual(reply['message']['authority_effect'],'none')

    def test_03_disposal_does_not_restore_peer(self):
        request=self.request();resource=self.peer.resource
        self.service.sessions.dispose_all()
        self.assertTrue(resource.closed);self.assertEqual(resource.memory,[])
        self.assertIsNone(self.peer._private_key)
        reply=self.machine_call(request)
        self.assertEqual(reply['schema_version'],'lab-api-transport-error/v1-candidate')
        self.assertEqual(reply['code'],'unauthenticated-channel')

    def tearDown(self):
        self.peer.close();self.service.close();self.key=None
        self.fixture_stack.close()
        self.assertFalse(self.root.exists())
