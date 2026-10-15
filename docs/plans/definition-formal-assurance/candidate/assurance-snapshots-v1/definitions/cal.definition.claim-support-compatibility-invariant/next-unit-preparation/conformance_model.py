"""Independent exact-tuple,scope/evidence/obligation finite controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 assessments=['aSchema','aIdentity','aImplementation','aRuntime','aOutside'];active=assessments[:-1];scopes=['qSchema','qIdentity','qImplementation','qRuntime','qOutside'];profiles=['pSchema','pIdentity','pImplementation','pRuntime','pOutside'];sets=['sSchema','sIdentity','sImplementation','sRuntime','sOutside'];ev=['eSchema','eIdentity','eImplementation','eRuntime','eOutside'];obl=['oSchema','oIdentity','oImplementation','oRuntime','oOutside'];subjects=['subject','outsideSubject'];contracts=['contract','outsideContract'];owners=['owner','outsideOwner']
 domains={'Assessment':assessments,'Subject':subjects,'Contract':contracts,'Scope':scopes,'Profile':profiles,'EvidenceSet':sets,'Evidence':ev,'Obligation':obl,'Owner':owners,'Token':['empty','reference','subject-digest','contract-digest','version','same-label']};aq=dict(zip(assessments,scopes));ap=dict(zip(assessments,profiles));ae=dict(zip(assessments,sets));maps={'assessmentSubject':lambda a:'outsideSubject' if a=='aOutside' else 'subject','assessmentContract':lambda a:'outsideContract' if a=='aOutside' else 'contract','assessmentScope':lambda a:aq[a],'assessmentProfile':lambda a:ap[a],'assessmentEvidenceSet':lambda a:ae[a],'assessmentOwner':lambda a:'outsideOwner' if a=='aOutside' else 'owner','assessmentSubjectDigest':lambda a:'subject-digest','assessmentContractDigest':lambda a:'contract-digest','assessmentProfileVersion':lambda a:'version','assessmentCauseReference':lambda a:'reference','subjectHandle':lambda s:'same-label','subjectDigest':lambda s:'subject-digest','contractHandle':lambda c:'same-label','contractDigest':lambda c:'contract-digest','scopeHandle':lambda q:'same-label','profileHandle':lambda p:'same-label','profileVersion':lambda p:'version','evidenceSetHandle':lambda e:'reference','evidenceSetSubject':lambda e:'outsideSubject' if e=='sOutside' else 'subject','evidenceSetContract':lambda e:'outsideContract' if e=='sOutside' else 'contract','evidenceHandle':lambda e:'reference','ownerHandle':lambda o:'reference','obligationHandle':lambda o:'reference'}
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['ConformanceAssessment','TupleDeclared','ConformanceAsserted']:predicates[n]=[[a] for a in active]
 predicates.update(SubjectDeclared=[['subject']],ContractDeclared=[['contract']],ScopeDeclared=[[q] for q in scopes[:-1]],ProfileDeclared=[[p] for p in profiles[:-1]],OwnerDeclared=[['owner']],EvidenceSetDeclared=[[e] for e in sets[:-1]],EvidenceCurrentDeclared=[[e] for e in sets[:-1]],NotEvaluableDeclared=[['aOutside']],ProfileApplicable=[[p,'contract',q] for p,q in zip(profiles[:-1],scopes[:-1])],ProfileCompleteDeclared=[[p,q] for p,q in zip(profiles[:-1],scopes[:-1])],ObligationApplicable=[['contract',q,o] for q,o in zip(scopes[:-1],obl[:-1])],EvidenceMember=[[s,e] for s,e in zip(sets[:-1],ev[:-1])],EvidenceMapsObligation=[[e,o] for e,o in zip(ev[:-1],obl[:-1])],EvidenceSatisfiesDeclared=[[e,o] for e,o in zip(ev[:-1],obl[:-1])],ProfileDeclaresSufficient=[[p,s,o] for p,s,o in zip(profiles[:-1],sets[:-1],obl[:-1])])
 for n,q in zip(b.SCOPE_KINDS,scopes):predicates[n]=[[q]]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('four-independent-scoped-exact-tuples',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-'+n,lambda m,n=n:m['predicates']['Actual'+n].append(['aSchema']),I=True)
 add('same-subject-separate-scopes-and-evidence',lambda m:None,I=True)
 add('scope-kind-overlap-permitted',lambda m:m['predicates']['SchemaScope'].append(['qIdentity']),I=True)
 add('outside-tuple-map-not-governing-assertion',lambda m:setfn(m,'assessmentEvidenceSet','aOutside','sSchema'),I=True)
 for n in ['TupleDeclared','ConformanceAsserted']:add('missing-asserted-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['aSchema']),T=False)
 for n,item in [('SubjectDeclared','subject'),('ContractDeclared','contract'),('ScopeDeclared','qSchema'),('ProfileDeclared','pSchema'),('OwnerDeclared','owner'),('EvidenceSetDeclared','sSchema')]:add('missing-explicit-'+n,lambda m,n=n,item=item:m['predicates'][n].remove([item]),T=False)
 add('profile-not-applicable-to-exact-contract-scope',lambda m:m['predicates']['ProfileApplicable'].remove(['pSchema','contract','qSchema']),T=False)
 for n,value in [('evidenceSetSubject','outsideSubject'),('evidenceSetContract','outsideContract')]:add('wrong-current-evidence-binding-'+n,lambda m,n=n,value=value:setfn(m,n,'sSchema',value),T=False)
 for n,value in [('assessmentSubjectDigest','contract-digest'),('assessmentContractDigest','subject-digest'),('assessmentProfileVersion','reference')]:add('substituted-exact-'+n,lambda m,n=n,value=value:setfn(m,n,'aSchema',value),T=False)
 for n,arg in [('subjectHandle','subject'),('subjectDigest','subject'),('contractHandle','contract'),('contractDigest','contract'),('scopeHandle','qSchema'),('profileHandle','pSchema'),('profileVersion','pSchema'),('evidenceSetHandle','sSchema'),('ownerHandle','owner')]:add('missing-exact-handle-or-value-'+n,lambda m,n=n,arg=arg:setfn(m,n,arg,'empty'),T=False)
 add('missing-current-evidence-declaration',lambda m:m['predicates']['EvidenceCurrentDeclared'].remove(['sSchema']),T=False)
 for n in ['EvidenceStaleAgainstSubject','EvidenceStaleAgainstContract']:add('stale-current-claim-'+n,lambda m,n=n:m['predicates'][n].append(['sSchema']),T=False)
 add('incomplete-profile-scope',lambda m:m['predicates']['ProfileCompleteDeclared'].remove(['pSchema','qSchema']),T=False)
 add('profile-no-sufficiency-for-one-obligation',lambda m:m['predicates']['ProfileDeclaresSufficient'].remove(['pSchema','sSchema','oSchema']),T=False)
 add('empty-obligation-reference',lambda m:setfn(m,'obligationHandle','oSchema','empty'),T=False)
 for n,args in [('EvidenceMember',['sSchema','eSchema']),('EvidenceMapsObligation',['eSchema','oSchema']),('EvidenceSatisfiesDeclared',['eSchema','oSchema'])]:add('obligation-without-'+n,lambda m,n=n,args=args:m['predicates'][n].remove(args),T=False)
 add('empty-satisfying-evidence-reference',lambda m:setfn(m,'evidenceHandle','eSchema','empty'),T=False)
 for n in b.ROLES:add('forbidden-collapsed-role-'+n,lambda m,n=n:m['predicates'][n].append(['aSchema']),T=False)
 add('additional-applicable-obligation-without-evidence',lambda m:m['predicates']['ObligationApplicable'].append(['contract','qSchema','oOutside']),T=False)
 add('empty-schema-obligation-set-needs-separate-witness',lambda m:m['predicates']['ObligationApplicable'].remove(['contract','qSchema','oSchema']),I=False)
 add('unasserted-not-evaluable-cause-needs-separate-witness',lambda m:setfn(m,'assessmentCauseReference','aOutside','empty'),I=False)
 add('runtime-scope-witness-not-guaranteed-by-schema',lambda m:m['predicates']['RuntimeScope'].clear(),I=False)
 add('missing-total-function-entry',lambda m:m['functions']['assessmentScope'].pop(),error='nontotal-function')
 add('ill-sorted-evidence-set-result',lambda m:setfn(m,'assessmentEvidenceSet','aSchema','owner'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='subject'),error='ill-sorted-constant')
 add('wrong-sufficiency-arity',lambda m:m['predicates'].update(ProfileDeclaresSufficient=[['pSchema','sSchema']]),error='ill-sorted-model-tuple')
 add('duplicate-assertion-tuple',lambda m:m['predicates']['ConformanceAssessment'].append(['aSchema']),error='duplicate-predicate-tuple')
 add('empty-profile-domain',lambda m:m['domains'].update(Profile=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['assessmentScope'].append(copy.deepcopy(m['functions']['assessmentScope'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.claim-support-compatibility-invariant/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Conformance-model-controls/v1-candidate','status':'PASS-for-exact-authored-Conformance-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Exact subject/contract/scope/profile/evidence/owner tuples with declared completeness,currentness and per-obligation sufficiency/evidence witnesses checked on supplied models. Actual conformance to any scope,owner authority,adequacy,publication/deployment,consumer maps,older-source fidelity and common denotations remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
