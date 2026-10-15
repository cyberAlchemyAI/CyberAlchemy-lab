"""Fresh complete Source16 scan and explicit reviewable public-input proposal.

No snapshot, archive export, freezer, service, private fixture or Lab call runs.
"""
import ast,collections,datetime,hashlib,importlib.util,json,os,stat,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];OLD=HERE.parent/'0008'
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v16'
SOURCE='8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7'
PROFILE='8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c'
PRIVATE_HOME=Path('/home/vlad_/.local/share/cal-paperclip-pilot-20261013')
def install(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
B=install('_R06_0009_original_builder',HERE/'build.py')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def binding(path):return B.bind(Path(path))
def at(path):return ROOT/path
def put(name,value):B.put(HERE/name,value)
def instant():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def inspect(row):
    raw=B.C.read(at(row['path']));assert sha(raw)==row['sha256'],row['path']
    findings=[];refusal=None
    try:findings=B.R.scan(raw,row['path'])
    except (ValueError,UnicodeError,RecursionError) as error:refusal=type(error).__name__
    return raw,findings,refusal
def main():
    assert not (HERE/'public-inputs.json').exists(),'exclusive preparation; retain earlier attempt'
    for name in ('build.py','check.py','disposition.schema.json'):
        assert (HERE/name).read_bytes()==(OLD/name).read_bytes(),'original boundary tool changed'
    for name in ('ARE-route.json','ARE-context.json','ARE-effect.json'):
        v=B.load(HERE/name);assert v['result']['ok'] and v['authority_effect']=='none'
    assert binding(API/'source-manifest.json')['sha256']==SOURCE
    assert binding(API/'contract-profile.json')['sha256']==PROFILE
    G=install('_R06_0009_exact_Source16_guard',API/'guard.py')
    source=G.verify(SOURCE);profile=B.load(API/'contract-profile.json');execution=B.load(API/'SCHEMA-EXECUTION-DEPENDENCIES.json')
    assert len(source['files'])==24497 and len(profile['files'])==24496 and len(execution['files'])==1451
    full={r['path']:r for r in source['files']};active={r['path']:r for r in execution['files']}
    assert len(full)==24497 and len(active)==1451
    assert all(full[r['path']]==r for r in [*profile['files'],*execution['files']])
    external=[r for r in source['files'] if Path(r['path']).is_absolute()];assert len(external)==66
    assert not any(at(r['path']).is_relative_to(PRIVATE_HOME) for r in source['files'])
    originals=B.load(OLD/'public-inputs.json');prefix='product/lab/release-candidates/v1/interface/api-integration-v14/'
    successor=API.relative_to(ROOT).as_posix()+'/'
    proposed=[];rebase=[]
    for item in originals['files']:
        old=item['binding'];path=old['path'];new=successor+path[len(prefix):] if path.startswith(prefix) else path
        assert new in full
        if new==path:assert full[new]==old,'nonlocal public dependency drift'
        else:rebase.append({'original_binding':old,'successor_binding':full[new],'kind':item['kind']})
        proposed.append({'binding':full[new],'kind':item['kind'],'reasons':[*item['reasons'],*(['Exact API16-local successor binding; original API14 binding retained in review correspondence.'] if new!=path else [])]})
    assert len(rebase)==69 and len(proposed)==446
    tree=ast.parse((API/'service.py').read_bytes())
    assignment=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and t.attr=='code_files' for t in n.targets))
    declared=ast.literal_eval(assignment.value.generators[0].iter)
    added=[]
    for name,why in [('machine_auth_scope.py','Actual Service.code_files and Machine transport select/proof/authenticate use the exact pure Source8 source-fact scope helper.'),
                     ('legacy_context_sessions.py','Actual Service.code_files and Session factory select the distinct original signed Legacy fixture runtime with unchanged private authority checks.')]:
        path=successor+name;assert name in declared and path in active and full[path]==active[path]
        proposed.append({'binding':full[path],'kind':'runtime-code','reasons':[why]});added.append(full[path])
    proposed.sort(key=lambda r:r['binding']['path'])
    chosen={r['binding']['path'] for r in proposed};assert len(chosen)==len(proposed)==448
    observations=[];public_findings=[];bytes_scanned=0;started=instant()
    prior={r['path']:r for r in B.load(ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/installation-release-R06-api10-audit-0148.json')['rows']}
    assert len(prior)==112
    for index,row in enumerate(source['files'],1):
        raw,findings,refusal=inspect(row);bytes_scanned+=len(raw);path=row['path']
        protected=B.protected_code(path) or Path(path).is_absolute() or Path(path).suffix=='.snapshot' or '/history/' in path or path in prior
        public=path in chosen
        if public:
            assert not protected and not findings and refusal is None,'public gate refusal: '+path
            B.C.privacy(raw)
        if findings or refusal:public_findings.append({'binding':row,'field_selectors':findings,'inspection_refusal_class':refusal,'public_selected':public})
        observations.append({**row,'size_bytes':len(raw),'active_execution_input':path in active,'proposed_public':public,
            'protected_path_gate':protected,'field_findings':findings,'inspection_refusal_class':refusal})
        if index%4000==0:print(json.dumps({'actual_fresh_rows_scanned':index,'public_selected':len(chosen),'finding_or_refusal_rows':len(public_findings)}),flush=True)
    assert {r['path'] for r in observations}==set(full) and len(observations)==24497
    assert all(not r['public_selected'] for r in public_findings)
    G.verify(SOURCE)
    assert binding(B.NATIVE)['sha256']==B.NATIVE_SHA and stat.S_IMODE(B.NATIVE.stat().st_mode)==0o755
    package=ROOT/'product/lab/release-candidates/v1/packaging/R02/packages/0003';r02=B.load(package/'selection.json')
    B.C.environment_guard(r02['environment'])
    wheels=[binding(package/'wheels'/r['filename']) for r in r02['wheels']];assert len(wheels)==8
    for r in r02['wheels']:assert sha(B.C.read(package/'wheels'/r['filename']))==r['sha256']
    abi=[binding(Path(n).resolve()) for n in ('/lib64/ld-linux-x86-64.so.2','/lib/x86_64-linux-gnu/libgcc_s.so.1','/lib/x86_64-linux-gnu/libc.so.6')]
    for row in abi:assert full.get(row['path'])==row,'ABI not in complete exact Source16'
    selection={'schema_version':'lab-R06-final-public-selection/v1-candidate','api_source_binding':binding(API/'source-manifest.json'),
        'api_profile_binding':binding(API/'contract-profile.json'),'files':proposed,'authority_effect':'none','actual_owner_outcome':None}
    put('public-inputs.json',selection)
    B.API=API
    B.public_selection(binding(HERE/'public-inputs.json'),source,profile,execution)
    omitted=[{'binding':r,'reason':'Exact mandatory active dependency remains protected under explicit public selection; omission does not remove guard obligation.'} for r in execution['files'] if r['path'] not in chosen]
    review={'schema_version':'lab-R06-Source16-explicit-public-selection-review/v1-candidate','result':'PASS-preparation','started_at':started,'reviewed_at':instant(),
        'API_source_binding':binding(API/'source-manifest.json'),'API_profile_binding':binding(API/'contract-profile.json'),'schema_execution_binding':binding(API/'SCHEMA-EXECUTION-DEPENDENCIES.json'),
        'public_selection_binding':binding(HERE/'public-inputs.json'),'prepare_code_binding':binding(Path(__file__)),
        'unchanged_original_tools':[binding(HERE/n) for n in ('build.py','check.py','disposition.schema.json')],
        'actual_source_entry_exit':'PASS','full_source_rows_retained':24497,'full_profile_rows_retained':24496,'active_rows_retained':1451,'external_rows_retained':66,
        'actual_rows_scanned':len(observations),'actual_bytes_scanned':bytes_scanned,'all_row_observations':observations,'finding_or_refusal_rows':public_findings,
        'public_finding_or_refusal_count':0,'prior_public_selection_binding':binding(OLD/'public-inputs.json'),'exact_API14_to_API16_correspondences':rebase,
        'additional_declared_runtime_bindings':added,'proposal_members':len(proposed),'proposal_kind_counts':dict(collections.Counter(r['kind'] for r in proposed)),
        'active_inputs_outside_public_proposal':omitted,'host_provided_native_binding':binding(B.NATIVE),'native_host_mode':'0o755','ABI_library_bindings':abi,'offline_wheel_bindings':wheels,
        'Paperclip_private_home_not_selected':True,'Paperclip_private_home_read_or_copied':False,'Root_exact_selection_required_before_freeze':True,
        'boundary_frozen':False,'public_payload_exported':False,'R06_complete':False,'whole_API_qualified':False,'authority_effect':'none','actual_owner_outcome':None}
    put('public-inputs-review.json',review)
    limitations={'schema_version':'lab-R06-Source16-public-proposal-limitations/v1-candidate','observed_at':instant(),
        'public_selection_binding':binding(HERE/'public-inputs.json'),'review_binding':binding(HERE/'public-inputs-review.json'),
        'active_rows_outside_public_count':len(omitted),'all_full_proof_rows_retained':True,
        'private_archives_signatures_construction_and_R02_snapshots':'All raw Legacy/Source8 fixture materials and original embedded-test R02 snapshots remain exact protected proof/host dependencies; no export authorization inferred from signatures.',
        'protected_fixture_named_runtime_files':[r for r in omitted if r['binding']['path'].endswith(('/fixture_context_sessions.py','/legacy_fixture_selection.py','/api50-typed-checks-v4/fixture.py'))],
        'protected_actual_runtime_scope_helpers':[r for r in omitted if '/fact-read-scope-v' in r['binding']['path']],
        'conservative_original_schema_gate':B.load(OLD/'public-inputs-limitations.json')['conservative_rejected_path_interpretations'],
        'Paperclip_home':'Outside Source16 proof/public selection; persistent policy/key/database/server logs are neither selected nor inspected/copied.',
        'historical_builder_context':'Unchanged0241 context/ARE and0209 recovery remain bound historical nonauthorizing inputs; new own ARE receipts cover only this authorized preparation.',
        'native_restore':'Unchanged originalR02 archive restore yields0600, not executable installation. Actual hostfb8470755/ABI/wheels are separately verified; signedtmp locator unchanged.',
        'snapshot_nested_constructor_names':'Future arbitrary public snapshots need independent verifier scope; current proposal contains no raw snapshot.',
        'pending_before_any_snapshot_or_freezer':['Parent review of exact448-member public-inputs hash and this limitation map','Fresh explicit effect boundary for actual snapshot/freezer/conformance outputs','Actual immutable boundary pin and distinct OS terminal evidence'],
        'conformance_claim_ceiling':'Original17 checks establish bounded candidate accounting/private scratch restore only; never wholeR06/release/API/human/R08 closure.',
        'portable_self_containment_claimed':False,'public_export_authorized':False,'boundary_frozen':False,'R06_complete':False,'authority_effect':'none','actual_owner_outcome':None}
    put('public-inputs-limitations.json',limitations)
    G.verify(SOURCE)
    print(json.dumps({'result':'PASS-preparation','public_members':448,'actual_source_rows_scanned':24497,'public_selection_binding':binding(HERE/'public-inputs.json'),
        'review_binding':binding(HERE/'public-inputs-review.json'),'limitations_binding':binding(HERE/'public-inputs-limitations.json'),'snapshot_or_freezer_executed':False,'R06_complete':False}),flush=True)
if __name__=='__main__':main()
