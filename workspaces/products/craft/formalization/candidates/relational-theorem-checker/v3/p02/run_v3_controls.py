"""V3 wrapper inspection controls; no new qualified runtime result is issued."""
from pathlib import Path
import copy
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'execution'))
import support as s
import evidence as e

controls=[]
def positive(name,fn):
    value=fn();s.require(value.get('application_authorized') is False,'inspection authorized application')
    controls.append({'name':name,'result':'pass','expected':'recorded-current-inspection'});return value
def negative(name,fn):
    try:fn()
    except Exception as ex:
        controls.append({'name':name,'result':'pass','expected':'rejected','reason':str(ex).splitlines()[0]});return
    raise AssertionError('unexpected acceptance '+name)

request=s.read(HERE.parent/'p01/request-fixture.json')
payload_path=s.V2/'s13/exact-contract-scope-kind-result.json'
payload=s.read(payload_path)
tag=e.tagged
manifest={'schema':'relational.proof-manifest/v3','identity':e.expected_identity(request),'change_class':'rule-only',
    'witness':{'layout':'staged','modules':[{'role':role,'module':m['module'],'source':tag(m['source']),'olean':tag(m['olean'])} for role,m in zip(['data','typed','closure','expansion'],payload['evidence']['actual'])]},
    'obligations':[o['id'] for o in e.c.required_inventory('rule-only')],
    'general':tag(payload['evidence']['general']['submission_source']),
    'projection':tag(payload['evidence']['projection'][0]['source']),
    'dependencies':tag(payload['evidence']['dependencies']),
    'bound_result':tag(s.binding(payload_path)),'generator':tag(s.binding(HERE/'proof_layout.py')),'authority_effect':'none'}
claims=[{'kind':kind,'model_class':payload['model_class'],'query_scope':payload['closure_scope'],'change_class':'rule-only','source_profile':request['source_profile'],'truth_assumptions':e.TRUTH_ASSUMPTIONS,'evidence_mode':'fresh-invocation-at-creation'} for kind in ['complete-closure','model-expansion']]
wrapper={'schema':'relational.qualification-result/v3','status':'qualified-candidate','request_identity':e.c.identity(request),'run_id':'inspection-shape-fixture-not-a-new-qualification','manifest':manifest,'claims':claims,'resource_report':{'enforcement':'advisory','outcome':'completed','events':[],'policy_identity':e.c.identity(request['resource_policy'])},'payload':tag(s.binding(payload_path)),'complete_closure':True,'application_authorized':False,'authority_effect':'none'}
positive('v3-staged-exact-bound-wrapper-inspection',lambda:e.validate(request,wrapper))
bad_payload=copy.deepcopy(payload);bad_payload['witness_layout']='unknown-layout'
negative('unknown-legacy-layout-rejected',lambda:e.validate_legacy(request['proposal'],bad_payload))
bad=copy.deepcopy(wrapper);bad['manifest']['identity']['request']='0'*64
negative('v3-stale-request-identity',lambda:e.validate(request,bad))
bad=copy.deepcopy(wrapper);bad['manifest']['witness']['modules'].pop()
negative('v3-truncated-manifest',lambda:e.validate(request,bad))
bad=copy.deepcopy(wrapper);bad['manifest']['obligations'].pop()
negative('v3-shrunken-obligations',lambda:e.validate(request,bad))
bad=copy.deepcopy(wrapper);bad['manifest']['generator']['sha256']='0'*64
negative('v3-stale-generator',lambda:e.validate(request,bad))
bad=copy.deepcopy(wrapper);bad['manifest']['general']=bad['manifest']['projection']
negative('v3-general-evidence-transplant',lambda:e.validate(request,bad))
bad=copy.deepcopy(wrapper);bad['resource_report']['policy_identity']='0'*64
negative('v3-resource-policy-substitution',lambda:e.validate(request,bad))
bad=copy.deepcopy(wrapper);bad['claims'][0]['model_class']='source-faithful-with-no-extra-premise'
negative('v3-strengthened-model-class',lambda:e.validate(request,bad))
bad=copy.deepcopy(wrapper);bad['claims'][0]['truth_assumptions']=[]
negative('v3-supplied-truth-assumptions-erased',lambda:e.validate(request,bad))
bad=copy.deepcopy(wrapper);bad['claims'][0]['kind']='active-norm'
negative('v3-norm-from-recursive-evidence',lambda:e.validate(request,bad))
bad=copy.deepcopy(wrapper);bad['application_authorized']=True
negative('v3-saved-evidence-authorizes-apply',lambda:e.validate(request,bad))
s.write(HERE/'v3-manifest-controls.json',{'result':'pass','controls':controls,'scope':'In-memory wrapper of exact current inherited evidence; recorded-current inspection only, no fresh qualification or publication issued.'})
print('V3 manifest controls passed: '+str(len(controls)))
