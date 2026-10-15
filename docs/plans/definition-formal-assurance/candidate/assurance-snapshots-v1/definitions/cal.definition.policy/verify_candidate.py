"""Independent supplied Policy model controls; no actual issuer authority or operational proof."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 for row in m['functions'][n]:
  if row['args']==[arg]:row['value']=value;return
 raise ValueError('Missing function argument')
def base_model():
 domains={'Entity':['p1','p2','outside'],'RuleSet':['rules','outsideRules'],'Version':['v1','vOutside'],'Issuer':['issuer','outsideIssuer'],'Scope':['scope','outsideScope','nestedScope'],'Rule':['rDecision','rAction','rTransition','rEvidence','rHandling'],'Target':['decision','action','transition','evidence','handling','outsideTarget'],'Token':['empty','shared-handle','outside-handle']}
 constants={'EMPTY':'empty'};policies=['p1','p2'];rules=domains['Rule'];targets=domains['Target'][:-1]
 maps={'policyRuleSet':lambda p:'rules' if p in policies else 'outsideRules','policyVersion':lambda p:'v1' if p in policies else 'vOutside','policyIssuer':lambda p:'issuer' if p in policies else 'outsideIssuer','policyScope':lambda p:'scope' if p in policies else 'outsideScope','issuerAuthorityScope':lambda i:'scope' if i=='issuer' else 'outsideScope','versionHandle':lambda z:'shared-handle','issuerHandle':lambda z:'shared-handle','scopeHandle':lambda z:'shared-handle','policyIdentityHandle':lambda z:'shared-handle','ruleSetVersion':lambda rs:'v1' if rs=='rules' else 'vOutside','ruleScope':lambda r:'scope','targetScope':lambda t:'outsideScope' if t=='outsideTarget' else 'scope'}
 assert maps.keys()==b.FUNCTIONS.keys()
 functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['Policy',*b.QUALIFIERS,'GovernedIdentityOrRecord','BoundedScope','ExactIssuanceDeclared']:predicates[n]=[[p] for p in policies]
 predicates.update(RuleSetNormative=[['rules']],ExactVersionDeclared=[['v1']],DeclaredIssuer=[['issuer']],ExactScopeDeclared=[['scope']],ScopeWithinIssuer=[['scope','scope']],ScopeWithinPolicy=[['scope','scope'],['nestedScope','scope']],RuleInSet=[[r,'rules'] for r in rules],Constrains=[[r,t] for r,t in zip(rules,targets) if r in ['rDecision','rTransition','rHandling']],Requires=[[r,t] for r,t in zip(rules,targets) if r in ['rAction','rEvidence']],DeclaredRuleApplication=[['p1',r,t] for r,t in zip(rules,targets)]+[['p2','rDecision','decision']])
 for n,t in zip(b.CATEGORIES,targets):predicates[n]=[[t]]
 for n in ['ResponsibilitySignal','RepositoryPermissionSignal','OwnerLabelSignal','RuleReferenceSignal']:predicates[n]=[['outside']]
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('versioned-scoped-normative-rule-targets-without-actual-outcomes',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-'+n,lambda m,n=n:m['predicates']['Actual'+n].append(['p1']),I=True)
 add('overlapping-target-categories-permitted',lambda m:m['predicates']['EvidenceTarget'].append(['decision']),I=True)
 add('declared-narrower-target-scope-permitted',lambda m:setfn(m,'targetScope','decision','nestedScope'),I=True)
 add('declared-narrower-rule-scope-permitted',lambda m:setfn(m,'ruleScope','rDecision','nestedScope'),I=True)
 add('rule-may-both-constrain-and-require',lambda m:m['predicates']['Requires'].append(['rDecision','decision']),I=True)
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['p1']),T=False)
 for n in ['GovernedIdentityOrRecord','BoundedScope','ExactIssuanceDeclared']:add('missing-policy-'+n,lambda m,n=n:m['predicates'][n].remove(['p1']),T=False)
 for n in ['RuleSetNormative','ExactVersionDeclared','DeclaredIssuer','ExactScopeDeclared','ScopeWithinIssuer']:add('missing-scoped-issuance-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('wrong-rule-set-version',lambda m:setfn(m,'ruleSetVersion','rules','vOutside'),T=False)
 for n,arg in [('policyIdentityHandle','p1'),('versionHandle','v1'),('issuerHandle','issuer'),('scopeHandle','scope')]:add('empty-required-'+n,lambda m,n=n,arg=arg:setfn(m,n,arg,'empty'),T=False)
 add('wrong-rule-scope',lambda m:setfn(m,'ruleScope','rDecision','outsideScope'),T=False)
 add('wrong-target-scope',lambda m:setfn(m,'targetScope','decision','outsideScope'),T=False)
 add('rule-not-in-bound-set',lambda m:m['predicates']['RuleInSet'].remove(['rDecision','rules']),T=False)
 add('target-without-category',lambda m:m['predicates']['DecisionTarget'].clear(),T=False)
 add('rule-with-neither-modality',lambda m:m['predicates']['Constrains'].remove(['rDecision','decision']),T=False)
 for n in b.ROLES[:4]:add('forbidden-policy-role-'+n,lambda m,n=n:m['predicates'][n].append(['p1']),T=False)
 add('empty-application-exposes-population-vacuity',lambda m:m['predicates']['DeclaredRuleApplication'].clear(),I=False)
 add('named-source-category-needs-explicit-witness',lambda m:m['predicates']['DeclaredRuleApplication'].remove(['p1','rHandling','handling']),I=False)
 add('outside-signals-do-not-define-policy',lambda m:None,I=True)
 add('same-record-handle-distinct-policy-identities',lambda m:None,I=True)
 add('missing-total-function-entry',lambda m:m['functions']['policyScope'].pop(),error='nontotal-function')
 add('ill-sorted-scope-result',lambda m:setfn(m,'policyScope','p1','issuer'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='scope'),error='ill-sorted-constant')
 add('wrong-application-arity',lambda m:m['predicates'].update(DeclaredRuleApplication=[['p1','rDecision']]),error='ill-sorted-model-tuple')
 add('duplicate-policy-tuple',lambda m:m['predicates']['Policy'].append(['p1']),error='duplicate-predicate-tuple')
 add('empty-version-domain',lambda m:m['domains'].update(Version=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['policyScope'].append(copy.deepcopy(m['functions']['policyScope'][0])),error='duplicate-function-tuple')
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
            if case['expected_error'] is not None or t!=case['expected_T'] or (case['expected_I'] is not None and i!=case['expected_I']):raise ValueError('Wrong authored control: '+case['case_id']+' '+str((t,i)))
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
    prior=json.loads((b.BASE/'definitions/cal.definition.parent-instance-authority-separation-invariant/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Policy-model-controls/v1-candidate','status':'PASS-for-exact-authored-Policy-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed declared versioned normative rule-set,exact scoped issuance and rule-target guards checked on supplied models. Actual issuer authority,issuance,effective version,execution,compliance,adoption and consumer alignment remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
