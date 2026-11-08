"""Static/pure tests; execute is exercised only with every effect dependency replaced."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
import types
import unittest
from unittest import mock
C=W=D=INPUTS=PLAN=None

class Tests(unittest.TestCase):
    def test_actual_selected_plan_exact_55_leaves(self):
        selected,raw,leaves,frames=C.validate_plan(PLAN)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),PLAN['manifest_sha256']);self.assertEqual(len(leaves),55)
        self.assertEqual(set(leaves),set(W.SCHEDULE));manifest=json.loads(leaves['manifest.json']);self.assertEqual(len(manifest['files']),54)
        for row in manifest['files']:
            name=row['path'].removeprefix(C.model.PACKAGE+'/');self.assertEqual(row['sha256'],hashlib.sha256(leaves[name]).hexdigest())
        self.assertEqual(selected['begin_pins']['mapper'],manifest['source_manifest_binding']['sha256'])
        self.assertEqual(C.preflight(PLAN)['effect_executed'],False)

    def test_plan_copy_leaf_and_digest_mutation_refuse(self):
        for kind in ('copy','leaf','digest','scratch','evidence'):
            p=copy.deepcopy(PLAN)
            if kind=='copy':p['copies'][0]['raw_hex']='00'
            elif kind=='leaf':p['leaves']['manifest.json']='00'
            elif kind=='digest':p['manifest_sha256']='f'*64
            else:p[kind]+='-wrong'
            with self.assertRaises(Exception):C.validate_plan(p)

    def test_repeated_effect_preflight_refuses(self):
        with mock.patch.object(C.os.path,'lexists',return_value=True):
            with self.assertRaises(RuntimeError):C.preflight(PLAN)

    def test_real_writer_single_thread_guard_precedes_umask_or_mkdir(self):
        obj=object.__new__(W.PackageWriter)
        with mock.patch.object(W.threading,'active_count',return_value=2),mock.patch.object(W.os,'umask') as mask,mock.patch.object(W.os,'mkdir') as mkdir:
            with self.assertRaises(W.Refusal):obj._mkdir(-1,'never')
            mask.assert_not_called();mkdir.assert_not_called()

    def test_fixture_single_thread_refuses_before_tree_claim(self):
        with mock.patch.object(C.threading,'active_count',return_value=2),mock.patch.object(C,'HeldCanonicalDirectory') as held:
            with self.assertRaises(RuntimeError):C.OwnedTree(C.SCRATCH)
            held.assert_not_called()

    def test_real_writer_attachment_failure_precedes_leaf_open(self):
        obj=object.__new__(W.PackageWriter);obj.closed=False;obj.unknown=False;obj.finished=False;obj.index=0;obj.total=0
        obj._scan=mock.Mock(side_effect=W.Refusal('selected-fixture-detached'))
        with mock.patch.object(W.os,'open') as opened:
            with self.assertRaises(W.Refusal):obj.emit(W.SCHEDULE[0],b'fixture')
            opened.assert_not_called();self.assertTrue(obj.unknown)

    def test_deadline_check_refuses_expired_synchronous_return(self):
        with mock.patch.object(C,'time',types.SimpleNamespace(monotonic=lambda:10)):
            C.deadline(11)
            for end in (10,9):
                with self.assertRaises(RuntimeError):C.deadline(end)
        tree=ast.parse(Path(INPUTS['candidate']['path']).read_bytes())
        exchange=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='exchange')
        calls=sorted((n.lineno,n.col_offset,ast.unparse(n.func)) for n in ast.walk(exchange) if isinstance(n,ast.Call));names=[x[2] for x in calls]
        begin=names.index('server.prepare_one');send=names.index('server.send_pending')
        self.assertIn('deadline',names[begin+1:send])

    def test_owned_teardown_attempts_each_once_and_retains_uncertainty(self):
        obj=object.__new__(C.OwnedTree);obj.closed=False;obj.uncertain=False;obj.fds={'':111,'child':222};obj.parent=mock.Mock();obj.parent.close.side_effect=RuntimeError('synthetic')
        calls=[]
        def close(fd):
            calls.append(fd)
            if fd==222:raise OSError('synthetic')
        with mock.patch.object(C.os,'close',side_effect=close):obj.close();obj.close()
        self.assertEqual(calls,[222,111]);obj.parent.close.assert_called_once();self.assertTrue(obj.uncertain)

    def test_parent_detachment_refuses_before_path_scan(self):
        obj=object.__new__(C.OwnedTree);obj.parent=types.SimpleNamespace(attached=lambda:False);obj.fds={'':111}
        with mock.patch.object(C.os,'lstat') as stat:
            with self.assertRaises(RuntimeError):obj.attached()
            stat.assert_not_called()

    def test_effect_body_has_no_spawn_thread_namespace_or_native(self):
        tree=ast.parse(Path(INPUTS['candidate']['path']).read_bytes())
        for n in ast.walk(tree):
            if isinstance(n,ast.Call):self.assertNotIn(ast.unparse(n.func).split('.')[-1],('Popen','fork','execve','Thread','start','system','run_native','spawn_standin'))
        text=ast.unparse(tree);self.assertIn('server.prepare_one()',text);self.assertIn('server.send_pending()',text)
        self.assertIn('server.writer._scan()',text);self.assertIn('runner.read_exact',text)


    def test_dispatch_loader_drift_after_precheck_never_compiles(self):
        good=b'marker=1';bad=b'marker=2'
        row={'path':'/synthetic/loader','size_bytes':len(good),'sha256':hashlib.sha256(good).hexdigest()}
        with mock.patch.object(D.Path,'read_bytes',side_effect=[good,bad]),mock.patch.object(D,'compile',create=True) as compiled:
            D.verified_read(row)
            with self.assertRaisesRegex(RuntimeError,'SELECTED_DRIFT'):D.load_loader({'loader':row})
            compiled.assert_not_called()

    def test_dispatch_plan_drift_after_precheck_never_parses(self):
        good=b'{"value":1}';bad=b'{"value":2}'
        row={'path':'/synthetic/plan','size_bytes':len(good),'sha256':hashlib.sha256(good).hexdigest()}
        with mock.patch.object(D.Path,'read_bytes',side_effect=[good,bad]),mock.patch.object(D.json,'loads') as parsed:
            D.verified_read(row)
            with self.assertRaisesRegex(RuntimeError,'SELECTED_DRIFT'):D.load_plan({'plan':row})
            parsed.assert_not_called()

    def test_dispatch_compiles_exact_held_bytes_without_second_read(self):
        good=b'marker=123';row={'path':'/synthetic/loader','size_bytes':len(good),'sha256':hashlib.sha256(good).hexdigest()}
        name='selected_local_loader_0013';saved=sys.modules.pop(name,None)
        try:
            with mock.patch.object(D.Path,'read_bytes',side_effect=[good,b'raise RuntimeError()']) as read:
                loaded=D.load_loader({'loader':row});self.assertEqual(loaded.marker,123);self.assertEqual(read.call_count,1)
        finally:
            sys.modules.pop(name,None)
            if saved is not None:sys.modules[name]=saved

    def test_dispatch_postguard_failure_emits_no_pass(self):
        fake=types.SimpleNamespace(load=lambda i:types.SimpleNamespace(execute=lambda p:{'result':'PASS'}))
        with mock.patch.object(D.sys,'argv',['dispatch','--execute-once']),mock.patch.object(D,'check',side_effect=[None,RuntimeError('postguard')]),mock.patch.object(D,'load_loader',return_value=fake),mock.patch.object(D,'load_plan',return_value={}),mock.patch.object(D,'print',create=True) as printed:
            with self.assertRaisesRegex(RuntimeError,'postguard'):D.run({})
            printed.assert_not_called()

    def mocked_execute(self,close_uncertain=False,readback_failure=False,body_failure=False):
        from contextlib import ExitStack
        events=[];documents={}
        class Tree:
            def __init__(self,path):self.path=path;self.uncertain=False
            def write(self,name,raw):
                events.append(('write',name));documents[name]=json.loads(raw)
            def attached(self):events.append(('attached',self.path))
            def snapshot(self):events.append(('snapshot',self.path));return {'selected':'seal'}
            def close(self):
                events.append(('close',self.path))
                if self.path==C.EVIDENCE:self.uncertain=close_uncertain
        writer=types.SimpleNamespace(finished=True,index=55,unknown=False,_scan=lambda:None)
        server=types.SimpleNamespace(transport_peer=(1,2,3,4),activate=lambda:None,writer=writer,finished=True,cleanup_uncertain=False,close=lambda:events.append(('server-close',)),abort=lambda:events.append(('abort',)))
        sock=types.SimpleNamespace(close=lambda:events.append(('socket-close',)))
        comp=types.SimpleNamespace(peer=(1,2,3,4),observe_synthetic=lambda f:b'activation')
        def verify(seal):
            events.append(('readback',));self.assertIn(('close',C.EVIDENCE),events)
            if readback_failure:raise RuntimeError('READBACK_UNKNOWN')
        with ExitStack() as stack:
            for obj,key,value in [(C,'preflight',lambda p:None),(C,'validate_plan',lambda p:({'attempt_id':'fixture'},b'{}',{},[])),(C,'OwnedTree',Tree),(C.model,'Composition',lambda *a:comp),(C,'LocalWriterMediator',lambda *a,**k:server),(C.transport,'socket_pair',lambda:(sock,sock)),(C.transport,'send_frame',lambda *a:None),(C.transport,'recv_frame',lambda *a:b'activation'),(C.wire,'schedule',lambda:()),(C,'verify_closed_evidence',verify)]:stack.enter_context(mock.patch.object(obj,key,value))
            if body_failure:server.activate=lambda:(_ for _ in ()).throw(ValueError('primary'))
            try:result=C.execute({'copies':[],'manifest_sha256':'a'*64})
            except BaseException as exc:result=exc
        return result,events,documents

    def test_evidence_close_uncertainty_cannot_leave_pass(self):
        result,events,docs=self.mocked_execute(close_uncertain=True)
        self.assertIsInstance(result,RuntimeError);self.assertEqual(docs['terminal.json']['result'],'UNKNOWN')
        self.assertNotIn(('readback',),events);self.assertEqual(events.count(('close',C.EVIDENCE)),1)
        self.assertFalse(any(v.get('result')=='PASS' for v in docs.values()))

    def test_pass_only_after_evidence_close_and_postclose_readback(self):
        result,events,docs=self.mocked_execute()
        self.assertEqual(result['result'],'PASS');self.assertTrue(result['evidence_postclose_verified'])
        self.assertLess(events.index(('close',C.EVIDENCE)),events.index(('readback',)))
        self.assertEqual(docs['terminal.json']['result'],'UNKNOWN')

    def test_postclose_readback_failure_cannot_leave_pass(self):
        result,events,docs=self.mocked_execute(readback_failure=True)
        self.assertIsInstance(result,RuntimeError);self.assertEqual(docs['terminal.json']['result'],'UNKNOWN')
        self.assertEqual(events.count(('close',C.EVIDENCE)),1)

    def test_primary_failure_retained_with_close_uncertainty(self):
        result,events,docs=self.mocked_execute(close_uncertain=True,body_failure=True)
        self.assertIsInstance(result,RuntimeError);self.assertEqual(docs['terminal.json']['primary_type'],'ValueError')
        self.assertEqual(docs['terminal.json']['result'],'UNKNOWN');self.assertIn(('server-close',),events)

    def test_held_ancestor_close_continues_once_after_failure(self):
        held=object.__new__(C.HeldCanonicalDirectory);held.fds=[111,222];held.records=[{},{}];calls=[]
        def close(fd):
            calls.append(fd)
            if fd==222:raise OSError('synthetic')
        with mock.patch.object(C.os,'close',side_effect=close):
            self.assertTrue(C.close_held(held));self.assertFalse(C.close_held(held))
        self.assertEqual(calls,[222,111]);self.assertEqual(held.fds,[])


def main(inputs,candidate,dispatch):
    global C,W,D,INPUTS,PLAN
    C=candidate;W=C.writer;D=dispatch;INPUTS=inputs
    PLAN=D.load_plan(inputs)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    print(json.dumps({'result':'PASS' if result.wasSuccessful() else 'FAIL','checks':result.testsRun,'static_only':True,'effect_runs':0,'package_writes':0,'namespace_runs':0,'host_qualified':False},sort_keys=True))
    return 0 if result.wasSuccessful() else 1
