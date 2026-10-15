"""Planned finite Finding controls for separated conclusion and referenced Research context."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 domains={'Finding':['primaryFinding','secondaryFinding','outsideFinding'],'DefinitionContext':['contextPrimary','contextSecondary','contextOutside'],'DerivationBasis':['runBasis','setBasis','secondarySetBasis','outsideBasis'],'ResearchContext':['researchOne','researchTwo','researchOutside'],'Question':['question','otherQuestion'],'Scope':['scope','outsideScope'],'Project':['project','outsideProject'],'Goal':['goalOne','goalTwo','outsideGoal'],'SourceMaterial':['sourceOne','sourceTwo','sourceOutside'],'Observation':['obsOne','obsTwo','obsOutside'],'Method':['method','outsideMethod'],'EvidenceItem':['supportOne','counterOne','supportTwo','counterTwo','evidenceOutside'],'Limitation':['limitOne','limitTwo','limitOutside'],'Route':['ownerRoute','challengeRoute','outsideRoute'],'Time':['created','updated','outsideTime'],'ClaimWording':['wordingOne','wordingTwo','wordingOutside'],'SupportBound':['boundOne','boundTwo','boundOutside'],'SiblingTarget':['siblingSet','siblingInquiry','siblingRun'],'Token':['empty','semantic.finding','definition','type.definition','scope.knowledge-development','CAV2-D61','reference','same-label']}
 def active_f(f):return f!='outsideFinding'
 def active_r(r):return r!='researchOutside'
 maps={'findingContext':lambda f:'contextPrimary' if f=='primaryFinding' else 'contextSecondary' if f=='secondaryFinding' else 'contextOutside','contextConcept':lambda c:'semantic.finding','contextKind':lambda c:'definition','contextCarrier':lambda c:'type.definition','contextOwnerScope':lambda c:'scope.knowledge-development','contextLineage':lambda c:'CAV2-D61','findingQuestion':lambda f:'question' if active_f(f) else 'otherQuestion','findingScope':lambda f:'scope' if active_f(f) else 'outsideScope','findingWording':lambda f:'wordingOne' if f=='primaryFinding' else 'wordingTwo' if f=='secondaryFinding' else 'wordingOutside','findingSupportBound':lambda f:'boundOne' if f=='primaryFinding' else 'boundTwo' if f=='secondaryFinding' else 'boundOutside','findingChallengeRoute':lambda f:'challengeRoute' if active_f(f) else 'outsideRoute','basisResearchContext':lambda x:'researchOne' if x=='runBasis' else 'researchTwo' if x!='outsideBasis' else 'researchOutside','researchQuestion':lambda r:'question' if active_r(r) else 'otherQuestion','researchScope':lambda r:'scope' if active_r(r) else 'outsideScope','researchProject':lambda r:'project' if active_r(r) else 'outsideProject','researchMethod':lambda r:'method' if active_r(r) else 'outsideMethod','researchCreated':lambda r:'created' if active_r(r) else 'outsideTime','researchUpdated':lambda r:'updated' if active_r(r) else 'outsideTime','researchOwnerRoute':lambda r:'ownerRoute' if active_r(r) else 'outsideRoute','researchChallengeRoute':lambda r:'challengeRoute' if active_r(r) else 'outsideRoute'}
 for n in b.FUNCTIONS:
  if n not in maps:maps[n]=lambda x:'same-label'
 functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['FindingSelected','ConclusionRecordDeclared','EvidenceBoundedConclusionDeclared','AttributableFindingDeclared','FindingLimitationsDeclared']:predicates[n]=[['primaryFinding'],['secondaryFinding']]
 for n in ['DefinitionContextDeclared','AcceptedSourceRelationDeclared']:predicates[n]=[['contextPrimary'],['contextSecondary']]
 for n in ['ResearchContextSelected','BoundedInvestigationDeclared','AttributableResearchDeclared','EphemeralRecordDeclared','ResearchSourceCollectionDeclared','ResearchObservationCollectionDeclared','ResearchSupportingCollectionDeclared','ResearchCounterevidenceCollectionDeclared','ResearchLimitationCollectionDeclared','ResearchFindingReferencesDeclared']:predicates[n]=[['researchOne'],['researchTwo']]
 declarations={'BasisDeclared':['runBasis','setBasis','secondarySetBasis'],'ResearchRunBasisDeclared':['runBasis'],'EvidenceSetBasisDeclared':['setBasis','secondarySetBasis'],'QuestionDeclared':['question'],'ScopeDeclared':['scope'],'ProjectDeclared':['project'],'GoalDeclared':['goalOne','goalTwo'],'SourceMaterialDeclared':['sourceOne','sourceTwo'],'ObservationDeclared':['obsOne','obsTwo'],'MethodDeclared':['method'],'EvidenceItemDeclared':['supportOne','counterOne','supportTwo','counterTwo'],'LimitationDeclared':['limitOne','limitTwo'],'RouteDeclared':['ownerRoute','challengeRoute'],'TimeDeclared':['created','updated'],'ClaimWordingDeclared':['wordingOne','wordingTwo'],'SupportBoundDeclared':['boundOne','boundTwo']}
 for n,values in declarations.items():predicates[n]=[[x] for x in values]
 predicates.update(DerivationIncluded=[['primaryFinding','runBasis'],['primaryFinding','setBasis'],['secondaryFinding','secondarySetBasis']],FindingDerivesFromResearch=[['primaryFinding','researchOne'],['primaryFinding','researchTwo'],['secondaryFinding','researchTwo']],ResearchFindingReference=[['researchOne','primaryFinding'],['researchTwo','primaryFinding'],['researchTwo','secondaryFinding']],ResearchGoalLinked=[[r,g] for r in ['researchOne','researchTwo'] for g in ['goalOne','goalTwo']],ResearchSourceIncluded=[['researchOne','sourceOne'],['researchTwo','sourceTwo']],ResearchObservationIncluded=[['researchOne','obsOne'],['researchTwo','obsTwo']],ResearchSupportingIncluded=[['researchOne','supportOne'],['researchTwo','supportTwo']],ResearchCounterevidenceIncluded=[['researchOne','counterOne'],['researchTwo','counterTwo']],ResearchLimitationIncluded=[['researchOne','limitOne'],['researchTwo','limitTwo']],FindingLimitationIncluded=[['primaryFinding','limitOne'],['secondaryFinding','limitTwo']],WordingWithinSupportDeclared=[['wordingOne','boundOne'],['wordingTwo','boundTwo']],PromotionDeclared=[['primaryFinding']],ResearchPromotionDeclared=[['researchOne']],SiblingMeaningAssignmentDeclared=[['primaryFinding','siblingSet']],ExplicitSiblingReferenceDeclared=[['primaryFinding','siblingSet']])
 return {'domains':domains,'constants':dict(zip(b.CONSTANTS,['empty','semantic.finding','definition','type.definition','scope.knowledge-development','CAV2-D61'])),'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('finding-bounded-wording-with-separated-Research-context-without-actual-outcomes',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-'+n,lambda m,n=n:m['predicates']['Actual'+n].append(['secondaryFinding']),I=True)
 for n in b.RESEARCH_OUTCOMES:add('independent-Research-actual-'+n,lambda m,n=n:m['predicates']['ResearchActual'+n].append(['researchTwo']),I=True)
 add('shared-printed-handles-do-not-collapse-Finding-and-Research',lambda m:None,I=True)
 add('supporting-and-counterevidence-may-overlap',lambda m:m['predicates']['ResearchCounterevidenceIncluded'].append(['researchOne','supportOne']),I=True)
 add('basis-subkind-labels-not-universally-exclusive',lambda m:m['predicates']['ResearchRunBasisDeclared'].append(['setBasis']),I=True)
 add('reversed-Research-time-labels-have-no-imported-order',lambda m:(setfn(m,'researchCreated','researchOne','updated'),setfn(m,'researchUpdated','researchOne','created')),I=True)
 def empty(m):
  for n in ['ResearchSourceIncluded','ResearchObservationIncluded','ResearchSupportingIncluded','ResearchCounterevidenceIncluded','ResearchLimitationIncluded']:m['predicates'][n]=[x for x in m['predicates'][n] if x[0]!='researchTwo']
  m['predicates']['FindingLimitationIncluded'].remove(['secondaryFinding','limitTwo'])
 add('one-context-and-finding-empty-optional-member-sets',empty,I=True)
 add('outside-context-classification-not-governing',lambda m:setfn(m,'contextConcept','contextOutside','reference'),I=True)
 for n in ['ConclusionRecordDeclared','EvidenceBoundedConclusionDeclared','AttributableFindingDeclared','FindingLimitationsDeclared']:add('missing-Finding-'+n,lambda m,n=n:m['predicates'][n].remove(['primaryFinding']),T=False)
 for n in ['DefinitionContextDeclared','AcceptedSourceRelationDeclared']:add('missing-normalized-'+n,lambda m,n=n:m['predicates'][n].remove(['contextPrimary']),T=False)
 for n in ['contextConcept','contextKind','contextCarrier','contextOwnerScope','contextLineage']:add('wrong-normalized-'+n,lambda m,n=n:setfn(m,n,'contextPrimary','reference'),T=False)
 for n in ['findingHandle','contextHandle','questionHandle','scopeHandle','wordingHandle','boundHandle','routeHandle']:
  arg={'findingHandle':'primaryFinding','contextHandle':'contextPrimary','questionHandle':'question','scopeHandle':'scope','wordingHandle':'wordingOne','boundHandle':'boundOne','routeHandle':'challengeRoute'}[n];add('empty-Finding-bound-'+n,lambda m,n=n,arg=arg:setfn(m,n,arg,'empty'),T=False)
 for n,value in [('QuestionDeclared','question'),('ScopeDeclared','scope'),('ClaimWordingDeclared','wordingOne'),('SupportBoundDeclared','boundOne'),('RouteDeclared','challengeRoute')]:add('missing-Finding-bound-'+n,lambda m,n=n,value=value:m['predicates'][n].remove([value]),T=False)
 add('wording-not-within-declared-support',lambda m:m['predicates']['WordingWithinSupportDeclared'].remove(['wordingOne','boundOne']),T=False)
 add('no-primary-derivation',lambda m:m['predicates'].update(DerivationIncluded=[['secondaryFinding','secondarySetBasis']]),T=False)
 add('basis-undeclared',lambda m:m['predicates']['BasisDeclared'].remove(['runBasis']),T=False)
 add('basis-with-neither-Run-nor-Set-kind',lambda m:m['predicates']['ResearchRunBasisDeclared'].remove(['runBasis']),T=False)
 add('empty-basis-handle',lambda m:setfn(m,'basisHandle','runBasis','empty'),T=False)
 add('basis-mapped-to-outside-Research',lambda m:setfn(m,'basisResearchContext','runBasis','researchOutside'),T=False)
 add('selected-Research-not-backed-by-a-finding-basis',lambda m:m['predicates']['ResearchContextSelected'].append(['researchOutside']),T=False)
 add('Research-context-not-selected',lambda m:m['predicates']['ResearchContextSelected'].remove(['researchOne']),T=False)
 add('Finding-Research-derivation-edge-omitted',lambda m:m['predicates']['FindingDerivesFromResearch'].remove(['primaryFinding','researchOne']),T=False)
 add('Research-finding-ref-omitted',lambda m:m['predicates']['ResearchFindingReference'].remove(['researchOne','primaryFinding']),T=False)
 for n,value in [('researchQuestion','otherQuestion'),('researchScope','outsideScope')]:add('Finding-Research-map-mismatch-'+n,lambda m,n=n,value=value:setfn(m,n,'researchOne',value),T=False)
 for n in ['BoundedInvestigationDeclared','AttributableResearchDeclared','EphemeralRecordDeclared','ResearchSourceCollectionDeclared','ResearchObservationCollectionDeclared','ResearchSupportingCollectionDeclared','ResearchCounterevidenceCollectionDeclared','ResearchLimitationCollectionDeclared','ResearchFindingReferencesDeclared']:add('missing-Research-'+n,lambda m,n=n:m['predicates'][n].remove(['researchOne']),T=False)
 for n,arg in [('researchHandle','researchOne'),('projectHandle','project'),('methodHandle','method'),('timeHandle','created'),('routeHandle','ownerRoute')]:add('empty-Research-bound-'+n,lambda m,n=n,arg=arg:setfn(m,n,arg,'empty'),T=False)
 for n,value in [('ProjectDeclared','project'),('MethodDeclared','method'),('TimeDeclared','created'),('RouteDeclared','ownerRoute')]:add('missing-Research-bound-'+n,lambda m,n=n,value=value:m['predicates'][n].remove([value]),T=False)
 add('Research-context-with-no-Goal',lambda m:m['predicates'].update(ResearchGoalLinked=[x for x in m['predicates']['ResearchGoalLinked'] if x[0]!='researchOne']),T=False)
 add('linked-Goal-undeclared',lambda m:m['predicates']['GoalDeclared'].remove(['goalOne']),T=False)
 add('empty-linked-Goal-handle',lambda m:setfn(m,'goalHandle','goalOne','empty'),T=False)
 for n,value in [('SourceMaterialDeclared','sourceOne'),('ObservationDeclared','obsOne'),('EvidenceItemDeclared','supportOne'),('EvidenceItemDeclared','counterOne'),('LimitationDeclared','limitOne')]:add('included-member-undeclared-'+n+'-'+value,lambda m,n=n,value=value:m['predicates'][n].remove([value]),T=False)
 for n,arg in [('sourceHandle','sourceOne'),('sourceProvenanceRef','sourceOne'),('observationHandle','obsOne'),('observationOriginRef','obsOne'),('evidenceHandle','supportOne'),('evidenceProvenanceRef','counterOne'),('limitationHandle','limitOne')]:add('included-member-empty-'+n,lambda m,n=n,arg=arg:setfn(m,n,arg,'empty'),T=False)
 add('Research-ref-points-to-outside-Finding',lambda m:m['predicates']['ResearchFindingReference'].append(['researchOne','outsideFinding']),T=False)
 add('Research-outcome-field-present',lambda m:m['predicates']['ResearchOutcomeFieldPresent'].append(['researchOne']),T=False)
 for n in b.FINDING_ROLES:add('collapsed-Finding-role-'+n,lambda m,n=n:m['predicates'][n].append(['primaryFinding']),T=False)
 for n in b.RESEARCH_ROLES:add('collapsed-Research-role-'+n,lambda m,n=n:m['predicates'][n].append(['researchOne']),T=False)
 add('sibling-meaning-assignment-without-ref',lambda m:m['predicates']['ExplicitSiblingReferenceDeclared'].clear(),T=False)
 add('empty-sibling-ref-handle',lambda m:setfn(m,'siblingHandle','siblingSet','empty'),T=False)
 add('no-plural-derivation-example-T-without-I',lambda m:m['predicates']['DerivationIncluded'].remove(['primaryFinding','setBasis']),I=False)
 add('no-promotion-example-T-without-I',lambda m:m['predicates']['PromotionDeclared'].clear(),I=False)
 add('no-counterevidence-example-T-without-I',lambda m:m['predicates']['ResearchCounterevidenceIncluded'].clear(),I=False)
 add('no-sibling-assignment-example-T-without-I',lambda m:m['predicates']['SiblingMeaningAssignmentDeclared'].clear(),I=False)
 add('no-Research-promotion-example-T-without-I',lambda m:m['predicates']['ResearchPromotionDeclared'].clear(),I=False)
 add('missing-total-basis-context-function-entry',lambda m:m['functions']['basisResearchContext'].pop(),error='nontotal-function')
 add('ill-sorted-finding-wording-result',lambda m:setfn(m,'findingWording','primaryFinding','question'),error='ill-sorted-function-result')
 add('ill-sorted-classification-constant',lambda m:m['constants'].update(SEMANTIC_FINDING='primaryFinding'),error='ill-sorted-constant')
 add('wrong-support-bound-relation-arity',lambda m:m['predicates'].update(WordingWithinSupportDeclared=[['wordingOne']]),error='ill-sorted-model-tuple')
 add('duplicate-Research-Finding-reference-tuple',lambda m:m['predicates']['ResearchFindingReference'].append(['researchOne','primaryFinding']),error='duplicate-predicate-tuple')
 add('empty-Question-domain',lambda m:m['domains'].update(Question=[]),error='empty-or-malformed-domain')
 add('duplicate-Research-project-function-tuple',lambda m:m['functions']['researchProject'].append(copy.deepcopy(m['functions']['researchProject'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.evidence-set/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Finding-model-controls/v1-candidate','status':'PASS-for-exact-authored-Finding-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Declared evidence-bounded attributable Finding and separately referenced Research context,one-or-more Run/Set bases,explicit wording/support bounds,limitations/challenge routes and source-preserving Research maps checked on supplied models. Actual support/wording adequacy,investigation,truth,admission,authority and owner/consumer correspondence remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
