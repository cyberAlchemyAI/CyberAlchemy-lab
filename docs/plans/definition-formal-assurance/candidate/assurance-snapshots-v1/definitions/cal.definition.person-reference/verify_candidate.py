"""Independent finite purpose-relative minimum, projection and non-entailment models."""
import itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Entity':['r1','r2','p1','p2'],'Purpose':['attribution','coordination'],'Scope':['lab','other'],'Field':['identifier','scope','label'],'Selection':['s'+str(i) for i in range(8)],'Token':['reference-1','reference-2','person-1','person-2','identifier-1','identifier-2']}
 functions={n:[{'args':list(xs),'value':domains[res][0]} for xs in itertools.product(*[domains[s] for s in args])] for n,(args,res) in b.FUNCTIONS.items()}
 for n,val in [('referencePerson','p1'),('referenceFields','s3')]:
  for row in functions[n]:row['value']=val
 setvalue({'functions':functions},'referencePurpose',['r2'],'coordination');setvalue({'functions':functions},'referenceFields',['r2'],'s1')
 for n,prefix in [('referenceIdentity','reference-'),('personIdentity','person-'),('referenceIdentifier','identifier-')]:
  for row in functions[n]:row['value']=prefix+('2' if row['args'][0] in ['r2','p2'] else '1')
 predicates={n:[] for n in b.SIGNATURE};predicates.update(PersonReference=[['r1'],['r2']],Person=[['p1'],['p2']],HumanIndividual=[['p1'],['p2']],IdentifierProjection=[['r1']],RecordProjection=[['r2']],PurposeBounded=[['r1'],['r2']],DeclaredPurpose=[['attribution'],['coordination']],DeclaredIdentityScope=[['lab']],ProjectionOf=[['r1','p1'],['r2','p1']],Member=[['s'+str(mask),field] for mask in range(8) for i,field in enumerate(domains['Field']) if mask&(1<<i)],Sufficient=[['s'+str(mask),purpose] for mask in range(8) for purpose in domains['Purpose'] if (mask&3==3 if purpose=='attribution' else mask&1==1)],NeededFor=[['identifier','attribution'],['scope','attribution'],['identifier','coordination']])
 return {'domains':domains,'constants':{},'functions':functions,'predicates':predicates}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('two-purpose-relative-minima-one-Person-no-actual-denotation',lambda m:None)
 add('identifier-and-record-projection-overlap-permitted',lambda m:m['predicates']['RecordProjection'].append(['r1']))
 add('identifier-OR-record-not-mandatory-conjunction',lambda m:m['predicates'].update(IdentifierProjection=[['r1'],['r2']],RecordProjection=[]))
 add('neither-identifier-nor-record-projection-rejected',lambda m:m['predicates'].update(IdentifierProjection=[],RecordProjection=[]),False)
 add('missing-purpose-bounded-role',lambda m:m['predicates'].update(PurposeBounded=[]),False)
 add('purpose-not-declared',lambda m:m['predicates'].update(DeclaredPurpose=[]),False,False)
 add('identity-scope-not-declared',lambda m:m['predicates'].update(DeclaredIdentityScope=[]),False,False)
 add('missing-Person-role',lambda m:m['predicates'].update(Person=[]),False,False)
 add('Person-is-not-HumanIndividual',lambda m:m['predicates'].update(HumanIndividual=[]),False)
 add('missing-selected-projection-pair',lambda m:m['predicates'].update(ProjectionOf=[['r1','p1']]),False)
 add('actual-denotation-alone-does-not-replace-recorded-projection',lambda m:m['predicates'].update(ProjectionOf=[],ActualDenotes=[['r1','p1'],['r2','p1']]),False)
 add('reference-selector-disagrees-with-projection',lambda m:setvalue(m,'referencePerson',['r1'],'p2'),False,False)
 def collapse(m):
  setvalue(m,'referencePerson',['r1'],'r1');m['predicates']['Person'].append(['r1']);m['predicates']['HumanIndividual'].append(['r1']);m['predicates']['ProjectionOf'][0]=['r1','r1']
 add('reference-never-selected-Person-itself',collapse,False,False)
 add('not-globally-disjoint-reference-role-for-unselected-Person',lambda m:m['predicates']['RecordProjection'].append(['p2']))
 add('field-selection-not-sufficient-for-purpose',lambda m:setvalue(m,'referenceFields',['r1'],'s1'),False)
 add('sufficient-but-irrelevant-field-rejected',lambda m:setvalue(m,'referenceFields',['r1'],'s7'),False)
 def redundant(m):setvalue(m,'referenceFields',['r1'],'s7');m['predicates']['NeededFor'].append(['label','attribution'])
 add('marking-extra-field-needed-cannot-hide-sufficient-proper-subset',redundant,False)
 add('empty-proper-subset-is-already-sufficient',lambda m:m['predicates']['Sufficient'].append(['s0','attribution']),False)
 add('selected-minimum-missing-needed-field-marker',lambda m:m['predicates'].update(NeededFor=[['identifier','attribution'],['identifier','coordination']]),False)
 def omit_empty(m):m['domains']['Selection'].remove('s0')
 add('omitting-empty-selection-fails-removal-closure',omit_empty,False)
 add('no-selection-for-removing-one-required-field',lambda m:m['predicates']['Member'].remove(['s2','scope']),False)
 add('reference-private-attribute-only-inference-forbidden',lambda m:m['predicates'].update(AllowedReferenceOnlyPrivateAttributes=[['r1']]),False)
 add('separately-authenticated-reference-denotation-permitted',lambda m:m['predicates'].update(ActualDenotes=[['r1','p1'],['r2','p1']]))
 add('same-lexical-reference-and-Person-identity-token-permitted',lambda m:setvalue(m,'referenceIdentity',['r1'],'person-1'))
 add('identifier-token-collision-not-universally-forbidden',lambda m:setvalue(m,'referenceIdentifier',['r2'],'identifier-1'))
 def different_people(m):setvalue(m,'referencePerson',['r2'],'p2');m['predicates']['ProjectionOf'][1]=['r2','p2']
 add('references-to-different-People-valid-but-fail-selected-shared-Person-I',different_people,True,False)
 add('only-one-reference-valid-but-fails-selected-two-reference-I',lambda m:m['predicates'].update(PersonReference=[['r1']]),True,False)
 def empty_minima(m):
  for n in ['r1','r2']:setvalue(m,'referenceFields',[n],'s0')
  m['predicates']['Sufficient']=[['s'+str(mask),purpose] for mask in range(8) for purpose in m['domains']['Purpose']]
 add('empty-sufficient-selection-valid-but-fails-selected-nonempty-I',empty_minima,True,False)
 add('no-reference-vacuous-primary-theory-fails-connected-I',lambda m:m['predicates'].update(PersonReference=[]),True,False)
 for n in b.OUTCOMES:add('independently-supported-world-outcome-permitted-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['r1']]))
 add('nontotal-projected-Person-selector',lambda m:m['functions']['referencePerson'].pop(),error='nontotal-function')
 add('ill-sorted-selection-selector',lambda m:setvalue(m,'referenceFields',['r1'],'lab'),error='ill-sorted-function-result')
 add('wrong-field-membership-arity',lambda m:m['predicates'].update(Member=[['s0']]),error='ill-sorted-model-tuple')
 add('duplicate-selected-projection-pair',lambda m:m['predicates']['ProjectionOf'].append(['r1','p1']),error='duplicate-predicate-tuple')
 add('empty-field-domain',lambda m:m['domains'].update(Field=[]),error='empty-or-malformed-domain')
 return rows
def qualify(model,ids):return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}
def verify(write=False):
    context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT)
    runtime=v.f.current_bindings();bindings=[b.ref(p) for p in [b.UNIT/'build_candidate.py',b.UNIT/'verify_candidate.py',b.IMPL/'verifier.py',b.IMPL/'ir.py',b.IMPL/'contracts.py',b.BASE/'units/A04/correspondence.py']]
    core=load('t.json')['payload'];typed=load('static-ir.json');packet=load('correspondence.json');counts=load('denominator.json')
    if not b.r.same_json(typed,b.ir.compile_interpretation(core,snap)) or not b.r.same_json(packet['interpretation'],core):raise ValueError('Substituted interpretation/IR')
    account=b.co.check(packet,snap,required_dependencies=[x['version_ref'] for x in core['depends_on']],required_conflicts=[x['finding_id'] for x in packet['source_precedence']['conflicts']])
    if not account['character_accounting_complete'] or not b.r.same_json(account,load('correspondence-check.json')):raise ValueError('Incomplete source account')
    if core['assumptions'] or packet['assumption_links'] or core['source_fidelity']!='pending':raise ValueError('Assumed target or owner fidelity')
    T=[x for x in typed['clauses'] if x['disposition']=='encoded'];I=[x for x in typed['populations'] if x['requirement']=='required']
    if len(T)!=counts['encoded_clauses'] or len(I)!=counts['required_populations']:raise ValueError('Changed theory/population denominator')
    ids={x['symbol_id']:b.ir.qualified(core['source'],core['scope'],x['symbol_id']) for x in core['declarations']}
    def evaluate(model):
        e=v.Denotation(typed['declarations'],model)
        tc=[{'clause_id':x['clause_id'],'truth':e.truth(x['formal_statement'])} for x in T]
        pc=[{'population_id':x['population_id'],'truth':e.truth(x['statement'])} for x in I]
        return all(x['truth'] for x in tc),all(x['truth'] for x in pc),tc,pc
    results=[]
    for case in controls():
        model=qualify(case['model'],ids)
        try:
            t,i,tc,pc=evaluate(model)
            if case['expected_error'] is not None or (t,i)!=(case['expected_T'],case['expected_I']):raise ValueError('Wrong authored control: '+case['case_id']+' '+str((t,i)))
            result={'case_id':case['case_id'],'status':'independently-evaluated-authored-model','model':model,'model_sha256':b.ir.digest(model),
                    'primary_theory_satisfied':t,'required_population_satisfied':i,'primary_clause_results':tc,'population_results':pc}
        except v.VerificationFault as error:
            if error.code!=case['expected_error']:raise
            result={'case_id':case['case_id'],'status':'rejected-model-structure','code':error.code,'model':model,'model_sha256':b.ir.digest(model)}
        results.append(result)
    queries=[];composed=b.ir.compose([typed])
    for q in load('query-policy.json')['queries']:
        model=base_model()
        model=qualify(model,ids);e=v.Denotation(typed['declarations'],model)
        target=v.renamed(q['target'],ids);witness=v.renamed(q['witness_condition'],ids)
        b.ir.check_composed_formula(composed,target);b.ir.check_composed_formula(composed,witness)
        if q['selected_in_T'] is not False or evaluate(model)[:2]!=(True,True) or e.truth(target) is not False or e.truth(witness) is not True:raise ValueError('Target assumed or no valid countermodel: '+q['query_id'])
        queries.append({'query_id':q['query_id'],'target_false':True,'witness_condition_true':True,'model':model,'model_sha256':b.ir.digest(model),'mechanized_proof':False})
    prior=json.loads((b.BASE/'definitions/cal.definition.identity-claim/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-person-reference-model-controls/v1-candidate','status':'PASS-for-exact-authored-person-reference-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite purpose-relative inclusion-minimal selection/projection models and fifteen targets outside T. Candidate removal closure and sufficient/needed field policy are checked in a finite universe. Actual denotation, field/purpose/sufficiency/identity common-carrier meaning, privacy/runtime enforcement, source precedence and whole-definition acceptance remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
