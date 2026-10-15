"""Fresh pinned proof checking and original-capture controls. Same-kernel replay is not independent checking."""
from pathlib import Path
import hashlib,json,os,re,subprocess,time
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[5]
ROOT=BASE.parents[3]

def binding(p):
    return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

def check_bound_tree(value):
    if isinstance(value,dict):
        if set(value)>={'path','sha256'}:assert binding(ROOT/value['path'])=={'path':value['path'],'sha256':value['sha256']}
        for child in value.values():check_bound_tree(child)
    elif isinstance(value,list):
        for child in value:check_bound_tree(child)

def declarations(s):
    stack=[];names=[]
    for line in s.splitlines():
        if m:=re.match(r'^namespace ([\w.]+)$',line):stack.append(m[1])
        elif re.match(r'^(mutual|section(?: [\w.]+)?)$',line):stack.append(None)
        elif re.match(r'^end(?: [\w.]+)?$',line):stack.pop()
        elif m:=re.match(r'^theorem (\w+)',line):names.append('.'.join([x for x in stack if x]+[m[1]]))
    return names

def run():
    driver=binding(Path(__file__))
    runtime=BASE/'v1/formal/.toolcache/lean-4.33.1-linux'
    lock_path=BASE/'v1/formal/toolchain-lock.json';lock=json.loads(lock_path.read_text())
    lean=runtime/'bin/lean';kernel=runtime/'lib/lean/libleanshared.so'
    assert binding(lean)['sha256']==lock['lean_binary_sha256']
    assert binding(kernel)['sha256']==lock['lean_shared_library_sha256']
    previous_path=HERE.parent/'K02-profile-evidence/verification.json'
    previous_binding=binding(previous_path);previous=json.loads(previous_path.read_text())
    assert previous['result']=='candidate-fragment-pass'
    dependencies=[ROOT/item['path'] for item in previous['sources']]
    for p,item in zip(dependencies,previous['sources']):assert binding(p)==item
    local=[HERE/(name+'.lean') for name in ['NumericWork','NumericTree','CombinedBudget','ResourcePreflight','BoundedEvidence','ResourceDiagnostics','ResourceControls','ResourceRuntimeControls']]
    sources=dependencies+local;captured=[binding(p) for p in sources]
    assert len({p.stem for p in sources})==len(sources)
    names=[];controls=[]
    for p in local:
        s=p.read_text();decls=declarations(s);names+=decls
        if p.stem=='ResourceControls':controls+=decls
        inspections=re.findall(r'^#print axioms ([\w.]+)$',s,re.M)
        assert [n.split('.')[-1] for n in decls]==inspections,(p,decls,inspections)
        code='\n'.join(line for line in s.splitlines() if not line.lstrip().startswith('--'))
        assert not re.search(r'\b(sorry|admit|native_decide|axiom)\b',code)
    assert len(names)==len(set(names))==55 and len(controls)==18
    context_path=HERE/'context-pack.json';control_path=HERE/'control-index.json'
    context=json.loads(context_path.read_text());control=json.loads(control_path.read_text())
    check_bound_tree(context);check_bound_tree(control)
    manifest_bindings=[binding(context_path),binding(control_path)]
    assert control['real_authoritative_snapshot_provider'] is False
    assert control['numeric_eligibility_is_integrality'] is False
    expr=re.findall(r'^#eval (.*)$',(HERE/'ResourceRuntimeControls.lean').read_text(),re.M)
    assert expr==[x['expression'] for x in control['runtime_cases']]
    # Inspect the actual runtime fixtures inherited by this run, not only labels.
    runtime_source=(HERE.parent/'K02-profile-evidence/AuthorityRuntimeControls.lean').read_text()
    for index,row in enumerate(control['imported_original_fixture_bindings']):
        original=(ROOT/row['original_bytes']['path']).read_bytes()
        assert len(original)==row['byte_count']
        assert hashlib.sha256(original).hexdigest()==row['computed_digest']
        literal=re.search(r'^def capture'+str(index)+r' : CandidateBindingCapture.Envelope := ⟨\[(.*?)\],(\d+),bootstrap.ref,"([^"]+)"⟩$',runtime_source,re.M)
        assert literal
        assert bytes(int(x) for x in literal[1].split(',') if x.strip())==original
        assert int(literal[2])==row['byte_count'] and literal[3]==row['submitted_digest']
    allowed={'propext','Quot.sound','Classical.choice'};records=[]
    for phase in ('compile','replay'):
        build=HERE/phase;build.mkdir(exist_ok=True)
        for p in build.glob('*.olean'):p.unlink()
        for p in sources:
            assert binding(Path(__file__))==driver,'driver drift'
            assert [binding(x) for x in sources]==captured,'source drift'
            output=build/(p.stem+'.olean');log=build/(p.stem+'.log')
            argv=[str(lean),'-o',str(output),str(p)];started=time.monotonic()
            result=subprocess.run(argv,cwd=p.parent,env=dict(os.environ,LEAN_PATH=str(build)),capture_output=True,text=True,timeout=300)
            log.write_text(result.stdout+result.stderr)
            axioms=sorted({x.strip() for group in re.findall(r'depends on axioms: \[([^]]*)\]',result.stdout) for x in group.split(',') if x.strip()})
            count=len(re.findall(r'(?:depends on axioms:|does not depend on any axioms)',result.stdout))
            expected=len(re.findall(r'^#print axioms ',p.read_text(),re.M))
            row={'phase':phase,'source':binding(p),'argv':argv,'cwd':str(p.parent),'LEAN_PATH':str(build),'seconds':round(time.monotonic()-started,3),'exit_code':result.returncode,'log':binding(log),'axioms':axioms,'inspected_declarations':count}
            if output.exists():row['olean']=binding(output)
            if p.stem=='ResourceRuntimeControls':
                assert result.stdout.strip().splitlines()==[x['expected'] for x in control['runtime_cases']],result.stdout
                row['runtime_composed_cases']=len(control['runtime_cases'])
            records.append(row)
            (HERE/'verification-in-progress.json').write_text(json.dumps(records,indent=2)+'\n')
            print(phase,p.stem,result.returncode,row['seconds'],flush=True)
            assert result.returncode==0 and 'warning:' not in result.stdout,(p,result.stdout,result.stderr)
            assert count==expected and set(axioms)<=allowed,(p,count,expected,axioms)
    assert binding(Path(__file__))==driver and binding(previous_path)==previous_binding
    assert [binding(p) for p in sources]==captured
    assert [binding(context_path),binding(control_path)]==manifest_bindings
    report={'task':'N01','unit':'K02-evidence-resources','result':'candidate-fragment-pass','method':'Fresh isolated pinned Lean compilation and separate fresh same-kernel replay; actual captured byte controls and per-declaration axiom inspection.','driver':driver,'toolchain_lock':binding(lock_path),'compiler':binding(lean),'kernel_library':binding(kernel),'context_pack':binding(context_path),'control_index':binding(control_path),'predecessor_verification':previous_binding,'sources':captured,'records':records,'new_declarations':names,'new_declaration_count':len(names),'new_general_declarations':len(names)-len(controls),'new_worked_control_declarations':len(controls),'allowed_axioms':sorted(allowed),'runtime_composed_cases':len(control['runtime_cases']),'combined_authority_inclusive_budget_exact':True,'numeric_guard_before_typed_decoding':True,'decimal_power_exponents_bounded':True,'bounded_evidence_preparation_exact':True,'original_source_envelopes_retained':True,'source_refusal_position_and_prefix_proved':True,'local_data_refusal_meanings_exact':True,'claim_scope':'Candidate guarded data preparation and local stage causes. Numeric work limits precede typed decoding; no measured whole-process bound or actual authenticity provider is established.','real_authoritative_snapshot_provider':False,'raw_source_refinement_proved':False,'whole_K02_source_refinement_proved':False,'independent_checker_run':False,'supported_resource_envelope_measured':False,'N03_API_freeze':False,'inherited_discharges':0,'N01_accepted':False,'authority_effect':'none'}
    (HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('VERIFIED',len(names),'new declarations;',len(records),'fresh invocations',flush=True)

if __name__=='__main__':run()
