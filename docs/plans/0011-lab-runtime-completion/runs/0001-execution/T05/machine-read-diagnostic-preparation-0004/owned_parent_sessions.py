from _cal_T05_selected_actual_API17_0003.legacy_fixture_selection import *
"""Real eleven-operation integration, Session custody and original preparation guards."""

# Owned helper namespace; production modules remain selected at true API origins.
from _cal_T05_selected_actual_API17_0003.example_fixture import *
from _cal_T05_selected_actual_API17_0003.service import *
from _cal_T05_selected_actual_API17_0003.projection_refresh import control as projection_control
from _cal_T05_selected_actual_API17_0003.current_legacy_context_sessions import stable_policy,R,D,EL
from _cal_T05_selected_actual_API17_0003.workspace import privacy
from contextlib import ExitStack
from datetime import timedelta
import argparse,copy,json,os,tempfile,threading,time,unittest
from unittest.mock import patch

class Sessions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack=ExitStack();cls.addClassCleanup(cls.stack.close)
        cls.view=cls.stack.enter_context(source.replay_source(PUBLIC_SOURCE_NAME));cls.schemas=Schemas(PROFILE)
        cls.materials,cls.metadata,cls.target=materials_for(cls.view)
        cls.events=[]
    def setUp(self):
        # Every method receives a fresh host/key/nonce and the same bounded grant.
        # A slow full suite must not inherit another method's expired permission.
        self.fixture_stack=ExitStack();self.addCleanup(self.fixture_stack.close)
        self.root=Path(self.fixture_stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-isolated-Session-method-')));self.root.chmod(0o700)
        self.key,self.policy,self.policy_pin=provision(self.root,PUBLIC_SOURCE_NAME,self.materials,self.metadata,principal=R.PRINCIPAL,projection_control=projection_control(self.view))
        self.channel=ReaderChannel(self.policy,self.policy_pin,self.schemas);self.authenticated=self.channel.authenticate(proof(self.key,self.channel.challenge))
        self.service=Service(self.view,self.channel,self.schemas);self.fixture_stack.callback(self.service.close)
        self.delivery_result=None;self.opened=[]
    def invoke(self,c,*,raw=None):
        raw=compact(c) if raw is None else raw;r=self.service.call(raw)
        from .owned_observer import record
        record(self.OWNED_OUTPUT,self.id(),self.service,raw,r)
        self.assertTrue(self.schemas.valid('api-reply',r),r)
        self.assertEqual(r['request_binding']['sha256'],source.sha(raw));self.assertEqual(r['contract_profile_binding'],self.schemas.profile_binding)
        self.events.append({'original_call':json.loads(raw),'request_byte_sha256':source.sha(raw),'reply':r})
        return r
    def success(self,c):
        r=self.invoke(c);self.assertEqual(r['kind'],'result',r);return r['message']
    def fresh_delivery(self):
        if self.delivery_result is None or instant(self.delivery_result['expires_at'])<now()+timedelta(seconds=150):
            ctx=self.service.sessions.bridge;selected=self.view.custody_signed_sources
            message=D.query(selected,ctx);message['budget'].update(max_input_bytes=65536,max_output_bytes=1048576)
            c=call(self.channel.context,'lab.status',cut(self.view));c.update(operation='context.get',message=message)
            self.delivery_result=self.success(c)
        return copy.deepcopy(self.delivery_result)
    def opening(self,*,key=None):
        delivery=self.fresh_delivery();selected=self.view.custody_signed_sources
        ref=lambda i:copy.deepcopy(selected.sources.resolve(i+'@'+R.VERSION)[0].artifact)
        c=call(self.channel.context,'lab.status',cut(self.view));actor=c['message']['actor'];budget=c['message']['budget'];budget['max_actions']=1
        c.update(operation='session.open',idempotency_key=key or 'open:'+uuid.uuid4().hex,message={
            'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:Session-open:'+uuid.uuid4().hex,
            'actor':actor,'assignment':ref(R.ASSIGNMENT),'profile':ref(R.PROFILE),'implementation':ref(R.IMPLEMENTATION),'capabilities':[ref(R.CAPABILITY)],
            'context_delivery_binding':binding('context-delivery:'+delivery['context_view']['version_ref'],compact(delivery)),
            'authority_envelope_binding':stable_policy(self.channel),'source_cut':copy.deepcopy(cut(self.view)),
            'budget':budget,'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'})
        return c
    def opening_success(self):
        c=self.opening();r=self.success(c);self.assertEqual(r['posture'],'active');self.opened.append(r['session_ref']);return r,c
    def inspection(self,sid):
        c=call(self.channel.context,'lab.status',cut(self.view));b=c['message']['budget'];a=c['message']['actor']
        c.update(operation='session.inspect',message={'schema_version':'lab-session-inspect-request/v1-candidate','request_ref':'request:Session-inspect:'+uuid.uuid4().hex,'actor':a,'session_ref':sid,'budget':b,'authority_effect':'none'})
        return c
    def closing(self,opened,state=None):
        state=self.success(self.inspection(opened['session_ref'])) if state is None else state
        c=call(self.channel.context,'lab.status',cut(self.view));c.update(operation='session.close',idempotency_key='close:'+uuid.uuid4().hex,
            message={'schema_version':'lab-agent-session-close/v1-candidate','request_ref':'request:Session-close:'+uuid.uuid4().hex,
                'session_ref':opened['session_ref'],'agent_instance_ref':opened['agent_instance_ref'],
                'expected_session_binding':state['last_receipt_binding'],'requested_at':now().isoformat(),'reason':'completed','eligible_audit_bindings':[],'authority_effect':'none'})
        return c
    def tearDown(self):
        # Clean up all test-owned resources, independent of original source validity.
        self.service.sessions.dispose_all()
    def refreshing(self):
        c=call(self.channel.context,'lab.status',cut(self.view));budget=c['message']['budget'];budget['max_actions']=1
        grant=self.channel.policy['projection_control'];prior=self.service.handlers.generations.get(source.sha(compact(cut(self.view))))
        c.update(operation='projection.refresh',idempotency_key='projection:Session-suite:'+uuid.uuid4().hex,message={
            'schema_version':'lab-projection-refresh-request/v1-candidate','request_ref':'request:Session-suite-projection:'+uuid.uuid4().hex,
            'source_cut':copy.deepcopy(cut(self.view)), 'projector_binding':grant['projector_binding'],
            'contract_catalog_binding':grant['contract_catalog_binding'],'expected_generation_binding':None if prior is None else prior.binding,
            'budget':budget,'authority_effect':'none'})
        return c
    def negative_open(self,change):
        c=self.opening();change(c['message']);before=set(self.service.sessions.live);r=self.invoke(c)
        self.assertEqual(r['kind'],'error',r);self.assertEqual(set(self.service.sessions.live),before);return r


