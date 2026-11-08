"""Fixed endpoint mechanics with generated owned fixtures, never actual custody."""
import argparse,array,base64,copy,json,os,socket,sys,tempfile,time,traceback,unittest
from pathlib import Path
from test_support import P,R
DEPS=R/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps'
SEED=bytes.fromhex('9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60')
PUBLIC=bytes.fromhex('d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a')

def rootrow(name,path):
    ancestors=[Path('/')]+[Path('/').joinpath(*path.parts[1:i])for i in range(2,len(path.parts)+1)]
    return {'root_id':name,'path':str(path),'ancestors':[P.identity(x.stat())for x in ancestors],
            'mount_ids':[mount(x)for x in ancestors]}
def mount(path):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:return P.mount_id(fd)
    finally:os.close(fd)
def row(name,root,path,base,kind):
    raw=path.read_bytes()
    return {'file_id':name,'binding':{'kind':kind,'root_id':root,'relative_path':str(path.relative_to(base)),
                'sha256':P.digest(raw),'size_bytes':len(raw)},'identity':P.identity(path.stat()),'mount_id':mount(path)}

class EndpointFixture:
    def __init__(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='owned-endpoint-',dir=TEMP);self.root=Path(self.tmp.name)
        self.host=self.root/'host';self.host.mkdir();self.journal=self.root/'journal';self.journal.mkdir()
        self.a,self.b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        self.a.settimeout(3);self.b.settimeout(3);self.endpoint=None;self.held=[];self.files={}
        self.put('key',SEED,'protected-input');self.put('source',b'fixture source','evidence')
        self.put('profile',b'fixture profile','evidence');self.put('basis',b'fixture nonrollback assertion, no actual authority','evidence')
        self.scope={'selection_sha256':'1'*64,'inventory_sha256':'2'*64,'principal_ref':'fixture:é👩',
                    'family':'optimized-0005','role':'participation','operation':'installation.execute','source_cut_sha256':P.digest(P.canonical({'store_ref':'completion-optimized-source8-0005-optimized-0005','branch_ref':'branch:completion-optimized-source8-0005-optimized-0005'})),
                    'root_control_sha256':self.files['basis']['binding']['sha256'],'attempt_id':'owned-attempt',
                    'not_before_unix':int(time.time())-10,'expires_unix':int(time.time())+600}
        self.policy={'schema_version':'lab-local-candidate-policy/v4-candidate','session_control':{},'reader_public_key':base64.b64encode(PUBLIC).decode(),'expires_at':'2099-01-01T00:00:00Z',
                     'principal_ref':self.scope['principal_ref'],'source_name':'completion-current-participation:optimized-0005','host_uid':os.geteuid(),
                     'source8_control':{'source_binding':{'ref':'source','sha256':self.files['source']['binding']['sha256']}},'allowed_operations':['context.get'],'authority_effect':'none','actual_owner_outcome':None,'revoked':False}
        self.put('policy',P.canonical(self.policy),'protected-input')
        self.control={'schema_version':'lab-startup-host-control/v1','scope':self.scope,'revoked':False,
                      'cleanup':{'scope_sha256':P.digest(P.canonical(self.scope)),'permitted':True,
                                 'not_before_unix':self.scope['not_before_unix'],'expires_unix':self.scope['expires_unix']+600}}
        self.put('control',P.canonical(self.control),'protected-input')
        self.roots=[rootrow('host',self.host),rootrow('journal',self.journal),rootrow('crypto',DEPS.parent)]
        self.crypto_rows=[row('crypto'+str(i),'crypto',p,DEPS.parent,'execution') for i,p in enumerate(sorted((DEPS/'cryptography').rglob('*')))if p.is_file()]
        who={'pid':os.getpid(),'start_ticks':P.process_start_ticks(os.getpid()),'uid':os.geteuid(),'gid':os.getegid()}
        info=os.fstat(self.b.fileno())
        self.value={'schema_version':'lab-startup-host-server-enrollment/v1','fixture_only':True,'host_inventory_sha256':'0'*64,
                    'worker':who,'host':who,'channel':{'device':info.st_dev,'inode':info.st_ino},'scope':self.scope,
                    'policy':{'file_id':'policy','binding':self.files['policy']['binding'],'source_name':'completion-current-participation:optimized-0005',
                       'profile_file_id':'profile','profile_binding':self.files['profile']['binding'],
                       'source_file_id':'source','source_binding':self.files['source']['binding'],'source_cut':{'store_ref':'completion-optimized-source8-0005-optimized-0005','branch_ref':'branch:completion-optimized-source8-0005-optimized-0005'}},
                    'control_file_id':'control','key_file_id':'key','crypto':{'root_id':'crypto','relative_directory':'deps',
                       'file_ids':[r['file_id']for r in self.crypto_rows]},
                    'journal':{'root_id':'journal','capacity':{'root_identity':P.identity(self.journal.stat()),'mount_id':mount(self.journal),
                       'control_binding':self.files['control']['binding'],'scope_sha256':P.digest(P.canonical(self.scope)),
                       'preimage_sha256':P.digest(P.canonical([])),'reserved_bytes':2*1024*1024,'reserved_inodes':20,
                       'not_before_unix':self.scope['not_before_unix'],'expires_unix':self.scope['expires_unix']+1200,
                       'nonrollback_basis':self.files['basis']['binding']}},'max_calls':8,'max_record_bytes':16384,'max_response_bytes':4096,'total_response_bytes':32768,'timeout_ms':1000}
    def put(self,name,raw,kind):
        p=self.host/name;p.write_bytes(raw);p.chmod(0o600);self.files[name]=row(name,'host',p,self.host,kind)
    def select(self):
        selected={'schema_version':'lab-protected-startup-selection/v2','posture':'fixture',
                  'family':self.scope['family'],'role':self.scope['role'],'operation':self.scope['operation'],'principal_ref':self.scope['principal_ref'],
                  'profile_sha256':self.files['profile']['binding']['sha256'],'source_cut':self.value['policy']['source_cut'],
                  'repository':str(self.host),'modules':{'closure_file_ids':['source','profile'],'modules':[]},
                  'cold':{'runtime_origins':[],'documents':{}},'runtime':None}
        self.put('worker_selection',P.canonical(selected),'evidence')
        self.scope['selection_sha256']=self.files['worker_selection']['binding']['sha256']
        self.control['scope']=self.scope;self.control['cleanup']['scope_sha256']=P.digest(P.canonical(self.scope))
        self.put('control',P.canonical(self.control),'protected-input')
        self.value['journal']['capacity']['control_binding']=self.files['control']['binding']
        self.value['journal']['capacity']['scope_sha256']=P.digest(P.canonical(self.scope))
        self.value['worker_selection_file_id']='worker_selection'
        runtime_paths={Path(os.path.realpath(sys.executable)),Path(P.__file__),Path(sys.pycache_prefix)}
        maps=set()
        for line in Path('/proc/self/maps').read_bytes().splitlines():
            fields=line.split(None,5)
            if len(fields)==6 and fields[5].startswith(b'/'):maps.add(Path(fields[5].decode()))
        maps.update(p for p in (DEPS/'cryptography').rglob('*.so'))
        maps.add(Path('/usr/lib/x86_64-linux-gnu/libgcc_s.so.1').resolve())
        maps.add(Path('/usr/lib/x86_64-linux-gnu/libpthread.so.0').resolve())
        maps.update(DEPS.glob('_cffi_backend*.so'))
        python_paths={Path(m.__file__) for m in sys.modules.values() if getattr(m,'__file__',None) is not None}
        python_paths.update(p for p in (DEPS/'cryptography').rglob('*.py'))
        python_paths.update(Path('/usr/lib/python3.14')/n for n in ('__future__.py','typing.py'))
        runtime_paths.update(python_paths)
        runtime_paths.update(maps)
        self.roots += [rootrow('repository',R),rootrow('system',Path('/usr'))]
        runtime_rows=[];path_ids={str(DEPS.parent/r['binding']['relative_path']):r['file_id'] for r in self.crypto_rows}
        for i,path in enumerate(sorted(runtime_paths)):
            if str(path) in path_ids:continue
            root,base=('repository',R)if path.is_relative_to(R)else('system',Path('/usr'))
            runtime_rows.append(row('runtime'+str(i),root,path,base,'execution'));path_ids[str(path)]='runtime'+str(i)
        self.value['runtime']={'interpreter_file_id':path_ids[os.path.realpath(sys.executable)],
                              'implementation_file_id':path_ids[P.__file__], 'cache_prefix_file_id':path_ids[sys.pycache_prefix],
                              'native_file_ids':[path_ids[str(p)]for p in sorted(maps)],'python_file_ids':[path_ids[str(p)]for p in sorted(python_paths)],'isolated':False}
        members=[r for n,r in self.files.items()if n!='enrollment']+self.crypto_rows+runtime_rows
        self.value['host_inventory_sha256']=P.digest(P.canonical({'roots':self.roots,'members':members}))
        self.put('enrollment',P.canonical(self.value),'protected-input')
        self.inputs=P.HeldInputs(self.roots,members+[self.files['enrollment']]);self.held.append(self.inputs)
    def open(self):
        self.select()
        try:self.endpoint=P.StartupHostEndpoint.for_fixture(self.inputs,'enrollment',self.files['enrollment']['binding'],self.b.fileno())
        except P.Refusal as error:
            codes=[];item=error
            while item is not None:
                codes.append(item.args[0] if type(item) is P.Refusal else type(item).__name__)
                item=item.__context__
            error.add_note("owned fixture internal codes: "+repr(codes))
            if 'SERVER_PYTHON_ORIGIN' in codes:
                allowed={self.inputs.path(n)for n in self.value['runtime']['python_file_ids']+self.value['runtime']['native_file_ids']}
                error.add_note('owned unexpected Python origins: '+repr(sorted({getattr(m,'__file__',None)for m in sys.modules.values() if getattr(m,'__file__',None) is not None}-allowed)))
            if 'SERVER_NATIVE_ORIGIN' in codes:
                allowed={self.inputs.path(n)for n in self.value['runtime']['native_file_ids']}
                unexpected=[]
                for line in Path('/proc/self/maps').read_bytes().splitlines():
                    bits=line.split(None,5)
                    if len(bits)==6 and bits[5].startswith(b'/') and bits[5].decode()not in allowed:unexpected.append(bits[5].decode())
                error.add_note('owned unexpected mapped origins: '+repr(sorted(set(unexpected))))
            if 'CRYPTO_LOADED_ORIGIN' in codes:
                error.add_note('owned crypto module origins: '+repr([(n,getattr(m,'__file__',None))for n,m in sys.modules.items()if n.startswith('cryptography')]))
            raise
        return self.endpoint
    def request(self,action='current',nonce='a'*64):
        challenge=None
        if action=='reader-proof':challenge={'schema_version':'lab-local-reader-challenge/v1-candidate','host_instance_ref':'host:R03-api:'+'1'*32,
            'connection_ref':'connection:R03-api:'+'2'*32,'nonce':'3'*64,'policy_sha256':self.files['policy']['binding']['sha256'],
            'expires_at':self.policy['expires_at'],'authority_effect':'none'}
        return {'schema_version':'lab-startup-host-request/v1','nonce':('%016x'%(self.endpoint._calls if self.endpoint else 0))+nonce[:48],'scope':self.scope,'action':action,
                'stage':'cleanup'if action=='cleanup'else'reader-authentication'if action=='reader-proof'else'admission','challenge':challenge}
    def call(self,request):
        self.a.send(P.canonical(request));self.endpoint.serve_once();return P.parse(self.a.recv(65536))
    def close(self):
        if self.endpoint:self.endpoint.close()
        self.a.close();self.b.close()
        for item in self.held:item.close()
        self.tmp.cleanup()

