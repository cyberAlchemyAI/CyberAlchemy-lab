"""Independent successor source/evidence audit and fresh ordinary FS probes only."""
import argparse,hashlib,json,os,stat,sys,tempfile,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
C=RUN/'T14/mixed-target-publisher-0002';HERE=Path(__file__).parent
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
MF='1de86d256f516fe7d14556fa7f8a0432d31575a73fb3c9b02745c13c3388eca2'
GUARD='5b93da5536db5c2121519095faa050fdf128051d64bf44fc2dd1a9651daae439'
RSEL='65db62bd0c3f77834c46bda13dd7b5292e03c2adf2a42856ac8c95c108d589b3'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bootstrap(path,pin):
    fds=[];links=[]
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);fds.append(parent)
        for name in path.parts[1:-1]:
            fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent);fds.append(fd)
            links.append((parent,name,fd,os.fstat(fd)));parent=fd
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent);fds.append(fd)
        before=os.fstat(fd);assert stat.S_ISREG(before.st_mode) and before.st_size<16*1024*1024
        raw=b''
        while piece:=os.read(fd,1024*1024):raw+=piece;assert len(raw)<=before.st_size
        stamp=lambda s:(s.st_dev,s.st_ino,s.st_uid,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        assert stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False))
        for p,n,h,s in links:
            current=os.stat(n,dir_fd=p,follow_symlinks=False)
            assert stat.S_ISDIR(current.st_mode) and (current.st_dev,current.st_ino)==(s.st_dev,s.st_ino)
        assert sha(raw)==pin;return raw
    finally:
        for fd in reversed(fds):os.close(fd)
args=argparse.ArgumentParser();args.add_argument('--probe-sha256',required=True);a=args.parse_args()
assert sha(Path(__file__).read_bytes())==a.probe_sha256
G=types.ModuleType('_T14_independent_successor_guard');G.__file__=str(C/'rehearsal-0001/guard.py')
exec(compile(bootstrap(Path(G.__file__),GUARD),G.__file__,'exec'),G.__dict__)
G.SELF_SELECTION=C/'rehearsal-0001/rehearsal-selection.json';G.SELF_PIN=RSEL
captured=G.verify();entry=dict(G.LAST);assert entry['source_rows']==80 and entry['installed_dependency_rows']==1010
sys.path.append(str(INSTALL/'deps'))
namespace='_T14_independent_successor_exact';package=types.ModuleType(namespace);package.__path__=[];sys.modules[namespace]=package
for leaf in ['typed_targets','publisher']:
    path=C/(leaf+'.py');module=types.ModuleType(namespace+'.'+leaf);module.__package__=namespace;module.__file__=str(path);sys.modules[module.__name__]=module
    exec(compile(captured[str(path.relative_to(ROOT))],str(path),'exec'),module.__dict__);setattr(package,leaf,module)
T=package.typed_targets;P=package.publisher
selected=T.parse(captured[str((C/'public-schema-example-selection.json').relative_to(ROOT))])
items=[];carrier_controls=[]
for row in selected['rows']:
    raw=captured[row['public_original_fixture']['path']];document=captured[row['schema']['path']];carrier=captured[row['carrier_binding']['path']]
    schemas=T.OriginalSchemas([row['schema']],{row['schema']['path']:document},carrier_bindings=[row['carrier_binding']],raw_carriers={row['carrier_binding']['path']:carrier})
    spec={k:row[k] for k in ['family','category','carrier_ref','schema_selector','identity_selector','identity_ref']};spec.update(schema_path=row['schema']['path'],raw_sha256=sha(raw))
    adapted=T.adapt(raw,spec,schemas);items.append({'output_path':'targets/'+row['family']+'.json','adapted':adapted})
    if row['family']=='typed-relation':
        for label,bad in [('wrong-version',{**spec,'carrier_ref':'cal.artifact-type.typed-relation/v999'}),('wrong-schema',{**spec,'schema_path':selected['rows'][0]['schema']['path']}),('wrong-fragment',{**spec,'schema_selector':'#/properties/kind'})]:
            try:T.adapt(raw,bad,schemas)
            except T.Refusal:carrier_controls.append({'case':label,'result':'REFUSED'})
            else:raise AssertionError(label+' incorrectly accepted')
    if row['family']=='registry-descriptor':
        try:T.adapt(raw,{**spec,'schema_selector':None},schemas)
        except T.Refusal:carrier_controls.append({'case':'registry-row-as-full-descriptor','result':'REFUSED'})
        else:raise AssertionError('registry distinction lost')
