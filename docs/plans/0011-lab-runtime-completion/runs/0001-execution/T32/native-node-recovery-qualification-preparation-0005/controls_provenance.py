"""Selected metadata, AST and inert read-port controls; never runs qualification."""
import ast,copy,hashlib,json,os
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
OLD=HERE.parent/'native-node-recovery-qualification-preparation-0004'
def need(v,s):
    if not v:raise ValueError(s)
def sha(v):return hashlib.sha256(v).hexdigest()
def fds():
    result={}
    for n in os.listdir('/proc/self/fd'):
        try:s=os.fstat(int(n));result[n]=(s.st_dev,s.st_ino,s.st_mode)
        except OSError:continue
    return result
def main():
    baseline=fds();checks=[]
    def check(name,fn,refusal=False):
        before=fds()
        try:fn()
        except (ValueError,KeyError,IndexError,TypeError):
            if not refusal:raise
        else:need(not refusal,'expected refusal: '+name)
        need(before==fds(),'FD changed');checks.append(name)
    tree=ast.parse((HERE/'qualify.py').read_bytes());prior=ast.parse((OLD/'qualify.py').read_bytes())
    functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)};oldf={n.name:n for n in prior.body if isinstance(n,ast.FunctionDef)}
    shape=lambda n:ast.dump(n,include_attributes=False)
    unchanged=[n for n in oldf if n!='run']
    check('all13-other-original-helper-bodies-identical',lambda:need(len(unchanged)==13 and all(shape(functions[n])==shape(oldf[n])for n in unchanged),'helper delta'))
    run=functions['run'];oldrun=oldf['run']
    def cases(f):return next(n for n in ast.walk(f)if isinstance(n,ast.With)and any('signed_catalog' in ast.unparse(i.context_expr)for i in n.items))
    check('entire-four-original-case-block-AST-identical',lambda:need(shape(cases(run))==shape(cases(oldrun)),'case delta'))
    def final(f):return next(n.finalbody for n in f.body if isinstance(n,ast.Try)and n.finalbody)
    check('whole-original-finally-AST-identical',lambda:need([shape(n)for n in final(run)]==[shape(n)for n in final(oldrun)],'finally delta'))
    for leaf in ('boundary.py','capture.py','resource-accounting-contract.json'):
        check('original-byte-identical-'+leaf,lambda leaf=leaf:need((HERE/leaf).read_bytes()==(OLD/leaf).read_bytes(),'original body delta'))
    packet=json.loads((HERE/'execution-selection-INACTIVE.json').read_bytes());dispatch=json.loads((HERE/'root-dispatch-INACTIVE.json').read_bytes())
    check('v3-closed-reference-set-and-dispatch-correspondence',lambda:need(len(packet['reference_bindings'])==8 and packet['reference_bindings']==dispatch['reference_bindings'] and packet['schema_version'].endswith('/v3-candidate')and dispatch['schema_version'].endswith('/v3-candidate'),'contract delta'))
    check('actual-owned-roots-deadline-dispatch-null',lambda:need(packet['technical_deadline_utc']is None and packet['root_dispatch_binding']is None and packet['store_parent']==packet['output_root']=={'path':None,'identity':None},'activation invented'))
    check('exact-active17',lambda:need(len(packet['active_code_bindings'])==len({v['path']for v in packet['active_code_bindings']})==17 and all(sha((ROOT/v['path']).read_bytes())==v['sha256']for v in packet['active_code_bindings']),'active delta'))
    refs=packet['reference_bindings'];metadata={key:json.loads((ROOT/row['path']).read_bytes())for key,row in refs.items()}
    check('all-eight-metadata-pins-current',lambda:need(all(sha((ROOT/v['path']).read_bytes())==v['sha256']for v in refs.values()),'metadata hash differs'))
    nested={n.name:n for n in run.body if isinstance(n,ast.FunctionDef)}
    code=ast.Module(body=[copy.deepcopy(nested[n])for n in ('execution_occurrences','all_selected')],type_ignores=[]);ast.fix_missing_locations(code)
    calls=[];reads=[];mut={}
    def exact(row):
        key=next((k for k,v in refs.items()if v==row),None)
        if key is None:return b'inert-owned-body'
        reads.append(key);return json.dumps(mut.get(key,metadata[key])).encode()
    scope={'Path':Path,'ROOT':ROOT,'need':need,'parse':json.loads,'exact':exact,'refs':refs,
        'execution_selected':metadata['execution_manifest']['files'],'selected':metadata['adoption_manifest']['files'],
        'selected_cache':{},'selected_public':lambda row:calls.append(row['path'])or b'inert-public-body',
        'own':packet['owned_code_bindings'],'packet_binding':{'path':'inert','sha256':'0'*64},'packet':packet}
    exec(compile(code,str(HERE/'qualify.py'),'exec'),scope)
    occurrence=scope['execution_occurrences'];all_selected=scope['all_selected']
    check('176-runtime-occurrences-175-distinct-physical-positive',lambda:need(len(occurrence())==176 and len({r['path']for r in occurrence()})==175,'occurrence count'))
    archive=metadata['execution_occurrence_map']['archive_binding']['path'];missing=metadata['execution_occurrence_map']['unavailable_historical_path']
    check('all329-first-proof-occurrences-archive-twice-missing-never',lambda:(calls.clear(),all_selected(),need(len(calls)==329 and calls.count(archive)==2 and missing not in calls,'proof count')))
    first=list(calls)
    check('all329-second-proof-recaptured-without-trust-cache',lambda:(calls.clear(),all_selected(),need(calls==first and calls.count(archive)==2,'fresh proof missing')))
    check('metadata-reparsed-every-call',lambda:need(all(reads.count(key)>=2 for key in refs),'metadata stale'))
    def reject(label,key,change):
        value=copy.deepcopy(metadata[key]);change(value);mut[key]=value
        try:check(label,occurrence,True)
        finally:mut.clear()
    reject('missing-original-declaration-refused','execution_manifest',lambda v:v['files'].pop())
    reject('changed-original-row-refused','execution_manifest',lambda v:v['files'][0].update(sha256='0'*64))
    reject('current-physical-input-pruned-refused','execution_current_manifest',lambda v:v['files'].pop())
    reject('current-physical-duplicate-refused','execution_current_manifest',lambda v:v['files'].__setitem__(0,v['files'][1]))
    reject('missing-old-path-silently-restored-refused','execution_current_manifest',lambda v:v.update(historical_missing_path_restored=True))
    reject('current-original-manifest-binding-forged-refused','execution_current_manifest',lambda v:v['historical_manifest_binding'].update(sha256='0'*64))
    reject('occurrence-pruned-refused','execution_occurrence_map',lambda v:v['occurrences'].pop())
    reject('occurrence-index-reordered-refused','execution_occurrence_map',lambda v:v['occurrences'].reverse())
    reject('occurrence-physical-index-substituted-refused','execution_occurrence_map',lambda v:v['occurrences'][82].update(current_index=0))
    reject('occurrence-original-row-substituted-refused','execution_occurrence_map',lambda v:v['occurrences'][82]['historical_row'].update(path=archive))
    reject('unavailable-historical-index-substituted-refused','execution_occurrence_map',lambda v:v.update(unavailable_historical_index=0))
    reject('archive-historical-index-substituted-refused','execution_occurrence_map',lambda v:v.update(already_selected_archive_historical_index=0))
    reject('runtime-count-narrowed-refused','execution_occurrence_map',lambda v:v.update(runtime_occurrences=175))
    reject('duplicate-archive-occurrence-dropped-refused','execution_occurrence_map',lambda v:v.update(archive_captures_each_all_selected_call=1))
    reject('old-path-alias-equivalence-refused','execution_occurrence_map',lambda v:v.update(old_path_restored_or_alias_equivalence_claimed=True))
    reject('across-call-proof-cache-refused','execution_occurrence_map',lambda v:v.update(cross_call_cache_allowed=True))
    reject('current-provenance-map-binding-forged-refused','execution_current_handoff',lambda v:v['occurrence_map_binding'].update(sha256='0'*64))
    reject('historical-unavailability-label-erased-refused','execution_current_handoff',lambda v:v.update(missing_historical_status='restored'))
    check('raw-historical176-unchanged-and-missing-original-explicit',lambda:need(len(metadata['execution_manifest']['files'])==176 and metadata['execution_occurrence_map']['unavailable_historical_index']==82 and not Path(missing).exists(),'history changed'))
    need(fds()==baseline,'control FD leak')
    result={'result':'PASS-inactive-provenance-and-AST-controls','checks':checks,'check_count':len(checks),'FD_delta':0,
        'actual_Source_API_native_executor_boundary_compiler_lease_or_installation_used':False,'synthetic_proof_reads_are_inert_ports':True,'actual_qualification_claimed':False}
    (HERE/'provenance-controls-result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'result':result['result'],'check_count':len(checks),'FD_delta':0}))
if __name__=='__main__':main()
