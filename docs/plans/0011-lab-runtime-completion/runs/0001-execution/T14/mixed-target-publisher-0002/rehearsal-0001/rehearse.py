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
stage='.'+bundle_id+'-stage-'+prepared['pins']['bundle_sha256'];commit=bundle_id+'.commit.json';cases=[];roots=[];processes=[];ledger=HERE/'parent-ledger.jsonl'
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

record('rehearsal-start',full_guard=entry,scope='new owned ordinary-filesystem byte publisher only',actual_native_or_owner_or_admission=False)
try:
    root,identity=newroot('positive');positive=run(root,identity,'positive');cold=run(root,identity,'positive-cold','inspect');again=run(root,identity,'positive-republish')
    assert positive['result']['state']=='committed-technical-bytes' and again['result']['state']=='already-committed-technical-bytes';assert 'refused_exception_class' not in cold['result']
    savecase({'case':'positive-cold-repeat','outcome':'PASS-technical-byte-publication-only','root':str(root),'processes':[positive,cold,again],'pins':prepared['pins']})
    for point in ['before-stage','partial-stage','after-stage','pre-link','post-link','after-commit','after-verified']:
        root,identity=newroot('kill-'+point);p,path=launch(root,identity,'kill-'+point,checkpoint=point);awaitcheckpoint(p,point);killed=terminal(p,path,True)
        before=files(root);cold=run(root,identity,'kill-'+point+'-cold','inspect');after=files(root)
        assert killed['observed_SIGKILL'] and before==after
        committed=(root/commit).exists();coldsuccess='refused_exception_class' not in cold['result'];assert committed==coldsuccess
        replay=run(root,identity,'kill-'+point+'-replay');physical=files(root)
        if point=='partial-stage':assert replay['result']['state']=='uncommitted-residue-inspection-required' and physical==after
        else:assert replay['result']['state'] in ['committed-technical-bytes','already-committed-technical-bytes']
        savecase({'case':'kill-'+point,'outcome':'PASS-actual-signal-and-cold-byte-inspection-only','root':str(root),'processes':[killed,cold,replay],'files_before_cold':before,'files_after_cold':after,'partial_residue_preserved':point=='partial-stage','physical_final_at_cold':committed})
    root,identity=newroot('competing-final');p,path=launch(root,identity,'competing-final',checkpoint='pre-link');awaitcheckpoint(p,'pre-link')
    put(root/commit,b'{"inert_marker":true}\n');foreign=(root/commit).stat().st_ino
    p.stdin.write('continue\n');p.stdin.flush();observed=terminal(p,path);assert observed['result']['state']=='uncertain-commit-inspection-required' and (root/commit).stat().st_ino==foreign
    cold=run(root,identity,'competing-final-cold','inspect');assert 'refused_exception_class' in cold['result']
    savecase({'case':'competing-final-no-replace','outcome':'PASS-competitor-and-stage-retained','root':str(root),'processes':[observed,cold],'foreign_inode_retained':True})
    for mutation in ['root-anchor','stage-anchor','lock-leaf']:
        root,identity=newroot(mutation);p,path=launch(root,identity,mutation,checkpoint='after-stage');awaitcheckpoint(p,'after-stage');retained=None
        if mutation=='root-anchor':
            retained=Path(str(root)+'-retained');os.rename(root,retained);os.mkdir(root,0o700);put(root/'publisher.lock',b'');roots.append(str(retained))
        elif mutation=='stage-anchor':
            retained=root/(stage+'-retained');os.rename(root/stage,retained);os.mkdir(root/stage,0o700);put(root/stage/'inert-foreign.json',b'{"inert_marker":true}\n')
        else:
            retained=root/'publisher.lock-retained';os.rename(root/'publisher.lock',retained);put(root/'publisher.lock',b'')
        p.stdin.write('continue\n');p.stdin.flush();observed=terminal(p,path);assert observed['result']['state']=='uncommitted-residue-inspection-required' and not (root/commit).exists()
        savecase({'case':mutation+'-replacement','outcome':'PASS-refusal-and-owned-residue-retention','root':str(root),'retained':str(retained),'processes':[observed]})
    root,identity=newroot('postcheck-stage-swap');p,path=launch(root,identity,'postcheck-stage-swap',checkpoint='pre-link');awaitcheckpoint(p,'pre-link')
    retained=root/(stage+'-retained');os.rename(root/stage,retained);os.mkdir(root/stage,0o700);put(root/stage/'inert-foreign.json',b'{"inert_marker":true}\n');foreign_inode=(root/stage).stat().st_ino
    p.stdin.write('continue\n');p.stdin.flush();observed=terminal(p,path)
    assert observed['result']['state']=='uncertain-commit-inspection-required' and (root/stage).stat().st_ino==foreign_inode and not (root/bundle_id).exists()
    assert (root/commit).read_bytes()==prepared['files']['technical-receipt.json'] and retained.exists()
    cold=run(root,identity,'postcheck-stage-swap-cold','inspect');assert 'refused_exception_class' in cold['result']
    savecase({'case':'postcheck-stage-source-swap','outcome':'PASS-selected-receipt-only-foreign-source-never-moved-cold-refused','root':str(root),'retained':str(retained),'processes':[observed,cold],'foreign_source_inode_retained':True,'exact_receipt_committed':True,'whole_body_success_claimed':False})
    root,identity=newroot('receipt');positive=run(root,identity,'receipt-positive');receipt=root/commit
    prior=receipt.read_bytes();changed=json.loads(prior);changed['actual_owner_outcome']='inert-forbidden-claim';receipt.write_bytes(encoded(changed));os.chmod(receipt,0o600)
    cold=run(root,identity,'receipt-mutated-cold','inspect');assert 'refused_exception_class' in cold['result']
    savecase({'case':'cold-whole-receipt-mutation','outcome':'PASS-whole-independent-receipt-refused','root':str(root),'original_receipt_sha256':sha(prior),'mutated_receipt_sha256':sha(receipt.read_bytes()),'processes':[positive,cold]})
    root,identity=newroot('foreign-residue');positive=run(root,identity,'foreign-positive');put(root/stage/'foreign.json',b'{"inert_marker":true}\n');before=files(root);cold=run(root,identity,'foreign-cold','inspect');assert 'refused_exception_class' in cold['result'] and files(root)==before
    savecase({'case':'cold-foreign-residue','outcome':'PASS-unknown-residue-preserved-and-refused','root':str(root),'processes':[positive,cold]})
    root,identity=newroot('lock-contention');p,path=launch(root,identity,'lock-owner',checkpoint='after-stage');awaitcheckpoint(p,'after-stage');contender=run(root,identity,'lock-contender');assert 'refused_exception_class' in contender['result']
    p.stdin.write('continue\n');p.stdin.flush();owner=terminal(p,path);assert owner['result']['state']=='committed-technical-bytes'
    savecase({'case':'actual-concurrent-owned-lock','outcome':'PASS-exclusive-owned-publisher-lock-only','root':str(root),'processes':[owner,contender]})
