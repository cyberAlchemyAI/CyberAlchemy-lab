"""Check fixed K04 sources and joins without accepting meanings or discharging IDs."""
from pathlib import Path
import hashlib, importlib.util, json, os, re, shutil, subprocess

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'authority/artifact-types').is_dir())
BASE=ROOT/'craft/formalization/candidates/relational-theorem-checker'
N=HERE.parent.parent
def binding(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def read(path):return json.loads(path.read_text())
def check_bindings(value):
    if isinstance(value,dict):
        if {'path','sha256'} <= value.keys():
            assert binding(ROOT/value['path'])=={k:value[k] for k in ['path','sha256']},value['path']
        for child in value.values():check_bindings(child)
    elif isinstance(value,list):
        for child in value:check_bindings(child)
def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
def execute(argv,build):
    result=subprocess.run(argv,cwd=build,env={**os.environ,'LEAN_PATH':str(build)},
        capture_output=True,text=True,timeout=90)
    assert result.returncode==0,result.stdout+result.stderr
    assert not result.stderr.strip(),result.stderr
    assert 'warning:' not in result.stdout,result.stdout
    return result.stdout

if __name__=='__main__':
    driver=binding(Path(__file__))
    manifests=[HERE/name for name in ['context-pack.json','profile-manifest.json','generation-audit.json','control-index.json']]
    for path in manifests:check_bindings(read(path))
    old_model_report=HERE.parent/'K04-draft/verification.json'
    check_bindings(read(old_model_report))
    assert read(old_model_report)['result']=='pass'
    request=read(N/'K04-assessment-request.json')
    assert request['status']=='pending-actual-response' and request['actual_response'] is None
    assert read(N/'sequential-review.json')['current_unit']=='K04'
    compiler=load_module(HERE/'generate_profiles.py','k04_profiles_readonly')
    text,trace=compiler.compile_profiles()
    assert text==(HERE/'LessonBodyProfiles.lean').read_text()
    assert trace==read(HERE/'generation-audit.json')['assertion_trace']
    controls_generator=load_module(HERE/'generate_controls.py','k04_controls_readonly')
    text,cases=controls_generator.generate()
    assert text==(HERE/'LessonSourceControls.lean').read_text()
    assert cases==read(HERE/'control-index.json')['runtime_cases']
    assert len(cases)==279 and sum(c['category']=='complete-schema' for c in cases)==250
    paths=[HERE/'LessonBodyProfiles.lean',HERE/'LessonSourceAdapter.lean',HERE/'LessonSourceControls.lean']
    new_names=[]
    for path in paths:
        code=path.read_text()
        names=re.findall(r'^theorem (\w+)',code,re.M)
        assert names==re.findall(r'^#print axioms (\w+)$',code,re.M)
        executable=re.sub(r'"(?:\\.|[^"\\])*"','""',code)
        executable='\n'.join(line for line in executable.splitlines() if not line.strip().startswith('--'))
        assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b',executable)
        new_names += ['RelationalSuccessor.CandidateLessonSource.'+name for name in names]
    assert len(new_names)==len(set(new_names))==9
    prior_report=HERE.parent/'K02-supporting-sources/verification.json'
    prior_audit=HERE.parent/'K02-supporting-sources/import-resolution-audit.json'
    prior=read(prior_report);audit=read(prior_audit)
    check_bindings(prior);check_bindings(audit)
    assert prior['result']=='candidate-fragment-pass'
    assert audit['result']=='import-resolution-audit-pass' and audit['verification']==binding(prior_report)
    pool={}
    for record in prior['records']+prior['reused_dependencies']:
        output=record.get('olean',record.get('reused_output'))
        key=(record['phase'],Path(output['path']).name)
        assert key not in pool
        pool[key]={'phase':record['phase'],'source':record['source'],'output':output}
    lock_path=BASE/'v1/formal/toolchain-lock.json'
    lock=read(lock_path)
    runtime=BASE/'v1/formal/.toolcache/lean-4.33.1-linux'
    lean=runtime/'bin/lean';kernel=runtime/'lib/lean/libleanshared.so'
    assert binding(lean)['sha256']==lock['lean_binary_sha256']
    assert binding(kernel)['sha256']==lock['lean_shared_library_sha256']
    sources=[HERE.parent/'K04-draft/LessonUseCandidate.lean',HERE.parent/'K04-draft/LessonUseControls.lean',*paths]
    stable=[binding(path) for path in sources+manifests+[prior_report,prior_audit,old_model_report]]
    records=[];imports=[];reused=[]
    for phase in ['compile','replay']:
        build=HERE/phase
        build.mkdir(exist_ok=True)
        for path in build.glob('*.olean'):path.unlink()
        for (entry_phase,_),entry in pool.items():
            if entry_phase!=phase:continue
            original=ROOT/entry['output']['path']
            target=build/original.name
            shutil.copy2(original,target)
            assert binding(target)['sha256']==entry['output']['sha256']
            reused.append({**entry,'reused_output':binding(target)})
        known={path.stem:binding(path) for path in sources}
        observed=[]
        for source in sources:
            copied=build/source.name
            shutil.copy2(source,copied)
            assert binding(copied)['sha256']==binding(source)['sha256']
            dependencies=execute([str(lean),'--deps',source.name],build)
            for line in dependencies.splitlines():
                dep=Path(line.strip()).resolve()
                assert dep.is_relative_to(build) or dep.is_relative_to(runtime/'lib/lean'),str(dep)
                if dep.is_relative_to(build):
                    assert dep.exists(),str(dep)
                    if dep.stem in known:
                        expected=next(r['olean'] for r in records if r['phase']==phase and Path(r['olean']['path']).name==dep.name)
                        assert binding(dep)==expected
                    else:
                        entry=pool[(phase,dep.name)]
                        assert binding(dep)['sha256']==entry['output']['sha256']
                imports.append({'phase':phase,'module':source.stem,'dependency':binding(dep)})
            log=execute([str(lean),'-o',source.stem+'.olean',source.name],build)
            log_path=build/(source.stem+'.log');log_path.write_text(log)
            inspected=re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",log,re.S)
            local_names=re.findall(r'^theorem (\w+)',source.read_text(),re.M) if source in paths else []
            assert {name for name,_ in inspected}=={'RelationalSuccessor.CandidateLessonSource.'+name for name in local_names}
            for _,listed in inspected:
                assert set(re.findall(r'[A-Za-z][A-Za-z0-9_.]*',listed))<={'propext','Quot.sound','Classical.choice'},listed
            booleans=[line=='true' for line in log.splitlines() if line in ['true','false']]
            if source.name=='LessonSourceControls.lean':
                assert len(booleans)==len(cases)
                assert all(actual==case['expected'] for actual,case in zip(booleans,cases))
                observed=booleans
            else:assert not booleans
            records.append({'phase':phase,'source':binding(source),'olean':binding(build/(source.stem+'.olean')),
                'log':binding(log_path),'axiom_inspections':len(inspected),'runtime_controls':len(booleans),
                'fresh_compilation':True,'prior_model_module':source not in paths})
            assert binding(Path(__file__))==driver
            for item in stable:assert binding(ROOT/item['path'])==item
        assert len(observed)==279
    report={'schema':'relational.k04-source-adapter-verification/v1','result':'candidate-fragment-pass',
        'task':'N01','unit':'K04-source-adapter','driver':driver,'context':binding(HERE/'context-pack.json'),
        'source_profile_manifest':binding(HERE/'profile-manifest.json'),'generation':binding(HERE/'generation-audit.json'),
        'controls':binding(HERE/'control-index.json'),'prior_verifications':[binding(prior_report),binding(old_model_report)],
        'prior_import_audit':binding(prior_audit),'toolchain_lock':binding(lock_path),
        'lean_binary':binding(lean),'kernel':binding(kernel),'records':records,'reused_dependencies':reused,
        'import_resolution':imports,'theorems':new_names,'new_candidate_theorems':9,
        'candidate_runtime_controls':279,'complete_shape_controls':250,'semantic_join_controls':29,
        'fresh_compilations':len(records),'axiom_inspections':sum(r['axiom_inspections'] for r in records),
        'fixed_complete_body_shapes':True,'complete_record_field_count':55,'record_type_count':6,
        'source_qualifier_adapter_exact':True,'qualified_source_requires_independent_candidate_meaning':True,
        'actual_owner_assessment':None,'registered_in_main_preparation_index':False,
        'general_schema_compiler_correspondence':False,'raw_source_refinement':False,
        'whole_original_source_interpretation':False,'independent_verification':False,
        'authenticated_policy_provider':False,'N01_accepted':False,'inherited_discharges':0,
        'pending_ids':request['pending_ids'],'goal_complete':False,'authority_effect':'none'}
    (HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ['result','new_candidate_theorems','candidate_runtime_controls',
        'fresh_compilations','axiom_inspections','inherited_discharges','N01_accepted']}))
