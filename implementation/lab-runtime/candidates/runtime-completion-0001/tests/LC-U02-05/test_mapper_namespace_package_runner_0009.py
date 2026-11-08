"""Pure bootstrap transcript and source-bound runner checks. No main/execute."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import socket
import sys
import time
import types
import unittest
R=N=M=W=F=INPUTS=None

class Sock:
    family=socket.AF_UNIX
    def __init__(self):self.timeouts=[];self.closed=False
    def getsockopt(self,*a):return socket.SOCK_SEQPACKET
    def set_inheritable(self,x):self.inherit=x
    def setsockopt(self,*a):pass
    def settimeout(self,x):self.timeouts.append(x)
    def close(self):self.closed=True

class PureTests(unittest.TestCase):
    def setup_case(self,change=None):
        s,_=F.manifest();raw=N.encode(s);sha=M.digest(raw);frames=F.frames(s,sha)
        bodies=[N.decode(x)['body'] for x in frames];peer=copy.deepcopy(bodies[1]['controller_tuple'])
        fake=types.SimpleNamespace(**{k:v for k,v in N.__dict__.items() if not k.startswith('__')})
        recv=[(frames[0],peer),(frames[2],peer)];sent=[];calls=[]
        fake.recv_packet=lambda sock:recv.pop(0)
        def send(sock,packet):
            self.assertEqual(packet,frames[1 if not sent else 3]);sent.append(packet)
        fake.send_packet=send
        def observe(pid,originals,label):calls.append(label);return copy.deepcopy(bodies[1]['claim'])
        fake.proc_observation=observe;fake.census=lambda:copy.deepcopy(bodies[1]['fd_census'])
        fake.pack_child_originals=lambda originals,label,claim:copy.deepcopy(bodies[1 if label=='self-before' else 3]['originals'])
        if change:change(fake,recv,bodies,frames,s)
        return s,raw,sha,frames,fake,recv,sent,calls

    def test_real_selected_frame_logic_keeps_socket_for_activate(self):
        s,raw,sha,frames,n,recv,sent,calls=self.setup_case();sock=Sock();start=time.monotonic()
        actual=R.bootstrap(n,sock,raw,sha,s,start)
        self.assertEqual(actual,frames);self.assertEqual(recv,[]);self.assertEqual(sent,[frames[1],frames[3]])
        self.assertEqual(calls,['self-before','self-after']);self.assertFalse(sock.closed)
        self.assertTrue(all(0<x<=60 for x in sock.timeouts));self.assertFalse(sock.inherit)
        model=M.Composition(raw,sha);activation=model.observe_synthetic(actual)
        self.assertEqual(N.decode(activation)['child_peer'][0],0)
        self.assertGreater(N.decode(activation)['host_peer'][0],0)

    def test_positive_child_visible_pid_refuses_before_observation(self):
        def change(n,recv,*a):recv[0]=(recv[0][0],(123,1000,1000))
        s,raw,sha,_,n,_,sent,calls=self.setup_case(change)
        with self.assertRaises(RuntimeError):R.bootstrap(n,Sock(),raw,sha,s,time.monotonic())
        self.assertEqual(sent,[]);self.assertEqual(calls,[])

    def test_second_peer_drift_refuses_receipt(self):
        def change(n,recv,*a):recv[1]=(recv[1][0],(0,1001,1000))
        s,raw,sha,_,n,_,sent,_=self.setup_case(change)
        with self.assertRaises(RuntimeError):R.bootstrap(n,Sock(),raw,sha,s,time.monotonic())
        self.assertEqual(len(sent),1)

    def test_current_self_drift_refuses_receipt(self):
        def change(n,*a):
            old=n.proc_observation
            def observe(pid,originals,label):
                v=old(pid,originals,label)
                if label=='self-after':v['start']+=1
                return v
            n.proc_observation=observe
        s,raw,sha,_,n,_,sent,_=self.setup_case(change)
        with self.assertRaises(RuntimeError):R.bootstrap(n,Sock(),raw,sha,s,time.monotonic())
        self.assertEqual(len(sent),1)

    def test_wrong_nonce_and_nonpositive_start_refuse(self):
        for mode in ('nonce','start'):
            def change(n,recv,bodies,frames,s):
                if mode=='nonce':s['nonce']='f'*64
                else:
                    b=copy.deepcopy(bodies[0]);b['controller_start']=True
                    recv[0]=(N.frame(0,s['nonce'],M.digest(N.encode(s)),None,b),recv[0][1])
            s,raw,sha,_,n,_,sent,_=self.setup_case(change)
            with self.assertRaises(Exception):R.bootstrap(n,Sock(),raw,sha,s,time.monotonic())
            self.assertEqual(sent,[])

    def test_deadline_and_bool_start_refuse_without_receive(self):
        for start in (True,time.monotonic()-61,float('nan')):
            s,raw,sha,_,n,recv,sent,_=self.setup_case()
            with self.assertRaises(RuntimeError):R.bootstrap(n,Sock(),raw,sha,s,start)
            self.assertEqual(len(recv),2);self.assertEqual(sent,[])

    def test_selected_model_extra_row_and_no_alias(self):
        s,_=F.manifest();r=copy.deepcopy(s['files'][0]);r.update(id='composition_model',view='control',child_path=R.MODEL_PATH,host_path=s['scratch_root']+'/control/mapper_namespace_package_model_0007.py')
        s['files'].append(r);rows,child=R.role_inventory(s);self.assertIn('composition_model',rows)
        self.assertFalse(any(x['view']=='host-only' for x in child))
        for mode in ('path','view','role'):
            v=copy.deepcopy(s)
            if mode=='path':v['files'][-1]['child_path']='/work/control/wrong'
            elif mode=='view':v['files'][-1]['view']='host-only'
            else:v['roles']['namespace_runner']='composition_model'
            with self.assertRaises(RuntimeError):R.role_inventory(v)

    def test_aggregate_closure_bound_refuses(self):
        s,_=F.manifest();s['files'].append({'id':'composition_model','view':'control','child_path':R.MODEL_PATH,'size_bytes':257*1024*1024})
        with self.assertRaises(RuntimeError):R.role_inventory(s)

    def test_exact_selected_source_reader_drift_and_bound(self):
        row=INPUTS['runner'];self.assertEqual(hashlib.sha256(R.read_exact(row['path'],row['sha256'],row['size_bytes'])).hexdigest(),row['sha256'])
        for sha,size in [('f'*64,row['size_bytes']),(row['sha256'],True),(row['sha256'],row['size_bytes']+1)]:
            with self.assertRaises(RuntimeError):R.read_exact(row['path'],sha,size)

    def test_module_collision_refuses_before_code(self):
        name='__reviewed_runner_collision';sys.modules[name]=types.ModuleType(name)
        try:
            with self.assertRaises(RuntimeError):R.load_module(name,b'raise Exception("EXECUTED")','/not-loaded')
        finally:del sys.modules[name]

    def test_static_fixed_handoff_order_and_no_launcher(self):
        tree=ast.parse(Path(INPUTS['runner']['path']).read_bytes());execute=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='execute')
        calls=sorted((n.lineno,n.col_offset,ast.unparse(n.func)) for n in ast.walk(execute) if isinstance(n,ast.Call))
        names=[x[2] for x in calls]
        for left,right in [('adapter.verify_postimage','bootstrap'),('bootstrap','client.Client'),('client.Client','c.activate'),('c.activate','bridge.install'),('bridge.install','build.build')]:
            self.assertLess(names.index(left),names.index(right))
        for n in ast.walk(tree):
            if isinstance(n,ast.Call):self.assertNotIn(ast.unparse(n.func).split('.')[-1],('Popen','fork','execve','sendmsg','dup2','PackageWriter','Mediator'))
        boot=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='bootstrap')
        self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr=='close' for n in ast.walk(boot)))
        self.assertFalse(any(isinstance(n,ast.keyword) and n.arg=='allow_eof' for n in ast.walk(boot)))


def main(inputs):
    global R,N,M,W,F,INPUTS
    INPUTS=inputs
    def raw(row):
        b=Path(row['path']).read_bytes()
        if len(b)!=row['size_bytes'] or hashlib.sha256(b).hexdigest()!=row['sha256']:raise RuntimeError('DRIFT')
        return b
    pkg=types.ModuleType('selected_runner_pure');pkg.__path__=[];sys.modules[pkg.__name__]=pkg
    def load(name,key):
        row=inputs[key];m=types.ModuleType(pkg.__name__+'.'+name);m.__package__=pkg.__name__;sys.modules[m.__name__]=m
        exec(compile(raw(row),row['path'],'exec'),m.__dict__);return m
    N=load('mapper_namespace_probe_common_0004','common');W=load('mapper_package_ipc_model_0004','wire')
    M=load('mapper_namespace_package_model_0007','model');R=load('runner','runner')
    F=load('fixture_helpers','fixture_helpers');F.N=N;F.M=M;F.W=W;F.HISTORY=json.loads(raw(inputs['namespace_record']))
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    print(json.dumps({'result':'PASS' if result.wasSuccessful() else 'FAIL','checks':result.testsRun,'pure_only':True,'namespace_executions':0,'builder_executions':0,'package_writes':0,'host_qualified':False},sort_keys=True))
    return 0 if result.wasSuccessful() else 1
