"""Closed transport schema for the supervisor envelope and optional inner result."""
from pathlib import Path
import copy
import json
HERE=Path(__file__).resolve().parent
def obj(properties,required=None):return {'type':'object','properties':properties,'required':list(properties) if required is None else required,'additionalProperties':False}
def arr(items):return {'type':'array','items':items}
text={'type':'string'};number={'type':'number','minimum':0};boolean={'type':'boolean'}
digest={'type':'string','pattern':'^[0-9a-f]{64}$'}
binding=obj({'path':text,'sha256':digest})
event=obj({'kind':text,'detail':text})
run_props={'schema':{'const':'relational.supervised-run/v3'},'status':{'enum':['refused','completed','nonqualified']},
           'enforcement':{'enum':['advisory','cgroup-v2','unavailable']},
           'outcome':{'enum':['completed','timeout','oom','cancelled','output-limit','policy-unavailable','worker-failed']},
           'events':arr(event),'policy_identity':digest,'complete':boolean,'qualified_receipt':{'const':False},
           'application_authorized':{'const':False},'authority_effect':{'const':'none'},'reason':text,'seconds':number,
           'job':text,'output_bytes_observed':{'type':'integer','minimum':0},'aggregate_rss_peak_observed':{'type':'integer','minimum':0},
           'observed_pids':arr({'type':'integer','minimum':1}),
           'cleanup':obj({'observed_pids':arr({'type':'integer','minimum':1}),'remaining_pids':{'const':[]}}),'output_prefix':text}
run_required=list(run_props)[:12]
run=obj(run_props,run_required)
old=json.loads((HERE.parent/'p01/contracts/result.schema.json').read_text())
common={'schema':{'const':'relational.supervised-qualification/v3'},'status':text,'qualified_result':{'type':'null'},
        'claims':{'const':[]},'complete_closure':{'const':False},'application_authorized':{'const':False},
        'authority_effect':{'const':'none'},'policy_identity':digest,'supervised_run':{'oneOf':[run,{'type':'null'}]},
        'request_bytes_sha256':digest,'reason':text,'failure_result':{'oneOf':old['oneOf'][1:]}}
failure=copy.deepcopy(common);failure['status']={'enum':['invalid','unsupported','unknown-resource','cancelled','unsupported-policy']}
failure=obj(failure,list(common)[:9]+['reason'])
success=copy.deepcopy(common)
success.pop('reason');success.pop('failure_result')
success.update(status={'const':'qualified-candidate'},qualified_result=old['oneOf'][0],
               claims=old['oneOf'][0]['properties']['claims'],complete_closure={'const':True},completion=binding)
finished=copy.deepcopy(run);finished['properties']['status']={'const':'completed'};finished['properties']['complete']={'const':True};finished['properties']['outcome']={'const':'completed'}
success['supervised_run']=finished
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:relational:v3:supervised-qualification','oneOf':[obj(success),failure]}
(HERE/'supervised-result.schema.json').write_text(json.dumps(schema,indent=2)+'\n')
