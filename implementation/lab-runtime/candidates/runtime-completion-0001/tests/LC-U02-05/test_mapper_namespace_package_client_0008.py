"""Real owned local socketpair client tests; synthetic parent, no writer/launch."""
import ast
import array
import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import sys
import threading
import time
import types
import unittest

C=None
B=None
F=None
M=None
N=None
W=None
INPUTS=None


class RuntimeTests(unittest.TestCase):
    def pair(self,scenario='normal',namespace=False):
        s,_=F.manifest();raw=N.encode(s);sha=M.digest(raw);frames=F.frames(s,sha)
        parent,child=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET|socket.SOCK_CLOEXEC)
        for sock in (parent,child):sock.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1);sock.settimeout(1)
        self.addCleanup(parent.close);self.addCleanup(child.close)
        client=(C.Client if namespace else C.LocalFixtureClient)(child,selection_raw=raw,selection_sha256=sha,
                                                               bootstrap_frames=frames,attempt_started=time.monotonic())
        self.addCleanup(client.close)
        model=M.Composition(raw,sha);activation=model.observe_synthetic(frames)
        state={'errors':[],'sent':[],'done':False};fixture_fds=[]
        def receive():
            packet,anc,flags,_=parent.recvmsg(W.FRAME_MAX,socket.CMSG_SPACE(12),socket.MSG_CMSG_CLOEXEC)
            if not packet:return None
            if flags & (socket.MSG_TRUNC|socket.MSG_CTRUNC) or len(anc)!=1 or anc[0][:2]!=(socket.SOL_SOCKET,socket.SCM_CREDENTIALS) or struct.unpack('iii',anc[0][2])!=(os.getpid(),os.getuid(),os.getgid()):
                raise RuntimeError('FIXTURE_KERNEL_CREDENTIALS')
            return packet
        def body():
            try:
                send=activation+b' ' if scenario=='activate-drift' else activation
                parent.send(send)
                ack=receive()
                if ack is None:return
                model.acknowledge_activation_synthetic(N.decode(ack),peer=model.peer)
                while model.phase=='PACKAGE':
                    request=receive()
                    if request is None:break
                    a=model.receive_synthetic(request,peer=model.peer,current_selection_sha=sha)
                    output=b'x'*(W.CHUNK_MAX+7) if a.get('verb') in ('SEAL','COLD_READ') else None
                    prepared=model.prepare_reply_synthetic(F.completion(a),output=output)
                    sent=[]
                    for index,packet in enumerate(prepared['packets']):
                        original=packet
                        if scenario!='normal':
                            v=W.decode(packet)
                            if scenario=='wrong-completion':v['completion_sha256']='f'*64;packet=W.encode(v)
                            elif scenario=='wrong-host-peer':v['host_peer'][0]+=1;packet=W.encode(v)
                            elif scenario=='wrong-child-peer':v['child_peer'][0]=1;packet=W.encode(v)
                            elif scenario=='wrong-ordinal':v['ordinal']+=1;packet=W.encode(v)
                            elif scenario=='wrong-selection':v['selection_sha256']='f'*64;packet=W.encode(v)
                            elif scenario=='noncanonical':packet+=b' '
                            elif scenario=='oversized':packet=b'x'*(W.FRAME_MAX+1)
                            elif scenario=='data-digest' and a.get('verb')=='SEAL' and v['payload']['kind']=='DATA_BEGIN':v['payload']['sha256']='f'*64;packet=W.encode(v)
                        if scenario=='rights':
                            fd=os.open('/dev/null',os.O_RDONLY|os.O_CLOEXEC);fixture_fds.append(fd)
                            parent.sendmsg([packet],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[fd,fd]))]);return
                        count=parent.send(packet)
                        if count!=len(packet):raise RuntimeError('FIXTURE_PARTIAL_SEND')
                        sent.append(bytes(packet));state['sent'].append(hashlib.sha256(packet).hexdigest())
                        if packet!=original and scenario!='data-digest':return
                    observed=F.send_observation(prepared);observed['sent_packets']=tuple(sent)
                    model.acknowledge_reply_synthetic(observed,current_selection_sha=sha)
                state['done']=model.phase=='WAIT_CHILD_EXIT'
            except BaseException as exc:state['errors'].append(type(exc).__name__)
            finally:
                for fd in fixture_fds:os.close(fd)
                parent.close()
        thread=threading.Thread(target=body);thread.start()
        def clean():
            child.close();thread.join(3)
            if thread.is_alive():raise RuntimeError('FIXTURE_THREAD_NOT_REAPED')
        self.addCleanup(clean)
        return client,model,state,thread

    def test_real_activation_and_complete_61_action_client(self):
        c,m,state,thread=self.pair();self.assertFalse(c.activated)
        result=c.activate();self.assertFalse(result['authority']);self.assertTrue(c.activated)
        manifest_sha=None
        for verb,target in W.schedule():
            if verb=='BEGIN':c.begin(c.begin_pins['mapper'],c.package_path)
            elif verb=='SEAL':self.assertEqual(len(c.seal(b'{}')),W.CHUNK_MAX+7)
            elif verb=='EMIT':
                raw=b'{"synthetic":true}';c.emit(target,raw)
                if target=='manifest.json':manifest_sha=W.sha(raw)
            elif verb=='COLD_READ':self.assertEqual(len(c.cold([c.package_path+'/'+x for x in ('semantic','governance','request.json')])),W.CHUNK_MAX+7)
            else:c.finish({'path':c.package_path+'/manifest.json','sha256':manifest_sha})
        thread.join(3);self.assertFalse(thread.is_alive());self.assertEqual(state['errors'],[])
        self.assertEqual(c.step,61);self.assertTrue(state['done']);self.assertEqual(m.protocol.step,61)
        self.assertEqual(len([x for x in m.retained if x['kind']=='held-leaf']),55)
        self.assertEqual(len(c.replies),m.protocol.ordinal)

    def test_namespace_type_does_not_accept_positive_local_peer(self):
        c,_,_,thread=self.pair(namespace=True)
        with self.assertRaises(C.Refusal):c.activate()
        self.assertFalse(c.activated);self.assertTrue(c.failed)
        c.close();thread.join(3)

    def test_package_call_before_activation_sends_nothing(self):
        c,_,_,_=self.pair()
        with self.assertRaises(C.Refusal):c.begin(c.begin_pins['mapper'],c.package_path)
        self.assertTrue(c.failed);self.assertEqual(c.step,0)

    def test_activate_drift_refuses(self):
        c,_,_,_=self.pair('activate-drift')
        with self.assertRaises(C.Refusal):c.activate()
        self.assertFalse(c.activated)

    def test_reactivation_refuses_without_package(self):
        c,_,_,_=self.pair();c.activate()
        with self.assertRaises(C.Refusal):c.activate()
        self.assertTrue(c.failed)

    def test_response_subject_mutations_refuse(self):
        for mode in ('wrong-completion','wrong-host-peer','wrong-child-peer','wrong-ordinal','wrong-selection','noncanonical','oversized'):
            with self.subTest(mode=mode):
                c,_,_,thread=self.pair(mode);c.activate()
                with self.assertRaises(C.Refusal):c.begin(c.begin_pins['mapper'],c.package_path)
                self.assertTrue(c.failed);self.assertEqual(c.step,0);c.close();thread.join(3)

    def test_real_passed_rights_are_closed_and_refused(self):
        c,_,_,thread=self.pair('rights');c.activate()
        before=len(os.listdir('/proc/self/fd'))
        with self.assertRaises(C.Refusal):c.begin(c.begin_pins['mapper'],c.package_path)
        thread.join(3)
        self.assertLessEqual(len(os.listdir('/proc/self/fd')),before)
        self.assertFalse(c.cleanup_uncertain);self.assertTrue(c.failed)

    def test_data_digest_substitution_refuses(self):
        c,_,_,_=self.pair('data-digest');c.activate();c.begin(c.begin_pins['mapper'],c.package_path)
        with self.assertRaises(C.Refusal):c.seal(b'{}')
        self.assertTrue(c.failed);self.assertEqual(c.step,1)

    def test_original_deadline_expired_constructor_closes_owned_socket(self):
        s,_=F.manifest();raw=N.encode(s);sha=M.digest(raw);a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        try:
            with self.assertRaises(C.Refusal):C.LocalFixtureClient(b,selection_raw=raw,selection_sha256=sha,bootstrap_frames=F.frames(s,sha),attempt_started=time.monotonic()-61)
            self.assertEqual(b.fileno(),-1)
        finally:a.close();b.close()

    def test_bootstrap_mutation_closes_before_activation(self):
        s,_=F.manifest();raw=N.encode(s);sha=M.digest(raw);frames=F.frames(s,sha);frames[0]+=b' '
        a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        try:
            with self.assertRaises(C.Refusal):C.LocalFixtureClient(b,selection_raw=raw,selection_sha256=sha,bootstrap_frames=frames,attempt_started=time.monotonic())
            self.assertEqual(b.fileno(),-1)
        finally:a.close();b.close()

    def test_runtime_deadline_does_not_renew_after_activation(self):
        c,_,_,_=self.pair();original=c.deadline;c.activate();self.assertEqual(c.deadline,original)
        c.deadline=time.monotonic()-1
        with self.assertRaises(C.Refusal):c.begin(c.begin_pins['mapper'],c.package_path)
        self.assertEqual(c.step,0)

    def test_fixture_type_cannot_install_builder_bridge_or_fd3(self):
        c,_,_,_=self.pair();c.activate()
        with self.assertRaises(C.Refusal):B.install(c,c.package_path)
        with self.assertRaises(C.Refusal):C.LocalFixtureClient.from_fd3()
        with self.assertRaises(C.Refusal):B.selected()

    def test_native_and_protected_bridge_paths_are_fixed_refusals(self):
        for fun in (B.run_native,B.read,B.verify_inputs):
            with self.assertRaises(C.Refusal):fun('anything')

    def test_fixed_source_has_no_launch_or_writer_import(self):
        for key in ('client','bridge'):
            tree=ast.parse(Path(INPUTS[key]['path']).read_bytes())
            for n in ast.walk(tree):
                if isinstance(n,ast.Call):self.assertNotIn(ast.unparse(n.func).split('.')[-1],('fork','execve','Popen','PackageWriter','Mediator','mkdir','write_bytes'))
        tree=ast.parse(Path(INPUTS['client']['path']).read_bytes())
        self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr=='sendmsg' for n in ast.walk(tree)))


