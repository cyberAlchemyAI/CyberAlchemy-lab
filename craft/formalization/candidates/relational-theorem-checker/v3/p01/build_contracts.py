"""Build strict v3 contracts from normative P00 and bound predecessor inputs."""
from pathlib import Path
import copy
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'execution'))
import support as s

DRAFT = 'https://json-schema.org/draft/2020-12/schema'
DIGEST = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
TEXT = {'type': 'string', 'minLength': 1}
NONE = {'const': 'none'}
FALSE = {'const': False}


def obj(properties, optional=()):
    return {'type': 'object', 'properties': properties, 'required': [k for k in properties if k not in optional], 'additionalProperties': False}


def array(items, **limits):
    return {'type': 'array', 'items': items, **limits}


def schema(name, value):
    return {'$schema': DRAFT, '$id': 'urn:relational:v3:' + name, **value}


def build():
    here = HERE / 'contracts'
    here.mkdir(exist_ok=True)
    v2catalog = s.read(s.V2 / 's15/obligation-catalog.json')
    catalog = copy.deepcopy(v2catalog)
    catalog['schema'] = 'relational.obligation-catalog/v3'
    catalog['source_catalog'] = s.binding(s.V2 / 's15/obligation-catalog.json')
    catalog['normative_contract'] = s.binding(HERE.parent / 'p00/EvidenceSemantics.lean')
    catalog['actual_registration_strategy'] = {'required_class': 'register', 'qualification_class': 'rule-only', 'method': 'fresh 20-obligation identity extension', 'receipt_reuse': False}
    catalog['supported_source_profile'] = 'rich-positive-recursive-v2'
    catalog['selected_extension_profiles'] = ['E00','E01','E02','E03','E04','E05','E06']
    catalog['extension_qualification'] = 'Each extension needs its independent additional catalog; selection alone does not implement or qualify it.'
    s.write(HERE / 'catalog.json', catalog)
    binding = {'oneOf': [
        obj({'kind': {'const': 'repo'}, 'path': {'type':'string','pattern':r'^(?!/)(?!.*(?:^|/)\.\.(?:/|$))[^\\]+$'}, 'sha256': DIGEST}),
        obj({'kind': {'const': 'toolchain'}, 'toolchain_identity': DIGEST, 'path': {'type':'string','pattern':r'^lib/lean/(?!.*(?:^|/)\.\.(?:/|$))[^\\]+$'}, 'sha256': DIGEST})
    ]}
    limits = s.read(s.V2 / 's17/preflight-bounds.json')['limits']
    work_limits = {k:v for k,v in limits.items() if k != 'lean_stage_seconds'}
    policy = obj({'schema': {'const':'relational.resource-policy/v3'},
        'work_limits': {'const': work_limits},
        'stage_seconds': {'type':'number','exclusiveMinimum':0,'maximum':60},
        'run_seconds': {'type':'number','exclusiveMinimum':0,'maximum':3600},
        'memory_bytes': {'type':'integer','minimum':1,'maximum':68719476736},
        'memory_mode': {'enum':['required','advisory']},
        'output_bytes': {'type':'integer','minimum':1,'maximum':8388608},
        'max_parallel_workers': {'const':1}})
    request = obj({'schema': {'const':'relational.qualification-request/v3'},
        'operation': {'const':'qualify'}, 'source_profile': {'const':'rich-positive-recursive-v2'},
        'proposal': s.read(s.V2 / 's06/rule-bundle.schema.json'),
        'resource_policy': policy, 'layout': {'enum':['combined','staged']},
        'build_mode': {'enum':['cold','warm']}})
    # The embedded legacy schema has no references; remove its metadata only.
    request['properties']['proposal'].pop('$schema', None)
    identity = obj({k:DIGEST for k in ['request','proposal','baseline','profile','catalog','toolchain','source_profile']})
    role = ['combined','data','typed','closure','expansion']
    module = obj({'role': {'enum':role}, 'module': TEXT, 'source':binding, 'olean':binding})
    inventories = []
    for layout, roles in [('combined',['combined']),('staged',['data','typed','closure','expansion'])]:
        prefix = []
        for r in roles:
            item = copy.deepcopy(module)
            item['properties']['role'] = {'const':r}
            prefix.append(item)
        inventories.append(obj({'layout': {'const':layout}, 'modules':{'type':'array','prefixItems':prefix,'items':False,'minItems':len(roles),'maxItems':len(roles)}}))
    manifest = obj({'schema':{'const':'relational.proof-manifest/v3'}, 'identity':identity,
        'change_class': {'enum':list(catalog['change_classes'])},
        'witness': {'oneOf':inventories},
        'obligations': array({'enum':[o['id'] for o in catalog['obligations']]},minItems=1,maxItems=21,uniqueItems=True),
        'general':binding,'projection':binding,'dependencies':binding,
        'bound_result':binding,'generator':binding,
        'authority_effect':NONE})
    claim = obj({'kind': {'enum':['derivation','complete-closure','absence','potential-norm','active-norm','active-conflict','model-expansion']},
        'model_class':TEXT,'query_scope':TEXT,'change_class':TEXT,'source_profile':TEXT,
        'truth_assumptions':array(TEXT), 'evidence_mode':{'const':'fresh-invocation-at-creation'}})
    resources = obj({'enforcement':{'enum':['cgroup-v2','advisory','unavailable']},
        'outcome': {'enum':['completed','timeout','oom','cancelled','output-limit','policy-unavailable','worker-failed']},
        'events':array(obj({'kind':TEXT,'detail':TEXT})), 'policy_identity':DIGEST})
    completed_resources = copy.deepcopy(resources)
    completed_resources['properties']['outcome'] = {'const':'completed'}
    completed_resources['properties']['enforcement'] = {'enum':['cgroup-v2','advisory']}
    qualified = obj({'schema':{'const':'relational.qualification-result/v3'},'status':{'const':'qualified-candidate'},
        'request_identity':DIGEST,'run_id':TEXT,'manifest':manifest,'claims':array(claim),
        'resource_report':completed_resources,'payload':binding,
        'complete_closure':{'const':True},'application_authorized':FALSE,'authority_effect':NONE})
    failure = obj({'schema':{'const':'relational.qualification-result/v3'},
        'status':{'enum':['invalid','unsupported','unknown-resource','cancelled','unsupported-policy']},
        'request_identity':DIGEST,'run_id':TEXT,'reason':TEXT,'stage':TEXT,
        'claims':array(claim,maxItems=0),'resource_report':resources,
        'complete_closure':FALSE,'application_authorized':FALSE,'authority_effect':NONE})
    inspection = obj({'schema':{'const':'relational.inspection-result/v3'},
        'status':{'enum':['recorded-current','stale-or-invalid']},
        'request_identity':DIGEST,'checked_bindings':array(binding),
        'reason':TEXT,'application_authorized':FALSE,'authority_effect':NONE})
    phase = ['prepared','running','completed','unknown-resource','cancelled','invalid','unsupported','unsupported-policy','reconciliation-required']
    run = obj({'schema':{'const':'relational.run-record/v3'},'run_id':TEXT,
        'request_identity':DIGEST,'phase':{'enum':phase},
        'inputs':array(binding),'outputs':array(binding),
        'resource_events':array(obj({'kind':TEXT,'detail':TEXT})),
        'timings':array(obj({'stage':TEXT,'parent':{'type':['string','null']},'seconds':{'type':'number','minimum':0},'mode':{'enum':['inclusive','exclusive']}})),
        'cache_checks':array(obj({'binding':binding,'current':{'type':'boolean'}})),
        'result':{'oneOf':[binding,{'type':'null'}]},'authority_effect':NONE})
    variants = {'request':request,'result':{'oneOf':[qualified,failure]},'proof-manifest':manifest,
        'resource-policy':policy,'run-record':run,'inspection':inspection,'binding':binding}
    for name,value in variants.items():
        s.write(here/(name+'.schema.json'),schema(name,value))
    inputs = [s.binding(s.V2/'s15/obligation-catalog.json'),s.binding(s.V2/'s06/rule-bundle.schema.json'),s.binding(s.V2/'s17/preflight-bounds.json'),s.binding(HERE.parent/'p00/EvidenceSemantics.lean')]
    s.write(HERE/'contract-source-bindings.json',{'bindings':inputs,'legacy_schema_adapter':'embedded exact proposal shape with metadata removed; exact input source bound separately'})
    coverage=s.read(s.SOURCE.parent/'coverage.json')
    coverage['schema']='relational.v3-execution-coverage/v1'
    coverage['selected_extensions']=['E00','E01','E02','E03','E04','E05','E06']
    coverage['state_note']='Preserved meanings/dispositions; extension selection is not implementation qualification.'
    s.write(HERE/'coverage.json',coverage)
    print('P01 contracts generated')


if __name__ == '__main__':
    build()
