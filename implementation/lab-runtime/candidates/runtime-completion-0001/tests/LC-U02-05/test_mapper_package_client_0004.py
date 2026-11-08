"""Real local fd3 transport; synthetic builder dependencies and replies only."""
import array
import ast
import base64
import hashlib
import json
import os
from pathlib import Path,PurePosixPath
import shutil
import socket
import stat
import struct
import subprocess
import sys
import tempfile
import time
import threading
import unittest

from t35_external_v1 import role_stage
from t35_external_v1.phase_scoped_v2 import mapper_package_adapter_0004 as adapter
from t35_external_v1.phase_scoped_v2 import mapper_package_client_0004 as client
from t35_external_v1.phase_scoped_v2 import mapper_package_ipc_model_0004 as wire

ROOT=Path(__file__).resolve().parents[6]
S=ROOT/'implementation/lab-runtime/candidates/runtime-completion-0001'
P=S/'t35_external_v1/phase_scoped_v2'
T=S/'tests/LC-U02-05'
E=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001'
CACHE=E/'LC-U01-02/python-bytecode-cache-disabled-0002'
NATIVE_REL='product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/bin/lab-context-native-reader'
HISTORICAL=ROOT/'product/lab/release-candidates/v1/interface/legacy-session-fixture-mapped-v2-action-0148/build.py'
HISTORICAL_SHA='dced09f9432318ef286475081ea5f4f7e6fa633c7cefbd9db76c0ec3c47ecbbb'
PINS={k:str(i)*64 for i,k in enumerate(('mapper','source','reader','adapter'),1)}

def sha(v):return hashlib.sha256(v).hexdigest()
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def binding(path):
    raw=Path(path).read_bytes();return {'path':str(path),'size_bytes':len(raw),'sha256':sha(raw)}
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:f.write(value)
def reply(request,payload):
    return wire.encode({'schema_version':'lab-mapper-package-ipc-response/v1','attempt_id':request['attempt_id'],
        'selection_sha256':request['selection_sha256'],'request_sha256':sha(wire.encode(request)),
        'ordinal':request['ordinal'],'status':'fixture-only','payload':payload})
def bytes_reply(sock,req,data):
    sock.send(reply(req,{'kind':'DATA_BEGIN','size_bytes':len(data),'sha256':sha(data)}))
    for offset in range(0,len(data),wire.CHUNK_MAX):
        sock.send(reply(req,{'kind':'DATA_CHUNK','offset':offset,'data':base64.b64encode(data[offset:offset+wire.CHUNK_MAX]).decode()}))
    sock.send(reply(req,{'kind':'DATA_END','sha256':sha(data)}))

def stdlib_rows():
    result=[]
    for parent,dirs,files in os.walk('/usr/lib/python3.14'):
        dirs[:]=sorted(d for d in dirs if d!='__pycache__')
        for name in sorted(files):
            p=Path(parent)/name
            if name.endswith(('.py','.so')) and p.is_file():result.append(binding(p.resolve()))
    return list({r['path']:r for r in result}.values())


