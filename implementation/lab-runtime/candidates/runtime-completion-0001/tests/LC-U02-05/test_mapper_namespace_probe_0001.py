"""Static/pure tests only; forbidden to invoke run, main, launch or proc reads."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import socket
import struct
import sys
import types
import unittest

C=None
CTRL=None
SOURCES={}


def sample_status():
    return b'PPid:\t100\nNSpid:\t101 1\nUid:\t1000 1000 1000 1000\nGid:\t1001 1001 1001 1001\nCapInh:\t0000000000000000\nCapPrm:\t0000000000000001\nCapEff:\t0000000000000001\nCapBnd:\t000001ffffffffff\nCapAmb:\t0000000000000000\nNoNewPrivs:\t1\n'


def observations():
    controller={'namespaces':{'pid':[1,1],'pid_for_children':[1,1],'user':[1,2],'mnt':[1,3]}}
    p={'pid':101,'start':9,'ppid':100,'nspid':[101,1],
       'uid':[1000]*4,'gid':[1001]*4,
       'namespaces':{'pid':[1,11],'pid_for_children':[1,11],'user':[1,12],'mnt':[1,13]},
       'caps':{k:'0000000000000001' for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb')},
       'no_new_privs':1,'uid_map':[[0,1000,1]],'gid_map':[[0,1001,1]],'setgroups':'deny',
       'exe_sha256':'c'*64,'exe_identity':[2,3,0,0,493]}
    claim=copy.deepcopy(p);claim.update(pid=1,ppid=0,nspid=[1],uid=[0]*4,gid=[0]*4,exe_identity=[2,3,65534,65534,493])
    return [controller,[p],copy.deepcopy([p]),claim,[101,1000,1001],'c'*64,[2,3,0,0,493]]


class PureTests(unittest.TestCase):
    def test_stat_comm_with_parenthesis_and_start_index(self):
        raw=b'101 (a ) strange) S 100 100 100 '+b'0 '*15+b'9 0 0\n'
        out=C.parse_stat(raw)
        self.assertEqual((out['pid'],out['ppid'],out['pgrp'],out['session'],out['start']),(101,100,100,100,9))

    def test_stat_bounds_and_invalid_fields(self):
        for raw in (b'x',b'1 (x) S 0',b'x'*4097):
            with self.assertRaises(C.Refusal):C.parse_stat(raw)

    def test_status_all_original_selected_fields(self):
        s=C.parse_status(sample_status());self.assertEqual(s['NSpid'],[101,1]);self.assertEqual(s['Uid'],[1000]*4)
        self.assertEqual(s['CapBnd'],'000001ffffffffff')

    def test_status_missing_duplicate_overflow_and_nonascii(self):
        for raw in (sample_status().replace(b'NoNewPrivs:\t1\n',b''),sample_status()+b'Uid:\t0 0 0 0\n',
                    sample_status().replace(b'1000',b'4294967295'),sample_status()+b'\xff',b'x'*65537):
            with self.assertRaises(C.Refusal):C.parse_status(raw)

    def test_status_invalid_cap_and_nnp(self):
        for old,new in [(b'000001ffffffffff',b'1'),(b'NoNewPrivs:\t1',b'NoNewPrivs:\t2')]:
            with self.assertRaises(C.Refusal):C.parse_status(sample_status().replace(old,new))

    def test_map_bounds_overlap_and_adjacent_positive(self):
        self.assertEqual(C.parse_map(b'0 1000 1\n1 2000 2\n'),[[0,1000,1],[1,2000,2]])
        for raw in (b'',b'0 1000 2\n1 2000 1',b'0 1000 2\n2 1001 1',b'0 4294967294 2',
                    b'0 1000 0',b'0 1 1\n'*65,b'x'*4097):
            with self.assertRaises(C.Refusal):C.parse_map(raw)

    def test_exact_stage2_frame_and_previous_digest(self):
        raw=C.frame(0,'a'*64,'b'*64,None,{})
        self.assertEqual(C.validate_frame(raw,0,'a'*64,'b'*64,None),{})
        for args in [(1,'a'*64,'b'*64,None),(0,'c'*64,'b'*64,None),(0,'a'*64,'b'*64,'d'*64)]:
            with self.assertRaises(C.Refusal):C.validate_frame(raw,*args)

    def test_frame_closed_duplicates_noncanonical_size(self):
        raw=C.frame(0,'a'*64,'b'*64,None,{})
        obj=json.loads(raw);obj['extra']=True
        with self.assertRaises(C.Refusal):C.validate_frame(C.encode(obj),0,'a'*64,'b'*64,None)
        for data in (b'{"x":1,"x":2}',b'{"x": 1}',b'\xff',b'x'*8193,b'{"n":NaN}'):
            with self.assertRaises(C.Refusal):C.decode(data)

    def test_namespace_positive_does_not_prove_host(self):
        self.assertEqual(len(C.join(*observations())),64)

    def test_required_unshare_each_namespace_not_concordance(self):
        for name in ('pid','user','mnt'):
            a=observations()
            for chain in (a[1],a[2]):chain[0]['namespaces'][name]=a[0]['namespaces'][name]
            a[3]['namespaces'][name]=a[0]['namespaces'][name]
            with self.assertRaisesRegex(C.Refusal,'UNSHARE_REQUIRED'):C.join(*a)

    def test_identity_cap_map_and_credential_mutations(self):
        for mode in ('caps','map','pid','inode','start','claim-extra'):
            a=observations()
            if mode=='caps':a[3]['caps']['CapEff']='0000000000000000'
            if mode=='map':a[3]['uid_map']=[[0,1002,1]]
            if mode=='pid':a[4][0]=200
            if mode=='inode':a[3]['exe_identity'][1]=99
            if mode=='start':a[2][0]['start']=10
            if mode=='claim-extra':a[3]['authority']=True
            with self.assertRaises(C.Refusal):C.join(*a)

    def test_child_uid_mapping_and_identity_coordinate_difference(self):
        a=observations();self.assertEqual(len(C.join(*a)),64)
        a[3]['uid'][1]=True
        with self.assertRaises(C.Refusal):C.join(*a)

    def test_sender_only_ordinary_send_no_ancillary(self):
        class Fake:
            def __init__(self):self.calls=[]
            def send(self,*args):self.calls.append(args);return len(args[0])
            def sendmsg(self,*args):raise AssertionError('FORBIDDEN')
        f=Fake();C.send_packet(f,b'fixed')
        self.assertEqual(f.calls,[(b'fixed',socket.MSG_NOSIGNAL)])
        class Short(Fake):
            def send(self,*args):return 1
        with self.assertRaises(C.Refusal):C.send_packet(Short(),b'fixed')
        class Busy(Fake):
            def send(self,*args):raise BlockingIOError()
        with self.assertRaises(BlockingIOError):C.send_packet(Busy(),b'fixed')

    def test_recv_exact_credentials_matching_explicit_is_indistinguishable(self):
        class Fake:
            def recvmsg(self,*args):return b'{}',[(socket.SOL_SOCKET,socket.SCM_CREDENTIALS,struct.pack('3i',101,1000,1001))],0,None
        self.assertEqual(C.recv_packet(Fake()),(b'{}',[101,1000,1001]))

    def test_rights_all_close_once_even_first_close_fault(self):
        closed=[];old=C.os.close
        def fake_close(fd):
            closed.append(fd)
            if fd==500:raise OSError('INERT_CLOSE')
        class Fake:
            def recvmsg(self,*args):return b'{}',[(socket.SOL_SOCKET,socket.SCM_RIGHTS,struct.pack('2i',500,501))],0,None
        try:
            C.os.close=fake_close
            with self.assertRaisesRegex(C.Refusal,'RIGHTS_CLOSE_UNKNOWN'):C.recv_packet(Fake())
        finally:C.os.close=old
        self.assertEqual(closed,[500,501])

    def test_recv_duplicate_unknown_truncated_eof(self):
        cred=(socket.SOL_SOCKET,socket.SCM_CREDENTIALS,struct.pack('3i',101,1000,1001))
        for anc,flags in [([cred,cred],0),([(99,99,b'x')],0),([cred],socket.MSG_CTRUNC),([cred],socket.MSG_TRUNC)]:
            class Fake:
                def recvmsg(self,*args):return b'{}',anc,flags,None
            with self.assertRaises(C.Refusal):C.recv_packet(Fake())
        class EOF:
            def recvmsg(self,*args):return b'',[],0,None
        self.assertEqual(C.recv_packet(EOF(),allow_eof=True),(None,None))
        with self.assertRaises(C.Refusal):C.recv_packet(EOF())

    def test_exact_argv_is_read_only_no_family_builder_or_native(self):
        args=CTRL.argv('/owned/control','a'*64)
        self.assertEqual(args[:8],['/usr/bin/bwrap','--die-with-parent','--unshare-all','--clearenv','--as-pid-1','--sync-fd','3','--ro-bind'])
        self.assertNotIn('--bind',args);self.assertNotIn('--preserve-fds',args)
        self.assertEqual(args[-1],'a'*64)
        self.assertIn('pycache_prefix=/work/control/cache',args)
        self.assertIn('-I',args);self.assertIn('-B',args);self.assertIn('-S',args)

    def test_census_boolean_type_and_extra_fd_refuse(self):
        import stat
        rows=[[0,stat.S_IFCHR],[1,stat.S_IFIFO],[2,stat.S_IFIFO],[3,stat.S_IFSOCK]]
        CTRL.census_valid(rows)
        for bad in (rows+[[4,stat.S_IFREG]],[[False,stat.S_IFCHR]]+rows[1:]):
            with self.assertRaises(C.Refusal):CTRL.census_valid(bad)


class StaticTests(unittest.TestCase):
    def test_only_one_send_site_no_sendmsg_or_sendall(self):
        found=[]
        for name,raw in SOURCES.items():
            for node in ast.walk(ast.parse(raw)):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in ('send','sendmsg','sendall'):
                    found.append((name,node.func.attr))
        self.assertEqual(found,[('common','send')])

    def test_sendmsg_injection_is_detected(self):
        raw=SOURCES['payload']+b'\ns.sendmsg([b"x"], [(1,2,b"tuple")])\n'
        found=[n.func.attr for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='sendmsg']
        self.assertEqual(found,['sendmsg'])

    def test_no_assert_runtime_validation(self):
        for raw in SOURCES.values():self.assertFalse(any(isinstance(n,ast.Assert) for n in ast.walk(ast.parse(raw))))

    def test_no_candidate_imports_or_run_on_import(self):
        for name,raw in SOURCES.items():
            tree=ast.parse(raw)
            for node in tree.body:
                self.assertIsInstance(node,(ast.Expr,ast.Import,ast.ImportFrom,ast.ClassDef,ast.FunctionDef,ast.Assign,ast.If))
                if isinstance(node,ast.If):self.assertIn("__name__",ast.unparse(node.test))
            for node in ast.walk(tree):
                if isinstance(node,(ast.Import,ast.ImportFrom)):
                    text=ast.unparse(node)
                    self.assertNotIn('mapper_',text);self.assertNotIn('mediator_probe_',text)

    def test_no_protected_or_native_process_route(self):
        for name,raw in SOURCES.items():
            tree=ast.parse(raw)
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):
                    self.assertFalse(any(x.name in ('subprocess','ctypes') for x in node.names))
            self.assertNotIn(b'Source8',raw);self.assertNotIn(b'lab-context-native-reader',raw)


def main(selection_path,selection_sha):
    global C,CTRL,SOURCES
    raw=Path(selection_path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=selection_sha:raise SystemExit('TEST_SELECTION_DRIFT')
    selection=json.loads(raw)
    for role in ('common','controller','payload'):
        row=selection['roles'][role];data=Path(row['path']).read_bytes()
        if len(data)!=row['size_bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:raise SystemExit('SOURCE_DRIFT')
        SOURCES[role]=data
    C=types.ModuleType('selected_probe_common_tests');exec(compile(SOURCES['common'],'selected-common','exec'),C.__dict__)
    CTRL=types.ModuleType('selected_probe_controller_tests');exec(compile(SOURCES['controller'],'selected-controller','exec'),CTRL.__dict__);CTRL.C=C
    suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    for role,data in SOURCES.items():
        if Path(selection['roles'][role]['path']).read_bytes()!=data:raise SystemExit('POST_SOURCE_DRIFT')
    print(json.dumps({'schema':'mapper-namespace-static-tests/v1','result':'PASS' if result.wasSuccessful() else 'FAIL','checks':result.testsRun,'probe_executions':0,'host_qualified':False,'cleanup':'clean'},sort_keys=True))
    return 0 if result.wasSuccessful() else 1
