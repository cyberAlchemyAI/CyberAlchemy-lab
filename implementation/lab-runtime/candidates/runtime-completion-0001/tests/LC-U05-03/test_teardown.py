"""Owned descriptor fault regressions; no actual host admission or authority."""
import argparse,os,socket,sys,traceback,unittest
from pathlib import Path
from test_support import P,B,Fixture

def live(fd):
    try:os.fstat(fd);return True
    except OSError:return False

class TeardownTests(unittest.TestCase):
    def fixture(self):
        f=Fixture(TEMP);self.addCleanup(self.cleanup_fixture,f);return f
    def cleanup_fixture(self,f):
        # Already attempted uncertain handles must never be retried numerically.
        for obj in list(f._held):
            try:obj.close()
            except P.Refusal:
                self.assertEqual(obj.teardown_status()['cleanup'],'unknown')
        f._held=[];f.close()
    def test_all_root_handles_attempted_and_no_reused_fd_retry(self):
        f=self.fixture();obj=f.inputs;owned=[x for group in obj._handles.values()for x in reversed(group)]
        real=os.close;calls=[];replacement=[]
        def faulty(fd):
            real(fd);calls.append(fd)
            if len(calls)==1:
                replacement.append(os.open('/dev/null',os.O_RDONLY))
                raise OSError('INERT_PRIVATE_CLOSE_MARKER')
        try:
            P.os.close=faulty
            with self.assertRaises(P.Refusal)as caught:obj.close()
        finally:P.os.close=real
        try:
            self.assertEqual(calls,owned);self.assertEqual(replacement[0],owned[0])
            self.assertTrue(live(replacement[0]));self.assertTrue(all(not live(fd)for fd in owned[1:]))
            self.assertEqual(caught.exception.cleanup_codes,('OWNED_DESCRIPTOR_CLOSE_UNCERTAIN',))
            with self.assertRaises(P.Refusal):obj.close()
            self.assertTrue(live(replacement[0]));self.assertEqual(obj.teardown_status(),{'closed':True,'cleanup':'unknown'})
            with self.assertRaises(P.Refusal):obj.read('common')
        finally:real(replacement[0])
    def test_socket_failure_still_closes_pidfd(self):
        a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET);pidfd=os.pidfd_open(os.getpid(),0)
        class Fault:
            def close(self):a.close();raise OSError('INERT_PRIVATE_CLOSE_MARKER')
        obj=object.__new__(P.HostCustody);obj._closed=False;obj._close_attempted=False;obj._cleanup_uncertain=False
        obj._socket=Fault();obj._pidfd=pidfd
        try:
            with self.assertRaises(P.Refusal):obj.close()
            self.assertFalse(live(pidfd));self.assertEqual(a.fileno(),-1)
            self.assertEqual(obj.teardown_status()['cleanup'],'unknown')
            with self.assertRaises(P.Refusal):obj.close()
        finally:a.close();b.close()
    def test_read_failure_closes_all_intermediates_and_fences_capability(self):
        f=self.fixture();real_open=os.open;real_close=os.close;opened=[];target=[];calls=[]
        def track(path,flags,*args,**kw):
            fd=real_open(path,flags,*args,**kw);opened.append(fd)
            if path=='common.py'and not target:target.append(fd)
            return fd
        def faulty(fd):
            real_close(fd);calls.append(fd)
            if target and fd==target[0]:raise OSError('INERT_PRIVATE_CLOSE_MARKER')
        try:
            P.os.open=track;P.os.close=faulty
            with self.assertRaises(P.Refusal)as caught:f.inputs.read('common')
        finally:P.os.open=real_open;P.os.close=real_close
        self.assertEqual(len(target),1);self.assertTrue(all(not live(fd)for fd in set(opened)))
        self.assertIn('OWNED_DESCRIPTOR_CLOSE_UNCERTAIN',caught.exception.cleanup_codes)
        self.assertEqual(f.inputs.teardown_status()['cleanup'],'unknown')
        with self.assertRaises(P.Refusal):f.inputs.read('common')
    def test_constructor_primary_preserved_when_rollback_close_fails(self):
        f=self.fixture();roots=list(f.inputs._roots.values());members=list(f.inputs._members.values())
        real_guard=P.HeldInputs.guard;real_close=os.close;real_open=os.open;opened=[];calls=[]
        primary=ValueError('INERT_PRIVATE_PRIMARY_MARKER')
        def fail_guard(self):raise primary
        def track(*args,**kw):fd=real_open(*args,**kw);opened.append(fd);return fd
        def faulty(fd):
            real_close(fd);calls.append(fd)
            if len(calls)==1:raise OSError('INERT_PRIVATE_CLOSE_MARKER')
        try:
            P.HeldInputs.guard=fail_guard;P.os.open=track;P.os.close=faulty
            try:P.HeldInputs(roots,members)
            except P.Refusal as error:
                self.assertIs(error.__context__,primary)
                self.assertIn('OWNED_DESCRIPTOR_CLOSE_UNCERTAIN',error.cleanup_codes)
                rendered=''.join(traceback.format_exception(error))
                self.assertNotIn('INERT_PRIVATE',rendered)
            else:self.fail('constructor admitted')
        finally:P.HeldInputs.guard=real_guard;P.os.open=real_open;P.os.close=real_close
        self.assertEqual(set(calls),set(opened));self.assertTrue(all(not live(fd)for fd in opened))
    def test_transport_admission_primary_not_masked_by_close_failure(self):
        a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET);factory=P.socket.socket
        class Wrapper:
            def __init__(self,fd):self.inner=factory(fileno=fd);self.family=self.inner.family
            def getsockopt(self,*args):return self.inner.getsockopt(*args)
            def close(self):self.inner.close();raise OSError('INERT_PRIVATE_CLOSE_MARKER')
        before=len(os.listdir('/proc/self/fd'))
        try:
            P.socket.socket=lambda *,fileno:Wrapper(fileno)
            with self.assertRaises(P.Refusal)as caught:P._adopt_seqpacket(a.fileno(),(os.getpid()+100,os.geteuid(),os.getegid()),1)
            self.assertEqual(caught.exception.args,('HOST_PEER',))
            self.assertIn('STARTUP_CLEANUP_UNCERTAIN',caught.exception.__notes__)
            self.assertEqual(len(os.listdir('/proc/self/fd')),before)
        finally:P.socket.socket=factory;a.close();b.close()
    def test_host_factory_owned_tail_keeps_primary_and_closes_pidfd(self):
        # Execute the unchanged factory's post-admission ownership try/except.
        # Admission checks are excluded; this cannot produce an actual capability.
        import ast,copy
        tree=ast.parse(Path(P.__file__).read_bytes())
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='HostCustody')
        fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='from_fixed_host_loader')
        tail=next(n for n in fn.body if isinstance(n,ast.Try))
        wrapper=ast.FunctionDef(name='owned_tail',args=ast.arguments(posonlyargs=[],args=[ast.arg(arg='obj'),ast.arg(arg='inherited_fd'),ast.arg(arg='peer')],kwonlyargs=[],kw_defaults=[],defaults=[]),body=[copy.deepcopy(tail)],decorator_list=[])
        a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        obj=object.__new__(P.HostCustody);obj._socket=None;obj._pidfd=None;obj._closed=False;obj._close_attempted=False;obj._cleanup_uncertain=False
        peer={'pid':os.getpid()};obj._peer=(os.getpid(),os.geteuid(),os.getegid());obj._timeout=1
        primary=RuntimeError('INERT_PRIVATE_ADMISSION')
        def fail(stage):raise primary
        obj.check=fail
        class Fault:
            def __init__(self,inner):self.inner=inner
            def close(self):self.inner.close();raise OSError('INERT_PRIVATE_CLOSE')
        env={'os':os,'_adopt_seqpacket':lambda *args:Fault(P._adopt_seqpacket(*args))}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[wrapper],type_ignores=[])),str(Path(P.__file__)),'exec'),env)
        before=len(os.listdir('/proc/self/fd'))
        try:
            with self.assertRaises(RuntimeError)as caught:env['owned_tail'](obj,a.fileno(),peer)
            self.assertIs(caught.exception,primary);self.assertTrue(P.cleanup_uncertain(primary))
            self.assertEqual(obj.teardown_status()['cleanup'],'unknown');self.assertEqual(len(os.listdir('/proc/self/fd')),before)
        finally:a.close();b.close()

    def test_startup_reports_descriptor_uncertainty_without_imports(self):
        f=self.fixture();startup=f.startup();original=f.custody.read
        def fault(*args,**kwargs):raise P.Refusal('INPUT_READ_CLOSE_FAILED',cleanup_codes=('OWNED_DESCRIPTOR_CLOSE_UNCERTAIN',))
        f.custody.read=fault
        try:result=startup.run()
        finally:f.custody.read=original
        self.assertEqual(result.primary_code,'PREFLIGHT_FAILED')
        self.assertIn('OWNED_DESCRIPTOR_CLOSE_UNCERTAIN',result.cleanup_codes)
        self.assertEqual(result.effect_state,'unknown');self.assertEqual(f.event_list(),[])

    def test_hostile_exception_hooks_cannot_escape_teardown_sanitizer(self):
        calls=[]
        class Hostile(RuntimeError):
            def __getattribute__(self,name):
                if name in ('__notes__','__dict__'):
                    calls.append(name);raise RuntimeError('INERT_PRIVATE_HOOK')
                return super().__getattribute__(name)
            def __str__(self):raise RuntimeError('INERT_PRIVATE_STRING')
        original=Hostile('INERT_PRIVATE_PRIMARY')
        @P.public_boundary
        def fail():
            try:raise original
            finally:P._finish_closes([OSError('INERT_PRIVATE_CLOSE')],sys.exception(),'CLOSE_FAILED')
        with self.assertRaises(P.Refusal)as caught:fail()
        self.assertIs(caught.exception.__context__,original)
        self.assertEqual(calls,[])
        self.assertEqual(caught.exception.cleanup_codes,('OWNED_DESCRIPTOR_CLOSE_UNCERTAIN',))
        rendered=''.join(traceback.format_exception(caught.exception))
        self.assertNotIn('INERT_PRIVATE',rendered)

    def test_exact_refusal_hostile_cleanup_element_never_compared(self):
        calls=[]
        class Hostile:
            def __eq__(self,other):calls.append(other);raise RuntimeError('INERT_PRIVATE_EQUALITY')
        error=P.Refusal('fixed',cleanup_codes=(Hostile(),))
        self.assertEqual(error.cleanup_codes,())
        error.cleanup_codes=(Hostile(),)
        @P.public_boundary
        def fail():raise error
        with self.assertRaises(P.Refusal)as caught:fail()
        self.assertEqual(calls,[]);self.assertFalse(P.cleanup_uncertain(caught.exception))
        self.assertNotIn('INERT_PRIVATE',''.join(traceback.format_exception(caught.exception)))

def main():
    global TEMP
    import json
    p=argparse.ArgumentParser();p.add_argument('--temp-root',required=True,type=Path);TEMP=p.parse_args().temp_root
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TeardownTests))
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS'if result.wasSuccessful()else'FAIL',
                      'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean'}))
    raise SystemExit(0 if result.wasSuccessful()else 1)
if __name__=='__main__':main()