def make_fixture(root):
    family=root/'legacy-fixture-source';mapped=family/'mapped';reader=family/'reader';snapshot=root/'snapshot'
    raw=HISTORICAL.read_bytes()
    if sha(raw)!=HISTORICAL_SHA:raise RuntimeError('HISTORICAL_DRIFT')
    pre=role_stage.render_python(raw,layout=role_stage.DisposableLayout(PurePosixPath(str(family)),PurePosixPath(str(snapshot)),'legacy-fixture-source'),role='mapped',name='build.py')
    post,record=adapter.adapt(pre,expected_preimage_sha256=sha(pre))
    assignments={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(post).body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Constant)}
    native=ROOT/NATIVE_REL
    if sha(native.read_bytes())!='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c':raise RuntimeError('NATIVE_INPUT_DRIFT')
    write(snapshot/NATIVE_REL,native.read_bytes()) # selected bytes only, never executed
    write(mapped/'policy.json',encoded({'intended_use_binding':{'original_Coordination_Context_value':'fixture-use'}}))
    write(mapped/'source-manifest.json',encoded({'fixture_only':True}))
    for name in ('manifest.json','period.json'):write(reader/'packages/0001'/name,encoded({'fixture_only':True}))
    attrs=['principal','principal_reference','goal','work','intent','profile','assignment','coordination','context','capability','implementation']
    ids=['fixture:'+v for v in attrs]+['fixture:scope','product:cyberalchemy-lab','fixture:project','fixture:product-capability']
    subjects=[]
    def add(identity,version,carrier,value):
        path=root/'originals'/f'{len(subjects):02}.json';raw=encoded(value);write(path,raw)
        subjects.append({'identity':identity,'version_ref':version,'carrier_ref':carrier,'effective_state':'current','record':value,'source':{'path':str(path),'sha256':sha(raw)}})
    for identity in ids:
        value={'name':identity}
        if identity=='fixture:coordination':value['intended_uses']=['fixture-use']
        add(identity,identity+'@1','fixture.node/v1',value)
    for i in range(10):
        source,target=ids[i],ids[i+1]
        add('typed-relation:fixture:'+str(i),'typed-relation:fixture:'+str(i)+'@1','cal.artifact-type.typed-relation/v3',{'payload':{'relation_kind_ref':'fixture-relation','source':{'kind':'fixture-kind','ref':source,'version_ref':source+'@1'},'target':{'kind':'fixture-kind','ref':target,'version_ref':target+'@1'},'qualifiers':{'index':i}}})
    write(reader/'packages/0001/record-index.json',encoded([{'version_ref':r['version_ref'],'carrier_ref':r['carrier_ref'],'original_binding':r['source']} for r in subjects[15:]]))
    definition={'identity':'definition:fixture','version_ref':'definition:fixture@1','record':{'fixture_only':True}}
    path=root/'originals/definition.json';write(path,encoded(definition['record']));definition['source']={'path':str(path),'sha256':sha(path.read_bytes())}
    config={'mapped':str(mapped),'reader':str(reader),'root':str(root),'subjects':subjects,'definition':definition,'mapper_pin':sha((mapped/'source-manifest.json').read_bytes()),'source_pin':assignments['SOURCE_PIN'],'reader_pin':assignments['PACKAGE_PIN']}
    write(root/'config.json',encoded(config));write(root/'preimage.py',pre);write(root/'build.py',post)
    roles={'wire':str(P/'mapper_package_ipc_model_0004.py'),'client':str(P/'mapper_package_client_0004.py'),'bridge':str(P/'mapper_package_bridge_0004.py'),'adapter':str(P/'mapper_package_adapter_0004.py'),'preimage':str(root/'preimage.py'),'builder':str(root/'build.py'),'fixture_base':str(T/'mapper_package_fixture_base_0004.py'),'fixture_config':str(root/'config.json')}
    rows=stdlib_rows()+[binding(p) for p in roles.values()]+[binding(p) for p in root.rglob('*') if p.is_file() and str(p) not in roles.values()]
    rows.append(binding(P/'mapper_package_runner_0004.py'))
    return config,roles,rows,record


