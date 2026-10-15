"""Independent typed finite assertion models: claim content is distinct from truth."""
import itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Claim':['c1','c2'],'Entity':['r1','p1','r2','p2','account','role'],'Policy':['pol1','pol2'],'EvidenceSet':['es1','es2'],'Owner':['owner1','owner2'],'Route':['route1','route2'],'Scope':['scope1','scope2'],'Identifier':['id1','id2']}
 functions={n:[{'args':list(xs),'value':domains[res][0]} for xs in itertools.product(*[domains[s] for s in args])] for n,(args,res) in b.FUNCTIONS.items()}
 for n,val in [('claimedPerson','p1')]:
  for row in functions[n]:row['value']=val
 predicates={n:[] for n in b.SIGNATURE};predicates.update(IdentityClaim=[['c1']],Attributable=[['c1']],Challengeable=[['c1']],Person=[['p1'],['p2']],HumanIndividual=[['p1'],['p2']],PersonReference=[['r1'],['r2']],BoundedReference=[['r1'],['r2']],DeclaredEvidencePolicy=[['pol1'],['pol2']],RecordedEvidenceSet=[['es1'],['es2']],AttributionRecord=[['owner1'],['owner2']],ChallengeRoute=[['route1'],['route2']],DeclaredScope=[['scope1'],['scope2']],ClaimsDenotes=[['c1','r1','p1']],DeclaresPolicy=[['c1','pol1']],PolicyApplies=[['pol1','scope1']],AttributedTo=[['c1','owner1']],ChallengedThrough=[['c1','route1']])
 return {'domains':domains,'constants':{},'functions':functions,'predicates':predicates}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('attributable-challengeable-assertion-without-world-denotation',lambda m:None)
 for n in ['Attributable','Challengeable','BoundedReference','DeclaredScope']:add('missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[]),False)
 for n in ['PersonReference','Person','DeclaredEvidencePolicy','RecordedEvidenceSet','AttributionRecord','ChallengeRoute']:add('missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[]),False,False)
 for n in ['ClaimsDenotes','DeclaresPolicy','PolicyApplies','AttributedTo','ChallengedThrough']:add('missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[]),False)
 add('wrong-asserted-reference-pair',lambda m:m['predicates'].update(ClaimsDenotes=[['c1','r2','p1']]),False)
 add('wrong-asserted-person-pair',lambda m:m['predicates'].update(ClaimsDenotes=[['c1','r1','p2']]),False)
 add('person-reference-function-disagrees-with-asserted-content',lambda m:setvalue(m,'claimReference',['c1'],'r2'),False)
 add('policy-function-disagrees-with-declared-policy',lambda m:setvalue(m,'claimPolicy',['c1'],'pol2'),False)
 add('scope-function-outside-recorded-policy-application',lambda m:setvalue(m,'claimScope',['c1'],'scope2'),False)
 add('attributor-function-disagrees-with-recorded-attribution',lambda m:setvalue(m,'claimOwner',['c1'],'owner2'),False)
 add('challenge-function-disagrees-with-route',lambda m:setvalue(m,'claimChallenge',['c1'],'route2'),False)
 add('person-not-human-rejected-by-separate-inherited-condition',lambda m:m['predicates'].update(HumanIndividual=[]),False)
 def collapsed(m):
  setvalue(m,'claimReference',['c1'],'p1');m['predicates']['PersonReference'].append(['p1']);m['predicates']['BoundedReference'].append(['p1']);m['predicates']['ClaimsDenotes']=[['c1','p1','p1']]
 add('bounded-reference-cannot-be-selected-referent',collapsed,False)
 add('unclaimed-person-may-also-be-human-reference-role-without-global-disjointness',lambda m:(m['predicates']['PersonReference'].append(['p2']),m['predicates']['BoundedReference'].append(['p2'])))
 add('extra-asserted-pair-not-universally-forbidden',lambda m:m['predicates']['ClaimsDenotes'].append(['c1','r2','p2']))
 def two(m):
  for n in ['IdentityClaim','Attributable','Challengeable']:m['predicates'][n].append(['c2'])
  for n,tuple in [('ClaimsDenotes',['c2','r1','p1']),('DeclaresPolicy',['c2','pol1']),('AttributedTo',['c2','owner1']),('ChallengedThrough',['c2','route1'])]:m['predicates'][n].append(tuple)
 add('two-claims-may-share-one-reference-person-identifier',two)
 def competing(m):
  two(m);setvalue(m,'claimedPerson',['c2'],'p2');m['predicates']['ClaimsDenotes'][-1]=['c2','r1','p2']
 add('competing-assertions-do-not-establish-reference-functionality',competing)
 add('no-claims-vacuous-primary-theory-fails-connected-I',lambda m:m['predicates'].update(IdentityClaim=[]),True,False)
 for n in b.SOURCE_OUTCOMES:add('claim-only-authorization-forbidden-'+n,lambda m,n=n:m['predicates'].__setitem__('AllowedClaimOnly'+n,[['c1']]),False)
 for n in b.OUTCOMES:add('independently-supported-world-outcome-permitted-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['c1']]))
 for n,args in [('ActualDenotes',['r1','p1']),('IdentifierDenotes',['id1','p1']),('EvidenceAuthentic',['es1']),('PolicySatisfied',['pol1','c1']),('ActualAttributorVerified',['owner1'])]:add('separately-established-'+n+'-permitted',lambda m,n=n,args=args:m['predicates'].__setitem__(n,[args]))
 add('nontotal-claim-person-selector',lambda m:m['functions']['claimedPerson'].pop(),error='nontotal-function')
 add('ill-sorted-reference-selector',lambda m:setvalue(m,'claimReference',['c1'],'pol1'),error='ill-sorted-function-result')
 add('wrong-asserted-denotation-arity',lambda m:m['predicates'].update(ClaimsDenotes=[['c1','r1']]),error='ill-sorted-model-tuple')
 add('duplicate-asserted-content-tuple',lambda m:m['predicates']['ClaimsDenotes'].append(['c1','r1','p1']),error='duplicate-predicate-tuple')
 add('empty-common-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.classification/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-identity-claim-model-controls/v1-candidate','status':'PASS-for-exact-authored-identity-claim-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite assertion models and sixteen targets outside T. Recorded attributable challengeable reference-to-Person assertion, declared evidence/policy and selected claim-only inference policy are checked; actual denotation/identifier/evidence/assurance/attributor truth, inherited Person/source precedence, common-carrier fidelity and whole-definition acceptance remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
