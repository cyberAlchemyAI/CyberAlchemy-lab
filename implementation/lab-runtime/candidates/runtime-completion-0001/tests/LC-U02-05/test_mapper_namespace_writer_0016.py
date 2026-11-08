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
            with self.assertRaisesRegex(RuntimeError,'PAYLOAD_DEAD'):C.live_join({**C.lineage_state(),'payload_pidfd':7},9,{}, {},('x',[]))
            ancestry.assert_not_called()
    def test_live_join_rechecks_original_ancestry_and_user_parent(self):
        state={**C.lineage_state(),'payload_pidfd':7,'payload_before':[{'start':33}],'wrapper':{'pid':12,'start':22},'payload_credentials':[13,1,2],'payload_claim':{}}
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


    def boundary_fixture(self,verb,change_at=None,kind='namespace'):
        from contextlib import ExitStack
        state={**C.lineage_state(),'payload_pidfd':7,'payload_before':[{'start':33}],'wrapper':{'pid':12,'start':22},'payload_credentials':[13,1,2],'payload_claim':{}}
        changed=[False];events=[];server=object.__new__(C.LiveMediator)
        server._held=(state,9,{'namespaces':{'user':[1,4]}},{},('sha',[1,2]));server.peer=(13,33,1,2);server.transport_peer=server.peer
        server.endpoint=mock.Mock();server.closed=False;server.failed=False;server.finished=False;server.pending=None;server.cleanup_uncertain=False;server.deadline=C.time.monotonic()+60;server.sha='a'*64
        writer=mock.Mock();writer.close_errors=0;server.writer=None if verb=='BEGIN' else writer;server._open_writer=mock.Mock(return_value=writer);server._guard=mock.Mock()
        action={'verb':verb,'ordinal':1,'request_sha256':'b'*64,'target':'leaf','blob_sha256':'c'*64,'size_bytes':1}
        writer.emit.return_value={'path':'leaf','sha256':'c'*64,'size':1,'durable_observed':True}
        writer.finish.return_value={'leaf_count':55,'manifest_row_count':54,'package_writer_complete':True}
        def received(*a):
            events.append('receive')
            if change_at=='receive':changed[0]=True
            return b'frame'
        def projected(*a,**k):
            events.append('project')
            if change_at=='projection':changed[0]=True
            return action
        server.model=types.SimpleNamespace(phase='PACKAGE',protocol=types.SimpleNamespace(ready={'data':b'x'}),receive_synthetic=projected,prepare_reply_synthetic=mock.Mock(return_value={'packets':(b'ack',)}),fail=mock.Mock())
        def selected(*a):
            events.append('pidfd')
            return ([7],[],[]) if changed[0] and kind=='pidfd' else ([],[],[])
        def ancestry(*a):
            events.append('ancestry')
            if changed[0] and kind=='ancestry':raise RuntimeError('LINEAGE_CHANGED')
            return [{}]
        stack=ExitStack()
        for obj,key,value in [(C.select,'select',selected),(C.original,'exited',lambda x:False),(C.ns,'ancestry',ancestry),(C.ns,'join',lambda *a:None),(C.original,'user_parent',lambda x:[9,9] if changed[0] and kind=='namespace' else [1,4]),(C.transport,'process_start',lambda x:33),(C.transport,'recv_frame',received)]:stack.enter_context(mock.patch.object(obj,key,value))
        return stack,server,writer,events,changed

    def test_lineage_changes_during_receive_refuse_before_all_writer_effects(self):
        for verb in ('BEGIN','EMIT','FINISH'):
            for kind in ('pidfd','ancestry','namespace'):
                with self.subTest(verb=verb,kind=kind):
                    stack,server,writer,events,changed=self.boundary_fixture(verb,'receive',kind)
                    with stack:
                        with self.assertRaises(C.mediator.Refusal):server.prepare_one()
                    self.assertIn('receive',events);self.assertNotIn('project',events)
                    server._open_writer.assert_not_called();writer.emit.assert_not_called();writer.finish.assert_not_called();self.assertTrue(server.failed)

    def test_lineage_change_after_projection_refuses_immediately_before_writer(self):
        for verb in ('BEGIN','EMIT','FINISH'):
            with self.subTest(verb=verb):
                stack,server,writer,events,changed=self.boundary_fixture(verb,'projection')
                with stack:
                    with self.assertRaises(C.mediator.Refusal):server.prepare_one()
                self.assertIn('project',events);server._open_writer.assert_not_called();writer.emit.assert_not_called();writer.finish.assert_not_called()

    def test_unchanged_live_lineage_allows_fixed_writer_prepare(self):
        for verb in ('BEGIN','EMIT','FINISH'):
            with self.subTest(verb=verb):
                stack,server,writer,events,changed=self.boundary_fixture(verb)
                with stack:result=server.prepare_one()
                self.assertEqual(result['verb'],verb);self.assertIsNotNone(server.pending['prepared']);self.assertFalse(server.failed)
                if verb=='BEGIN':server._open_writer.assert_called_once()
                elif verb=='EMIT':writer.emit.assert_called_once_with('leaf',b'x')
                else:writer.finish.assert_called_once()
                self.assertGreaterEqual(events.count('pidfd'),3)

    def test_changed_lineage_after_prepare_refuses_before_ack_send(self):
        stack,server,writer,events,changed=self.boundary_fixture('EMIT')
        with stack,mock.patch.object(C.transport,'send_frame') as send:
            server.prepare_one();writer.emit.assert_called_once();changed[0]=True
            with self.assertRaises(C.mediator.Refusal):server.send_pending()
            send.assert_not_called();self.assertTrue(server.failed);self.assertTrue(writer.unknown)

    def test_prepare_projection_only_adds_three_fixed_effect_guards(self):
        base=ast.parse(Path(I['mediator']['path']).read_text());child=ast.parse(Path(I['candidate']['path']).read_text())
        def method(tree,name):
            cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==name)
            return next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='prepare_one')
        node=method(child,'LiveMediator');removed=[0]
        class Remove(ast.NodeTransformer):
            def visit_Expr(self,n):
                if isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=='self._live_guard':removed[0]+=1;return None
                return self.generic_visit(n)
        result=Remove().visit(node)
        self.assertEqual(removed[0],3);self.assertEqual(ast.dump(result),ast.dump(method(base,'Mediator')))

    def retained_fixture(self):
        row=I['consumed_observations'];raw=Path(row['path']).read_bytes()
        self.assertEqual((len(raw),hashlib.sha256(raw).hexdigest()),(row['size_bytes'],row['sha256']))
        observed=json.loads(raw);state=copy.deepcopy(observed['state']);state.update(C.lineage_state());state['payload_pidfd']=7
        controller=state['host_join_summary']['controller'];before=state['payload_before'];fake_exe=b'owned synthetic executable identity only'
        before[0]['exe_sha256']=C.ns.sha(fake_exe);state['payload_claim']['exe_sha256']=C.ns.sha(fake_exe)
        indexed={r['pid']:(i,r) for i,r in enumerate(before)}
        def read(path,limit,**kwargs):
            _,proc,pid,name=path.split('/');i,r=indexed[int(pid)]
            data=fake_exe if name=='exe' else bytes.fromhex(observed['proc']['hello-before/%d/%s'%(i,name)])
            self.assertLessEqual(len(data),limit);return data,r['exe_identity']
        def namespace(pid,name):return indexed[pid][1]['namespaces'][name]
        return observed,state,controller,read,namespace,(C.ns.sha(fake_exe),before[0]['exe_identity'])

    def test_original_duplicate_capture_reproduces_refusal(self):
        observed,state,controller,read,namespace,exe=self.retained_fixture();originals={}
        with mock.patch.object(C.ns,'read_regular',read),mock.patch.object(C.ns,'namespace',namespace):
            C.ns.ancestry(state['payload_credentials'][0],state['wrapper'],originals,'package-current')
            before=dict(originals)
            with self.assertRaisesRegex(C.ns.Refusal,'ORIGINAL_REUSE'):
                C.ns.ancestry(state['payload_credentials'][0],state['wrapper'],originals,'package-current')
        self.assertEqual(originals,before)

    def test_full_fixed_schedule_repeated_lineage_is_unique_and_bounded(self):
        observed,state,controller,read,namespace,exe=self.retained_fixture();bootstrap={k:bytes.fromhex(v) for k,v in observed['proc'].items()};before=dict(bootstrap)
        budget=C.live_budget(PLAN);self.assertEqual(budget['successful_live_joins'],1461)
        with mock.patch.object(C.ns,'read_regular',read),mock.patch.object(C.ns,'namespace',namespace),mock.patch.object(C.select,'select',return_value=([],[],[])),mock.patch.object(C.original,'exited',return_value=False),mock.patch.object(C.original,'user_parent',return_value=controller['namespaces']['user']):
            for ordinal in range(budget['successful_live_joins']):
                self.assertEqual(C.live_join(state,9,controller,bootstrap,exe),tuple([state['payload_credentials'][0],state['payload_before'][0]['start']]+state['payload_credentials'][1:]))
        self.assertEqual(bootstrap,before);self.assertEqual(state['lineage_next'],1461)
        self.assertEqual([r['ordinal'] for r in state['lineage_checks']],list(range(1461)))
        self.assertTrue(all(r['join_passed'] for r in state['lineage_checks']))
        self.assertEqual(state['lineage_first']['ordinal'],0);self.assertEqual(state['lineage_last']['ordinal'],1460)
        evidence=json.loads(C.lineage_evidence(state,budget));self.assertFalse(evidence['all_raw_observations_retained'])
        self.assertNotIn('lineage_originals',state)
        for label in ('first','last'):
            sample=evidence[label];rows=[{'name':k,'sha256':C.ns.sha(bytes.fromhex(v)),'size_bytes':len(bytes.fromhex(v))} for k,v in sorted(sample['originals'].items())]
            self.assertEqual(C.ns.sha(C.ns.encode(rows)),evidence['checks'][sample['ordinal']]['originals_sha256'])

    def test_lineage_count_exhaustion_refuses_before_proc(self):
        state={**C.lineage_state(),'lineage_next':C.MAX_LIVE_JOINS}
        with mock.patch.object(C.ns,'ancestry') as read:
            with self.assertRaisesRegex(RuntimeError,'LINEAGE_COUNT_BOUND'):C.live_join(state,9,{}, {},('x',[]))
            read.assert_not_called()
        self.assertEqual(state['lineage_next'],C.MAX_LIVE_JOINS)

    def test_failed_partial_check_is_consumed_and_sampled(self):
        state={**C.lineage_state(),'payload_pidfd':7,'payload_before':[{'start':33}],'wrapper':{},'payload_credentials':[13,1,2]}
        def partial(pid,wrapper,local,label):local[label+'/partial']=b'public fixture';raise RuntimeError('READ_FAILED')
        with mock.patch.object(C.select,'select',return_value=([],[],[])),mock.patch.object(C.original,'exited',return_value=False),mock.patch.object(C.ns,'ancestry',partial):
            with self.assertRaisesRegex(RuntimeError,'READ_FAILED'):C.live_join(state,9,{}, {},('x',[]))
        self.assertEqual(state['lineage_next'],1);self.assertFalse(state['lineage_checks'][0]['join_passed']);self.assertEqual(state['lineage_last']['originals'],{'package-current-0000/partial':b'public fixture'})

    def test_sample_oversize_refuses_without_reuse_or_false_check(self):
        state={**C.lineage_state(),'payload_pidfd':7,'payload_before':[{'start':33}],'wrapper':{},'payload_credentials':[13,1,2]}
        def partial(pid,wrapper,local,label):local[label+'/partial']=b'x'*(C.MAX_LIVE_SAMPLE_RAW+1);raise RuntimeError('READ_FAILED')
        with mock.patch.object(C.select,'select',return_value=([],[],[])),mock.patch.object(C.original,'exited',return_value=False),mock.patch.object(C.ns,'ancestry',partial):
            with self.assertRaisesRegex(RuntimeError,'LINEAGE_SAMPLE_BOUND'):C.live_join(state,9,{}, {},('x',[]))
            with self.assertRaisesRegex(RuntimeError,'LINEAGE_INCOMPLETE'):C.live_join(state,9,{}, {},('x',[]))
        self.assertEqual(state['lineage_next'],1);self.assertEqual(state['lineage_checks'],[])

    def test_noninteger_lineage_ordinal_refuses(self):
        for ordinal in (True,False,1.0,-1):
            with self.subTest(ordinal=ordinal):
                with self.assertRaisesRegex(RuntimeError,'LINEAGE_COUNT_BOUND'):C.live_join({**C.lineage_state(),'lineage_next':ordinal},9,{}, {},('x',[]))

    def test_checked_cost_formula_keeps_sixty_second_hold(self):
        v=C.live_budget(PLAN)
        self.assertEqual((v['frames'],v['reply_packets'],v['writer_effects']),(232,240,57))
        self.assertEqual(v['full_selection_scans'],939)
        source=Path(I['candidate']['path']).read_text();self.assertIn('end=started+60',source)
        # A selected host timing is a sample, not a deterministic upper bound.
        self.assertGreater(v['full_selection_scans']*0.151,60)


def main(inputs,candidate,payload):
    global C,P,I,PLAN
    C=candidate;P=payload;I=inputs;raw=Path(inputs['plan']['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=inputs['plan']['sha256']:raise RuntimeError('PLAN_DRIFT')
    PLAN=json.loads(raw);result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    print(json.dumps({'result':'PASS' if result.wasSuccessful() else 'FAIL','checks':result.testsRun,'effect_runs':0,'namespace_runs':0,'package_writes':0,'host_qualified':False},sort_keys=True))
    return 0 if result.wasSuccessful() else 1