class ClientTests(unittest.TestCase):
    def pair(self,peer=None):
        a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        b.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        c=client.Client(a,attempt_id='fixture',selection_sha256='a'*64,begin_pins=PINS,peer=peer or(os.getpid(),os.getuid(),os.getgid()),package_path='/fixture/package',timeout_seconds=2)
        self.addCleanup(c.close);self.addCleanup(b.close);return c,b
    def serve(self,b,fun):
        errors=[]
        def body():
            try:
                raw=b.recv(65536);fun(b,wire.decode(raw))
            except BaseException as e:errors.append(type(e).__name__)
        t=threading.Thread(target=body);t.start();self.addCleanup(lambda:t.join(3));return t,errors
    def test_real_kernel_credentials_ack(self):
        c,b=self.pair();t,errors=self.serve(b,lambda s,r:s.send(reply(r,{'kind':'ACK'})))
        c.begin(PINS['mapper'],'/fixture/package');t.join();self.assertEqual(errors,[]);self.assertEqual(c.step,1)
    def test_wrong_selected_peer_refuses(self):
        c,b=self.pair((os.getpid()+1,os.getuid(),os.getgid()));self.serve(b,lambda s,r:s.send(reply(r,{'kind':'ACK'})))
        with self.assertRaises(client.Refusal):c.begin(PINS['mapper'],'/fixture/package')
        self.assertTrue(c.failed)
    def test_wrong_response_subject_refuses(self):
        c,b=self.pair()
        def wrong(s,r):
            v=wire.decode(reply(r,{'kind':'ACK'}));v['request_sha256']='f'*64;s.send(wire.encode(v))
        self.serve(b,wrong)
        with self.assertRaises(client.Refusal):c.begin(PINS['mapper'],'/fixture/package')
    def test_passed_rights_closed_and_refused(self):
        c,b=self.pair();fd=os.open('/dev/null',os.O_RDONLY);self.addCleanup(lambda:os.close(fd))
        before=len(os.listdir('/proc/self/fd'))
        t,errors=self.serve(b,lambda s,r:s.sendmsg([reply(r,{'kind':'ACK'})],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[fd,fd]))]))
        with self.assertRaises(client.Refusal):c.begin(PINS['mapper'],'/fixture/package')
        t.join();self.assertEqual(len(os.listdir('/proc/self/fd')),before);self.assertFalse(c.cleanup_uncertain)
    def test_oversized_frame_refuses(self):
        c,b=self.pair();self.serve(b,lambda s,r:s.send(b'x'*65537))
        with self.assertRaises(client.Refusal):c.begin(PINS['mapper'],'/fixture/package')
    def test_wrong_order_no_transport(self):
        c,b=self.pair();b.settimeout(.02)
        with self.assertRaises(client.Refusal):c.emit('request.json',b'{}')
        with self.assertRaises(TimeoutError):b.recv(1)
    def test_begin_subject_refusal_is_sticky_without_send(self):
        c,b=self.pair();b.settimeout(.02)
        with self.assertRaises(client.Refusal):c.begin('f'*64,'/fixture/package')
        with self.assertRaises(client.Refusal):c.begin(PINS['mapper'],'/fixture/package')
        self.assertTrue(c.failed)
        with self.assertRaises(TimeoutError):b.recv(1)
    def test_response_blob_digest_refuses(self):
        c,b=self.pair()
        def wrong(s,r):
            s.send(reply(r,{'kind':'DATA_BEGIN','size_bytes':3,'sha256':'0'*64}))
            s.send(reply(r,{'kind':'DATA_CHUNK','offset':0,'data':'YWJj'}))
            s.send(reply(r,{'kind':'DATA_END','sha256':'0'*64}))
        t,errors=self.serve(b,wrong)
        with self.assertRaises(client.Refusal):c.exchange('SEAL',{},want_bytes=True)
        t.join();self.assertEqual(errors,[]);self.assertTrue(c.failed)
    def test_chunked_response_exact_bytes(self):
        c,b=self.pair();data=b'fixture'*10000
        t,errors=self.serve(b,lambda s,r:bytes_reply(s,r,data))
        self.assertEqual(c.exchange('SEAL',{},want_bytes=True),data);t.join();self.assertEqual(errors,[])


