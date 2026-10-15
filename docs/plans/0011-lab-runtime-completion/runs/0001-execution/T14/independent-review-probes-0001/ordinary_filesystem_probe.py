"""Independent T14 ordinary-byte filesystem probes; original callbacks unchanged."""
import argparse,hashlib,importlib.util,json,os,stat,sys,tempfile,traceback
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution';HERE=Path(__file__).absolute().parent
C=RUN/'T14/mixed-target-publisher-0001';INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
DEPENDENCY_SHA='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
MF='9161e89f0d622fbe4c6f8d95fbf1e7c412cd07318fb817444c777cbcf2fdb6b6'
EXPECTED=None
def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def need(value, reason):
    if not value:
        raise ValueError(reason)

def dependency_guard():
    selection_path = RUN / 'T07/revision-0002/dependency-selection-0002.json'
    raw = selection_path.read_bytes(); need(sha(raw) == DEPENDENCY_SHA, 'independent full dependency selection differs')
    selected = json.loads(raw)
    rows = {r['destination']: {'sha256': r['sha256'], 'size_bytes': r['size_bytes'],
                             'mode': 0o755 if r['kind'] in {'interpreter', 'native-executable'} else 0o644}
            for r in selected['inputs']}
    rows.update(selected['wheel_members']); rows['lib/abi/ld-linux-x86-64.so.2']['mode'] = 0o755
    need(len(rows) == 1010, 'full installed closure required')
    for name, row in rows.items():
        path = INSTALL / name
        need(not any(p.is_symlink() for p in (path, *path.parents)), 'unsafe selected dependency')
        before = path.lstat()
        need(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid()
             and stat.S_IMODE(before.st_mode) == row['mode'] and before.st_size == row['size_bytes'], 'selected dependency identity differs')
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            actual = os.fstat(fd); need((actual.st_dev, actual.st_ino, actual.st_mtime_ns, actual.st_ctime_ns)
                                        == (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_ctime_ns), 'dependency attachment differs')
            digest = hashlib.sha256()
            while chunk := os.read(fd, 1024 * 1024):
                digest.update(chunk)
            after = os.fstat(fd); current = path.lstat()
            fields = lambda x: (x.st_dev, x.st_ino, x.st_mode, x.st_uid, x.st_size, x.st_mtime_ns, x.st_ctime_ns)
            need(fields(before) == fields(after) == fields(current) and digest.hexdigest() == row['sha256'], 'dependency bytes changed')
        finally:
            os.close(fd)
    return {'status': 'PASS', 'installed_files': 1010, 'selection_sha256': DEPENDENCY_SHA}
def source_guard():
    need(sha((C/'source-manifest.json').read_bytes())==MF,'selected component manifest differs')
    for row in json.loads((C/'source-manifest.json').read_bytes())['files']:
        path=ROOT/row['path'];need(not any(p.is_symlink() for p in [path,*path.parents]) and sha(path.read_bytes())==row['sha256'],'selected component source differs')
    need(sha(Path(__file__).absolute().read_bytes())==EXPECTED,'independently pinned observer differs')
