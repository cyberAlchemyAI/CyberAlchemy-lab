"""Exact candidate relation/population targets and model-local controls.

Generated obligations do not establish source fidelity or universal validity.
Only explicit, digest-bound identity shared-carrier alignment is supported here.
"""
import json
import re
from pathlib import Path
import contracts as c
import resolver as r

HERE=Path(__file__).resolve().parent
PROFILE=HERE/'profiles/relation-and-population-policy.json'


class PolicyFault(ValueError):
    def __init__(self,code,path=''):self.code=code;self.path=path


def exact(value,keys,code):
    if not isinstance(value,dict) or set(value)!=set(keys):raise PolicyFault(code)


def ident(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]*',value):raise PolicyFault('invalid-identity')
    return value


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(value):return r.digest(canonical(value))
def var():return {'op':'var','name':'x'}
def pred(name):return {'op':'pred','name':name,'args':[var()]}
def negate(formula):return {'op':'not','arg':formula}
def both(*formulas):return {'op':'and','args':list(formulas)}
def quant(op,carrier,formula):return {'op':op,'var':'x','sort':carrier,'body':formula}
def difference(carrier,left,right):return quant('exists',carrier,both(pred(left),negate(pred(right))))


def structural(kind,payload):
    result=c.validate({'schema_version':'definition-assurance-input/v1-candidate','kind':kind,'authority_effect':'none','payload':payload},kind)
    if result['status']!='structurally-valid':raise PolicyFault('malformed-'+kind)


def load_profile():
    value=r.parse(PROFILE.read_bytes(),str(PROFILE))
    if value['schema_version']!='definition-assurance-relation-policy/v1-candidate' or value['authority_effect']!='none':raise PolicyFault('invalid-local-policy')
    return value


def endpoint(binding,source,scope):
    exact(binding,['source','scope','predicate','carrier'],'malformed-endpoint-binding')
    if not r.same_json(binding['source'],source) or binding['scope']!=scope:raise PolicyFault('endpoint-source-scope-mismatch')
    ident(binding['predicate']);ident(binding['carrier'])


def alignment(relation,bindings,root):
    if relation['alignment']['status']!='reviewed':raise PolicyFault('unresolved-carrier-alignment')
    ref=relation['alignment']['map_ref']
    raw=r.read_bytes(r.resolve_root(root),ref['path'])
    if r.digest(raw)!=ref['sha256']:raise PolicyFault('stale-alignment-binding',ref['path'])
    doc=r.parse(raw,ref['path'])
    keys=['schema_version','authority_effect','mapping_kind','carrier','scope','left_source','right_source','reviewer_ref','review_basis','equivalence_claim']
    exact(doc,keys,'malformed-alignment-record')
    if doc['schema_version']!='definition-assurance-carrier-alignment/v1-candidate' or doc['authority_effect']!='none' or doc['equivalence_claim']!='none':raise PolicyFault('invalid-alignment-record')
    if doc['mapping_kind']!='identity-shared-carrier':raise PolicyFault('unsupported-carrier-mapping')
    if (doc['scope']!=relation['scope'] or not r.same_json(doc['left_source'],relation['left_definition']) or not r.same_json(doc['right_source'],relation['right_definition']) or doc['carrier']!=bindings['left']['carrier'] or doc['carrier']!=bindings['right']['carrier']):raise PolicyFault('unaligned-carriers')
    if any(not isinstance(doc[key],str) or not doc[key].strip() for key in ['reviewer_ref','review_basis']):raise PolicyFault('unattributed-alignment-record')
    return doc['carrier']


