"""Supplied bounded Review,exact subject,use and separate effect models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 domains={s:[s.lower()+'A',s.lower()+'Outside'] for s in b.SORTS};domains.update(Review=['r0','r1','rOutside'],SubjectVersionSet=['ss0','ss1','ssOutside'],SubjectVersion=['sv0','sv1','svOutside'],ReviewUse=['uCurrent','uSuccessor','uOutside'],DefinitionVersion=['current','successor','unresolved'],ReviewEffect=['e'+str(i) for i in range(5)]+['eExtra','eOutside'],Decision=['d0','dOutside'],EffectKind=[n.lower() for n in b.EFFECTS]+['custom','kindOutside'],Contract=['c0','cOutside'],Token=['empty','reference','extra','subject0','revision0','revision1'])
 constants={'EMPTY':'empty','CURRENT_VERSION':'current',**{n.upper():n.lower() for n in b.EFFECTS}};maps={}
 for n,sort in b.FIELDS.items():maps[n]=lambda r,sort=sort:domains[sort][-1] if r=='rOutside' else domains[sort][0]
 maps['reviewSubjects']=lambda r:{'r0':'ss0','r1':'ss1','rOutside':'ssOutside'}[r]
 maps.update(subjectIdentity=lambda s:'extra' if s=='svOutside' else 'subject0',subjectExactRevision=lambda s:'extra' if s=='svOutside' else 'revision1' if s=='sv1' else 'revision0',useReview=lambda u:'rOutside' if u=='uOutside' else 'r0',useVersion=lambda u:{'uCurrent':'current','uSuccessor':'successor','uOutside':'unresolved'}[u],useScope=lambda u:'assessmentscopeOutside' if u=='uOutside' else 'assessmentscopeA',effectReview=lambda e:'rOutside' if e=='eOutside' else 'r0',effectDecision=lambda e:'dOutside' if e=='eOutside' else 'd0',effectKind=lambda e:'kindOutside' if e=='eOutside' else 'custom' if e=='eExtra' else b.EFFECTS[int(e[1:])].lower(),effectContract=lambda e:'cOutside' if e=='eOutside' else 'c0')
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['ReviewApplicable','ReviewInScopeDeclared','AttributableAssessmentDeclared','BoundedAssessmentDeclared','GovernedIdentityOrRecordDeclared']:predicates[n]=[['r0'],['r1']]
 for n,sort in b.FIELDS.items():predicates[sort+'Declared']=[[x] for x in dict.fromkeys(maps[n](r) for r in ['r0','r1'])]
 predicates.update(ExactSubjectVersionDeclared=[['sv0'],['sv1']],SubjectMemberDeclared=[['ss0','sv0'],['ss0','sv1'],['ss1','sv0']],DefinitionVersionDeclared=[['current'],['successor']],AdmittedSuccessorVersionDeclared=[['successor']],SeparateDecisionDeclared=[['d0']],EffectKindDeclared=[[n.lower()] for n in b.EFFECTS]+[['custom']],AdmittedContractDeclared=[['c0']],ReviewHasEffectDeclared=[['r0',n.lower()] for n in b.EFFECTS],DecisionGrantsReviewEffectDeclared=[['d0','r0',n.lower()] for n in b.EFFECTS])
 for n in ['ReviewUseApplicable','UseInScopeDeclared','UseWithinApplicabilityAndExclusionsDeclared']:predicates[n]=[['uCurrent'],['uSuccessor']]
 for n in ['ReviewEffectApplicable','EffectInScopeDeclared']:predicates[n]=[['e'+str(i)] for i in range(5)]
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('bounded-assessment-exact-revisions-current-successor-use-and-conditional-effects',lambda m:None,I=True)
 for n in b.ACTUAL:add('independent-Review-actual-'+n,lambda m,n=n:m['predicates']['ReviewActual'+n].append(['r1']),I=True)
 for n in b.EFFECT_ACTUAL:add('independent-Effect-actual-'+n,lambda m,n=n:m['predicates']['EffectActual'+n].append(['e0']),I=True)
 for n in b.USE_ACTUAL:add('independent-Use-actual-'+n,lambda m,n=n:m['predicates']['UseActual'+n].append(['uCurrent']),I=False)
 add('one-subject-can-have-two-exact-revisions',lambda m:None,I=True)
 add('a-Review-need-not-have-any-declared-effect',lambda m:None,I=True)
 add('outside-Review-empty-handle',lambda m:setfn(m,'reviewHandle','rOutside','empty'),I=True)
 add('outside-use-can-have-unresolved-version',lambda m:setfn(m,'definitionVersionHandle','unresolved','empty'),I=True)
 add('outside-effect-can-lack-a-Decision-reference',lambda m:setfn(m,'decisionHandle','dOutside','empty'),I=True)
 def custom_effect(m):
  for n in ['ReviewEffectApplicable','EffectInScopeDeclared']:m['predicates'][n].append(['eExtra'])
  m['predicates']['ReviewHasEffectDeclared'].append(['r0','custom']);m['predicates']['DecisionGrantsReviewEffectDeclared'].append(['d0','r0','custom'])
 add('five-effect-labels-need-not-exhaust-real-effect-kinds',custom_effect,I=True)
 for n in ['ReviewInScopeDeclared','AttributableAssessmentDeclared','BoundedAssessmentDeclared','GovernedIdentityOrRecordDeclared']:add('missing-Review-'+n,lambda m,n=n:m['predicates'][n].remove(['r0']),T=False)
 add('Review-declared-scope-without-membership',lambda m:m['predicates']['ReviewApplicable'].remove(['r0']),T=False)
 for sort in b.FIELDS.values():add('missing-assessment-component-'+sort,lambda m,sort=sort:m['predicates'][sort+'Declared'].clear(),T=False)
 add('selected-subject-set-without-any-member',lambda m:m['predicates'].update(SubjectMemberDeclared=[['ss1','sv0']]),T=False)
 add('subject-member-without-exact-version-declaration',lambda m:m['predicates']['ExactSubjectVersionDeclared'].remove(['sv0']),T=False)
 for n in ['subjectIdentity','subjectExactRevision']:add('empty-subject-'+n,lambda m,n=n:setfn(m,n,'sv0','empty'),T=False)
 for sort,arg in [('Review','r0'),('SubjectVersionSet','ss0'),('QuestionSet','questionsetA'),('CriterionSet','criterionsetA'),('EvidenceSet','evidencesetA'),('AlternativeSet','alternativesetA'),('ClaimCeiling','claimceilingA'),('OwnerRoute','ownerrouteA'),('AssessmentScope','assessmentscopeA'),('Context','contextA'),('SubjectVersion','sv0'),('ReviewUse','uCurrent'),('DefinitionVersion','current'),('ReviewEffect','e0'),('Decision','d0'),('EffectKind','admission'),('Contract','c0')]:add('empty-selected-'+sort+'-handle',lambda m,sort=sort,arg=arg:setfn(m,b.HANDLES[sort],arg,'empty'),T=False)
 for n in ['UseInScopeDeclared','UseWithinApplicabilityAndExclusionsDeclared']:add('missing-use-'+n,lambda m,n=n:m['predicates'][n].remove(['uCurrent']),T=False)
 add('use-declared-scope-without-membership',lambda m:m['predicates']['ReviewUseApplicable'].remove(['uCurrent']),T=False)
 add('use-binds-outside-Review',lambda m:setfn(m,'useReview','uCurrent','rOutside'),T=False)
 add('use-version-without-declaration',lambda m:m['predicates']['DefinitionVersionDeclared'].remove(['current']),T=False)
 add('use-successor-without-admission-declaration',lambda m:m['predicates']['AdmittedSuccessorVersionDeclared'].clear(),T=False)
 add('use-unresolved-version-is-neither-current-nor-successor',lambda m:setfn(m,'useVersion','uCurrent','unresolved'),T=False)
 add('use-scope-does-not-match-assessment-scope',lambda m:setfn(m,'useScope','uCurrent','assessmentscopeOutside'),T=False)
 for n in ['EffectInScopeDeclared','SeparateDecisionDeclared','EffectKindDeclared','AdmittedContractDeclared','DecisionGrantsReviewEffectDeclared','ReviewHasEffectDeclared']:add('missing-effect-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('effect-declared-scope-without-membership',lambda m:m['predicates']['ReviewEffectApplicable'].remove(['e0']),T=False)
 add('effect-binds-outside-Review',lambda m:setfn(m,'effectReview','e0','rOutside'),T=False)
 add('effect-binds-outside-Decision',lambda m:setfn(m,'effectDecision','e0','dOutside'),T=False)
 add('effect-binds-outside-contract',lambda m:setfn(m,'effectContract','e0','cOutside'),T=False)
 add('effect-kind-changed-without-corresponding-grant',lambda m:setfn(m,'effectKind','e0','custom'),T=False)
 add('Review-has-effect-without-selected-effect-record',lambda m:m['predicates']['ReviewHasEffectDeclared'].append(['r1','approval']),T=False)
 add('collapse-Admission-and-Approval-effect-labels',lambda m:m['constants'].update(APPROVAL='admission'),T=False)
 add('missing-symbol',lambda m:m['predicates'].pop('ReviewApplicable'),error='model-signature-denominator-mismatch')
 add('partial-total-function',lambda m:m['functions']['reviewSubjects'].pop(),error='nontotal-function')
 add('ill-sorted-constant',lambda m:m['constants'].update(EMPTY='r0'),error='ill-sorted-constant')
 add('wrong-grant-arity',lambda m:m['predicates'].update(DecisionGrantsReviewEffectDeclared=[['d0','r0']]),error='ill-sorted-model-tuple')
 add('duplicate-Review-tuple',lambda m:m['predicates']['ReviewApplicable'].append(['r0']),error='duplicate-predicate-tuple')
 add('empty-subject-version-domain',lambda m:m['domains'].update(SubjectVersion=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['reviewSubjects'].append(copy.deepcopy(m['functions']['reviewSubjects'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.provenance/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Review-model-controls/v1-candidate','status':'PASS-for-exact-authored-Review-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed bounded Review assessment,exact subject versions,current/successor uses and necessary separate Decision/contract effect guards checked on supplied models. Actual adequacy,grant,approval,validation,truth,execution,authority,owner acceptance and consumer maps remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
