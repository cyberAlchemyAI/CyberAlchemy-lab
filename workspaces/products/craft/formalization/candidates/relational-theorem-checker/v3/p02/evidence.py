"""Exact saved evidence correlation. No saved result grants application."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import importlib.util
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'docs/plans/relational-theorem-checker/PLAN-SOURCE.json').is_file())
import proof_layout
_spec=importlib.util.spec_from_file_location('relational_v3_contracts',HERE.parent/'p01/contracts.py')
c=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(c)
TRUTH_ASSUMPTIONS=[
    'Externally supplied accepted assessments and independent root truth.',
    'Tested JSON normalization and source-to-Lean generation.',
    'Same pinned Lean kernel and trusted host/hash execution.',
]


def require(condition,message):
    if not condition: raise ValueError(message)
def identity(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def check(binding):
    p=Path(binding['path'])
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in str(p),'unsafe repository binding')
    path=(ROOT/p).resolve()
    require(path.is_relative_to(ROOT),'binding resolves outside repository')
    require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==binding['sha256'],'missing or stale bound artifact '+str(p))
    return path
def boundary(proposal,result=None):
    request={'proposal':proposal}
    if result is not None:request['result']=result
    result=subprocess.run([sys.executable,str(HERE/'legacy_boundary.py')],input=json.dumps(request),capture_output=True,text=True,timeout=60)
    try:response=json.loads(result.stdout)
    except Exception as e:raise ValueError('legacy boundary failed '+result.stderr[:200]) from e
    require(result.returncode==0 and response['ok'],response.get('error','legacy boundary failed'))
    return response['value']


def validate_legacy(proposal,result):
    require(result.get('witness_layout') in [None,'split-independent-stages-v2'],'unknown legacy witness layout')
    actual=result['evidence']['actual']
    split=result.get('witness_layout')=='split-independent-stages-v2'
    require(len(actual)==(4 if split else 1),'incomplete actual proof module inventory')
    info=boundary(proposal,result)
    evaluation={'closure':result['closure'],'steps':result['certificates']}
    if split:
        layout=result['evidence']['layout']
        require(len(layout['parts'])==4,'incomplete split layout parts')
        source=check(layout['combined_source'])
        stem=source.stem
        generated=proof_layout.render(info['before_normal_form'],info['normal_form'],evaluation,'staged',stem)
        combined=proof_layout.render(info['before_normal_form'],info['normal_form'],evaluation,'combined',stem)[0][2]
        require(source.read_text()==combined,'combined witness values/proofs differ from exact proposal/result')
        require(len(set(x['module'] for x in actual))==4,'duplicate actual module')
        for n in range(4):
            role,name,text=generated[n]; part=layout['parts'][n]; compiled=actual[n]
            require(part['module']==name and compiled['module']==name and compiled['source']==part['source'],'module/order/source correlation changed')
            require(check(part['source']).read_text()==text,'generated staged source differs')
            check(compiled['olean'])
        check(layout['generator'])
    else:
        stem=actual[0]['module']
        expected=proof_layout.render(info['before_normal_form'],info['normal_form'],evaluation,'combined',stem)[0][2]
        require(check(actual[0]['source']).read_text()==expected,'generated combined source differs')
        check(actual[0]['olean'])
    require(len(result['evidence']['projection'])==1,'wrong projection witness inventory')
    require(check(result['evidence']['projection'][0]['source']).read_text()==info['projection_source'],'projection/source-support mismatch')
    paths={b['path'] for o in result['obligations'] for b in o['evidence']}
    require(len(paths)==1,'ambiguous obligation evidence')
    for o in result['obligations']:
        for b in o['evidence']:
            evidence=c.decode(check(b).read_bytes())
            require(all(evidence[k]==result['evidence'][k] for k in ['actual','general','projection','dependencies']),'result differs from bound proof evidence')
    general=result['evidence']['general']
    audit=general['audit']
    require(audit['accepted'] and audit['fresh_kernel_replay'] and audit['allowed_axiom_types_bound'],'missing recorded general replay')
    require(audit['required_statement']=='Successor.Runtime.Catalog.RequiredGeneralBundle' and audit['statement_mode']=='definition-value','wrong required statement/mode')
    require(set(audit['transitive_axioms']) <= {'propext','Quot.sound','Classical.choice'},'custom transitive axiom')
    expected='import RuntimeCatalog\nimport RuntimeProofs\nnamespace V2Submission\ntheorem required : Successor.Runtime.Catalog.RequiredGeneralBundle := Successor.Runtime.Proofs.general_bundle\nend V2Submission\n'
    require(check(general['submission_source']).read_text()==expected,'general submission target/value changed')
    require(len(general['modules'])==1 and general['modules'][0]['module']=='Submitted','general submission module inventory')
    for m in general['modules']:
        require(check(m['source']).read_text()==expected,'general compiled source differs')
        check(m['olean'])
    return {'status':'recorded-current','application_authorized':False,'authority_effect':'none','normalized':info}


def tagged(binding):return {'kind':'repo',**binding}


def expected_identity(request):
    p=request['proposal'];b=p['before']
    return {'request':c.identity(request),'proposal':c.identity(p),'baseline':c.identity(b),
        'profile':b['profile_identity'],'catalog':c.identity(c.catalog()),'toolchain':b['toolchain']['sha256'],
        'source_profile':c.identity({'id':request['source_profile'],'profile_identity':b['profile_identity']})}


def validate(request,result,manifest=None):
    c.validate('request',request);c.validate('result',result)
    require(result['status']=='qualified-candidate','no proof manifest for incomplete/refused result')
    manifest=result['manifest'] if manifest is None else manifest
    require(manifest==result['manifest'],'caller manifest substitution')
    c.validate_manifest_inventory(manifest,'rule-only')
    require(result['request_identity']==c.identity(request) and manifest['identity']==expected_identity(request),'request/profile/catalog/toolchain identity mismatch')
    require(result['resource_report']['policy_identity']==c.identity(request['resource_policy']),'resource-policy identity mismatch')
    require(manifest['witness']['layout']==request['layout'],'requested witness layout mismatch')
    require(manifest['bound_result']==result['payload'],'payload binding mismatch')
    require(manifest['generator']==tagged({'path':str((HERE/'proof_layout.py').relative_to(ROOT)),'sha256':hashlib.sha256((HERE/'proof_layout.py').read_bytes()).hexdigest()}),'generator changed')
    payload=c.decode(check(result['payload']).read_bytes())
    saved=validate_legacy(request['proposal'],payload)
    actual=payload['evidence']['actual'];modules=manifest['witness']['modules']
    require(len(modules)==len(actual),'manifest/actual module count mismatch')
    for n,module in enumerate(modules):
        compiled=actual[n]
        require(module['module']==compiled['module'] and module['source']==tagged(compiled['source']) and module['olean']==tagged(compiled['olean']),'manifest differs from bound module evidence')
    require(manifest['general']==tagged(payload['evidence']['general']['submission_source']),'manifest general source mismatch')
    require(manifest['projection']==tagged(payload['evidence']['projection'][0]['source']),'manifest projection source mismatch')
    require(manifest['dependencies']==tagged(payload['evidence']['dependencies']),'manifest dependencies mismatch')
    claims=result['claims']
    require(all(x['change_class']=='rule-only' and x['source_profile']==request['source_profile'] for x in claims),'claim scope/profile differs')
    require(all(x['kind'] in ['complete-closure','model-expansion'] for x in claims),'query/norm claims require their separate checked interfaces')
    require(all(x['model_class']==payload['model_class'] and x['query_scope']==payload['closure_scope'] for x in claims),'claim model/closure scope mismatch')
    require(all(x['truth_assumptions']==TRUTH_ASSUMPTIONS for x in claims),'claim truth assumptions omitted or changed')
    return {'schema':'relational.inspection-result/v3','status':'recorded-current','request_identity':c.identity(request),'checked_bindings':[result['payload'],manifest['generator'],manifest['general'],manifest['projection'],manifest['dependencies']]+[b for m in modules for b in [m['source'],m['olean']]],'reason':'Exact current request/source/value/module/obligation evidence; saved inspection is not fresh application replay.','application_authorized':False,'authority_effect':'none'}