def compile_relation(relation,bindings,root,*,proper=False,distinction='permitted',forbidden=()):
    structural('relation',relation);exact(bindings,['left','right'],'malformed-endpoint-bindings')
    endpoint(bindings['left'],relation['left_definition'],relation['scope']);endpoint(bindings['right'],relation['right_definition'],relation['scope'])
    if type(proper) is not bool or distinction not in {'permitted','all-models'}:raise PolicyFault('invalid-relation-options')
    carrier=alignment(relation,bindings,root);left=bindings['left']['predicate'];right=bindings['right']['predicate'];kind=relation['relation_class'];direction=relation['direction']
    if left==right and not r.same_json(relation['left_definition'],relation['right_definition']):raise PolicyFault('collapsed-predicate-identity')
    if kind=='unresolved' or direction=='unresolved':raise PolicyFault('unresolved-relation-classification')
    if proper and kind!='subtype':raise PolicyFault('properness-on-nonsubtype')
    if forbidden and kind!='independent-axis':raise PolicyFault('forbidden-inferences-on-other-relation')
    profile=load_profile();targets=[]
    def target(label,formula,query_type):
        targets.append({'key':relation['relation_id']+':'+label,'statement':formula,'query_type':query_type,'minimum_strength':profile['minimum_strength'][query_type],'carrier':carrier,'source_refs':[relation['left_definition'],relation['right_definition']],'scope':relation['scope']})
    if kind=='alias':
        if direction!='both':raise PolicyFault('alias-requires-both-directions')
        target('equivalence',quant('forall',carrier,{'op':'iff','left':pred(left),'right':pred(right)}),'universal-property')
    elif kind=='subtype':
        if direction not in {'forward','reverse'}:raise PolicyFault('subtype-requires-direction')
        child,parent=(left,right) if direction=='forward' else (right,left)
        target('inclusion',quant('forall',carrier,{'op':'implies','left':pred(child),'right':pred(parent)}),'universal-property')
        if proper:target('properness',difference(carrier,parent,child),'model-witness' if distinction=='permitted' else 'universal-property')
    elif kind=='disjoint':
        if direction!='both':raise PolicyFault('disjoint-requires-both-direction-marker')
        target('disjointness',quant('forall',carrier,negate(both(pred(left),pred(right)))),'universal-property')
    elif kind=='overlap-distinct':
        if direction not in {'forward','reverse','both'}:raise PolicyFault('distinction-requires-direction')
        target('intersection',quant('exists',carrier,both(pred(left),pred(right))),'model-witness')
        if direction in {'forward','both'}:target('left-difference',difference(carrier,left,right),'model-witness' if distinction=='permitted' else 'universal-property')
        if direction in {'reverse','both'}:target('right-difference',difference(carrier,right,left),'model-witness' if distinction=='permitted' else 'universal-property')
    elif kind=='independent-axis':
        if direction!='none' or not forbidden or len(set(forbidden))!=len(forbidden) or not set(forbidden)<={'left-implies-right','right-implies-left'}:raise PolicyFault('explicit-forbidden-inferences-required')
        for inference in sorted(forbidden):
            antecedent,consequent=(left,right) if inference=='left-implies-right' else (right,left)
            target('forbid-'+inference,difference(carrier,antecedent,consequent),'model-witness')
    else:raise PolicyFault('unsupported-relation')
    if relation['required_statements'] and not r.same_json(relation['required_statements'],[row['statement'] for row in targets]):raise PolicyFault('submitted-target-substitution')
    return targets


def compile_populations(populations,bindings,scope):
    expected={(binding['carrier'],binding['predicate']) for binding in bindings.values()};seen=set();ids=set();targets=[]
    for population in populations:
        structural('population',population);key=(population['carrier'],population['predicate_ref'])
        if key not in expected or key in seen or population['population_id'] in ids or population['scope']!=scope:raise PolicyFault('population-binding-denominator-mismatch')
        seen.add(key);ids.add(population['population_id']);formula=quant('exists',key[0],pred(key[1]))
        requirement=population['requirement']
        if requirement=='exempt':
            if population['statement'] is not None or population['review_ref'] is None:raise PolicyFault('unreviewable-population-exemption')
            targets.append({'key':population['population_id'],'statement':None,'query_type':'source-review','minimum_strength':'source-review','status':'exemption-review-required','review_ref':population['review_ref'],'review_subject_sha256':sha(population),'carrier':key[0],'predicate':key[1],'scope':scope})
        else:
            if requirement=='required' and not r.same_json(population['statement'],formula):raise PolicyFault('population-statement-substitution')
            if requirement=='unresolved' and population['statement'] is not None and not r.same_json(population['statement'],formula):raise PolicyFault('population-statement-substitution')
            targets.append({'key':population['population_id'],'statement':formula,'query_type':'model-witness','minimum_strength':'model-witness','status':'required' if requirement=='required' else 'unresolved-policy','carrier':key[0],'predicate':key[1],'scope':scope})
    if seen!=expected:raise PolicyFault('missing-population-policy')
    return targets


