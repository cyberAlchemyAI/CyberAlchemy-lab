"""Closed performance contract before instrumented execution."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
def obj(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
text={'type':'string','minLength':1};nat={'type':'integer','minimum':0};number={'type':'number','minimum':0}
ref=obj({'path':text,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
nullable=lambda s:{'anyOf':[s,{'type':'null'}]}
stage=obj({'id':nat,'parent':nullable(nat),'name':text,'start_seconds':number,'end_seconds':nullable(number),
    'inclusive_seconds':nullable(number),'exclusive_seconds':nullable(number),'outcome':{'enum':['completed','refused','unfinished']}})
memory=obj({'backend':{'enum':['advisory','cgroup-v2','unavailable']},'peak_aggregate_rss_observed':nullable(nat),
    'hard_aggregate_cap':{'type':'boolean'},'policy_bytes':nat})
memory['allOf']=[{'if':{'properties':{'backend':{'enum':['advisory','unavailable']}}},'then':{'properties':{'hard_aggregate_cap':{'const':False}}}}]
policy=json.loads((HERE.parent/'p01/contracts/resource-policy.schema.json').read_text())
sample=obj({'name':text,'input':ref,'output':ref,'build_mode':{'enum':['cold','warm']},'layout':{'enum':['combined','staged']},
    'workload':obj({'domain':nat,'predicates':nat,'rules':nat,'maximum_rule_variables':nat,'ground_candidates':nat,'typed_instances':nullable(nat)}),
    'resource_policy':policy,'status':{'enum':['qualified-candidate','unknown-resource','cancelled','invalid','unsupported','unsupported-policy']},
    'actual_kernel_completion':{'type':'boolean'},'supervised_seconds':nullable(number),'client_seconds':number,'memory':memory,
    'output_bytes_observed':nullable(nat),'stage_tree':{'type':'array','items':stage},'required_ids':{'type':'array','uniqueItems':True,'items':text},
    'cache_check':nullable(ref),'measurement_scope':text,'authority_effect':{'const':'none'}})
sample['allOf']=[{'if':{'properties':{'status':{'const':'qualified-candidate'}}},'then':{'properties':{'actual_kernel_completion':{'const':True}}},
    'else':{'properties':{'actual_kernel_completion':{'const':False}}}}]
report=obj({'schema':{'const':'relational.performance-report/v3'},'samples':{'type':'array','minItems':1,'items':sample},
    'retained_measurements':{'type':'array','items':ref},'timing_policy':{'const':'Monotonic intervals; exclusive time subtracts the union of direct child intervals; inclusive nesting is not independently summed.'},
    'selection':{'enum':['no-optimization','requires-separate-equivalence-qualified-optimization']},
    'limits':{'type':'array','minItems':1,'items':text},'authority_effect':{'const':'none'}})
(HERE/'performance-report.schema.json').write_text(json.dumps({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:relational:v3:performance-report',**report},indent=2)+'\n')
