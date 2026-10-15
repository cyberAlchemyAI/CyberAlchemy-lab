"""AST/closed-schema and exact fresh-table loop with owned inert byte ports."""
import ast,copy,hashlib,json,os,runpy,sys
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
OLD=HERE.parent/'native-node-recovery-qualification-preparation-0003'
def need(value,why):
    if not value:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def fds():
    rows={}
    for name in os.listdir('/proc/self/fd'):
        try:s=os.fstat(int(name));rows[name]=(s.st_dev,s.st_ino,s.st_mode)
        except OSError:continue
    return rows
def main():
    baseline=fds();checks=[]
    def check(label,fn,refuses=False):
        try:fn()
        except ValueError:
            if not refuses:raise
        else:need(not refuses,'expected inert refusal: '+label)
        checks.append(label)
    tree=ast.parse((HERE/'qualify.py').read_bytes());old=ast.parse((OLD/'qualify.py').read_bytes())
    fn={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)};of={n.name:n for n in old.body if isinstance(n,ast.FunctionDef)}
    shape=lambda n:ast.dump(n,include_attributes=False)
    unchanged=[name for name in of if name!='run']
    check('all13-other-original-helper-bodies-including-FD-protocol-identical',lambda:need(all(shape(fn[n])==shape(of[n])for n in unchanged)and len(unchanged)==13,'helper changed'))
    packet=json.loads((HERE/'execution-selection-INACTIVE.json').read_bytes());dispatch=json.loads((HERE/'root-dispatch-INACTIVE.json').read_bytes())
    check('v2-selection-and-dispatch-inactive',lambda:need(packet['schema_version'].endswith('/v2-candidate')and dispatch['schema_version'].endswith('/v2-candidate')and packet['root_dispatch_binding']is None and packet['technical_deadline_utc']is None and packet['store_parent']==packet['output_root']=={'path':None,'identity':None},'activation claimed'))
    check('exact-five-closed-reference-bindings',lambda:need(set(packet['reference_bindings'])=={'adoption_handoff','adoption_manifest','adoption_peer','migration_scope','execution_manifest'},'reference shape'))
    check('dispatch-binds-current-execution-and-complete-references',lambda:need(dispatch['reference_bindings']==packet['reference_bindings']and dispatch['ontology_execution_selection_binding']==packet['ontology_execution_selection_binding'],'dispatch underbinding'))
    check('exact-active17-and-actual-file-hashes',lambda:need(len(packet['active_code_bindings'])==len({r['path']for r in packet['active_code_bindings']})==17 and all(sha((ROOT/r['path']).read_bytes())==r['sha256']for r in packet['active_code_bindings']),'active closure differs'))
    check('exact-installed827-selector',lambda:need(packet['ontology_execution_selection_binding']['sha256']=='3b67921318a8d9153f798c91d954e015bda51846608ded31cb6c8cc189806c10','old role reused'))
    check('migration-unqualified-data-only',lambda:need(dispatch['migration_status']=='UNQUALIFIED-original480-versus-selected827136','migration proof fabricated'))
    # Exercise the actual nested fresh read loop using symbolic byte sources;
    # no original capture/guard/module is patched or loaded.
    run=fn['run'];loopfn=next(n for n in ast.walk(run)if isinstance(n,ast.FunctionDef)and n.name=='all_selected')
    guard=[{'path':'fixture/guard/%03d'%i,'sha256':sha(b'x'),'size_bytes':1}for i in range(153)]
    execution=[guard[0],*[{'path':'fixture/execution/%03d'%i,'sha256':sha(b'x'),'size_bytes':1}for i in range(175)]]
    refs={k:{'path':'fixture/reference/'+k,'sha256':''}for k in('adoption_manifest','execution_manifest','adoption_handoff','adoption_peer','migration_scope')}
    data={ROOT/r['path']:b'x'for r in guard+execution}
    for key in refs:
        body=json.dumps({'files':guard if key=='adoption_manifest'else execution}).encode()if key in('adoption_manifest','execution_manifest')else b'owned-inert-reference'
        refs[key]['sha256']=sha(body);data[ROOT/refs[key]['path']]=body
    own={k:{'path':'fixture/own/'+k,'sha256':sha(b'own')}for k in('runner','capture','boundary')}
    packet_binding={'path':'fixture/packet','sha256':sha(b'packet')}
    installed_binding={'path':'fixture/installed-selector','sha256':sha(b'installed-selector')}
    data.update({ROOT/r['path']:b'own'for r in own.values()});data[ROOT/packet_binding['path']]=b'packet';calls=[]
    data[ROOT/installed_binding['path']]=b'installed-selector'
    def capture(path,pin):
        calls.append(path);body=data[path];need(sha(body)==pin,'owned inert byte mutation');return body
    scope={'ROOT':ROOT,'Path':Path,'need':need,'parse':json.loads,'refs':refs,'selected':guard,'execution_selected':execution,'selected_cache':{},'own':own,'packet_binding':packet_binding,'packet':{'ontology_execution_selection_binding':installed_binding},'capture':capture,'selected_public':lambda r:capture(ROOT/r['path'],r['sha256']),'exact':lambda r:capture(ROOT/r['path'],r['sha256'])}
    unit=ast.Module(body=[copy.deepcopy(loopfn)],type_ignores=[]);ast.fix_missing_locations(unit);exec(compile(unit,str(HERE/'qualify.py'),'exec'),scope);verify=scope['all_selected']
    verify();first=calls[:];calls.clear();verify();second=calls[:]
    def body_calls(rows):return [path for path in rows if path in{ROOT/r['path']for r in guard+execution}]
    check('both-tables-full329-occurrences-read-on-every-invocation',lambda:need(len(body_calls(first))==len(body_calls(second))==329 and first==second,'proof read reused/pruned'))
    check('overlapping-source-path-verified-twice-per-invocation',lambda:need(first.count(ROOT/guard[0]['path'])==second.count(ROOT/guard[0]['path'])==2,'table scopes deduplicated'))
    check('both-manifest-bytes-freshly-recaptured-each-invocation',lambda:need(all(second.count(ROOT/refs[k]['path'])==1 for k in('adoption_manifest','execution_manifest')),'manifest not recaptured'))
    changed=ROOT/execution[-1]['path'];saved=data[changed];data[changed]=b'y'
    check('last-execution-row-mutation-refuses-after-primed-code-cache',verify,True);data[changed]=saved
    changed=ROOT/guard[-1]['path'];saved=data[changed];data[changed]=b'y'
    check('last-guard-row-mutation-refuses-after-primed-code-cache',verify,True);data[changed]=saved
    changed=ROOT/refs['execution_manifest']['path'];saved=data[changed];data[changed]=b'{}'
    check('changed-execution-manifest-refuses',verify,True);data[changed]=saved
    changed=ROOT/installed_binding['path'];saved=data[changed];data[changed]=b'changed-selector'
    check('changed-installed-selector-refuses-on-entry-exit-proof',verify,True);data[changed]=saved
    # Original full independent finally blocks are unchanged except v2 result
    # data; the existing32 FD/cleanup controls execute those exact subtrees.
    final=next(n.finalbody for n in run.body if isinstance(n,ast.Try));ofinal=next(n.finalbody for n in of['run'].body if isinstance(n,ast.Try))
    check('all-pre-result-independent-exit-and-FD-acceptance-AST-identical',lambda:need([shape(n)for n in final[:-1]]==[shape(n)for n in ofinal[:-1]],'exit guard/clock/FD acceptance changed'))
    fd=runpy.run_path(str(HERE/'controls_fd.py'),run_name='_owned_original_FD_controls')['main']()
    need(fd['result']=='PASS'and fd['check_count']==32,'original32 FD/case/cleanup controls fail')
    need(fds()==baseline and 'ctypes'not in sys.modules,'contract controls resource change')
    return {'result':'PASS-bounded-AST-schema-and-owned-inert-only','contract_checks':checks,'contract_check_count':len(checks),'original_FD_controls':fd,'total_checks':len(checks)+32,'all13_other_helpers_AST_identical':True,'full4_original_case_AST_identical':True,'both153_and176_table_reads_fresh':True,'FD_delta':0,'ctypes_imported':False,'actual_API_Source_native_executor_boundary_installation_or_lease_used':False,'actual4case_deadlinefit_or_runtime_qualified':False}
if __name__=='__main__':
    result=main()
    with(HERE/'controls-result.json').open('x')as output:json.dump(result,output,sort_keys=True,indent=2);output.write('\n')
    print(json.dumps(result,sort_keys=True))