def main(inputs):
    global C,B,F,M,N,W,INPUTS
    INPUTS=inputs
    def checked(row):
        raw=Path(row['path']).read_bytes()
        if len(raw)!=row['size_bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:raise RuntimeError('INPUT_DRIFT')
        return raw
    pkg=types.ModuleType('selected_runtime_0008');pkg.__path__=[];sys.modules[pkg.__name__]=pkg
    def load(name,row):
        mod=types.ModuleType(pkg.__name__+'.'+name);mod.__package__=pkg.__name__;sys.modules[mod.__name__]=mod
        exec(compile(checked(row),row['path'],'exec'),mod.__dict__);setattr(pkg,name,mod);return mod
    N=load('mapper_namespace_probe_common_0004',inputs['common']);W=load('mapper_package_ipc_model_0004',inputs['wire'])
    M=load('mapper_namespace_package_model_0007',inputs['model'])
    C=load('mapper_namespace_package_client_0008',inputs['client']);B=load('mapper_namespace_package_bridge_0008',inputs['bridge'])
    F=load('selected_fixture_helpers',inputs['fixture_helpers']);F.M=M;F.N=N;F.W=W
    F.HISTORY=json.loads(checked(inputs['namespace_record']))
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    print(json.dumps({'result':'PASS' if result.wasSuccessful() else 'FAIL','checks':result.testsRun,
                     'socketpair_only':True,'namespace_executions':0,'package_writes':0,'native_executions':0,'protected_reads':0,'host_qualified':False,'cleanup':'clean'},sort_keys=True))
    return 0 if result.wasSuccessful() else 1
