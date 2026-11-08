"""Independent scoped counting standing and valid8/admissible5 models; no actual governing authentication."""
import itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Entity':['a1','a2','a3','c1','c2','c3','x1','x2','action1','owner1'],'State':['before','after'],'Token':['empty','scope','other-scope','purpose','identity','other-identity']+[n.lower()+'-value' for n in b.FIELDS]};functions={}
 for n,(args,_) in b.FUNCTIONS.items():
  rows=[]
  for xs in itertools.product(*[domains[s] for s in args]):
   e=xs[0]
   if n=='scopeToken':value='other-scope' if e=='a3' else 'scope'
   elif n=='purposeToken':value='purpose'
   elif n=='authorityIdentity':value='identity' if e in ['a1','a2'] else 'other-identity'
   else:
    field=next(x for x in b.FIELDS if x.lower()+'FieldValue'==n);value='empty' if e=='c2' and field not in b.FIVE else field.lower()+'-value'
   rows.append({'args':list(xs),'value':value})
  functions[n]=rows
 p={n:[] for n in b.SIGNATURE};p.update(Authority=[[a] for a in ['a1','a2','a3']],RightStanding=[['a1'],['a2']],CountingDutyStanding=[['a3']],OwnerQualified=[['a1'],['a2'],['a3']],DeclaredObject=[['x1'],['x2']],TermObject=[['x1']],ArtifactObject=[['x2']],AuthorityClaim=[['c1'],['c2'],['c3']],ValidClaim=[['c1']],AdmissibleClaim=[['c1'],['c2']],DeclaredCountsObject=[['a1','x1'],['a2','x1'],['a3','x2']],MayDecideCountsFor=[['a1','x1'],['a2','x1'],['a3','x2']],ClaimForAuthority=[['c1','a1']])
 for n in b.FIELDS:p['Explicit'+n]=[['c1'],['c3']]+([['c2']] if n in b.FIVE else [])
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('scoped-right-and-duty-necessary-fields-not-governing-sufficiency',lambda m:None)
 add('inclusive-right-and-duty-overlap-permitted',lambda m:m['predicates']['CountingDutyStanding'].append(['a2']))
 for n in b.OUTCOMES:add('independent-world-fact-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['a1']]))
 add('independent-exact-counting-action-authorization-permitted',lambda m:m['predicates'].update(AuthorizedFor=[['a1','x1','before']]))
 add('independent-actual-counting-outcome-permitted',lambda m:m['predicates'].update(ActualCount=[['a1','x1','before']]))
 add('complete-valid-claim-can-also-be-governing-without-inferred-source-approval',lambda m:m['predicates'].update(GoverningClaim=[['c1']]))
 add('governing-marker-with-five-fields-not-excluded-by-partial-transition-projection',lambda m:m['predicates'].update(GoverningClaim=[['c2']]))
 add('independent-authenticated-owner-marker-permitted',lambda m:m['predicates'].update(AuthenticatedOwner=[['c1']]))
 add('missing-owner-qualification',lambda m:m['predicates'].update(OwnerQualified=[]),False,True)
 add('missing-right-standing',lambda m:m['predicates'].update(RightStanding=[]),False,False)
 add('missing-counting-duty-standing',lambda m:m['predicates'].update(CountingDutyStanding=[]),False,False)
 add('missing-declared-object-type',lambda m:m['predicates'].update(DeclaredObject=[]),False,True)
 def no_types(m):
  for n in b.OBJECT_KINDS:m['predicates'][n]=[]
 add('missing-object-kind-classification',no_types,False,True)
 add('missing-declared-counts-object',lambda m:m['predicates'].update(DeclaredCountsObject=[]),False,False)
 add('missing-counting-permission-description',lambda m:m['predicates'].update(MayDecideCountsFor=[]),False,False)
 for n in ['scopeToken','purposeToken']:add('empty-'+n+'-invalid-and-rich-shared-context-fails',lambda m,n=n:setvalue(m,n,['a1'],'empty'),False,False)
 for n in b.FIELDS:add('valid-claim-missing-explicit-'+n,lambda m,n=n:m['predicates']['Explicit'+n].remove(['c1']),False,True)
 for n in b.FIVE:add('admissible-claim-missing-explicit-'+n,lambda m,n=n:m['predicates']['Explicit'+n].remove(['c2']),False,True)
 for n in b.FIELDS:add('valid-claim-empty-'+n+'-value',lambda m,n=n:setvalue(m,n.lower()+'FieldValue',['c1'],'empty'),False,True)
 add('valid-marker-without-claim-type',lambda m:m['predicates']['AuthorityClaim'].remove(['c1']),False,True)
 add('all-eight-named-can-be-valid-primary-permits-rich-insufficient-witness-fails',lambda m:m['predicates']['ValidClaim'].append(['c3']),True,False)
 add('all-eight-named-can-be-admissible-primary-permits-rich-insufficient-witness-fails',lambda m:m['predicates']['AdmissibleClaim'].append(['c3']),True,False)
 add('valid-not-automatically-admissible',lambda m:m['predicates']['AdmissibleClaim'].remove(['c1']),True,False)
 add('admissible-not-automatically-valid',lambda m:m['predicates'].update(ValidClaim=[]),True,False)
 add('no-Authority-vacuous-standing-T-fails-rich-I',lambda m:m['predicates'].update(Authority=[]),True,False)
 add('nontotal-purpose-function',lambda m:m['functions']['purposeToken'].pop(),error='nontotal-function')
 add('ill-sorted-field-value',lambda m:setvalue(m,'scopeFieldValue',['c1'],'a1'),error='ill-sorted-function-result')
 add('ill-sorted-empty-sentinel',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-counting-relation-arity',lambda m:m['predicates'].update(MayDecideCountsFor=[['a1']]),error='ill-sorted-model-tuple')
 add('duplicate-claim-to-Authority-tuple',lambda m:m['predicates']['ClaimForAuthority'].append(['c1','a1']),error='duplicate-predicate-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.responsibility/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Authority-model-controls/v1-candidate','status':'PASS-for-exact-authored-Authority-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied Authority scoped-standing/necessary-claim-field models and twenty targets outside T. No actual owner/right/duty/surface/purpose/scope/object/claim/basis/entity/history denotation, validity/admissibility sufficiency or equivalence, dedicated Authority carrier, governing authentication, transfer or source-fidelity proof.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
