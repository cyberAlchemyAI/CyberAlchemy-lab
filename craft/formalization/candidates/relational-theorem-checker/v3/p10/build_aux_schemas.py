"""Closed profile and measurement-summary contracts; immutable runtime schema is reused."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
def obj(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
text={'type':'string','minLength':1};nat={'type':'integer','minimum':0};number={'type':'number','minimum':0}
ref=obj({'path':text,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
sample=json.loads((HERE/'performance-report.schema.json').read_text())['properties']['samples']['items']['properties']
profile=obj({'schema':{'const':'relational.benchmark-profile/v3'},'source':ref,
    'samples':{'type':'array','minItems':3,'items':obj({k:sample[k] for k in ['name','input','workload','build_mode','layout']})},
    'resource_policy':sample['resource_policy'],'profile':{'const':'rich-positive-recursive-v2'},
    'fixed_required_ids':{'type':'array','minItems':20,'maxItems':20,'uniqueItems':True,'items':text},
    'primary_stress_dimension':text,'runtime_roots':{'type':'array','items':text},'uncontrolled':{'type':'array','items':text},'authority_effect':{'const':'none'}})
category=obj({k:({'anyOf':[number,{'type':'null'}]} if k=='other_worker_time' else number) for k in ['compile_tools','general_replay','source_cache_guards','source_projection','reference_evaluator_process','saved_inspection_process','other_worker_time']})
nullable=lambda s:{'anyOf':[s,{'type':'null'}]}
row=obj({'name':text,'status':sample['status'],'client_seconds':number,'worker_seconds':nullable(number),'category_seconds':category,
    'finite_evaluator_seconds':nullable(number),'peak_rss_observed':nullable(nat),'scope':text})
read=obj({'name':text,'seconds':number,'output':ref,'scope':text})
retained=obj({'layout':{'enum':['combined','staged']},'generation':nat,'application_seconds_inclusive':number,
    'proposal_supervised_seconds':number,'successor_registration_supervised_seconds':number,'application_source':ref,
    'proposal_record':ref,'registration_record':ref,'scope':text})
summary=obj({'result':{'const':'pass'},'rows':{'type':'array','items':row},'read_timings':{'type':'array','items':read},
    'recorded_shadow_timings':{'type':'array','minItems':4,'maxItems':4,'items':retained},
    'controls':{'type':'array','items':obj({'name':text,'result':{'const':'pass'}})},'report':ref,'authority_effect':{'const':'none'}})
for name,schema in [('benchmark-profile',profile),('performance-controls',summary)]:
    (HERE/(name+'.schema.json')).write_text(json.dumps({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:relational:v3:'+name,**schema},indent=2)+'\n')