except BaseException as exc:
    record('harness-failure',exception_class=type(exc).__name__)
    for p in processes:
        if p.poll() is None:
            os.kill(p.pid,signal.SIGKILL);p.communicate(timeout=20);record('failure-cleanup-terminal',pid=p.pid,exit_code=p.returncode)
    raise
finally:
    G.verify();exitguard=G.LAST;record('rehearsal-final-guard',full_guard=exitguard);os.close(ledgerfd)
report={'schema_version':'lab-T14-owned-filesystem-rehearsal/v1-candidate','result':'PASS-scoped-descriptor-receipt-controls-independent-review-pending',
        'authority_effect':'none','task_complete':False,'frozen_candidate_manifest_sha256':G.MFPIN,'rehearsal_selection_sha256':SELECTION,
        'dependency_selection_sha256':G.DEPPIN,'full_guard_entry':entry,'full_guard_exit':exitguard,'case_count':len(cases),'cases':cases,
        'all_owned_roots_retained':roots,'old_source_directory_rename_not_present':True,'independent_successor_review_pending':True,
        'no_native_Store_Service_Session_ProtectedReader_or_global_lease_runtime_lock':True,
        'no_original_publisher_full_native_body_event_owner_or_363_family_qualification':True,'actual_owner_or_admission':False,
        'ledger':{'path':str(ledger),'sha256':sha(ledger.read_bytes())}}
put(HERE/'rehearsal-result.json',encoded(report));print(json.dumps({'cases':len(cases),'result_sha256':sha((HERE/'rehearsal-result.json').read_bytes())}),flush=True)
