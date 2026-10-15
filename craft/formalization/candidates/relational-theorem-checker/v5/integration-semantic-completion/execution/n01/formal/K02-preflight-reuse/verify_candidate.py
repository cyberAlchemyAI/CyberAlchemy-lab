"""Fresh-check new reuse modules against exact previously verified dependency outputs. No fresh dependency rebuild is claimed."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,time
HERE=Path(__file__).resolve().parent;BASE=HERE.parents[5];ROOT=BASE.parents[3]
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def check_tree(v):
    if isinstance(v,dict):
        if {'path','sha256'}<=v.keys():assert binding(ROOT/v['path'])=={'path':v['path'],'sha256':v['sha256']}
        for x in v.values():check_tree(x)
    elif isinstance(v,list):
        for x in v:check_tree(x)
def run():
    driver=binding(Path(__file__));prior_path=HERE.parent/'K02-evidence-resources/verification.json';prior=json.loads(prior_path.read_text())
    prior_audit=HERE.parent/'K02-evidence-resources/import-resolution-audit.json';audit=json.loads(prior_audit.read_text())
    check_tree(prior);check_tree(audit)
    assert prior['result']=='candidate-fragment-pass' and audit['result']=='import-resolution-audit-pass' and audit['verification']==binding(prior_path)
    context_path=HERE/'context-pack.json';controls_path=HERE/'control-index.json';context=json.loads(context_path.read_text());controls=json.loads(controls_path.read_text());check_tree(context);check_tree(controls)
    stable=[binding(p) for p in [context_path,controls_path,prior_path,prior_audit]]
    lock_path=BASE/'v1/formal/toolchain-lock.json';lock=json.loads(lock_path.read_text());runtime=BASE/'v1/formal/.toolcache/lean-4.33.1-linux';lean=runtime/'bin/lean';kernel=runtime/'lib/lean/libleanshared.so'
    assert binding(lean)['sha256']==lock['lean_binary_sha256'] and binding(kernel)['sha256']==lock['lean_shared_library_sha256']
    sources=[HERE/(n+'.lean') for n in ['CertifiedPreflight','TypedReuse','EvidenceReuse','ReuseCollection','ReusableEntry','ReuseRuntimeControls']];captured=[binding(p) for p in sources]
    names=[]
    for p in sources:
        text=p.read_text();short=re.findall(r'^theorem (\w+)',text,re.M)
        assert short==re.findall(r'^#print axioms (\w+)$',text,re.M)
        code='\n'.join(x for x in text.splitlines() if not x.lstrip().startswith('--'))
        assert not re.search(r'\b(sorry|admit|native_decide|axiom)\b',code)
        names+=['RelationalSuccessor.CandidatePreflightReuse.'+n for n in short]
    assert len(names)==len(set(names))==23
    assert re.findall(r'^#eval (.*)$',sources[-1].read_text(),re.M)==[x['expression'] for x in controls['runtime_cases']]
    allowed={'propext','Quot.sound','Classical.choice'};records=[];import_records=[];reused=[]
    for phase in ('compile','replay'):
        build=HERE/phase;build.mkdir(exist_ok=True)
        for p in build.glob('*.olean'):p.unlink()
        for old in prior['records']:
            if old['phase']!=phase:continue
            output=ROOT/old['olean']['path'];assert binding(output)==old['olean']
            target=build/output.name;shutil.copy2(output,target)
            assert binding(target)['sha256']==old['olean']['sha256']
            reused.append({'phase':phase,'source':old['source'],'prior_output':old['olean'],'reused_output':binding(target)})
        for p in sources:
            assert binding(Path(__file__))==driver and [binding(x) for x in sources]==captured
            output=build/(p.stem+'.olean');log=build/(p.stem+'.log');argv=[str(lean),'-o',str(output),str(p)];started=time.monotonic()
            result=subprocess.run(argv,cwd=p.parent,env=dict(os.environ,LEAN_PATH=str(build)),capture_output=True,text=True,timeout=180)
            log.write_text(result.stdout+result.stderr)
            assert result.returncode==0 and 'warning:' not in result.stdout,(p,result.stdout,result.stderr)
            axioms=sorted({x.strip() for g in re.findall(r'depends on axioms: \[([^]]*)\]',result.stdout) for x in g.split(',') if x.strip()})
            count=len(re.findall(r'(?:depends on axioms:|does not depend on any axioms)',result.stdout));expected=len(re.findall(r'^#print axioms ',p.read_text(),re.M))
            assert count==expected and set(axioms)<=allowed
            row={'phase':phase,'source':binding(p),'argv':argv,'cwd':str(p.parent),'LEAN_PATH':str(build),'exit_code':result.returncode,'log':binding(log),'olean':binding(output),'seconds':round(time.monotonic()-started,3),'axioms':axioms,'inspected_declarations':count}
            if p.stem=='ReuseRuntimeControls':
                assert result.stdout.strip().splitlines()==[x['expected'] for x in controls['runtime_cases']],result.stdout
                row['runtime_composed_cases']=22
            records.append(row);print(phase,p.stem,row['seconds'],flush=True)
            deps=subprocess.run([str(lean),'--deps',str(p)],cwd=p.parent,env=dict(os.environ,LEAN_PATH=str(build)),capture_output=True,text=True,timeout=30)
            assert deps.returncode==0 and not deps.stderr
            origins=[]
            for line in deps.stdout.splitlines():
                dep=Path(line.strip()).resolve();assert dep.is_file()
                if dep.is_relative_to(build):
                    matching=[r for r in records if r['phase']==phase and Path(r['olean']['path']).name==dep.name]
                    cached=[r for r in reused if r['phase']==phase and Path(r['reused_output']['path']).name==dep.name]
                    assert len(matching)+len(cached)==1,dep
                    expected_binding=matching[0]['olean'] if matching else cached[0]['reused_output']
                    assert binding(dep)==expected_binding
                    origin='fresh-local-module' if matching else 'exact-verified-prior-phase-output'
                else:
                    assert dep.is_relative_to(runtime/'lib/lean'),dep
                    origin='pinned-runtime-library'
                origins.append(dict(binding(dep),origin=origin))
            import_records.append({'phase':phase,'source':binding(p),'dependencies':origins})
    assert binding(Path(__file__))==driver and [binding(p) for p in sources]==captured
    assert [binding(p) for p in [context_path,controls_path,prior_path,prior_audit]]==stable
    check_tree(prior);check_tree(audit)
    report={'task':'N01','unit':'K02-preflight-reuse','result':'candidate-fragment-pass','method':'Fresh isolated new-module compilation and separate fresh new-module same-kernel replay; exact verified matching-phase dependency outputs reused without recompilation.','driver':driver,'compiler':binding(lean),'kernel_library':binding(kernel),'toolchain_lock':binding(lock_path),'context_pack':binding(context_path),'control_index':binding(controls_path),'prior_verification':binding(prior_path),'prior_import_audit':binding(prior_audit),'dependency_sources':prior['sources'],'reused_dependencies':reused,'sources':captured,'records':records,'new_declarations':names,'new_declaration_count':23,'new_general_declarations':23,'new_worked_control_declarations':0,'runtime_composed_cases':22,'allowed_axioms':sorted(allowed),'reusable_entry_equal_guarded':True,'local_dependency_rebuild':False,'raw_source_refinement_proved':False,'independent_checker_run':False,'supported_resource_envelope_measured':False,'real_authoritative_snapshot_provider':False,'live_consumer_integration':False,'N03_API_freeze':False,'inherited_discharges':0,'N01_accepted':False,'authority_effect':'none'}
    (HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    import_report={'task':'N01','unit':'K02-preflight-reuse','result':'import-resolution-audit-pass','driver':driver,'verification':binding(HERE/'verification.json'),'resolved_source_phase_pairs':len(import_records),'records':import_records,'claim_scope':'All new imports resolve to fresh local outputs or exact corresponding prior verified compile/replay outputs; dependencies were not rebuilt and checking is not independent.','inherited_discharges':0,'authority_effect':'none'}
    (HERE/'import-resolution-audit.json').write_text(json.dumps(import_report,indent=2)+'\n')
    print('PASS: 23 declarations; 12 fresh new-module invocations; 12 exact import audits; 22 runtime cases per phase.',flush=True)
if __name__=='__main__':run()