prepared=T.prepare_byte_bundle(items,'independent-successor-seven',schema_binding_sha256=sha(captured[str((C/'public-schema-example-selection.json').relative_to(ROOT))]))
pins=dict(prepared['pins']);guard_binding={'path':G.__file__,'sha256':GUARD};roots=[]
def put(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:os.write(fd,raw);os.fsync(fd)
    finally:os.close(fd)
def root():
    path=Path(tempfile.mkdtemp(prefix='cal-T14-publisher-independent-v2-'));path.chmod(0o700);put(path/'publisher.lock',b'');roots.append(str(path));return path
def publisher(path):return P.OwnedBytePublisher(path,P.ident(path.stat()),G.verify,guard_binding,purpose='owned-technical-rehearsal')
def cold(path):
    pub=publisher(path)
    try:return pub.inspect_committed('independent-successor-seven',pins,prepared['files'])
    finally:pub.close()
beforefds=len(os.listdir('/proc/self/fd'));baseline_root=root();pub=publisher(baseline_root)
try:baseline=pub.publish(prepared,pins)
finally:pub.close()
assert baseline['state']=='committed-technical-bytes';baseline_cold=cold(baseline_root);assert baseline_cold['technical_byte_closure_verified']
assert len(os.listdir('/proc/self/fd'))==beforefds
armed={'callback':None}
def observe(event,args):
    if event=='ctypes.dlopen' and args==(None,) and armed['callback'] is not None:
        callback=armed['callback'];armed['callback']=None;callback()
sys.addaudithook(observe)
race_results=[]
for scenario in ['late-foreign-stage','late-competing-receipt']:
    path=root();stage='.'+'independent-successor-seven'+'-stage-'+pins['bundle_sha256'];record='independent-successor-seven.commit.json'
    foreign=path/'foreign-pending';retained=path/'original-selected-stage-retained'
    if scenario=='late-foreign-stage':foreign.mkdir(mode=0o700);put(foreign/'inert-canary.bin',b'independent inert foreign marker');foreign_inode=foreign.stat().st_ino
    sr,sw=os.pipe();ar,aw=os.pipe();peer=os.fork()
    if peer==0:
        try:
            os.close(sw);os.close(ar);assert os.read(sr,1)==b'G'
            if scenario=='late-foreign-stage':os.rename(path/stage,retained);os.rename(foreign,path/stage)
            else:put(path/record,b'independent foreign receipt marker')
            os.write(aw,b'A');os._exit(0)
        except BaseException:os.write(aw,b'F');os._exit(1)
    os.close(sr);os.close(aw)
    def signal_peer():os.write(sw,b'G');assert os.read(ar,1)==b'A'
    armed['callback']=signal_peer;pub=publisher(path)
    try:outcome=pub.publish(prepared,pins)
    finally:pub.close()
    _,status=os.waitpid(peer,0);os.close(sw);os.close(ar)
    assert os.waitstatus_to_exitcode(status)==0 and armed['callback'] is None
    assert outcome['state']=='uncertain-commit-inspection-required' and outcome['automatic_retry'] is False
    try:cold_result=cold(path)
    except (T.Refusal,FileNotFoundError):cold_result={'result':'REFUSED'}
    else:raise AssertionError('foreign source/destination cold inspection accepted')
    if scenario=='late-foreign-stage':
        assert (path/stage).stat().st_ino==foreign_inode and (path/stage/'inert-canary.bin').read_bytes()==b'independent inert foreign marker'
        assert retained.is_dir() and not (path/'independent-successor-seven').exists()
        assert (path/record).read_bytes()==prepared['files']['technical-receipt.json']
    else:assert (path/record).read_bytes()==b'independent foreign receipt marker'
    assert len(os.listdir('/proc/self/fd'))==beforefds
    race_results.append({'case':scenario,'peer_exit_code':0,'live_result':outcome,'cold_result':cold_result,'unknown_residue_preserved':True,'foreign_source_namespace_renamed_into_committed_bundle':False,'original_component_callbacks_or_libc_mutated':False})

# Audit every externally selected author evidence byte, including its process events.
qualification=T.parse(G.capture(C/'rehearsal-0001/qualification.json','29a2ac09981c2321103b14794d96c70b430c6e129cbeb6bc2cc4b109074e399a'))
evidence=T.parse(G.capture(C/'rehearsal-0001/evidence-selection.json','5b0157be76ec4f3d5cb5eddcdc7709ccda560b52ddbb05aca2ae8ef03514cc0b'))
evidence_bytes={}
for row in evidence['files']:
    p=Path(row['path']);p=p if p.is_absolute() else ROOT/p
    evidence_bytes[str(p)]=G.capture(p,row['sha256'],size=row['size_bytes'])
main=T.parse(G.capture(C/'rehearsal-0001/rehearsal-result.json','99f969e9e271d1b5d942fd1e2548add0bac811d9583b4ec7ddc80f1933c4fc63'))
supplement=T.parse(G.capture(C/'rehearsal-0001/supplemental-result.json','349cdf6bef760f78a08847d8db913e70b3c4c70a545c90ce6b84fef80415fc32'))
processes=[p for case in main['cases']+supplement['cases'] for p in case['processes']]
assert len(main['cases'])==16 and len(supplement['cases'])==5 and len(processes)==46
assert len({p['pid'] for p in processes})==46
assert sum(p['exit_code']==-9 for p in processes)==7 and sum(p['exit_code']==0 for p in processes)==39
for p in processes:
    if p['exit_code']==-9:assert p['observed_SIGKILL'];continue
    assert p['process_cleanup']['descriptor_delta']==0 and p['process_cleanup']['publisher_closed']
    assert {x['kind'] for x in p['guards']}=={'full-guard-entry','full-guard-exit'}
    for g in p['guards']:assert g['counts']['source_rows']==80 and g['counts']['installed_dependency_rows']==1010
    ev=p['durable_events'];raw=G.capture(Path(ev['path']),ev['sha256']);assert len(raw.splitlines())==ev['count']
assert qualification['task_complete'] is False and qualification['actual_owner_or_admission'] is False
exit_software=G.verify();exit_guard=dict(G.LAST);assert captured==exit_software and entry==exit_guard
assert sha(Path(__file__).read_bytes())==a.probe_sha256
out={'schema_version':'lab-T14-independent-successor-FS-review-evidence/v2-candidate','result':'PASS-owned-FS-component-only','carrier_controls':carrier_controls,'baseline_publish':baseline,'baseline_independent_cold_inspection':baseline_cold,'real_OS_peer_boundary_probes':race_results,'dependency_source_entry':entry,'dependency_source_exit':exit_guard,'author_evidence_rows_verified':len(evidence['files']),'author_cases':21,'author_processes':46,'author_SIGKILL':7,'author_completed_guarded_children':39,'own_real_OS_peers':2,'own_descriptor_delta':len(os.listdir('/proc/self/fd'))-beforefds,'all_fresh_owned_roots_retained':True,'root_locator_sha256s':[sha(p.encode()) for p in roots],'concurrent_load':'Root full-learning positive session 81567 was running while this ordinary filesystem review executed. No latency inference or Lab lease acquired.','actual_Lab_native_Service_Session_ProtectedReader_or_global_lock':False,'original_component_callbacks_or_libc_modified':False,'authority_effect':'none','native_admission_or_history_index_owner_363_closure':False,'scope_ceiling':'True-origin exact captured candidate code and 80-source/1010 dependency guards; independent owned ordinary FS boundary probes and author evidence audit only. No full original schema/format dependency, trusted shared startup, actual native history/scope/preimage/owner reservation, power failure, perpetual physical immutability or complete T14 qualification.'}
with (HERE/'probe-evidence.json').open('x') as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'result':out['result'],'evidence_sha256':sha((HERE/'probe-evidence.json').read_bytes()),'carrier_controls':len(carrier_controls),'own_peer_probes':2,'author_evidence_rows':len(evidence['files']),'descriptor_delta':out['own_descriptor_delta']}))
