"""Real selected byte-publisher process. Observer controls only owned code boundaries."""
import base64,datetime,hashlib,json,os,stat,sys,time,types,uuid
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');CANDIDATE=HERE.parent
I=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
sys.path.append(str(I/'deps'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bootstrap(path,pin):
    # Explicit startup capture of this new guard, never an existing callback patch.
    raw=path.read_bytes()
    if path.is_symlink() or sha(raw)!=pin:raise ValueError('guard startup selection')
    module=types.ModuleType('_T14_rehearsal_guard_'+uuid.uuid4().hex);module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__);return module
G=bootstrap(HERE/'guard.py',sys.argv[1]);G.SELF_SELECTION=HERE/'rehearsal-selection.json';G.SELF_PIN=sys.argv[2]
config_path=Path(sys.argv[3]);config=json.loads(G.capture(config_path,sys.argv[4]));event_path=config_path.parent/(config_path.stem+'-events.jsonl')
event_fd=os.open(event_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
def event(kind,**values):
    row={'kind':kind,'pid':os.getpid(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'monotonic_ns':time.monotonic_ns(),**values}
    raw=(json.dumps(row,sort_keys=True)+'\n').encode();os.write(event_fd,raw);os.fsync(event_fd);return row

def checkpoint(label):
    row=event('checkpoint',label=label);print(json.dumps(row),flush=True)
    command=sys.stdin.readline().strip()
    if command!='continue':raise RuntimeError('rehearsal checkpoint command refused')

pub=None;tool=5;registered=False;out=None;phase='entry';beforefds=None
try:
    captured=G.verify();event('full-guard-entry',counts=G.LAST)
    namespace='_T14_actual_owned_'+uuid.uuid4().hex
    package=types.ModuleType(namespace);package.__path__=[];package.__file__=str(CANDIDATE/'__init__.py');sys.modules[namespace]=package
    for leaf in ['typed_targets','publisher']:
        path=CANDIDATE/(leaf+'.py');raw=captured[str(path.relative_to(ROOT))]
        m=types.ModuleType(namespace+'.'+leaf);m.__package__=namespace;m.__file__=str(path);sys.modules[m.__name__]=m
        exec(compile(raw,str(path),'exec'),m.__dict__);setattr(package,leaf,m)
    T=package.typed_targets;P=package.publisher
    selection=T.parse(captured[str((CANDIDATE/'public-schema-example-selection.json').relative_to(ROOT))]);items=[]
    for row in selection['rows']:
        raw=captured[row['public_original_fixture']['path']];schema=captured[row['schema']['path']]
        bindings=T.OriginalSchemas([row['schema']],{row['schema']['path']:schema})
        spec={k:row[k] for k in ['family','category','carrier_ref','schema_selector','identity_selector','identity_ref']}
        spec.update(schema_path=row['schema']['path'],raw_sha256=T.sha(raw))
        items.append({'output_path':'targets/'+row['family']+'.json','adapted':T.adapt(raw,spec,bindings)})
    prepared=T.prepare_byte_bundle(items,config['bundle_id'],schema_binding_sha256=T.sha(captured[str((CANDIDATE/'public-schema-example-selection.json').relative_to(ROOT))]))
    event('prepared',pins=prepared['pins'],expected_paths=sorted(prepared['files']),families=[r['family'] for r in selection['rows']])
    beforefds=len(os.listdir('/proc/self/fd'));root=Path(config['root'])
    pub=P.OwnedBytePublisher(root,tuple(config['root_identity']),G.verify,{'path':str(HERE/'guard.py'),'sha256':sys.argv[1]},purpose='owned-technical-rehearsal')
    source=captured[str((CANDIDATE/'publisher.py').relative_to(ROOT))].decode().splitlines()
    lines={}
    for n,line in enumerate(source,1):
        if "self.live_guard();stage=" in line:lines[n]='before-stage'
        if "verify_byte_bundle(self.snapshot(base,expected_paths),expected_pins);self.live_guard()" in line:lines[n]='after-stage'
        if "if fn(self.fd" in line:lines[n]='pre-rename'
        if "committed=True;os.fsync" in line:lines[n]='post-rename'
        if "verify_byte_bundle(self.snapshot(base,expected_paths),expected_pins);self.check()" in line:lines[n]='after-commit'
        if "return {'state':'committed-technical-bytes'" in line:lines[n]='after-verified'
    fired=set();write_count=[0]
    def line_observer(code,line):
        if code is P.OwnedBytePublisher.publish.__code__:
            label=lines.get(line)
            if label and label not in fired:
                fired.add(label)
                if label==config.get('checkpoint'):checkpoint(label)
    def return_observer(code,offset,retval):
        # The observer never serializes retval, arguments, locals, or body bytes.
        if code is P.OwnedBytePublisher.write.__code__:
            write_count[0]+=1
            if write_count[0]==1 and config.get('checkpoint')=='partial-stage':checkpoint('partial-stage')
    sys.monitoring.use_tool_id(tool,'T14-owned-boundary-observer');registered=True
    sys.monitoring.register_callback(tool,sys.monitoring.events.LINE,line_observer)
    sys.monitoring.register_callback(tool,sys.monitoring.events.PY_RETURN,return_observer)
    sys.monitoring.set_local_events(tool,P.OwnedBytePublisher.publish.__code__,sys.monitoring.events.LINE)
    sys.monitoring.set_local_events(tool,P.OwnedBytePublisher.write.__code__,sys.monitoring.events.PY_RETURN)
    phase='actual-owned-byte-'+config['operation']
    if config['operation']=='publish':out=pub.publish(prepared,prepared['pins'])
    elif config['operation']=='inspect':out=pub.inspect_committed(config['bundle_id'],prepared['pins'],tuple(prepared['files']))
    else:raise ValueError('unselected operation')
    event('operation-result',result=out)
except BaseException as exc:
    out={'refused_exception_class':type(exc).__name__,'phase':phase};event('operation-refusal',result=out)
finally:
    if registered:
        sys.monitoring.set_events(tool,0)
        for code in [P.OwnedBytePublisher.publish.__code__,P.OwnedBytePublisher.write.__code__]:sys.monitoring.set_local_events(tool,code,0)
        for kind in [sys.monitoring.events.LINE,sys.monitoring.events.PY_RETURN]:sys.monitoring.register_callback(tool,kind,None)
        sys.monitoring.free_tool_id(tool)
    if pub:pub.close()
    try:G.verify();event('full-guard-exit',counts=G.LAST)
    except BaseException as exc:event('full-guard-exit-refusal',exception_class=type(exc).__name__)
    event('process-result',result=out,publisher_closed=bool(pub and pub.closed and not pub.fds),
          descriptor_delta=None if beforefds is None else len(os.listdir('/proc/self/fd'))-beforefds,
          authority_effect='none',actual_native_or_owner_or_admission=False)
    os.close(event_fd)
print(json.dumps({'kind':'terminal-result','pid':os.getpid(),'result':out}),flush=True)
