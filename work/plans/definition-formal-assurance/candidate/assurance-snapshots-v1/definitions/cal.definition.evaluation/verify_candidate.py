"""Independent finite controls for exact declared Evaluation records;no actual execution or admission inferred."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 suffix=['Pass','Fail','ExternalNE','Blocked','AfterPass','Validation','Effect','Cycle','Outside'];runs=['ordinary','validation','effect','outside'];profiles=['pOrdinary','pValidation','pEffect','pOutside'];inputs=['input','otherInput','outsideInput'];checks=['c'+s for s in suffix];outs=['o'+s for s in suffix];sets=['os'+s.title() for s in runs];ess=['es'+s for s in suffix];items=['evidence','outsideEvidence'];blockers=['bExternal','bFail','bOutside'];tokens=['empty','reference','digest','differentDigest']
 def run(o):return 'validation' if o=='oValidation' else 'effect' if o=='oEffect' else 'outside' if o=='oOutside' else 'ordinary'
 def profile(r):return 'p'+r.title()
 def inp(r):return 'otherInput' if r=='effect' else 'outsideInput' if r=='outside' else 'input'
 domains={'EvaluationRun':runs,'Profile':profiles,'Subject':['subject','outsideSubject'],'InputState':inputs,'Check':checks,'OutcomeSet':sets,'Outcome':outs,'OutcomeStatus':['pass','fail','ne','unknown'],'EvidenceSet':ess,'Evidence':items,'Blocker':blockers,'Token':tokens}
 maps={'runProfile':profile,'runSubject':lambda r:'outsideSubject' if r=='outside' else 'subject','runInput':inp,'runOutcomes':lambda r:'os'+r.title(),'runProfileDigest':lambda r:'digest','runSubjectDigest':lambda r:'digest','runInputDigest':lambda r:'differentDigest' if r=='effect' else 'digest','profileDigest':lambda p:'digest','subjectDigest':lambda s:'digest','inputDigest':lambda i:'differentDigest' if i=='otherInput' else 'digest','runHandle':lambda r:'reference','profileHandle':lambda p:'reference','subjectHandle':lambda s:'reference','inputHandle':lambda i:'reference','outcomeSetHandle':lambda s:'reference','outcomeRun':run,'outcomeCheck':lambda o:'c'+o[1:],'outcomeStatus':lambda o:'fail' if o=='oFail' else 'ne' if o in ['oExternalNE','oBlocked'] else 'pass','outcomeEvidence':lambda o:'es'+o[1:],'outcomeHandle':lambda o:'reference','checkHandle':lambda c:'reference','evidenceSetHandle':lambda s:'reference','evidenceHandle':lambda e:'reference','blockerHandle':lambda bb:'reference','blockerCause':lambda bb:'reference','blockerUpstreamCheck':lambda bb:'cFail' if bb=='bFail' else 'cOutside'}
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE};active=runs[:-1]
 for n in ['Evaluation','RunRecordDeclared','ProfileApplicationDeclared']:predicates[n]=[[r] for r in active]
 selectedouts=outs[:7]
 predicates.update(ProfileDeclared=[[p] for p in profiles[:-1]],ProfileCurrentDeclared=[[p] for p in profiles[:-1]],SubjectCurrentDeclared=[['subject']],InputCurrentDeclared=[['input'],['otherInput']],OutcomeSetDeclared=[[s] for s in sets[:-1]],EvidenceSetDeclared=[[es] for es in ess],ValidationRole=[['validation']],ValidationProfileDeclared=[['pValidation']],EffectfulExecutionDeclared=[['effect']],ProfileEffectIncludedDeclared=[['pEffect']],OutcomeIncluded=[['os'+run(o).title(),o] for o in selectedouts],ProfileCheckDeclared=[[profile(run(o)),'c'+o[1:]] for o in selectedouts],ProfileCoverageDeclared=[[profile(run(o)),'c'+o[1:]] for o in selectedouts],EvidenceMember=[['esPass','evidence']],BlockerDeclared=[['bExternal'],['bFail']],DependencyBlockerDeclared=[['bFail']],BlockerIncluded=[['oExternalNE','bExternal'],['oBlocked','bFail']],ProfileDependencyDeclared=[['pOrdinary','cBlocked','cFail'],['pOrdinary','cAfterPass','cPass']])
 return {'domains':domains,'constants':{'EMPTY':'empty','PASS':'pass','FAIL':'fail','NOT_EVALUABLE':'ne'},'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('collect-all-pass-fail-causal-NE-qualified-roles',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-'+n,lambda m,n=n:m['predicates']['Actual'+n].append(['ordinary']),I=True)
 add('empty-evidence-membership-permitted-in-source-fragment',lambda m:m['predicates'].update(EvidenceMember=[]),I=True)
 add('outside-record-result-not-governing',lambda m:setfn(m,'outcomeStatus','oOutside','unknown'),I=True)
 add('same-handles-do-not-collapse-profile-and-subject-objects',lambda m:None,I=True)
 add('validation-profile-does-not-force-validation-role',lambda m:m['predicates']['ValidationProfileDeclared'].append(['pOrdinary']),I=True)
 add('passed-prerequisite-does-not-force-dependent-PASS',lambda m:setfn(m,'outcomeStatus','oAfterPass','fail'),I=True)
 def cycle(m):
  for n in ['ProfileCheckDeclared','ProfileCoverageDeclared']:m['predicates'][n].append(['pOrdinary','cCycle'])
  m['predicates']['OutcomeIncluded'].append(['osOrdinary','oCycle']);m['predicates']['ProfileDependencyDeclared'] += [['pOrdinary','cCycle','cPass'],['pOrdinary','cPass','cCycle']]
 add('declared-PASS-cycle-no-acyclicity-claim',cycle,I=True)
 for n in ['RunRecordDeclared','ProfileApplicationDeclared']:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['ordinary']),T=False)
 for n,arg in [('ProfileDeclared','pOrdinary'),('ProfileCurrentDeclared','pOrdinary'),('SubjectCurrentDeclared','subject'),('InputCurrentDeclared','input'),('OutcomeSetDeclared','osOrdinary')]:add('missing-exact-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False)
 for n,arg in [('runHandle','ordinary'),('profileHandle','pOrdinary'),('subjectHandle','subject'),('inputHandle','input'),('outcomeSetHandle','osOrdinary'),('profileDigest','pOrdinary'),('subjectDigest','subject'),('inputDigest','input')]:add('empty-binding-'+n,lambda m,n=n,arg=arg:setfn(m,n,arg,'empty'),T=False)
 for n in ['runProfileDigest','runSubjectDigest','runInputDigest']:add('wrong-exact-'+n,lambda m,n=n:setfn(m,n,'ordinary','differentDigest'),T=False)
 for n in ['FAIL','NOT_EVALUABLE']:add('collapsed-status-'+n,lambda m,n=n:m['constants'].update({n:'pass'}),T=False)
 add('unknown-included-outcome-status',lambda m:setfn(m,'outcomeStatus','oPass','unknown'),T=False)
 add('wrong-outcome-run',lambda m:setfn(m,'outcomeRun','oPass','validation'),T=False)
 add('outcome-check-not-declared-in-profile',lambda m:m['predicates']['ProfileCheckDeclared'].remove(['pOrdinary','cPass']),T=False)
 add('outcome-outside-profile-coverage',lambda m:m['predicates']['ProfileCoverageDeclared'].remove(['pOrdinary','cPass']),T=False)
 add('outcome-evidence-set-not-declared',lambda m:m['predicates']['EvidenceSetDeclared'].remove(['esPass']),T=False)
 for n,arg in [('outcomeHandle','oPass'),('checkHandle','cPass'),('evidenceSetHandle','esPass'),('evidenceHandle','evidence')]:add('empty-outcome-or-evidence-'+n,lambda m,n=n,arg=arg:setfn(m,n,arg,'empty'),T=False)
 add('omitted-declared-check-outcome',lambda m:m['predicates']['OutcomeIncluded'].remove(['osOrdinary','oPass']),T=False)
 def duplicate(m):
  m['predicates']['OutcomeIncluded'].append(['osOrdinary','oOutside']);setfn(m,'outcomeRun','oOutside','ordinary');setfn(m,'outcomeCheck','oOutside','cPass')
 add('two-outcomes-for-same-declared-check',duplicate,T=False)
 add('NE-without-causal-blocker',lambda m:m['predicates']['BlockerIncluded'].remove(['oExternalNE','bExternal']),T=False)
 add('causal-blocker-not-declared',lambda m:m['predicates']['BlockerDeclared'].remove(['bExternal']),T=False)
 for n in ['blockerHandle','blockerCause']:add('empty-causal-'+n,lambda m,n=n:setfn(m,n,'bExternal','empty'),T=False)
 for status in ['pass','fail']:add('blocked-dependent-recorded-'+status,lambda m,status=status:setfn(m,'outcomeStatus','oBlocked',status),T=False)
 add('dependency-blocker-not-qualified',lambda m:m['predicates']['DependencyBlockerDeclared'].remove(['bFail']),T=False)
 add('dependency-blocker-wrong-upstream-check',lambda m:setfn(m,'blockerUpstreamCheck','bFail','cPass'),T=False)
 add('dependency-upstream-check-not-profile-declared',lambda m:m['predicates']['ProfileDependencyDeclared'].append(['pOrdinary','cPass','cOutside']),T=False)
 add('dependency-downstream-check-not-profile-declared',lambda m:m['predicates']['ProfileDependencyDeclared'].append(['pOrdinary','cOutside','cPass']),T=False)
 add('validation-role-without-validation-profile',lambda m:m['predicates']['ValidationProfileDeclared'].remove(['pValidation']),T=False)
 for n in ['ConformanceDeterminationRole','AuthorityDecisionRole']:add('excluded-role-'+n,lambda m,n=n:m['predicates'][n].append(['ordinary']),T=False)
 add('effectful-declaration-without-explicit-profile-inclusion',lambda m:m['predicates']['ProfileEffectIncludedDeclared'].remove(['pEffect']),T=False)
 add('no-qualified-validation-example-T-without-I',lambda m:m['predicates'].update(ValidationRole=[]),I=False)
 add('no-explicit-effect-example-T-without-I',lambda m:m['predicates'].update(EffectfulExecutionDeclared=[]),I=False)
 def empty_profile(m):
  for n in ['ProfileCheckDeclared','ProfileCoverageDeclared','ProfileDependencyDeclared']:m['predicates'][n]=[x for x in m['predicates'][n] if x[0]!='pOrdinary']
  m['predicates']['OutcomeIncluded']=[x for x in m['predicates']['OutcomeIncluded'] if x[0]!='osOrdinary']
 add('empty-profile-no-implicit-check-population',empty_profile,I=False)
 add('missing-total-input-function-entry',lambda m:m['functions']['runInput'].pop(),error='nontotal-function')
 add('ill-sorted-outcome-status-result',lambda m:setfn(m,'outcomeStatus','oPass','cPass'),error='ill-sorted-function-result')
 add('ill-sorted-PASS-constant',lambda m:m['constants'].update(PASS='digest'),error='ill-sorted-constant')
 add('wrong-dependency-relation-arity',lambda m:m['predicates'].update(ProfileDependencyDeclared=[['pOrdinary','cPass']]),error='ill-sorted-model-tuple')
 add('duplicate-outcome-inclusion-tuple',lambda m:m['predicates']['OutcomeIncluded'].append(['osOrdinary','oPass']),error='duplicate-predicate-tuple')
 add('empty-outcome-domain',lambda m:m['domains'].update(Outcome=[]),error='empty-or-malformed-domain')
 add('duplicate-input-function-tuple',lambda m:m['functions']['runInput'].append(copy.deepcopy(m['functions']['runInput'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.drift-assessment/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Evaluation-model-controls/v1-candidate','status':'PASS-for-exact-authored-Evaluation-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Exact declared profile/subject/input/digest and collect-all status/coverage/causal-blocker guards checked on supplied models. PASS and declared cause/evidence do not create actual execution,correctness,adequacy,conformance,admission or authority. Accepted profile/check/dependency/consumer maps,source-owner fidelity and common denotations remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
