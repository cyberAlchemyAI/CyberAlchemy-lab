"""Supplied Registry entry,binding,overlay and discriminator models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
NAMES=['Main','Accepted','Expired','Super','Authority','Typed','Outside']
def base_model():
 ds={s:[s+'Value',s+'Outside'] for s in b.SORTS}
 ds.update(RequestReference=['q'+n for n in NAMES],SubjectIntentReference=['subjectMain','subjectTyped','subjectOutside'],ArtifactTypeReference=['typeProposed','typeOutput','typeOutside'],IdentityKey=['key'+n for n in NAMES]+['keySubjectMain','keySubjectTyped','keySubjectOutside','keyTypeProposed','keyTypeOutput','keyTypeOutside'],DependencySetReference=['depsPopulated','depsEmpty','depsOutside'],DependencyReference=['depOne','depOutside'],ComponentReference=['componentDraft','componentOutside'],Token=['empty','none','reference','differentReference'])
 constants={'EMPTY':'empty','NONE':'none'}
 maps={n:(lambda q,s=s:s+'Outside' if q=='qOutside' else s+'Value') for n,s in b.FACETS.items()}
 maps.update(requestSubject=lambda q:'subjectTyped' if q=='qTyped' else 'subjectOutside' if q=='qOutside' else 'subjectMain',requestProposedType=lambda q:'typeOutside' if q=='qOutside' else 'typeProposed',requestDependencies=lambda q:'depsPopulated' if q=='qMain' else 'depsOutside' if q=='qOutside' else 'depsEmpty',requestIdentity=lambda q:'key'+q[1:],subjectIdentity=lambda s:'keySubject'+s[len('subject'):],typeIdentity=lambda t:'keyType'+t[len('type'):],requestAuthorityEffect=lambda q:'none')
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE};selected=ds['RequestReference'][:-1]
 for s in b.SORTS:
  if s not in ['RequestReference','Token']:predicates[s+'Declared']=[[x] for x in ds[s] if not x.endswith('Outside')]
 for n in ['RequestApplicable','RequestInScopeDeclared','CandidateIntakeDeclared','IntakeCreationDeclared']:predicates[n]=[[q] for q in selected]
 for n,s in b.FACETS.items():predicates[n+'BindingDeclared']=[[q,maps[n](q)] for q in selected]
 subjects=['subjectMain','subjectTyped'];reg='RegistryReferenceValue';res='ResolutionObservationValue';ana='CompatibilityAnalysisValue'
 predicates.update(ResolutionBindingDeclared=[[res,reg,s] for s in subjects],UnresolvedResultDeclared=[[res]],CompatibilityBindingDeclared=[[ana,s] for s in subjects],ExactReuseRejectedDeclared=[[ana]],DependencySetMemberDeclared=[['depsPopulated','depOne']],RequestDependencyMemberDeclared=[['qMain','depOne']],SubjectAuthoredDeclared=[['subjectTyped']],ExactTypeExistsDeclared=[['subjectTyped']],DraftComponentDeclared=[['qMain','componentDraft']],AttachmentDeclared=[['qMain','componentDraft']],CandidateOutputDeclared=[['qAccepted','typeOutput']],CandidateTypePostureDeclared=[['typeOutput']],RequestAcceptedDeclared=[['qAccepted']],ResolvedDeclared=[['qExpired']],ReplacedDeclared=[['qSuper']],ExpiredDeclared=[['qExpired']],SupersededDeclared=[['qSuper']],RequestActualAuthority=[['qAuthority']])
 return {'domains':ds,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('complete-intake-with-separated-output-and-terminal-alternatives',lambda m:None,I=True)
 for n in b.ACTUAL:
  if n!='Authority':add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['RequestActual'+n].append(['qAuthority']),I=True)
 add('selected-empty-request-handle',lambda m:setfn(m,b.HANDLES['RequestReference'],'qMain','empty'),T=False)
 add('outside-empty-request-handle',lambda m:setfn(m,b.HANDLES['RequestReference'],'qOutside','empty'),I=True)
 add('selected-scope-disagreement',lambda m:m['predicates']['RequestInScopeDeclared'].remove(['qMain']),T=False)
 add('selected-candidate-intake-missing',lambda m:m['predicates']['CandidateIntakeDeclared'].remove(['qMain']),T=False)
 for n,s in b.FACETS.items():
  value=next(x['value'] for x in base_model()['functions'][n] if x['args']==['qMain'])
  add('missing-facet-declaration-'+n,lambda m,s=s,value=value:m['predicates'][s+'Declared'].remove([value]),T=False)
  add('empty-facet-handle-'+n,lambda m,s=s,value=value:setfn(m,b.HANDLES[s],value,'empty'),T=False)
  add('missing-exact-binding-'+n,lambda m,n=n,value=value:m['predicates'][n+'BindingDeclared'].remove(['qMain',value]),T=False)
  alternate=next(x for x in base_model()['domains'][s] if x!=value)
  add('conflicting-extra-binding-'+n,lambda m,n=n,alternate=alternate:m['predicates'][n+'BindingDeclared'].append(['qMain',alternate]),T=False)
 for n,arg in [('requestIdentity','qMain'),('subjectIdentity','subjectMain'),('typeIdentity','typeProposed')]:
  add('identity-key-empty-'+n,lambda m,n=n,arg=arg:setfn(m,b.HANDLES['IdentityKey'],next(x['value'] for x in m['functions'][n] if x['args']==[arg]),'empty'),T=False)
 add('request-collapses-with-subject',lambda m:setfn(m,'requestIdentity','qMain','keySubjectMain'),T=False)
 add('request-collapses-with-proposed-type',lambda m:setfn(m,'requestIdentity','qMain','keyTypeProposed'),T=False)
 add('shared-request-identity-alias-policy-unresolved',lambda m:setfn(m,'requestIdentity','qTyped','keyMain'),I=True)
 add('creation-declaration-missing',lambda m:m['predicates']['IntakeCreationDeclared'].remove(['qMain']),T=False)
 add('resolution-observation-binding-missing',lambda m:m['predicates']['ResolutionBindingDeclared'].remove(['ResolutionObservationValue','RegistryReferenceValue','subjectMain']),T=False)
 add('unresolved-result-missing',lambda m:m['predicates']['UnresolvedResultDeclared'].clear(),T=False)
 add('compatibility-subject-binding-missing',lambda m:m['predicates']['CompatibilityBindingDeclared'].remove(['CompatibilityAnalysisValue','subjectMain']),T=False)
 add('rejected-exact-reuse-missing',lambda m:m['predicates']['ExactReuseRejectedDeclared'].clear(),T=False)
 add('eligible-current-match-disqualifies-intake',lambda m:m['predicates']['AdmittedCurrentMatchDeclared'].append(['RegistryReferenceValue','DiscriminatorPathValue','DiscriminatorValueValue','typeProposed']),T=False)
 add('unrelated-registry-match-permitted',lambda m:m['predicates']['AdmittedCurrentMatchDeclared'].append(['RegistryReferenceOutside','DiscriminatorPathValue','DiscriminatorValueValue','typeProposed']),I=True)
 add('unrelated-discriminator-match-permitted',lambda m:m['predicates']['AdmittedCurrentMatchDeclared'].append(['RegistryReferenceValue','DiscriminatorPathOutside','DiscriminatorValueValue','typeProposed']),I=True)
 def change_registry(m):
  setfn(m,'requestRegistry','qMain','RegistryReferenceOutside');m['predicates']['RegistryReferenceDeclared'].append(['RegistryReferenceOutside']);next(x for x in m['predicates']['requestRegistryBindingDeclared'] if x[0]=='qMain')[1]='RegistryReferenceOutside'
 add('changed-registry-without-matching-observation',change_registry,T=False)
 add('declared-authority-effect',lambda m:setfn(m,'requestAuthorityEffect','qMain','reference'),T=False)
 add('none-collapses-with-empty',lambda m:m['constants'].update(NONE='empty'),T=False)
 for n in ['ConsumedAsSubjectDeclared','AdmissionRequestDeclared','SelfRegistrationDeclared','SelfAdmissionDeclared','ConvenienceWideningDeclared']:add('forbidden-'+n,lambda m,n=n:m['predicates'][n].append(['qMain']),T=False)
 add('request-satisfies-subject-dependency',lambda m:m['predicates']['SatisfiesSubjectDependencyDeclared'].append(['qMain','subjectMain','depOne']),T=False)
 add('dependency-for-unrelated-subject-permitted',lambda m:m['predicates']['SatisfiesSubjectDependencyDeclared'].append(['qMain','subjectOutside','depOne']),I=True)
 add('subject-authored-before-exact-type-exists',lambda m:m['predicates']['SubjectAuthoredDeclared'].append(['subjectMain']),T=False)
 add('exact-type-exists-declaration-missing',lambda m:m['predicates']['ExactTypeExistsDeclared'].clear(),T=False)
 add('unused-exact-type-exists-is-not-admission',lambda m:m['predicates']['ExactTypeExistsDeclared'].append(['subjectMain']),I=True)
 add('draft-component-no-attachment',lambda m:m['predicates']['AttachmentDeclared'].clear(),T=False)
 add('draft-component-is-admitted-contract',lambda m:m['predicates']['AdmittedContractComponentDeclared'].append(['componentDraft']),T=False)
 add('unrelated-component-admission-marker-permitted',lambda m:m['predicates']['AdmittedContractComponentDeclared'].append(['componentOutside']),I=True)
 add('draft-component-marker-missing-population-loss',lambda m:m['predicates']['DraftComponentDeclared'].clear(),I=False)
 add('accepted-request-without-candidate-output',lambda m:m['predicates']['CandidateOutputDeclared'].clear(),T=False)
 add('candidate-output-lacks-candidate-posture',lambda m:m['predicates']['CandidateTypePostureDeclared'].clear(),T=False)
 add('candidate-output-claims-admission',lambda m:m['predicates']['TypeAdmittedDeclared'].append(['typeOutput']),T=False)
 add('output-collapses-with-request',lambda m:setfn(m,'typeIdentity','typeOutput','keyAccepted'),T=False)
 add('output-collapses-with-intended-subject',lambda m:setfn(m,'typeIdentity','typeOutput','keySubjectMain'),T=False)
 def extra_output(m):
  m['predicates']['CandidateOutputDeclared'].append(['qAccepted','typeProposed']);m['predicates']['CandidateTypePostureDeclared'].append(['typeProposed'])
 add('multiple-separate-candidate-outputs-permitted',extra_output,I=True)
 add('request-not-accepted-population-loss',lambda m:m['predicates']['RequestAcceptedDeclared'].clear(),I=False)
 add('resolved-without-expiry-or-supersession',lambda m:m['predicates']['ExpiredDeclared'].clear(),T=False)
 add('replaced-without-expiry-or-supersession',lambda m:m['predicates']['SupersededDeclared'].clear(),T=False)
 add('rejected-without-expiry-or-supersession',lambda m:m['predicates']['RejectedDeclared'].append(['qMain']),T=False)
 add('terminal-can-have-both-expiry-and-supersession',lambda m:m['predicates']['SupersededDeclared'].append(['qExpired']),I=False)
 add('unterminated-expiry-marker-no-chronology-invented',lambda m:m['predicates']['ExpiredDeclared'].append(['qMain']),I=True)
 add('owner-treatment-selection-declaration-not-real-selection',lambda m:m['predicates']['OwnerTreatmentSelectedDeclared'].append(['qMain']),I=True)
 add('missing-exact-dependency-member',lambda m:m['predicates']['RequestDependencyMemberDeclared'].clear(),T=False)
 add('extra-unbound-dependency-member',lambda m:m['predicates']['RequestDependencyMemberDeclared'].append(['qAccepted','depOne']),T=False)
 add('dependency-reference-not-declared',lambda m:m['predicates']['DependencyReferenceDeclared'].clear(),T=False)
 add('outside-request-forbidden-marker-unconstrained',lambda m:m['predicates']['ConsumedAsSubjectDeclared'].append(['qOutside']),I=True)
 add('wrong-facet-result-sort',lambda m:setfn(m,'requestSubject','qMain','typeProposed'),error='ill-sorted-function-result')
 add('missing-signature-symbol',lambda m:m['predicates'].pop('CandidateOutputDeclared'),error='model-signature-denominator-mismatch')
 add('nontotal-request-selector',lambda m:m['functions']['requestRegistry'].pop(),error='nontotal-function')
 add('ill-sorted-none-constant',lambda m:m['constants'].update(NONE='qMain'),error='ill-sorted-constant')
 add('wrong-resolution-binding-arity',lambda m:m['predicates'].update(ResolutionBindingDeclared=[['ResolutionObservationValue','RegistryReferenceValue']]),error='ill-sorted-model-tuple')
 add('duplicate-request-binding',lambda m:m['predicates']['requestSubjectBindingDeclared'].append(['qMain','subjectMain']),error='duplicate-predicate-tuple')
 add('empty-component-domain',lambda m:m['domains'].update(ComponentReference=[]),error='empty-or-malformed-domain')
 add('duplicate-selector-function-tuple',lambda m:m['functions']['requestRegistry'].append(copy.deepcopy(m['functions']['requestRegistry'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.artifact-type-registry/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ArtifactTypeRequest-model-controls/v1-candidate','status':'PASS-for-exact-authored-ArtifactTypeRequest-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed unmatched Request declarations,exact field and identity bindings,zero matches,separate candidate output and terminal alternatives checked on supplied models. Actual resolver execution,compatibility correctness,owner selection,subject authorship,admission,consumer alignment and whole fidelity remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
