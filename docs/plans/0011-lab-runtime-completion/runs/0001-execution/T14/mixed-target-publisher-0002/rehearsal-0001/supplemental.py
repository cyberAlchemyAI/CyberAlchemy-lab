"""Actual owned filesystem process/signal rehearsal; no Lab native runtime."""
import datetime,hashlib,json,os,select,signal,stat,subprocess,sys,time,types,uuid
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');CANDIDATE=HERE.parent
I=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
sys.path.append(str(I/'deps'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(obj):return (json.dumps(obj,sort_keys=True,indent=2)+'\n').encode()
def put(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
if sha(Path(__file__).read_bytes())!=sys.argv[1]:raise ValueError('independent supplemental code pin differs')
G=types.ModuleType('_owned_rehearsal_guard');G.__file__=str(HERE/'guard.py');raw=(HERE/'guard.py').read_bytes();exec(compile(raw,G.__file__,'exec'),G.__dict__)
GUARD=sha(raw);SELECTION=sha((HERE/'rehearsal-selection.json').read_bytes());G.SELF_SELECTION=HERE/'rehearsal-selection.json';G.SELF_PIN=SELECTION
captured=G.verify();entry=G.LAST
package_name='_T14_plan_'+uuid.uuid4().hex;package=types.ModuleType(package_name);package.__path__=[];sys.modules[package_name]=package
path=CANDIDATE/'typed_targets.py';T=types.ModuleType(package_name+'.typed_targets');T.__package__=package_name;T.__file__=str(path);sys.modules[T.__name__]=T
exec(compile(captured[str(path.relative_to(ROOT))],str(path),'exec'),T.__dict__)
selected=T.parse(captured[str((CANDIDATE/'public-schema-example-selection.json').relative_to(ROOT))]);items=[]
for row in selected['rows']:
    raw=captured[row['public_original_fixture']['path']];schema=captured[row['schema']['path']]
    descriptor=captured[row['carrier_binding']['path']]
    schemas=T.OriginalSchemas([row['schema']],{row['schema']['path']:schema},carrier_bindings=[row['carrier_binding']],raw_carriers={row['carrier_binding']['path']:descriptor})
    spec={k:row[k] for k in ['family','category','carrier_ref','schema_selector','identity_selector','identity_ref']};spec.update(schema_path=row['schema']['path'],raw_sha256=T.sha(raw))
    items.append({'output_path':'targets/'+row['family']+'.json','adapted':T.adapt(raw,spec,schemas)})
bundle_id='owned-seven-public-families';prepared=T.prepare_byte_bundle(items,bundle_id,schema_binding_sha256=T.sha(captured[str((CANDIDATE/'public-schema-example-selection.json').relative_to(ROOT))]))
stage='.'+bundle_id+'-stage-'+prepared['pins']['bundle_sha256'];commit=bundle_id+'.commit.json';cases=[];roots=[];processes=[];ledger=HERE/'supplemental-parent-ledger.jsonl'
ledgerfd=os.open(ledger,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
def record(kind,**values):
    row={'kind':kind,'parent_pid':os.getpid(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'monotonic_ns':time.monotonic_ns(),**values}
    os.write(ledgerfd,(json.dumps(row,sort_keys=True)+'\n').encode());os.fsync(ledgerfd)

def newroot(label):
    root=Path('/tmp')/('cal-T14-publisher-'+label+'-'+uuid.uuid4().hex);os.mkdir(root,0o700);put(root/'publisher.lock',b'')
    roots.append(str(root));s=root.stat();identity=(s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode));record('owned-root-created',root=str(root),identity=identity);return root,identity

def launch(root,identity,label,operation='publish',checkpoint=None):
    config={'root':str(root),'root_identity':identity,'bundle_id':bundle_id,'operation':operation,'checkpoint':checkpoint,'independent_pins':prepared['pins']}
    path=HERE/(label+'-config.json');put(path,encoded(config))
    args=[str(I/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(I/'lib/abi'),str(I/'bin/python'),'-I','-X','utf8','-B','-S',str(HERE/'worker.py'),GUARD,SELECTION,str(path),sha(path.read_bytes())]
    p=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env={'LC_ALL':'C','PATH':'/usr/bin:/bin'})
    processes.append(p);record('process-started',label=label,pid=p.pid,args=args,config_sha256=sha(path.read_bytes()))
    return p,path

def awaitcheckpoint(p,label):
    deadline=time.monotonic()+60
    while time.monotonic()<deadline:
        ready=select.select([p.stdout],[],[],min(2,deadline-time.monotonic()))[0]
        if not ready:
            if p.poll() is not None:break
            continue
        line=p.stdout.readline()
        if not line:break
        row=json.loads(line)
        if row.get('kind')=='checkpoint':
            assert row['label']==label;record('actual-checkpoint-observed',pid=p.pid,label=label);return row
        raise AssertionError('terminal before checkpoint '+json.dumps(row))
    raise AssertionError('checkpoint absent '+str(p.pid))

def terminal(p,path,kill=False):
    if kill:
        record('SIGKILL-dispatched',pid=p.pid,signal=signal.SIGKILL);os.kill(p.pid,signal.SIGKILL)
    stdout,stderr=p.communicate(timeout=60)
    obs={'pid':p.pid,'exit_code':p.returncode,'observed_SIGKILL':p.returncode==-signal.SIGKILL,
         'stdout_sha256':sha(stdout.encode()),'stderr_sha256':sha(stderr.encode()),'stderr_nonempty':bool(stderr)}
    eventpath=path.parent/(path.stem+'-events.jsonl');events=[json.loads(row) for row in eventpath.read_bytes().splitlines()]
    obs['durable_events']={'path':str(eventpath),'sha256':sha(eventpath.read_bytes()),'count':len(events)}
    result=next((row['result'] for row in reversed(events) if row['kind']=='process-result'),None)
    guards=[row for row in events if row['kind'].startswith('full-guard')]
    obs.update(result=result,guards=guards,process_cleanup=next((row for row in reversed(events) if row['kind']=='process-result'),None))
    record('process-terminal-observed',**obs);return obs

def run(root,identity,label,operation='publish'):
    p,path=launch(root,identity,label,operation);return terminal(p,path)
def files(root):
    return sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and not p.is_symlink())
def savecase(row):
    cases.append(row);put(HERE/(row['case']+'-result.json'),encoded(row));print(json.dumps({'case':row['case'],'outcome':row['outcome']}),flush=True)

record('supplemental-rehearsal-start',full_guard=entry,scope='actual selected owned-byte races only',actual_native_or_owner_or_admission=False)
try:
    for label,mutatebytes in [('samebyte-leaf',False),('differentbyte-leaf',True)]:
        root,identity=newroot(label);p,path=launch(root,identity,label,checkpoint='pre-link');awaitcheckpoint(p,'pre-link')
        leaf=root/stage/'targets/typed-relation.json';retained=root/'retained-selected-public-leaf.json';original=leaf.read_bytes();os.rename(leaf,retained)
        put(leaf,b'{"inert_marker":true}\n' if mutatebytes else original)
        p.stdin.write('continue\n');p.stdin.flush();observed=terminal(p,path);assert observed['result']['state']=='uncertain-commit-inspection-required'
        cold=run(root,identity,label+'-cold','inspect');assert ('refused_exception_class' in cold['result'])==mutatebytes
        assert (root/commit).read_bytes()==prepared['files']['technical-receipt.json'] and retained.read_bytes()==original
        savecase({'case':label+'-after-last-check','outcome':'PASS-live-refusal-cold-independent-byte-result','root':str(root),'processes':[observed,cold],'cold_exact_bytes_succeeded':not mutatebytes,'same_physical_original_inferred':False})
    root,identity=newroot('prelink-root');p,path=launch(root,identity,'prelink-root',checkpoint='pre-link');awaitcheckpoint(p,'pre-link')
    retained=Path(str(root)+'-retained');os.rename(root,retained);os.mkdir(root,0o700);put(root/'publisher.lock',b'');roots.append(str(retained))
    p.stdin.write('continue\n');p.stdin.flush();observed=terminal(p,path)
    assert observed['result']['state']=='uncertain-commit-inspection-required' and not (root/commit).exists() and (retained/commit).read_bytes()==prepared['files']['technical-receipt.json']
    savecase({'case':'prelink-root-attachment-swap','outcome':'PASS-held-original-root-only-new-root-untouched','root':str(root),'retained':str(retained),'processes':[observed]})
    root,identity=newroot('postlink-receipt');p,path=launch(root,identity,'postlink-receipt',checkpoint='post-link');awaitcheckpoint(p,'post-link')
    retained=root/'retained-selected-receipt.json';os.rename(root/commit,retained);put(root/commit,b'{"inert_marker":true}\n');foreign_inode=(root/commit).stat().st_ino
    p.stdin.write('continue\n');p.stdin.flush();observed=terminal(p,path);cold=run(root,identity,'postlink-receipt-cold','inspect')
    assert observed['result']['state']=='uncertain-commit-inspection-required' and 'refused_exception_class' in cold['result'] and (root/commit).stat().st_ino==foreign_inode and retained.read_bytes()==prepared['files']['technical-receipt.json']
    savecase({'case':'postlink-receipt-destination-replacement','outcome':'PASS-uncertainty-foreign-receipt-retained-cold-refused','root':str(root),'processes':[observed,cold]})
    root,identity=newroot('postlink-exception');p,path=launch(root,identity,'postlink-exception',checkpoint='post-link');awaitcheckpoint(p,'post-link')
    p.stdin.write('observer-stop\n');p.stdin.flush();observed=terminal(p,path);cold=run(root,identity,'postlink-exception-cold','inspect')
    assert observed['result']['state']=='uncertain-commit-inspection-required' and 'refused_exception_class' not in cold['result']
    savecase({'case':'actual-commit-before-python-bookkeeping-exception','outcome':'PASS-uncertainty-classified-cold-exact-bytes','root':str(root),'processes':[observed,cold],'exception_from_new_observer_only':True})
except BaseException as exc:
    record('supplemental-harness-failure',exception_class=type(exc).__name__)
    for p in processes:
        if p.poll() is None:os.kill(p.pid,signal.SIGKILL);p.communicate(timeout=20);record('failure-cleanup-terminal',pid=p.pid,exit_code=p.returncode)
    raise
finally:
    G.verify();exitguard=G.LAST;record('supplemental-final-guard',full_guard=exitguard);os.close(ledgerfd)
report={'schema_version':'lab-T14-supplemental-owned-receipt-boundaries/v2-candidate','result':'PASS-scoped-controls-independent-review-pending','cases':cases,'case_count':len(cases),'full_guard_entry':entry,'full_guard_exit':exitguard,'retained_owned_roots':roots,'source_manifest_sha256':G.MFPIN,'rehearsal_worker_selection_sha256':SELECTION,'supplemental_code_sha256':sha(Path(__file__).read_bytes()),'ordinary_process_filesystem_only':True,'power_failure_or_perpetual_immutability_not_proven':True,'native_history_owner_admission_or_complete_T14':False,'authority_effect':'none'}
put(HERE/'supplemental-result.json',encoded(report));print(json.dumps({'cases':len(cases),'result_sha256':sha((HERE/'supplemental-result.json').read_bytes())}),flush=True)