def root():
    p=Path(tempfile.mkdtemp(prefix='cal-T14-publisher-independent-'));p.chmod(0o700)
    fd=os.open(p/'publisher.lock',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
    return p

def save(path,value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
def main():
    global EXPECTED
    a=argparse.ArgumentParser();a.add_argument('--observer-sha256',required=True);args=a.parse_args();EXPECTED=args.observer_sha256
    entry=dependency_guard();source_guard();name='_T14_independent_selected_component'
    spec=importlib.util.spec_from_file_location(name,C/'__init__.py',submodule_search_locations=[str(C)]);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    T=__import__(name+'.typed_targets',fromlist=['adapt']);P=__import__(name+'.publisher',fromlist=['OwnedBytePublisher'])
    selected=json.loads((C/'public-schema-example-selection.json').read_bytes());items=[];carrier_gap=None
    for row in selected['rows']:
        raw=(ROOT/row['public_original_fixture']['path']).read_bytes();document=(ROOT/row['schema']['path']).read_bytes()
        schemas=T.OriginalSchemas([row['schema']],{row['schema']['path']:document});s={k:row[k] for k in ['family','category','carrier_ref','schema_selector','identity_selector','identity_ref']};s.update(schema_path=row['schema']['path'],raw_sha256=sha(raw))
        item=T.adapt(raw,s,schemas);items.append({'output_path':'targets/'+row['family']+'.json','adapted':item})
        if row['family']=='typed-relation':
            bad={**s,'carrier_ref':'cal.artifact-type.typed-relation/v999'}
            try:wrong=T.adapt(raw,bad,schemas)
            except T.Refusal:carrier_gap={'result':'REFUSED-as-required'}
            else:carrier_gap={'result':'ACCEPTED-impossible-carrier-version','genuine_schema_path':s['schema_path'],'original_carrier_ref':s['carrier_ref'],'accepted_metadata_carrier_ref':wrong['metadata']['carrier_ref'],'schema_shape_validated':wrong['metadata']['schema_shape_validated'],'native_or_owner_qualified':False}
    prepared=T.prepare_byte_bundle(items,'independent-ordinary-seven',schema_binding_sha256=sha((C/'public-schema-example-selection.json').read_bytes()));pins=dict(prepared['pins']);binding={'path':str(Path(__file__).absolute()),'sha256':EXPECTED}
    p=root();identity=P.ident(p.stat());publisher=P.OwnedBytePublisher(p,identity,source_guard,binding,purpose='owned-technical-rehearsal')
    baseline=publisher.publish(prepared,pins);assert baseline['state']=='committed-technical-bytes';publisher.close()
    cold=P.OwnedBytePublisher(p,identity,source_guard,binding,purpose='owned-technical-rehearsal');inspected=cold.inspect_committed('independent-ordinary-seven',pins,prepared['files']);assert inspected['technical_byte_closure_verified'];cold.close()
    # An unchanged source-name publication following real last-boundary stage replacement.
    # A new observer-only audit hook reports ctypes.dlopen; an OS peer performs
    # the ordinary rename before the original untouched publisher invokes renameat2.
    race=root();rid=P.ident(race.stat());foreign=race/'foreign-pending';foreign.mkdir(mode=0o700);canary=foreign/'foreign-canary.bin';fd=os.open(canary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.write(fd,b'independent foreign byte canary');os.close(fd);foreign_ino=foreign.stat().st_ino
    stage='.'+'independent-ordinary-seven'+'-stage-'+pins['bundle_sha256'];retained=race/'original-selected-stage-retained'
    signal_r,signal_w=os.pipe();ack_r,ack_w=os.pipe();peer=os.fork()
    if peer==0:
        try:
            os.close(signal_w);os.close(ack_r);assert os.read(signal_r,1)==b'G'
            os.rename(race/stage,retained);os.rename(foreign,race/stage);os.write(ack_w,b'A');os._exit(0)
        except BaseException:os.write(ack_w,b'F');os._exit(1)
    os.close(signal_r);os.close(ack_w);armed={'value':True}
    def observe(event,args):
        if event=='ctypes.dlopen' and args==(None,) and armed['value']:
            armed['value']=False;os.write(signal_w,b'G');assert os.read(ack_r,1)==b'A'
    sys.addaudithook(observe)
    publisher=P.OwnedBytePublisher(race,rid,source_guard,binding,purpose='owned-technical-rehearsal');outcome=publisher.publish(prepared,pins);publisher.close();_,peer_status=os.waitpid(peer,0);os.close(signal_w);os.close(ack_r)
    final=race/'independent-ordinary-seven';foreign_committed=final.is_dir() and final.stat().st_ino==foreign_ino and (final/'foreign-canary.bin').read_bytes()==b'independent foreign byte canary'
    assert foreign_committed and retained.is_dir() and not armed['value'] and os.waitstatus_to_exitcode(peer_status)==0
    result={'schema_version':'lab-T14-independent-ordinary-filesystem-counterexamples/v1-candidate','authority_effect':'none','actual_owner_outcome':None,'dependencies_entry':entry,'dependencies_exit':dependency_guard(),'component_manifest_sha256':MF,'component_files_entry_exit_verified':55,'actual_runtime':sys.version.split()[0],'baseline_new_owned_technical_publish':baseline,'baseline_new_cold_exact_inspection':inspected,'carrier_version_binding_probe':carrier_gap,'source_name_replacement_race':{'observer':'new audit observer coordinates actual ordinary OS peer at ctypes.dlopen boundary; no original callback/code or libc function replaced','real_peer_exit_code':os.waitstatus_to_exitcode(peer_status),'original_publisher_result':outcome,'foreign_unselected_directory_moved_to_final_committed_name':foreign_committed,'original_selected_stage_preserved_at_separate_retained_name':retained.is_dir(),'foreign_canary_original_bytes_preserved':True,'postcommit_uncertainty_reported':outcome['state']=='uncertain-commit-inspection-required','independently_selected_bundle_pins_match_actual_final_directory':False},'all_roots_new_owned_retained':True,'root_locator_sha256s':[sha(str(x).encode()) for x in [p,race]],'original_native_API_Service_Session_protected_reader_constructor_or_global_lease_executed':False,'original_component_callbacks_mutated':False,'general_native_admission_or_member_coverage_qualified':False}
    source_guard();save(HERE/'probe-evidence-0001.json',result);print(json.dumps({'evidence_path':str(HERE/'probe-evidence-0001.json'),'evidence_sha256':sha((HERE/'probe-evidence-0001.json').read_bytes()),'carrier_version_probe':carrier_gap['result'],'real_source_name_replacement_committed_foreign':foreign_committed,'original_uncertainty_reported':outcome['state']},sort_keys=True))
if __name__=='__main__':main()
