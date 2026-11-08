"""Real kernel transport tests plus isolated non-admitted parser fixtures.

object.__new__ below deliberately exercises the wire primitive only; these test
objects bypass admission and never enter Startup or claim genuine host authority.
"""
import argparse,array,copy,json,os,socket,struct,time,unittest
from pathlib import Path
from test_support import P,Fixture

class HostTests(unittest.TestCase):
    def peer(self):return (os.getpid(),os.geteuid(),os.getegid())
    def test_transport_duplicates_fd_and_preserves_caller(self):
        a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        try:
            duplicate=P._adopt_seqpacket(a.fileno(),self.peer(),1);duplicate.close()
            a.send(b'x');self.assertEqual(b.recv(1),b'x')
        finally:a.close();b.close()
    def test_stream_no_fallback(self):
        a,b=socket.socketpair()
        try:
            before=len(os.listdir('/proc/self/fd'))
            with self.assertRaises(P.Refusal):P._adopt_seqpacket(a.fileno(),self.peer(),1)
            self.assertEqual(len(os.listdir('/proc/self/fd')),before)
        finally:a.close();b.close()
    def test_regular_fd_and_closed_fd_no_duplicate_leak(self):
        fd=os.open('/dev/null',os.O_RDONLY)
        try:
            before=len(os.listdir('/proc/self/fd'))
            for _ in range(10):
                with self.assertRaises(OSError):P._adopt_seqpacket(fd,self.peer(),1)
            self.assertEqual(len(os.listdir('/proc/self/fd')),before)
        finally:os.close(fd)
        with self.assertRaises(OSError):P._adopt_seqpacket(-1,self.peer(),1)
    def test_wrong_expected_peer(self):
        a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        try:
            with self.assertRaises(P.Refusal):P._adopt_seqpacket(a.fileno(),(os.getpid()+100,os.geteuid(),os.getegid()),1)
        finally:a.close();b.close()
    def wire(self, mode='valid', *, credentials=True, small_ancillary=False, close_error=False):
        a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        if credentials:a.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        a.settimeout(2);b.settimeout(2)
        child=os.fork()
        if child==0:
            a.close();fds=[]
            try:
                raw=b.recv(65536);q=P.parse(raw)
                response={'schema_version':'lab-startup-host-response/v1','request_sha256':P.digest(raw),
                          'nonce':q['nonce'],'scope':q['scope'],'permitted':True,'reader_proof':None}
                if mode=='nonce':response['nonce']='0'*64
                if mode=='digest':response['request_sha256']='0'*64
                if mode=='scope':response['scope']={'wrong':True}
                if mode=='denied':response['permitted']=False
                if mode=='extra':response['extra']=True
                if mode=='proof':response['reader_proof']={'unexpected':True}
                body=P.canonical(response)
                if mode=='truncated':body+=b' '*65536
                if mode=='malformed':body=b'{'
                if mode=='duplicate':body=b'{"x":1,"x":2}'
                if mode=='noncanonical':body=b' '+body
                ancillary=[]
                if mode=='rights':
                    fds=[os.open('/dev/null',os.O_RDONLY)for _ in range(4)]
                    ancillary=[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',fds))]
                b.sendmsg([body],ancillary)
                os._exit(0)
            except BaseException:os._exit(2)
        b.close()
        obj=object.__new__(P.HostCustody);obj._socket=a;obj._scope={'fixture_wire_only':True}
        obj._peer=(child,os.geteuid(),os.getegid());obj._max=4096;obj._current=lambda cleanup=False:None
        if mode=='wrong-peer':obj._peer=(os.getpid(),os.geteuid(),os.getegid())
        if small_ancillary:
            class SmallBuffer:
                def send(self,raw):return a.send(raw)
                def recvmsg(self,n,anc,flags):return a.recvmsg(n,0,flags)
            obj._socket=SmallBuffer()
        real_close=os.close;closed=[]
        def close_once(fd):
            real_close(fd);closed.append(fd)
            if len(closed)==1:raise OSError('inert-close-after-success')
        before=len(os.listdir('/proc/self/fd'))
        try:
            if close_error:P.os.close=close_once
            result=obj._exchange('current','admission')
            self.assertEqual(mode,'valid');self.assertIsNone(result)
        finally:
            P.os.close=real_close
            after=len(os.listdir('/proc/self/fd'));a.close()
            _,status=os.waitpid(child,0);self.assertEqual(os.waitstatus_to_exitcode(status),0)
            self.assertEqual(before,after,'delivered rights leaked')
            if close_error:
                self.assertEqual(len(closed),4)
                self.assertTrue(obj._cleanup_uncertain)
    def test_real_child_kernel_credentials(self):self.wire()
    def test_missing_credentials_refused(self):
        with self.assertRaises(P.Refusal):self.wire(credentials=False)
    def test_wrong_kernel_peer_refused(self):
        with self.assertRaises(P.Refusal):self.wire('wrong-peer')
    def test_all_delivered_rights_closed(self):
        with self.assertRaises(P.Refusal):self.wire('rights')
    def test_close_error_does_not_skip_remaining_rights(self):
        with self.assertRaises(P.Refusal):self.wire('rights',close_error=True)
    def test_kernel_control_truncation_refused(self):
        with self.assertRaises(P.Refusal):self.wire('rights',small_ancillary=True)
    def test_kernel_payload_truncation_refused(self):
        with self.assertRaises(P.Refusal):self.wire('truncated')
    def test_closed_canonical_nonce_request_scope(self):
        for mode in ('nonce','digest','scope','denied','extra','proof','malformed','duplicate','noncanonical'):
            with self.subTest(mode=mode),self.assertRaises((P.Refusal,ValueError)):self.wire(mode)
    def test_cleanup_current_after_positive_expiry_is_separate(self):
        with Fixture(TEMP)as f:
            now=int(time.time());scope={'not_before_unix':now-20,'expires_unix':now-1,
                                      'inventory_sha256':'0'*64,'root_control_sha256':f.file_binding('runtime')['sha256']}
            enrollment={'fixture_only':True}
            control={'schema_version':'lab-startup-host-control/v1','scope':scope,'revoked':True,
                     'cleanup':{'scope_sha256':P.digest(P.canonical(scope)),'permitted':True,
                                'not_before_unix':now-1,'expires_unix':now+20}}
            f.put('host_enrollment','host-enrollment.json',P.canonical(enrollment),'evidence')
            f.put('host_control','host-control.json',P.canonical(control),'evidence');f.reseal()
            obj=object.__new__(P.HostCustody);obj._closed=False;obj._creator_pid=os.getpid();obj.inputs=f.inputs
            obj._pidfd=os.pidfd_open(os.getpid(),0);obj._peer=self.peer();obj._start_ticks=P.process_start_ticks(os.getpid());obj._executable_id='runtime'
            self.addCleanup(os.close,obj._pidfd)
            obj._enrollment_id='host_enrollment';obj._enrollment_raw=P.canonical(enrollment)
            obj._control_id='host_control';obj._scope=scope
            a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
            self.addCleanup(a.close);self.addCleanup(b.close);obj._socket=a
            st=os.fstat(a.fileno());obj._channel_identity={'device':st.st_dev,'inode':st.st_ino}
            obj._client={'pid':os.getpid(),'start_ticks':obj._start_ticks};obj._peer_selection={'fixture':True}
            obj._basis_id='runtime'
            obj._attestation=self.attestation(obj._peer_selection,f.inputs.selected('runtime'),scope,
                                             obj._channel_identity,obj._client,f.file_binding('runtime'))
            with self.assertRaises(P.Refusal):obj._current(False)
            obj._current(True)
            obj._creator_pid+=1
            with self.assertRaises(P.Refusal):obj._current(True)
    def test_same_uid_fixture_never_admits_actual_host(self):
        with Fixture(TEMP)as f:
            # Closed valid-shaped selector still fails independent host custody.
            scope={'selection_sha256':f.sha,'inventory_sha256':'0'*64,'principal_ref':'fixture',
                   'family':'optimized-0005','role':'participation','operation':'installation.execute','source_cut_sha256':'1'*64,
                   'root_control_sha256':'2'*64,'attempt_id':'fixture','not_before_unix':0,'expires_unix':2**63-1}
            f.put('hc','control.json',b'{}','evidence')
            f.put('he','enrollment.json',b'{}','evidence');f.reseal()
            scope['inventory_sha256']=f.inputs.inventory_digest(('he','hc'))
            peer=dict(zip(('pid','uid','gid'),self.peer()));peer.update(start_ticks=P.process_start_ticks(os.getpid()),executable_file_id='runtime')
            value={'schema_version':'lab-startup-host-enrollment/v1','peer':peer,
                   'scope':scope,'control_binding':f.file_binding('hc'),'max_response_bytes':4096,'timeout_ms':500,
                   'loader_attestation':{}}
            f.put('he','enrollment.json',P.canonical(value),'evidence');f.reseal()
            with self.assertRaises(P.Refusal):P.HostCustody.from_fixed_host_loader(f.inputs,'he',f.file_binding('he'),'hc',scope,-1)

    def attestation(self,peer,executable,scope,channel,client,basis):
        now=int(time.time())
        return {'schema_version':'lab-startup-loader-attestation/v1','peer':peer,'executable':executable,
                'scope_sha256':P.digest(P.canonical(scope)),'inventory_sha256':scope['inventory_sha256'],
                'custody_basis':basis,'client':client,'channel':channel,'exec_excluded':True,
                'writable_aliases_excluded':True,'not_before_unix':now-5,'expires_unix':now+60}
    def test_attestation_exact_joins_and_no_self_assertion_fallback(self):
        # Pure parser fixtures establish no actual loader evidence or authority.
        with Fixture(TEMP)as f:
            peer={'pid':123,'start_ticks':456};exe=f.inputs.selected('runtime');basis=f.file_binding('runtime')
            scope={'inventory_sha256':'a'*64,'root_control_sha256':basis['sha256']}
            channel={'device':1,'inode':2};client={'pid':3,'start_ticks':4}
            v=self.attestation(peer,exe,scope,channel,client,basis)
            P.loader_attestation(v,peer,exe,scope,channel,client)
            changes={'peer':{'pid':124,'start_ticks':456},'executable':{},'scope_sha256':'0'*64,
                     'inventory_sha256':'0'*64,'channel':{'device':1,'inode':3},'client':{'pid':4,'start_ticks':4},
                     'exec_excluded':False,'writable_aliases_excluded':False,'expires_unix':0,
                     'not_before_unix':2**63-1,'custody_basis':dict(basis,sha256='0'*64)}
            for key,value in changes.items():
                changed=copy.deepcopy(v);changed[key]=value
                with self.subTest(field=key),self.assertRaises(P.Refusal):P.loader_attestation(changed,peer,exe,scope,channel,client)
            with self.assertRaises(P.Refusal):P.loader_attestation({},peer,exe,scope,channel,client)

def main():
    global TEMP
    p=argparse.ArgumentParser();p.add_argument('--temp-root',required=True,type=Path);TEMP=p.parse_args().temp_root
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(HostTests))
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS'if r.wasSuccessful()else'FAIL','checks':r.testsRun,'effect_state':'owned-inert','cleanup':'clean'}));raise SystemExit(0 if r.wasSuccessful()else 1)
if __name__=='__main__':main()
