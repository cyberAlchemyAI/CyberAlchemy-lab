import ast,hashlib,json,pathlib,sys,types,unittest
D=pathlib.Path(__file__).parent;L=D.parent;C=L/'context-policy-topology-0002';P=L/'context-policy-topology-0001'
h=lambda b:hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
raw=(C/'freeze.json').read_bytes();need(h(raw)=='2c6e5ab3ccb94d5709b585d1307b30f47c101bed5b456db6638c0a333e61839c','FREEZE')
f=json.loads(raw);pins={str(C/'freeze.json'):h(raw)}
for name,pin in f['bindings'].items():need(h((C/name).read_bytes())==pin,'MEMBER');pins[str(C/name)]=pin
need(h((L/'CONTEXT-POLICY-TOPOLOGY-INDEPENDENT-STATIC-REVIEW-0001.md').read_bytes())==f['predecessor_hold_review_sha256'],'HOLD')
need(h((P/'freeze.json').read_bytes())==f['predecessor_freeze_sha256'],'PREDECESSOR')
def audit(event,args):
 if event=='open' and isinstance(args[0],(str,bytes)) and str(args[0]).endswith('branch.snapshot'):raise RuntimeError('NO_ARCHIVE')
 if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.fork','os.exec'):raise RuntimeError('NO_EFFECT')
sys.addaudithook(audit)
a=types.ModuleType('selected');a.__file__=str(C/'adapter.py')
exec(compile((C/'adapter.py').read_bytes(),a.__file__,'exec'),a.__dict__)
t=types.ModuleType('tests');t.__file__=str(C/'test_adapter.py')
exec(compile((C/'test_adapter.py').read_bytes(),t.__file__,'exec'),t.__dict__)
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(t));need(r.wasSuccessful(),'AUTHOR_SUITE')
outputs={'projected-host-policy.py.txt':a.project_policy_guard('host'),'projected-child-policy.py.txt':a.project_policy_guard('child'),'projected-control.py.txt':a.project_control(),'projected-build.py.txt':a.project_build(),'projected-release-hooks.py.txt':a.project_release_hook()}
for name,raw in outputs.items():need(raw==(C/name).read_bytes()==(P/name).read_bytes(),'PROJECTION_IDENTITY')
for name,pin in a.PINS.items():need(h((L/name).read_bytes())==pin,'ORIGINAL')
# Only the two assigned state transition bodies may change.
def bodies(path):
 tree=ast.parse(path.read_bytes());return {n.name:ast.dump(n) for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
old=bodies(P/'adapter.py');new=bodies(C/'adapter.py');changed=[k for k in old if old[k]!=new[k]]
need(set(old)==set(new) and set(changed)=={'RetentionModel','ProofModel'},'DIFF_SCOPE')
def fixture():
 m=a.ProofModel(policy_sha='a'*64,expires_at='2026-10-20T18:20:00Z',attempt='fixture',peer=(42,1000,1000))
 request={'schema':'context-parent-proof-request/v1','attempt':'fixture','challenge':{'schema_version':'lab-context-host-challenge/v1-candidate','host_instance_ref':'host:R03-context:test','connection_ref':'connection:R03-context:test','nonce':'b'*64,'policy_sha256':'a'*64,'expires_at':m.expiry,'authority_effect':'none'}}
 return m,a.compact(request)
def refused(fn):
 try:fn()
 except a.Refused:return
 raise RuntimeError('EXPECTED_REFUSAL')
count=0
for case in ('empty','fields','invalidutf8','duplicate','oversize','peer','boolpeer','stale','policy'):
 m,valid=fixture();raw=valid;peer=(42,1000,1000);current=True
 if case=='empty':raw=b''
 elif case=='fields':raw=b'{}'
 elif case=='invalidutf8':raw=b'\xff'
 elif case=='duplicate':raw=b'{"schema":"x","schema":"y"}'
 elif case=='oversize':raw=b'x'*8193
 elif case=='peer':peer=(43,1000,1000)
 elif case=='boolpeer':peer=(True,1000,1000)
 elif case=='stale':current=False
 else:raw=raw.replace(b'a'*64,b'c'*64)
 refused(lambda:m.consume(raw,peer=peer,current=current));need(m.state=='UNKNOWN_CONSUMED','R01_STATE')
 refused(lambda:m.consume(valid,peer=(42,1000,1000),current=True));refused(m.sign);refused(m.restart);count+=1
for ordinal,empty,attached in ((37,True,True),(38,False,True),(38,True,False),(38.0,True,True),(False,True,True)):
 m=a.RetentionModel();m.closed_channel(channel_closed=True,local_proof_handle_dropped=True,policy_attached=True)
 refused(lambda:m.release_transport_scratch(ordinal,scratch_empty=empty,policy_attached=attached));need(m.state=='UNKNOWN' and m.unknown is True,'R02_STATE')
 refused(lambda:m.release_transport_scratch(38,scratch_empty=True,policy_attached=True));refused(m.result);refused(m.cleanup_effect);count+=1
m,raw=fixture();rec=m.consume(raw,peer=(42,1000,1000),current=True);m.durable(retained_request_sha=rec['request_sha256'],fsync_observed=True,current=True);need(m.state=='SIGN_ELIGIBLE_MODEL_ONLY','POSITIVE');refused(m.sign)
m=a.RetentionModel();m.closed_channel(channel_closed=True,local_proof_handle_dropped=True,policy_attached=True);m.release_transport_scratch(38,scratch_empty=True,policy_attached=True);need(m.result()['owned_host_policy_and_transport_key_removed'] is False,'RETAINED_POSITIVE');m.external_gate(os_exit=0,container_absent=True,final_closed=True,output_verified=True,independent_review=True,parent_key_dropped=True);need(m.state=='CLEANUP_ELIGIBLE_MODEL_ONLY','CLEANUP_POSITIVE');refused(m.cleanup_effect)
for p,pin in pins.items():need(h(pathlib.Path(p).read_bytes())==pin,'POSTDRIFT')
print(json.dumps({'verdict':'PASS_PURE_CORRECTION_ONLY','author_tests':r.testsRun,'independent_negative_sequences':count,'positive_sequences':2,'projection_identity_count':len(outputs),'changed_bodies':changed,'effect':'NOT_RUN','archive_body':'UNOPENED','pins':pins},sort_keys=True))
