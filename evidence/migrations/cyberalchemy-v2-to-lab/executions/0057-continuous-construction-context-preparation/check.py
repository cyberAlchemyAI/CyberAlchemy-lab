"""Read-only governance preflight against the frozen, tested 0056 package."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
PREV=HERE.parent/'0056-continuous-task-loop-context-import'
PACKAGE=ROOT/'.local/ontology-context-import-0056/package'
PREFIX='cyberAlchemy-v2/ontology/governance/continuous-construction/'
P=PACKAGE/PREFIX
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
read=tool.read
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,obj):
    content=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    path=HERE/name
    if path.exists() and path.read_text()!=content:raise ValueError('Frozen result changed: '+name)
    path.write_text(content)
def command(args):
    result=subprocess.run(args,capture_output=True,text=True)
    return {'command':args,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
def run():
    for b in read(PREV/'verification.json')['bindings']:
        assert sha(ROOT/b['path'])==b['sha256'],b['path']
    manifest=read(PREV/'package-inputs.json')
    for b in manifest:assert sha(PACKAGE/b['path'])==b['sha256'],b['path']
    binding=read(P/'construction-binding.json');evidence=read(P/'evidence/conformance-candidate.json')
    checks=[]
    def exact(label,path,expected):
        file=PACKAGE/path
        observed=sha(file) if file.is_file() else None
        checks.append({'binding':label,'path':path,'expected_sha256':expected,'observed_sha256':observed,'result':'PASS' if observed==expected else 'BLOCK'})
    def walk(value,ptr):
        if isinstance(value,dict):
            if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str):exact(ptr,value['path'],value['sha256'])
            for k,v in value.items():walk(v,ptr+'/'+k)
        elif isinstance(value,list):
            for i,v in enumerate(value):walk(v,ptr+'/'+str(i))
    walk(binding['stages'],'construction-binding.json#/stages')
    compiler=binding['stages'][4]['compiler'];runtime=binding['stages'][5]['runtime']
    for key in ['compiler','views']:exact('construction compiler '+key,compiler[key+'_path'],compiler[key+'_sha256'])
    for key,file in [('manifest','Cargo.toml'),('lock','Cargo.lock'),('library','src/lib.rs'),('cli','src/main.rs')]:
        exact('construction runtime '+key,PREFIX+'runtime/'+file,runtime[key+'_sha256'])
        exact('evidence runtime '+key,PREFIX+'runtime/'+file,evidence['exact_runtime_baseline'][key+'_sha256'])
    for key,file in [('graph','graph.json'),('system_ontology','system-ontology.json'),('build_receipt','build-receipt.json')]:
        exact('evidence generated '+key,PREFIX+'domainspec/generated/'+file,evidence['domainspec_build'][key+'_sha256'])
    for selected in binding['selected_sources']:
        lines=(PACKAGE/selected['path']).read_bytes().splitlines(keepends=True)
        indexes=[i for i,line in enumerate(lines) if line.rstrip(b'\r\n').decode()==selected['selector']]
        assert len(indexes)==1
        start=indexes[0];end=next((i for i in range(start+1,len(lines)) if lines[i].startswith(b'## ')),len(lines))
        assert hashlib.sha256(b''.join(lines[start:end])).hexdigest()==selected['sha256']
    business=read(P/'business-ontology.json');system=read(P/'domainspec/generated/system-ontology.json')
    for graph,idkey,edges in [(business,'id','relations'),(system,'node_id','edges')]:
        ids=[n[idkey] for n in graph['nodes']];assert len(ids)==len(set(ids));assert graph['authority_effect']=='none'
        for edge in graph[edges]:assert edge['source'] in ids and edge['target'] in ids
    counts={'business_concepts':len(business['nodes']),'business_relations':len(business['relations']),'system_concepts':len(system['nodes']),'system_relations':len(system['edges'])}
    missing=[s for s in business['source_bindings'] if not (PACKAGE/s['path']).is_file()]
    loader='/home/vrondelli/.cache/auth-completion/build-tools/node_modules/tsx/dist/loader.mjs'
    validation=command(['node','--import',loader,str(P/'scripts/validate.ts')])
    dump('source-validation.json',validation)
    build=command(['node','--import',loader,str(P/'scripts/build.ts'),'--emit-json'])
    if build['exit_code']==0:
        output=json.loads(build['stdout'])
        build={'exit_code':0,'output_sha256':hashlib.sha256(build['stdout'].encode()).hexdigest(),'changed_generated_artifacts':[name for name,content in output.items() if (P/'domainspec/generated'/name).read_text()!=content]}
    dump('build-check.json',build)
    binary=P/'runtime/target/debug/governance-continuous-construction'
    cases=[]
    for case in evidence['positive_cli_cases']+evidence['hostile_cli_cases']:
        result=command([str(binary),'evaluate','--program',str(P/'programs/continuous-construction.program.json'),'--attempt',str(P/case['attempt']),'--repository-root',str(PACKAGE)])
        observed=json.loads(result['stdout']);serialized=json.dumps(observed)
        matches=observed['decision']==case['decision'] and observed['effect_authorized'] is False and observed['authority_effect']=='none'
        matches=matches and all(code in serialized for code in case.get('codes',[]))
        if 'routine_confirmation_required' in case:matches=matches and observed['routine_confirmation_required']==case['routine_confirmation_required']
        cases.append({'attempt':case['attempt'],'expected':case,'observed':observed,'exit_code':result['exit_code'],'result':'PASS' if matches else 'BLOCK'})
    dump('decision-examples.json',cases)
    transcripts=read(PREV/'validation-transcripts.json')
    rust=next(t for t in transcripts if t['command'][:2]==['cargo','test'])
    assert rust['exit_code']==0
    count=sum(int(n) for n in re.findall(r'test result: ok\. (\d+) passed;',rust['stdout']))
    assert count==29
    for b in manifest:assert sha(PACKAGE/b['path'])==b['sha256'],'Validation mutated '+b['path']
    report={'result':'BLOCK','authority_effect':'none','counts':counts,'exact_bindings':checks,'stale_binding_count':sum(c['result']=='BLOCK' for c in checks),'missing_selected_sources':missing,'source_validator_passed':validation['exit_code']==0,'decision_cases_passed':sum(c['result']=='PASS' for c in cases),'decision_cases_total':len(cases),'reused_rust_tests':count,'snapshot_manifest':{'path':str((PREV/'package-inputs.json').relative_to(ROOT)),'sha256':sha(PREV/'package-inputs.json')},'limitations':['Runtime fixture success does not repair stale construction evidence.','Missing governance Product selection needs exact recovery or an explicit successor selection.','No context imported and no operational authority granted.']}
    assert report['stale_binding_count']>0 and validation['exit_code']!=0
    dump('preparation.json',report)
    return report
if __name__=='__main__':
    result=run();print(json.dumps({k:v for k,v in result.items() if k not in ['exact_bindings','missing_selected_sources']}))
