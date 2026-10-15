"""Supplied Validation exact-binding,partial PASS,coverage and scoped-evidence models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 domains={s:[s.lower()+'A',s.lower()+'Outside'] for s in b.SORTS};domains.update(Validation=['vPass','vPartial','vFail','vEmpty','vOutside'],EvaluationReference=['evalPass','evalPartial','evalFail','evalEmpty','evalOutside'],CriteriaProfile=['pFull','pPartial','pFail','pEmpty','pOutside'],InputReference=['inputA','inputB','inputOutside'],ReceiptReference=['rPass','rPartial','rFail','rEmpty','rOutside'],DeclaredCheck=['c0','c1','cOutside'],Outcome=['oPass0','oPass1','oPart0','oNE','oFail','oFailPass','oOutside'],OutcomeTag=['tagPass','tagFail','tagNE','tagOther'],Digest=['dFull','dPartial','dFail','dEmpty','dSubject','dInputA','dInputB','dOutside'],ConformanceProfile=['confFull','confPartial','confOutside'],ConformanceEvidenceUse=['uFull','uPartial','uOutside'],Token=['empty','reference','extra'])
 constants={'EMPTY':'empty','PASS':'tagPass','FAIL':'tagFail','NOT_EVALUABLE':'tagNE'};maps={}
 for n,s in b.FIELDS.items():maps[n]=lambda v,s=s:domains[s][-1] if v=='vOutside' else domains[s][0]
 maps['valEvaluation']=lambda v:{'vPass':'evalPass','vPartial':'evalPartial','vFail':'evalFail','vEmpty':'evalEmpty','vOutside':'evalOutside'}[v]
 maps['valProfile']=lambda v:{'vPass':'pFull','vPartial':'pPartial','vFail':'pFail','vEmpty':'pEmpty','vOutside':'pOutside'}[v]
 maps['valInput']=lambda v:'inputOutside' if v=='vOutside' else 'inputB' if v=='vPartial' else 'inputA'
 maps['valReceipt']=lambda v:{'vPass':'rPass','vPartial':'rPartial','vFail':'rFail','vEmpty':'rEmpty','vOutside':'rOutside'}[v]
 maps['profileDigest']=lambda p:{'pFull':'dFull','pPartial':'dPartial','pFail':'dFail','pEmpty':'dEmpty','pOutside':'dOutside'}[p]
 maps['subjectDigest']=lambda s:'dOutside' if s=='subjectreferenceOutside' else 'dSubject';maps['inputDigest']=lambda i:{'inputA':'dInputA','inputB':'dInputB','inputOutside':'dOutside'}[i]
 for n,field in [('Profile','valProfile'),('Subject','valSubject'),('Input','valInput')]:maps['val'+n+'Digest']=lambda v,n=n,field=field:maps[n.lower()+'Digest'](maps[field](v))
 maps['profileScope']=lambda p:'coveragescopeOutside' if p in ['pPartial','pOutside'] else 'coveragescopeA';maps['profileMode']=lambda p:'evaluationmodeOutside' if p=='pOutside' else 'evaluationmodeA'
 maps['outcomeValidation']=lambda o:{'oPass0':'vPass','oPass1':'vPass','oPart0':'vPartial','oNE':'vPartial','oFail':'vFail','oFailPass':'vFail','oOutside':'vOutside'}[o]
 maps['outcomeCheck']=lambda o:'cOutside' if o=='oOutside' else 'c1' if o in ['oPass1','oNE','oFailPass'] else 'c0';maps['outcomeTag']=lambda o:'tagOther' if o=='oOutside' else 'tagNE' if o=='oNE' else 'tagFail' if o=='oFail' else 'tagPass'
 maps['useValidation']=lambda u:{'uFull':'vPass','uPartial':'vPartial','uOutside':'vOutside'}[u];maps['useProfile']=lambda u:{'uFull':'confFull','uPartial':'confPartial','uOutside':'confOutside'}[u];maps['useScope']=lambda u:'coveragescopeOutside' if u=='uOutside' else 'coveragescopeA'
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE};selected=['vPass','vPartial','vFail','vEmpty']
 for n in ['ValidationApplicable','ValidationInScopeDeclared','CompleteOutcomeRecordDeclared']:predicates[n]=[[x] for x in selected]
 for n,s in b.FIELDS.items():predicates[s+'Declared']=[[x] for x in dict.fromkeys(maps[n](v) for v in selected)]
 predicates.update(ReportedPASSDeclared=[['vPass'],['vPartial'],['vEmpty']],CompletePASSCoverageDeclared=[['vPass']],ProfileCoverageDeclared=[[x] for x in ['pFull','pPartial','pFail','pEmpty']],ProfileEvaluationModeDeclared=[[x] for x in ['pFull','pPartial','pFail','pEmpty']],DeclaredCheckDeclared=[['c0'],['c1']],DigestDeclared=[[x] for x in domains['Digest'] if x!='dOutside'],CoverageScopeDeclared=[['coveragescopeA'],['coveragescopeOutside']],EvaluationModeDeclared=[['evaluationmodeA']],ProfileCheckDeclared=[[p,c] for p in ['pFull','pPartial','pFail'] for c in ['c0','c1']],OutcomeIncluded=[[maps['outcomeValidation'](o),o] for o in domains['Outcome'] if o!='oOutside'],CheckEvaluableDeclared=[['vPass','c0'],['vPass','c1'],['vPartial','c0'],['vFail','c0'],['vFail','c1']],ReceiptOutcomeRecordedDeclared=[[maps['valReceipt'](maps['outcomeValidation'](o)),o] for o in domains['Outcome'] if o!='oOutside'],PASSCoveredCheckDeclared=[['vPass','c0'],['vPass','c1'],['vPartial','c0']],ConformanceProfileDeclared=[['confFull'],['confPartial']],ConformanceProfileApplicableDeclared=[['confFull','subjectreferenceA','coveragescopeA'],['confPartial','subjectreferenceA','coveragescopeA']],ConformanceSufficiencyDeclared=[['confFull','pFull','coveragescopeA'],['confPartial','pPartial','coveragescopeA']],ConformanceRequiredCheckDeclared=[['confFull','c0'],['confFull','c1'],['confPartial','c0']])
 for n in ['ConformanceEvidenceUseApplicable','UseInScopeDeclared','UseWithinContextAndScopeDeclared']:predicates[n]=[['uFull'],['uPartial']]
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('exact-bound-complete-partial-empty-PASS-FAIL-NE-and-scoped-evidence',lambda m:None,I=True)
 for n in b.ACTUAL:add('independent-Validation-actual-'+n,lambda m,n=n:m['predicates']['ValidationActual'+n].append(['vPartial']),I=True)
 for n in b.USE_ACTUAL:add('independent-Use-actual-'+n,lambda m,n=n:m['predicates']['UseActual'+n].append(['uPartial']),I=True)
 add('outside-validation-empty-handle',lambda m:setfn(m,'validationHandle','vOutside','empty'),I=True)
 add('outside-profile-opaque-empty-handle',lambda m:setfn(m,'criteriaProfileHandle','pOutside','empty'),I=True)
 add('outside-outcome-can-have-unlisted-tag',lambda m:setfn(m,'outcomeTag','oOutside','tagOther'),I=True)
 add('outside-use-empty-handle',lambda m:setfn(m,'conformanceEvidenceUseHandle','uOutside','empty'),I=True)
 add('empty-profile-complete-PASS-declaration-is-vacuous-not-actual-coverage',lambda m:m['predicates']['CompletePASSCoverageDeclared'].append(['vEmpty']),I=True)
 add('complete-PASS-label-can-be-absent-with-passed-checks',lambda m:m['predicates']['CompletePASSCoverageDeclared'].clear(),I=False)
 def repeated_outcome(m):
  m['domains']['Outcome'].append('oRepeated')
  for n,(sorts,result) in b.FUNCTIONS.items():
   if sorts==['Outcome']:m['functions'][n].append({'args':['oRepeated'],'value':next(x['value'] for x in m['functions'][n] if x['args']==['oPass0'])})
  m['predicates']['OutcomeIncluded'].append(['vPass','oRepeated']);m['predicates']['ReceiptOutcomeRecordedDeclared'].append(['rPass','oRepeated'])
 add('multiple-included-PASS-outcomes-for-one-check-allowed',repeated_outcome,I=True)
 def aggregate_receipt(m):
  setfn(m,'valReceipt','vPartial','rPass');m['predicates']['ReceiptOutcomeRecordedDeclared'].extend([['rPass','oPart0'],['rPass','oNE']])
 add('shared-receipt-reference-does-not-identify-evaluations',aggregate_receipt,I=True)
 add('scoped-required-check-set-can-repeat-source-profile-subset',lambda m:m['predicates']['ConformanceRequiredCheckDeclared'].append(['confPartial','c0']),error='duplicate-predicate-tuple')
 # Duplicate tuples are malformed even when the source-level cardinality policy stays open.
 for n in ['ValidationInScopeDeclared','CompleteOutcomeRecordDeclared']:add('missing-Validation-'+n,lambda m,n=n:m['predicates'][n].remove(['vPass']),T=False)
 add('declared-validation-without-membership',lambda m:m['predicates']['ValidationApplicable'].remove(['vPass']),T=False)
 for s in b.FIELDS.values():add('missing-Validation-component-'+s,lambda m,s=s:m['predicates'][s+'Declared'].clear(),T=False)
 for field in ['Profile','Subject','Input']:add('different-bound-'+field+'-digest',lambda m,field=field:setfn(m,'val'+field+'Digest','vPass','dOutside'),T=False)
 add('missing-declared-digests',lambda m:m['predicates']['DigestDeclared'].clear(),T=False)
 for n in ['ProfileCoverageDeclared','ProfileEvaluationModeDeclared','CoverageScopeDeclared','EvaluationModeDeclared']:add('missing-profile-scope-or-mode-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('PASS-and-FAIL-tags-collapsed',lambda m:m['constants'].update(FAIL='tagPass'),T=False)
 add('PASS-and-NE-tags-collapsed',lambda m:m['constants'].update(NOT_EVALUABLE='tagPass'),T=False)
 add('selected-outcome-with-unlisted-tag',lambda m:setfn(m,'outcomeTag','oPass0','tagOther'),T=False)
 add('included-outcome-bound-to-wrong-Validation',lambda m:setfn(m,'outcomeValidation','oPass0','vPartial'),T=False)
 add('selected-outcome-check-not-declared-by-profile',lambda m:m['predicates']['ProfileCheckDeclared'].remove(['pFull','c0']),T=False)
 add('missing-selected-check-declaration',lambda m:m['predicates']['DeclaredCheckDeclared'].clear(),T=False)
 add('omitted-declared-check-outcome',lambda m:m['predicates']['OutcomeIncluded'].remove(['vPass','oPass1']),T=False)
 add('receipt-omits-recorded-outcome',lambda m:m['predicates']['ReceiptOutcomeRecordedDeclared'].remove(['rPass','oPass0']),T=False)
 add('NE-labelled-as-evaluable',lambda m:m['predicates']['CheckEvaluableDeclared'].append(['vPartial','c1']),T=False)
 add('PASS-labelled-as-not-evaluable',lambda m:m['predicates']['CheckEvaluableDeclared'].remove(['vPass','c0']),T=False)
 add('reported-PASS-with-evaluable-FAIL',lambda m:setfn(m,'outcomeTag','oPass0','tagFail'),T=False)
 add('FAIL-evaluation-reported-as-PASS',lambda m:m['predicates']['ReportedPASSDeclared'].append(['vFail']),T=False)
 add('NE-check-claimed-PASS-covered',lambda m:m['predicates']['PASSCoveredCheckDeclared'].append(['vPartial','c1']),T=False)
 add('undeclared-check-claimed-PASS-covered',lambda m:m['predicates']['PASSCoveredCheckDeclared'].append(['vPass','cOutside']),T=False)
 add('passed-evaluable-check-lost-from-derived-coverage',lambda m:m['predicates']['PASSCoveredCheckDeclared'].remove(['vPass','c1']),T=False)
 add('partial-PASS-with-NE-claimed-complete',lambda m:m['predicates']['CompletePASSCoverageDeclared'].append(['vPartial']),T=False)
 for n in b.ROLES:add('Validation-meaning-collapse-'+n,lambda m,n=n:m['predicates'][n].append(['vPass']),T=False)
 for s,arg in [('Validation','vPass'),('EvaluationReference','evalPass'),('SubjectReference','subjectreferenceA'),('CriteriaProfile','pFull'),('InputReference','inputA'),('EvaluationEnvironment','evaluationenvironmentA'),('ValidatorIdentity','validatoridentityA'),('ReceiptReference','rPass'),('Context','contextA'),('DeclaredCheck','c0'),('Outcome','oPass0'),('Digest','dFull'),('CoverageScope','coveragescopeA'),('EvaluationMode','evaluationmodeA'),('ConformanceProfile','confFull'),('ConformanceEvidenceUse','uFull')]:add('empty-selected-'+s+'-handle',lambda m,s=s,arg=arg:setfn(m,b.HANDLES[s],arg,'empty'),T=False)
 for n in ['UseInScopeDeclared','UseWithinContextAndScopeDeclared']:add('missing-evidence-use-'+n,lambda m,n=n:m['predicates'][n].remove(['uFull']),T=False)
 add('evidence-use-declared-without-membership',lambda m:m['predicates']['ConformanceEvidenceUseApplicable'].remove(['uFull']),T=False)
 add('use-binds-outside-Validation',lambda m:setfn(m,'useValidation','uFull','vOutside'),T=False)
 add('evidence-use-without-reported-PASS',lambda m:m['predicates']['ReportedPASSDeclared'].remove(['vPass']),T=False)
 add('use-binds-undeclared-ConformanceProfile',lambda m:m['predicates']['ConformanceProfileDeclared'].remove(['confFull']),T=False)
 add('missing-applicable-conformance-profile',lambda m:m['predicates']['ConformanceProfileApplicableDeclared'].clear(),T=False)
 add('missing-exact-scope-sufficiency',lambda m:m['predicates']['ConformanceSufficiencyDeclared'].clear(),T=False)
 add('changed-evidence-use-scope',lambda m:setfn(m,'useScope','uFull','coveragescopeOutside'),T=False)
 add('partial-evidence-use-requires-uncovered-NE-check',lambda m:m['predicates']['ConformanceRequiredCheckDeclared'].append(['confPartial','c1']),T=False)
 add('missing-symbol',lambda m:m['predicates'].pop('ValidationApplicable'),error='model-signature-denominator-mismatch')
 add('partial-total-function',lambda m:m['functions']['valProfile'].pop(),error='nontotal-function')
 add('ill-sorted-constant',lambda m:m['constants'].update(EMPTY='vPass'),error='ill-sorted-constant')
 add('wrong-outcome-inclusion-arity',lambda m:m['predicates'].update(OutcomeIncluded=[['vPass']]),error='ill-sorted-model-tuple')
 add('duplicate-Validation-tuple',lambda m:m['predicates']['ValidationApplicable'].append(['vPass']),error='duplicate-predicate-tuple')
 add('empty-Outcome-domain',lambda m:m['domains'].update(Outcome=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['valProfile'].append(copy.deepcopy(m['functions']['valProfile'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.traceability/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Validation-model-controls/v1-candidate','status':'PASS-for-exact-authored-Validation-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed exact Validation bindings,declared check outcomes,evaluable PASS,partial coverage and scope-qualified conformance-evidence guards checked on supplied models. Actual execution,truth,Conformance,authority,owner fidelity and consumer alignment remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
