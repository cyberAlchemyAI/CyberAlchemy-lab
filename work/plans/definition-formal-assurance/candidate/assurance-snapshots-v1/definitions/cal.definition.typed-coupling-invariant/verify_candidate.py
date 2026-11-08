"""Independent authored finite denotation: reliance trigger, representation and outcomes."""
import itertools,json,copy
import build_candidate as b
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def base_model():
 domains={sort:[sort+'-a',sort+'-b'] for sort in b.SORTS};domains.update(Use=['u','unused'],Object=['a','z'],Relation=['r','ordinary'])
 functions={n:[{'args':list(xs),'value':domains[res][0]} for xs in itertools.product(*[domains[s] for s in args])] for n,(args,res) in b.FUNCTIONS.items()}
 for n in ['useTarget','relationTarget']:
  for row in functions[n]:row['value']='z'
 predicates={n:[] for n in b.SIGNATURE}
 for n in b.REQUIRED:predicates[n]=[['r']]
 predicates['TypedRelation'].append(['ordinary'])
 predicates.update(DecisionReliesOnConstraintOrChange=[['u']],ReliedCoupling=[['u']],NonOrthogonal=[['u']],Orthogonal=[['unused']],Represents=[['u','r']],HasEvidence=[['r','EvidenceRef-a']],HasReviewEffect=[['r','ReviewEffect-a']],ValidationEffectDescription=[['ReviewEffect-a']],NamedKind=[['Kind-a']])
 return {'domains':domains,'constants':{},'functions':functions,'predicates':predicates}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(name,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('relied-decision-has-vector-and-no-promoted-outcome',lambda m:None)
 for n in b.REQUIRED:add('missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['ordinary']] if n=='TypedRelation' else []),False)
 for n in ['NamedKind','HasEvidence','HasReviewEffect','ValidationEffectDescription','Represents']:add('missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[]),False)
 for use,relation in [('useSource','relationSource'),('useTarget','relationTarget'),('useScope','relationScope')]:add('representative-mismatches-'+use,lambda m,n=relation:setvalue(m,n,['r'],next(x for x in m['domains'][b.FUNCTIONS[n][1]] if x!=next(q['value'] for q in m['functions'][n] if q['args']==['r']))),False)
 add('reliance-not-recorded-as-coupling',lambda m:m['predicates'].update(ReliedCoupling=[]),False,False)
 add('coupling-without-selected-reliance-role',lambda m:m['predicates'].update(DecisionReliesOnConstraintOrChange=[]),False)
 add('reliance-cannot-be-classified-orthogonal',lambda m:m['predicates']['Orthogonal'].append(['u']),False)
 add('reliance-cannot-omit-nonorthogonal-meaning',lambda m:m['predicates'].update(NonOrthogonal=[]),False)
 for n in b.RELIANCE[1:]:
  def replace_role(m,n=n):m['predicates']['DecisionReliesOnConstraintOrChange']=[];m['predicates'][n]=[['u']]
  add('representation-required-for-'+n,replace_role)
  def role_missing_rep(m,n=n):replace_role(m,n);m['predicates']['Represents']=[]
  add('missing-representation-for-'+n,role_missing_rep,False)
 def both_roles(m):
  for n in b.RELIANCE:m['predicates'][n]=[['u']]
 add('one-use-may-have-several-reliance-roles',both_roles)
 add('promotion-effect-description-not-actual-promotion',lambda m:m['predicates'].update(ValidationEffectDescription=[],PromotionEffectDescription=[['ReviewEffect-a']]))
 for n in b.OUTCOMES:add('outcome-can-be-independent-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['r']]))
 def unused(m):
  for n in b.RELIANCE+['ReliedCoupling','NonOrthogonal','Represents']:m['predicates'][n]=[]
 add('all-uses-unrelied-vacuous-T-not-I',unused,True,False)
 def self_link(m):
  setvalue(m,'useTarget',['u'],'a');setvalue(m,'relationTarget',['r'],'a')
 add('no-universal-distinct-endpoint-policy-invented',self_link)
 add('unrelied-nonorthogonal-idea-needs-no-coupling',lambda m:m['predicates'].update(Orthogonal=[],NonOrthogonal=[['u'],['unused']]))
 add('unclassified-unused-idea-is-not-false-nonorthogonality',lambda m:m['predicates'].update(Orthogonal=[]))
 add('malformed-object-result',lambda m:setvalue(m,'useSource',['u'],'Kind-a'),error='ill-sorted-function-result')
 add('nontotal-relation-owner',lambda m:m['functions']['relationOwner'].pop(),error='nontotal-function')
 add('bad-evidence-tuple',lambda m:m['predicates'].update(HasEvidence=[['r']]),error='ill-sorted-model-tuple')
 add('duplicate-representation',lambda m:m['predicates']['Represents'].append(['u','r']),error='duplicate-predicate-tuple')
 return rows
def qualify(model,ids):return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}
def verify(write=False):
    context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT)
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
    prior=json.loads((b.BASE/'definitions/cal.definition.identity-relation/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-typed-coupling-model-controls/v1-candidate','status':'PASS-for-exact-authored-typed-coupling-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite models and seven targets outside T; selected reliance requires at least one exact typed representative. No actual compliance, automatic promotion, effect execution, owner fidelity, native enumeration or whole Definition acceptance.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
