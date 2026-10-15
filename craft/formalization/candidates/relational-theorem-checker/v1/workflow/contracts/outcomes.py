"""Local successor outcome contracts; truth verification remains R02/R03."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'execution'))
import support as s
BASE=Path(__file__).resolve().parent
EXECUTION=['completed','not-run','timeout','unavailable','provider-error']
CURRENTNESS=['current','stale','unresolved']
METHODS=['verified-checker','kernel-proof','checked-model-witness','bounded-search','none']
VERDICTS=['satisfied','violated','unknown','unsupported','not-run']
DIMENSIONS=['selected-data-compatibility','invariant-preservation','model-conservativity']
DIMENSION_VALUES=['verified-for-named-scope','violated','unknown','unsupported','not-applicable']


def obj(properties):return {'type':'object','additionalProperties':False,'properties':properties,'required':list(properties)}
def enum(values):return {'enum':values}
def array(items,unique=False,minimum=0):return {'type':'array','items':items,'uniqueItems':unique,'minItems':minimum}


def schema():
    text={'type':'string','minLength':1};sha={'type':'string','pattern':'^[a-f0-9]{64}$'}
    binding=obj({'path':text,'sha256':sha})
    diagnostic=obj({'code':text,'message':text,'location':text,'obligation_id':{'anyOf':[text,{'type':'null'}]},'next_action':text})
    result=obj({'obligation_id':text,'hard':{'const':True},
        'required_statement':obj({'id':text,'definition_bindings':array(binding,True,1)}),
        'execution':enum(EXECUTION),'currentness':enum(CURRENTNESS),'evidence_method':enum(METHODS),
        'verdict':enum(VERDICTS),'evidence_refs':array(binding,True),'diagnostics':array(diagnostic)})
    result['allOf']=[{'if':{'properties':{'verdict':{'const':'satisfied'}}},'then':{'properties':{
        'execution':{'const':'completed'},'currentness':{'const':'current'},
        'evidence_method':enum(['verified-checker','kernel-proof','checked-model-witness']),'evidence_refs':{'minItems':1}}}}]
    document=obj({'schema_version':{'const':'relational.cli-outcome/v1-candidate'},
        'command':enum(['check-instance','check-extension','check-proof','replay-evidence']),
        'profile_id':text,'baseline_identity':{'anyOf':[sha,{'type':'null'}]},'proposal_identity':{'anyOf':[sha,{'type':'null'}]},
        'execution':enum(EXECUTION),'currentness':enum(CURRENTNESS),
        'evidence':obj({'methods':array(enum(METHODS),True),'policy_identity':{'anyOf':[sha,{'type':'null'}]},'trust_boundary':array(text,True)}),
        'results':array(result),'required_hard_obligation_ids':array(text,True),
        'missing_hard_obligation_ids':array(text,True),'unresolved_hard_obligation_ids':array(text,True),
        'readiness':enum(['ready-for-review','blocked','unresolved','not-applicable']),
        'compatibility_dimensions':obj({dimension:enum(DIMENSION_VALUES) for dimension in DIMENSIONS}),
        'diagnostics':array(diagnostic),'authority_effect':{'const':'none'}})
    document.update({'$schema':'https://json-schema.org/draft/2020-12/schema',
        '$id':'https://cyberalchemy.local/schemas/relational-checker/cli-outcome/v1-candidate',
        'title':'Local candidate CLI outcome successor'})
    document['allOf']=[{'if':{'properties':{'readiness':{'const':'ready-for-review'}}},'then':{'properties':{
        'command':enum(['check-extension','replay-evidence']),'execution':{'const':'completed'},'currentness':{'const':'current'},
        'required_hard_obligation_ids':{'minItems':1},'missing_hard_obligation_ids':{'maxItems':0},'unresolved_hard_obligation_ids':{'maxItems':0},
        'results':{'minItems':1,'items':{'properties':{'verdict':{'const':'satisfied'}}}},
        'compatibility_dimensions':{'properties':{dimension:{'const':'verified-for-named-scope'} for dimension in DIMENSIONS}}}}}]
    return document


def validate(outcome,required_ids):
    """required_ids must come from the trusted policy, never the submission."""
    import jsonschema
    jsonschema.Draft202012Validator(schema()).validate(outcome)
    expected=set(required_ids);s.require(len(expected)==len(required_ids),'trusted required inventory has duplicates')
    s.require(set(outcome['required_hard_obligation_ids'])==expected,'client selected a weaker required set')
    ids=[result['obligation_id'] for result in outcome['results']]
    s.require(len(set(ids))==len(ids) and set(ids)<=expected,'duplicate or injected obligation result')
    missing=expected-set(ids)
    unresolved=missing|{result['obligation_id'] for result in outcome['results'] if result['verdict']!='satisfied'}
    s.require(set(outcome['missing_hard_obligation_ids'])==missing,'missing inventory hidden')
    s.require(set(outcome['unresolved_hard_obligation_ids'])==unresolved,'unresolved inventory hidden')
    s.require(set(outcome['evidence']['methods'])=={result['evidence_method'] for result in outcome['results']},'evidence methods collapsed or misreported')
    if outcome['readiness']=='ready-for-review':s.require(not unresolved,'ready with unresolved required obligation')
    if outcome['command'] in ['check-instance','check-proof']:s.require(outcome['readiness']=='not-applicable','single check inferred extension readiness')
    return True


def exit_code(outcome):
    if any(d['code']=='input-invalid' for d in outcome['diagnostics']):return 2
    if outcome['execution']=='timeout':return 6
    if outcome['execution']=='unavailable':return 5
    if outcome['execution']=='provider-error':return 8
    if outcome['currentness']=='stale':return 7
    verdicts={r['verdict'] for r in outcome['results']}
    if 'unsupported' in verdicts:return 3
    if 'violated' in verdicts:return 1
    if outcome['execution']!='completed' or outcome['currentness']!='current' or outcome['unresolved_hard_obligation_ids']:return 4
    if outcome['command'] in ['check-extension','replay-evidence'] and outcome['readiness']!='ready-for-review':return 4
    return 0