def evaluate_formula(formula,carrier,extensions,assignment=None):
    """Small independent set-membership evaluator for policy controls only."""
    env={} if assignment is None else assignment;op=formula['op']
    if op=='pred':return env[formula['args'][0]['name']] in extensions[formula['name']]
    if op=='not':return not evaluate_formula(formula['arg'],carrier,extensions,env)
    if op=='and':return all(evaluate_formula(row,carrier,extensions,env) for row in formula['args'])
    if op in {'implies','iff'}:
        left=evaluate_formula(formula['left'],carrier,extensions,env);right=evaluate_formula(formula['right'],carrier,extensions,env)
        return (not left or right) if op=='implies' else left==right
    if op in {'forall','exists'}:
        values=[evaluate_formula(formula['body'],carrier,extensions,{**env,formula['var']:value}) for value in carrier]
        return all(values) if op=='forall' else any(values)
    raise PolicyFault('unsupported-control-formula')


def assess_model(targets,population_targets,carrier,extensions):
    if not targets or not population_targets:raise PolicyFault('empty-control-denominator')
    if not isinstance(carrier,list) or not carrier or any(not isinstance(x,str) or not x for x in carrier) or len(set(carrier))!=len(carrier):raise PolicyFault('invalid-model-carrier')
    if not isinstance(extensions,dict) or any(not isinstance(values,list) or any(not isinstance(value,str) for value in values) or len(set(values))!=len(values) or not set(values)<=set(carrier) for values in extensions.values()):raise PolicyFault('invalid-model-extension')
    unresolved=[row['key'] for row in population_targets if row['status']!='required']
    if unresolved:return {'status':'unresolved-population-policy','pending':unresolved,'semantic_ready':False,'authority_effect':'none'}
    needed={row['predicate'] for row in population_targets}
    if not needed<=set(extensions):raise PolicyFault('missing-model-predicate')
    populations=[row['key'] for row in population_targets if not evaluate_formula(row['statement'],carrier,extensions)]
    if populations:return {'status':'vacuous-required-population','missing':populations,'semantic_ready':False,'authority_effect':'none'}
    outcomes=[{'key':row['key'],'holds_in_this_model':evaluate_formula(row['statement'],carrier,extensions),'query_type':row['query_type']} for row in targets]
    return {'status':'model-local-supported' if all(x['holds_in_this_model'] for x in outcomes) else 'model-local-counterexample','targets':outcomes,'semantic_ready':False,'authority_effect':'none','claim_ceiling':'Selected finite model only; no universal entailment, source fidelity or whole-definition assurance.'}


def check_axis_move(before,after,intended_axes,recorded_couplings):
    if not isinstance(before,dict) or not isinstance(after,dict) or set(before)!=set(after) or not before:raise PolicyFault('malformed-axis-state')
    for values in [intended_axes,recorded_couplings]:
        if not isinstance(values,list) or any(not isinstance(x,str) for x in values) or len(set(values))!=len(values) or not set(values)<=set(before):raise PolicyFault('malformed-axis-selection')
    # Exact JSON equality avoids bool/integer collapse in axis values.
    changed={key for key in before if not r.same_json(before[key],after[key])}
    return {'frame_holds':bool(intended_axes) and changed<=set(intended_axes)|set(recorded_couplings) and set(recorded_couplings)<=changed,'changed_axes':sorted(changed),'authority_effect':'none','semantic_ready':False,'claim_ceiling':'Frame condition for this selected move; declaration of a coupling grants no authority.'}
