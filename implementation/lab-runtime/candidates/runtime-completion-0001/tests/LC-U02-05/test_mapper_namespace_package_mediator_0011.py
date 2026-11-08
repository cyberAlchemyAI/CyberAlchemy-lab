"""Local sockets + recording writer only; never instantiate PackageWriter."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import threading
import time
import types
import unittest
N=W=M=C=R=P=TR=F=A=INPUTS=None

class RecordedWriter:
    def __init__(self,owner):self.owner=owner;self.index=0;self.hashes={};self.unknown=False;self.closed=False;self.finished=False;self.close_errors=0;self.total=0
    def _scan(self):
        if self.owner.mode=='detach' and self.index:raise RuntimeError('FIXTURE_DETACH')
    def emit(self,name,raw):
        self.owner.events.append(('write',name));self.index+=1;self.hashes[name]=W.sha(raw);self.total+=len(raw)
        if self.owner.mode=='writer-error':raise RuntimeError('FIXTURE_WRITE_UNKNOWN')
        if self.owner.mode=='source-drift':self.owner.drift=True
        receipt={'path':name,'sha256':W.sha(raw),'size':len(raw),'durable_observed':True}
        if self.owner.mode=='false-receipt':receipt['durable_observed']=1
        return receipt
    def finish(self):
        self.finished=True;self.owner.events.append(('finish',self.index))
        return {'leaf_count':self.index,'manifest_row_count':54,'total_bytes':self.total,'scratch_retained':True,'package_writer_complete':True}
    def close(self):self.closed=True


def selection():
    s,_=F.manifest();rows={r['id']:r for r in s['files']}
    for role,path in R.BOOTSTRAP_PATHS.items():
        rows[s['roles'][role]]['child_path']=path;rows[s['roles'][role]]['host_path']=s['scratch_root']+'/control'+path[len('/work/control'):]
    s['files'].append({'id':'composition_model','view':'control','host_path':s['scratch_root']+'/control/mapper_namespace_package_model_0007.py','child_path':R.MODEL_PATH,'sha256':'a'*64,'size_bytes':32})
    return s

class Tests(unittest.TestCase):
    def setup_pair(self,mode='normal',wrongpeer=False):
        s=selection();raw=N.encode(s);sha=W.sha(raw);frames=F.frames(s,sha);model=M.Composition(raw,sha);model.observe_synthetic(frames)
        left,right=TR.socket_pair();self.addCleanup(left.close);self.addCleanup(right.close)
        class FixtureMediator(P.Mediator):
            def __init__(self,*a,**kw):self.events=[];self.mode=mode;self.drift=False;super().__init__(*a,**kw)
            def _transport_peer(self):return (os.getpid(),TR.process_start(os.getpid()),os.getuid(),os.getgid())
            def _guard(self):
                if self.drift:raise RuntimeError('FIXTURE_SELECTED_SOURCE_DRIFT')
                if self.writer is not None:self.writer._scan()
            def _open_writer(self):self.events.append(('begin',None));return RecordedWriter(self)
        peer=model.peer
        if wrongpeer:peer=(peer[0]+1,*peer[1:])
        binding={'path':s['scratch_root']+'/control/selection.json','sha256':sha,'size_bytes':len(raw)}
        server=FixtureMediator(left,selection_raw=raw,selection_sha256=sha,selection_binding=binding,bootstrap_frames=frames,host_peer=peer,attempt_started=time.monotonic())
        client=C.LocalFixtureClient(right,selection_raw=raw,selection_sha256=sha,bootstrap_frames=frames,attempt_started=time.monotonic())
        self.addCleanup(server.close);self.addCleanup(client.close)
        return server,client

    def run_case(self,mode='normal'):
        server,client=self.setup_pair(mode);fail=[];states=[]
        def serve():
            try:
                server.activate()
                while not server.finished:
                    before=server.model.protocol.step;a=server.prepare_one()
                    self.assertEqual(server.model.protocol.step,before)
                    states.append((a['verb'],before))
                    if mode=='lost-ack' and a['verb']=='EMIT':
                        client.sock.shutdown(socket.SHUT_RDWR);client.close()
                    if mode=='deadline' and a['verb']=='EMIT':server.deadline=time.monotonic()-1
                    server.send_pending();server.events.append(('sent',a['verb']))
            except BaseException as e:fail.append(type(e).__name__)
        thread=threading.Thread(target=serve);thread.start()
        def clean():client.close();server.close();thread.join(3);self.assertFalse(thread.is_alive())
        self.addCleanup(clean)
        caught=False
        try:
            client.activate()
            for verb,target in W.schedule():
                if verb=='BEGIN':client.begin(client.begin_pins['mapper'],client.package_path)
                elif verb=='SEAL':
                    value={'semantic':[],'governance':[]};value[target]=[{'fixture':i} for i in range(25)]
                    output=client.seal(json.dumps(value,indent=2).encode());self.assertEqual(len(json.loads(output)[target]),25)
                elif verb=='EMIT':client.emit(target,b'{"fixture":true}')
                elif verb=='COLD_READ':
                    output=client.cold([client.package_path+'/'+x for x in ('semantic','governance','request.json')]);self.assertEqual(json.loads(output)['cut']['semantic_cursor'],25)
                else:client.finish({'path':client.package_path+'/manifest.json','sha256':W.sha(b'{"fixture":true}')})
        except C.Refusal:caught=True
        client.close();thread.join(3);self.assertFalse(thread.is_alive())
        return server,fail,states,caught

    def test_all_61_actions_local_codec_with_recording_writer(self):
        s,fail,states,caught=self.run_case();self.assertFalse(caught);self.assertEqual(fail,[])
        self.assertTrue(s.finished);self.assertEqual(s.model.phase,'WAIT_CHILD_EXIT');self.assertEqual(s.writer.index,55)
        self.assertEqual(s.writer.hashes.keys(),{target for verb,target in W.schedule() if verb=='EMIT'})
        self.assertEqual(len([r for r in s.records if r.get('writer_receipt',{} ) and r['writer_receipt'].get('durable_observed') is True]),55)
        self.assertEqual(s.events[-2:],[('finish',55),('sent','FINISH')])
        self.assertEqual(sum(v is not None for v,_ in states),61)

    def test_failed_writer_never_acknowledges_leaf(self):
        s,fail,_,caught=self.run_case('writer-error');self.assertTrue(caught);self.assertTrue(fail)
        self.assertTrue(s.failed and s.writer.unknown);self.assertEqual(s.writer.index,1)
        self.assertFalse(any(r.get('writer_receipt',{} ) and r['writer_receipt'].get('durable_observed') for r in s.records))

    def test_changed_sources_detach_deadline_and_false_receipt_fence(self):
        for mode in ('source-drift','detach','deadline','false-receipt'):
            with self.subTest(mode=mode):
                s,fail,_,caught=self.run_case(mode);self.assertTrue(caught);self.assertTrue(fail)
                self.assertTrue(s.failed and s.writer.unknown);self.assertEqual(s.writer.index,1)
                self.assertIsNotNone(s.pending);self.assertFalse(s.finished)

    def test_lost_ack_retains_written_leaf_and_cannot_repeat(self):
        s,fail,_,caught=self.run_case('lost-ack');self.assertTrue(caught);self.assertTrue(fail)
        self.assertEqual(s.writer.index,1);self.assertIsNotNone(s.pending['receipt']);self.assertTrue(s.writer.unknown)
        with self.assertRaises(P.Refusal):s.prepare_one()
        self.assertEqual(s.writer.index,1)

    def test_wrong_independent_host_peer_refuses_before_writer(self):
        with self.assertRaises(P.Refusal):self.setup_pair(wrongpeer=True)

    def test_package_before_activation_refuses_without_writer(self):
        s,c=self.setup_pair()
        with self.assertRaises(P.Refusal):s.prepare_one()
        self.assertIsNone(s.writer);self.assertTrue(s.failed)

    def test_wrong_activation_ack_refuses(self):
        s,c=self.setup_pair();fail=[]
        def body():
            try:s.activate()
            except P.Refusal:fail.append(True)
        t=threading.Thread(target=body);t.start();raw,anc,flags,_=c.sock.recvmsg(65536,socket.CMSG_SPACE(12));self.assertEqual(raw,s.activation)
        c.sock.send(N.encode({'schema':'mapper-namespace-package-activation-ack/v1','activation_sha256':'f'*64,'selection_sha256':s.sha}));t.join(3)
        self.assertFalse(t.is_alive());self.assertEqual(fail,[True]);self.assertIsNone(s.writer)

    def test_extra_leaf_and_truncation_refuse_before_write(self):
        for mode in ('extra','truncated'):
            s,c=self.setup_pair();fail=[]
            def body():
                try:s.activate();s.prepare_one()
                except P.Refusal:fail.append(True)
            t=threading.Thread(target=body);t.start();c.activate()
            raw=W.encode(W.envelope(c.attempt_id,c.selection_sha256,0,'EMIT',{'leaf':'extra.json','blob_id':0})) if mode=='extra' else b'x'*65537
            c.sock.send(raw);t.join(3);self.assertFalse(t.is_alive());self.assertEqual(fail,[True]);self.assertIsNone(s.writer)

    def test_source_drift_during_receive_refuses_before_writer(self):
        s,c=self.setup_pair();fail=[];original=TR.recv_frame
        def receive(endpoint,peer):
            raw=original(endpoint,peer)
            if W.decode(raw).get('verb')=='BEGIN':s.drift=True
            return raw
        TR.recv_frame=receive
        def body():
            try:s.activate();s.prepare_one()
            except P.Refusal:fail.append(True)
        thread=threading.Thread(target=body);thread.start()
        try:
            c.activate()
            with self.assertRaises(C.Refusal):c.begin(c.begin_pins['mapper'],c.package_path)
            thread.join(3);self.assertFalse(thread.is_alive());self.assertEqual(fail,[True]);self.assertIsNone(s.writer)
        finally:c.close();s.close();thread.join(3);TR.recv_frame=original

    def test_fixed_writer_adapter_body_and_no_launcher(self):
        tree=ast.parse(Path(INPUTS['mediator']['path']).read_bytes())
        opener=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='_open_writer')
        self.assertTrue(any(isinstance(n,ast.ImportFrom) and n.module=='mapper_package_writer_0001' for n in ast.walk(opener)))
        self.assertTrue(any(isinstance(n,ast.Call) and ast.unparse(n.func)=='PackageWriter' for n in ast.walk(opener)))
        for n in ast.walk(tree):
            if isinstance(n,ast.Call):self.assertNotIn(ast.unparse(n.func).split('.')[-1],('Popen','fork','execve','spawn_standin','sendmsg'))
        src=ast.unparse(tree);self.assertIn('self.writer.emit',src);self.assertIn('self.writer.finish',src)


def main(inputs):
    global N,W,M,C,R,P,TR,F,A,INPUTS
    INPUTS=inputs
    def read(row):
        b=Path(row['path']).read_bytes()
        if len(b)!=row['size_bytes'] or hashlib.sha256(b).hexdigest()!=row['sha256']:raise RuntimeError('DRIFT')
        return b
    pkg=types.ModuleType('selected_parent_runtime');pkg.__path__=[];sys.modules[pkg.__name__]=pkg
    def load(name,key):
        row=inputs[key];m=types.ModuleType(pkg.__name__+'.'+name);m.__package__=pkg.__name__;m.__file__=row['path'];sys.modules[m.__name__]=m
        exec(compile(read(row),row['path'],'exec'),m.__dict__);return m
    N=load('mapper_namespace_probe_common_0004','common');W=load('mapper_package_ipc_model_0004','wire')
    M=load('mapper_namespace_package_model_0007','model');C=load('mapper_namespace_package_client_0008','client')
    R=load('mapper_namespace_package_runner_0010','runner');TR=load('mapper_package_transport_0001','transport')
    P=load('mapper_namespace_package_mediator_0011','mediator');F=load('fixture_helpers','fixture_helpers')
    F.N=N;F.M=M;F.W=W;F.HISTORY=json.loads(read(inputs['namespace_record']))
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    print(json.dumps({'result':'PASS' if result.wasSuccessful() else 'FAIL','checks':result.testsRun,'local_socket_only':True,'recording_writer_only':True,'namespace_runs':0,'package_writes':0,'native_runs':0,'protected_reads':0,'host_qualified':False},sort_keys=True))
    return 0 if result.wasSuccessful() else 1
