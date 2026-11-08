"""Independent obligation policy for computed extension profiles."""
from copy import deepcopy
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'proposals'))
import classifier as c
s=c.s
BASE=Path(__file__).resolve().parent
NON_RULE=('baseline-current','computed-classification','source-profile-projection','carrier-projection',
          'selected-data-compatibility','invariant-preservation','conservative-expansion','inhabited-model','protected-root-independence')
RULE=('typed-rule-profile','derivation-soundness','closure-adequacy','protected-lineage',
      'independence-witnesses','rule-extension-compatibility')
SUPPORTED={'unchanged','instance-only','fresh-kind-extension','rule-only-extension'}


def policy():
    return {'schema':'relational.obligation-policy/v1','policy_version':'complete-derived-obligations/v1',
            'supported_profiles':sorted(SUPPORTED),'non_rule_obligations':list(NON_RULE),'rule_obligations':list(RULE),
            'authority_effect':'none','source_scope':'closed-required-string registry and unchanged F0 semantics; full source-wide meanings remain unsupported',
            'evidence_rule':'Submitted evidence may fill required entries but cannot select IDs, weaken policy, substitute profile or shrink the generated set.'}


def generate(proposal):
    computed=c.classify(proposal);profile=computed['profile']
    required=list(NON_RULE)
    if computed['rule_change']:required+=RULE
    if profile not in SUPPORTED:required+=['unsupported-change-meaning']
    prefix=c.identity(proposal)
    return {'schema':'relational.required-obligations/v1','proposal_identity':prefix,'classification':computed,
            'policy_identity':c.identity(policy()),'supported':profile in SUPPORTED,
            'obligations':[{'id':prefix+':'+name,'name':name,'hard':True,
                            'scope':'L3' if name in RULE else 'L2',
                            'status':'pending' if profile in SUPPORTED else 'unsupported'} for name in required],
            'inherited_full_source_semantics':'unsupported; unchanged baseline obligations retained outside the named extension claim',
            'authority_effect':'none'}


def validate_submission(proposal,submitted):
    expected=generate(proposal)
    s.require(set(submitted)=={'proposal_identity','policy_identity','obligations'},'unknown or missing evidence fields')
    s.require(submitted['proposal_identity']==expected['proposal_identity'],'evidence from another proposal')
    s.require(submitted['policy_identity']==expected['policy_identity'],'weakened or substituted policy')
    s.require(isinstance(submitted['obligations'],list),'evidence obligations must be a list')
    actual={item['id']:item for item in submitted['obligations']}
    s.require(len(actual)==len(submitted['obligations']) and set(actual)=={o['id'] for o in expected['obligations']},'required obligation omitted, duplicated or injected')
    for obligation in expected['obligations']:
        item=actual[obligation['id']]
        s.require(item.get('name')==obligation['name'] and item.get('hard') is True and item.get('scope')==obligation['scope'],'required statement or scope weakened')
    return expected


def source_projection(proposal):
    computed=c.classify(proposal)
    s.require(computed['profile'] in SUPPORTED,'unsupported source projection profile')
    if computed['profile']!='fresh-kind-extension':return {'result':'pass','added_sources':[]}
    rows={row['id']:row for row in proposal['after']['registry']['kinds']};bindings=[]
    for kind_id in computed['added_kind_ids']:
        row=rows[kind_id];s.check_binding(row['source']);document=s.read(s.ROOT/row['source']['path'])
        s.require(set(document)=={'schema','declaration','semantic_profile','qualifier_interpretation','formal_predicate'},'unknown structural declaration content')
        s.require(document['schema']=='relational.structural-declaration/v1-candidate' and document['semantic_profile']=='closed-required-string-ordered-pairs/v1','unsupported new normative profile')
        s.require(document['declaration']=={key:value for key,value in row.items() if key not in {'source','version'}},'new source-to-normal-form mismatch')
        s.require(document['qualifier_interpretation']=={field:'nonempty-string-annotation' for field in row['fields']},'reference or additional semantic meaning requires a new proof profile')
        s.require(document['formal_predicate']=='Registry.InstanceValid; no inference rule or external evidence meaning','new semantic claim not bound to formal predicate')
        bindings.append(row['source'])
    return {'result':'pass','added_sources':bindings,'profile':'closed-required-string-ordered-pairs/v1'}


def carrier(proposal):
    original=s.read(s.BASE/'coverage/carrier/candidate-carrier-schema.json');result=deepcopy(original)
    result['$id']='https://cyberalchemy.local/schemas/relational-checker/extension-carrier/'+c.identity(proposal)
    result['properties']['schema_version']['const']='relational-checker.extension-carrier/v1-candidate'
    kinds=proposal['after']['registry']['kinds']
    result['properties']['payload']['properties']['relation_kind_ref']['enum']=[k['id'] for k in kinds]
    branches=[]
    for row in kinds:
        template=deepcopy(original['allOf'][0])
        template['if']['properties']['payload']['properties']['relation_kind_ref']['const']=row['id']
        payload=template['then']['properties']['payload']
        payload['oneOf']=[{'properties':{'source':{'properties':{'kind':{'const':p['source_kind']}}},
                           'target':{'properties':{'kind':{'const':p['target_kind']}}}}} for p in row['pairs']]
        payload['properties']['qualifiers']={'type':'object','additionalProperties':False,'required':row['fields'],
                                             'properties':{field:{'type':'string','minLength':1} for field in row['fields']}}
        branches.append(template)
    result['allOf']=branches
    return result
