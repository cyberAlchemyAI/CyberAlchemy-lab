"""Independent finite models: descriptive Claim, only-if fields and known-implicit nongoverning disposition."""
import itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Entity':['c1','c2','c3','c4','c5','c6','a1','b1','x1','owner1'],'State':['before','after'],'Token':['empty']+[n.lower()+'-value' for n in b.FIELDS]};functions={}
 for n,(args,_) in b.FUNCTIONS.items():
  field=next(x for x in b.FIELDS if x.lower()+'FieldValue'==n);functions[n]=[{'args':[e],'value':'empty' if e=='c2' and field=='Challenge' or e in ['c4','c6'] and field in ['Surface','Challenge'] else field.lower()+'-value'} for e in domains['Entity']]
 p={n:[] for n in b.SIGNATURE};claims=['c1','c2','c3','c4','c5','c6']
 p.update(AuthorityClaim=[[c] for c in claims],ExplicitAssertion=[[c] for c in claims],Challengeable=[[c] for c in claims],DescribesMayPerform=[[c] for c in claims],ValidClaim=[['c1'],['c5']],AdmissibleClaim=[['c1'],['c2']],Authority=[['a1']],AuthorityBoundary=[['b1']],GoverningClaim=[['c5','after']],CandidateEvidence=[['c2','after']],Residue=[['c4','after']],ImplicitChallenge=[['c2','after']],ImplicitSurface=[['c4','after']],ClaimAboutAuthority=[['c1','a1']])
 for n in b.FIELDS:p['Explicit'+n]=[[c] for c in claims if not(c=='c2' and n=='Challenge' or c in ['c4','c6'] and n in ['Surface','Challenge'])]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('descriptive-claim-necessary-fields-and-known-implicit-posture-not-actual-right',lambda m:None)
 for n in b.OUTCOMES:add('independent-world-fact-'+n,lambda m,n=n:m['predicates'][n].append(['c1']))
 add('independent-actual-authorization-permitted',lambda m:m['predicates']['ActualAuthorizedFor'].append(['c1','x1','after']))
 add('independent-actual-performance-permitted',lambda m:m['predicates']['ActualPerformed'].append(['c1','x1','after']))
 add('independent-owner-authentication-permitted',lambda m:m['predicates']['AuthenticatedOwner'].append(['c1']))
 add('independent-complete-valid-governing-marker-permitted',lambda m:m['predicates']['GoverningClaim'].append(['c1','after']))
 add('unknown-surface-not-silently-known-implicit-or-governing-forbidden',lambda m:m['predicates']['GoverningClaim'].append(['c6','after']))
 add('candidate-evidence-and-residue-overlap-not-excluded',lambda m:m['predicates']['Residue'].append(['c2','after']),True,False)
 for n in ['ExplicitAssertion','Challengeable','DescribesMayPerform']:add('claim-missing-'+n,lambda m,n=n:m['predicates'][n].remove(['c1']),False,True)
 for n in b.TARGET_FIELDS:add('target-claim-missing-named-'+n,lambda m,n=n:m['predicates']['Explicit'+n].remove(['c4']),False,True)
 for n in b.TARGET_FIELDS:add('target-claim-empty-'+n,lambda m,n=n:setvalue(m,n.lower()+'FieldValue',['c4'],'empty'),False,True)
 for n in b.FIELDS:add('valid-claim-missing-explicit-'+n,lambda m,n=n:m['predicates']['Explicit'+n].remove(['c1']),False,True)
 for n in b.FIELDS:add('valid-claim-empty-'+n+'-value',lambda m,n=n:setvalue(m,n.lower()+'FieldValue',['c1'],'empty'),False,True)
 for n in b.FIVE:add('admissible-claim-missing-explicit-'+n,lambda m,n=n:m['predicates']['Explicit'+n].remove(['c2']),False,True)
 for n in b.FIVE:add('admissible-claim-empty-'+n+'-value',lambda m,n=n:setvalue(m,n.lower()+'FieldValue',['c2'],'empty'),False,True)
 for n in b.FIELDS:
  add('known-implicit-'+n+'-without-candidate-or-residue',lambda m,n=n:m['predicates']['Implicit'+n].append(['c1','after']),False,True)
  add('known-implicit-'+n+'-with-selected-candidate-disposition',lambda m,n=n:m['predicates']['Implicit'+n].append(['c1','after']) or m['predicates']['CandidateEvidence'].append(['c1','after']))
 add('known-implicit-claim-governing-rejected',lambda m:m['predicates']['GoverningClaim'].append(['c2','after']),False,True)
 add('known-implicit-evidence-disposition-missing',lambda m:m['predicates'].update(CandidateEvidence=[]),False,False)
 add('known-implicit-residue-disposition-missing',lambda m:m['predicates'].update(Residue=[]),False,False)
 add('known-implicit-after-state-does-not-ban-independent-before-governing-marker',lambda m:m['predicates']['GoverningClaim'].append(['c2','before']))
 add('complete-eight-fields-can-be-valid-rich-insufficient-witness-fails',lambda m:m['predicates']['ValidClaim'].append(['c3']),True,False)
 add('complete-eight-fields-can-be-admissible-rich-insufficient-witness-fails',lambda m:m['predicates']['AdmissibleClaim'].append(['c3']),True,False)
 add('no-joint-valid-admissible-rich-witness-still-T',lambda m:m['predicates']['AdmissibleClaim'].remove(['c1']),True,False)
 add('no-valid-marker-still-T',lambda m:m['predicates'].update(ValidClaim=[]),True,False)
 def no_claim(m):
  for n in ['AuthorityClaim','ValidClaim','AdmissibleClaim']:m['predicates'][n]=[]
 add('no-Claim-vacuous-T-fails-rich-I',no_claim,True,False)
 add('valid-marker-without-Claim-type',lambda m:m['predicates']['AuthorityClaim'].remove(['c1']),False,False)
 add('nontotal-field-function',lambda m:m['functions']['scopeFieldValue'].pop(),error='nontotal-function')
 add('ill-sorted-field-value',lambda m:setvalue(m,'scopeFieldValue',['c1'],'c1'),error='ill-sorted-function-result')
 add('ill-sorted-empty-sentinel',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-known-implicit-relation-arity',lambda m:m['predicates'].update(ImplicitScope=[['c1']]),error='ill-sorted-model-tuple')
 add('duplicate-claim-to-Authority-tuple',lambda m:m['predicates']['ClaimAboutAuthority'].append(['c1','a1']),error='duplicate-predicate-tuple')
 add('empty-Entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.authority/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-AuthorityClaim-model-controls/v1-candidate','status':'PASS-for-exact-authored-AuthorityClaim-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied descriptive Claim/necessary-field/known-implicit disposition models and twenty-four outside-T targets. Known implicit is distinct from missing/unknown. No actual owner/right/route/surface/scope/object/claim/basis/entity/history denotation, validity/admissibility sufficiency or equivalence, exact tuple/source-carrier conformance, governing authentication, transfer or unbounded transition/source-fidelity proof.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