class EndpointTests(unittest.TestCase):
    def fixture(self):
        f=EndpointFixture();self.addCleanup(f.close);return f
    def test_exact_original_proof_and_consumed_before_response(self):
        f=self.fixture();e=f.open();q=f.request('reader-proof');response=f.call(q)
        proof=response['reader_proof'];self.assertEqual(proof['challenge'],q['challenge'])
        # Original API30 uses compact(challenge), raw32 public key and base64 proof.
        e._key.public_key().verify(base64.b64decode(proof['signature'],validate=True),P.canonical(q['challenge']))
        self.assertEqual(proof['schema_version'],'lab-local-reader-proof/v1-candidate')
        records=list(f.journal.glob('*/proof-consumed.json'));self.assertEqual(len(records),1)
        self.assertEqual(P.parse(records[0].read_bytes())['request'],q);self.assertTrue(e._proof_consumed)
        self.assertIsNone(f.call(f.request(nonce='b'*64))['reader_proof'])
        with self.assertRaises(P.Refusal):f.call(f.request('reader-proof',nonce='c'*64))
    def test_existing_empty_attempt_and_restart_refuse(self):
        f=self.fixture();name='attempt-'+P.digest(f.scope['attempt_id'].encode());(f.journal/name).mkdir()
        fd=os.open(f.journal,os.O_RDONLY|os.O_DIRECTORY)
        try:f.value['journal']['capacity']['preimage_sha256']=P.digest(P.canonical(P.journal_inventory(fd)))
        finally:os.close(fd)
        with self.assertRaises(P.Refusal):f.open()
        self.assertTrue((f.journal/name).is_dir())
    def test_lost_reply_retains_consumption_and_no_restart(self):
        f=self.fixture();e=f.open();f.a.send(P.canonical(f.request('reader-proof')));f.a.close()
        with self.assertRaises(P.Refusal):e.serve_once()
        self.assertTrue(e._proof_consumed);self.assertTrue(e._poisoned)
        self.assertEqual(len(list(f.journal.glob('*/proof-consumed.json'))),1)
        with self.assertRaises(P.Refusal):P.StartupHostEndpoint.for_fixture(f.inputs,'enrollment',f.files['enrollment']['binding'],f.b.fileno())
    def test_wrong_key_policy_refuses_before_journal(self):
        f=self.fixture();f.put('key',b'\x01'*32,'protected-input')
        with self.assertRaises(P.Refusal):f.open()
        self.assertEqual(list(f.journal.iterdir()),[])
    def test_insufficient_reserve_refuses_before_journal(self):
        f=self.fixture();f.value['journal']['capacity']['reserved_inodes']=2
        with self.assertRaises(P.Refusal):f.open()
        self.assertEqual(list(f.journal.iterdir()),[])
    def test_fixture_cannot_promote_actual(self):
        f=self.fixture();f.select()
        with self.assertRaises(P.Refusal):P.StartupHostEndpoint.from_fixed_host_loader(f.inputs,'enrollment',f.files['enrollment']['binding'],f.b.fileno())
        self.assertEqual(list(f.journal.iterdir()),[])
    def test_nonce_replay_and_call_limit(self):
        f=self.fixture();f.value['max_calls']=1;f.open();f.call(f.request())
        with self.assertRaises(P.Refusal):f.call(f.request(nonce='b'*64))
        self.assertEqual(len(list(f.journal.glob('*/proof-consumed.json'))),0)
    def test_wrong_challenge_cannot_sign(self):
        for field,value in [('authority_effect','grant'),('policy_sha256','0'*64),('expires_at','2098-01-01T00:00:00Z'),('extra','x')]:
            with self.subTest(field=field):
                f=self.fixture();e=f.open();q=f.request('reader-proof');q['challenge'][field]=value
                with self.assertRaises(P.Refusal):f.call(q)
                self.assertFalse(e._proof_consumed);self.assertEqual(list(f.journal.glob('*/proof-consumed.json')),[])
    def test_rights_closed_and_request_not_consumed(self):
        f=self.fixture();e=f.open();fd=os.open('/dev/null',os.O_RDONLY);before=len(os.listdir('/proc/self/fd'))
        try:
            f.a.sendmsg([P.canonical(f.request())],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[fd,fd,fd]))])
            with self.assertRaises(P.Refusal):e.serve_once()
            self.assertEqual(len(os.listdir('/proc/self/fd')),before)
        finally:os.close(fd)
        self.assertEqual(list(f.journal.glob('*/proof-consumed.json')),[])
    def test_cleanup_after_positive_expiry_cannot_sign(self):
        f=self.fixture();e=f.open();real=P.time.time
        try:
            P.time.time=lambda:f.scope['expires_unix']+1
            self.assertIsNone(f.call(f.request('cleanup'))['reader_proof'])
            with self.assertRaises(P.Refusal):f.call(f.request('reader-proof',nonce='b'*64))
        finally:P.time.time=real
        self.assertFalse(e._proof_consumed)
    def test_fsync_failure_retains_attempt_and_poison(self):
        f=self.fixture();e=f.open();real=P.os.fsync
        def fail(fd):raise OSError('INERT_PRIVATE_FSYNC')
        try:
            P.os.fsync=fail
            with self.assertRaises(P.Refusal)as caught:f.call(f.request('reader-proof'))
        finally:P.os.fsync=real
        self.assertTrue(e._poisoned);self.assertFalse(e._proof_consumed)
        self.assertEqual(len(list(f.journal.glob('*/proof-consumed.json'))),1)
        self.assertNotIn('INERT_PRIVATE_FSYNC',''.join(traceback.format_exception(caught.exception)))
    def test_scope_substitution_before_consumption(self):
        f=self.fixture();f.open();q=f.request();q=copy.deepcopy(q);q['scope']['principal_ref']='foreign'
        with self.assertRaises(P.Refusal):f.call(q)
        self.assertEqual(list(f.journal.glob('*/proof-consumed.json')),[])

    def test_second_process_different_attempt_cannot_share_reserve(self):
        f=self.fixture();f.open();before=sorted(p.name for p in f.journal.iterdir())
        child=os.fork()
        if child==0:
            other=None
            try:
                other=EndpointFixture();other.journal.rmdir();other.journal=f.journal
                other.roots[1]=rootrow('journal',f.journal)
                other.value['journal']['capacity']['root_identity']=P.identity(f.journal.stat())
                other.value['journal']['capacity']['mount_id']=mount(f.journal)
                other.scope['attempt_id']='different-attempt'
                try:other.open()
                except P.Refusal:code=0
                else:code=2
            except BaseException:code=3
            finally:
                if other is not None:other.close()
            os._exit(code)
        _,status=os.waitpid(child,0);self.assertEqual(os.waitstatus_to_exitcode(status),0)
        self.assertEqual(sorted(p.name for p in f.journal.iterdir()),before)
        self.assertIsNone(f.call(f.request())['reader_proof'])
    def test_wrong_runtime_cache_policy_refuses_before_key_or_journal(self):
        f=self.fixture();f.select();original=sys.pycache_prefix
        try:
            sys.pycache_prefix=str(f.root/'attacker-cache')
            with self.assertRaises(P.Refusal):P.StartupHostEndpoint.for_fixture(f.inputs,'enrollment',f.files['enrollment']['binding'],f.b.fileno())
        finally:sys.pycache_prefix=original
        self.assertEqual(list(f.journal.iterdir()),[])
    def test_coherent_other_family_policy_refuses_unchanged_scope(self):
        f=self.fixture();f.policy['source_name']='completion-legacy:legacy-source8-20261018-b'
        f.put('policy',P.canonical(f.policy),'protected-input');f.value['policy']['binding']=f.files['policy']['binding']
        f.value['policy']['source_name']=f.policy['source_name']
        with self.assertRaises(P.Refusal):f.open()
        self.assertEqual(list(f.journal.iterdir()),[])
    def test_cleanup_capacity_must_cover_independent_cleanup_interval(self):
        f=self.fixture();f.value['journal']['capacity']['expires_unix']=f.scope['expires_unix']
        with self.assertRaises(P.Refusal):f.open()
        self.assertEqual(list(f.journal.iterdir()),[])
    def test_complete_fixed_constructor_query_count_fits_derived_bound(self):
        from test_support import Fixture
        for family in ('optimized-0005','legacy-source8-20261018-b'):
            for operation in ('installation.execute','release.prepare'):
                with self.subTest(family=family,operation=operation),Fixture(TEMP,family=family)as f:
                    f.selection['operation']=operation
                    private=P.parse((f.root/'private.json').read_bytes());private['anchor']['operation']=operation
                    f.put('private','private.json',P.canonical(private),'protected-input');f.reseal()
                    budget=P.startup_query_budget(f.selection)
                    result=f.startup().run()
                    self.assertIsNone(result.primary_code);self.assertEqual(result.cleanup_codes,())
                    self.assertLessEqual(f.custody._checks+1,budget['total']) # add actual host admission
                    self.assertGreater(f.custody._checks,1000)
                    print(json.dumps({'fixture_family':family,'operation':operation,'observed_queries':f.custody._checks,
                                      'selected_budget':budget}),file=sys.stderr)

    def test_independent_legacy_metadata_endpoint_proof(self):
        f=self.fixture();f.scope.update(family='legacy-source8-20261018-b',role='installation-metadata')
        cut={'store_ref':'completion-legacy-source8-20261018-b','branch_ref':'branch:completion-legacy-source8-20261018-b'}
        f.scope['source_cut_sha256']=P.digest(P.canonical(cut))
        f.policy.pop('source8_control');f.policy.update(schema_version='lab-local-current-legacy-installation-release-policy/v1-candidate',
            session_control=None,installation_release_control={},current_legacy_installation_control={'source_cut':cut},
            source_name='completion-legacy:legacy-source8-20261018-b',allowed_operations=['installation.execute','release.prepare'])
        f.put('policy',P.canonical(f.policy),'protected-input')
        f.value['policy'].update(binding=f.files['policy']['binding'],source_name=f.policy['source_name'],source_cut=cut)
        f.open();response=f.call(f.request('reader-proof'))
        self.assertEqual(response['scope']['role'],'installation-metadata');self.assertIsNotNone(response['reader_proof'])
    def test_union_policy_refuses_before_attempt_creation(self):
        f=self.fixture();f.policy['installation_release_control']={}
        f.put('policy',P.canonical(f.policy),'protected-input');f.value['policy']['binding']=f.files['policy']['binding']
        with self.assertRaises(P.Refusal):f.open()
        self.assertEqual(list(f.journal.iterdir()),[])
    def test_original_worker_policy_uid_is_not_signing_host_identity(self):
        f=self.fixture();f.policy['host_uid']=os.geteuid()+1
        f.put('policy',P.canonical(f.policy),'protected-input');f.value['policy']['binding']=f.files['policy']['binding']
        with self.assertRaises(P.Refusal):f.open()
        self.assertEqual(list(f.journal.iterdir()),[])

    def test_factory_primary_survives_real_close_failure(self):
        f=self.fixture();f.select();real_current=P.StartupHostEndpoint._current;real_close=P.os.close;seen=[]
        primary=ValueError('INERT_PRIVATE_ADMISSION')
        def current(obj,cleanup):raise primary
        def close(fd):
            real_close(fd);seen.append(fd)
            if len(seen)==1:raise OSError('INERT_PRIVATE_CLOSE')
        # Fault is armed only after socket/pidfd ownership, at admission currentness.
        def armed(obj,cleanup):
            P.os.close=close
            raise primary
        before=len(os.listdir('/proc/self/fd'))
        try:
            P.StartupHostEndpoint._current=armed
            with self.assertRaises(P.Refusal)as caught:
                P.StartupHostEndpoint.for_fixture(f.inputs,'enrollment',f.files['enrollment']['binding'],f.b.fileno())
        finally:P.StartupHostEndpoint._current=real_current;P.os.close=real_close
        self.assertIs(caught.exception.__context__,primary)
        self.assertTrue(P.cleanup_uncertain(caught.exception));self.assertTrue(seen)
        self.assertEqual(len(os.listdir('/proc/self/fd')),before)
        self.assertNotIn('INERT_PRIVATE',''.join(traceback.format_exception(caught.exception)))

def main():
    global TEMP
    p=argparse.ArgumentParser();p.add_argument('--temp-root',required=True,type=Path);TEMP=p.parse_args().temp_root
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(EndpointTests))
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS'if result.wasSuccessful()else'FAIL',
                      'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean'}))
    raise SystemExit(0 if result.wasSuccessful()else 1)
if __name__=='__main__':main()
