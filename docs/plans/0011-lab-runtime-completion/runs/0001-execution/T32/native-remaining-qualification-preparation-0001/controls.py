"""Pure AST/owned inert evidence controls only; never executes caller/probe/native."""
import ast,base64,copy,hashlib,importlib.util,json,os,sys,tempfile,types
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
B=HERE.parent
OLD=B/'migration-native-role-compatibility-preparation-0002'
BASE=ROOT/'product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001'
checks=[]
def need(v,s):
    if not v:raise ValueError(s)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def shape(n):return ast.dump(n,include_attributes=False)
def funcs(p):return {n.name:n for n in ast.parse(p.read_bytes()).body if isinstance(n,ast.FunctionDef)}
def fds():
    rows={}
    for name in os.listdir('/proc/self/fd'):
        try:s=os.fstat(int(name));rows[name]=(s.st_dev,s.st_ino,s.st_mode)
        except OSError:continue
    return rows
def check(label,fn,refuses=False):
    before=fds()
    try:fn()
    except (ValueError,KeyError,OSError,TypeError):
        if not refuses:raise
    else:need(not refuses,'expected inert refusal: '+label)
    need(fds()==before,'inert FD leak');checks.append(label)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m

def main():
    initial=fds()
    for p in HERE.rglob('*.py'):ast.parse(p.read_bytes(),str(p))
    for name in ('lifecycle.py','withdrawal.py'):
        old=funcs(B/'native-lifecycle-recovery-adoption-0003/postimages'/name)
        new=funcs(HERE/'callers'/name)
        oldbody=copy.deepcopy(old['run']);newbody=copy.deepcopy(new['run'])
        oldbody.body=oldbody.body[2:];newbody.body=newbody.body[1:]
        check('entire-original-'+name+'-run-after-explicit-factory-check-identical',lambda:need(shape(oldbody)==shape(newbody),'original run changed'))
        check('original-'+name+'-emit-helper-identical',lambda:need(shape(old['emit'])==shape(new['emit']),'original writer changed'))
    source=(HERE/'observer-build/observer/src/lib.rs').read_text()
    clean=source.replace('    t32_observe(directory, "after-lock");\n','').replace('            if committed_paths.len() == 1 { t32_observe(directory, "after-first-link"); }\n','').replace('    t32_observe(directory, "before-cleanup");\n','');clean=clean[:clean.index('\n// T32 additive observer:')]
    check('exact-three-checkpoint-delta-strips-to-current-production',lambda:need(clean==(BASE/'production/src/lib.rs').read_text(),'native semantic/persistence delta'))
    for f in ['Cargo.toml','Cargo.lock','src/main.rs','src/context_adapter.rs','src/governance_context_adapter.rs','tests/context_binding.rs','tests/replay.rs']:
        check('observer-original-production-byte-parity-'+f,lambda f=f:need((HERE/'observer-build/observer'/f).read_bytes()==(BASE/'production'/f).read_bytes(),'observer source/test/lock changed'))
    check('observer-W1-fixture-original-byte-parity',lambda:need((HERE/'observer-build/fixtures/w1/positive-baseline.json').read_bytes()==(BASE/'fixtures/w1/positive-baseline.json').read_bytes(),'W1 source changed'))
    recipe=json.loads((HERE/'observer-build/ROOT-BUILD-INACTIVE.json').read_bytes())
    check('five-offline-locked-original-test-cohort-no-ambient-environment',lambda:need(len(recipe['commands'])==5 and all(c['environment']['CARGO_NET_OFFLINE']=='true'for c in recipe['commands'])and all('--offline'in c['argv']and '--locked'in c['argv']for c in recipe['commands'][2:])and recipe['no_ambient_environment_inheritance']is True and recipe['active']is False,'build proposal widened'))
    cohort=json.loads((HERE/'ORIGINAL27.json').read_bytes())
    check('all27-cases-distinct-and-original6-14-7-counts',lambda:need(len(cohort['cases'])==len({c['id']for c in cohort['cases']})==27 and [sum(c['cohort']==k for c in cohort['cases'])for k in ['direct-native','wrapper-recovery','controls']]==[6,14,7],'cohort narrowed'))
    matrix=json.loads((HERE/'N01-N11.json').read_bytes())
    check('all-original-N01-N11-obligations-verbatim-retained',lambda:need([(v['id'],v['case'])for v in matrix['required_cases']]==[(v['id'],v['case'])for v in json.loads((B/'native-lifecycle-recovery-adoption-0003/CONTROL-MATRIX.json').read_bytes())['required_cases']],'obligation changed'))
    paths=json.loads((HERE/'THREE-PATHS.json').read_bytes())['paths']
    check('original26-lifecycle29-withdrawal48-migration-tests-all-enumerated',lambda:need([sum(len(c['methods'])for c in p['test_classes'])for p in paths]==[26,29,48],'tests narrowed'))
    dag=json.loads((HERE/'DAG.json').read_bytes());nodes={n['id']for n in dag['nodes']};done=set()
    while len(done)<len(nodes):
        ready={n for n in nodes-done if all(a in done for a,b in dag['edges']if b==n)}
        need(ready,'DAG has cycle');done.update(ready)
    check('reviewed-next-gate-DAG-acyclic',lambda:need(len(done)==10,'DAG node loss'))
    p=HERE/'migration827';pkg=types.ModuleType('_T32_remaining_inert');pkg.__path__=[str(p)];sys.modules[pkg.__name__]=pkg
    capture=load(pkg.__name__+'.capture',p/'capture.py');c=load(pkg.__name__+'.execution_contract',p/'execution_contract.py');io=load(pkg.__name__+'.private_io',p/'private_io.py')
    oldf=funcs(OLD/'execution_contract.py');newf=funcs(p/'execution_contract.py')
    for name in oldf:
        if name=='evidence':
            node=copy.deepcopy(newf[name])
            for n in ast.walk(node):
                if isinstance(n,ast.Constant)and n.value=='lab-O05-native-byte-compatibility/v2-candidate':n.value='lab-O05-native-byte-compatibility/v1-candidate'
            check('entire-full176-evidence-parser-only-version-literal-delta',lambda:need(shape(node)==shape(oldf[name]),'evidence parser changed'))
        else:check('original-probe-contract-helper-AST-identical-'+name,lambda name=name:need(shape(newf[name])==shape(oldf[name]),'contract helper changed'))
    oldprobe=funcs(OLD/'compatibility_probe.py');newprobe=funcs(p/'compatibility_probe.py')
    for name in oldprobe:
        node=copy.deepcopy(newprobe[name])
        for n in ast.walk(node):
            if isinstance(n,ast.Constant)and isinstance(n.value,str):n.value=n.value.replace('selected827','selected574').replace('lab-O05-native-byte-compatibility/v2-candidate','lab-O05-native-byte-compatibility/v1-candidate')
        check('original-probe-full-function-AST-only-explicit827-version-text-'+name,lambda name=name,node=node:need(shape(node)==shape(oldprobe[name]),'probe algorithm changed'))
    oldinputs=json.loads((OLD/'input-selection.json').read_bytes())['inputs'];inputs=json.loads((p/'input-selection.json').read_bytes())['inputs']
    check('all90-original-public-migration-inputs-retained-literally',lambda:need(inputs[:90]==oldinputs,'input selection pruned'))
    check('explicit-installed827-role-and-original480-distinct',lambda:need(c.NATIVE=='82713671f1c1271f92b7ae675ccee531c0ee972828e25899c0c19e64015025f6'and c.NATIVE!=c.OLD_NATIVE and json.loads(c.bytes_for(c.EXECUTION))['ontology_role']['sha256']==c.NATIVE,'native role substituted'))
    # Reading exact selected public bytes is not a full API Source verification.
    c.input_guard()
    archive_row=next({k:r[k]for k in('path','sha256')}for r in inputs if r['path'].endswith('migration/candidate/0001/native.snapshot'))
    archive=json.loads(c.bytes_for(archive_row));families={k:[]for k in('semantic','governance')};event_bytes={}
    for family in families:
        for i in range(1,89):
            name=f'{family}/{i:08d}-ontology-{family}:O05:{i}.json';r=archive['files'][name];raw=base64.b64decode(r['base64_original_bytes'],validate=True)
            need(sha(raw)==r['sha256'],'original archive bytes differ');families[family].append(json.loads(raw));event_bytes[name]=sha(raw)
    with tempfile.TemporaryDirectory(prefix='cal-T32-remaining-inert-')as tmp:
        root=Path(tmp);counter=[0]
        def stream(value):
            path=root/str(counter[0]);counter[0]+=1;raw=value if type(value)is bytes else c.canonical(value);io.write(path,raw);return {'path':str(path),'sha256':sha(raw)}
        replay={'result':'PASS','checkpoint_parity':'PASS','authority_effect':'none','semantic_events':families['semantic'],'governance_events':families['governance']};drafts=copy.deepcopy(families)
        for events in drafts.values():
            for e in events:e['event_digest']='0'*64
        rows=[]
        for mode,request,out,pre,post in [('read',None,replay,event_bytes,event_bytes),('seal',drafts,families,{},{}),('append',families,{'result':'PASS','authority_effect':'none'},{},event_bytes),('read',None,replay,event_bytes,event_bytes)]:
            rows.append({'mode':mode,'returncode':0,'request_binding':stream(request)if request is not None else None,'stdout_binding':stream(out),'stderr_binding':stream(b''),'files_before':copy.deepcopy(pre),'files_after':copy.deepcopy(post)})
        value={'schema_version':'lab-O05-native-byte-compatibility/v2-candidate','authority_effect':'none','actual_owner_outcome':None,'execution_selection_binding':c.EXECUTION,'historical_scope_binding':c.HISTORICAL,'input_selection_binding':c.INPUTS,'probe_module_binding':c.bind(p/'compatibility_probe.py'),'captured_at':'2026-10-15T03:00:00+00:00','historical_archive_binding':archive_row,'event_bytes':event_bytes,'observations':rows}
        verify=lambda v:c.evidence(v,runtime_bindings=[c.bind(p/'compatibility_probe.py')])
        check('inert-synthetic-complete176-evidence-parser-positive-not-native-proof',lambda:verify(value))
        for label,mutate in [('missing-event',lambda v:v['event_bytes'].pop(next(iter(v['event_bytes'])))),('failed-child',lambda v:v['observations'][0].update(returncode=1)),('old574-executor',lambda v:v['execution_selection_binding'].update(sha256='3b0c97b2b31363f6d344af10e2dde3281dbffb042a6746e67f0b9fe1795a3bf4')),('altered-append',lambda v:v['observations'][2].update(files_after={})),('altered-cold',lambda v:v['observations'][3].update(files_after={})),('forged-authority',lambda v:v.update(authority_effect='admit')),('partial-protocol',lambda v:v['observations'].pop())]:
            changed=copy.deepcopy(value);mutate(changed);check('evidence-parser-refuses-'+label,lambda changed=changed:verify(changed),True)
    need(fds()==initial and 'ctypes'not in sys.modules,'inert resources changed')
    return {'result':'PASS-static-and-owned-inert-only','checks':checks,'check_count':len(checks),'FD_delta':0,'ctypes_imported':False,'selected_public_probe_input_rows':len(inputs),'actual_API_Source_guard_native_probe_factory_lifecycle_withdrawal_compiler_lease_or_installation_executed':False,'synthetic_evidence_is_empirical_proof':False,'all_actual_remaining_qualification_pending':True}
if __name__=='__main__':
    result=main()
    with(HERE/'controls-result.json').open('x')as out:json.dump(result,out,sort_keys=True,indent=2);out.write('\n')
    print(json.dumps(result,sort_keys=True))
