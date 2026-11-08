"""Static/pure integration checks. No candidate execute/launch/socket/package calls."""
import ast,copy,hashlib,json,sys,types,unittest
from pathlib import Path
from unittest import mock
C=P=I=PLAN=None

class Tests(unittest.TestCase):
    def test_actual_selection_and_manifest(self):
        s,raw,leaves=C.validate_plan(PLAN)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),PLAN['manifest_sha256']);self.assertEqual(len(leaves),55)
        self.assertEqual(len(s['files']),695);self.assertEqual(sum(r['view']=='runtime' for r in s['files']),677)
        self.assertEqual(len(json.loads(leaves['manifest.json'])['files']),54)
    def test_copy_drift_refuses(self):
        p=copy.deepcopy(PLAN);p['copies'][0]['raw_hex']='00'
        with self.assertRaises(Exception):C.validate_plan(p)
    def test_selection_digest_and_roots_refuse(self):
        for key in ('manifest_sha256','scratch','evidence'):
            p=copy.deepcopy(PLAN);p[key]=('a'*64 if key=='manifest_sha256' else p[key]+'-wrong')
            with self.assertRaises(Exception):C.validate_plan(p)
    def test_extra_leaf_refuses(self):
        p=copy.deepcopy(PLAN);p['leaves']['extra.json']='00'
        with self.assertRaises(Exception):C.validate_plan(p)
    def test_existing_root_refuses_before_runtime_or_launch(self):
        with mock.patch.object(C.os.path,'lexists',return_value=True),mock.patch.object(C.runner,'read_exact') as read,mock.patch.object(C.original,'launch') as launch:
            with self.assertRaisesRegex(RuntimeError,'ALREADY_CONSUMED'):C.preflight(PLAN)
            read.assert_not_called();launch.assert_not_called()
    def test_preflight_exact_ro_only_projection(self):
        with mock.patch.object(C.os.path,'lexists',return_value=False),mock.patch.object(C.runner,'read_exact',return_value=b''):
            v=C.preflight(PLAN)
        a=v['argv'];self.assertIn('--as-pid-1',a);self.assertIn('--sync-fd',a);self.assertEqual(a[a.index('--sync-fd')+1],'3')
        self.assertNotIn('--bind',a);self.assertNotIn('--dev-bind',a)
        self.assertIn(C.SCRATCH+'/output/legacy-fixture-source',a);self.assertIn('/work/out/legacy-fixture-source',a)
        self.assertNotIn(C.EVIDENCE,a);self.assertNotIn(C.SCRATCH+'/host',a)
    def test_fixed_payload_emits_exact_61_actions_and_55_bytes(self):
        events=[];leaves={k:bytes.fromhex(v) for k,v in PLAN['leaves'].items()}
        class Client:
            def begin(self,pin,out):events.append(('BEGIN',''));self.pin=pin
            def seal(self,raw):
                v=json.loads(raw);target='semantic' if v['semantic'] else 'governance';self_test.assertEqual(len(v[target]),25);events.append(('SEAL',target))
            def emit(self,leaf,raw):self_test.assertEqual(raw,leaves[leaf]);events.append(('EMIT',leaf))
            def cold(self,args):
                self_test.assertEqual(args,[P.PACKAGE+'/'+x for x in ('semantic','governance','request.json')]);events.append(('COLD_READ',2 if len(events)==54 else 3))
            def finish(self,binding):self_test.assertEqual(binding,{'path':P.PACKAGE+'/manifest.json','sha256':C.ns.sha(leaves['manifest.json'])});events.append(('FINISH',''))
        self_test=self;client=Client();P.emit_fixture(client,'a'*64,leaves,C.model.wire,C.ns)
        self.assertEqual(events,C.model.wire.schedule());self.assertEqual(len(events),61)
    def test_bad_payload_leafset_refuses_before_any_client_call(self):
        client=mock.Mock()
        with self.assertRaisesRegex(RuntimeError,'FIXTURE_LEAF_SET'):P.emit_fixture(client,'a'*64,{},C.model.wire,C.ns)
        self.assertEqual(client.mock_calls,[])
    def test_payload_retains_namespace_peer_and_finish_eof(self):
        source=Path(I['payload']['path']).read_text();tree=ast.parse(source)
        bootstrap=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='bootstrap')
        self.assertIn("peer[0] == 0",ast.unparse(bootstrap));self.assertIn("claim['pid'] == 1",ast.unparse(bootstrap))
        execute=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='execute');text=ast.unparse(execute)
        self.assertIn('allow_eof=True',text);self.assertLess(text.index('c.step == 61'),text.index('allow_eof=True'))
        self.assertNotIn('build.build',text);self.assertNotIn('LocalFixtureClient',source)
    def test_stage2_pump_exact_validation_projection(self):
        old=Path(I['controller']['path']).read_text();new=Path(I['pump']['path']).read_text()
        def function(text):return next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='pump')
        expected=ast.get_source_segment(old,function(old))
        expected=expected.replace("wrapper={'pid':pid,'start':r['start']}","wrapper={'pid':pid,'start':r['start']};state['wrapper']=wrapper")
        expected=expected.replace('sock.shutdown(socket.SHUT_RDWR)',"state['payload_pidfd']=payload_fd;payload_fd=-1")
        expected=expected.replace('verify_retained_child(root,',"original.verify_retained_child(root.fds[''],")
        self.assertEqual(ast.dump(function(expected)),ast.dump(function(new)))
    def test_dead_payload_refuses_before_ancestry_or_dispatch(self):
        with mock.patch.object(C.select,'select',return_value=([7],[],[])),mock.patch.object(C.ns,'ancestry') as ancestry:
            with self.assertRaisesRegex(RuntimeError,'PAYLOAD_DEAD'):C.live_join({'payload_pidfd':7},9,{}, {},('x',[]))
            ancestry.assert_not_called()
    def test_live_join_rechecks_original_ancestry_and_user_parent(self):
        state={'payload_pidfd':7,'payload_before':[{'start':33}],'wrapper':{'pid':12,'start':22},'payload_credentials':[13,1,2],'payload_claim':{}}
        controller={'namespaces':{'user':[1,4]}}
        with mock.patch.object(C.select,'select',return_value=([],[],[])),mock.patch.object(C.original,'exited',return_value=False),mock.patch.object(C.ns,'ancestry',return_value=[{}]) as ancestry,mock.patch.object(C.ns,'join') as join,mock.patch.object(C.original,'user_parent',return_value=[1,4]):
            self.assertEqual(C.live_join(state,9,controller,{},('sha',[1,2])),(13,33,1,2));ancestry.assert_called_once();join.assert_called_once()
        with mock.patch.object(C.select,'select',return_value=([],[],[])),mock.patch.object(C.original,'exited',return_value=False),mock.patch.object(C.ns,'ancestry',return_value=[{}]),mock.patch.object(C.ns,'join'),mock.patch.object(C.original,'user_parent',return_value=[9,9]):
            with self.assertRaisesRegex(RuntimeError,'USER_PARENT_DRIFT'):C.live_join(state,9,controller,{},('sha',[1,2]))
    def test_child_result_requires_exact_success_stream(self):
        expected={'schema':'mapper-namespace-runner-result/v1','synthetic_only':True,'actions':61,'host_qualified':False};raw=(json.dumps(expected,sort_keys=True)+'\n').encode()
        with mock.patch.object(C.original,'drain_streams',return_value=[]):
            C.result_streams({'status':0},[],{'stdout':raw,'stderr':b''},{})
            for streams,status in [({'stdout':raw,'stderr':b'bad'},0),({'stdout':raw+b'x','stderr':b''},0),({'stdout':raw,'stderr':b''},256)]:
                with self.assertRaises(RuntimeError):C.result_streams({'status':status},[],streams,{})
    def test_postclose_contract_stays_provisional_only(self):
        tree=ast.parse(Path(I['candidate']['path']).read_text());source=ast.unparse(tree)
        self.assertIn("'result': 'UNKNOWN'",source);self.assertIn('owned.verify_closed_evidence(seal)',source)
        self.assertLess(source.index('finally:\n            evidence.close()'),source.index('owned.verify_closed_evidence(seal)'))
        self.assertIn('parent.shutdown(socket.SHUT_RDWR)',source);self.assertNotIn('os.unlink',source)


def main(inputs,candidate,payload):
    global C,P,I,PLAN
    C=candidate;P=payload;I=inputs;raw=Path(inputs['plan']['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=inputs['plan']['sha256']:raise RuntimeError('PLAN_DRIFT')
    PLAN=json.loads(raw);result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    print(json.dumps({'result':'PASS' if result.wasSuccessful() else 'FAIL','checks':result.testsRun,'effect_runs':0,'namespace_runs':0,'package_writes':0,'host_qualified':False},sort_keys=True))
    return 0 if result.wasSuccessful() else 1