class BuilderTests(unittest.TestCase):
    def run_builder(self,mutation=None):
        with tempfile.TemporaryDirectory(prefix='mapper-ipc-fixture-') as directory:
            root=Path(directory);config,roles,rows,record=make_fixture(root)
            package=Path(config['mapped'])/'packages/0001'
            a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
            self.addCleanup(a.close);self.addCleanup(b.close)
            a.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1);a.settimeout(30)
            pins={'mapper':config['mapper_pin'],'source':config['source_pin'],'reader':config['reader_pin'],'adapter':binding(P/'mapper_package_adapter_0004.py')['sha256']}
            selection={'posture':'synthetic-only','bindings':rows,'roles':roles,'preimage_sha256':sha((root/'preimage.py').read_bytes()),'cache':binding(CACHE),'interpreter':binding('/usr/bin/python3.14'),'inherited_fd':b.fileno(),'attempt_id':'fixture-build','selection_sha256':'a'*64,'begin_pins':pins,'peer':[os.getpid(),os.getuid(),os.getgid()],'package':str(package)}
            manifest=root/'selection.json';write(manifest,encoded(selection))
            if mutation=='selected-postimage-drift':
                changed=(root/'build.py').read_bytes()+b'\n# substituted postimage\n'
                (root/'build.py').write_bytes(changed)
                for row in selection['bindings']:
                    if row['path']==str(root/'build.py'):row.update(binding(root/'build.py'))
                manifest.write_bytes(encoded(selection))
            command=['/usr/bin/python3.14','-I','-B','-S','-X','pycache_prefix='+str(CACHE)]
            if sys.flags.optimize:command.append('-O')
            command +=[str(P/'mapper_package_runner_0004.py'),str(manifest),sha(manifest.read_bytes()),str(manifest.stat().st_size)]
            started=time.monotonic()
            process=subprocess.Popen(command,pass_fds=(b.fileno(),),stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},cwd=str(root));b.close()
            model=wire.ProtocolModel(attempt_id='fixture-build',selection_sha256='a'*64,begin_pins=pins,peer=(process.pid,1,os.getuid(),os.getgid()))
            try:
                while model.step<61:
                    a.settimeout(max(.001,30-(time.monotonic()-started)))
                    if time.monotonic()-started>=30:raise TimeoutError('FIXTURE_DEADLINE')
                    packet,anc,flags,_=a.recvmsg(65536,socket.CMSG_SPACE(12),socket.MSG_CMSG_CLOEXEC)
                    if not packet:break
                    self.assertEqual(flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC),0)
                    self.assertEqual(len(anc),1);self.assertEqual(anc[0][:2],(socket.SOL_SOCKET,socket.SCM_CREDENTIALS));self.assertEqual(struct.unpack('3i',anc[0][2]),(process.pid,os.getuid(),os.getgid()))
                    req=wire.decode(packet);blob=bytes(model.ready['data']) if model.ready else None
                    action=model.receive(packet,peer=model.peer)
                    result=None
                    if model.pending:
                        verb,target=action['verb'],action['target']
                        if verb=='BEGIN':package.mkdir(parents=True)
                        elif verb=='SEAL':
                            value=json.loads(blob)
                            for e in value[target]:e['event_digest']=sha(encoded(e))
                            result=encoded(value)
                        elif verb=='EMIT':write(package/target,blob)
                        elif verb=='COLD_READ':result=encoded({'authority_effect':'none','cut':{'semantic_cursor':25},'governance_cursor':25,'governed_nodes':[{'fixture_only':True} for _ in range(15)]})
                        model.complete_synthetic(action['action_id'],success=True)
                    if result is None:a.send(reply(req,{'kind':'ACK'}))
                    else:bytes_reply(a,req,result)
                out,err=process.communicate(timeout=15)
            except BaseException:
                process.kill();out,err=process.communicate();raise
            evidence=Path(os.environ['MAPPER_FIXTURE_EVIDENCE'])/('postimage-drift' if mutation else 'full-builder')
            evidence.mkdir()
            for name in ('preimage.py','build.py','config.json','selection.json'):
                write(evidence/name,(root/name).read_bytes())
            write(evidence/'child.stdout',out);write(evidence/'child.stderr',err)
            write(evidence/'observation.json',encoded({'argv':command,'os_exit':process.returncode,'elapsed_seconds':time.monotonic()-started,'trace':model.trace,'step':model.step,'adapter_record':record,'fixture_only':True,'native_processes':0,'protected_reads':0}))
            if package.exists():shutil.copytree(package,evidence/'synthetic-package')
            if mutation:
                self.assertEqual(process.returncode,1,(out,err));self.assertEqual(model.step,0);self.assertFalse(package.exists());return
            self.assertEqual(process.returncode,0,(out,err));self.assertEqual(model.step,61)
            self.assertEqual([(r['verb'],r['target']) for r in model.trace],wire.schedule())
            files=sorted(p for p in package.rglob('*') if p.is_file());self.assertEqual(len(files),55)
            mapping=json.loads((package/'mapping.json').read_bytes());self.assertEqual(len(mapping['rows']),25)
            self.assertEqual(sum(r['subject_identity']['subject_kind']=='node' for r in mapping['rows']),15)
            self.assertEqual(sum(r['subject_identity']['subject_kind']=='relation' for r in mapping['rows']),10)
            self.assertEqual(len(json.loads((package/'manifest.json').read_bytes())['files']),54)
            for row in rows:self.assertEqual(binding(row['path']),row)
            self.assertEqual(record['projection']['nodes'],15)
            self.assertIn(b'"native_processes": 0',out)

    def test_full_historical_projection_over_fd3(self):self.run_builder()
    def test_coherent_postimage_repin_refuses_before_begin(self):self.run_builder('selected-postimage-drift')
